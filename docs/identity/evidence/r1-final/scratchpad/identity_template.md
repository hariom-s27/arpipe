# ARPipe Runnable Identity v1

Pinned 2026-09-26 by R1-FINAL v3, under the author-ratified **T0.4 Amendment 01**
(`docs/identity/T0_4_AMENDMENT_01.md`, ratified by Hariom Singh on 2026-09-26).

Evidence labels: **VERIFIED** (repository content or command output), **DERIVED** (mechanical
consequence of verified facts), **INFERRED** (interpretation not stated by the repository),
**NOT VERIFIABLE** (required evidence is absent). Every SHA below was taken from Git command
output in full.

## 1. Final tip commit

| Item | Value |
|---|---|
| Tip SHA | `@@TIP@@` |
| Parent SHA | `@@PARENT@@` |
| Subject | `test(r1): enforce T0.4 Amendment 01 and register strict expected failures` |
| Branch | `r1-final` |
| Start of this task | `1db8ccddf282ec86a6785df80b04a73d680a60f9` (`docs(r1): record T0.4 guard forensics`) |
| `arpipe/` tree at the tip | `@@ARPIPE_TREE@@` |
| `configs/` tree at the tip | `@@CONFIGS_TREE@@` |

The identity is pinned at the tip above. Section 7's later records commit adds documentation
only and changes no file in the identity universe; the universe digest in section 3 is the
value to re-check.

## 2. Identity file universe

Obtained with `git ls-files arpipe/ configs/` at the tip. **VERIFIED**

- Total files: **@@COUNT@@**
- Combined manifest digest: `@@DIGEST@@`
- Recipe: SHA-256 over UTF-8 lines `<file sha256>  <path>\n`, one per file, in bytewise path
  order. Recomputing this digest from section 3's table reproduces the value. **DERIVED**
- Every file's working-tree bytes hash equal to its Git blob at the tip (0 mismatches over
  @@COUNT@@ files). **VERIFIED**
- The universe matches the previously observed 59-file universe exactly: same 59 paths, same
  59 SHA-256 values, same combined digest. Nothing was added, removed or changed. **VERIFIED**
- Untracked material (`__pycache__`, `*.pyc`, scratch files, built fixtures) is excluded: the
  universe is exactly the Git-tracked set.

## 3. Per-file SHA-256

| # | Path | SHA-256 |
|---|---|---|
@@TABLE@@

## 4. A1–A4 composition

The tip differs from the T0.4 base `ff030d97c13c8a2a977521bf91be2aca0cbf3034` under `arpipe/`
in exactly four files, each supplied by one authorizing commit. All five SHAs were resolved
from Git. **VERIFIED**

| Item | Commit | Path | Change |
|---|---|---|---|
| A1 | `d5513859a5315800a7b6c68711756798129ab8ee` | `arpipe/models.py` | `Confidence.QUARANTINE`; optional fields `StoredDoc.script_map`, `PageProfile.script_meta`, `DocProfile.script_map`, `MDASpan.body_script` (+9 lines) |
| A2 | `ca1498f75f14495bfc6ec829ef2b5ef728da2d3d` | `arpipe/triage.py` | the `verify` import, `_compute_page_script_meta`, `script_meta` in `profile_page` after `kind` is assigned, `script_map` in `profile_document` (+73 lines) |
| A3 | `ab9666b032a5838be3ae3a24a58aae68a4fd46b0` | `arpipe/ocr.py` | the `OcrEngineUnavailable` class only, with no raise paths (+17 lines) |
| A4 | `24b8e000f23d18faabd16f828bd20eeb5328ddf7` | `arpipe/store.py` | `write_year(..., write_span=True)` parameter and its branch (+19 −6 lines) |

Each authorizing commit touches exactly its one path, its parent chains A1 → A2 → A3 → A4, and
each file at the tip equals that commit's blob byte for byte. **VERIFIED**

Relation to the D6 provider half (E0 snapshot `dea3ae5399be50872768c8703c878c907ee6818b`,
`arpipe/` tree `48faf1a372e720e8bf941f1a4359a62430d0b133`): **VERIFIED**

| Path | Candidate vs E0 | Note |
|---|---|---|
| `arpipe/models.py` | byte-identical to E0 | blob `e91c73c8d537a7873a765933bd959feed0aa9fd9` |
| `arpipe/triage.py` | byte-identical to E0 | blob `de9d528924db97f733f9f2ee985e6d1a8be406af` |
| `arpipe/ocr.py` | strict subset of E0 | every candidate-added line occurs in E0's file; 59 further E0-added lines (the P-B5 raise paths) are **not** taken |
| `arpipe/store.py` | strict subset of E0 | every candidate-added line occurs in E0's file; 70 further E0-added lines (the `state.py` hooks) are **not** taken |

Consistent with D6 section 9.5, which authorises no P-B5 raise behaviour and no `state.py`.
`arpipe/patterns.py` is kept at the Phase-4/T0.4-base blob `afd8e86a9641ba4d1f95ef9be39e58a0a228bece`;
its 2026-09-17 executed bytes are not recoverable from any commit (it was dirty in the
`reports/pm1_baseline.json` porcelain). That is an irreducible limitation, recorded, not repaired.
**VERIFIED** (blob); **NOT VERIFIABLE** (its executed bytes)

## 5. Governing reconstruction rule

From the ratified amendment, sections 1, 2 and 5:

1. Only `arpipe/models.py`, `arpipe/triage.py`, `arpipe/ocr.py` and `arpipe/store.py` may differ
   from the T0.4 base, and only by the hunks admitted under A1–A4. Any fifth changed `arpipe/`
   path is unauthorized and fails the R1 suite.
2. The Track-A protected symbols and files stay byte-identical to the T0.4 base.
3. The governing behavioural requirement: T0.4-base triage and candidate triage must produce
   identical page kinds and identical OCR-page sets for every FIT and VALIDATION page.

Enforcement lives in `tests/test_t0_4_amendment_01.py` (49 tests) and `conftest.py`. The
original T0.4 guards are not edited.

## 6. T0.4 Amendment 01 reference

- Record: `docs/identity/T0_4_AMENDMENT_01.md`, committed as `e86d755acead1b4f5f1b744106a93c7585805d02`.
- Author: Hariom Singh. Date: 2026-09-26. Changes to the draft: none.
- SHA-256 of the ratified text: `2df5ff64dbbd2c2a6806468bb07cdcad6e33594fdfa6fc2ae579d68723d0eaca`.
- The record path does not match `docs/experiments/PHASE2.1_T0.4_AMENDMENT_*.md`, and no file
  matching that glob exists. **VERIFIED**
- D6 erratum: recorded in Annex B of the amendment. `docs/decisions/D6_Q6_AS_IS_IDENTITY_DECISION_v1.md`
  is unchanged from `755c5519b9ab9484ab033685e563350a0cd0d685`. **VERIFIED**

## 7. Track-B status

**UNRESOLVED / DEFERRED.**

No T0.4 document names a commit or tree for the Track-B "same frozen sequence"; the full trace
is Annex C of the amendment. No Track-B execution is authorized by this identity or by the
amendment. This is not an R1 gate.

## 8. Execution environment

This section certifies the environment **of this pinning run only**. It does not certify the
2026-09-17 runtime environment, which D6 section 9.4 leaves open.

- Python: `3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]`
- Interpreter: `D:\sem_iitk\sem9\thesis\sep_week1\arpipe-0.1.0\arpipe\.venv\Scripts\python.exe`
- OS: `Windows-11-10.0.26200-SP0`, `Microsoft Windows [Version 10.0.26200.9550]`, AMD64

Tesseract:

```text
@@TESS_VERSION@@
```

Available Tesseract language packs:

```text
@@TESS_LANGS@@
```

`pip freeze` (the virtual environment itself):

```text
@@FREEZE@@
```

## 9. jsonschema — TEST-ONLY

`jsonschema` is **a test-environment dependency only**. It is installed into a scratch
directory outside the repository and supplied through `PYTHONPATH` for test runs. It is not in
the virtual environment, not in `arpipe/requirements.txt`, and not imported by any `arpipe/`
module. `arpipe/requirements.txt` is unchanged from the T0.4 base. **VERIFIED**

Packages visible only via that scratch `PYTHONPATH` (`jsonschema` and its transitive
dependencies), i.e. the exact TEST-ONLY delta:

```text
@@TEST_ONLY@@
```

## 10. Import provenance

For every execution in this task, `arpipe` resolved inside the checkout under test. **VERIFIED**

| Run | Checkout | Resolved `arpipe.__file__` |
|---|---|---|
| Full suite | `D:\sem_iitk\sem9\thesis\sep_week1\r1-final-suite` (clean, detached at the tip) | `...\r1-final-suite\arpipe\__init__.py` |
| T0.4-base triage | scratch export of `ff030d97c13c8a2a977521bf91be2aca0cbf3034` | `...\scratchpad\base-t04\arpipe\__init__.py` |
| Candidate triage | scratch export of the tip | `...\scratchpad\cand-t04\arpipe\__init__.py` |
| Step-4 runs A and B | two separate scratch exports of the tip | `...\scratchpad\run-a\arpipe\__init__.py`, `...\scratchpad\run-b\arpipe\__init__.py` |

Each scratch export was verified file by file against its Git blobs before use (46 files for
the base, 59 for the candidate; 0 mismatches). The suite checkout sits directly under
`D:\sem_iitk\sem9\thesis\sep_week1\` so the T0.1 relative `live_store` path resolves.

## 11. Smoke result

`tests/test_import_smoke.py::test_every_arpipe_module_imports` — **1 passed**. Every
discoverable `arpipe.*` module imports from the pinned checkout. **VERIFIED**

## 12. Negative-test results

Run in scratch clones outside the candidate worktree; the candidate worktree was never
modified (its HEAD and clean status were re-checked after each mutation). All scratch clones
were discarded afterwards. **VERIFIED**

| # | Mutation | Expected | Observed |
|---|---|---|---|
| Control | none | all pass | 49 passed |
| Control (CRLF) | clone with `core.autocrlf=true` | all pass | 49 passed — the byte comparisons are checkout-config independent |
| (i) | exactly one byte of the protected `_classify` source flipped (`<` → `>` in `if n_chars < BLANK_CHARS ...`), verified as a single differing byte at the same file length | source-level identity test MUST fail | **FAILED as required**: `test_protected_source_is_byte_identical_to_the_t0_4_base[triage._classify]` and `test_authorized_file_differs_from_base_only_by_its_authorized_hunks[arpipe/triage.py]`; 2 failed, 47 passed |
| (ii-a) | one fifth `arpipe/` path modified and committed (`arpipe/verify.py`) | exact-set test MUST fail | **FAILED as required**: `unauthorized: ['arpipe/verify.py']` |
| (ii-b) | one fifth `arpipe/` path added, untracked (`arpipe/zz_fifth_path.py`) | exact-set test MUST fail | **FAILED as required**: `untracked files under arpipe/: ['arpipe/zz_fifth_path.py']` |
| (ii-c) | one fifth `arpipe/` path modified, uncommitted | exact-set test MUST fail | **FAILED as required**: `working tree changes outside A1-A4: ['arpipe/verify.py']` |
| (iii) | `arpipe/` restored to the T0.4 base, so the three guards pass | XPASS(strict) → suite failure | **3 failed**, each reported `[XPASS(strict)] T0.4 Amendment 01 ...` |
| (iv) | a fifth path changed as well, so the guards report a different violation | unrelated failure → FAIL, not XFAIL | **3 failed**, no XFAIL |

In addition, `test_strict_expected_failure_semantics` exercises the registration's decision
function over 12 cases (violation → XFAIL, pass → XPASS, fifth path → FAIL, missing path →
FAIL, wrong exception type → FAIL, different message → FAIL, unknown violation → FAIL).

## 13. Track-A base-vs-candidate behavioural result

**The governing evidence for T0.4 Amendment 01.** T0.4-base triage and candidate triage were
run in separate processes from separate clean exports, over every eligible FIT and VALIDATION
document. Triage profiling only: no pipeline, no OCR. **VERIFIED**

Universe, derived from the frozen split manifests (never hard-coded):

| Item | Value |
|---|---|
| Source | `dataset/corpus_freeze/development_manifest.csv` (`split = FIT`), `dataset/corpus_freeze/validation_manifest.csv` (`split = VALIDATION`) |
| Manifest rows | FIT 60, VALIDATION 48, HOLDOUT 54 |
| Disjointness | FIT∩VALIDATION, FIT∩HOLDOUT, VALIDATION∩HOLDOUT are empty on document_id, company_id and issuer name |
| Eligible and run | FIT 60/60, VALIDATION 48/48 — none excluded |
| PDF location | content-addressed `live_store/blobs/<aa>/<bb>/<sha>.pdf` keyed by the frozen manifest `pdf_sha256`, content hash re-verified before opening |

Results:

| Measure | Value |
|---|---|
| FIT documents | @@FIT_DOCS@@ |
| FIT pages | @@FIT_PAGES@@ |
| VALIDATION documents | @@VAL_DOCS@@ |
| VALIDATION pages | @@VAL_PAGES@@ |
| Total documents | @@TOT_DOCS@@ |
| Total pages | @@TOT_PAGES@@ |
| Exact PageKind matches | **@@KIND_MATCH@@** |
| PageKind mismatches | **@@KIND_MISMATCH@@** |
| Exact OCR-set matches (per page) | **@@OCR_MATCH@@** |
| OCR-set mismatches (per page) | **@@OCR_MISMATCH@@** |
| Exact OCR-set matches (per document) | **@@OCR_DOC_MATCH@@** of @@TOT_DOCS@@ |
| OCR-set mismatches (per document) | **@@OCR_DOC_MISMATCH@@** |
| Document errors | 0 |
| Page-count disagreements | 0 |

There is **no mismatch to report**: every mismatch list is empty. Supplementary, beyond what
the amendment requires: all @@SUPP_IDENT@@ pages are identical on *every* serialised
`PageProfile` field except `script_meta` (which A2 adds by design) — `n_chars`, `word_count`,
`image_area_frac`, `text_area_frac`, `n_images`, `n_columns`, `orientation`, page geometry,
`script`, `mojibake_ratio`, `dpi_estimate` and `rotation`. The 14 triage thresholds after
`configure` and the `NEEDS_OCR` set (`broken_text`, `hybrid`, `scanned`, `vector_text`) are
equal in both runs.

Candidate page-kind totals over the @@TOT_PAGES@@ pages: @@KINDS@@. Pages routed to OCR:
@@OCR_ROUTED_TOTAL@@ (FIT @@OCR_ROUTED_FIT@@, VALIDATION @@OCR_ROUTED_VAL@@).

## 14. Secondary `page_profile.csv` comparison

A **secondary diagnostic**, not the governing criterion: the provenance of the code that
originally produced `dataset/corpus_freeze/page_profile.csv` was not established by the
forensic audit.

| Run vs `page_profile.csv` | Exact matches | Mismatches |
|---|---|---|
| Candidate | **@@PP_CAND_MATCH@@** (FIT @@PP_FIT@@, VALIDATION @@PP_VAL@@) | **@@PP_CAND_MISMATCH@@** |
| T0.4 base | **@@PP_BASE_MATCH@@** | **@@PP_BASE_MISMATCH@@** |

All @@PP_CAND_MATCH@@ rows for FIT and VALIDATION documents agree, with no page lacking a
profile row and no profile row lacking a page, and every document's `page_count` matching.
`physical_page` is 0-based in this file and aligns with `PageProfile.page_no` directly. Only
rows whose `document_id` is a FIT or VALIDATION document were read; all other rows were skipped
on their `document_id` without inspection. **VERIFIED**

No candidate-vs-`page_profile` mismatch exists, so no provenance investigation was triggered.

## 15. Historical 57/58 comparison

57 of 58 FIT documents match the 2026-09-17 outputs on all available comparable fields; per-page
kinds were not serialized historically; one document differs (INE00LO01017_2025) — attribution:
UNATTRIBUTED.

Field-level counts from the preserved comparison
(`sep_week1/r1-final-evidence/historical-comparison.json`, SHA-256 `@@H_HIST@@`): `located`
58 exact; `start_page` 57 exact, 1 different; `end_page` 58 exact; `grade` 57 exact, 1
different; `span_path_nullness` 58 exact; `script_map` 58 exact; `per_page_kind`
`UNAVAILABLE_BOTH` for all 58, because the historical outputs never serialised per-page kinds.
Fully comparable documents: 0, precisely because of that missing field. **VERIFIED**

That comparison was produced by the earlier session from a checkout whose `arpipe/` and
`configs/` trees are the byte-identical tree objects this identity pins
(`@@ARPIPE_TREE@@`, `@@CONFIGS_TREE@@`), so it describes this code. **VERIFIED**

## 16. Step-4 drift attribution

Attribution: **UNATTRIBUTED**. Detail in section 17.

## 17. Step-4 investigation — INE00LO01017_2025

**FIT status, verified first.** `INE00LO01017_2025` is row `INE00LO01017` / FY2025 of
`dataset/corpus_freeze/development_manifest.csv` with `split = FIT`, and is absent from the
VALIDATION manifest. Verified before any of its files were opened. **VERIFIED**

**Determinism — three runs agree.** Run #1 is the earlier session's recorded output; runs A and
B were executed in this task from two separate clean exports of the tip. All three produce
byte-identical `result.json`: `start_page` 16, `end_page` 29, grade `high`, method
`heading+trimmed`, score 0.99, supporters 2, `ocr_pages` 0, `ocr_engine` null, `n_words` 5772,
candidates `[["heading", 16, 29, 0.92], ["heading_text", 16, 29, 0.63], ["body_score", 15, 20, 0.72]]`.
Distinct outcome tuples across the three runs: **1**. **VERIFIED**

Both preserved 2026-09-17 runs (`pm1_baseline_run` and `pm1_after_run`) agree with each other:
`start_page` 15, grade `medium`, method `body_score+refined+trimmed`, score 0.72, supporters 0,
candidates `[["body_score", 15, 20, 0.72]]`. So the historical value does not depend on which
run is used. **VERIFIED**

**A. Which pages in the MD&A span window were OCR-routed?** **None.** The document profiles as
243 pages, 242 `digital` and 1 `scanned`; the whole-document OCR-page set is `[1]` in both the
base and the candidate triage. Every page of the span window (0-based 15–29 historically, 16–29
in the candidate) is `digital` with 1 851–5 016 characters, and no page in the window is routed
to OCR. Both runs independently report `ocr_pages = 0` and `ocr_engine = null`, historically and
now. **VERIFIED**

**B. Does `pm1_baseline.json` or any permitted 2026-09-17 manifest record the Tesseract
version?** **No.** `reports/pm1_baseline.json` has no version key at all; its only engine-related
content is `extraction_config.escalator = ["tesseract"]`. The `manifest.jsonl` schemas of both
preserved runs (23 keys each) contain `ocr_engine`, `ocr_pages` and `pipeline_version` but no
Tesseract, leptonica or engine-version field; `manifest.parquet` has the same columns. The
document's own `document.json`, `mda.json` and `mda_blocks.json` carry no version-like field.
Neither run log contains any line mentioning tesseract, leptonica or tessdata. **VERIFIED
(absence)**

**C. Compare the historical version against Tesseract 5.4.0.20240606.** **Not possible.** No
historical Tesseract version is recorded anywhere permitted, so there is nothing to compare
against the version installed now (`tesseract v5.4.0.20240606`, leptonica-1.84.1, langs eng /
hin / osd). **NOT VERIFIABLE**

**Classification: UNATTRIBUTED.**

- Not `NONDETERMINISM`: three candidate runs from separate clean exports agree byte for byte,
  and the two historical runs agree with each other. **DERIVED**
- Not `OCR_ENGINE_DRIFT`: no page in the span window was OCR-routed, in either era, and both
  eras report `ocr_pages = 0` / `ocr_engine = null`. OCR did not touch the evidence this span
  was computed from. **DERIVED**
- Not established as `PATTERNS_DRIFT`: the difference is that the candidate finds a `heading`
  candidate (page 16, 0.92) and a `heading_text` candidate (page 16, 0.63) that the historical
  run did not, while both find the identical `body_score` candidate (pages 15–20, 0.72); with
  two supporters and score 0.99 the candidate grades `high`, where the historical solo
  `body_score` span graded `medium`. `arpipe/patterns.py` is one plausible source — it was
  dirty in the 2026-09-17 porcelain and its executed bytes are unrecoverable — but so are
  `segment.py`, `textlayer.py` and `verify.py`, all of which are listed modified in the same
  porcelain and all of which feed heading detection. The evidence does not isolate one.
  Asserting `patterns.py` on the correlation alone would be inference presented as fact.
  **INFERRED, therefore not adopted**
- One further verified fact narrows nothing further: the historical `run_config` for this
  document is identical to the candidate's effective configuration except that the historical
  record carries eight extra `verify:` keys (`devanagari_frac_min`, `digit_embedded_frac_min`,
  `english_word_frac_max`, `high_codepoint_freq_min`, `long_word_frac_min`,
  `rare_punct_freq_min`, `wrong_language_min_tokens`, `wrong_language_window`) whose values
  equal the `verify.py` module defaults. Configuration drift is therefore not the cause.
  **VERIFIED / DERIVED**

Attribution therefore stays **UNATTRIBUTED**, and section 15's required sentence preserves that
result. No code was changed, and the historical comparison was not modified.

## 18. Full test-suite result

Clean checkout `D:\sem_iitk\sem9\thesis\sep_week1\r1-final-suite`, detached at the tip, working
tree clean. Command: `python -m pytest -q`. Process exit code **0**. **VERIFIED**

| Measure | Count |
|---|---|
| Total tests | 431 |
| Passed | 411 |
| Failed | 0 |
| xfailed | 3 |
| xpassed | 0 |
| Skipped | 17 |
| Errors | 0 |

The three xfailed are exactly the registered original T0.4 guards, as strict expected failures:

- `tests/t0_4/test_t0_4_setup.py::test_frozen_corpus_and_history_are_unchanged`
- `tests/t0_4/test_t0_4_setup.py::test_fail_closed_setup_audit_passes`
- `tests/t0_4/test_t0_4_closure_record.py::test_frozen_inputs_are_unchanged_since_the_audited_commit`

Every other T0.4 test passes (93 of them), the new enforcement tests pass (49), the A5
immutability test `test_historical_immutability_strict_allowlist` passes, the import smoke test
passes, and the T0.1 tests pass.

The 17 skips are pre-existing environment skips, unrelated to this task: 13 + 2 need synthetic
fixtures (`run tests/make_fixtures.py first`), 1 needs sampling stores, 1 needs `live_store`
blobs. To confirm they hide nothing, the fixtures were built in a scratch copy and the
fixture-dependent tests were run there: **103 passed, 1 skipped** (the remaining skip needs
`live_store` blobs inside that scratch copy). No fixture was added to the repository.

## 19. Frozen-path result

Recomputed independently from `tools/t0_4/core.py` and the closure record, not read from test
output. **VERIFIED**

| Check | Result |
|---|---|
| `PROTECTED_PATHS` (13 entries) vs T0.4 base | exactly `arpipe/models.py`, `arpipe/ocr.py`, `arpipe/store.py`, `arpipe/triage.py` |
| `FROZEN_SINCE_AUDIT` (7 entries) vs `33ba76acf9da13d25027e39414e724dfa1170b59` | the same four paths |
| `arpipe/` vs T0.4 base at the tip | the same four paths — no fifth path |
| `tools/t0_4`, `tests/t0_4`, `configs/t0_4`, `artifacts/t0_4`, `tools/audit_t0_4_*.py`, `tools/build_t0_4_manifest.py`, the three T0.4 docs, vs the forensic commit | **empty** — the original guards and frozen T0.4 material are untouched |
| `dataset/`, `configs/t0_1r`, `configs/t0_3a`, `configs/t0_3a_r1` vs T0.4 base | **empty** |
| `git diff --check`, `git diff --cached --check` | clean, exit 0 |
| `git status --porcelain -uall` | empty |

The frozen-path diff is empty except for the explicitly ratified A1–A4 reconstruction, and no
unauthorized `arpipe/` path changed.

## 20. Document-hash result

`python tools/check_doc_hashes.py` — **10 hash claims across 1 doc, 0 unallowed failures**,
exit code 0. **VERIFIED**

## 21. Identity scope

This identity is:

> a runnable reconstruction of the As-Is provider half on the Phase-4 consumers.

It is **not** byte-identical to the complete 2026-09-17 tree.

It is **not** a C2 baseline decision.

**C2 remains CONDITIONAL.** No baseline-relative improvement claim may be made from this
identity. The C2 gate opens only when further evidence bounds the 2026-09-17 → 2026-09-20
provider drift, per D6 section 10.

The identity must not be described as "equivalent" to, or as having "identical behaviour" to,
the 2026-09-17 system. What is established is stated exactly in sections 13, 14 and 15.

## 22. Evidence files

Retained outside the repository, under this session's scratchpad. Listed with SHA-256 so the
numbers above can be traced.

| File | SHA-256 |
|---|---|
| `universe.json` (the derived FIT + VALIDATION universe) | `@@H_UNIVERSE@@` |
| `profile_base.json` (T0.4-base triage, all pages) | `@@H_PROFILE_BASE@@` |
| `profile_cand.json` (candidate triage, all pages) | `@@H_PROFILE_CAND@@` |
| `comparison.json` (governing + secondary comparison) | `@@H_COMPARISON@@` |
| `evidence_compact.json` (per-document page-kind and OCR-set digests) | `@@H_COMPACT@@` |
| `suite_pin.txt`, `suite_pin.xml` (full-suite output and JUnit XML) | `@@H_SUITE_TXT@@`, `@@H_SUITE_XML@@` |
| `negative_tests.out` (Step 2E transcript) | `@@H_NEG@@` |
| `historical-comparison.json` (preserved from the earlier session) | `@@H_HIST@@` |

## 23. Out-of-scope findings — recorded, not resolved

Track-B frozen-sequence semantics; legacy-font research; OCR benchmark execution; Gold
annotation; the Oracle roster; B1–B8 decisions; C1 metric-contract issues; missing-PDF
acquisition; HOLDOUT methodology; the C2 decision.

No HOLDOUT PDF, output, annotation or document directory was inspected, and no HOLDOUT manifest
row was followed. The HOLDOUT manifest was read only for its `document_id`, `company_id` and
`issuer` columns, to prove split disjointness.
