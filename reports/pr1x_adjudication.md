# P-R1X: Forensic Adjudication Report
**Instrumented Acquisition Telemetry Pilot — Protocol Compliance & Adjudication**

- **Adjudication Phase:** Phase A (Final Forensic Adjudication)
- **Adjudication Date:** 2026-09-18
- **Adjudicator:** ARPipe Forensic Adjudication Agent
- **Governing Standard:** P-R1X v1.2 Frozen Execution Protocol & Runbook Section 10 Interruption Rule

---

## 1. Protocol Version
- **Protocol:** P-R1X v1.2 (Instrumented Acquisition Telemetry Pilot)
- **Pilot Population:** $N = 10$ observations (5 targets with historical `downloaded=False`, 5 controls with historical `downloaded=True`), frozen in `reports/pc0_sample_manifest.json` (SHA-256: `394c628d842bdcf967b6dd82ab695fb4b17a88602c7c79c0b17561a3d931bb0e`).
- **Nominal Design:** 3 temporal observation windows spaced at 90-minute intervals ($T_0$, $T_0 + 90\text{m}$, $T_0 + 180\text{m}$), strictly sequential single-worker execution, unadorned `httpx.Client` with `HostLimiter` (1.5s interval).

## 2. Engineering Base
- **Base Commit SHA:** `56497721cb68c4831e6f225074b6bd7ea17bffb0` (`r1-fetch-telemetry`)
- **Analytical Reference Commit:** `3beee249db36f9fdd1a8a2e01d6fdc3c6024d870` (`r1-telemetry-analysis`)

## 3. Execution Commit
- **Execution Commit SHA:** `0b1d595407eacb13b115811cdb610b3e1f56a767`
- **Commit Message:** `P-R1X: execute instrumented acquisition telemetry pilot`
- **Execution Run ID:** `5e675cbec11647819858e673b9a95ab6`

## 4. Execution Worktree Reference
- **Execution Worktree Path:** `D:\sem_iitk\sem9\thesis\sep_week1\arpipe-pr1x-execution`
- **Execution Branch:** `pr1x-execution`
- **Adjudication Worktree Path:** `D:\sem_iitk\sem9\thesis\sep_week1\arpipe-pr1x-adjudication`
- **Adjudication Branch:** `pr1x-adjudication`

---

## 5. Window 1 Evidence
- **Predeclared Scheduled Start:** `2026-09-17 20:05:00 UTC`
- **Actual Start Timestamp:** `2026-09-17T20:05:00.001357+00:00`
- **Actual End Timestamp:** `2026-09-17T20:05:16.462782+00:00`
- **Start Latency:** $+1.357\text{ ms}$ (adhered exactly to schedule)
- **Duration:** $16.461\text{ s}$
- **Observation Count:** 10 observations (10 completed, 0 incomplete)
- **Observation Sequence:** 1 to 10 matching `reports/pc0_sample_manifest.json` exactly
- **Execution Discipline:** Strictly sequential, single worker, no concurrency
- **Outcomes:** 10/10 `SUCCESS_STORED_DOC` on attempt 1 (100% HTTP 200, 0 retries, 0 exceptions)
- **Safety Stops:** 0 triggered
- **Window Adjudication:** **VALID** — Fully eligible for primary temporal analysis

## 6. Window 2 Evidence
- **Predeclared Scheduled Start:** `2026-09-17 21:35:00 UTC` (exactly $T_0 + 90\text{m}$)
- **Actual Start Timestamp:** `2026-09-17T21:35:00.002051+00:00`
- **Actual End Timestamp:** `2026-09-17T21:35:17.593142+00:00`
- **Start Latency:** $+2.051\text{ ms}$ (adhered exactly to schedule)
- **Duration:** $17.591\text{ s}$
- **Observation Count:** 10 observations (10 completed, 0 incomplete)
- **Observation Sequence:** 1 to 10 matching `reports/pc0_sample_manifest.json` exactly
- **Execution Discipline:** Strictly sequential, single worker, no concurrency
- **Outcomes:** 10/10 `SUCCESS_STORED_DOC` on attempt 1 (100% HTTP 200, 0 retries, 0 exceptions)
- **Safety Stops:** 0 triggered
- **Window Adjudication:** **VALID** — Fully eligible for primary temporal analysis

## 7. Window 3 Evidence
- **Predeclared Scheduled Start:** `2026-09-17 23:05:00 UTC` (nominal $T_0 + 180\text{m}$)
- **Actual Start Timestamp:** `2026-09-18T08:17:46.015193+00:00`
- **Actual End Timestamp:** `2026-09-18T08:18:19.806417+00:00`
- **Start Latency / Elapsed Delay:** $+33,166.015\text{ s}$ (**9 hours, 12 minutes, 46.015 seconds**)
- **Duration:** $33.791\text{ s}$
- **Observation Count:** 10 observations (10 completed, 0 incomplete)
- **Observation Sequence:** 1 to 10 matching `reports/pc0_sample_manifest.json` exactly
- **Execution Discipline:** Strictly sequential, single worker
- **Outcomes:** 10/10 `SUCCESS_STORED_DOC` on attempt 1 (100% HTTP 200, 0 retries, 0 exceptions)
- **Safety Stops:** 0 triggered
- **Window Adjudication:** **POST_INTERRUPTION_SUPPLEMENTAL** — Ineligible for primary temporal analysis

---

## 8. Interruption Evidence & Mechanism
1. **Timing Evidence:** Window 2 completed normally at `2026-09-17T21:35:17.593142+00:00`. The runner process scheduled Window 3 for `2026-09-17 23:05:00 UTC` and entered an inter-window wait loop (`time.sleep` in 30-second increments).
2. **Process / Host State:** The runner process did not execute Window 3 at `23:05:00 UTC`. Instead, execution resumed at `2026-09-18T08:17:46.015193+00:00`. Surviving runbook notes and code inspection confirm that the local host machine entered overnight sleep/suspend while the process blocked in `time.sleep()`. Upon host resume at 08:17:46 UTC, the remaining sleep duration evaluated to $\le 0$, prompting the runner to initiate Window 3 immediately.
3. **Delay Calculation:**
   $$\Delta t = \text{2026-09-18 08:17:46.015193 UTC} - \text{2026-09-17 23:05:00 UTC} = 33,166.015\text{ s} \approx 9\text{h } 12\text{m } 46\text{s}$$
4. **Governing Protocol Rule:** Under P-R1X v1.2 Runbook Section 10 (*Unexpected Interruption / Crash Rule*):
   - All artifacts already written are preserved.
   - Do NOT automatically rerun interrupted observations or windows.
   - Mark affected observations/windows as `INCOMPLETE`.
   - Do NOT add replacement observations or substitute timestamps.
   - Do NOT continue under a changed execution state unless a new protocol version is created.
5. **Verdict:** This governing rule is controlling. The runner should not have proceeded to execute Window 3 as if it were a valid scheduled temporal window after a 9-hour suspension. Because the run occurred, its artifacts are preserved as supplemental evidence, but it cannot be counted as the third temporal window in the primary analysis.

---

## 9. Protocol Compliance Assessment

| Requirement | Protocol Specification | Actual Execution | Compliance Status |
|---|---|---|---|
| Engineering Base SHA | `56497721cb68c4831e6f225074b6bd7ea17bffb0` | Matches exactly | **COMPLIANT** |
| Dedicated Worktree | Isolated worktree, no production change | Used `arpipe-pr1x-execution` | **COMPLIANT** |
| Sample Population | Exact 10 observations from manifest | 10 observations, zero substitution | **COMPLIANT** |
| Sequential Single Worker | 1 worker, sequential execution | Sequential single worker throughout | **COMPLIANT** |
| Client Configuration | Unadorned `httpx.Client`, UA only | Default UA, no cookies, no headers | **COMPLIANT** |
| Pacing Enforcement | `HostLimiter(min_interval=1.5)` | Enforced across all attempts | **COMPLIANT** |
| Window 1 Schedule | 2026-09-17 20:05:00 UTC | Started 20:05:00.001 UTC | **COMPLIANT** |
| Window 2 Schedule | 2026-09-17 21:35:00 UTC ($T_0 + 90\text{m}$) | Started 21:35:00.002 UTC | **COMPLIANT** |
| Window 3 Schedule | 2026-09-17 23:05:00 UTC ($T_0 + 180\text{m}$) | Started 2026-09-18 08:17:46 UTC | **NON-COMPLIANT** (Delayed by 9h 12m) |
| Interruption Handling | Mark incomplete, do not substitute | Window 3 executed late post-sleep | **NON-COMPLIANT** (Adjudicated as Supplemental) |

---

## 10. Primary Analysis-Eligible Observations
The primary temporal analysis dataset is restricted strictly to protocol-valid scheduled windows: **Window 1** and **Window 2**.

- **Valid Windows:** 2 (`WINDOW_1`, `WINDOW_2`)
- **Total Primary Observations:** 20 observations
- **Target Observations ($N_{\text{target}} = 10$):**
  - Window 1: 5 observations (`INE002A01018::FY2010`, `INE040A01034::FY2014`, `INE081A01020::FY2016`, `INE171A01029::FY2021`, `INE226A01021::FY2022`)
  - Window 2: 5 observations (identical 5 targets)
  - Outcome: 10/10 successful acquisitions (`SUCCESS_STORED_DOC`), 100% HTTP 200, 0 retries
- **Control Observations ($N_{\text{control}} = 10$):**
  - Window 1: 5 observations (`INE002A01018::FY2012`, `INE009A01021::FY2013`, `INE040A01034::FY2017`, `INE044A01036::FY2018`, `INE081A01020::FY2024`)
  - Window 2: 5 observations (identical 5 controls)
  - Outcome: 10/10 successful acquisitions (`SUCCESS_STORED_DOC`), 100% HTTP 200, 0 retries
- **Target vs. Control Difference:** 0.0% difference in acquisition success under tested conditions.
- **Bitwise Payload Reproducibility:** 10/10 document blobs across Window 1 and Window 2 are bitwise identical (matching SHA-256 hashes).

## 11. Supplemental Observations
- **Dataset:** Window 3 observations executed post-interruption at `2026-09-18 08:17:46 UTC`
- **Total Supplemental Observations:** 10 observations (5 targets, 5 controls)
- **Supplemental Outcomes:** 10/10 successful acquisitions (`SUCCESS_STORED_DOC`), 100% HTTP 200, 0 retries
- **Admissibility:** Excluded from primary temporal comparison. Retained in project archives as descriptive current-access evidence confirming that endpoints remained reachable after the 9-hour suspension.

---

## 12. Directly Observed Results

1. **Current Endpoint Reachability:** All 10 exchange URLs (5 target zero-download FYs and 5 control FYs) were successfully resolved, connected, streamed, and stored.
2. **Bitwise Consistency:** All 10 stored documents yielded identical SHA-256 hashes across all runs (Window 1, Window 2, and Window 3).
3. **No Active Failure Signal:** Exactly 0 retries, 0 connection errors, 0 timeouts, 0 HTTP error codes (403, 429, 503), and 0 safety stop signals occurred.
4. **Historical Failure Not Reproduced:** The historical condition (`downloaded=False, terminal_state=FIRST_FAILURE_AT_DOWNLOAD`) was **NOT OBSERVED** and **NOT REPRODUCED** on this pilot sample under the test conditions.

---

## 13. Historical-Causality Status: UNKNOWN / NOT ESTABLISHED

The central historical question is:
> *Why were 318 discovered documents lost at the download stage on 2026-09-11?*

P-R1X does **NOT** establish historical causality. Specifically:
- Current success **cannot** be used to infer why historical requests failed.
- The evidence does not prove origin throttling, WAF bot detection, CDN downtime, market-hours blocking, IP blocking, or network partition on 2026-09-11.
- **Adjudicated Classification:** **UNKNOWN / NOT ESTABLISHED**. Current access is viable; historical failure mechanism remains unreproduced and unexplained.

---

## 14. Unresolved Confounders

1. **Time-of-Day & Market Hours:** Valid Windows 1 and 2 ran late at night UTC (20:05 and 21:35 UTC; 01:35 and 03:05 IST), well outside Indian market hours (09:15 to 15:30 IST). The nominal Window 3 occurred at 08:17 UTC (13:47 IST, during market hours) but was unblinded and confounded by host suspension.
2. **Concurrency & Load:** P-R1X executed with a single worker and a conservative 1.5s delay. Historical batch runs may have utilized multiple concurrent threads or tighter intervals, introducing potential concurrency-dependent rate limiting.
3. **Client Network & IP Reputation:** The local machine IP, ASN, and routing path on 2026-09-17/18 may differ from the network environment active during the historical 2026-09-11 runs.
4. **Origin State Changes:** Upstream server-side infrastructure, load balancers, or CDN caching rules at `nsearchives.nseindia.com` may have changed between 2026-09-11 and 2026-09-17.

---

## 15. Methodological Limitations

1. **Interrupted Protocol:** P-R1X v1.2 was specified as a 3-window temporal design spanning 180 minutes. Due to process suspension, it yielded only a 2-window valid temporal baseline (90-minute interval).
2. **Pilot Sample Scale:** $N = 10$ observations (5 targets, 5 controls) represents a purposive diagnostic sample, not a random or comprehensive sample of the 576-observation historical universe.
3. **Absence of Failure Trace:** Because zero requests failed, no failure telemetry was emitted into `pr1x_live_telemetry.jsonl` (0 bytes). The instrumented telemetry pipeline was tested for pass-through capability, but failure-layer diagnostic mechanisms (`L0` through `L6`) remain unexercised on live errors.

---

## 16. Future Repair-Experiment Decision: INSUFFICIENT EVIDENCE

- **Adjudicated Decision:** **INSUFFICIENT EVIDENCE**
- **Basis for Decision:**
  1. **Absence of Failure Signal:** The baseline acquisition engine succeeded completely (20/20 in valid windows) on the target sample. There is no active failure to fix.
  2. **Historical Cause Unknown:** Because the root cause of the 2026-09-11 losses remains unknown, designing an engineering repair (e.g. adding fake browser headers, cookies, or session managers) would be unguided speculation.
  3. **Incomplete Temporal Design:** The pilot was interrupted before completing its 3-window scheduled design.
  4. **Important Scope Distinction:** "INSUFFICIENT EVIDENCE" does **NOT** assert that the historical acquisition problem is solved or that no repair will ever be needed; it asserts that the P-R1X pilot data alone does not provide the empirical basis required to formulate an acquisition repair experiment.

---

## 17. Artifact Integrity & SHA-256 Hashes

The following SHA-256 hashes establish the tamper-evident provenance of all execution and adjudication files:

### Original Execution Artifacts
| Relative Path | SHA-256 Checksum | Size (Bytes) |
|---|---|---|
| `reports/pc0_sample_manifest.json` | `394c628d842bdcf967b6dd82ab695fb4b17a88602c7c79c0b17561a3d931bb0e` | 11,752 |
| `reports/pr1x_execution_runbook.md` | `4d6f9b320dcb612b4ab9eb3eb0ffd9530589c692a8b19d29c826e18506e39de9` | 7,768 |
| `reports/pr1x_environment.json` | `cc8f9ed239e27b2dbda896545cd691e6eeb12bab6477ecedd726719f419a79bd` | 1,047 |
| `reports/pr1x_live_telemetry.jsonl` | `01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b` | 1 |
| `reports/pr1x_observation_results.json` | `6fc3c5af586e4d2c185e01184e76065a1f72dc16a52a2e1c9e498988dab2e987` | 35,376 |
| `reports/pr1x_execution_summary.md` | `6dbcf74005f9e1c9bceaf30fbf8641b67f91a7d6490c49c8071396e056bca298` | 8,744 |

### Adjudication Artifacts
| Relative Path | Adjudication Purpose |
|---|---|
| `reports/pr1x_temporal_validity.json` | Machine-readable temporal validity classification of Windows 1, 2, and 3 |
| `reports/pr1x_adjudication.json` | Machine-readable comprehensive adjudication findings |
| `reports/pr1x_adjudication.md` | Full human-readable forensic adjudication report |
| `reports/pr1x_memory_update_notes.md` | Canonical memory reconciliation instructions for Phase B |
| `reports/pr1x_artifact_hashes.json` | Canonical manifest of all SHA-256 hashes |

---

## 18. Final Git State
- **Adjudication Worktree:** `D:\sem_iitk\sem9\thesis\sep_week1\arpipe-pr1x-adjudication`
- **Adjudication Branch:** `pr1x-adjudication`
- **Base Commit:** `0b1d595407eacb13b115811cdb610b3e1f56a767`
- **Original Execution Worktree Status:** Untouched (`D:\sem_iitk\sem9\thesis\sep_week1\arpipe-pr1x-execution` preserved without modification)
- **Overall Project Finding:** P-R1X did not produce a clean three-window temporal experiment. It produced a valid two-window primary temporal subset plus a post-interruption supplemental observation run.
