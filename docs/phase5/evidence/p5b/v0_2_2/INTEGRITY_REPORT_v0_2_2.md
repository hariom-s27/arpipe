# INTEGRITY_REPORT_v0_2_2.md

Verdict: **P5_B22_PASS_WITH_REVIEW_ITEMS**

| Check | Expected | Measured | Status |
|---|---|---|---|
| G1 | {"frame_rows": 1, "ledger_rows": 3215, "source_rows": 3216} | {"frame_rows": 1, "ledger_rows": 3215, "source_rows": 3216, "sum": 3216} | PASS |
| G2 | {"evidence_other_fields_differences": 0, "only_removed_obs_id": "OBS_INE00FF01025_2015_p0000_BODY_occ1_dd9826bd", "provenance_byte_copy": true, "retained_field_differences": 0} | {"evidence_other_fields_differences": 0, "provenance_byte_copy": true, "removed_obs_ids": ["OBS_INE00FF01025_2015_p0000_BODY_occ1_dd9826bd"], "retained_field_differences": 0} | PASS |
| G3 | {"documents": 60, "manifest_hash_mismatches": 0} | {"documents": 60, "manifest_hash_mismatches": {}} | PASS |
| G4 | {"key_duplicates": 0, "obs_id_duplicates": 0, "out_of_range_pages": 0} | {"key_duplicates": 0, "obs_id_duplicates": 0, "out_of_range_pages": 0} | PASS |
| G5 | {"distinct_pngs": 146, "missing_equivalent_conditional": 0, "png_hash_mismatches": 0, "rows": 259, "types": {"FRAME_STATUS_EVIDENCE": 1, "STRUCTURAL_TITLE_EVIDENCE": 258}} | {"distinct_pngs": 146, "missing_equivalent_conditional": 0, "png_hash_mismatches": 0, "rows": 259, "types": {"FRAME_STATUS_EVIDENCE": 1, "STRUCTURAL_TITLE_EVIDENCE": 258}} | PASS |
| G6 | {"class_split": {"CONDITIONAL": 12, "EQUIVALENT": 21, "NOT EQUIVALENT BUT CONFUSABLE": 47}, "entries": 80} | {"class_split": {"CONDITIONAL": 12, "EQUIVALENT": 21, "NOT EQUIVALENT BUT CONFUSABLE": 47}, "entries": 80} | PASS |
| G7 | {"CONDITIONAL": 66, "EQUIVALENT": 150, "NOT EQUIVALENT BUT CONFUSABLE": 2999} | {"CONDITIONAL": 66, "EQUIVALENT": 150, "NOT EQUIVALENT BUT CONFUSABLE": 2999} | PASS |
| G8 | {"each_has_match_level_and_class_status": true, "entries_reconciled": 80} | {"class_status_counts": {"AGREES": 40, "CONFLICT": 11, "NONE": 29}, "entries_reconciled": 80, "majority_ledger_class_split": {"CONDITIONAL": 1, "EQUIVALENT": 16, "NONE": 29, "NOT EQUIVALENT BUT CONFUSABLE": 34}, "match_level_counts": {"L1": 26, "L2": 25, "NONE": 29}, "overlap_entries": 24, "unmatched_ledger_rows_by_class": {"CONDITIONAL": 65, "EQUIVALENT": 145, "NOT EQUIVALENT BUT CONFUSABLE": 2941}} | PASS |
| G9 | {"blocking_hits": 0} | {"blocking_hits": 0, "possible_hits": []} | PASS |
| G10 | {"historical_finding_recorded": true, "reproducible": true} | {"F-V02-REPRO": "HISTORICAL: prior audit reported that v0.2 builder output differs from v0.2 .md; not re-run in P5-B.2.2 by design.", "reproducible": true} | PASS |
| G11 | {"catalog_class_tags_counted": true, "report_24_11_45_1_assessed": true} | {"catalog_tag_counts": {"CONDITIONAL": 12, "EQUIVALENT": 21, "NOT EQUIVALENT BUT CONFUSABLE": 47, "UNRESOLVED": 1}, "p5_b2_report_correct": false, "p5_b2_report_counts": {"CONDITIONAL": 11, "EQUIVALENT": 24, "NOT EQUIVALENT BUT CONFUSABLE": 45, "UNRESOLVED": 1}} | PASS |
| G12 | {"zero_byte_files": 0} | {"zero_byte_files": []} | PASS |

## Reconciliation findings

- Match levels: `{"L1": 26, "L2": 25, "NONE": 29}`
- Class status: `{"AGREES": 40, "CONFLICT": 11, "NONE": 29}`
- Overlap entries: `24`
- Unmatched ledger rows: `{"CONDITIONAL": 65, "EQUIVALENT": 145, "NOT EQUIVALENT BUT CONFUSABLE": 2941}`
- Majority-ledger-class split: `{"CONDITIONAL": 1, "EQUIVALENT": 16, "NONE": 29, "NOT EQUIVALENT BUT CONFUSABLE": 34}`
