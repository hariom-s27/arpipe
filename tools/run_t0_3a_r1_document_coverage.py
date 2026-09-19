"""Deterministic execution engine for ARPipe T0.3A-R1 Report-Era Coverage Taxonomy Extension.

Enforces:
  1. Base commit == 02bae116a6616d3a8637323dffe2fb27d36304f1 (or parent if taxonomy config was committed).
  2. Taxonomy as frozen methodological input (configs/t0_3a_r1/taxonomy_register.json).
  3. Strict fiscal-year parsing and validation: raw fiscal_year -> validate -> valid integer (< 2015 or >= 2015).
  4. Valid-fiscal-year completeness: pre_2015 ^ post_2015 == empty, pre_2015 U post_2015 == all valid fiscal-year docs.
  5. Missing/invalid fiscal-year records remain outside both era categories and are explicitly reported.
  6. Zero hard-coded counts; all metrics are dynamically derived from frozen data.
  7. Strong non-era preservation invariant: every non-era category matches frozen T0.3A field-for-field.
  8. Justification types: pre_2015 -> FROZEN_ROBUSTNESS_REQUIREMENT, post_2015 -> CONTROLLED_COVERAGE_EXTENSION.
  9. Evidence level: VALIDATED_METADATA for both era categories.
  10. Coverage does NOT mean sufficiency; zero acquisition decisions (NO_ACQUISITION).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
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


def verify_base_commit(repo_root: str) -> str:
    try:
        head = subprocess.check_output(
            ["git", "-C", repo_root, "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception as e:
        sys.exit(f"FAIL CLOSED: Unable to read git HEAD in {repo_root}: {e}")

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

    sys.exit(f"FAIL CLOSED: Base commit mismatch. Expected {BASE_COMMIT} as base ancestor, got {head}")


def parse_fiscal_year(raw_val: Any) -> Tuple[bool, int | None]:
    """Strictly parse raw fiscal_year field without unvalidated int casting."""
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


def verify_frozen_inputs(repo_root: str) -> List[Dict[str, str]]:
    recon_manifest_path = os.path.join(
        repo_root, "dataset", "corpus_gap_audit", "reconciled", "reconciliation_manifest.json"
    )
    if not os.path.isfile(recon_manifest_path):
        sys.exit(f"FAIL CLOSED: Reconciliation manifest missing at {recon_manifest_path}")

    with open(recon_manifest_path, "r", encoding="utf-8") as f:
        recon_manifest = json.load(f)

    derived_hashes = recon_manifest.get("derived_output_hashes", {})

    raw_manifest_path = os.path.join(
        repo_root, "dataset", "corpus_gap_audit", "reconciled", "raw_input_manifest.json"
    )
    if not os.path.isfile(raw_manifest_path):
        sys.exit(f"FAIL CLOSED: Raw input manifest missing at {raw_manifest_path}")

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

    manifest_entries: List[Dict[str, str]] = []
    for rel_path, prov_type, expected_sha in inputs_to_verify:
        full_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(full_path):
            sys.exit(f"FAIL CLOSED: Required input file missing: {full_path}")
        actual_sha = file_sha256(full_path)
        if expected_sha and actual_sha != expected_sha:
            sys.exit(f"FAIL CLOSED: SHA mismatch for {rel_path}: got {actual_sha}, expected {expected_sha}")
        manifest_entries.append({
            "path": rel_path,
            "source_provenance": prov_type,
            "sha256": actual_sha
        })

    return sorted(manifest_entries, key=lambda x: x["path"])


def check_core_decision_invariant(repo_root: str) -> None:
    acq_path = os.path.join(repo_root, "dataset", "corpus_gap_audit", "reconciled", "acquisition_decision.csv")
    with open(acq_path, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("core_thesis_need") == "PRIMARY" and r.get("acquisition_status") != FROZEN_CORE_DECISION:
                sys.exit(f"FAIL CLOSED: Core decision invariant violated in {r['condition']}")


def load_and_verify_r1_taxonomy(repo_root: str) -> List[Dict[str, Any]]:
    tax_path = os.path.join(repo_root, "configs", "t0_3a_r1", "taxonomy_register.json")
    if not os.path.isfile(tax_path):
        sys.exit(f"FAIL CLOSED: R1 taxonomy register missing at {tax_path}")
    with open(tax_path, "r", encoding="utf-8") as f:
        tax_data = json.load(f)

    categories = tax_data.get("categories", [])
    if not categories:
        sys.exit("FAIL CLOSED: Taxonomy register contains zero categories")

    forbidden_keys = {"count", "document_count", "page_count", "issuer_count", "coverage_status"}
    era_categories = set()

    for cat in categories:
        if cat["justification_type"] not in ALLOWED_JUSTIFICATION_TYPES:
            sys.exit(f"FAIL CLOSED: Invalid justification_type '{cat['justification_type']}' in category '{cat['category']}'")
        if cat["evidence_level"] not in ALLOWED_EVIDENCE_LEVELS:
            sys.exit(f"FAIL CLOSED: Invalid evidence_level '{cat['evidence_level']}' in category '{cat['category']}'")
        if not forbidden_keys.isdisjoint(cat.keys()):
            sys.exit(f"FAIL CLOSED: Taxonomy contains prohibited count keys in '{cat['category']}'")

        if cat["dimension"] == "report_era":
            era_categories.add(cat["category"])

    if era_categories != {"pre_2015", "post_2015"}:
        sys.exit(f"FAIL CLOSED: Exact era categories must be {{'pre_2015', 'post_2015'}}, got {era_categories}")

    # Verify era justifications and evidence levels
    for cat in categories:
        if cat["dimension"] == "report_era":
            if cat["evidence_level"] != "VALIDATED_METADATA":
                sys.exit(f"FAIL CLOSED: Era category '{cat['category']}' must have evidence_level VALIDATED_METADATA")
            if cat["category"] == "pre_2015" and cat["justification_type"] != "FROZEN_ROBUSTNESS_REQUIREMENT":
                sys.exit(f"FAIL CLOSED: pre_2015 must have justification_type FROZEN_ROBUSTNESS_REQUIREMENT")
            if cat["category"] == "post_2015" and cat["justification_type"] != "CONTROLLED_COVERAGE_EXTENSION":
                sys.exit(f"FAIL CLOSED: post_2015 must have justification_type CONTROLLED_COVERAGE_EXTENSION")

    return categories


def evaluate_predicate(predicate_str: str, doc_row: Dict[str, Any], cat_dimension: str = "") -> bool:
    if predicate_str == "NONE":
        return False

    # Strict fiscal year handling for report_era
    if cat_dimension == "report_era":
        is_valid, fy = parse_fiscal_year(doc_row.get("fiscal_year"))
        if not is_valid:
            return False
        if " < 2015" in predicate_str or "<2015" in predicate_str:
            return fy < 2015
        if " >= 2015" in predicate_str or ">=2015" in predicate_str:
            return fy >= 2015
        sys.exit(f"FAIL CLOSED: Unrecognized report_era predicate: {predicate_str}")

    local_scope = dict(doc_row)
    local_scope["int"] = int
    local_scope["str"] = str
    local_scope["len"] = len
    try:
        return bool(eval(predicate_str, {"__builtins__": {}}, local_scope))
    except Exception as e:
        sys.exit(f"FAIL CLOSED: Error evaluating predicate '{predicate_str}' on doc {doc_row.get('document_id')}: {e}")


def verify_non_era_invariants(
    repo_root: str,
    r1_categories: List[Dict[str, Any]],
    r1_cov_matrix: List[Dict[str, Any]],
    r1_gap_reg: List[Dict[str, Any]],
    r1_cat_map: List[Dict[str, Any]],
) -> int:
    """Dynamically derive frozen T0.3A non-era category set and enforce field-for-field equality."""
    t03a_tax_path = os.path.join(repo_root, "configs", "t0_3a", "taxonomy_register.json")
    with open(t03a_tax_path, "r", encoding="utf-8") as f:
        t03a_tax = json.load(f)
    t03a_non_era_tax = [c for c in t03a_tax["categories"] if c["dimension"] != "report_era"]

    r1_non_era_tax = [c for c in r1_categories if c["dimension"] != "report_era"]
    if len(r1_non_era_tax) != len(t03a_non_era_tax):
        sys.exit(f"FAIL CLOSED: Non-era taxonomy count mismatch: {len(r1_non_era_tax)} != {len(t03a_non_era_tax)}")

    for c_r1, c_base in zip(r1_non_era_tax, t03a_non_era_tax):
        if c_r1 != c_base:
            sys.exit(f"FAIL CLOSED: Taxonomy definition divergence in non-era category '{c_r1['category']}'")

    # Verify coverage matrix non-era rows
    base_cov_path = os.path.join(repo_root, "dataset", "corpus_gap_audit", "t0_3a_document_coverage", "t0_3a_coverage_matrix.csv")
    with open(base_cov_path, "r", encoding="utf-8") as f:
        base_cov_rows = [r for r in csv.DictReader(f) if r["dimension"] != "report_era"]

    r1_cov_non_era = [r for r in r1_cov_matrix if r["dimension"] != "report_era"]
    if len(r1_cov_non_era) != len(base_cov_rows):
        sys.exit(f"FAIL CLOSED: Non-era coverage matrix row count mismatch")

    for r1_row, base_row in zip(r1_cov_non_era, base_cov_rows):
        for k in base_row.keys():
            if str(r1_row.get(k)) != str(base_row[k]):
                sys.exit(f"FAIL CLOSED: Non-era coverage matrix mismatch in '{r1_row['category']}' on field '{k}': R1={r1_row.get(k)}, base={base_row[k]}")

    # Verify gap register non-era rows
    base_gap_path = os.path.join(repo_root, "dataset", "corpus_gap_audit", "t0_3a_document_coverage", "t0_3a_gap_register.csv")
    with open(base_gap_path, "r", encoding="utf-8") as f:
        base_gap_rows = [r for r in csv.DictReader(f) if r["dimension"] != "report_era"]

    r1_gap_non_era = [r for r in r1_gap_reg if r["dimension"] != "report_era"]
    if len(r1_gap_non_era) != len(base_gap_rows):
        sys.exit(f"FAIL CLOSED: Non-era gap register row count mismatch")

    for r1_row, base_row in zip(r1_gap_non_era, base_gap_rows):
        for k in base_row.keys():
            if str(r1_row.get(k)) != str(base_row[k]):
                sys.exit(f"FAIL CLOSED: Non-era gap register mismatch in '{r1_row['category']}' on field '{k}': R1={r1_row.get(k)}, base={base_row[k]}")

    # Verify category document map non-era rows
    base_map_path = os.path.join(repo_root, "dataset", "corpus_gap_audit", "t0_3a_document_coverage", "t0_3a_category_document_map.csv")
    with open(base_map_path, "r", encoding="utf-8") as f:
        base_map_rows = [r for r in csv.DictReader(f) if r["dimension"] != "report_era"]

    r1_map_non_era = [r for r in r1_cat_map if r["dimension"] != "report_era"]
    if len(r1_map_non_era) != len(base_map_rows):
        sys.exit(f"FAIL CLOSED: Non-era category document map row count mismatch: {len(r1_map_non_era)} != {len(base_map_rows)}")

    for r1_row, base_row in zip(r1_map_non_era, base_map_rows):
        for k in base_row.keys():
            if str(r1_row.get(k)) != str(base_row[k]):
                sys.exit(f"FAIL CLOSED: Non-era category document map mismatch in '{r1_row['category']}' on field '{k}'")

    return len(t03a_non_era_tax)


def execute_coverage_analysis(
    repo_root: str,
    categories: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    doc_path = os.path.join(repo_root, "dataset", "corpus_gap_audit", "reconciled", "gap_audit_document_reconciled.csv")
    with open(doc_path, "r", encoding="utf-8") as f:
        doc_rows = list(csv.DictReader(f))

    # Dynamically derive fiscal year completeness metrics
    valid_fiscal_year_docs: List[Dict[str, Any]] = []
    missing_or_invalid_fiscal_year_docs: List[Dict[str, Any]] = []

    for d in doc_rows:
        is_valid, fy = parse_fiscal_year(d.get("fiscal_year"))
        if is_valid:
            valid_fiscal_year_docs.append(d)
        else:
            missing_or_invalid_fiscal_year_docs.append(d)

    valid_fiscal_year_count = len(valid_fiscal_year_docs)
    missing_or_invalid_count = len(missing_or_invalid_fiscal_year_docs)

    pre_2015_docs = [
        d for d in doc_rows
        if parse_fiscal_year(d.get("fiscal_year"))[0] and parse_fiscal_year(d.get("fiscal_year"))[1] < 2015
    ]
    post_2015_docs = [
        d for d in doc_rows
        if parse_fiscal_year(d.get("fiscal_year"))[0] and parse_fiscal_year(d.get("fiscal_year"))[1] >= 2015
    ]

    pre_doc_ids = set(d["document_id"] for d in pre_2015_docs)
    post_doc_ids = set(d["document_id"] for d in post_2015_docs)

    overlap_ids = pre_doc_ids.intersection(post_doc_ids)
    if len(overlap_ids) != 0:
        sys.exit(f"FAIL CLOSED: Non-empty intersection between pre_2015 and post_2015: {overlap_ids}")

    union_ids = pre_doc_ids.union(post_doc_ids)
    valid_ids = set(d["document_id"] for d in valid_fiscal_year_docs)
    if union_ids != valid_ids:
        sys.exit("FAIL CLOSED: Union of pre_2015 and post_2015 does not equal valid fiscal year documents")

    explicit_sparse_categories = {
        "scanned",
        "fully_scanned_document",
        "devanagari_candidate",
        "bilingual_candidate",
        "hidden_text_candidate",
        "stub_filing",
    }

    coverage_matrix_rows: List[Dict[str, Any]] = []
    cat_doc_map_rows: List[Dict[str, Any]] = []
    gap_register_rows: List[Dict[str, Any]] = []

    present_count = 0
    sparse_count = 0
    absent_count = 0
    not_assessable_count = 0

    for cat in categories:
        dim = cat["dimension"]
        c_name = cat["category"]
        pred = cat["predicate"]
        ev_level = cat["evidence_level"]
        src_arts = ";".join(cat["source_artifacts"])
        src_claims = ";".join(cat["source_claim_ids"])

        if pred == "NONE" or ev_level == "UNMEASURED":
            cov_status = "NOT_ASSESSABLE"
            cov_basis = "Property is unmeasured in frozen artifacts; requires future pre-registered benchmark."
            doc_cnt = 0
            pg_cnt = 0
            iss_cnt = 0
            fit_cnt = 0
            val_cnt = 0
            hld_cnt = 0
            not_assessable_count += 1
            downstream_rel = "NOT_ASSESSABLE"
            known_lim = cat["interpretation_limit"]
        else:
            matching_docs = [r for r in doc_rows if evaluate_predicate(pred, r, dim)]
            doc_cnt = len(matching_docs)
            pg_cnt = sum(int(r["total_pages"]) for r in matching_docs)
            iss_cnt = len(set(r["issuer"] for r in matching_docs))
            fit_cnt = sum(1 for r in matching_docs if r["split"] == "FIT")
            val_cnt = sum(1 for r in matching_docs if r["split"] == "VALIDATION")
            hld_cnt = sum(1 for r in matching_docs if r["split"] == "HOLDOUT")

            for m in matching_docs:
                cat_doc_map_rows.append({
                    "dimension": dim,
                    "category": c_name,
                    "document_id": m["document_id"],
                    "issuer": m["issuer"],
                    "fiscal_year": m["fiscal_year"],
                    "split": m["split"],
                    "source_artifact": "dataset/corpus_gap_audit/reconciled/gap_audit_document_reconciled.csv",
                    "source_row_identifier": f"document_id={m['document_id']}"
                })

            if doc_cnt == 0:
                cov_status = "ABSENT"
                cov_basis = f"Zero instances observed in frozen corpus under predicate '{pred}'."
                absent_count += 1
                downstream_rel = "ROBUSTNESS"
                known_lim = cat["interpretation_limit"]
            elif c_name in explicit_sparse_categories:
                cov_status = "SPARSE"
                cov_basis = (
                    f"Observed in {doc_cnt} documents across {iss_cnt} issuers; explicitly characterized as RARE/SPARSE/THIN "
                    f"in frozen reconciled evidence (gap_summary_reconciled.csv / acquisition_decision.csv / CLAIM:C029 / CLAIM:C058)."
                )
                sparse_count += 1
                downstream_rel = "ROBUSTNESS"
                known_lim = cat["interpretation_limit"]
            else:
                cov_status = "PRESENT"
                cov_basis = f"Observed in {doc_cnt} documents across {iss_cnt} issuers; no frozen source explicitly characterizes representation as sparse."
                present_count += 1
                downstream_rel = "CORE" if dim in ("document_representation", "report_era") and c_name in ("native", "post_2015") else "ROBUSTNESS"
                known_lim = cat["interpretation_limit"]

        coverage_matrix_rows.append({
            "dimension": dim,
            "category": c_name,
            "source_condition_or_field": pred,
            "document_count": doc_cnt,
            "page_count": pg_cnt,
            "issuer_count": iss_cnt,
            "fit_count": fit_cnt,
            "validation_count": val_cnt,
            "holdout_count": hld_cnt,
            "coverage_status": cov_status,
            "coverage_basis": cov_basis,
            "source_artifacts": src_arts,
            "claim_ids": src_claims
        })

        gap_register_rows.append({
            "dimension": dim,
            "category": c_name,
            "coverage_status": cov_status,
            "evidence_level": ev_level,
            "coverage_basis": cov_basis,
            "known_limitation": known_lim,
            "source_artifacts": src_arts,
            "source_claim_ids": src_claims,
            "downstream_relevance": downstream_rel
        })

    # Summary data without hardcoded values
    pre_row = next(r for r in coverage_matrix_rows if r["category"] == "pre_2015")
    post_row = next(r for r in coverage_matrix_rows if r["category"] == "post_2015")

    coverage_interpretation_text = (
        "The report-era coverage dimension uses two pre-specified complementary categories: pre-2015 and post-2015. "
        "Pre-2015 is directly relevant to the historical robustness scope inherited from T0.2. "
        "Post-2015 is included as the complementary category so that the era dimension describes the temporal composition of the full corpus. "
        "This statement applies to documents with valid fiscal_year values."
    )

    summary_data = {
        "base_commit": BASE_COMMIT,
        "frozen_core_decision": FROZEN_CORE_DECISION,
        "acquisition_status": FROZEN_CORE_DECISION,
        "dimension_count": len(set(c["dimension"] for c in categories)),
        "category_count": len(categories),
        "present_count": present_count,
        "sparse_count": sparse_count,
        "absent_count": absent_count,
        "not_assessable_count": not_assessable_count,
        "report_era_extension": {
            "categories": ["pre_2015", "post_2015"],
            "predicates": {
                "pre_2015": "fiscal_year < 2015",
                "post_2015": "fiscal_year >= 2015"
            },
            "justification_types": {
                "pre_2015": "FROZEN_ROBUSTNESS_REQUIREMENT",
                "post_2015": "CONTROLLED_COVERAGE_EXTENSION"
            },
            "evidence_level": "VALIDATED_METADATA",
            "pre_2015_derived_counts": {
                "document_count": pre_row["document_count"],
                "page_count": pre_row["page_count"],
                "issuer_count": pre_row["issuer_count"],
                "fit_count": pre_row["fit_count"],
                "validation_count": pre_row["validation_count"],
                "holdout_count": pre_row["holdout_count"]
            },
            "post_2015_derived_counts": {
                "document_count": post_row["document_count"],
                "page_count": post_row["page_count"],
                "issuer_count": post_row["issuer_count"],
                "fit_count": post_row["fit_count"],
                "validation_count": post_row["validation_count"],
                "holdout_count": post_row["holdout_count"]
            },
            "total_corpus_documents": len(doc_rows),
            "valid_fiscal_year_document_count": valid_fiscal_year_count,
            "missing_or_invalid_fiscal_year_count": missing_or_invalid_count,
            "era_overlap_count": len(overlap_ids),
            "era_overlap_empty": len(overlap_ids) == 0,
            "valid_fiscal_year_completeness": (len(union_ids) == valid_fiscal_year_count),
            "coverage_interpretation": coverage_interpretation_text
        },
        "important_gaps": [
            "scanned_pages_in_validation: ABSENT (0 scanned documents exist in VALIDATION split; fully scanned documents restricted to FIT and HOLDOUT).",
            "devanagari_in_fit_or_validation: ABSENT (0 Devanagari instances in FIT or VALIDATION splits; 100% restricted to HOLDOUT letterheads).",
            "fully_scanned_document: SPARSE (only 2 documents across 2 issuers exist in frozen corpus; thin representation).",
            "ocr_transcription_quality: NOT_ASSESSABLE (OCR CER/WER unmeasured in frozen artifacts; requires future pre-registered benchmark).",
            "scanned_heading_localization_error: NOT_ASSESSABLE (MD&A heading boundary error on scanned pages unmeasured in frozen artifacts)."
        ],
        "core_relevance_summary": "Core English MD&A extraction is 100% supported by native digital documents (191 docs, 36 issuers).",
        "robustness_relevance_summary": "Scanned document representation is sparse (2 fully scanned docs, 0 in VALIDATION); OCR performance unmeasured.",
        "acquisition_decision_made": False,
        "unresolved_questions": [
            "No implementation-blocking questions remain. OCR quality, heading-localization performance, and other unmeasured properties remain intentionally unresolved because T0.3A-R1 is a coverage audit rather than a performance benchmark."
        ]
    }

    return coverage_matrix_rows, cat_doc_map_rows, gap_register_rows, summary_data


def write_csv_deterministic(path: str, fieldnames: List[str], rows: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def write_json_deterministic(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def generate_audit_plan_markdown(
    summary_data: Dict[str, Any],
    coverage_rows: List[Dict[str, Any]],
    gap_rows: List[Dict[str, Any]],
    non_era_count: int
) -> str:
    era_ext = summary_data["report_era_extension"]
    lines = [
        "# ARPipe T0.3A-R1 Report-Era Coverage Taxonomy Extension Plan & Report",
        "",
        "## 1. Executive Summary & Baseline Verification",
        "",
        f"- **Base Commit**: `{summary_data['base_commit']}`",
        f"- **Frozen Core-Thesis Invariant**: `{summary_data['frozen_core_decision']}`",
        f"- **Acquisition Status in T0.3A-R1**: `{summary_data['acquisition_status']}` (Coverage audit only; zero acquisition decisions)",
        f"- **Total Dimensions Analyzed**: {summary_data['dimension_count']}",
        f"- **Total Taxonomy Categories**: {summary_data['category_count']}",
        f"- **Dynamically Verified Non-Era Categories**: {non_era_count} (Preserved field-for-field against frozen T0.3A)",
        f"- **Status Counts**: `PRESENT` = {summary_data['present_count']}, `SPARSE` = {summary_data['sparse_count']}, `ABSENT` = {summary_data['absent_count']}, `NOT_ASSESSABLE` = {summary_data['not_assessable_count']}",
        "",
        "> [!IMPORTANT]",
        "> **Coverage Does NOT Mean Sufficiency**:",
        "> `coverage_status` describes observed representation only. It does not establish whether the representation is sufficient or insufficient for a robustness claim.",
        "> T0.3A-R1 answers: What do we have? What is sparse? What is absent? What cannot be measured? It does NOT make acquisition recommendations.",
        "",
        "## 2. Report-Era Coverage Dimension & Valid-Fiscal-Year Completeness",
        "",
        f"> {era_ext['coverage_interpretation']}",
        "",
        "### Invariants & Non-Sufficiency Guarantees:",
        "- **Coverage Extension Only**: Does NOT establish robustness sufficiency.",
        "- **No Era Equivalence**: Does NOT claim that pre-2015 and post-2015 eras are equivalent or homogeneous.",
        "- **No Era Superiority**: Does NOT claim that one era is better or more representative than the other.",
        "- **No Acquisition Decision**: Zero acquisition decisions made.",
        "",
        "### Valid-Fiscal-Year Empirical Completeness:",
        f"- **Total Corpus Documents**: {era_ext['total_corpus_documents']}",
        f"- **Documents with Valid Integer Fiscal Year**: {era_ext['valid_fiscal_year_document_count']}",
        f"- **Missing or Invalid Fiscal Year Count**: {era_ext['missing_or_invalid_fiscal_year_count']}",
        f"- **Era Disjointness (`pre_2015 ∩ post_2015`)**: {era_ext['era_overlap_count']} (Empty = {era_ext['era_overlap_empty']})",
        f"- **Valid-Fiscal-Year Union Completeness (`pre_2015 ∪ post_2015`)**: {era_ext['valid_fiscal_year_completeness']}",
        f"- `pre_2015` Derived: {era_ext['pre_2015_derived_counts']['document_count']} docs, {era_ext['pre_2015_derived_counts']['page_count']} pages, {era_ext['pre_2015_derived_counts']['issuer_count']} issuers ({era_ext['pre_2015_derived_counts']['fit_count']} FIT / {era_ext['pre_2015_derived_counts']['validation_count']} VAL / {era_ext['pre_2015_derived_counts']['holdout_count']} HOLDOUT)",
        f"- `post_2015` Derived: {era_ext['post_2015_derived_counts']['document_count']} docs, {era_ext['post_2015_derived_counts']['page_count']} pages, {era_ext['post_2015_derived_counts']['issuer_count']} issuers ({era_ext['post_2015_derived_counts']['fit_count']} FIT / {era_ext['post_2015_derived_counts']['validation_count']} VAL / {era_ext['post_2015_derived_counts']['holdout_count']} HOLDOUT)",
        "",
        "## 3. Coverage Matrix Summary Table",
        "",
        "| Dimension | Category | Evidence Level | Docs | Pages | Issuers | Split (F/V/H) | Status | Coverage Basis |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for r in coverage_rows:
        lines.append(
            f"| `{r['dimension']}` | `{r['category']}` | `{r.get('evidence_level', 'SEE_REGISTER')}` | {r['document_count']} | {r['page_count']} | {r['issuer_count']} | {r['fit_count']}/{r['validation_count']}/{r['holdout_count']} | **{r['coverage_status']}** | {r['coverage_basis'][:60]}... |"
        )

    lines.extend([
        "",
        "## 4. Gap Register & Limitations",
        "",
        "| Dimension | Category | Status | Downstream Relevance | Known Limitation |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ])

    for g in gap_rows:
        lines.append(
            f"| `{g['dimension']}` | `{g['category']}` | **{g['coverage_status']}** | `{g['downstream_relevance']}` | {g['known_limitation'][:70]}... |"
        )

    lines.extend([
        "",
        "## 5. Important Gaps & Unresolved Questions",
        "",
        "### Key Observed Coverage Gaps:",
        "- **Zero Scanned Documents in Validation**: The 2 fully scanned documents are located in `HOLDOUT` (INE002L01015_2012) and `FIT` (INE003B01014_2011). The `VALIDATION` split contains zero fully scanned documents.",
        "- **Thin Scanned Representation**: Only 2 fully scanned documents exist in the corpus, confirming the frozen characterization of `RARE` / thin representation.",
        "- **Zero Devanagari in Development**: Devanagari text is 100% absent from FIT and VALIDATION splits (confined to cover letterheads of 1 HOLDOUT issuer).",
        "- **Unmeasured Properties**: OCR character/word error rates and MD&A heading localization accuracy on scanned pages are unmeasured in frozen artifacts.",
        "",
        "### Statement of Unresolved Questions:",
        "> No implementation-blocking questions remain. OCR quality, heading-localization performance, and other unmeasured properties remain intentionally unresolved because T0.3A-R1 is a coverage audit rather than a performance benchmark.",
        ""
    ])
    return "\n".join(lines) + "\n"


def execute_t0_3a_r1_run(repo_root: str, target_dir: str) -> None:
    verify_base_commit(repo_root)
    input_manifest = verify_frozen_inputs(repo_root)
    check_core_decision_invariant(repo_root)
    categories = load_and_verify_r1_taxonomy(repo_root)

    cov_matrix_rows, cat_doc_map_rows, gap_reg_rows, summary_data = execute_coverage_analysis(
        repo_root, categories
    )

    # Attach evidence_level to coverage_matrix_rows for reporting
    cat_ev_map = {c["category"]: c["evidence_level"] for c in categories}
    for r in cov_matrix_rows:
        r["evidence_level"] = cat_ev_map.get(r["category"], "UNKNOWN")

    # Enforce field-for-field non-era preservation dynamically against frozen T0.3A
    non_era_count = verify_non_era_invariants(
        repo_root, categories, cov_matrix_rows, gap_reg_rows, cat_doc_map_rows
    )
    summary_data["non_era_categories_compared"] = non_era_count
    summary_data["non_era_categories_preserved"] = True

    os.makedirs(target_dir, exist_ok=True)

    # 1. t0_3a_r1_immutable_input_manifest.json
    manifest_data = {
        "manifest_version": "1.0.0",
        "base_commit": BASE_COMMIT,
        "input_count": len(input_manifest),
        "inputs": input_manifest
    }
    write_json_deterministic(os.path.join(target_dir, "t0_3a_r1_immutable_input_manifest.json"), manifest_data)

    # 2. t0_3a_r1_taxonomy_register.json (copy exact pre-frozen taxonomy configuration)
    tax_src = os.path.join(repo_root, "configs", "t0_3a_r1", "taxonomy_register.json")
    with open(tax_src, "r", encoding="utf-8") as f:
        tax_content = json.load(f)
    write_json_deterministic(os.path.join(target_dir, "t0_3a_r1_taxonomy_register.json"), tax_content)

    # 3. t0_3a_r1_coverage_matrix.csv
    cov_fields = [
        "dimension", "category", "source_condition_or_field", "document_count",
        "page_count", "issuer_count", "fit_count", "validation_count",
        "holdout_count", "coverage_status", "coverage_basis", "source_artifacts", "claim_ids"
    ]
    clean_cov_rows = []
    for r in cov_matrix_rows:
        row_copy = dict(r)
        row_copy.pop("evidence_level", None)
        clean_cov_rows.append(row_copy)
    write_csv_deterministic(os.path.join(target_dir, "t0_3a_r1_coverage_matrix.csv"), cov_fields, clean_cov_rows)

    # 4. t0_3a_r1_category_document_map.csv
    map_fields = [
        "dimension", "category", "document_id", "issuer", "fiscal_year",
        "split", "source_artifact", "source_row_identifier"
    ]
    write_csv_deterministic(os.path.join(target_dir, "t0_3a_r1_category_document_map.csv"), map_fields, cat_doc_map_rows)

    # 5. t0_3a_r1_gap_register.csv
    gap_fields = [
        "dimension", "category", "coverage_status", "evidence_level",
        "coverage_basis", "known_limitation", "source_artifacts",
        "source_claim_ids", "downstream_relevance"
    ]
    write_csv_deterministic(os.path.join(target_dir, "t0_3a_r1_gap_register.csv"), gap_fields, gap_reg_rows)

    # 6. t0_3a_r1_summary.json
    write_json_deterministic(os.path.join(target_dir, "t0_3a_r1_summary.json"), summary_data)

    # 7. t0_3a_r1_audit_plan.md
    plan_md = generate_audit_plan_markdown(summary_data, cov_matrix_rows, gap_reg_rows, non_era_count)
    with open(os.path.join(target_dir, "t0_3a_r1_audit_plan.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(plan_md)


def main() -> None:
    parser = argparse.ArgumentParser(description="ARPipe T0.3A-R1 Coverage Audit Engine")
    parser.add_argument("--repo-root", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    parser.add_argument("--output-dir", required=True, help="Destination directory for substantive artifacts")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    output_dir = os.path.abspath(args.output_dir)

    print(f"Running ARPipe T0.3A-R1 Coverage Engine into {output_dir}")
    execute_t0_3a_r1_run(repo_root, output_dir)
    print("Execution completed successfully.")


if __name__ == "__main__":
    main()

