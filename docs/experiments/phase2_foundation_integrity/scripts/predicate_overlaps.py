# Phase-2 READ_ONLY predicate-overlap and evidence-level analysis. Reads frozen CSV/JSON only; writes nothing.
import csv, json, collections, glob


def rd(p):
    with open(p, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


pp = rd('dataset/corpus_freeze/page_profile.csv')
kind = {(r['document_id'], int(r['physical_page'])): r['kind'] for r in pp}
cpm = rd('dataset/corpus_gap_audit/condition_page_map.csv')
auxs = collections.defaultdict(set)
for r in cpm:
    auxs[(r['document_id'], int(r['page_index']))].add(r['condition'])
print("=== page-level: detector kind (T0 page_profile) x T0.1 condition_page_map label ===")
kinds = ['digital', 'scanned', 'broken_text', 'hybrid', 'blank', 'vector_text']
for cond in ['native_page', 'scanned_page', 'ocr_layer_page', 'two_column_page', 'devanagari_page']:
    c = collections.Counter(kind[k] for k, v in auxs.items() if cond in v)
    print(f"{cond:16s} total={sum(c.values()):6d}  by detector kind:", {k: c.get(k, 0) for k in kinds})
print()
print("pages by detector kind:", dict(collections.Counter(r['kind'] for r in pp)))
none = collections.Counter(kind[k] for k in kind if not auxs.get(k))
print("pages with NO T0.1 condition label, by kind:", dict(none))
nat = {k for k, v in auxs.items() if 'native_page' in v}
dig = {k for k, v in kind.items() if v == 'digital'}
print("digital(detector) & native_page:", len(dig & nat), " digital only:", len(dig - nat), " native_page only:", len(nat - dig))
sc_t = {k for k, v in auxs.items() if 'scanned_page' in v}
sc_d = {k for k, v in kind.items() if v == 'scanned'}
print("scanned: detector-kind", len(sc_d), " T0.1 scanned_page", len(sc_t), " intersection", len(sc_d & sc_t),
      " detector-only", len(sc_d - sc_t), " T0.1-only", len(sc_t - sc_d))
print("  T0.1-only scanned_page pages by detector kind:", dict(collections.Counter(kind[k] for k in sc_t - sc_d)))
oc_t = {k for k, v in auxs.items() if 'ocr_layer_page' in v}
oc_p = {(r['document_id'], int(r['physical_page'])) for r in pp if r['render_mode_ocr_layer_indicator'] == 'True'}
print("ocr_layer: T0.1 ocr_layer_page", len(oc_t), " page_profile render_mode indicator", len(oc_p), " equal sets:", oc_t == oc_p)
print("  ocr_layer_page pages by detector kind:", dict(collections.Counter(kind[k] for k in oc_t)))
print("  ocr_layer_page & scanned_page overlap:", len(oc_t & sc_t))

print("\n=== columns: n_columns distribution (detector) vs T0.1 two_column_page ===")
nc = collections.Counter(int(r['n_columns'] or 0) for r in pp)
print("n_columns dist:", dict(sorted(nc.items())))
two = {k for k, v in auxs.items() if 'two_column_page' in v}
n2 = {(r['document_id'], int(r['physical_page'])) for r in pp if int(r['n_columns'] or 0) == 2}
nge2 = {(r['document_id'], int(r['physical_page'])) for r in pp if int(r['n_columns'] or 0) >= 2}
print("T0.1 two_column_page:", len(two), " detector n_columns==2:", len(n2), " n_columns>=2:", len(nge2),
      " two_column_page == (n_columns==2)?", two == n2, " two_column_page subset of (n>=2)?", two <= nge2)
rec = rd('dataset/corpus_gap_audit/reconciled/gap_audit_document_reconciled.csv')
n = lambda r, k: int(float(r[k] or 0))
print("T0.1 multi_column_page_count total (doc CSV):", sum(n(r, 'multi_column_page_count') for r in rec),
      " two_column_page_count total:", sum(n(r, 'two_column_page_count') for r in rec),
      " one_column total:", sum(n(r, 'one_column_page_count') for r in rec))
print("detector pages n_columns>=3:", sum(v for k, v in nc.items() if k >= 3), " n_columns>=2:", sum(v for k, v in nc.items() if k >= 2))

print("\n=== document-level legacy: T0.1 legacy_candidate_page_count vs detector broken_text pages ===")
bt = collections.Counter(r['document_id'] for r in pp if r['kind'] == 'broken_text')
docs_bt = set(bt)
docs_leg = {r['document_id'] for r in rec if n(r, 'legacy_candidate_page_count') > 0}
print("docs with >=1 broken_text page (detector):", len(docs_bt), " pages:", sum(bt.values()))
print("docs with legacy_candidate_page_count>0 (T0.1/T0.3A):", len(docs_leg), " pages:", sum(n(r, 'legacy_candidate_page_count') for r in rec))
print("doc overlap:", len(docs_bt & docs_leg), " detector-only:", len(docs_bt - docs_leg), " T0.1-only:", len(docs_leg - docs_bt))
eq = sum(1 for r in rec if n(r, 'legacy_candidate_page_count') == bt.get(r['document_id'], 0))
print("docs where legacy_candidate_page_count == broken_text page count:", eq, "/", len(rec))
inv = {r['document_id']: r for r in rd('dataset/corpus_freeze/corpus_inventory.csv')}
leg_col = [c for c in inv[next(iter(inv))].keys() if 'legacy' in c.lower()]
print("T0 inventory legacy columns:", leg_col)
for c in leg_col:
    print("  ", c, "True count:", sum(1 for r in inv.values() if str(r.get(c)).strip() == 'True'))

print("\n=== evidence / verification status values across frozen T0.1 page-level files ===")
for f in ['dataset/corpus_gap_audit/condition_page_map.csv', 'dataset/corpus_gap_audit/table_candidates.csv',
          'dataset/corpus_gap_audit/language_candidates.csv', 'dataset/corpus_gap_audit/manual_review_results.csv',
          'dataset/corpus_gap_audit/reconciled/manual_review_results_reconciled.csv',
          'dataset/corpus_gap_audit/reconciled/gap_audit_document_reconciled.csv']:
    rows = rd(f)
    for col in ['verification_status', 'candidate_status', 'detector_status', 'evidence_status', 'review_status',
                'reviewer_type', 'reviewer', 'human_reviewed']:
        if col in rows[0]:
            print(f"{f.split('/')[-1]:44s} {col:20s}", dict(collections.Counter(r[col] for r in rows).most_common(6)))
print("page_profile evidence_status:", dict(collections.Counter(r['evidence_status'] for r in pp).most_common(5)))
print("\nprevalence of proxy flags among ALL 37,917 pages: table_candidate CANDIDATE rows =",
      len(rd('dataset/corpus_gap_audit/table_candidates.csv')),
      f"({len(rd('dataset/corpus_gap_audit/table_candidates.csv'))/len(pp):.1%})")
print("docs flagged: annexure_candidate", sum(1 for r in rec if r['annexure_candidate'] == 'True'),
      " toc_candidate", sum(1 for r in rec if r['toc_candidate'] == 'True'),
      " combined_mdna_candidate", sum(1 for r in rec if r['combined_mdna_candidate'] == 'True'), "of", len(rec))
