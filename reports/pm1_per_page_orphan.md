# PM1 — Per-page `orphan_start_frac` + `arpipe orderqc`

**84 of 194 documents have at least one page with `orphan_start_frac > 0.03` while the document-level score remains `<= 0.03`.**

Measurement/diagnostic task only. No production behavior changed: MD&A candidate
detection, ranking, arbitration, reading order, `_column_cut`, extracted text, MD&A
boundaries, grading, confidence, acceptance/rejection, OCR routing/thresholds,
`ORPHAN_START_FRAC_MAX`, reason-code semantics, verification, document identity/year
logic, and manifest semantics are all unchanged and verified unchanged (Section B).

---

## A. Implementation

### Files changed (production code, all additive)

| File | Change |
|---|---|
| `arpipe/verify.py` | Refactored `_reconstruct_paragraphs` into a page-tag-carrying `_reconstruct_paragraphs_tagged` (byte-identical output for the untagged case); refactored `order_quality`'s inline scoring loop into a shared `_score_paragraphs` helper (byte-identical output). Added `order_quality_by_page`, `pages_over_diagnostic_threshold`, `document_hides_bad_page`, and two new constants: `PAGE_ORPHAN_DIAGNOSTIC_THRESHOLD = 0.03` and `PAGE_ORPHAN_MIN_PARAGRAPHS = 2`. `order_quality`'s signature, return value, and the existing `ORPHAN_START_FRAC_MAX` gate are untouched. |
| `arpipe/textlayer.py` | Added `page_has_full_width_block(path, page_no)`, a diagnostic-only reuse of the existing `COLUMN_FULLWIDTH_FRAC` threshold and `_blocks()` geometry. Nothing else changed. |
| `arpipe/pipeline.py` | After `mda_text` is built (unchanged), added a block that calls `verify.order_quality_by_page()` on the same per-page `ordered`/`span_pages` data already computed for `mda_text`, and adds two new keys (`orphan_start_frac_pages`, `orphan_start_frac_pages_min_paragraphs`) to `res.qc` via dict-spread, *after* `grade`/`reasons`/`vrep` were already computed from the pre-existing `qc` dict. Nothing upstream of that point (locate, OCR, verify, grade, build_reasons, store.write_year's span/text writing) was touched. |
| `arpipe/cli.py` | Added `cmd_orderqc` and the `orderqc` subparser. No existing command's code was touched. |

### Metric source

The page-level metric is **the same calculation** the document-level `orphan_start_frac`
already uses (`verify.order_quality`), not a re-derived or re-averaged one:

- `_reconstruct_paragraphs_tagged` is the *only* paragraph-reconstruction algorithm in
  the module now; `_reconstruct_paragraphs(text)` is a one-line wrapper over it
  (`[(ln, None) for ln in text.split("\n")]`, tags discarded on return). A dedicated
  test (`test_page_reconstruction_matches_document_reconstruction_on_real_fixture`)
  reconstructs a real fixture's MD&A span both ways and asserts the paragraph lists —
  and therefore every orphan/dangling flag — are identical.
- `_score_paragraphs` (the orphan/dangling test itself: `_orphan_start`, `_SENT_END_RE`,
  `_looks_like_heading`, `_dangling_tail`) is called by both `order_quality` and
  `order_quality_by_page`. There is exactly one implementation of the test.
- `order_quality`'s prose-only basis, `orphan_basis`/`orphan_gate_version` labels, and
  the `< 5` paragraphs special case are all untouched.

### Page attribution rule

> A reconstructed paragraph is attributed to the **physical page containing its first
> non-whitespace source line** (equivalently, its first source character).

Page provenance is threaded through reconstruction itself: each source line carries its
originating physical page as a tag *before* paragraphs are assembled from lines, and a
paragraph inherits the tag of whichever line started it. Page membership is never
recovered afterward from character offsets in the joined `mda_text`.

In practice, this reduces to a clean rule with no ambiguous cross-page case: pipeline.py
builds `mda_text` as `"\n\n".join(ordered)`, one prose string per span page; the
document-level `_reconstruct_paragraphs` already treats the blank line this join inserts
between pages exactly like any other blank line — a forced paragraph break. So no
paragraph the document-level metric has ever scored actually straddles two pages, and
the page-level reconstruction (which reproduces the identical blank-line join before
tagging) inherits that property for free. A paragraph that *looks* like the continuation
of a sentence begun on the previous page is, and always was, scored as its own paragraph,
attributed to the page it physically starts on — this is exactly the “cross-page
paragraph attribution” case, verified in `test_cross_page_paragraph_attribution`.

### Page array schema

```json
"qc": {
  "orphan_start_frac": 0.0192,
  "orphan_start_frac_pages": [null, null, 0.0, 0.087, null, ...],
  "orphan_start_frac_pages_min_paragraphs": 2
}
```

- Length = the document's total physical page count (`profile.n_pages`).
- Index `i` (0-based, in the JSON array) corresponds to **1-based physical PDF page `i+1`**.
- `null` = not measured: either outside the located MD&A span, or inside it but with
  fewer than `PAGE_ORPHAN_MIN_PARAGRAPHS` (= 2) reconstructed paragraphs attributed to
  that page (a rate from 0 or 1 paragraphs is a coin flip, not a stable estimate — never
  reported as a fabricated `0.0`).
- `0.0` = the page was measured and no orphan starts were observed on it.
- The existing document-level `qc.orphan_start_frac` field is unchanged, in place, and
  remains the regression oracle.

### Full-width-block rule

`textlayer.page_has_full_width_block(path, page_no)` reuses, unchanged, the exact
geometry test `_column_cut` already applies internally to decide a block masks the
gutter from `_gap_cut` (`b.w > COLUMN_FULLWIDTH_FRAC * text_w`, `COLUMN_FULLWIDTH_FRAC =
0.60`) — the documented mechanism behind the P16B column-split fallback. It returns
`None` when the page has no extractable block geometry (typically a scanned page, or the
`annual_report.pdf` copy is unavailable). It is called only by `arpipe orderqc`, only for
pages already flagged over the diagnostic threshold, against the page's own
`annual_report.pdf` copy already materialised by `arpipe extract` — never during
extraction itself, so it can never affect extraction behavior.

### `arpipe orderqc`

Reads the existing manifest (`store.load_manifest`) — never reruns extraction, OCR, or
segmentation. For every document with at least one page `> 0.03` (strict), prints every
qualifying page (company, fiscal year, document-level score, physical page, page score,
full-width-block verdict), ordered deterministically by `(company_id, fiscal_year,
physical_page)`. Reports the aggregate hiding count and full-width co-occurrence counts.
`--json PATH` writes the full findings + summary machine-readably.

---

## B. Regression against the frozen baseline

```
documents compared        = 194
orphan document score changes = 0
grade changes              = 0
confidence changes         = 0
reason changes             = 0
span start changes         = 0
span end changes           = 0
accept/reject changes      = 0
documents with any diff    = 0
```

Every one of the 194 documents in `reports/pm1_baseline.json` matches its
after-PM1 counterpart exactly on all seven tracked fields. See
`reports/pm1_regression_result.json` for the full per-field tally (raw, machine-checked).

**How the baseline was produced.** `reports/pm1_baseline.json` was captured by running
the *actual pre-PM1 code* (verify.py/textlayer.py/pipeline.py/cli.py's PM1 edits were
precisely reversed — restoring all four files to their exact pre-PM1 byte content,
confirmed by `grep -c PM1` returning 0 in each and by re-running the full test suite —
over the full 194-document `live_store` corpus, then the PM1 edits were reapplied and the
identical corpus was re-extracted for the "after" run). Both runs used the same
extraction tool (`tools/pm1_run_corpus.py`, itself unchanged production
`pipeline.process_document` distributed across worker processes for wall-clock reasons
only — `arpipe extract`'s own `ThreadPoolExecutor` is GIL-bound and would take
~8 hours on this corpus instead of ~8 minutes) and the same configuration
(`live_store`, `cohort_companies.csv`, `ARPIPE_OCR_WORKERS=1`, Tesseract-only escalator).
sha256 checkpoints of every file the pipeline imports but PM1 does not touch
(`segment.py`, `triage.py`, `patterns.py`, `config.py`, `ocr.py`, `store.py`,
`models.py`) were taken immediately before and after each run and are byte-identical
throughout — a concurrent, unrelated session was observed editing some of these files
during this work (see Caveats), but never mid-run.

Grade distribution, identical in both runs: `{"medium": 85, "high": 42, "low": 53,
"failed": 12, "quarantine": 2}` (127 accepted, 67 rejected) — and matches the
independently-recorded `reports/pb4_corpus_validation.json` baseline for this same
194-document corpus exactly.

---

## C. Page-level findings

```
documents measured       = 182   (194 total; 12 are mda_not_located -> no span, no qc.order_quality fields at all)
pages measured           = 2728  (non-null entries across all 194 orphan_start_frac_pages arrays)
documents with page > 0.03 = 135  (69.6% of measured documents)
total bad pages          = 706
```

---

## D. Aggregate hiding

```
documents with page > 0.03 but document score <= 0.03  =  84
```

84 of 194 documents (43.3% of the whole corpus, 62.2% of the 135 documents that have any
bad page at all) would read as clean on the document-level `orphan_start_frac` alone.

---

## E. Full-width diagnostic

```
bad pages with full-width block     = 429  (60.8% of bad pages)
bad pages without full-width block  = 199  (28.2% of bad pages)
bad pages not measurable            =  78  (11.0% - no extractable block geometry, e.g. a scanned page)
```

---

## F. Distribution

Measured page scores (`n = 2728`, non-null entries only):

```
min    = 0.0
P25    = 0.0
median = 0.0
P75    = 0.0312
P90    = 0.0833
P95    = 0.125
max    = 0.6471
```

---

## G. Interpretation

**How often the document aggregate hides a bad page.** Often. In 84 of 194 documents
(43.3%), the whole-document `orphan_start_frac` sits at or below the same 0.03 line used
to flag documents today, while at least one physical page inside that same document's
MD&A span exceeds it — in some cases considerably (the worst single page in the corpus
scores 0.6471). A document-level average is, by construction, diluted by every clean
page in the span; a 12-page span with one severely scrambled page and eleven clean ones
can average out to a small, unremarkable-looking document score.

**How concentrated the bad pages are.** Bad pages are not spread thinly across the whole
corpus — they cluster. 135 of 194 documents (69.6%) have at least one page over the
diagnostic threshold, but among only those 135 documents there are 706 bad pages total
(a mean of ~5.2 per affected document), while the median score across *all* 2728 measured
pages is exactly 0.0 and even the 75th percentile (0.0312) sits barely above the
threshold. That combination — most measured pages clean, but a majority of documents
carrying at least one page well past the gate — is the shape of a localized reading-order
failure (a handful of specific pages per document going wrong), not a general degradation
across every page a document contributes.

**How often the known full-width-block pattern co-occurs.** Often, but far from always.
60.8% of bad pages carry a block wider than 60% of the page's text band — the mechanism
`_column_cut` already exists to work around when it can. 28.2% of bad pages show no such
block at all, meaning whatever is driving those particular pages' scrambled order is not
captured by this one geometric signal. The remaining 11.0% could not be checked (typically
a scanned page with no extractable text-block geometry in the PDF object model). **No
causal claim is made from this co-occurrence** — a full-width block being present on a bad
page does not establish that it caused the bad page, only that the two are frequently
observed together.

No threshold was changed, no production gate was added, and no recommendation for a
production change follows from any of the above; this section is descriptive only, per
the task's explicit instruction.

---

## Tests

**Focused (`arpipe/tests/test_pm1_orderqc.py`): 19/19 passed.** Covers all 17 M1.10 items:
clean page (0.0); one orphan (expected fraction, cross-checked against `order_quality`);
page isolation; cross-page paragraph attribution; pages outside the span (absent from the
map, `None` after array-fill); insufficient-prose page (`None`, not a fake `0.0`);
document-level metric unchanged; page exactly at `0.030` not flagged (strict `>`); page
`>0.03` flagged; full-width block true/false (real pymupdf geometry) and `None` for an
out-of-range page; multiple bad pages all printed; hidden-aggregate case counted; an
already-bad document not double-counted as hidden; deterministic page ordering; JSON
round-trip preserves `null`; and a dedicated side-effect-free / equivalence test proving
the page-level reconstruction is byte-identical to the document-level one on a real fixture
(`B_twocol_toc.pdf`), so changing page telemetry cannot affect extraction behavior.

**Full suite (`pytest arpipe/tests -q`): 333 passed, 1 failed, 2 skipped** (336 collected).
The one failure, `tests/test_pipeline.py::test_p33_is_given_below_not_pointer`, is in
`segment.is_cross_reference_pointer` — a module PM1 never touches — and fails identically
whether the PM1 edits are present or fully reversed (verified directly, both ways). It is
pre-existing and out of scope for this task.

*A concurrent, unrelated Claude Code session was observed actively modifying this same
repository during this work (new files under `arpipe/tests/`, `tools/`, `reports/`; live
edits to `segment.py`/`triage.py`). One transient full-suite run briefly showed a second
failure, `test_pb2_candidate_body_script.py::test_b213_...`, in a test file that did not
exist earlier in this session and that exercises candidate-arbitration code PM1 never
touches; a later run (after that other session's edit presumably landed) showed only the
one pre-existing P33 failure. Neither failure is caused by, or related to, this task's
diff.*

---

## Repository integrity (M1.12)

```
segment.py behavioral logic changed by PM1  : NO   (file not edited by this task)
patterns.py changed by PM1                  : NO   (file not edited by this task)
ORPHAN_START_FRAC_MAX changed               : NO   (still 0.03, arpipe/verify.py:51)
OCR routing changed                         : NO
OCR thresholds changed                      : NO
MD&A spans changed                          : NO   (0 span_start/span_end changes, Section B)
candidate behavior changed                  : NO   (segment.py not edited)
grading changed                             : NO   (0 grade changes, Section B; verify.grade/build_reasons not edited)
acceptance changed                          : NO   (0 accept/reject changes, Section B)
194-document corpus changed                 : NO   (live_store/documents.jsonl sha256 identical before/after: see reports/pm1_baseline.json)
```

PM1 edited exactly four production files: `arpipe/verify.py`, `arpipe/textlayer.py`,
`arpipe/pipeline.py`, `arpipe/cli.py`. All additions; the only pre-existing function
bodies touched were `_reconstruct_paragraphs` (replaced by a one-line wrapper over a new
tagged version with proven byte-identical output) and `order_quality` (its scoring loop
extracted into a shared helper with proven byte-identical output) — both in
`arpipe/verify.py`. `git status` shows numerous *other* modified/untracked files in this
repository; none of them were touched by this task (they predate it or belong to the
concurrent session noted above).

## Deliverables

```
reports/pm1_baseline.json           immutable, 194 documents, frozen pre-PM1
reports/pm1_per_page_orphan.json    full findings + summary + interpretation
reports/pm1_per_page_orphan.md      this file
reports/pm1_regression_result.json  raw per-document regression diff (empty)
reports/pm1_orderqc_raw.json        raw `arpipe orderqc --json` output
arpipe/tests/test_pm1_orderqc.py    19 focused tests
tools/pm1_run_corpus.py             corpus extraction runner (process-parallel)
tools/pm1_build_baseline.py         builds reports/pm1_baseline.json (refuses to overwrite)
tools/pm1_regression_check.py       builds reports/pm1_regression_result.json
```
