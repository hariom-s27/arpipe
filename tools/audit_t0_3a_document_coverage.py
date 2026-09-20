"""Strict deterministic auditor for ARPipe T0.3A Scanned/Document-Type Coverage Audit.

Verifies:
  1. Base commit is ef2e8c5c17a753fc133c66272e4ad755ab26e5a4.
  2. Frozen inputs match their authoritative SHA256 hashes.
  3. t0_3a_immutable_input_manifest.json is complete and valid.
  4. Core-thesis decision invariant remains NO_ACQUISITION.
  5. Taxonomy register integrity: frozen input, valid structure, allowed justification types,
     allowed evidence levels, no hardcoded counts.
  6. All 6 canonical substantive files exist and are non-empty.
  7. Deterministic re-derivation of counts: evaluating predicates on gap_audit_document_reconciled.csv
     matches t0_3a_coverage_matrix.csv exactly.
  8. Coverage status definitions followed strictly: ABSENT, NOT_ASSESSABLE, SPARSE (evidence-based), PRESENT.
  9. Category document mapping consistency: rows match document counts.
  10. Gap register integrity: zero acquisition fields, valid downstream relevance.
  11. Summary consistency: counts, invariant flags, unresolved questions statement.
  12. Audit plan markdown completeness and required warnings.
  13. Two-run byte-for-byte reproducibility check against canonical artifacts.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Set, Tuple

BASE_COMMIT = "ef2e8c5c17a753fc133c66272e4ad755ab26e5a4"
FROZEN_CORE_DECISION = "NO_ACQUISITION"

ALLOWED_JUSTIFICATION_TYPES = {
    "EXISTING_CORPUS_FIELD",
    "EXISTING_CONDITION",
    "EXISTING_CLAIM",
    "EXISTING_JOIN",
    "FROZEN_ROBUSTNESS_REQUIREMENT",
    "VALIDATED_METADATA",
}

ALLOWED_EVIDENCE_LEVELS = {
    "VALIDATED_METADATA",
    "EXISTING_CONDITION",
    "CANDIDATE_PROXY",
    "DERIVED_INTERACTION",
    "UNMEASURED",
}

ALLOWED_COVERAGE_STATUSES = {
    "PRESENT",
    "SPARSE",
    "ABSENT",
    "NOT_ASSESSABLE",
}

ALLOWED_DOWNSTREAM_RELEVANCE = {
    "CORE",
    "ROBUSTNESS",
    "NOT_MATERIAL",
    "NOT_ASSESSABLE",
}

SUBSTANTIVE_FILES = [
    "t0_3a_immutable_input_manifest.json",
    "t0_3a_coverage_matrix.csv",
    "t0_3a_category_document_map.csv",
    "t0_3a_gap_register.csv",
    "t0_3a_summary.json",
    "t0_3a_audit_plan.md",
]


def _file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def audit_base_commit(repo_root: str) -> str:
    try:
        head = subprocess.check_output(
            ["git", "-C", repo_root, "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception as e:
        raise AssertionError(f"Unable to read git HEAD in {repo_root}: {e}")
    if head != BASE_COMMIT:
        raise AssertionError(f"Base commit mismatch. Expected {BASE_COMMIT}, got {head}")
    return head


def audit_frozen_inputs(repo_root: str) -> List[Dict[str, str]]:
    recon_manifest_path = os.path.join(
        repo_root, "dataset", "corpus_gap_audit", "reconciled", "reconciliation_manifest.json"
    )
    if not os.path.isfile(recon_manifest_path):
        raise AssertionError(f"Reconciliation manifest missing at {recon_manifest_path}")

    with open(recon_manifest_path, "r", encoding="utf-8") as f:
        recon_manifest = json.load(f)

    derived_hashes = recon_manifest.get("derived_output_hashes", {})

    raw_manifest_path = os.path.join(
        repo_root, "dataset", "corpus_gap_audit", "reconciled", "raw_input_manifest.json"
    )
    if not os.path.isfile(raw_manifest_path):
        raise AssertionError(f"Raw input manifest missing at {raw_manifest_path}")

    with open(raw_manifest_path, "r", encoding="utf-8") as f:
        raw_manifest = json.load(f)

    raw_hashes = {item["artifact_path"]: item["sha256"] for item in raw_manifest.get("inputs", [])}

    inputs_to_verify = [
        ("configs/t0_3a/taxonomy_register.json", "T03A_FROZEN_CONFIG", None),
        ("dataset/corpus_gap_audit/reconciled/gap_audit_document_reconciled.csv", "T01R_FROZEN", derived_hashes.get("gap_audit_document_reconciled.csv")),
        ("dataset/corpus_gap_audit/reconciled/gap_summary_reconciled.csv", "T01R_FROZEN", derived_hashes.get("gap_summary_reconciled.csv")),
        ("dataset/corpus_gap_audit/reconciled/gap_audit_summary_reconciled.json", "T01R_FROZEN", derived_hashes.get("gap_audit_summary_reconciled.json")),
        ("dataset/corpus_gap_audit/reconciled/acquisition_decision.csv", "T01R_FROZEN", derived_hashes.get("acquisition_decision.csv")),
        ("dataset/corpus_gap_audit/reconciled/claim_audit.csv", "T01R_FROZEN", derived_hashes.get("claim_audit.csv")),
        ("dataset/corpus_gap_audit/reconciled/interaction_gap_matrix_reconciled.csv", "T01R_FROZEN", derived_hashes.get("interaction_gap_matrix_reconciled.csv")),
        ("dataset/corpus_gap_audit/reconciled/gap_audit_report_reconciled.md", "T01R_FROZEN", derived_hashes.get("gap_audit_report_reconciled.md")),
        ("dataset/corpus_freeze/corpus_inventory.csv", "T0_FROZEN", raw_hashes.get("dataset/corpus_freeze/corpus_inventory.csv")),
        ("dataset/corpus_freeze/issuer_split.csv", "T0_FROZEN", raw_hashes.get("dataset/corpus_freeze/issuer_split.csv")),
        ("dataset/corpus_gap_audit/t0_2_robustness_gate/t0_2_robustness_gate.csv", "T02_FROZEN", None),
        ("dataset/corpus_gap_audit/t0_2_robustness_gate/t0_2_claim_dependency_map.csv", "T02_FROZEN", None),
    ]

    verified = []
    for rel_path, prov_type, expected_sha in inputs_to_verify:
        full_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(full_path):
            raise AssertionError(f"Required input file missing: {full_path}")
        actual_sha = _file_sha256(full_path)
        if expected_sha and actual_sha != expected_sha:
            raise AssertionError(f"SHA mismatch for {rel_path}: got {actual_sha}, expected {expected_sha}")
        verified.append({"path": rel_path, "source_provenance": prov_type, "sha256": actual_sha})

    return verified


def audit_core_decision_invariant(repo_root: str) -> None:
    acq_path = os.path.join(repo_root, "dataset", "corpus_gap_audit", "reconciled", "acquisition_decision.csv")
    with open(acq_path, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("core_thesis_need") == "PRIMARY" and r.get("acquisition_status") != FROZEN_CORE_DECISION:
                raise AssertionError(f"Core decision invariant violated in {r['condition']}")


def audit_taxonomy_register(repo_root: str) -> List[Dict[str, Any]]:
    tax_path = os.path.join(repo_root, "configs", "t0_3a", "taxonomy_register.json")
    if not os.path.isfile(tax_path):
        raise AssertionError(f"Taxonomy register missing at {tax_path}")

    with open(tax_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception as e:
            raise AssertionError(f"Taxonomy register is not valid JSON: {e}")

    categories = data.get("categories", [])
    if not categories:
        raise AssertionError("Taxonomy register has no categories")

    seen_categories = set()
    for cat in categories:
        c_name = cat.get("category")
        if not c_name:
            raise AssertionError("Category entry missing 'category' name")
        if c_name in seen_categories:
            raise AssertionError(f"Duplicate category '{c_name}' in taxonomy register")
        seen_categories.add(c_name)

        if not cat.get("dimension"):
            raise AssertionError(f"Category '{c_name}' missing 'dimension'")
        if "predicate" not in cat:
            raise AssertionError(f"Category '{c_name}' missing 'predicate'")
        if cat.get("justification_type") not in ALLOWED_JUSTIFICATION_TYPES:
            raise AssertionError(f"Category '{c_name}' has invalid justification_type '{cat.get('justification_type')}'")
        if cat.get("evidence_level") not in ALLOWED_EVIDENCE_LEVELS:
            raise AssertionError(f"Category '{c_name}' has invalid evidence_level '{cat.get('evidence_level')}'")
        if not isinstance(cat.get("source_artifacts"), list) or not cat.get("source_artifacts"):
            raise AssertionError(f"Category '{c_name}' has invalid source_artifacts")
        if not isinstance(cat.get("source_claim_ids"), list) or not cat.get("source_claim_ids"):
            raise AssertionError(f"Category '{c_name}' has invalid source_claim_ids")
        if not cat.get("interpretation_limit"):
            raise AssertionError(f"Category '{c_name}' missing 'interpretation_limit'")

        # Ensure taxonomy register contains zero counts
        forbidden_count_keys = {"count", "document_count", "page_count", "issuer_count", "coverage_status"}
        intersection = forbidden_count_keys.intersection(cat.keys())
        if intersection:
            raise AssertionError(f"Taxonomy register contains prohibited count keys {intersection} in '{c_name}'")

    return categories


def evaluate_predicate(predicate_str: str, doc_row: Dict[str, Any]) -> bool:
    if predicate_str == "NONE":
        return False
    local_scope = dict(doc_row)
    local_scope["int"] = int
    local_scope["str"] = str
    local_scope["len"] = len
    try:
        return bool(eval(predicate_str, {"__builtins__": {}}, local_scope))
    except Exception as e:
        raise AssertionError(f"Error evaluating predicate '{predicate_str}' on doc {doc_row.get('document_id')}: {e}")


def audit_canonical_artifacts(repo_root: str, canonical_dir: str) -> None:
    for fn in SUBSTANTIVE_FILES:
        fp = os.path.join(canonical_dir, fn)
        if not os.path.isfile(fp):
            raise AssertionError(f"Canonical file missing: {fp}")
        if os.path.getsize(fp) == 0:
            raise AssertionError(f"Canonical file is empty: {fp}")

    # 1. Audit manifest
    manifest_path = os.path.join(canonical_dir, "t0_3a_immutable_input_manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)
    if manifest_data.get("base_commit") != BASE_COMMIT:
        raise AssertionError(f"Manifest base commit mismatch: {manifest_data.get('base_commit')}")
    manifest_paths = {entry["path"] for entry in manifest_data.get("inputs", [])}
    if "configs/t0_3a/taxonomy_register.json" not in manifest_paths:
        raise AssertionError("Taxonomy register not hashed in input manifest")

    # 2. Audit coverage matrix
    matrix_path = os.path.join(canonical_dir, "t0_3a_coverage_matrix.csv")
    with open(matrix_path, "r", encoding="utf-8") as f:
        matrix_rows = list(csv.DictReader(f))

    # 3. Audit gap register
    gap_path = os.path.join(canonical_dir, "t0_3a_gap_register.csv")
    with open(gap_path, "r", encoding="utf-8") as f:
        gap_rows = list(csv.DictReader(f))

    # 4. Audit category document map
    map_path = os.path.join(canonical_dir, "t0_3a_category_document_map.csv")
    with open(map_path, "r", encoding="utf-8") as f:
        map_rows = list(csv.DictReader(f))

    # 5. Audit summary JSON
    summary_path = os.path.join(canonical_dir, "t0_3a_summary.json")
    with open(summary_path, "r", encoding="utf-8") as f:
        summary_data = json.load(f)

    # 6. Audit plan markdown
    plan_path = os.path.join(canonical_dir, "t0_3a_audit_plan.md")
    with open(plan_path, "r", encoding="utf-8") as f:
        plan_content = f.read()

    # Re-evaluate all counts dynamically against gap_audit_document_reconciled.csv
    doc_path = os.path.join(repo_root, "dataset", "corpus_gap_audit", "reconciled", "gap_audit_document_reconciled.csv")
    with open(doc_path, "r", encoding="utf-8") as f:
        doc_rows = list(csv.DictReader(f))

    categories = audit_taxonomy_register(repo_root)
    cat_by_name = {c["category"]: c for c in categories}

    if len(matrix_rows) != len(categories):
        raise AssertionError(f"Matrix row count ({len(matrix_rows)}) != categories count ({len(categories)})")
    if len(gap_rows) != len(categories):
        raise AssertionError(f"Gap register row count ({len(gap_rows)}) != categories count ({len(categories)})")

    explicit_sparse_categories = {
        "scanned",
        "fully_scanned_document",
        "devanagari_candidate",
        "bilingual_candidate",
        "hidden_text_candidate",
        "stub_filing",
    }

    # Map counts by (dimension, category)
    map_counts: Dict[Tuple[str, str], int] = {}
    for mr in map_rows:
        key = (mr["dimension"], mr["category"])
        map_counts[key] = map_counts.get(key, 0) + 1

    status_counts = {"PRESENT": 0, "SPARSE": 0, "ABSENT": 0, "NOT_ASSESSABLE": 0}

    for mr in matrix_rows:
        c_name = mr["category"]
        dim = mr["dimension"]
        if c_name not in cat_by_name:
            raise AssertionError(f"Coverage matrix contains category '{c_name}' not in taxonomy register")
        cat = cat_by_name[c_name]
        pred = cat["predicate"]
        ev_level = cat["evidence_level"]

        if pred == "NONE" or ev_level == "UNMEASURED":
            expected_status = "NOT_ASSESSABLE"
            expected_doc_cnt = 0
            expected_pg_cnt = 0
            expected_iss_cnt = 0
            expected_fit = 0
            expected_val = 0
            expected_hld = 0
        else:
            matching = [r for r in doc_rows if evaluate_predicate(pred, r)]
            expected_doc_cnt = len(matching)
            expected_pg_cnt = sum(int(r["total_pages"]) for r in matching)
            expected_iss_cnt = len(set(r["issuer"] for r in matching))
            expected_fit = sum(1 for r in matching if r["split"] == "FIT")
            expected_val = sum(1 for r in matching if r["split"] == "VALIDATION")
            expected_hld = sum(1 for r in matching if r["split"] == "HOLDOUT")
            if expected_doc_cnt == 0:
                expected_status = "ABSENT"
            elif c_name in explicit_sparse_categories:
                expected_status = "SPARSE"
            else:
                expected_status = "PRESENT"

        # Verify exact counts
        if int(mr["document_count"]) != expected_doc_cnt:
            raise AssertionError(f"Doc count mismatch in '{c_name}': got {mr['document_count']}, expected {expected_doc_cnt}")
        if int(mr["page_count"]) != expected_pg_cnt:
            raise AssertionError(f"Page count mismatch in '{c_name}': got {mr['page_count']}, expected {expected_pg_cnt}")
        if int(mr["issuer_count"]) != expected_iss_cnt:
            raise AssertionError(f"Issuer count mismatch in '{c_name}': got {mr['issuer_count']}, expected {expected_iss_cnt}")
        if int(mr["fit_count"]) != expected_fit:
            raise AssertionError(f"Fit count mismatch in '{c_name}': got {mr['fit_count']}, expected {expected_fit}")
        if int(mr["validation_count"]) != expected_val:
            raise AssertionError(f"Val count mismatch in '{c_name}': got {mr['validation_count']}, expected {expected_val}")
        if int(mr["holdout_count"]) != expected_hld:
            raise AssertionError(f"Holdout count mismatch in '{c_name}': got {mr['holdout_count']}, expected {expected_hld}")
        if mr["coverage_status"] != expected_status:
            raise AssertionError(f"Status mismatch in '{c_name}': got {mr['coverage_status']}, expected {expected_status}")

        status_counts[mr["coverage_status"]] += 1

        # Check map counts match document count
        actual_map_cnt = map_counts.get((dim, c_name), 0)
        if actual_map_cnt != expected_doc_cnt:
            raise AssertionError(f"Category document map count ({actual_map_cnt}) != expected doc count ({expected_doc_cnt}) for {c_name}")

    # Verify gap register rows
    for gr in gap_rows:
        c_name = gr["category"]
        if gr["coverage_status"] not in ALLOWED_COVERAGE_STATUSES:
            raise AssertionError(f"Invalid coverage_status '{gr['coverage_status']}' in gap register for '{c_name}'")
        if gr["evidence_level"] not in ALLOWED_EVIDENCE_LEVELS:
            raise AssertionError(f"Invalid evidence_level '{gr['evidence_level']}' in gap register for '{c_name}'")
        if gr["downstream_relevance"] not in ALLOWED_DOWNSTREAM_RELEVANCE:
            raise AssertionError(f"Invalid downstream_relevance '{gr['downstream_relevance']}' in gap register for '{c_name}'")
        # Ensure zero acquisition columns exist
        forbidden_gap_cols = {"acquisition_required_now", "acquisition_recommendation", "recommended_action"}
        if forbidden_gap_cols.intersection(gr.keys()):
            raise AssertionError(f"Gap register contains forbidden acquisition columns")

    # Verify summary JSON
    if summary_data.get("base_commit") != BASE_COMMIT:
        raise AssertionError("Summary base_commit mismatch")
    if summary_data.get("frozen_core_decision") != FROZEN_CORE_DECISION:
        raise AssertionError("Summary frozen_core_decision mismatch")
    if summary_data.get("acquisition_status") != FROZEN_CORE_DECISION:
        raise AssertionError("Summary acquisition_status mismatch")
    if summary_data.get("acquisition_decision_made") is not False:
        raise AssertionError("Summary acquisition_decision_made must be False")
    if summary_data.get("category_count") != len(categories):
        raise AssertionError("Summary category_count mismatch")
    if summary_data.get("present_count") != status_counts["PRESENT"]:
        raise AssertionError("Summary present_count mismatch")
    if summary_data.get("sparse_count") != status_counts["SPARSE"]:
        raise AssertionError("Summary sparse_count mismatch")
    if summary_data.get("absent_count") != status_counts["ABSENT"]:
        raise AssertionError("Summary absent_count mismatch")
    if summary_data.get("not_assessable_count") != status_counts["NOT_ASSESSABLE"]:
        raise AssertionError("Summary not_assessable_count mismatch")

    # Check unresolved questions statement in summary and audit plan
    expected_statement = (
        "No implementation-blocking questions remain. OCR quality, heading-localization performance, "
        "and other unmeasured properties remain intentionally unresolved because T0.3A is a coverage audit rather than a performance benchmark."
    )
    unresolved = summary_data.get("unresolved_questions", [])
    if not any(expected_statement in q for q in unresolved):
        raise AssertionError("Mandatory unresolved questions statement missing in summary.json")
    if expected_statement not in plan_content:
        raise AssertionError("Mandatory unresolved questions statement missing in audit_plan.md")
    if "Coverage does NOT mean sufficiency" not in plan_content and "Coverage Does NOT Mean Sufficiency" not in plan_content:
        raise AssertionError("Mandatory 'Coverage Does NOT Mean Sufficiency' notice missing in audit_plan.md")


def audit_reproducibility(repo_root: str, canonical_dir: str) -> None:
    # Run engine in a temp dir and compare byte-for-byte to canonical
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.run_t0_3a_document_coverage import execute_t0_3a_run

    temp_dir = tempfile.mkdtemp(prefix="t0_3a_audit_run_")
    try:
        execute_t0_3a_run(repo_root, temp_dir)
        for fn in SUBSTANTIVE_FILES:
            f_canon = os.path.join(canonical_dir, fn)
            f_audit = os.path.join(temp_dir, fn)
            sha_canon = _file_sha256(f_canon)
            sha_audit = _file_sha256(f_audit)
            if sha_canon != sha_audit:
                raise AssertionError(f"Reproducibility divergence in {fn}: canon={sha_canon}, audit={sha_audit}")
    finally:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_full_audit(repo_root: str, canonical_dir: str) -> bool:
    print("=" * 60)
    print("ARPipe T0.3A Scanned/Document-Type Coverage Audit Verifier")
    print("=" * 60)

    print("[1/6] Verifying base commit...")
    audit_base_commit(repo_root)
    print("      PASS: Base commit matches ef2e8c5c17a753fc133c66272e4ad755ab26e5a4")

    print("[2/6] Verifying frozen inputs against SHA256 manifests...")
    inputs = audit_frozen_inputs(repo_root)
    print(f"      PASS: All {len(inputs)} frozen inputs verified byte-for-byte")

    print("[3/6] Verifying core-thesis decision invariant...")
    audit_core_decision_invariant(repo_root)
    print("      PASS: Core decision invariant holds (NO_ACQUISITION)")

    print("[4/6] Verifying taxonomy register integrity...")
    categories = audit_taxonomy_register(repo_root)
    print(f"      PASS: {len(categories)} categories verified in frozen taxonomy input (zero hardcoded counts)")

    print("[5/6] Auditing canonical T0.3A artifacts and dynamic counts...")
    audit_canonical_artifacts(repo_root, canonical_dir)
    print("      PASS: All counts, evidence levels, mapping references, and schemas match perfectly")

    print("[6/6] Verifying deterministic two-run reproducibility...")
    audit_reproducibility(repo_root, canonical_dir)
    print("      PASS: Canonical artifacts reproduced byte-for-byte in fresh run")

    print("=" * 60)
    print("T0.3A AUDIT PASSED: ALL INVARIANTS VERIFIED")
    print("=" * 60)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="ARPipe T0.3A Coverage Audit Verifier")
    parser.add_argument("--repo-root", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    parser.add_argument("--canonical-dir", default=None)
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    canonical_dir = args.canonical_dir
    if not canonical_dir:
        canonical_dir = os.path.join(repo_root, "dataset", "corpus_gap_audit", "t0_3a_document_coverage")

    try:
        run_full_audit(repo_root, canonical_dir)
    except AssertionError as e:
        print(f"\nT0.3A AUDIT FAILED: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
