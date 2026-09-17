# P-M2.1: Native vs OCR `orphan_start_frac` at True Page Grain

## A. Population

- **Total corpus documents**: 194
- **Located documents**: 182
- **Unlocated documents (excluded from page scoring)**: 12 (reason: `mda_not_located`)
- **Total MD&A physical pages**: 2734
- **Measured page scores**: 2547
- **Native pages**: 2592 total (2412 measured, 180 unmeasured)
- **OCR pages**: 141 total (134 measured, 7 unmeasured)
- **Unknown-provenance pages**: 1 total (1 measured, 0 unmeasured)
- **Null / unmeasured pages**: 187 (breakdown: {'fewer_than_min_paragraphs': 187})

> **Accounting Reconciliation**: `2734 (total) = 2412 (native) + 134 (ocr) + 1 (unknown) + 187 (null)`
> **Reconciliation Verified**: True

### Document-Level Context
- Pure-native documents: 160
- Pure-OCR documents: 5
- Mixed documents: 16
- Unknown-provenance documents: 1

## B. Page-Level Distribution

| Population | N pages | N documents | Min | P25 | Median | P75 | P90 | P95 | Max |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Native** | 2412 | 169 | 0.0000 | 0.0000 | 0.0000 | 0.0303 | 0.0833 | 0.1221 | 0.6471 |
| **OCR** | 134 | 21 | 0.0000 | 0.0000 | 0.0000 | 0.0620 | 0.1250 | 0.1667 | 0.4286 |

*Percentile method: linear (numpy.percentile method='linear' or exact pure-Python equivalent)*

## C. Threshold Diagnostics

| Metric | Native | OCR |
| :--- | ---: | ---: |
| Total measured pages ($N$) | 2412 | 134 |
| Count < 0.03 | 1805 | 78 |
| Count == 0.03 | 0 | 0 |
| Count > 0.03 | 607 | 56 |
| Fraction > 0.03 | 0.2517 | 0.4179 |
| Max score $\le 0.03$ | 0.0294 | 0.0294 |
| Min score $> 0.03$ | 0.0303 | 0.0323 |
| Gap around 0.03 | 0.0009 | 0.0029 |
| Near-gate count ($0.029 \le s \le 0.031$) | 19 | 1 |

## D. Native vs OCR Interpretation

1. **Is OCR materially different from native at page grain?**
   - Median delta (OCR - Native): `0.0000`
   - P95 delta (OCR - Native): `0.0446`
   - Max delta (OCR - Native): `-0.2185`
   - Fraction > 0.03 delta (OCR - Native): `0.1663`
   - Descriptive summary: Native median is `0.0000` (P95 `0.1221`, 25.2% > 0.03). OCR median is `0.0000` (P95 `0.1667`, 41.8% > 0.03).

2. **Is the evidence based on enough independent OCR documents?**
   - Native: 2412 pages across 169 independent documents.
   - OCR: 134 pages across 21 independent documents.
   - Correlation note: Pages within the same document are correlated. Inferential claims must respect the independent document sample size ($N=21$).

3. **Does 0.03 sit in an observed empty band?**
   - Native: Gap is `0.0009` (max $\le 0.03$: `0.0294`, min $> 0.03$: `0.0303`). There are 19 observations tightly flanking the boundary ($0.029 \le s \le 0.031$). The threshold sits within a continuous distribution, not an empty band.
   - OCR: Gap is `0.0029` (max $\le 0.03$: `0.0294`, min $> 0.03$: `0.0323`).

4. **Is a separate threshold study justified?**
   - Verdict: **SEPARATE OCR THRESHOLD STUDY JUSTIFIED — NOT IMPLEMENTED**
   - Rationale: The observed OCR page-level distribution differs materially from native (fraction > 0.03 delta: +0.1663, median delta: +0.0000), justifying a future pre-registered threshold-fitting study. Production threshold remains 0.03.

## E. Highest-Scoring Pages

### Top OCR Pages by `orphan_start_frac`
| Company ID | FY | Physical Page | Score | Provenance Source | Document Grade | Document Reasons |
| :--- | ---: | ---: | ---: | :--- | :--- | :--- |
| INE119A01028 | 2013 | 68 | 0.4286 | `ocr_stats:words=726` | low | source_shredded, span_truncated |
| INE002A01018 | 2018 | 88 | 0.2500 | `ocr_stats:words=463` | low | source_shredded, span_truncated |
| INE040A01034 | 2017 | 25 | 0.2188 | `ocr_stats:words=613` | low | source_shredded, span_truncated |
| INE002A01018 | 2018 | 100 | 0.2105 | `ocr_stats:words=462` | low | source_shredded, span_truncated |
| INE191H01014 | 2025 | 93 | 0.1818 | `ocr_stats:words=88` | low | source_shredded, span_truncated |
| INE002A01018 | 2018 | 103 | 0.1786 | `ocr_stats:words=179` | low | source_shredded, span_truncated |
| INE002A01018 | 2018 | 68 | 0.1667 | `ocr_stats:words=277` | low | source_shredded, span_truncated |
| INE002A01018 | 2018 | 104 | 0.1667 | `ocr_stats:words=382` | low | source_shredded, span_truncated |
| INE040A01034 | 2018 | 40 | 0.1538 | `ocr_stats:words=795` | medium | source_shredded, span_truncated |
| INE002A01018 | 2018 | 87 | 0.1500 | `ocr_stats:words=87` | low | source_shredded, span_truncated |
| INE004C01028 | 2017 | 39 | 0.1429 | `ocr_stats:words=329` | low | year_unproven, order_scrambled, span_truncated |
| INE002A01018 | 2018 | 95 | 0.1333 | `ocr_stats:words=198` | low | source_shredded, span_truncated |
| INE002A01018 | 2018 | 99 | 0.1333 | `ocr_stats:words=205` | low | source_shredded, span_truncated |
| INE001B01026 | 2018 | 48 | 0.1250 | `ocr_stats:words=11` | low | source_shredded, span_truncated |
| INE002A01018 | 2018 | 81 | 0.1250 | `ocr_stats:words=542` | low | source_shredded, span_truncated |
| INE192B01031 | 2025 | 159 | 0.1111 | `ocr_stats:words=52` | high | span_truncated |
| INE002A01018 | 2018 | 86 | 0.1081 | `ocr_stats:words=533` | low | source_shredded, span_truncated |
| INE002A01018 | 2018 | 70 | 0.1000 | `ocr_stats:words=529` | low | source_shredded, span_truncated |
| INE044A01036 | 2012 | 21 | 0.0952 | `ocr_stats:words=134` | medium | span_truncated |
| INE081A01020 | 2013 | 65 | 0.0933 | `ocr_stats:words=588` | medium | source_shredded, span_truncated |

### Top Native Pages by `orphan_start_frac`
| Company ID | FY | Physical Page | Score | Provenance Source | Document Grade | Document Reasons |
| :--- | ---: | ---: | ---: | :--- | :--- | :--- |
| INE002S01010 | 2017 | 45 | 0.6471 | `page_kind:digital` | low | source_shredded |
| INE002L01015 | 2024 | 40 | 0.5000 | `page_kind:digital` | low | source_shredded, span_truncated |
| INE044A01036 | 2013 | 16 | 0.4359 | `page_kind:digital` | low | source_shredded, span_truncated |
| INE008A01015 | 2025 | 146 | 0.4167 | `page_kind:digital` | quarantine | source_shredded, span_truncated, WRONG_LANGUAGE_RISK |
| INE040A01034 | 2018 | 35 | 0.4118 | `page_kind:digital` | medium | source_shredded, span_truncated |
| INE171A01029 | 2012 | 34 | 0.3750 | `page_kind:digital` | low | section_leak, order_scrambled, span_truncated |
| INE797F01020 | 2012 | 29 | 0.3729 | `page_kind:digital` | low | source_shredded, span_truncated |
| INE171A01029 | 2012 | 42 | 0.3548 | `page_kind:digital` | low | section_leak, order_scrambled, span_truncated |
| INE171A01029 | 2012 | 41 | 0.3529 | `page_kind:digital` | low | section_leak, order_scrambled, span_truncated |
| INE040A01034 | 2025 | 232 | 0.3478 | `page_kind:digital` | medium | section_leak, span_truncated |
| INE008A01015 | 2024 | 108 | 0.3214 | `page_kind:digital` | quarantine | source_shredded, span_truncated, WRONG_LANGUAGE_RISK |
| INE002L01015 | 2025 | 46 | 0.3093 | `page_kind:digital` | low | source_shredded, span_truncated |
| INE191H01014 | 2025 | 99 | 0.3077 | `page_kind:digital` | low | source_shredded, span_truncated |
| INE008A01015 | 2024 | 143 | 0.3077 | `page_kind:digital` | quarantine | source_shredded, span_truncated, WRONG_LANGUAGE_RISK |
| INE192B01031 | 2012 | 53 | 0.3030 | `page_kind:digital` | low | identity_unproven, year_unproven, source_shredded, span_truncated |
| INE004Z01011 | 2024 | 47 | 0.3000 | `page_kind:digital` | medium | source_shredded, span_truncated |
| INE191H01014 | 2025 | 96 | 0.2917 | `page_kind:digital` | low | source_shredded, span_truncated |
| INE191H01014 | 2025 | 95 | 0.2857 | `page_kind:digital` | low | source_shredded, span_truncated |
| INE008A01015 | 2024 | 134 | 0.2857 | `page_kind:digital` | quarantine | source_shredded, span_truncated, WRONG_LANGUAGE_RISK |
| INE002L01015 | 2025 | 48 | 0.2791 | `page_kind:digital` | low | source_shredded, span_truncated |

## F. Production Reason & Full-Width Block Correlation

### Production Reason Codes for High-Scoring Pages (`score > 0.03`)
| Population | Total Bad Pages | Containing Doc has `source_shredded` | Containing Doc has `order_scrambled` | Has Either Reason | Has Neither Reason |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Native | 607 | 273 | 46 | 319 | 288 |
| OCR | 56 | 49 | 1 | 50 | 6 |

### Full-Width Block Geometric Signal for High-Scoring Pages (`score > 0.03`)
| Population | Total Bad Pages | Full-Width Block = True | Full-Width Block = False | Full-Width Status Unavailable |
| :--- | ---: | ---: | ---: | ---: |
| Native | 607 | 396 (65.2%) | 211 (34.8%) | 0 (0.0%) |
| OCR | 56 | 43 (76.8%) | 7 (12.5%) | 6 (10.7%) |

> Note: Co-occurrence is not causation.

## G. Regression & Production Safety

```text
production behavior changed: NO
threshold changed: NO (ORPHAN_START_FRAC_MAX = 0.03)
OCR routing changed: NO
segmentation changed: NO
grading changed: NO
verification changed: NO
```

## Final Decision

**SEPARATE OCR THRESHOLD STUDY JUSTIFIED — NOT IMPLEMENTED**

The observed OCR page-level distribution differs materially from native (fraction > 0.03 delta: +0.1663, median delta: +0.0000), justifying a future pre-registered threshold-fitting study. Production threshold remains 0.03.
