import os
import tempfile
import csv
import pytest

from arpipe import evaluate


def test_compute_boundary_iou():
    # Exact match
    assert evaluate.compute_boundary_iou((10, 20), (10, 20)) == 1.0
    # Both None (correct rejection of non-existent section)
    assert evaluate.compute_boundary_iou(None, None) == 1.0
    # One None
    assert evaluate.compute_boundary_iou((10, 20), None) == 0.0
    assert evaluate.compute_boundary_iou(None, (10, 20)) == 0.0
    # Disjoint
    assert evaluate.compute_boundary_iou((10, 20), (25, 30)) == 0.0
    # Partial: [10..20] (11 pgs) and [15..25] (11 pgs) -> inter: [15..20] (6 pgs), union: [10..25] (16 pgs)
    assert evaluate.compute_boundary_iou((10, 20), (15, 25)) == round(6 / 16, 4)


def test_compute_pk_and_windowdiff_exact():
    total_pages = 100
    span = (20, 35)
    # Perfect match must yield 0 penalty
    assert evaluate.compute_pk(total_pages, span, span) == 0.0
    assert evaluate.compute_windowdiff(total_pages, span, span) == 0.0

    # None vs None must also yield 0 penalty
    assert evaluate.compute_pk(total_pages, None, None) == 0.0
    assert evaluate.compute_windowdiff(total_pages, None, None) == 0.0


def test_compute_pk_and_windowdiff_penalties():
    total_pages = 100
    true_span = (20, 35)
    pred_span = (50, 65)

    pk = evaluate.compute_pk(total_pages, true_span, pred_span)
    wd = evaluate.compute_windowdiff(total_pages, true_span, pred_span)
    assert pk > 0.0
    assert wd > 0.0
    assert pk <= 1.0
    assert wd <= 1.0


def test_check_start_accuracy():
    assert evaluate.check_start_accuracy((10, 20), (10, 20)) == (True, True, True)
    assert evaluate.check_start_accuracy((10, 20), (11, 20)) == (False, True, True)
    assert evaluate.check_start_accuracy((10, 20), (12, 20)) == (False, False, True)
    assert evaluate.check_start_accuracy((10, 20), (15, 20)) == (False, False, False)
    assert evaluate.check_start_accuracy(None, None) == (True, True, True)
    assert evaluate.check_start_accuracy((10, 20), None) == (False, False, False)


def test_end_to_end_evaluate():
    with tempfile.TemporaryDirectory() as td:
        labels_csv = os.path.join(td, "labels.csv")
        report_md = os.path.join(td, "eval_report.md")

        with open(labels_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "sha256", "company_id", "cin", "fy_end", "doc_kind", "cap_band",
                "exchange", "total_pages", "proposed_start", "proposed_end",
                "true_start", "true_end", "reason_code", "labeller", "labelled_at",
                "verified_by"
            ])
            # Row 1: Exact OK
            writer.writerow(["sha1", "C1", "", "2012", "digital", "large", "both", "100", "10", "20", "10", "20", "OK", "user", "", "read_pdf"])
            # Row 2: Off by 1 (WRONG_START)
            writer.writerow(["sha2", "C2", "", "2013", "scanned", "micro", "bse", "50", "11", "20", "10", "20", "WRONG_START", "user", "", "read_pdf"])
            # Row 3: Missing in doc
            writer.writerow(["sha3", "C3", "", "2020", "digital", "mid", "both", "80", "", "", "", "", "NO_MDA_IN_DOC", "user", "", "read_pdf"])

        ret = evaluate.evaluate_file(labels_csv, report_md)
        assert ret == 0
        assert os.path.exists(report_md)
        content = open(report_md, encoding="utf-8").read()
        assert "# Evaluation Report" in content
        assert "Exact Start Accuracy" in content
        assert "Start Within 1 Page" in content
        assert "Per-Method Precision" in content
        assert "Supporter Calibration" in content


def test_evaluate_excludes_unverified_rows():
    with tempfile.TemporaryDirectory() as td:
        labels_csv = os.path.join(td, "labels.csv")

        with open(labels_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "sha256", "company_id", "cin", "fy_end", "doc_kind", "cap_band",
                "exchange", "total_pages", "proposed_start", "proposed_end",
                "true_start", "true_end", "reason_code", "labeller", "labelled_at",
                "verified_by"
            ])
            # Row 1: read_pdf -> included
            writer.writerow(["sha1", "C1", "", "2012", "digital", "large", "both", "100", "10", "20", "10", "20", "OK", "user", "", "read_pdf"])
            # Row 2: unknown -> excluded
            writer.writerow(["sha2", "C2", "", "2013", "scanned", "micro", "bse", "50", "11", "20", "10", "20", "WRONG_START", "user", "", "unknown"])
            # Row 3: copied_from_run -> excluded
            writer.writerow(["sha3", "C3", "", "2014", "digital", "mid", "both", "80", "5", "10", "5", "10", "OK", "user", "", "copied_from_run"])
            # Row 4: empty verified_by -> excluded
            writer.writerow(["sha4", "C4", "", "2015", "digital", "mid", "both", "80", "5", "10", "5", "10", "OK", "user", "", ""])

        res = evaluate.evaluate_labels(labels_csv, dataset_roots=[])
        assert res["n"] == 1
        assert res["overall"]["exact_start"] == 1.0


def test_log_holdout_access():
    with tempfile.TemporaryDirectory() as td:
        log_path = os.path.join(td, "eval_holdout_log.csv")
        warn = evaluate.log_holdout_access(split="holdout", log_path=log_path)
        assert "WARNING: Scoring holdout set" in warn
        assert os.path.exists(log_path)
        with open(log_path, encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == 2  # header + 1 row
            assert "holdout" in lines[1]


