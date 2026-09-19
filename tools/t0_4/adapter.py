"""Track-A invocation gates and the common ARPipe output adapter."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .core import NOT_AVAILABLE, NOT_YET_RENDERED, PRIMARY_ENGINES, SetupInvariantError

ADAPTER_VERSION = "1.0.0"
FORBIDDEN_TRACK_A_KEYS = {
    "pdf",
    "pdf_path",
    "original_pdf",
    "neighboring_pages",
    "previous_page",
    "following_page",
    "document_text",
    "hidden_pdf_text",
    "bookmarks",
    "toc",
    "external_metadata",
    "prior_engine_output",
    "page_context",
}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def validate_track_a_request(request: Mapping[str, Any], *, verify_file: bool = False) -> None:
    leaked = FORBIDDEN_TRACK_A_KEYS.intersection(request)
    if leaked:
        raise SetupInvariantError(f"Track A received forbidden context: {sorted(leaked)}")
    required = {"document_id", "page_number", "image_path", "input_image_hash"}
    missing = required - set(request)
    if missing:
        raise SetupInvariantError(f"Track A request missing: {sorted(missing)}")
    image_path = Path(str(request["image_path"]))
    if image_path.suffix.lower() != ".png":
        raise SetupInvariantError("Track A accepts only the frozen PNG page image")
    image_hash = str(request["input_image_hash"])
    if image_hash == NOT_YET_RENDERED or len(image_hash) != 64:
        raise SetupInvariantError("Track A requires a finalized 64-character image SHA-256")
    if verify_file:
        actual = sha256_bytes(image_path.read_bytes())
        if actual != image_hash:
            raise SetupInvariantError("Track A image bytes do not match input_image_hash")


def validate_primary_engine_inputs(records: Iterable[Mapping[str, Any]]) -> None:
    grouped: dict[tuple[str, int], list[Mapping[str, Any]]] = {}
    for record in records:
        key = (str(record["document_id"]), int(record["page_number"]))
        grouped.setdefault(key, []).append(record)
    for key, group in grouped.items():
        engines = [str(row["engine_id"]) for row in group]
        if sorted(engines) != sorted(PRIMARY_ENGINES):
            raise SetupInvariantError(f"{key} does not have exactly the four primary engines")
        hashes = {str(row["input_image_hash"]) for row in group}
        if len(hashes) != 1 or NOT_YET_RENDERED in hashes:
            raise SetupInvariantError(f"{key} does not use one identical finalized image hash")
        if any(row.get("fallback_engine") not in (None, NOT_AVAILABLE) for row in group):
            raise SetupInvariantError(f"{key} contains a silent engine fallback")


def _optional(raw: Mapping[str, Any], key: str) -> Any:
    value = raw.get(key, NOT_AVAILABLE)
    return NOT_AVAILABLE if value is None else value


def _validate_bbox(value: Any) -> Any:
    if value == NOT_AVAILABLE:
        return value
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or len(value) != 4:
        raise SetupInvariantError("bbox must be four numeric coordinates or NOT_AVAILABLE")
    if not all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in value):
        raise SetupInvariantError("bbox coordinates must be numeric")
    if value[2] < value[0] or value[3] < value[1]:
        raise SetupInvariantError("bbox coordinates are inverted")
    return list(value)


def _validate_confidence(value: Any) -> Any:
    if value == NOT_AVAILABLE:
        return value
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1:
        raise SetupInvariantError("confidence must be within [0, 1] or NOT_AVAILABLE")
    return value


def _validate_reading_order(value: Any) -> Any:
    if value == NOT_AVAILABLE:
        return value
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise SetupInvariantError("reading_order must be a non-negative integer or NOT_AVAILABLE")
    return value


def adapt_engine_output(
    *,
    document_id: str,
    page_number: int,
    engine_id: str,
    input_image_hash: str,
    raw_output: Any,
    raw_units: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Adapt actual engine fields without synthesizing unsupported structure."""
    if engine_id not in PRIMARY_ENGINES:
        raise SetupInvariantError(f"unknown primary engine: {engine_id}")
    if len(input_image_hash) != 64 or input_image_hash == NOT_YET_RENDERED:
        raise SetupInvariantError("common adaptation requires a finalized input image hash")
    raw_bytes = json.dumps(raw_output, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    units: list[dict[str, Any]] = []
    for raw in raw_units:
        claimed_engine = raw.get("source_engine", engine_id)
        if claimed_engine != engine_id:
            raise SetupInvariantError("unit source_engine differs from invoked engine")
        raw_page = raw.get("page", page_number)
        if raw_page != page_number:
            raise SetupInvariantError("adapter unit page differs from invocation page")
        units.append({
            "page": page_number,
            "block_id": _optional(raw, "block_id"),
            "line_id": _optional(raw, "line_id"),
            "text": str(raw.get("text", "")),
            "bbox": _validate_bbox(_optional(raw, "bbox")),
            "block_type": _optional(raw, "block_type"),
            "reading_order": _validate_reading_order(_optional(raw, "reading_order")),
            "confidence": _validate_confidence(_optional(raw, "confidence")),
            "source_engine": engine_id,
        })
    return {
        "adapter_version": ADAPTER_VERSION,
        "source_engine": engine_id,
        "document_id": document_id,
        "page": page_number,
        "input_image_hash": input_image_hash,
        "raw_output_hash": sha256_bytes(raw_bytes),
        "units": units,
    }


def validate_holdout_access(split: str, purpose: str, *, final_freeze_complete: bool) -> None:
    forbidden = {
        "tuning", "threshold_selection", "engine_selection", "sampling_change",
        "error_driven_methodology_change", "benchmark_execution",
    }
    if split == "HOLDOUT" and purpose in forbidden and not final_freeze_complete:
        raise SetupInvariantError(f"HOLDOUT is locked before final freeze: {purpose}")


def validate_cloud_replay(*, preserved_raw_output_exists: bool, regenerate_requested: bool) -> None:
    if preserved_raw_output_exists and regenerate_requested:
        raise SetupInvariantError("preserved cloud output must be replayed, not regenerated")
