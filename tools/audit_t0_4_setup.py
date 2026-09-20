"""Fail-closed audit for the T0.4 preregistration and setup-only harness."""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.t0_4.core import (
    BASE_COMMIT,
    SetupInvariantError,
    build_manifest,
    canonical_json,
    config_hash_manifest,
    contains_absolute_path,
    deterministic_repeat,
    read_json,
    validate_config_set,
    validate_manifest,
    verify_base_ancestor,
    verify_protected_paths_unchanged,
    write_canonical_json,
)

ALLOWED_ARTIFACTS = {
    "benchmark_manifest.json",
    "config_hashes.json",
    "final_closure_audit.json",
    "setup_audit.json",
}

REQUIRED_DELIVERABLES = {
    "docs/experiments/T0.4_ocr_benchmark_preregistration.md",
    "docs/experiments/T0.4_p-x1_reuse_audit.md",
    "tools/t0_4/README.md",
    "tools/t0_4/adapter.py",
    "tools/t0_4/core.py",
    "tools/t0_4/renderer.py",
    "tools/build_t0_4_manifest.py",
    "tools/audit_t0_4_setup.py",
    "tests/t0_4/test_t0_4_setup.py",
    "artifacts/t0_4/benchmark_manifest.json",
    "artifacts/t0_4/config_hashes.json",
}


def _assert_artifact_directory_is_setup_only(repo_root: Path) -> None:
    artifact_dir = repo_root / "artifacts/t0_4"
    unexpected = sorted(
        path.relative_to(artifact_dir).as_posix()
        for path in artifact_dir.rglob("*")
        if path.is_file() and path.name not in ALLOWED_ARTIFACTS
    )
    if unexpected:
        raise SetupInvariantError(f"unexpected benchmark/result artifacts exist: {unexpected}")


def _assert_no_new_pdf_or_engine_call_code(repo_root: Path) -> None:
    scoped_roots = [
        repo_root / "configs/t0_4",
        repo_root / "docs/experiments",
        repo_root / "tools/t0_4",
        repo_root / "tests/t0_4",
        repo_root / "artifacts/t0_4",
    ]
    new_pdfs = [path for root in scoped_roots if root.exists() for path in root.rglob("*.pdf")]
    if new_pdfs:
        raise SetupInvariantError(f"T0.4 added PDF files: {new_pdfs}")
    execution_markers = ("requests.post(", "boto3.client(", "google.genai", ".transcribe(")
    for path in (repo_root / "tools/t0_4").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        marker = next((item for item in execution_markers if item in text), None)
        if marker:
            raise SetupInvariantError(f"engine/API execution marker {marker!r} in {path.name}")


def _assert_no_nondeterministic_metadata(value: object) -> None:
    forbidden_keys = {"generated_at", "timestamp", "hostname", "uuid", "absolute_path"}
    if isinstance(value, dict):
        leaked = forbidden_keys.intersection(str(key).lower() for key in value)
        if leaked:
            raise SetupInvariantError(f"nondeterministic metadata keys present: {sorted(leaked)}")
        for child in value.values():
            _assert_no_nondeterministic_metadata(child)
    elif isinstance(value, list):
        for child in value:
            _assert_no_nondeterministic_metadata(child)
    elif isinstance(value, str) and re.search(
        r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b",
        value,
    ):
        raise SetupInvariantError("UUID leaked into deterministic artifact")


def run_audit(repo_root: Path) -> dict:
    verify_base_ancestor(repo_root)
    verify_protected_paths_unchanged(repo_root)
    validate_config_set(repo_root)
    missing_deliverables = sorted(
        rel for rel in REQUIRED_DELIVERABLES if not (repo_root / rel).is_file()
    )
    if missing_deliverables:
        raise SetupInvariantError(f"missing T0.4 deliverables: {missing_deliverables}")
    manifest = build_manifest(repo_root)
    validate_manifest(manifest)
    first_hash, second_hash = deterministic_repeat(repo_root)
    if first_hash != second_hash:
        raise SetupInvariantError("deterministic repeat hashes differ")

    manifest_path = repo_root / "artifacts/t0_4/benchmark_manifest.json"
    if not manifest_path.is_file() or read_json(manifest_path) != manifest:
        raise SetupInvariantError("checked-in benchmark manifest is missing or stale")
    hashes = config_hash_manifest(repo_root)
    hash_path = repo_root / "artifacts/t0_4/config_hashes.json"
    if not hash_path.is_file() or read_json(hash_path) != hashes:
        raise SetupInvariantError("checked-in config hash manifest is missing or stale")

    deterministic_text = canonical_json(manifest) + canonical_json(hashes)
    if contains_absolute_path(deterministic_text):
        raise SetupInvariantError("absolute machine path leaked into deterministic artifacts")
    _assert_no_nondeterministic_metadata(manifest)
    _assert_no_nondeterministic_metadata(hashes)
    _assert_artifact_directory_is_setup_only(repo_root)
    _assert_no_new_pdf_or_engine_call_code(repo_root)

    manifest_hash = hashlib.sha256(canonical_json(manifest).encode("utf-8")).hexdigest()
    return {
        "schema_version": "1.0.0",
        "task_id": "T0.4",
        "base_commit": BASE_COMMIT,
        "status": "PASS",
        "checks": {
            "base_commit_is_ancestor": "PASS",
            "common_output_adapter": "PASS",
            "configuration_hash_consistency": "PASS",
            "deterministic_repeat_byte_identical": "PASS",
            "frozen_corpus_unchanged": "PASS",
            "frozen_historical_artifacts_unchanged": "PASS",
            "holdout_protection": "PASS",
            "identical_track_a_image_contract": "PASS",
            "no_absolute_paths_in_deterministic_artifacts": "PASS",
            "no_timestamps_hostnames_or_uuids_in_deterministic_artifacts": "PASS",
            "no_api_call_code": "PASS",
            "no_benchmark_execution_artifacts": "PASS",
            "no_new_pdfs": "PASS",
            "no_production_behavior_change": "PASS",
            "oracle_routing_protocol": "PASS",
            "required_deliverables_present": "PASS",
            "separate_page_and_document_gold": "PASS",
            "track_a_track_b_separation": "PASS",
            "uncertainty_preregistered": "PASS"
        },
        "derived_counts": manifest["derived_counts"],
        "manifest_sha256": manifest_hash,
        "deterministic_repeat_sha256": first_hash,
        "execution_attestations": {
            "api_calls_made": False,
            "benchmark_executed": False,
            "ocr_engines_executed": False,
            "pdfs_acquired": False,
            "production_behavior_modified": False
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/t0_4/setup_audit.json"),
        help="Repository-relative deterministic audit report.",
    )
    args = parser.parse_args()
    repo_root = REPO_ROOT
    report = run_audit(repo_root)
    write_canonical_json(repo_root / args.output, report)
    print("T0.4 setup audit: PASS")
    print(f"Deterministic manifest SHA-256: {report['deterministic_repeat_sha256']}")
    print("No benchmark execution, PDF acquisition, OCR invocation, or API call occurred.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
