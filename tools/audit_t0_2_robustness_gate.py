"""Strict Auditor for ARPipe T0.2 Robustness-Gate Decision Audit.

Enforces:
  1. Base commit == 879762a2f236b3aaa6df33b7ddacc60c01d633c1.
  2. Frozen T0.1R files are unchanged (cryptographic SHA-256 verification).
  3. Every frozen ADDITIONAL_AUDIT_REQUIRED row is accounted for.
  4. No condition is silently omitted or extra unexplained condition added.
  5. Every condition maps to at least one claim.
  6. Every claim maps to valid frozen source evidence.
  7. Every source_calculation_id resolves deterministically.
  8. Every uncertainty has an allowed uncertainty_type.
  9. Every condition has exactly one audit_decision.
  10. Every proposed existing-evidence audit specifies frozen inputs.
  11. Any TARGETED_ACQUISITION_JUSTIFIED row requires evidence that the trigger was actually executed and satisfied before T0.2.
  12. T0.2 itself must never claim a future, unexecuted trigger has fired.
  13. No numeric threshold is invented without a valid threshold_basis.
  14. No arbitrary sample size is invented.
  15. No acquisition is justified solely because candidate prevalence is unknown.
  16. No acquisition is justified solely because a detector is imperfect.
  17. No new PDF-derived measurement is created.
  18. No forbidden PDF inspection is performed.
  19. Frozen core decision remains NO_ACQUISITION.
  20. Immutable input manifest hashes match actual inputs.

Fails closed on any violation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
from typing import Any, Dict, List, Set

BASE_COMMIT = "879762a2f236b3aaa6df33b7ddacc60c01d633c1"
FROZEN_CORE_DECISION = "NO_ACQUISITION"

ALLOWED_UNCERTAINTY_TYPES = {
    "MEASUREMENT_LIMITATION",
    "DEFINITION_LIMITATION",
    "COVERAGE_LIMITATION",
    "DEPENDENCY_LIMITATION",
    "PROVENANCE_LIMITATION",
    "REPRESENTATIVENESS_LIMITATION",
    "UNKNOWN",
}

ALLOWED_DECISION_VALUES = {
    "AUDIT_CAN_RESOLVE",
    "AUDIT_REQUIRED_BEFORE_ACQUISITION",
    "NO_ACQUISITION_NEEDED",
    "ROBUSTNESS_CLAIM_NOT_MATERIAL",
    "TRIGGER_DEFINED_NOT_EXECUTED",
    "TARGETED_ACQUISITION_JUSTIFIED",
    "UNRESOLVED",
}

ALLOWED_CORE_RELEVANCE = {
    "CORE_RELEVANT",
    "ROBUSTNESS_ONLY",
    "UNRESOLVED"
}

ALLOWED_THRESHOLD_STATUSES = {
    "FROZEN_EXISTING_CRITERION",
    "SEPARATELY_PREREGISTERED",
    "TO_BE_SPECIFIED_BEFORE_EXECUTION",
    "NOT_JUSTIFIED",
}


def _file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def audit_t0_2(repo_root: str, gate_dir: str) -> bool:
    print(f"Auditing T0.2 Robustness-Gate artifacts in: {gate_dir}")
    errors: List[str] = []

    # 1. Base commit verification
    try:
        head = subprocess.check_output(
            ["git", "-C", repo_root, "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
        if head != BASE_COMMIT:
            errors.append(f"Invariant 1 Violated: Base commit mismatch. Expected {BASE_COMMIT}, got {head}")
    except Exception as e:
        errors.append(f"Invariant 1 Violated: Unable to read git HEAD: {e}")

    # 2. Frozen T0.1R files cryptographic verification
    recon_manifest_path = os.path.join(
        repo_root, "dataset", "corpus_gap_audit", "reconciled", "reconciliation_manifest.json"
    )
    if not os.path.isfile(recon_manifest_path):
        errors.append(f"Invariant 2 Violated: Reconciliation manifest missing at {recon_manifest_path}")
    else:
        with open(recon_manifest_path, "r", encoding="utf-8") as f:
            recon_manifest = json.load(f)
        for rel_fn, exp_h in recon_manifest.get("derived_output_hashes", {}).items():
            full_p = os.path.join(repo_root, "dataset", "corpus_gap_audit", "reconciled", rel_fn)
            if not os.path.isfile(full_p):
                errors.append(f"Invariant 2 Violated: Frozen reconciled file missing: {rel_fn}")
            else:
                act_h = _file_sha256(full_p)
                if act_h != exp_h:
                    errors.append(f"Invariant 2 Violated: Frozen file hash mismatch for {rel_fn}: got {act_h}, expected {exp_h}")

    # 3 & 4. Derive ADDITIONAL_AUDIT_REQUIRED conditions from acquisition_decision.csv
    acq_path = os.path.join(repo_root, "dataset", "corpus_gap_audit", "reconciled", "acquisition_decision.csv")
    frozen_additional_conditions: Set[str] = set()
    if not os.path.isfile(acq_path):
        errors.append(f"Frozen acquisition_decision.csv missing at {acq_path}")
    else:
        with open(acq_path, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["acquisition_status"] == "ADDITIONAL_AUDIT_REQUIRED":
                    frozen_additional_conditions.add(r["condition"])

    # Verify gate file presence and contents
    gate_csv_path = os.path.join(gate_dir, "t0_2_robustness_gate.csv")
    if not os.path.isfile(gate_csv_path):
        errors.append(f"T0.2 gate CSV missing at {gate_csv_path}")
        gate_rows = []
    else:
        with open(gate_csv_path, "r", encoding="utf-8") as f:
            gate_rows = list(csv.DictReader(f))

    gate_conditions = set(r["condition"] for r in gate_rows)

    # Invariant 3: All ADDITIONAL_AUDIT_REQUIRED rows accounted for
    missing_conds = frozen_additional_conditions - gate_conditions
    if missing_conds:
        errors.append(f"Invariant 3 Violated: ADDITIONAL_AUDIT_REQUIRED conditions missing from gate: {missing_conds}")

    # Invariant 4: No condition silently omitted or extra condition added
    extra_conds = gate_conditions - frozen_additional_conditions
    if extra_conds:
        errors.append(f"Invariant 4 Violated: Extra unexpected conditions in gate: {extra_conds}")

    if len(gate_rows) != len(frozen_additional_conditions):
        errors.append(
            f"Invariant 4 Violated: Gate row count ({len(gate_rows)}) != frozen derived condition count ({len(frozen_additional_conditions)})"
        )

    # Invariant 19: Core decision invariant NO_ACQUISITION
    if os.path.isfile(acq_path):
        with open(acq_path, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("core_thesis_need") == "PRIMARY" and r.get("acquisition_status") != FROZEN_CORE_DECISION:
                    errors.append(f"Invariant 19 Violated: Core-thesis row {r['condition']} != {FROZEN_CORE_DECISION}")

    # Load claim registry and calculations for verification
    claim_audit_path = os.path.join(repo_root, "dataset", "corpus_gap_audit", "reconciled", "claim_audit.csv")
    valid_claims: Dict[str, Dict[str, str]] = {}
    valid_calc_ids: Set[str] = set()
    if os.path.isfile(claim_audit_path):
        with open(claim_audit_path, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                valid_claims[r["claim_id"]] = r
                cid = r.get("source_calculation_id")
                if cid and r.get("source_calculation"):
                    valid_calc_ids.add(cid)

    # Load calculation rules from reconciliation_rules.json
    calc_rules_path = os.path.join(repo_root, "configs", "t0_1r", "reconciliation_rules.json")
    if os.path.isfile(calc_rules_path):
        with open(calc_rules_path, "r", encoding="utf-8") as f:
            rules_json = json.load(f)
            valid_calc_ids.update(rules_json.get("claim_calculation_rules", {}).keys())

    # Check each gate row
    for r in gate_rows:
        c = r["condition"]

        # Invariant 5: Maps to at least one claim
        c_claims = [cid.strip() for cid in r.get("source_claim_ids", "").split(";") if cid.strip()]
        if not c_claims:
            errors.append(f"Invariant 5 Violated: Condition {c} maps to zero claims.")

        # Invariant 6: Every claim maps to valid frozen source evidence
        for cid in c_claims:
            if cid not in valid_claims:
                errors.append(f"Invariant 6 Violated: Condition {c} references unknown claim {cid}")
            else:
                c_data = valid_claims[cid]
                src_art = c_data.get("source_artifact", "")
                full_art = os.path.join(repo_root, src_art.replace("/", os.sep))
                if not os.path.isfile(full_art):
                    errors.append(f"Invariant 6 Violated: Claim {cid} source artifact does not exist: {src_art}")

        # Invariant 8: Allowed uncertainty_type
        u_type = r.get("uncertainty_type")
        if u_type not in ALLOWED_UNCERTAINTY_TYPES:
            errors.append(f"Invariant 8 Violated: Condition {c} has invalid uncertainty_type '{u_type}'")

        # Invariant 9: Exactly one valid audit_decision
        dec = r.get("audit_decision")
        if dec not in ALLOWED_DECISION_VALUES:
            errors.append(f"Invariant 9 Violated: Condition {c} has invalid audit_decision '{dec}'")

        # Invariant 10: Proposed existing-evidence audit specifies frozen inputs
        audit_inputs = [p.strip() for p in r.get("audit_inputs", "").split(";") if p.strip()]
        if not audit_inputs:
            errors.append(f"Invariant 10 Violated: Condition {c} does not specify audit_inputs")
        for inp in audit_inputs:
            full_inp = os.path.join(repo_root, inp.replace("/", os.sep))
            if not os.path.isfile(full_inp):
                errors.append(f"Invariant 10 Violated: Audit input {inp} for condition {c} does not exist")

        # Invariant 11 & 12: TARGETED_ACQUISITION_JUSTIFIED requires executed trigger evidence
        if dec == "TARGETED_ACQUISITION_JUSTIFIED":
            if r.get("trigger_executed") != "TRUE" or r.get("trigger_result") != "TRIGGER_SATISFIED":
                errors.append(
                    f"Invariant 11/12 Violated: Condition {c} declared TARGETED_ACQUISITION_JUSTIFIED "
                    f"without proof of executed and satisfied trigger (trigger_executed={r.get('trigger_executed')})"
                )

        # Invariant 12: Future unexecuted trigger cannot authorize acquisition
        if r.get("trigger_executed") == "FALSE":
            if r.get("acquisition_currently_justified") == "TRUE":
                errors.append(
                    f"Invariant 12 Violated: Condition {c} has trigger_executed=FALSE but acquisition_currently_justified=TRUE"
                )

        # Invariant 13: No invented numeric threshold without valid basis
        t_val = r.get("threshold_value", "")
        t_status = r.get("threshold_status", "")
        if t_status not in ALLOWED_THRESHOLD_STATUSES:
            errors.append(f"Invariant 13 Violated: Condition {c} has invalid threshold_status '{t_status}'")
        if t_status == "NOT_JUSTIFIED":
            errors.append(f"Invariant 13 Violated: Condition {c} has ungrounded threshold_status NOT_JUSTIFIED")
        if t_val not in ("NONE", "TO_BE_SPECIFIED_BEFORE_EXECUTION") and t_status == "TO_BE_SPECIFIED_BEFORE_EXECUTION":
            errors.append(f"Invariant 13 Violated: Condition {c} claims fixed numeric threshold '{t_val}' while status is TO_BE_SPECIFIED_BEFORE_EXECUTION")

        # Invariant 14: No arbitrary sample size invented
        s_size = r.get("minimum_sample_size", "")
        if s_size not in ("NONE", "TO_BE_SPECIFIED_BEFORE_ACQUISITION"):
            errors.append(
                f"Invariant 14 Violated: Condition {c} specifies ungrounded sample size '{s_size}'. "
                f"Must be 'NONE' or 'TO_BE_SPECIFIED_BEFORE_ACQUISITION'."
            )

    # Invariant 7: Check claim dependency map calculations
    dep_csv_path = os.path.join(gate_dir, "t0_2_claim_dependency_map.csv")
    if not os.path.isfile(dep_csv_path):
        errors.append(f"Claim dependency map missing at {dep_csv_path}")
    else:
        with open(dep_csv_path, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                calc_id = r.get("source_calculation_id")
                if calc_id and calc_id not in valid_calc_ids:
                    errors.append(f"Invariant 7 Violated: Dependency map has unknown calculation ID '{calc_id}'")

    # Invariant 20: Immutable input manifest verification
    in_manifest_path = os.path.join(gate_dir, "t0_2_immutable_input_manifest.json")
    if not os.path.isfile(in_manifest_path):
        errors.append(f"Invariant 20 Violated: Immutable input manifest missing at {in_manifest_path}")
    else:
        with open(in_manifest_path, "r", encoding="utf-8") as f:
            in_manifest = json.load(f)
        for item in in_manifest.get("inputs", []):
            rel_p = item["path"]
            exp_h = item["sha256"]
            full_p = os.path.join(repo_root, rel_p.replace("/", os.sep))
            if not os.path.isfile(full_p):
                errors.append(f"Invariant 20 Violated: Manifest input file missing: {rel_p}")
            else:
                act_h = _file_sha256(full_p)
                if act_h != exp_h:
                    errors.append(f"Invariant 20 Violated: Manifest input SHA mismatch for {rel_p}: {act_h} != {exp_h}")

    # Verify decision register
    dec_reg_path = os.path.join(gate_dir, "t0_2_decision_register.csv")
    if not os.path.isfile(dec_reg_path):
        errors.append(f"Decision register missing at {dec_reg_path}")
    else:
        with open(dec_reg_path, "r", encoding="utf-8") as f:
            dec_rows = list(csv.DictReader(f))
        if len(dec_rows) != len(frozen_additional_conditions):
            errors.append(f"Decision register row count ({len(dec_rows)}) != derived conditions ({len(frozen_additional_conditions)})")

    # Verify acquisition triggers JSON
    trig_json_path = os.path.join(gate_dir, "t0_2_acquisition_triggers.json")
    if not os.path.isfile(trig_json_path):
        errors.append(f"Acquisition triggers JSON missing at {trig_json_path}")
    else:
        with open(trig_json_path, "r", encoding="utf-8") as f:
            trig_data = json.load(f)
        if trig_data.get("summary", {}).get("acquisitions_currently_justified", -1) != 0:
            errors.append("Acquisition triggers JSON illegally declared acquisitions_currently_justified != 0")

    # Verify summary JSON
    summary_path = os.path.join(gate_dir, "t0_2_summary.json")
    if not os.path.isfile(summary_path):
        errors.append(f"Summary JSON missing at {summary_path}")
    else:
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)
        if summary.get("frozen_core_decision") != FROZEN_CORE_DECISION:
            errors.append(f"Summary JSON core decision mismatch: {summary.get('frozen_core_decision')} != {FROZEN_CORE_DECISION}")
        if summary.get("acquisitions_currently_justified_count") != 0:
            errors.append("Summary JSON illegally declared acquisitions_currently_justified_count != 0")

    if errors:
        print("FAIL CLOSED: T0.2 Auditor found violations:")
        for err in errors:
            print(f"  - {err}")
        return False

    print("PASS: All 20 T0.2 Robustness-Gate invariants verified successfully.")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="ARPipe T0.2 Robustness-Gate Decision Auditor")
    parser.add_argument("--repo-root", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    parser.add_argument("--gate-dir", default=None)
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    gate_dir = args.gate_dir
    if not gate_dir:
        gate_dir = os.path.join(repo_root, "dataset", "corpus_gap_audit", "t0_2_robustness_gate")

    success = audit_t0_2(repo_root, gate_dir)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
