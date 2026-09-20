# Phase 2 - Foundation Integrity Audit

| Field | Value |
|---|---|
| Phase | PHASE 2 - FOUNDATION INTEGRITY AUDIT (read-only audit of the frozen ARPipe foundation) |
| Audit date | 2026-09-20 |
| Repository | ARPipe (main checkout `sep_week1/arpipe-0.1.0`; the thesis-level repository does not contain these commits) |
| Worktree | `D:\sem_iitk\sem9\thesis\sep_week1\arpipe-phase2-foundation-integrity` |
| Branch | `phase2-foundation-integrity` |
| Base commit | `63e3c047a09044d9c3bd9c61e3b56a01612f3d11` (T0.4 final closure) |
| Base tree | `91ee231effb2f9ba5cef39d5c17059e3aace0996` |
| Machine-readable record | `docs/experiments/PHASE2_FOUNDATION_INTEGRITY_FINDINGS.json` (findings, milestone table, 183 hash checks, 252-blob hash registry) |
| Audit scripts | `docs/experiments/phase2_foundation_integrity/scripts/` (8 read-only scripts) |

## Decision

**FOUNDATION READY FOR PHASE 3 - WITH DOCUMENTED ISSUES.** 0 blockers, 11 targeted issues, 28 findings in total. The gate criteria of the task (section 24) are met (table in section 12).

READY means the frozen foundation is internally valid enough to carry into Phase 3, with the issues below recorded and carried as dependencies. It does **not** mean that corpus sufficiency, population adequacy, sampling inferential adequacy, the Gold methodology, the OCR strategy, the Legacy/REMAP status or any thesis claim has been established. B1-B8 are unresolved and were not decided.

## 1. Starting state

| Check | Result |
|---|---|
| Target path absent before creation | Yes |
| Created from | `git worktree add -b phase2-foundation-integrity <path> 63e3c047a09044d9c3bd9c61e3b56a01612f3d11` |
| HEAD equals the base commit | Yes (`63e3c047a09044d9c3bd9c61e3b56a01612f3d11`); tree `91ee231e...` |
| Working tree clean | Yes: 0 lines from `git status --porcelain --untracked-files=all` |
| Branch unique | Yes: one ref named `phase2-foundation-integrity` |
| Other worktrees not modified | HEAD and a hash of the status output were recorded for all 27 pre-existing worktrees before the audit and compared after it: 0 differences. Ten of them (including the main checkout) were already dirty before the audit, from other sessions; their dirty state is byte-for-byte unchanged and none of it was touched. Exactly one worktree was added (this one). |
| Worktrees not used | Main/shared checkout, Phase-1 verification, E0, t0.4-routing-clarification, t0.4-gold and every dirty worktree were never used as a working location. They were touched only read-only: Git object commands (`git show`, `git cat-file`, `git rev-parse`), `git -C <path> status/diff` (including on the dirty t0.3a-document-coverage worktree), read-only SHA-256 of files in the Phase-1 worktree, and read-only hashing of the PDF store under the main checkout. |
| Note on the task text | The suggested location is under the thesis folder, but the commit exists only in the ARPipe repository (main checkout `sep_week1/arpipe-0.1.0`), so the worktree was created from that repository (finding P2-01 records a malformed SHA in the task text). |

## 2. Scope

**Primary foundation:** T0.3A, T0.3A-R1, T0.4 Initial, T0.4 Audited Tree, T0.4 Final Closure. **Dependencies (inspected only to verify a claim, denominator, predicate, provenance link or dependency):** T0, T0.1, T0.1R, T0.2.

**Boundary kept.** No OCR or benchmark was run; no PDF was acquired or rendered (the local PDF bytes were hashed read-only, nothing was opened for content or Legacy evidence); no Gold was created and no HOLDOUT item was annotated; sampling and routing were not redesigned or altered; no B1-B8 item was decided; no Phase-3, Gold or Legacy work was started; no additional worktree was created. Decisions that would need any of these are recorded as OPEN_QUESTION or OUT_OF_SCOPE.

## 3. Frozen milestones checked

| Stage | Commit | Type | Parent(s) | Tree | Subject |
|---|---|---|---|---|---|
| T0 | `23d62286c4b807607b29a4dc14940179f90e3c0d` | commit | `158a9eac48a3` | `7099ae0d77badd0bd13faeb14fe434d9dda49c17` | T0: freeze diverse extraction corpus and issuer splits |
| T0.1 | `b6b76d964e78edce37b3d42e3668450526ee4bb7` | commit | `23d62286c4b8` | `677481d204cb073430c1a4c4ec066e7c6d70799b` | T0.1: audit extraction corpus coverage and identify gaps |
| T0.1R | `879762a2f236b3aaa6df33b7ddacc60c01d633c1` | commit | `5089a0b441e4` | `9a4fe6f355a7c6b04d3cab7c5a925b624eaf6d43` | T0.1R: promote final verified reconciled artifacts after stub, dependency, and acquisition corrections |
| T0.2 | `ef2e8c5c17a753fc133c66272e4ad755ab26e5a4` | commit | `879762a2f236` | `793dbcf57564169142f79d5b1e90912f2006453d` | T0.2: implement deterministic robustness-gate decision audit engine and derived package |
| T0.3A | `02bae116a6616d3a8637323dffe2fb27d36304f1` | commit | `ef2e8c5c17a7` | `39bc2fe59104ec97b8779a56f39c986ed94b9012` | T0.3A: scanned and document-type coverage audit with frozen taxonomy input and zero acquisition |
| T0.3A-R1 | `ff030d97c13c8a2a977521bf91be2aca0cbf3034` | commit | `f0e5805a2e26` | `af8abb3b667e8a914112a30f9c8ae4b67ba1d6bc` | T0.3A-R1: report-era coverage taxonomy extension, deterministic engine, auditor, and test suite |
| T0.4 Initial | `b937b58298930114de08d9b0236714c564c6da02` | commit | `ff030d97c13c` | `9f4e6f10ae560a6ffa47b99ce4b3f2da70fcea15` | T0.4: preregister dual-track OCR benchmark |
| T0.4 Audited Tree | `33ba76acf9da13d25027e39414e724dfa1170b59` | commit | `b937b5829893` | `d5fc73d81b6248534caea9d7c756626f08b3c47b` | T0.4-CLOSE: register vector_text route, fix held-out wording, add closure audit engine |
| T0.4 Final Closure | `63e3c047a09044d9c3bd9c61e3b56a01612f3d11` | commit | `33ba76acf9da` | `91ee231effb2f9ba5cef39d5c17059e3aace0996` | T0.4-CLOSE: record final closure audit; T0.4 closed for the gold phase |

Five commits in the range are not registered milestones (recorded so the 13/14 arithmetic is explicit):

| Commit | Parent | Tree | Subject |
|---|---|---|---|
| `55e507566d1d` | `b6b76d964e78` | `d503288e3bba` | T0.1R: add configuration allowlist, rules, and reviewer expectations |
| `80420420253c` | `55e507566d1d` | `15db658597f8` | T0.1R: implement reconciliation engine, auditor, and tests |
| `937065e1ddd2` | `80420420253c` | `6de00f83a3ac` | T0.1R: promote verified reconciled corpus gap audit artifacts |
| `5089a0b441e4` | `937065e1ddd2` | `ee592e6e16d5` | T0.1R: apply final corrections to stub rule, interaction dependency, and core acquisition wording |
| `f0e5805a2e26` | `02bae116a661` | `1b63b0032aea` | T0.3A-R1: freeze pre-specified report-era taxonomy register before measurement |

- **Commit counts.** 13 commits occur after T0 (`git rev-list T0..closure`); 14 exist including T0 (`git rev-list --reverse T0^..closure`); 9 registered milestones plus the 5 commits above = 14. Merge commits in the range: 0.
- **Correction to the task text.** The T0.1R SHA given in the task has 41 hex characters and does not resolve; the 40-character SHA above (prefix `879762a`) is the parent of T0.2, the tip of `t0.1-reconcile`, and the Phase-1 registry value (P2-01).
- **Endpoint.** The closure commit is the endpoint of the lineage and equals the tip of `t0.4-ocr-benchmark` and the remote-tracking refs `origin/t0.4-*`. Later branches (`t0.4-gold`, `t0.4-routing-clarification`, `phase1-frozen-foundation-verification`) descend from it and are post-closure work.

## 4. Audit methodology

1. **Evidence-tracing order** (task section 4): Git object identity, frozen configuration, frozen implementation, frozen derived artifact, frozen report, narrative. Where sources disagree both are recorded with their predicates and neither is chosen.
2. **Git-object first.** History and blobs were read with `git show`, `git cat-file`, `git ls-tree`, `git diff-tree`, `git rev-list`, `git merge-base` and `git fsck`; working-tree files were used only where they are identical to the blobs (verified for the hashed artifacts).
3. **READ_ONLY_REPRODUCTION.** Frozen tools were run only with outputs redirected to a scratch directory, or in compare-only mode, or under `PYTHONDONTWRITEBYTECODE=1` with the pytest cache disabled; `git status` was empty after every run. Inputs, code and configuration were the frozen ones; no parameter was changed.
4. **Deterministic repeat vs independent re-derivation.** A repeat of the same code on the same inputs shows determinism, not correctness.

| Item | Kind |
|---|---|
| Frozen manifest builder reproduces the manifest and config hashes | DETERMINISTIC REPEAT |
| Closure engine `--check` recomputation; T0.4 setup audit; the 357-test suite | DETERMINISTIC REPEAT |
| Closure record's "independent implementation reproduced all 475 ranks" | `tools/t0_4/closure.py` has its own `_rank`, but same author and repository; independent of `core.build_manifest`, not of the specification reading |
| `reproduce_sampling.py` (written for this audit) | CODE-INFORMED RE-IMPLEMENTATION: a different code path written after reading the rules in `core.py`; it cannot detect a wrong rule, only a wrong execution |
| Hash checks against Git blobs | INDEPENDENT of the recording tools (they recompute SHA-256 from the objects) |
| PDF byte hashing | INDEPENDENT of the T0 tool (bytes hashed again); confirms identity, not content |

5. **Limits.** Historical events that Git cannot establish (who edited what, when, or what was shown to an external model) are not inferred. Absence of evidence is not treated as evidence of absence. The T0/T0.1 numbers that depend on PDF content were not re-derived (no PDF was parsed).

## 5. Evidence classification rules

| Axis | Values (as used in the finding table) |
|---|---|
| Evidence class | VERIFIED_FACT; DETERMINISTIC_DERIVED; PROXY_OR_CANDIDATE; DOCUMENTED_CLAIM; HISTORICAL_CONTEXT; OPEN_QUESTION |
| Audit status | CONSISTENT; INCONSISTENT; UNVERIFIED; OUT_OF_SCOPE |
| Severity | NON_BLOCKING; TARGETED_ISSUE; BLOCKER (only where Phase 3 cannot be supported without repair or re-baselining) |
| Bucket | MUST_FIX (blockers); SHOULD_FIX (important, non-blocking, cheap to record or correct); DEFERRED_P3 (claims, scope, population, sampling wording); DEFERRED_P45 (Gold, Legacy, OCR, REMAP, annotation) |

The axes are recorded separately. Nothing was promoted: proxy to truth, candidate to verified, documented claim to verified fact, recommendation to decision.

## 6. Audit results

### A. Lineage and frozen-artifact integrity

- Nine registered commits exist as commit objects; linear, unbranched ancestry; 13/14 commit counts confirmed; 0 merges (V01).
- Registered commit SHAs commit to their trees; closure tree `91ee231e...` confirmed; branch tips equal the registered commits (V02).
- 178 files were touched by the range and 0 pre-existing files were changed or deleted. 18 files were amended once, all inside their own stage: T0.1R (`configs/t0_1r/input_allowlist.json`, `reconciliation_rules.json`, `tests/t0_1/test_t0_1_reconciliation.py`, `tools/audit_t0_1_reconciliation.py`, `tools/reconcile_t0_1.py` at `5089a0b`; the 9 `reconciled/` outputs promoted at `937065e` and re-promoted at `879762a`) and the T0.4 audited tree (`docs/experiments/T0.4_ocr_benchmark_preregistration.md`, `T0.4_p-x1_reuse_audit.md`, `tools/audit_t0_4_setup.py`, `tools/t0_4/README.md` at `33ba76a`). No later stage altered an earlier stage (V04). The T0.4 amendments are documented (P2-02).
- The registered T0.1R milestone is the final promotion; the first promotion `937065e` differs (documented stub-rule, dependency and acquisition-wording corrections at `5089a0b`/`879762a`).

### B. Internal consistency

| Quantity | Result | Where |
|---|---|---|
| Documents / pages / issuers | 208 records = 194 with PDFs + 14 MISSING; 194 unique SHA-256; 37,917 pages; 36 issuers. Stated identically in the T0, T0.1, T0.1R, T0.3A-R1 and T0.4 summaries; no off-by-one string in any stage summary. CONSISTENT | V07, V08 |
| FIT / VALIDATION / HOLDOUT | Documents 92 / 48 / 54 = 194; issuers 18 / 9 / 9 = 36; disjoint at issuer and document level; T0.4 Track A 223 / 118 / 134 = 475 units; Track B 208 = 194 + 14. CONSISTENT | V07 |
| Development / Challenge / Blinded annotation | Development 60 inside FIT 92; roster 25 inside development; challenge 45 overlaps FIT 23 / VALIDATION 14 / HOLDOUT 8 and development 16, documented as never an independent test set. T0.4 replaces these with `benchmark_role`; the terms are not linked but not contradictory. CONSISTENT | V16, P2-19 |
| Representation classes | 6 detector kinds plus `other` = 7 (`core.py:290-298`); `other` never occurs. Page kinds sum to 37,917. CONSISTENT | V06, P2-17 |
| Sampling dimensions and levels | (issuer, stratum, era, representation class, length) = 36 x 11 x 2 x 3 x 7 = 16,632 declared cells, 475 observed, 16,157 zero-availability. CONSISTENT (interpretation: P2-18) | V06 |
| Era | `fiscal_year < 2015` in the T0.3A register, R1 and `core.py`; 58 + 136 = 194 documents; 6,863 + 31,054 = 37,917 pages. CONSISTENT | V09 |
| Category names and coverage statuses | 35 categories in 10 dimensions in both T0.3A and R1; statuses PRESENT 25 / SPARSE 6 / ABSENT 2 / NOT_ASSESSABLE 2 = 35 in both. R1 changes only the `post_2015` justification text. CONSISTENT | V09 |
| Acquisition decisions | NO_ACQUISITION in T0.1R, T0.2, T0.3A, R1, T0.4; T0.2 gates fully scanned documents with AUDIT_REQUIRED_BEFORE_ACQUISITION; 0 acquisitions justified or executed. CONSISTENT | V08 |
| Category predicates and evidence levels | Several mismatches: P2-03 to P2-10, P2-12, P2-13 | section 6D-E |
| Descriptive fields | `file_size_bytes` differs from the stored file for 83/194 documents (P2-14); missing-record split wording (P2-15); T0.3A `page_count` semantics (P2-10) |  |

### C. Terminology

| Term | Operative meaning(s) in the frozen record | Result |
|---|---|---|
| PRESENT / SPARSE / ABSENT / NOT_ASSESSABLE | T0.3A/R1 coverage statuses only (25/6/2/2). ABSENT = zero documents; SPARSE is justified by frozen characterizations such as "RARE", with no stated numeric threshold (not audited further); NOT_ASSESSABLE count 2 matches the two UNMEASURED categories. | CONSISTENT |
| CANDIDATE_PROXY | Same meaning throughout (detector or heuristic output, not verified): 17 T0.3A categories, all detector labels in T0.4, `candidate_status` in T0.1. | CONSISTENT |
| VERIFIED / human-verified | No measured category carries a VERIFIED label; `sha256_verified` (T0) means the hash was recomputed; "human-verified" occurs only prospectively (oracle route, gold); legacy `verified_by = read_pdf`. | CONSISTENT |
| NOT_REVIEWED | T0.1 `verification_status` (all 52,478 + 29,476 + 2 page rows; 72 review rows after T0.1R). Distinct from `NOT_YET_ANNOTATED` (T0.4 gold) and `NOT_AVAILABLE` (engine capability). | CONSISTENT |
| HOLDOUT / held-out | T0 frozen split (54 documents); T0.4 `FINAL_HOLDOUT_LOCKED` / `FINAL_ONLY_LOCKED`; plus the legacy holdout of `configs/eval_protocol.md` and P-X1 partitions. "Held-out" is confined to HOLDOUT within T0.4 scope (closure section 9, engine re-run). | P2-26 |
| unobserved / unseen | "Unobserved" is coverage terminology (zero-availability cell; Devanagari x OCR-layer). "Unseen" occurs in T0.4 tooling/tests/closure text only as guard vocabulary, and once in the raw T0.1 report ("9 issuers completely unseen during development"). | P2-26 |
| validation / validated | VALIDATION split; `VALIDATION_PRE_FREEZE` role; `VALIDATED_METADATA` label (undefined); "schema validation" (allowed HOLDOUT use); code `validate_*` checks. | P2-12 |
| challenge | T0 challenge-coverage set (45 documents; overlaps all splits); not used by T0.4. | CONSISTENT |
| blinded annotation | T0 roster (25 documents, single `annotator_id`, `saw_pipeline_output`, all blank); T0.4 uses "blind" only for the adjudicator; legacy protocol "blind holdout labelling". | P2-19 |
| native | Six meanings: T0 `doc_kind` digital (151 documents); T0.1 any native page (191); T0.1R/T0.3A NATIVE (60); T0.1 `native_page` (36,988 pages); detector `digital`/`native_ok` (35,580); oracle route `NATIVE` (label never defined). | P2-03, P2-04 |
| mixed | T0 `doc_kind` mixed (38 documents: 5-85% of non-blank pages in NEEDS_OCR) vs T0.1R MIXED (132 documents: scanned > 0 or OCR-layer > 0). | P2-13 |
| scanned | Detector page kind (804); T0.1 `scanned_page` (284); T0 `doc_kind` scanned (5 documents, at least 85% NEEDS_OCR pages, including broken/vector/hybrid); T0.1R SCANNED (2 documents, 100% scanned pages). | P2-05 |
| broken_text | Detector kind (n_chars >= 120 and mojibake ratio > 0.02): 803 pages, 24 documents; also a representation class, a label, a ROUTING class and an empty stratum. | P2-07, P2-18 |
| legacy_font | Three operationalizations and seven names. | P2-07, P2-16 |
| vector_text | One meaning (n_chars < 120, image < 0.55, at least 400 drawings): 32 pages; route OCR confirmed. | CONSISTENT |
| OCR | Four senses: T0 document-level `OCR_layer` (producer strings, INFERRED), T0.1 page-level OCR-layer proxy (189 pages, 98 documents), the route action (NEEDS_OCR), the OCR engines. | P2-08 |
| REMAP | Prose and schema names only; never defined operationally. | P2-16 |
| oracle / gold | `ORACLE_ROUTING` condition, oracle subset, oracle labels; PageGold/DocumentGold (human-only, none exist); legacy `historical_ground_truth` MD&A labels; T0 roster gold columns (blank). Distinct data classes, none for HOLDOUT. | P2-19 |
| control | `native_clean_control` stratum (contains 22 hybrid units) vs "native-only baseline" (cost comparison). | P2-04 |
| route | Detector action (NEEDS_OCR), ROUTING classes (5), oracle routes (3), the `vector_text` route statement. | P2-17 |
| sampling stratum | One primary stratum per page (11-level priority) vs `condition_labels` (13-value vocabulary that also contains representation and routing-class names) vs `representation_class` (7) vs coverage cell (5-tuple). | P2-04 |

### D. Predicate integrity

Documented definition vs implementation vs derived output, for the predicates that share a name across stages:

| Name | Predicate A (used by) | Predicate B (used by) | Overlap / difference | Consequence |
|---|---|---|---|---|
| native (document) | T0 `doc_kind` digital: at most 5% of non-blank pages in NEEDS_OCR (T0 inventory; T0.4 Track B `native`): 151 docs | T0.1 any native page (191 docs, "native text" report); T0.1R/T0.3A NATIVE = no scanned and no OCR-layer page (60 docs) | 60 inside 191; only 21 of the 60 have every page native | P2-03: a summary sentence uses 191 for "native digital documents" |
| native (page) | Detector `digital` -> `native_ok` (35,580 pages; T0.4 `representation_class`) | T0.1 `native_page`: chars > 50 and not scanned (36,988 pages; T0.4 label `native_ok`) | 35,497 in both; 83 detector-only; 1,491 T0.1-only (broken 803, hybrid 483, scanned 194, vector 11) | P2-04: 157 units carry `native_ok` with an OCR-routed class |
| scanned | Detector: n_chars < 120 and image >= 0.55 (or >= 0.25 without vector-path threshold): 804 pages (T0.4) | T0.1: chars <= 20 and image >= 0.85: 284 pages (T0.3A) | B inside A; 520 A-only | P2-05 |
| multi_column | T0.1 estimator, >= 3 columns: 17,190 pages (T0.1, T0.3A) | Detector `n_columns >= 2` or T0.1 `two_column_page` (T0.4) | T0.1 two-column (15,015) is not a subset of detector n >= 2 (18,855) or equal to n == 2 (9,521) | P2-06 |
| legacy_font_candidate | Detector broken_text: 803 pages / 24 docs (T0 `legacy_font`, T0.4) | broken_text or U+FFFD or > 5 PUA characters: 1,007 pages / 56 docs (T0.3A) | 24 inside 56; 32 B-only; config ratio 0.05 unused | P2-07 |
| OCR-layer candidate | Documented: PDF render mode 3 / OCR producer (T0.1, T0.1R, T0.3A) | Implemented: `kind == scanned and n_chars > 50` (T0 profile, consumed by T0.1) | 189 pages, all detector-scanned, none in T0.1 `scanned_page` | P2-08 |

Other candidate predicates (documented in the T0.3A register / implemented in `tools/audit_corpus_gaps.py` / derived output):

| Predicate | Documented | Implemented | Derived output | Result |
|---|---|---|---|---|
| table candidate | Vector grid and aligned numeric lines | `has_vector_grid or numeric_lines_count >= min_align_rows` (config: grid rects >= 4, aligned rows >= 3) | 29,476 pages (77.7%); 190 docs | CONSISTENT; proxy, saturated (P2-11) |
| annexure candidate | Keyword in outline or heading | Keyword in any page text | 188/194 docs | INCONSISTENT (P2-09) |
| TOC candidate | Keyword in first 30 pages | Keyword substring (incl. `index`) on pages < 50 | 174/194 docs | INCONSISTENT (P2-09) |
| combined MD&A candidate | Outline/heading with Directors' Report or Governance | Outline title or heading line with governance / directors' report / annexure / board | 44/194 docs | CONSISTENT (two extra trigger words) |
| duplicate-text candidate | Bounding-box overlap IoU >= 0.40 | IoU >= 0.70 with equal text, or >= 0.40 (near overlap); min 30 chars | 68 pages / 35 docs | CONSISTENT with the register; the exact flag rule was not traced (UNVERIFIED detail) |
| hidden-text candidate | Font size < 0.5 pt | `size < hidden_text_max_font_size` (0.5) | 4 pages / 3 docs | CONSISTENT |
| era | `fiscal_year < 2015` | Same in T0.3A, R1 and `core.py` | 58 / 136 docs | CONSISTENT |
| hybrid | Text layer plus large image regions | n_chars >= 120, image >= 0.25 and n_chars < 600 | 483 pages | CONSISTENT as a page kind; route: P2-17 |
| vector_text / broken_text / blank | CLAUDE.md, models.py, triage.py | `_classify` order: blank, broken_text, text-empty branch (scanned, vector_text, scanned, blank/digital), hybrid, digital | 32 / 803 / 215 pages | CONSISTENT; `blank` undocumented in CLAUDE.md (P2-17) |

### E. Evidence level and proxy vs truth

| Category | Evidence class | Coverage status (T0.3A) | Human-verified | Independently verified | Proxy only | Treated as truth downstream |
|---|---|---|---|---|---|---|
| table_candidate | PROXY_OR_CANDIDATE | PRESENT (190 docs) | No | No | Yes | Not found in T0.3A/R1/T0.4 |
| annexure_candidate | PROXY_OR_CANDIDATE | PRESENT (188) | No | No | Yes | Not found |
| toc_candidate | PROXY_OR_CANDIDATE | PRESENT (174) | No | No | Yes | Not found |
| combined_mdna_candidate | PROXY_OR_CANDIDATE | PRESENT (44) | No | No | Yes | Not found |
| OCR-layer (`has_ocr_layer_pages`) | PROXY_OR_CANDIDATE | PRESENT (98 docs, 189 pages) | No | No | Yes | Not found |
| legacy_font_candidate | PROXY_OR_CANDIDATE | PRESENT (56 docs) | No | No | Yes | Not found |
| hidden_text_candidate | PROXY_OR_CANDIDATE | SPARSE (3 docs) | No | No | Yes | Not found |
| duplicate_text_candidate | PROXY_OR_CANDIDATE | PRESENT (35) | No | No | Yes | Not found |
| devanagari / bilingual | PROXY_OR_CANDIDATE | SPARSE (2 docs, 1 issuer, both HOLDOUT) | No | No | Yes | Not found |
| document native / mixed / scanned | DETERMINISTIC_DERIVED from proxies | PRESENT / PRESENT / SPARSE | No | No | Derived from detector heuristics | Not found (P2-13) |

Not human-verified: every row above. No precision or recall exists and none is stated here. T0.4 `sampling_spec.json` states that selection never upgrades a proxy's evidence level, and the manifest bears this out (all detector labels CANDIDATE_PROXY). T0.2 decisions cite proxy-derived counts (duplicate-text, TOC offset); whether they are adequate is acquisition adequacy and out of scope. The `VALIDATED_METADATA` label is undefined (P2-12).

### F. Sampling integrity

| Item | Result |
|---|---|
| Declared dimensions | (issuer_id, sampling_stratum, era, representation_class, length_category), stated identically in the preregistration, `sampling_spec.json` and the closure |
| Cells | 16,632 declared; 475 observed; 16,157 zero-availability, never filled or duplicated. Only 15 of 77 (stratum, representation) pairs occur on any page, so 13,392 declared cells are structurally impossible (P2-18) |
| One page per observed cell / uniqueness | 475 of 475 cells select one page; 475 unique physical pages; 401 carry two or more labels; each is the minimum-rank page of its cell (re-derived) |
| Issuer/split restrictions | The cell contains `issuer_id`, so a cell has one split; issuer-disjointness holds; oracle subset restricted to FIT and VALIDATION (0 HOLDOUT) |
| Rank reproduction | SHA-256 of `seed NUL document_id NUL decimal page` with seed `t0.4-coverage-v1`; the encoding is in code (`core.py:349-351`), not in the prose spec (closure section 7 notes this). All 475 ranks reproduced |
| Config / manifest hash | `sampling_spec.json` 412e040e...; manifest d1eb3042...; both match the records and were re-derived (V05, V06) |
| Selected page to source | Each page traces to `page_profile.csv` row (`document_id`, `physical_page`), then to the inventory, issuer split and the T0.1 files; the closure record lists source commit and hash per file (`23d6228` for the T0 files, `b6b76d9` for the T0.1 files). The manifest itself does not store rule id or source commit per unit (closure section 7) |
| Relationship to HOLDOUT | Documented: HOLDOUT units "may be predeclared and integrity-checked but not inspected for tuning". T0.4 sampling therefore includes 134 HOLDOUT units and does not exclude HOLDOUT; all are `FINAL_HOLDOUT_LOCKED`. "Unobserved" (zero-availability cell) is a coverage term and is not "final held-out evaluation" |
| Reproduction label | READ_ONLY_REPRODUCTION (deterministic repeat; code-informed re-implementation) |

### G. Routing integrity

Page kind -> triage predicate -> route -> downstream action, from `arpipe/triage.py` (`_classify`, `NEEDS_OCR`, `ocr_page_numbers`), `arpipe/pipeline.py` and the T0.4 configs. A page kind is not a route and no route was inferred from a name.

| Page kind (detector) | Triage predicate | In NEEDS_OCR | Downstream action (code) | T0.4 representation class | T0.4 ROUTING class | Oracle route |
|---|---|---|---|---|---|---|
| digital | usable text (n_chars >= 120) without the broken or hybrid conditions, or n_chars 15-119 with image < 0.25 and drawings < 400 | No | Text layer read (`textlayer.extract_pages`) | native_ok | native_ok | NATIVE (label never defined) |
| scanned | n_chars < 120 and image >= 0.55, or >= 0.25 | Yes | OCR (`_ocr_pages`) | scanned | scanned | OCR |
| vector_text | n_chars < 120, drawings >= 400, image < 0.55 | Yes | OCR | vector_text | vector_text | OCR by closure statement; no oracle label pre-assigned |
| broken_text | n_chars >= 120 and mojibake ratio > 0.02 | Yes | OCR; text layer not read | broken_text | broken_text | Undefined (B1/B2) |
| hybrid | n_chars >= 120 (< 600) and image >= 0.25 | Yes | Page OCR; docs say "read text, OCR the image" | hybrid | none | none (B1) |
| blank | n_chars < 15 and image < 0.05 and drawings < 20 (or n_chars < 15 in the text-empty branch) | No | Excluded implicitly (`content` list, missing-page list); no route documented | blank | none | none |
| (none) | No detector kind or producer for `legacy_font` | No | None; REMAP lane exists in T0.4 prose only | label `legacy_font_candidate` = broken_text | legacy_font | LEGACY (label only) |

Result: every detector kind has an identifiable code path; `vector_text` handling is explicit and agrees with the registered design; `broken_text` handling is explicit in code and comments but T0.4 prose introduces a REMAP lane the code does not have; hybrid and blank are not explicit in the registered design (P2-17). Whether `legacy_font` should be a separate production route was not decided.

### H. Oracle / Gold interface integrity

| Item | Frozen record | Result |
|---|---|---|
| PageGold schema | `gold_schema.json` `page_gold`: 11 required fields; provenance requires annotator_id, protocol_version, adjudication_status; page numbers >= 0 (0-based, matches the profile) | CONSISTENT |
| DocumentGold schema | `document_gold`: 11 required fields; `annotation_provenance` unconstrained | P2-19 |
| OracleRouteGold | Not a frozen name. Record = `oracle_routing_spec.json` `annotation_fields` (document_id, page_number, annotator_id, route, confidence, reason); not covered by `gold_schema.json` | P2-19 |
| Annotation roster | T0 `annotation_roster.csv`: 25 FIT documents, one `annotator_id` column, all gold columns blank | CONSISTENT with T0 protocol |
| Blinding / `saw_pipeline_output` | Only in the T0 roster header; absent from every T0.4 schema; only the adjudicator is "blind to all engine outputs" | P2-19 |
| Double annotation / adjudication | Only in `oracle_routing_spec.json`: rank 0-3, `expected_fraction` 0.25, third blind adjudicator, evidence "rendered page image plus the written route protocol"; PageGold has an `adjudication_status` enum | B4, B5, B6 |
| Reading-order reference unit | Pairs of strings; unit unspecified | B7 |
| Oracle terminology | `ACTUAL_ROUTING`/`ORACLE_ROUTING`, routes `NATIVE`/`LEGACY`/`OCR`; subset "from the frozen FIT and VALIDATION partitions only" | CONSISTENT with the preregistration |
| HOLDOUT authorization fields | `holdout_policy` in `benchmark_config.json`; `holdout_role` in `sampling_spec.json`; `benchmark_role` in the manifest | B8 |

### I. Hash and reproducibility integrity

| Recorded in | Pairs | Match | Note |
|---|---|---|---|
| T0 `hashes/*.sha256` | 5 | 5 | corpus_inventory, development, validation, holdout, challenge |
| T0.1 `input_hashes.json` (root, run_01, run_02) | 36 | 36 | 12 T0 files x 3 copies |
| T0.1 `audit_config.sha256` (dataset copy) | 1 | 1 | CRLF copy pinned by T0.1R |
| T0.1 `configs/audit_config.sha256` | 1 | 0 | P2-20: blob plus one trailing newline reproduces the recorded value |
| T0.1R `raw_input_manifest.json` | 29 | 29 |  |
| T0.1R `reconciliation_manifest.json` | 16 | 16 | 3 configs, 13 outputs |
| T0.2 / T0.3A / T0.3A-R1 immutable input manifests | 17 / 12 / 19 | 17 / 12 / 19 |  |
| T0.4 `config_hashes.json` | 12 | 12 | sampling_spec 412e040e... |
| T0.4 `setup_audit.json` | 2 | 2 | manifest_sha256 and deterministic_repeat_sha256 both d1eb3042... |
| T0.4 manifest `source_hashes` | 6 | 6 |  |
| Closure report scalar hashes | 4 | 4 | record file 96cc089d..., manifest, sampling config, corpus inventory |
| PDF bytes (local store) vs inventory | 194 | 194 | read-only byte hashing; `file_size_bytes` differs for 83 (P2-14) |
| Phase-1 report table | 27 | 17 | P2-21: 10 rows not reproducible |

UNVERIFIED_HASH (independent): `zero_availability_cells_sha256` in the closure record is reproduced only by the frozen closure engine (definition at `tools/t0_4/closure.py:450-481`); it was not called wrong. The T0.4 sampling manifest hash, sampling configuration hash and setup-audit hash are all reproduced (V05, V06). The full recorded-versus-actual table (183 rows) and the SHA-256 of all 252 blobs in the closure tree are in the JSON record.

### J. HOLDOUT safety

**No HOLDOUT integrity breach was found.** Evidence (V12): no HOLDOUT gold, annotation, engine output or benchmark result exists; the roster is FIT-only with every gold and blinding field blank; the oracle subset has 0 HOLDOUT units; every HOLDOUT unit is `FINAL_HOLDOUT_LOCKED`; no image hash exists (475 `NOT_YET_RENDERED`); no historical MD&A label maps to a HOLDOUT document (0 of 20). Membership: 54 documents, 9 issuers, disjoint from FIT and VALIDATION at issuer level.

Bounded exposures, none of which is leakage on the evidence found: the challenge set includes 8 HOLDOUT documents; T0.1's review queue has 26 HOLDOUT items (never actually reviewed on the evidence, P2-27); T0.1 and T0.3A computed HOLDOUT coverage statistics; the legacy holdout protocol and the pre-T0 development exposure of HOLDOUT documents are not reconciled or established (P2-26). "Unobserved" (coverage) and "final held-out evaluation" (HOLDOUT only) are kept apart in T0.4 (closure section 8-9, re-run PASS).

### K. Provenance

| Output | Source -> transformation -> output -> hash -> commit | Reproducible from Git alone |
|---|---|---|
| T0 corpus freeze | local `live_store` `documents.jsonl`/`profiles.jsonl` + repository CSVs -> `tools/freeze_extraction_corpus.py --seed 20260918` -> `dataset/corpus_freeze/*` -> `hashes/*.sha256`, `input_hashes.json` -> `23d6228` | No: inputs outside Git (P2-24); outputs and hashes verified |
| T0.1 gap audit | PDFs + T0 artifacts -> `tools/audit_corpus_gaps.py` + `audit_config.json` -> `dataset/corpus_gap_audit/*` (+ run_01/run_02 repeats) -> `input_hashes.json`, `audit_config.sha256` -> `b6b76d9` | No (PDFs); hashes verified (P2-20) |
| T0.1R reconciliation | raw T0/T0.1 artifacts (29 pinned inputs) -> `tools/reconcile_t0_1.py` + `configs/t0_1r/*` -> `reconciled/*` (13 outputs) -> `reconciliation_manifest.json` -> `879762a` | Yes (inputs pinned by hash) |
| T0.2, T0.3A, T0.3A-R1 | pinned inputs (17 / 12 / 19) -> runner + auditor + register -> outputs -> immutable input manifest -> `ef2e8c5` / `02bae11` / `ff030d9` | Yes; repeat only (tests), not independent |
| T0.4 manifest and setup | 6 pinned CSVs + `sampling_spec.json` -> `tools/build_t0_4_manifest.py` -> `benchmark_manifest.json`, `config_hashes.json` -> `setup_audit.json` -> `b937b58` | Yes (reproduced byte for byte) |
| T0.4 closure | objects of `33ba76a` -> `tools/audit_t0_4_final_closure.py` -> `final_closure_audit.json` (record; no self-hash) -> report -> `63e3c04` | Yes (compare-only re-run exits 0) |

A later consumer can identify where each number came from, the generating code and configuration (same commit as the artifact for single-commit stages), the pinned input set and whether the artifact is frozen. Deterministic repeats were distinguished from independent re-derivation in section 4.

### L. Git object integrity

- Every registered commit and tree exists; all 252 blobs of the closure tree are readable and hashed; `git fsck --full --no-dangling --no-progress` exit 0; no replace refs, grafts, shallow file or alternates (V03).
- Phase 1's corrected E0 finding concerns E0 safety commits (`dea3ae5`, `e8517ee`, `58f79b85`) that are not ancestors of the closure; it does not enter the T0-T0.4 lineage. The E0 snapshots `916407d` and `d9f974b` descend from the closure and are post-closure records (V03).
- Evidence-bounded: Git shows what is recorded, not how the files were produced or edited before commit; no such inference is made.

## 7. Findings

| Finding ID | Area | Artifact | Commit | Evidence Class | Status | Severity | Observed | Expected | Impact | Repair | Owner/Phase |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P2-01 | A/L Lineage | Task milestone registry: T0.1R SHA | 879762a2f236b3aaa6df33b7ddacc60c01d633c1 | VERIFIED_FACT | INCONSISTENT | NON_BLOCKING | The T0.1R SHA in the Phase-2 task text is 41 hex characters (`...df33db7dd...`) and does not resolve as a Git object. The 7-character prefix `879762a` resolves uniquely to the 40-character SHA `879762a2f236b3aaa6df33b7ddacc60c01d633c1` (`...df33b7dd...`, one `d` fewer), which is the tip of branch `t0.1-reconcile`, the sole parent of T0.2, and the value in the Phase-1 registry. | A 40-hex SHA that resolves to a commit. | None on the repository. Any script fed the 41-character string fails to resolve it. | None to history. This report uses the 40-character SHA and records the correction. | Task author (registry text) |
| P2-02 | A Lineage | T0.4 preregistration and P-X1 reuse audit (freeze-set docs); tools/audit_t0_4_setup.py; tools/t0_4/README.md | 33ba76a | DOCUMENTED_CLAIM | CONSISTENT | NON_BLOCKING | The preregistration says it is 'frozen before execution' and the P-X1 audit 'frozen before benchmark execution', yet both were amended at 33ba76a (documented in closure sections 1 and 9). The preregistration names these two docs as part of the configuration freeze, but `artifacts/t0_4/config_hashes.json` hashes only the 12 JSON configs; the two docs are identified by Git blob only. | Freeze-set members identified either by a recorded content hash or by an explicit commit. | No scientific effect. A consumer citing the docs at b937b58 would cite superseded text. | None. Cite the 63e3c04 blobs. | Phase 3 (citation rule) |
| P2-03 | B/D Consistency | T0.3A and T0.3A-R1 `core_relevance_summary` (t0_3a_summary.json:7, t0_3a_r1_summary.json:7; tools/run_t0_3a_document_coverage.py:319) | 02bae11 / ff030d9 | DETERMINISTIC_DERIVED | INCONSISTENT | TARGETED_ISSUE | The sentence 'Core English MD&A extraction is 100% supported by native digital documents (191 docs, 36 issuers)' is a hard-coded string literal, not derived from the register. The same artifacts' coverage matrix gives native=60, mixed=132, scanned=2 documents. 191 is T0.1's count of documents containing at least one native text page (CLAIM:C005); T0 classified 151 documents `digital`; T0.1R explicitly separated '191 docs containing native pages' from '60 whole-document native representation' (tools/reconcile_t0_1.py:499-506). | A summary sentence derivable from registered categories, worded 'documents containing at least one native text page (191)'. | A reader or later phase could cite '191 native documents' for a category the register counts as 60. No acquisition decision is derived from this sentence (T0.2 decides). | None in Phase 2 (frozen artifact; a separately authorized amendment would be required). Recorded here. Proposed wording recorded. | Amendment task / Phase 3 (do not cite the sentence) |
| P2-04 | D/C Predicates | T0.4 `condition_labels` label `native_ok` vs `representation_class` `native_ok`; T0.1 `native_page` (tools/audit_corpus_gaps.py:254-262); tools/t0_4/core.py:290-329; metrics_spec.json ROUTING.classes | b937b58 / b6b76d9 | DETERMINISTIC_DERIVED | INCONSISTENT | TARGETED_ISSUE | The label `native_ok` in `condition_labels` comes from T0.1 `native_page` (char_count > 50 and not (chars <= 20 and image >= 0.85)), which also covers hybrid, broken_text and vector_text pages. The routing-class name `native_ok` is the detector kind `digital`. Detector digital = 35,580 pages; T0.1 native_page = 36,988. In the 475-unit manifest 157 units carry the label `native_ok` together with an OCR-routed representation class: hybrid 102/102, broken_text 20/20, scanned 28/72, vector_text 7/17. Stratum `native_clean_control` (60 units, all splits) contains 22 hybrid units. | One meaning per label; page-kind and routing-class vocabularies kept apart. | Deriving routing classes from `condition_labels` (instead of `representation_class`) mislabels at least 157 units. `native_clean_control` is not a clean-native set. | None in Phase 2 (frozen artifact; a separately authorized amendment would be required). Recorded here. Consumers must use `representation_class` for page kind. | Phase 3 / Phase 4 (Gold universe) |
| P2-05 | D/C Predicates | `scanned` in T0.1 (audit_corpus_gaps.py:254-256) vs detector (arpipe/triage.py:_classify) vs T0.3A categories vs T0.4 stratum | b6b76d9 / 02bae11 / b937b58 | DETERMINISTIC_DERIVED | INCONSISTENT | NON_BLOCKING | Predicate A (detector `scanned`): n_chars < 120 and image area >= 0.55, or >= 0.25 when drawings < 400 -> 804 pages. Predicate B (T0.1 `scanned_page`): chars <= 20 and image >= 0.85 -> 284 pages, a strict subset of A (A-only 520, B-only 0). T0.3A categories (`scanned`, `fully_scanned_document`, `mixed_scanned_pages`) use B; the T0.4 stratum and representation class `scanned` use A (72 units). | One documented predicate per name, or distinct names. | 'Scanned' counts in T0.3A (2 fully scanned documents) and T0.4 (72 scanned units) are not comparable. | None in Phase 2 (frozen artifact; a separately authorized amendment would be required). Recorded here. | Phase 3 (state which predicate) |
| P2-06 | D/C Predicates | `multi_column` in T0.1/T0.3A vs T0.4 (tools/audit_corpus_gaps.py:657-659; tools/t0_4/core.py:312,327) | b6b76d9 / b937b58 | DETERMINISTIC_DERIVED | INCONSISTENT | NON_BLOCKING | T0.1/T0.3A `multi_column` = T0.1 estimator with >= 3 columns (17,190 pages, 191 documents). T0.4 label `multi_column` = detector `n_columns >= 2` (18,855 pages) OR T0.1 `two_column_page` (15,015 pages). The two estimators disagree: T0.1 `two_column_page` is not equal to detector `n_columns == 2` (9,521) and is not a subset of `n_columns >= 2`. | Same name, same predicate; or distinct names for the >=2 and >=3 column notions. | T0.3A `multi_column_layout` (191 documents) and T0.4 stratum `multi_column` (94 units) measure different things. | None in Phase 2 (frozen artifact; a separately authorized amendment would be required). Recorded here. | Phase 3 |
| P2-07 | D Predicates | `legacy_font_candidate`: tools/freeze_extraction_corpus.py:416,975; tools/audit_corpus_gaps.py:264; tools/t0_4/core.py:318; configs/t0_3a/taxonomy_register.json | 23d6228 / b6b76d9 / b937b58 | DETERMINISTIC_DERIVED | INCONSISTENT | TARGETED_ISSUE | Three operationalizations share one name. (a) T0 document-level `legacy_font` = document has >= 1 detector `broken_text` page: 24 documents, evidence INFERRED. (b) T0.3A `legacy_font_candidate` = `legacy_candidate_page_count > 0`, where a page is a candidate if detector broken_text OR any U+FFFD OR more than 5 private-use characters: 56 documents, 1,007 pages; the register describes only 'U+FFFD or PUA', and the config key `broken_font_min_pua_or_mojibake_ratio` (0.05) is never read. (c) T0.4 label/stratum = `cid_or_broken_text_indicator`, identical to `kind == broken_text` (803/803 pages; 20/20 units). Overlap: the 24 documents in (a) and (c) are inside the 56 in (b); 32 documents are (b)-only. | One documented predicate per name. | Legacy-font coverage differs by 2.3x (24 vs 56 documents) depending on the definition; the 32 (b)-only documents contribute no legacy-labelled page to T0.4. Bears on B1 and B5. | None in Phase 2 (frozen artifact; a separately authorized amendment would be required). Recorded here. | Phase 4/5 (Legacy) after author decision; Phase 3 must name the predicate |
| P2-08 | D Predicates | OCR-layer proxy: tools/freeze_extraction_corpus.py:977; tools/audit_corpus_gaps.py:249,1062; configs/t0_3a/taxonomy_register.json:134; dataset/corpus_gap_audit/gap_audit_report.md:86; tools/reconcile_t0_1.py:556-566 | 23d6228 / b6b76d9 / 879762a / 02bae11 | PROXY_OR_CANDIDATE | INCONSISTENT | TARGETED_ISSUE | About eight frozen artifacts describe the OCR-layer proxy as detection of 'PDF render mode 3 (invisible text layer)' or OCR producer signatures. The implemented predicate is `kind == 'scanned' and n_chars > 50` (T0 page profile); T0.1 consumes it unchanged (`is_t0_ocr`, line 249) and no code inspects PDF text render modes. 189 pages, all detector-`scanned`, none in T0.1 `scanned_page`. The evidence label stays CANDIDATE_PROXY. | Documented definition equals the implemented predicate. | The proxy can be misdescribed as a direct invisible-text measurement. The 71 documents whose MIXED status rests only on this proxy (see P2-13) inherit the description. | None in Phase 2 (frozen artifact; a separately authorized amendment would be required). Recorded here. | Amendment task / Phase 3 wording |
| P2-09 | D Predicates | TOC and annexure candidates: configs/t0_3a/taxonomy_register.json vs configs/audit_config.json and tools/audit_corpus_gaps.py:355-357,515,592,665 | 02bae11 / b6b76d9 | DETERMINISTIC_DERIVED | INCONSISTENT | TARGETED_ISSUE | (a) TOC: the register says the keyword is sought 'within the first 30 pages'; the implementation flags any page with a keyword and `physical_page < 50` (`toc_max_start_page_search`). The keyword list includes the substring `index`, and `toc_min_entries` is not applied to candidate flagging: 174 of 194 documents flagged (89.7%). (b) Annexure: the register says a keyword match 'in document outline or heading'; the implementation flags a document when any page's full text contains 'annexure' (`has_annexure_keyword`): 188 of 194 documents (96.9%). `combined_mdna_candidate` matches its register description (outline title or heading line), apart from two extra trigger words (`board`, `annexure`). | Documented window and scope equal the implemented window and scope. | The register misstates two predicates; both proxies are near-saturated. No sensitivity of the counts to the window or scope was tested (out of scope). | None in Phase 2 (frozen artifact; a separately authorized amendment would be required). Recorded here. | Amendment task / Phase 3 wording |
| P2-10 | C Terminology | T0.3A/T0.3A-R1 coverage matrix column `page_count` (t0_3a_coverage_matrix.csv, t0_3a_r1_coverage_matrix.csv) | 02bae11 / ff030d9 | DETERMINISTIC_DERIVED | INCONSISTENT | TARGETED_ISSUE | In the T0.3A/R1 matrices `page_count` is the total pages of member documents, not the pages exhibiting the condition (verified by summing `total_pages`): legacy_font_candidate 13,377 vs 1,007 candidate pages; has_ocr_layer_pages 23,877 vs 189 OCR-layer pages; multi_column_layout 37,667 vs 17,190; native 7,694 = total pages of the 60 NATIVE documents. The audit plan does not define the column, and T0.1 uses the suffix `_page_count` for pages that exhibit the condition. | A column name that states its denominator. | Misreading OCR-layer pages as 23,877 overstates them 126x. | None in Phase 2 (frozen artifact; a separately authorized amendment would be required). Recorded here. | Amendment task / Phase 3 (never quote the column as condition pages) |
| P2-11 | E Evidence | Proxy categories: table_candidate, annexure_candidate, toc_candidate, combined_mdna_candidate, OCR-layer, legacy-font, hidden-text, duplicate-text | b6b76d9 / 879762a / 02bae11 | PROXY_OR_CANDIDATE | CONSISTENT | NON_BLOCKING | Every proxy is labelled CANDIDATE_PROXY (T0.3A register: 17 categories) and NOT_REVIEWED at page level (condition_page_map 52,478 rows, table_candidates 29,476, language_candidates 2); T0.1R records human_reviewed_count = 0. No promotion to VERIFIED was found. Flagged prevalence is near-saturated: table_candidate 29,476 of 37,917 pages (77.7%); annexure_candidate 188/194 documents; toc_candidate 174/194. Not human-verified; no precision or recall exists. | Proxies stay proxies; prevalence not read as truth. | T0.3A prevalences are proxy prevalences. The largest T0.4 stratum (`table_candidate`, 138 units) is a proxy stratum. | None needed. | Phase 3 (wording) |
| P2-12 | C/E Evidence | Evidence-level vocabularies; `VALIDATED_METADATA` (18 files) | 23d6228 .. 63e3c04 | DOCUMENTED_CLAIM | UNVERIFIED | NON_BLOCKING | `VALIDATED_METADATA` labels era, size, stub and split metadata in T0.3A and T0.4 but is defined nowhere, and the T0 inventory has no `fiscal_year_evidence` column. Five vocabularies coexist without a mapping: T0 (KNOWN_FROM_PRIOR / OBSERVED / INFERRED / UNKNOWN), T0.1 (NOT_REVIEWED / MODEL_REVIEWED), T0.3A (EXISTING_CONDITION / EXISTING_CORPUS_FIELD / VALIDATED_METADATA / CANDIDATE_PROXY / DERIVED_INTERACTION / UNMEASURED), T0.4 (VALIDATED_METADATA / CANDIDATE_PROXY / NOT_YET_ANNOTATED), and the T0.4 sentinels. | Each evidence label defined once; a cross-stage mapping. | 'Validated' could be read as human-verified; nothing frozen supports that reading. | None (a definition would be a new decision). | Phase 3 |
| P2-13 | D/E Predicates | `document_representation` (T0.1R reconciled gap_audit_document_reconciled.csv; T0.3A register `native`/`mixed`) | 879762a / 02bae11 | DETERMINISTIC_DERIVED | CONSISTENT | NON_BLOCKING | Verified rule: NATIVE = scanned_page_count == 0 and ocr_page_count == 0 (60 documents; only 21 of them have every page native); MIXED = scanned > 0 or ocr > 0 (132 documents: 71 via the OCR-layer proxy only, 34 via scanned pages only, 27 via both); SCANNED = fully scanned (2). All 189 OCR-layer pages are detector-`scanned`. T0.1R documented the ocr-to-MIXED dependency (KNOWN_DEPENDENCY). The T0.3A register limit for `native` mentions only 'absence of scanned pages', and the category is labelled EXISTING_CONDITION, not proxy. | Document classes that state the proxy dependency at the point of use. | Document-level classes rest on detector heuristics that are not human-verified. | None needed beyond this record. | Phase 3 (wording) |
| P2-14 | B Consistency | T0 corpus_inventory.csv column `file_size_bytes` (tools/freeze_extraction_corpus.py:297) | 23d6228 | VERIFIED_FACT | INCONSISTENT | NON_BLOCKING | For 83 of 194 documents the recorded `file_size_bytes` differs from the size of the stored PDF (deltas -7.29 MB to +15.48 MB, median +222 KB, both signs) although the SHA-256 matches for 194/194. The tool copies `n_bytes` from the fetch-stage manifest instead of measuring the stored blob; the reason for the difference is not recorded. | A size field equal to the size of the hashed file. | Descriptive only. Identity is the SHA-256, which was verified. | None in Phase 2 (frozen artifact; a separately authorized amendment would be required). Recorded here. | Phase 3 (do not use as an integrity check) |
| P2-15 | B/C Consistency | Missing-byte records: freeze_protocol.md and stratification_report.md vs T0.4 preregistration and manifest Track B | 23d6228 / b937b58 | DETERMINISTIC_DERIVED | INCONSISTENT | NON_BLOCKING | T0 says the 14 MISSING records are 'excluded from every split'. In the T0.4 Track-B manifest 6 of the 14 carry their issuer's split with role INPUT_UNAVAILABLE (FIT 2, VALIDATION 4) and 8 are UNASSIGNED_HISTORICAL; the preregistration says records 'deliberately excluded from all frozen partitions remain UNASSIGNED_HISTORICAL'. The two statements agree for 8 records and are ambiguous for 6. Document counts (194 = 92 + 48 + 54) are unaffected. | One rule for missing records stated once. | Wording only. | None in Phase 2 (frozen artifact; a separately authorized amendment would be required). Recorded here. | Phase 3 |
| P2-16 | C Terminology | Legacy-font / REMAP vocabulary (configs/t0_4/metrics_spec.json, future_results_schema.json, oracle_routing_spec.json, T0.4 docs, P-X1 audit) | b937b58 / 33ba76a | DOCUMENTED_CLAIM | INCONSISTENT | NON_BLOCKING | One concept has seven names: `legacy_font` (routing class), `legacy_font_candidate` (label/stratum), `LEGACY` (oracle route), 'REMAP lane' (preregistration), `LEGACY_FONT_REMAP` (metrics level), `LEGACY_REMAP` (future-results track), 'legacy-font lane' (P-X1 audit). REMAP is never defined operationally; no code implements it (about a dozen non-CSV mentions, all prose, schema names or guard regexes). | One term per concept and one definition. | Naming only. The Legacy/REMAP decision itself is out of scope for Phase 2. | None in Phase 2 (frozen artifact; a separately authorized amendment would be required). Recorded here. | Phase 4/5 |
| P2-17 | G Routing | arpipe/CLAUDE.md 'Five page classes'; arpipe/models.py:19; arpipe/triage.py:284-285; arpipe/pipeline.py:171,232,247; arpipe/ocr.py:257; configs/t0_4/metrics_spec.json ROUTING.classes | b467e36 / 9cf5192 / 0fb8cbf / b937b58 | DOCUMENTED_CLAIM | INCONSISTENT | TARGETED_ISSUE | Hybrid: CLAUDE.md and models.py say 'read text, OCR the image'; the code puts HYBRID in NEEDS_OCR, reads the text layer only for DIGITAL pages, and OCRs whole pages (`_ocr_pages`); no code branches on HYBRID (only docstring hints). Blank: PageKind has six members but CLAUDE.md lists 'five page classes'; blank is excluded implicitly at triage.py:303 and pipeline.py:247 with no documented route. T0.4 ROUTING.classes (native_ok, legacy_font, broken_text, scanned, vector_text) omit hybrid and blank: 157 of 475 units (33%) sit in representation classes with no ROUTING class, and `legacy_font` is a ROUTING class with no PageKind and no producer. Route rows verified consistent: digital -> text layer; scanned, broken_text, vector_text -> OCR. | Every page class has one documented status; conflicting sources recorded, not resolved. | Routing semantics for hybrid depend on which frozen source is read. Phase 2 does not choose. | None. Both sources recorded; the choice belongs to the author (B1). | Author decision (B1) then Phase 4/5 |
| P2-18 | F/G Sampling | Closure audit section 5 wording; sampling_spec.json `sampling_stratum_priority`; tools/t0_4/core.py | 63e3c04 / 33ba76a | DETERMINISTIC_DERIVED | INCONSISTENT | NON_BLOCKING | The closure attributes the empty `broken_text` and `ocr_layer_proxy` strata to 'the corpus and priority order'. Both are structural: `legacy_font_candidate` (identical to broken_text, higher priority) always pre-empts `broken_text`, and the OCR-layer indicator is defined as `kind == scanned and ...`, so `scanned` always pre-empts `ocr_layer_proxy`. Only 15 of 77 declared (stratum, representation) pairs occur on any page; 13,392 of the 16,632 declared cells lie in the other 62 pairs, so most of the 16,157 zero-availability cells are structurally impossible combinations, not coverage gaps. | Interpretive text that names predicate identity and containment as the cause. | Citing '16,157 zero-availability cells' as a coverage gap would mislead. The closure's definition of the number is accurate. | None in Phase 2 (frozen artifact; a separately authorized amendment would be required). Recorded here. | Phase 3 (coverage wording) |
| P2-19 | H Gold/oracle | configs/t0_4/gold_schema.json; oracle_routing_spec.json; dataset/corpus_freeze/annotation_roster.csv | b937b58 / 23d6228 | VERIFIED_FACT | INCONSISTENT | NON_BLOCKING | (a) `OracleRouteGold` is not a frozen name: the oracle record exists only as `oracle_routing_spec.json:annotation_fields` and is not validated by `gold_schema.json`, whose `oneOf` has only page_gold and document_gold. (b) No T0.4 schema has a blinding field; `saw_pipeline_output` exists only in the T0 roster header (25 rows, all blank); blinding of primary annotators to detector output is unspecified (only the adjudicator is 'blind to all engine outputs'). (c) PageGold `annotation_provenance` requires annotator_id, protocol_version and adjudication_status; DocumentGold `annotation_provenance` is an unconstrained object. (d) `reading_order_pairs` are string-ID pairs with no reference unit. (e) The `bbox` coordinate convention is unspecified. | Gold and oracle records described consistently, with blinding fields. | The frozen record does not misdescribe these items; it is silent or asymmetric. Gold-phase schema work must supply them. | None in Phase 2 (frozen artifact; a separately authorized amendment would be required). Recorded here. | Phase 4/5 (Gold) |
| P2-20 | I Hash | configs/audit_config.sha256 vs configs/audit_config.json | b6b76d9 | DETERMINISTIC_DERIVED | INCONSISTENT | TARGETED_ISSUE | Recorded `8e26bec124a34806...`; actual blob `a3a575cda1ec7345...`. The recorded value is reproduced exactly by the blob plus one trailing newline, so the hashed content is identifiable. The two `audit_config.json` copies parse to identical JSON (same canonical hash); the dataset copy is CRLF, its `.sha256` matches (`65ed1a7e...`), and T0.1R's raw_input_manifest pins that copy. History shows a single commit for both files. | `sha256sum -c configs/audit_config.sha256` succeeds. | A verification command fails on a frozen T0.1 artifact. The pinned copy verifies, so no primary-foundation artifact is affected. | None in Phase 2 (frozen artifact; a separately authorized amendment would be required). Recorded here. Diagnosis: 1-byte trailing-newline difference. | Amendment task |
| P2-21 | I/K Hash | docs/experiments/PHASE1_FROZEN_FOUNDATION_VERIFICATION.md, 'Artifact verification' table | e52166f | DOCUMENTED_CLAIM | INCONSISTENT | TARGETED_ISSUE | 10 of the 27 SHA-256 strings in the table are marked 'Matches / VERIFIED' but do not equal the SHA-256 of the cited blob (issuer_split.csv, page_profile.csv, audit_config.json, gap_audit_document.csv, condition_page_map.csv, table_candidates.csv, language_candidates.csv, manual_review_manifest.csv, manual_review_results.csv, toc_offset_candidates.csv). None equals the SHA-256 of any of the 252 blobs in the closure tree or of the Phase-1 worktree file. Five share only the 8-character prefix printed in the closure report. The cited pin sources (raw_input_manifest.json, final_closure_audit.json) record the correct values. The other 17 rows match. | Recorded hashes reproducible from the cited artifacts. | The table cannot serve as a hash registry. Its 'byte for byte' conclusion is unsupported as written; the frozen artifacts themselves are unaffected. | None to the Phase-1 document (not Phase-2-owned). Phase 2 supplies a verified registry in the JSON record. | Phase-1 document owner |
| P2-22 | K Provenance | docs/experiments/PHASE1_FROZEN_FOUNDATION_VERIFICATION.md, 'Issues' section 2 | e52166f | DOCUMENTED_CLAIM | INCONSISTENT | TARGETED_ISSUE | Phase 1 says the T0.4 closure report 'documents 8 methodological questions'. The closure (markdown and JSON) documents two observations (native_clean_control reading; class-to-route map) and contains none of the double-annotation, adjudication, reading-order, HOLDOUT-authorization, hash-rank or precedence topics. The list of eight is the post-closure T0.4-GOLD register (B1-B8), renumbered and lossy in Phase 1 (no precedence item; 'route-class to oracle-class mapping' as item 8), and it defers them to 'Phase 2 (Gold Method Research and Integration)', whereas this Phase 2 is the integrity audit. | B1-B8 attributed to their source, with stable numbering. | A later reader following Phase 1 would look for the questions in the frozen closure and not find them. | None to the Phase-1 document. Section 'B1-B8' of this report gives the traced record. | Phase-1 document owner |
| P2-23 | K Provenance | B1-B8 register: docs/experiments/T0.4-GOLD_preimplementation_audit.md (d9f974b); T0.4-routing-clarification.md (916407d) | d9f974b / 916407d | HISTORICAL_CONTEXT | UNVERIFIED | NON_BLOCKING | The register exists only in post-closure safety-snapshot commits (subject 'REPOSITORY SAFETY SNAPSHOT - NOT A SCIENTIFIC METHODOLOGY COMMIT') on local branches; `origin/t0.4-gold` and `origin/t0.4-routing-clarification` still point at 63e3c04. The T0.4-LF record contains an unadopted recommendation ('A. One class, OCR route (recommended)', status T0.4_LF_BLOCKED, 'No rule was adopted'). Every checkable fact in the register was reproduced (see Audit results, B1-B8). | Deferred questions traceable from a published commit. | The register is outside the frozen foundation and not on the remote refs observed. | None. | Author (publication); Phase 3 cites by commit |
| P2-24 | K Provenance | Inputs outside Git: live_store PDFs (`*.pdf` ignored), corpus_inventory.csv `source_locator` (194 absolute local paths), P-X1 harness snapshot | 23d6228 / b937b58 | DOCUMENTED_CLAIM | CONSISTENT | NON_BLOCKING | PDF bytes are not in Git. Read-only byte hashing of the 194 local PDFs found 194/194 SHA-256 matches with the inventory and 0 missing. T0/T0.1 independent re-derivation therefore needs the local store; the T0.4 sampling reproduction needs only Git-tracked CSVs. The P-X1 reuse audit's description of the P-X1 harness rests on an external snapshot the audit itself says is 'not present in the T0.3A-R1 Git tree'; those descriptions are UNVERIFIED from the tree. | Inputs either in Git or identified by a verifiable hash. | T0/T0.1 numbers can be re-derived only on this machine's store. | None. | Phase 3 (record the dependency) |
| P2-25 | K Provenance | T0.3A register/measurement ordering (02bae11) vs T0.3A-R1 pre-specification (f0e5805 -> ff030d9) | 02bae11 / f0e5805 / ff030d9 | DOCUMENTED_CLAIM | UNVERIFIED | NON_BLOCKING | T0.3A's subject says 'frozen taxonomy input', but the register and the measurement outputs are in one commit, so Git cannot show that the register preceded the measurement. For R1, f0e5805 adds only configs/t0_3a_r1/taxonomy_register.json and is an ancestor of ff030d9, so that ordering is Git-verifiable; however both era categories had already been measured in T0.3A (58/6,863/29 and 136/31,054/36, identical in R1), and R1 changed only the justification text of `post_2015`. | Pre-specification claims supported by commit order. | 'Pre-specified before measurement' holds for the R1 engine run, not for the era counts having been unseen. | None. | Phase 3 (wording) |
| P2-26 | J HOLDOUT | Legacy holdout protocol (configs/eval_protocol.md, labels_*_queue.csv, eval_holdout_log.csv) vs T0 HOLDOUT; raw T0.1 report line 155 | 23d6228 / b6b76d9 | DETERMINISTIC_DERIVED | UNVERIFIED | TARGETED_ISSUE | 'Holdout' has at least three referents in the frozen tree: (1) T0 frozen `HOLDOUT` (54 documents, 9 issuers, issuer-disjoint, seed 20260918); (2) the legacy holdout of `configs/eval_protocol.md` (45-document queue, document-level random split, seed 20260912, `contaminated` flag, 4 holdout-scoring log entries on 2026-09-11 at commit bc5f174); (3) P-X1's historical development/holdout page partitions (external snapshot). T0 and T0.4 never reference the legacy protocol. By SHA-256, the 45 legacy-holdout documents fall in T0 FIT 18 / VALIDATION 13 / HOLDOUT 14, and 26 of the 92 legacy-FIT-queue documents fall in T0 HOLDOUT. `labels_holdout.csv` has no data rows, and none of the 20 historical labels maps to a T0 HOLDOUT document. The raw T0.1 report says the HOLDOUT has '9 issuers completely unseen during development'; T0.1R's claim audit (58 claims) neither audits nor retracts it. Whether ARPipe development before T0 (2026-09-18) processed HOLDOUT documents is not established by the frozen record. | A single, defined meaning of 'held-out'/'unseen', and a stated position on pre-T0 exposure. | T0/T0.4 HOLDOUT is locked from T0.4 tuning and gold annotation; the frozen record does not support 'never processed by ARPipe'. No leakage evidence was found. | None. Absence of evidence is not treated as evidence of absence. | Phase 3 (claims/scope) |
| P2-27 | J HOLDOUT | T0 challenge_coverage_manifest.csv; T0.1 manual_review_manifest.csv / manual_review_results.csv; T0.3A `devanagari_candidate` | 23d6228 / b6b76d9 / 02bae11 | DETERMINISTIC_DERIVED | UNVERIFIED | NON_BLOCKING | HOLDOUT documents took part in coverage-oriented selections, all before T0.4: the challenge set has 8 HOLDOUT documents (T0 documents it as overlapping and 'never an independent test set'); T0.1's 72-item manual-review queue has 26 HOLDOUT items, and the raw results labelled all 72 `MODEL_REVIEWED` by `gemini_assistant_model` with notes that only restate the detector's own fields (e.g. 'Model inspected: vector_grid=True, aligned_numeric_rows=1'); T0.1R re-labelled all 72 `NOT_REVIEWED` ('auto-relabelled from json snippet without model inspection'). The only Devanagari documents (2, one issuer) are both HOLDOUT (FIT 0, VALIDATION 0). | HOLDOUT used only as the T0.4 policy allows; queued reviews not executed on HOLDOUT. | No evidence that any HOLDOUT page was actually reviewed. Git cannot exclude content shown to an external model outside the recorded workflow. Executing the T0.1 review queue as-is would inspect 26 HOLDOUT items. | None. | Phase 3/4 (do not execute the queue as-is) |
| P2-28 | B/K Consistency | Closure decision wording `CLOSED_FOR_GOLD_PHASE` (T0.4_final_closure_audit.md section 12; commit subject 63e3c04) | 63e3c04 | DOCUMENTED_CLAIM | CONSISTENT | NON_BLOCKING | The decision is defined by four closure conditions (vector_text_route, sampling_cell_inspection, sampling_metadata_provenance, held_out_terminology); the closure itself lists two observations to settle 'before oracle annotation'. The post-closure register (B1-B8) later lists eight open items. The label is accurate for its four conditions. | A closure label read within its stated scope. | 'Closed for the gold phase' must not be read as 'Gold protocol specified'. | None. | Phase 3 (wording) |

### MUST FIX BEFORE PHASE 3

None. No finding meets the blocker definition (task section 23): no primary-foundation hash mismatch, no unresolved denominator contradiction, no HOLDOUT breach, no missing provenance artifact, no unidentifiable routing implementation, no missing Git object.

### SHOULD FIX BEFORE PHASE 3

Important but non-blocking. All are corrections to frozen or Phase-1 text that Phase 2 may not make; each needs a separately authorized amendment, or must be honoured as a citation rule in Phase 3.

- **P2-01** (INCONSISTENT, NON_BLOCKING): A/L Lineage - Task milestone registry
- **P2-03** (INCONSISTENT, TARGETED_ISSUE): B/D Consistency - T0.3A and T0.3A-R1 `core_relevance_summary`
- **P2-04** (INCONSISTENT, TARGETED_ISSUE): D/C Predicates - T0.4 `condition_labels` label `native_ok` vs `representation_class` `native_ok`; T0.1 `native_page`
- **P2-08** (INCONSISTENT, TARGETED_ISSUE): D Predicates - OCR-layer proxy
- **P2-09** (INCONSISTENT, TARGETED_ISSUE): D Predicates - TOC and annexure candidates
- **P2-10** (INCONSISTENT, TARGETED_ISSUE): C Terminology - T0.3A/T0.3A-R1 coverage matrix column `page_count`
- **P2-17** (INCONSISTENT, TARGETED_ISSUE): G Routing - arpipe/CLAUDE.md 'Five page classes'; arpipe/models.py
- **P2-20** (INCONSISTENT, TARGETED_ISSUE): I Hash - configs/audit_config.sha256 vs configs/audit_config.json
- **P2-21** (INCONSISTENT, TARGETED_ISSUE): I/K Hash - docs/experiments/PHASE1_FROZEN_FOUNDATION_VERIFICATION.md, 'Artifact verification' table
- **P2-22** (INCONSISTENT, TARGETED_ISSUE): K Provenance - docs/experiments/PHASE1_FROZEN_FOUNDATION_VERIFICATION.md, 'Issues' section 2

### DEFERRED TO PHASE 3

Claims, scope, population, sampling and wording questions.

- **P2-02** (CONSISTENT, NON_BLOCKING): A Lineage - T0.4 preregistration and P-X1 reuse audit
- **P2-05** (INCONSISTENT, NON_BLOCKING): D/C Predicates - `scanned` in T0.1
- **P2-06** (INCONSISTENT, NON_BLOCKING): D/C Predicates - `multi_column` in T0.1/T0.3A vs T0.4
- **P2-11** (CONSISTENT, NON_BLOCKING): E Evidence - Proxy categories
- **P2-12** (UNVERIFIED, NON_BLOCKING): C/E Evidence - Evidence-level vocabularies; `VALIDATED_METADATA`
- **P2-13** (CONSISTENT, NON_BLOCKING): D/E Predicates - `document_representation`
- **P2-14** (INCONSISTENT, NON_BLOCKING): B Consistency - T0 corpus_inventory.csv column `file_size_bytes`
- **P2-15** (INCONSISTENT, NON_BLOCKING): B/C Consistency - Missing-byte records
- **P2-18** (INCONSISTENT, NON_BLOCKING): F/G Sampling - Closure audit section 5 wording; sampling_spec.json `sampling_stratum_priority`; tools/t0_4/core.py
- **P2-23** (UNVERIFIED, NON_BLOCKING): K Provenance - B1-B8 register
- **P2-24** (CONSISTENT, NON_BLOCKING): K Provenance - Inputs outside Git
- **P2-25** (UNVERIFIED, NON_BLOCKING): K Provenance - T0.3A register/measurement ordering
- **P2-26** (UNVERIFIED, TARGETED_ISSUE): J HOLDOUT - Legacy holdout protocol
- **P2-27** (UNVERIFIED, NON_BLOCKING): J HOLDOUT - T0 challenge_coverage_manifest.csv; T0.1 manual_review_manifest.csv / manual_review_results.csv; T0.3A `devanagari_candidate`
- **P2-28** (CONSISTENT, NON_BLOCKING): B/K Consistency - Closure decision wording `CLOSED_FOR_GOLD_PHASE`

### DEFERRED TO PHASE 4/5+

Gold, Legacy, OCR, REMAP, annotation and related methodological questions.

- **P2-07** (INCONSISTENT, TARGETED_ISSUE): D Predicates - `legacy_font_candidate`
- **P2-16** (INCONSISTENT, NON_BLOCKING): C Terminology - Legacy-font / REMAP vocabulary
- **P2-19** (INCONSISTENT, NON_BLOCKING): H Gold/oracle - configs/t0_4/gold_schema.json; oracle_routing_spec.json; dataset/corpus_freeze/annotation_roster.csv

### VERIFIED SAFE

| ID | Area | Checked and passed |
|---|---|---|
| V01 | Lineage | All nine registered milestone commits exist as commit objects (with the P2-01 SHA correction); the range T0..closure has 14 commits including T0 and 13 after T0; 0 merge commits; linear ancestry; 5 unregistered intermediate commits (55e5075, 8042042, 937065e, 5089a0b inside T0.1R; f0e5805 inside T0.3A-R1). |
| V02 | Lineage | Closure tree is 91ee231effb2f9ba5cef39d5c17059e3aace0996; each registered commit SHA commits to its tree (recorded in section 3). Branch tips still equal the registered commits: extraction-corpus-freeze 23d6228, t0.1-gap-audit b6b76d9, t0.1-reconcile 879762a, t0.2-robustness-gate ef2e8c5, t0.3a-document-coverage 02bae11, t0.3a-r1-taxonomy-extension ff030d9, t0.4-ocr-benchmark 63e3c04 (and origin/t0.4-* 63e3c04). |
| V03 | Git objects | No replace refs, no grafts, not shallow, no alternates; `git fsck --full --no-dangling` exit 0. The E0 safety commits (dea3ae5, e8517ee, 58f79b85) are not ancestors of the closure; 916407d, d9f974b and the Phase-1 commits descend from it. Phase 1's E0 finding is outside the T0-T0.4 lineage. |
| V04 | Frozen artifacts | 178 files were touched by the 14 commits; 0 pre-existing files were changed or deleted; 18 files were amended once, all inside their own stage (T0.1R internals: 2 configs, 1 test, 2 tools, 9 reconciled outputs; T0.4 audited tree: 2 docs, audit_t0_4_setup.py, README). No later stage altered an earlier stage's artifacts. |
| V05 | Hashes | 155 of 156 recorded (path, sha256) pairs in frozen manifests match the Git blobs at 63e3c04: T0 hashes/*.sha256 (5), input_hashes.json x3 (36), raw_input_manifest (29), reconciliation_manifest (16), T0.2 manifest (17), T0.3A manifest (12), T0.3A-R1 manifest (19), config_hashes.json (12), setup_audit (2), benchmark_manifest source_hashes (6), dataset audit_config.sha256 (1). The single exception is P2-20. |
| V06 | Sampling | READ_ONLY_REPRODUCTION: the frozen builder run with output redirected to scratch reproduces benchmark_manifest.json (d1eb3042c82900e345541ef6b7afbba95a6d7d8dc2e7948e5d610eaf89912f15) and config_hashes.json (199c7d56c622e3e19fe58adadede2871ad4f2e3f459adb53f4a4fd8c816fd74f) byte for byte; sampling_spec.json hashes to 412e040e... as recorded. This is a deterministic repeat. A separate re-implementation written for this audit (code-informed, different code path) reproduces all 475 units on eight fields, and reproduces every closure count: 16,632 declared cells, 475 observed, 16,157 zero-availability, 82 singletons (stratum and split breakdowns), cell sizes 1/8/1,908, buckets 134/85/95/79, 401 multi-label pages, FIT 223 / VALIDATION 118 / HOLDOUT 134. The closure engine re-run in --check mode against 33ba76a exits 0. |
| V07 | Corpus | 208 records = 194 present + 14 MISSING; 194 unique SHA-256 and 37,917 pages; documents 92/48/54 and issuers 18/9/9 (36) for FIT/VALIDATION/HOLDOUT; issuer-disjoint; development 60 inside FIT; roster 25 inside development; per-issuer document counts match issuer_split.csv; local PDF bytes match 194/194 recorded SHA-256. |
| V08 | Consistency | Totals 194 / 36 / 37,917 / 208 / 14 are stated consistently in the T0, T0.1, T0.1R, T0.3A-R1 and T0.4 summaries (no off-by-one strings). The acquisition decision is NO_ACQUISITION in T0.1R, T0.2, T0.3A, T0.3A-R1 and T0.4 (T0.2: acquisitions_currently_justified_count 0, pdf_acquisitions_executed 0). |
| V09 | T0.3A-R1 | The 33 non-era coverage rows and register records are identical to T0.3A (only `post_2015` justification text differs); era counts 58 + 136 = 194 documents and 6,863 + 31,054 = 37,917 pages; the R1 register in configs/ equals the dataset copy byte for byte. |
| V10 | Joins | Page numbering is 0-based and contiguous in all 194 documents; every T0.1 auxiliary key (52,478 + 29,476 + 2) resolves to a page-profile row; no off-by-one in the T0.4 join. |
| V11 | Evidence | All detector-derived T0.4 labels are CANDIDATE_PROXY (1,062 label-evidence entries) and only `pre_2015` is VALIDATED_METADATA (184); page-level T0.1 files are 100% NOT_REVIEWED; human_reviewed_count is 0. No proxy-to-truth promotion was found. |
| V12 | HOLDOUT | No HOLDOUT gold, annotation, engine output or benchmark result exists in the frozen tree: the roster is FIT-only with all 14 gold/blinding columns blank in 25 rows; no other CSV carries filled annotation columns; the oracle literal subset contains 0 HOLDOUT units and the spec restricts it to FIT and VALIDATION; all 134 Track-A and 54 Track-B HOLDOUT units are FINAL_HOLDOUT_LOCKED; all 475 image hashes are NOT_YET_RENDERED. T0.4 sampling includes HOLDOUT (134 units) by protocol ('predeclared and integrity-checked but not inspected for tuning'); it does not exclude it. |
| V13 | Tests | Deterministic repeat of the closure test claim: tests/t0_4 96 passed; the other tests/ suites 59 passed; arpipe/tests 185 passed, 17 skipped; total 340 passed + 17 skipped = 357 collected, equal to the closure record. The worktree stayed clean after every run. |
| V14 | B-register facts | Reproduced from frozen data: `legacy_font_candidate` equals `kind == broken_text` (803/803 pages, 20/20 units); hybrid 102 and blank 55 units; `native_clean_control` on 60 units and in 0 condition_labels; oracle subset 79 (FIT 52, VALIDATION 27) literal vs 121 (80/41) by stratum, of 341 FIT+VALIDATION units; first rank digit in 0-3 for 355/475 (74.7%) units and 50/79 (63.3%) of the literal subset, '0' for 249. |
| V15 | Routing | vector_text -> OCR is confirmed in code (NEEDS_OCR) and in closure section 1; scanned and broken_text -> OCR and digital -> text layer are consistent across code, comments and CLAUDE.md; the 14 default.yaml triage thresholds equal the triage.py constants. |
| V16 | Terminology | T0 role sets are coherent (development 60 inside FIT 92; annotation roster 25 inside development; challenge 45 documented as overlapping FIT 23 / VALIDATION 14 / HOLDOUT 8 and development 16). 'Unseen' does not occur in T0.4 scoped files; 'unobserved' is used only for coverage; the closure engine's terminology check passes on recomputation. |

### Summary counts

| Measure | Count |
|---|---|
| Total findings | 28 |
| CONSISTENT | 5 |
| INCONSISTENT | 18 |
| UNVERIFIED | 5 |
| OUT_OF_SCOPE (findings) | 0 |
| Blockers | 0 |
| Targeted issues | 11 |
| Non-blocking findings | 17 |
| Documentation-only issues | 8 |
| Deferred questions (findings carrying an open question) | 8 |
| B1-B8 items open (unresolved, undecided) | 8 |
| Open questions listed (OQ1-OQ6) plus one out-of-scope entry (OQ7) | 6 + 1 |
| Verified-safe items | 16 |

## 8. Repairs

**No repair was made.** No frozen artifact, configuration, manifest, code, corpus file, sampling specification, Gold schema, protocol or HOLDOUT artifact was edited. Repair gate (task section 21) applied to every proposed correction of a frozen or Phase-1 artifact (P2-03, P2-08, P2-09, P2-10, P2-20, P2-21, P2-22): the finding is real and directly supported by frozen evidence, but each correction fails the last question (it cannot be made without modifying historical frozen objects or a non-Phase-2 document), so it is classified and deferred. The Phase-2-owned outputs are this report, the JSON record and the scripts; no objectively erroneous statement was found in them on re-audit (counts in the JSON are computed from the same data as this report, and the hash tallies were recomputed from the raw check rows).

## 9. B1-B8 (recorded, not decided)

Origin: the register B1-B8 is the "Blocker register" of `docs/experiments/T0.4-GOLD_preimplementation_audit.md` (commit `d9f974b`); B1/B2 are also worked in `docs/experiments/T0.4-routing-clarification.md` (commit `916407d`). Both are post-closure, non-frozen records. The frozen closure names only two open observations (native_clean_control reading; class-to-route map). Every checkable fact in the register was reproduced from frozen data (V14). Classification uses the task vocabulary; nothing was converted into an implementation decision.

| ID | Item | Frozen evidence (verified) | Faithfully represented? | Contradicts recorded status? | Classification |
|---|---|---|---|---|---|
| B1 | Legacy route / class-to-route map (`ORACLE_ROUTE_MAPPING_UNRESOLVED`) | Verified: detector has no `legacy_font` kind; `legacy_font_candidate` is `kind == broken_text` (803/803, 20/20); broken_text is in NEEDS_OCR; the REMAP lane exists in T0.4 prose only. Closure observation 2 records the class-to-route gap for broken_text/REMAP. hybrid (102 units) and blank (55) have no ROUTING class. | Yes. The frozen closure represents the legacy part (observation 2); hybrid/blank are recorded only in the post-closure register. The register's hybrid 'production route' follows CLAUDE.md prose, while NEEDS_OCR includes hybrid (P2-17). | None against the unresolved status. | REQUIRES AUTHOR DECISION. The T0.4-LF record holds an unadopted DOCUMENTED RECOMMENDATION (one class, OCR route). |
| B2 | Route precedence for overlapping classes (`ROUTE_PRECEDENCE_UNRESOLVED`) | Verified: only `sampling_stratum_priority` names both (`legacy_font_candidate` before `broken_text`), scoped to choosing a primary sampling stratum. No routing precedence is frozen. Closure section 5 attributes the empty `broken_text` stratum to corpus and priority order; the cause is predicate identity (P2-18). | Yes for the register; the frozen closure is silent on precedence. | None. | REQUIRES AUTHOR DECISION (collapses into B1 if one class is chosen; that option is a documented recommendation, not a decision). |
| B3 | Oracle subset reading of `native_clean_control` | Verified: stratum only (0 of 475 units carry it as a label); 79 units literal vs 121 by stratum. The 22 hybrid units in the stratum (60 units, all splits) show it is not a clean-native set (P2-04). Closure observation 1 states both readings. | Yes. Matches closure observation 1 ('Decide which reading is intended before oracle annotation'). | None. | REQUIRES AUTHOR DECISION. |
| B4 | Oracle double-annotation rank undefined | Verified: `double_annotation.rule` names no seed, key or encoding; the only frozen rank on units is the sampling `selection_rank` (minimum per cell), which yields 355/475 (74.7%) and 50/79 (63.3%) in 0-3 against `expected_fraction` 0.25. The closure does not mention it. | Yes for the register; not represented in the frozen closure (post-closure finding). | None. | REQUIRES AUTHOR DECISION. |
| B5 | Oracle evidence policy vs distinguishing NATIVE from LEGACY | Frozen text verified: `adjudication.allowed_evidence` = 'rendered page image plus the written route protocol'; primary-annotator evidence unspecified. The register's inference that a rendered image cannot separate NATIVE from LEGACY is a reasoned claim that no frozen experiment tests, and Phase 2 does not test it. | Yes as a documented claim; its truth is UNVERIFIED here. | None. | OPEN METHODOLOGICAL QUESTION. |
| B6 | General double-annotation rate for PageGold and DocumentGold | Verified: a double-annotation and adjudication rule exists only in `oracle_routing_spec.json`; the roster has one `annotator_id` column; PageGold provenance has an `adjudication_status` enum but no rate or slice rule; DocumentGold provenance is unconstrained (P2-19); the closure is silent. | Yes. | None. | REQUIRES AUTHOR DECISION. |
| B7 | Reading-order reference unit | Verified: `reading_order_pairs` are pairs of strings with no stated unit; `metrics_spec.json` unit is 'page_or_document_as_declared'; `common_output_schema.json` carries block_id and line_id, each possibly NOT_AVAILABLE; gold_schema has `lines` and `regions` but no blocks. | Yes. | None. | REQUIRES AUTHOR DECISION. |
| B8 | HOLDOUT gold annotation authorization | Verified: `holdout_policy` = `allowed_before_final_freeze: false`, three allowed uses (manifest predeclaration, schema validation, split-integrity audit), five forbidden uses; annotation is named in neither list. The register cites only the allowed-uses list; the `false` flag supports a default-deny reading, so both readings are textually available. No HOLDOUT annotation exists in the frozen tree; the legacy protocol permits blind holdout labelling but predates the split. | Yes, with the nuance that the register omits the `allowed_before_final_freeze: false` flag. | None. | REQUIRES AUTHOR DECISION. |

**ALREADY FROZEN (verified, not B items):**

- Oracle subset excludes HOLDOUT ('FIT and VALIDATION partitions only'; 0 HOLDOUT units under either reading).
- vector_text -> OCR in the ACTUAL_ROUTING condition (closure section 1); digital -> text layer; scanned and broken_text (detector route) -> OCR.
- Track-A unit key (document_id, page_number), Track-B unit key (document_id), the renderer contract (RGB PNG, 300 DPI, no preprocessing) and the NOT_YET_ANNOTATED / NOT_YET_RENDERED / INPUT_UNAVAILABLE sentinels.

The unresolved status of B1-B8 is not a Phase-2 defect. Integrity issues connected to them: P2-17 (hybrid/blank route sources), P2-18 (empty strata), P2-19 (Gold interface), P2-22 (Phase-1 misattribution and renumbering), P2-23 (register provenance).

## 10. Unresolved questions

| ID | Class | Question |
|---|---|---|
| OQ1 | OPEN_QUESTION | B1-B8 (see the B1-B8 table). None is resolved by this audit. |
| OQ2 | OPEN_QUESTION | Whether ARPipe development before T0 processed or inspected the documents now in HOLDOUT (P2-26). |
| OQ3 | OPEN_QUESTION | Which `legacy_font` predicate any later claim uses: 24-document detector-based, 56-document T0.1-based, or a future one (P2-07). |
| OQ4 | OPEN_QUESTION | Whether the raw T0.1 statement '9 issuers completely unseen during development' can be supported (P2-26). |
| OQ5 | OPEN_QUESTION | The meaning of `VALIDATED_METADATA` and a mapping between the five evidence vocabularies (P2-12). |
| OQ6 | OPEN_QUESTION | Whether frozen amendments (P2-03, P2-08, P2-09, P2-10, P2-20) are to be made, and by which authorized task. |
| OQ7 | OUT_OF_SCOPE | Corpus sufficiency, population adequacy, acquisition necessity, Gold design optimality, OCR necessity or strategy, Legacy/REMAP status, and final thesis claims. |

## 11. Phase-3 dependencies

- Cite T0.4 documents at the 63e3c04 blobs; the preregistration and P-X1 audit changed at 33ba76a (P2-02).
- Do not quote the T0.3A/R1 sentence 'native digital documents (191 docs)' or the coverage-matrix `page_count` as condition pages (P2-03, P2-10).
- State which predicate is meant by native, scanned, multi_column and legacy_font whenever a count is quoted (P2-04 to P2-07); use `representation_class`, not `condition_labels`, for page kind.
- Describe the OCR-layer and TOC candidates by their implemented predicates, and keep every candidate labelled as a proxy that is not human-verified (P2-08, P2-09, P2-11, P2-13).
- Do not present the 16,157 zero-availability cells as coverage gaps (P2-18); the definition of the figure is accurate.
- Define 'unseen' and 'held-out' before any claim, and do not claim HOLDOUT was never processed by ARPipe (P2-26); do not execute the T0.1 manual-review queue on its 26 HOLDOUT items (P2-27).
- Use the verified hash registry in the JSON record, not the Phase-1 hash table (P2-21).
- Cite the B1-B8 register by commit (d9f974b, 916407d), not through the Phase-1 report (P2-22, P2-23).
- Read `CLOSED_FOR_GOLD_PHASE` within its four-condition scope (P2-28).
- The Devanagari coverage exists only in HOLDOUT (2 documents, 1 issuer); any Devanagari claim interacts with the HOLDOUT lock (P2-27).

## 12. Final readiness decision

| Gate criterion (task section 24) | Result |
|---|---|
| 1. Milestone lineage intact | Met (V01-V04) |
| 2. Required frozen artifacts present and identifiable | Met: 155/156 manifest-recorded hashes match, the one exception is explained (P2-20); 4/4 closure-report scalar hashes; 194/194 local PDF hashes |
| 3. No HOLDOUT integrity breach | Met (section 6J); caveats P2-26, P2-27 are open questions, not breaches |
| 4. No unresolved provenance defect affecting a primary foundation artifact | Met: the hard-coded sentence in P2-03 has a traceable origin (T0.1 CLAIM:C005) and is mislabelled, not untraceable |
| 5. Proxies remain labelled as proxies | Met (V11, P2-11) |
| 6. Important predicates traceable to implementation | Met, with documented-versus-implemented mismatches recorded (P2-07 to P2-09) |
| 7. Sampling provenance traceable | Met (V06, section 6F) |
| 8. Routing semantics identifiable without silent inference | Met, with the hybrid/blank source conflict recorded and not resolved (P2-17) |
| 9. Remaining issues non-blocking or explicitly deferred | Met: 0 blockers; 10 SHOULD_FIX, 15 DEFERRED_P3, 3 DEFERRED_P45 |

**Decision: FOUNDATION READY FOR PHASE 3 - WITH DOCUMENTED ISSUES.** Phase 3 may start once the SHOULD_FIX items are either amended by separately authorized tasks or honoured as citation rules (section 11). This audit did not start Phase 3, Gold, Legacy or OCR work and made no scientific decision.

## Appendix A. Scripts (read-only; run from the repository root)

| Script | Purpose |
|---|---|
| `t0_split_arithmetic.py` | T0 split, role-set and roster arithmetic (P2-15, P2-26, V07) |
| `legacy_holdout_mapping.py` | Legacy label/queue files mapped to T0 splits by SHA-256 (P2-26) |
| `document_predicates.py` | Document-level representation predicates and cross-tab (P2-03, P2-13) |
| `page_numbering_and_joins.py` | Page-numbering base and auxiliary-key joins (V10) |
| `reproduce_sampling.py` | Code-informed re-implementation of the T0.4 sampling; closure and B-register counts (V06, V14) |
| `predicate_overlaps.py` | Page- and document-level predicate overlaps; evidence status values (P2-04 to P2-08) |
| `verify_recorded_hashes.py` | Recomputes every recorded (path, sha256) pair against Git blobs (V05, P2-20, P2-21) |
| `pdf_hash_and_cell_feasibility.py` | Local PDF byte hashes vs inventory; structural feasibility of the cell space (P2-14, P2-18) |

One-off Git queries used in the audit: `git rev-list`, `git rev-list --merges`, `git merge-base --is-ancestor`, `git diff-tree --name-status -r --root` per commit, `git ls-tree -r -z`, `git cat-file --batch`, `git fsck --full --no-dangling --no-progress`, `git for-each-ref refs/replace`, and `git show <commit>:<path>` for the Phase-1, B-register and T0.4-LF records.

## Appendix B. Tests run (deterministic repeat)

| Suite | Result |
|---|---|
| `tests/t0_4` | 96 passed |
| `tests` excluding `t0_4` (T0.1, T0.2, T0.3A, T0.3A-R1) | 59 passed |
| `arpipe/tests` | 185 passed, 17 skipped |
| Total | 340 passed + 17 skipped = 357 collected; equals the closure record |
| Closure engine `--check` against `33ba76a` | exit 0 |

A first attempt to run the wider suite in a `git archive` export failed with 11 environment errors (no `.git`, and a `../arpipe-0.1.0/live_store` path that does not exist outside the real layout); it says nothing about the foundation and was superseded by the runs above in the real worktree.
