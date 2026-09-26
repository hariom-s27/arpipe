# P-B source coverage register

## Observation point and search boundary

`CURRENT_GOVERNANCE_STATE` means evidence observable in the thesis repository at **2026-09-26 08:49:29 UTC**. The thesis repository is `D:/sem_iitk/sem9/thesis`, branch `main`, HEAD `313f00b7e8c364c056a5a9d284ff843128419e21`; `origin/main` was `14d665992404c885f1160b6ea568460ce87a3904`. The main working tree had no modified tracked files and had the untracked directories `_r1_private_archive`, `sep_week1/d6-q6-identity-decision`, `sep_week1/r1-final-evidence`, `sep_week1/r1-final`, `sep_week1/r1-resume-2-final`, `sep_week1/r1-resume-2`, `sep_week1/runnable-identity-r1-resume`, `sep_week1/runnable-identity`, `sep_week1/t04-guard-forensics`, `sep_week2/arpipe_doc_24sep`, and `sep_week2/arpipe_doc_Sep23`. This is the state **before** the dedicated P-B worktree was made. Git listed no existing P-B worktree. The P-B worktree was then created at `sep_week2/pb-governance-worktree`, on `pb-governance-20260926` from the same base SHA, initially clean.

The numbered Sep23 and Sep24 thesis packs are **untracked thesis material**, not ARPipe repository records. The ARPipe repository is separate. Its inspected local refs include `phase3-claims-scope` (`112d8297837f72881ead46ca2d9fb0735d10b3a1`), `phase4-b1-b8` (`50769ffc6b5ec75919ddbab523db49cc1d80c223`), `d6-q6-identity-decision` (`755c5519b9ab9484ab033685e563350a0cd0d685`), `t0.4-gold-method-research` (`1c53c42129b68259698143b6c13bc2d0d073fbf6`), `t04-guard-forensics` (`1db8ccddf282ec86a6785df80b04a73d680a60f9`), and `r1-final` (`53dcab40c374b499637ad3f68596549540ef1c42`). Their origin counterparts were enumerated. The thesis `main` and `origin/main` were inspected; later remote changes were not fetched or used.

## Search performed

Search performed 2026-09-26 from 08:49 UTC with PowerShell, `rg`, `git grep`, `git ls-files`, `git ls-tree`, `git log`, `git status`, `git worktree list`, `Get-FileHash`, and direct line-numbered reads. Search roots were the thesis tracked Markdown/JSON files at the snapshot HEAD; `ARPipe_Memory`; `sep_week1/arpipe-docs` and `sep_week1/arpipe-docs_2`; `sep_week2/arpipe-docs/arpipe-docs` and `sep_week2/arpipe-explain`; the two untracked `sep_week2/arpipe_doc_*` governance packs; and `docs/` at the six ARPipe refs above. The readable ARPipe worktrees `sep_week1/phase3-claims-scope`, `sep_week1/phase4-b1-b8`, `sep_week1/d6-q6-identity-decision`, and `sep_week1/r1-final` were compared to their Git blobs. For governance claims, committed blobs take precedence over mutable worktree copies. The identical Phase 3 and Phase 4 copies in those worktrees were de-duplicated by SHA-256, not filename.

The case-insensitive discovery expression actually run was:

```text
AUTHOR CHOICE|RATIFIED|AUTHOR.APPROVED|DECISION|AMENDMENT|SUPERSEDED|REPLACES|REPLACED|PROPOSED|PENDING|DEFER_UNTIL_TRIGGER|DECIDE_NOW|CONDITIONAL|AS-IS|C1|C2|CC-1|CC-4|B[1-8]|D(10|[1-9])|Q(10|[1-9])
```

The additional targeted searches used `Q1b|Q2|Q3|Q4|Q5|Q6|Q7|Q8|Q9|Q10|K12|PG-1|CC-4|C1-D1`, `AUTHOR CHOICE|AUTHOR.APPROVED|RATIFIED|adopted|supersed|amend`, and the exact string `Q1b`. Filename patterns included `*DECISION*`, `*ROADMAP*`, `*CLOSURE*`, `*GOLD*`, `*SOURCE*`, `*CORRECTION*`, `*CRITIQUE*`, `*TRIAGE*`, `*AMENDMENT*`, `*IDENTITY*`, and `*P-B*`. The terms `AUTHOR-APPROVED`, `AUTHOR APPROVED`, `SUPERSEDED`, `REPLACES`, `REPLACED`, `AMENDMENT`, `DEFER_UNTIL_TRIGGER`, `DECIDE_NOW`, and `CONDITIONAL` were therefore searched literally or by the shown case-insensitive equivalent. Decision IDs `D1`–`D10`, `Q1`–`Q10` (plus `Q1b`), `B1`–`B8`, `C1`, `C2`, `CC-1`, `CC-4`, `PG-1`, and As-Is were included in the combined or targeted searches.

Representative exact commands (with the discovery expression above substituted for `PATTERN`) were:

```text
git grep -l -i -E PATTERN 313f00b7e8c364c056a5a9d284ff843128419e21 -- '*.md' '*.json'
rg -l -i PATTERN sep_week2/arpipe_doc_Sep23 sep_week2/arpipe_doc_24sep
git -C sep_week1/r1-final grep -l -i -E PATTERN r1-final -- 'docs/**/*.md' 'docs/**/*.json'
git -C sep_week1/r1-final grep -l -i -E PATTERN phase3-claims-scope phase4-b1-b8 d6-q6-identity-decision t0.4-gold-method-research -- 'docs/**/*.md' 'docs/**/*.json'
git grep -n -i Q1b 313f00b7e8c364c056a5a9d284ff843128419e21 -- '*.md' '*.json'
rg -n -i Q1b sep_week2/arpipe_doc_Sep23 sep_week2/arpipe_doc_24sep
git -C sep_week1/r1-final grep -n -i Q1b phase3-claims-scope phase4-b1-b8 d6-q6-identity-decision t0.4-gold-method-research r1-final -- docs
```

`git grep -l` returned 93 matching thesis tracked Markdown/JSON paths (of 138 such tracked paths), `rg -l` returned 29 matching files in the two untracked governance packs (31 files total), and `git grep -l` returned 195 matching paths at ARPipe `r1-final` under `docs/`. The five selected earlier ARPipe refs yielded 81 matching ref/path pairs. These are candidate counts, not counts of ratified decisions. Direct inspection then concentrated on the exact sources in [the manifest](P-B_SOURCE_MANIFEST.md). Source content was not inferred from filenames alone.

## Discovered source families and competing versions

| Family | Files discovered / treatment |
|---|---|
| Direct-author transcription and later scoped selection | ARPipe Phase 4 `PHASE4_B1_B8_TRIAGE.md` §0; `D6_Q6_AS_IS_IDENTITY_DECISION_v1.md`; `T0_4_AMENDMENT_01.md`. These are the strongest available author-choice records, with the transcription limits described below. |
| Formal preparation and unresolved fields | ARPipe `PHASE3_DECISION_SHEET.md`, `PHASE3_CLAIM_EVIDENCE_MATRIX.md`, `PHASE3_POPULATION_SAMPLING.md`, `PHASE3_B1_B8_IMPACT.md`, `PHASE4_DECISION_SHEET.md`, `PHASE4_B1_B3_FACTUAL_ERRATA.md`, and `PHASE2.1_B1_B8_DECISION_REGISTER.md`. Their proposed/blank fields were preserved. |
| Identity, closure and contract facts | ARPipe `RUNNABLE_IDENTITY_v1.md`, `R1_A1_A6_DECISION_RECORD.md`, T0.4 closure and frozen contract references. Execution facts are not treated as author approval. |
| Thesis historical/research pack | All 22 files in `sep_week2/arpipe_doc_Sep23`, including 10–12, 14, 16–20 and `T0.4-LF-RECON.md`; all nine `A01`–`A09` files in `sep_week2/arpipe_doc_24sep`. The Sep23 decision sheet calls its entries recommendations; the Sep24 pack labels itself research/synthesis. Neither pack silently becomes ARPipe canon. |
| Tracked earlier thesis memory/docs | `ARPipe_Memory` and earlier `arpipe-docs` copies were searched for provenance and historical context. `ARPipe_Memory/03_DECISIONS.md` explicitly points to `02_DECISIONS.md` as superseding it for that memory family; that statement does not supersede Phase 3/4 governance. |

The four inspected ARPipe copies of `PHASE3_DECISION_SHEET.md` have the same SHA-256 `2C5ACE858D2685B76C187642E8174C88439FC36491C5E4C58A1AE351C3712719`; three Phase 4 copies have the same SHA-256 `65206BE41B74BD4069EE4B2AB10FA8AA9F21DA059D22F295681E8BA26936DE91`. Conversely `sep_week2/arpipe_doc_Sep23/20_SOURCES.md` has SHA-256 `C6659C89C273D6E2843BBCA2F68EF4025BE283CC49AF65359D33979670A15A8A`, whereas the older tracked `sep_week2/arpipe-docs/arpipe-docs/20_SOURCES.md` has `6CCD94106AE509A606AD029DCBD15587769BCF57AF65B722C9E4D528C1EEE353`. Equal filenames were not treated as equal versions.

### Discovered files not used as current-decision authority

| Source files / paths | Reason excluded from current ratification evidence |
|---|---|
| `sep_week2/arpipe_doc_Sep23/01_THE_SHORT_VERSION.md`, `03_T0.1_GAP_AUDIT.md` through `09_T0.4_OCR_PREREG.md`, `13_GIT_AND_REPO_STATE.md`, `15_WHAT_THE_FIELD_KNOWS.md` | Historical phase narrative, repository status, or external research. They were inventoried as part of the 22-file pack; their facts may contextualize the project but they contain no stronger author-choice record than R05/R09/R12. They were not cited to establish a current ratified D/Q/B choice. |
| Tracked `sep_week1/arpipe-docs*` and `sep_week2/arpipe-docs/arpipe-docs/*`, `sep_week2/arpipe-explain/*` | Earlier pipeline explanation/source versions. Their different `20_SOURCES.md` bytes establish a competing copy, not a later governance vote. |
| ARPipe `docs/identity/evidence/**`, test outputs, reports, generated JSON/XML and duplicate `docs/phase3`/`docs/phase4` files at other branches | Execution or historical evidence and byte-identical governance copies, not an additional author selection. Selected identity/contract facts are drawn from the precise R sources in the manifest. |
| ARPipe `t0.4-gold-method-research` decision memo and research siblings | Located and keyword-inspected as method preparation; its required author choices are not completed. No decision was promoted from this research-only branch. |

## Source hierarchy used

The project record says the author is the sole decision authority (Phase 4 triage §0.1) and marks both Phase 3 and Phase 4 sheets as proposed with blank author-choice fields. No comprehensive cross-repository precedence rule was found. P-B therefore uses: **A**, explicit recorded author input or author-ratified amendment, interpreted only within its stated scope; **B**, formal governance sheets, closure records, and frozen contracts, authoritative for their recorded facts and unresolved state but not for an unfilled author choice; **C**, thesis research, critiques, recommendations, and agent syntheses; **D**, older drafts and historical memory. A Git commit records source bytes; it does not itself ratify a choice. A later source does not supersede an earlier decision without explicit scope and authority. A P-B output is never input evidence for this P-B reconstruction.

## Coverage limits and absence classifications

| Item | Classification | Consequence |
|---|---|---|
| Original direct author message and exact date for the Phase 4 D1–D10 input | `INSUFFICIENT_SOURCE_COVERAGE` | Phase 4 §0 says supplied directly and records “verbatim, condensed” operative clauses. The original full message is not in the inspected project files. The recorded clauses support scoped decisions, but their unabridged wording/date cannot be independently recovered. This is PG-1, not a reason to fill the blank Phase 3 fields. |
| P4R and LFG pasted reports cited by Sep24 A01; the A10 adversarial review cited by A09 | `INSUFFICIENT_SOURCE_COVERAGE` | These referenced source texts were not found as local files in the searched roots. Claims relying only on them remain secondary or unresolved. |
| Canonical pre-existing file numbering this task's `Q1b`–`Q10` author-input list | `NOT_FOUND_AFTER_EXHAUSTIVE_SEARCH` **within the stated governance search roots only** | The P-B Q labels are inquiry IDs, not assumed to equal Phase 3's Q labels. Their topics are reconstructed from named gaps and questions in formal sources. This statement does not cover private conversation history. |
| Private chats, accounts, un-fetched remotes, external literature, ignored `data/`, `week2/`, `sep_week01/`, binary PDFs, OCR artifacts, HOLDOUT/Gold content, tests and production code | `NOT_SEARCHED` for governance ratification | They were outside this local governance transcription boundary. Frozen configuration/implementation was read only where an existing governance record specifically cited a contract fact; such facts do not establish approval. |

No project-wide negative claim about an inaccessible author conversation is made. For B1–B8, the formal records affirmatively say no B decision was adopted. For other unresolved items, the status is based on explicit blank fields/gaps and the stated coverage, not silence alone.
