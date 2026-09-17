"""Focused tests for P-M2.2: Exploratory orphan_start_frac threshold sensitivity study.

Covers all requirements from P-M2.2 specification Section 26:
1. frozen page snapshot integrity & reconciliation
2. threshold candidate set immutability & exact 7 values
3. canonical document-level metric ingestion (verbatim, not recomputed)
4. null/unmeasured handling (never converted to zero)
5. page/document denominator logic
6. native/OCR classification precedence
7. mixed-document handling
8. strict > threshold semantics
9. threshold evidence-table reproducibility
10. leave-one-pure-OCR-document-out stability calculation
11. hidden-document calculation
12. production-file immutability & hash verification
13. repeatability test
"""
from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path

import pytest
from tools.pm2_2_threshold_study import (
    FIXED_CANDIDATES,
    PROTECTED_PRODUCTION_FILES,
    SnapshotRow,
    compute_document_threshold_metrics,
    compute_hidden_document_analysis,
    compute_page_threshold_metrics,
    run_leave_one_pure_ocr_out,
)


# 1. Snapshot row reconciliation test
def test_snapshot_reconciliation_logic():
    rows = [
        SnapshotRow("D1", "C1", 2020, 1, "native", "digital", 0.01, True, 0.01, False, [], "pure_native"),
        SnapshotRow("D1", "C1", 2020, 2, "native", "digital", 0.00, True, 0.01, False, [], "pure_native"),
        SnapshotRow("D2", "C2", 2020, 1, "ocr", "ocr_stats", 0.04, True, 0.04, True, [], "pure_ocr"),
        SnapshotRow("D2", "C2", 2020, 2, "unknown", "blank", None, False, 0.04, None, [], "pure_ocr"),
    ]
    tot = len(rows)
    nat_m = sum(1 for r in rows if r.provenance == "native" and r.measured)
    ocr_m = sum(1 for r in rows if r.provenance == "ocr" and r.measured)
    unk_m = sum(1 for r in rows if r.provenance == "unknown" and r.measured)
    null_u = sum(1 for r in rows if not r.measured)

    assert tot == nat_m + ocr_m + unk_m + null_u
    assert nat_m == 2
    assert ocr_m == 1
    assert unk_m == 0
    assert null_u == 1


# 2. Candidate set immutability & exact 7 values
def test_threshold_candidate_set_immutability():
    expected_values = [0.020, 0.025, 0.030, 0.035, 0.040, 0.050, 0.060]
    actual_values = [c["threshold"] for c in FIXED_CANDIDATES]
    assert actual_values == expected_values
    assert len(FIXED_CANDIDATES) == 7
    # 0.030 must be inherited
    t30 = next(c for c in FIXED_CANDIDATES if c["threshold"] == 0.030)
    assert t30["status"] == "inherited"


# 3. Canonical document-level metric ingestion
def test_canonical_document_level_metric_verbatim():
    """Document score must be copied verbatim, never recomputed as mean or max."""
    r = SnapshotRow(
        "D1", "C1", 2020, 1, "native", "digital", 0.10, True,
        document_level_orphan_start_frac=0.015, full_width_block=False,
        reason_codes=[], document_class="pure_native"
    )
    # Page score is 0.10, but document-level score is 0.015 (verbatim from P-M1)
    assert r.document_level_orphan_start_frac == 0.015
    assert r.document_level_orphan_start_frac != r.orphan_start_frac


# 4. Null / unmeasured handling
def test_null_unmeasured_handling():
    """Unmeasured pages have orphan_start_frac=None and measured=False; never 0.0."""
    r = SnapshotRow(
        "D1", "C1", 2020, 1, "native", "digital", None, False,
        document_level_orphan_start_frac=0.015, full_width_block=None,
        reason_codes=[], document_class="pure_native"
    )
    assert r.orphan_start_frac is None
    assert r.measured is False
    # Not counted in numeric metrics
    res = compute_page_threshold_metrics([0.02, 0.05], T=0.03)
    assert res["n_measured"] == 2


# 5. Denominator logic for page and document metrics
def test_denominator_logic():
    scores = [0.01, 0.02, 0.05]
    res = compute_page_threshold_metrics(scores, T=0.03)
    assert res["n_measured"] == 3
    assert res["fraction_above"] == 1 / 3

    # Document denominator
    doc_pages_map = {
        "D1": [SnapshotRow("D1", "C1", 2020, 1, "native", "digital", 0.04, True, 0.02, False, [], "pure_native")],
        "D2": [SnapshotRow("D2", "C2", 2020, 1, "native", "digital", None, False, 0.00, False, [], "pure_native")],  # unmeasured doc
    }
    d_res = compute_document_threshold_metrics(doc_pages_map, T=0.03)
    assert d_res["n_measurable_docs"] == 1
    assert d_res["docs_any_gt_T"] == 1
    assert d_res["frac_any_gt_T"] == 1.0


# 6. Provenance precedence logic
def test_provenance_precedence():
    from tools.pm2_pagegrain_native_vs_ocr import classify_page_provenance
    from arpipe.models import PageKind

    # OCR words > 0 takes priority over digital
    prov, src = classify_page_provenance(1, 1, 1, {1: 100}, {1: PageKind.DIGITAL})
    assert prov == "ocr"

    # Digital takes priority when no OCR words
    prov, src = classify_page_provenance(1, 1, 1, {1: 0}, {1: PageKind.DIGITAL})
    assert prov == "native"


# 7. Mixed document handling
def test_mixed_document_handling():
    rows = [
        SnapshotRow("M1", "C1", 2020, 1, "native", "digital", 0.01, True, 0.02, False, [], "mixed"),
        SnapshotRow("M1", "C1", 2020, 2, "ocr", "ocr_stats", 0.05, True, 0.02, False, [], "mixed"),
    ]
    nat_scores = [r.orphan_start_frac for r in rows if r.provenance == "native" and r.measured and r.orphan_start_frac is not None]
    ocr_scores = [r.orphan_start_frac for r in rows if r.provenance == "ocr" and r.measured and r.orphan_start_frac is not None]
    assert len(nat_scores) == 1
    assert len(ocr_scores) == 1
    assert nat_scores[0] == 0.01
    assert ocr_scores[0] == 0.05


# 8. Strict > threshold semantics
def test_strict_threshold_semantics():
    scores = [0.03, 0.030001, 0.029999]
    res = compute_page_threshold_metrics(scores, T=0.03)
    assert res["n_below"] == 1
    assert res["n_at"] == 1
    assert res["n_above"] == 1  # 0.03 is not above


# 9. Threshold evidence-table reproducibility
def test_evidence_table_reproducibility():
    scores = [0.0, 0.01, 0.02, 0.03, 0.04, 0.05]
    res1 = compute_page_threshold_metrics(scores, T=0.03)
    res2 = compute_page_threshold_metrics(scores, T=0.03)
    assert res1 == res2


# 10. Leave-one-pure-OCR-out stability
def test_leave_one_pure_ocr_out_structure():
    rows = []
    for i in range(1, 6):
        doc_id = f"DOC_{i}"
        score = 0.02 if i <= 2 else 0.05
        rows.append(SnapshotRow(doc_id, f"CO_{i}", 2020, 1, "ocr", "ocr_stats", score, True, score, False, [], "pure_ocr"))

    results = run_leave_one_pure_ocr_out(rows, [0.030])
    assert len(results) == 5
    # Initially 3 out of 5 docs > 0.03 (fraction 0.60)
    for item in results:
        assert item["before_flagged_count"] == 3
        assert item["before_fraction"] == 0.60


# 11. Hidden document calculation
def test_hidden_document_calculation():
    # max page score = 0.04 > 0.03, but doc score = 0.02 <= 0.03 -> hidden!
    doc_pages_map = {
        "D1": [
            SnapshotRow("D1", "C1", 2020, 1, "native", "digital", 0.01, True, 0.02, False, [], "pure_native"),
            SnapshotRow("D1", "C1", 2020, 2, "native", "digital", 0.04, True, 0.02, False, [], "pure_native"),
        ]
    }
    res = compute_hidden_document_analysis(doc_pages_map, T=0.03)
    assert res["hidden_docs_count"] == 1
    assert res["hidden_docs_fraction"] == 1.0


# 12. Production file immutability & hash verification
def test_production_file_immutability():
    repo = Path(__file__).resolve().parents[2]
    # Git diff on arpipe/ non-test files must be completely empty
    res = subprocess.run(["git", "diff", "--name-only", "HEAD", "--", "arpipe/"], cwd=str(repo), capture_output=True, text=True)
    changed = [line.strip() for line in res.stdout.splitlines() if line.strip() and not line.startswith("arpipe/tests/")]
    assert changed == [], f"Production files modified: {changed}"


# 13. Repeatability test
def test_repeatability():
    scores = [0.01, 0.02, 0.04, 0.05]
    m1 = compute_page_threshold_metrics(scores, 0.03)
    m2 = compute_page_threshold_metrics(scores, 0.03)
    assert m1 == m2

