# ARPipe Evaluation & Split Protocol

*Protocol established 12 September 2026 (seed: 20260912). Queue split corrected
12 September 2026 after 5 already-labelled documents, including one confirmed
`contaminated=true` document (SAIL FY2011), were found to have leaked into
`labels_holdout_queue.csv` in the first version of this split.*

---

## 1. Purpose and Principles

ARPipe extracts the Management Discussion & Analysis (MD&A) section from Indian corporate annual reports. Accurate evaluation requires a strict boundary between development/tuning data and evaluation holdout data.

Self-referential scoring and "train-on-test" contamination invalidate headline metrics. This protocol defines the boundary rules governing development, labelling, threshold fitting, and reporting.

---

## 2. Dataset Partitions & Queues

### Fit / Development Set (`labels_fit.csv` & `labels_fit_queue.csv`)

- **`labels_fit.csv`**: The 20 historical P11 documents. All 20 are spent as
  holdout candidates because they have been repeatedly inspected and audited
  (this file's whole history is public in this repo's commits). Two are
  marked `contaminated=true` because they were the specific documents a rule
  was written against:
    - **SAIL FY2011** (`INE114A01011`): P27's `is_cross_reference_pointer`.
    - **KRBL FY2014** (`INE001B01026`): P25's outline-target prose validation.
  The remaining 18 are `contaminated=false` -- never used to tune a rule, but
  still ineligible as a holdout because they've been read and re-scored
  multiple times during this audit.
- **`labels_fit_queue.csv`**: **92** unlabelled candidates, eligible for
  future fit-set labelling.

### Holdout Set (`labels_holdout.csv` & `labels_holdout_queue.csv`)

- **`labels_holdout_queue.csv`**: **45** unlabelled candidates, eligible for
  future *blinded* holdout labelling.
- **`labels_holdout.csv`**: Once labelled via `arpipe label`, these documents
  form the blinded holdout set. Currently empty (0 rows) -- nothing has been
  holdout-labelled yet.

**How the queues were built.** `to_label.csv` (the 154-document stratified
sample from `sample_for_labelling`) was swept for candidates before checking
whether any of them were already in `labels_fit.csv` -- 17 of the 20 P11
documents turned out to also be present in `to_label.csv` (it samples from
the same underlying store, with no knowledge of what's already labelled).
Those 17 were **excluded** from the queue pool first, leaving 137 genuinely
unlabelled candidates. Those 137 were then split 2/3 fit (92) / 1/3 holdout
(45) **stratified by (era, cap_band, doc_kind)** with a fixed seed
(`20260912`, recorded per-row in `split_seed`) -- a pure random split over
an already-stratified sample can easily leave a whole cell with zero holdout
representation by chance; stratifying the split preserves coverage across
every populated cell (verified: zero cells with 2+ candidates end up with
zero holdout representation).

**Rule**: Only `labels_fit.csv` and `labels_fit_queue.csv` may be inspected
document-by-document when developing algorithms, tuning thresholds, creating
regex patterns, or debugging failures.

**Rule**: Documents in the holdout set may be **SCORED**, but **MUST NOT** be
inspected document-by-document.
  - If a holdout document fails an evaluation, record that it failed.
  - **Do NOT open the PDF to inspect why it failed and then write a rule or
    tune a threshold for it.**
  - If a developer opens and inspects a holdout document to diagnose or write
    a fix, that document is permanently contaminated. It must be removed
    from `labels_holdout.csv` and moved permanently into `labels_fit.csv`
    with `contaminated=true`.

---

## 3. Ground Truth Verification Requirement

- **`verified_by="read_pdf"` is mandatory.**
  - A document only enters scored metrics (accuracy, IoU, Pk, WindowDiff) if
    `verified_by == "read_pdf"`.
  - Rows with `verified_by="copied_from_run"` (pipeline predictions adopted
    without independent human reading) or `verified_by="unknown"`
    (provenance unrecorded) are strictly excluded from scoring.
  - Interactive labelling via `arpipe label` automatically stamps new
    ground-truth entries with `verified_by="read_pdf"`.

---

## 4. Evaluation CLI & Holdout Access Logging

Run evaluation via the unified CLI command:
```powershell
arpipe evaluate --split fit|holdout|both
```
- **`--split fit` (default)**: Evaluates `labels_fit.csv` (or fallback
  `labels.csv`). Safe for repeated iterations during development.
- **`--split holdout`**: Evaluates `labels_holdout.csv`.
  - **Warning**: A holdout evaluated dozens of times ceases to be a blinded
    holdout.
  - When `--split holdout` or `--split both` is invoked, the harness prints
    a visible one-line warning naming the date and git commit:
    ```
    WARNING: Scoring holdout set on <timestamp> (git commit: <commit>). Logged to eval_holdout_log.csv.
    ```
  - An entry is appended to `eval_holdout_log.csv` recording the timestamp,
    git commit, split, and document count.

---

## 5. OCR & Ground-Truth Labelling Notes

- **Tesseract OCR Engine**:
  - Tesseract is installed at: `C:\Program Files\Tesseract-OCR\tesseract.exe`
  - It may not be on the global `PATH` in every shell. Scripts and workers
    should check the full absolute path rather than assuming a bare
    `tesseract` call will resolve.
- **Live Dataset Cross-Check**:
  - A 194-document dataset with OCR results and triage metadata already
    exists in `live_dataset/manifest.jsonl`.
  - Useful for cross-checking candidate properties, cap bands, and document
    kinds before running intensive jobs -- but note it was produced by
    whatever pipeline commit was checked out when it ran; treat its `span`
    values as a real prediction, not as ground truth.

---

## 6. Known limitation, not yet fixed

Section 2's queues were rebuilt once already (see the note at the top of
this file) after a leak was found. If `to_label.csv` is ever regenerated or
re-sampled, the same exclusion-then-stratify procedure must be repeated
against whatever is in `labels_fit.csv` / `labels_holdout.csv` **at that
time** -- documents hand-labelled into either file after this protocol was
written are not automatically excluded from a future re-sample.
