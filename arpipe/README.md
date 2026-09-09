# arpipe — Indian annual-report → MD&A pipeline (FY2010–FY2025)

A reference implementation of the architecture in the accompanying plan.
It collects annual reports for Indian listed companies, decides **per page**
whether text can be read from the PDF or must be OCR'd, locates the
Management Discussion & Analysis section, verifies it belongs to the right
company and financial year, and writes a structured corpus.

```
dataset/
├── companies/ACME_INDUSTRIES_LIMITED__INE123A01016/
│   ├── 2015/
│   │   ├── annual_report.pdf     # hardlink into blobs/, costs no extra disk
│   │   ├── mda.txt               # the deliverable
│   │   ├── mda.json              # span, method, verification, QC metrics
│   │   └── document.json         # source URL, sha256, page count, producer
│   └── 2016/ ...
├── manifest.jsonl                # append-only, one row per processed document
└── manifest.parquet              # snapshot for analysis
store/
└── blobs/ab/cd/abcd….pdf         # content-addressed, deduplicated PDFs
```

## Why it is shaped this way

**Triage is per page, not per document.** A 250-page report with 12 scanned
pages costs 12 OCR pages here, not 250. Triage reads only the PDF object
model — no rendering — so it runs in ~50 ms for a digital report and ~250 ms
for a fully scanned one.

**Locate before you OCR.** The MD&A is 3–25 pages of a 150–400 page document.
The pipeline finds the section using free signals (bookmarks, contents page,
typographic headings, digital pages), OCRs a 1-in-6 index sample only if that
fails, and only then OCRs the located span at full quality. On a fully
scanned report this turns ~300 OCR pages into ~35.

**Every extraction carries its own evidence.** `mda.json` records which of the
five location strategies won, what the other four said, the CIN/ISIN/name
match, the fiscal-year evidence, and QC metrics. A text file with no
provenance is not a dataset.

**Failures are loud.** Section leakage into the auditor's report, over-long
spans, degenerate VLM output, name or year mismatches all downgrade
confidence to `low` and keep the row out of the clean corpus rather than
silently poisoning it.

## Install

```bash
pip install -r requirements.txt
sudo apt-get install -y tesseract-ocr tesseract-ocr-hin qpdf   # OCR + repair
```

## Run

```bash
python -m arpipe.cli universe --out companies.csv
python -m arpipe.cli discover --companies companies.csv --out reports.jsonl \
        --from-year 2010 --to-year 2025 --use-screener
python -m arpipe.cli fetch    --manifest reports.jsonl --root store --workers 4
python -m arpipe.cli triage   --root store           # cost forecast, no OCR
python -m arpipe.cli extract  --root store --out dataset --companies companies.csv
python -m arpipe.cli audit    --out dataset
```

Add a GPU OCR rung by pointing at any OpenAI-compatible server:

```bash
export ARPIPE_VLM_URL=http://gpu-box:8000
export ARPIPE_VLM_MODEL=PaddlePaddle/PaddleOCR-VL
python -m arpipe.cli extract --root store --out dataset --vlm-url $ARPIPE_VLM_URL
```

## Modules

| module | responsibility |
|---|---|
| `universe.py` | company master; ISIN as the stable key; NSE symbol-change chaining |
| `discover.py` | NSE / BSE / screener adapters → per-year candidate URLs |
| `fetch.py` | polite per-host rate limiting, zip unwrapping, qpdf repair, CAS store |
| `triage.py` | per-page routing: digital / scanned / hybrid / broken-text / vector-text; script ID; column count |
| `textlayer.py` | XY-cut reading order, de-hyphenation, running-header removal |
| `ocr.py` | escalation ladder (tesseract → self-hosted VLM → cloud) with a quality gate and a VLM repetition guard |
| `segment.py` | five MD&A location strategies + arbiter + boundary refinement |
| `verify.py` | CIN/ISIN/name identity, fiscal-year evidence, SEBI-era consistency, section QC |
| `store.py` | output tree, manifests, resumability |
| `pipeline.py` | the locate-then-OCR ordering that makes the cost model work |

## Tests

```bash
python tests/make_fixtures.py fixtures   # builds 6 synthetic annual reports
python -m pytest tests -q
```

The fixtures reproduce the real failure modes: two-column bodies, contents
pages whose dot leaders OCR into junk (`Management's Discussion and Analysis
..............:006`), fully scanned reports, and hybrid reports where only a
band of pages is scanned.

## Known limits of this scaffold

* `discover.py`'s BSE adapter needs the live response shape confirmed against
  the current `api.bseindia.com` payload; the NSE adapter matches the current
  `/api/annual-reports` schema.
* No table extraction yet — see the plan's §7 for the Camelot/gmft/TATR
  routing that belongs in a `tables.py`.
* The LLM adjudication rung is wired (`call_llm` injection point in
  `segment.from_llm`) but no provider client ships here.
* Thresholds in `triage.py` and `configs/default.yaml` are hand-set. They
  should be re-fit against a labelled sample of ~300 real filings before a
  full run; that labelling exercise is step 1 of the plan's Phase 1.
