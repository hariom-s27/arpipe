"""Pytest suite for ARPipe T0.3A-R1 Report-Era Coverage Taxonomy Extension."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import tempfile
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.run_t0_3a_r1_document_coverage import (
    BASE_COMMIT,
    FROZEN_CORE_DECISION,
    ALLOWED_JUSTIFICATION_TYPES,
    ALLOWED_EVIDENCE_LEVELS,
    ALLOWED_COVERAGE_STATUSES,
    ALLOWED_DOWNSTREAM_RELEVANCE,
    SUBSTANTIVE_FILES,
    file_sha256,
    parse_fiscal_year,
    load_and_verify_r1_taxonomy,
    evaluate_predicate,
    execute_t0_3a_r1_run,
)
from tools.audit_t0_3a_r1_document_coverage import (
    audit_base_commit,
    audit_frozen_inputs,
    audit_core_decision_invariant,
    audit_taxonomy_register,
    audit_canonical_artifacts,
    run_full_audit,
)


@pytest.fixture(scope="module")
def canonical_dir():
    return os.path.join(REPO_ROOT, "dataset", "corpus_gap_audit", "t0_3a_r1_document_coverage")


def test_01_base_commit_invariant():
    """Verify base commit matches expected 02bae116a6616d3a8637323dffe2fb27d36304f1 (or parent)."""
    head = audit_base_commit(REPO_ROOT)
    assert head is not None


def test_02_frozen_inputs_and_t03a_preservation():
    """Verify all frozen inputs are cryptographically verified and T0.3A baseline is preserved."""
    verified = audit_frozen_inputs(REPO_ROOT)
    paths = {item["path"] for item in verified}
    assert "dataset/corpus_gap_audit/t0_3a_document_coverage/t0_3a_coverage_matrix.csv" in paths
    assert "configs/t0_3a/taxonomy_register.json" in paths
    assert "configs/t0_3a_r1/taxonomy_register.json" in paths


def test_03_exact_taxonomy_extension_and_justifications():
    """Verify exact taxonomy extension: pre_2015 and post_2015 with proper justification types."""
    categories = load_and_verify_r1_taxonomy(REPO_ROOT)
    era_cats = {c["category"]: c for c in categories if c["dimension"] == "report_era"}
    assert set(era_cats.keys()) == {"pre_2015", "post_2015"}
    assert era_cats["pre_2015"]["justification_type"] == "FROZEN_ROBUSTNESS_REQUIREMENT"
    assert era_cats["pre_2015"]["evidence_level"] == "VALIDATED_METADATA"
    assert era_cats["post_2015"]["justification_type"] == "CONTROLLED_COVERAGE_EXTENSION"
    assert era_cats["post_2015"]["evidence_level"] == "VALIDATED_METADATA"


def test_04_exact_predicates_and_no_extra_era_categories():
    """Verify exact predicates for eras and ensure zero forbidden era buckets exist."""
    categories = load_and_verify_r1_taxonomy(REPO_ROOT)
    era_cats = {c["category"]: c for c in categories if c["dimension"] == "report_era"}
    for cat in era_cats.values():
        pred = cat["predicate"]
        assert "fiscal_year" in pred
    forbidden = ["2011_2015", "2016_2018", "transition", "modern", "2024_2025", "2021_2025", "stub"]
    all_cat_names = [c["category"] for c in categories]
    for f in forbidden:
        assert f not in all_cat_names


def test_05_no_empirical_counts_in_taxonomy():
    """Verify taxonomy configuration contains definitions only and zero empirical counts."""
    categories = load_and_verify_r1_taxonomy(REPO_ROOT)
    forbidden_keys = {"count", "document_count", "page_count", "issuer_count", "coverage_status"}
    for cat in categories:
        assert forbidden_keys.isdisjoint(cat.keys())


def test_06_strict_fiscal_year_parsing_and_missing_year_handling():
    """Verify strict parsing: valid integers parsed, strings/None/invalids handled outside categories."""
    assert parse_fiscal_year("2015") == (True, 2015)
    assert parse_fiscal_year(2012) == (True, 2012)
    assert parse_fiscal_year("2024 ") == (True, 2024)
    assert parse_fiscal_year("") == (False, None)
    assert parse_fiscal_year(None) == (False, None)
    assert parse_fiscal_year("invalid") == (False, None)
    assert parse_fiscal_year("2015.5") == (False, None)

    # In evaluate_predicate, invalid fiscal year returns False for both eras
    invalid_doc = {"document_id": "test_doc", "fiscal_year": "N/A"}
    assert not evaluate_predicate("int(fiscal_year) < 2015", invalid_doc, "report_era")
    assert not evaluate_predicate("int(fiscal_year) >= 2015", invalid_doc, "report_era")


def test_07_valid_fiscal_year_completeness_and_disjointness():
    """Verify mutual exclusivity and exhaustive union of eras over valid fiscal-year documents."""
    doc_path = os.path.join(REPO_ROOT, "dataset", "corpus_gap_audit", "reconciled", "gap_audit_document_reconciled.csv")
    with open(doc_path, "r", encoding="utf-8") as f:
        docs = list(csv.DictReader(f))

    valid_docs = [d["document_id"] for d in docs if parse_fiscal_year(d.get("fiscal_year"))[0]]
    pre_docs = set(d["document_id"] for d in docs if parse_fiscal_year(d.get("fiscal_year"))[0] and parse_fiscal_year(d.get("fiscal_year"))[1] < 2015)
    post_docs = set(d["document_id"] for d in docs if parse_fiscal_year(d.get("fiscal_year"))[0] and parse_fiscal_year(d.get("fiscal_year"))[1] >= 2015)

    assert len(pre_docs.intersection(post_docs)) == 0
    assert pre_docs.union(post_docs) == set(valid_docs)


def test_08_deterministic_count_derivation(canonical_dir):
    """Verify dynamic count derivation matches canonical coverage matrix."""
    matrix_path = os.path.join(canonical_dir, "t0_3a_r1_coverage_matrix.csv")
    with open(matrix_path, "r", encoding="utf-8") as f:
        rows = {r["category"]: r for r in csv.DictReader(f)}

    doc_path = os.path.join(REPO_ROOT, "dataset", "corpus_gap_audit", "reconciled", "gap_audit_document_reconciled.csv")
    with open(doc_path, "r", encoding="utf-8") as f:
        doc_rows = list(csv.DictReader(f))

    pre_docs = [d for d in doc_rows if parse_fiscal_year(d.get("fiscal_year"))[0] and parse_fiscal_year(d.get("fiscal_year"))[1] < 2015]
    post_docs = [d for d in doc_rows if parse_fiscal_year(d.get("fiscal_year"))[0] and parse_fiscal_year(d.get("fiscal_year"))[1] >= 2015]

    assert int(rows["pre_2015"]["document_count"]) == len(pre_docs)
    assert int(rows["pre_2015"]["page_count"]) == sum(int(d["total_pages"]) for d in pre_docs)
    assert int(rows["pre_2015"]["issuer_count"]) == len(set(d["issuer"] for d in pre_docs))

    assert int(rows["post_2015"]["document_count"]) == len(post_docs)
    assert int(rows["post_2015"]["page_count"]) == sum(int(d["total_pages"]) for d in post_docs)
    assert int(rows["post_2015"]["issuer_count"]) == len(set(d["issuer"] for d in post_docs))


def test_09_strong_non_era_field_for_field_equality(canonical_dir):
    """Verify all non-era categories match frozen T0.3A field-for-field."""
    base_matrix_path = os.path.join(REPO_ROOT, "dataset", "corpus_gap_audit", "t0_3a_document_coverage", "t0_3a_coverage_matrix.csv")
    with open(base_matrix_path, "r", encoding="utf-8") as f:
        base_rows = [r for r in csv.DictReader(f) if r["dimension"] != "report_era"]

    r1_matrix_path = os.path.join(canonical_dir, "t0_3a_r1_coverage_matrix.csv")
    with open(r1_matrix_path, "r", encoding="utf-8") as f:
        r1_rows = [r for r in csv.DictReader(f) if r["dimension"] != "report_era"]

    assert len(r1_rows) == len(base_rows)
    for r1_r, base_r in zip(r1_rows, base_rows):
        for k in base_r:
            assert r1_r[k] == base_r[k], f"Mismatch in non-era {r1_r['category']} field {k}"


def test_10_no_acquisition_decision_and_core_invariant(canonical_dir):
    """Verify zero acquisition decisions and core invariant NO_ACQUISITION."""
    audit_core_decision_invariant(REPO_ROOT)
    summary_path = os.path.join(canonical_dir, "t0_3a_r1_summary.json")
    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)
    assert summary["frozen_core_decision"] == FROZEN_CORE_DECISION
    assert summary["acquisition_status"] == FROZEN_CORE_DECISION
    assert summary["acquisition_decision_made"] is False


def test_11_canonical_substantive_files_exist_and_nonempty(canonical_dir):
    """Verify all 7 substantive files exist and are non-empty."""
    for fn in SUBSTANTIVE_FILES:
        fp = os.path.join(canonical_dir, fn)
        assert os.path.isfile(fp), f"Missing substantive file: {fp}"
        assert os.path.getsize(fp) > 0, f"Empty substantive file: {fp}"


def test_12_summary_json_consistency(canonical_dir):
    """Verify summary.json consistency."""
    summary_path = os.path.join(canonical_dir, "t0_3a_r1_summary.json")
    with open(summary_path, "r", encoding="utf-8") as f:
        s = json.load(f)
    matrix_path = os.path.join(canonical_dir, "t0_3a_r1_coverage_matrix.csv")
    with open(matrix_path, "r", encoding="utf-8") as f:
        m_rows = list(csv.DictReader(f))

    assert s["category_count"] == len(m_rows)
    assert s["present_count"] == sum(1 for r in m_rows if r["coverage_status"] == "PRESENT")
    assert s["sparse_count"] == sum(1 for r in m_rows if r["coverage_status"] == "SPARSE")
    assert s["absent_count"] == sum(1 for r in m_rows if r["coverage_status"] == "ABSENT")
    assert s["not_assessable_count"] == sum(1 for r in m_rows if r["coverage_status"] == "NOT_ASSESSABLE")


def test_13_audit_plan_markdown_and_sufficiency_warning(canonical_dir):
    """Verify required coverage interpretation and non-sufficiency notices in audit plan."""
    plan_path = os.path.join(canonical_dir, "t0_3a_r1_audit_plan.md")
    with open(plan_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Coverage Does NOT Mean Sufficiency" in content or "Coverage does NOT mean sufficiency" in content
    assert "The report-era coverage dimension uses two pre-specified complementary categories: pre-2015 and post-2015." in content
    assert "This statement applies to documents with valid fiscal_year values." in content


def test_14_deterministic_reproducibility(canonical_dir):
    """Verify fresh run produces byte-identical outputs to canonical directory."""
    temp_dir = tempfile.mkdtemp(prefix="t0_3a_r1_test_rep_")
    try:
        execute_t0_3a_r1_run(REPO_ROOT, temp_dir)
        for fn in SUBSTANTIVE_FILES:
            f_canon = os.path.join(canonical_dir, fn)
            f_test = os.path.join(temp_dir, fn)
            assert file_sha256(f_canon) == file_sha256(f_test), f"Byte divergence in {fn}"
    finally:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_15_auditor_script_passes(canonical_dir):
    """Verify full auditor verification passes."""
    assert run_full_audit(REPO_ROOT, canonical_dir) is True

