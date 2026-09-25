# D6 / Q6 — As-Is ARPipe Identity Decision (v1)

`recorded_on`: 2026-09-24
Decision date supplied by author: **not supplied** (recorded on the date above)
Recorded from worktree `d6-q6-identity-decision`, branch `d6-q6-identity-decision`,
START_SHA `50769ffc6b5ec75919ddbab523db49cc1d80c223`.

---

## 1. Purpose

Record the author's resolution of D6 / Q6 — *"Which identity, if any, is intended
'As-Is ARPipe'?"* — which `docs/phase3/PHASE3_DECISION_SHEET.md` leaves blank at
its `**AUTHOR CHOICE:**` field (line 109), and on which R1 halted.

This record establishes **identity only**. It does not make the system runnable,
does not repair production code, and does not create a baseline.

---

## 2. AUTHOR DECISION — VERBATIM

The following is the only verbatim author wording on D6 that exists in the
repository. It is quoted from `docs/phase4/PHASE4_B1_B8_TRIAGE.md` (row D6 of the
supplied decision table), where Phase 4 records it as supplied directly to that
task and treated as authoritative:

> "The coherent historical operational ARPipe system immediately before the
> specific change being evaluated… If the baseline cannot be established
> coherently, no baseline-relative improvement claim is made."

Related verbatim author wording, same source (row D2):

> "A baseline-relative methods claim is retained only if the As-Is comparator is
> later established coherently."

**No new verbatim author prose was supplied for this task.** The author resolved
the remaining choices through structured selection; those selections are recorded
in §3 and are explicitly **not** presented as author prose.

---

## 3. AUTHOR SELECTION (this task, structured — not verbatim prose)

The author was presented with unranked, evidence-supported options and selected:

| Question | Author's selection |
|---|---|
| Which As-Is identity should D6 record? | **Adopt the reconstructed 2026-09-17 executed state** — Phase-4 committed production code **union** the E0 provider half, as the tree that actually executed. |
| May C2 baseline-relative claims rely on it? | **Not yet — verify drift first.** C2 stays CONDITIONAL-unmet until further evidence bounds the 2026-09-17 → 2026-09-20 drift in `models/ocr/store/triage`. The identity is adopted for R1 runnability purposes only. |
| Does R1 get authorization to build it as one commit? | **Decide in R1, not here.** The identity decision is recorded; the exact file-level composition is left for the next R1 task to propose against this decision, under its own authorization gate. |

No option was labelled best, correct, preferred, strongest, safest or recommended,
and no ranking was presented.

---

## 4. Selected identity

**The reconstructed 2026-09-17 executed state.**

It has **no single commit SHA**. It is defined by two components:

| Component | Source | Exact reference |
|---|---|---|
| Consumer half (committed) | Phase-4 production code | `50769ffc6b5ec75919ddbab523db49cc1d80c223`, `arpipe/` tree `1d63ab4989173b199dcd181f47f2a566929d9bef` |
| Provider half (preserved) | E0 repository-safety snapshot | `dea3ae5399be50872768c8703c878c907ee6818b` (branch tip `e8517ee57365fc0799052d696f851fc25906a6b5`), `arpipe/` tree `48faf1a372e720e8bf941f1a4359a62430d0b133` |

The executed tree itself was: commit `0fb8cbf6d932f4190bdfe3b2a1fecf62170cca14`
plus uncommitted working-tree modifications, as recorded by the run manifest.

---

## 5. Repository evidence supporting the identity — REPO-VERIFIED

**5.1 The execution is documented.** `reports/pm1_baseline.json` is a run manifest:

| Field | Value |
|---|---|
| `task` | `PM1 M1.1 - immutable pre-implementation baseline` |
| `timestamp_utc` | `2026-09-17T07:13:12Z` |
| `git_sha` | `0fb8cbf6d932f4190bdfe3b2a1fecf62170cca14` |
| `git_worktree_dirty` | `true` |
| `corpus_document_count` | 194 |
| `grade_distribution` | `{failed: 12, high: 42, low: 53, medium: 85, quarantine: 2}` |
| `accepted_count` / `rejected_count` | 127 / 67 |

Its `note_on_git_state` records: *"The working tree already carried substantial
uncommitted work (P34 wrong-language quarantine, P-B7 state.py, script-map
telemetry, etc.) before PM1 started, on top of commit 0fb8cbf (P33)."*

**5.2 The provider half demonstrably executed.** The distribution contains **2
documents graded `quarantine`**, which requires `Confidence.QUARANTINE` — absent
from Phase-4 `models.py`, present in `dea3ae5`.

**5.3 Phase-4's own `pipeline.py` ran in that tree.** `reports/pm1_per_page_orphan.json`
and `reports/pm1_regression_result.json` record the after-run: 194 documents
compared, **0** changes of any kind (`total_documents_with_any_diff: 0`), with
`implementation.files_changed` = `verify.py`, `textlayer.py`, `pipeline.py`,
`cli.py`. That `pipeline.py` is byte-identical to Phase-4 HEAD's
(`66ecf6cfa0d8…`) and cannot execute without `profile.script_map`. The script-map
provider was therefore live on 2026-09-17.

**5.4 The snapshot is a faithful capture.** E0 independently recorded pre-E0 dirty
SHA-256 values in `docs/experiments/E0_REPOSITORY_SAFETY.md` §2.3 — `models.py`
`E40FAA0B467C…`, `ocr.py` `AFFEC70F2533…`, `store.py` `9F5A1B8EE3F9…`,
`triage.py` `351A4AAC1EFC…` — all matching `dea3ae5`'s blobs.

---

## 6. Historical provenance — root cause

At `0fb8cbf` (P33) **none** of the four symbols exist anywhere in `arpipe/`; the
tree is self-consistent. P34, script-map, P-B5 and `write_span` all originated as
**uncommitted** work on top of it.

`c9d71bb` (P-M1, parent `0fb8cbf`) then committed **5 of the 14 modified tracked
files** — `arpipe/cli.py`, `arpipe/pipeline.py`, `arpipe/textlayer.py`,
`arpipe/verify.py`, `arpipe/tests/test_pm1_orderqc.py` — and left `models.py`,
`ocr.py`, `store.py`, `triage.py`, `segment.py` uncommitted.

**The root cause of the R1 failure is therefore a partial commit that split one
coherent working implementation across the commit boundary, committing the
consumer half and leaving the provider half behind.** `dea3ae5` later preserved
that provider half on a separate branch.

Production code is byte-identical from `c9d71bb` through `50769ff`; the only
`arpipe/` change between them is the added P-M2 test
`arpipe/tests/test_pm2_pagegrain_native_vs_ocr.py`.

### Symbol trace — REPO-VERIFIED

| Symbol | Introduced | In Phase 4 lineage? | Historical-use evidence | Scientific-behaviour implication | Identity consequence |
|---|---|---|---|---|---|
| `profile.script_map` | uncommitted on `0fb8cbf`; provider only in `dea3ae5` | consumer call site only (`pipeline.py:167`) | after-run completed 194 docs with this `pipeline.py` | adds per-page script / legacy-font telemetry | restoring it imports E0's `triage.py` computation |
| `Confidence.QUARANTINE` | same | consumer only (`pipeline.py:385`) | **2 documents graded `quarantine`** | P34 wrong-language gate outcome | restoring it imports E0's `models.py` enum |
| `ocr_mod.OcrEngineUnavailable` | same | consumer only (`pipeline.py:396`; comment `cli.py:260`) | present in tree; no firing observed in the manifests | reclassifies `mda_not_located` → `ocr_engine_unavailable` | restoring it imports E0's `ocr.py` class **and** its raise behaviour |
| `write_span` | same | consumer only (`pipeline.py:392`) | implied by the 2 quarantined rows | suppresses `mda.txt` for quarantined rows (P34) | restoring it imports E0's `store.py` parameter |

### Correction to the R1 blocker report

`docs/identity/R1_RUNNABLE_IDENTITY_BLOCKER.md` states that the quarantine branch
is unreachable because `verify.grade()` returns only high/medium/low. **That is
incorrect.** `arpipe/pipeline.py:325` assigns `grade = "quarantine"` directly on
the P34 gate, overriding `verify.grade()`, and Phase-4 `verify.py` does define
`looks_like_wrong_language` (line 586) and `page_has_bilingual_heading` (line 642).
`Confidence.QUARANTINE` is live, load-bearing production logic. The 2 quarantined
documents in the 2026-09-17 run confirm it executed.

---

## 7. Candidate comparison — existence ≠ execution ≠ evaluated ≠ canonical

| Candidate | SHA | Exists? | Ever executed? | Historical evaluated execution? | Formally adopted? | Status |
|---|---|---|---|---|---|---|
| P33 / pre-change main | `0fb8cbf6d932f4190bdfe3b2a1fecf62170cca14` | Yes, coherent | No evidence as a clean tree | No | No | PROVENANCE UNCERTAIN |
| P-M1 | `c9d71bb127fcc46d690a8fbd9e5088b7049b6c05` | Yes | No — `AttributeError` at `pipeline.py:167` | No | No | NOT A PLAUSIBLE AS-IS IDENTITY |
| START / P0b | `24520ce623037fde7c3b0a9d0d4e5f8fc5618831` | Yes (same `arpipe/` tree as Phase 4) | No | No | No | NOT A PLAUSIBLE AS-IS IDENTITY |
| Phase 4 | `50769ffc6b5ec75919ddbab523db49cc1d80c223` | Yes | No | No | No | NOT A PLAUSIBLE AS-IS IDENTITY |
| **Executed 2026-09-17 tree** | no single SHA | Only as two halves | **Yes — 194 docs** | **Yes** | **Yes, by this record** | **SELECTED** |
| E0 saved checkout | `e8517ee57365fc0799052d696f851fc25906a6b5` (code `dea3ae5…`) | Yes | Not as a commit | Overlaps; unproven | No — "not promoted to canonical" | RECOVERY SNAPSHOT |
| Step0A | `0d39395dfb81c987e05546471fbb80947c8fdce8` | **Absent from this repository** (`fatal: bad object`) | Unknown | Unknown | No — "accepted canonical SHA null" | CURATED / UNADOPTED |

---

## 8. What this decision ESTABLISHES

1. The intended As-Is ARPipe system is the **coherent operational tree that
   executed on 2026-09-17**, not any single existing commit.
2. Phase-4 / START / P-M1 production code is **not** an As-Is identity on its own —
   it is the consumer half of a partial commit.
3. The E0 snapshot is **not** adopted as the As-Is identity. It is adopted only as
   the **preservation source** for the provider half.
4. Step0A is **not** the As-Is identity.
5. R1's halt was correct, and R1 now has a recorded identity to work against.

## 9. What this decision does NOT establish — LIMITATION

1. **It does not establish byte-identity** between the E0 provider half
   (2026-09-20) and the provider half that executed (2026-09-17). The trees
   demonstrably drifted: `arpipe/patterns.py` is listed modified in the 09-17
   porcelain and clean in the 09-20 inventory, and no record states whether
   `models.py`, `ocr.py`, `store.py` or `triage.py` changed in that window.
   **This is the irreducible provenance limit of this decision.**
2. It does not establish that the 2026-09-17 run is *the* evaluated execution for
   any particular claim — only that it is a documented operational execution.
3. It does not fix "the specific change being evaluated", which the author's
   verbatim D6 wording makes As-Is relational to. That remains open.
4. It does not certify the runtime environment, external binaries, model revisions
   or package versions of the 2026-09-17 run.
5. It does not adopt, validate or authorize any E0 content beyond the four
   definitions' provider role — notably not `state.py`, `MDASpan.body_script`,
   `PageProfile.script_meta`, or the P-B5 OCR raise behaviour, each of which
   changes behaviour and none of which is authorized here.
6. It makes no B1–B8, C1 or C4 decision, and does not resolve D6's sibling
   questions.

## 10. Effect on C2 — IMPLEMENTATION CONSEQUENCE

Per the author's selection, **C2 remains `RETAINED — CONDITIONAL, gate unmet`**, as
`docs/phase4/PHASE4_B1_B8_TRIAGE.md` line 67 already records.

- No baseline-relative improvement claim may be made from this identity yet.
- The identity is adopted **for R1 runnability purposes only**.
- The C2 gate opens only when further evidence bounds the 2026-09-17 → 2026-09-20
  drift in `models.py`, `ocr.py`, `store.py`, `triage.py`.
- Candidate evidence for that bounding, preserved on disk and **not inspected in
  this task**: `pm1_after_run/`, `pm1_baseline_run/`, `pm1_after_run.log`,
  `pm1_baseline_run.log` (recorded in `E0_REPOSITORY_SAFETY.md` §3.1–3.2).

## 11. Effect on R1 — IMPLEMENTATION CONSEQUENCE

R1 is authorized to establish a runnable identity **against this decision**, and is
**not** authorized to choose the file-level composition on its own initiative — per
the author's selection, that composition is to be proposed by R1 under its own
authorization gate.

R1 must therefore, in a later task:

1. Propose the exact file-level composition (which provider files, verbatim or
   subset) and obtain authorization before applying it.
2. Note that `arpipe/triage.py` remains on the R1 §7 STOP list; supplying
   `script_map` from `dea3ae5` changes it, so that requires explicit authorization.
3. Note that any composition drawn from `dea3ae5` imports behaviour changes listed
   in §9.5 unless deliberately excluded.
4. Address the independent blocker recorded in the R1 report:
   `tests/test_phase2_1_semantic_conformance.py::test_historical_immutability_strict_allowlist`
   asserts zero changed paths under `arpipe/` and already fails at the untouched
   Phase-4 commit. An authorized allowlist amendment is required.

No repair, no copying of definitions, and no modification of `arpipe/` was
performed in this task.

## 12. T0.4 amendment

**No T0.4 amendment required.** No preregistered T0.4 rule references As-Is
identity, baseline identity, or system identity; the single `baseline` token in
`configs/t0_4/engine_registry.json` is the OCR engine descriptor
`"engine_type": "local OCR baseline"`, unrelated to this decision.

## 13. Reopen trigger

This record is reopened if any of the following occurs:

1. Evidence bounding the 2026-09-17 → 2026-09-20 provider drift is produced
   (opens or closes the C2 gate).
2. "The specific change being evaluated" is fixed, making the relational D6
   criterion resolvable to a different state.
3. The Step0A object `0d39395…` is recovered into this repository.
4. Any 2026-09-17 run manifest is found that contradicts §5.
5. The author writes verbatim D6 wording into
   `docs/phase3/PHASE3_DECISION_SHEET.md`, closing provenance gap PG-1.

## 14. References to historical records

Read-only; none modified by this task.

| Record | Relevance |
|---|---|
| `docs/phase3/PHASE3_DECISION_SHEET.md` §"D6 / Q6" (heading line 83; blank `AUTHOR CHOICE:` line 109) | The unresolved question this record answers |
| `docs/phase3/PHASE3_CLAIMS_SCOPE_RESEARCH.md` lines 66, 141–142, 146 | Candidate comparison; "No recovery snapshot promoted to canonical"; "accepted canonical SHA null"; the four-defect static evidence |
| `docs/phase4/PHASE4_B1_B8_TRIAGE.md` lines 19, 23, 33–40, 67 | Verbatim author D6/D2 wording; provenance gap PG-1; C2 conditional status |
| `reports/pm1_baseline.json` | 2026-09-17 execution manifest, porcelain, grade distribution |
| `reports/pm1_per_page_orphan.json`, `reports/pm1_regression_result.json` | After-run, 194 documents, zero diffs |
| `docs/experiments/E0_REPOSITORY_SAFETY.md` §2.3, §3.1–3.2 | Pre-E0 dirty-tree SHA-256 inventory; preserved run directories |
| `docs/identity/R1_RUNNABLE_IDENTITY_BLOCKER.md` (untracked, worktree `runnable-identity`) | R1 halt report; contains the reachability error corrected in §6 |

---

## 15. Label key

- **AUTHOR DECISION** — §2 (verbatim, Phase 4 source) and §3 (structured selections, this task).
- **RESEARCH / REPOSITORY EVIDENCE** — §5, §6, §7.
- **IMPLEMENTATION CONSEQUENCE** — §10, §11, §12.
- **LIMITATION** — §9, and §5's drift boundary.

No researcher interpretation appears in §2. §3 records structured selections and is
not presented as author prose.
