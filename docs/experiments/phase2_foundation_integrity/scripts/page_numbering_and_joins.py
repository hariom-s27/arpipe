# Phase-2 audit script (READ ONLY). Run with the working directory at the repository root. Prints to stdout; writes nothing.
import csv, collections
def rd(p):
    with open(p, encoding='utf-8', newline='') as f: return list(csv.DictReader(f))
pp=rd('dataset/corpus_freeze/page_profile.csv')
print("page_profile cols:", list(pp[0].keys())); print("rows:", len(pp))
mn=collections.defaultdict(lambda:10**9); mx=collections.defaultdict(int); cnt=collections.Counter()
for r in pp:
    d=r['document_id']; p=int(r['physical_page']); mn[d]=min(mn[d],p); mx[d]=max(mx[d],p); cnt[d]+=1
print("physical_page min per doc:", collections.Counter(mn.values()))
print("docs where max-min+1==count:", sum(1 for d in cnt if mx[d]-mn[d]+1==cnt[d]), "/", len(cnt))
if 'page_index' in pp[0]: print("page_index present in page_profile")
print("kind counts:", collections.Counter(r['kind'] for r in pp))
for col in ['cid_or_broken_text_indicator','render_mode_ocr_layer_indicator']:
    print(col, collections.Counter(r[col] for r in pp))
print("cid_or_broken_text_indicator vs kind==broken_text crosstab:", collections.Counter((r['cid_or_broken_text_indicator'], r['kind']=='broken_text') for r in pp))
G='dataset/corpus_gap_audit/'
cpm=rd(G+'condition_page_map.csv'); print("\ncondition_page_map cols:", list(cpm[0].keys()), "rows:", len(cpm))
print("conditions:", collections.Counter(r['condition'] for r in cpm))
mn2=collections.defaultdict(lambda:10**9)
for r in cpm: mn2[r['document_id']]=min(mn2[r['document_id']],int(r['page_index']))
print("condition_page_map page_index min per doc:", collections.Counter(mn2.values()))
tc=rd(G+'table_candidates.csv'); lc=rd(G+'language_candidates.csv')
print("table_candidates rows", len(tc), "cols", list(tc[0].keys()), "detector_status:", collections.Counter(r.get('detector_status') for r in tc))
print("language_candidates rows", len(lc), "cols", list(lc[0].keys()))
print("min page_index tc/lc:", min(int(r['page_index']) for r in tc), min(int(r['page_index']) for r in lc))
# check join overlap: every (doc,page_index) in aux exists as (doc,physical_page) in profile?
prof={(r['document_id'],int(r['physical_page'])) for r in pp}
for nm,rows in [('condition_page_map',cpm),('table_candidates',tc),('language_candidates',lc)]:
    miss=sum(1 for r in rows if (r['document_id'],int(r['page_index'])) not in prof)
    print(f"{nm}: keys not found in page_profile via (doc,page_index==physical_page): {miss} of {len(rows)}")
