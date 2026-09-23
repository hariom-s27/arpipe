# Phase 4 — B1/B3 factual errata (append-only)

**Status:** DOCUMENTATION CORRECTION RECORD. **This file contains no B1–B8 decision.**
Nothing here adopts, closes, amends or ratifies any B item. All eight items remain
`PENDING_AUTHOR_DECISION` in the unchanged Phase 2.1 register.

**Base commit:** `112d8297837f72881ead46ca2d9fb0735d10b3a1` (Phase 3 / P1 package).
**Branch:** `phase4-b1-b8`.

**Provenance rule applied.** `docs/experiments/PHASE2.1_B1_B8_DECISION_REGISTER.md` is
**not modified**. The historical wording is preserved verbatim below and corrected here
by append-only erratum, following the existing project convention in
`docs/experiments/PHASE2.1_PROVENANCE_CORRECTIONS.md` (`ERRONEOUS-QUOTED:` prefix).

## Recomputation basis

All values below were recomputed in this worktree from the frozen artifacts, not copied
from any prior document. Read-only; no detector, OCR, rendering or extraction was run.

| Artifact | SHA-256 | Role |
|---|---|---|
| `artifacts/t0_4/benchmark_manifest.json` | `d1eb3042c82900e345541ef6b7afbba95a6d7d8dc2e7948e5d610eaf89912f15` | Track A 475-unit population; source for E-1, E-2 |
| `configs/t0_4/oracle_routing_spec.json` | `d5aa91eb161cc04eb06fd20edc5941e88e9dcdcc70c71d17e2c259d3a625fbc3` | Oracle eligibility predicate text |
| `configs/t0_4/sampling_spec.json` | `412e040e9bcdc3915110906cd66d38a025e3aaad3f1f12bf31bf32327e17375c` | Sampling stratum priority |
| `reports/legacy_font_corpus_measurement.csv` (git blob `a8004593`) | blob-addressed, read via `git cat-file` | P-B3 per-page record, 37,917 rows; source for E-3.2 |
| `reports/legacy_font_corpus_measurement.md` (git blob `ceb14c31`) | blob-addressed, read via `git cat-file` | P-B3 report; population fingerprint |

The two P-B3 reports are **HISTORICAL / NOT CURRENTLY REPRODUCIBLE**: they are read as
committed historical detector output. Reading them does not promote their contents to
VERIFIED, and no P-B3 rerun was performed. They are not Gold.

---

## E-1 — B3 literal oracle split correction

**Evidence status: REPO-VERIFIED (independently recomputed).**

### Historical wording (preserved, unchanged in source)

`docs/experiments/PHASE2.1_B1_B8_DECISION_REGISTER.md`, section `B3 — Oracle Routing
Population Specification`, `verified_state`, line 109:

> Literal reading: 79 units (FIT: 50, VALIDATION: 29) and completely excludes all 42
> native-control units.

### Correction

    ERRONEOUS-QUOTED: FIT 50 / VALIDATION 29
    CORRECTED:        FIT 52 / VALIDATION 27

**Erratum (one line):** the B3 literal-reading split is FIT 52 / VALIDATION 27, not
FIT 50 / VALIDATION 29; the total of 79 units and the exclusion of all 42 native-control
units are both correct as recorded.

### Source and method of recomputation

Source: `artifacts/t0_4/benchmark_manifest.json` → `track_a.units` (475 records,
`unit_key = [document_id, page_number]`).

Predicate, applied literally as written in `oracle_routing_spec.json` — `condition_labels`
read as condition labels:

    split in {FIT, VALIDATION}
      AND condition_labels INTERSECT {scanned, broken_text, vector_text,
                                      legacy_font_candidate, native_clean_control}
          is non-empty

Result: **79 units total — FIT 52, VALIDATION 27.**

Matched-label decomposition (units may carry more than one label):
`scanned` 52, `broken_text` 15, `legacy_font_candidate` 15, `vector_text` 12,
`native_clean_control` 0.

Corroborating counts, also recomputed and **matching** the historical record:

- `native_clean_control` as a **condition label**: 0 of 475. (Register correct.)
- `native_clean_control` as a **sampling stratum**: 60 of 475; 42 in FIT/VALIDATION.
  (Register's "42 native-control units" correct.)
- Stratum reading: 79 + 42 = **121**. (Register correct.)

### Scope limit of this erratum

This corrects an arithmetic split only. It does **not** decide B3, does not select
between the literal and stratum readings, does not choose an estimand, and does not
approve any oracle population. `DEC-B3.selected_option` remains `null`.

### Explicitly NOT affected: the "50" in B4

`DEC-B4.verified_state` separately states "50 of 79 literal oracle units (63.3%)"
beginning with hex 0–3. That is a different quantity that coincidentally equals the
erroneous FIT count. It was recomputed independently and is **CORRECT**:

| B4 statistic | Recomputed | Register | Verdict |
|---|---:|---:|---|
| units with `selection_rank` hex prefix 0–3, all 475 | 355 (74.7%) | 355 (74.7%) | MATCH |
| units with `selection_rank` hex prefix 0–3, literal 79 | 50 (63.3%) | 50 (63.3%) | MATCH |

No B4 erratum arises. Do not propagate the E-1 correction into B4's figures.

---

## E-2 — Provenance of the figure "106"

**Evidence status: INFERRED provenance / REPO-VERIFIED arithmetic.**

### Where "106" appears

- **Conversational and task/instruction history**, and historical decision material
  supplied as task context.
- **It does not appear** as an authoritative committed statistic. A search of `docs/`
  and `configs/` at `112d8297` returns no occurrence of 106 as an oracle, unit,
  eligibility or population count. (The only textual matches are incidental substrings
  inside SHA-256 hash digests.)
- `17_B1_B8_DECISION_SHEET.md`, one possible historical locus, is
  **NOT FOUND — UNVERIFIED / NOT PRESENT IN WORKTREE**, as already recorded at
  `docs/experiments/PHASE2.1_CLOSEOUT.md:34`. Its contents cannot be checked here.

### How it reproduces

    121 (stratum reading)  -  15 (hybrid units inside stratum native_clean_control,
                                  restricted to split in {FIT, VALIDATION})
    = 106

Recomputed from `benchmark_manifest.json`:

| Quantity | Value |
|---|---:|
| literal reading (E-1) | 79 |
| `sampling_stratum == native_clean_control` and split in {FIT, VALIDATION} | 42 |
| stratum reading (79 + 42) | 121 |
| of those 42, `representation_class == hybrid` | **15** |
| of those 42, `representation_class == native_ok` | 27 |
| 121 − 15 | **106** |

The subtraction reproduces exactly. The hybrid count is 15 under **both** the
`representation_class` and the `condition_labels` reading, so the figure is not
sensitive to which field is used.

Related and distinct: across **all** splits, the `native_clean_control` stratum contains
**22** hybrid units (and 38 `native_ok`). That 22 is the figure recorded under P2-04 and
quoted in `DEC-B3.verified_state`; it is correct and is **not** the 15 used above. The
difference is the split restriction.

### Status statements

- "106" is a **derived conversational/historical figure**.
- It is **NOT** an authoritative frozen statistic.
- It is **NOT** a Gold population.
- It is **NOT** an adopted B3 decision, nor evidence for one.
- It is neither deleted nor endorsed here. It is recorded so that a later reader can
  recognise where it came from and decline to treat it as frozen.

---

## E-3 — B1 factual record

**Evidence status: REPO-VERIFIED (recomputed / read at `112d8297`), facts only.**

### E-3.1 — `legacy_font_candidate` is identical to `broken_text` by construction

In the relevant profiling evidence the two are the **same set**, not merely correlated:

| Level | `legacy_font_candidate` | `broken_text` | Identical? |
|---|---:|---:|---|
| Track A benchmark units (`benchmark_manifest.json`, 475 units) | 20 | 20 | **YES** — set equality; 0 in either difference |
| P-B3 corpus pages (`page_kind`, 37,917 rows) | — | 803 pages across 24 documents | matches the register's "803/803, 20/20" |

The register's B1 statement is therefore confirmed: the T0.4 sampling stratum
`legacy_font_candidate` carries no information beyond detector `broken_text`.

### E-3.2 — P-B3 detector-kind cross-tab for `legacy_font_confirmed` pages

Recomputed from `reports/legacy_font_corpus_measurement.csv` (git blob `a8004593`,
37,917 rows), cross-tabulating `legacy_class == legacy_font_confirmed` against the
ARPipe detector's `page_kind`:

| `page_kind` | `legacy_font_confirmed` pages | Share |
|---|---:|---:|
| **`digital`** | **225** | **51.49%** |
| `broken_text` | 211 | 48.28% |
| `hybrid` | 1 | 0.23% |
| `scanned` | 0 | 0.00% |
| `vector_text` | 0 | 0.00% |
| `blank` | 0 | 0.00% |
| **Total** | **437** | 100% |

For context (not requested; recorded to prevent misreading the row above):
`legacy_font_supported` (1,638 pages) cross-tabulates as `digital` 1,618,
`hybrid` 7, `blank` 11, `scanned` 2.

**Factual consequence, stated without interpretation:** under the historical P-B3
predicate, a majority of `legacy_font_confirmed` pages carry detector kind `digital`.
`PageKind.DIGITAL` is not a member of `NEEDS_OCR` (`arpipe/triage.py:284-285`), so those
pages are read from the text layer and are not reached by the `broken_text → OCR` route.

**Evidence limits that must travel with this table.** The P-B3 `confirmed` category
combines a font-name heuristic with page-level corruption; it is **not** forensic proof
that the named font caused the corruption, and it is **not** Gold. The cross-tab is
HISTORICAL detector output against HISTORICAL profiling output. It establishes a
recorded co-occurrence, nothing more.

### E-3.3 — `verify._window_is_legacy_font` is a quarantine heuristic, not the router

| Fact | Evidence |
|---|---|
| The function exists | `arpipe/verify.py:570` |
| Its only caller is `looks_like_wrong_language` | `arpipe/verify.py:620` |
| That function is applied to already-extracted MD&A text, for wrong-language quarantine | `arpipe/pipeline.py:321` (`verify.looks_like_wrong_language(mda_text)`); `arpipe/verify.py:84` labels it "wrong-language quarantine" |
| It is **not** the production routing class or router | `arpipe/triage.py` does not import `arpipe/verify.py` (imports at `triage.py:18-27` are `math`, `statistics`, `typing`, `pymupdf`, `.models`, `.patterns`) |
| There is no `legacy_font` page class | `PageKind` (`arpipe/models.py:15-22`) has exactly six members: `DIGITAL`, `SCANNED`, `HYBRID`, `BROKEN_TEXT`, `VECTOR_TEXT`, `BLANK` |

The presence of a legacy-font heuristic in `verify.py` must not be cited as evidence that
a legacy-font routing class exists. It runs downstream of routing, on output text.

### E-3.4 — The hybrid/blank class-to-route mapping attributed to B1 by P2-17 is absent from B1/B2

**P2-17** (`docs/experiments/PHASE2_FOUNDATION_INTEGRITY_FINDINGS.json`) records the
hybrid/blank routing-documentation conflict and assigns it:

> **repair:** "None. Both sources recorded; the choice belongs to the author (B1)."
> **owner_phase:** "Author decision (B1) then Phase 4/5"

**The actual B1 decision text does not contain that mapping.** `DEC-B1`'s `question`,
`verified_state`, `recommended_current_contract` and `interpretation_constraint` concern
only: the `legacy_font` class, the REMAP lane, `broken_text → OCR`, and legacy occurrence
as a forensic question. Across the whole of the `B1` and `B2` register sections, the
tokens `hybrid` and `blank` occur exactly **once**, inside `DEC-B2.verified_state`, and
there only as a description of the current `if/elif` order in `arpipe/triage.py:_classify`
(`blank → broken_text → {scanned, vector_text, digital} → hybrid → digital`). That is a
statement of existing code behaviour, not a class-to-route decision.

**Recorded facts about hybrid and blank (not a decision):**

- `PageKind.HYBRID` is a member of `NEEDS_OCR` (`arpipe/triage.py:284-285`), i.e. code
  OCRs hybrid pages; `arpipe/CLAUDE.md` and `arpipe/models.py:19` describe hybrid as
  "read text, OCR the image". P2-17 records these two sources as conflicting and
  explicitly does **not** resolve them.
- `configs/t0_4/metrics_spec.json` `ROUTING.classes` lists `native_ok`, `legacy_font`,
  `broken_text`, `scanned`, `vector_text` — omitting `hybrid` and `blank`, and including
  `legacy_font`, which has no `PageKind` and no producer.
- Per P2-17, 157 of 475 units (33%) sit in representation classes with no ROUTING class.

**Consequence for provenance, not for policy:** an author answering `DEC-B1` as written
would not thereby decide hybrid/blank routing. If the author intends B1 to also settle
hybrid/blank, that is a **scope extension of B1** and must be stated as such. This
erratum does not extend it.

### E-3.5 — Mandatory interpretation constraint

The facts in E-3 **do not** prove that real legacy-font pages are absent from the corpus.

- E-3.1 establishes a redundancy between a sampling stratum and a detector label. It says
  nothing about real legacy encoding.
- E-3.2 is historical heuristic output, not forensic proof of mechanism.
- E-3.3 establishes where a heuristic lives in the code, not what the corpus contains.
- Genuine legacy-font occurrence in the ARPipe corpus remains **UNRESOLVED**, exactly as
  `DEC-B1.empirical_status` records. `legacy_font_candidate` must not be read as a
  prevalence estimate.

---

## Register status after this erratum

| Item | Status | Changed by this file? |
|---|---|---|
| B1 | `PENDING_AUTHOR_DECISION` | No |
| B2 | `PENDING_AUTHOR_DECISION` | No |
| B3 | `PENDING_AUTHOR_DECISION` | No |
| B4 | `PENDING_AUTHOR_DECISION` | No |
| B5 | `PENDING_AUTHOR_DECISION` | No |
| B6 | `PENDING_AUTHOR_DECISION` | No |
| B7 | `PENDING_AUTHOR_DECISION` | No |
| B8 | `PENDING_AUTHOR_DECISION` | No |

`PHASE2.1_STATUS = WAITING_FOR_AUTHOR_DECISIONS` is unchanged.
`docs/experiments/PHASE2.1_B1_B8_DECISION_REGISTER.md` is byte-identical to `112d8297`.
