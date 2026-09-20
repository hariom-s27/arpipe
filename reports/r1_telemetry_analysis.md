# ARPipe — R1 Telemetry Analysis & Acquisition-Resolution Experiment Design

**Authoritative Report:** `reports/r1_telemetry_analysis.md`
**Companion Data:** [`reports/r1_telemetry_analysis.json`](file:///D:/sem_iitk/sem9/thesis/sep_week1/arpipe-r1-telemetry-analysis/reports/r1_telemetry_analysis.json)
**Worktree:** `D:\sem_iitk\sem9\thesis\sep_week1\arpipe-r1-telemetry-analysis`
**Branch:** `r1-telemetry-analysis`
**Base Commit:** `56497721cb68c4831e6f225074b6bd7ea17bffb0` (R1 Frozen Base)
**Mode:** ANALYSIS & EXPERIMENT DESIGN ONLY (No network acquisition, no corpus rerun, no production code changes, no memory edits)

---

## 1. Scope

This report provides the formal telemetry analysis of the frozen R1 acquisition failure instrumentation and defines the smallest evidence-supported next experiment to resolve remaining acquisition uncertainties.

### Operational Boundaries
1. **Analysis Only:** No live network requests were executed during this analysis.
2. **Behavioral Invariance Preserved:** No production code, retry parameters, backoffs, timeouts, headers, cookies, or scheduling logic have been modified.
3. **Strict Epistemological Demarcation:** Synthetic matrix fixtures are strictly separated from live telemetry, and historical unknowns are rigorously guarded against retrospective speculation.
4. **Memory Immutability:** Project memory (`ARPipe_Memory`) remains unmodified during this analysis task.

---

## 2. Evidence Sources

The analysis synthesizes evidence from the following authoritative artifacts:

| Artifact | Location | SHA-256 Digest | Evidence Class | Role in Analysis |
|---|---|---|---|---|
| `r1_matrix_telemetry.jsonl` | `reports/r1_telemetry/` | `466dca2953cea16b698fe81dec2ef852634c4b6e5a476acb831033b941a90631` | `CONTROLLED_TEST_EVIDENCE` | Authoritative 17-record fixture trace from frozen R1 runner |
| `r1_generation_summary.json` | `reports/r1_telemetry/` | `92e2dc8e4a82eec021dd1c91684b9b04ab51a42367cf5a6099a8e200135dce05` | `CONTROLLED_TEST_EVIDENCE` | Validation summary of the 9 matrix fixtures |
| `r1_fetch_telemetry.json` | `reports/` | `10310bd9cce4f55b198a7e6f5777e7c86d3ecce029f068003e750623fc6d26ab` | `CONTROLLED_TEST_EVIDENCE` | Verification record of R1 test suite and equivalence |
| `r1_fetch_telemetry.md` | `reports/` | `edf26f03a433e1e344c956195c1cab605b519dc3aec62a4e142a0dbbf48a895c` | `CONTROLLED_TEST_EVIDENCE` | Specification and implementation report of R1 |
| `pm5_stage_table.csv` | `sep_week1/arpipe-pm5-coverage/reports/` | `30e93b59ac689f00fab182583fb25883322e429be42b4ba14e13a1011b916dc9` | `HISTORICALLY_ESTABLISHED` | 576-observation universe establishing the 318 download losses |
| `cohort_reports.jsonl` | `sep_week1/arpipe-pm5-coverage/reports/pm5_source_snapshots/` | `26dd20a3205315bdfbfef7343e09968449c2ba68ea822d5dd95a28f8f01cba68` | `HISTORICALLY_ESTABLISHED` | Discovered URLs and source metadata for the 512 discovered reports |
| `pc0_sample_manifest.json` | `sep_week1/arpipe-pc0-coverage-diag/reports/` | `394c628d842bdcf967b6dd82ab695fb4b17a88602c7c79c0b17561a3d931bb0e` | `HISTORICALLY_ESTABLISHED` | Frozen 10-observation diagnostic sample (5 zero FYs + 5 controls) |
| `pc0r_diagnosis.json` | `sep_week1/arpipe-pc0r-acquisition-pilot/reports/` | `b0f745be326f53a6d71329bf8df3a2862a98444a7ec52c92e92ec40b3bfaebf7` | `CURRENTLY_REPRODUCED` | Evidence ruling out client asymmetry (50/50 success in open window) |
| `R1.md`, `P-M5.md`, `P-C0.md`, `P-C0R.md` | `ARPipe_Memory/experiments/` | N/A (read-only) | `SYNTHESIS` | Contextual baseline and historical chronology |

---

## 3. R1 Telemetry Schema Reconstitution (`r1-v1`)

Inspection of `arpipe/telemetry.py`, `arpipe/fetch.py`, and `reports/r1_telemetry/r1_matrix_telemetry.jsonl` establishes the schema version `r1-v1`. Every attempt that fails emits exactly one JSON record to the JSONL sink. Successful attempts emit zero records.

### Complete Field Specification

| Field Name | Type | Presence | Measures | What It Establishes | What It Cannot Establish |
|---|---|---|---|---|---|
| `telemetry_schema_version` | `str` | Mandatory | Fixed string `"r1-v1"` | Format compliance and parser versioning | Physical network characteristics |
| `run_id` | `str` | Mandatory | Identifier for batch execution run | Logical grouping of attempts across a command run | Global cross-run sequencing |
| `request_sequence_id` | `int` | Mandatory | Monotonic sequence number (1, 2, 3...) per writer | Process-level chronological ordering | Absolute wall-clock duration between requests |
| `timestamp_utc` | `str` | Mandatory | ISO 8601 UTC timestamp of attempt conclusion | Attempt completion time with microsecond resolution | Network packet dispatch time or server-side time |
| `company_id` | `str` | Mandatory | Company ISIN (e.g., `INE040A01034`) | Target entity identity within cohort universe | Corporate status or filing availability |
| `fy_end` | `int` | Mandatory | Target fiscal year end (e.g., `2014`) | Accounting period targeted | Report presence on target exchange |
| `source` | `str` | Mandatory | Repository identifier (`nse`, `bse`, `screener`) | Target source exchange protocol | Server edge-node identity or CDN routing |
| `url_redacted` | `str` | Mandatory | URL with sensitive query params redacted | Exact endpoint path, hostname, and safe parameters | Pre-redacted token/secret contents |
| `url_sha256` | `str` | Mandatory | SHA-256 hex digest of `url_redacted` | Unique cryptographic URL identifier | Original URL without rainbow/preimage table |
| `attempt_number` | `int` | Mandatory | 1-based attempt index (1, 2, 3...) | Trajectory position within retry policy | Cause of failure on prior attempts |
| `terminal_state` | `bool` | Mandatory | `true` if attempt terminates fetch operation | Whether the fetch pipeline gave up on the URL | Whether further retries would have succeeded |
| `retry_exhausted` | `bool` | Mandatory | `true` if attempt exhausted retry budget | Depletion of retry policy budget | Efficacy of larger retry limit |
| `error_type` | `str` | Mandatory | Taxonomy category (`HTTP_FAILURE`, `NETWORK_FAILURE`, `TIMEOUT`, `RESET`, `VALIDATION_FAILURE`, `OTHER_FAILURE`) | High-level fault classification | Deep root cause inside remote server or CDN |
| `status_code` | `int \| null` | Mandatory | HTTP response code (403, 429, 503, 200) or `null` | HTTP-layer rejection vs network-layer drop | Specific reason origin issued rejection code |
| `error_message` | `str` | Mandatory | Text description or exception message | Exact string produced by exception or status | Remote server internal log trace |
| `exception_class` | `str \| null` | Optional | Fully-qualified Python exception class | Exact client/library exception raised | Physical OSI transport state outside client OS |
| `first_failure_layer` | `str \| null` | Optional | Protocol layer (`L0_DNS`, `L1_CONNECT`, `L2_TLS`, `L3_HTTP`, `L4_RECEIPT`, `L5_CLASSIFICATION`, `L6_VALIDATION`) | Earliest architectural layer that collapsed | Multi-layer compound interactions |
| `response_content_type` | `str \| null` | Optional | Value of response `Content-Type` header | Server MIME declaration (e.g. `text/html` vs `application/zip`) | Payload validity before inspection |
| `bytes_received` | `int \| null` | Optional | Number of bytes received before failure | Payload truncation vs zero-byte drop | Integrity of partial byte stream |
| `elapsed_ms` | `float \| null` | Optional | Elapsed time from attempt start to failure (ms) | Client-perceived latency to failure | Granular breakdown between DNS, TCP, and TTFB |

### URL Redaction & Security Semantics
- Query parameter keys containing `token`, `auth`, `key`, `secret`, `signature`, `pwd`, `session`, `credential`, or `X-Amz-*` have their values strictly replaced with `[REDACTED]`.
- No authorization headers, cookies, or credentials are ever recorded.
- `url_sha256` is computed deterministically over `url_redacted`.

### Non-Blocking Persistence Semantics
- Telemetry emission is strictly best-effort.
- `emit_failure_telemetry()` catches all exceptions.
- If writing fails due to `PermissionError`, disk full (`OSError(28)`), or serialization error, the error is swallowed, `write_failures` is incremented on the writer, and the acquisition control flow proceeds without interruption or behavioral alteration.

---

## 4. Controlled Telemetry Characterization

The R1 deterministic test matrix is a synthetic verification suite executed by `tools/generate_r1_telemetry.py`. The resulting artifacts (`reports/r1_telemetry/r1_matrix_telemetry.jsonl` and `reports/r1_telemetry/r1_generation_summary.json`) characterize telemetry behavior under controlled fixtures:

```
[CONTROLLED TEST EVIDENCE]
Total Test Cases: 9 fixtures + 1 writer-failure fixture
Total HTTP Requests Simulated: 21
Total Telemetry Records Emitted: 17
```

### Breakdown by Fixture

| # | Fixture Name | Target Entity | FY | Requests | Emitted Records | Error Type | Status Code | First Failure Layer | Terminal Record Details |
|:---:|---|---|:---:|:---:|:---:|---|:---:|:---:|---|
| 1 | **200 PDF** | `INE002A01018` | 2024 | 1 | 0 | None (Success) | 200 | N/A | Returns `StoredDoc`; 0 records emitted |
| 2 | **200 ZIP** | `INE009A01021` | 2023 | 1 | 0 | None (Success) | 200 | N/A | Returns `StoredDoc`; 0 records emitted |
| 3 | **403 Forbidden** | `INE040A01034` | 2014 | 3 | 3 | `HTTP_FAILURE` | 403 | `L3_HTTP` | Att 1: F/F; Att 2: F/F; Att 3: T/T (`terminal=True, retry_exhausted=True`) |
| 4 | **429 Too Many Req** | `INE081A01020` | 2016 | 3 | 3 | `HTTP_FAILURE` | 429 | `L3_HTTP` | Att 1: F/F; Att 2: F/F; Att 3: T/T (`terminal=True, retry_exhausted=True`) |
| 5 | **503 Service Unavail**| `INE171A01029` | 2021 | 3 | 3 | `HTTP_FAILURE` | 503 | `L3_HTTP` | Att 1: F/F; Att 2: F/F; Att 3: T/T (`terminal=True, retry_exhausted=True`) |
| 6 | **Timeout** | `INE226A01021` | 2022 | 3 | 3 | `TIMEOUT` | `null` | `L4_RECEIPT` | Att 1: F/F; Att 2: F/F; Att 3: T/T (`httpx.ReadTimeout`) |
| 7 | **Connection Error** | `INE044A01036` | 2018 | 3 | 3 | `NETWORK_FAILURE`| `null` | `L1_CONNECT` | Att 1: F/F; Att 2: F/F; Att 3: T/T (`httpx.ConnectError`) |
| 8 | **Malformed ZIP** | `INE002A01018` | 2010 | 1 | 1 | `VALIDATION_FAILURE`| 200 | `L6_VALIDATION`| Att 1: T/F (`terminal=True, retry_exhausted=False, BadZipFile`) |
| 9 | **Malformed PDF** | `INE040A01034` | 2017 | 1 | 1 | `VALIDATION_FAILURE`| 200 | `L6_VALIDATION`| Att 1: T/F (`terminal=True, retry_exhausted=False, qpdf repair failed`) |
| 10| **Writer Failure** | N/A | N/A | N/A | 0 | Absorbed | N/A | N/A | `PermissionError`/`OSError(28)` swallowed; returns unaffected |

### Controlled Telemetry Metrics
- **Terminal Records:** Exactly 7 of 17 records have `terminal_state=true` (5 from exhausted retries on attempt 3, and 2 from immediate validation aborts on attempt 1).
- **Non-Terminal Records:** Exactly 10 of 17 records have `terminal_state=false` (attempts 1 and 2 of the 5 retriable fixtures).
- **Retry Exhausted Records:** Exactly 5 of 17 records have `retry_exhausted=true` (all occurring at attempt 3).
- **Validation Failures:** Exactly 2 records have `status_code=200` with `terminal_state=true` and `retry_exhausted=false`, confirming that validation failures abort immediately without useless retries.
- **Latency Distribution in Matrix:** Synthetic mock responses completed in 0.10ms to 0.59ms. The corrupted PDF fixture completed in 63.59ms due to executing the real external `qpdf` repair process before confirming corruption.

---

## 5. Statistical Restriction

> [!CAUTION]
> **CRITICAL EPISTEMOLOGICAL RESTRICTION:**
> The R1 deterministic test matrix is a synthetic test fixture designed to verify telemetry emission across code branches. It is **NOT** a random sample, stratified sample, or natural representation of historical acquisition attempts.
>
> Under no circumstances may an analyst compute, report, or infer:
> 1. Overall failure rates (e.g. 17 failures / 21 requests = 81.0% is a meaningless fixture artifact).
> 2. Dominant failure probability (e.g. HTTP 403 vs 429 vs Timeout proportions).
> 3. Expected historical failure distribution.
> 4. Prevalence of validation errors vs network errors.
> 5. Population-level parameters of any kind.
>
> All numbers in Section 4 are strictly counts characterizing code paths, not empirical estimates of reality.

---

## 6. Historical-vs-Current Evidence Distinction

A rigorous epistemological boundary must separate what is historically known about the 2026-09-11 crawl from what has been observed in current testing.

### Evidence Classification Table

| Class | Evidence Statement | Primary Grounding |
|---|---|---|
| **HISTORICALLY ESTABLISHED** | 318 company-years were lost at the DISCOVERED $\rightarrow$ DOWNLOADED transition on 2026-09-11. | `pm5_stage_table.csv` (SHA-256: `30e93b59...`) |
| **HISTORICALLY ESTABLISHED** | Historical failure reason-code completeness was 0.0% (all 318 losses coded `REASON_CODE_MISSING`). | `pm5_reason_code_completeness.csv` |
| **HISTORICALLY ESTABLISHED** | Pre-R1 code caught network exceptions to stderr without writing to `documents.jsonl`, and silently returned `None` on exhausted 403/429/503 retries. | Git inspection of `arpipe/fetch.py` at `0fb8cbf` |
| **HISTORICALLY ESTABLISHED** | All 194 successful historical downloads occurred within a single 4.5-minute window (10:28:44–10:33:08 UTC) on 2026-09-11 in 3 FY bursts. | `live_store_documents.jsonl` timestamps |
| **HISTORICALLY ESTABLISHED** | Strictly 8 fiscal years had zero archive downloads (FY2010, 2014, 2016, 2019, 2020, 2021, 2022, 2023). | P-C0 Table 2 reconciliation with `pm5_stage_table.csv` |
| **CURRENTLY REPRODUCED** | Archive endpoint `nsearchives.nseindia.com` exhibits acute temporal access variation (0/9 at ~13:17 UTC vs 10/10 at ~13:59 UTC vs 50/50 at 14:40–15:20 UTC). | P-C0 and P-C0R diagnostic runs on 2026-09-17 |
| **CURRENTLY REPRODUCED** | Zero-download URLs sampled in P-C0 exist and return valid ZIP and PDF payloads when the endpoint is responsive. | P-C0 Step 3 payload verification |
| **CURRENTLY REPRODUCED** | Client configuration asymmetry (browser headers, cookies, Referer) does NOT explain failures (10/10 paired arms succeeded identically). | P-C0R A/B trial (`pc0r_client_comparison.csv`) |
| **CURRENTLY REPRODUCED** | R1 attempt-level failure telemetry persists structured JSONL without modifying acquisition flow or return values (32/32 tests pass). | Commit `5649772` on branch `r1-fetch-telemetry` |
| **OBSERVED** | R1 test matrix generates 17 per-attempt failure records across 9 fixtures. | `r1_matrix_telemetry.jsonl` |
| **OBSERVED** | Live requests to NSE archive at ~13:17 UTC failed with connection resets (`10054`) and 45s read timeouts. | P-C0 diagnostic-base check logs |
| **INFERRED** | R1 telemetry engine is safe for live deployment and will record the exact failure layer if endpoint instability recurs. | R1 non-blocking verification suite |
| **INFERRED** | Historical crawl encountered either transient endpoint instability, network-level blocks, or rate limiting during the 4.5-minute burst. | Synthesis of burst timing and current access volatility |
| **PLAUSIBLE BUT UNPROVEN** | Historical 318 losses were caused by origin/CDN rate limiting (HTTP 429). | Unproven; no attempt logs exist for 2026-09-11 |
| **PLAUSIBLE BUT UNPROVEN** | Historical 318 losses were caused by Akamai WAF access denial (HTTP 403). | Unproven; no attempt logs exist for 2026-09-11 |
| **PLAUSIBLE BUT UNPROVEN** | Historical 318 losses were caused by transport-layer connection drops or timeouts. | Unproven; no attempt logs exist for 2026-09-11 |
| **PLAUSIBLE BUT UNPROVEN** | Historical fetch requests were actually dispatched for all 318 pairs (historical invocation gap). | Unproven; lack of dispatch logs means execution is unproven |
| **UNKNOWN** | Historical HTTP status code distribution for the 318 losses. | Strictly UNKNOWN |
| **UNKNOWN** | Historical exception distribution for the 318 losses. | Strictly UNKNOWN |
| **UNKNOWN** | Historical failure layer distribution for the 318 losses. | Strictly UNKNOWN |
| **UNKNOWN** | Historical retry-exhaustion distribution for the 318 losses. | Strictly UNKNOWN |
| **UNKNOWN** | Exact historical request dispatch timing and ordering on 2026-09-11. | Strictly UNKNOWN |
| **UNKNOWN** | Exact client network IP, routing, or proxy environment on 2026-09-11. | Strictly UNKNOWN |
| **BLOCKED** | Universe V2 dataset freezing and downstream pipeline re-evaluations. | Blocked on acquisition diagnosis and resolution |
| **RULED OUT** | Pre-fetch filter hypothesis (`cohort_fetch_manifest.jsonl` filtering out zero-download FYs). | Disproven by P-C0 (file was post-hoc labeling artifact) |
| **RULED OUT** | Client header/cookie asymmetry as cause of current failure. | Disproven by P-C0R (10/10 paired arms succeeded) |
| **RULED OUT** | Persistent payload corruption for successful downloads. | Disproven by P-C0 (valid ZIPs/PDFs verified with qpdf) |
| **RULED OUT** | Behavioral drift introduced by R1 telemetry. | Disproven by R1 (15/15 behavioral equivalence fixtures match) |

---

## 7. Reconciliation with P-C0 / P-C0R / P-M5

### What R1 Now Makes Measurable
- For any future fetch attempt (whether in a diagnostic probe or a live run), R1 records:
  1. The exact attempt number (1, 2, 3) and whether retries were exhausted.
  2. The precise HTTP status code (distinguishing 403 Forbidden vs 429 Too Many Requests vs 503 Service Unavailable).
  3. The exact architectural failure layer (`L0_DNS`, `L1_CONNECT`, `L2_TLS`, `L3_HTTP`, `L4_RECEIPT`, `L6_VALIDATION`).
  4. The exact Python exception class (`httpx.ConnectError`, `httpx.ReadTimeout`, `zipfile.BadZipFile`).
  5. The client-perceived elapsed latency in milliseconds.
  6. The cryptographic SHA-256 hash of the redacted URL.

### What R1 Does NOT Make Historically Recoverable
- R1 was implemented on 2026-09-17. The 318 historical losses occurred on 2026-09-11 under pre-R1 code (`0fb8cbf`) that had zero structured logging.
- Telemetry added post-hoc cannot travel back in time. The historical cause of the 2026-09-11 losses remains permanently **UNKNOWN** from retrospective observation alone.

### Which P-C0 / P-C0R Questions Are Now Better Instrumented
- In P-C0, the failure at ~13:17 UTC (0/9 successes) was captured only through raw console output and terminal stack traces.
- In P-C0R, the pilot executed during a stable open window (14:40–15:20 UTC) where 50/50 probes succeeded, so zero failure mechanisms could be observed.
- If a future experiment encounters a closed or volatile window, R1 will persist full attempt-level structured telemetry, instantly resolving whether failures are transport-layer drops (`L1_CONNECT` / `L4_RECEIPT`) or HTTP rejections (`L3_HTTP` 429/403).

### Status of Previous Hypotheses
- **Pre-fetch filter:** RULED OUT in P-C0; R1 confirms that no filtering exists in `fetch.py`.
- **Client header asymmetry:** RULED OUT in P-C0R; default headers succeed identically to browser/discovery headers in open windows.
- **Payload corruption:** RULED OUT in P-C0; URLs yield valid binary ZIP/PDF archives.
- **Temporal access variation:** CURRENTLY REPRODUCED; endpoint stability varies dramatically across sub-hour windows.
- **Transport vs. HTTP status failure:** UNRESOLVED in the wild; fully instrumented and ready to be captured by R1.

---

## 8. Remaining Hypotheses

The following hypothesis table accounts for all plausible mechanisms explaining why archive downloads fail:

| ID | Hypothesis Name | Supporting Evidence | Contrary Evidence | Current Status | Distinguishing Observation | Confidence |
|:---:|---|---|---|:---:|---|:---:|
| **H1** | **Transient Transport Collapse** (TCP reset, connect abort, read timeout) | P-C0 observed connection resets (`10054`) and 45s timeouts at ~13:17 UTC. | Probes in P-C0R at 14:40–15:20 UTC had 0 connection drops across 50 probes. | `PLAUSIBLE BUT UNPROVEN` | Live telemetry records `first_failure_layer in ('L1_CONNECT', 'L4_RECEIPT')` with `status_code=null` and `ConnectError`/`ReadTimeout`. | MEDIUM |
| **H2** | **Rate / Cadence Limiting** (Akamai WAF or origin throttle) | Historical 512 requests ran in a dense 4.5-minute burst (~1.9 req/sec). | P-C0R polite pacing (1 req / 1–5s) had 100% success; no 429 observed under polite pacing. | `PLAUSIBLE BUT UNPROVEN` | Live telemetry records `first_failure_layer='L3_HTTP'` with `status_code=429` or `403` when request rate increases. | MEDIUM |
| **H3** | **Temporal Access Window Restriction** (Time-of-day / market-hours maintenance) | Documented transition from 0% success (~13:17 UTC) to 100% success (~13:59 UTC) on identical code and network. | P-C0R 40-minute window was uniformly 100% stable; temporal boundaries are not yet mapped. | `CURRENTLY REPRODUCED` (Variation observed) | Multi-window longitudinal probe demonstrates failure concentration in specific time windows. | HIGH |
| **H4** | **URL-Specific Stale / Missing Artifacts** | 313 of the 318 un-downloaded URLs have never been probed in any diagnostic experiment. | All 5 zero-download URLs probed in P-C0/P-C0R existed and returned valid payloads. | `PLAUSIBLE BUT UNPROVEN` | Live telemetry records `status_code=404` or `VALIDATION_FAILURE` persistently for specific URLs across all time windows. | LOW |
| **H5** | **Historical Invocation Gap** (Requests never dispatched on 2026-09-11) | Historical timestamps show 3 discrete FY bursts totaling only 194 successful writes; no failed records written. | Pre-R1 code had silent fall-through on 403/429/503 which naturally produces zero writes. | `PLAUSIBLE BUT UNPROVEN` | Historical runtime logs or external dispatch records confirming script crash. | MEDIUM |

---

## 9. Information Gap

> **The Fundamental Information Gap:**
> Prior to R1, fetch failures were invisible on disk. In P-C0R, the endpoint was in an open window, resulting in 50/50 successes and zero failure observations.
>
> Therefore, we have **never captured structured, attempt-level telemetry from un-downloaded historical URLs under volatile or failing conditions**.
>
> Specifically, we do not know:
> 1. When the endpoint rejects requests, does it fail at the **transport layer** (`first_failure_layer='L1_CONNECT'`, `status_code=null`) or the **HTTP application layer** (`first_failure_layer='L3_HTTP'`, `status_code=429/403`)?
> 2. Do failures correlate with **request cadence** (rapid burst vs. polite spacing) or strictly with **temporal windows** (calendar time)?
> 3. Do un-downloaded URLs from the other 3 unsampled zero-download FYs (FY2019, FY2020, FY2023) exhibit persistent URL-level defects?

---

## 10. Proposed Next Experiment: P-R1X

### Title
**P-R1X: Instrumented Acquisition Telemetry Pilot**

### Objective
Deploy the frozen R1 attempt-level telemetry engine (`r1-v1`) in a controlled, non-destructive live acquisition probe against the frozen 10-observation diagnostic sample across 3 scheduled temporal windows, capturing structured telemetry on any failures to distinguish transport collapse (`L1_CONNECT` / `L4_RECEIPT`) from HTTP application rejection (`L3_HTTP` 429/403) and validation failure (`L6_VALIDATION`).

### Hypothesis
If acquisition failures occur on `nsearchives.nseindia.com`, R1 failure telemetry will capture the exact failure layer, distinguishing transport-layer TCP resets / timeouts (`status_code=null`) from HTTP rate-limit / WAF challenges (`status_code in (429, 403)`). If all attempts succeed across all windows, it will establish that the sampled un-downloaded URLs remain accessible under polite acquisition pacing during those windows.

### Evidence Basis
1. P-M5 established 318 un-downloaded losses with 0.0% failure reason logging.
2. P-C0 established acute temporal access variation at `nsearchives.nseindia.com` (0/9 at ~13:17 UTC vs 10/10 at ~13:59 UTC).
3. P-C0R proved that client configuration asymmetry does not explain failures (10/10 paired arms succeeded identically).
4. R1 established frozen, non-blocking failure telemetry (`r1-v1`) with verified behavioral invariance.

### Frozen Candidate Population Source
- **Authoritative Source:** `reports/pc0_sample_manifest.json` from P-C0
- **SHA-256 Digest:** `394c628d842bdcf967b6dd82ab695fb4b17a88602c7c79c0b17561a3d931bb0e`
- **Originating Table:** `reports/pm5_stage_table.csv` (SHA-256: `30e93b59ac689f00fab182583fb25883322e429be42b4ba14e13a1011b916dc9`)

### Population Inclusion Rule
The exact 10 observations pre-frozen in `reports/pc0_sample_manifest.json`:
- **Target Group (`DOWNLOAD_ZERO_FY`, $N=5$):**
  `discovered=True, downloaded=False`, drawn from strictly zero-download fiscal years:
  1. `INE002A01018::FY2010` (Reliance Industries, FY2010)
  2. `INE040A01034::FY2014` (HDFC Bank, FY2014)
  3. `INE081A01020::FY2016` (Tata Steel, FY2016)
  4. `INE171A01029::FY2021` (Federal Bank, FY2021)
  5. `INE226A01021::FY2022` (Voltas, FY2022)
- **Control Group (`DOWNLOAD_NONZERO_FY_CONTROL`, $N=5$):**
  `discovered=True, downloaded=True`, drawn from non-zero download fiscal years:
  6. `INE002A01018::FY2012` (Reliance Industries, FY2012)
  7. `INE009A01021::FY2013` (Infosys, FY2013)
  8. `INE040A01034::FY2017` (HDFC Bank, FY2017)
  9. `INE044A01036::FY2018` (Sun Pharma, FY2018)
  10. `INE081A01020::FY2024` (Tata Steel, FY2024)

### Sampling Rule
100% census of the frozen 10-observation manifest. No sampling, no replacement, no substitution, no adaptive exclusion.

### Sample Size
$N = 10$ distinct company-year observations (5 targets + 5 controls).

### Independent Variable
**Temporal observation window:** Probing the fixed 10-observation sample across 3 pre-scheduled temporal windows separated by 30 minutes:
- Window 1: $T_0$
- Window 2: $T_0 + 30$ minutes
- Window 3: $T_0 + 60$ minutes

### Controlled Variables
1. **Client Configuration:** Standard unseeded `httpx.Client` (proven invariant in P-C0R).
2. **Request Ordering:** Deterministic sequential order (Observations 1 through 10).
3. **Pacing:** `HostLimiter` with minimum 2.0 seconds pause between consecutive requests.
4. **Retry Policy:** Frozen production policy (`retries=3`, timeout=120.0s, backoff `5 * (attempt + 1)**2` on 403/429/503).
5. **Telemetry Sink:** Active local JSONL sink via `--telemetry-path`.

### Measurements
1. **Per-observation outcome:** `StoredDoc` (success) vs `None` (silent fall-through on 403/429/503 exhaustion or validation abort) vs raised exception (`ConnectError`, `ReadTimeout`).
2. **Per-attempt structured telemetry:** Persisted `r1-v1` records containing `attempt_number`, `terminal_state`, `retry_exhausted`, `error_type`, `status_code`, `first_failure_layer`, `exception_class`, `bytes_received`, `elapsed_ms`, and `url_sha256`.

### Telemetry Fields Required
All mandatory fields of schema `r1-v1` plus optional architectural fields: `first_failure_layer`, `exception_class`, `bytes_received`, `elapsed_ms`, `response_content_type`.

### Number of Attempts
- Up to 3 attempts per observation per window as dictated by the frozen retry policy.
- Minimum total HTTP requests: 30 (if all succeed on attempt 1 across all 3 windows).
- Maximum total HTTP requests: 90 (if all exhaust 3 retries across all 3 windows).

### Attempt Schedule
- **Window 1:** $T_0$ (10 observations sequenced with 2.0s polite pause)
- **Window 2:** $T_0 + 30$ min (10 observations sequenced with 2.0s pause)
- **Window 3:** $T_0 + 60$ min (10 observations sequenced with 2.0s pause)

### Success Criteria
The experiment successfully completes if:
1. All 3 scheduled windows execute without harness crashes.
2. All attempt outcomes are recorded in structured evaluation logs.
3. For every failed attempt, a valid `r1-v1` record is persisted to the designated JSONL file.
4. The telemetry writer failure count is exactly 0.

### Failure Criteria
The experiment fails if:
1. The test harness crashes or raises unhandled exceptions.
2. Failures occur without emitting corresponding `r1-v1` telemetry records.
3. Emitted telemetry violates schema `r1-v1`.
4. Telemetry emission modifies acquisition return values or control flow.

### Interpretation Rules
1. **Transport Collapse Hypothesis (H1) Supported:** If failures occur and are predominantly characterized by `first_failure_layer in ('L1_CONNECT', 'L4_RECEIPT')` with `status_code=null` and `exception_class` of `ConnectError`, `ReadTimeout`, or `ConnectionResetError`.
2. **HTTP Rejection / Rate Limiting Hypothesis (H2) Supported:** If failures occur and are predominantly characterized by `first_failure_layer='L3_HTTP'` with `status_code=429` (rate limit) or `403` (Akamai challenge).
3. **Validation Failure Hypothesis Supported:** If failures occur with `status_code=200` and `first_failure_layer='L6_VALIDATION'` (`BadZipFile` or unrepairable PDF).
4. **Persistent Availability / Pacing Hypothesis Supported:** If all 10 observations succeed across all 3 windows (100% success), confirming that the un-downloaded URLs remain accessible under polite pacing, and that failures require either closed temporal windows or burst-load conditions.
5. **URL-Specific Defect (H4) Supported:** If target zero-download observations fail while control observations succeed within the exact same window.

### Stop Conditions
1. Immediate halt if remote host returns persistent 403 with IP-ban / block signature.
2. Immediate halt if telemetry writer fails to write to disk.
3. Normal completion after Window 3.

### What the Experiment Cannot Prove
1. **Cannot prove the historical cause of the 318 losses on 2026-09-11:** Historical telemetry does not exist; retrospective certainty is impossible.
2. **Cannot prove behavior of unsampled zero-download fiscal years:** FY2019, FY2020, and FY2023 were not included in the 10-observation sample.
3. **Cannot prove endpoint response to full 512-request burst crawl:** The experiment uses polite pacing ($N=10$, 2.0s pause) to preserve non-destructive operation.

---

## 11. Frozen Population Provenance

The candidate population for P-R1X is derived strictly from historical artifacts without post-hoc selection:

```
P-M5 Funnel Audit (2026-09-17 10:25 UTC)
reports/pm5_stage_table.csv (SHA-256: 30e93b59ac689f00fab182583fb25883322e429be42b4ba14e13a1011b916dc9)
├── 576 Total Company-Years
├── 512 Discovered Reports
└── 318 Un-Downloaded Losses (0.0% reason codes)
      │
      ▼
P-C0 Coverage Diagnosis Sample Freeze (2026-09-17 13:50 UTC)
reports/pc0_sample_manifest.json (SHA-256: 394c628d842bdcf967b6dd82ab695fb4b17a88602c7c79c0b17561a3d931bb0e)
├── 5 DOWNLOAD_ZERO_FY Targets (FY2010, 2014, 2016, 2021, 2022)
└── 5 DOWNLOAD_NONZERO_FY_CONTROL Targets (FY2012, 2013, 2017, 2018, 2024)
      │
      ▼
R1 Test Matrix Construction (2026-09-17 16:19 UTC)
reports/r1_telemetry/r1_generation_summary.json (SHA-256: 92e2dc8e4a82eec021dd1c91684b9b04ab51a42367cf5a6099a8e200135dce05)
└── Synthetic fixtures parametrized using exact company_ids from pc0_sample_manifest.json
      │
      ▼
P-R1X Proposed Population
Verbatim census of reports/pc0_sample_manifest.json (N = 10)
```

---

## 12. Production-Change Decision

> ### DECISION: **INSUFFICIENT EVIDENCE**

### Rationale
1. **Historical Causality is Unproven:** No historical per-attempt telemetry exists for the 2026-09-11 crawl.
2. **Telemetry to Date is Synthetic:** The 17 records in R1 were generated under mock/synthetic conditions to verify schema correctness; zero live failure telemetry has been collected in the wild.
3. **Current Probes Succeeded Under Baseline Code:** P-C0R demonstrated 100% success (50/50) under standard fetch client configurations during open windows, and ruled out client header asymmetry.
4. **Failure Layer is Unknown in the Wild:** It is unknown whether live failures are dominated by `L1_CONNECT` TCP resets, `L4_RECEIPT` timeouts, or `L3_HTTP` 429 rate limits.
5. **Intervention Risks Harm:** Modifying retry counts, backoff timings, session pooling, or headers before identifying the failure layer risks masking root causes, triggering aggressive IP bans, or degrading pipeline performance.

**Action:** No production acquisition code may be modified. Live instrumentation must precede any intervention.

---

## 13. Limitations

1. **Retrospective Barrier:** Historical loss distribution across the 318 un-downloaded documents cannot be recovered by any future experiment.
2. **Sample Breadth:** The 10-observation sample covers 5 of the 8 zero-download fiscal years. Observations from FY2019, FY2020, and FY2023 remain unsampled.
3. **Pacing Limitation:** A polite probe (2.0s pause) cannot test whether burst-load concurrency triggers Akamai rate limiting without running a potentially destructive high-rate probe.
4. **Exchange CDN Volatility:** Observed access conditions on `nsearchives.nseindia.com` may change across days or weeks, meaning current probe results describe current endpoint dynamics, not permanent physical constants.

---

## 14. Final Verdict

# TELEMETRY ANALYSIS COMPLETE — NEXT EXPERIMENT SPECIFIED

---

*Analysis completed cleanly. No production code altered. No network traffic dispatched. R1 base frozen.*
