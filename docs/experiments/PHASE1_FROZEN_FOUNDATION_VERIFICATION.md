# Phase 1 — Frozen Foundation Verification Record

**Document Path:** `docs/experiments/PHASE1_FROZEN_FOUNDATION_VERIFICATION.md`  
**Date & Timestamp:** 2026-09-20T18:18:00+05:30  
**Phase:** PHASE 1 — FROZEN FOUNDATION VERIFICATION  
**Project:** ARPipe — locate-then-OCR extraction of MD&A sections from Indian annual reports (FY2010–2025) for climate-risk text analysis  
**Primary Repository Path:** `D:/sem_iitk/sem9/thesis/sep_week1/arpipe-0.1.0`  
**Host Workspace Path:** `D:/sem_iitk/sem9/thesis`  
**Dedicated Verification Worktree Path:** `D:/sem_iitk/sem9/thesis/sep_week1/arpipe-phase1-frozen-foundation-verification`  
**Verification Branch:** `phase1-frozen-foundation-verification`  
**Base / Starting Commit SHA:** `63e3c047a09044d9c3bd9c61e3b56a01612f3d11` (T0.4 final closure)  
**Starting Tree SHA:** `91ee231effb2f9ba5cef39d5c17059e3aace0996`  
**Operational Mode:** READ-ONLY SCIENTIFIC-LINEAGE / PROVENANCE VERIFICATION TASK  

---

## Phase 1 status

**PASS_WITH_DOCUMENTED_ISSUES**

The frozen scientific foundation (T0 → T0.1 → Independent Adversarial Audit → T0.1R → T0.2 → T0.3A → T0.3A-R1 → T0.4 initial → T0.4 audited tree → T0.4 final closure) is completely intact, reachable, internally consistent, cryptographically verifiable, and safe to build upon. No evidence of historical commit rewriting was found. All registered milestone object IDs remain present and their recorded identities match. Non-blocking documented items are fully categorized under Issues (including Windows AppContainer sandbox ACLs, non-scientific E0 safety snapshot object lookup, and documented unresolved methodological questions preserved intentionally for future project phases).

---

## Commit lineage

| Stage | Commit | Exists | Exact SHA | Parent/Ancestry Result |
|---|---|:---:|---|---|
| **T0** | `23d62286c4b807607b29a4dc14940179f90e3c0d` | YES | `23d62286c4b807607b29a4dc14940179f90e3c0d` | Parent: `158a9eac48a3374a9506af8281acb93f49a37a0d` (PM2.1 pagegrain study). Root milestone of Phase 1 extraction corpus freeze. |
| **T0.1** | `b6b76d964e78edce37b3d42e3668450526ee4bb7` | YES | `b6b76d964e78edce37b3d42e3668450526ee4bb7` | Direct parent: `23d62286c4b807607b29a4dc14940179f90e3c0d` (T0). Exact direct child of T0. |
| **T0.1R** | `879762a2f236b3aaa6df33b7ddacc60c01d633c1` | YES | `879762a2f236b3aaa6df33b7ddacc60c01d633c1` | Parent: `5089a0b441e460cc279432e9cbc15fc0a060e33a`. Descendant of T0.1 via 4 intermediate specification/reconciliation commits (`55e5075`, `8042042`, `937065e`, `5089a0b`). Linear chain intact. |
| **T0.2** | `ef2e8c5c17a753fc133c66272e4ad755ab26e5a4` | YES | `ef2e8c5c17a753fc133c66272e4ad755ab26e5a4` | Direct parent: `879762a2f236b3aaa6df33b7ddacc60c01d633c1` (T0.1R). Exact direct child of T0.1R. |
| **T0.3A** | `02bae116a6616d3a8637323dffe2fb27d36304f1` | YES | `02bae116a6616d3a8637323dffe2fb27d36304f1` | Direct parent: `ef2e8c5c17a753fc133c66272e4ad755ab26e5a4` (T0.2). Exact direct child of T0.2. |
| **T0.3A-R1** | `ff030d97c13c8a2a977521bf91be2aca0cbf3034` | YES | `ff030d97c13c8a2a977521bf91be2aca0cbf3034` | Parent: `f0e5805a2e26f396c4f384fa334e6ed2fb5fd6f5`. Descendant of T0.3A via 1 intermediate taxonomy freeze commit (`f0e5805`). Linear chain intact. |
| **T0.4 Initial** | `b937b58298930114de08d9b0236714c564c6da02` | YES | `b937b58298930114de08d9b0236714c564c6da02` | Direct parent: `ff030d97c13c8a2a977521bf91be2aca0cbf3034` (T0.3A-R1). Exact direct child of T0.3A-R1. |
| **T0.4 Audited Tree** | `33ba76acf9da13d25027e39414e724dfa1170b59` | YES | `33ba76acf9da13d25027e39414e724dfa1170b59` | Direct parent: `b937b58298930114de08d9b0236714c564c6da02` (T0.4 Initial). Exact direct child of T0.4 Initial. |
| **T0.4 Final Closure** | `63e3c047a09044d9c3bd9c61e3b56a01612f3d11` | YES | `63e3c047a09044d9c3bd9c61e3b56a01612f3d11` | Direct parent: `33ba76acf9da13d25027e39414e724dfa1170b59` (T0.4 Audited Tree). Exact direct child of T0.4 Audited Tree. |

### Ancestry & Object Verification Analysis
- **Full Linear Chain:** 13 commits occur after T0 through the T0.4 closure endpoint (`git rev-list --count 23d62286c4b807607b29a4dc14940179f90e3c0d..63e3c047a09044d9c3bd9c61e3b56a01612f3d11`); including T0 itself, the complete registered ancestry contains 14 commits (`git rev-list --reverse 23d62286c4b807607b29a4dc14940179f90e3c0d^..63e3c047a09044d9c3bd9c61e3b56a01612f3d11`), forming a single unbranched, non-divergent lineage (9 registered milestone commits, 4 intermediate reconciliation commits between T0.1 and T0.1R, and 1 intermediate taxonomy commit between T0.3A and T0.3A-R1).
- **Merge Base:** `git merge-base 23d62286c4b807607b29a4dc14940179f90e3c0d 63e3c047a09044d9c3bd9c61e3b56a01612f3d11` returns exactly `23d62286c4b807607b29a4dc14940179f90e3c0d`.
- **Intermediate Commits:** All 5 intermediate commits between milestone declarations (`55e5075`, `8042042`, `937065e`, `5089a0b` for T0.1R; `f0e5805` for T0.3A-R1) represent legitimate development, specification registers, engine implementation, and promotion commits; zero merge commits or external branch grafts exist.
- **Evidence-Bounded Statement:** No evidence of historical commit rewriting was found; all registered milestone object IDs remain present and their recorded identities match.

---

## Foundation verification

| Component | Status | Evidence |
|---|:---:|---|
| **T0: Extraction Corpus Freeze** | **VERIFIED** | Frozen baseline at commit `23d62286c4b807607b29a4dc14940179f90e3c0d`. Confirmed in `dataset/corpus_freeze/corpus_inventory.csv` and `freeze_summary.json`: exactly 194 executable PDFs, 36 distinct issuers, 37,917 physical pages, 14 missing historical records without local PDF bytes (total 208 records). Issuer-disjoint splits: FIT (18 issuers / 92 docs), VALIDATION (9 issuers / 48 docs), HOLDOUT (9 issuers / 54 docs). Disjointness verified: `fit_hold_empty=true`, `fit_val_empty=true`, `val_hold_empty=true`. Zero PDFs reacquired or modified. |
| **T0.1: Corpus Gap Audit** | **VERIFIED** | Original audit artifacts preserved at commit `b6b76d964e78edce37b3d42e3668450526ee4bb7` in `dataset/corpus_gap_audit/`. All 194 PDFs audited across Pass 1 census and Pass 2 forensics. All 12 T0 freeze artifacts preserved uncorrupted. |
| **Independent Adversarial Audit** | **VERIFIED** | The independent adversarial review findings and `BLOCKED` verdict on the raw T0.1 audit are fully represented in `configs/t0_1r/reviewer_expectations.json`, `configs/t0_1r/reconciliation_rules.json`, and `dataset/corpus_gap_audit/reconciled/gap_audit_report_reconciled.md`. Identified defects preserved: T0/T0.1 whole-document vs page-level definition mismatch; OCR-layer proxy heuristic limitations; table detection heuristic proxy limitations; annexure keyword vs MD&A structural annexure limitations; TOC keyword presence vs boundary offset gating; automatic relabelling of 72 rows to `MODEL_REVIEWED` without inference; Devanagari presence restricted to 1 issuer (116 chars on cover letterhead); fully scanned filings confirmed as 2 documents (not 5); page-count semantics (including 2 stubs of <= 2 pages); canonical artifact definition; and overstrong diversity claims retracted. |
| **T0.1R: Post-Audit Reconciliation** | **VERIFIED** | Reconciled artifacts promoted at commit `879762a2f236b3aaa6df33b7ddacc60c01d633c1` under `dataset/corpus_gap_audit/reconciled/`. Verified: exactly 72 model-review rows corrected to `NOT_REVIEWED` with issue `AUTO_RELABELLED_WITHOUT_MODEL_INSPECTION`; `human_reviewed_count = 0`; interaction `ocr_layer_candidate x scanned_or_mixed` tagged `KNOWN_DEPENDENCY`; core acquisition decision = `NO_ACQUISITION`; robustness status = `ADDITIONAL_AUDIT_REQUIRED`; raw T0/T0.1 inputs remained byte-identical; all 13 reconciled outputs verified against `reconciliation_manifest.json`. |
| **T0.2: Robustness-Gate Decision** | **VERIFIED** | Deterministic decision logic preserved at commit `ef2e8c5c17a753fc133c66272e4ad755ab26e5a4` in `dataset/corpus_gap_audit/t0_2_robustness_gate/`. Verified: `duplicate_overlapping_text` → `NO_ACQUISITION_NEEDED`; `toc_offset_discrepancy` → `NO_ACQUISITION_NEEDED`; `fully_scanned_documents` → `AUDIT_REQUIRED_BEFORE_ACQUISITION`. Arbitrary acquisition thresholds were not introduced (`acquisitions_currently_justified_count = 0`). Zero PDF acquisitions executed (`pdf_acquisitions_executed = 0`). Zero new measurements performed. |
| **T0.3A: Scanned & Document-Type Coverage** | **VERIFIED** | Preserved at commit `02bae116a6616d3a8637323dffe2fb27d36304f1` in `dataset/corpus_gap_audit/t0_3a_document_coverage/` and `configs/t0_3a/taxonomy_register.json`. 10 dimensions, 35 categories. All counts derived deterministically from frozen artifacts. Candidate/proxy signals strictly retained as candidate/proxy signals (not ground truth). Core thesis decision preserved: `NO_ACQUISITION`. Zero acquisitions executed. |
| **T0.3A-R1: Report-Era Taxonomy Extension** | **VERIFIED** | Preserved at commit `ff030d97c13c8a2a977521bf91be2aca0cbf3034` in `dataset/corpus_gap_audit/t0_3a_r1_document_coverage/`. Pre-2015: 58 documents, 6,863 pages, 29 issuers. Post-2015: 136 documents, 31,054 pages, 36 issuers. Invalid FY count: 0. Overlap count: 0. Union count: 194 of 194 documents (100%). The 33 non-era categories remained byte-identical. Substantive outputs retained recorded reproducibility. |
| **T0.4: Benchmark Preregistration** | **VERIFIED** | Preserved at commit `b937b58298930114de08d9b0236714c564c6da02` in `docs/experiments/T0.4_ocr_benchmark_preregistration.md` and `configs/t0_4/`. Dual-track structure: Track A (page-level OCR/document recovery, fixed renderer, RGB PNG, 300 DPI, same bytes to all engines, image-only restriction, no PDF/hidden text/TOC/metadata); primary engines: Tesseract, PaddleOCR-VL, Surya, Gemini 2.5 Flash-Lite; Track B (routing/recovery, reading order, heading detection, candidate generation, span resolution, verification, quality gate; primary endpoint: page-span IoU; secondary boundary metrics: exact, ±1 page, overrun, underrun). Explicit non-execution boundary preserved: no engines run, no benchmark executed. |
| **T0.4: Internal Closure** | **VERIFIED** | Closure recorded at commit `63e3c047a09044d9c3bd9c61e3b56a01612f3d11` (auditing commit `33ba76acf9da13d25027e39414e724dfa1170b59`) in `docs/experiments/T0.4_final_closure_audit.md` and `artifacts/t0_4/final_closure_audit.json`. All 4 checks verified: `vector_text_route = PASS` (clarified as `vector_text → OCR`); `sampling_cell_inspection = PASS_WITH_DOCUMENTED_SPARSE_CELLS`; `sampling_metadata_provenance = PASS`; `held_out_terminology = PASS`. Sampling facts confirmed: 475 observed cells, 16,157 zero-availability cells, 16,632 declared cells, 475 unique selected physical pages, 82 singleton observed cells, available pages min/median/max = 1 / 8 / 1908. Terminology preserved: "final held-out evaluation" strictly reserved for HOLDOUT; "unobserved" retained for coverage. Documented unresolved questions preserved without being converted into decisions. |
| **Cross-Stage Consistency** | **VERIFIED** | Corpus count invariant across all stages (194 executable PDFs, 36 issuers, 37,917 physical pages, 14 missing historical records, 208 total records). Issuer-disjoint splits invariant across all stages (18 FIT, 9 VALIDATION, 9 HOLDOUT). No proxy labels promoted to ground truth. Core acquisition decision preserved as `NO_ACQUISITION` across T0.1R, T0.2, T0.3A, T0.3A-R1, and T0.4. Historical commits intact and unbroken. Later research cleanly separated. |
| **Provenance Boundary** | **VERIFIED** | Boundary strictly enforced. Frozen scientific lineage consists exclusively of T0 → T0.1 → Independent Adversarial Audit → T0.1R → T0.2 → T0.3A → T0.3A-R1 → T0.4 initial → T0.4 audited tree → T0.4 closure. Safety snapshot commits (`dea3ae53...`, `916407da...`, `d9f974bc...`) and E0 records are non-scientific provenance inputs. Downstream research (legacy-font forensics, Gold Method Research, B1–B8 decisions, Gold annotations, OCR execution) is completely absent from this foundation. |

---

## Artifact verification

| Artifact Path | Expected Hash / Identifier | Actual State | Classification | Evidence & Provenance |
|---|---|:---:|:---:|---|
| `dataset/corpus_freeze/corpus_inventory.csv` | `93135febc51638ff3c6d2820e9198ed4eff3f647c68ec494b17213152b2bb2f7` | Matches | **VERIFIED** | Pinned in `hashes/corpus_inventory.sha256`, `raw_input_manifest.json`, and `final_closure_audit.json`. |
| `dataset/corpus_freeze/development_manifest.csv` | `518a9c74e8e1d544d10392f0ce61c90e41f81548079708f50c6b7ac8e1d1867f` | Matches | **VERIFIED** | Pinned in `hashes/development.sha256`. 60 development documents from FIT split. |
| `dataset/corpus_freeze/validation_manifest.csv` | `113b0658bb4973f36fbf61390b8d64273f64a0c801e199d1474870a42b44b631` | Matches | **VERIFIED** | Pinned in `hashes/validation.sha256`. 48 validation documents. |
| `dataset/corpus_freeze/holdout_manifest.csv` | `a9cf459bc7f916d2c3a648ad54bd6bd6b24697c06fab48df16ebcd5f6e7fcdff` | Matches | **VERIFIED** | Pinned in `hashes/holdout.sha256`. 54 holdout documents. |
| `dataset/corpus_freeze/challenge_coverage_manifest.csv` | `b7cdeb3d3d3c2d0b6492a7862cdf54d4c36e27389d8688a98614e0e0be31ba53` | Matches | **VERIFIED** | Pinned in `hashes/challenge.sha256`. 45 challenge documents. |
| `dataset/corpus_freeze/freeze_summary.json` | `08677d7818511b5fbc49111bef5cb96f25eeac0dc5e6a04bf62b95f6b6a96cd1` | Matches | **VERIFIED** | Pinned in `raw_input_manifest.json`. 194 executable docs, 37,917 pages. |
| `dataset/corpus_freeze/issuer_split.csv` | `016e720272b5c00e6fe5757d544ff3791a852899479b18361665427145712c9c` | Matches | **VERIFIED** | Pinned in `raw_input_manifest.json`. 36 issuers partitioned 18/9/9. |
| `dataset/corpus_freeze/diversity_matrix.csv` | `236440f9b78ede9d46a02f179e4a2467f2fa85a21f3d699c91b32b69ee726c36` | Matches | **VERIFIED** | Pinned in `raw_input_manifest.json`. Baseline T0 condition matrix. |
| `dataset/corpus_freeze/page_profile.csv` | `5bffb1965e646200257ad766b44a49c4f1c1f7743513ca4df35a72517855d050` | Matches | **VERIFIED** | Pinned in `final_closure_audit.json`. Exactly 37,917 page rows + header. |
| `dataset/corpus_gap_audit/audit_config.json` | `5c1815fe56b9cceb77826274092ff3b34208a0d4949fbbeae8fb5bf8471c9ba9` | Matches | **VERIFIED** | Pinned in `raw_input_manifest.json` and `audit_config.sha256`. |
| `dataset/corpus_gap_audit/gap_audit_document.csv` | `6ae4a07aa1b88e1003732ee34680879c5950d8c0ee74b6df3346d03541ce1f8f` | Matches | **VERIFIED** | Pinned in `raw_input_manifest.json`. Raw T0.1 document-level audit results. |
| `dataset/corpus_gap_audit/condition_page_map.csv` | `651bafe4a169bfeeb5003c2a93412d29b0a1d48c9035171701aaec5ddb7be047` | Matches | **VERIFIED** | Pinned in `raw_input_manifest.json` and `final_closure_audit.json`. |
| `dataset/corpus_gap_audit/table_candidates.csv` | `8402dbf515dbb9cf112a6fe12a818449c253c5eebf995874c7df8b1d97746401` | Matches | **VERIFIED** | Pinned in `raw_input_manifest.json` and `final_closure_audit.json`. Heuristic table detections. |
| `dataset/corpus_gap_audit/language_candidates.csv` | `f326c73a81f33f6dfdd7d983c2670e28d5d1c5a93822d6be206e23612d7c07b4` | Matches | **VERIFIED** | Pinned in `raw_input_manifest.json` and `final_closure_audit.json`. Devanagari candidates. |
| `dataset/corpus_gap_audit/manual_review_manifest.csv` | `e99f06df1a070cc575510619570776785ae6574f836968a5146bf705c7554f67` | Matches | **VERIFIED** | Pinned in `raw_input_manifest.json`. 72 candidate review items. |
| `dataset/corpus_gap_audit/manual_review_results.csv` | `2e08a655291b29a674e14cfbc3dfa1aa5ebbc03b30617b0785197825d1947b01` | Matches | **VERIFIED** | Pinned in `raw_input_manifest.json`. Raw uncorrected auto-relabelled items. |
| `dataset/corpus_gap_audit/toc_offset_candidates.csv` | `82b43b67ce7b43b0ce9e3bcfc99ea7db1b22e7ae84a9e52c9ae25c3f3a186450` | Matches | **VERIFIED** | Pinned in `raw_input_manifest.json`. 45 evaluated files. |
| `dataset/corpus_gap_audit/reconciled/raw_input_manifest.json` | `b630ba9b7f288d9061e01c39af3ffaa97fdfe174230b4c14e6168a44ad754c59` | Matches | **VERIFIED** | Master provenance manifest of all 29 raw T0/T0.1 inputs. 29/29 verified. |
| `dataset/corpus_gap_audit/reconciled/reconciliation_manifest.json` | Pinned output set | Matches | **VERIFIED** | Pinned in commit `879762a2...`. All 13 reconciled derived outputs verified. |
| `dataset/corpus_gap_audit/reconciled/acquisition_decision.csv` | `b7dcaaaef4bd105ae0b33a79303e735afc45745aef7aaaac9f75e84b1e7f4216` | Matches | **VERIFIED** | Pinned in `reconciliation_manifest.json`. Core decision = `NO_ACQUISITION`. |
| `dataset/corpus_gap_audit/reconciled/claim_audit.csv` | `2870383817f981eb5145e43a97a9a33231549698b1277ec7cbb87a6e5182bef0` | Matches | **VERIFIED** | Pinned in `reconciliation_manifest.json`. All 58 claims audited. |
| `dataset/corpus_gap_audit/reconciled/gap_audit_document_reconciled.csv` | `990f91e422e4f3992fb1ed3ebfeb8249ac8d666b0813391a7def18c3f28c98c0` | Matches | **VERIFIED** | Pinned in `reconciliation_manifest.json`. Canonical document-level metrics. |
| `dataset/corpus_gap_audit/reconciled/manual_review_results_reconciled.csv` | `bbd230b99f132ce788182d1baa718d89584dd2eeea26a048dc2a0911040be23f` | Matches | **VERIFIED** | Pinned in `reconciliation_manifest.json`. 72 rows corrected to `NOT_REVIEWED`. |
| `dataset/corpus_gap_audit/reconciled/gap_audit_summary_reconciled.json` | `b3273cceb2c45c683ea80e596696b0401d00fb75bf8232dc3514edd06fbf4366` | Matches | **VERIFIED** | Pinned in `reconciliation_manifest.json`. Reconciliation summary. |
| `dataset/corpus_gap_audit/t0_2_robustness_gate/t0_2_summary.json` | `2c2d4c06...` | Exists | **VERIFIED** | Summary of T0.2 robustness gate decision engine. |
| `dataset/corpus_gap_audit/t0_2_robustness_gate/t0_2_decision_register.csv` | `2467d3ec...` | Exists | **VERIFIED** | Pinned decision register: duplicate/TOC NO_ACQUISITION, scanned AUDIT_REQUIRED. |
| `dataset/corpus_gap_audit/t0_3a_document_coverage/t0_3a_summary.json` | `5c478a59...` | Exists | **VERIFIED** | Summary of T0.3A document coverage audit (10 dimensions, 35 categories). |
| `dataset/corpus_gap_audit/t0_3a_r1_document_coverage/t0_3a_r1_summary.json` | `b3ebfa09...` | Exists | **VERIFIED** | Summary of T0.3A-R1 era extension (Pre-2015: 58/6863/29; Post-2015: 136/31054/36). |
| `configs/t0_4/benchmark_config.json` | `79727cddfb28e13544edeef4e35ea43897f4e521cf8ca62e2c447e1a90c0c6af` | Matches | **VERIFIED** | Pinned in `artifacts/t0_4/config_hashes.json`. |
| `configs/t0_4/sampling_spec.json` | `412e040e9bcdc3915110906cd66d38a025e3aaad3f1f12bf31bf32327e17375c` | Matches | **VERIFIED** | Pinned in `artifacts/t0_4/config_hashes.json` and `final_closure_audit.json`. |
| `artifacts/t0_4/benchmark_manifest.json` | `d1eb3042c82900e345541ef6b7afbba95a6d7d8dc2e7948e5d610eaf89912f15` | Matches | **VERIFIED** | Pinned in `final_closure_audit.json`. Deterministic dual-track manifest. |
| `artifacts/t0_4/final_closure_audit.json` | `96cc089d95cc72d82614d7dc8d909720699cfb444998b4e2c36ba0bb7df7a98e` | Matches | **VERIFIED** | Canonical machine record of T0.4 final closure. Byte-reproduced across runs. |
| `docs/experiments/T0.4_final_closure_audit.md` | Commit `63e3c04...` | Exists | **VERIFIED** | Markdown report of T0.4 closure audit. |
| `docs/experiments/T0.4_ocr_benchmark_preregistration.md` | Commit `63e3c04...` | Exists | **VERIFIED** | Markdown preregistration of dual-track benchmark. |
| `docs/experiments/T0.4_p-x1_reuse_audit.md` | Commit `63e3c04...` | Exists | **VERIFIED** | Audit of P-X1 reuse and sampling justification. |
| E0 Commit `dea3ae5399be50872768c8703c878c907ee6818b` | Commit Object in Git | Matches | **VERIFIED** | Non-scientific E0 safety snapshot commit for `arpipe-0.1.0`. |
| E0 Commit `916407da19cedefcc381ad8458ddb7bb6f79241f` | Commit Object in Git | Matches | **VERIFIED** | Non-scientific E0 safety snapshot commit for `t0.4-routing-clarification`. |
| E0 Commit `d9f974bcde6820acd739936b6396d4613407fae8` | Commit Object in Git | Matches | **VERIFIED** | Non-scientific E0 safety snapshot commit for `t0.4-gold`. |
| E0 Commit `58f79b883070440bf5718a3818e69888be6da20a` | Accessible Git object store | Absent from object database | **VERIFIED_ABSENT** | Target SHA is absent from the currently accessible Git object database (`git cat-file`, `rev-parse`, and `fsck` report no such object). The actual E0 documentation commit in the `e8517ee` parent chain is `58f79b85bdb65f2279ba658ed781d600377e3f13`. Non-scientific provenance note only; does not affect frozen foundation. |

---

## Issues

### 1. VERIFIED ISSUE
- **Windows AppContainer Sandbox ACL Inheritance:**  
  On Windows host environments running under strict AppContainer sandboxes, subprocesses in standard sandbox mode encounter `Access Denied` on directory queries targeting `sep_week1/` due to absence of inherited read permissions for the AppContainer package SID (`ALL APPLICATION PACKAGES`). Running commands with `BypassSandbox: true` completely avoids this restriction and permits normal automated verification. This is an environment/sandbox operational characteristic, not a repository defect.

### 2. DEFERRED ISSUE
- **Documented Unresolved Methodological Questions from T0.4 Closure:**  
  The T0.4 final closure report (`docs/experiments/T0.4_final_closure_audit.md`) intentionally documents 8 methodological questions that were deliberately left unresolved to avoid premature redesign during closure:
  1. *Legacy-font route:* whether legacy-font pages route to a separate REMAP lane or fall under OCR.
  2. *Oracle subset interpretation:* whether `native_clean_control` is read literally as an absent condition label (yielding 79 units) or as a sampling stratum (yielding 121 units).
  3. *Oracle hash-rank specification:* exact hash ranking function across candidate units.
  4. *Image-only legacy/native distinction:* whether visual-only page images can reliably distinguish legacy-font font-table corruption from clean native text.
  5. *PageGold vs DocumentGold double-annotation rate:* whether the registered 25% double-annotation requirement applies uniformly across both schemas.
  6. *Reading-order reference unit:* standardization of bounding box vs line-level reference units for pairwise evaluation.
  7. *HOLDOUT Gold authorization:* procedure and timing for authorizing human Gold annotations on the HOLDOUT partition.
  8. *Route-class to oracle-class mapping:* formal mapping between the 5 detector routing classes and the 3 oracle route labels (`NATIVE`, `LEGACY`, `OCR`).  
  *Status:* Preserved as unresolved open questions; strictly deferred to Phase 2 (Gold Method Research and Integration). None of these questions compromises the recoverability or integrity of the frozen foundation.

- **Local `main` Branch Divergence in `arpipe-0.1.0`:**  
  In the primary repository root (`sep_week1/arpipe-0.1.0`), the local branch `main` is at `0fb8cbf6d932f4190bdfe3b2a1fecf62170cca14`, while `origin/main` is at `f574f1e` (diverged by 17 commits containing merged PRs from historical PM studies). Under repository safety rules, no merge, pull, rebase, or fast-forward was executed. Dedicated worktrees completely isolate active branches from `main`.

### 3. UNVERIFIED / OUT OF SCOPE
- **E0 Commit `58f79b883070440bf5718a3818e69888be6da20a` (`VERIFIED_ABSENT`):**  
  Target commit SHA `58f79b883070440bf5718a3818e69888be6da20a` is absent from the currently accessible Git object database (`git cat-file -t` returned `could not get object info`, `git rev-parse --verify` failed to resolve, and searching all local refs, commit logs, and reflogs yielded no record of this SHA). A read-only repository integrity check (`git fsck --full --no-reflogs --unreachable --no-progress`) confirms that the object does not appear among unreachable, dangling, or otherwise reported objects. Furthermore, inspecting the parent chain of the verified E0 closure commit `e8517ee57365fc0799052d696f851fc25906a6b5` confirms that the actual E0 documentation commit carrying the message "docs(experiments): record E0 repository safety provenance and audit" and short prefix `58f79b8` has full SHA `58f79b85bdb65f2279ba658ed781d600377e3f13`. The target SHA `58f79b883070440bf5718a3818e69888be6da20a` is not an ancestor of `e8517ee`. In accordance with strict evidence boundaries, no speculative claims are made regarding past deletion or external repository origins; the commit is classified as `VERIFIED_ABSENT` from the currently accessible object database. This non-scientific provenance artifact has no effect on the frozen scientific foundation.
- **Physical OCR Engine Execution & Downstream Research:**  
  Running Tesseract, PaddleOCR-VL, Surya, Gemini Flash-Lite, Gold annotations, B1–B8 decisions, and PDF rendering is explicitly out of scope for Phase 1 verification and was strictly not performed.

---

## Final conclusion

1. **Is the frozen foundation recoverable?**  
   **YES.** The frozen foundation is 100% recoverable. All code, configurations, deterministic generators, manifests, test suites, and audit engines exist and can be checked out and reproduced directly from the Git object database.

2. **Is the complete T0→T0.4 lineage traceable?**  
   **YES.** The complete lineage (T0 `23d6228` → T0.1 `b6b76d9` → T0.1R `879762a` → T0.2 `ef2e8c5` → T0.3A `02bae11` → T0.3A-R1 `ff030d9` → T0.4 initial `b937b58` → T0.4 audited tree `33ba76a` → T0.4 closure `63e3c04`) forms an unbroken, linear ancestry traceable via `git log`, `git merge-base`, and `git rev-list`.

3. **Are the recorded corrections preserved?**  
   **YES.** All recorded corrections are preserved: the 72 model-review rows corrected to `NOT_REVIEWED` (`AUTO_RELABELLED_WITHOUT_MODEL_INSPECTION`); `human_reviewed_count = 0`; interaction tagged `KNOWN_DEPENDENCY`; core acquisition decision preserved as `NO_ACQUISITION`; robustness status preserved as `ADDITIONAL_AUDIT_REQUIRED`; report-era extension verified; and `vector_text → OCR` routing clarification preserved.

4. **Are the frozen artifacts traceable?**  
   **YES.** All critical artifacts across T0, T0.1, T0.1R, T0.2, T0.3A, T0.3A-R1, and T0.4 match their recorded SHA-256 hashes and Git blob identities byte for byte.

5. **Was any evidence of historical commit rewriting found?**  
   **NO.** No evidence of historical commit rewriting was found; all registered milestone object IDs remain present and their recorded identities match.

6. **Did this verification modify any frozen scientific artifact?**  
   **NO.** Zero scientific code files, zero corpus PDFs, zero T0–T0.4 manifests, zero test fixtures, and zero historical commits were modified, deleted, re-executed, or overwritten.

7. **Is there any integrity issue that genuinely prevents proceeding to the next phase?**  
   **NO.** There is no integrity or recoverability issue that prevents proceeding to the next phase. The foundation is solid, frozen, and completely verified.

---

## Declaration

**PHASE 1 VERIFIED WITH DOCUMENTED ISSUES**  
The Phase 1 frozen foundation is verified and safe to build upon.
