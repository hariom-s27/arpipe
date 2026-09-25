<!--
Preserved by the R1 Evidence Preservation task, 2026-09-26.

This is the complete R1 Evidence Recovery Report, transferred verbatim from the
final message of the R1 Evidence Recovery session. Two conversational framing
lines were not carried over, and nothing else was changed:

  1. the leading "Written for: ..." audience line;
  2. the closing paragraph offering to package the report as a shareable page.

No finding, caution, correction or qualification was removed, reworded or
softened. This is a forensic record, not a success narrative: it documents
setup iterations that the R1 record itself does not mention, including a first
100-of-108 universe build, a failing first negative-test control, and a first
959-mismatch secondary comparison.

The evidence it describes is archived at docs/identity/evidence/r1-final/.
See docs/identity/R1_EVIDENCE_PRESERVATION_01.md for the preservation record.
-->

**Scope note carried from the recovery session.** Read-only throughout: no reruns, no commits, no source/test/config/dataset changes, no HOLDOUT processing. The clean `r1-final` worktree already sat on the expected commit, so no temporary worktree was created. `r1-final` is still at `383fa792…`, `git status` empty.

# R1 Evidence Recovery Report

## 1. Executive conclusion

**RECOVERED.** Every governing Track-A artifact named by R1-FINAL survives and hash-matches the values recorded in `RUNNABLE_IDENTITY_v1.md` §22 — all 8 scratchpad files plus `historical-comparison.json`, 9/9 exact. The base and candidate execution trees also survive and verify byte-exact against their Git commits, so the source→execution→output→comparison→claim chain closes with EXPLICIT links for the 108-document, 20,950-page, PageKind, OCR-routing and base/candidate-separation claims. The 431-test, 103-test and document-hash claims are not backed by any file artifact but are recovered verbatim from the preserved R1-FINAL session transcript, which records the exact commands and outputs.

Two cautions. First, **none of this evidence is in Git** — it lives in a Windows `Temp` scratchpad and the Claude transcript store, both subject to routine cleanup; the `r1-final-suite` checkout that produced `suite_pin.*` was already deleted. Second, the recovery surfaced setup iterations the R1 record does not mention (a first 100-document universe, a failing first negative-test control, a 959-mismatch first secondary comparison), all resolved before the governing runs and none changing a governing result.

No R1-REPRO is needed. A preservation task is.

## 2. Git identity and ancestry

| Item | Observed |
|---|---|
| Branch | `r1-final` (also `origin/r1-final`) |
| Final commit | `383fa79228d48bf39401936090b9cbe9c5509e95` |
| Parent | `28a67b63d890d8407fa9738a71ae37ad63148b73` ✓ |
| Worktree state | clean, `git status --porcelain -uall` empty |
| Identity universe | **59** tracked files under `arpipe/` + `configs/` at `28a67b6` ✓ |
| Combined digest | `de250c36a660d94a2e28b49b82860f77e130b04a6fdcfc3ebf444043f57ef203` ✓ |

The digest was **recomputed independently today** from Git blobs (SHA-256 per file, `<sha>  <path>\n` in bytewise path order) and reproduces exactly. `identity_universe.json` in the scratchpad matches that recomputation path-for-path and hash-for-hash, 59/59.

Observed ancestry — every expected commit is an ancestor of `383fa79`, and the DAG is strictly linear (0 merge commits; 10 commits from `755c551` to tip by both `--first-parent` and full count):

```
ff030d9 T0.4 base → 50769ff Phase-4 → 755c551 D6/Q6 identity
 → d551385 A1 → ca1498f A2 → ab9666b A3 → 24b8e00 A4 → c779c2e A5
 → 588b6e6 import smoke → 1db8ccd guard forensics
 → e86d755 T0.4 Amendment 01 → 28a67b6 enforcement+strict-xfail → 383fa79 R1-FINAL
```

Ancestry was tested with `git merge-base --is-ancestor`, not inferred from branch names. Note the record's own convention: identity is pinned at **`28a67b6`** ("the tip"); `383fa79` adds only four `docs/identity/*.md` files and changes no identity-universe file. Confirmed: `arpipe/` tree `f6475922…` and `configs/` tree `4b56d25b…` are identical across `588b6e6`, `28a67b6` and `383fa79`.

## 3. Search ledger

| Location | Scope searched | Relevant artifacts found | Relevant artifacts absent | Complete? | Reason for stopping |
|---|---|---|---|---|---|
| **1.** `arpipe-0.1.0/scratch/` | full recursive inventory (1,833 files); grep for `383fa79\|28a67b6\|588b6e6\|R1-FINAL\|suite_pin\|T0_4_AMENDMENT`; mtime filter | none | all R1 artifacts | Yes | 0 identifier hits; 0 files newer than 2026-09-20 (newest 2026-09-17 12:53) — predates the R1 era entirely |
| **2.** `arpipe-0.1.0/pm1_baseline_run/`, `pm1_after_run/` | top level, manifests, 35 company dirs each, mtimes; the one FIT doc relevant to §17 | **historical comparison inputs** (2026-09-17 outputs, mtimes 03:49–03:57 and 12:52); `manifest.jsonl` ×2 | no R1-FINAL execution artifacts | Yes | 0 files newer than 2026-09-18; these are the *historical* side, not R1 outputs |
| **3.** `sep_week1/r1-final-evidence/` | full tree, depth-unbounded for artifacts; all scripts read | **`historical-comparison.json`, `determinism-comparison.json`, `preregistration.json/.txt`, `fit-inputs.json`, 58+4+4 `execution.json`/`result.json`, 66 per-doc logs, `pytest-full.xml`, env/identity captures, `candidate-a`, `candidate-b`** | the eight §22 scratchpad files | Yes | complete; note its `pytest-full.xml` is the **older 382-test** run |
| **4.** Paths named by the R1 records (`r1-final-suite`, "this session's scratchpad") | direct resolution | **R1-FINAL session scratchpad `948b3666…`** with all 8 §22 files + `base-t04`, `cand-t04`, `run-a`, `run-b`, `out-run-a/b`, scripts, logs | **`sep_week1/r1-final-suite` — DELETED** | Yes | transcript shows it removed at 02:11 IST after a failed first attempt |
| **5a.** All 37 sibling session scratchpads, both project temp roots | filename search for the 8 artifact names; per-session file counts | only `948b3666…` | — | Yes | exhaustive over both roots |
| **5b.** All 9 other R1-era worktrees | `git status -uall` + artifact-name find to depth 3 | 2 untracked blocker `.md` files only | no execution artifacts | Yes | all clean or doc-only |
| **5c.** Claude session transcript store | all 30 transcripts, keyword-indexed | **`948b3666….jsonl`** (915 lines, 3.39 MB, sha256 `9352b967…`) + 2 saved tool-result files | **no transcript for the session that ran the 58-doc/4-doc batches** | Yes | that session's dir does not exist in the store |
| **5d.** Whole thesis tree, depth 6 | filename search for the 8 artifact names | `historical-comparison.json` only | the other 7 | Yes | confirms they exist *only* in the Temp scratchpad |

Semantically these are `NOT_FOUND_IN_SEARCHED_LOCATIONS`. The coverage above is stated so a later NOT_FOUND is reproducible; nothing here implies an artifact never existed.

## 4. Original artifacts recovered

**A. R1-FINAL session scratchpad** — `C:\Users\hario\AppData\Local\Temp\claude\d--sem-iitk-sem9-thesis\948b3666-670c-4ce4-951f-ff0d9a9b4562\scratchpad\`

| File | Bytes | SHA-256 | mtime (IST) | vs §22 |
|---|---|---|---|---|
| `universe.json` | 45,550 | `a1eb84a0006a8bf931f512cc980602e55c9fb62a2f0a0a2766e94cb07152725a` | 09-26 01:48:16 | **MATCH** |
| `profile_base.json` | 7,174,860 | `317657f9632f9e617c5e5a144c0db393f1610920072990eca168ca5a76e45be6` | 01:52:30 | **MATCH** |
| `profile_cand.json` | 7,174,860 | `7d350ff0aad1165678668f91aa440bec308f1551f40f5658fa7bf9bc87121363` | 01:52:33 | **MATCH** |
| `comparison.json` | 2,427 | `1cae94f9c7a792a12d166b14b8f7fea5f406e67e41b9898edb29af8a0a016e14` | 01:53:12 | **MATCH** |
| `evidence_compact.json` | 73,972 | `767e421257f5703d7790e39d2cf02f784c6506a4b0b54588c9ebfbb179ffc2c5` | 02:03:18 | **MATCH** |
| `suite_pin.txt` | 1,976 | `1861f8fcb03e869d90ed70c6e141740e9507fa21a105cc90cd0a0a19aee68110` | 01:58:36 | **MATCH** |
| `suite_pin.xml` | 60,979 | `8e7475f6b336f0fd73472002b62af6d591b4aedfbc3df7cae12f2eeaffd97a06` | 01:58:35 | **MATCH** |
| `negative_tests.out` | 4,176 | `287aa8a1c114aa5074ecccc720ff2f0bb764319ca571fdb029e02abfc6961ada` | 01:45:21 | **MATCH** |

Supporting, not hash-listed in §22: `identity_universe.json` (`ff99ed2b…`), `environment_final.txt` (`b7322634…`), `build_universe.py` (`6af0a519…`), `profile_docs.py` (`41804798…`), `compare_profiles.py` (`fcd4b158…`), `run_pipeline_doc.py` (`c0f2dee0…`), `negative_tests.sh` (`edff8050…`), `gen_identity.py` (`5ff6ccee…`), `identity_template.md`, `profile_base.log` / `profile_cand.log`, `run-a.log` / `run-b.log`, and the four execution trees `base-t04/`, `cand-t04/`, `run-a/`, `run-b/` with outputs `out-run-a/`, `out-run-b/`.

Filesystem context: all of the above sit as siblings in one scratchpad directory whose naming ties it to this project and session; `base-t04`/`cand-t04` were created 01:47:02, one minute before the universe was built and two before profiling began. Both execution trees still contain `__pycache__/*.cpython-314.pyc` — in-place bytecode, consistent with having actually been executed there.

**B. Repository-side evidence dir** — `D:\sem_iitk\sem9\thesis\sep_week1\r1-final-evidence\` (untracked)

| File | Bytes | SHA-256 | mtime (IST) |
|---|---|---|---|
| `historical-comparison.json` | 24,856 | `e9fc54826b42694f31c62b29a5850ce2f2a6605ba5a79797066373132a5f5329` (**matches §22**) | 09-26 00:41:42 |
| `determinism-comparison.json` | 2,261 | `142990c9054b10b18cb895497e28ed7669f9a969d4af1c83e8627ba301df7bb8` (not in §22) | 00:43:02 |
| `preregistration.json` | 2,858 | `e613eb85dedef358ba1eb1b5812744c70150829aeb79fc2cbe1898a17a7bb95f` | 00:36:24 |
| `fit-inputs.json` | 3,986,960 | `831bd3e712dbf53ff711e1bae3eeabcdc40ece1f55f3f30f2eda701ba96fae77` | 00:36:24 |
| `compare_outputs.py` / `prepare_run.py` / `run_document.py` / `run_batch.py` | — | `3e97dc51…` / `ce835661…` / `2248c6b3…` / `88658229…` | 00:36–00:39 |
| `pytest-full.xml` (**older 382-test run**) | 64,618 | `437dfbdf992df953d264ecf9493c2bb0c793a0ddf4a25552bad16a7d7f49731a` | 00:44:09 |

Plus `primary/` (58 docs), `smoke-a/`, `smoke-b/` (4 each), 66 per-document logs, and worktrees `candidate-a`/`candidate-b`, both clean at `588b6e6`.

**C. Preserved 2026-09-17 historical outputs** — `arpipe-0.1.0/pm1_baseline_run/manifest.jsonl` (`a2d0243c…`, 2026-09-17 03:57:04) and `pm1_after_run/manifest.jsonl` (`5d8bed2a…`, 12:52:20).

**D. Session transcript** — `C:\Users\hario\.claude\projects\d--sem-iitk-sem9-thesis\948b3666-670c-4ce4-951f-ff0d9a9b4562.jsonl`, 3,388,079 bytes, sha256 `9352b967c0c6dc4d30b850420b2ac92da1773caf4113c6578fd9642e8055d217`, 915 lines, 128 tool calls, spanning 2026-09-25T19:49:46Z → 20:33:35Z (01:19–02:13 IST).

Nothing was moved, renamed, normalised or copied before recording the above.

## 5. Artifact provenance chains

**Chain 1 — the governing Track-A comparison** (all links EXPLICIT):

| Link | Artifact / value | Evidence | Class |
|---|---|---|---|
| SOURCE (base) | `ff030d97c13c8a2a977521bf91be2aca0cbf3034` | `evidence_compact.json: base_commit`; transcript `git archive` call | EXPLICIT |
| SOURCE (cand) | `28a67b63d890d8407fa9738a71ae37ad63148b73` | `evidence_compact.json: candidate_commit` | EXPLICIT |
| TREE fidelity | `base-t04`, `cand-t04` exports | **re-verified today: 46/46 and 59/59 files hash-equal to their Git blobs, 0 mismatches, no extra non-pycache files** | EXPLICIT |
| RUN METADATA | distinct `checkout`, `arpipe_file`, `python`, `seconds` (220.09 vs 223.82) inside each profile | `profile_base.json` / `profile_cand.json` headers; `profile_*.log` print `sys.path[:4]` rooted in each export | EXPLICIT |
| INPUT | 108 docs from `development_manifest.csv` + `validation_manifest.csv` | `universe.json`; manifests committed `23d6228`, **2026-09-18** | EXPLICIT |
| INPUT integrity | `pdf_sha256` re-verified against content-addressed blobs | `build_universe.py`; **re-verified today: 108/108 blobs hash-match the frozen manifest** | EXPLICIT |
| OUTPUT | `profile_base.json`, `profile_cand.json` | hashes match §22 | EXPLICIT |
| COMPARISON | `comparison.json`, `evidence_compact.json` | hashes match §22; `compare_profiles.py` recovered | EXPLICIT |
| CLAIM | §13 of the identity record | `gen_identity.py` substitutes every number from `comparison.json`/`evidence_compact.json` — the record is mechanically generated, not hand-typed | EXPLICIT |

The decisive recovered fact: **`profile_base.json` and `profile_cand.json` differ in exactly 17 bytes, all within the header fields (`checkout`, `arpipe_file`, `seconds`), at offsets 140–1011. The `thresholds_after_configure`, `needs_ocr_kinds` and entire `documents` payloads are equal.** Identical page-kind and OCR-routing results are therefore not a summary assertion — they are the byte-level state of two independently produced 7.17 MB outputs.

**Chain 2 — 431-test suite** (one link transcript-borne):

`28a67b6` → `git worktree add --detach` to `r1-final-suite`, verified clean, `arpipe` resolved inside it (transcript 01:57 IST) → `pytest -q --junitxml` → `suite_pin.txt` + `suite_pin.xml` (hashes match §22) → §18. The worktree no longer exists, and neither `suite_pin` file records a commit; the commit binding is EXPLICIT **in the transcript**, MISSING in the artifacts themselves.

**Chain 3 — 58-document historical comparison** (all links EXPLICIT, but no transcript):

`588b6e6` → `candidate-a` worktree (still present, clean, at that commit) → `preregistration.json` fixes the 58-document roster at 00:36:24 → `run_document.py` asserts FIT membership, commit match, clean tree, and PDF hash before opening each file → 58 `result.json`/`execution.json` (each records `candidate_import` = `candidate-a`) → `compare_outputs.py` vs `pm1_baseline_run` → `historical-comparison.json` (hash matches §22) → §15.

**Chain 4 — four-document determinism** (all links EXPLICIT): `candidate-a` → `smoke-a`; `candidate-b` → `smoke-b`; both at `588b6e6`; `compare_outputs.py` in determinism mode → `determinism-comparison.json`.

## 6. Track-A evidence

What is **independently verified**, in the report's formal sense (traceable through preserved artifacts without relying on R1 prose):

- **108 documents — VERIFIED.** `universe.json` roster is exactly the 60 FIT + 48 VALIDATION rows of the frozen manifests: document-id sets, splits and `pdf_sha256` values all agree, and the same 108 ids key both profile outputs. Manifest columns confirm 60/48 rows.
- **20,950 pages — VERIFIED**, and independently corroborated: the frozen `dataset/corpus_freeze/page_profile.csv` holds exactly 20,950 rows for these 108 documents (FIT 12,652 / VALIDATION 8,298), and its per-document row count equals the profiled `n_pages` for all 108.
- **PageKind 20,950 / 20,950 identical — VERIFIED.** Direct consequence of the byte-identical `documents` payloads; `comparison.json` reports `pagekind_mismatches: 0` with an empty mismatch list.
- **OCR page routing 20,950 / 20,950 identical — VERIFIED.** Same substrate; `ocr_page_mismatches: 0`. `compare_profiles.py` additionally asserts each page's `needs_ocr` flag agrees with `ocr_page_numbers()`, so the two routing representations are cross-checked.
- **Document OCR-page sets 108 / 108 identical — VERIFIED.** `ocr_set_document_mismatches: 0`.
- **Base/candidate separation — VERIFIED.** Two exports from two different commits, byte-verified against Git; differing in **exactly** `models.py`, `ocr.py`, `store.py`, `triage.py` and no fifth path; two processes launched concurrently (distinct PIDs 1503/1504, separate logs, different elapsed times); each process asserted at runtime that `arpipe`, `triage`, `models`, `config` all resolved inside its own export. The same `python.exe` was used for both — appropriate, since the variable under test is the source tree.
- **Population integrity (pre-execution) — VERIFIED.** The strongest available form: the roster is not a post-hoc list of documents that happened to succeed, it is the *complete* frozen manifest population, with `not_runnable: []` and `document_errors: []`. The manifests were committed on 2026-09-18, eight days before execution; `universe.json` was written at 01:48:16 and profiling launched at 01:48:48 — ordering confirmed by both filesystem mtimes and transcript call order. No document was excluded for failure, disagreement, unusual behaviour or output availability; none could have been, because the run covered the manifests in full.

One process detail the R1 record omits, reported for completeness: the **first** universe build (01:47:34) located PDFs by company-directory and found only 100 of 108, listing 8 as "no PDF at expected baseline path". Those 8 were then located in the content-addressed store, and `build_universe.py` was rewritten to resolve every PDF by its frozen `pdf_sha256` with content re-verification. This happened **before any triage ran** and was driven by file location, not by results — it is not outcome-dependent exclusion. But it does mean the final method described in §13 was adopted mid-task rather than pre-registered.

Supplementary (as the record labels it): all 20,950 pages agree on every serialised `PageProfile` field. Precisely: `profile_docs.py` serialises 13 fields and **excludes `script_meta` from serialisation entirely**, so `script_meta` was never compared rather than compared-and-differing. §13's phrase "identical on every serialised field except `script_meta`" is accurate only under that reading.

## 7. Historical 58-document comparison

`historical-comparison.json`, sha256 `e9fc54826b42694f31c62b29a5850ce2f2a6605ba5a79797066373132a5f5329` — matches §22.

| Field | EXACT | DIFFERENT | Other |
|---|---|---|---|
| `located` | 58 | 0 | |
| `start_page` | 57 | 1 | |
| `end_page` | 58 | 0 | |
| `grade` | 57 | 1 | |
| `span_path_nullness` | 58 | 0 | |
| `script_map` | 58 | 0 | |
| `per_page_kind` | — | — | `UNAVAILABLE_BOTH` ×58 |

58 compared, 57 exact on all available comparable fields, 1 with differences, `fully_comparable_documents: 0` (precisely because per-page kinds were never serialised historically — so "57/58" rests on 6 fields, not 7).

The single difference, **`INE00LO01017_2025`**: `start_page` 15 → 16, `grade` medium → high. Independently re-checked at source today: both preserved 2026-09-17 runs (`pm1_baseline_run`, `pm1_after_run`) record start 15 / end 29 / medium, and the candidate records 16 / 29 / high — so the historical value does not depend on which run is used. The roster compared equals the pre-registered `primary_documents` list exactly, in order.

Attribution **UNATTRIBUTED**, retained. Not reinterpreted. The supporting basis is preserved and checks out: both profiles show the document as 243 pages, 242 `digital` + 1 `scanned`, whole-document OCR set `[1]`, and **every page of the span window is `digital` with `needs_ocr` false** in both base and candidate — so OCR did not touch the evidence the span was computed from. `reports/pm1_baseline.json` contains one occurrence of "tesseract" (the `escalator` config value) and zero occurrences of "leptonica" or "tessdata"; no historical engine version exists to compare against.

One small correction to §17: it gives the window character range as "1 851–5 016". The 5,016-character page is page 13, which lies **outside** both the historical (15–29) and candidate (16–29) windows; the maximum inside either window is 4,384. The conclusion is unaffected — every window page is `digital` and unrouted either way.

## 8. Four-document determinism — kept separate from Track A

`determinism-comparison.json`, sha256 `142990c9054b10b18cb895497e28ed7669f9a969d4af1c83e8627ba301df7bb8` (not hash-listed in §22).

Documents: `INE001F01019_2012`, `INE001F01019_2013`, `INE001F01019_2017`, `INE008A01015_2024`. Result: `documents_compared: 4`, `exact_on_all_available_comparable_fields: 4`, `documents_with_differences: 0`; `located`/`start_page`/`end_page`/`grade`/`span_path_nullness`/`script_map` all EXACT ×4; **`per_page_kind: UNAVAILABLE_BOTH` ×4** — the stated limitation, preserved. `fully_comparable_documents: 0`.

Provenance: `smoke-a` ran from `candidate-a`, `smoke-b` from `candidate-b`, two separate worktrees both still present and clean at `588b6e6`; each document's `execution.json` names its own checkout. `preregistration.json` records why a fifth candidate (`INE008A01015_2025`) was dropped: `NOT_FIT; no output opened; no replacement` — an eligibility exclusion made before execution, not an outcome-dependent one.

**This is a 4-document, 2-run pipeline determinism result. It is not evidence for the 108-document Track-A comparison**, which used a different method (triage profiling, no pipeline, no OCR) and a different population.

Separately, §17's three-run agreement on `INE00LO01017_2025` is also recovered: `out-run-a/result.json` and `out-run-b/result.json` (from `run-a`/`run-b`, both byte-verified today against `28a67b6`, 59/59) agree with the earlier session's run #1 — 1 distinct outcome tuple across three runs. The transcript's equality test was JSON-object equality, not a byte comparison; the record's phrase "byte-identical `result.json`" slightly overstates the test performed, though the compared structures were fully equal.

## 9. Test-suite evidence

**431-test suite — VERIFIED.** `suite_pin.txt` (`1861f8fc…`) ends `411 passed, 17 skipped, 3 xfailed in 62.61s`. `suite_pin.xml` (`8e7475f6…`) carries `tests="431" errors="0" failures="0" skipped="20"`, `timestamp="2026-09-26T01:57:33.237685+05:30"`, `hostname="Hariom-Singh"`. Parsing its 431 `<testcase>` elements gives exactly **411 pass / 17 skip / 3 xfail**, 0 failures, 0 errors, 0 xpassed — matching the claim on every line. The 3 xfails are exactly the three registered original T0.4 guards. The 17 skips break down 13 + 2 fixture skips, 1 sampling, 1 `live_store` — 17. The 49 enforcement tests in `tests/test_t0_4_amendment_01.py` are all present and all passing, including the 12 parametrised `test_strict_expected_failure_semantics` cases.

Execution identity comes from the transcript, not the artifacts: worktree added at `28a67b6`, `git status` empty, `arpipe` resolved to `r1-final-suite\arpipe\__init__.py`, `jsonschema 4.26.0` supplied from the scratch `test-deps` on `PYTHONPATH`, pytest exit 0. The transcript also preserves a **third** run at 02:09 IST against the *final* commit `383fa79`, again `411 passed, 17 skipped, 3 xfailed`, with the identity digest re-checked in the same call and matching.

**103-test scratch-fixture run — VERIFIED (transcript-only).** Recovered verbatim: fixtures built in `run-b/arpipe` (70 MB), `arpipe` confirmed importing from `run-b`, then `103 passed, 1 skipped in 5.94s` with the remaining skip being `live_store blobs not present`. Corroborated physically — the `run-b` export survives, verifies 59/59 against `28a67b6`, and still holds its 70 MB `fixtures` directory, while `run-a` has none. No fixture entered the repository.

**The 382-test result is excluded**, as instructed. For the record it is a genuinely different run: `pytest-full.xml` in `r1-final-evidence`, `tests="382" failures="5"`, timestamp 2026-09-26T00:43:03, exit code 1, the 5 failures being 2 `tests/t0_1` PDF-path failures plus the 3 T0.4 guards not yet registered as xfail. `tests/t0_1` is byte-identical between `588b6e6` and `28a67b6`; the 49-test delta comes from `tests/test_t0_4_amendment_01.py` and `conftest.py`, added in `28a67b6`.

## 10. Negative-test evidence

`negative_tests.out` (`287aa8a1…`) recovered, plus the generating script `negative_tests.sh` (`edff8050…`). All six required outcomes are present as original execution output:

| Case | Recorded outcome |
|---|---|
| Control | 49 passed |
| Control, `core.autocrlf=true` | 49 passed (410 CRLF working-file lines) |
| (i) one byte of protected `_classify` flipped (`<`→`>`, offset 13396) | 2 failed, 47 passed — both expected tests |
| (ii-a) fifth path committed (`arpipe/verify.py`) | FAILED, `unauthorized: ['arpipe/verify.py']` |
| (ii-b) fifth path untracked (`arpipe/zz_fifth_path.py`) | FAILED, `untracked files under arpipe/` |
| (ii-c) fifth path uncommitted | FAILED, `working tree changes outside A1-A4` |
| (iii) `arpipe/` restored to T0.4 base | 3 failed, each `[XPASS(strict)]` |
| (iv) unrelated violation added | 3 failed, no XFAIL |

All mutations ran in disposable clones under the scratchpad; the transcript confirms the candidate worktree's HEAD was unchanged and the clones were deleted, with no `neg-clone` entry in the worktree registry today.

Two honest qualifications:
- **The byte-binding is INFERRED.** The transcript records the clone at `HEAD=e86d755` with `conftest.py` and `tests/test_t0_4_amendment_01.py` copied in as *uncommitted* files. Those files were committed as `28a67b6` 22 seconds later (01:45:21 → 01:45:43), and the transcript shows no edit to them in between (last patch 01:44:42, matching the file's mtime). So the tested bytes are almost certainly blob `6f1185d4…`, but no artifact hashes them at test time. The linkage is strong, and it is an inference.
- **The first control run failed and is not mentioned in the record.** At 01:43:23 the control produced `27 failed, 22 passed`. A `_working_bytes()` helper was then added to the test file — it undoes a checkout-time LF→CRLF conversion, and only when the committed blob contains no CR — after which the control passed 49/49 and the CRLF robustness control was added. That is a defensible fix to a Windows checkout artefact, and the surviving `negative_tests.out` is the post-fix run. But the enforcement suite's byte comparisons were relaxed in response to a failing control, and §12 presents only the clean result.

## 11. Document-hash evidence

**VERIFIED (transcript-only).** No file artifact exists. The transcript preserves two executions of `python tools/check_doc_hashes.py`:

- 01:31:48 IST, in `r1-final` — full listing of all 10 `[PASS]` lines against `docs/experiments/PHASE2.1_PROVENANCE_CORRECTIONS.md:63–72` (each `recorded=` equals `actual=`), then `Checked 10 hash claim(s) across 1 doc(s); 0 unallowed failure(s).`, `exit=0`.
- 02:09 IST, in `r1-final-suite` at the final commit `383fa79` — same summary line.

The claim's substance is therefore fully auditable, but only from the transcript.

## 12. Evidence-chain limitations

Reasons a claim could not reach a stronger footing, rather than restatements of status:

1. **`suite_pin.txt` / `suite_pin.xml` do not identify their own commit.** Neither embeds a SHA, and the `r1-final-suite` worktree that produced them was deleted at 02:11 IST (after a first `git worktree remove` failed with `Permission denied`, followed by `rm -rf` and `git worktree prune`). Taken alone, these two files are `FOUND_BUT_INCOMPLETE`; they reach VERIFIED only because the transcript records the checkout, its commit and its clean status. The JUnit timestamp (01:57:33) and the `suite_pin.txt` mtime (01:58:36) are consistent with that window, but timestamps alone cannot establish which tree ran.
2. **`comparison.json` carries no identity of its own.** It contains only numbers — no base or candidate commit, no population manifest, no run metadata, no timestamp. A reviewer handed only this file could not tell what was compared. It reaches VERIFIED through `profile_base/cand` headers, `evidence_compact.json`'s two commit fields, and the surviving exports.
3. **The 103-test and document-hash claims have no artifact at all** — no `.txt`, `.xml` or `.json` was written. They rest entirely on the session transcript, which is a preserved contemporaneous record but not a project artifact and not covered by any retention guarantee.
4. **The session that produced `r1-final-evidence` left no transcript.** The 58-document and 4-document runs are auditable only from their own outputs, scripts and pre-registration. Those are internally strong (each `execution.json` names its checkout; `run_document.py` asserts commit, clean tree and PDF hash before opening anything), but there is no independent record of the commands issued.
5. **Filesystem timestamps are contextual only.** They are consistent with the transcript throughout, and I have used them for ordering, not for establishing execution time. All clock-based ordering claims above are corroborated by transcript call sequence.
6. **`arpipe/patterns.py` executed bytes remain unrecoverable** (dirty in the 2026-09-17 porcelain) — an irreducible limitation already recorded, and unchanged by this recovery.
7. **No 2026-09-17 Tesseract version is recorded anywhere permitted**, re-confirmed at source, so the §17 OCR-drift question stays `NOT VERIFIABLE`.
8. **Hash matches were not treated as provenance.** Every §22 match above is accompanied by an independent link — export-vs-Git verification, artifact-internal run metadata, execution-directory relationship, or a transcript call — precisely because byte identity alone would not establish historical origin.

## 13. Remaining provenance gaps

- **Durability is the live risk.** Every recovered governing artifact sits in `C:\Users\hario\AppData\Local\Temp\…` or the Claude transcript store. Neither is in Git, neither is backed up, and both are ordinary cleanup targets. The `r1-final-suite` deletion already shows how fast a link in the chain disappears.
- `determinism-comparison.json` and the `run-a`/`run-b` artifacts are not hash-listed in §22, so the record does not currently pin them.
- The `r1-final-evidence` session's command history is gone and cannot be recovered.
- The negative-test file-byte binding stays INFERRED unless the tested bytes are hashed in a future run.
- Track B remains UNRESOLVED / DEFERRED; C2 remains CONDITIONAL. Neither is touched by this recovery.

## 14. R1 recovery status

**RECOVERED.**

Major governing execution artifacts are found and sufficiently verified: 9/9 hash-listed artifacts recovered exactly, both execution trees byte-verified against Git, the 59-file identity digest reproduced independently, ancestry confirmed on the real DAG, and the population traced to manifests frozen eight days before execution with no document excluded. The three claims lacking file artifacts (431-test at the final tip, 103-test, document-hash) are recovered from a preserved contemporaneous transcript with full commands and outputs.

This verdict is about the *survival and traceability of evidence*, not a re-endorsement of R1's conclusions. The qualifications in §6, §7, §8 and §10 — the mid-task universe-method change, the `5 016` range slip, the JSON-not-byte equality, the unreported first control failure — are all recorded because the standard here is that a reviewer should be able to see what actually happened, not only the cleaned-up result.

## 15. Next action

**No R1-REPRO is needed, and none was performed.** The historical evidence was recovered rather than recreated, so a reproducibility run would answer a question that is not currently open.

The action this recovery does argue for is a **separately authorized preservation task**: copy the `948b3666…` scratchpad, the session transcript, and `r1-final-evidence/` into a durable location with a hash manifest, and extend the §22 table to cover `determinism-comparison.json` and the `run-a`/`run-b` artifacts. That is a preservation step, not a new experiment — but it is outside this task's scope and I have not started it.

Not begun, per scope: B1–B8, Gold, OCR experiments, prior-art research, HOLDOUT work beyond the disjointness columns already read.
