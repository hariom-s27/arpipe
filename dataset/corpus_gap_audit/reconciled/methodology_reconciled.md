# ARPipe T0.1R Post-Audit Reconciliation Methodology

## 1. Reconciliation Purpose and Scope
This document defines the post-audit reconciliation methodology applied to the completed ARPipe T0.1 Corpus Gap Audit. The objective is to preserve the historical raw evidence while correcting construct definitions, auditing claims, repairing review provenance, and machine-checking the corrected scientific report.

## 2. Strict Operational Boundaries
- **No T0 or Production Code Modification**: T0 corpus artifacts and pipeline code in `arpipe/` remain strictly immutable.
- **No Detector Development or PDF Inspection**: T0.1R does not run new detectors or inspect raw PDF bytes to invent new condition labels.
- **Derived Evidence Isolation**: All reconciled artifacts reside under `dataset/corpus_gap_audit/reconciled/` and are explicitly marked as `DERIVED_RECONCILIATION`.
- **Fail-Closed Input Verification**: All inputs are checked against `configs/t0_1r/input_allowlist.json` using `git show <commit>:<path>` byte comparison.

## 3. Source-of-Truth Evidentiary Hierarchy
1. Frozen PDF disk bytes + SHA-256
2. Frozen T0 baseline artifacts (`dataset/corpus_freeze/`)
3. T0.1 RAW machine-readable artifacts (`dataset/corpus_gap_audit/`)
4. T0.1 implementation code establishing detector semantics (`tools/audit_corpus_gaps.py`)
5. Explicit deterministic calculations derived from 1–4
6. Narrative report text (subordinate to machine-readable data)

## 4. Key Methodological Corrections
- **Model-Review Provenance**: Reclassified auto-relabelled records to `NOT_REVIEWED` with issue `AUTO_RELABELLED_WITHOUT_MODEL_INSPECTION`.
- **Fully Scanned Documents**: Reconciled from canonical `gap_audit_document.csv` confirming exactly 2 fully scanned documents (91 pages).
- **Mixed Representation**: Reconciled to canonical count of 132 documents (30,132 pages).
- **Corpus Hygiene and Stub Classification**: Documents with `total_pages <= 2` are classified as `STUB`; documents with `total_pages > 2` are classified as `STANDARD`. Stubs remain part of the frozen corpus.
- **Candidate Proxy vs Ground Truth**: Explicitly distinguished heuristic signals (tables, annexures, running furniture, TOC offsets, OCR proxy) from verified semantic ground truth.
- **Interaction Dependencies**: Renamed metric to `total_pages_in_docs_meeting_both`. Classified interaction dependencies into `TAUTOLOGICAL` (strict equivalence), `KNOWN_DEPENDENCY` (definitional implication without two-way equivalence, e.g. OCR proxy implying mixed/scanned representation in `tools/audit_corpus_gaps.py`), or `NOT_ASSESSED`, with code function provenance without line numbers.
- **Core vs Robustness Acquisition Boundary**: Narrowed core acquisition finding to: No additional acquisition is currently justified for the core thesis under the predefined claim scope and available evidence. Targeted acquisition may remain an optional robustness extension for explicitly defined edge-case claims.
- **Claim-Register-Driven Validation**: Every quantitative and scientific statement is indexed in `claim_audit.csv` with machine-executable calculation IDs and semantic anchors.
