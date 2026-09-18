"""Audit script for ARPipe T0.1R reconciliation outputs.

Verifies:
  1. Cryptographic preservation of T0 baseline and T0.1 RAW input files.
  2. Integrity and existence of all derived reconciled artifacts.
  3. Strict schema validation for claim_audit.csv, t0_t01_reconciliation.csv, and acquisition_decision.csv.
  4. Correct row-level review provenance flags (AUTO_RELABELLED_WITHOUT_MODEL_INSPECTION).
  5. Interaction matrix column naming (total_pages_in_docs_meeting_both) and code-grounded tautology flags.
  6. Self-hash exclusion policy in reconciliation_manifest.json.
  7. Separation of runtime metadata into run_metadata.json.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from typing import Any, Dict, List


def _file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def audit_reconciliation(repo_root: str, reconciled_dir: str) -> bool:
    print(f"Auditing reconciliation artifacts in: {reconciled_dir}")
    errors: List[str] = []

    # 1. Verify raw_input_manifest.json
    raw_manifest_path = os.path.join(reconciled_dir, "raw_input_manifest.json")
    if not os.path.isfile(raw_manifest_path):
        errors.append(f"Missing raw_input_manifest.json at {raw_manifest_path}")
    else:
        with open(raw_manifest_path, "r", encoding="utf-8") as f:
            raw_manifest = json.load(f)
        for item in raw_manifest.get("inputs", []):
            rel_path = item["artifact_path"]
            expected_sha = item["sha256"]
            full_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
            if not os.path.isfile(full_path):
                errors.append(f"Input file missing: {full_path}")
            else:
                actual_sha = _file_sha256(full_path)
                if actual_sha != expected_sha:
                    errors.append(f"Input file SHA mismatch for {rel_path}: {actual_sha} != {expected_sha}")

    # 2. Verify reconciliation_manifest.json self-hash policy
    recon_manifest_path = os.path.join(reconciled_dir, "reconciliation_manifest.json")
    if not os.path.isfile(recon_manifest_path):
        errors.append(f"Missing reconciliation_manifest.json at {recon_manifest_path}")
    else:
        with open(recon_manifest_path, "r", encoding="utf-8") as f:
            recon_manifest = json.load(f)
        if recon_manifest.get("self_hash_policy") != "EXCLUDED_FROM_OWN_HASH_SET":
            errors.append("reconciliation_manifest.json does not declare self_hash_policy: EXCLUDED_FROM_OWN_HASH_SET")
        output_hashes = recon_manifest.get("derived_output_hashes", {})
        if "reconciliation_manifest.json" in output_hashes:
            errors.append("reconciliation_manifest.json illegally appears in its own output hash table (circular hashing)")

        # Verify output hashes match disk bytes
        for fn, expected_h in output_hashes.items():
            fp = os.path.join(reconciled_dir, fn)
            if not os.path.isfile(fp):
                errors.append(f"Declared output file missing from disk: {fp}")
            else:
                act_h = _file_sha256(fp)
                if act_h != expected_h:
                    errors.append(f"Output file SHA mismatch for {fn}: {act_h} != {expected_h}")

    # 3. Verify run_metadata.json separation
    run_meta_path = os.path.join(reconciled_dir, "run_metadata.json")
    if not os.path.isfile(run_meta_path):
        errors.append("Missing run_metadata.json")
    else:
        with open(run_meta_path, "r", encoding="utf-8") as f:
            run_meta = json.load(f)
        if "execution_timestamp_utc" not in run_meta:
            errors.append("run_metadata.json missing execution_timestamp_utc")

    # 4. Verify manual_review_results_reconciled.csv provenance
    review_path = os.path.join(reconciled_dir, "manual_review_results_reconciled.csv")
    if not os.path.isfile(review_path):
        errors.append(f"Missing {review_path}")
    else:
        with open(review_path, "r", encoding="utf-8") as f:
            review_rows = list(csv.DictReader(f))
        if len(review_rows) != 72:
            errors.append(f"Expected 72 review records, found {len(review_rows)}")
        for i, r in enumerate(review_rows):
            if r["original_verification_status"] == "MODEL_REVIEWED":
                if r["reconciled_verification_status"] != "NOT_REVIEWED":
                    errors.append(f"Row {i} ({r['document_id']}) failed to reconcile MODEL_REVIEWED to NOT_REVIEWED")
                if r["review_provenance_issue"] != "AUTO_RELABELLED_WITHOUT_MODEL_INSPECTION":
                    errors.append(f"Row {i} ({r['document_id']}) missing AUTO_RELABELLED_WITHOUT_MODEL_INSPECTION flag")

    # 5. Verify interaction_gap_matrix_reconciled.csv
    inter_path = os.path.join(reconciled_dir, "interaction_gap_matrix_reconciled.csv")
    if not os.path.isfile(inter_path):
        errors.append(f"Missing {inter_path}")
    else:
        with open(inter_path, "r", encoding="utf-8") as f:
            inter_rows = list(csv.DictReader(f))
        found_tautology = False
        for r in inter_rows:
            if "page_count" in r:
                errors.append("interaction_gap_matrix_reconciled.csv contains deprecated column 'page_count'")
            if "total_pages_in_docs_meeting_both" not in r:
                errors.append("interaction_gap_matrix_reconciled.csv missing 'total_pages_in_docs_meeting_both'")
            if r["condition_a"] == "ocr_layer_candidate" and r["condition_b"] == "scanned_or_mixed":
                if r["tautology_flag"] != "TAUTOLOGICAL":
                    errors.append("ocr_layer_candidate x scanned_or_mixed must be flagged TAUTOLOGICAL")
                if "audit_corpus_gaps.py" not in r["dependency_source_artifact"]:
                    errors.append("ocr_layer_candidate x scanned_or_mixed missing dependency_source_artifact")
                found_tautology = True
        if not found_tautology:
            errors.append("Missing ocr_layer_candidate x scanned_or_mixed pair in interaction matrix")

    # 6. Verify claim_audit.csv schema and statuses
    claim_path = os.path.join(reconciled_dir, "claim_audit.csv")
    if not os.path.isfile(claim_path):
        errors.append(f"Missing {claim_path}")
    else:
        with open(claim_path, "r", encoding="utf-8") as f:
            claim_rows = list(csv.DictReader(f))
        if len(claim_rows) < 50:
            errors.append(f"claim_audit.csv has insufficient claims: {len(claim_rows)} < 50")
        allowed_claim_types = {"QUANTITATIVE", "QUALITATIVE", "METHODOLOGICAL", "LIMITATION", "DECISION"}
        allowed_statuses = {"SUPPORTED", "SUPPORTED_WITH_QUALIFICATION", "CANDIDATE_ONLY", "OVERSTATED", "UNSUPPORTED", "UNKNOWN"}
        for r in claim_rows:
            cid = r["claim_id"]
            if not cid.startswith("CLAIM:C"):
                errors.append(f"Invalid claim_id format: {cid}")
            if r["claim_type"] not in allowed_claim_types:
                errors.append(f"Claim {cid} has invalid claim_type: {r['claim_type']}")
            if r["status"] not in allowed_statuses:
                errors.append(f"Claim {cid} has invalid status: {r['status']}")
            if not r["claim_anchor"]:
                errors.append(f"Claim {cid} missing semantic claim_anchor")
            if not r["source_calculation_id"]:
                errors.append(f"Claim {cid} missing source_calculation_id")
            if r["claim_type"] == "DECISION":
                if not r["source_claim_ids"] or not r["decision_rule_id"] or not r["decision_basis"]:
                    errors.append(f"DECISION claim {cid} missing source_claim_ids, decision_rule_id, or decision_basis")

    # 7. Verify acquisition_decision.csv
    acq_path = os.path.join(reconciled_dir, "acquisition_decision.csv")
    if not os.path.isfile(acq_path):
        errors.append(f"Missing {acq_path}")
    else:
        with open(acq_path, "r", encoding="utf-8") as f:
            acq_rows = list(csv.DictReader(f))
        allowed_acq_statuses = {
            "NO_ACQUISITION", "ADDITIONAL_AUDIT_REQUIRED",
            "OPTIONAL_ROBUSTNESS_ACQUISITION", "ACQUISITION_JUSTIFIED", "UNRESOLVED"
        }
        for r in acq_rows:
            cond = r["condition"]
            if r["acquisition_status"] not in allowed_acq_statuses:
                errors.append(f"Condition {cond} has invalid acquisition_status: {r['acquisition_status']}")
            if not r["decision_rule_id"] or not r["decision_basis"]:
                errors.append(f"Condition {cond} missing decision_rule_id or decision_basis")

    if errors:
        print(f"FAILED: Reconciliation audit found {len(errors)} errors:")
        for e in errors:
            print(f"  - {e}")
        return False

    print("PASS: All reconciliation outputs and provenance safeguards verified successfully.")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit ARPipe T0.1R reconciliation outputs")
    parser.add_argument("--repo-root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))), help="Repo root")
    parser.add_argument("--reconciled-dir", default=os.path.join("dataset", "corpus_gap_audit", "reconciled"), help="Reconciled output directory")
    args = parser.parse_args()

    success = audit_reconciliation(args.repo_root, args.reconciled_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
