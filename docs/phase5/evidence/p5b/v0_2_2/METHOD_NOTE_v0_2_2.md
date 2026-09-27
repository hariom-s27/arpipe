# METHOD_NOTE_v0_2_2.md

## Change from v0.2

One ledger row was moved to frame status. The catalog builder now carries over catalog entries and records L1/L2 reconciliation findings without changing titles or classes. The leak check covers the title document and builder source. Reproducibility is checked against two copied runs.

## Observation identity

In accordance with protocol standards, observation identity is formally established prior to deduplication as the 5-tuple:
```
(document_id, page_0based, location, heading_text_verbatim, occurrence_index)
```
Where:
- `document_id`: Unique frozen document identifier matching `FIT_BLIND_MANIFEST.csv`.
- `page_0based`: Physical 0-based PDF page index ($0 \le \text{page\_0based} < \text{page\_count}$).
- `location`: Document partition, either `TOC` (Table of Contents) or `BODY`.
- `heading_text_verbatim`: Verbatim character sequence from the text layer or pass-1 extraction.
- `occurrence_index`: 1-based ordinal counter distinguishing legitimate multiple printed occurrences of identical text on the same page and location.

#### Deterministic Unique Identifier (`obs_id`)
```
obs_id = OBS_{document_id}_p{page_0based:04d}_{location}_occ{occurrence_index}_{sha256(heading_text_verbatim)[:8]}
```
Across all 3,216 rows in `TITLE_EVIDENCE_LEDGER_v0_2.csv`, exactly 3,216 unique `obs_id` values exist (100% collision-free).

## Quality-control fallback rule

> "If the independent human spot-check finds more than 5% of sampled rows wrong in page, text or class, the affected scope is redone under the lighter declared procedure (TOC + section-opening pages, verified page by page)."

## Coverage computation

The coverage line uses `PROVENANCE_v0_2_2.csv:sheets_viewed_logged` and `PROVENANCE_v0_2_2.csv:sheets_required`. Text-layer-only rows use `EVIDENCE_INDEX_v0_2_2.csv:page_provenance joined by obs_id to TITLE_EVIDENCE_LEDGER_v0_2_2.csv:assigned_class`.

Logged visual coverage of the underlying reading: 416/1610 contact sheets (25.84%); 38 EQUIVALENT/CONDITIONAL rows are text-layer-only.

## Known issues

- K-A — v0.2.1 FAILED: `V0_2_1_FAILURE_RECORD.csv` lists the zero-byte files: ["build_title_equivalence_v0_2_1.py", "METHOD_NOTE_v0_2_1.md", "run_leak_check_v0_2_1.py", "validate_integrity_v0_2_1.py"].
- K-B — INFERRED: an earlier audit executed the v0.2 builder inside `v0_2`, overwrote `TITLE_EQUIVALENCE_v0_2.md`, and edited it back. Its current bytes passed C5.
- K-C — INFERRED: earlier runs read Claude Code session logs under `C:\Users\hario\.claude\projects\` without disclosing that access in their reports.
- K-D — INFERRED: HISTORICAL: prior audit reported that v0.2 builder output differs from v0.2 .md; not re-run in P5-B.2.2 by design. The prior builder contained a document ID in a text string. F-BUILDER-DRIFT: RESOLVED AS K-I: expected list now taken from output/v0_2/HASHES_v0_2.txt; see K-I
- K-E — F-COUNTS: {"catalog_tag_counts": {"CONDITIONAL": 12, "EQUIVALENT": 21, "NOT EQUIVALENT BUT CONFUSABLE": 47, "UNRESOLVED": 1}, "p5_b2_report_correct": false, "p5_b2_report_counts": {"CONDITIONAL": 11, "EQUIVALENT": 24, "NOT EQUIVALENT BUT CONFUSABLE": 45, "UNRESOLVED": 1}}.
- K-F — 38 EQUIVALENT/CONDITIONAL rows are text-layer-only.
- K-G — Single-document CONDITIONAL titles needing a rules-reviewer decision: ["Management Discussion and Analysis", "MANAGEMENT DISCUSSION AND ANALYSIS", "5. Management Discussion and Analysis", "34. Management Discussion and Analysis Report", "21. Management Discussion and Analysis Report:", "17. MANAGEMENT DISCUSSION AND ANALYSIS REPORT:", "Management Discussion and Analysis Report", "Business Environment"].
- K-H — Attempt 1 stopped at INVALID_EXPECTED_HASH; attempt 2 stopped at OUTPUT_NOT_EMPTY; attempt 3 stopped at INPUT_HASH_MISMATCH. Read-only flags at C3: 10. Snapshot-only blocked-attempt folders: ["v0_2_2_attempt1_blocked", "v0_2_2_attempt2_blocked", "v0_2_2_attempt3_blocked", "v0_2_2_attempt4_blocked", "v0_2_2_attempt5_blocked"].
- K-J — VERIFIED by attempts 4–5: the v0.2 title list is a curated catalog and cannot be re-derived by grouping ledger headings. Attempt 4 began inventing a selection rule and stopped. Attempt 5 stopped at the first untraceable entry. This run carries over and reconciles the catalog; mismatches go to the rules reviewer.
- K-K — Class-count history: P5-B.2 reported 24/11/45/1; P5-B.2.1 and re-intake reported 28/6/46; verified catalog tags are 21/12/47/1. The first two are not catalog-tag counts. The majority-ledger-class split is recorded in `P5B22_SUMMARY.json`.
- K-L — Logged visual coverage is 416/1610 = 25.84%; an earlier document quoted 22.5% for the same numerator and denominator.
- K-I — VERIFIED by hashes; cause INFERRED: four v0.2 non-data files — `METHOD_NOTE_v0_2.md`, `build_title_equivalence.py`, `run_leak_check.py`, and `validate_integrity.py` — have LastWriteTime 2026-09-27 13:42 and differ from hashes printed in the P5-B.2 chat report while matching `output/v0_2/HASHES_v0_2.txt`, which passed C5. All v0.2 data inputs used here match both records. The rewriting session is not established. The copied rule and key text come from the current version.
