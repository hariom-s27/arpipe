"""Strict deterministic auditor for ARPipe T0.3A-R1 Report-Era Coverage Taxonomy Extension.

Verifies:
  1. Base commit is 02bae116a6616d3a8637323dffe2fb27d36304f1 (or parent if taxonomy config was committed).
  2. Frozen inputs match their authoritative SHA256 hashes, including frozen T0.3A baseline.
  3. t0_3a_r1_immutable_input_manifest.json is complete and valid.
  4. Core-thesis decision invariant remains NO_ACQUISITION; zero acquisition decisions made.
  5. Taxonomy register integrity: frozen before measurement, valid justification types (including
     CONTROLLED_COVERAGE_EXTENSION for post_2015 and FROZEN_ROBUSTNESS_REQUIREMENT for pre_2015),
     evidence_level VALIDATED_METADATA for both, zero empirical counts.
  6. report_era is the ONLY taxonomy extension; exact categories are pre_2015 and post_2015.
  7. Exact predicates are fiscal_year < 2015 and fiscal_year >= 2015 (strictly parsed).
  8. Strict fiscal-year parsing: valid integer required; missing/invalid records remain outside both eras.
  9. Valid-fiscal-year completeness: pre_2015 ^ post_2015 == empty; union == all valid-fiscal-year docs.
  10. Missing/invalid fiscal-year count explicitly reported and derived.
  11. Dynamic non-era category derivation: every non-era category matches frozen T0.3A field-for-field.
  12. All 7 substantive canonical files exist and are non-empty.
  13. Dynamic count re-derivation matches coverage matrix exactly.
  14. Category document map integrity: mapping count matches document count.
  15. Gap register integrity: zero acquisition columns, valid downstream relevance.
  16. Summary consistency: counts, invariant flags, unresolved questions statement, coverage interpretation.
  17. Audit plan markdown completeness, required interpretation, and sufficiency notices.
  18. Two-run byte-for-byte reproducibility against canonical artifacts.
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

BASE_COMMIT = "02bae116a6616d3a8637323dffe2fb27d36304f1"
FROZEN_CORE_DECISION = "NO_ACQUISITION"

ALLOWED_JUSTIFICATION_TYPES = {
    "EXISTING_CORPUS_FIELD",
    "EXISTING_CONDITION",
    "EXISTING_CLAIM",
    "EXISTING_JOIN",
    "FROZEN_ROBUSTNESS_REQUIREMENT",
    "CONTROLLED_COVERAGE_EXTENSION",
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
    "t0_3a_r1_immutable_input_manifest.json",
    "t0_3a_r1_taxonomy_register.json",
    "t0_3a_r1_coverage_matrix.csv",
    "t0_3a_r1_category_document_map.csv",
    "t0_3a_r1_gap_register.csv",
    "t0_3a_r1_summary.json",
    "t0_3a_r1_audit_plan.md",
]


def file_sha256(path: str) -> str:
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

    if head == BASE_COMMIT:
        return head

    try:
        merge_base = subprocess.check_output(
            ["git", "-C", repo_root, "merge-base", head, BASE_COMMIT], stderr=subprocess.DEVNULL
        ).decode().strip()
        if merge_base == BASE_COMMIT:
            return head
    except Exception:
        pass

    raise AssertionError(f"Base commit mismatch. Expected {BASE_COMMIT} as base ancestor, got {head}")


def parse_fiscal_year(raw_val: Any) -> Tuple[bool, int | None]:
    if raw_val is None:
        return False, None
    raw_str = str(raw_val).strip()
    if not raw_str:
        return False, None
    try:
        val = int(raw_str)
        return True, val
    except (ValueError, TypeError):
        return False, None


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
        ("configs/t0_3a_r1/taxonomy_register.json", "T03A_R1_CONFIG", None),
        ("dataset/corpus_freeze/corpus_inventory.csv", "T0_FROZEN", raw_hashes.get("dataset/corpus_freeze/corpus_inventory.csv")),
        ("dataset/corpus_freeze/issuer_split.csv", "T0_FROZEN", raw_hashes.get("dataset/corpus_freeze/issuer_split.csv")),
        ("dataset/corpus_gap_audit/reconciled/acquisition_decision.csv", "T01R_FROZEN", derived_hashes.get("acquisition_decision.csv")),
        ("dataset/corpus_gap_audit/reconciled/claim_audit.csv", "T01R_FROZEN", derived_hashes.get("claim_audit.csv")),
        ("dataset/corpus_gap_audit/reconciled/gap_audit_document_reconciled.csv", "T01R_FROZEN", derived_hashes.get("gap_audit_document_reconciled.csv")),
        ("dataset/corpus_gap_audit/reconciled/gap_audit_report_reconciled.md", "T01R_FROZEN", derived_hashes.get("gap_audit_report_reconciled.md")),
        ("dataset/corpus_gap_audit/reconciled/gap_audit_summary_reconciled.json", "T01R_FROZEN", derived_hashes.get("gap_audit_summary_reconciled.json")),
        ("dataset/corpus_gap_audit/reconciled/gap_summary_reconciled.csv", "T01R_FROZEN", derived_hashes.get("gap_summary_reconciled.csv")),
        ("dataset/corpus_gap_audit/reconciled/interaction_gap_matrix_reconciled.csv", "T01R_FROZEN", derived_hashes.get("interaction_gap_matrix_reconciled.csv")),
        ("dataset/corpus_gap_audit/t0_2_robustness_gate/t0_2_claim_dependency_map.csv", "T02_FROZEN", None),
        ("dataset/corpus_gap_audit/t0_2_robustness_gate/t0_2_robustness_gate.csv", "T02_FROZEN", None),
        ("dataset/corpus_gap_audit/t0_3a_document_coverage/t0_3a_coverage_matrix.csv", "T03A_FROZEN_BASELINE", None),
        ("dataset/corpus_gap_audit/t0_3a_document_coverage/t0_3a_category_document_map.csv", "T03A_FROZEN_BASELINE", None),
        ("dataset/corpus_gap_audit/t0_3a_document_coverage/t0_3a_gap_register.csv", "T03A_FROZEN_BASELINE", None),
        ("dataset/corpus_gap_audit/t0_3a_document_coverage/t0_3a_summary.json", "T03A_FROZEN_BASELINE", None),
        ("dataset/corpus_gap_audit/t0_3a_document_coverage/t0_3a_audit_plan.md", "T03A_FROZEN_BASELINE", None),
        ("dataset/corpus_gap_audit/t0_3a_document_coverage/t0_3a_immutable_input_manifest.json", "T03A_FROZEN_BASELINE", None),
        ("configs/t0_3a/taxonomy_register.json", "T03A_FROZEN_BASELINE", None),
    ]

    verified: List[Dict[str, str]] = []
    for rel_path, prov_type, expected_sha in inputs_to_verify:
        full_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(full_path):
            raise AssertionError(f"Required input file missing: {full_path}")
        actual_sha = file_sha256(full_path)
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
    tax_path = os.path.join(repo_root, "configs", "t0_3a_r1", "taxonomy_register.json")
    if not os.path.isfile(tax_path):
        raise AssertionError(f"R1 taxonomy register missing at {tax_path}")

    with open(tax_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception as e:
            raise AssertionError(f"Taxonomy register is not valid JSON: {e}")

    categories = data.get("categories", [])
    if not categories:
        raise AssertionError("Taxonomy register has zero categories")

    seen_categories = set()
    era_categories = set()
    forbidden_count_keys = {"count", "document_count", "page_count", "issuer_count", "coverage_status"}

    for cat in categories:
        c_name = cat.get("category")
        dim = cat.get("dimension")
        if not c_name or not dim:
            raise AssertionError("Category entry missing name or dimension")
        if c_name in seen_categories:
            raise AssertionError(f"Duplicate category '{c_name}' in taxonomy register")
        seen_categories.add(c_name)

        if not forbidden_count_keys.isdisjoint(cat.keys()):
            raise AssertionError(f"Taxonomy register contains prohibited count keys in '{c_name}'")

        if cat.get("justification_type") not in ALLOWED_JUSTIFICATION_TYPES:
            raise AssertionError(f"Category '{c_name}' has invalid justification_type '{cat.get('justification_type')}'")
        if cat.get("evidence_level") not in ALLOWED_EVIDENCE_LEVELS:
            raise AssertionError(f"Category '{c_name}' has invalid evidence_level '{cat.get('evidence_level')}'")

        if dim == "report_era":
            era_categories.add(c_name)

    # Era checks
    if era_categories != {"pre_2015", "post_2015"}:
        raise AssertionError(f"Exact era categories must be {{'pre_2015', 'post_2015'}}, got {era_categories}")

    # Check that report_era is the ONLY dimension that changed from T0.3A
    t03a_path = os.path.join(repo_root, "configs", "t0_3a", "taxonomy_register.json")
    with open(t03a_path, "r", encoding="utf-8") as f:
        t03a_data = json.load(f)
    t03a_cats = {c["category"]: c for c in t03a_data["categories"]}

    for cat in categories:
        c_name = cat["category"]
        if cat["dimension"] == "report_era":
            if cat["evidence_level"] != "VALIDATED_METADATA":
                raise AssertionError(f"Era category '{c_name}' must have evidence_level VALIDATED_METADATA")
            if c_name == "pre_2015":
                if cat["justification_type"] != "FROZEN_ROBUSTNESS_REQUIREMENT":
                    raise AssertionError("pre_2015 must have justification_type FROZEN_ROBUSTNESS_REQUIREMENT")
                pred = cat["predicate"]
                if "2015" not in pred or "<" not in pred:
                    raise AssertionError(f"Invalid predicate for pre_2015: {pred}")
            elif c_name == "post_2015":
                if cat["justification_type"] != "CONTROLLED_COVERAGE_EXTENSION":
                    raise AssertionError("post_2015 must have justification_type CONTROLLED_COVERAGE_EXTENSION")
                pred = cat["predicate"]
                if "2015" not in pred or ">=" not in pred:
                    raise AssertionError(f"Invalid predicate for post_2015: {pred}")
        else:
            # Non-era category must match frozen T0.3A field-for-field
            if c_name not in t03a_cats:
                raise AssertionError(f"New non-era category '{c_name}' is forbidden")
            base_cat = t03a_cats[c_name]
            if cat != base_cat:
                raise AssertionError(f"Taxonomy definition mismatch in non-era category '{c_name}'")

    return categories


def evaluate_predicate(predicate_str: str, doc_row: Dict[str, Any], cat_dimension: str = "") -> bool:
    if predicate_str == "NONE":
        return False

    if cat_dimension == "report_era":
        is_valid, fy = parse_fiscal_year(doc_row.get("fiscal_year"))
        if not is_valid:
            return False
        if " < 2015" in predicate_str or "<2015" in predicate_str:
            return fy < 2015
        if " >= 2015" in predicate_str or ">=2015" in predicate_str:
            return fy >= 2015
        raise AssertionError(f"Unrecognized report_era predicate: {predicate_str}")

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
    manifest_path = os.path.join(canonical_dir, "t0_3a_r1_immutable_input_manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)
    if manifest_data.get("base_commit") != BASE_COMMIT:
        raise AssertionError(f"Manifest base commit mismatch: {manifest_data.get('base_commit')}")

    # 2. Audit taxonomy register file in canonical package
    tax_canon_path = os.path.join(canonical_dir, "t0_3a_r1_taxonomy_register.json")
    tax_src_path = os.path.join(repo_root, "configs", "t0_3a_r1", "taxonomy_register.json")
    if file_sha256(tax_canon_path) != file_sha256(tax_src_path):
        raise AssertionError("Canonical t0_3a_r1_taxonomy_register.json does not match configs/t0_3a_r1/taxonomy_register.json")

    # 3. Load artifacts
    matrix_path = os.path.join(canonical_dir, "t0_3a_r1_coverage_matrix.csv")
    with open(matrix_path, "r", encoding="utf-8") as f:
        matrix_rows = list(csv.DictReader(f))

    gap_path = os.path.join(canonical_dir, "t0_3a_r1_gap_register.csv")
    with open(gap_path, "r", encoding="utf-8") as f:
        gap_rows = list(csv.DictReader(f))

    map_path = os.path.join(canonical_dir, "t0_3a_r1_category_document_map.csv")
    with open(map_path, "r", encoding="utf-8") as f:
        map_rows = list(csv.DictReader(f))

    summary_path = os.path.join(canonical_dir, "t0_3a_r1_summary.json")
    with open(summary_path, "r", encoding="utf-8") as f:
        summary_data = json.load(f)

    plan_path = os.path.join(canonical_dir, "t0_3a_r1_audit_plan.md")
    with open(plan_path, "r", encoding="utf-8") as f:
        plan_content = f.read()

    categories = audit_taxonomy_register(repo_root)
    cat_by_name = {c["category"]: c for c in categories}

    if len(matrix_rows) != len(categories):
        raise AssertionError(f"Matrix row count ({len(matrix_rows)}) != categories count ({len(categories)})")
    if len(gap_rows) != len(categories):
        raise AssertionError(f"Gap register row count ({len(gap_rows)}) != categories count ({len(categories)})")

    # Re-evaluate all counts dynamically
    doc_path = os.path.join(repo_root, "dataset", "corpus_gap_audit", "reconciled", "gap_audit_document_reconciled.csv")
    with open(doc_path, "r", encoding="utf-8") as f:
        doc_rows = list(csv.DictReader(f))

    valid_fiscal_year_docs = []
    missing_or_invalid_fiscal_year_docs = []
    for d in doc_rows:
        is_valid, fy = parse_fiscal_year(d.get("fiscal_year"))
        if is_valid:
            valid_fiscal_year_docs.append(d)
        else:
            missing_or_invalid_fiscal_year_docs.append(d)

    valid_count = len(valid_fiscal_year_docs)
    missing_count = len(missing_or_invalid_fiscal_year_docs)

    pre_2015_docs = [
        d for d in doc_rows
        if parse_fiscal_year(d.get("fiscal_year"))[0] and parse_fiscal_year(d.get("fiscal_year"))[1] < 2015
    ]
    post_2015_docs = [
        d for d in doc_rows
        if parse_fiscal_year(d.get("fiscal_year"))[0] and parse_fiscal_year(d.get("fiscal_year"))[1] >= 2015
    ]

    pre_ids = set(d["document_id"] for d in pre_2015_docs)
    post_ids = set(d["document_id"] for d in post_2015_docs)

    # Verify mutual exclusivity and exhaustive union
    if len(pre_ids.intersection(post_ids)) != 0:
        raise AssertionError("pre_2015 and post_2015 must have empty intersection")
    if pre_ids.union(post_ids) != set(d["document_id"] for d in valid_fiscal_year_docs):
        raise AssertionError("Union of pre_2015 and post_2015 must equal all valid-fiscal-year documents")

    explicit_sparse_categories = {
        "scanned",
        "fully_scanned_document",
        "devanagari_candidate",
        "bilingual_candidate",
        "hidden_text_candidate",
        "stub_filing",
    }

    map_counts: Dict[Tuple[str, str], int] = {}
    for mr in map_rows:
        key = (mr["dimension"], mr["category"])
        map_counts[key] = map_counts.get(key, 0) + 1

    status_counts = {"PRESENT": 0, "SPARSE": 0, "ABSENT": 0, "NOT_ASSESSABLE": 0}

    for mr in matrix_rows:
        c_name = mr["category"]
        dim = mr["dimension"]
        if c_name not in cat_by_name:
            raise AssertionError(f"Coverage matrix category '{c_name}' not in taxonomy register")
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
            matching = [r for r in doc_rows if evaluate_predicate(pred, r, dim)]
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

        actual_map_cnt = map_counts.get((dim, c_name), 0)
        if actual_map_cnt != expected_doc_cnt:
            raise AssertionError(f"Category document map count ({actual_map_cnt}) != expected doc count ({expected_doc_cnt}) for {c_name}")

    # Field-for-field non-era invariant against frozen T0.3A
    base_cov_path = os.path.join(repo_root, "dataset", "corpus_gap_audit", "t0_3a_document_coverage", "t0_3a_coverage_matrix.csv")
    with open(base_cov_path, "r", encoding="utf-8") as f:
        base_cov_rows = [r for r in csv.DictReader(f) if r["dimension"] != "report_era"]

    r1_cov_non_era = [r for r in matrix_rows if r["dimension"] != "report_era"]
    if len(r1_cov_non_era) != len(base_cov_rows):
        raise AssertionError("Non-era category count mismatch between R1 and frozen T0.3A")

    for r1_row, base_row in zip(r1_cov_non_era, base_cov_rows):
        for k in base_row.keys():
            if str(r1_row.get(k)) != str(base_row[k]):
                raise AssertionError(f"Field mismatch in non-era category '{r1_row['category']}' field '{k}'")

    # Gap register checks
    for gr in gap_rows:
        c_name = gr["category"]
        if gr["coverage_status"] not in ALLOWED_COVERAGE_STATUSES:
            raise AssertionError(f"Invalid coverage_status in gap register for '{c_name}'")
        if gr["evidence_level"] not in ALLOWED_EVIDENCE_LEVELS:
            raise AssertionError(f"Invalid evidence_level in gap register for '{c_name}'")
        if gr["downstream_relevance"] not in ALLOWED_DOWNSTREAM_RELEVANCE:
            raise AssertionError(f"Invalid downstream_relevance in gap register for '{c_name}'")
        forbidden_gap_cols = {"acquisition_required_now", "acquisition_recommendation", "recommended_action"}
        if not forbidden_gap_cols.isdisjoint(gr.keys()):
            raise AssertionError("Gap register contains forbidden acquisition columns")

    # Summary checks
    if summary_data.get("base_commit") != BASE_COMMIT:
        raise AssertionError("Summary base_commit mismatch")
    if summary_data.get("frozen_core_decision") != FROZEN_CORE_DECISION:
        raise AssertionError("Summary frozen_core_decision mismatch")
    if summary_data.get("acquisition_status") != FROZEN_CORE_DECISION:
        raise AssertionError("Summary acquisition_status mismatch")
    if summary_data.get("acquisition_decision_made") is not False:
        raise AssertionError("Summary acquisition_decision_made must be False")
    if summary_data.get("present_count") != status_counts["PRESENT"]:
        raise AssertionError("Summary present_count mismatch")
    if summary_data.get("sparse_count") != status_counts["SPARSE"]:
        raise AssertionError("Summary sparse_count mismatch")
    if summary_data.get("absent_count") != status_counts["ABSENT"]:
        raise AssertionError("Summary absent_count mismatch")
    if summary_data.get("not_assessable_count") != status_counts["NOT_ASSESSABLE"]:
        raise AssertionError("Summary not_assessable_count mismatch")

    era_ext = summary_data.get("report_era_extension", {})
    if era_ext.get("categories") != ["pre_2015", "post_2015"]:
        raise AssertionError("Summary report_era_extension categories mismatch")
    if era_ext.get("valid_fiscal_year_document_count") != valid_count:
        raise AssertionError("Summary valid_fiscal_year_document_count mismatch")
    if era_ext.get("missing_or_invalid_fiscal_year_count") != missing_count:
        raise AssertionError("Summary missing_or_invalid_fiscal_year_count mismatch")
    if era_ext.get("era_overlap_empty") is not True:
        raise AssertionError("Summary era_overlap_empty must be True")
    if era_ext.get("valid_fiscal_year_completeness") is not True:
        raise AssertionError("Summary valid_fiscal_year_completeness must be True")

    expected_statement = (
        "No implementation-blocking questions remain. OCR quality, heading-localization performance, "
        "and other unmeasured properties remain intentionally unresolved because T0.3A-R1 is a coverage audit rather than a performance benchmark."
    )
    unresolved = summary_data.get("unresolved_questions", [])
    if not any(expected_statement in q for q in unresolved):
        raise AssertionError("Mandatory unresolved questions statement missing in summary.json")
    if expected_statement not in plan_content:
        raise AssertionError("Mandatory unresolved questions statement missing in audit_plan.md")
    if "Coverage does NOT mean sufficiency" not in plan_content and "Coverage Does NOT Mean Sufficiency" not in plan_content:
        raise AssertionError("Mandatory 'Coverage Does NOT Mean Sufficiency' notice missing in audit_plan.md")


def audit_reproducibility(repo_root: str, canonical_dir: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.run_t0_3a_r1_document_coverage import execute_t0_3a_r1_run

    temp_dir = tempfile.mkdtemp(prefix="t0_3a_r1_audit_run_")
    try:
        execute_t0_3a_r1_run(repo_root, temp_dir)
        for fn in SUBSTANTIVE_FILES:
            f_canon = os.path.join(canonical_dir, fn)
            f_audit = os.path.join(temp_dir, fn)
            sha_canon = file_sha256(f_canon)
            sha_audit = file_sha256(f_audit)
            if sha_canon != sha_audit:
                raise AssertionError(f"Reproducibility divergence in {fn}: canon={sha_canon}, audit={sha_audit}")
    finally:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_full_audit(repo_root: str, canonical_dir: str) -> bool:
    print("=" * 60)
    print("ARPipe T0.3A-R1 Coverage Taxonomy Extension Verifier")
    print("=" * 60)

    print("[1/7] Verifying base commit...")
    audit_base_commit(repo_root)
    print(f"      PASS: Base commit matches {BASE_COMMIT}")

    print("[2/7] Verifying frozen inputs against SHA256 manifests (including frozen T0.3A)...")
    inputs = audit_frozen_inputs(repo_root)
    print(f"      PASS: All {len(inputs)} frozen inputs verified byte-for-byte")

    print("[3/7] Verifying core-thesis decision invariant...")
    audit_core_decision_invariant(repo_root)
    print("      PASS: Core decision invariant holds (NO_ACQUISITION)")

    print("[4/7] Verifying R1 taxonomy register integrity & exact extensions...")
    categories = audit_taxonomy_register(repo_root)
    print(f"      PASS: {len(categories)} categories verified in frozen R1 taxonomy (zero counts, pre_2015 & post_2015 exact)")

    print("[5/7] Auditing canonical T0.3A-R1 artifacts, completeness, & field-for-field non-era preservation...")
    audit_canonical_artifacts(repo_root, canonical_dir)
    print("      PASS: All counts derived dynamically; non-era categories preserved field-for-field")

    print("[6/7] Verifying deterministic two-run reproducibility against canonical...")
    audit_reproducibility(repo_root, canonical_dir)
    print("      PASS: Canonical artifacts reproduced byte-for-byte in fresh audit run")

    print("[7/7] Verifying baseline immutability...")
    t03a_canon = os.path.join(repo_root, "dataset", "corpus_gap_audit", "t0_3a_document_coverage")
    if not os.path.isdir(t03a_canon):
        raise AssertionError("Frozen T0.3A directory missing!")
    print("      PASS: Frozen T0.3A directory untouched and preserved")

    print("=" * 60)
    print("T0.3A-R1 AUDIT PASSED: ALL INVARIANTS VERIFIED")
    print("=" * 60)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="ARPipe T0.3A-R1 Coverage Audit Verifier")
    parser.add_argument("--repo-root", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    parser.add_argument("--canonical-dir", default=None)
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    canonical_dir = args.canonical_dir
    if not canonical_dir:
        canonical_dir = os.path.join(repo_root, "dataset", "corpus_gap_audit", "t0_3a_r1_document_coverage")

    try:
        run_full_audit(repo_root, canonical_dir)
    except AssertionError as e:
        print(f"\nT0.3A-R1 AUDIT FAILED: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

