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

## 2026-09-29 (late afternoon): pilot drawn; A/B folders built and zipped
- **Did:**
  - Title list v0.2 frozen for the pilot (decisions §9.5; PR #69, main `fcc1ae7`).
    - Git blob `9f01105e714e8c32cb6a076472cebcb00433145b`.
    - LF SHA-256 `0c0caa07c91014228b299da88343a37e12a949d82ee3f11bedcfc5f3c5d9e39e`, which equals the local hash.
  - `.exe` rebuilt after the F7 merge, from main `bed1f46` (Python 3.14.3, PyInstaller 6.22.3, jsonschema 4.26.0).
    - SHA-256 `18213fb9d195ee273731c2135f9caac9d5cf07d9aa070767dd38ead7dd1b1604`.
    - It supersedes `44DD37BC…`.
  - Pilot build run **once** from worktree `phase5-pilot` (detached at `fcc1ae7`), output in `D:\gold_blind\pilot`.

    | Output | SHA-256 |
    |---|---|
    | `pilot_bundle.zip` | `a83e2182bf5a4414f8632f0562d5cde107a652206051e3015fcfe033bfe18cf0` |
    | `BUNDLE_MANIFEST.json` | `f588c7d8773dd6ba4411c9ef24305489868040be91e45845df022a8fc0963c07` |
    | `DRAW_REPORT.json` | `278bdec919c3f144fed765da5095a3402ef0d7eae018654651dd143acff222cf` |
    | `PILOT_ROSTER.csv` | `b4f1d35dd90f784a775efe4561e8410d7b434bead889656b91747c70dd4f9fdb` |
    | `RETEST_ROSTER.csv` | `91ff25208268a7e7b2a8f4132b4b157e56ff255d267cb2124d7d034f63099ec4` |
    | `WORKSPACE_MANIFEST.json` | `51238b4cfce4b8b6f3b91728574165f40ea46a2e81979240c05f18752f3c4a32` |

    - Draw: 10 pilot documents / 5 issuers, 6 retest documents / 3 issuers.
    - 10 PDFs staged and hash-verified.
  - Two annotator guides (markdown) added to both workspaces; project `claude/round4/`.
    - `HOW_TO_ANNOTATE_GUIDE.md`: the steps.
    - `FORM_FIELD_GUIDE_WITH_EXAMPLE.md`: every field, with an **invented** example report. Real pilot documents are never used as examples.
  - Final zips (the guides are included; `records` is empty in both):

    | Zip | SHA-256 |
    |---|---|
    | `ANNOTATOR_A.zip` | `3ce340f82b0a1c714e6592fb4d18f6f6f3a3f97860d7883222f752b07bfbacb4` |
    | `ANNOTATOR_B.zip` | `25276ff719efe5c434f3b132547d5dffd89db2faa2a9dfef0691e0c0a621c770` |

    Earlier zips without the guides are superseded.
  - Test in the B workspace: role shown, PDF verified (69 pages), nothing sealed.
- **Decided:**
  - Keep the Windows `.exe`; no HTML tool, since all annotators use Windows.
  - Output format from this chat: `.md` files until the author asks for PDF.
- **Remains:**
  - Record who is A and B (if two fellows, the professor adjudicates).
  - Send the zips.
  - Log PR in the repo.
  - F8: adjudication tool; a friendly message when the `.exe` runs outside a bundle; skip the geometry tests when tkinter is missing.
  - After the pilot: rules review and 6-row spot-check; SAP text-metric wording; main-drift decision; review-CSV commit at method freeze.

## 2026-09-29 (afternoon): pilot title list frozen; fixed .exe built
- **Did:**
  - Rebuilt `.exe` from main `bed1f46`, SHA-256 `18213FB9D195EE273731C2135F9CAAC9D5CF07D9AA070767DD38EAD7DD1B1604` (supersedes `44DD37BC…`).
    - Verified on the author's PC: role set by `ROLE.txt`, input column visible, labels wrapped, scrollbars.
    - It must run from inside a bundle folder; running it from `dist` fails with a missing-schema error (F8: friendlier message).
  - Annotator guide PDF for B (4 pages, no answers or IDs) prepared in the project chat.
  - Pilot title list committed as `docs/phase5/TITLE_EQUIVALENCE_v0.md` (decisions §9.5).
- **Next:** build the pilot bundle with the list → run the draw once → stage the PDFs → build the A/B workspaces with the `.exe` → record the draw, roster, bundle and manifest hashes here.

## 2026-09-29 (early morning): F7 pilot-ready built and verified; .exe built; draw digest decided
- **Did:**
  - `.exe` built from main `0450456` (Python 3.14.3, PyInstaller 6.22.3, jsonschema 4.26.0; in `D:\gold_tools\exe_build`), SHA-256 `44DD37BC2ED9763BE78E1B84D34DDA9EA42A94B440F9F0A00D7D715D9CB77159`.
    - It starts, and its isolation check correctly refused a launch from inside the repo.
    - The form's input column was pushed off-screen by a long label → fixed in F7.
    - This `.exe` is superseded; rebuild after the F7 merge.
  - F7 (Claude Code, Sonnet 5 Extra High), branch `phase5-f7-pilot-ready` (`9b928bb`):
    - form layout: wrapped labels, scroll area with both scrollbars, window size fitted to the screen;
    - role set by `ROLE.txt`;
    - `tools/phase5/pilot_draw.py` (PILOT_PLAN v0.1.1 §2–§4, 4-token core set);
    - `tools/phase5/stage_pdfs.py` (copy from `live_store`, hash-verified);
    - custodian `--exe/--exe-sha256` and `ROLE.txt`;
    - README start banner.
  - Decisions §9.4: issuer-level draw digests = `SHA-256(domain || 0x00 || company_id)`.
- **Verified here:**
  - Phase 5 tests 220 passed. The 2 failures are GUI geometry tests that import tkinter, which is absent on this Linux box; they pass on the author's PC.
  - Author's PC full suite: the same 11 known failures, plus 48 new passing tests.
  - The agent found why 3 of the known failures happen: `--basetemp` sits inside the repo, so the isolation check trips. It is a test-setup artifact, not a tool bug.
  - This chat's own 22 checks all pass on synthetic data:
    - frame (HOLDOUT, DEVELOPMENT and _MISSING excluded);
    - pair tie broken by a **hand-computed** digest;
    - hard flag only from core CANDIDATE rows on pair members (devanagari and NOT_OBSERVED ignored);
    - hard-issuer reservation, fill by issuer digest, retest disjoint (10 + 6);
    - deterministic; out-dir inside the repo refused; fewer than 5 issuers refused;
    - staging copies and verifies;
    - `ROLE.txt` valid/invalid handling.
- **Remains:**
  - Merge F7 → rebuild the `.exe` → author freezes the pilot title list → bundle with the list → run the draw (once) → stage PDFs → build the A/B workspaces with the `.exe`.
  - F8 adjudication tool.
  - Minor follow-up: make the 2 geometry tests skip when tkinter is missing.

## 2026-09-29 (night): scope decided; F6 built and verified; K1 answered
- **Did:**
  - Author decisions recorded as decisions §9:
    - scope = MD&A location + text only; climate moves to a separate later pipeline;
    - role = infrastructure;
    - tokens 4; SAP 1=C, 2=B, 3=A, 4=A, 5=A; A1, A2, A4, A5 yes; A3 = 2 per issuer;
    - pilot first, with the rules review after the pilot.
  - K1 checked from the Claude Code, Codex and Gemini session records → **No**, with one metadata-only deviation (first Gemini P5-B session; see §9.2).
  - Title list drafted (v0.2, project `claude/round3/TITLE_EQUIVALENCE_v0.md`): 96/96 recorded headings and 37/37 TOC/body pairs normalise. Spot-check rule fixed and 6 rows picked (`TITLE_RULES_CHECK_v0_1.md`).
  - F6 (Claude Code, Sonnet 5 Max), branch `phase5-f6-bundle-v04` (`0fcc527`):
    - schema/protocol v0.4, with anchor text on shared boundary pages;
    - protocol §6 provenance fixed; Acrobat pin added;
    - frozen title-list bundling (`--title-list/--title-list-sha256`, `BUNDLE_MANIFEST.json`);
    - hash-checked seal guard;
    - `.exe`-ready path resolver;
    - custodian writes `ASSIGNMENT.csv`;
    - scoring accepts v0.4;
    - `TOOL_VERSION` p5t-0.2.0.
- **Verified here:**
  - v0–v0.3 schemas/protocols and `DRYRUN_REPORT.*` unchanged; Phase 5 tests 179 passed, 3 skipped.
  - Author's PC full suite: the same 11 known failures, 663 passed (640 + 23 new).
  - This chat's own 24 checks all pass. The seal guard refuses a wrong hash, an edited list, a missing list, a missing or corrupt manifest, the placeholder, and a deleted placeholder with a fake list; it seals a correctly frozen bundle. The anchor rules, the ABSENT nulling, the frozen-exe resolver and scoring all behave as specified.
  - The agent disclosed one `python -c` use against the rules (stopped; covered by tests).
- **Remains:**
  - Ask Annotator B and the adjudicator; set the fallback date.
  - Build the `.exe` (outside the thesis folder).
  - Freeze the pilot title list (author signs) → commit the list and the review CSV → pilot bundle.
  - Pilot draw.
  - F7 adjudication tool.
  - Two training PDFs (companies outside the corpus).

## 2026-09-28 (evening): F3b merged: Gold schema v0.3, protocol v0.3, tool and scoring (decisions §8.7)
- **Did:**
  - F3b ran in Claude Code (Sonnet 5 Max). PR #63 (`c405dfe`, merge `48d386b`).
  - Added `gold_schema_v0_3.json`, `GOLD_SCHEMA_v0_3.md` and `GOLD_PROTOCOL_v0_3.md`.
  - Updated the annotator core and app, `make_bundle.py`, scoring, and three Phase 5 test files.
  - The first run stopped (`BLOCKED:pilot_dryrun`): the dry-run runner built PRESENT forms without the new answers. This chat approved a 4-line fix to `run_dryrun.py` `_answer()`. It also had the stale protocol pointers corrected in `BUNDLE_README.md` and the `make_bundle.py` placeholder (v0.1 → v0.3).
  - The committed `DRYRUN_REPORT.json`/`.md` were deliberately not regenerated. They remain the v0.2 dry-run record, and no test reads them.
- **Verified here (after the merge, on `main` = `48d386b`):**
  - The v0.1/v0.2 schema and protocol files and both `DRYRUN_REPORT` files are byte-identical to before.
  - Phase 5 tests: 157 passed, 2 skipped.
  - Author's PC, full suite: 11 failed (same names as the baseline), 640 passed (594 + 46 new).
  - This chat's own 22 synthetic checks: 22/22 behaved as specified. They cover:
    - refusal of None, "No", 0, 1, "false" and missing answers;
    - flags or `mixed_end_page` supplied by the form are ignored;
    - flag/answer mismatch in both directions;
    - `mixed_end_page` null, or not equal to the end page, when the end page is shared;
    - ABSENT records with answers refused (by the schema, at sealing);
    - scoring refuses mismatched v0.3 Gold;
    - `shared_page_agreement` counts only PRESENT/PRESENT pairs.
- **Found/decided:**
  - Two things the agent did beyond the task list are accepted:
    - Rule 8 now points at the §4 shared-page definition.
    - The app's `mixed_*` tick-boxes were removed, because the flags are now derived from the two answers.
  - For v0.3 records, `exact_flag_agreement` now also reflects shared-page disagreements, because the derived `mixed_*` flags are in `flags`. This is expected, and should be noted when the SAP is revised.
- **Remains (OPEN, not decided):**
  - `boundary_evidence.mixed_end_page` is not enforced as null on ABSENT/AMBIGUOUS; the tool writes null.
  - `TOOL_VERSION` is still `p5t-0.1.0`.
  - The SAP needs wording for §8.7: a word count is analysed only when both answers are No; agreement on the two answers is descriptive.
  - The schema doc's title line still says v0.1.
  - Next steps: title rules + title-list freeze; optional LM-dictionary run; author items (7 vs 4, SAP options, A1–A5, K1, annotators); pilot draw.

## 2026-09-28 (afternoon): text-layer audit built, calibrated and frozen; shared-page fields decided
- **Did:**
  - Audit v0.1 (PR #56, Codex) and v0.2 (PR #59, Gemini Flash; verified here). `tools/phase5/derived/text_layer_audit.py`, script SHA-256 `69e1d153…fafbdad70`.
  - FIT calibration run twice in `D:\gold_blind` (input `fb1df75e…`; v0.1 output `B3AE60CF…`, identical across two Pythons; v0.2 output `9C021464…`).
  - Decisions §8 (PR #57), §8.5 (PR #58), §8.6 frozen thresholds (PR #60), §8.7 shared pages (PR #61).
- **Found:**
  - The earlier "8 broken-text docs" was a keyword over-count. The real positives are Span 2018 (broken body) and Jubilant 2013 / Gujarat Cotex 2017 (legacy-font heading only).
  - Frozen by the pre-registered §8.4 rule: `max_bad_char_share` 0.1207, `min_latin_word_share` 0.3980 → 3/3 found, 0 false positives. Runs pass these on the command line; script defaults unchanged.
  - The computed `start_page_shared` (20% rule) failed: 21 of 31 flags wrong → human field instead (§8.7).
- **Remains:**
  - F3b: schema v0.3 + protocol v0.3 + tool + scoring (`start_page_shared`/`end_page_shared` required booleans). Worktree `phase5-schema-v03` at `299200a`; prompt in project `claude/round3/NEXT_CODEX_F3B_SCHEMA_v0_3.md`.
  - Title rules + title-list freeze; optional LM-dictionary run; author items (7 vs 4, SAP options, A1–A5, K1, annotators); pilot draw.

## 2026-09-28 (morning): D1–D7 decided; schema v0.2 (F3) and protocol/SAP v0.2 (F5) merged
- **Did:**
  - Decisions: PR #50 (D1–D7 + D4 statutory list), #51 (A1–A5 + field specs), #52 (review fixes: stub without hand counting, robust broken-text test, `schema_version`, Hindi-only span, reversibility). File: `docs/phase5/decisions/D1_D7_DECISIONS_v0_1.md`.
  - F3 (Codex GPT-5.6 Sol Extra High): PR #53 (`bf85ef2`). Gold schema v0.2: `NO_ENGLISH_MDA`, `EXTERNAL_REFERENCE_ONLY` (+ `HINDI_COPY` span allowed only there), `stub` (+ optional count), `contains_csr_esg` + `csr_esg_pages`, required `schema_version: "0.2"`; annotator core refuses to seal while the title list is unfrozen (test-only override); scoring picks the schema by `schema_version`.
  - F5 (Codex, same model): PR #54 (`460e57d`). `GOLD_PROTOCOL_v0_2.md` (boundary hierarchy, Rules 1/3/5/7 updated, new Rules 10–12), `SAP_v0_2.md` (presence handling, exact and ±1 start, strata, §14 sensitivities), `CHANGELOG_v0_2.md`; bundle ships protocol v0.2.
  - This chat re-verified both: v0.1 files byte-identical; Phase 5 tests 87 passed; 21 own adversarial schema records all behaved as specified. Full suite on the author's PC = the same 11 known failures + 11 new passes (569 passed).
- **Found:**
  - Tests on the author's PC must use `D:\sem_iitk\sem9\thesis\.venv\Scripts\python.exe`; a bare `python` in a new VS Code window lacks `rapidfuzz`/`yaml` (9 collection errors). All future prompts name this interpreter.
  - F5 OPEN item (no formula for page-exclusion sensitivities) resolved as PROPOSED in SAP v0.2 §14: D3 via `substantive_start_page`; CSR/ESG via page-set IoU with CSR and gap pages removed.
- **Remains:** §7.3 broken-text / word-count script + calibration on 60 FIT docs; title rules and title-list freeze; author items (7 vs 4, SAP options, A1–A5, K1); annotators; pilot draw.

## 2026-09-28 (morning): title review CSV final (v0.1, corrected)
- **Did:** the author corrected the review after this chat's row check and page-by-page screenshot checks (HDFC ends, CRISIL 2017 start, Reliance 2018/2025, IDBI 2012, Mac Hotels, Modern Steels 2017, Craftsman 2025, Tata Steel 2024, PVR 2018, IDBI 2024).
  - Final `MDNA_TITLE_REVIEW_v0_1.csv`: 60 rows, 46,448 bytes, SHA-256 `2A362F03E284C51772987635D8F9EC8EED0AD857357FF0DD05E719570B61A60E` (supersedes `1374BBAA…`). Backup in `D:\gold_review_backup\`.
- **Found (checked by script):**
  - 59 Y + 1 NOT_AR. Every Y row has a start and an end; start <= end in all 59; no placeholders left.
  - 38 have a TOC title, 58 a body title. Of 37 with both, only 14 match exactly; 33 match after normalising (and/&, 's, Discussions, Report, year, Annexure/item labels).
  - Pre-fill accepted: TOC 22/38, body 34/58; the rest were typed.
  - Notes mention: annexure 19, inside the Directors' Report 15, running headers 12, wrapped titles 10, spreads 8, broken text layer 8, decorative heading 7, bilingual 3; 12 rows carry an UNSURE flag.
  - HDFC rule: MD&A ends before the first statutory Directors' Report item (content test), in all five years.
- **Remains:** author decisions D1–D7 (see `REVIEW_LEARNINGS_60_FIT_DOCS.md`); then freeze the title list and commit the CSV; "7 vs 4"; SAP options; A1–A5; K1.

## 2026-09-28 (early morning): the 60-document title review finished
- **Did:**
  - The author reviewed all 60 FIT documents in `review.html`, checking each with this chat. The export is `MDNA_TITLE_REVIEW_v0_1.csv`, saved in `D:\gold_blind\output\p5b3\review\`.
    - 60 rows; 43,813 bytes; written 28-09-2026 06:26:50.
    - SHA-256 `1374BBAAFEAEF6587BC386578011CF175066B63685B91B0F40026022699BB7DA`.
  - A backup copy is at `D:\gold_review_backup\`, with the same hash. It is deliberately **outside** the thesis folder.
  - Saved `claude/round3/REVIEW_LEARNINGS_60_FIT_DOCS.md`: rules, the D1–D7 open decisions, title facts, pipeline improvements and issuer series.
  - Saved `REVIEW_NOTES_TEMPLATE.md`. Updated `MDNA_START_END_CHECKLIST.md` with the heading-style test and the content test.
- **Found:**
  - The TOC page number is the reliable start signal. Pre-fill misses came mostly from wrapped titles, pointers taken as the BODY, running headers, decorative headings and broken text layers.
  - The TOC and body titles often differ ("and"/"&", "'s", "Report", year).
  - The end of MD&A inside the Directors' Report needs a style or content test (HDFC).
- **Decided (rule):** Gold files never go inside `D:\sem_iitk\sem9\thesis`, where agents can read them. The working copy stays in `D:\gold_blind` and the backup in `D:\gold_review_backup`. The CSV enters the repo only as one planned commit, after it is checked and D1–D7 are decided.
- **Remains:**
  - The author attaches the CSV to this chat.
  - Open checks: CRISIL 2017 start, the HDFC ends, Tata Steel 2024, the PVR 2018 and IDBI 2024 in-between pages, Modern Steels 2017.
  - D1–D7 decisions.
  - "7 vs 4"; SAP options; A1–A5; K1.
- **Next:** validate the CSV; count the patterns; draft the title rules; freeze the title list.

## 2026-09-28 (night): dry run merged; SAP OPEN-items options memo
- **Did:**
  - PR #45 (dry run) and #46 (log) merged.
  - Codex wrote `docs/phase5/research/SAP_OPEN_ITEMS_OPTIONS_2026-09-27.md` (`7252784`, docs only, no decisions).
- **Found (proposed defaults, all AUTHOR_DECISION):**
  - §7 interval: issuer-cluster bootstrap, as a sensitivity only; the census stays the headline.
  - §8 empty/empty gap Jaccard: undefined, reported as a count.
  - Signed differences: A minus B.
  - Non-comparable pairs: defined per metric; span and gap metrics use PRESENT/PRESENT pairs.
  - Prediction CSV: keep the current 7-column CLI format.
- **Remains (author):** choose the SAP options; the title review CSV; "7 vs 4"; A1–A5.
- **Remains (tooling, after the decisions):** add the §8 outputs to scoring; move the title-list guard into the annotator core.

## 2026-09-28 (night): P5-C custodian merged; pilot dry run
- **Did:**
  - Custodian builder merged (PR #44, `bd3aae7`; 10 synthetic tests).
  - Codex ran the P5-C dry run (`phase5-dryrun`, `073c054`): a synthetic end-to-end run of custodian → annotator → export → scoring.
  - This chat changed the §6 trigger status from BLOCKED to NOT_APPLICABLE (`8bf6e66`). §6 is identical in v0.1 and v0.1.1, and its thresholds apply to the 10-document pilot, not to synthetic files.
  - Tests on the main + dry-run merge: 559 passed, plus the same 10 pre-existing main-drift failures.
- **Found (dry-run FINDINGS):**
  - (1) The title-list freeze is enforced in the app layer only. `annotator_core.seal_raw_record` has no title-list check, so a script could seal records before the list is frozen.
    - **Proposed:** move the check into the core (small P5-T follow-up).
  - (2) `raw_ab_agreement` does not return the gap-set Jaccard or the non-comparable counts named in SAP §8. These are the known OPEN items; the SAP options memo is in progress.
- **Remains:** merge `phase5-dryrun`; the SAP options memo; P5-T core title-list guard (follow-up); the title review CSV; the "7 vs 4" answer.

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
