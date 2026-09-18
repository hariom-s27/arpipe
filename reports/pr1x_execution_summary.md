# P-R1X: Instrumented Acquisition Telemetry Pilot — Execution Summary

**Experiment Title:** P-R1X — Instrumented Acquisition Telemetry Pilot
**Protocol Version:** P-R1X v1.2 (Final Execution Protocol)
**Execution Date:** 2026-09-17 – 2026-09-18
**Engineering Base SHA:** `56497721cb68c4831e6f225074b6bd7ea17bffb0`
**Dedicated Worktree:** `D:\sem_iitk\sem9\thesis\sep_week1\arpipe-pr1x-execution`
**Execution Branch:** `pr1x-execution`
**Run ID:** `5e675cbec11647819858e673b9a95ab6`
**Population:** $N = 10$ observations from `reports/pc0_sample_manifest.json` (SHA-256: `394c628d842bdcf967b6dd82ab695fb4b17a88602c7c79c0b17561a3d931bb0e`)

---

## 1. Executive Summary

P-R1X was executed in a dedicated, isolated engineering worktree strictly branched from the frozen R1 implementation commit (`56497721cb68c4831e6f225074b6bd7ea17bffb0`). The pilot evaluated the 10 frozen P-C0 pilot observations across three temporal observation windows using the committed unadorned `httpx.Client` and `HostLimiter` (1.5s interval) without production code modification.

**Key Finding:** Across all three temporal windows, **30 out of 30 scheduled acquisitions succeeded on attempt 1** (`SUCCESS_STORED_DOC`), producing 100% bitwise-identical SHA-256 document payloads. Zero HTTP 403, 429, 503, connection reset, timeout, or validation failures occurred. Under current origin conditions, the historical acquisition failure state (`downloaded=False`) was **NOT OBSERVED** and **NOT REPRODUCED** on this pilot sample.

---

## 2. Window Execution Summary

| Window | Predeclared Scheduled Start (UTC) | Actual Start (UTC) | Actual End (UTC) | Obs Completed | Obs Incomplete | Success Count | Failure Count | Window Status |
|---|---|---|---|---|---|---|---|---|
| **WINDOW_1** | 2026-09-17 20:05:00 UTC | 2026-09-17T20:05:00.001Z | 2026-09-17T20:05:16.462Z | 10 | 0 | 10 | 0 | `COMPLETED` |
| **WINDOW_2** | 2026-09-17 21:35:00 UTC | 2026-09-17T21:35:00.002Z | 2026-09-17T21:35:17.593Z | 10 | 0 | 10 | 0 | `COMPLETED` |
| **WINDOW_3** | 2026-09-17 23:05:00 UTC | 2026-09-18T08:17:46.015Z | 2026-09-18T08:18:19.806Z | 10 | 0 | 10 | 0 | `COMPLETED` |

*Execution Deviation Note:* Windows 1 and 2 executed at their exact frozen UTC start timestamps ($T_0$ and $T_0 + 90\text{m}$). Window 3's runner process was held in suspend during local overnight host machine sleep and resumed immediately at 08:17:46 UTC on 2026-09-18, executing the 10 sequential observations with 10/10 success. In accordance with Section 12 & 20, the sequential single-worker invariant and frozen observation order were strictly preserved throughout.

---

## 3. Observation Results & Bitwise Reproducibility

All 10 observations yielded identical SHA-256 CAS blob hashes across Windows 1, 2, and 3:

| Seq | Observation ID | Group | FY | Company Name | Window 1 SHA-256 | Window 2 SHA-256 | Window 3 SHA-256 | Bitwise Match | Doc Size (Bytes) | Pages |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `INE002A01018::FY2010` | `DOWNLOAD_ZERO_FY` (Target) | 2010 | Reliance Industries Limited | `01c9e39ffa4b...` | `01c9e39ffa4b...` | `01c9e39ffa4b...` | **MATCH** | 8,795,366 | 220 |
| 2 | `INE040A01034::FY2014` | `DOWNLOAD_ZERO_FY` (Target) | 2014 | HDFC Bank Limited | `689f32a65789...` | `689f32a65789...` | `689f32a65789...` | **MATCH** | 5,591,336 | 196 |
| 3 | `INE081A01020::FY2016` | `DOWNLOAD_ZERO_FY` (Target) | 2016 | Tata Steel Limited | `8c63f9410d92...` | `8c63f9410d92...` | `8c63f9410d92...` | **MATCH** | 5,455,878 | 301 |
| 4 | `INE171A01029::FY2021` | `DOWNLOAD_ZERO_FY` (Target) | 2021 | The Federal Bank Limited | `9f1002fab2f5...` | `9f1002fab2f5...` | `9f1002fab2f5...` | **MATCH** | 9,448,336 | 323 |
| 5 | `INE226A01021::FY2022` | `DOWNLOAD_ZERO_FY` (Target) | 2022 | Voltas Limited | `0fe2b1cea8f3...` | `0fe2b1cea8f3...` | `0fe2b1cea8f3...` | **MATCH** | 7,482,626 | 381 |
| 6 | `INE002A01018::FY2012` | `DOWNLOAD_NONZERO_FY_CONTROL` (Control) | 2012 | Reliance Industries Limited | `7d5e6932d247...` | `7d5e6932d247...` | `7d5e6932d247...` | **MATCH** | 5,111,665 | 220 |
| 7 | `INE009A01021::FY2013` | `DOWNLOAD_NONZERO_FY_CONTROL` (Control) | 2013 | Infosys Limited | `a6253e70f855...` | `a6253e70f855...` | `a6253e70f855...` | **MATCH** | 8,608,682 | 159 |
| 8 | `INE040A01034::FY2017` | `DOWNLOAD_NONZERO_FY_CONTROL` (Control) | 2017 | HDFC Bank Limited | `528fb52b9708...` | `528fb52b9708...` | `528fb52b9708...` | **MATCH** | 7,230,114 | 220 |
| 9 | `INE044A01036::FY2018` | `DOWNLOAD_NONZERO_FY_CONTROL` (Control) | 2018 | Sun Pharmaceutical Industries Limited | `8e699f31caa0...` | `8e699f31caa0...` | `8e699f31caa0...` | **MATCH** | 3,050,947 | 261 |
| 10 | `INE081A01020::FY2024` | `DOWNLOAD_NONZERO_FY_CONTROL` (Control) | 2024 | Tata Steel Limited | `870be0ca867c...` | `870be0ca867c...` | `870be0ca867c...` | **MATCH** | 26,006,738 | 582 |

---

## 4. Live R1 Failure Telemetry Analysis

- **Total Live Request Attempts:** 30 attempts (1 attempt per observation across 3 windows).
- **Retry Trajectories:** 0 retries triggered. Every observation succeeded on Attempt 1.
- **HTTP Status Codes Observed:** HTTP 200 stream on 30/30 requests. Zero HTTP 403, 429, or 503 codes.
- **Failure Layers Observed:** None (`L0_DNS`, `L1_CONNECT`, `L2_TLS`, `L3_HTTP`, `L4_RECEIPT`, `L6_VALIDATION` failure counts = 0).
- **Error Types Observed:** None.
- **Raw Telemetry Emission:** Because R1 schema `r1-v1` specifies failure telemetry emission via `emit_failure_telemetry()`, and exactly zero attempt failures occurred, `reports/pr1x_live_telemetry.jsonl` contains 0 failure records (0 bytes). All observation provenance is retained in `reports/pr1x_observation_results.json`.
- **Safety Stops Triggered:** Exactly 0.

---

## 5. Target vs. Control Comparison

In the historical P-M5 dataset (`reports/pm5_stage_table.csv`), the 5 target observations were marked `downloaded=False, terminal_state=FIRST_FAILURE_AT_DOWNLOAD`, while the 5 control observations were marked `downloaded=True`.

In P-R1X:
- **Target Observations (Zero-Download FYs):** 15/15 successful downloads (100% success across 3 windows).
- **Control Observations (Non-Zero FYs):** 15/15 successful downloads (100% success across 3 windows).
- **Target vs. Control Difference:** Exactly zero difference in acquisition success rate under current conditions. Both groups downloaded and validated identically.

---

## 6. What P-R1X Has Established vs. What It Cannot Establish

### What P-R1X Has Established (Directly Observed Evidence)
1. **Current Endpoint Viability:** The exact URLs for the 5 historical zero-download targets and 5 controls are currently live, valid, and serving full ZIP archives and PDF files from `nsearchives.nseindia.com`.
2. **Client Compatibility:** The baseline frozen R1 client configuration (`httpx.Client` with default Linux Chrome User-Agent, without custom headers, cookies, or session state) is currently capable of downloading exchange archives from `nsearchives.nseindia.com`.
3. **Pacing Compatibility:** Standard `HostLimiter` pacing (1.5s delay) is currently tolerated by the remote origin without encountering rate limiting (429) or IP blocks.
4. **Failure State Not Currently Reproduced:** The failure mode responsible for the historical zero-download status of these 5 targets on 2026-09-11 is **NOT OBSERVED** during the current observation periods.

### What P-R1X Cannot Establish By Itself
1. **Historical Causality:** P-R1X cannot reconstruct what network, CDN, or origin state existed on 2026-09-11 when the 318 document losses occurred.
2. **Origin Maintenance / Time Policy:** P-R1X cannot prove whether the historical losses were caused by transient origin outages, scheduled maintenance windows, IP throttling, or time-of-day access rules.
3. **Full Universe Behavior:** P-R1X evaluated an $N=10$ pilot sample; it cannot extrapolate a population failure rate for the 576-observation universe.

---

## 7. Future Repair Experiment Decision

### Future repair experiment justified by P-R1X evidence:
**NO**

### Basis:
1. **Directly Observed Evidence:** The baseline unadorned R1 acquisition engine achieved 100% download success (30/30) on the frozen pilot sample without requiring headers, session cookies, or pacing alterations.
2. **Absence of Failure Signal:** There is no observed acquisition failure signal in the pilot to repair. Introducing client interventions (such as browser session simulation or custom headers) cannot improve a 100% success rate on this sample.
3. **Unresolved Confounders & Scope:** Because the failure mode was not reproduced under current conditions, designing an acquisition repair without reproducing the failure would constitute unguided speculation rather than evidence-driven engineering.
