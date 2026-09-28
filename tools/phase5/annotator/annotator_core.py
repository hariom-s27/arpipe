"""Core logic for the offline ARPipe Gold annotation tool (P5-T).

Standard library only, plus ``jsonschema`` for validation. This module has no GUI,
no network code and no PDF rendering. It never imports anything from ``arpipe/``.

Status: DRAFT_PENDING_PILOT. Implements GOLD_PROTOCOL v0.1 sections 2, 7-9 and
GOLD_SCHEMA v0.2 sections 1-3 for RAW records.

Page convention (GOLD_PROTOCOL v0.1 section 2): annotators type the viewer's
1-based physical page number (page labels disabled). The tool stores
``page_index_0based = viewer_page_1based - 1``.
"""

from __future__ import annotations

import csv
import datetime as _dt
import hashlib
import json
import os
import re
import secrets
import stat
from pathlib import Path
from typing import Any, Iterable

TOOL_VERSION = "p5t-0.1.0"
SCHEMA_FILENAME = "gold_schema_v0_2.json"
PROTOCOL_FILENAME = "GOLD_PROTOCOL_v0_1.md"
VIEWER_PAGE_CONVENTION = "VIEWER_PHYSICAL_1_BASED_STORED_ZERO_BASED"
RAW_ROLES = ("ANNOTATOR_A", "ANNOTATOR_B")
HASH_LOG_NAME = "HASH_LOG.txt"
WORKSPACE_ID_NAME = "WORKSPACE_ID.txt"
EXPORT_LOCK_NAME = "EXPORTED.lock"
TITLE_LIST_PLACEHOLDER = "TITLE_LIST_NOT_YET_FROZEN.txt"
ASSIGNMENT_COLUMNS = ["document_id", "source_pdf_sha256", "physical_page_count"]

DOC_ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

# Directory names / relative paths whose presence under the bundle root means the
# workspace is not isolated from the repository or from system output.
FORBIDDEN_DIR_NAMES = ("arpipe", "reports")
FORBIDDEN_REL_DIRS = (("docs", "identity"),)
FORBIDDEN_FILE_RE = re.compile(r"^labels.*\.csv$", re.IGNORECASE)


class AnnotatorError(Exception):
    """Any refusal by the tool. The message is shown to the annotator verbatim."""


class SchemaUnavailable(AnnotatorError):
    """``jsonschema`` cannot be imported, so records cannot be submitted."""


# ---------------------------------------------------------------------------
# Workspace isolation
# ---------------------------------------------------------------------------

def workspace_refusals(bundle_root: Path, cwd: Path | None = None) -> list[str]:
    """Return every reason the tool must refuse to start (empty list = OK).

    Refuses when the working directory or the bundle root, or any parent of either,
    contains ``.git``; or when ``arpipe/``, ``reports/``, ``docs/identity/`` or a
    ``labels*.csv`` file exists anywhere under the bundle root.
    """
    reasons: list[str] = []
    bundle_root = Path(bundle_root).resolve()
    starts = [bundle_root]
    if cwd is not None:
        starts.append(Path(cwd).resolve())
    seen: set[Path] = set()
    for start in starts:
        for directory in (start, *start.parents):
            if directory in seen:
                continue
            seen.add(directory)
            if (directory / ".git").exists():
                reasons.append(f"repository marker found: {directory / '.git'}")
    for dirpath, dirnames, filenames in os.walk(bundle_root):
        here = Path(dirpath)
        for name in dirnames:
            if name in FORBIDDEN_DIR_NAMES:
                reasons.append(f"forbidden folder under bundle: {here / name}")
            if name == ".git":
                reasons.append(f"repository marker found: {here / name}")
        for parts in FORBIDDEN_REL_DIRS:
            candidate = here.joinpath(*parts)
            if candidate.is_dir():
                reasons.append(f"forbidden folder under bundle: {candidate}")
        for name in filenames:
            if FORBIDDEN_FILE_RE.match(name):
                reasons.append(f"forbidden file under bundle: {here / name}")
    # De-duplicate while keeping order.
    return list(dict.fromkeys(reasons))


def assert_workspace_isolated(bundle_root: Path, cwd: Path | None = None) -> None:
    reasons = workspace_refusals(bundle_root, cwd)
    if reasons:
        raise AnnotatorError(
            "The tool will not start in this location:\n- " + "\n- ".join(reasons)
        )


def load_or_create_workspace_id(records_dir: Path) -> str:
    """Random workspace id; never contains a hostname or user name."""
    records_dir.mkdir(parents=True, exist_ok=True)
    path = records_dir / WORKSPACE_ID_NAME
    if path.exists():
        value = path.read_text(encoding="utf-8").strip()
        if not re.fullmatch(r"ws-[0-9a-f]{32}", value):
            raise AnnotatorError(f"malformed workspace id in {path}")
        return value
    value = "ws-" + secrets.token_hex(16)
    path.write_text(value + "\n", encoding="utf-8", newline="\n")
    return value


# ---------------------------------------------------------------------------
# Hashing, assignment, schema
# ---------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_assignment(path: Path) -> dict[str, dict[str, Any]]:
    """Read the assignment CSV (document_id, source_pdf_sha256, physical_page_count)."""
    with open(path, encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ASSIGNMENT_COLUMNS:
            raise AnnotatorError(
                f"assignment columns must be exactly {ASSIGNMENT_COLUMNS}, "
                f"got {reader.fieldnames}"
            )
        rows: dict[str, dict[str, Any]] = {}
        for line_no, row in enumerate(reader, start=2):
            doc = row["document_id"]
            sha = row["source_pdf_sha256"]
            count = row["physical_page_count"]
            if not DOC_ID_RE.match(doc or ""):
                raise AnnotatorError(f"line {line_no}: invalid document_id {doc!r}")
            if not SHA256_RE.match(sha or ""):
                raise AnnotatorError(f"line {line_no}: invalid source_pdf_sha256")
            if not (count or "").isdigit() or int(count) < 1:
                raise AnnotatorError(f"line {line_no}: invalid physical_page_count")
            if doc in rows:
                raise AnnotatorError(f"line {line_no}: duplicate document_id {doc}")
            rows[doc] = {
                "document_id": doc,
                "source_pdf_sha256": sha,
                "physical_page_count": int(count),
            }
    if not rows:
        raise AnnotatorError("assignment file has no documents")
    return rows


def verify_pdf(path: Path, expected_sha256: str) -> str:
    """Hash the chosen PDF; refuse to proceed on mismatch."""
    actual = sha256_file(path)
    if actual != expected_sha256:
        raise AnnotatorError(
            "The chosen file is not the assigned PDF (SHA-256 mismatch). "
            "Pick the file you were assigned; do not continue with this one."
        )
    return actual


def load_schema(bundle_root: Path) -> dict[str, Any]:
    with open(Path(bundle_root) / SCHEMA_FILENAME, encoding="utf-8") as handle:
        return json.load(handle)


def protocol_version_hash(bundle_root: Path) -> str:
    return sha256_file(Path(bundle_root) / PROTOCOL_FILENAME)


def schema_enums(schema: dict[str, Any]) -> dict[str, list[str]]:
    """Controlled vocabularies for the form dropdowns, read from the schema itself."""
    props = schema["$defs"]["commonRecord"]["properties"]
    return {
        "presence_state": list(props["presence_state"]["enum"]),
        "presence_reason_code": list(props["presence_reason_code"]["enum"]),
        "flags": list(props["flags"]["items"]["enum"]),
        "ambiguity_code": list(props["ambiguity_code"]["enum"]),
        "aids_used": list(props["aids_used"]["items"]["enum"]),
        "alternative_span_type": list(
            schema["$defs"]["alternativeSpan"]["properties"]["type"]["enum"]
        ),
    }


# ---------------------------------------------------------------------------
# Page conversion and record construction
# ---------------------------------------------------------------------------

def viewer_to_stored(viewer_page_1based: Any, page_count: int, label: str = "page") -> int:
    """Convert a viewer 1-based physical page to the stored 0-based index."""
    if isinstance(viewer_page_1based, bool) or not isinstance(viewer_page_1based, int):
        raise AnnotatorError(f"{label}: enter a whole viewer page number")
    if not 1 <= viewer_page_1based <= page_count:
        raise AnnotatorError(
            f"{label}: viewer page {viewer_page_1based} is outside 1..{page_count}"
        )
    return viewer_page_1based - 1


def _opt_page(value: Any, page_count: int, label: str) -> int | None:
    return None if value is None else viewer_to_stored(value, page_count, label)


def _span(start: Any, end: Any, page_count: int, label: str) -> dict[str, int]:
    return {
        "start_page": viewer_to_stored(start, page_count, f"{label} start"),
        "end_page": viewer_to_stored(end, page_count, f"{label} end"),
    }


def now_rfc3339() -> str:
    return _dt.datetime.now().astimezone().replace(microsecond=0).isoformat()


def build_raw_record(form: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    """Build a RAW record from viewer-page form input.

    ``form`` holds what the annotator entered (all pages 1-based, as in the viewer).
    ``ctx`` holds what the tool knows: document_id, source_pdf_sha256,
    physical_page_count, annotator_role, workspace_id, protocol_version_hash,
    started_at, and optionally completed_at.
    """
    n = int(ctx["physical_page_count"])
    if form.get("viewer_page_count") != n:
        raise AnnotatorError(
            f"The viewer shows {form.get('viewer_page_count')} pages but the verified "
            f"PDF has {n}. Check page labels are disabled; do not continue until they match."
        )
    primary = form.get("primary_span_viewer")
    primary_span = None if primary is None else _span(primary[0], primary[1], n, "primary span")
    be = form.get("boundary_evidence_viewer", {}) or {}
    flag_pages = {
        flag: sorted({viewer_to_stored(p, n, f"flag page ({flag})") for p in pages})
        for flag, pages in (form.get("flag_pages_viewer") or {}).items()
    }
    record: dict[str, Any] = {
        "schema_version": "0.2",
        "record_type": "RAW",
        "document_id": ctx["document_id"],
        "source_pdf_sha256": ctx["source_pdf_sha256"],
        "annotator_role": ctx["annotator_role"],
        "presence_state": form.get("presence_state"),
        "presence_reason_code": form.get("presence_reason_code"),
        "primary_span": primary_span,
        "alternative_spans": [
            {**_span(s, e, n, "alternative span"), "type": t}
            for s, e, t in (form.get("alternative_spans_viewer") or [])
        ],
        "gap_pages": sorted(
            {viewer_to_stored(p, n, "gap page") for p in (form.get("gap_pages_viewer") or [])}
        ),
        "flags": sorted(set(form.get("flags") or [])),
        "stub_word_count": form.get("stub_word_count"),
        "csr_esg_pages": sorted(
            {
                viewer_to_stored(p, n, "CSR/ESG page")
                for p in (form.get("csr_esg_pages_viewer") or [])
            }
        ),
        "ambiguity_code": form.get("ambiguity_code", "NONE"),
        "admissible_spans": [
            _span(s, e, n, "admissible span")
            for s, e in (form.get("admissible_spans_viewer") or [])
        ],
        "parent_section": form.get("parent_section") or None,
        "annexure_identity": form.get("annexure_identity") or None,
        "boundary_evidence": {
            "heading_start_page": _opt_page(be.get("heading_start_page"), n, "heading start"),
            "substantive_start_page": _opt_page(
                be.get("substantive_start_page"), n, "substantive start"
            ),
            "last_content_page": _opt_page(be.get("last_content_page"), n, "last content"),
            "next_section_heading_page": _opt_page(
                be.get("next_section_heading_page"), n, "next section heading"
            ),
            "mixed_end_page": _opt_page(be.get("mixed_end_page"), n, "mixed end"),
            "viewer_start_page_1based": None if primary is None else primary[0],
            "viewer_end_page_1based": None if primary is None else primary[1],
        },
        "timestamps": {
            "started_at": ctx["started_at"],
            "completed_at": ctx.get("completed_at") or now_rfc3339(),
        },
        "aids_used": sorted(set(form.get("aids_used") or [])),
        "structured_provenance": {
            "annotation_workspace_id": ctx["workspace_id"],
            "viewer_name": form.get("viewer_name", ""),
            "viewer_version": form.get("viewer_version", ""),
            "viewer_page_convention": VIEWER_PAGE_CONVENTION,
            "physical_page_count": n,
            "search_queries": list(form.get("search_queries") or []),
            "search_usable": bool(form.get("search_usable")),
            "bookmark_pages": sorted(
                {viewer_to_stored(p, n, "bookmark page") for p in (form.get("bookmark_pages_viewer") or [])}
            ),
            "flag_pages": flag_pages,
            "visible_parent_heading": form.get("visible_parent_heading") or None,
            "conditional_title_context": form.get("conditional_title_context") or None,
            "source_pdf_hash_verified": True,
            "no_repository_access_attested": bool(form.get("no_repository_access_attested")),
            "no_system_output_access_attested": bool(
                form.get("no_system_output_access_attested")
            ),
        },
        "protocol_version_hash": ctx["protocol_version_hash"],
    }
    return record


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _parse_ts(value: str) -> _dt.datetime:
    return _dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def tool_invariant_errors(record: dict[str, Any]) -> list[str]:
    """Numeric and cross-field checks GOLD_SCHEMA v0.2 assigns to the tool."""
    errors: list[str] = []
    try:
        n = int(record["structured_provenance"]["physical_page_count"])
    except (KeyError, TypeError, ValueError):
        return ["structured_provenance.physical_page_count missing or not an integer"]

    def check_span(span: Any, label: str) -> None:
        if not isinstance(span, dict):
            return
        s, e = span.get("start_page"), span.get("end_page")
        if isinstance(s, int) and isinstance(e, int) and not (0 <= s <= e < n):
            errors.append(f"{label}: need 0 <= start <= end < {n}, got {s}..{e}")

    primary = record.get("primary_span")
    check_span(primary, "primary_span")
    for i, span in enumerate(record.get("alternative_spans") or []):
        check_span(span, f"alternative_spans[{i}]")
    for i, span in enumerate(record.get("admissible_spans") or []):
        check_span(span, f"admissible_spans[{i}]")

    gaps = record.get("gap_pages") or []
    if gaps:
        if gaps != sorted(gaps):
            errors.append("gap_pages must be sorted")
        if not isinstance(primary, dict):
            errors.append("gap_pages need a primary span (hull)")
        else:
            lo, hi = primary.get("start_page"), primary.get("end_page")
            bad = [g for g in gaps if not (isinstance(lo, int) and lo < g < hi)]
            if bad:
                errors.append(f"gap_pages {bad} are not strictly inside the hull {lo}..{hi}")

    csr_pages = record.get("csr_esg_pages") or []
    if isinstance(csr_pages, list) and csr_pages:
        if not isinstance(primary, dict):
            errors.append("csr_esg_pages need a primary span")
        else:
            lo, hi = primary.get("start_page"), primary.get("end_page")
            outside = [
                page
                for page in csr_pages
                if isinstance(page, int)
                and not (isinstance(lo, int) and isinstance(hi, int) and lo <= page <= hi)
            ]
            if outside:
                errors.append(
                    f"csr_esg_pages {outside} are outside primary_span {lo}..{hi}"
                )
        in_gaps = [page for page in csr_pages if page in gaps]
        if in_gaps:
            errors.append(f"csr_esg_pages {in_gaps} are also gap_pages")

    be = record.get("boundary_evidence") or {}
    for key in (
        "heading_start_page",
        "substantive_start_page",
        "last_content_page",
        "next_section_heading_page",
        "mixed_end_page",
    ):
        value = be.get(key)
        if isinstance(value, int) and not 0 <= value < n:
            errors.append(f"boundary_evidence.{key} = {value} is outside 0..{n - 1}")
    vs, ve = be.get("viewer_start_page_1based"), be.get("viewer_end_page_1based")
    if isinstance(primary, dict):
        if vs != primary.get("start_page", -9) + 1 or ve != primary.get("end_page", -9) + 1:
            errors.append("viewer audit pages must equal stored primary span + 1")
    elif vs is not None or ve is not None:
        errors.append("viewer audit pages must be null when there is no primary span")

    prov = record.get("structured_provenance") or {}
    bookmarks = prov.get("bookmark_pages") or []
    if bookmarks != sorted(bookmarks):
        errors.append("bookmark_pages must be sorted")
    if any(not 0 <= p < n for p in bookmarks if isinstance(p, int)):
        errors.append("bookmark_pages outside the document")
    flags = set(record.get("flags") or [])
    for flag, pages in (prov.get("flag_pages") or {}).items():
        if flag not in flags:
            errors.append(f"flag_pages has pages for {flag!r}, which is not in flags")
        if isinstance(pages, list):
            if pages != sorted(pages):
                errors.append(f"flag_pages[{flag!r}] must be sorted")
            if any(not 0 <= p < n for p in pages if isinstance(p, int)):
                errors.append(f"flag_pages[{flag!r}] outside the document")

    ts = record.get("timestamps") or {}
    try:
        if _parse_ts(ts["completed_at"]) < _parse_ts(ts["started_at"]):
            errors.append("timestamps.completed_at is before started_at")
    except (KeyError, TypeError, ValueError):
        errors.append("timestamps are missing or unparseable")
    return errors


def validate_record(record: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    """Schema errors plus tool invariants. Raises SchemaUnavailable without jsonschema."""
    try:
        import jsonschema  # noqa: PLC0415 - optional at open time, required at submit
    except ImportError as exc:  # pragma: no cover - exercised via monkeypatch
        raise SchemaUnavailable(
            "jsonschema is not installed, so records cannot be validated or submitted."
        ) from exc
    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    )
    errors = [
        f"schema: {'/'.join(str(p) for p in err.absolute_path) or '<record>'}: {err.message}"
        for err in sorted(validator.iter_errors(record), key=lambda e: list(e.absolute_path))
    ]
    return errors + tool_invariant_errors(record)


# ---------------------------------------------------------------------------
# Canonical JSON, sealing, supersession
# ---------------------------------------------------------------------------

def canonical_json_bytes(obj: Any) -> bytes:
    """Sorted keys, UTF-8, LF line endings, no trailing spaces, final newline."""
    text = json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2, separators=(",", ": "))
    return (text + "\n").encode("utf-8")


def _role_dir(records_dir: Path, role: str) -> Path:
    if role not in RAW_ROLES:
        raise AnnotatorError(f"unknown annotator role {role!r}")
    return Path(records_dir) / role


def _assert_not_exported(records_dir: Path, role: str) -> None:
    if (_role_dir(records_dir, role) / EXPORT_LOCK_NAME).exists():
        raise AnnotatorError(
            f"{role} records were already exported to the custodian. No new record or "
            "supersession is allowed after export (GOLD_PROTOCOL v0.1 section 9)."
        )


def _assert_title_list_frozen(
    records_dir: Path, allow_unfrozen_title_list: bool
) -> None:
    placeholder = Path(records_dir).parent / TITLE_LIST_PLACEHOLDER
    if placeholder.exists() and not allow_unfrozen_title_list:
        raise AnnotatorError(
            "The title list is not frozen yet, so records cannot be sealed."
        )


def existing_records(records_dir: Path, document_id: str, role: str) -> list[Path]:
    folder = _role_dir(records_dir, role)
    if not folder.is_dir():
        return []
    prefix = f"{document_id}__{role}__"
    return sorted(
        p for p in folder.iterdir()
        if p.name.startswith(prefix) and "__SUPERSEDE__" not in p.name and p.suffix == ".json"
    )


def superseded_hashes(records_dir: Path, role: str) -> set[str]:
    folder = _role_dir(records_dir, role)
    out: set[str] = set()
    if folder.is_dir():
        for p in folder.glob("*__SUPERSEDE__*.json"):
            out.add(json.loads(p.read_text(encoding="utf-8"))["superseded_raw_sha256"])
    return out


def _write_sealed(folder: Path, filename: str, data: bytes, records_dir: Path) -> tuple[Path, str]:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / filename
    if path.exists():
        raise AnnotatorError(f"refusing to overwrite {path}")
    digest = hashlib.sha256(data).hexdigest()
    with open(path, "xb") as handle:
        handle.write(data)
    os.chmod(path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    rel = path.relative_to(records_dir).as_posix()
    with open(Path(records_dir) / HASH_LOG_NAME, "a", encoding="utf-8", newline="\n") as log:
        log.write(f"{digest}  {rel}\n")
    return path, digest


def seal_raw_record(
    records_dir: Path,
    record: dict[str, Any],
    schema: dict[str, Any],
    *,
    allow_unfrozen_title_list: bool = False,
) -> tuple[Path, str]:
    """Validate, write canonical JSON read-only, and log its SHA-256.

    Refuses a second record for the same document and role; use ``supersede``.
    """
    _assert_title_list_frozen(records_dir, allow_unfrozen_title_list)
    errors = validate_record(record, schema)
    if errors:
        raise AnnotatorError("Record is not valid:\n- " + "\n- ".join(errors))
    role = record["annotator_role"]
    _assert_not_exported(records_dir, role)
    if existing_records(records_dir, record["document_id"], role):
        raise AnnotatorError(
            f"A sealed {role} record for {record['document_id']} already exists. "
            "Records are never overwritten; use Supersede with a reason."
        )
    data = canonical_json_bytes(record)
    digest = hashlib.sha256(data).hexdigest()
    name = f"{record['document_id']}__{role}__{digest[:8]}.json"
    return _write_sealed(_role_dir(records_dir, role), name, data, records_dir)


def supersede(
    records_dir: Path,
    old_sha256: str,
    new_record: dict[str, Any],
    reason: str,
    schema: dict[str, Any],
    workspace_id: str,
    *,
    allow_unfrozen_title_list: bool = False,
) -> tuple[Path, str, Path, str]:
    """Seal a replacement raw record plus a supersession record naming the old hash.

    The original record's bytes and hash stay in place (GOLD_SCHEMA v0.1 section 1).
    Returns (new_record_path, new_sha, supersession_path, supersession_sha).
    """
    _assert_title_list_frozen(records_dir, allow_unfrozen_title_list)
    if not reason or not reason.strip():
        raise AnnotatorError("A supersession needs a written reason.")
    role = new_record["annotator_role"]
    doc = new_record["document_id"]
    _assert_not_exported(records_dir, role)
    current = {
        sha256_file(p): p for p in existing_records(records_dir, doc, role)
    }
    if old_sha256 not in current:
        raise AnnotatorError("old_sha256 is not a sealed record for this document and role")
    if old_sha256 in superseded_hashes(records_dir, role):
        raise AnnotatorError("that record has already been superseded")
    errors = validate_record(new_record, schema)
    if errors:
        raise AnnotatorError("Record is not valid:\n- " + "\n- ".join(errors))
    data = canonical_json_bytes(new_record)
    new_sha = hashlib.sha256(data).hexdigest()
    if new_sha in current:
        raise AnnotatorError("the replacement is byte-identical to an existing record")
    folder = _role_dir(records_dir, role)
    new_path, new_sha = _write_sealed(folder, f"{doc}__{role}__{new_sha[:8]}.json", data, records_dir)
    note = {
        "record_kind": "SUPERSESSION",
        "tool_version": TOOL_VERSION,
        "document_id": doc,
        "annotator_role": role,
        "superseded_raw_sha256": old_sha256,
        "superseding_raw_sha256": new_sha,
        "reason": reason.strip(),
        "created_at": now_rfc3339(),
        "annotation_workspace_id": workspace_id,
    }
    note_bytes = canonical_json_bytes(note)
    note_sha = hashlib.sha256(note_bytes).hexdigest()
    note_path, note_sha = _write_sealed(
        folder, f"{doc}__{role}__SUPERSEDE__{note_sha[:8]}.json", note_bytes, records_dir
    )
    return new_path, new_sha, note_path, note_sha


def read_hash_log(records_dir: Path) -> list[tuple[str, str]]:
    path = Path(records_dir) / HASH_LOG_NAME
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, _, rel = line.partition("  ")
        if not SHA256_RE.match(digest) or not rel:
            raise AnnotatorError(f"malformed HASH_LOG line: {line!r}")
        rows.append((digest, rel))
    return rows


def parse_page_list(text: str) -> list[int]:
    """Parse '12, 14-16' into [12, 14, 15, 16] (viewer pages). Used by the form."""
    pages: list[int] = []
    for part in (text or "").replace(";", ",").split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = (x.strip() for x in part.split("-", 1))
            if not (a.isdigit() and b.isdigit()) or int(a) > int(b):
                raise AnnotatorError(f"bad page range {part!r}")
            pages.extend(range(int(a), int(b) + 1))
        elif part.isdigit():
            pages.append(int(part))
        else:
            raise AnnotatorError(f"bad page number {part!r}")
    return pages


def iter_role_files(records_dir: Path, role: str) -> Iterable[Path]:
    folder = _role_dir(records_dir, role)
    return sorted(p for p in folder.glob("*.json")) if folder.is_dir() else []
