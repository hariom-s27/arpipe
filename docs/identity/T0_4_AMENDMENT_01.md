# T0.4 Amendment 01 — Governance Record

Recorded 2026-09-26 on branch `r1-final` (R1-FINAL v3, Step 1). This file is the governance
record required by the amendment itself (section 8). The ratified amendment text below is
reproduced exactly; the only entries added inside it are the three author fields, which the
author supplied in the ratification statement recorded after it. Everything after the
ratification statement is an annex added by the recording task and is **not** part of the
ratified text.

Evidence labels: **VERIFIED** (repository content or command output), **DERIVED** (mechanical
consequence of verified facts), **INFERRED** (interpretation not stated by the repository),
**NOT VERIFIABLE** (required evidence is absent).

## 1. Ratified text

The block below is the exact ratified text. The tamper-evidence hash in Annex A is computed
over the lines between the opening and closing fences, with line endings normalised to LF.

~~~text
------------------------------------------------------------
T0.4 AMENDMENT 01 — R1 PROVIDER RECONSTRUCTION
(TRACK A SCOPE ONLY)
------------------------------------------------------------

1. WHAT CHANGES

The following four files may differ from the T0.4 base only by the hunks
admitted under A1–A4:

    arpipe/models.py
    arpipe/triage.py
    arpipe/ocr.py
    arpipe/store.py

The authorized commits are:

    d5513859a5315800a7b6c68711756798129ab8ee
    ca1498f75f14495bfc6ec829ef2b5ef728da2d3d
    ab9666b032a5838be3ae3a24a58aae68a4fd46b0
    24b8e000f23d18faabd16f828bd20eeb5328ddf7

Do not trust these SHA values merely because they appear here.
R1-FINAL must independently resolve and verify every full SHA from Git.

No other path under arpipe/ may differ from the T0.4 base.

2. WHAT STAYS PROTECTED — TRACK A

The protected symbols and files identified in:

    docs/identity/T0_4_GUARD_FORENSICS.md

as the Track-A protected scope, and ratified by the author below, must remain
byte-identical to the T0.4 base.

The governing behavioural requirement is stronger than the source list:

    T0.4-base triage and candidate triage must produce identical page kinds
    and identical OCR-page sets for every FIT and VALIDATION page.

The behavioural reproduction is the governing evidence for this amendment.

The source-level protected list is the regression guard against future edits.

3. TRACK B — EXPLICITLY UNRESOLVED

The meaning of the T0.4 phrase:

    "the same frozen sequence"

is not established by the repository record.

This amendment makes no claim about its meaning.

Under a literal interpretation referring to the T0.4 base tree, the T0.4 base
could not execute the full Track-B pipeline end to end because the frozen tree
did not contain all provider-side objects required by its consumers.

Track B is therefore explicitly DEFERRED.

No Track-B execution is authorized by this amendment.

Before any Track-B execution occurs, the author must resolve the meaning of
the frozen sequence and record the resolution through the applicable governance
mechanism.

This unresolved Track-B question is NOT an R1 gate.

4. ORIGINAL T0.4 GUARDS

The three original T0.4 guard implementations are not edited.

They remain byte-identical to the forensic state.

They continue to execute.

Because the authorized A1–A4 reconstruction necessarily causes those literal
path-level guards to report the known T0.4 freeze deviation, their existing
node IDs may be registered externally as STRICT EXPECTED FAILURES.

The original guard implementations themselves must remain unchanged.

STRICT means:

    expected guard failure -> XFAIL
    unexpected guard pass  -> XPASS(strict) -> SUITE FAILURE
    unrelated failure      -> SUITE FAILURE

The expected-failure registration must cite this amendment and identify the
four authorized A1–A4 paths.

5. EXACT PATH BOUNDARY

The only production paths under arpipe/ authorized to differ from the T0.4
base are exactly:

    arpipe/models.py
    arpipe/triage.py
    arpipe/ocr.py
    arpipe/store.py

Any fifth changed arpipe/ path is unauthorized and must fail the R1 suite.

6. PHASE 2.1 ADMISSION

The Phase 2.1 immutability mechanism must admit, by exact path only, the
new amendment record and the new enforcement/expected-failure registration,
without modifying the original T0.4 guards.

The original frozen T0.4 directories remain untouched.

7. D6 ERRATUM

The D6/Q6 decision record:

    docs/decisions/D6_Q6_AS_IS_IDENTITY_DECISION_v1.md

recorded:

    "T0.4 amendment: NO"

That statement did not account for the T0.4 path-level guards established by
the later forensic audit.

This amendment records the correction.

The original historical decision must not be rewritten as though this
amendment existed at the time.

8. AMENDMENT FORMAT

T0.4 itself did not define a complete amendment-file format.

This amendment therefore establishes the format for this specific governance
record.

The amendment file is exactly:

    docs/identity/T0_4_AMENDMENT_01.md

It must NOT match:

    docs/experiments/PHASE2.1_T0.4_AMENDMENT_*.md

The Phase 2.1 conformance rule concerning that path pattern remains unchanged.

AUTHOR: Hariom Singh

DATE: 2026-09-26

CHANGES TO THIS DRAFT: none

------------------------------------------------------------
END AMENDMENT
------------------------------------------------------------
~~~

## 2. Ratification statement (verbatim from the author)

The author's ratification message, received in the R1-FINAL v3 session on 2026-09-26, read:

> I explicitly ratify Part 1 of the T0.4 Amendment 01 draft verbatim.
>
> AUTHOR: Hariom Singh
> DATE: 2026-09-26
> CHANGES TO THIS DRAFT: none
>
> Proceed with R1-FINAL v3 from Step 0.1 and follow all stated stop conditions. Do not infer or alter the ratified text.

The blank `AUTHOR:`, `DATE:` and `CHANGES TO THIS DRAFT:` lines of the draft were completed
from exactly those three values. No other character of the draft was changed. **VERIFIED**
(the draft as received had all three fields blank; the ratification message supplied them).

## Annex A — Resolved identifiers (machine-readable)

Every SHA below was resolved from Git during R1-FINAL Step 0, from command output. None was
copied from the prompt without resolution. The enforcement tests read this annex.

```text
T0_4_BASE_COMMIT: ff030d97c13c8a2a977521bf91be2aca0cbf3034
A1_COMMIT: d5513859a5315800a7b6c68711756798129ab8ee
A2_COMMIT: ca1498f75f14495bfc6ec829ef2b5ef728da2d3d
A3_COMMIT: ab9666b032a5838be3ae3a24a58aae68a4fd46b0
A4_COMMIT: 24b8e000f23d18faabd16f828bd20eeb5328ddf7
FORENSIC_COMMIT: 1db8ccddf282ec86a6785df80b04a73d680a60f9
RATIFIED_TEXT_SHA256: 2df5ff64dbbd2c2a6806468bb07cdcad6e33594fdfa6fc2ae579d68723d0eaca
```

| Identifier | Source of resolution | Label |
|---|---|---|
| `T0_4_BASE_COMMIT` | `BASE_COMMIT` at `tools/t0_4/core.py:17`; `git rev-parse --verify ff030d97c13c8a2a977521bf91be2aca0cbf3034^{commit}` succeeds; subject "T0.3A-R1: report-era coverage taxonomy extension, deterministic engine, auditor, and test suite"; it is an ancestor of the forensic commit | VERIFIED |
| `A1_COMMIT` | subject "fix(r1): restore authorized model provider fields (A1)"; parent `755c5519b9ab9484ab033685e563350a0cd0d685`; touches only `arpipe/models.py` | VERIFIED |
| `A2_COMMIT` | subject "fix(r1): restore observed script telemetry provider (A2)"; parent is `A1_COMMIT`; touches only `arpipe/triage.py` | VERIFIED |
| `A3_COMMIT` | subject "fix(r1): supply OCR exception type without raise paths (A3)"; parent is `A2_COMMIT`; touches only `arpipe/ocr.py` | VERIFIED |
| `A4_COMMIT` | subject "fix(r1): restore quarantine span suppression (A4)"; parent is `A3_COMMIT`; touches only `arpipe/store.py` | VERIFIED |
| `FORENSIC_COMMIT` | subject "docs(r1): record T0.4 guard forensics"; parent `588b6e60b20922e1f0986df492e370ac435c0747`; tree `6c26042393a95eff6b5f0096f1971a56a5babcfe`; the R1-FINAL start state | VERIFIED |
| `RATIFIED_TEXT_SHA256` | SHA-256 of the text between the fences in section 1, LF-normalised | DERIVED |

The four authorized SHAs in the ratified text (section 1) equal `A1_COMMIT` to `A4_COMMIT`
character for character. **VERIFIED**

The amendment file path `docs/identity/T0_4_AMENDMENT_01.md` does not match the glob
`docs/experiments/PHASE2.1_T0.4_AMENDMENT_*.md` (different directory and different name).
**VERIFIED**

## Annex B — D6 erratum (amendment section 7)

This annex records the correction that section 7 of the ratified text calls for. It does not
alter `docs/decisions/D6_Q6_AS_IS_IDENTITY_DECISION_v1.md`, which remains byte-identical to
its committed form (commit `755c5519b9ab9484ab033685e563350a0cd0d685`).

```text
ERRATUM to docs/decisions/D6_Q6_AS_IS_IDENTITY_DECISION_v1.md section 12
recorded_under:  T0.4 Amendment 01 (docs/identity/T0_4_AMENDMENT_01.md), section 7
erratum_date:    2026-09-26
author_ratified: Hariom Singh (2026-09-26), by ratification of the amendment

Section 12 of the D6/Q6 record ("12. T0.4 amendment") states "No T0.4 amendment required."
on the ground that no preregistered T0.4 rule references As-Is identity, baseline identity,
or system identity. That assessment did not account for the T0.4 path-level guards:

  tools/t0_4/core.py            PROTECTED_PATHS (includes "arpipe"), diffed against
                                ff030d97c13c8a2a977521bf91be2aca0cbf3034
  tests/t0_4/test_t0_4_closure_record.py
                                FROZEN_SINCE_AUDIT (includes "arpipe"), diffed against
                                33ba76acf9da13d25027e39414e724dfa1170b59

Any R1 composition that changes a file under arpipe/, as D6 section 11 anticipates, fails
those guards. This erratum corrects the scope of the section 12 assessment only. It does not
state that D6 adopted any amendment, and it does not alter D6's identity decision.
```

**Wording note (VERIFIED).** Section 7 of the ratified text quotes D6 as having recorded
`"T0.4 amendment: NO"`. That exact string does not occur in the D6 record. The D6 record
contains the heading `## 12. T0.4 amendment` (line 234) and the sentence
`**No T0.4 amendment required.**` (line 236). The two carry the same meaning. The ratified text
was not altered; this note only states which wording the repository actually contains.

## Annex C — Track-B trace (record only, non-gating)

Requested by R1-FINAL Step 0.6: find every occurrence of "the same frozen sequence" and close
variants in the T0.4 documentation, and classify each. This trace does not resolve Track B and
does not gate R1. Track B remains **UNRESOLVED / DEFERRED**.

**Search scope.** `docs/experiments/T0.4_*.md`, `tools/t0_4/`, `tests/t0_4/`, `configs/t0_4/`,
`artifacts/t0_4/`, `tools/audit_t0_4_*.py`, `tools/build_t0_4_manifest.py`. Pattern
(case-insensitive, extended regex): `same[[:space:]]+frozen|frozen[[:space:]]+sequence|same[[:space:]]+(downstream[[:space:]]+)?sequence|identical[[:space:]]+(downstream[[:space:]]+)?sequence|frozen[[:space:]]+downstream|same[[:space:]]+downstream|frozen[[:space:]]+(ARPipe|pipeline|stages)`,
plus a second pass for `downstream implementation`, `same pipeline/implementation/stages/steps`,
`frozen source/production/code/tree/system` and `production ARPipe`. No match in
`tools/t0_4/`, `tests/t0_4/`, `configs/t0_4/`, `artifacts/t0_4/`, `tools/audit_t0_4_*.py` or
`tools/build_t0_4_manifest.py` for the phrase family. The only other file in `docs/` that
contains the phrase is `docs/identity/T0_4_GUARD_FORENSICS.md`, which quotes the T0.4 text and
is not itself T0.4 documentation.

Classification key: `SPECIFIC_COMMIT` names a commit or tree; `METHODOLOGICAL` states an
invariance or procedure requirement without naming a code state; `INFORMAL` uses "frozen" as a
descriptor without naming a commit; `NOT_VERIFIABLE` cannot be determined.

### C.1 The phrase and its close variants

Path for entries 1 to 4: `docs/experiments/T0.4_ocr_benchmark_preregistration.md`.

1. **Line 15** (table row) — class **METHODOLOGICAL**. Exact text:
   `| Prohibited inference | MD&A end-page localization from an isolated page | Engine-specific downstream pipeline |`
2. **Line 17** — class **METHODOLOGICAL**. Exact text:
   "The shared link is `EngineRawOutput → CommonARPipeRepresentation`. Track A evaluates recovery from the page image. Track B evaluates how that recovery affects MD&A localization when every engine feeds the same downstream implementation."
3. **Lines 88 and 90** — class **METHODOLOGICAL** (primary occurrence). Exact text, line 88:
   "After recovery every engine uses the same frozen sequence:"
   and line 90:
   "`document profile → routing → recovery → standardized reading order → heading inventory → candidate generation → span resolution → verification → quality gate`."
4. **Line 102** — class **INFORMAL**. Exact text (first two sentences of the line):
   "Route of `vector_text` (recorded at T0.4-CLOSE as a clarification; no methodology change). In the ACTUAL_ROUTING condition `vector_text` is routed to OCR, exactly as in the frozen ARPipe triage (`arpipe/triage.py`: `PageKind.VECTOR_TEXT` is a member of `NEEDS_OCR`)."

Notes on the classes:

- Entries 1 to 3 state that every engine must feed the same downstream implementation, and
  entry 3 names the stage list. None names a commit, tree or version. Entry 3 is the primary
  occurrence. The class describes the sentence. Which code state realises "the same frozen
  sequence" is **NOT VERIFIABLE** from the repository, as the forensic record (section 9) also
  found.
- Entry 4 is about the `vector_text` route (Track A / routing), not the Track-B sequence. It
  names the file `arpipe/triage.py` and the symbols `PageKind.VECTOR_TEXT` and `NEEDS_OCR`, but
  no commit, so it is not `SPECIFIC_COMMIT`.

### C.2 Related "frozen production ARPipe" statements (not variants of the phrase)

5. `docs/experiments/T0.4_final_closure_audit.md`, **line 3** — class **INFORMAL**. Opening
   context: "... The frozen corpus, T0.4 configurations, manifests, and production ARPipe are unchanged."
6. `docs/experiments/T0.4_final_closure_audit.md`, **line 29** — class **INFORMAL**. Opening
   text: "Frozen rationale, quoted from the frozen sources: "glyphs drawn as vector paths -> OCR" (`arpipe/models.py`), ..."
7. `docs/experiments/T0.4_ocr_benchmark_preregistration.md`, **line 140** — class
   **METHODOLOGICAL**. Text: "This worktree may inspect repository metadata, ... It must not ... change production ARPipe behavior; ..." The prohibition is scoped to "This worktree".

### C.3 Result

- No occurrence is `SPECIFIC_COMMIT`. No T0.4 document names a commit or tree for the Track-B
  "same frozen sequence". **VERIFIED**
- The identity of the frozen sequence is **NOT VERIFIABLE** from the repository. This matches
  the forensic record (`docs/identity/T0_4_GUARD_FORENSICS.md` sections 3.2, 9 and 11).
- Under a literal reading that points at the T0.4 base tree, that tree could not run the
  downstream sequence end to end (forensic record section 8.1). This is the reason the
  amendment defers Track B.
- Track B is **UNRESOLVED / DEFERRED**. No Track-B execution is authorized. This trace makes no
  claim about the meaning of the phrase.
