# T0 — Extraction corpus freeze protocol

## Worktree / git provenance

| Field | Value |
|---|---|
| Source repository | `D:\sem_iitk\sem9\thesis\sep_week1\arpipe-pm2.1-pagegrain` (a worktree of the shared repo `arpipe-0.1.0`) |
| Base commit | `158a9eac48a3374a9506af8281acb93f49a37a0d` ("research: analyze orphan rate at native vs OCR page grain") |
| New worktree | `D:\sem_iitk\sem9\thesis\sep_week1\arpipe-extraction-corpus-freeze` |
| Branch | `extraction-corpus-freeze` |
| Base-commit verification | Verified via `git worktree list` on `arpipe-0.1.0` before branching: `arpipe-pm2.1-pagegrain` was clean (`git status` — only one untracked cache file), on branch `pm2.1-pagegrain-native-vs-ocr`, up to date with `origin/pm2.1-pagegrain-native-vs-ocr`. No other session had a pending edit to this worktree at branch time. |
| Worktree path collision check | `D:\sem_iitk\sem9\thesis\sep_week1\arpipe-extraction-corpus-freeze` did not exist before this task. |
| Branch collision check | `extraction-corpus-freeze` did not exist in `git branch -a` before this task. |

This task did not touch any R1 / P-C0 / P-R1X / P-M5 / forensic / audit worktree. It reads (never writes) two files from `arpipe-0.1.0` outside this worktree — see "Local PDF store" below — which is the only cross-worktree interaction in this task.

## What this freeze does NOT do

No OCR, no remapping, no reading-order code, no heading detector, no candidate generator, no span resolver, no verifier, no quality gate, and no repair of the historical PDF-acquisition problem. `tools/freeze_extraction_corpus.py` never imports `arpipe.segment`, `arpipe.verify`, `arpipe.ocr`, `arpipe.pipeline`, or `arpipe.evaluate`. The only `arpipe`-adjacent artifacts read are pre-existing, already-committed data files (`documents.jsonl`, `profiles.jsonl`, `labels.csv`, `to_label.csv`, `companies.csv`) — never pipeline source modules.

**PRODUCTION EXTRACTION CODE MODIFIED: NO.** `git diff --stat` against the base commit touches only files under `dataset/corpus_freeze/` and `tools/freeze_extraction_corpus.py`.

## Local PDF store (read-only, out-of-worktree)

The 194 locally available annual-report PDFs live in `D:\sem_iitk\sem9\thesis\sep_week1\arpipe-0.1.0\live_store\` (content-addressed `blobs/<sha[0:2]>/<sha[2:4]>/<sha>.pdf`, ~1.4 GB), produced by that repo's earlier, already-committed `fetch`/`triage` pipeline stages. `live_store/` is gitignored in every worktree of `arpipe-0.1.0` (see its `.gitignore`: `/live_store/`), so it is **not** copied into this worktree — copying 1.4 GB of binary blobs into a git worktree whose only job is to freeze *manifests* would bloat this worktree for no benefit, and the STRICTLY LOCAL rule only requires reading PDFs that are already locally available, not relocating them. `corpus_inventory.csv`'s `source_locator` column records the absolute path to each PDF's blob plus the live_store root, so any consumer can resolve every PDF byte-for-byte from the frozen SHA-256.

No PDF was downloaded, fetched, or otherwise newly acquired. No PDF was deleted or modified. This task queried only:

- `live_store/documents.jsonl` (194 rows — fetch-stage manifest: `sha256`, `path`, `n_bytes`, `n_pages`, `source`, `url`, `pdf_producer`, `is_encrypted`, `fetched_at`)
- `live_store/profiles.jsonl` (194 rows — triage/textlayer-stage document+page profile: `doc_kind`, `frac_needing_ocr`, `has_outline`, `outline_titles`, `bilingual`, `dominant_script`, and per-page `kind`/`n_chars`/`n_words`/`text_area_frac`/`image_area_frac`/`n_images`/`n_columns`/`script`/`mojibake_ratio`/`dpi_estimate`/`rotation`)
- this worktree's own `companies.csv`, `labels.csv`, `to_label.csv` (all git-tracked, already committed at the base commit)

Every fact drawn from these files is tagged `KNOWN_FROM_PRIOR` in `corpus_inventory.csv` / `diversity_matrix.csv`, distinct from facts this task measured itself (`OBSERVED`) or derived with a cheap heuristic (`INFERRED`). See section 19 of the T0 brief and `CONDITIONS`/`EVIDENCE_STATES` in `tools/freeze_extraction_corpus.py`.

## Also considered, excluded from the corpus

- `arpipe/fixtures/*.pdf` (7 files: `A_digital_outline`, `B_twocol_toc`, `C_scanned`/`C_src`, `D_hybrid`/`D_src`, `E_bilingual`) — synthetic unit-test fixtures built by an earlier task to exercise specific pipeline code paths (per `PIPELINE_STATUS.md` §2/§3), not real annual reports. Excluded from `corpus_inventory.csv` because they are not "annual-report PDFs"; noted here so they are not mistaken for an unexplained gap.
- Materialised `companies/<ISSUER>/<FY>/annual_report.pdf` trees found under several other worktrees (e.g. `arpipe-step0a-recovery/snapshot/.../companies/...`) are hardlink/symlink/copy materialisations of the *same* 194 blobs (see `arpipe/store.py:link_pdf`), not additional unique documents. Confirmed by content-addressing: their SHA-256 identity is defined by the blob path they link to.
- PDFs under `week2/`, `old _work/`, `sep_week01/` are unrelated coursework/paper material, not annual reports.

## Environment used to run the tool

`tools/freeze_extraction_corpus.py` was executed with the Python virtual environment already present at `sep_week1/arpipe-pm2.1-pagegrain/.venv` (Python 3.14, `pymupdf==1.28.2`, `pandas==3.0.5`), invoked read-only (no writes made into that worktree). This worktree (`arpipe-extraction-corpus-freeze`) does not carry its own `.venv` because virtual environments are untracked/per-worktree; any environment with `pymupdf>=1.24` reproduces the same fresh-profiling results, since the tool performs no rendering (no OCR, no rasterization) — only object-model reads (`get_toc`, `get_fonts`, `page.rect`, `get_text("text")` for a small per-document page sample, plus a whole-file SHA-256).

## Method: how development diversity was maximised

`greedy_diversity_select()` in `tools/freeze_extraction_corpus.py` is a **greedy diversity-maximising selection** — explicitly *not* a globally optimal set-cover solver. At each step it picks the not-yet-selected FIT document that covers the most still-uncovered conditions, where each condition is weighted `1 / (number of FIT documents with that condition)` so a condition seen in only 2–3 documents dominates the score over a condition seen in 100. Ties favour a document from an issuer not yet represented in the development set; the fixed tie-break order underneath is a seeded shuffle (`random.Random(seed)`), so results are exactly reproducible for a fixed seed and otherwise arbitrary. The same function (different seed string, different condition axis list) drives the annotation-roster selection from the development set.

The challenge-coverage set is a simple rarity-weighted ranking (not a greedy cover): every document that trips at least one of the challenge conditions is scored by the sum of `1 / frequency` over the conditions it trips, sorted descending, and the top `--challenge-max` (default 45) are kept. It intentionally overlaps FIT/VALIDATION/HOLDOUT and development — see `dataset/corpus_freeze/challenge_coverage_manifest.csv` — and must never be read as an independent test set.

## Reproducibility

Seed: `20260918` (`--seed`, also the run date). Running `tools/freeze_extraction_corpus.py --seed 20260918` three times produced **byte-identical** files in `dataset/corpus_freeze/` each time (verified with `diff -rq` across full copies of the output directory between runs, after each fix to the tool during development). This includes CSV row order (the inventory is sorted by `(company_id, fiscal_year, sha256)` before any selection logic runs, not by filesystem/JSONL append order), the FIT/VALIDATION/HOLDOUT assignment, the development/challenge/roster selections, and every manifest hash under `hashes/`.

Verified invariants (also asserted in `freeze_summary.json`):

- `FIT ∩ VALIDATION = ∅`, `FIT ∩ HOLDOUT = ∅`, `VALIDATION ∩ HOLDOUT = ∅` (issuer-grouped by construction: a document's split is always its issuer's split)
- `development ⊆ FIT`
- `annotation_roster ⊆ development`
- no PDF's SHA-256 changed between runs (re-hashed from bytes each run, not cached)
- no exact duplicate SHA-256 counted twice (194 unique SHA-256 among the 194 present documents)
- no new `mda_present` / `mda_start_page` / `mda_end_page` gold labels were written anywhere (`annotation_roster.csv`'s gold columns are blank for every row; the only existing gold, in the base commit's `labels.csv`, is surfaced purely as a `notes` annotation in `corpus_inventory.csv`, never copied into the roster)
- production extraction code (`arpipe/*.py`) unchanged from the base commit

## Known local corpus limitations (do not over-read this freeze)

- **No bilingual or Devanagari-script real annual report exists in the local corpus.** `profiles.jsonl`'s page-level `script` field never records `devanagari` or `other_indic` across all 194 documents' ~38k pages; a fresh full-text regex scan (`\u0900-\u097f`) over sampled pages found Devanagari characters in only 2 documents (both from a single issuer, `INE002L01015`). The only Hindi/bilingual *fixture* in the project is the synthetic `E_bilingual.pdf`, excluded per above. `PIPELINE_STATUS.md` independently documents that Hindi OCR (`tesseract-ocr-hin`) is not installed on this machine, so this gap was already known, not discovered here.
- **`table_heavy`, `full_width_header`, `full_width_footer`, `toc_offset`, `duplicate_text` are marked `UNKNOWN` corpus-wide.** No cheap, already-frozen local signal answers these; a real answer needs either a table-geometry pass (a "table parser", explicitly out of scope for T0) or the TOC-offset solver in `arpipe/segment.py` (explicitly out of scope — that module *is* candidate generation).
- **14 of the base commit's 20 `labels.csv` (historical-ground-truth) documents have no PDF bytes anywhere in the current `live_store/`.** This is a pre-existing store/acquisition gap (consistent with the already-diagnosed P-C0 coverage problem — see this project's own memory of that diagnosis), not something T0 investigates or repairs (STRICTLY LOCAL: not re-fetched). These 14 are recorded as explicit `..._MISSING` rows in `corpus_inventory.csv` rather than silently dropped, and excluded from every split/selection/matrix because there is nothing local to profile.
- This corpus is **36 issuers**, mostly at 6 fiscal years each (2012/2013/2017/2018/2024/2025, with a few issuers holding an older 2011 or 2015 report instead). It is a diversity-maximising sample of what happens to be locally available, not a statistically representative sample of Indian annual reports or of the 576-company universe referenced elsewhere in this project. See `stratification_report.md` for the full breakdown and every other explicit non-claim required by section 35 of the T0 brief.
