# Phase-2 READ_ONLY re-implementation of T0.4 sampling. Does NOT import tools.t0_4. Reads frozen CSV/JSON only.
# Run with cwd = the Phase-2 worktree root. Writes nothing.
import csv, json, hashlib, statistics, collections


def rd(p):
    with open(p, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def T(v):
    return str(v).strip().lower() == 'true'


spec = json.load(open('configs/t0_4/sampling_spec.json', encoding='utf-8'))
SEED = spec['sampling_seed']
PRIO = spec['sampling_stratum_priority']
inv = rd('dataset/corpus_freeze/corpus_inventory.csv')
pp = rd('dataset/corpus_freeze/page_profile.csv')
issuer_rows = rd('dataset/corpus_freeze/issuer_split.csv')
sp = {r['issuer_id']: r['split'] for r in issuer_rows}
docs = {r['document_id']: r for r in inv}
aux = collections.defaultdict(set)
for r in rd('dataset/corpus_gap_audit/condition_page_map.csv'):
    aux[(r['document_id'], int(r['page_index']))].add(r['condition'])
tables = {(r['document_id'], int(r['page_index'])) for r in rd('dataset/corpus_gap_audit/table_candidates.csv')
          if r['detector_status'] == 'CANDIDATE'}
lang = collections.defaultdict(set)
for r in rd('dataset/corpus_gap_audit/language_candidates.csv'):
    k = (r['document_id'], int(r['page_index']))
    if T(r['is_hindi_page']):
        lang[k].add('devanagari_candidate')
    if T(r['is_bilingual_page']):
        lang[k].add('bilingual_candidate')
KIND = {'digital': 'native_ok', 'broken_text': 'broken_text', 'scanned': 'scanned',
        'vector_text': 'vector_text', 'hybrid': 'hybrid', 'blank': 'blank'}
MAP = {'devanagari_page': 'devanagari_candidate', 'native_page': 'native_ok', 'ocr_layer_page': 'ocr_layer_proxy',
       'scanned_page': 'scanned', 'two_column_page': 'multi_column'}


def rank(doc, page):
    return hashlib.sha256(f"{SEED}\x00{doc}\x00{page}".encode('utf-8')).hexdigest()


def length(d):
    if T(d['short_report']):
        return 'short'
    if T(d['long_report']):
        return 'long'
    return 'medium'


def stratum(labels):
    for s in PRIO:
        if s == 'native_clean_control':
            if 'native_ok' in labels:
                return s
            continue
        if s == 'other':
            return s
        if s in labels:
            return s


best = {}
allpages = []
for p in pp:
    d = docs[p['document_id']]
    page = int(p['physical_page'])
    fy = int(d['fiscal_year'])
    key = (p['document_id'], page)
    labels = set(lang.get(key, set()))
    rc = KIND.get(p['kind'], 'other')
    labels.add(rc)
    if int(p['n_columns'] or 0) >= 2:
        labels.add('multi_column')
    if fy < 2015:
        labels.add('pre_2015')
    if T(p['render_mode_ocr_layer_indicator']):
        labels.add('ocr_layer_proxy')
    if T(p['cid_or_broken_text_indicator']):
        labels.add('legacy_font_candidate')
    if key in tables:
        labels.add('table_candidate')
    for v in aux.get(key, ()):
        labels.add(MAP.get(v, v))
    st = stratum(labels)
    era = 'pre_2015' if fy < 2015 else 'post_2015'
    ln = length(d)
    rk = rank(p['document_id'], page)
    cell = (d['company_id'], st, era, rc, ln)
    rec = dict(doc=p['document_id'], page=page, issuer=d['company_id'], split=sp[d['company_id']], stratum=st,
               labels=sorted(labels), rc=rc, era=era, ln=ln, rank=rk, kind=p['kind'])
    allpages.append((cell, rec))
    inc = best.get(cell)
    if inc is None or (rk, p['document_id'], page) < (inc['rank'], inc['doc'], inc['page']):
        best[cell] = rec
cellsize = collections.Counter(c for c, _ in allpages)
print("MY RE-DERIVATION: observed cells =", len(best))
man = json.load(open('artifacts/t0_4/benchmark_manifest.json', encoding='utf-8'))
mu = {(u['document_id'], u['page_number']): u for u in man['track_a']['units']}
mine = {(r['doc'], r['page']): r for r in best.values()}
print("manifest Track-A units:", len(mu), " unit-key set equal to mine:", set(mu) == set(mine))
fields = [('sampling_stratum', 'stratum'), ('condition_labels', 'labels'), ('representation_class', 'rc'),
          ('era', 'era'), ('length_category', 'ln'), ('selection_rank', 'rank'), ('split', 'split'),
          ('issuer_id', 'issuer')]
bad = collections.Counter()
for k, u in mu.items():
    m = mine.get(k)
    if not m:
        continue
    for a, b in fields:
        if u[a] != m[b]:
            bad[a] += 1
print("field mismatches manifest-vs-mine:", dict(bad) or "NONE")

# --- closure-record claims
n_issuers = len(issuer_rows)
declared = n_issuers * len(PRIO) * 2 * 3 * 7
print("declared cells", n_issuers, "x", len(PRIO), "x2x3x7 =", declared, " zero-availability =", declared - len(best))
sizes = [cellsize[c] for c in best]
print("cell size min/median/max:", min(sizes), statistics.median(sizes), max(sizes), " singletons:",
      sum(1 for s in sizes if s == 1))
b = collections.Counter('1' if s == 1 else '2-5' if s <= 5 else '6-20' if s <= 20 else '21-100' if s <= 100 else '>100'
                        for s in sizes)
print("size buckets 2-5/6-20/21-100/>100:", b['2-5'], b['6-20'], b['21-100'], b['>100'])
sing = [(c, r) for c, r in best.items() if cellsize[c] == 1]
print("singletons by stratum:", dict(collections.Counter(c[1] for c, _ in sing)))
print("singletons by split:", dict(collections.Counter(r['split'] for _, r in sing)))
print("cells by split:", dict(collections.Counter(r['split'] for r in best.values())))
print("pages with >=2 condition labels among selected:", sum(1 for r in best.values() if len(r['labels']) >= 2))
print("strata with zero selected:", [s for s in PRIO if s not in {r['stratum'] for r in best.values()}])
print("rep classes with zero selected:",
      [x for x in ['native_ok', 'broken_text', 'scanned', 'vector_text', 'hybrid', 'blank', 'other']
       if x not in {r['rc'] for r in best.values()}])
print("selected by stratum:", dict(collections.Counter(r['stratum'] for r in best.values())))
print("selected by rep class:", dict(collections.Counter(r['rc'] for r in best.values())))
print("vector_text pages in corpus:", sum(1 for p in pp if p['kind'] == 'vector_text'), " vector_text cells:",
      sum(1 for c in best if c[3] == 'vector_text'), " singleton:",
      sum(1 for c in best if c[3] == 'vector_text' and cellsize[c] == 1))

# --- B-register claims
u = list(mu.values())
print("\nB-REGISTER CHECKS")
print("legacy_font_candidate label vs representation broken_text in manifest:",
      dict(collections.Counter((('legacy_font_candidate' in x['condition_labels']), x['representation_class'] == 'broken_text') for x in u)))
print("hybrid units:", sum(1 for x in u if x['representation_class'] == 'hybrid'), " blank units:",
      sum(1 for x in u if x['representation_class'] == 'blank'))
print("native_clean_control stratum units:", sum(1 for x in u if x['sampling_stratum'] == 'native_clean_control'),
      " 'native_clean_control' in any condition_labels:", sum(1 for x in u if 'native_clean_control' in x['condition_labels']))
print("hybrid units carrying native_ok label:",
      sum(1 for x in u if x['representation_class'] == 'hybrid' and 'native_ok' in x['condition_labels']),
      " blank w/ native_ok:", sum(1 for x in u if x['representation_class'] == 'blank' and 'native_ok' in x['condition_labels']))
SUBSET = {'scanned', 'broken_text', 'vector_text', 'legacy_font_candidate', 'native_clean_control'}
fv = [x for x in u if x['split'] in ('FIT', 'VALIDATION')]
lit = [x for x in fv if SUBSET & set(x['condition_labels'])]
strat = [x for x in fv if (SUBSET & set(x['condition_labels'])) or x['sampling_stratum'] == 'native_clean_control']
print("FIT+VALIDATION units:", len(fv), " literal oracle subset:", len(lit),
      dict(collections.Counter(x['split'] for x in lit)), " stratum-reading:", len(strat),
      dict(collections.Counter(x['split'] for x in strat)))
print("literal subset rep classes:", dict(collections.Counter(x['representation_class'] for x in lit)))
litset = {(x['document_id'], x['page_number']) for x in lit}
print("added by stratum reading, rep classes:",
      dict(collections.Counter(x['representation_class'] for x in strat if (x['document_id'], x['page_number']) not in litset)))


def d03(xs):
    return (sum(1 for x in xs if x['selection_rank'][0] in '0123'), len(xs))


print("rank first hex digit in 0-3: all units", d03(u), " literal subset", d03(lit),
      " first digit '0' count:", sum(1 for x in u if x['selection_rank'][0] == '0'))
print("HOLDOUT units in oracle literal subset:", sum(1 for x in lit if x['split'] == 'HOLDOUT'))
print("units carrying ocr_layer_proxy label:", sum(1 for x in u if 'ocr_layer_proxy' in x['condition_labels']),
      " as primary stratum:", sum(1 for x in u if x['sampling_stratum'] == 'ocr_layer_proxy'))
print("units with 'broken_text' in condition_labels:", sum(1 for x in u if 'broken_text' in x['condition_labels']),
      " with stratum broken_text:", sum(1 for x in u if x['sampling_stratum'] == 'broken_text'))
