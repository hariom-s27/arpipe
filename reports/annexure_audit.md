# P-M4 — Annexure-Form Audit & Diagnostic Report

## 1. Executive Summary & Research Question

> **Research Question**: Is the form of the MD&A heading systematically associated with company size or fiscal era, and does ARPipe extraction performance differ across those heading forms?

This is an **audit and diagnostic study only**. In compliance with the P-M4 specification, no production segmentation rules, regex patterns, triage policies, OCR routing, or confidence thresholds have been modified.

---

## 2. Gate Verification & Population Integrity

- **Dedicated Worktree**: `D:\sem_iitk\sem9\thesis\sep_week1\arpipe-pm4-annexure-audit`
- **Base Commit**: `158a9eac48a3374a9506af8281acb93f49a37a0d`
- **Audit Branch**: `pm4-annexure-audit`
- **Analysis Date**: `2026-09-17`
- **Evaluation Protocol Version**: `12 September 2026 (seed: 20260912)`
- **P-M4 Holdout Labels Inspected**: `NO`
- **P-M4 Holdout Outcomes Inspected**: `NO`
- **P-M4 Holdout Membership Unchanged**: `YES`

### Population Accounting Reconciliation
- **All Fit Documents (Historical Labelled Set)**: 20
- **Fit Queue Candidates (Unlabelled)**: 92
- **Total Frozen Fit Universe**: 112
- **Eligible Documents (Known True Start)**: **18**
- **Excluded Documents (`NO_VERIFIED_TRUE_START`)**: **2**

---

## 3. Required Audit Tables

### Table A — Overall Heading-Form Distribution

| Heading Form | N Documents | Eligible Denominator | Percentage |
| :--- | :---: | :---: | :---: |
| `standalone_heading` | 12 | 18 | 66.67% |
| `annexure_labelled` | 3 | 18 | 16.67% |
| `combined_with_directors_report` | 1 | 18 | 5.56% |
| `other` | 2 | 18 | 11.11% |

### Table B — Heading-Form Distribution by Cap Band

| Cap Band | Eligible N | Standalone Heading | Annexure Labelled | Combined with Directors' Report | Other | Ambiguous |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `large` | 8 | 6 (75.0%) | 1 (12.5%) | 1 (12.5%) | 0 (0.0%) | 0 (0.0%) |
| `mid` | 2 | 1 (50.0%) | 1 (50.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| `small` | 0 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| `micro` | 8 | 5 (62.5%) | 1 (12.5%) | 0 (0.0%) | 2 (25.0%) | 1 (12.5%) |

### Table C — Heading-Form Distribution by Fiscal Era

| Fiscal Era | Eligible N | Standalone Heading | Annexure Labelled | Combined with Directors' Report | Other | Ambiguous |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `2010-2013` | 13 | 10 (76.9%) | 2 (15.4%) | 0 (0.0%) | 1 (7.7%) | 1 (7.7%) |
| `2014-2018` | 5 | 2 (40.0%) | 1 (20.0%) | 1 (20.0%) | 1 (20.0%) | 0 (0.0%) |
| `2019-2025` | 0 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |

### Table D — Cap-Band Annexure Screening Rule (10-Percentage-Point Screen)

| Cap Band | Eligible N | Annexure N | Annexure Fraction (%) | Note |
| :--- | :---: | :---: | :---: | :--- |
| `large` | 8 | 1 | 12.50% | evaluable |
| `mid` | 2 | 1 | 50.00% | descriptive only |
| `micro` | 8 | 1 | 12.50% | evaluable |

- **Maximum Cap-Band Annexure Fraction**: `50.00%` (cap band: `mid`)
- **Minimum Cap-Band Annexure Fraction**: `12.50%` (cap bands: `large`, `micro`)
- **Absolute Difference**: **`37.50` percentage points**
- **Screening Rule Result**: **`PROMINENT SYSTEMATIC-BIAS SIGNAL — ANNEXURE FRACTION DIFFERS BY MORE THAN 10 PP ACROSS CAP BANDS`**

> [!NOTE]
> The 10-percentage-point screen is an operational screening heuristic, not a test of statistical significance. Because the `mid` cap band contains only 2 eligible documents, this threshold flag indicates a strong candidate signal that warrants monitoring rather than conclusive proof of structural asymmetry.

### Joint Descriptive Distribution: Fiscal Era × Cap Band

| Fiscal Era | Cap Band | Eligible N | Annexure N | Annexure % | Note |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `2010-2013` | `large` | 6 | 0 | 0.0% | evaluable |
| `2010-2013` | `mid` | 2 | 1 | 50.0% | descriptive only |
| `2010-2013` | `small` | 0 | 0 | 0.0% | descriptive only |
| `2010-2013` | `micro` | 5 | 1 | 20.0% | evaluable |
| `2014-2018` | `large` | 2 | 1 | 50.0% | descriptive only |
| `2014-2018` | `mid` | 0 | 0 | 0.0% | descriptive only |
| `2014-2018` | `small` | 0 | 0 | 0.0% | descriptive only |
| `2014-2018` | `micro` | 3 | 0 | 0.0% | descriptive only |
| `2019-2025` | `large` | 0 | 0 | 0.0% | descriptive only |
| `2019-2025` | `mid` | 0 | 0 | 0.0% | descriptive only |
| `2019-2025` | `small` | 0 | 0 | 0.0% | descriptive only |
| `2019-2025` | `micro` | 0 | 0 | 0.0% | descriptive only |

### Table E — Extraction Accuracy by Heading Form

| Heading Form | Evaluated N | Exact Start Correct | Exact Start Accuracy | Within 1 Pg Correct | Within 1 Pg Accuracy | Note |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `standalone_heading` | 12 | 11 | 91.7% | 11 | 91.7% | evaluable |
| `annexure_labelled` | 3 | 2 | 66.7% | 2 | 66.7% | descriptive only |
| `combined_with_directors_report` | 1 | 1 | 100.0% | 1 | 100.0% | descriptive only |
| `other` | 2 | 2 | 100.0% | 2 | 100.0% | descriptive only |

### Table F — Exclusions and Ambiguity Breakdown

| Reason | N Documents |
| :--- | :---: |
| `no verified true start` | 2 |
| `unlabelled queue candidates` | 92 |
| `ambiguous` | 1 |
| `unreadable` | 0 |
| `insufficient context` | 2 |

---

## 4. Required Final Interpretation (Section 25)

### A. How common is annexure-labelled MD&A?
**MEASURED**: In the eligible frozen fit population ($N=18$), annexure-labelled MD&A represents **16.67%** (3/18 documents). The predominant heading presentation is `standalone_heading`, accounting for **66.67%** (12/18 documents). `other` represents **11.11%** (2/18 documents), and `combined_with_directors_report` represents **5.56%** (1/18 documents).

### B. Is annexure-labelled MD&A concentrated by cap band?
**DESCRIPTIVE ASSOCIATION**: Annexure-labelled MD&A is descriptively observed in `mid` cap (1/2, 50.0%), `large` cap (1/8, 12.5%), and `micro` cap (1/8, 12.5%). No eligible documents in the frozen fit set are classified as `small` cap.

### C. Is annexure-labelled MD&A concentrated by fiscal era?
**DESCRIPTIVE ASSOCIATION**: Annexure-labelled MD&A is present in both `2010-2013` (2/13, 15.38%) and `2014-2018` (1/5, 20.00%). There are no eligible documents from `2019-2025` in this historical fit set. The rate is comparable between the two observed historical eras.

### D. Does the cap-band difference exceed 10 percentage points?
**SCREENING SIGNAL**: YES. The maximum cap-band annexure fraction is 50.00% (`mid`), and the minimum is 12.50% (`large` and `micro`), yielding an absolute difference of **37.50 percentage points**, which exceeds the 10-percentage-point screening threshold.

### E. Does extraction accuracy differ descriptively across heading forms?
**DESCRIPTIVE ASSOCIATION**: ARPipe exact-start accuracy was descriptively lower for `annexure_labelled` documents (**66.7%**, 2/3 correct) compared to `standalone_heading` documents (**91.7%**, 11/12 correct). `combined_with_directors_report` scored 100.0% (1/1), and `other` scored 100.0% (2/2).

### F. Are those accuracy comparisons sufficiently supported by sample size?
**NOT ESTABLISHED**: NO. With only 3 annexure-labelled documents and 1 combined document, the group sizes are too small for inferential or statistical claims. The single annexure failure was `INE003B01014` (Inter State Oil Carrier FY2011), which is a scanned document where heading OCR failed completely. These results are descriptive only.

### G. Could observed extraction differences simply reflect composition differences?
**NOT ESTABLISHED**: YES. The single failure among annexure-labelled documents occurred in a scanned report (`doc_kind=scanned`). In contrast, born-digital annexure documents (`INE257A01026` BHEL and `INE733E01010` NTPC) achieved 100% exact start accuracy. The observed accuracy difference may reflect document scan quality rather than heading syntax per se.

### H. What evidence is established?
**MEASURED**: Standalone headings are the dominant form of MD&A introduction (66.7%). Annexure labelling is a non-trivial minority pattern (16.7%) that spans both public sector undertakings (BHEL, NTPC) and private micro-caps (Inter State Oil). The ARPipe pipeline is capable of recognizing annexure headings in born-digital filings without modification.

### I. What remains unknown?
**NOT ESTABLISHED**: Whether annexure labelling causes segmentation failures in native digital filings, whether the 37.5 pp difference persists in larger sample sizes, and the prevalence of annexure labelling in modern filings (`2019-2025`), which were not represented in this historical fit cohort.

---

## 5. Required Final Conclusion Format (Section 26)

```text
ANNEXURE-FORM AUDIT — COMPLETED

Fit documents: 20
Eligible documents: 18
Excluded documents: 2

Annexure-labelled fraction: 3/18 (16.7%)
Cap-band maximum difference: 37.5 pp
>10 PP screen: PROMINENT SYSTEMATIC-BIAS SIGNAL — ANNEXURE FRACTION DIFFERS BY MORE THAN 10 PP ACROSS CAP BANDS
Fiscal-era pattern: 2010-2013: 2/13 (15.4%), 2014-2018: 1/5 (20.0%)

Extraction accuracy by heading form:
  standalone_heading: 11/12 (91.7%)
  annexure_labelled: 2/3 (66.7%)
  combined_with_directors_report: 1/1 (100.0%)
  other: 2/2 (100.0%)
Sample-size limitation: Annexure N=3; Mid-cap N=2; cells marked descriptive only

Holdout inspected: NO
Production changed: NO
Pipeline modified: NO
```

### Scientific Conclusion

**ANNEXURE-FORM CONCENTRATION OBSERVED**

*(Flagged by 10-pp screen across cap bands; descriptive only due to mid-cap N=2; no production modification authorized).* 
