> **ERRATUM — quarantine reachability. Recorded 2026-09-26 by R1-FINAL v3, under T0.4
> Amendment 01.**
>
> The earlier statement that quarantine was unreachable was incorrect. `pipeline.py:325`
> directly assigns `grade = "quarantine"`, and the 2026-09-17 outputs demonstrate that this
> path executed. It affects the "Reachability note" below and the parenthesis in the
> "Option B - minimal repair" section, which argued that `Confidence.QUARANTINE` and
> `write_span` could be restored inertly because the branch could not be reached. Both
> preserved 2026-09-17 runs contain two `quarantine` rows (INE008A01015 FY2024 and FY2025,
> reasons including `WRONG_LANGUAGE_RISK`) with `path = null`, which is the
> `store.write_year(write_span=False)` behaviour. The reasoning that reached quarantine only
> through `verify.grade()` missed the direct assignment in `pipeline.py`.
>
> This erratum is established from the existing provenance record
> (`docs/identity/R1_RESUME_GATE_BLOCKER.md`, evidence E2 and the `Confidence.QUARANTINE`
> row of its symbol table, which cites `pipeline.py:385` with the grade set at
> `pipeline.py:325`). `arpipe/pipeline.py` was not inspected or modified to establish it.
>
> Everything below this box is the original report, preserved unchanged.

# R1 — Runnable Identity: HALTED (R1_IDENTITY_BLOCKER)

**Task:** R1 IMPLEMENT — Establish Provenance-Supported Runnable Identity
**Date:** 2026-09-24
**Verdict:** **STOPPED at the §6 Implementation Decision Gate — neither Option A nor Option B is justified by repository evidence.**
**Commits made:** none. Worktree left clean except this report (uncommitted).

---

## 1. Purpose

Establish a provenance-supported, clean-checkout-runnable identity for ARPipe.
This report records why that identity **cannot** be established without an author
decision that R1 explicitly forbids this task from making.

## 2. Repository identity

| Item | Value |
|---|---|
| Repository | `hariom-s27/arpipe` (`https://github.com/hariom-s27/arpipe.git`) |
| Main checkout | `D:/sem_iitk/sem9/thesis/sep_week1/arpipe-0.1.0` |
| Worktree created | `D:/sem_iitk/sem9/thesis/sep_week1/runnable-identity` |
| Branch | `runnable-identity` |
| Phase 4 base SHA (START_SHA) | `50769ffc6b5ec75919ddbab523db49cc1d80c223` |
| Phase 4 commit subject | `docs(phase4): B1-B8 triage and author decision sheet` |
| Phase 4 commit date | 2026-09-23 19:38:44 +0530 |
| FINAL_SHA | *(none — no commit created)* |
| Worktree state at START | clean |

**Phase 4 identification evidence.** `50769ff` is the tip of branch `phase4-b1-b8`
and of `origin/phase4-b1-b8`; it is the last of the two Phase-4 commits
(`aba233b` then `50769ff`); both are docs-only. It is an ancestor of `origin/main`
via merge `b34922e` ("Merge pull request #21 from hariom-s27/phase4-b1-b8").
Only the unrelated `lf-fixture-suite` merge follows it on `main`. Identification
is unambiguous.

## 3. Environment

| Item | Value |
|---|---|
| OS | Windows 11 Home Single Language 10.0.26200 |
| Python | 3.14.3 |
| Interpreter | `arpipe-0.1.0/arpipe/.venv/Scripts/python.exe` (venv is untracked; not reproducible from Git) |
| Dependency convention | `arpipe/requirements.txt` (lower bounds only; **not a lock file**) |

Installed (relevant): pymupdf 1.28.2, pdfplumber 0.11.10, pypdf 6.18.0,
httpx 0.28.1, rapidfuzz 3.14.6, tenacity 9.1.4, pandas 3.0.5, pyarrow 25.0.1,
PyYAML 6.0.3, pytest 9.1.1, pytesseract 0.3.13, ocrmypdf 17.11.0,
pillow 12.3.0, numpy 2.5.3. **`jsonschema` is NOT installed and NOT listed in
`requirements.txt`, yet `tests/t0_4/test_t0_4_setup.py` imports it** (see §9).

Git tree hashes at START: `arpipe/` = `1d63ab4989173b199dcd181f47f2a566929d9bef`,
`configs/` = `4b56d25b28c18132cb1fcf4f847e4582a195036a`.

---

## 4. Original reproducibility failure

The package **imports** and the **CLI starts** cleanly at START. The failure is
runtime-only, inside `arpipe.pipeline.process_document`.

Exact first error, reproduced on all three FIT smoke documents:

```
File "arpipe/pipeline.py", line 167, in process_document
    doc.script_map = profile.script_map
                     ^^^^^^^^^^^^^^^^^^
AttributeError: 'DocProfile' object has no attribute 'script_map'
```

## 5. Diagnosis — missing / inconsistent definitions

R1 named three symbols. A fourth was found (`write_span`), already recorded in
`docs/phase3/PHASE3_CLAIMS_SCOPE_RESEARCH.md:146`. All four are **call sites
present at START with no reachable definition**.

| Name | Call site | Definition at START | Committed anywhere reachable from `main`? | Call-site expectation |
|---|---|---|---|---|
| `profile.script_map` | `arpipe/pipeline.py:167` (read) | **absent** — `DocProfile` has no such field | No | per-page script/language telemetry list |
| `doc.script_map` | `arpipe/pipeline.py:167` (write) | **absent** — `StoredDoc` is `slots=True` with no such slot | No | assignable field persisted into `document.json` |
| `Confidence.QUARANTINE` | `arpipe/pipeline.py:385` | **absent** — enum has HIGH/MEDIUM/LOW/FAILED | No | enum member for grade `"quarantine"` |
| `store.write_year(write_span=)` | `arpipe/pipeline.py:392` | **absent** — parameter not in signature | No | suppress `mda.txt` for quarantined rows (P34) |
| `ocr_mod.OcrEngineUnavailable` | `arpipe/pipeline.py:396` | **absent** — not defined in `arpipe/ocr.py` | No | typed exception carrying `.page_no`, `.trail`, `.detail` (P-B5) |

All four verified programmatically against the clean checkout.

**Reachability note.** At START, `arpipe/verify.py:grade()` returns only
`"high" | "medium" | "low"` — it *never* returns `"quarantine"`. So the
quarantine branch is unreachable with the committed grader. `verify.py` is
byte-identical across START, P-M1 and the E0 snapshot, so quarantine grading was
never live in any of them.

---

## 6. Provenance analysis (R1 §5 dirty-working-tree gate)

### 6.1 Where the counterparts actually live

Per-file SHA-256 comparison of production modules:

| File | P-M1 `c9d71bb` | E0 snapshot `dea3ae5` | START `50769ff` |
|---|---|---|---|
| `pipeline.py` | `66ecf6cfa0d8` | `66ecf6cfa0d8` | `66ecf6cfa0d8` |
| `cli.py` | `69c9d4519b7f` | `69c9d4519b7f` | `69c9d4519b7f` |
| `verify.py` | `29dd0a415d58` | `29dd0a415d58` | `29dd0a415d58` |
| `patterns.py` | `0166ed14baa4` | `0166ed14baa4` | `0166ed14baa4` |
| `models.py` | `7d8dbc4a1196` | **`e40faa0b467c`** | `7d8dbc4a1196` |
| `ocr.py` | `5b6c4092549f` | **`affec70f2533`** | `5b6c4092549f` |
| `store.py` | `41f4f4aa3d38` | **`9f5a1b8ee3f9`** | `41f4f4aa3d38` |
| `triage.py` | `17e5a4ad79e0` | **`351a4aac1efc`** | `17e5a4ad79e0` |
| `textlayer.py` | `ee5e60fcee63` | **`02e868e011aa`** | `ee5e60fcee63` |
| `segment.py` | `e90c67b7d334` | **`6b1122cefdb6`** | `e90c67b7d334` |

START is byte-identical to P-M1 for **every** production module. The counterpart
definitions exist **only** in `dea3ae5`.

The E0 snapshot's hashes match the pre-E0 dirty-tree SHA-256 values recorded
independently in `docs/experiments/E0_REPOSITORY_SAFETY.md` §2.3 (e.g.
`models.py` `E40FAA0B467C...`, `ocr.py` `AFFEC70F2533...`, `store.py`
`9F5A1B8EE3F9...`, `triage.py` `351A4AAC1EFC...`). The snapshot is therefore a
faithful capture of the 2026-09-20 working tree.

### 6.2 Status of that snapshot

- `dea3ae5` lives **only** on `wip/2026-09-20-repository-safety`. It is **not**
  an ancestor of `50769ff` or of `origin/main`.
- Its own commit subject: *"REPOSITORY SAFETY SNAPSHOT — **NOT A SCIENTIFIC
  METHODOLOGY COMMIT** — preserve pre-E0 working tree modifications..."*.
- Its parent is `0fb8cbf` (2026-09-12), i.e. it branches from a point **before**
  P-M1; it is a preservation branch, not a lineage continuation.

### 6.3 What the snapshot would actually import

The snapshot does **not** contain isolated counterpart definitions. It carries a
large body of *later experimental* work entangled with them:

- `triage.py` — adds `_compute_page_script_meta()`: per-page Devanagari fraction,
  English-word fraction, `legacy_font_suspected`, `dominant_script`,
  `script_confidence`. This **is** legacy-font / script routing telemetry, and it
  adds a new `triage` to `verify` import.
- `ocr.py` — the **P-B5 behavioural change**: `Escalator.run_page` previously
  returned an empty `OcrPage` when every rung failed; it now **raises**. Documents
  that formerly recorded `mda_not_located` would record `ocr_engine_unavailable`.
  This is a genuine change of scientific outcome, not an interface repair.
- `store.py` — adds `write_span` **plus** `open_state` / `import_manifest_state` /
  `snapshot_state`, depending on `arpipe/state.py`, a 437-line module absent at START.
- `models.py` — adds the needed `QUARANTINE` and `script_map` **plus** unrelated
  `PageProfile.script_meta` and `MDASpan.body_script` (P-B2 Phase 1).
- Also in the snapshot: `test_ocr_bakeoff.py`, `test_ocr_preflight.py`,
  `test_legacy_font_corpus_measurement.py`, `test_script_map.py`,
  `test_pb2_candidate_body_script.py`, `state.py`.

Classification: **later experimental implementation**, not an
historically/evaluationally supported one.

### 6.4 A third, incompatible candidate

`docs/phase3/PHASE3_CLAIMS_SCOPE_RESEARCH.md:141` names an
`arpipe-step0a-candidate` at `0d39395...`. That object is **absent from this
repository** (`fatal: bad object`); the tree survives on disk at
`sep_week1/arpipe-step0a-candidate` as a **separate repo owned by another
account** (read-only; inspected via the filesystem, no git config changed).

It has `QUARANTINE`, `OcrEngineUnavailable` and `write_span`, has **no**
`script_map` anywhere, and its `pipeline.py` (`92c497bee8e9...`) **differs** from
START's — it omits the line-167 call entirely.

### 6.5 Three mutually incompatible candidates

| Candidate | `pipeline.py` | line-167 `script_map` call | QUARANTINE / write_span / OcrEngineUnavailable |
|---|---|---|---|
| START = P-M1 = main lineage | `66ecf6cf` | **present** | **absent** → cannot run |
| E0 snapshot `dea3ae5` | `66ecf6cf` (same) | present | present (+ script-map impl, P-B5, state.py) |
| Step0A candidate `0d39395` | `92c497be` (**different**) | **absent** | present |

### 6.6 Governing repository record

`docs/phase3/PHASE3_DECISION_SHEET.md` **D6 / Q6 — "Which identity, if any, is
intended 'As-Is ARPipe'?"** — **`AUTHOR CHOICE:` is blank.** Phase 3 records:

- *"No recovery snapshot promoted to canonical."*
- *"Recovery receipt says no accepted canonical SHA."* / *"accepted canonical SHA null"*
- *"E0 is a more complete saved later implementation; main is earlier; Step0A is curated and unadopted."*
- *"...investigate E0's suitability in the authorized later stage... Do not choose START for convenience."*
- *"These are inspected interface conflicts, not a baseline execution result. **No repair is made.**"*
- *"**No code fix or baseline execution is authorized in P1.**"*

**Provenance verdict: NOT ESTABLISHED.** Repository evidence establishes what the
E0 code *is* (a later saved working state) and explicitly records that it was
**never adopted** as the evaluated implementation.

---

## 7. Decision gate (R1 §6) — outcome

**Option A — commit existing evaluated code: REJECTED.** The definitions are not
in this worktree (clean at START); they are in a foreign branch's snapshot that
is self-labelled "NOT A SCIENTIFIC METHODOLOGY COMMIT", and Phase 3 records that
no snapshot was promoted to canonical. R1 §5: *"Do NOT commit a local definition
merely because doing so makes the package runnable."*

**Option B — minimal repair: REJECTED**, blocked by `script_map`.

`Confidence.QUARANTINE` and `write_span` could in principle be restored inertly
(the quarantine branch is unreachable under the committed `grade()`), and
`OcrEngineUnavailable` could be defined as a bare class without the P-B5 raiser.
But **`pipeline.py:167` executes unconditionally**, so it must be resolved, and
every available shape is forbidden:

| Repair shape | Why it is not authorized |
|---|---|
| (a) port E0's `_compute_page_script_meta` into `triage.py` | `triage.py` is an R1 §7 **STOP** file; and it implements legacy-font / script routing signals, forbidden by §2 and §7 |
| (b) add `script_map` as empty-default fields in `models.py` | Invents a null behaviour matching **no** candidate; `StoredDoc` is serialized into `document.json`, so it silently changes persisted output schema |
| (c) delete the line-167 call | Adopts the Step0A pipeline — selecting an explicitly **unadopted** candidate |

Each of (a)/(b)/(c) **is** the D6 "which identity is As-Is ARPipe" choice. R1 §2
forbids *"making C2 baseline decisions"*, *"reconstructing an As-Is baseline"*,
*"implementing legacy-font routing"* and *"new routing logic"*.

**→ R1 §6 "No safe option": STOP.**

---

## 8. Independent blocker — the repository's own conformance guard

`tests/test_phase2_1_semantic_conformance.py::test_historical_immutability_strict_allowlist`
diffs every path against `BASE_COMMIT 03a63f5`, requires each to match a 6-pattern
allowlist, and asserts **zero** changed paths under `arpipe/`, `dataset/`,
`configs/t0_4/`.

1. It **already fails at the untouched START commit** — `docs/phase4/PHASE4_DECISION_SHEET.md`
   is not allowlisted. This is pre-existing, not caused by R1.
2. Any `arpipe/` repair R1 asks for trips the explicit zero-change assertion.
3. Even `docs/identity/RUNNABLE_IDENTITY_v1.md`, the file R1 §11 mandates, is not
   allowlisted and would fail.

R1 §13 forbids weakening or deleting the test, so R1 as specified cannot be
completed on this base without an authorized allowlist amendment.

---

## 9. Tests and checks (run at START, no changes made)

| Check | Result |
|---|---|
| Import / package startup | **PASS** — `arpipe`, `pipeline`, `cli`, `triage`, `ocr`, `store`, `verify`, `segment` all import |
| CLI startup (`python -m arpipe.cli -h`) | **PASS** — full subcommand list renders |
| Full pytest | **1 failed, 311 passed, 17 skipped, 1 collection error** |
| — failure | `test_historical_immutability_strict_allowlist` (pre-existing, §8) |
| — collection error | `tests/t0_4/test_t0_4_setup.py` — `ModuleNotFoundError: jsonschema` (missing dep, not in `requirements.txt`) |
| HOLDOUT-safety gate | **PASS** — see below |
| Three-document FIT smoke test | **FAIL (3/3)** — identical `AttributeError` at `pipeline.py:167` |
| Clean-checkout runnable | **NO** |

This is **not** "all tests passed".

### HOLDOUT-safety gate

Test HOLDOUT references are **split-metadata and governance prose only**:
issuer-disjointness assertions over `holdout_manifest.csv`'s `issuer_id`/`split`
columns, manifest hash pinning, and wording checks. No test opens a HOLDOUT PDF,
reads HOLDOUT page content, generates HOLDOUT predictions, or touches HOLDOUT
Gold. `tools/t0_4/adapter.py:validate_holdout_access` is a **guard that raises**
on forbidden HOLDOUT purposes before final freeze. Reported, not altered.

### Three-document FIT smoke test

**Selection rule (recorded before execution):** rows of
`dataset/corpus_freeze/development_manifest.csv` with `split == "FIT"`, sorted by
`document_id` ascending (C locale), first three. 60 FIT rows total. No document
was substituted after seeing results.

| # | document_id | pdf_sha256 | Result | Runtime |
|---|---|---|---|---|
| 1 | `INE001F01019_2012` | `7ca96fce59cda07b884371a9af00365ccde511c33e5aaabb515b79df5e459dcb` | FAIL `AttributeError` @ `pipeline.py:167` | 0.37 s |
| 2 | `INE001F01019_2013` | `b43ffd8429742abbb63df738c25524448013c04f24a16ab8ce7a841307d1dd06` | FAIL `AttributeError` @ `pipeline.py:167` | 0.37 s |
| 3 | `INE001F01019_2017` | `7d6c7f1dff985bd0ddb0e3f676f1673c0a0a73c9a8e5561ea362e0c5b00118cc` | FAIL `AttributeError` @ `pipeline.py:167` | 0.31 s |

No output produced; profiling succeeded, the run aborted at line 167. Outputs were
directed to the session scratchpad, outside all frozen artifacts. The rule happens
to select three documents from one issuer; it was **not** changed, because this is
an executability test, not a performance or coverage test.

---

## 10. Scope and preservation audit

- **No commit created.** `arpipe/` unchanged. `configs/` unchanged. `tools/` unchanged. `tests/` unchanged.
- Frozen corpus and frozen dataset artifacts unchanged; read-only access to `development_manifest.csv` and `freeze_summary.json` only.
- **HOLDOUT untouched:** no HOLDOUT document accessed, no page content inspected, no prediction generated, no Gold inspected or created, no evaluation performed.
- No Gold created; no annotation performed; no sample-size decision.
- Phase 2.1 / Phase 3 / Phase 4 / T0 / T0.4 historical records unchanged.
- No B1–B8, C1, C2 or C4 decision made. No baseline reconstructed.
- No OCR, legacy-font, REMAP or routing work. No performance optimization. No performance-based selection — the halt is on provenance and authorization, and no output quality was measured.
- No new literature or external research.
- Nothing pushed to origin.
- `arpipe-step0a-candidate` treated as a read-only forensic tree; no git config modified.

## 11. What is needed to unblock

1. **D6 / Q6 author decision** — which identity is the intended "As-Is ARPipe": the E0 saved later implementation, the earlier main behaviour, or a newly-defined identity. This is the C2-coupled decision R1 forbids this task from making.
2. Given (1), an explicit authorization covering the `script_map` resolution, since every shape touches a §7 STOP file, a forbidden routing signal, or an unadopted candidate.
3. An authorized amendment to `ALLOWED_PHASE2_1_PATTERNS` (and to the `arpipe/` zero-change assertion) permitting the R1 repair and `docs/identity/`.
4. Add `jsonschema` to `arpipe/requirements.txt` (or record the intended exclusion), so the suite collects.

## 12. START-state SHA-256 manifest — `arpipe/` and `configs/`

```
0af8dbf9cc78fa702135b3cbf987f695009632f65eb61e283822f0e8bdac8a94  arpipe/CLAUDE.md
964ac96fa02a6031d1440bfc4e97d759113485a94b6707cf8ff62471d23c3712  arpipe/README.md
3942d5b3558f3e75c9eeca9222b4384bcca5503c9c825fcff70fc99dc10c1d82  arpipe/__init__.py
69c9d4519b7f3ba42c316f5395a9a2e21eb77053718458376ff32e6b7cbb48bb  arpipe/cli.py
cc1c2e0666d5777ee3f07bb6abb20ae44ba3e4bfd991dc90325539032ca86341  arpipe/companies.csv
93aba31b53d4173bde3ad322bd5625416eca29e86b89887461f5bc2c7d760c7c  arpipe/config.py
1ab406c607eac5c9799d5b5ac89b8c42f56bde8659f9f6214de5063d5bd3cb85  arpipe/configs/default.yaml
b45ca6ac379c5053d9f4268d6ed40a9f246a28557fc771edad6385a9bef73cbd  arpipe/configs/eval_protocol.md
bdfbe34ff572fc263e3cbd75dcd9081062619314d893f1d495989a3e9a66bca8  arpipe/discover.py
05a26ebd1eda21ce6594f32e90365f84882e2ccf59186e278c27b4a8e302b1ea  arpipe/eval_report.md
6e1c1b9ba6ef1e1c103d0882515f1c81fccceffd16bee5a18a8776b51457d057  arpipe/evaluate.py
37e298b47ab4ddb30b4c27f39c49fa092a872c7394a8588f4cdc9e6afd33fa76  arpipe/fetch.py
cd11a9752fad97049264b4d938bc99bc0dfbf63e92f6b7404d4e2ec5caff2eec  arpipe/labeller.py
7d8dbc4a1196cab812374d287a918f7dc60bd24359c89a4d82bb98c3cc37d2cd  arpipe/models.py
5b6c4092549f59155e50a9170503899558701e8695d6e91eb5f07ee1558aea13  arpipe/ocr.py
0166ed14baa4ed46fc55e8726c3449be29eda200ed6ade06846e8b7a14e507b5  arpipe/patterns.py
c773a391af94716ba0dd7d573963c2e8a33026012d2d9941c4768a006cdae619  arpipe/pilot_reports.jsonl
66ecf6cfa0d8a7ea46c928fbf646fbb06c4f5687a33e46555438e976bf76060d  arpipe/pipeline.py
5dc81b5223453abe2acfe3c0511decd0f36c40fee786ef112d60d9f19e482e49  arpipe/preflight.py
6c1cc994edfd749a6fdc8cda11ddf38f9389f9641e0bfc5ae36ff3ce007e5c2a  arpipe/reports_sample.jsonl
c2db8f0845394eebc6564f1191253e67c3bf6257cb6180a21debf47614ebe608  arpipe/requirements.txt
e90c67b7d334fe896029a2960dc49b1782f1a1b9f692f0be9feec73890de96ba  arpipe/segment.py
41f4f4aa3d38cf8a2485fac362d202f96c87294e5f6be4b09e06061075ff6d02  arpipe/store.py
ca233ddfd8c5c1682c094e38f533045efe06e7081233df649a344c2c31081063  arpipe/tests/make_fixtures.py
448d434253f263de5ce8f014c4807ac5b18940519e1a24a2ebb2ddeca2fc0e17  arpipe/tests/test_column_cut.py
6858ed9f5bdff687aed81216e8576a8181c0fb7ab09209673810a905b50b1a1e  arpipe/tests/test_config.py
8835977dcc0c283911e9e74c57acd8fc850c0440829c58d3bb1fdef24562bb8a  arpipe/tests/test_discover.py
bab55988b3462ecd84767d52e702804ee0d9f7be86798670460f924760143353  arpipe/tests/test_evaluate.py
ebd7ad63c86668ebb3b9a540d753b68b8fd461cdd54094111b4d4d8d80bc88b1  arpipe/tests/test_labeller.py
85e558d95d96274efa82c28f1a624a76f01ec5ac40a26d0a056602d5ca395f06  arpipe/tests/test_pipeline.py
5d5ba30ef365dc32bf23878fcfd8c895f4d7c1756fffb694461af8a0e3e23020  arpipe/tests/test_pm1_orderqc.py
aa54ab7044130be8dd512438dce11214ed838f0aa7f6306fae43d762827cc1c5  arpipe/tests/test_pm2_pagegrain_native_vs_ocr.py
dd3c97a85d0a6431b5aa3a93facd1a89759d6aa0c259e482dd074ed8b22578ba  arpipe/tests/test_preflight.py
ee5e60fcee63e3e6534ab9182e81b42a5f9140094b976732d7071653d80e798a  arpipe/textlayer.py
5b65e1edd5718890d1fed79ee4bb2beaf203649586a782f542d41350c7e05e08  arpipe/to_label.csv
17e5a4ad79e0442e5978a9981a9fca2474740a0d07371fae1dfc6df39d4134bd  arpipe/triage.py
c2e5463515b1179d052c6fb46e1cc6454a9e3a498beb29cf80e2c7799004e69d  arpipe/universe.py
29dd0a415d58874a53e01d52c8b802ad2f9fb550eb2c2a50efa9525f780f4b63  arpipe/verify.py
a3a575cda1ec7345f3a9ba5544da67401ab01a3c6041a22719b032cbeaefdd7e  configs/audit_config.json
912f60587ba2bc3de15ccd9048b10d3e43e6fd24b186d2a2cf4f7028cdcf6221  configs/audit_config.sha256
b45ca6ac379c5053d9f4268d6ed40a9f246a28557fc771edad6385a9bef73cbd  configs/eval_protocol.md
da647fba4b9a99059c7cfae5f2bbc1e07617f8e23385ef5e814e2a0d5dd646d2  configs/phase2_1/semantic_fixtures.json
65a10ae8c30237e8a3e9debedd6eae13328965e1cef0584c0a2506687889caf0  configs/t0_1r/input_allowlist.json
9dbbec3e8d5565a3d29114e1bcb46b613c187a8017832b00f2ff9d984ae4cdd9  configs/t0_1r/reconciliation_rules.json
c1286cde18df7efb3e68b78c9bcaf41a6888d5718d1136bbbe2944e124b03b26  configs/t0_1r/reviewer_expectations.json
0fbe3030eb03c4d4f4dafb338713f592f84f753936aca6c60f4a3fbeed7c6efb  configs/t0_3a/taxonomy_register.json
1be25b1f5f7b52249122cd7e29a8ed1f105f35ef8fff5d607dcf45c24df7de10  configs/t0_3a_r1/taxonomy_register.json
79727cddfb28e13544edeef4e35ea43897f4e521cf8ca62e2c447e1a90c0c6af  configs/t0_4/benchmark_config.json
3748fa145a3bb0667cc68dd1c3ac1c910cd3c5ea9b0b8d572c6460ea5bb05ac5  configs/t0_4/benchmark_manifest_schema.json
7648ea43aa0e06a5bab8d35ac19385cce2607d2ea09772e27bcaf50c81b871af  configs/t0_4/common_output_schema.json
089bf6de4d6de0ec64c49f19498e626bb8c5eaa579dfdbe2ea68bdc9a6a5ef42  configs/t0_4/efficiency_schema.json
74575cac2e96c71e01b006f258310362fbce1a05e5c899a0007542e7ccb4ed5e  configs/t0_4/engine_registry.json
78fb43f16e8d679b868b2b6600c3ad213ae1df5e5f4c0b7c8b8a37319ebcbc25  configs/t0_4/failure_taxonomy.json
538c498ff8c6ceda2f85cb92acf0e5bfe7a948cd6174db1729af1f6d599a5e66  configs/t0_4/future_results_schema.json
e8b33a4a0e04da72c3572604ca3f82677920617607abe266717975ee3cc65247  configs/t0_4/gold_schema.json
d7590bebe271163f2ad341cace35f4749754cf22da3018cef32b12ad09c66336  configs/t0_4/metrics_spec.json
d5aa91eb161cc04eb06fd20edc5941e88e9dcdcc70c71d17e2c259d3a625fbc3  configs/t0_4/oracle_routing_spec.json
bdbc512abe729c8401462223b2b540d997838ab897f369360cb3956b1939a781  configs/t0_4/raw_output_schema.json
412e040e9bcdc3915110906cd66d38a025e3aaad3f1f12bf31bf32327e17375c  configs/t0_4/sampling_spec.json
```

END TASK — halted at R1_IDENTITY_BLOCKER; no commit created.
