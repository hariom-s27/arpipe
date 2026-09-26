# ARPipe Phase-5 corpus-frame metadata check v0

**Document status:** `DRAFT_PENDING_PILOT`

**Execution date:** 2026-09-27

**PROPOSED.** This is a metadata-only readiness check for FIT and VALIDATION. It is not
annotation, corpus repair, a selector draw, or a claim that any candidate has been
confirmed through document reading.

## 1. Access boundary

**VERIFIED.** FIT/VALIDATION issuer IDs were first selected from
`dataset/corpus_freeze/issuer_split.csv`; only their document IDs were then joined to
`corpus_inventory.csv`. `page_profile.csv` was restricted by that approved ID set before
`page_count` or `script` was read. No HOLDOUT row or PDF content was read.

**VERIFIED.** PDF handling was limited to byte existence and SHA-256 hashing. No PDF was
opened, parsed, rendered, searched, or text-extracted. Predictions, labels, evaluation
outputs, reports, and P5-B artifacts were not consulted.

## 2. Non-DEVELOPMENT FIT roster and byte check

**DERIVED.** The exact roster rule is: join
`dataset/corpus_freeze/corpus_inventory.csv.company_id` to
`dataset/corpus_freeze/issuer_split.csv.issuer_id`; retain `split = FIT`; remove every
`document_id` present in `development_manifest.csv`; remove IDs ending `_MISSING`.

**DERIVED.** Result: **32 documents across 16 issuers**. The count is reported evidence,
not a selector constant.

**VERIFIED.** Tried live-store root
`D:/sem_iitk/sem9/thesis/sep_week1/arpipe-0.1.0/live_store`. For each roster SHA, the
checked path was `blobs/<sha[0:2]>/<sha[2:4]>/<sha>.pdf`.

| Check | Result |
|---|---:|
| **VERIFIED.** roster documents | 32 |
| **VERIFIED.** file exists and SHA-256 matches manifest | 32 |
| **VERIFIED.** missing file | 0 |
| **VERIFIED.** hash mismatch | 0 |

## 3. Script metadata and bilingual premise

**VERIFIED.** Across executable FIT and VALIDATION IDs, every `page_profile.csv` script
label is either `latin` or `unknown`: 27,189 page rows are `latin` and 575 are `unknown`.
These detector labels do not establish the natural-language content of a document.

**VERIFIED.** In top-level
`dataset/corpus_gap_audit/condition_document_map.csv`, all six FIT rows for issuer ID
`INE008A01015` (IDBI Bank; fiscal years 2012, 2013, 2017, 2018, 2024, 2025) have
`bilingual_candidate = NOT_OBSERVED` and `verification_status = NOT_REVIEWED`.

**INFERRED.** Author-supplied context says IDBI is government-controlled, bilingual
reports are therefore likely, and the frozen detectors cannot see legacy-encoded Hindi.
This is not upgraded to a verified corpus fact.

## 4. Short/stub candidates

**DERIVED.** The threshold was `page_count < 20`, plus any existing `STUB` flag in
`dataset/corpus_gap_audit/reconciled/gap_audit_document_reconciled.csv`. Exactly these
FIT/VALIDATION candidates were found:

| Status | document_id | split | page_count | development status | metadata flag |
|---|---|---|---:|---|---|
| `CANDIDATE` | `INE00FF01025_2015` | FIT | 1 | DEVELOPMENT | `STUB` |
| `CANDIDATE` | `INE00LO01017_2015` | FIT | 2 | non-DEVELOPMENT; pilot pool | `STUB` |

**INFERRED.** `INE00FF01025_2015` was reported `NOT_AN_ANNUAL_REPORT` by the isolated
P5-B reading (author-supplied). This task did not inspect that artifact or the PDF and
does not treat the report as verified.

**PROPOSED.** Candidates stay in their frozen corpus roles. Future Gold applies the
written protocol, including `ABSENT / NOT_AN_ANNUAL_REPORT`, without replacing bytes or
prejudging either candidate.

## 5. Use and limits

**DERIVED.** The 32-document/16-issuer frame is the only permitted pool for the proposed
PILOT and disjoint RETEST slices. No slice was drawn here.

**PROPOSED.** These metadata checks establish availability and identify review
candidates only. They do not establish bilingual prevalence, annual-report identity,
MD&A presence, span boundaries, or Gold quality.
