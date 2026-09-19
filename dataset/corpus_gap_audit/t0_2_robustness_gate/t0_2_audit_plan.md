# T0.2 Robustness-Gate Decision Audit Plan and Evidence Report

## 1. Executive Summary & Verification of Baseline

- **Base Commit**: `879762a2f236b3aaa6df33b7ddacc60c01d633c1`
- **Frozen Core-Thesis Invariant**: `NO_ACQUISITION`
- **Core Decision Invariant Status**: `PRESERVED`
- **Total Derived Conditions**: 3
- **Derived Condition Set**: `duplicate_overlapping_text`, `toc_offset_discrepancy`, `fully_scanned_documents`
- **Triggers Defined**: 1
- **Triggers Executed**: 0
- **Acquisitions Currently Justified**: 0

T0.2 is a deterministic decision audit evaluating all conditions marked `ADDITIONAL_AUDIT_REQUIRED` in the frozen T0.1R acquisition decision table.
It enforces a strict non-measurement policy: zero PDF acquisitions, zero new PDF inspections, zero new OCR detectors, and zero newly invented numeric thresholds.

## 2. Core-Thesis Invariant Protection

The frozen T0.1R core-thesis acquisition decision is **`NO_ACQUISITION`**.
T0.2 machine-checks and guarantees that this core-thesis decision remains completely frozen and unmodified.
Execution fails closed immediately if any attempt is made to alter this baseline decision.

## 3. Condition Derivation and Claim Traceability

The scope of T0.2 is derived dynamically from frozen `acquisition_decision.csv`:
```sql
SELECT condition, current_evidence, source_claim_ids
FROM acquisition_decision.csv
WHERE acquisition_status == 'ADDITIONAL_AUDIT_REQUIRED'
```
Exactly 3 conditions are derived and audited without omission or manual hard-coding.

### Audit Decisions Summary Table

| Condition | Audit Decision | Trigger Status | Trigger Executed | Acquisition Justified | Reason Summary |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `duplicate_overlapping_text` | **NO_ACQUISITION_NEEDED** | `NOT_APPLICABLE` | `FALSE` | `FALSE` | Observed evidence in frozen duplicate_text_candidates.csv directly confirms 35 d... |
| `toc_offset_discrepancy` | **NO_ACQUISITION_NEEDED** | `NOT_APPLICABLE` | `FALSE` | `FALSE` | Frozen claim CLAIM:C051 and reconciled report establish that body-heading discov... |
| `fully_scanned_documents` | **AUDIT_REQUIRED_BEFORE_ACQUISITION** | `DEFINED_UNEXECUTED` | `FALSE` | `FALSE` | Frozen artifacts establish 2 fully scanned documents (91 pages) and 63 documents... |

## 4. Condition-by-Condition Evidence Analysis

### 4.1 `duplicate_overlapping_text`
- **Uncertainty Type**: `MEASUREMENT_LIMITATION`
- **Relevance**: `ROBUSTNESS_ONLY`
- **Observed Evidence**: Frozen `duplicate_text_candidates.csv` directly confirms 35 candidate documents and 68 candidate pages across 18 issuers in all three splits (14 FIT, 10 VALIDATION, 11 HOLDOUT).
- **Existing-Evidence Audit**: Recounting and split cross-tabulation demonstrate that candidate instances are already present in the corpus across multiple corporate issuers and splits. These observed instances provide sufficient coverage for deduplication and drop-shadow filtering evaluation without expanding the corpus.
- **Decision**: **`NO_ACQUISITION_NEEDED`**.

### 4.2 `toc_offset_discrepancy`
- **Uncertainty Type**: `DEPENDENCY_LIMITATION`
- **Relevance**: `ROBUSTNESS_ONLY`
- **Observed Evidence**: In `toc_offset_candidates.csv`, 45 documents were assessed (2 strong candidates, 22 candidates, 4 unresolved, 17 not observed; 149 unassessed).
- **Existing-Evidence Audit**: Reconciled finding `CLAIM:C051` formally established that body heading discovery operates independently of TOC. Empirical evidence shows TOC offsets are an auxiliary signal, not a gating prerequisite for MD&A boundary localization.
- **Decision**: **`NO_ACQUISITION_NEEDED`**.

### 4.3 `fully_scanned_documents`
- **Uncertainty Type**: `COVERAGE_LIMITATION`
- **Relevance**: `ROBUSTNESS_ONLY`
- **Observed Evidence**: Exactly 2 fully scanned documents (91 pages across 2 issuers: `INE002L01015_2012` [43 pages], `INE003B01014_2011` [48 pages]) and 63 documents with scanned pages (284 candidate pages / 1,732 total pages across 30 issuers) exist in frozen reconciled artifacts.
- **Limitation**: Frozen artifacts contain zero OCR quality metrics (CER/WER) or OCR-based localization metrics. T0.2 is strictly forbidden from performing new PDF inspections or OCR measurements.
- **Pre-registered Robustness Hypothesis**: Defined `HYP_ROB_SCANNED_01`.
- **Falsifiable Trigger**: Defined `TRIGGER_HISTORICAL_SCAN_01`, conditioned on a future pre-registered benchmark.
- **Trigger State**: `trigger_definition_status = DEFINED_UNEXECUTED`, `trigger_executed = FALSE`, `trigger_result = NOT_EXECUTED`, `acquisition_currently_justified = FALSE`.
- **Thresholds & Sample Size**: No arbitrary numbers invented (`threshold_status = TO_BE_SPECIFIED_BEFORE_EXECUTION`, `minimum_sample_size = TO_BE_SPECIFIED_BEFORE_ACQUISITION`).
- **Decision**: **`AUDIT_REQUIRED_BEFORE_ACQUISITION`**.

## 5. Summary of Invariant Checks

1. Base commit strictly verified: `879762a2f236b3aaa6df33b7ddacc60c01d633c1`.
2. All frozen T0.1R inputs verified by SHA-256 and preserved byte-identically.
3. Core-thesis decision strictly maintained: `NO_ACQUISITION`.
4. Non-measurement policy maintained: zero PDF acquisitions, zero OCR experiments, zero new labels.
5. Deterministic reproducibility: all outputs generated with stable sort order and LF line terminators.

