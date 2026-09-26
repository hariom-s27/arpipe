# R1-FINAL evidence preservation — omission register

Every artifact that was considered during the R1 Evidence Preservation task and
**not** placed in the public archive, with the reason.

**Omission is not evidence that an artifact never existed.** Several entries
below are present on disk right now and were deliberately left out; two are
genuinely gone. The status codes distinguish these.

Status codes: `PRESERVED`, `PRESERVED_PRIVATELY`, `EXCLUDED_BY_SCOPE`,
`NOT_FOUND`, `NOT_RECOVERABLE`, `NOT_REQUIRED_FOR_PROVENANCE`.

Totals: 593 files snapshotted; 251 preserved publicly; 3 preserved privately;
339 excluded. Hashes for **all 593**, including every excluded file, are in
`r1-final-evidence-manifest.json`, so any omitted artifact can be identified
later by hash even if this archive is all that survives.

---

## 1. Raw corpus material

| Artifact | Status | Detail |
|---|---|---|
| 68 × `annual_report.pdf` under `primary/`, `smoke-a/`, `smoke-b/`, `out-run-a/`, `out-run-b/` | `EXCLUDED_BY_SCOPE` | 507,929,568 bytes of raw annual-report PDFs. Considered because they are the literal inputs to the 58-document and 4-document runs. Excluded under scope §18 (corpus redistribution restriction) and classified `EXCLUDE` at the release gate. **Provenance is unaffected**: each document's `pdf_sha256` is recorded in `result.json`, `fit-inputs.json` and `universe.json`, and `run_document.py` asserted that hash before opening each file. Per-file SHA-256 for all 68 is in the manifest. |
| `mda.txt`, `mda.json`, `mda_blocks.json`, `document.json` (269 files, 8,502,025 bytes) | `EXCLUDED_BY_SCOPE` / `NOT_REQUIRED_FOR_PROVENANCE` | Extracted management-discussion text and per-document extraction payloads. Classified `PRIVATE_ARCHIVE_REQUIRED` — corpus-derived content. None of the comparisons read them: `compare_outputs.py` compares `located`, `start_page`, `end_page`, `grade`, `span_path_nullness`, `script_map` and `per_page_kind`, all of which live in `result.json`, which **is** preserved. Hashes in the manifest. |
| Rendered annual-report page PNGs | `NOT_FOUND` | Searched across the scratchpad and `r1-final-evidence/`. The only images present are a committed report chart inside the two worktree checkouts and a 20-byte synthetic `page.png` test fixture. No rendered corpus page images exist in the R1 evidence; none were copied. |
| `reports/legacy_font_corpus_measurement.csv` (23,384,908 bytes) | `EXCLUDED_BY_SCOPE` | The 23 MB corpus CSV named in scope §17/§18. Considered because it sits in the same repository tree. It is not an input to, or output of, any R1-FINAL execution and is referenced by no R1 artifact. Not copied; provenance unaffected. |
| `arpipe-0.1.0/runs/` (16 MB) | `EXCLUDED_BY_SCOPE` | Unrelated earlier pipeline run output. No R1 artifact references it. |
| `arpipe-0.1.0/pm1_baseline_run/` bulk (1.4 GB), `pm1_after_run/` bulk (25 MB) | `EXCLUDED_BY_SCOPE` | Only the two `manifest.jsonl` files and the two run logs are required — those are the comparison inputs actually read by `compare_outputs.py`, and they **are** preserved under `historical-baseline/`. The surrounding per-company output trees (including raw PDFs) are not. |

## 2. Execution trees

All four are reconstructible from Git and were byte-verified against their
commits during R1 recovery. Instead of copying them, the archive preserves a
per-file SHA-256 listing of each under `tree-manifests/`.

| Artifact | Status | Detail |
|---|---|---|
| `scratchpad/base-t04/` (76 files, 7,334,967 B) | `EXCLUDED_BY_SCOPE` | `git archive` export of `ff030d97c13c8a2a977521bf91be2aca0cbf3034`; verified 46/46 against Git blobs during recovery. Hash listing: `tree-manifests/base-t04.sha256`. |
| `scratchpad/cand-t04/` (89 files, 7,383,477 B) | `EXCLUDED_BY_SCOPE` | Export of `28a67b63…`; verified 59/59. Listing: `tree-manifests/cand-t04.sha256`. |
| `scratchpad/run-a/` (90 files, 7,416,714 B) | `EXCLUDED_BY_SCOPE` | Export of `28a67b63…`; verified 59/59. Listing: `tree-manifests/run-a.sha256`. |
| `scratchpad/run-b/` (103 files, 80,457,639 B) | `EXCLUDED_BY_SCOPE` | Export of `28a67b63…` plus a 70 MB built `arpipe/fixtures/` directory. The export half is reconstructible; the fixtures are synthetic, rebuildable via `tests/make_fixtures.py`, and gitignored by repository convention. Listing: `tree-manifests/run-b.sha256`. |
| `r1-final-evidence/candidate-a/`, `candidate-b/` (50 MB each) | `EXCLUDED_BY_SCOPE` | Live Git worktrees, both confirmed clean at `588b6e60b20922e1f0986df492e370ac435c0747` during this task. Fully reconstructible from that commit. Not copied and **not modified or removed** — they remain registered worktrees. |
| `__pycache__/*.pyc` inside the execution trees | `EXCLUDED_BY_SCOPE` | Evidentially useful (in-place bytecode consistent with actual execution there) and therefore **hash-listed** in the tree manifests, but not copied as bytes. |

## 3. Test scaffolding

| Artifact | Status | Detail |
|---|---|---|
| `r1-final-evidence/pytest-temp/` (57 MB) | `EXCLUDED_BY_SCOPE` | pytest temporary directories from the 382-test run. The run's result is preserved as `pytest-full.xml` and `pytest-exit.txt`. |
| `scratchpad/test-deps/`, `r1-final-evidence/test-deps/` (2.8 MB each) | `EXCLUDED_BY_SCOPE` | Vendored `jsonschema 4.26.0` and its dependencies, supplied on `PYTHONPATH`. Identified by version in `environment_final.txt`; bytes not required for provenance. |
| `r1-final-suite/` worktree | `NOT_RECOVERABLE` | The checkout at `28a67b6` that produced `suite_pin.txt` / `suite_pin.xml`. Deleted 2026-09-26 02:11 IST (a `git worktree remove` failed with Permission denied, then `rm -rf` and `git worktree prune`). Confirmed absent today: no such path, no worktree-registry entry. **This does affect provenance** — it is why the `suite_pin.*` → commit binding is TRANSCRIPT-ONLY rather than EXPLICIT. The artifacts it produced survive and are preserved. |

## 4. Transcripts

| Artifact | Status | Detail |
|---|---|---|
| `948b3666-670c-4ce4-951f-ff0d9a9b4562.jsonl` (3,388,079 B) | `PRESERVED_PRIVATELY` | The R1-FINAL session transcript. Private conversation content, so not published here. Held in the private tier; hash recorded in this archive and in README §1.3. Sole evidence for three recovered claims. |
| 2 tool-result files under `948b3666…/tool-results/` | `PRESERVED_PRIVATELY` | Referenced by the transcript. Same treatment. |
| Transcript for the session that produced `r1-final-evidence/` | `NOT_FOUND` | The 58-document and 4-document runs left no transcript. All 28 transcripts in the store were searched during recovery; that session's directory does not exist. **This affects provenance**: those runs are auditable only from their own outputs, scripts and pre-registration — which are internally strong (each `execution.json` names its checkout; `run_document.py` asserted commit, clean tree and PDF hash before opening any file) but have no independent command record. No hash or reference exists elsewhere. |
| Other session transcripts in the store | `EXCLUDED_BY_SCOPE` | Not R1-FINAL execution evidence. |

## 5. Repository state

| Artifact | Status | Detail |
|---|---|---|
| `wip/2026-09-20-repository-safety` (`e8517ee57365fc0799052d696f851fc25906a6b5`) | `EXCLUDED_BY_SCOPE` | Considered because it is a live branch in the same repository and is named in scope §17. Explicitly held **outside** the public R1 evidence package by scope §18. It is an unrelated WIP snapshot and is referenced by no R1 artifact. The commit SHA is recorded here so the exclusion is auditable; the branch itself is untouched. |
| `arpipe/patterns.py` as executed on 2026-09-17 | `NOT_RECOVERABLE` | The file was dirty in the 2026-09-17 porcelain, so the executed bytes were never committed and no copy survives. Searched during recovery; unchanged by preservation. **This affects provenance** for the historical baseline side: the exact 2026-09-17 source state cannot be fully reconstructed. Already recorded as an irreducible limitation in the R1 record. |
| Historical Tesseract version (2026-09-17) | `NOT_FOUND` | Re-confirmed at source during recovery: `reports/pm1_baseline.json` contains one occurrence of "tesseract" (the `escalator` config value) and zero of "leptonica" or "tessdata". No engine version is recorded anywhere permitted, so the §17 OCR-drift question remains NOT VERIFIABLE. |
| `scratchpad/A1_A6.md`, `scratchpad/amendment_body.md` | `EXCLUDED_BY_SCOPE` | Working drafts of records that were committed at `383fa792` and `e86d755`. Superseded by the committed versions, which are the authoritative text. Classified `PUBLIC_SAFE`; hashes in the manifest. |
| Any HOLDOUT material | `NOT_REQUIRED_FOR_PROVENANCE` | No HOLDOUT document was executed, read or copied. `universe.json` records HOLDOUT only as a row count (54) and as disjointness columns. The public archive was scanned for HOLDOUT paths after copying: zero hits. |
