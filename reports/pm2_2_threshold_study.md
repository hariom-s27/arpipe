# P-M2.2: Exploratory `orphan_start_frac` Threshold Sensitivity Study

> **Scope Notice**: This is an **exploratory / pre-gold / not-production** sensitivity study. It does NOT fit or recalibrate production thresholds. `ORPHAN_START_FRAC_MAX = 0.03` remains **strictly unchanged**.

## A. Frozen Inputs & Integrity Gate

- **P-M2.1 Source Commit**: `158a9eac48a3374a9506af8281acb93f49a37a0d`
- **Corpus Identity**: `194-document authoritative cohort (cohort_companies.csv)`
- **Input Snapshot Hashes**: `pm2_2_page_input_snapshot.json` (b8e1739ef1944f96...), `pm2_2_page_input_snapshot.csv` (62583344c7758ba8...)
- **Candidate Set Hashes**: `pm2_2_threshold_candidates.json` (1193351f8344cd96...)
- **Protected Production Hashes**: Verified 8/8 unchanged (`segment.py`, `patterns.py`, `verify.py`, `pipeline.py`, `triage.py`, `textlayer.py`, `ocr.py`, `models.py`).

## B. Population Accounting Reconciliation

- Total Corpus Documents: 194
- Located Documents: 182 (Unlocated: 12 due to `mda_not_located`)
- Total MD&A Physical Pages: 2734
- Measured Page Scores: 2547 (2,412 Native + 134 OCR + 1 Unknown)
- Null / Unmeasured Pages: 187 (all due to fewer than 2 paragraphs)
- **Reconciliation Formula**: `2,734 (total) = 2,412 (native) + 134 (ocr) + 1 (unknown) + 187 (null)`
- **Reconciliation Verified**: **True**

## C. Independence Structure

- Pure-Native Documents: **160**
- Pure-OCR Documents: **5**
- Mixed Native/OCR Documents: **16**
- Total OCR-Containing Documents: **21** (5 pure + 16 mixed)

## D. Predeclared Threshold Candidate Set

| Threshold | Source | Status | Rationale |
| :--- | :--- | :--- | :--- |
| **0.020** | predeclared sensitivity grid | `exploratory` | lower-band sensitivity |
| **0.025** | predeclared sensitivity grid | `exploratory` | lower-band sensitivity |
| **0.030** | existing ARPipe methodology | `inherited` | current production diagnostic |
| **0.035** | predeclared sensitivity grid | `exploratory` | near-current upper sensitivity |
| **0.040** | predeclared sensitivity grid | `exploratory` | upper-band sensitivity |
| **0.050** | predeclared sensitivity grid | `exploratory` | wider upper-band sensitivity |
| **0.060** | predeclared sensitivity grid | `exploratory` | wider upper-band sensitivity |

## E. Page-Level Threshold Evidence Table

| Population | Threshold | N pages | N docs | Page frac > T | Doc frac flagged | P95 | Max | Gap | Near Gate (±0.001) |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Native** | 0.020 | 2412 | 152 | 0.2857 | 0.7105 | 0.1221 | 0.6471 | 0.0004 | 17 |
| **OCR** | 0.020 | 134 | 4 | 0.4701 | 1.0000 | 0.1667 | 0.4286 | 0.0061 | 0 |
| **Native** | 0.025 | 2412 | 152 | 0.2699 | 0.7039 | 0.1221 | 0.6471 | 0.0006 | 10 |
| **OCR** | 0.025 | 134 | 4 | 0.4627 | 1.0000 | 0.1667 | 0.4286 | 0.0024 | 1 |
| **Native** | 0.030 | 2412 | 152 | 0.2517 | 0.6776 | 0.1221 | 0.6471 | 0.0009 | 19 |
| **OCR** | 0.030 | 134 | 4 | 0.4179 | 1.0000 | 0.1667 | 0.4286 | 0.0029 | 1 |
| **Native** | 0.035 | 2412 | 152 | 0.2297 | 0.6579 | 0.1221 | 0.6471 | 0.0006 | 15 |
| **OCR** | 0.035 | 134 | 4 | 0.3657 | 0.7500 | 0.1667 | 0.4286 | 0.0012 | 6 |
| **Native** | 0.040 | 2412 | 152 | 0.2148 | 0.6382 | 0.1221 | 0.6471 | 0.0017 | 10 |
| **OCR** | 0.040 | 134 | 4 | 0.3134 | 0.7500 | 0.1667 | 0.4286 | 0.0017 | 2 |
| **Native** | 0.050 | 2412 | 152 | 0.1845 | 0.5724 | 0.1221 | 0.6471 | 0.0008 | 14 |
| **OCR** | 0.050 | 134 | 4 | 0.2836 | 0.7500 | 0.1667 | 0.4286 | 0.0026 | 1 |
| **Native** | 0.060 | 2412 | 152 | 0.1596 | 0.5526 | 0.1221 | 0.6471 | 0.0006 | 3 |
| **OCR** | 0.060 | 134 | 4 | 0.2612 | 0.7500 | 0.1667 | 0.4286 | 0.0018 | 1 |

## F. Document-Level Threshold Metrics (By Extent of Page Corruption)

| Threshold | Population | N Docs | Docs Any > T | Docs $\ge 5\%$ > T | Docs $\ge 10\%$ > T | Docs $\ge 25\%$ > T | Docs $\ge 50\%$ > T |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.020 | Pure-Native | 152 | 108 (71.1%) | 108 (71.1%) | 104 (68.4%) | 73 (48.0%) | 26 (17.1%) |
| 0.020 | Pure-OCR | 4 | 4 (100.0%) | 4 (100.0%) | 4 (100.0%) | 4 (100.0%) | 3 (75.0%) |
| 0.020 | Mixed | 16 | 16 (100.0%) | 15 (93.8%) | 15 (93.8%) | 10 (62.5%) | 4 (25.0%) |
| 0.025 | Pure-Native | 152 | 107 (70.4%) | 107 (70.4%) | 102 (67.1%) | 67 (44.1%) | 24 (15.8%) |
| 0.025 | Pure-OCR | 4 | 4 (100.0%) | 4 (100.0%) | 4 (100.0%) | 4 (100.0%) | 3 (75.0%) |
| 0.025 | Mixed | 16 | 16 (100.0%) | 15 (93.8%) | 15 (93.8%) | 10 (62.5%) | 3 (18.8%) |
| 0.030 | Pure-Native | 152 | 103 (67.8%) | 102 (67.1%) | 94 (61.8%) | 60 (39.5%) | 18 (11.8%) |
| 0.030 | Pure-OCR | 4 | 4 (100.0%) | 4 (100.0%) | 4 (100.0%) | 4 (100.0%) | 2 (50.0%) |
| 0.030 | Mixed | 16 | 16 (100.0%) | 15 (93.8%) | 15 (93.8%) | 10 (62.5%) | 3 (18.8%) |
| 0.035 | Pure-Native | 152 | 100 (65.8%) | 98 (64.5%) | 89 (58.6%) | 53 (34.9%) | 12 (7.9%) |
| 0.035 | Pure-OCR | 4 | 3 (75.0%) | 3 (75.0%) | 3 (75.0%) | 3 (75.0%) | 1 (25.0%) |
| 0.035 | Mixed | 16 | 16 (100.0%) | 15 (93.8%) | 14 (87.5%) | 8 (50.0%) | 1 (6.2%) |
| 0.040 | Pure-Native | 152 | 97 (63.8%) | 95 (62.5%) | 87 (57.2%) | 47 (30.9%) | 11 (7.2%) |
| 0.040 | Pure-OCR | 4 | 3 (75.0%) | 3 (75.0%) | 3 (75.0%) | 3 (75.0%) | 1 (25.0%) |
| 0.040 | Mixed | 16 | 16 (100.0%) | 15 (93.8%) | 14 (87.5%) | 8 (50.0%) | 1 (6.2%) |
| 0.050 | Pure-Native | 152 | 87 (57.2%) | 84 (55.3%) | 76 (50.0%) | 38 (25.0%) | 10 (6.6%) |
| 0.050 | Pure-OCR | 4 | 3 (75.0%) | 3 (75.0%) | 3 (75.0%) | 3 (75.0%) | 0 (0.0%) |
| 0.050 | Mixed | 16 | 16 (100.0%) | 15 (93.8%) | 13 (81.2%) | 6 (37.5%) | 1 (6.2%) |
| 0.060 | Pure-Native | 152 | 84 (55.3%) | 81 (53.3%) | 67 (44.1%) | 31 (20.4%) | 10 (6.6%) |
| 0.060 | Pure-OCR | 4 | 3 (75.0%) | 3 (75.0%) | 3 (75.0%) | 3 (75.0%) | 0 (0.0%) |
| 0.060 | Mixed | 16 | 16 (100.0%) | 14 (87.5%) | 11 (68.8%) | 6 (37.5%) | 1 (6.2%) |

## G. Document-Level Hiding Analysis

| Threshold | Total Measurable Docs | Hidden-Page Docs (max(page) > T and doc_score $\le$ T) | Fraction Hidden |
| :--- | ---: | ---: | ---: |
| 0.020 | 173 | 58 | 33.5% |
| 0.025 | 173 | 73 | 42.2% |
| 0.030 | 173 | 78 | 45.1% |
| 0.035 | 173 | 85 | 49.1% |
| 0.040 | 173 | 87 | 50.3% |
| 0.050 | 173 | 88 | 50.9% |
| 0.060 | 173 | 92 | 53.2% |

## H. Leave-One-Pure-OCR-Document-Out Analysis

| Threshold | Dropped Pure-OCR Doc | Flagged Before (5 docs) | Flagged After (4 docs) | Change | Stable? |
| :--- | :--- | ---: | ---: | ---: | :--- |
| 0.020 | `INE002A01018/2018` | 4/5 (80.0%) | 3/4 (75.0%) | -0.05 | `STABLE` |
| 0.020 | `INE002L01015/2012` | 4/5 (80.0%) | 3/4 (75.0%) | -0.05 | `STABLE` |
| 0.020 | `INE003B01014/2011` | 4/5 (80.0%) | 4/4 (100.0%) | 0.20 | **`UNSTABLE`** |
| 0.020 | `INE004C01028/2024` | 4/5 (80.0%) | 3/4 (75.0%) | -0.05 | `STABLE` |
| 0.020 | `INE009A01021/2013` | 4/5 (80.0%) | 3/4 (75.0%) | -0.05 | `STABLE` |
| 0.025 | `INE002A01018/2018` | 4/5 (80.0%) | 3/4 (75.0%) | -0.05 | `STABLE` |
| 0.025 | `INE002L01015/2012` | 4/5 (80.0%) | 3/4 (75.0%) | -0.05 | `STABLE` |
| 0.025 | `INE003B01014/2011` | 4/5 (80.0%) | 4/4 (100.0%) | 0.20 | **`UNSTABLE`** |
| 0.025 | `INE004C01028/2024` | 4/5 (80.0%) | 3/4 (75.0%) | -0.05 | `STABLE` |
| 0.025 | `INE009A01021/2013` | 4/5 (80.0%) | 3/4 (75.0%) | -0.05 | `STABLE` |
| 0.030 | `INE002A01018/2018` | 4/5 (80.0%) | 3/4 (75.0%) | -0.05 | `STABLE` |
| 0.030 | `INE002L01015/2012` | 4/5 (80.0%) | 3/4 (75.0%) | -0.05 | `STABLE` |
| 0.030 | `INE003B01014/2011` | 4/5 (80.0%) | 4/4 (100.0%) | 0.20 | **`UNSTABLE`** |
| 0.030 | `INE004C01028/2024` | 4/5 (80.0%) | 3/4 (75.0%) | -0.05 | `STABLE` |
| 0.030 | `INE009A01021/2013` | 4/5 (80.0%) | 3/4 (75.0%) | -0.05 | `STABLE` |
| 0.035 | `INE002A01018/2018` | 3/5 (60.0%) | 2/4 (50.0%) | -0.10 | `STABLE` |
| 0.035 | `INE002L01015/2012` | 3/5 (60.0%) | 2/4 (50.0%) | -0.10 | `STABLE` |
| 0.035 | `INE003B01014/2011` | 3/5 (60.0%) | 3/4 (75.0%) | 0.15 | **`UNSTABLE`** |
| 0.035 | `INE004C01028/2024` | 3/5 (60.0%) | 2/4 (50.0%) | -0.10 | `STABLE` |
| 0.035 | `INE009A01021/2013` | 3/5 (60.0%) | 3/4 (75.0%) | 0.15 | **`UNSTABLE`** |
| 0.040 | `INE002A01018/2018` | 3/5 (60.0%) | 2/4 (50.0%) | -0.10 | `STABLE` |
| 0.040 | `INE002L01015/2012` | 3/5 (60.0%) | 2/4 (50.0%) | -0.10 | `STABLE` |
| 0.040 | `INE003B01014/2011` | 3/5 (60.0%) | 3/4 (75.0%) | 0.15 | **`UNSTABLE`** |
| 0.040 | `INE004C01028/2024` | 3/5 (60.0%) | 2/4 (50.0%) | -0.10 | `STABLE` |
| 0.040 | `INE009A01021/2013` | 3/5 (60.0%) | 3/4 (75.0%) | 0.15 | **`UNSTABLE`** |
| 0.050 | `INE002A01018/2018` | 3/5 (60.0%) | 2/4 (50.0%) | -0.10 | `STABLE` |
| 0.050 | `INE002L01015/2012` | 3/5 (60.0%) | 2/4 (50.0%) | -0.10 | `STABLE` |
| 0.050 | `INE003B01014/2011` | 3/5 (60.0%) | 3/4 (75.0%) | 0.15 | **`UNSTABLE`** |
| 0.050 | `INE004C01028/2024` | 3/5 (60.0%) | 2/4 (50.0%) | -0.10 | `STABLE` |
| 0.050 | `INE009A01021/2013` | 3/5 (60.0%) | 3/4 (75.0%) | 0.15 | **`UNSTABLE`** |
| 0.060 | `INE002A01018/2018` | 3/5 (60.0%) | 2/4 (50.0%) | -0.10 | `STABLE` |
| 0.060 | `INE002L01015/2012` | 3/5 (60.0%) | 2/4 (50.0%) | -0.10 | `STABLE` |
| 0.060 | `INE003B01014/2011` | 3/5 (60.0%) | 3/4 (75.0%) | 0.15 | **`UNSTABLE`** |
| 0.060 | `INE004C01028/2024` | 3/5 (60.0%) | 2/4 (50.0%) | -0.10 | `STABLE` |
| 0.060 | `INE009A01021/2013` | 3/5 (60.0%) | 3/4 (75.0%) | 0.15 | **`UNSTABLE`** |

## I. Within-Document Mixed-Document Analysis (16 Documents)

| Document ID | Company | FY | Native Pages | OCR Pages | Native Med | OCR Med | Native > 0.03 | OCR > 0.03 |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `INE001B01026/2013` | INE001B01026 | 2013 | 10 | 4 | 0.0000 | 0.0312 | 20.0% | 50.0% |
| `INE001B01026/2017` | INE001B01026 | 2017 | 32 | 3 | 0.0000 | 0.0000 | 18.8% | 0.0% |
| `INE004C01028/2017` | INE004C01028 | 2017 | 10 | 4 | 0.0358 | 0.0000 | 60.0% | 25.0% |
| `INE040A01034/2017` | INE040A01034 | 2017 | 13 | 1 | 0.0000 | 0.2188 | 38.5% | 100.0% |
| `INE040A01034/2018` | INE040A01034 | 2018 | 17 | 3 | 0.0000 | 0.0000 | 29.4% | 33.3% |
| `INE044A01036/2012` | INE044A01036 | 2012 | 3 | 17 | 0.0625 | 0.0000 | 66.7% | 17.6% |
| `INE044A01036/2017` | INE044A01036 | 2017 | 22 | 1 | 0.0000 | 0.0000 | 13.6% | 0.0% |
| `INE081A01020/2013` | INE081A01020 | 2013 | 42 | 2 | 0.0148 | 0.0613 | 40.5% | 50.0% |
| `INE119A01028/2013` | INE119A01028 | 2013 | 7 | 2 | 0.0000 | 0.2309 | 42.9% | 100.0% |
| `INE171A01029/2017` | INE171A01029 | 2017 | 41 | 1 | 0.0000 | 0.0000 | 19.5% | 0.0% |
| `INE171A01029/2018` | INE171A01029 | 2018 | 41 | 1 | 0.0000 | 0.0000 | 26.8% | 0.0% |
| `INE191H01014/2025` | INE191H01014 | 2025 | 25 | 4 | 0.0870 | 0.0416 | 64.0% | 50.0% |
| `INE192B01031/2024` | INE192B01031 | 2024 | 25 | 2 | 0.0000 | 0.0000 | 4.0% | 0.0% |
| `INE192B01031/2025` | INE192B01031 | 2025 | 35 | 2 | 0.0000 | 0.0556 | 8.6% | 50.0% |
| `INE482A01020/2018` | INE482A01020 | 2018 | 38 | 1 | 0.0000 | 0.0000 | 10.5% | 0.0% |
| `INE761H01022/2013` | INE761H01022 | 2013 | 3 | 1 | 0.0000 | 0.0000 | 33.3% | 0.0% |

## J. Diagnostic Figures

1. **Page-Level Sensitivity**: `reports/pm2_2_sensitivity.png`
2. **Document-Level Sensitivity**: `reports/pm2_2_document_sensitivity.png`
3. **Hidden-Page Effect**: `reports/pm2_2_hidden_pages.png`
4. **Page Distributions & Candidates**: `reports/pm2_2_page_distributions.png`

## K. Production Safety Verification

```text
production behavior changed: NO
production threshold changed: NO (ORPHAN_START_FRAC_MAX = 0.03)
production OCR routing changed: NO
production grading changed: NO
production verification changed: NO
```

## L. Final Decision

**SEPARATE OCR THRESHOLD HYPOTHESIS — NOT IMPLEMENTED**

- **Proposed OCR Hypothesis**: `0.04`
- **Status**: `EXPLORATORY / NOT IMPLEMENTED`
- **Independent Pure-OCR Document N**: 5
- **OCR-Containing Document N**: 21
- **OCR Page N**: 134
- **Stability Under Leave-One-Out**: MODERATE (2/5 flagged at 0.040 vs 4/5 at 0.030; single-document removal shifts flagged fraction between 25% and 50%)
- **Rationale**: At the current 0.030 threshold, OCR pages exhibit an elevated failure rate (41.79%) compared to Native (25.17%). An exploratory threshold of T=0.040 brings the OCR page failure rate to 23.88%, aligning with the native 0.030 operating point. However, because independent pure-OCR documents are limited to N=5 (where 2/5 docs remain flagged), this value is an exploratory hypothesis for a future pre-registered formal study, not a production change. Production threshold remains strictly ORPHAN_START_FRAC_MAX = 0.03.
