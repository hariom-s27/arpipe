"""Unit tests for ARPipe T0.2 Robustness-Gate Decision Audit.

Tests:
  1. Base-commit invariant (879762a2f236b3aaa6df33b7ddacc60c01d633c1).
  2. Cryptographic verification of frozen T0.1R inputs.
  3. Complete derivation of ADDITIONAL_AUDIT_REQUIRED rows without hard-coding.
  4. No condition omission or extra unexplained conditions.
  5. Claim dependency completeness and source calculation ID resolution.
  6. Uncertainty enum validity.
  7. Decision enum validity.
  8. Trigger-state consistency (trigger_executed == FALSE -> acquisition_currently_justified == FALSE).
  9. TARGETED_ACQUISITION_JUSTIFIED forbidden when trigger is unexecuted.
  10. Threshold-basis validation (no invented numbers without frozen basis).
  11. Sample-size justification validation (no invented sample sizes).
  12. Frozen core-thesis decision invariant (NO_ACQUISITION).
  13. T0.2 deterministic reproducibility (independent runs match byte-for-byte).
  14. Audit script passes with zero errors.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import tempfile
import unittest

from tools.run_t0_2_robustness_gate import (
    BASE_COMMIT,
    FROZEN_CORE_DECISION,
    ALLOWED_UNCERTAINTY_TYPES,
    ALLOWED_DECISION_VALUES,
    ALLOWED_THRESHOLD_STATUSES,
    run_t0_2,
    derive_additional_audit_conditions,
    verify_frozen_inputs,
    verify_base_commit,
    check_core_decision_invariant,
)
from tools.audit_t0_2_robustness_gate import audit_t0_2

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class TestT02RobustnessGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp(prefix="t0_2_test_")
        run_t0_2(REPO_ROOT, cls.test_dir)

    def test_01_base_commit_invariant(self):
        """1. Verify that base commit matches exact frozen T0.1R SHA."""
        head = subprocess.check_output(
            ["git", "-C", REPO_ROOT, "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
        self.assertEqual(head, BASE_COMMIT, f"Base commit mismatch: expected {BASE_COMMIT}, got {head}")

    def test_02_frozen_input_hash_verification(self):
        """2. Verify that all consumed frozen T0.1R inputs match their cryptographic hashes."""
        inputs = verify_frozen_inputs(REPO_ROOT)
        self.assertGreater(len(inputs), 0)
        for item in inputs:
            full_path = os.path.join(REPO_ROOT, item["path"].replace("/", os.sep))
            self.assertTrue(os.path.isfile(full_path), f"Frozen input missing: {item['path']}")
            disk_sha = _file_sha256(full_path)
            self.assertEqual(disk_sha, item["sha256"], f"Hash mismatch for {item['path']}")

    def test_03_complete_derivation_of_additional_audit_rows(self):
        """3. Verify that conditions are dynamically derived from acquisition_decision.csv."""
        derived = derive_additional_audit_conditions(REPO_ROOT)
        self.assertGreater(len(derived), 0)
        for r in derived:
            self.assertEqual(r["acquisition_status"], "ADDITIONAL_AUDIT_REQUIRED")
        derived_names = [r["condition"] for r in derived]
        self.assertIn("duplicate_overlapping_text", derived_names)
        self.assertIn("toc_offset_discrepancy", derived_names)
        self.assertIn("fully_scanned_documents", derived_names)

    def test_04_no_condition_omission_or_extra(self):
        """4. Verify gate rows match derived ADDITIONAL_AUDIT_REQUIRED rows exactly."""
        derived = derive_additional_audit_conditions(REPO_ROOT)
        derived_conditions = set(r["condition"] for r in derived)

        gate_csv_path = os.path.join(self.test_dir, "t0_2_robustness_gate.csv")
        self.assertTrue(os.path.isfile(gate_csv_path))
        with open(gate_csv_path, "r", encoding="utf-8") as f:
            gate_rows = list(csv.DictReader(f))

        gate_conditions = set(r["condition"] for r in gate_rows)
        self.assertEqual(gate_conditions, derived_conditions, "Condition set mismatch between gate and source")
        self.assertEqual(len(gate_rows), len(derived))

    def test_05_claim_dependency_completeness(self):
        """5. Verify that claim dependency map resolves valid claims and calculations."""
        dep_csv_path = os.path.join(self.test_dir, "t0_2_claim_dependency_map.csv")
        self.assertTrue(os.path.isfile(dep_csv_path))
        with open(dep_csv_path, "r", encoding="utf-8") as f:
            dep_rows = list(csv.DictReader(f))

        claim_audit_path = os.path.join(REPO_ROOT, "dataset", "corpus_gap_audit", "reconciled", "claim_audit.csv")
        valid_claims = set()
        valid_calc_ids = set()
        with open(claim_audit_path, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                valid_claims.add(r["claim_id"])
                cid = r.get("source_calculation_id")
                if cid and r.get("source_calculation"):
                    valid_calc_ids.add(cid)

        calc_rules_path = os.path.join(REPO_ROOT, "configs", "t0_1r", "reconciliation_rules.json")
        with open(calc_rules_path, "r", encoding="utf-8") as f:
            valid_calc_ids.update(json.load(f).get("claim_calculation_rules", {}).keys())

        for r in dep_rows:
            self.assertIn(r["claim_id"], valid_claims, f"Unknown claim: {r['claim_id']}")
            if r.get("source_calculation_id"):
                self.assertIn(r["source_calculation_id"], valid_calc_ids, f"Unknown calculation: {r['source_calculation_id']}")

    def test_06_uncertainty_enum_validity(self):
        """6. Verify all uncertainty_type values belong to allowed enum set."""
        gate_csv_path = os.path.join(self.test_dir, "t0_2_robustness_gate.csv")
        with open(gate_csv_path, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                self.assertIn(
                    r["uncertainty_type"],
                    ALLOWED_UNCERTAINTY_TYPES,
                    f"Invalid uncertainty_type in row {r['condition']}: {r['uncertainty_type']}"
                )

    def test_07_decision_enum_validity(self):
        """7. Verify all audit_decision values belong to allowed enum set."""
        gate_csv_path = os.path.join(self.test_dir, "t0_2_robustness_gate.csv")
        with open(gate_csv_path, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                self.assertIn(
                    r["audit_decision"],
                    ALLOWED_DECISION_VALUES,
                    f"Invalid audit_decision in row {r['condition']}: {r['audit_decision']}"
                )

    def test_08_trigger_state_consistency(self):
        """8. Verify trigger consistency: unexecuted trigger cannot justify acquisition."""
        gate_csv_path = os.path.join(self.test_dir, "t0_2_robustness_gate.csv")
        with open(gate_csv_path, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("trigger_executed") == "FALSE":
                    self.assertEqual(
                        r.get("acquisition_currently_justified"),
                        "FALSE",
                        f"Row {r['condition']} has unexecuted trigger but claims acquisition justified!"
                    )
                    self.assertEqual(
                        r.get("trigger_result"),
                        "NOT_EXECUTED",
                        f"Row {r['condition']} has trigger_executed=FALSE but trigger_result={r.get('trigger_result')}"
                    )

    def test_09_targeted_acquisition_forbidden_when_unexecuted(self):
        """9. Verify TARGETED_ACQUISITION_JUSTIFIED is forbidden when trigger is unexecuted."""
        gate_csv_path = os.path.join(self.test_dir, "t0_2_robustness_gate.csv")
        with open(gate_csv_path, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("audit_decision") == "TARGETED_ACQUISITION_JUSTIFIED":
                    self.assertEqual(
                        r.get("trigger_executed"),
                        "TRUE",
                        f"Row {r['condition']} illegally declared TARGETED_ACQUISITION_JUSTIFIED while trigger was unexecuted"
                    )

    def test_10_threshold_basis_validation(self):
        """10. Verify that no numeric threshold is invented without frozen basis."""
        gate_csv_path = os.path.join(self.test_dir, "t0_2_robustness_gate.csv")
        with open(gate_csv_path, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                t_val = r.get("threshold_value")
                t_status = r.get("threshold_status")
                self.assertIn(t_status, ALLOWED_THRESHOLD_STATUSES)
                if t_status == "TO_BE_SPECIFIED_BEFORE_EXECUTION":
                    self.assertEqual(t_val, "TO_BE_SPECIFIED_BEFORE_EXECUTION")

    def test_11_sample_size_justification_validation(self):
        """11. Verify that no arbitrary sample size is invented."""
        gate_csv_path = os.path.join(self.test_dir, "t0_2_robustness_gate.csv")
        with open(gate_csv_path, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                s_size = r.get("minimum_sample_size")
                self.assertIn(
                    s_size,
                    ("NONE", "TO_BE_SPECIFIED_BEFORE_ACQUISITION"),
                    f"Ungrounded sample size in row {r['condition']}: {s_size}"
                )

    def test_12_core_decision_invariant(self):
        """12. Verify frozen core-thesis decision invariant (NO_ACQUISITION)."""
        check_core_decision_invariant(REPO_ROOT)
        summary_path = os.path.join(self.test_dir, "t0_2_summary.json")
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)
        self.assertEqual(summary.get("frozen_core_decision"), FROZEN_CORE_DECISION)
        self.assertEqual(summary.get("core_decision_invariant_status"), "PRESERVED")

    def test_13_deterministic_reproducibility(self):
        """13. Verify byte-for-byte reproducibility across independent runs."""
        run1_dir = tempfile.mkdtemp(prefix="t0_2_run1_")
        run2_dir = tempfile.mkdtemp(prefix="t0_2_run2_")

        run_t0_2(REPO_ROOT, run1_dir)
        run_t0_2(REPO_ROOT, run2_dir)

        files = [
            "t0_2_immutable_input_manifest.json",
            "t0_2_robustness_gate.csv",
            "t0_2_claim_dependency_map.csv",
            "t0_2_audit_trace.csv",
            "t0_2_decision_register.csv",
            "t0_2_acquisition_triggers.json",
            "t0_2_summary.json",
            "t0_2_audit_plan.md"
        ]

        for fn in files:
            f1 = os.path.join(run1_dir, fn)
            f2 = os.path.join(run2_dir, fn)
            self.assertTrue(os.path.isfile(f1), f"Missing file in run1: {fn}")
            self.assertTrue(os.path.isfile(f2), f"Missing file in run2: {fn}")

            sha1 = _file_sha256(f1)
            sha2 = _file_sha256(f2)
            self.assertEqual(sha1, sha2, f"Byte divergence in {fn} between run1 and run2")

    def test_14_audit_script_passes(self):
        """14. Verify audit_t0_2_robustness_gate.py passes cleanly."""
        success = audit_t0_2(REPO_ROOT, self.test_dir)
        self.assertTrue(success, "Audit tool reported violations in T0.2 package")


if __name__ == "__main__":
    unittest.main()
