# Phase-2 READ_ONLY final checks: (1) byte-hash the 194 local PDFs vs inventory (no rendering, no parsing);
# (2) structural feasibility of the declared sampling cell space. Writes nothing.
import csv, hashlib, os, re, collections, json, time


def rd(p):
    with open(p, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


inv = [r for r in rd('dataset/corpus_freeze/corpus_inventory.csv') if 'MISSING' not in r['document_id']]
t0 = time.time()
ok = bad = missing = size_bad = 0
bad_ids = []
for r in inv:
    loc = r['source_locator'].split(' (live_store root=')[0]
    if not os.path.exists(loc):
        missing += 1
        bad_ids.append((r['document_id'], 'path_missing'))
        continue
    h = hashlib.sha256()
    with open(loc, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    if os.path.getsize(loc) != int(r['file_size_bytes']):
        size_bad += 1
    if h.hexdigest() == r['pdf_sha256']:
        ok += 1
    else:
        bad += 1
        bad_ids.append((r['document_id'], 'hash_mismatch'))
print(f"PDF byte-hash check: docs={len(inv)} match={ok} mismatch={bad} path_missing={missing} size_mismatch={size_bad} ({time.time()-t0:.1f}s)")
print("problems:", bad_ids[:10])

# structural feasibility of (stratum x representation_class) pairs across ALL 37,917 pages (using frozen rules, re-implemented)
spec = json.load(open('configs/t0_4/sampling_spec.json', encoding='utf-8'))
PRIO = spec['sampling_stratum_priority']
pp = rd('dataset/corpus_freeze/page_profile.csv')
aux = collections.defaultdict(set)
for r in rd('dataset/corpus_gap_audit/condition_page_map.csv'):
    aux[(r['document_id'], int(r['page_index']))].add(r['condition'])
tables = {(r['document_id'], int(r['page_index'])) for r in rd('dataset/corpus_gap_audit/table_candidates.csv') if r['detector_status'] == 'CANDIDATE'}
lang = collections.defaultdict(set)
for r in rd('dataset/corpus_gap_audit/language_candidates.csv'):
    k = (r['document_id'], int(r['page_index']))
    if str(r['is_hindi_page']).lower() == 'true':
        lang[k].add('devanagari_candidate')
docs = {r['document_id']: r for r in rd('dataset/corpus_freeze/corpus_inventory.csv')}
KIND = {'digital': 'native_ok', 'broken_text': 'broken_text', 'scanned': 'scanned', 'vector_text': 'vector_text', 'hybrid': 'hybrid', 'blank': 'blank'}
MAP = {'devanagari_page': 'devanagari_candidate', 'native_page': 'native_ok', 'ocr_layer_page': 'ocr_layer_proxy', 'scanned_page': 'scanned', 'two_column_page': 'multi_column'}
pairs = collections.Counter()
for p in pp:
    d = docs[p['document_id']]
    key = (p['document_id'], int(p['physical_page']))
    labels = set(lang.get(key, set()))
    rc = KIND.get(p['kind'], 'other')
    labels.add(rc)
    if int(p['n_columns'] or 0) >= 2:
        labels.add('multi_column')
    if int(d['fiscal_year']) < 2015:
        labels.add('pre_2015')
    if p['render_mode_ocr_layer_indicator'] == 'True':
        labels.add('ocr_layer_proxy')
    if p['cid_or_broken_text_indicator'] == 'True':
        labels.add('legacy_font_candidate')
    if key in tables:
        labels.add('table_candidate')
    for v in aux.get(key, ()):
        labels.add(MAP.get(v, v))
    st = None
    for s in PRIO:
        if s == 'native_clean_control':
            if 'native_ok' in labels:
                st = s
                break
            continue
        if s == 'other' or s in labels:
            st = s
            break
    pairs[(st, rc)] += 1
reps = ['native_ok', 'broken_text', 'scanned', 'vector_text', 'hybrid', 'blank', 'other']
print(f"\n(stratum x representation_class) pairs declared: {len(PRIO)*len(reps)}; occurring on >=1 page in the frozen corpus: {len(pairs)}")
print("occurring pairs per representation class:", {r: sum(1 for (s, x) in pairs if x == r) for r in reps})
print("strata that can never be primary (structural, by construction of the predicates + priority):", [s for s in PRIO if not any(k[0] == s for k in pairs)])
n_issuers = 36
print(f"declared cells = {n_issuers}*{len(PRIO)}*2*3*{len(reps)} = {n_issuers*len(PRIO)*2*3*len(reps)}; "
      f"cells in structurally-impossible stratum x representation pairs = {n_issuers*2*3*(len(PRIO)*len(reps)-len(pairs))}")
