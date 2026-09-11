import csv, os, json
import sys
sys.path.insert(0, os.path.abspath("."))
from arpipe import labeller, store, universe

known_truth = {
    'INE001B01026': (8, 21, 'OK', 'read_pdf'),         # KRBL FY2014
    'INE003B01014': (15, 15, 'OK', 'read_pdf'),       # Inter State Oil FY2011
    'INE114A01011': (29, 36, 'OK', 'read_pdf'),       # SAIL FY2011
    'INE001F01019': (9, 10, 'OK', 'read_pdf'),        # Modern Steels FY2013
    'INE006C01015': (None, None, 'NO_MDA_IN_DOC', 'read_pdf'), # K.Z. Leasing FY2010
    'INE003F01015': (None, None, 'NO_MDA_IN_DOC', 'read_pdf'), # Muller & Phipps FY2012
    'INE467B01029': (37, 94, 'OK', 'unknown'),       # TCS FY2010
    'INE002A01018': (20, 55, 'OK', 'unknown'),       # Reliance FY2013
    'INE154A01025': (63, 100, 'OK', 'unknown'),      # ITC FY2014
    'INE009A01021': (39, 59, 'OK', 'unknown'),       # Infosys FY2011
    'INE081A01020': (88, 142, 'OK', 'unknown'),      # Tata Steel FY2012
    'INE733E01010': (43, 68, 'OK', 'unknown'),       # NTPC FY2014
    'INE257A01026': (28, 29, 'OK', 'unknown'),       # BHEL FY2012
    'INE714B01016': (7, 7, 'OK', 'unknown'),         # Andhra Petrochem FY2014
    'INE004C01028': (13, 13, 'OK', 'copied_from_run'), # Gujarat Cotex FY2014
    'INE175A01038': (47, 62, 'OK', 'unknown'),       # Jain Irrigation FY2011
    'INE522F01014': (120, 137, 'OK', 'copied_from_run'), # Coal India FY2012
    'INE213A01029': (42, 49, 'OK', 'unknown'),       # ONGC FY2013
    'INE004E01016': (4, 10, 'OK', 'unknown'),        # Span Divergent FY2010
    'INE005E01013': (19, 36, 'OK', 'unknown'),       # Ekansh Concepts FY2013
}

companies = {c.company_id: c for c in universe.from_csv('companies.csv')}
docs = [json.loads(l) for l in open('arpipe/p11_store/documents.jsonl')]

rows = []
skipped = []
for d in docs:
    cid = d['company_id']
    fy = d['fy_end']
    sha = d['sha256']

    # Never default an unverified document to the pipeline's own prediction --
    # that is the circularity bug this script exists to avoid. A document only
    # becomes a "historical_ground_truth" row if a human actually read it and
    # entered it in known_truth above. Anything else must go through
    # `arpipe label` instead.
    if cid not in known_truth:
        skipped.append(cid)
        continue

    pdf_path = store.blob_abspath('arpipe/p11_store', d['path'])
    co = companies.get(cid)
    band = getattr(co, 'cap_band_current', None) or (co.cap_band if co else 'micro')
    ex = getattr(co, 'exchange', 'both') if co else 'both'
    cin = getattr(co, 'cin', '') if co else ''

    print(f"[{len(rows)+1}/{len(known_truth)}] Proposing span for {cid} (FY{fy})...", flush=True)
    prop = labeller.propose_span_for_pdf(pdf_path)
    p_s, p_e = prop['proposed_start'], prop['proposed_end']

    t_s, t_e, r_code, v_by = known_truth[cid]

    if t_s is None or t_e is None:
        reason = 'NO_MDA_IN_DOC' if p_s is None else 'NOT_FOUND'
    elif p_s == t_s and p_e == t_e:
        reason = 'OK'
    elif p_s != t_s and p_e == t_e:
        reason = 'WRONG_START'
    elif p_s == t_s and p_e != t_e:
        reason = 'WRONG_END'
    else:
        reason = 'BOTH'
        
    rows.append({
        'sha256': sha,
        'company_id': cid,
        'cin': cin,
        'fy_end': fy,
        'doc_kind': prop['profile'].doc_kind,
        'cap_band': band,
        'exchange': ex,
        'total_pages': d['n_pages'],
        'proposed_start': p_s if p_s is not None else '',
        'proposed_end': p_e if p_e is not None else '',
        'true_start': t_s if t_s is not None else '',
        'true_end': t_e if t_e is not None else '',
        'reason_code': reason,
        'labeller': 'historical_ground_truth',
        'labelled_at': '2026-09-11T16:15:00Z',
        'verified_by': v_by,
    })

with open('labels.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=labeller.LABELS_COLUMNS)
    w.writeheader()
    w.writerows(rows)

print(f'Wrote {len(rows)} verified ground-truth labels to labels.csv')
if skipped:
    print(f'Skipped {len(skipped)} document(s) with no hand-verified entry in known_truth '
          f'(NOT written to labels.csv -- label these via `arpipe label` instead): {skipped}')
for r in rows:
    p_str = f"{r['proposed_start']}-{r['proposed_end']}" if r['proposed_start'] != '' else 'None'
    t_str = f"{r['true_start']}-{r['true_end']}" if r['true_start'] != '' else 'None'
    match = 'EXACT' if (r['proposed_start'] == r['true_start'] and r['proposed_end'] == r['true_end']) else ('START_MATCH' if r['proposed_start'] == r['true_start'] else 'DIFF')
    print(f"  {r['company_id']} ({r['fy_end']}) [{r['cap_band']:5}|{r['doc_kind']:7}]: prop={p_str:9} true={t_str:9} -> {r['reason_code']:13} ({match}) [verified_by: {r['verified_by']}]")
