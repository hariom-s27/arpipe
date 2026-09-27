# Phase 5 work status: what changed, what is pending, what is on hold

**Date:** 2026-09-27 (late evening IST). **Working line:** `phase5-a1` (`e1803fc`) →
`phase5-b-intake` (`a286de6`). **`main` is on hold:** nothing was pushed to it, merged
into it or reconciled with it.

## 1. Changed in this session (each on its own branch; none merged)

| Branch | Commit | What | Checks |
|---|---|---|---|
| `phase5-a1b` | `3eb1041` | **P5-A.1b errata.** Adds `PILOT_PLAN_v0_1_1.md` (only §3 replaced) and "Errata v0.1.1" in `CHANGELOG_v0_1.md`. Core set of 4 exact conditions; 3 extra conditions marked AUTHOR_CHOICE_PENDING. No selection computed | Tests equal the base (423 passed; the 2 known `live_store` failures); `PILOT_PLAN_v0_1.md` SHA-256 unchanged (`f842b219…2b08`); doc-hash check 0 failures |
| `phase5-annotation-tool` | `c0fa4c9` | **P5-T tool.** `tools/phase5/annotator/`: core, tkinter form, `export_role.py`, `make_bundle.py`, bundle README, `TOOL_NOTES.md`. Plus 34 synthetic tests and 2 exact allowlist patterns | 457 passed (= 423 + 34; same 2 environment failures). Headless GUI run: bundle → form → refused while the title list is unfrozen → seal → export → lock |
| `phase5-research-r1` | this commit | `research/BLOCKER_RESEARCH_R1_2026-09-27.md` (title rules T1–T7, viewer pin), this status file, and a log entry | Docs only |

## 2. Can proceed now (independent of the blockers)

| Item | Owner | Note |
|---|---|---|
| Review and open PRs for the three branches above, **into the Phase 5 line, not `main`** | Author | Suggested base: `phase5-a1` for `phase5-a1b` / `phase5-annotation-tool`; `phase5-b-intake` for `phase5-research-r1` |
| Human MD&A title review (worksheet / review page) | Author | Already under way on the author's PC. Nothing in the repo yet |
| Record the P5-A.1b extension choice (add `devanagari_candidate` / `scanned` / `ocr_layer_candidate` or not) | Author | One line in `PILOT_PLAN_v0_1_1.md` §3 |
| Review the six P5-T design choices (`TOOL_NOTES.md`) | Author / rules reviewer | All reversible |

## 3. Blocked pending research or decision

| Item | Blocked on | Research status |
|---|---|---|
| Freeze the blind title list | Human title review + rules decisions T1–T5 | **Evidence and options ready** (`research/BLOCKER_RESEARCH_R1_…` §2). T6 and T7 need no decision |
| Schema flag for MD&A embedded in a non-Directors'-Report section (T2) | Author decision on T2 option A | Gap identified; schema change deferred to the method revision |
| Viewer pin (product, version, setting) | Method freeze | **Recommendation ready:** Acrobat Reader, "Use logical page numbers" off (§3) |
| A1–A5, C1-D1 signatures | Author | No research needed |
| K1 answer (repo-side Claude logs during P5-B) | Author | Only the author knows |
| `INE00LO01017_2015` (2-page stub candidate in the pilot pool) | Author's PC (PDF not in cloud) | Needs a visual check before the pilot draw |
| P5-C pilot (Phase 6) | Title list frozen + tool accepted + selector freeze/commit-reveal | Cannot start before those |
| Interval method | Author, before HOLDOUT scoring | Not a pilot blocker; recommendation unchanged |
| Q10 climate recipe (C4, B7) | Governance deferral | On hold by design |

## 4. Completed earlier: verification status

| Item | Status | How |
|---|---|---|
| P5-B intake pack (`898e248`) | **Re-verified.** `build_intake_pack.py` re-run gives byte-identical output (clean `git status`) | This session |
| `DOCUMENT_WORKSHEET_v0_2_2.csv` | **Re-verified.** The copy the author re-sent is byte-identical to the repo (`0d05c6d7…66b4`); all reviewer columns are still empty | This session |
| Phase 5 line tests | **Re-verified.** `e1803fc` and `a286de6`: 423 passed, 17 skipped, 3 xfailed, 2 environment failures | This session |
| `make_review_page.py` (`32d090a`) | Compiles. **Not re-run**: its inputs (`output\p5b3`) are on the author's PC | Needs P5-B.3 output or the review CSV |
| P5-B.3 pre-fill (`P5_B3_PASS`) | **Not independently verifiable here.** Outputs aren't in the repo | Upload `MDNA_TITLE_REVIEW_v0_1.csv` + p5b3 hashes to verify |
| `origin/phase5-gold-method-v01` alias of `e143222` | Known state; no action (recorded in `CHANGELOG_v0_1.md`) | — |

## 5. On hold deliberately (and why)

- **`main` reconciliation.** 11 `arpipe/` files drift from the R1 pin, and there are 10
  test failures on `main`. The instruction was to keep `main` on hold, so none of this
  was touched.
- **`PIPELINE_STATUS.md` and the `arpipe/CLAUDE.md` bug list are stale.** They are on
  `main` / frozen paths. Record only.
- **No methodology change was made.** Every change is a new file or a draft errata on a
  side branch, and v0.1 files are byte-identical. The P5-A.1b extension, the T1–T5
  title rules, the T2 schema flag and the viewer pin all wait for the author.
