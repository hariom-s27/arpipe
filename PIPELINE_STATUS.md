# ARPipe — pipeline status & gap analysis

**Checked:** 2026-09-10 · **Machine:** Windows 11, Python 3.14.3, venv at `arpipe/.venv`
**Verdict:** every stage runs end to end on **born-digital** PDFs. The OCR half of
the pipeline (scanned / hybrid / Hindi reports) cannot run on this machine and has
no automated test.

---

## 1. How to run it on this machine

Since **P19**, blob paths in `documents.jsonl` are stored relative to the store
root and resolved against `--root` at read time, so `extract` / `triage` /
`audit` run from **any** working directory and `--out` may be on **any** drive
(a cross-drive `--out` falls back to copying the PDF into the tree and records
`link_mode: copy` in `document.json`). Put the repo root on `PYTHONPATH` so the
package imports:

```bash
export PYTHONPATH=arpipe-0.1.0                 # or the absolute repo-root path
PY=arpipe-0.1.0/arpipe/.venv/Scripts/python.exe   # Windows venv

$PY -m arpipe.cli universe --out companies.csv
$PY -m arpipe.cli discover --companies companies.csv --out reports.jsonl \
      --from-year 2023 --to-year 2025 --limit 5 --use-screener
$PY -m arpipe.cli fetch    --manifest reports.jsonl --root live_store --workers 4
$PY -m arpipe.cli triage   --root live_store
$PY -m arpipe.cli extract  --root live_store --out live_dataset --companies companies.csv
$PY -m arpipe.cli audit    --out live_dataset
```

One machine-specific gotcha:

* `pytest` and `make_fixtures.py` need the repo root on `PYTHONPATH`
  (`PYTHONPATH=arpipe-0.1.0`, or `..` when run from inside `arpipe/`).

(The old "`--out` must be on the same drive as the store" gotcha is gone — P19
fixed the cross-drive crash; see §4 bug #1.)

---

## 2. Stage-by-stage verification (run today)

| Stage | Ran? | Evidence | Notes |
|---|---|---|---|
| `universe` | ✅ | 2,568 companies pulled from live NSE masters → `companies.csv` | NSE equity list + symbol-change chaining work |
| `discover` | ✅ | 12 candidate URLs for 2 companies, 2023–25, from `nse` + `screener` | **BSE source produced nothing** — see §3 |
| `fetch` | ✅ | 4/4 PDFs downloaded fresh from NSE into a new store; sha256 paths identical to the old store; hardlink dedup confirmed (`nlink` > 1) | polite host limiter, zip-unwrap present |
| `triage` | ✅ | 1,275 pages profiled: 3 digital + 1 mixed, 65 pages (5.1%) flagged for OCR | pure object-model read, no rendering, fast |
| `extract` (digital) | ✅ | 4/4 reports → `mda.txt` + `mda.json`, all graded **high**; MD&A located by heading (3) and TOC (1); 0 OCR pages needed; 5.2k–15.2k words each | this is the happy path and it is solid |
| `extract` (scanned) | ❌ | fixture `C_scanned.pdf` → `mda_not_located`, `confidence=FAILED` | no OCR engine → cannot read any page |
| `extract` (hybrid) | ⚠️ | fixture `D_hybrid.pdf` → span located via TOC but `n_words=0`, quarantined **LOW** | fails *loudly* (by design) but yields nothing |
| `audit` | ✅ | summarised 4-row manifest: `by_confidence {high: 4}`, `mean_words 9785` | reads manifest.jsonl / .parquet fine |

Real deliverable produced today: `arpipe/_demo_out/` — 4 MD&A extractions
(~39k words total) with full `mda.json` / `document.json` provenance.
39/39 unit tests pass (`PYTHONPATH=arpipe-0.1.0 pytest arpipe/tests -q`).

---

## 3. What's left — blocking a real crawl

### A. OCR path is entirely absent (highest priority)

Missing system binaries: **`tesseract` · `qpdf` · Ghostscript/`pdftoppm`**, and the
**`tesseract-ocr-hin`** language pack. Consequences:

* Any **scanned** report → `mda_not_located`, total loss.
* Any **hybrid** report where the MD&A falls in a scanned band → quarantined, 0 words.
* `pipeline.py` passes 2 (index-sample OCR), 3-refine (`refine_end` via OCR),
  full-span OCR, and the front-matter OCR fallback are all **unreachable and untested**.
* Bilingual PSU reports (Hindi + English) have no path at all.

When Tesseract raises (binary absent), `ocr.Escalator.run_page` swallows the error
and returns an empty page — so today the failure is silent at the OCR layer and
only surfaces later as "not located" / LOW. Acceptable for now, but it means the
5.1% OCR forecast from `triage` is currently 5.1% of **nothing**.

Fix: install the binaries (`choco install tesseract qpdf ghostscript` +
Hindi traineddata), then build an end-to-end test that runs
`pipeline.process_document` over `C_scanned.pdf` / `D_hybrid.pdf` / `E_bilingual.pdf`.

### B. BSE discovery is inert

* Every row in `companies.csv` has an **empty `bse_scrip`** (2,571/2,571). It is only
  populated from `universe --bse-json <file>`, which nothing supplies.
* `discover_bse` returns `[]` immediately when `bse_scrip` is missing, so BSE is
  effectively not a source — only NSE + screener are.
* Per the README, the BSE adapter's response shape also still needs confirming
  against the current `api.bseindia.com` payload.
* Net: ~3,000 BSE-only companies are unreachable, and NSE-listed companies have no
  BSE fallback when NSE is missing a year.

### C. `configs/default.yaml` is not wired to anything

`grep` finds **zero** references to `yaml` / `default.yaml` / any loader in the code.
`pyyaml` isn't even installed. Every threshold actually lives hard-coded in the
modules: `triage.py` (120 char/page, 0.55 image area, 0.02 mojibake…),
`ocr.quality_gate` (40 words, 0.72 conf…), `segment.py` (0.55 / 0.7 score gates,
60-page cap), `verify.py` (88 / 72 name-match). The plan calls all of these
"hand-set, re-fit against ~300 labelled filings first" — that labelling exercise
has not started.

### D. LLM adjudication rung (segment strategy S5) is unreachable

`segment.from_llm` exists and takes an injected `call_llm`, but
`cli.cmd_extract` never builds or passes one — `process_document(..., call_llm=None)`
always. There is no provider client and no `--llm` flag. Pass 3 in `pipeline.py` is
dead code from the CLI.

### E. No table extraction

No `tables.py`. `segment` flags `looks_like_tables` and QC can down-grade, but there
is no Camelot / gmft / TATR routing. MD&A prose is captured; embedded data tables
are flattened into text.

### F. AWS / cloud OCR rung not installed

`boto3` absent; `TextractBackend` untested. Rung 3 is code-only. (English-only
anyway — never route Hindi there.)

---

## 4. Bugs found today

1. **`store.link_pdf` cross-drive crash. — FIXED (P19).** Now `os.link` →
   `os.symlink` → `shutil.copy2`, catching `(OSError, ValueError)`, warning on
   copy, and returning the mode into `document.json` as `link_mode`.
2. **`fetch._repair` malformed qpdf command.** The primary call is
   `["qpdf", "--replace-input" if False else out, "--qdf", …, path, out]` —
   the `if False` leftover makes it `["qpdf", out, "--qdf", …, path, out]`, which
   qpdf rejects (two output positionals). It only works via the bare
   `["qpdf", path, out]` fallback in the `except`. → delete the dead ternary,
   pass `path` as input and `out` as output.
3. **`discover` `--use-bse` flag is a no-op.** argparse `action="store_true",
   default=True` → always on, can't be turned off. Harmless only because BSE
   returns nothing (§3B). → `default=False`.
4. **Import ergonomics.** Running `python -m arpipe.cli` still needs the repo
   root on `PYTHONPATH` (`No module named 'arpipe'` otherwise). The blob-path
   half of this is **fixed (P19)** — paths are store-root-relative and resolved
   against `--root`, so the cwd no longer matters. Still worth a `pyproject.toml`
   console-script or a top-level shim for the import.

---

## 5. Priority order

1. Install `tesseract` (+ `hin`), `qpdf`, Ghostscript → unlock the OCR path.
2. Add an end-to-end OCR test over the scanned / hybrid / bilingual fixtures.
3. ~~Fix bug #1~~ (done, P19). Fix bug #3 (one-line); #2 while you're in `fetch.py`.
4. Wire `configs/default.yaml` into a single `config.load()` used by every module.
5. Label ~300 real reports (era × cap band × scan quality) and re-fit every threshold.
6. Confirm the BSE adapter against a live payload; populate `bse_scrip` in `universe`.
7. Ship a `call_llm` provider + `--llm` flag for the residue.
8. `tables.py`.
