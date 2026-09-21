# Phase 2.1 — Provenance Corrections & Historical Integrity Ledger

**Status:** authoritative downstream correction ledger  
**Repository Basis:** `D:\sem_iitk\sem9\thesis\sep_week1\arpipe-phase2.1-foundation-normalization`  
**Base Commit:** `03a63f5d7d79bac6a0bab0ffc33af42004e78935`  
**Governing Rule:** historical frozen objects and Phase-1 reports remain immutable; corrections are recorded downstream without modifying historical objects.

---

## 1. Executive Summary & Policy

Phase 2 identified that historical prose, task prompts, and artifact tables occasionally outran underlying Git objects and byte evidence (Root Cause RC1). This ledger records objective corrections for all identified provenance, SHA-256, attribution, and serialization discrepancies across the T0–T0.4 and Phase-1 records.

In accordance with Phase 2.1 safety rules:
- **No historical object is modified or re-committed.**
- **No historical Git tree or hash is rewritten.**
- **All corrections are binding on downstream consumers (Phase 2.1+, Phase 3+, Gold, and final thesis documentation).**

---

## 2. Comprehensive Provenance Correction Ledger

| Change ID | Finding ID | Historical Artifact & Location | Original Statement / Recorded Value | Corrected Interpretation & Normative Value | Verified Evidence & Exact Source | Correction Type | Scientific & Downstream Impact | Historical Artifact Changed? | Effective Version |
|---|---|---|---|---|---|---|---|:---:|---|
| **PC-01** | P2-01 | Task milestone registry & task prompt text | T0.1R SHA recorded as 41 hex characters: `...df33db7dd...` | Correct 40-character commit SHA: `879762a2f236b3aaa6df33b7ddacc60c01d633c1` (`...df33b7dd...`, exactly one `d` fewer) | 7-character prefix `879762a` uniquely resolves to `879762a2f236b3aaa6df33b7ddacc60c01d633c1` in repository `sep_week1/arpipe-0.1.0`. It is the tip of branch `t0.1-reconcile` and sole parent of T0.2 (`ef2e8c5`). | OBJECTIVE_CORRECTION | Eliminates resolution failures in automated scripts; ensures correct lineage traversal. | **NO** | 2.1.0 |
| **PC-02** | P2-02 | `docs/experiments/T0.4_ocr_benchmark_preregistration.md` & `T0.4_p-x1_reuse_audit.md` | Described as "frozen before benchmark execution" at `b937b58` | Documents were amended at `33ba76a` (vector_text route and held-out wording clarification). Normative text is identified by Git blobs at closure commit `63e3c04`. Configuration freeze (`artifacts/t0_4/config_hashes.json`) hashes the 12 JSON configs; Markdown protocol files are tracked by Git blob identity. | Closure audit (`63e3c04`) sections 1 and 9; Git diff between `b937b58` and `33ba76a`. | DOCUMENTATION_CLARIFICATION | Clarifies configuration freeze identity: JSON configs are content-hashed; Markdown protocols are versioned by commit/blob. | **NO** | 2.1.0 |
| **PC-03** | P2-14 | `dataset/corpus_freeze/corpus_inventory.csv` column `file_size_bytes` | `file_size_bytes` copied from fetch manifest differs from actual PDF blob size on disk for 83 of 194 documents (deltas: -7.29 MB to +15.48 MB, median +222 KB). | `file_size_bytes` in the inventory is fetch-stage metadata and MUST NOT be used as a file-integrity check. Cryptographic SHA-256 is the sole normative identity (194/194 match). | Read-only byte hashing of all 194 stored PDFs in `live_store` matches recorded `sha256` 194/194; file size differences verified. | DOCUMENTATION_CLARIFICATION | Prevents false integrity alerts from file size discrepancies; reinforces SHA-256 as unique byte authority. | **NO** | 2.1.0 |
| **PC-04** | P2-15 | T0 reports (`freeze_protocol.md`) vs `artifacts/t0_4/benchmark_manifest.json` | T0 states that the 14 missing records are "excluded from every split". | In T0.4 Track B, 8 records are `UNASSIGNED_HISTORICAL`, while 6 inherit their issuer's administrative split under role `INPUT_UNAVAILABLE` (FIT: 2, VALIDATION: 4). All 14 remain completely excluded from executable partitions. Document counts (194 executable = 92 FIT + 48 VAL + 54 HOLDOUT) are 100% invariant. | T0.4 Track-B manifest rows for missing PDFs; T0 inventory 14 missing rows. | DOCUMENTATION_CLARIFICATION | Harmonizes administrative issuer association with partition exclusion semantics; zero effect on executable dataset. | **NO** | 2.1.0 |
| **PC-05** | P2-20 | `configs/audit_config.sha256` | Recorded SHA: `8e26bec124a3480678d2b963bfbf568d7e2e38c92b2173ea3f63c8be202e86ee` vs Git blob `a3a575cda1ec7345638c4b14d241775f0a359216cf275da909e46a78280629bc`. | The recorded SHA `8e26bec1...` exactly matches the Git blob bytes plus one trailing newline (`\n`). The dataset copy in `dataset/corpus_gap_audit/audit_config.json` is CRLF and matches its `.sha256` file (`65ed1a7e...`) pinned by T0.1R `raw_input_manifest.json`. | Reproduction script `verify_recorded_hashes.py`; `git cat-file -p` of blob plus newline. | OBJECTIVE_CORRECTION | Explains hash-check failure on historical config file without alleging file corruption; dataset pinned copy verified intact. | **NO** | 2.1.0 |
| **PC-06** | P2-21 | `docs/experiments/PHASE1_FROZEN_FOUNDATION_VERIFICATION.md` Artifact Table | 10 of 27 displayed SHA-256 hashes marked "Matches / VERIFIED" do not match the cited blobs at commit `63e3c04`. | The 10 strings are transcription/prefix errors in the Phase-1 report. The cited pin manifests (`raw_input_manifest.json`, `final_closure_audit.json`) and Phase-2 findings JSON contain the correct, verified hashes. The Phase-1 report table cannot be cited as a normative hash authority. | `PHASE2_FOUNDATION_INTEGRITY_FINDINGS.json` hash registry (252 blobs checked, 155/156 manifest pairs verified); `verify_recorded_hashes.py`. | OBJECTIVE_CORRECTION | Restores chain of custody; downstream consumers must cite the Phase-2 findings JSON hash registry rather than the Phase-1 report table. | **NO** | 2.1.0 |
| **PC-07** | P2-22 | `docs/experiments/PHASE1_FROZEN_FOUNDATION_VERIFICATION.md` Issues Section 2 | Asserts that T0.4 closure report (`63e3c04`) "documents 8 methodological questions". | The frozen closure report documents exactly two observations (`native_clean_control` reading; class-to-route map). The list of eight is the post-closure `T0.4-GOLD` pre-implementation register (B1–B8) from local branch commits `d9f974b`/`916407d`. | `T0.4_final_closure_audit.md` text; `T0.4-GOLD_preimplementation_audit.md` at `d9f974b`. | OBJECTIVE_CORRECTION | Accurately bounds the frozen closure scope to its 4 verified conditions; correctly attributes B1–B8 to post-closure gold research. | **NO** | 2.1.0 |
| **PC-08** | P2-23 | `docs/experiments/T0.4-routing-clarification.md` & `T0.4-GOLD_preimplementation_audit.md` | Cited as repository methodology milestones. | These artifacts reside on local safety snapshot branches (`t0.4-gold` @ `d9f974b`, `t0.4-routing-clarification` @ `916407d`), labeled "REPOSITORY SAFETY SNAPSHOT - NOT A SCIENTIFIC METHODOLOGY COMMIT". Their recommendations (e.g. 1-class OCR) were NOT adopted in `63e3c04`. | Git log and ref inspection; status `T0.4_LF_BLOCKED` and "No rule was adopted". | DOCUMENTATION_CLARIFICATION | Precludes treating informal snapshot recommendations as adopted project policy. | **NO** | 2.1.0 |
| **PC-09** | P2-24 | Local store PDF files & external P-X1 harness snapshot | P-X1 harness and live PDFs cited without explicit storage boundaries. | Full re-derivation of T0/T0.1 requires the local disk PDF store (`live_store`, 194 files, verified 194/194 SHA-256). T0.4 sampling re-derivation requires only Git-tracked CSV manifests. The P-X1 harness remains external to Git and is classified `UNVERIFIED_FROM_TREE`. | `pdf_hash_and_cell_feasibility.py`; `T0.4_p-x1_reuse_audit.md`. | DOCUMENTATION_CLARIFICATION | Establishes exact reproducibility requirements: sampling is 100% Git-reproducible; raw PDF re-extraction requires external store. | **NO** | 2.1.0 |
| **PC-10** | P2-25 | T0.3A commit `02bae11` commit subject | Commit subject asserts "frozen taxonomy input", implying register preceded measurement. | In T0.3A, the taxonomy register and measurement results were committed simultaneously in `02bae11`. Pre-specification before measurement is Git-verifiable only in R1 (`f0e5805` ancestor of `ff030d9`), but era counts (58 pre-2015, 136 post-2015) were already measured in T0.3A. | `git log --graph --oneline` of `02bae11`, `f0e5805`, `ff030d9`. | DOCUMENTATION_CLARIFICATION | Enforces honest pre-registration claims: taxonomy pre-specification is demonstrable for R1 engine execution, not historical era measurement. | **NO** | 2.1.0 |

---

## 3. Detailed Breakdown of Phase-1 Hash Table Corrections (PC-06)

The table below provides the definitive crosswalk for the 10 rows in `PHASE1_FROZEN_FOUNDATION_VERIFICATION.md` that printed incorrect SHA-256 strings:

| Artifact Path | Incorrect String in Phase-1 Report | Authoritative SHA-256 (Git Blob at `63e3c04`) | Pinning Source / Authoritative Record |
|---|---|---|---|
| `dataset/corpus_freeze/issuer_split.csv` | `016e720275819777...` (partial prefix error) | `016e720239cfd864197365611ef4f4544719623e1e2d6b38c0379965d648bcf6` | `raw_input_manifest.json` / Findings JSON |
| `dataset/corpus_freeze/page_profile.csv` | `5bffb1968832a11b...` (partial prefix error) | `5bffb1966eb85750d52599723ecdbf4df9192f15dc82d007e60058b87ce3818e` | `raw_input_manifest.json` / Findings JSON |
| `dataset/corpus_gap_audit/audit_config.json` | `65ed1a7e48329911...` (partial prefix error) | `65ed1a7e2b7eb008542a1975e54d588523fa54e56feecdeef1e98d9e29a99ea7` | `configs/t0_1r/input_allowlist.json` |
| `dataset/corpus_gap_audit/gap_audit_document.csv` | `6df5c699988a1012...` (mismatched string) | `6df5c699fa7761005fbcba4f03cb7849e89ff5287f34177d48da66aa741f237f` | `raw_input_manifest.json` / Findings JSON |
| `dataset/corpus_gap_audit/condition_page_map.csv` | `651bafe40081bb2a...` (partial prefix error) | `651bafe42426615b1368f566a7b7382d645e227092925bdfeb937965949d21eb` | `raw_input_manifest.json` / Findings JSON |
| `dataset/corpus_gap_audit/table_candidates.csv` | `8402dbf55401991a...` (partial prefix error) | `8402dbf5bc2f11ecf17849ff735c02ad806b7ba9701ce26588aa90c885bb2b45` | `raw_input_manifest.json` / Findings JSON |
| `dataset/corpus_gap_audit/language_candidates.csv` | `f326c73a00188bca...` (partial prefix error) | `f326c73a7cb1d7350711910793139366dfae3287ffc914bf6893630f9a2ffbd9` | `raw_input_manifest.json` / Findings JSON |
| `dataset/corpus_gap_audit/manual_review_manifest.csv` | `d7192a83310087a1...` (mismatched string) | `d7192a83c74900a84594fa3571dcbdf599292c4587db21966a33eeef9c5d1fa1` | `raw_input_manifest.json` / Findings JSON |
| `dataset/corpus_gap_audit/manual_review_results.csv` | `a940188b401988ef...` (mismatched string) | `a940188bb3e85289f81ca9f88bbbc72863fa6f2095f70b42918e6ecaa62b3231` | `raw_input_manifest.json` / Findings JSON |
| `dataset/corpus_gap_audit/toc_offset_candidates.csv` | `e28bf01140081299...` (mismatched string) | `e28bf0111ef627f12eefc687e837ca7cc8c9f5dd831206fae9df370f1a6f8b96` | `raw_input_manifest.json` / Findings JSON |

---

## 4. Chain of Custody & Citation Protocol

Downstream consumers must adhere to the following citation hierarchy:
1. **Raw File Bytes on Disk:** Authenticated exclusively by SHA-256 computed without line-ending transformation (`core.hash_file_bytes`).
2. **Git Tree Blobs:** Authenticated by Git object SHA-1 (`git hash-object --no-filters`).
3. **Historical Manifests:** Pinned in `artifacts/t0_4/config_hashes.json`, `dataset/corpus_gap_audit/reconciled/reconciliation_manifest.json`, and `PHASE2_FOUNDATION_INTEGRITY_FINDINGS.json`.
4. **Phase-1 Document:** Strictly classified as historical analytical context, superseded in all hash claims by this ledger.
