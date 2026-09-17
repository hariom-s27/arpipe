# P-R1X Execution Runbook

## 1. Protocol & Provenance Metadata
- **Protocol Version:** P-R1X v1.2 (Final Execution Protocol)
- **Engineering Base SHA:** `56497721cb68c4831e6f225074b6bd7ea17bffb0`
- **Analytical Reference Commit:** `3beee249db36f9fdd1a8a2e01d6fdc3c6024d870`
- **Worktree Directory:** `D:\sem_iitk\sem9\thesis\sep_week1\arpipe-pr1x-execution`
- **Execution Branch:** `pr1x-execution`
- **P-C0 Manifest Path:** `reports/pc0_sample_manifest.json`
- **P-C0 Manifest SHA-256:** `394c628d842bdcf967b6dd82ab695fb4b17a88602c7c79c0b17561a3d931bb0e`
- **Originating P-M5 Stage-Table SHA-256:** `30e93b59ac689f00fab182583fb25883322e429be42b4ba14e13a1011b916dc9`
- **Pre-Execution Freeze UTC:** `2026-09-17 19:58:00 UTC`

---

## 2. Frozen Temporal Observation Windows & 90-Minute Spacing Rule
The experiment specifies three distinct temporal observation windows separated by 90 minutes of nominal spacing to provide runtime headroom for sequential observations and retry backoffs.

### Exact Predeclared Window Start Timestamps
- **Window 1 (T0):** `2026-09-17 20:05:00 UTC`
- **Window 2 (T0 + 90m):** `2026-09-17 21:35:00 UTC`
- **Window 3 (T0 + 180m):** `2026-09-17 23:05:00 UTC`

**Verification:**
- $\text{Window 2} - \text{Window 1} = 90\text{ minutes}$
- $\text{Window 3} - \text{Window 1} = 180\text{ minutes}$

*Immutability Rule:* Once frozen in this runbook before the first live request, these timestamps **MUST NOT** be altered under any circumstances. No rescheduling is permitted due to observation outcomes, durations, provider responses, or delays.

---

## 3. Concurrency Model & Sequential Execution Rule
- **Concurrency:** Strictly sequential execution stream.
- **Workers:** Exactly 1 worker.
- **Rules:**
  - One orchestration stream.
  - One active observation at a time.
  - No thread pools, async event loops, multiprocessing, background fetchers, or overlapping calls.
  - Only the committed frozen R1 acquisition path (`fetch.fetch_one`) is invoked.

---

## 4. Window Non-Overlap Rule
- A later window **MUST NOT** begin while a preceding window's observation sequence is still active.
- If Window 1 is still active at `2026-09-17 21:35:00 UTC`:
  - Do NOT overlap windows.
  - Do NOT launch parallel clients or workers.
  - Do NOT pause Window 1 to start Window 2.
  - Do NOT reschedule Window 2.
  - Record `NOT_STARTED_DUE_TO_PRIOR_WINDOW_ACTIVE` for Window 2.
  - Mark experiment status as `INCOMPLETE`.
- Similarly, if Window 2 is active at `2026-09-17 23:05:00 UTC`, record `NOT_STARTED_DUE_TO_PRIOR_WINDOW_ACTIVE` for Window 3 and mark `INCOMPLETE`.

---

## 5. Frozen Population & Exact Observation Order
Population is exactly $N = 10$ observations from `reports/pc0_sample_manifest.json` (5 target zero-download FYs, 5 control non-zero FYs). This is a census of the pilot sample, not the 576-observation universe. No substitutions, replacements, or adaptive selections.

The exact sequential execution order in EVERY window:

| Seq | Observation ID | Company Name | FY | Designation | Exact Target URL |
|---|---|---|---|---|---|
| 1 | `INE002A01018::FY2010` | Reliance Industries Limited | 2010 | TARGET (`DOWNLOAD_ZERO_FY`) | `https://nsearchives.nseindia.com/annual_reports/AR_RELIANCE_2009_2010_20082010120000.zip` |
| 2 | `INE040A01034::FY2014` | HDFC Bank Limited | 2014 | TARGET (`DOWNLOAD_ZERO_FY`) | `https://nsearchives.nseindia.com/annual_reports/AR_3393_HDFCBANK_2013_2014_12062014114216.zip` |
| 3 | `INE081A01020::FY2016` | Tata Steel Limited | 2016 | TARGET (`DOWNLOAD_ZERO_FY`) | `https://nsearchives.nseindia.com/annual_reports/AR_9362_TATASTEEL_2015_2016_16082016104323.zip` |
| 4 | `INE171A01029::FY2021` | The Federal Bank Limited | 2021 | TARGET (`DOWNLOAD_ZERO_FY`) | `https://nsearchives.nseindia.com/annual_reports/AR_18152_FEDERALBNK_2020_2021_17062021235201_18062021070010.zip` |
| 5 | `INE226A01021::FY2022` | Voltas Limited | 2022 | TARGET (`DOWNLOAD_ZERO_FY`) | `https://nsearchives.nseindia.com/annual_reports/AR_19956_VOLTAS_2021_2022_28052022144748_05282022150002.zip` |
| 6 | `INE002A01018::FY2012` | Reliance Industries Limited | 2012 | CONTROL (`DOWNLOAD_NONZERO_FY_CONTROL`) | `https://nsearchives.nseindia.com/annual_reports/AR_RELIANCE_2011_2012_29062012101059.zip` |
| 7 | `INE009A01021::FY2013` | Infosys Limited | 2013 | CONTROL (`DOWNLOAD_NONZERO_FY_CONTROL`) | `https://nsearchives.nseindia.com/annual_reports/AR_27_INFY_2012_2013_20062013105245.zip` |
| 8 | `INE040A01034::FY2017` | HDFC Bank Limited | 2017 | CONTROL (`DOWNLOAD_NONZERO_FY_CONTROL`) | `https://nsearchives.nseindia.com/annual_reports/AR_10840_HDFCBANK_2016_2017_25072017151900.zip` |
| 9 | `INE044A01036::FY2018` | Sun Pharmaceutical Industries Limited | 2018 | CONTROL (`DOWNLOAD_NONZERO_FY_CONTROL`) | `https://nsearchives.nseindia.com/annual_reports/AR_13921_SUNPHARMA_2017_2018_01102018175233.zip` |
| 10 | `INE081A01020::FY2024` | Tata Steel Limited | 2024 | CONTROL (`DOWNLOAD_NONZERO_FY_CONTROL`) | `https://nsearchives.nseindia.com/annual_reports/AR_24166_TATASTEEL_2023_2024_2206202419194.pdf` |

---

## 6. Verified R1 Client Configuration
- Client: `httpx.Client(headers={"User-Agent": discover.UA}, timeout=120, follow_redirects=True)`
- User-Agent: `Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36`
- Streaming: `client.stream("GET", ref.url, follow_redirects=True, timeout=120.0)`
- Chunks & Buffer: `1 << 18` (256 KB) chunks, `max_bytes = 400 << 20` (400 MB)
- Prohibitions: No `requests.Session`, no cookies, no custom headers (`Accept`, `Referer`, `Origin`), no session state reuse.

---

## 7. Verified R1 Pacing & Retry Policy
- **Pacing:** `fetch.HostLimiter(min_interval=1.5)` (enforces minimum 1.5 seconds elapsed between requests targeting the same host).
- **Retries:** Maximum 3 attempts (`retries=3`).
- **Retry Backoff Schedule:**
  - Status 403, 429, 503: `time.sleep(5 * (attempt + 1) ** 2)` -> 5s, 20s, 45s.
  - General Exceptions: `time.sleep(2 * (attempt + 1))` -> 2s, 4s, 6s.

---

## 8. Observation Start / End Definitions
- `observation_start_utc`: The UTC timestamp immediately before entering the frozen R1 acquisition call for that observation (including any HostLimiter wait).
- `observation_end_utc`: The UTC timestamp immediately after the frozen R1 acquisition call returns its terminal result.
- `elapsed_ms`: Monotonic clock duration (`(t1_mono - t0_mono) * 1000.0`). Wall-clock UTC timestamps are used for labeling only.

---

## 9. Predeclared Safety Stop Signals
Ordinary failures (HTTP 403, 429, 503, timeouts, resets, connection errors) are observations, NOT stop conditions.
Live requests must halt **ONLY** for explicitly predeclared safety signals:
1. **WAF / Human-Verification Challenge:** Remote origin explicitly presents a CAPTCHA, Cloudflare challenge, or bot interstitial.
2. **Provider Block:** Remote origin response explicitly states that client IP/access is permanently blocked, banned, or prohibited (ordinary 403 by itself is not sufficient).
3. **Security Boundary:** Explicit credential, TLS certificate validation failure, or trust boundary breakdown requiring operator intervention.
4. **Provider Instruction:** Remote origin administrator, security team, or response header/body explicitly demands client cessation.
5. **Infrastructure Safety:** Local system failure (e.g. disk exhaustion, NIC failure, socket exhaustion) making continued execution unsafe.

---

## 10. Unexpected Interruption / Crash Rule
If execution is interrupted or crashes:
- Preserve all artifacts and telemetry already written to disk.
- Do NOT automatically rerun interrupted observations or windows.
- Mark affected observations/windows as `INCOMPLETE`.
- Do NOT add replacement observations or substitute timestamps.
