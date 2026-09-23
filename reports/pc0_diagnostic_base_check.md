# P-C0 Diagnostic Base Sufficiency Check

**Mode:** READ-ONLY DIAGNOSTIC GATE
**Question:** Can clean committed HEAD `0fb8cbf6d932f4190bdfe3b2a1fecf62170cca14` plus the already-frozen P-M5 evidence support starting P-C0 (diagnosis of the 22.05% coverage problem)?
**Machine-readable companion:** `reports/pc0_diagnostic_base_check.json`

---

## 0. Setup and provenance

| Item | Value |
|---|---|
| Target HEAD SHA | `0fb8cbf6d932f4190bdfe3b2a1fecf62170cca14` ("P33: audit post-P25 patterns for false positives, fix is-given-below rejection") |
| Original worktree (READ-ONLY, untouched) | `D:\sem_iitk\sem9\thesis\sep_week1\arpipe-0.1.0` |
| Original worktree observed state | HEAD = 0fb8cbf on branch `main`, but **working tree is dirty**: 13 modified tracked files (`arpipe/cli.py`, `pipeline.py`, `fetch.py`, `store.py`, `verify.py`, etc.) and ~45 untracked files/dirs, and the branch is 17 commits behind `origin/main`. This is exactly the contamination the earlier Step 0/0A/0B attempts ran into — confirmed directly, not assumed. |
| Diagnostic worktree (created this task) | `D:\sem_iitk\sem9\thesis\sep_week1\arpipe-pc0-diagnostic-base`, created via `git worktree add --detach <path> 0fb8cbf6d932f4190bdfe3b2a1fecf62170cca14`, run from `arpipe-0.1.0`. Detached HEAD at 0fb8cbf, `git status` clean. No dirty-tree changes were imported. |
| P-M5 evidence source | `D:\sem_iitk\sem9\thesis\sep_week1\arpipe-pm5-coverage`, branch `pm5-coverage-funnel` @ commit `7292111` ("P-M5: coverage funnel study"), tracking `origin/pm5-coverage-funnel`, working tree clean. Read-only: files were opened and hashed, never edited, committed, merged, or cherry-picked. |

### P-M5 evidence files used, with SHA-256 (independently recomputed, not copied from any manifest)

| File | SHA-256 |
|---|---|
| `reports/coverage.json` | `c84166741d36a9774b7c9f29d71ea9583934d98c2ab153e651ec66ec4d371bcf` |
| `reports/pm5_expected_universe_snapshot.csv` | `b287a82d0fa2b15098882c328be6afc2c1672c9255f64103e4aaeabd94ccebe5` |
| `reports/pm5_expected_universe_snapshot.json` | `3c409ed44183651ab376f2cd8dc7ab6a29fb1fba0ae6dc34fb36498fdb12f7c8` |
| `reports/pm5_source_snapshot_manifest.json` | `827406a1d2fce8a084e65583c5adea172a330c2233c025c0e02b858c0ce1adfb` |
| `reports/pm5_stage_table.csv` | `30e93b59ac689f00fab182583fb25883322e429be42b4ba14e13a1011b916dc9` |
| `reports/pm5_source_snapshots/cohort_reports.jsonl` | `c24f148ae5971dca545168921caa207aa6cfd84021958fcf969bd812a4a04b67` |
| `reports/pm5_source_snapshots/live_store_documents.jsonl` | `3a7c7bf15f554298e1c7f4a62b90ea6328a9e1e1e4ecde4840aee7ce42abab31` |
| `reports/pm5_source_snapshots/live_dataset_manifest.jsonl` | `8607cd29d9e660fee1b18ce9d980e0a39c217275201d72114e4ce0a9fe89a625` |

**Cross-check:** `coverage.json` embeds `stage_csv_sha256` and `expected_csv_sha256`, and `pm5_source_snapshot_manifest.json` embeds hashes for the three `pm5_source_snapshots/` files. All embedded hashes match the independently recomputed values above exactly. The frozen evidence is internally consistent and has not silently drifted.

**Coverage headline (from `coverage.json`, not regenerated):** 576 expected → 512 discovered → 194 downloaded → 170 identity-verified → 182 MDA-located → 127 accepted = **22.05%**. The single largest loss is DISCOVERED→DOWNLOADED: 318 company-years (62.11% transition loss).

---

## Step 1 — The fiscal-year pattern

All 16 fiscal years (FY2010–FY2025), read directly from `pm5_stage_table.csv` (576 rows = 36 companies × 16 years):

| FY | expected | discovered | downloaded | identity_verified | mda_located | accepted | class | era |
|---|---|---|---|---|---|---|---|---|
| 2010 | 36 | 28 | 0 | 0 | 0 | 0 | **ZERO** | E1_pre2013 |
| 2011 | 36 | 29 | 1 | 1 | 1 | 0 | **ZERO** | E1_pre2013 |
| 2012 | 36 | 28 | 28 | 23 | 26 | 17 | **NONZERO** | E1_pre2013 |
| 2013 | 36 | 29 | 29 | 23 | 28 | 17 | **NONZERO** | E2_BRreport |
| 2014 | 36 | 30 | 0 | 0 | 0 | 0 | **ZERO** | E2_BRreport |
| 2015 | 36 | 33 | 2 | 0 | 0 | 0 | **ZERO** | E3_CompaniesAct2013 |
| 2016 | 36 | 31 | 0 | 0 | 0 | 0 | **ZERO** | E4_IndAS |
| 2017 | 36 | 31 | 31 | 28 | 29 | 22 | **NONZERO** | E4_IndAS |
| 2018 | 36 | 31 | 31 | 26 | 28 | 18 | **NONZERO** | E4_IndAS |
| 2019 | 36 | 32 | 0 | 0 | 0 | 0 | **ZERO** | E4_IndAS |
| 2020 | 36 | 33 | 0 | 0 | 0 | 0 | **ZERO** | E5_MandatedRatios |
| 2021 | 36 | 34 | 0 | 0 | 0 | 0 | **ZERO** | E5_MandatedRatios |
| 2022 | 36 | 35 | 0 | 0 | 0 | 0 | **ZERO** | E5_MandatedRatios |
| 2023 | 36 | 36 | 0 | 0 | 0 | 0 | **ZERO** | E6_BRSR |
| 2024 | 36 | 36 | 36 | 35 | 35 | 26 | **NONZERO** | E6_BRSR |
| 2025 | 36 | 36 | 36 | 34 | 35 | 27 | **NONZERO** | E6_BRSR |

- **Zero-coverage FYs (10):** 2010, 2011, 2014, 2015, 2016, 2019, 2020, 2021, 2022, 2023
- **Non-zero-coverage FYs (6):** 2012, 2013, 2017, 2018, 2024, 2025

**Pattern classification:** neither contiguous, nor simple alternating, nor a single pre/post-date split. Non-zero years form **three tight 2-year clusters** — {2012,2013}, {2017,2018}, {2024,2025} — separated by multi-year zero gaps, with a leading zero pair (2010–2011). It does **not** align with the `era_definition_version` regulatory-boundary buckets already recorded in the stage table (E1, E4 and E6 are each internally mixed zero/nonzero), so era membership does not explain the split.

**Timestamp clustering (new finding from the frozen `fetched_at` field in `live_store_documents.jsonl`):** all 194 historical successful downloads occurred inside **one continuous ~4.5-minute window** on 2026-09-11 (10:28:44–10:33:08 UTC). Within that single run, successes arrive in three mutually exclusive sub-windows, in FY order: FY2012/2013 first, FY2017/2018 next, FY2024/2025 last, with negligible trickle (1–2 docs) for FY2011/FY2015 interleaved. This rules out "separate partial crawls on different days for different research phases" — it was one run — and points toward a **time/session-dependent condition on the source side** as the more likely mechanism.

---

## Step 2 — The 10-observation diagnostic sample

Selected from the frozen stage table, 5 distinct companies per group, each with `discovered=True`; exact URLs recovered from the frozen `cohort_reports.jsonl` snapshot (top NSE→BSE→screener priority shown):

| # | Group | Company / FY | first_failed_stage | reason_code | terminal_state | Top discovered URL |
|---|---|---|---|---|---|---|
| 1 | ZERO | Reliance / FY2010 | DOWNLOAD | REASON_CODE_MISSING | FIRST_FAILURE_AT_DOWNLOAD | `nsearchives.nseindia.com/annual_reports/AR_RELIANCE_2009_2010_20082010120000.zip` |
| 2 | ZERO | Infosys / FY2011 | DOWNLOAD | REASON_CODE_MISSING | FIRST_FAILURE_AT_DOWNLOAD | `bseindia.com/bseplus/AnnualReport/500209/5002090311.pdf` |
| 3 | ZERO | HDFC Bank / FY2014 | DOWNLOAD | REASON_CODE_MISSING | FIRST_FAILURE_AT_DOWNLOAD | `nsearchives.nseindia.com/annual_reports/AR_3393_HDFCBANK_2013_2014_12062014114216.zip` |
| 4 | ZERO | Sun Pharma / FY2015 | DOWNLOAD | REASON_CODE_MISSING | FIRST_FAILURE_AT_DOWNLOAD | `nsearchives.nseindia.com/annual_reports/AR_8644_SUNPHARMA_2014_2015_07102015123110.zip` |
| 5 | ZERO | Tata Steel / FY2016 | DOWNLOAD | REASON_CODE_MISSING | FIRST_FAILURE_AT_DOWNLOAD | `nsearchives.nseindia.com/annual_reports/AR_9362_TATASTEEL_2015_2016_16082016104323.zip` |
| 6 | NONZERO | Reliance / FY2012 | — | — | ACCEPTED | `nsearchives.nseindia.com/annual_reports/AR_RELIANCE_2011_2012_29062012101059.zip` |
| 7 | NONZERO | Infosys / FY2013 | — | — | ACCEPTED | `nsearchives.nseindia.com/annual_reports/AR_27_INFY_2012_2013_20062013105245.zip` |
| 8 | NONZERO | HDFC Bank / FY2017 | ACCEPTANCE | source_shredded | FIRST_FAILURE_AT_ACCEPTANCE | `nsearchives.nseindia.com/annual_reports/AR_10840_HDFCBANK_2016_2017_25072017151900.zip` |
| 9 | NONZERO | Sun Pharma / FY2018 | — | — | ACCEPTED | `nsearchives.nseindia.com/annual_reports/AR_13921_SUNPHARMA_2017_2018_01102018175233.zip` |
| 10 | NONZERO | Tata Steel / FY2024 | — | — | ACCEPTED | `nsearchives.nseindia.com/annual_reports/AR_24166_TATASTEEL_2023_2024_2206202419194.pdf` |

Full row-level detail (all P-M5 stage fields, all discovered sources per pair) is in the companion JSON under `step2_selected_sample`.

---

## Step 3 — Raw HTTP diagnostic (10 URLs, 2 curl passes each, 20 requests total)

Method: (1) bare curl, default UA, `-L --max-time 30`; (2) `curl -L --max-time 45 --max-redirs 10 --retry 2 --retry-delay 3` (up to 3 total attempts on transient errors). Full headers, first 500 bytes of body, and curl's own stderr/exit code captured verbatim. No ARPipe code touched.

| # | Group | URL host | Result |
|---|---|---|---|
| 1 | ZERO | nsearchives.nseindia.com | `curl: (56) Recv failure: Connection was reset` |
| 2 | ZERO | www.bseindia.com | **HTTP/1.1 200 OK**, `Content-Type: application/pdf`, `Content-Length: 5698015`, body starts `%PDF-1.6`, `Last-Modified: Thu, 20 Oct 2011` |
| 3 | ZERO | nsearchives.nseindia.com | `curl: (28) Operation timed out after 45011ms` (×3 attempts, all timed out) |
| 4 | ZERO | nsearchives.nseindia.com | `curl: (28) Operation timed out` (×3 attempts) |
| 5 | ZERO | nsearchives.nseindia.com | `curl: (28) Operation timed out` (×3 attempts) |
| 6 | NONZERO | nsearchives.nseindia.com | `curl: (28) Operation timed out` (×3 attempts) |
| 7 | NONZERO | nsearchives.nseindia.com | `curl: (56) Recv failure: Connection was reset` |
| 8 | NONZERO | nsearchives.nseindia.com | `curl: (28) Operation timed out` (×3 attempts) |
| 9 | NONZERO | nsearchives.nseindia.com | `curl: (28) Operation timed out` (×3 attempts) |
| 10 | NONZERO | nsearchives.nseindia.com | `curl: (28) Operation timed out` (×3 attempts) |

**Key finding:** all 9 sampled `nsearchives.nseindia.com` URLs fail identically today — a mix of connection resets and 45s timeouts — with **no visible difference between the ZERO group (4 URLs) and the NONZERO group (5 URLs)**. The 1 sampled BSE URL (a ZERO-coverage company-year, Infosys FY2011) succeeds cleanly with a genuine, valid PDF that has existed since 2011 (not a recently vanished source). Both hosts are Akamai-fronted (`Akamai-GRN` header present on the successful BSE response too), so "Akamai blocks all non-browser clients" is not the explanation — the block is specific to the NSE archive host's own configuration.

---

## Step 4 — Committed HEAD fetch-logic comparison

- **`arpipe/fetch.py:fetch_one()`** streams the GET with `follow_redirects=True`, 120s timeout, up to 3 attempts. HTTP 403/429/503 trigger a backoff-and-continue retry; any other exception — **including connection reset and timeout, exactly what today's probes hit** — is caught, retried with linear backoff, and re-raised after 3 attempts.
- **`arpipe/cli.py:cmd_fetch()`**'s `_fetch_pair()` catches that exception, prints a one-line `WARN` to **stderr only**, and fails over to the next candidate source (NSE→BSE→screener). If all candidates raise, the pair is simply absent from `documents.jsonl` with **no structured reason recorded anywhere**.
- This is directly confirmed, not inferred: `reports/pm5_reason_code_completeness.csv` shows **0.0% reason-code coverage** for both DISCOVERY (0/64) and DOWNLOAD (0/318) stage losses, versus 100% for IDENTITY and 90.7% for ACCEPTANCE — exactly consistent with the stderr-only error handling above (IDENTITY/ACCEPTANCE's later stages, unlike DOWNLOAD, do write structured reason codes).
- **A concrete, testable code asymmetry:** `discover.py:nse_session()` builds a cookie-bearing, Referer-carrying client used only for the discovery-stage NSE API calls. `cli.py:cmd_fetch()` builds an entirely separate, fresh `httpx.Client` (User-Agent only, no cookies, no Referer) to actually download the archive file from the different host `nsearchives.nseindia.com`. Whether that host's bot-mitigation requires the discovery session's cookies/Referer to avoid resets is a concrete hypothesis P-C0 can test directly (e.g. replay `fetch_one` with vs. without the discovery cookie jar) without modifying any implementation.
- **Would committed HEAD accept today's observed responses?** For the 9 NSE URLs: no — they'd hit the generic-exception retry-then-raise path and reproduce a DOWNLOAD-stage failure with no captured reason, matching the frozen `REASON_CODE_MISSING` rows exactly. For the BSE URL: yes — `fetch_one` would accept and store it immediately.
- **Open ambiguity, explicitly flagged:** `tools/pm5_coverage.py` states in its own docstring that it "does not import arpipe production modules and does not run discover/fetch/…" — the frozen evidence is a reconciliation of an **earlier real run's** log files (dated 2026-09-11), and it cannot be proven from this evidence alone that that run used code byte-identical to HEAD 0fb8cbf (the live `arpipe-0.1.0` tree is confirmed dirty right now). This does not block sufficiency (criterion 3 requires HEAD to contain enough logic to *compare against*, not proof of historical code identity) — it is a sub-question for P-C0 to carry forward.

---

## Step 5 — Zero-year vs non-zero-year comparison

No structural difference was found between the two groups' sampled URLs: identical `AR_<id>_<SYMBOL>_<FY0>_<FY1>_<timestamp>.<ext>` filename structure (matched by the same regex in `discover.py`), same hostname for 9/10 samples, `.zip` dominant in **both** groups with one `.pdf` outlier landing in the *nonzero* group (not the zero group), zero redirects observed in either group, and no auth/cookie requirement observed for the one URL that succeeded. The only measurable difference in the frozen evidence is **temporal** (the `fetched_at` clustering in Step 1), not structural. Today's live probing found no group-based difference either. This directly rules out (with evidence, not assumption) a source-identifier or file-format explanation, and is consistent with a time/session/rate-limit-state-dependent mechanism on the NSE side.

**Caveat:** today's uniform NSE failure should not be over-read as proof of the historical mechanism — see the network-environment note below.

---

## Step 6 — Sufficiency determination

| Criterion | Met? | Evidence |
|---|---|---|
| 1. Frozen P-M5 evidence consumable without reconstructing the worktree | ✅ | `pm5-coverage-funnel` branch clean, committed, origin-tracked; all required files present, tracked, hash-verified |
| 2. 10 observations selectable from that evidence | ✅ | 5+5 done, real URLs recovered from frozen `cohort_reports.jsonl` |
| 3. Committed HEAD has enough fetch/invocation logic to compare | ✅ | `discover.py`/`fetch.py`/`cli.py` fully present and read; retry/backoff/client-construction behavior fully reconstructed and compared against live probes |
| 4. No dirty-tree change required merely to diagnose | ✅ | Every step used only the clean diagnostic worktree and the clean pm5-coverage branch; `arpipe-0.1.0`'s dirty tree was never read or written |

**All four criteria hold.**

**Identified open ambiguity (does not block sufficiency):** whether the 2026-09-11 historical crawl ran on HEAD-identical code — a sub-question for P-C0, not a missing dependency.

**Network-environment caveat:** raw HTTP results here were captured from the IIT Kanpur campus network on 2026-09-17. NSE's archive CDN blocking/resetting all 9 sampled requests today may reflect current IP-reputation/WAF state rather than a timeless property of the URLs. This diagnostic gate only needed to show that HEAD's code and live sources are **jointly sufficient to run the comparison and generate falsifiable hypotheses** — which they are — not that today's network conditions exactly reproduce 2026-09-11's conditions.

---

## Step 7 — Scope compliance

Did **not**: rerun the 576-observation crawl, rerun the 194-document extraction, modify download logic, add retry/backoff, repair manifests, alter stage membership, modify P-M5 evidence, create Universe V2, or change production code. Total network requests made: 20 (10 URLs × 2 curl passes), a bounded 10-observation diagnostic as instructed.

---

## Final verdict

# DIAGNOSTIC BASE SUFFICIENT — P-C0 MAY START
