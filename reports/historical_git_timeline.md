# Historical Git and Architectural Timeline (2026-09-10 – 2026-09-18)

This timeline documents the precise chronology of Git commits, source code modifications, and contemporaneous artifact generation surrounding the 2026-09-11 historical acquisition run and subsequent forensic investigations.

---

## 1. Contemporaneous Acquisition Phase (2026-09-11)

| Timestamp (IST) | Timestamp (UTC) | Git Commit / Event | File / Artifact Affected | Evidential Significance |
|---|---|---|---|---|
| **2026-09-11 06:19:04** | 2026-09-11 00:49:04 | Commit `0bc0d6c` | `arpipe/discover.py` | Added filename_symbol, filename_years, mis-filed attachment validation, and `--resume` support to discovery. |
| **2026-09-11 06:24:38** | 2026-09-11 00:54:38 | Commit `36e4c62` | `arpipe/fetch.py` | Implemented priority-based candidate failover (`_fetch_pair`), single-download deduplication, `HostLimiter(min_interval=1.5)`, and `retries=3`. This is the exact acquisition engine active during the crawl. |
| **2026-09-11 15:12:17** | 2026-09-11 09:42:17 | Commit `9cf5192` | `arpipe/universe.py`, `arpipe/cli.py` | Added `cap_band_current` and updated `cmd_sample_for_labelling` to recognize candidate store paths (`live_store`, `store`). |
| **2026-09-11 15:52:54** | 2026-09-11 10:22:54 | File mtime | `tools/select_labelling_cohort.py` | Cohort selection tool authored to select 36 companies across Large (6), Mid (8), Small (10), Micro (12). |
| **2026-09-11 15:53:04** | 2026-09-11 10:23:04 | File ctime/mtime | `cohort_companies.csv` | 36-company cohort generated, establishing the 576 company-year universe denominator. |
| **2026-09-11 15:53:11** | 2026-09-11 10:23:11 | Artifact timestamp | `cohort_reports.jsonl` | Earliest `discovered_at` timestamp recorded in candidate manifest. |
| **2026-09-11 15:57:27** | 2026-09-11 10:27:27 | File mtime | `cohort_reports.jsonl` | Discovery completed; 1,164 candidate rows written covering 512 distinct company-years. 64 company-years had zero discovered candidates. |
| **2026-09-11 15:58:22** | 2026-09-11 10:28:22 | File ctime/mtime | `cohort_fetch_manifest.jsonl` | Intermediate manifest written on disk containing 460 candidate rows covering EXACTLY the 194 successful download pairs and 0 of the 318 losses. |
| **2026-09-11 15:58:41** | 2026-09-11 10:28:41 | File ctime | `live_store/documents.jsonl` | Output documents JSONL file created on disk in `live_store`. |
| **2026-09-11 15:58:44** | 2026-09-11 10:28:44 | Artifact timestamp | `live_store/documents.jsonl` | First document download recorded (`INE002A01018::FY2013` @ 10:28:44.383654 UTC). |
| **2026-09-11 16:03:08** | 2026-09-11 10:33:08 | File mtime / record | `live_store/documents.jsonl` | Last document download recorded (`INE00WC01027::FY2024` @ 10:33:08.081915 UTC). Acquisition crawl terminated. Total duration: 4m 23.7s. Total successes: 194. |
| **2026-09-11 16:10:51** | 2026-09-11 10:40:51 | File mtime | `live_store/profiles.jsonl` | Triage stage completed (`cmd_triage`), profiling the 194 downloaded documents. |
| **2026-09-11 16:11:13** | 2026-09-11 10:41:13 | File mtime | `to_label.csv` | Sampling stage completed (`cmd_sample_for_labelling`), drawing stratified candidates from `live_store`. |
| **2026-09-11 16:13:52** | 2026-09-11 10:43:52 | Commit `84318d3` | `tools/select_labelling_cohort.py` | Committed cohort selection script. Active working tree was clean at this point. |
| **2026-09-11 16:21:07** | 2026-09-11 10:51:07 | Commit `1d7dc05` | Multiple evaluation files | Committed `cohort_companies.csv`, `cohort_fetch_manifest.jsonl`, `eval_report.md`, `labels.csv`, `to_label.csv`, `tools/seed_historical_labels.py`. |
| **2026-09-11 19:16:34** | 2026-09-11 13:46:34 | Commit `bc5f174` | `.gitignore`, reports | Added `.gitignore` rules explicitly ignoring `/live_store/`, `/live_dataset/`, `/cohort_reports.jsonl`, and `/all_reports.jsonl` as regenerable data. |

---

## 2. Post-Hoc Diagnostic & Telemetry Phase (2026-09-17 – 2026-09-18)

| Timestamp (IST) | Git Commit / Worktree | Event / Finding |
|---|---|---|
| **2026-09-17 17:11:14** | Commit `7292111` (`arpipe-pm5-coverage`) | **P-M5 Coverage Funnel Study:** Frozen stage table (`pm5_stage_table.csv`) constructed. Established: 576 expected, 512 discovered, 194 downloaded, 318 lost at download. Quantified 0.0% reason-code coverage at DOWNLOAD stage. |
| **2026-09-17 18:36:00** | Worktree `arpipe-pc0-diagnostic-base` | **Diagnostic Base Check:** Probed 9 URLs at 13:17 UTC; observed 0/9 failures (`CURLE_RECV_ERROR 56` resets and 45s timeouts). |
| **2026-09-17 19:40:00** | Worktree `arpipe-pc0-coverage-diag` | **P-C0 Coverage Diagnosis:** Probed 10 URLs at 13:59 UTC; observed 10/10 successes with valid ZIP/PDF magic bytes. Identified sub-hour endpoint volatility. Investigated `cohort_fetch_manifest.jsonl`. |
| **2026-09-17 19:54:00** | Worktree `arpipe-pc0r-acquisition-pilot` | **P-C0R Controlled A/B Trial:** 10/10 paired comparisons between Arm A (session cookies + headers) and Arm B (unseeded client) succeeded identically, ruling out client asymmetry as current cause. |
| **2026-09-17 22:30:17** | Commit `5649772` (`arpipe-r1-fetch-telemetry`) | **Milestone R1 Implementation:** Added structured attempt-level telemetry (`r1-v1`) to `arpipe/fetch.py` and `arpipe/cli.py` with zero behavioral change (15/15 equivalence fixtures verified). Worktree frozen read-only. |
| **2026-09-17 23:25:53** | Commit `3beee24` (`arpipe-r1-telemetry-analysis`) | **R1 Telemetry Analysis & P-R1X Protocol:** Analyzed synthetic telemetry matrix and pre-registered protocol P-R1X v1.2. |
| **2026-09-18 13:54:24** | Commit `0b1d595` (`arpipe-pr1x-execution`) | **P-R1X Execution:** Executed 3 temporal windows under R1 telemetry. All 30 attempts HTTP 200, 0 retries. Historical failure mode was NOT observed. |
| **2026-09-18 14:33:59** | Commit `ca92b8e` (`arpipe-pr1x-adjudication`) | **P-R1X Forensic Adjudication:** Adjudicated W1 and W2 as VALID ($N=20$), W3 as POST_INTERRUPTION_SUPPLEMENTAL ($N=10$). Historical cause classified as UNKNOWN. Repair experiment decision: INSUFFICIENT EVIDENCE. |
| **2026-09-18 [CURRENT]** | Branch `pr1x-historical-audit` | **Historical Acquisition-Cause Evidence Audit:** Forensic investigation of surviving 2026-09-11 evidence. |

---

## 3. Key Code Provenance Findings

1. **Committed Engine Stability:** `arpipe/fetch.py` was committed at `36e4c62` (06:24:38 IST on Sep 11) and underwent **zero code changes** between that commit and baseline freeze `0fb8cbf`. The code executed during the 15:58–16:03 IST crawl is byte-identical to `36e4c62`.
2. **Observability Void by Construction:** The committed code in `fetch.py` and `cli.py` printed failure notices to stderr (`WARN fetch failover...`, `FAILED ... across all candidate sources`) and swallowed exhausted 403/429/503 errors via a silent `return None` path. Zero attempt-level telemetry or error logs were designed to be persisted to disk.
3. **Manifest Divergence:** `cohort_fetch_manifest.jsonl` was timestamped at 10:28:22 UTC on 2026-09-11, exactly 22 seconds before `live_store/documents.jsonl` was initialized, and contained exclusively the 194 successful download pairs.
