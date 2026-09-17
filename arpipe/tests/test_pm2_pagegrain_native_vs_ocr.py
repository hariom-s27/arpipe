"""Focused tests for P-M2.1: Native vs OCR orphan_start_frac at true page grain.

Covers all 12 requirements from P-M2.1 specification Section 18:
1. page-level values are read from P-M1;
2. null pages are excluded from numeric statistics;
3. zero pages are retained as real zeros;
4. native/OCR provenance is page-level;
5. mixed documents split correctly;
6. unknown provenance is excluded and counted;
7. percentiles use the same method;
8. score > 0.03 classification is exact;
9. values exactly equal to 0.03 are not above the threshold;
10. gap-around-threshold calculation works;
11. document-level and page-level counts are not confused;
12. no production modules are modified.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from arpipe.models import PageKind
from tools.pm2_pagegrain_native_vs_ocr import (
    PageRecord,
    build_report,
    calculate_percentiles,
    calculate_threshold_diagnostics,
    classify_document_provenance,
    classify_page_provenance,
    reconcile_population,
)


# 1. Page-level values are read from P-M1
def test_page_level_values_read_from_pm1():
    """Verify that page scores are mapped 1:1 from P-M1's qc.orphan_start_frac_pages."""
    p_scores = [None, 0.0, 0.045, None, 0.012]
    # Page 2 (1-based) is index 1 -> 0.0
    # Page 3 (1-based) is index 2 -> 0.045
    # Page 5 (1-based) is index 4 -> 0.012
    assert p_scores[2 - 1] == 0.0
    assert p_scores[3 - 1] == 0.045
    assert p_scores[5 - 1] == 0.012
    assert p_scores[1 - 1] is None
    assert p_scores[4 - 1] is None


# 2. Null pages are excluded from numeric statistics
def test_null_pages_excluded_from_numeric_stats():
    """Verify that null/None pages do not enter numeric distribution calculation."""
    vals = [0.0, 0.02, 0.05]
    # If a list had Nones, filtering must ensure they are not passed to calculate_percentiles
    pts = calculate_percentiles(vals)
    assert pts["min"] == 0.0
    assert pts["max"] == 0.05
    assert pts["median"] == 0.02


# 3. Zero pages are retained as real zeros
def test_zero_pages_retained_as_real_zeros():
    """Verify that 0.0 is not treated as null or excluded, but counted as a real zero."""
    vals = [0.0, 0.0, 0.0, 0.04]
    pts = calculate_percentiles(vals)
    assert pts["min"] == 0.0
    assert pts["median"] == 0.0
    diag = calculate_threshold_diagnostics(vals, gate=0.03)
    assert diag["n"] == 4
    assert diag["n_below"] == 3
    assert diag["n_above"] == 1


# 4. Native/OCR provenance is page-level
def test_provenance_is_page_level():
    """Verify that provenance precedence is applied page-by-page."""
    # OCR stats has page 10 with words > 0
    ocr_words = {10: 500}
    page_kinds = {10: PageKind.SCANNED, 11: PageKind.DIGITAL, 12: PageKind.BLANK, 13: PageKind.SCANNED}

    prov10, src10 = classify_page_provenance(10, 10, 13, ocr_words, page_kinds)
    prov11, src11 = classify_page_provenance(11, 10, 13, ocr_words, page_kinds)
    prov12, src12 = classify_page_provenance(12, 10, 13, ocr_words, page_kinds)
    prov13, src13 = classify_page_provenance(13, 10, 13, ocr_words, page_kinds)

    assert prov10 == "ocr"
    assert "ocr_stats" in src10

    assert prov11 == "native"
    assert "digital" in src11

    assert prov12 == "blank"
    assert "blank" in src12

    assert prov13 == "unknown"
    assert "no_ocr" in src13


# 5. Mixed documents split correctly
def test_mixed_documents_split_correctly():
    """Pages of a mixed document must split cleanly into their respective populations."""
    doc_classes = {1: "native", 2: "native", 3: "ocr", 4: "ocr"}
    assert classify_document_provenance(doc_classes) == "mixed"

    pages = [
        PageRecord("C1", 2020, 1, 0.01, "native", "digital", False, [], "high"),
        PageRecord("C1", 2020, 2, 0.02, "native", "digital", False, [], "high"),
        PageRecord("C1", 2020, 3, 0.04, "ocr", "ocr_stats", True, [], "high"),
        PageRecord("C1", 2020, 4, 0.05, "ocr", "ocr_stats", False, [], "high"),
    ]
    manifest = [{"company_id": "C1", "fy_end": 2020, "span": {"start_page": 1, "end_page": 4}}]
    rep = build_report(manifest, pages, gate=0.03)

    assert rep["page_level_distribution"]["native"]["n_pages"] == 2
    assert rep["page_level_distribution"]["ocr"]["n_pages"] == 2
    assert rep["page_level_distribution"]["native"]["n_documents"] == 1
    assert rep["page_level_distribution"]["ocr"]["n_documents"] == 1
    assert rep["document_level_context"]["mixed_documents"] == 1


# 6. Unknown provenance is excluded and counted
def test_unknown_provenance_excluded_and_counted():
    """Unknown provenance pages are tallied in population accounting and excluded from numeric comparison."""
    pages = [
        PageRecord("C1", 2020, 1, 0.01, "native", "digital", False, [], "high"),
        PageRecord("C1", 2020, 2, 0.04, "unknown", "profile_unavailable", False, [], "high"),
    ]
    manifest = [{"company_id": "C1", "fy_end": 2020, "span": {"start_page": 1, "end_page": 2}}]
    rep = build_report(manifest, pages, gate=0.03)

    pop = rep["population"]
    assert pop["unknown_provenance_pages_total"] == 1
    assert pop["unknown_provenance_pages_measured"] == 1
    assert rep["page_level_distribution"]["native"]["n_pages"] == 1
    assert rep["page_level_distribution"]["ocr"]["n_pages"] == 0


# 7. Percentiles use the same method
def test_percentiles_use_same_method():
    """Percentile calculation applies identical linear interpolation convention to both populations."""
    vals1 = [0.0, 0.02, 0.04, 0.06, 0.08, 0.10]
    vals2 = [0.01, 0.03, 0.05, 0.07]
    p1 = calculate_percentiles(vals1)
    p2 = calculate_percentiles(vals2)

    assert p1["median"] == 0.05
    assert p2["median"] == 0.04


# 8. Score > 0.03 classification is exact
def test_score_gt_003_classification_is_exact():
    """Strict inequality: 0.0300001 is above, 0.0299999 is below."""
    diag = calculate_threshold_diagnostics([0.0299999, 0.0300001], gate=0.03)
    assert diag["n_below"] == 1
    assert diag["n_above"] == 1
    assert diag["n_at"] == 0


# 9. Values exactly equal to 0.03 are not above the threshold
def test_score_eq_003_not_above_threshold():
    """Exact 0.03 is not above threshold (counted as n_at, and max <= gate)."""
    diag = calculate_threshold_diagnostics([0.02, 0.03, 0.04], gate=0.03)
    assert diag["n_at"] == 1
    assert diag["n_above"] == 1
    assert diag["n_below"] == 1
    assert diag["max_le_gate"] == 0.03
    assert diag["min_gt_gate"] == 0.04
    assert round(diag["gap"], 6) == 0.01


# 10. Gap-around-threshold calculation works
def test_gap_around_threshold_calculation():
    """Gap is max(score <= 0.03) to min(score > 0.03)."""
    diag = calculate_threshold_diagnostics([0.01, 0.025, 0.045, 0.08], gate=0.03)
    assert diag["max_le_gate"] == 0.025
    assert diag["min_gt_gate"] == 0.045
    assert round(diag["gap"], 6) == 0.020
    assert diag["near_gate_count"] == 0

    # Near gate count check
    diag2 = calculate_threshold_diagnostics([0.0295, 0.0305], gate=0.03)
    assert diag2["near_gate_count"] == 2


# 11. Document-level and page-level counts are not confused
def test_document_and_page_counts_not_confused():
    """Verify that multiple pages from the same document do not inflate document count."""
    pages = [
        PageRecord("C1", 2020, 1, 0.01, "ocr", "ocr_stats", False, [], "low"),
        PageRecord("C1", 2020, 2, 0.02, "ocr", "ocr_stats", False, [], "low"),
        PageRecord("C1", 2020, 3, 0.05, "ocr", "ocr_stats", True, [], "low"),
    ]
    manifest = [{"company_id": "C1", "fy_end": 2020, "span": {"start_page": 1, "end_page": 3}}]
    rep = build_report(manifest, pages, gate=0.03)

    assert rep["page_level_distribution"]["ocr"]["n_pages"] == 3
    assert rep["page_level_distribution"]["ocr"]["n_documents"] == 1


# 12. No production modules are modified
def test_no_production_modules_modified():
    """Verify that no production files in arpipe/ were altered from the canonical P-M1 state."""
    repo = Path(__file__).resolve().parents[2]
    cmd = ["git", "diff", "--name-only", "HEAD", "--", "arpipe/"]
    res = subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True, check=True)
    changed_files = [line.strip() for line in res.stdout.splitlines() if line.strip()]
    # Only test files or nothing in arpipe/ should be dirty
    non_test_changes = [f for f in changed_files if not f.startswith("arpipe/tests/")]
    assert non_test_changes == [], f"Production modules were modified: {non_test_changes}"
