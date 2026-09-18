# P-M5 — Coverage Funnel

**Status: COVERAGE FUNNEL INCOMPLETE — DENOMINATOR NOT RELIABLY RECONCILED**
(arithmetic accounting is fully reconciled; a stage-ordering/monotonicity
violation blocks a clean PASS — see §7 and §11)

Base commit: `158a9eac48a3374a9506af8281acb93f49a37a0d` (158a9ea)
Branch: `pm5-coverage-funnel` · Worktree: `D:\sem_iitk\sem9\thesis\sep_week1\arpipe-pm5-coverage`
Analysis code: `tools/pm5_coverage.py`, `tools/pm5_tests.py` (uncommitted working-tree files in this worktree; sha256 recorded in `coverage.json`)
Data cutoff: `2026-09-17T10:25:19Z` (UTC) — see §1

---

## 0. What this document is

An audit of **coverage and attrition**, not extraction accuracy. It measures
how many of the company-years ARPipe was expected to cover at a frozen
snapshot actually survive each pipeline stage, and where they are lost. It
does not change discovery, fetch, verification, segmentation, OCR routing,
or acceptance rules, and does not retry, repair, or manually complete any
failed case.

---

## 1. Population definition and snapshot cutoff (Table A)

| field | value |
|---|---|
| Expected observation count | **576** (36 companies × 16 fiscal years, FY2010–FY2025) |
| Universe snapshot date | 2026-09-11T15:53:04+05:30 (`cohort_companies.csv` mtime) |
| Discovery snapshot date | 2026-09-11T15:57:27+05:30 (`cohort_reports.jsonl` mtime) |
| Manifest snapshot date | 2026-09-17T01:22:38+05:30 (`live_dataset/manifest.jsonl` mtime) |
| Data cutoff timestamp | **2026-09-17T10:25:19Z UTC** (moment the source files were pinned/hashed into `reports/pm5_source_snapshots/`) |
| Universe rule version | `pm5-v1` — see `pm5_expected_universe_snapshot.json.meta.universe_rule_version` |

**Why a "pin" timestamp, not a git commit, defines the cutoff.** The
company/discovery/fetch/extraction evidence this audit needs
(`cohort_reports.jsonl`, `live_store/documents.jsonl`,
`live_dataset/manifest.jsonl`) is `.gitignore`d — it lives only on disk in
the shared `arpipe-0.1.0` checkout, which P-M5 is explicitly forbidden from
using or modifying as a working directory. These files are **not** reachable
through any git SHA. Per the memory note that this worktree is concurrently
used by other sessions, each file was hashed immediately before and
immediately after copying it read-only into this worktree
(`reports/pm5_source_snapshots/`); all six hashes matched exactly (no torn
read, no concurrent write during the pin — see
`reports/pm5_source_snapshot_manifest.json`). Nothing written to those
source files after `2026-09-17T10:25:19Z` is reflected anywhere in this
audit. `arpipe-0.1.0` itself was never written to.

**Source provenance:**

| file | role | sha256 (pinned copy) | rows |
|---|---|---|---|
| `cohort_companies.csv` | EXPECTED (git-tracked, commit 158a9ea) | see `pm5_expected_universe_snapshot.json` | 36 |
| `cohort_reports.jsonl` | DISCOVERED | see `pm5_source_snapshot_manifest.json` | 1164 |
| `live_store/documents.jsonl` | DOWNLOADED | see `pm5_source_snapshot_manifest.json` | 194 |
| `live_dataset/manifest.jsonl` | IDENTITY / MDA_LOCATION / ACCEPTED | see `pm5_source_snapshot_manifest.json` | 194 |

---

## 2. Expected universe (Table A, §§2–6 of the task spec)

The denominator is derived **independently of any downstream outcome**:

```
expected = cohort_companies.csv (36 firms) × FY{2010..2025} (16 years)
         = 576 observations
```

`cohort_companies.csv` is the cap-band-stratified study cohort built by
`tools/select_labelling_cohort.py` (6 large + 8 mid + 10 small + 12 micro,
selected on `cap_band_current` before any discovery/fetch/extract was run).
FY2010–2025 is the study range declared in `README.md` and
`arpipe/CLAUDE.md` ("FY2010–FY2025"), applied uniformly to every cohort
company as a fixed protocol parameter — not derived from what discovery
later returned (discovery in fact returned candidates spanning exactly
2010–2025 for this cohort, confirming the range was applied as declared).

**No company-year was excluded from the denominator.** The frozen company
master carries no `listing_date` field, so there is no canonical evidence to
support a `not_listed_in_year` exclusion for any of the 576 combinations.
Per §39 (no denominator repair) and §3 (do not use downstream failure
reasons as exclusions), every one of the 576 observations is
`expected_flag=True`, `expected_reason=in_scope`. A company genuinely not
yet listed in an early FY simply fails at the DISCOVERY stage instead of
being excluded — this is the conservative, spec-compliant choice.

**Uniqueness:** `observation_id` (`{company_id}::FY{fy}`) and
(`company_id`,`FY`) are both unique by construction (Cartesian product over
36 distinct ISINs, confirmed distinct). Verified — see
`pm5_test_results.txt`.

Snapshot files: `reports/pm5_expected_universe_snapshot.csv` / `.json`
(frozen; all downstream funnel calculations read only from this file).

---

## 3. Funnel stage derivation — canonical evidence used

| stage | canonical evidence | flag definition |
|---|---|---|
| DISCOVERED | `cohort_reports.jsonl` | ≥1 discovery record for (company_id, fy_end) |
| DOWNLOADED | `live_store/documents.jsonl` | a `StoredDoc` row exists for (company_id, fy_end); `authoritative_download_artifact_id` = its `sha256` |
| IDENTITY_VERIFIED | `live_dataset/manifest.jsonl` → `verification` | `verification.company_ok AND verification.year_ok` (from `arpipe/verify.py verify()`) |
| MDA_LOCATED | `live_dataset/manifest.jsonl` → `span` | `span is not None` (from `arpipe/segment.py` via `pipeline.process_document`) |
| ACCEPTED | `live_dataset/manifest.jsonl` → `ok` | `ok` (== `confidence in {high, medium}`, set by `arpipe/pipeline.py: res.ok = grade in ("high","medium")`) |

No new identity, segmentation, or acceptance rule was invented for M5; each
flag reads a field the frozen pipeline already persists.

No duplicate (company_id, fy_end) exists in `documents.jsonl` or
`manifest.jsonl` (checked) — multi-source discovery never produces more than
one downloaded/processed artifact per observation in this snapshot, so no
double-counting logic was needed. `authoritative_artifact_id` (download,
`documents.jsonl.sha256`) and `authoritative_artifact_sha256` (extraction,
`manifest.jsonl.sha256`) match exactly for every observation that reaches
both stages (checked, 0 mismatches) — lineage is consistent.

---

## 4. ⚠️ A real, evidence-based stage-ordering violation

The task's fixed funnel order is
`EXPECTED → DISCOVERED → DOWNLOADED → IDENTITY_VERIFIED → MDA_LOCATED → ACCEPTED`,
which conceptually requires `MDA_LOCATED ⊆ IDENTITY_VERIFIED`
(`N_mda_located ≤ N_identity_verified`).

**The frozen pipeline's actual control flow runs in the opposite order.**
In `arpipe/pipeline.py: process_document()`, `segment.locate()` (which
produces the MD&A `span`) runs **first**; `verify.verify()` (which produces
`company_ok`/`year_ok`) is only ever called **after** a span was found, using
text drawn from inside/near that span plus front matter. If `span is None`,
the function returns early and `verification` is never computed at all —
confirmed empirically: **0 of 194** processed documents have `verification`
populated with `span=None`, and **0** have `span` populated with
`verification=None`.

Consequence: **12 of 194** processed observations have a located MD&A span
(`mda_located=True`) whose identity/year verification did not both pass
(`identity_verified=False`) — all 12 are graded `low` and excluded from
`accepted`, so they do not corrupt the final corpus, but they do violate the
literal subset relationship the funnel order assumes:

```
N_mda_located      = 182
N_identity_verified = 170        <-- violates N_mda_located <= N_identity_verified
```

Per §25 of the task spec ("Do not alter stage membership to enforce these
inequalities... report the inconsistency and block completion"), this audit
**does not** redefine `mda_located` to be identity-gated (that would not be
the canonical segmentation signal `segment.py` actually produced), and does
**not** force reconciliation. The 12 affected `observation_id`s are exactly
the rows with `mda_located=True, identity_verified=False` in
`pm5_stage_table.csv`; each is still assigned `first_failed_stage=IDENTITY`
under the spec's fixed reporting order (§19), independent of the pipeline's
actual execution order, with `first_failed_reason_code=REASON_CODE_MISSING`
(no verify.py reason code exists for "not attempted") since `verification`
is null for these 12.

**This is the reason the final verdict is INCOMPLETE rather than PASS**,
even though the arithmetic accounting identity (§7 below) fully reconciles.

---

## 5. Table B — Overall funnel

| stage | N | % of expected | loss from previous | transition loss rate | cumulative survival |
|---|---:|---:|---:|---:|---:|
| EXPECTED | 576 | 100.00% | — | — | 100.00% |
| DISCOVERED | 512 | 88.89% | 64 | 11.11% | 88.89% |
| DOWNLOADED | 194 | 33.68% | 318 | 62.11% | 33.68% |
| IDENTITY_VERIFIED | 170 | 29.51% | 24 | 12.37% | 29.51% |
| MDA_LOCATED | 182 | 31.60% | **−12** | **−7.06%** | 31.60% |
| ACCEPTED | 127 | 22.05% | 55 | 30.22% | 22.05% |

The negative "loss" at the IDENTITY_VERIFIED → MDA_LOCATED transition is the
direct numeric signature of §4's violation, not a data-entry error — it is
reported, not smoothed over.

By far the largest attrition is **DISCOVERED → DOWNLOADED (62.11%, 318
observations)**. See §8.

---

## 6. Table C — First-failure accounting

| first_failed_stage | first_failed_reason_code | N | % of all losses | % of stage losses |
|---|---|---:|---:|---:|
| DOWNLOAD | REASON_CODE_MISSING | 318 | 70.82% | 100.00% |
| DISCOVERY | REASON_CODE_MISSING | 64 | 14.25% | 100.00% |
| ACCEPTANCE | source_shredded | 27 | 6.01% | 62.79% |
| IDENTITY | mda_not_located | 12 | 2.67% | 50.00% |
| IDENTITY | year_unproven | 6 | 1.34% | 25.00% |
| ACCEPTANCE | span_truncated | 6 | 1.34% | 13.95% |
| IDENTITY | identity_unproven | 6 | 1.34% | 25.00% |
| ACCEPTANCE | section_leak | 4 | 0.89% | 9.30% |
| ACCEPTANCE | REASON_CODE_MISSING | 4 | 0.89% | 9.30% |
| ACCEPTANCE | year_unproven | 2 | 0.45% | 4.65% |

Full table: `reports/pm5_loss_reasons.csv`.

---

## 7. Table K — Accounting reconciliation

| group | expected | accepted | first_failure_total | data_state_missing | accounting_residual |
|---|---:|---:|---:|---:|---:|
| OVERALL | 576 | 127 | 449 | 0 | **0** |
| era=E1 (pre-2013) | 108 | 17 | 91 | 0 | 0 |
| era=E2 (2013–14) | 72 | 17 | 55 | 0 | 0 |
| era=E3 (2015) | 36 | 0 | 36 | 0 | 0 |
| era=E4 (2016–19) | 144 | 40 | 104 | 0 | 0 |
| era=E5 (2020–22) | 108 | 0 | 108 | 0 | 0 |
| era=E6 (2023–25) | 108 | 53 | 55 | 0 | 0 |

**The arithmetic identity `EXPECTED = ACCEPTED + first-failure + DATA_STATE_MISSING`
holds exactly, everywhere, with residual 0.** Every one of the 576 expected
observations resolves to exactly one terminal state (§21); no
`DATA_STATE_MISSING` was needed because every observation's evidence was
unambiguous — the funnel *stage-order assumption*, not the accounting
identity, is what's violated (§4).

---

## 8. Table D — Year-level coverage

| FY | expected | discovered | downloaded | identity_verified | mda_located | accepted | coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2010 | 36 | 28 | 0 | 0 | 0 | 0 | 0.00% |
| 2011 | 36 | 29 | 1 | 1 | 1 | 0 | 0.00% |
| 2012 | 36 | 28 | 28 | 23 | 26 | 17 | 47.22% |
| 2013 | 36 | 29 | 29 | 23 | 28 | 17 | 47.22% |
| 2014 | 36 | 30 | 0 | 0 | 0 | 0 | 0.00% |
| 2015 | 36 | 33 | 2 | 0 | 0 | 0 | 0.00% |
| 2016 | 36 | 31 | 0 | 0 | 0 | 0 | 0.00% |
| 2017 | 36 | 31 | 31 | 28 | 29 | 22 | 61.11% |
| 2018 | 36 | 31 | 31 | 26 | 28 | 18 | 50.00% |
| 2019 | 36 | 32 | 0 | 0 | 0 | 0 | 0.00% |
| 2020 | 36 | 33 | 0 | 0 | 0 | 0 | 0.00% |
| 2021 | 36 | 34 | 0 | 0 | 0 | 0 | 0.00% |
| 2022 | 36 | 35 | 0 | 0 | 0 | 0 | 0.00% |
| 2023 | 36 | 36 | 0 | 0 | 0 | 0 | 0.00% |
| 2024 | 36 | 36 | 36 | 35 | 35 | 26 | 72.22% |
| 2025 | 36 | 36 | 36 | 34 | 35 | 27 | 75.00% |

**This is the single most important finding in this audit.** Discovery is
near-complete and roughly flat across all 16 years (28–36 of 36, 78–100%).
Download success, however, is **binary by fiscal year, not gradual**: eight
fiscal years (2010, 2014, 2016, 2019, 2020, 2021, 2022, 2023) have **zero**
downloads despite 28–36 discovered candidates each, while the other eight
years (2011 partially, 2012, 2013, 2015 partially, 2017, 2018, 2024, 2025)
were substantively or fully fetched. Full table: `reports/coverage_by_fy.csv`.

**Interpretation discipline (§35, §47):** the canonical evidence at this
cutoff cannot distinguish "fetch was attempted for FY2020 and failed for
every one of 33 candidates" from "fetch was never attempted for FY2020 at
all" — `fetch.py` prints failures to stdout but persists no failure log, and
`cohort_fetch_manifest.jsonl` (the fetch-input candidate list) itself
contains **zero rows for the eight zero-download years**, which is more
consistent with **staged/incremental fetch runs that have not yet reached
those years** than with fetch attempts that failed. This audit reports the
observed fact (`downloaded=False`, `REASON_CODE_MISSING`) and explicitly
does **not** claim "these reports could not be downloaded" or "do not
exist" — that stronger claim is not established by the evidence available.

---

## 9. Table E — Era coverage

| era | expected | discovered | downloaded | identity_verified | mda_located | accepted | coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| E1 pre-2013 (FY2010–12) | 108 | 85 | 29 | 24 | 27 | 17 | 15.74% |
| E2 BR-Report (FY2013–14) | 72 | 59 | 29 | 23 | 28 | 17 | 23.61% |
| E3 Companies Act 2013 (FY2015) | 36 | 33 | 2 | 0 | 0 | 0 | 0.00% |
| E4 Ind AS (FY2016–19) | 144 | 125 | 62 | 54 | 57 | 40 | 27.78% |
| E5 Mandated ratios (FY2020–22) | 108 | 102 | 0 | 0 | 0 | 0 | 0.00% |
| E6 BRSR (FY2023–25) | 108 | 108 | 72 | 69 | 70 | 53 | 49.07% |

`era_definition_version = pm5-v1` (derived, not pre-existing — see §12
Limitations). Full transition loss rates: `reports/coverage_by_era.csv`.

---

## 10. Table F — Cap-band coverage

| cap_band | expected | discovered | downloaded | identity_verified | mda_located | accepted | coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| large | 96 | 96 | 36 | 36 | 36 | 32 | 33.33% |
| mid | 128 | 128 | 48 | 42 | 47 | 33 | 25.78% |
| small | 160 | 111 | 44 | 38 | 42 | 27 | 16.88% |
| micro | 192 | 177 | 66 | 54 | 57 | 35 | 18.23% |

`large` companies have 0% discovery loss (96/96) and the highest final
coverage (33.33%); `small` companies have the highest discovery loss
(30.62%, largest single dimension-transition difference found in the 10pp
screen — see §11). Full table: `reports/coverage_by_cap_band.csv`.

## Table G — Exchange coverage

| exchange | expected | discovered | downloaded | identity_verified | mda_located | accepted | coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| both (NSE+BSE) | 400 | 351 | 134 | 122 | 131 | 97 | 24.25% |
| bse (BSE-only) | 176 | 161 | 60 | 48 | 51 | 30 | 17.05% |

`exchange` is the static, frozen `cohort_companies.csv` field — never
inferred from which source happened to succeed. No `nse`-only company
exists in this cohort (micro-caps were deliberately chosen to include
BSE-only issuers per `tools/select_labelling_cohort.py`).

## Table H — Era × cap-band coverage

Full 6×4 = 24-cell table: `reports/coverage_by_era_cap_band.csv`
(`expected`, `accepted`, `coverage`, all five transition loss rates per
cell). **No project-defined minimum-N convention exists anywhere in this
repository**, so per §31 every cell — regardless of size — is labeled
`SPARSE — DESCRIPTIVE ONLY` uniformly; none is given a stronger
interpretation.

---

## 11. Table I — 10-percentage-point screens

Applied identically to every (dimension × transition) combination — not
selected after seeing which is largest. Full table:
`reports/coverage_screen_10pp.csv`; largest few shown:

| dimension | transition | max group | max loss% | min group | min loss% | diff (pp) | status |
|---|---|---|---:|---|---:|---:|---|
| era | downloaded→identity_verified | E3 (FY2015) | 100.00 | E6 (2023–25) | 4.17 | **95.83** | >10pp — SPARSE/DESCRIPTIVE ONLY |
| era | discovered→downloaded | E5 (2020–22) | 100.00 | E6 (2023–25) | 33.33 | 66.67 | >10pp — SPARSE/DESCRIPTIVE ONLY |
| cap_band | small (expected→discovered) | small | 30.62 | large | 0.00 | 30.62 | >10pp — SPARSE/DESCRIPTIVE ONLY |
| cap_band | mda_located→accepted | micro | 38.60 | large | 11.11 | 27.49 | >10pp — SPARSE/DESCRIPTIVE ONLY |

**Every** flagged difference in this table is labeled
`SPARSE / DESCRIPTIVE ONLY` because, per §32, no already-frozen sample-size
convention exists in this repository to justify a stronger reading. These
are screening signals, not significance tests, and are not interpreted
causally.

---

## 12. Reason-code completeness (Table J)

| stage | failed_N | reason_present_N | reason_missing_N | reason_coverage_% |
|---|---:|---:|---:|---:|
| DISCOVERY | 64 | 0 | 64 | 0.00% |
| DOWNLOAD | 318 | 0 | 318 | 0.00% |
| IDENTITY | 24 | 24 | 0 | 100.00% |
| MDA_LOCATION | 0 | 0 | 0 | n/a (empty — see §4) |
| ACCEPTANCE | 43 | 39 | 4 | 90.70% |
| **OVERALL** | **449** | **63** | **386** | **14.03%** |

Reason-code coverage is **itself incomplete, and badly so** — 86% of all
losses carry `REASON_CODE_MISSING`, almost entirely because DISCOVERY and
DOWNLOAD failures are not logged with a persisted reason anywhere in the
frozen pipeline state (`discover.py`/`fetch.py` print to stdout only; no
negative-result artifact exists). IDENTITY and ACCEPTANCE-stage failures,
by contrast, are well-instrumented (100% and 90.7% reason coverage) because
`verify.py` persists structured reason codes. This 14.03% overall figure
should not be read as "the pipeline mostly doesn't explain its failures" —
it should be read as "89% of all losses occur at the two stages (DOWNLOAD,
DISCOVERY) that have no persisted failure telemetry at all."

`MDA_LOCATION` shows 0 failed observations as a *first*-failure stage: this
is not because MD&A location never fails (`mda_not_located` occurs 12
times), but because those 12 all have `identity_verified=False` too, so
under the fixed stage order (§19) they are attributed to `IDENTITY`
instead — see §4.

---

## 13. Loss concentration

| n_companies_with_loss | n_companies_total | total_losses | top5_share | top10_share |
|---:|---:|---:|---:|---:|
| 36 | 36 | 449 | 16.93% | 32.52% |

**Every one of the 36 cohort companies has at least one lost observation.**
Loss is not concentrated in a handful of problem issuers — the top 5
companies account for only 16.93% of all 449 losses, and the top 10 for
32.52%, both close to what uniform distribution across 36 firms would give
(13.9% / 27.8%). This points to **broad, systemic attrition** (dominated by
the DOWNLOAD-stage, staged-fetch pattern in §8) rather than **issuer-specific
attrition**. Full ranking: `reports/pm5_loss_by_company.csv`.

---

## 14. Required final questions

**A. Exact expected denominator?** 576 company-years (36 firms ×
FY2010–2025), frozen in `pm5_expected_universe_snapshot.csv`.

**B. Cutoff?** `2026-09-17T10:25:19Z` UTC (pin timestamp of the three
gitignored evidence files; see §1).

**C. Survivors per stage?** DISCOVERED 512, DOWNLOADED 194, IDENTITY_VERIFIED
170, MDA_LOCATED 182 (see §4 for why this exceeds IDENTITY_VERIFIED),
ACCEPTED 127.

**D. Largest attrition?** DISCOVERED → DOWNLOADED: 318 observations lost
(62.11% transition loss), concentrated in 8 of 16 fiscal years that show
zero downloads despite near-complete discovery (§8).

**E. Canonical reasons for the first losses?** Predominantly
`REASON_CODE_MISSING` (DOWNLOAD 318, DISCOVERY 64 — 85% of all losses have
no persisted reason). Where reasons exist: `source_shredded` (27,
reprocessor-compressed PDFs capped below `high`/`medium`), `mda_not_located`
(12), `span_truncated` (6), `identity_unproven`/`year_unproven` (12
combined).

**F. Coverage differ by fiscal year?** Yes, sharply and structurally — 0%
in 8 years, 47–75% in the other 8 (§8), tracking which years have been
fetched at all rather than a smooth quality gradient.

**G. Coverage differ by fiscal era?** Yes: 0% (E3, E5) to 49.07% (E6); see
§9. Interacts heavily with F, since eras are FY buckets.

**H. Coverage differ by cap band?** Yes: 16.88% (small) to 33.33% (large);
large caps have zero discovery loss. See §10.

**I. Coverage differ by exchange?** Yes, descriptively: 24.25% (both) vs
17.05% (BSE-only); not decomposed further (confounded with cap band, since
BSE-only firms in this cohort are disproportionately micro-cap).

**J. Any transition loss rates >10pp apart?** Yes, extensively — see §11
and the full `coverage_screen_10pp.csv` (era and cap_band dimensions both
produce multiple >10pp differences).

**K. Which >10pp findings are stable enough to interpret vs. sparse?**
**None** are given a stronger interpretation. No project-defined
minimum-sample-size convention exists anywhere in this repository, so every
>10pp finding in this audit — without exception — is labeled `SPARSE /
DESCRIPTIVE ONLY` per §32's explicit rule (no threshold was invented
post-hoc to promote any of them).

**L. Is reason-code coverage itself incomplete?** Yes, substantially: 14.03%
overall (§12), driven entirely by the DISCOVERY/DOWNLOAD stages having no
persisted failure telemetry in the frozen pipeline.

**M. Are losses concentrated in a small number of companies?** No — losses
are broadly distributed across all 36 companies (§13); top-10 share
(32.52%) is close to the 27.8% a uniform distribution would produce.

**N. What evidence is measured?** Three gitignored, pinned-and-hashed
snapshots (`cohort_reports.jsonl`, `live_store/documents.jsonl`,
`live_dataset/manifest.jsonl`) plus one git-tracked file
(`cohort_companies.csv`), all read-only, none re-derived or re-run.

**O. What remains unknown?**
1. Whether the 8 zero-download fiscal years reflect *attempted-and-failed*
   fetches or *not-yet-attempted* fetches (§8) — the frozen state cannot
   distinguish these.
2. Whether any of the 64 DISCOVERY-stage losses reflect companies not yet
   listed in that FY (no `listing_date` field exists to check this).
3. Whether the 12 MDA_LOCATED-without-IDENTITY_VERIFIED observations (§4)
   are wrong-company/wrong-year documents or true documents the identity
   check under-verified — this audit does not adjudicate individual
   documents (that would be a retry/repair action, forbidden under §22).

---

## 15. Limitations (read before citing era/cap-band figures)

1. **`era_definition_version` and its FY-bucket boundaries were derived, not
   found pre-existing**, from the regulatory threshold years already coded
   into `arpipe/verify.py: check_era()`/`era_signals()` (2013, 2015, 2016,
   2020, 2023). No named era-bucket scheme existed anywhere in the frozen
   repository before this audit built one from those boundaries. This is
   the most defensible option available under §18 ("do not create new era
   boundaries"), since these are literally the only frozen era-relevant
   boundaries in production code — but it is an interpretive step this
   report is flagging explicitly, not a pre-registered taxonomy.
2. **`cap_band` is a static, company-level attribute**, fixed at
   cohort-selection time (2026-09-11), not a true time-varying firm-year
   cap band (no such series exists in the frozen state). A company that
   changed market-cap tier across FY2010–2025 is shown under one band for
   every year.
3. **§4's stage-ordering violation** (`mda_located` not fully nested inside
   `identity_verified`) is a structural property of how
   `arpipe/pipeline.py` sequences `segment.locate()` before
   `verify.verify()`. It affects only 12 of 576 observations (2.1%) and
   none of the 127 accepted rows, but it is the reason this audit's final
   verdict is INCOMPLETE rather than PASS.

---

## 16. Reproducibility & production immutability

- Full analysis re-run twice from the same pinned inputs:
  `pm5_stage_table.csv`, `pm5_expected_universe_snapshot.csv`, and
  `coverage.json` (excluding the wall-clock `analysis_date` field) were
  byte-identical across both runs. See `pm5_test_results.txt`.
- Protected production files (`discover.py`, `fetch.py`, `triage.py`,
  `segment.py`, `patterns.py`, `verify.py`, `pipeline.py`, `ocr.py`,
  `models.py`, plus `store.py`/`universe.py`/`config.py`/`evaluate.py`/
  `textlayer.py`/`preflight.py`; `state.py` does not exist in this
  codebase) were sha256-hashed before analysis began
  (`pm5_protected_file_hashes_pre.txt`) and re-hashed after
  (`pm5_protected_file_hashes_post.txt`) — all identical.
  `git status --short` / `git diff --stat` in this worktree show no
  changes to any tracked file; only new files under `tools/` and
  `reports/` were added.
- `arpipe-0.1.0` (the shared worktree) was never written to; only read,
  immediately after which its files were re-hashed and confirmed unchanged
  (§1).

---

## 17. Final verdict

```
COVERAGE FUNNEL INCOMPLETE — DENOMINATOR NOT RELIABLY RECONCILED
```

The expected-universe denominator (576) is frozen, unique, and fully
accounted for (accounting residual = 0 everywhere, §7). The funnel's
required stage monotonicity is **not** fully satisfied
(`N_mda_located=182 > N_identity_verified=170`), for the specific,
narrow, fully-documented reason in §4. Production behavior was not changed
by this audit in either case.
