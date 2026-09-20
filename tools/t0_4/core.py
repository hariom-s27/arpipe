"""Deterministic T0.4 manifest construction and setup validation.

Only frozen metadata is read. This module does not open PDFs, render pages,
probe engines, call APIs, or produce benchmark results.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

BASE_COMMIT = "ff030d97c13c8a2a977521bf91be2aca0cbf3034"
SCHEMA_VERSION = "1.0.0"
NOT_AVAILABLE = "NOT_AVAILABLE"
NOT_YET_ANNOTATED = "NOT_YET_ANNOTATED"
NOT_YET_RENDERED = "NOT_YET_RENDERED"

PRIMARY_ENGINES = (
    "tesseract_5_hindi",
    "paddleocr_vl_1_6",
    "surya_2",
    "gemini_2_5_flash_lite",
)

SOURCE_FILES = (
    "dataset/corpus_freeze/corpus_inventory.csv",
    "dataset/corpus_freeze/issuer_split.csv",
    "dataset/corpus_freeze/page_profile.csv",
    "dataset/corpus_gap_audit/condition_page_map.csv",
    "dataset/corpus_gap_audit/table_candidates.csv",
    "dataset/corpus_gap_audit/language_candidates.csv",
)

CONFIG_FILES = (
    "benchmark_config.json",
    "benchmark_manifest_schema.json",
    "common_output_schema.json",
    "efficiency_schema.json",
    "engine_registry.json",
    "failure_taxonomy.json",
    "future_results_schema.json",
    "gold_schema.json",
    "metrics_spec.json",
    "oracle_routing_spec.json",
    "raw_output_schema.json",
    "sampling_spec.json",
)

PROTECTED_PATHS = (
    "arpipe",
    "configs/t0_1r",
    "configs/t0_3a",
    "configs/t0_3a_r1",
    "dataset/corpus_freeze",
    "dataset/corpus_gap_audit",
    "tests/t0_1",
    "tests/t0_2",
    "tests/t0_3a",
    "tests/t0_3a_r1",
    "tools/run_t0_2_robustness_gate.py",
    "tools/run_t0_3a_document_coverage.py",
    "tools/run_t0_3a_r1_document_coverage.py",
)

DOC_CONDITION_COLUMNS = (
    "native",
    "scanned",
    "mixed",
    "legacy_font",
    "OCR_layer",
    "hidden_text",
    "duplicate_text",
    "bilingual",
    "Devanagari",
    "two_column",
    "multi_column",
    "table_heavy",
    "long_report",
    "short_report",
    "vector_text_pages",
    "visual_text_disagreement",
    "deep_hierarchy",
    "annexure",
    "combined_mda",
    "unusual_heading",
)

STRATUM_PRIORITY = (
    "devanagari_candidate",
    "legacy_font_candidate",
    "vector_text",
    "broken_text",
    "scanned",
    "ocr_layer_proxy",
    "table_candidate",
    "multi_column",
    "pre_2015",
    "native_clean_control",
    "other",
)

SPLIT_ROLES = {
    "FIT": "FIT_TUNING",
    "VALIDATION": "VALIDATION_PRE_FREEZE",
    "HOLDOUT": "FINAL_HOLDOUT_LOCKED",
}


class SetupInvariantError(ValueError):
    """Raised when a preregistered setup invariant is violated."""


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def object_sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def write_canonical_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(value), encoding="utf-8", newline="\n")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def is_true(value: Any) -> bool:
    return str(value).strip().lower() == "true"


def require_relative_posix(path: str) -> None:
    if not path or "\\" in path or Path(path).is_absolute() or re.match(r"^[A-Za-z]:", path):
        raise SetupInvariantError(f"deterministic artifact path must be relative POSIX: {path!r}")


def verify_base_ancestor(repo_root: Path) -> str:
    head = subprocess.check_output(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"], text=True
    ).strip()
    merge_base = subprocess.check_output(
        ["git", "-C", str(repo_root), "merge-base", head, BASE_COMMIT], text=True
    ).strip()
    if merge_base != BASE_COMMIT:
        raise SetupInvariantError(
            f"wrong base: expected ancestor {BASE_COMMIT}, got merge-base {merge_base}"
        )
    return head


def verify_protected_paths_unchanged(repo_root: Path) -> None:
    command = ["git", "-C", str(repo_root), "diff", "--name-only", BASE_COMMIT, "--", *PROTECTED_PATHS]
    changed = subprocess.check_output(command, text=True).strip().splitlines()
    if changed:
        raise SetupInvariantError(f"frozen historical paths changed: {changed}")


def config_hash_manifest(repo_root: Path) -> dict[str, Any]:
    config_dir = repo_root / "configs" / "t0_4"
    hashes: dict[str, str] = {}
    for name in CONFIG_FILES:
        path = config_dir / name
        if not path.is_file():
            raise SetupInvariantError(f"missing T0.4 config: {path.relative_to(repo_root)}")
        rel = path.relative_to(repo_root).as_posix()
        hashes[rel] = file_sha256(path)
    return {"schema_version": SCHEMA_VERSION, "files": dict(sorted(hashes.items()))}


def validate_engine_registry(registry: Mapping[str, Any]) -> None:
    declared = tuple(registry.get("primary_engine_ids", []))
    if declared != PRIMARY_ENGINES:
        raise SetupInvariantError(f"primary engine registry mismatch: {declared}")
    records = {record.get("engine_id"): record for record in registry.get("engines", [])}
    required = {
        "engine_id", "engine_family", "engine_type", "version", "model_or_checkpoint",
        "runtime", "input_mode", "input_format", "output_format", "layout_support",
        "reading_order_support", "table_support", "confidence_support", "local_or_cloud",
        "installation_status", "python_version", "cuda_version", "hardware_requirements",
        "checkpoint_hash", "primary",
    }
    for engine_id in PRIMARY_ENGINES:
        record = records.get(engine_id)
        if record is None:
            raise SetupInvariantError(f"missing primary engine: {engine_id}")
        missing = required - set(record)
        if missing:
            raise SetupInvariantError(f"engine {engine_id} missing fields: {sorted(missing)}")
        if not str(record["version"]).strip():
            raise SetupInvariantError(f"engine {engine_id} has no version")
        if record["input_mode"] != "single rendered page image":
            raise SetupInvariantError(f"engine {engine_id} violates Track-A image-only input")


def validate_config_set(repo_root: Path) -> dict[str, Any]:
    parsed = {name: read_json(repo_root / "configs" / "t0_4" / name) for name in CONFIG_FILES}
    benchmark = parsed["benchmark_config.json"]
    if benchmark.get("base_commit") != BASE_COMMIT:
        raise SetupInvariantError("benchmark_config base commit mismatch")
    if benchmark.get("execution_policy") != "SETUP_ONLY_DO_NOT_EXECUTE_BENCHMARK":
        raise SetupInvariantError("benchmark execution is not disabled")
    if benchmark["track_a"]["input_mode"] != "IMMUTABLE_RENDERED_PAGE_IMAGE_ONLY":
        raise SetupInvariantError("Track A is not image-only")
    if benchmark["track_a"]["primary_endpoint"] != "CER":
        raise SetupInvariantError("Track A primary endpoint must be CER")
    if benchmark["track_b"]["primary_endpoint"] != "page_span_iou":
        raise SetupInvariantError("Track B primary endpoint must be page-span IoU")
    validate_engine_registry(parsed["engine_registry.json"])

    metrics = parsed["metrics_spec.json"]
    if not metrics.get("no_composite_winner_score"):
        raise SetupInvariantError("composite winner score must be prohibited")
    if metrics["levels"]["B_DOCUMENT_STRUCTURE"]["primary"] != "pairwise_reading_order_accuracy":
        raise SetupInvariantError("pairwise reading order must be the structure primary")
    uncertainty = metrics.get("uncertainty", {})
    if uncertainty.get("confidence_level") != 0.95 or uncertainty.get("replicates") != 10000:
        raise SetupInvariantError("95% 10,000-replicate uncertainty plan is not frozen")

    failure_codes = [item.get("code") for item in parsed["failure_taxonomy.json"].get("failure_types", [])]
    if len(failure_codes) != len(set(failure_codes)) or "OCR_FAILURE" in failure_codes:
        raise SetupInvariantError("failure taxonomy is duplicated or overly generic")
    required_failures = {
        "INPUT_FAILURE", "ENGINE_LOAD_FAILURE", "MODEL_LOAD_FAILURE", "TIMEOUT",
        "API_ERROR", "RATE_LIMIT", "EMPTY_OUTPUT", "MALFORMED_OUTPUT", "OCR_GARBLED",
        "READING_ORDER_FAILURE", "HEADING_FAILURE", "CANDIDATE_MISS",
        "SPAN_BOUNDARY_FAILURE", "VERIFIER_FALSE_ACCEPT", "VERIFIER_FALSE_REJECT",
    }
    if set(failure_codes) != required_failures:
        raise SetupInvariantError("failure taxonomy does not match preregistration")

    oracle = parsed["oracle_routing_spec.json"]
    if oracle.get("conditions") != ["ACTUAL_ROUTING", "ORACLE_ROUTING"]:
        raise SetupInvariantError("oracle-routing conditions invalid")
    if not oracle["adjudication"].get("engine_outputs_forbidden"):
        raise SetupInvariantError("engine outputs must be forbidden during oracle annotation")
    return parsed


def _page_auxiliary_sets(repo_root: Path) -> tuple[dict[tuple[str, int], set[str]], set[tuple[str, int]], dict[tuple[str, int], set[str]]]:
    labels: dict[tuple[str, int], set[str]] = {}
    table_pages: set[tuple[str, int]] = set()
    language: dict[tuple[str, int], set[str]] = {}

    for row in read_csv(repo_root / "dataset/corpus_gap_audit/condition_page_map.csv"):
        key = (row["document_id"], int(row["page_index"]))
        labels.setdefault(key, set()).add(row["condition"])
    for row in read_csv(repo_root / "dataset/corpus_gap_audit/table_candidates.csv"):
        if row.get("detector_status") == "CANDIDATE":
            table_pages.add((row["document_id"], int(row["page_index"])))
    for row in read_csv(repo_root / "dataset/corpus_gap_audit/language_candidates.csv"):
        key = (row["document_id"], int(row["page_index"]))
        page_labels = language.setdefault(key, set())
        if is_true(row.get("is_hindi_page")):
            page_labels.add("devanagari_candidate")
        if is_true(row.get("is_bilingual_page")):
            page_labels.add("bilingual_candidate")
    return labels, table_pages, language


def _length_category(doc: Mapping[str, str]) -> str:
    if is_true(doc.get("short_report")):
        return "short"
    if is_true(doc.get("long_report")):
        return "long"
    return "medium"


def _representation_class(kind: str) -> str:
    return {
        "digital": "native_ok",
        "broken_text": "broken_text",
        "scanned": "scanned",
        "vector_text": "vector_text",
        "hybrid": "hybrid",
        "blank": "blank",
    }.get(kind, "other")


def _page_conditions(
    profile: Mapping[str, str],
    fiscal_year: int,
    auxiliary: set[str],
    is_table_page: bool,
    language: set[str],
) -> tuple[list[str], dict[str, str]]:
    labels: set[str] = set(language)
    kind = profile.get("kind", "other")
    representation = _representation_class(kind)
    labels.add(representation)
    if int(profile.get("n_columns") or 0) >= 2:
        labels.add("multi_column")
    if fiscal_year < 2015:
        labels.add("pre_2015")
    if is_true(profile.get("render_mode_ocr_layer_indicator")):
        labels.add("ocr_layer_proxy")
    if is_true(profile.get("cid_or_broken_text_indicator")):
        labels.add("legacy_font_candidate")
    if is_table_page:
        labels.add("table_candidate")
    mapped = {
        "devanagari_page": "devanagari_candidate",
        "native_page": "native_ok",
        "ocr_layer_page": "ocr_layer_proxy",
        "scanned_page": "scanned",
        "two_column_page": "multi_column",
    }
    labels.update(mapped.get(value, value) for value in auxiliary)
    evidence = {
        label: ("VALIDATED_METADATA" if label == "pre_2015" else "CANDIDATE_PROXY")
        for label in sorted(labels)
    }
    return sorted(labels), evidence


def _sampling_stratum(labels: Sequence[str]) -> str:
    label_set = set(labels)
    for stratum in STRATUM_PRIORITY:
        if stratum == "native_clean_control" and "native_ok" in label_set:
            return stratum
        if stratum == "other":
            return stratum
        if stratum in label_set:
            return stratum
    raise AssertionError("unreachable sampling-stratum selection")


def _selection_rank(seed: str, document_id: str, page_number: int) -> str:
    payload = f"{seed}\x00{document_id}\x00{page_number}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_manifest(repo_root: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    config = read_json(repo_root / "configs/t0_4/sampling_spec.json")
    seed = config["sampling_seed"]
    inventory = read_csv(repo_root / "dataset/corpus_freeze/corpus_inventory.csv")
    profiles = read_csv(repo_root / "dataset/corpus_freeze/page_profile.csv")
    issuer_rows = read_csv(repo_root / "dataset/corpus_freeze/issuer_split.csv")
    auxiliary, table_pages, language_pages = _page_auxiliary_sets(repo_root)

    issuer_split = {row["issuer_id"]: row["split"] for row in issuer_rows}
    if set(issuer_split.values()) != set(SPLIT_ROLES):
        raise SetupInvariantError("unexpected frozen split vocabulary")
    documents = {row["document_id"]: row for row in inventory}
    profiled_documents = {row["document_id"] for row in profiles}

    candidates: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    for profile in profiles:
        document_id = profile["document_id"]
        doc = documents.get(document_id)
        if doc is None:
            raise SetupInvariantError(f"page profile has unknown document: {document_id}")
        issuer_id = doc["company_id"]
        split = issuer_split.get(issuer_id)
        if split is None:
            raise SetupInvariantError(f"document issuer has no frozen split: {document_id}")
        page_number = int(profile["physical_page"])
        fiscal_year = int(doc["fiscal_year"])
        key = (document_id, page_number)
        labels, evidence = _page_conditions(
            profile,
            fiscal_year,
            auxiliary.get(key, set()),
            key in table_pages,
            language_pages.get(key, set()),
        )
        representation = _representation_class(profile.get("kind", "other"))
        era = "pre_2015" if fiscal_year < 2015 else "post_2015"
        length = _length_category(doc)
        stratum = _sampling_stratum(labels)
        rank = _selection_rank(seed, document_id, page_number)
        unit = {
            "document_id": document_id,
            "issuer_id": issuer_id,
            "fiscal_year": fiscal_year,
            "page_number": page_number,
            "split": split,
            "sampling_stratum": stratum,
            "condition_labels": labels,
            "condition_evidence": evidence,
            "representation_class": representation,
            "era": era,
            "length_category": length,
            "benchmark_role": SPLIT_ROLES[split],
            "source_pdf_sha256": doc["pdf_sha256"],
            "input_image_hash": NOT_YET_RENDERED,
            "selection_rank": rank,
        }
        coverage_cell = (issuer_id, stratum, era, representation, length)
        incumbent = candidates.get(coverage_cell)
        if incumbent is None or (rank, document_id, page_number) < (
            incumbent["selection_rank"], incumbent["document_id"], incumbent["page_number"]
        ):
            candidates[coverage_cell] = unit

    track_a_units = sorted(
        candidates.values(), key=lambda row: (row["split"], row["issuer_id"], row["document_id"], row["page_number"])
    )

    track_b_units: list[dict[str, Any]] = []
    for doc in inventory:
        issuer_id = doc["company_id"]
        split = issuer_split.get(issuer_id)
        input_available = doc["document_id"] in profiled_documents
        if split is None:
            if input_available:
                raise SetupInvariantError(f"executable document issuer has no frozen split: {doc['document_id']}")
            split = "UNASSIGNED_HISTORICAL"
        fiscal_year = int(doc["fiscal_year"])
        conditions = sorted(column for column in DOC_CONDITION_COLUMNS if is_true(doc.get(column)))
        conditions.extend(["pre_2015" if fiscal_year < 2015 else "post_2015", f"length_{_length_category(doc)}"])
        track_b_units.append({
            "document_id": doc["document_id"],
            "issuer_id": issuer_id,
            "fiscal_year": fiscal_year,
            "split": split,
            "benchmark_role": SPLIT_ROLES[split] if input_available else "INPUT_UNAVAILABLE",
            "document_conditions": sorted(set(conditions)),
            "input_status": "PROFILED_LOCAL_INPUT" if input_available else "INPUT_UNAVAILABLE",
            "source_pdf_sha256": doc["pdf_sha256"],
        })
    track_b_units.sort(key=lambda row: (row["split"], row["issuer_id"], row["fiscal_year"], row["document_id"]))

    split_counts_a = Counter(row["split"] for row in track_a_units)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "base_commit": BASE_COMMIT,
        "source_hashes": {
            rel: file_sha256(repo_root / rel) for rel in sorted(SOURCE_FILES)
        },
        "track_a": {"unit_key": ["document_id", "page_number"], "units": track_a_units},
        "track_b": {"unit_key": ["document_id"], "units": track_b_units},
        "derived_counts": {
            "frozen_records": len(inventory),
            "profiled_documents": len(profiled_documents),
            "input_unavailable_documents": len(inventory) - len(profiled_documents),
            "profiled_pages": len(profiles),
            "track_a_units": len(track_a_units),
            "track_a_fit_units": split_counts_a["FIT"],
            "track_a_validation_units": split_counts_a["VALIDATION"],
            "track_a_holdout_units": split_counts_a["HOLDOUT"],
            "track_b_units": len(track_b_units),
        },
    }
    validate_manifest(manifest, issuer_split)
    return manifest


def validate_split_integrity(units: Iterable[Mapping[str, Any]]) -> None:
    seen: dict[str, str] = {}
    for unit in units:
        issuer = str(unit["issuer_id"])
        split = str(unit["split"])
        prior = seen.setdefault(issuer, split)
        if prior != split:
            raise SetupInvariantError(f"issuer {issuer} crosses {prior} and {split}")


def validate_manifest(manifest: Mapping[str, Any], issuer_split: Mapping[str, str] | None = None) -> None:
    if manifest.get("base_commit") != BASE_COMMIT:
        raise SetupInvariantError("manifest base commit mismatch")
    track_a = list(manifest["track_a"]["units"])
    track_b = list(manifest["track_b"]["units"])
    page_keys = [(row["document_id"], row["page_number"]) for row in track_a]
    if len(page_keys) != len(set(page_keys)):
        raise SetupInvariantError("duplicate physical Track-A benchmark page")
    doc_keys = [row["document_id"] for row in track_b]
    if len(doc_keys) != len(set(doc_keys)):
        raise SetupInvariantError("duplicate Track-B benchmark document")
    validate_split_integrity(track_a)
    validate_split_integrity(track_b)
    for row in track_a:
        labels = row["condition_labels"]
        if labels != sorted(set(labels)):
            raise SetupInvariantError("condition labels must be sorted and unique")
        if set(labels) != set(row["condition_evidence"]):
            raise SetupInvariantError("every condition label requires explicit evidence level")
        if row["input_image_hash"] != NOT_YET_RENDERED:
            raise SetupInvariantError("setup manifest must not claim an unrendered image hash")
        if issuer_split is not None and issuer_split.get(row["issuer_id"]) != row["split"]:
            raise SetupInvariantError("Track-A split differs from frozen issuer split")
    for row in track_b:
        if issuer_split is not None:
            frozen_split = issuer_split.get(row["issuer_id"])
            if frozen_split is None:
                if row["split"] != "UNASSIGNED_HISTORICAL" or row["input_status"] != "INPUT_UNAVAILABLE":
                    raise SetupInvariantError("unassigned history must remain unavailable and unassigned")
            elif frozen_split != row["split"]:
                raise SetupInvariantError("Track-B split differs from frozen issuer split")


def deterministic_repeat(repo_root: Path) -> tuple[str, str]:
    first = canonical_json(build_manifest(repo_root))
    second = canonical_json(build_manifest(repo_root))
    first_hash = hashlib.sha256(first.encode("utf-8")).hexdigest()
    second_hash = hashlib.sha256(second.encode("utf-8")).hexdigest()
    if first != second:
        raise SetupInvariantError("manifest generation is not byte-for-byte deterministic")
    return first_hash, second_hash


def contains_absolute_path(text: str) -> bool:
    patterns = (
        r"(?i)(?:^|[\"'\s])[A-Z]:[\\/]",
        r"(?:^|[\"'\s])/(?:home|Users|tmp|var/tmp)/",
    )
    return any(re.search(pattern, text) for pattern in patterns)


def validate_gold_record(record: Mapping[str, Any]) -> None:
    """Keep human gold structurally separate from outputs and telemetry."""
    forbidden = {
        "engine_id", "engine_output", "raw_output", "raw_output_hash",
        "common_adapter_output", "runtime_metrics", "telemetry", "metric_value",
        "execution_status", "configuration_hash",
    }
    leaked = forbidden.intersection(record)
    if leaked:
        raise SetupInvariantError(f"non-gold data leaked into gold: {sorted(leaked)}")
    if record.get("gold_level") not in {"PAGE", "DOCUMENT"}:
        raise SetupInvariantError("gold_level must be PAGE or DOCUMENT")
    if record.get("annotation_status") not in {"ANNOTATED", NOT_YET_ANNOTATED}:
        raise SetupInvariantError("gold annotation_status is invalid")
