# Phase-2 audit script (READ ONLY). Run with the working directory at the repository root. Prints to stdout; writes nothing.
import csv, collections, json, re
def rd(p):
    with open(p, encoding='utf-8', newline='') as f: return list(csv.DictReader(f))
B='dataset/corpus_freeze/'
inv=rd(B+'corpus_inventory.csv'); sp=rd(B+'issuer_split.csv')
dev=rd(B+'development_manifest.csv'); val=rd(B+'validation_manifest.csv'); hol=rd(B+'holdout_manifest.csv')
ch=rd(B+'challenge_coverage_manifest.csv'); ro=rd(B+'annotation_roster.csv')
print("inventory rows:", len(inv))
present=[r for r in inv if r['openable']=='True' or r['sha256_verified']=='True']
print("cols sample:", [c for c in inv[0].keys() if 'split' in c.lower() or 'missing' in c.lower() or 'note' in c.lower()])
# split per issuer
isplit={r['issuer_id']:r['split'] for r in sp}
print("issuer_split counts:", collections.Counter(isplit.values()), "n_issuers", len(isplit))
# doc->split via company_id
miss=[r for r in inv if 'MISSING' in r['document_id'].upper()]
print("MISSING rows in inventory:", len(miss), "; example:", miss[0]['document_id'] if miss else None)
docs=[r for r in inv if 'MISSING' not in r['document_id'].upper()]
print("non-missing docs:", len(docs), "unique sha:", len({r['pdf_sha256'] for r in docs}), "pages:", sum(int(r['page_count']) for r in docs))
dsplit={r['document_id']:isplit.get(r['company_id']) for r in docs}
print("docs per split:", collections.Counter(dsplit.values()))
# per-issuer doc counts vs issuer_split num_documents
bad=[(r['issuer_id'],r['num_documents'],sum(1 for d in docs if d['company_id']==r['issuer_id'])) for r in sp if int(r['num_documents'])!=sum(1 for d in docs if d['company_id']==r['issuer_id'])]
print("issuer num_documents mismatches:", bad)
# manifests vs computed split
for name,m in [('development',dev),('validation',val),('holdout',hol)]:
    c=collections.Counter(r['split'] for r in m)
    mism=[r['document_id'] for r in m if dsplit.get(r['document_id'])!=r['split']]
    print(f"{name}_manifest: n={len(m)} split_col={dict(c)} dev_col={dict(collections.Counter(r['development'] for r in m))} split_mismatch_vs_issuer_split={len(mism)}")
devids={r['document_id'] for r in dev}; valids={r['document_id'] for r in val}; holids={r['document_id'] for r in hol}
print("dev∩val:",len(devids&valids)," dev∩hol:",len(devids&holids)," val∩hol:",len(valids&holids))
fitdocs={d for d,s in dsplit.items() if s=='FIT'}
print("FIT docs:",len(fitdocs)," dev⊆FIT:", devids<=fitdocs," FIT minus dev:", len(fitdocs-devids))
print("holdout_manifest ids == HOLDOUT docs:", holids=={d for d,s in dsplit.items() if s=='HOLDOUT'})
print("validation_manifest ids == VALIDATION docs:", valids=={d for d,s in dsplit.items() if s=='VALIDATION'})
# challenge composition
chc=collections.Counter(dsplit.get(r['document_id'],'?') for r in ch)
print("challenge (45) by split:", dict(chc), " overlap with development:", len({r['document_id'] for r in ch}&devids))
print("challenge HOLDOUT docs:", [r['document_id'] for r in ch if dsplit.get(r['document_id'])=='HOLDOUT'][:20])
roids={r['document_id'] for r in ro}
print("roster n=",len(ro)," roster⊆dev:", roids<=devids," roster split:", collections.Counter(dsplit.get(d) for d in roids))
# roster gold columns blank?
gold_cols=['mda_present','mda_start_page','mda_end_page','heading_text_verbatim','heading_form','boundary_ambiguous','ambiguity_reason','excluded_neighbours','language','per_page_text_quality','annotator_id','annotation_date','minutes_spent','saw_pipeline_output']
nonblank={c:sum(1 for r in ro if (r.get(c) or '').strip()) for c in gold_cols}
print("roster non-blank counts per gold/blinding column:", nonblank)
# issuers per split
ispl=collections.defaultdict(set)
for r in docs: ispl[dsplit[r['document_id']]].add(r['company_id'])
print("issuers per split (from docs):", {k:len(v) for k,v in ispl.items()}, " total:", len(set().union(*ispl.values())))
print("issuer overlap between splits:", [ (a,b,len(ispl[a]&ispl[b])) for a in ispl for b in ispl if a<b])
# historical labels KNOWN-FROM-PRIOR in notes
hl=[(r['document_id'],dsplit.get(r['document_id']),re.search(r'true_start=(\d+) true_end=(\d+)',r.get('notes','') or '')) for r in docs if 'KNOWN-FROM-PRIOR historical_ground_truth' in (r.get('notes') or '')]
print("docs with KNOWN-FROM-PRIOR historical label in inventory notes:", [(a,b,m.group(0) if m else None) for a,b,m in hl])
print("...by split:", collections.Counter(b for a,b,m in hl))
