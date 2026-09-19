"""Unit tests for ARPipe T0.3A Scanned/Document-Type Coverage Audit.

Tests:
  1. Base-commit invariant (ef2e8c5c17a753fc133c66272e4ad755ab26e5a4).
  2. Cryptographic verification of frozen inputs.
  3. Frozen core-thesis decision invariant (NO_ACQUISITION).
  4. Taxonomy register schema, allowed types, and absence of hardcoded counts.
  5. Removal of arbitrary era buckets (pre_2015 and post_2015 only).
  6. Script and language proxies (no unevidenced english_monolingual).
  7. Proper naming: no_toc_keyword_candidate.
  8. Layout and structure / coverage interactions separation.
  9. Evidence limitations dimension: unmeasured properties with NOT_ASSESSABLE status.
  10. Evidence-based sparsity without invented numeric thresholds.
  11. Canonical substantive files presence and validity.
  12. Dynamic derivation of coverage matrix counts via predicates.
  13. Category document mapping consistency.
  14. Gap register validity (zero acquisition columns).
  15. Summary JSON schema and count consistency.
  16. Mandatory unresolved questions statement and sufficiency notice.
  17. Deterministic two-run byte-for-byte reproducibility.
  18. Auditor script full execution pass.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.run_t0_3a_document_coverage import (
    BASE_COMMIT,
    FROZEN_CORE_DECISION,
    ALLOWED_JUSTIFICATION_TYPES,
    ALLOWED_EVIDENCE_LEVELS,
    ALLOWED_COVERAGE_STATUSES,
    ALLOWED_DOWNSTREAM_RELEVANCE,
    execute_t0_3a_run,
    load_taxonomy_register,
    evaluate_predicate,
    verify_base_commit,
    verify_frozen_inputs,
    check_core_decision_invariant,
)
from tools.audit_t0_3a_document_coverage import (
    run_full_audit,
    audit_base_commit,
    audit_frozen_inputs,
    audit_core_decision_invariant,
    audit_taxonomy_register,
    audit_canonical_artifacts,
)


def _file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class TestT03ADocumentCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canonical_dir = os.path.join(REPO_ROOT, "dataset", "corpus_gap_audit", "t0_3a_document_coverage")
        cls.test_dir = tempfile.mkdtemp(prefix="t0_3a_test_run_")
        execute_t0_3a_run(REPO_ROOT, cls.test_dir)

    def test_01_base_commit_invariant(self):
        head = audit_base_commit(REPO_ROOT)
        self.assertEqual(head, BASE_COMMIT)

    def test_02_frozen_inputs_manifest_integrity(self):
        verified_inputs = audit_frozen_inputs(REPO_ROOT)
        self.assertGreaterEqual(len(verified_inputs), 12)
        manifest_path = os.path.join(self.canonical_dir, "t0_3a_immutable_input_manifest.json")
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
        manifest_shas = {item["path"]: item["sha256"] for item in manifest_data.get("inputs", [])}
        for item in verified_inputs:
            self.assertIn(item["path"], manifest_shas)
            self.assertEqual(item["sha256"], manifest_shas[item["path"]])

    def test_03_core_decision_invariant(self):
        audit_core_decision_invariant(REPO_ROOT)
        summary_path = os.path.join(self.canonical_dir, "t0_3a_summary.json")
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)
        self.assertEqual(summary["frozen_core_decision"], FROZEN_CORE_DECISION)
        self.assertEqual(summary["acquisition_status"], FROZEN_CORE_DECISION)
        self.assertFalse(summary["acquisition_decision_made"])

    def test_04_taxonomy_register_frozen_integrity(self):
        categories = audit_taxonomy_register(REPO_ROOT)
        self.assertGreater(len(categories), 20)
        forbidden_keys = {"count", "document_count", "page_count", "issuer_count", "coverage_status"}
        for cat in categories:
            self.assertIn(cat["justification_type"], ALLOWED_JUSTIFICATION_TYPES)
            self.assertIn(cat["evidence_level"], ALLOWED_EVIDENCE_LEVELS)
            self.assertTrue(set(cat.keys()).isdisjoint(forbidden_keys))

    def test_05_no_arbitrary_era_buckets(self):
        categories = load_taxonomy_register(REPO_ROOT)
        era_cats = [c["category"] for c in categories if c["dimension"] == "report_era"]
        self.assertEqual(set(era_cats), {"pre_2015", "post_2015"})
        for forbidden in ["pre_2010_historical", "historical_2011_2015", "transition_2017_2018", "modern_2024_2025"]:
            self.assertNotIn(forbidden, era_cats)

    def test_06_script_and_language_candidates(self):
        categories = load_taxonomy_register(REPO_ROOT)
        lang_cats = {c["category"]: c for c in categories if c["dimension"] == "language_script"}
        self.assertIn("devanagari_candidate", lang_cats)
        self.assertIn("bilingual_candidate", lang_cats)
        self.assertIn("no_devanagari_candidate", lang_cats)
        self.assertIn("devanagari_in_fit_or_validation", lang_cats)
        self.assertNotIn("english_monolingual", lang_cats)
        for c in lang_cats.values():
            self.assertEqual(c["evidence_level"], "CANDIDATE_PROXY")

    def test_07_no_toc_keyword_candidate_naming(self):
        categories = load_taxonomy_register(REPO_ROOT)
        cat_names = [c["category"] for c in categories]
        self.assertIn("no_toc_keyword_candidate", cat_names)
        self.assertNotIn("toc_absent", cat_names)

    def test_08_coverage_intersections_dimension(self):
        categories = load_taxonomy_register(REPO_ROOT)
        intersections = {c["category"]: c for c in categories if c["dimension"] == "coverage_intersections"}
        self.assertIn("scanned_with_multi_column", intersections)
        self.assertIn("scanned_with_table_candidate", intersections)
        for c in intersections.values():
            self.assertEqual(c["evidence_level"], "DERIVED_INTERACTION")

    def test_09_evidence_limitations_dimension(self):
        categories = load_taxonomy_register(REPO_ROOT)
        limitations = {c["category"]: c for c in categories if c["dimension"] == "evidence_limitations"}
        self.assertIn("ocr_transcription_quality", limitations)
        self.assertIn("scanned_heading_localization_error", limitations)
        for c in limitations.values():
            self.assertEqual(c["evidence_level"], "UNMEASURED")
            self.assertEqual(c["predicate"], "NONE")

    def test_10_evidence_based_sparsity(self):
        matrix_path = os.path.join(self.canonical_dir, "t0_3a_coverage_matrix.csv")
        with open(matrix_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        sparse_cats = {r["category"] for r in rows if r["coverage_status"] == "SPARSE"}
        expected_sparse = {
            "scanned",
            "fully_scanned_document",
            "devanagari_candidate",
            "bilingual_candidate",
            "hidden_text_candidate",
            "stub_filing",
        }
        self.assertEqual(sparse_cats, expected_sparse)

    def test_11_substantive_files_exist_and_nonempty(self):
        expected_files = [
            "t0_3a_immutable_input_manifest.json",
            "t0_3a_coverage_matrix.csv",
            "t0_3a_category_document_map.csv",
            "t0_3a_gap_register.csv",
            "t0_3a_summary.json",
            "t0_3a_audit_plan.md",
        ]
        for fn in expected_files:
            fp = os.path.join(self.canonical_dir, fn)
            self.assertTrue(os.path.isfile(fp), f"Missing file {fp}")
            self.assertGreater(os.path.getsize(fp), 0, f"Empty file {fp}")

    def test_12_coverage_matrix_derived_dynamically(self):
        doc_path = os.path.join(REPO_ROOT, "dataset", "corpus_gap_audit", "reconciled", "gap_audit_document_reconciled.csv")
        with open(doc_path, "r", encoding="utf-8") as f:
            doc_rows = list(csv.DictReader(f))

        matrix_path = os.path.join(self.canonical_dir, "t0_3a_coverage_matrix.csv")
        with open(matrix_path, "r", encoding="utf-8") as f:
            matrix_rows = list(csv.DictReader(f))

        categories = load_taxonomy_register(REPO_ROOT)
        cat_map = {c["category"]: c for c in categories}

        for r in matrix_rows:
            c_name = r["category"]
            cat = cat_map[c_name]
            pred = cat["predicate"]
            if pred == "NONE":
                self.assertEqual(int(r["document_count"]), 0)
                self.assertEqual(r["coverage_status"], "NOT_ASSESSABLE")
            else:
                matching = [d for d in doc_rows if evaluate_predicate(pred, d)]
                self.assertEqual(int(r["document_count"]), len(matching))
                self.assertEqual(int(r["page_count"]), sum(int(d["total_pages"]) for d in matching))
                self.assertEqual(int(r["issuer_count"]), len(set(d["issuer"] for d in matching)))
                self.assertEqual(int(r["fit_count"]), sum(1 for d in matching if d["split"] == "FIT"))
                self.assertEqual(int(r["validation_count"]), sum(1 for d in matching if d["split"] == "VALIDATION"))
                self.assertEqual(int(r["holdout_count"]), sum(1 for d in matching if d["split"] == "HOLDOUT"))

    def test_13_category_document_map_integrity(self):
        map_path = os.path.join(self.canonical_dir, "t0_3a_category_document_map.csv")
        with open(map_path, "r", encoding="utf-8") as f:
            map_rows = list(csv.DictReader(f))

        matrix_path = os.path.join(self.canonical_dir, "t0_3a_coverage_matrix.csv")
        with open(matrix_path, "r", encoding="utf-8") as f:
            matrix_rows = list(csv.DictReader(f))

        counts_in_map = {}
        for mr in map_rows:
            key = (mr["dimension"], mr["category"])
            counts_in_map[key] = counts_in_map.get(key, 0) + 1

        for r in matrix_rows:
            key = (r["dimension"], r["category"])
            expected = int(r["document_count"])
            actual = counts_in_map.get(key, 0)
            self.assertEqual(actual, expected, f"Mismatch for {key}")

    def test_14_gap_register_zero_acquisition_fields(self):
        gap_path = os.path.join(self.canonical_dir, "t0_3a_gap_register.csv")
        with open(gap_path, "r", encoding="utf-8") as f:
            gap_rows = list(csv.DictReader(f))

        forbidden = {"acquisition_required_now", "acquisition_recommendation", "recommended_action"}
        for r in gap_rows:
            self.assertTrue(set(r.keys()).isdisjoint(forbidden))
            self.assertIn(r["downstream_relevance"], ALLOWED_DOWNSTREAM_RELEVANCE)
            self.assertIn(r["coverage_status"], ALLOWED_COVERAGE_STATUSES)
            self.assertIn(r["evidence_level"], ALLOWED_EVIDENCE_LEVELS)

    def test_15_summary_json_consistency(self):
        summary_path = os.path.join(self.canonical_dir, "t0_3a_summary.json")
        with open(summary_path, "r", encoding="utf-8") as f:
            s = json.load(f)
        matrix_path = os.path.join(self.canonical_dir, "t0_3a_coverage_matrix.csv")
        with open(matrix_path, "r", encoding="utf-8") as f:
            matrix_rows = list(csv.DictReader(f))

        present = sum(1 for r in matrix_rows if r["coverage_status"] == "PRESENT")
        sparse = sum(1 for r in matrix_rows if r["coverage_status"] == "SPARSE")
        absent = sum(1 for r in matrix_rows if r["coverage_status"] == "ABSENT")
        not_assessable = sum(1 for r in matrix_rows if r["coverage_status"] == "NOT_ASSESSABLE")

        self.assertEqual(s["present_count"], present)
        self.assertEqual(s["sparse_count"], sparse)
        self.assertEqual(s["absent_count"], absent)
        self.assertEqual(s["not_assessable_count"], not_assessable)
        self.assertEqual(s["category_count"], len(matrix_rows))

    def test_16_mandatory_unresolved_questions_and_sufficiency_warning(self):
        plan_path = os.path.join(self.canonical_dir, "t0_3a_audit_plan.md")
        with open(plan_path, "r", encoding="utf-8") as f:
            plan = f.read()

        expected_statement = (
            "No implementation-blocking questions remain. OCR quality, heading-localization performance, "
            "and other unmeasured properties remain intentionally unresolved because T0.3A is a coverage audit rather than a performance benchmark."
        )
        self.assertIn(expected_statement, plan)
        self.assertTrue("Coverage does NOT mean sufficiency" in plan or "Coverage Does NOT Mean Sufficiency" in plan)

    def test_17_deterministic_reproducibility(self):
        substantive = [
            "t0_3a_immutable_input_manifest.json",
            "t0_3a_coverage_matrix.csv",
            "t0_3a_category_document_map.csv",
            "t0_3a_gap_register.csv",
            "t0_3a_summary.json",
            "t0_3a_audit_plan.md",
        ]
        for fn in substantive:
            f_canon = os.path.join(self.canonical_dir, fn)
            f_test = os.path.join(self.test_dir, fn)
            self.assertEqual(_file_sha256(f_canon), _file_sha256(f_test), f"Byte divergence in {fn}")

    def test_18_audit_script_passes(self):
        self.assertTrue(run_full_audit(REPO_ROOT, self.canonical_dir))


if __name__ == "__main__":
    unittest.main()
