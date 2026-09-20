# Phase-2 audit script (READ ONLY). Run with the working directory at the repository root. Prints to stdout; writes nothing.
import csv, collections, re
def rd(p):
    with open(p, encoding='utf-8', newline='') as f: return list(csv.DictReader(f))
B='dataset/corpus_freeze/'
inv=rd(B+'corpus_inventory.csv'); sp=rd(B+'issuer_split.csv')
isplit={r['issuer_id']:r['split'] for r in sp}
sha2doc={}
for r in inv: sha2doc[r['pdf_sha256']]=r
def split_of(sha):
    r=sha2doc.get(sha)
    if r is None: return 'NOT_IN_T0_INVENTORY'
    if 'MISSING' in r['document_id'].upper(): return 'T0_MISSING_'+str(isplit.get(r['company_id'],'UNASSIGNED'))
    return isplit.get(r['company_id'],'UNASSIGNED')
L=rd('labels.csv')
print("labels.csv (20) mapping to T0 inventory by sha256:")
c=collections.Counter(split_of(r['sha256']) for r in L); print(dict(c))
for r in L:
    s=sha2doc.get(r['sha256'])
    print("  ", r['sha256'][:10], r['company_id'], r['fy_end'], r['true_start'], r['true_end'], '->', (s['document_id'] if s else None), split_of(r['sha256']))
for name in ['labels_fit_queue.csv','labels_holdout_queue.csv','to_label.csv','labels_fit.csv']:
    R=rd(name)
    c=collections.Counter(split_of(r['sha256']) for r in R)
    print(f"\n{name}: n={len(R)} -> T0 split of each row (by sha256):", dict(c))
    if 'split_seed' in R[0]: print("   split_seed values:", collections.Counter(r['split_seed'] for r in R))
# labels_holdout.csv raw
print("\n--- labels_holdout.csv raw head:")
print(open('labels_holdout.csv',encoding='utf-8').read()[:400])
print("\n--- eval_holdout_log.csv:")
print(open('eval_holdout_log.csv',encoding='utf-8').read()[:1200])
