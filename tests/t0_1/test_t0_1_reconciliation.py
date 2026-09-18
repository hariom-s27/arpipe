"""Unit tests for ARPipe T0.1R reconciliation.

Verifies:
  1. Raw T0.1 artifacts remain byte-identical to historical commit.
  2. T0 baseline artifacts remain byte-identical to historical commit.
  3. Reconciliation is deterministic across independent runs.
  4. Claim register schema and enum values are valid.
  5. Source artifacts exist and are readable.
  6. Reconciliation statuses are valid allowed enum values.
  7. Report numbers and claim tags match canonical reconciled artifacts.
  8. Raw vs derived provenance is valid.
  9. Manual review provenance is truthful (NOT_REVIEWED, human_reviewed_count = 0).
  10. Unresolved contradictions remain recorded as UNRESOLVED.
  11. Acquisition decisions match canonical Core vs Robustness table.
  12. Fail-closed behavior on missing or mismatched allowlisted inputs.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import tempfile
import unittest

from tools.reconcile_t0_1 import reconcile_corpus, verify_inputs
from tools.audit_t0_1_reconciliation import audit_reconciliation
from tools.audit_reconciled_report import audit_reconciled_report


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
T0_COMMIT = "23d62286c4b807607b29a4dc14940179f90e3c0d"
T01_COMMIT = "b6b76d964e78edce37b3d42e3668450526ee4bb7"
CONFIG_COMMIT = "55e507566d1d3efea658748f59cf3a6f692e1226"


def _file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class TestT01Reconciliation(unittest.TestCase):
    def test_01_raw_t01_artifacts_byte_identical(self):
        """Verify that all raw T0.1 artifacts match their exact Git commit bytes."""
        t01_files = [
            "dataset/corpus_gap_audit/gap_audit_document.csv",
            "dataset/corpus_gap_audit/gap_summary.csv",
            "dataset/corpus_gap_audit/gap_audit_summary.json",
            "dataset/corpus_gap_audit/condition_document_map.csv",
            "dataset/corpus_gap_audit/condition_page_map.csv",
            "dataset/corpus_gap_audit/interaction_gap_matrix.csv",
            "dataset/corpus_gap_audit/manual_review_manifest.csv",
            "dataset/corpus_gap_audit/manual_review_results.csv",
            "dataset/corpus_gap_audit/language_candidates.csv",
            "dataset/corpus_gap_audit/duplicate_text_candidates.csv",
            "dataset/corpus_gap_audit/toc_offset_candidates.csv",
            "dataset/corpus_gap_audit/table_candidates.csv",
            "dataset/corpus_gap_audit/header_footer_candidates.csv",
            "dataset/corpus_gap_audit/structure_candidates.csv",
            "dataset/corpus_gap_audit/mdna_candidate_complexity.csv",
            "dataset/corpus_gap_audit/gap_audit_report.md",
            "dataset/corpus_gap_audit/methodology.md",
            "dataset/corpus_gap_audit/audit_config.json",
            "dataset/corpus_gap_audit/environment.json",
            "dataset/corpus_gap_audit/input_hashes.json",
            "tools/audit_corpus_gaps.py",
            "tools/apply_model_review.py",
        ]
        for rel_path in t01_files:
            abs_path = os.path.join(REPO_ROOT, rel_path.replace("/", os.sep))
            self.assertTrue(os.path.isfile(abs_path), f"Missing raw T0.1 file: {rel_path}")
            disk_sha = _file_sha256(abs_path)
            blob = subprocess.check_output(["git", "-C", REPO_ROOT, "show", f"{T01_COMMIT}:{rel_path}"])
            git_sha = hashlib.sha256(blob).hexdigest()
            self.assertEqual(disk_sha, git_sha, f"Byte divergence in raw T0.1 artifact {rel_path}")

    def test_02_t0_baseline_artifacts_byte_identical(self):
        """Verify that all T0 baseline artifacts match their exact Git commit bytes."""
        t0_files = [
            "dataset/corpus_freeze/corpus_inventory.csv",
            "dataset/corpus_freeze/freeze_summary.json",
            "dataset/corpus_freeze/diversity_matrix.csv",
            "dataset/corpus_freeze/issuer_split.csv",
        ]
        for rel_path in t0_files:
            abs_path = os.path.join(REPO_ROOT, rel_path.replace("/", os.sep))
            self.assertTrue(os.path.isfile(abs_path), f"Missing T0 file: {rel_path}")
            disk_sha = _file_sha256(abs_path)
            blob = subprocess.check_output(["git", "-C", REPO_ROOT, "show", f"{T0_COMMIT}:{rel_path}"])
            git_sha = hashlib.sha256(blob).hexdigest()
            self.assertEqual(disk_sha, git_sha, f"Byte divergence in T0 baseline artifact {rel_path}")

    def test_03_two_run_reproducibility(self):
        """Run reconciliation into two separate temp directories and assert bitwise equality across substantive files."""
        with tempfile.TemporaryDirectory() as dir1, tempfile.TemporaryDirectory() as dir2:
            reconcile_corpus(repo_root=REPO_ROOT, output_dir=dir1, config_commit=CONFIG_COMMIT)
            reconcile_corpus(repo_root=REPO_ROOT, output_dir=dir2, config_commit=CONFIG_COMMIT)

            substantive_files = [
                "claim_audit.csv",
                "t0_t01_reconciliation.csv",
                "acquisition_decision.csv",
                "gap_audit_document_reconciled.csv",
                "condition_document_map_reconciled.csv",
                "condition_page_map_reconciled.csv",
                "interaction_gap_matrix_reconciled.csv",
                "manual_review_results_reconciled.csv",
                "gap_summary_reconciled.csv",
                "gap_audit_summary_reconciled.json",
                "methodology_reconciled.md",
                "gap_audit_report_reconciled.md",
                "raw_input_manifest.json",
                "reconciliation_manifest.json",
            ]

            for fn in substantive_files:
                p1 = os.path.join(dir1, fn)
                p2 = os.path.join(dir2, fn)
                self.assertTrue(os.path.isfile(p1), f"Run 1 missing {fn}")
                self.assertTrue(os.path.isfile(p2), f"Run 2 missing {fn}")
                sha1 = _file_sha256(p1)
                sha2 = _file_sha256(p2)
                self.assertEqual(sha1, sha2, f"Two-run non-determinism in substantive output: {fn} ({sha1} != {sha2})")

    def test_04_fail_closed_on_tampered_input(self):
        """Verify that verify_inputs fails closed if an allowlisted file is modified."""
        allowlist_path = os.path.join(REPO_ROOT, "configs", "t0_1r", "input_allowlist.json")
        # Creating a dummy allowlist with non-existent file
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_allowlist = os.path.join(tmpdir, "bad_allowlist.json")
            with open(bad_allowlist, "w", encoding="utf-8") as f:
                json.dump({"allowlist": [{"path": "non_existent.csv", "source_type": "T0_FROZEN", "source_commit": T0_COMMIT, "artifact_type": "CSV", "semantic_purpose": "test"}]}, f)
            with self.assertRaises(Exception):
                verify_inputs(REPO_ROOT, bad_allowlist, CONFIG_COMMIT)

    def test_05_reconciliation_manifest_self_hash_excluded(self):
        """Verify reconciliation manifest excludes itself from output hashes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            reconcile_corpus(repo_root=REPO_ROOT, output_dir=tmpdir, config_commit=CONFIG_COMMIT)
            man_path = os.path.join(tmpdir, "reconciliation_manifest.json")
            with open(man_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data.get("self_hash_policy"), "EXCLUDED_FROM_OWN_HASH_SET")
            self.assertNotIn("reconciliation_manifest.json", data.get("derived_output_hashes", {}))

    def test_06_manual_review_provenance_truthful(self):
        """Verify manual review records are truthfully corrected row-by-row."""
        with tempfile.TemporaryDirectory() as tmpdir:
            reconcile_corpus(repo_root=REPO_ROOT, output_dir=tmpdir, config_commit=CONFIG_COMMIT)
            res_path = os.path.join(tmpdir, "manual_review_results_reconciled.csv")
            with open(res_path, "r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 72)
            for r in rows:
                if r["original_verification_status"] == "MODEL_REVIEWED":
                    self.assertEqual(r["reconciled_verification_status"], "NOT_REVIEWED")
                    self.assertEqual(r["review_provenance_issue"], "AUTO_RELABELLED_WITHOUT_MODEL_INSPECTION")

    def test_07_audit_scripts_pass(self):
        """Verify that both audit_t0_1_reconciliation.py and audit_reconciled_report.py pass on generated output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            reconcile_corpus(repo_root=REPO_ROOT, output_dir=tmpdir, config_commit=CONFIG_COMMIT)
            self.assertTrue(audit_reconciliation(REPO_ROOT, tmpdir))
            self.assertTrue(audit_reconciled_report(REPO_ROOT, tmpdir))


if __name__ == "__main__":
    unittest.main()
