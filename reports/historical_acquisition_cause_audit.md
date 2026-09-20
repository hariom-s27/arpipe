# ARPipe — Historical Acquisition-Cause Evidence Audit
## Final Forensic Research Report: 2026-09-11 Acquisition Gap Investigation

**Document Identifier:** `ARPIPE-HISTORICAL-AUDIT-2026-09-18`<br>
**Investigation Mode:** LOCAL / OFFLINE READ-ONLY HISTORICAL FORENSICS<br>
**Governing Worktree:** `D:\sem_iitk\sem9\thesis\sep_week1\arpipe-pr1x-historical-audit`<br>
**Governing Branch:** `pr1x-historical-audit`<br>
**Adjudicated Base Commit:** `ca92b8e8d043cccb9556a6fc591927b3bbf1cf32` (P-R1X Adjudication Result)<br>
**Historical Transition Under Investigation:** `DISCOVERED` &rarr; `DOWNLOADED`<br>
**Primary Finding:** **POPULATION RECONCILED (318/318) — PHYSICAL MECHANISM UNKNOWN (0.0% REASONS PERSISTED) — INSUFFICIENT HISTORICAL EVIDENCE FOR TARGETED EXPERIMENT**

---

## 1. Executive Summary & Scope

This forensic audit investigates the surviving historical evidence surrounding the original 2026-09-11 acquisition loss in the ARPipe corpus. In the initial full-universe crawl, out of **576 expected company-years** (36 firms &times; 16 fiscal years FY2010–2025), **512 company-years were successfully discovered**, but only **194 company-years were downloaded**, leaving an attrition gap of **exactly 318 company-years** lost at the `DISCOVERED` &rarr; `DOWNLOADED` transition.

In strict compliance with forensic audit protocols:
- **No live network requests were fired.**
- **No external servers, exchange endpoints, or APIs were contacted.**
- **No historical source files were edited, regenerated, or fabricated.**
- **Git operations remained strictly local and offline.**
- **The investigation operates entirely within dedicated worktree `arpipe-pr1x-historical-audit` branched from verified base `ca92b8e`.**

### Key Findings at a Glance

1. **Population Identity Reconciliation: EXACT (YES).** All 318 historical loss identities have been fully reconstructed from `pm5_stage_table.csv` and cross-referenced with contemporaneous discovery manifest `cohort_reports.jsonl`. Exactly 318 unique observations, 0 duplicates, 0 missing, 0 invented.
2. **Historical Reason-Code Completeness: EXACTLY 0.0% (0 of 318).** The historical crawl on 2026-09-11 persisted zero per-attempt logs, zero HTTP status codes, zero socket exceptions, and zero terminal failure states. All 318 losses are recorded as `REASON_CODE_MISSING`.
3. **Request Invocation State: `REQUEST_NOT_CONFIRMED`.** Under the mandatory epistemic distinction (`NO_REQUEST_EVIDENCE != REQUEST_DID_NOT_OCCUR`), surviving records show candidate URLs were discovered, but no record confirms whether HTTP requests were actually dispatched for the 318 losses.
4. **Intermediate Fetch Manifest Finding:** A contemporaneous file `cohort_fetch_manifest.jsonl` was written at 10:28:22 UTC on 2026-09-11 (22 seconds prior to the first successful download), containing 460 candidate rows covering **exactly the 194 successful pairs** and **omitting all 318 losses**.
5. **Next-Experiment Decision: `INSUFFICIENT HISTORICAL EVIDENCE FOR TARGETED EXPERIMENT`.** A targeted experiment attempting to reproduce a specific historical failure mechanism cannot be designed without speculating beyond the surviving evidence. The project advances to an **INFORMATION-GAP / OBSERVABILITY TASK** (Roadmap Task 2).

---

## 2. Evidence Hierarchy & Epistemological Rules

Every source analyzed in this audit has been classified according to the project's strict evidence hierarchy and temporality schema:

| Level | Evidence Source Category | Applied Sources | Epistemic Weight |
|:---|:---|:---|:---|
| **LEVEL 1** | Contemporaneous Historical Acquisition Artifacts | `cohort_reports.jsonl` (SHA: `c24f148a...`), `live_store/documents.jsonl` (SHA: `3a7c7bf1...`), `cohort_fetch_manifest.jsonl` (SHA: `d242cf51...`), `cohort_companies.csv` (SHA: `5f2d8078...`) | **HIGHEST:** Immutable physical records created during the 2026-09-11 run. |
| **LEVEL 2** | Contemporaneous Logs, Manifests & Telemetry | File mtimes/ctimes, directory structures in `live_store` and `live_dataset_prev` | Direct physical metadata establishing execution sequence and timing. |
| **LEVEL 3** | Git Commit / Code State Used Historically | Commit `84318d3` / `9cf5192` (`arpipe/fetch.py`, `arpipe/cli.py`) | Proven control flow and configuration active during the crawl. |
| **LEVEL 4** | Shell / Task Transcripts Generated During Run | `ConsoleHost_history.txt` | Partial operational command history. |
| **LEVEL 5** | Later Analytical Reports Reconstructing Event | `pm5_stage_table.csv`, `coverage.json`, `coverage_diagnosis.json` (P-C0), `pc0r_diagnosis.json` (P-C0R), `pr1x_adjudication.json` (P-R1X) | Secondary analytical reconstructions; cannot override Level 1–3 facts. |
| **LEVEL 6** | Current Project-Memory Summaries | `ARPipe_Memory/01_CURRENT_STATE.md`, `02_DECISIONS.md`, `03_EVIDENCE_REGISTER.md` | Navigation maps; do not establish historical truth independently. |

### Evidence Temporality Classifications
- `CONTEMPORANEOUS`: Created during the historical acquisition itself on 2026-09-11 (`cohort_reports.jsonl`, `live_store/documents.jsonl`, `cohort_fetch_manifest.jsonl`, `cohort_companies.csv`, Commit `84318d3`).
- `NEAR_CONTEMPORANEOUS`: Preserved snapshots pinned immediately around the baseline freeze (`reports/pm5_source_snapshots/`).
- `POST_HOC_RECONSTRUCTION`: Analytical studies compiled later to diagnose the gap (`pm5_stage_table.csv`, P-C0, P-C0R, P-R1X).
- `CURRENT_ANALYSIS`: Produced during this present audit (`historical_loss_ledger.csv`, `historical_evidence_register.csv`).

---

## 3. Source Inventory & Chain of Custody

All 29 source artifacts inspected during this audit were hashed prior to analysis and verified after analysis. In accordance with Section 8 of the protocol, **pre-analysis SHA-256 digests equal post-analysis SHA-256 digests across 100% of inspected files**. Zero source files were modified.

```
Source Integrity Verification:
- Total Historical Source Artifacts Inspected: 29
- Pre-Analysis Hashes Computed: 29
- Post-Analysis Hashes Computed: 29
- Hash Match Rate: 100.0% (pre_hash == post_hash)
- Working Copies Modified: 0
- Audit Integrity Status: UNCOMPROMISED / VERIFIED PRISTINE
```

Full cryptographic digests are permanently recorded in [`reports/historical_audit_hashes.json`](file:///D:/sem_iitk/sem9/thesis/sep_week1/arpipe-pr1x-historical-audit/reports/historical_audit_hashes.json).

---

## 4. Historical Population Reconstruction & Identity Integrity

### Population Identity Integrity Result

```
### Population Identity Integrity
- Expected discovered -> downloaded loss population: 318
- Reconstructed identities: 318
- Duplicates: 0
- Missing identities: 0
- Invented identities: 0
- Unresolved identity conflicts: 0
- Exact reconstruction: YES
```

The authoritative 318-row historical loss ledger is committed in [`reports/historical_loss_ledger.csv`](file:///D:/sem_iitk/sem9/thesis/sep_week1/arpipe-pr1x-historical-audit/reports/historical_loss_ledger.csv). Every row establishes:
- `company_year_id`: Standardized observation identifier (e.g. `INE002A01018::FY2010`)
- `company`: Exact corporate name (e.g. `Reliance Industries Limited`)
- `fiscal_year`: Fiscal year integer (2010–2023)
- `historical_url`: Primary discovered candidate URL from `cohort_reports.jsonl`
- `population_source`: `reports/pm5_stage_table.csv` (SHA-256: `30e93b59ac689f00...`)
- `source_row_or_index`: Exact row pointer in `pm5_stage_table.csv`
- `evidence_locator`: Exact line references in `pm5_stage_table.csv` and `cohort_reports.jsonl`
- `request_status`: `REQUEST_NOT_CONFIRMED`
- `http_status`: `NOT_RECORDED`
- `exception_type`: `NOT_RECORDED`
- `failure_layer`: `UNKNOWN`
- `reason_code`: `REASON_CODE_MISSING`
- `historical_cause_status`: `UNKNOWN_AFTER_REVIEW`

### Distribution of Reconstructed Losses

The 318 losses partition cleanly across fiscal years as follows:

| Fiscal Year | Expected Universe | Discovered | Downloaded | Transition Loss | Loss Type | Dominant Candidate Extension |
|:---|:---:|:---:|:---:|:---:|:---|:---|
| **2010** | 36 | 28 | 0 | **28** | `DOWNLOAD_ZERO_FY` | ZIP (28) |
| **2011** | 36 | 29 | 1 | **28** | Partial Loss | ZIP (28) |
| **2012** | 36 | 28 | 28 | 0 | Complete Success | - |
| **2013** | 36 | 29 | 29 | 0 | Complete Success | - |
| **2014** | 36 | 30 | 0 | **30** | `DOWNLOAD_ZERO_FY` | ZIP (30) |
| **2015** | 36 | 33 | 2 | **31** | Partial Loss | ZIP (31) |
| **2016** | 36 | 31 | 0 | **31** | `DOWNLOAD_ZERO_FY` | ZIP (28), PDF (3) |
| **2017** | 36 | 31 | 31 | 0 | Complete Success | - |
| **2018** | 36 | 31 | 31 | 0 | Complete Success | - |
| **2019** | 36 | 32 | 0 | **32** | `DOWNLOAD_ZERO_FY` | PDF (20), ZIP (12) |
| **2020** | 36 | 33 | 0 | **33** | `DOWNLOAD_ZERO_FY` | PDF (22), ZIP (11) |
| **2021** | 36 | 34 | 0 | **34** | `DOWNLOAD_ZERO_FY` | PDF (23), ZIP (11) |
| **2022** | 36 | 35 | 0 | **35** | `DOWNLOAD_ZERO_FY` | PDF (23), ZIP (12) |
| **2023** | 36 | 36 | 0 | **36** | `DOWNLOAD_ZERO_FY` | PDF (26), ZIP (10) |
| **2024** | 36 | 36 | 36 | 0 | Complete Success | - |
| **2025** | 36 | 36 | 36 | 0 | Complete Success | - |
| **TOTAL** | **576** | **512** | **194** | **318** | **318 LOSSES** | **ZIP (211), PDF (107)** |

---

## 5. Request Invocation State & Observability Void

### Mandatory Epistemic Principle: `NO_REQUEST_EVIDENCE != REQUEST_DID_NOT_OCCUR`

A critical requirement of this audit is distinguishing between:
1. **Evidence that a request did not occur** (`REQUEST_DID_NOT_OCCUR`), and
2. **Absence of surviving evidence confirming that a request occurred** (`REQUEST_NOT_CONFIRMED`).

### Findings on Request Invocation

All 318 losses are classified as **`REQUEST_NOT_CONFIRMED`**.

Surviving physical evidence proves:
1. **Discovery was executed and completed:** `cohort_reports.jsonl` contains 1,164 candidate rows timestamped 10:23:11 to 10:27:27 UTC on 2026-09-11. Every one of the 318 losses had valid discovered candidate URLs.
2. **Downloads were executed for 194 pairs:** `live_store/documents.jsonl` contains 194 records timestamped 10:28:44 to 10:33:08 UTC.
3. **No persistent log exists for the 318 losses:** In the pre-R1 codebase (commits `36e4c62` &rarr; `84318d3`), `fetch_one()` printed errors to stderr (`WARN fetch failover...`) and `cmd_fetch` printed `FAILED ... across all candidate sources` to stderr. Neither function wrote attempt records, error messages, or failure codes to disk.
4. **The Silent Drop Path:** In `arpipe/fetch.py:fetch_one()`, when remote servers return HTTP 403, 429, or 503, the retry loop executes `time.sleep()` and `continue` **without setting `last_err`**. If all 3 attempts encounter 403/429/503, the loop terminates with `last_err is None`, and `fetch_one()` executes `return None` **silently**—producing zero stderr prints and zero disk records.
5. **The Intermediate Manifest Clue:** At 10:28:22 UTC (22 seconds before the first download began), `cohort_fetch_manifest.jsonl` was written containing exactly the 194 pairs that subsequently succeeded. If `cmd_fetch` was invoked with `--manifest cohort_fetch_manifest.jsonl`, requests for the 318 were never dispatched by that process. However, because shell command history and terminal transcripts were not preserved, this hypothesis remains plausible but unproven.

---

## 6. Historical Configuration Snapshot

From historical Git commits `84318d3`, `9cf5192`, and `0fb8cbf`, the exact committed client configuration active during the crawl has been established:

- **HTTP Library:** `httpx` (`httpx.Client`)
- **User-Agent:** `Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36` (`discover.UA`)
- **Client Headers:** `{"User-Agent": discover.UA}` (No `Accept`, `Referer`, `Accept-Language`, or `Sec-Ch-Ua` headers in `cmd_fetch`)
- **Session / Cookies:** Empty cookie jar (unseeded fresh client; session cookies were used only during discovery)
- **Request Timeout:** `120.0s` per request stream
- **Retry Count:** `retries = 3` attempts per observation
- **Retry Backoff Schedule:**
  - HTTP 403, 429, 503: `5 * (attempt + 1) ** 2` seconds (Attempt 1: 5s; Attempt 2: 20s; Attempt 3: 45s)
  - Generic Exceptions (Network/Timeout/Reset): `2 * (attempt + 1)` seconds (Attempt 1: 2s; Attempt 2: 4s; Attempt 3: 6s)
- **Pacing Engine:** `fetch.HostLimiter(min_interval=1.5)` (token bucket per netloc host)
- **Concurrency Architecture:** `concurrent.futures.ThreadPoolExecutor(workers=4)` (default CLI parameter)
- **Client Lifecycle:** A single `httpx.Client` was instantiated in `cmd_fetch` and shared across all 4 worker threads.
- **Redirect Policy:** `follow_redirects=True` (httpx default `max_redirects=20`)
- **Streaming & Buffer Limits:** `chunk_size = 1 << 18` (256 KB); `max_bytes = 400 << 20` (400 MB)
- **Format Validation & Repair:** First 2 bytes sniff (`b"PK"` &rarr; ZIP extraction; else PDF &rarr; `pymupdf.open()` &rarr; fallback `qpdf` xref repair).

**Status:** **PARTIALLY ESTABLISHED**. The software implementation is fully established; however, specific runtime arguments (e.g. `--workers`, `--min-interval`, `--manifest`) passed on the command line on 2026-09-11 are `NOT_RECORDED`.

---

## 7. Hypothesis Matrix Summary

The complete evaluation matrix of historical failure mechanisms is committed in [`reports/historical_hypothesis_matrix.csv`](file:///D:/sem_iitk/sem9/thesis/sep_week1/arpipe-pr1x-historical-audit/reports/historical_hypothesis_matrix.csv).

| Failure Hypothesis | Direct Evidence | Indirect Evidence | Contradicting Evidence | Final Audit Status |
|:---|:---|:---|:---|:---:|
| **HTTP 403/429/503 Rejection** | None (0 records) | Code gap: silent `return None` on 3x HTTP rejections without logging | 0/80 rejections in contemporary open windows (P-C0, P-C0R, P-R1X) | `PLAUSIBLE_BUT_UNPROVEN` |
| **Transport Failure (Reset / Connect / DNS)** | None (0 records) | P-C0 Step 3 experienced `CURLE_RECV_ERROR 56` connection resets | 0/20 resets in P-R1X valid windows; 50/50 success in P-C0R | `PLAUSIBLE_BUT_UNPROVEN` |
| **Timeout (Connect / Read)** | None (0 records) | P-C0 Step 3 experienced 45s read timeouts on archive host | 0/30 timeouts in P-R1X; mean response < 3.5s | `PLAUSIBLE_BUT_UNPROVEN` |
| **Receipt Failure (Truncated Stream)** | None (0 records) | None | All 194 historical successes were intact with valid byte sizes | `UNKNOWN_AFTER_REVIEW` |
| **Validation Failure (Corrupt ZIP / Bad PDF)** | None (0 records) | `qpdf` fallback pass existed in code | Sampled URLs from zero FYs yielded 100% valid ZIP/PDF files with matching magic bytes and bitwise CAS hashes | **`RULED_OUT`** (for tested sample) |
| **Acquisition Invocation Gap (Un-dispatched)** | `cohort_fetch_manifest.jsonl` written @ 10:28:22 UTC omitted all 318 losses | `cmd_fetch` reads a manifest file; intermediate file contains exactly the 194 successes | Cannot prove whether file was an input filter or post-hoc export | `PLAUSIBLE_BUT_UNPROVEN` |
| **URL Syntax / Malformation Defect** | None | None | All 318 candidate URLs are valid, syntactically well-formed regulatory links | **`RULED_OUT`** |
| **Temporal / Time-of-Day Access Policy** | All 194 historical successes occurred in one 4.5-min burst | P-C0 observed sub-hour shift (0/9 failures &rarr; 10/10 successes in 50m) | P-R1X Window 3 ran during Indian market hours (13:47 IST) and achieved 10/10 success | `PLAUSIBLE_BUT_UNPROVEN` |
| **Concurrency / Burst Load Throttle** | None (0 records) | `cmd_fetch` used 4 concurrent worker threads | 194 documents downloaded in 4.5 min (~1.36s/doc) under 4 workers | `PLAUSIBLE_BUT_UNPROVEN` |
| **Retry Exhaustion** | None (0 records) | `fetch_one()` hardcoded `retries = 3` | 20/20 valid requests succeeded on Attempt 1 in P-R1X | `PLAUSIBLE_BUT_UNPROVEN` |
| **Client Configuration Asymmetry** | None | `cmd_discover` used session cookies; `cmd_fetch` was unseeded | P-C0R Part 6 trial showed 10/10 paired comparisons succeeded identically with and without cookies/Referer | **`RULED_OUT`** (as technical barrier) |

---

## 8. Answers to Required Analytical Questions (Section 31)

### Q1. Can the exact 318 historical loss identities be reconstructed?
**YES.** All 318 historical loss identities are fully reconstructed. Exactly 318 unique observations, 0 duplicates, 0 missing, 0 invented.

### Q2. How many have directly documented failure reasons?
**EXACTLY 0 (0.0%).** Zero reason codes survive for the 318 download losses (`pm5_reason_code_completeness.csv` = 0.0%). All 318 are recorded as `REASON_CODE_MISSING`.

### Q3. How many have indirect evidence?
**318 of 318 (100.0%).** All 318 have indirect evidence regarding discovered URLs in `cohort_reports.jsonl`, fiscal year clustering, and absence from `cohort_fetch_manifest.jsonl`.

### Q4. How many remain unclassified?
**318 of 318 (100.0%).** At the physical root-cause mechanism layer, all 318 remain `UNKNOWN_AFTER_REVIEW`.

### Q5. Is there direct historical evidence of HTTP 403?
**NO.** Exactly 0 HTTP status codes were logged on 2026-09-11.

### Q6. Is there direct historical evidence of HTTP 429?
**NO.** Exactly 0 rate-limiting responses were logged on 2026-09-11.

### Q7. Is there direct historical evidence of HTTP 503?
**NO.** Exactly 0 service unavailable responses were logged on 2026-09-11.

### Q8. Is there direct historical evidence of DNS/connect/TLS/timeout failure?
**NO.** Exactly 0 socket exceptions or transport error traces survive from 2026-09-11.

### Q9. Is there direct historical evidence that the downloader was invoked?
**NO.** Classified as **`REQUEST_NOT_CONFIRMED`** under `NO_REQUEST_EVIDENCE != REQUEST_DID_NOT_OCCUR`.

### Q10. Is there direct retry-exhaustion evidence?
**NO.** Coverage is **NONE OF 318**. Attempt-level telemetry was not implemented until Milestone R1 on 2026-09-17.

### Q11. Is there direct receipt or validation-failure evidence?
**NO.** Zero validation failures were recorded historically; contemporary testing on sampled URLs disproved payload corruption.

### Q12. What historical HTTP/client configuration is actually established?
**PARTIALLY ESTABLISHED.** The codebase implementation at commit `84318d3` is fully established (`httpx.Client`, User-Agent only, no cookies, 120s timeout, 3 retries, HostLimiter 1.5s, 4 workers). Runtime arguments passed on 2026-09-11 are `NOT_RECORDED`.

### Q13. What historical concurrency/load is established?
**PARTIALLY ESTABLISHED.** Code defaulted to `workers = 4` with cross-thread host rate limiting (`HostLimiter(1.5)`). Runtime worker flag is `NOT_RECORDED`.

### Q14. What historical timing is established?
**PARTIALLY ESTABLISHED.** Discovery ran from 10:23 to 10:27 UTC; successful downloads ran from 10:28:44 to 10:33:08 UTC. For the 318 losses, exactly 0 timestamps survive.

### Q15. Which hypotheses can genuinely be ruled out?
1. Validation failure / payload corruption on the target sample.
2. URL syntax malformation or invalid link paths.
3. Client configuration asymmetry (missing cookies/Referer) as an absolute barrier.
4. `cohort_fetch_manifest.jsonl` as an independent predictive filter.

### Q16. Which remain plausible but unproven?
1. Upstream origin / CDN rate limiting or connection resets.
2. Workflow invocation gap / staged manifest execution.
3. Silent drop on repeated HTTP 403/429/503.
4. Concurrency burst triggering origin anti-bot defenses.
5. Retry exhaustion.

### Q17. What remains unknown because the original run did not preserve sufficient evidence?
1. Whether requests were actually dispatched for the 318 losses.
2. What specific HTTP status codes or socket errors occurred if dispatched.
3. The exact CLI command line and parameters used to run the crawl.
4. The exact operational reason why `cohort_fetch_manifest.jsonl` contained only 194 pairs.

---

## 9. Final Historical Synthesis

In accordance with Section 32, this audit strictly separates:

### WHAT IS HISTORICALLY ESTABLISHED ABOUT 2026-09-11
- 512 company-years were discovered; 194 were downloaded; exactly 318 were lost.
- All 194 successful downloads occurred inside a single 4.5-minute window (10:28:44–10:33:08 UTC).
- The historical system persisted **0.0% reason codes** and **0 attempt-level telemetry records**.
- `cohort_fetch_manifest.jsonl` existed on disk at 10:28:22 UTC containing only the 194 successful pairs.
- The committed acquisition code silently dropped exhausted 403/429/503 responses without persistent logging.

### WHAT IS ONLY KNOWN ABOUT CURRENT 2026 BEHAVIOR
- Under polite single-worker pacing, `nsearchives.nseindia.com` is viable and achieved **100% success on Attempt 1** across 20 valid temporal observations in P-R1X and 50 observations in P-C0R.
- The archive endpoint exhibits sub-hour accessibility shifts (0/9 failures followed by 10/10 successes within 50 minutes in P-C0).
- An unseeded, cookie-less, Referer-less client succeeds identically to a session-warmed client today (P-C0R).
- The historical failure mode (`downloaded=False`) was **NOT OBSERVED and NOT REPRODUCED** under current test conditions.

---

## 10. Next-Experiment Decision

```
============================================================
NEXT-EXPERIMENT DECISION:
INSUFFICIENT HISTORICAL EVIDENCE FOR TARGETED EXPERIMENT
============================================================
```

### Governing Rationale
Under Section 33 of the audit protocol, a targeted experiment is justified only if:
1. A specific historical mechanism is sufficiently evidenced,
2. The mechanism is testable,
3. The unresolved confounders are explicit, and
4. The experiment can be designed without inventing missing historical facts.

Because surviving historical records contain **0.0% reason codes**, zero HTTP telemetry, zero error traces, and cannot even confirm whether requests were invoked (`REQUEST_NOT_CONFIRMED`), designing a targeted repair or reproduction experiment claiming to test the specific historical failure mechanism would constitute **unguided speculation and invention of unrecorded historical facts**.

### Required Next Task
In accordance with Section 40 of the protocol:
- **Next Task:** **`INFORMATION-GAP / OBSERVABILITY TASK`**
- **Roadmap Identifier:** `Task 2 (Evidence-Driven Acquisition Strategy: Classify Recoverable vs. Excluded vs. Unrecoverable)`
- **Objective:** Deploy structured R1 attempt-level telemetry across the full 318 un-downloaded cohort to systematically categorize each company-year into:
  - **Category A (Recoverable Technical Gaps):** Missing documents that succeed under instrumented acquisition.
  - **Category B (Systematic URL / Parser Defects):** Discovered URLs requiring targeted correction.
  - **Category C (Genuine Archival Unavailability):** Company-years that do not exist at source (e.g. pre-incorporation, corporate reorganization, missing regulatory filings).

---

## 11. Artifact Integrity Verification

Prior to and immediately following this audit, SHA-256 digests were computed across all 29 source artifacts.

- **Historical Source Artifacts Inspected:** 29
- **Source Hashes Preserved:** **YES** (`pre_hash == post_hash` across all 29 files)
- **Source Artifacts Modified:** **NO** (0 files edited)
- **Direct Claims with Exact Locators:** 10 / 10
- **Contradictory Sources:** 0 unresolved conflicts
- **Population Identity Exact:** **YES** (318 of 318 reconciled)

Full cryptographic provenance is permanently recorded in [`reports/historical_audit_hashes.json`](file:///D:/sem_iitk/sem9/thesis/sep_week1/arpipe-pr1x-historical-audit/reports/historical_audit_hashes.json).
