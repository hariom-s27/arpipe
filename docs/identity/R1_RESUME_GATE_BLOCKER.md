# R1-RESUME — Implementation Gate Blocker

`recorded_on`: 2026-09-25 · worktree `sep_week1/runnable-identity-r1-resume` ·
branch `runnable-identity-r1-resume` · START_SHA = D6/Q6 commit
`755c5519b9ab9484ab033685e563350a0cd0d685` (parent `50769ff`).
Status: **HALTED at §16 decision gate (Outcome B + one INFERRED dependency). No
change to `arpipe/`, no commit.** This file is untracked.

Note: the prompt's D6/Q6 SHA string (`755c5519b9ab9484ab033e685e563350a0cd0d685`,
41 chars) is malformed; git has exactly one commit touching
`docs/decisions/D6_Q6_AS_IS_IDENTITY_DECISION_v1.md`: the SHA above.

## 1. D6/Q6 record — verified

Matches all six expected points (reconstructed 2026-09-17 state; Phase-4 consumer
half + E0 provider half; no single SHA; C2 conditional; adopted for R1
runnability; composition deferred to R1). Two clauses bind this gate:

- §9.5: does **not** authorize `state.py`, `MDASpan.body_script`,
  `PageProfile.script_meta`, or the P-B5 OCR raise behaviour.
- §11.1–2: R1 must *propose* the composition and obtain authorization;
  `triage.py` needs explicit authorization.

## 2. New repository evidence (read-only, preserved PM1 runs in `arpipe-0.1.0`)

| # | Observation | Class |
|---|---|---|
| E1 | `pm1_baseline_run/` and `pm1_after_run/`: 182/182 `document.json` carry a non-empty `script_map`; all 37,133 entries have exactly the 7 keys emitted by E0 `triage._compute_page_script_meta`, `measurement_source = "existing_triage_telemetry"`, `legacy_font_suspected = "unknown"`. | DIRECT |
| E2 | Both runs: 194 manifest rows, 2 `quarantine` (INE008A01015 FY2024/2025, reasons incl. `WRONG_LANGUAGE_RISK`), `path = null` → E0 `store.write_year(write_span=False)` behaviour executed. | DIRECT |
| E3 | 364/364 `mda.json` contain `span.body_script: null` → the executed `models.py` had E0's `MDASpan.body_script` field; `annotate_body_script` was never called (consistent with Phase-4 `pipeline.py`, which does not call it). | DIRECT |
| E4 | 0 rows with `ocr_engine_unavailable` in either run; 29 rows used tesseract. Neither confirms nor refutes that the executed `ocr.py` had the P-B5 raise path. | DIRECT (absence) |
| E5 | `reports/pm1_baseline.json` porcelain lists `models.py, ocr.py, patterns.py, segment.py, store.py, triage.py, textlayer.py, configs/default.yaml` as modified on 09-17; no per-file hashes. Baseline run used pre-PM1 consumer files (reversed), after-run used PM1 = Phase-4 files. | DIRECT |
| E6 | `patterns.py`: P33 = PM1 = Phase-4 = E0 blob `afd8e86a`; dirty on 09-17 → the executed `patterns.py` is not recoverable from any commit. | DERIVED |
| E7 | E0 `configs/default.yaml` adds 8 `verify:` keys; every value equals the `verify.py` module default → behaviour-neutral. | DERIVED |
| E8 | E0 `textlayer.py` differs from Phase-4 only by two trailing blank lines. | DERIVED |

## 3. Four symbols

| Symbol | Required by | Candidate definition | Historical-use evidence | Required? | Additional behaviour | Class | Gate result |
|---|---|---|---|---|---|---|---|
| `profile.script_map` | `pipeline.py:167` (runtime `AttributeError`) | E0 `models.DocProfile.script_map`, `StoredDoc.script_map`, `PageProfile.script_meta`, `triage._compute_page_script_meta` + 2 call-site hunks | E1 | Yes | per-page script telemetry in `document.json`; `triage` imports 3 private `verify` symbols | DIRECT | **BLOCKED** — `triage.py` STOP-list; `PageProfile.script_meta` excluded by D6 §9.5 |
| `Confidence.QUARANTINE` | `pipeline.py:385` (grade set at `pipeline.py:325`, overriding `verify.grade()`) | E0 `models.py` enum member | E2 | Yes | none beyond P34 gate already in Phase-4 `pipeline.py` | DIRECT | Authorized (D6 provider role) |
| `ocr_mod.OcrEngineUnavailable` | `pipeline.py:396` except clause (evaluated when any exception propagates) | E0 `ocr.py` class, plus `_ensure_ready` and `Escalator.run_page` raise | E4 — no firing | Yes (class) | P-B5 raise path changes failure classification | INFERRED whether raise path executed | **BLOCKED** — class-only is a never-existed file; full file imports behaviour D6 §9.5 excludes |
| `write_span` | `pipeline.py:392` | E0 `store.write_year` parameter | E2 | Yes | E0 file also adds `open_state`/`import_manifest_state`/`snapshot_state` (lazy `state.py` imports) and a `rows=` kwarg | DIRECT | Authorized as a subset (hunk only) |

## 4. E0 provider files

| File | Required? | Historical component | Extra behaviour? | Class | Provenance | Proposed |
|---|---|---|---|---|---|---|
| `models.py` | Yes | QUARANTINE, 2×`script_map`, `script_meta`, `body_script` | `body_script` field (schema of `mda.json`) | DIRECT (E1–E3) | BEHAVIOURALLY SUPPORTED, not byte-proven for 09-17 | **Needs authorization**: verbatim E0 (historically supported, includes `body_script` + `script_meta`, contrary to D6 §9.5) vs subset (contradicts E3) |
| `triage.py` | Yes | `script_map` provider | telemetry only; no routing read | DIRECT (E1) | BEHAVIOURALLY SUPPORTED | **Needs explicit authorization** (STOP-list, D6 §11.2) |
| `ocr.py` | Yes (class) | `OcrEngineUnavailable` | P-B5 raise behaviour | INFERRED | UNKNOWN | **Needs author choice**: class only vs E0 verbatim |
| `store.py` | Yes (`write_span`) | P34 span suppression | state hooks (dead unless called) | DIRECT (E2) | BEHAVIOURALLY SUPPORTED | `write_span` hunk only; state hooks excluded |
| `segment.py` | No | `annotate_body_script` never called (E3) | P-B2 telemetry helpers | DERIVED | — | Exclude; STOP-list, not needed |
| `state.py`, `STATE.md` | No | none | P-B7 queue | DERIVED | — | Exclude (D6 §9.5) |
| `textlayer.py` | No | — | none (E8) | DERIVED | — | Keep Phase-4 |
| `configs/default.yaml` | No | — | none (E7) | DERIVED | — | Exclude (neutral) |
| `pnb_only.csv`, `reports.jsonl`, E0 tests | No | — | data / tests for excluded features | DERIVED | — | Exclude |
| `patterns.py` | n/a | executed bytes unrecoverable (E6) | — | DERIVED | irreducible limitation | Keep Phase-4; record limitation |

## 5. Why the gate fails

1. **Conflict between §14 and D6 §9.5.** The minimum historically-supported
   reconstruction must include `MDASpan.body_script` and `PageProfile.script_meta`
   (E1, E3: DIRECT). D6 §9.5 says neither is authorized. Only the author can
   resolve this.
2. **`triage.py`** must change to supply `script_map`; it is on the STOP list and
   D6 §11.2 requires explicit authorization.
3. **`ocr.py` composition depends on an INFERRED claim** (whether the 09-17 tree
   had the P-B5 raise path). Stop required per §8.
4. **Integrity test.** `test_historical_immutability_strict_allowlist` fails
   **at START** (first violation `docs/phase3/PHASE3_CLAIM_EVIDENCE_MATRIX.md`).
   Any `arpipe/` change or `docs/identity/RUNNABLE_IDENTITY_v1.md` adds more
   violations. Amendment needs explicit authorization (§25).
5. **`jsonschema`** still missing from venv and from `arpipe/requirements.txt` →
   collection error in `tests/t0_4/test_t0_4_setup.py`. Adding it to the
   requirements changes dependency declarations and needs authorization (§25).

## 6. Decisions needed to resume

- A1: authorize `models.py` = E0 verbatim (incl. `body_script`, `script_meta`) —
  amends D6 §9.5 — or a subset (contradicts E3).
- A2: authorize `triage.py` = E0 verbatim.
- A3: `ocr.py` = class only, or E0 verbatim (incl. P-B5 raise path).
- A4: `store.py` = `write_span` hunk only (proposed), or E0 verbatim.
- A5: allowlist amendment for `test_historical_immutability_strict_allowlist`
  (START already fails; R1 adds `arpipe/` + `docs/identity/`).
- A6: add `jsonschema` to `arpipe/requirements.txt` or not.

Not done: no C2 drift check (e.g. re-running E0 `triage` against E1 outputs),
no HOLDOUT access, no smoke test, no `arpipe/` change, no commit.
