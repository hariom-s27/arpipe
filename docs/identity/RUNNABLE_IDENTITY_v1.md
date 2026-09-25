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
| Tip SHA | `28a67b63d890d8407fa9738a71ae37ad63148b73` |
| Parent SHA | `e86d755acead1b4f5f1b744106a93c7585805d02` |
| Subject | `test(r1): enforce T0.4 Amendment 01 and register strict expected failures` |
| Branch | `r1-final` |
| Start of this task | `1db8ccddf282ec86a6785df80b04a73d680a60f9` (`docs(r1): record T0.4 guard forensics`) |
| `arpipe/` tree at the tip | `f6475922f2a6837c7e6a86cefb5fb30aef602e69` |
| `configs/` tree at the tip | `4b56d25b28c18132cb1fcf4f847e4582a195036a` |

The identity is pinned at the tip above. Section 7's later records commit adds documentation
only and changes no file in the identity universe; the universe digest in section 3 is the
value to re-check.

## 2. Identity file universe

Obtained with `git ls-files arpipe/ configs/` at the tip. **VERIFIED**

- Total files: **59**
- Combined manifest digest: `de250c36a660d94a2e28b49b82860f77e130b04a6fdcfc3ebf444043f57ef203`
- Recipe: SHA-256 over UTF-8 lines `<file sha256>  <path>\n`, one per file, in bytewise path
  order. Recomputing this digest from section 3's table reproduces the value. **DERIVED**
- Every file's working-tree bytes hash equal to its Git blob at the tip (0 mismatches over
  59 files). **VERIFIED**
- The universe matches the previously observed 59-file universe exactly: same 59 paths, same
  59 SHA-256 values, same combined digest. Nothing was added, removed or changed. **VERIFIED**
- Untracked material (`__pycache__`, `*.pyc`, scratch files, built fixtures) is excluded: the
  universe is exactly the Git-tracked set.

## 3. Per-file SHA-256

| # | Path | SHA-256 |
|---|---|---|
| 1 | `arpipe/CLAUDE.md` | `0af8dbf9cc78fa702135b3cbf987f695009632f65eb61e283822f0e8bdac8a94` |
| 2 | `arpipe/README.md` | `964ac96fa02a6031d1440bfc4e97d759113485a94b6707cf8ff62471d23c3712` |
| 3 | `arpipe/__init__.py` | `3942d5b3558f3e75c9eeca9222b4384bcca5503c9c825fcff70fc99dc10c1d82` |
| 4 | `arpipe/cli.py` | `69c9d4519b7f3ba42c316f5395a9a2e21eb77053718458376ff32e6b7cbb48bb` |
| 5 | `arpipe/companies.csv` | `cc1c2e0666d5777ee3f07bb6abb20ae44ba3e4bfd991dc90325539032ca86341` |
| 6 | `arpipe/config.py` | `93aba31b53d4173bde3ad322bd5625416eca29e86b89887461f5bc2c7d760c7c` |
| 7 | `arpipe/configs/default.yaml` | `1ab406c607eac5c9799d5b5ac89b8c42f56bde8659f9f6214de5063d5bd3cb85` |
| 8 | `arpipe/configs/eval_protocol.md` | `b45ca6ac379c5053d9f4268d6ed40a9f246a28557fc771edad6385a9bef73cbd` |
| 9 | `arpipe/discover.py` | `bdfbe34ff572fc263e3cbd75dcd9081062619314d893f1d495989a3e9a66bca8` |
| 10 | `arpipe/eval_report.md` | `05a26ebd1eda21ce6594f32e90365f84882e2ccf59186e278c27b4a8e302b1ea` |
| 11 | `arpipe/evaluate.py` | `6e1c1b9ba6ef1e1c103d0882515f1c81fccceffd16bee5a18a8776b51457d057` |
| 12 | `arpipe/fetch.py` | `37e298b47ab4ddb30b4c27f39c49fa092a872c7394a8588f4cdc9e6afd33fa76` |
| 13 | `arpipe/labeller.py` | `cd11a9752fad97049264b4d938bc99bc0dfbf63e92f6b7404d4e2ec5caff2eec` |
| 14 | `arpipe/models.py` | `e40faa0b467c74bdc405f5d7de898633b07a3f2b5da425e8f3c1b05c6c2b2217` |
| 15 | `arpipe/ocr.py` | `c94b5d8d4b7fb6d2be4e9b605e9088d7f289ab903c10f6f1fbef611b20c15e4a` |
| 16 | `arpipe/patterns.py` | `0166ed14baa4ed46fc55e8726c3449be29eda200ed6ade06846e8b7a14e507b5` |
| 17 | `arpipe/pilot_reports.jsonl` | `c773a391af94716ba0dd7d573963c2e8a33026012d2d9941c4768a006cdae619` |
| 18 | `arpipe/pipeline.py` | `66ecf6cfa0d8a7ea46c928fbf646fbb06c4f5687a33e46555438e976bf76060d` |
| 19 | `arpipe/preflight.py` | `5dc81b5223453abe2acfe3c0511decd0f36c40fee786ef112d60d9f19e482e49` |
| 20 | `arpipe/reports_sample.jsonl` | `6c1cc994edfd749a6fdc8cda11ddf38f9389f9641e0bfc5ae36ff3ce007e5c2a` |
| 21 | `arpipe/requirements.txt` | `c2db8f0845394eebc6564f1191253e67c3bf6257cb6180a21debf47614ebe608` |
| 22 | `arpipe/segment.py` | `e90c67b7d334fe896029a2960dc49b1782f1a1b9f692f0be9feec73890de96ba` |
| 23 | `arpipe/store.py` | `1fd9cccb9d0fd80d7d0a95835cf4c7ba5207e58439464543e8c71540bc6a02d5` |
| 24 | `arpipe/tests/make_fixtures.py` | `ca233ddfd8c5c1682c094e38f533045efe06e7081233df649a344c2c31081063` |
| 25 | `arpipe/tests/test_column_cut.py` | `448d434253f263de5ce8f014c4807ac5b18940519e1a24a2ebb2ddeca2fc0e17` |
| 26 | `arpipe/tests/test_config.py` | `6858ed9f5bdff687aed81216e8576a8181c0fb7ab09209673810a905b50b1a1e` |
| 27 | `arpipe/tests/test_discover.py` | `8835977dcc0c283911e9e74c57acd8fc850c0440829c58d3bb1fdef24562bb8a` |
| 28 | `arpipe/tests/test_evaluate.py` | `bab55988b3462ecd84767d52e702804ee0d9f7be86798670460f924760143353` |
| 29 | `arpipe/tests/test_labeller.py` | `ebd7ad63c86668ebb3b9a540d753b68b8fd461cdd54094111b4d4d8d80bc88b1` |
| 30 | `arpipe/tests/test_pipeline.py` | `85e558d95d96274efa82c28f1a624a76f01ec5ac40a26d0a056602d5ca395f06` |
| 31 | `arpipe/tests/test_pm1_orderqc.py` | `5d5ba30ef365dc32bf23878fcfd8c895f4d7c1756fffb694461af8a0e3e23020` |
| 32 | `arpipe/tests/test_pm2_pagegrain_native_vs_ocr.py` | `aa54ab7044130be8dd512438dce11214ed838f0aa7f6306fae43d762827cc1c5` |
| 33 | `arpipe/tests/test_preflight.py` | `dd3c97a85d0a6431b5aa3a93facd1a89759d6aa0c259e482dd074ed8b22578ba` |
| 34 | `arpipe/textlayer.py` | `ee5e60fcee63e3e6534ab9182e81b42a5f9140094b976732d7071653d80e798a` |
| 35 | `arpipe/to_label.csv` | `5b65e1edd5718890d1fed79ee4bb2beaf203649586a782f542d41350c7e05e08` |
| 36 | `arpipe/triage.py` | `351a4aac1efcee4899999b7c76899856a963d1687442fea4a75dcab9cc754892` |
| 37 | `arpipe/universe.py` | `c2e5463515b1179d052c6fb46e1cc6454a9e3a498beb29cf80e2c7799004e69d` |
| 38 | `arpipe/verify.py` | `29dd0a415d58874a53e01d52c8b802ad2f9fb550eb2c2a50efa9525f780f4b63` |
| 39 | `configs/audit_config.json` | `a3a575cda1ec7345f3a9ba5544da67401ab01a3c6041a22719b032cbeaefdd7e` |
| 40 | `configs/audit_config.sha256` | `912f60587ba2bc3de15ccd9048b10d3e43e6fd24b186d2a2cf4f7028cdcf6221` |
| 41 | `configs/eval_protocol.md` | `b45ca6ac379c5053d9f4268d6ed40a9f246a28557fc771edad6385a9bef73cbd` |
| 42 | `configs/phase2_1/semantic_fixtures.json` | `da647fba4b9a99059c7cfae5f2bbc1e07617f8e23385ef5e814e2a0d5dd646d2` |
| 43 | `configs/t0_1r/input_allowlist.json` | `65a10ae8c30237e8a3e9debedd6eae13328965e1cef0584c0a2506687889caf0` |
| 44 | `configs/t0_1r/reconciliation_rules.json` | `9dbbec3e8d5565a3d29114e1bcb46b613c187a8017832b00f2ff9d984ae4cdd9` |
| 45 | `configs/t0_1r/reviewer_expectations.json` | `c1286cde18df7efb3e68b78c9bcaf41a6888d5718d1136bbbe2944e124b03b26` |
| 46 | `configs/t0_3a/taxonomy_register.json` | `0fbe3030eb03c4d4f4dafb338713f592f84f753936aca6c60f4a3fbeed7c6efb` |
| 47 | `configs/t0_3a_r1/taxonomy_register.json` | `1be25b1f5f7b52249122cd7e29a8ed1f105f35ef8fff5d607dcf45c24df7de10` |
| 48 | `configs/t0_4/benchmark_config.json` | `79727cddfb28e13544edeef4e35ea43897f4e521cf8ca62e2c447e1a90c0c6af` |
| 49 | `configs/t0_4/benchmark_manifest_schema.json` | `3748fa145a3bb0667cc68dd1c3ac1c910cd3c5ea9b0b8d572c6460ea5bb05ac5` |
| 50 | `configs/t0_4/common_output_schema.json` | `7648ea43aa0e06a5bab8d35ac19385cce2607d2ea09772e27bcaf50c81b871af` |
| 51 | `configs/t0_4/efficiency_schema.json` | `089bf6de4d6de0ec64c49f19498e626bb8c5eaa579dfdbe2ea68bdc9a6a5ef42` |
| 52 | `configs/t0_4/engine_registry.json` | `74575cac2e96c71e01b006f258310362fbce1a05e5c899a0007542e7ccb4ed5e` |
| 53 | `configs/t0_4/failure_taxonomy.json` | `78fb43f16e8d679b868b2b6600c3ad213ae1df5e5f4c0b7c8b8a37319ebcbc25` |
| 54 | `configs/t0_4/future_results_schema.json` | `538c498ff8c6ceda2f85cb92acf0e5bfe7a948cd6174db1729af1f6d599a5e66` |
| 55 | `configs/t0_4/gold_schema.json` | `e8b33a4a0e04da72c3572604ca3f82677920617607abe266717975ee3cc65247` |
| 56 | `configs/t0_4/metrics_spec.json` | `d7590bebe271163f2ad341cace35f4749754cf22da3018cef32b12ad09c66336` |
| 57 | `configs/t0_4/oracle_routing_spec.json` | `d5aa91eb161cc04eb06fd20edc5941e88e9dcdcc70c71d17e2c259d3a625fbc3` |
| 58 | `configs/t0_4/raw_output_schema.json` | `bdbc512abe729c8401462223b2b540d997838ab897f369360cb3956b1939a781` |
| 59 | `configs/t0_4/sampling_spec.json` | `412e040e9bcdc3915110906cd66d38a025e3aaad3f1f12bf31bf32327e17375c` |

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
tesseract v5.4.0.20240606
 leptonica-1.84.1
  libgif 5.2.1 : libjpeg 8d (libjpeg-turbo 3.0.1) : libpng 1.6.43 : libtiff 4.6.0 : zlib 1.3 : libwebp 1.4.0 : libopenjp2 2.5.2
 Found AVX2
 Found AVX
 Found FMA
 Found SSE4.1
 Found libarchive 3.7.4 zlib/1.3.1 liblzma/5.6.1 bz2lib/1.0.8 liblz4/1.9.4 libzstd/1.5.6
```

Available Tesseract language packs:

```text
List of available languages in "C:\Program Files\Tesseract-OCR/tessdata/" (3):
eng
hin
osd
```

`pip freeze` (the virtual environment itself):

```text
annotated-types==0.8.0
anyio==4.15.1
certifi==2026.7.22
cffi==2.1.1
charset-normalizer==3.5.1
colorama==0.4.6
cryptography==50.0.1
defusedxml==0.7.1
fonttools==4.64.0
fpdf2==2.8.8
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
idna==3.19
img2pdf==0.6.3
iniconfig==2.3.0
lxml==6.1.3
markdown-it-py==4.2.0
mdurl==0.1.2
numpy==2.5.3
ocrmypdf==17.11.0
packaging==26.3
pandas==3.0.5
pdfminer.six==20260107
pdfplumber==0.11.10
pi_heif==1.4.0
pikepdf==10.13.0.post1
pillow==12.3.0
pluggy==1.6.0
pyarrow==25.0.1
pycparser==3.0
pydantic==2.13.5
pydantic_core==2.46.5
Pygments==2.21.0
pymupdf==1.28.2
pypdf==6.18.0
pypdfium2==5.13.0
pytesseract==0.3.13
pytest==9.1.1
python-dateutil==2.9.0.post0
PyYAML==6.0.3
RapidFuzz==3.14.6
rich==15.0.0
six==1.17.0
tenacity==9.1.4
typing-inspection==0.4.4
typing_extensions==4.16.0
tzdata==2026.3
uharfbuzz==0.56.1
```

## 9. jsonschema — TEST-ONLY

`jsonschema` is **a test-environment dependency only**. It is installed into a scratch
directory outside the repository and supplied through `PYTHONPATH` for test runs. It is not in
the virtual environment, not in `arpipe/requirements.txt`, and not imported by any `arpipe/`
module. `arpipe/requirements.txt` is unchanged from the T0.4 base. **VERIFIED**

Packages visible only via that scratch `PYTHONPATH` (`jsonschema` and its transitive
dependencies), i.e. the exact TEST-ONLY delta:

```text
attrs==26.1.0
jsonschema-specifications==2025.9.1
jsonschema==4.26.0
referencing==0.37.0
rpds-py==2026.6.3
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
| FIT documents | 60 |
| FIT pages | 12652 |
| VALIDATION documents | 48 |
| VALIDATION pages | 8298 |
| Total documents | 108 |
| Total pages | 20950 |
| Exact PageKind matches | **20950** |
| PageKind mismatches | **0** |
| Exact OCR-set matches (per page) | **20950** |
| OCR-set mismatches (per page) | **0** |
| Exact OCR-set matches (per document) | **108** of 108 |
| OCR-set mismatches (per document) | **0** |
| Document errors | 0 |
| Page-count disagreements | 0 |

There is **no mismatch to report**: every mismatch list is empty. Supplementary, beyond what
the amendment requires: all 20950 pages are identical on *every* serialised
`PageProfile` field except `script_meta` (which A2 adds by design) — `n_chars`, `word_count`,
`image_area_frac`, `text_area_frac`, `n_images`, `n_columns`, `orientation`, page geometry,
`script`, `mojibake_ratio`, `dpi_estimate` and `rotation`. The 14 triage thresholds after
`configure` and the `NEEDS_OCR` set (`broken_text`, `hybrid`, `scanned`, `vector_text`) are
equal in both runs.

Candidate page-kind totals over the 20950 pages: digital 19472, broken_text 708, scanned 392, hybrid 229, blank 133, vector_text 16. Pages routed to OCR:
1345 (FIT 927, VALIDATION 418).

## 14. Secondary `page_profile.csv` comparison

A **secondary diagnostic**, not the governing criterion: the provenance of the code that
originally produced `dataset/corpus_freeze/page_profile.csv` was not established by the
forensic audit.

| Run vs `page_profile.csv` | Exact matches | Mismatches |
|---|---|---|
| Candidate | **20950** (FIT 12652, VALIDATION 8298) | **0** |
| T0.4 base | **20950** | **0** |

All 20950 rows for FIT and VALIDATION documents agree, with no page lacking a
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
(`sep_week1/r1-final-evidence/historical-comparison.json`, SHA-256 `e9fc54826b42694f31c62b29a5850ce2f2a6605ba5a79797066373132a5f5329`): `located`
58 exact; `start_page` 57 exact, 1 different; `end_page` 58 exact; `grade` 57 exact, 1
different; `span_path_nullness` 58 exact; `script_map` 58 exact; `per_page_kind`
`UNAVAILABLE_BOTH` for all 58, because the historical outputs never serialised per-page kinds.
Fully comparable documents: 0, precisely because of that missing field. **VERIFIED**

That comparison was produced by the earlier session from a checkout whose `arpipe/` and
`configs/` trees are the byte-identical tree objects this identity pins
(`f6475922f2a6837c7e6a86cefb5fb30aef602e69`, `4b56d25b28c18132cb1fcf4f847e4582a195036a`), so it describes this code. **VERIFIED**

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
| `universe.json` (the derived FIT + VALIDATION universe) | `a1eb84a0006a8bf931f512cc980602e55c9fb62a2f0a0a2766e94cb07152725a` |
| `profile_base.json` (T0.4-base triage, all pages) | `317657f9632f9e617c5e5a144c0db393f1610920072990eca168ca5a76e45be6` |
| `profile_cand.json` (candidate triage, all pages) | `7d350ff0aad1165678668f91aa440bec308f1551f40f5658fa7bf9bc87121363` |
| `comparison.json` (governing + secondary comparison) | `1cae94f9c7a792a12d166b14b8f7fea5f406e67e41b9898edb29af8a0a016e14` |
| `evidence_compact.json` (per-document page-kind and OCR-set digests) | `767e421257f5703d7790e39d2cf02f784c6506a4b0b54588c9ebfbb179ffc2c5` |
| `suite_pin.txt`, `suite_pin.xml` (full-suite output and JUnit XML) | `1861f8fcb03e869d90ed70c6e141740e9507fa21a105cc90cd0a0a19aee68110`, `8e7475f6b336f0fd73472002b62af6d591b4aedfbc3df7cae12f2eeaffd97a06` |
| `negative_tests.out` (Step 2E transcript) | `287aa8a1c114aa5074ecccc720ff2f0bb764319ca571fdb029e02abfc6961ada` |
| `historical-comparison.json` (preserved from the earlier session) | `e9fc54826b42694f31c62b29a5850ce2f2a6605ba5a79797066373132a5f5329` |

## 23. Out-of-scope findings — recorded, not resolved

Track-B frozen-sequence semantics; legacy-font research; OCR benchmark execution; Gold
annotation; the Oracle roster; B1–B8 decisions; C1 metric-contract issues; missing-PDF
acquisition; HOLDOUT methodology; the C2 decision.

No HOLDOUT PDF, output, annotation or document directory was inspected, and no HOLDOUT manifest
row was followed. The HOLDOUT manifest was read only for its `document_id`, `company_id` and
`issuer` columns, to prove split disjointness.
