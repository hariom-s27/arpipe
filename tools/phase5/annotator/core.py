"""Offline, repository-independent RAW Gold record validation and sealing."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path


SCHEMA_FILE = "gold_schema_v0_1.json"
PROTOCOL_FILE = "GOLD_PROTOCOL_v0_1.md"
PAGE_CONVENTION = "VIEWER_PHYSICAL_1_BASED_STORED_ZERO_BASED"
ROLES = ("ANNOTATOR_A", "ANNOTATOR_B")
ASSIGNMENT_COLUMNS = ("document_id", "source_pdf_sha256", "physical_page_count")
_ID = re.compile(r"[A-Za-z0-9._-]{1,256}\Z")
_HASH = re.compile(r"[0-9a-f]{64}\Z")


class AnnotationError(ValueError):
    """A refused workspace, assignment, record, or submission."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                       allow_nan=False) + "\n").encode("utf-8")


def check_workspace(bundle_root: Path, working_directory: Path | None = None) -> None:
    """Refuse a repository or prohibited material before starting the UI."""
    root = Path(bundle_root).resolve()
    cwd = Path(working_directory or Path.cwd()).resolve()
    if not root.is_dir() or not (root == cwd or root in cwd.parents):
        raise AnnotationError("Start the tool from inside the extracted bundle")
    for parent in (cwd, *cwd.parents):
        if (parent / ".git").exists():
            raise AnnotationError("Repository detected in working-directory ancestry")
    for path in root.rglob("*"):
        rel = tuple(part.lower() for part in path.relative_to(root).parts)
        if (path.is_dir() and path.name.lower() in {"arpipe", "reports"}) or (
            len(rel) >= 2 and any(rel[i:i + 2] == ("docs", "identity")
                                  for i in range(len(rel) - 1))
        ) or (path.is_file() and re.fullmatch(r"labels.*\.csv", path.name, re.I)):
            raise AnnotationError(f"Forbidden path in bundle: {path.relative_to(root)}")


def workspace_id(bundle_root: Path) -> str:
    path = Path(bundle_root) / "workspace_id.txt"
    if path.exists():
        value = path.read_text(encoding="utf-8").strip()
        try:
            uuid.UUID(value)
        except ValueError as exc:
            raise AnnotationError("Invalid workspace_id.txt") from exc
        return value
    value = str(uuid.uuid4())
    try:
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(value + "\n")
    except FileExistsError:
        return workspace_id(bundle_root)
    return value


def load_assignments(path: Path) -> dict[str, dict]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != ASSIGNMENT_COLUMNS:
            raise AnnotationError("Assignment columns must be exactly: " + ", ".join(ASSIGNMENT_COLUMNS))
        rows = {}
        for row in reader:
            document_id = row["document_id"]
            digest = row["source_pdf_sha256"]
            try:
                count = int(row["physical_page_count"])
            except (TypeError, ValueError) as exc:
                raise AnnotationError("Invalid physical_page_count") from exc
            if not _ID.fullmatch(document_id or "") or not _HASH.fullmatch(digest or "") or count < 1:
                raise AnnotationError("Invalid assignment row")
            if document_id in rows:
                raise AnnotationError("Duplicate document_id in assignments")
            rows[document_id] = {**row, "physical_page_count": count}
    return rows


def verify_source(path: Path, assignment: dict, viewer_page_count: int | None = None) -> str:
    if viewer_page_count is not None and viewer_page_count != assignment["physical_page_count"]:
        raise AnnotationError("Viewer page count differs from assignment")
    digest = sha256_file(path)
    if digest != assignment["source_pdf_sha256"]:
        raise AnnotationError("Selected file SHA-256 differs from assignment")
    return digest


def viewer_to_index(value: int | str, page_count: int) -> int:
    if isinstance(value, bool) or not str(value).strip().isdigit():
        raise AnnotationError("Enter a physical viewer page number")
    page = int(value)
    if not 1 <= page <= page_count:
        raise AnnotationError(f"Viewer page must be in [1, {page_count}]")
    return page - 1


def load_schema(bundle_root: Path) -> dict:
    return json.loads((Path(bundle_root) / SCHEMA_FILE).read_text(encoding="utf-8"))


def _check_page(value: object, count: int) -> None:
    if type(value) is not int or not 0 <= value < count:
        raise AnnotationError(f"Stored page must be in [0, {count - 1}]")


def _check_span(span: dict, count: int) -> None:
    _check_page(span["start_page"], count)
    _check_page(span["end_page"], count)
    if span["start_page"] > span["end_page"]:
        raise AnnotationError("Span start exceeds end")


def _sorted_unique(values: list, name: str) -> None:
    if values != sorted(set(values)):
        raise AnnotationError(f"{name} must be sorted and unique")


def validate_raw(record: dict, schema: dict, assignment: dict | None = None) -> None:
    try:
        import jsonschema
    except ImportError as exc:
        raise AnnotationError("jsonschema is required to submit") from exc
    try:
        jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(record)
    except jsonschema.ValidationError as exc:
        raise AnnotationError(f"Schema validation failed: {exc.message}") from exc
    if record["record_type"] != "RAW" or record["annotator_role"] not in ROLES:
        raise AnnotationError("Only RAW A/B records can be submitted")
    provenance = record["structured_provenance"]
    count = provenance["physical_page_count"]
    if assignment is not None and (
        record["document_id"] != assignment["document_id"]
        or record["source_pdf_sha256"] != assignment["source_pdf_sha256"]
        or count != assignment["physical_page_count"]
    ):
        raise AnnotationError("Record identity differs from assignment")
    primary = record["primary_span"]
    if primary is not None:
        _check_span(primary, count)
    for field in ("alternative_spans", "admissible_spans"):
        spans = record[field]
        for span in spans:
            _check_span(span, count)
        keys = [(span["start_page"], span["end_page"]) for span in spans]
        if keys != sorted(keys):
            raise AnnotationError(f"{field} must be in document order")
    for field in ("gap_pages",):
        _sorted_unique(record[field], field)
        for page in record[field]:
            _check_page(page, count)
    if record["gap_pages"]:
        if primary is None:
            raise AnnotationError("Gap pages require a primary hull")
        if any(not primary["start_page"] < page < primary["end_page"]
               for page in record["gap_pages"]):
            raise AnnotationError("Every gap must be strictly inside the primary hull")
    evidence = record["boundary_evidence"]
    for name in ("heading_start_page", "substantive_start_page", "last_content_page",
                 "next_section_heading_page", "mixed_end_page"):
        if evidence[name] is not None:
            _check_page(evidence[name], count)
    for edge, field in (("start_page", "viewer_start_page_1based"),
                        ("end_page", "viewer_end_page_1based")):
        viewer = evidence.get(field)
        if primary is None:
            if viewer is not None:
                raise AnnotationError("Viewer primary-page copy requires a primary span")
        elif viewer is None or viewer_to_index(viewer, count) != primary[edge]:
            raise AnnotationError("Viewer and stored primary pages disagree")
    if ("mixed_end_page" in record["flags"]) != (evidence["mixed_end_page"] is not None):
        raise AnnotationError("mixed_end_page flag and field disagree")
    if evidence["mixed_end_page"] is not None and primary is not None and evidence["mixed_end_page"] != primary["end_page"]:
        raise AnnotationError("Mixed end page must equal primary end")
    for field in ("bookmark_pages",):
        pages = provenance[field]
        _sorted_unique(pages, field)
        for page in pages:
            _check_page(page, count)
    for flag, pages in provenance["flag_pages"].items():
        if flag not in record["flags"]:
            raise AnnotationError("flag_pages key requires its flag")
        _sorted_unique(pages, "flag_pages")
        for page in pages:
            _check_page(page, count)
    if not provenance["annotation_workspace_id"]:
        raise AnnotationError("Missing workspace ID")
    try:
        started = datetime.fromisoformat(record["timestamps"]["started_at"].replace("Z", "+00:00"))
        completed = datetime.fromisoformat(record["timestamps"]["completed_at"].replace("Z", "+00:00"))
    except ValueError as exc:
        raise AnnotationError("Invalid timestamp") from exc
    if completed < started:
        raise AnnotationError("Completion precedes start")
    if record["presence_state"] == "AMBIGUOUS" and record["presence_reason_code"] != record["ambiguity_code"]:
        raise AnnotationError("Ambiguity reason and code disagree")


def _role_files(root: Path, document_id: str, role: str) -> tuple[list[tuple[Path, str]], list[dict]]:
    folder = root / "records" / role
    raw = []
    controls = []
    if folder.exists():
        paths = {path.name: path for path in folder.glob("*.json")}
        log = root / "records" / "HASH_LOG.txt"
        if not log.is_file():
            raise AnnotationError("Role files exist without HASH_LOG.txt")
        seen = set()
        for line in log.read_text(encoding="utf-8").splitlines():
            match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9._-]+\.json)", line)
            if not match:
                raise AnnotationError("Malformed HASH_LOG.txt")
            logged_hash, name = match.groups()
            if name not in paths:
                continue
            if name in seen:
                raise AnnotationError("Duplicate role file in HASH_LOG.txt")
            seen.add(name)
            path = paths[name]
            data = path.read_bytes()
            value = json.loads(data)
            digest = hashlib.sha256(data).hexdigest()
            if digest != logged_hash:
                raise AnnotationError("Sealed role file differs from HASH_LOG.txt")
            if value.get("document_id") != document_id or value.get("annotator_role") != role:
                continue
            if value.get("record_type") == "RAW":
                raw.append((path, digest))
            elif value.get("record_type") == "SUPERSEDE":
                controls.append(value)
        if seen != set(paths):
            raise AnnotationError("Role file missing from HASH_LOG.txt")
    return raw, controls


def _write_sealed(root: Path, role: str, filename: str, data: bytes) -> tuple[Path, str]:
    folder = root / "records" / role
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / filename
    with path.open("xb") as stream:
        stream.write(data)
    path.chmod(0o444)
    digest = hashlib.sha256(data).hexdigest()
    with (root / "records" / "HASH_LOG.txt").open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(f"{digest}  {filename}\n")
    return path, digest


def create_supersede(root: Path, document_id: str, role: str, old_hash: str, reason: str) -> tuple[Path, str]:
    if role not in ROLES or not _ID.fullmatch(document_id) or not _HASH.fullmatch(old_hash):
        raise AnnotationError("Invalid supersede identity")
    if not reason.strip():
        raise AnnotationError("Supersede reason is required")
    if (Path(root) / "records" / "COMPARISON_LOCKED").exists():
        raise AnnotationError("Comparison already locked; raw supersession is closed")
    raw, controls = _role_files(Path(root), document_id, role)
    if not raw or len(raw) != len(controls) + 1 or raw[-1][1] != old_hash:
        raise AnnotationError("Old hash is not the latest eligible raw record")
    control = {"record_type": "SUPERSEDE", "document_id": document_id,
               "annotator_role": role, "old_sha256": old_hash, "reason": reason.strip(),
               "created_at": datetime.now(timezone.utc).isoformat()}
    data = canonical_bytes(control)
    digest = hashlib.sha256(data).hexdigest()
    return _write_sealed(Path(root), role, f"{document_id}__{role}__supersede__{digest[:8]}.json", data)


def submit_raw(root: Path, record: dict, assignment: dict, source_path: Path,
               viewer_page_count: int, schema: dict) -> tuple[Path, str]:
    root = Path(root)
    if (root / "records" / "COMPARISON_LOCKED").exists():
        raise AnnotationError("Comparison already locked; raw submission is closed")
    verify_source(source_path, assignment, viewer_page_count)
    validate_raw(record, schema, assignment)
    if record["protocol_version_hash"] != sha256_file(root / PROTOCOL_FILE):
        raise AnnotationError("Protocol hash does not match the bundle")
    if record["structured_provenance"]["annotation_workspace_id"] != workspace_id(root):
        raise AnnotationError("Workspace ID does not match the bundle")
    role = record["annotator_role"]
    document_id = record["document_id"]
    raw, controls = _role_files(root, document_id, role)
    if controls and not raw:
        raise AnnotationError("Supersede exists without a RAW record")
    if raw and (len(controls) != len(raw) or controls[-1]["old_sha256"] != raw[-1][1]):
        raise AnnotationError("A second submission requires an explicit supersede record")
    data = canonical_bytes(record)
    digest = hashlib.sha256(data).hexdigest()
    return _write_sealed(root, role, f"{document_id}__{role}__{digest[:8]}.json", data)
