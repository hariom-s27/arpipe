# Phase-2 audit script (READ ONLY). Run with the working directory at the repository root. Prints to stdout; writes nothing.
import csv, collections, json
def rd(p):
    with open(p, encoding='utf-8', newline='') as f: return list(csv.DictReader(f))
G='dataset/corpus_gap_audit/'
rec=rd(G+'reconciled/gap_audit_document_reconciled.csv')
print("reconciled doc csv: rows",len(rec)); print("cols:", list(rec[0].keys()))
inv={r['document_id']:r for r in rd('dataset/corpus_freeze/corpus_inventory.csv')}
print()
c=collections.Counter((r['document_representation'], inv[r['document_id']]['doc_kind_prior']) for r in rec if r['document_id'] in inv)
print("CROSSTAB document_representation (T0.1R) x doc_kind_prior (T0 inventory / detector NEEDS_OCR-fraction):")
for k,v in sorted(c.items()): print("  ",k,v)
print()
def num(r,k):
    try: return int(float(r[k]))
    except: return 0
for col in ['scanned_page_count','ocr_page_count','legacy_candidate_page_count','devanagari_page_count','hidden_text_candidate_page_count','duplicate_text_candidate_page_count','table_candidate_page_count','two_column_page_count','multi_column_page_count']:
    if col in rec[0]:
        print(f"{col}: docs>0 = {sum(1 for r in rec if num(r,col)>0)} ; sum_pages = {sum(num(r,col) for r in rec)}")
print()
print("document_representation counts:", collections.Counter(r['document_representation'] for r in rec))
print("docs with NATIVE & legacy_candidate_page_count>0:", sum(1 for r in rec if r['document_representation']=='NATIVE' and num(r,'legacy_candidate_page_count')>0))
print("docs with NATIVE & scanned_page_count>0:", sum(1 for r in rec if r['document_representation']=='NATIVE' and num(r,'scanned_page_count')>0))
print("docs scanned_page_count>0 by representation:", collections.Counter(r['document_representation'] for r in rec if num(r,'scanned_page_count')>0))
