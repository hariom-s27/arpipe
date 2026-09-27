# ARPipe research execution log

**Read this first in every new chat.** Newest entry is at the top. Each entry has four parts: **Did**, **Found/decided**, **Remains**, **Next**.
- Detailed context: `claude/ARPIPE_MASTER_CONTEXT.md` in the "hari" project.
- Governance: `docs/governance/CURRENT_DECISIONS.md`.

## Standing rules (short)
- **Phase 5 base:** Phase 5 work starts from `origin/phase5-a1` (`e1803fc`). `main` still differs in 11 `arpipe/` files. No HOLDOUT content anywhere.
- **Blind work:** blind title work runs only in `D:\gold_blind`, which is not a git repo. There, use Python by full path (`C:\Program Files\Python314\python.exe`), no hidden or base64 code, and write only to that run's output folder. Hashes and counts come only from code output.
- **Which tool for which task:**

| Task | Best tool |
|---|---|
| Multi-step builds and audits with strict rules | Codex, GPT-5.6 Sol Extra High/Ultra; or Claude Code Opus |
| Verification, repo intake, analysis, prompt writing, small mechanical tools | This Claude chat. It can fetch and push the repo, but can't reach `D:\` |
| Running an already-written, hash-pinned script | Gemini 3.8 Flash (Antigravity) is OK |
| Reading, judging or rewriting evidence | Not Gemini Flash |

---

## 2026-09-27 (night): PR cleanup done
- **Did:** the author used `gh`. PR #42 (last log entry) was merged. #37 and #39 were closed. #36 and #40 were auto-marked MERGED (their content arrived via #41).
- **Found:**
  - `main` = `b8018fe`, no open PRs. It holds the stronger P5-T, P5-S, the interop test and the log. No conflict markers.
  - Tests: 545 passed; 10 failures, the same pre-existing main-drift set.
- **Remains:**
  - P5-C custodian builder (Codex, still running; no commits yet, so no PR possible yet).
  - SAP OPEN-items options memo (after custodian).
  - Title review CSV.
  - The P5-A.1b "7 vs 4" answer. Main currently has 4 + 3 pending.
- **Rule:** only open the PRs this chat lists as ready. Overlapping branches are combined into one PR branch first.

## 2026-09-27 (night): PRs merged to main; PR-ready branch
- **Did:**
  - The author merged PRs #33 (drift), #35 (b-intake), #34 (the **Codex** P5-T) and #38 (`phase5-a1b`, the 4 + 3-pending version) into main.
  - PR #39 (`phase5-a1b-codex`) now conflicts and is not merged.
  - This chat built `pr-phase5-to-main` (a fast-forward from main). It brings in `phase5-integration`: scoring, the interop test, the log, and the other chat's P5-T (`c0fa4c9`), which **replaces** the Codex P5-T files (`app.py`, `core.py`, the committed zip, its test).
  - P5-C prep (custodian builder) is running in Codex from `phase5-integration`.
- **Found:**
  - `main` (and this branch) show 10 test failures. They are the **pre-existing main drift** (see the drift report); none are new.
  - This branch: 545 passed. Main: 514 passed.
  - Main's tests also rewrite `reports/annexure_audit.*`; restore those files with `git checkout -- reports/`.
  - The Phase 5 line (`phase5-integration`) was NOT merged with main, so its `arpipe/` stays identical to R1.
- **Decide (author):**
  - Open and merge PR `pr-phase5-to-main → main`.
  - Close PR #39 unless the answer is "yes 7" (a follow-up errata would then be needed).
  - The drift option for main.

## 2026-09-27 (night): integration branch
- **Did:**
  - The author pushed the drift report (`main-drift-diagnosis`, `9c92aad`).
  - This chat built `phase5-integration` = `phase5-b-intake` + `phase5-annotation-tool` + `phase5-scoring` + `main-drift-diagnosis`. It resolved the one allowlist conflict (keeping both entries).
  - Added `tests/test_phase5_scoring_interop.py`: records made by the annotator core, through its canonical bytes, are accepted by the scoring engine.
- **Found:**
  - Full pytest: 471 passed, 17 skipped, 3 xfailed, 2 environment failures. That is base 423 + 34 + 12 + 2.
  - The annotator and the scoring engine agree on the record format (viewer 1-based pages are stored 0-based).
- **Remains:** the P5-A.1b choice, then merge the chosen branch; one PR `phase5-integration → main`; the title review; the SAP OPEN items before any scoring.

## 2026-09-27 (late evening): P5-S scoring and main-drift diagnosis
- **Did (Codex, GPT-5.6 Sol Extra High):**
  - P5-S → `phase5-scoring` (`c220017`). This chat re-tested it: base + 12 tests.
  - Main-drift diagnosis report written (`docs/decisions/MAIN_DRIFT_DIAGNOSIS_2026-09-27.md`); the author pushes it.
- **Found:**
  - P5-S implements SAP §1–§8.
  - OPEN, not implemented:
    - the §7 interval method;
    - the §8 empty/empty gap-set Jaccard;
    - the direction of signed A/B differences;
    - the non-comparable count definitions;
    - the issuer map (supplied as an input);
    - the prediction CSV layout (documented by the CLI, not the SAP).
  - `main` differs from Phase 5 in 11 `arpipe/` files. `universe.py` (`ac0301d`, 17 Sep, a direct commit to main, −176 lines) **can change output**. `models.py`, `cli.py` and `fetch.py` are UNSURE.
  - The `origin/main` archive gives 495 passed, 12 failed (some of it environment).
- **Decided:** HOLDOUT must run on the R1 identity, not `main`. Resolving the drift on `main` is an author decision; the options are in the report.
- **Remains:** push the drift report; author decisions (P5-A.1b 7 vs 4; drift option; SAP OPEN items before scoring); the title review.

## 2026-09-27 (late evening): duplicate versions compared
- **Did:**
  - The Codex versions were pushed under their own names: `phase5-a1b-codex` (`9ec7732`) and `phase5-annotation-tool-codex` (`77443b7`).
  - A mis-push (from the parent folder, into the thesis repo) was deleted by the author. ARPipe was untouched.
  - Tested both P5-T versions in clean worktrees here.
- **Found:**
  - **P5-T:** `phase5-annotation-tool` (`c0fa4c9`, other chat) gives base + 34 tests.
    - It has a deterministic bundle and an export lock that stops new records once the role is exported.
    - It refuses to seal records while the title list is unfrozen.
    - It documents its design choices, and it commits no built files.
  - The Codex version gives base + 17 tests and commits `annotator_bundle.zip` (a build artifact).
  - **P5-A.1b:** the versions differ only in the author choice (4 exact conditions + 3 pending, vs all 7). Both are otherwise correct and the tests equal the base.
- **Decided (proposed):**
  - Keep `phase5-annotation-tool` (`c0fa4c9`). Keep the Codex P5-T branch as reference only; do not merge it.
  - For P5-A.1b, merge the version that matches the author's answer ("yes 7" → `phase5-a1b-codex`; "only 4" → `phase5-a1b`).
- **Rule:** every command block starts with `cd <folder>` and `git remote get-url origin` before any push.

## 2026-09-27 (late evening): duplicate work detected; lines merged
- **Did:** this chat found that another Claude session (`session_01WQKd…`) had already pushed P5-A.1b (`3eb1041`), P5-T (`c0fa4c9`) and research R1 (`22c870a`). It did this while Codex was running the same P5-A.1b and P5-T tasks. `phase5-b-intake` was fast-forwarded to `22c870a`, so there is one log line.
- **Found:**
  - The Codex P5-A.1b push was rejected (non-fast-forward) because the remote branch already existed. Nothing was overwritten.
  - The pushed P5-A.1b is careful: a core set of 4 exact conditions, with 3 extensions marked AUTHOR_CHOICE_PENDING.
- **Decided:**
  - Use the pushed P5-A.1b and P5-T.
  - Stop the duplicate Codex runs and don't push them.
  - Keep the Codex main-drift diagnosis and P5-S scoring; they are unique.
- **Rule from now on:** one coordinating chat at a time. Every chat reads this log first and checks `git ls-remote` before starting a task.

## 2026-09-27 (late evening): independent tasks done in parallel; blocker research R1
- **Did (Claude Code session; nothing on `main`):**
  - P5-A.1b errata → `phase5-a1b` `3eb1041`.
  - P5-T annotation tool → `phase5-annotation-tool` `c0fa4c9` (34 synthetic tests, headless GUI run).
  - Blocker research R1 + status record → `phase5-research-r1`.
  - Re-verified: the intake pack is reproducible; the worksheet the author re-sent is byte-identical; the test baseline is 423 passed.
- **Found:**
  - The P5-A.1b mapping has only 4 exact one-to-one conditions; `devanagari_candidate`, `scanned` and `ocr_layer_candidate` are author choices.
  - The regulation (Clause 49 IV(F), LODR Reg. 34(2)(e)) supports treating spelling variants as one title and supports embedding MD&A in the Directors' Report. It also treats MD&A and the Corporate Governance report as separate reports.
  - Schema gap: no flag for MD&A embedded in a non-Directors'-Report section.
  - Viewer: Acrobat's "Use logical page numbers" setting can be pinned; SumatraPDF has no such setting.
- **Remains:** the author's title review; decisions T1–T5; the P5-A.1b extension choice; the P5-T design review; the viewer pin; A1–A5; K1; a visual check of `INE00LO01017_2015`.
- **Next:** see `docs/phase5/WORK_STATUS_2026-09-27.md` §2–3.

## 2026-09-27 (evening): parallel tasks set up; log moved
- **Did:**
  - Built the review page on the author's PC: 60 documents, 429 page images. The author is now reviewing.
  - The log moved to `docs/phase5/` (`06c7357`), because `docs/` at the root breaks the path allowlist test (`test_phase2_1_semantic_conformance`).
  - Full pytest on `phase5-b-intake` equals the base `e1803fc`: 423 passed, 17 skipped, 3 xfailed, and 2 environment failures (the cloud copy has no `live_store`).
  - Wrote parallel prompts for P5-A.1b (pilot-token errata) and P5-T (annotation tool). Each runs in its own worktree and window.
- **Found:** the P5-A.1b problem is confirmed from the repo. The §3 tokens don't match the source's 17 `condition` values; only `legacy_font_candidate` matches.
- **Remains:** the author's title review, P5-A.1b, P5-T, A1–A5 signatures, and the K1 answer.
- **Next:** the author reviews; in parallel, Codex runs P5-A.1b and P5-T. Then open PRs.

## 2026-09-27 (evening): P5-B.3 MD&A title pre-fill + review tool
- **Did:**
  - Codex ran P5-B.3 in `D:\gold_blind`. It copied the MD&A title lines by code from each PDF's text layer (PyMuPDF 1.28.2), rendered the pages, and pre-filled the 60-document worksheet.
  - This chat added `docs/phase5/evidence/p5b/review_tool/make_review_page.py`. It builds an offline review page: pre-fill, all candidate lines, page images, a link to open the PDF, answers that autosave, and "Download CSV". It was tested in a headless browser.
- **Found:**
  - `P5_B3_PASS`. V1–V7 PASS: 94/94 pre-filled titles found verbatim on their page; reproducible; 0 changes outside `output\p5b3`.
  - 37 documents have a TOC and a body title, 20 only a body title, and 3 have no hit: `INE004C01028_2017`, `INE004E01016_2018`, and `INE00FF01025_2015` (the SEBI letter).
  - Flags: MENTION_LIKE 24, MANY_HITS 13, HINT_DISAGREES 9, NO_TEXT_LAYER 0.
- **Remains:** a human confirms or corrects all 60 (no-hit and flagged documents first), then decides the title rules, then freezes the blind title list.
- **Next:** the author runs the review tool and fills in the answers, then sends `MDNA_TITLE_REVIEW_v0_1.csv`.

## 2026-09-27 (evening): P5-B intake into the repo
- **Did:**
  - Package committed as `06261d1` (PR #32 → main `2fb2718`).
  - This chat re-verified it independently and added `intake/` (`898e248`, branch `phase5-b-intake`). Contents: field-format audit, 216 key-row candidates, 124 quoted strings, and the 60-document worksheet.
- **Found:**
  - The package is intact (25/25 hashes; 3,215 + 1 rows; 60 documents; 259 evidence rows / 146 PNGs).
  - **The ledger's heading fields are mostly AI notes, not verbatim headings.** Clean: EQUIVALENT 24/150, CONDITIONAL 0/66. Some key rows are *mentions*. The notes contain page references.
- **Decided:**
  - The ledger is structurally sound but **not** a title record, and must never go to annotators.
  - The old catalog is a draft only.
  - Take the pre-declared fallback: TOC + section openings, human-verified.
- **Remains:** the human title review (see above).

## 2026-09-27 (day): P5-B.2.2 clean rebuild (attempts 1–6)
- **Did:** a series of Codex runs in `D:\gold_blind`.
  - Attempt 1 was a re-typed hash.
  - Attempt 2: the output folder wasn't empty.
  - Attempt 3: the P5-B.2 chat report had wrong hashes for 4 v0.2 files. Fixed by using v0.2's own record (K-I).
  - Attempt 4 started inventing a selection rule and was stopped.
  - Attempt 5: a catalog entry couldn't be traced to the ledger.
  - Attempt 6 (prompt v6): `P5_B22_PASS_WITH_REVIEW_ITEMS`.
- **Found:**
  - Frame-status row split out (3,215 + 1).
  - Catalog tags 21/12/47 (+1); the earlier 24/11/45 and 28/6/46 were wrong.
  - Visual coverage 416/1,610 = 25.84%.
  - Catalog vs ledger: 29/80 titles with no match, 11 conflicts.
- **Learned (process):**
  - Open `D:\gold_blind` in its own VS Code window; the extension uses the window's folder.
  - Deactivate the thesis venv.
  - Never rename folders while a run is live.
  - Hashes come only from files.

## 2026-09-27 (morning): P5-A.1 and early P5-B
- **Did:**
  - P5-A.1: Gold method v0.1 (`e1803fc`, 425 tests passed, merged via PR #31).
  - P5-B v0 → v0.1 → v0.2: the isolated AI title reading.
  - v0.2.1 FAILED: 0-byte files.
- **Open items:**
  - K1 answer: did any P5-B work run in a Claude Code session in the thesis folder?
  - P5-A.1b pilot-token errata.
  - A1–A5 author signatures.
  - P5-T annotation tool.
