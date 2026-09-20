from __future__ import annotations

import copy
import csv
import hashlib
import json
import subprocess
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from tools.t0_4.adapter import (
    FORBIDDEN_TRACK_A_KEYS,
    adapt_engine_output,
    validate_cloud_replay,
    validate_holdout_access,
    validate_primary_engine_inputs,
    validate_track_a_request,
)
from tools.t0_4.core import (
    BASE_COMMIT,
    CONFIG_FILES,
    NOT_AVAILABLE,
    NOT_YET_RENDERED,
    PRIMARY_ENGINES,
    SetupInvariantError,
    build_manifest,
    canonical_json,
    config_hash_manifest,
    contains_absolute_path,
    deterministic_repeat,
    read_json,
    validate_config_set,
    validate_engine_registry,
    validate_gold_record,
    validate_manifest,
    validate_split_integrity,
    verify_base_ancestor,
    verify_protected_paths_unchanged,
)
from tools.audit_t0_4_setup import run_audit

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "configs/t0_4"


@pytest.fixture(scope="module")
def manifest() -> dict:
    return build_manifest(ROOT)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _engine_rows(image_hash: str = "a" * 64) -> list[dict]:
    return [
        {
            "document_id": "doc",
            "page_number": 7,
            "engine_id": engine,
            "input_image_hash": image_hash,
            "fallback_engine": NOT_AVAILABLE,
        }
        for engine in PRIMARY_ENGINES
    ]


def test_exact_base_exists_and_is_ancestor():
    resolved = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", BASE_COMMIT], text=True
    ).strip()
    assert resolved == BASE_COMMIT
    assert verify_base_ancestor(ROOT)


def test_frozen_corpus_and_history_are_unchanged():
    verify_protected_paths_unchanged(ROOT)


def test_all_config_json_is_parseable_and_validated():
    assert {path.name for path in CONFIG_DIR.glob("*.json")} == set(CONFIG_FILES)
    validate_config_set(ROOT)


def test_json_schemas_are_meta_schema_valid_and_manifest_conforms(manifest):
    schema_names = [
        "benchmark_manifest_schema.json",
        "common_output_schema.json",
        "efficiency_schema.json",
        "future_results_schema.json",
        "gold_schema.json",
        "raw_output_schema.json",
    ]
    for name in schema_names:
        Draft202012Validator.check_schema(read_json(CONFIG_DIR / name))
    Draft202012Validator(read_json(CONFIG_DIR / "benchmark_manifest_schema.json")).validate(manifest)


def test_manifest_is_byte_deterministic(manifest):
    first = canonical_json(manifest)
    second = canonical_json(build_manifest(ROOT))
    assert first == second
    assert deterministic_repeat(ROOT)[0] == hashlib.sha256(first.encode("utf-8")).hexdigest()


def test_counts_are_derived_from_frozen_inputs(manifest):
    inventory = _read_csv(ROOT / "dataset/corpus_freeze/corpus_inventory.csv")
    profiles = _read_csv(ROOT / "dataset/corpus_freeze/page_profile.csv")
    profile_docs = {row["document_id"] for row in profiles}
    counts = manifest["derived_counts"]
    assert counts["frozen_records"] == len(inventory)
    assert counts["profiled_pages"] == len(profiles)
    assert counts["profiled_documents"] == len(profile_docs)
    assert counts["input_unavailable_documents"] == len(inventory) - len(profile_docs)


def test_no_hard_coded_corpus_counts_in_builder(manifest):
    source = (ROOT / "tools/t0_4/core.py").read_text(encoding="utf-8")
    counts = manifest["derived_counts"]
    for name in ("frozen_records", "profiled_documents", "input_unavailable_documents", "profiled_pages"):
        assert f"= {counts[name]}" not in source


def test_issuer_disjointness_and_split_preservation(manifest):
    validate_split_integrity(manifest["track_a"]["units"])
    validate_split_integrity(manifest["track_b"]["units"])
    frozen = {
        row["issuer_id"]: row["split"]
        for row in _read_csv(ROOT / "dataset/corpus_freeze/issuer_split.csv")
    }
    for track in ("track_a", "track_b"):
        for row in manifest[track]["units"]:
            if row["issuer_id"] in frozen:
                assert frozen[row["issuer_id"]] == row["split"]
            else:
                assert track == "track_b"
                assert row["split"] == "UNASSIGNED_HISTORICAL"
                assert row["input_status"] == "INPUT_UNAVAILABLE"


def test_no_duplicate_physical_benchmark_units(manifest):
    page_keys = [(row["document_id"], row["page_number"]) for row in manifest["track_a"]["units"]]
    document_keys = [row["document_id"] for row in manifest["track_b"]["units"]]
    assert len(page_keys) == len(set(page_keys))
    assert len(document_keys) == len(set(document_keys))


def test_overlapping_condition_labels_are_one_physical_page(manifest):
    overlaps = [row for row in manifest["track_a"]["units"] if len(row["condition_labels"]) >= 3]
    assert overlaps
    assert all(isinstance(row["sampling_stratum"], str) for row in overlaps)
    assert all(set(row["condition_labels"]) == set(row["condition_evidence"]) for row in overlaps)


def test_manifest_rejects_duplicate_page(manifest):
    bad = copy.deepcopy(manifest)
    bad["track_a"]["units"].append(copy.deepcopy(bad["track_a"]["units"][0]))
    with pytest.raises(SetupInvariantError, match="duplicate physical"):
        validate_manifest(bad)


def test_cross_partition_issuer_fails_closed():
    with pytest.raises(SetupInvariantError, match="crosses"):
        validate_split_integrity([
            {"issuer_id": "ISSUER", "split": "FIT"},
            {"issuer_id": "ISSUER", "split": "HOLDOUT"},
        ])


@pytest.mark.parametrize("forbidden", sorted(FORBIDDEN_TRACK_A_KEYS))
def test_track_a_rejects_original_pdf_neighbors_and_extra_context(forbidden):
    request = {
        "document_id": "doc",
        "page_number": 1,
        "image_path": "page.png",
        "input_image_hash": "a" * 64,
        forbidden: "leak",
    }
    with pytest.raises(SetupInvariantError, match="forbidden context"):
        validate_track_a_request(request)


def test_track_a_checks_actual_image_hash(tmp_path):
    image = tmp_path / "page.png"
    image.write_bytes(b"immutable-page-image")
    request = {
        "document_id": "doc",
        "page_number": 1,
        "image_path": str(image),
        "input_image_hash": hashlib.sha256(image.read_bytes()).hexdigest(),
    }
    validate_track_a_request(request, verify_file=True)
    request["input_image_hash"] = "0" * 64
    with pytest.raises(SetupInvariantError, match="do not match"):
        validate_track_a_request(request, verify_file=True)


def test_primary_engines_require_identical_image_hash_and_no_fallback():
    rows = _engine_rows()
    validate_primary_engine_inputs(rows)
    rows[0]["input_image_hash"] = "b" * 64
    with pytest.raises(SetupInvariantError, match="identical"):
        validate_primary_engine_inputs(rows)
    rows = _engine_rows()
    rows[0]["fallback_engine"] = "tesseract_5_hindi"
    with pytest.raises(SetupInvariantError, match="fallback"):
        validate_primary_engine_inputs(rows)


def test_unrendered_hash_cannot_reach_an_engine():
    with pytest.raises(SetupInvariantError, match="finalized"):
        validate_primary_engine_inputs(_engine_rows(NOT_YET_RENDERED))


def test_common_adapter_uses_explicit_not_available_without_fabrication():
    adapted = adapt_engine_output(
        document_id="doc",
        page_number=3,
        engine_id="tesseract_5_hindi",
        input_image_hash="a" * 64,
        raw_output={"text": "hello"},
        raw_units=[{"text": "hello"}],
    )
    unit = adapted["units"][0]
    for field in ("block_id", "line_id", "bbox", "block_type", "reading_order", "confidence"):
        assert unit[field] == NOT_AVAILABLE
    assert unit["source_engine"] == "tesseract_5_hindi"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("bbox", [0, 0, 1]),
        ("bbox", [5, 0, 1, 2]),
        ("confidence", 1.2),
        ("reading_order", -1),
    ],
)
def test_common_adapter_rejects_fabricated_or_malformed_structure(field, value):
    with pytest.raises(SetupInvariantError):
        adapt_engine_output(
            document_id="doc",
            page_number=3,
            engine_id="tesseract_5_hindi",
            input_image_hash="a" * 64,
            raw_output={},
            raw_units=[{"text": "x", field: value}],
        )


def test_common_adapter_rejects_source_engine_mismatch():
    with pytest.raises(SetupInvariantError, match="source_engine"):
        adapt_engine_output(
            document_id="doc",
            page_number=3,
            engine_id="surya_2",
            input_image_hash="a" * 64,
            raw_output={},
            raw_units=[{"text": "x", "source_engine": "tesseract_5_hindi"}],
        )


def test_holdout_is_locked_before_final_freeze():
    validate_holdout_access("HOLDOUT", "manifest_predeclaration", final_freeze_complete=False)
    with pytest.raises(SetupInvariantError, match="locked"):
        validate_holdout_access("HOLDOUT", "tuning", final_freeze_complete=False)


def test_engine_registry_versions_and_image_mode_are_present():
    registry = read_json(CONFIG_DIR / "engine_registry.json")
    validate_engine_registry(registry)
    primary = [row for row in registry["engines"] if row["primary"]]
    assert len(primary) == 4
    assert all(row["version"] and row["installation_status"] for row in primary)


def test_missing_engine_version_fails():
    registry = read_json(CONFIG_DIR / "engine_registry.json")
    registry["engines"][0]["version"] = ""
    with pytest.raises(SetupInvariantError, match="no version"):
        validate_engine_registry(registry)


def test_configuration_hash_manifest_is_stable():
    first = config_hash_manifest(ROOT)
    second = config_hash_manifest(ROOT)
    assert first == second
    assert all(len(value) == 64 for value in first["files"].values())


def test_metric_schema_freezes_primary_endpoints_and_uncertainty():
    metrics = read_json(CONFIG_DIR / "metrics_spec.json")
    assert metrics["levels"]["A_OCR"]["primary"] == "CER"
    assert metrics["levels"]["B_DOCUMENT_STRUCTURE"]["primary"] == "pairwise_reading_order_accuracy"
    assert metrics["levels"]["C_ARPIPE_DOCUMENT_TASK"]["primary"] == "page_span_iou"
    assert metrics["uncertainty"]["confidence_level"] == 0.95
    assert metrics["uncertainty"]["track_a_cluster"] == "document_id"
    assert metrics["uncertainty"]["track_b_cluster"] == "issuer_id"
    assert metrics["no_composite_winner_score"] is True


def test_failure_taxonomy_is_specific_and_complete():
    taxonomy = read_json(CONFIG_DIR / "failure_taxonomy.json")
    codes = {row["code"] for row in taxonomy["failure_types"]}
    assert "OCR_FAILURE" not in codes
    assert {"INPUT_FAILURE", "MALFORMED_OUTPUT", "CANDIDATE_MISS", "SPAN_BOUNDARY_FAILURE"} <= codes


def test_oracle_routing_protocol_is_blind_and_preselected():
    oracle = read_json(CONFIG_DIR / "oracle_routing_spec.json")
    assert oracle["conditions"] == ["ACTUAL_ROUTING", "ORACLE_ROUTING"]
    assert oracle["subset_rule"]["frozen_before_engine_output"] is True
    assert oracle["double_annotation"]["selected_before_disagreement_observation"] is True
    assert oracle["adjudication"]["engine_outputs_forbidden"] is True


def test_gold_schema_separates_page_and_document_and_missing_status():
    schema = read_json(CONFIG_DIR / "gold_schema.json")
    assert {"page_gold", "document_gold"} <= set(schema["$defs"])
    assert "NOT_YET_ANNOTATED" in schema["$defs"]["annotation_status"]["enum"]
    assert "mda_end_page" not in schema["$defs"]["page_gold"]["properties"]


@pytest.mark.parametrize("leak", ["raw_output", "runtime_metrics", "metric_value", "engine_output"])
def test_benchmark_output_and_telemetry_cannot_be_gold(leak):
    record = {"gold_level": "PAGE", "annotation_status": "ANNOTATED", leak: {}}
    with pytest.raises(SetupInvariantError, match="leaked"):
        validate_gold_record(record)


def test_raw_output_provenance_and_telemetry_schemas_have_required_fields():
    raw = read_json(CONFIG_DIR / "raw_output_schema.json")
    efficiency = read_json(CONFIG_DIR / "efficiency_schema.json")
    assert {"raw_output", "raw_output_hash", "common_adapter_output", "adapter_version"} <= set(raw["required"])
    assert {"cold_start_seconds", "model_load_seconds", "warm_runtime_seconds", "peak_ram_bytes", "peak_vram_bytes"} <= set(efficiency["required"])


def test_cloud_output_must_be_replayed_not_regenerated():
    validate_cloud_replay(preserved_raw_output_exists=True, regenerate_requested=False)
    with pytest.raises(SetupInvariantError, match="replayed"):
        validate_cloud_replay(preserved_raw_output_exists=True, regenerate_requested=True)


def test_deterministic_manifest_has_no_absolute_path(manifest):
    assert not contains_absolute_path(canonical_json(manifest))
    assert contains_absolute_path('{"path":"C:\\\\Users\\\\person\\\\file"}')


def test_track_a_and_track_b_have_distinct_units_and_gold_contracts():
    config = read_json(CONFIG_DIR / "benchmark_config.json")
    assert config["track_a"]["benchmark_unit"] == ["document_id", "page_number"]
    assert config["track_b"]["benchmark_unit"] == ["document_id", "engine_route"]
    assert config["track_b"]["requires_full_document_context"] is True
    assert "span_resolution" in config["track_b"]["common_downstream_pipeline"]


def test_future_results_has_no_winner_or_composite_field():
    schema = read_json(CONFIG_DIR / "future_results_schema.json")
    properties = schema["properties"]
    assert "winner" not in properties
    assert "composite_score" not in properties


def test_fail_closed_setup_audit_passes():
    report = run_audit(ROOT)
    assert report["status"] == "PASS"
    assert all(value == "PASS" for value in report["checks"].values())
    assert report["execution_attestations"]["benchmark_executed"] is False
