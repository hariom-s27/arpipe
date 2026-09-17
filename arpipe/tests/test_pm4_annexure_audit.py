import csv
import hashlib
import json
import os
import subprocess
import pytest

from tools import pm4_annexure_audit


def test_gate_verification():
    gate_info = pm4_annexure_audit.verify_base_gate()
    assert gate_info["base_commit"] == pm4_annexure_audit.EXPECTED_BASE_COMMIT
    assert gate_info["holdout_labels_inspected"] == "NO"
    assert gate_info["holdout_outcomes_inspected"] == "NO"
    assert gate_info["holdout_membership_unchanged"] == "YES"


def test_split_file_hashes():
    for filename, expected_hash in pm4_annexure_audit.EXPECTED_SPLIT_HASHES.items():
        assert os.path.exists(filename), f"Missing split file: {filename}"
        h = pm4_annexure_audit.compute_sha256(filename)
        assert h == expected_hash, f"Hash mismatch for {filename}"


def test_audit_execution_and_population_counts():
    data = pm4_annexure_audit.run_audit()
    pop = data["population_counts"]
    assert pop["all_fit_labelled"] == 20
    assert pop["fit_queue_unlabelled"] == 92
    assert pop["total_fit_pool"] == 112
    assert pop["eligible_documents"] == 18
    assert pop["excluded_documents"] == 2

    # Exactly 20 records
    assert len(data["records"]) == 20

    # Every eligible record has valid true_start_page
    eligible = [r for r in data["records"] if r["is_eligible"]]
    assert len(eligible) == 18
    for r in eligible:
        assert isinstance(r["true_start_page"], int)
        assert r["heading_form"] in pm4_annexure_audit.HEADING_FORMS


def test_table_a_math():
    data = pm4_annexure_audit.run_audit()
    table_a = data["table_a"]
    total_n = sum(r["N"] for r in table_a)
    assert total_n == 18
    total_pct = sum(r["percentage"] for r in table_a)
    assert round(total_pct, 1) == 100.0

    counts = {r["heading_form"]: r["N"] for r in table_a}
    assert counts["standalone_heading"] == 12
    assert counts["annexure_labelled"] == 3
    assert counts["combined_with_directors_report"] == 1
    assert counts["other"] == 2


def test_table_b_cap_bands_and_screen():
    data = pm4_annexure_audit.run_audit()
    table_b = data["table_b"]
    assert len(table_b) == 4
    band_names = [b["cap_band"] for b in table_b]
    assert band_names == ["large", "mid", "small", "micro"]

    # Table D screen
    td = data["table_d"]
    assert td["max_cap_band_annexure_fraction"] == 50.0  # mid cap
    assert td["min_cap_band_annexure_fraction"] == 12.5  # large and micro
    assert td["absolute_difference_pp"] == 37.5
    assert td["screen_flag"] is True
    assert "PROMINENT SYSTEMATIC-BIAS SIGNAL" in td["verdict"]


def test_table_c_eras():
    data = pm4_annexure_audit.run_audit()
    table_c = data["table_c"]
    assert len(table_c) == 3
    eras = [e["era"] for e in table_c]
    assert eras == ["2010-2013", "2014-2018", "2019-2025"]

    c_map = {e["era"]: e["N"] for e in table_c}
    assert c_map["2010-2013"] == 13
    assert c_map["2014-2018"] == 5
    assert c_map["2019-2025"] == 0


def test_table_e_accuracy_descriptive():
    data = pm4_annexure_audit.run_audit()
    table_e = data["table_e"]
    e_map = {r["heading_form"]: r for r in table_e}

    # standalone: 11/12
    assert e_map["standalone_heading"]["exact_start_correct"] == 11
    assert e_map["standalone_heading"]["N"] == 12
    assert e_map["standalone_heading"]["exact_start_accuracy"] == 91.67

    # annexure: 2/3
    assert e_map["annexure_labelled"]["exact_start_correct"] == 2
    assert e_map["annexure_labelled"]["N"] == 3
    assert e_map["annexure_labelled"]["exact_start_accuracy"] == 66.67
    assert e_map["annexure_labelled"]["descriptive_only"] is True


def test_reproducibility_run_twice():
    """Run audit twice and assert bit-for-bit identical outputs."""
    # First execution
    data1 = pm4_annexure_audit.run_audit()
    pm4_annexure_audit.export_reports(data1)

    files_to_check = [
        "reports/annexure_audit.json",
        "reports/annexure_audit.md",
        "reports/annexure_audit_accuracy.csv",
        "reports/annexure_audit_by_cap_band.csv",
        "reports/annexure_audit_by_era.csv",
        "reports/annexure_audit_document_labels.csv",
    ]
    hashes1 = {f: pm4_annexure_audit.compute_sha256(f) for f in files_to_check}

    # Second execution
    data2 = pm4_annexure_audit.run_audit()
    pm4_annexure_audit.export_reports(data2)
    hashes2 = {f: pm4_annexure_audit.compute_sha256(f) for f in files_to_check}

    for f in files_to_check:
        assert hashes1[f] == hashes2[f], f"Reproducibility failure on {f}"


def test_production_immutability():
    """Verify that protected production files are unmodified."""
    protected_files = [
        "arpipe/segment.py",
        "arpipe/patterns.py",
        "arpipe/pipeline.py",
        "arpipe/verify.py",
        "arpipe/triage.py",
        "arpipe/ocr.py",
        "arpipe/models.py",
    ]
    res = subprocess.run(
        ["git", "diff", "--name-only", pm4_annexure_audit.EXPECTED_BASE_COMMIT, "--"] + protected_files,
        capture_output=True,
        text=True,
    )
    diff_files = [f.strip() for f in res.stdout.splitlines() if f.strip()]
    assert len(diff_files) == 0, f"Protected production files were modified: {diff_files}"
