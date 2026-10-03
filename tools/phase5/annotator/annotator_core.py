"""Core logic for the offline ARPipe Gold annotation tool (P5-T).

Standard library only, plus ``jsonschema`` for validation. This module has no GUI,
no network code and no PDF rendering. It never imports anything from ``arpipe/``.

Status: DRAFT_PENDING_PILOT. Implements GOLD_PROTOCOL v0.4 sections 2, 4, 7-9 and
GOLD_SCHEMA v0.4 sections 1-3 for RAW records.

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

TOOL_VERSION = "p5t-0.2.1"
SCHEMA_FILENAME = "gold_schema_v0_4.json"
PROTOCOL_FILENAME = "GOLD_PROTOCOL_v0_4.md"
VIEWER_PAGE_CONVENTION = "VIEWER_PHYSICAL_1_BASED_STORED_ZERO_BASED"
# Decisions 8.7 / GOLD_PROTOCOL v0.4 section 4: two required Yes/No answers on every
# PRESENT record, and the flags the tool derives from them (never separate form inputs).
SHARED_PAGE_QUESTIONS = (
    ("start_page_shared", "Start page shared with another section?"),
    ("end_page_shared", "End page shared with another section?"),
)
DERIVED_FLAGS = ("mixed_start_page", "mixed_end_page")
# GOLD_PROTOCOL v0.4 section 4: the anchor text field paired with each shared-page answer.
ANCHOR_TEXT_FIELDS = {
    "start_page_shared": "start_anchor_text",
    "end_page_shared": "end_anchor_text",
}
RAW_ROLES = ("ANNOTATOR_A", "ANNOTATOR_B")
# F7: a bundle root may fix the role for its folder (custodian/build_workspaces.py
# always writes one). One line, exactly ANNOTATOR_A or ANNOTATOR_B; anything else in
# the file is a refusal, not a fall-through to the prompt.
ROLE_FILENAME = "ROLE.txt"
HASH_LOG_NAME = "HASH_LOG.txt"
WORKSPACE_ID_NAME = "WORKSPACE_ID.txt"
EXPORT_LOCK_NAME = "EXPORTED.lock"
TITLE_LIST_PLACEHOLDER = "TITLE_LIST_NOT_YET_FROZEN.txt"
# Title-list seal guard (GOLD_PROTOCOL v0.4 section 6): sealing requires the placeholder
# gone, this accepted title list present, and BUNDLE_MANIFEST.json's recorded hash of it
# to still match, so a list edited after bundling is caught.
TITLE_LIST_FILENAME = "TITLE_EQUIVALENCE_v0.md"
BUNDLE_MANIFEST_FILENAME = "BUNDLE_MANIFEST.json"
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


def read_role_file(bundle_root: Path) -> str | None:
    """Return the role fixed by ``ROLE.txt`` in the bundle root, or ``None`` if absent.

    Refuses (rather than falling through to the prompt) if the file exists but does
    not contain exactly one non-blank line equal to ``ANNOTATOR_A`` or ``ANNOTATOR_B``.
    """
    path = Path(bundle_root) / ROLE_FILENAME
    if not path.exists():
        return None
    lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if len(lines) != 1 or lines[0] not in RAW_ROLES:
        raise AnnotatorError(
            f"{ROLE_FILENAME} must contain exactly one line, ANNOTATOR_A or ANNOTATOR_B."
        )
    return lines[0]


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


def require_bundle_file(path: Path) -> Path:
    """Explain a missing bundle file without exposing a startup traceback."""
    if not path.is_file():
        raise AnnotatorError(
            f"{path.name} is missing from the annotation folder; "
            "start annotator_app.exe from inside your annotation folder."
        )
    return path


def load_schema(bundle_root: Path) -> dict[str, Any]:
    with open(require_bundle_file(Path(bundle_root) / SCHEMA_FILENAME), encoding="utf-8") as handle:
        return json.load(handle)


def protocol_version_hash(bundle_root: Path) -> str:
    return sha256_file(require_bundle_file(Path(bundle_root) / PROTOCOL_FILENAME))


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


def _anchor_text(value: Any, applies: bool, label: str) -> str | None:
    """The stripped anchor text when ``applies``, else null (any value sent is ignored)."""
    if not applies:
        return None
    text = (value or "").strip()
    if not text:
        raise AnnotatorError(f"{label}: type the heading line copied from the shared page.")
    return text


def build_raw_record(form: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    """Build a RAW record from viewer-page form input.

    ``form`` holds what the annotator entered (all pages 1-based, as in the viewer).
    ``ctx`` holds what the tool knows: document_id, source_pdf_sha256,
    physical_page_count, annotator_role, workspace_id, protocol_version_hash,
    started_at, and optionally completed_at.

    A PRESENT form must answer both ``start_page_shared`` and ``end_page_shared`` with
    True or False (no default). The ``mixed_start_page`` / ``mixed_end_page`` flags and
    ``boundary_evidence.mixed_end_page`` are set from those answers alone, so they cannot
    disagree with them; values the form supplies for them are ignored. On a PRESENT record,
    ``start_anchor_text`` / ``end_anchor_text`` are taken from the form (stripped, refused if
    empty) exactly when the matching answer is True, else null; on any other presence_state
    both anchors and ``mixed_end_page`` are forced null regardless of what the form sends.
    """
    n = int(ctx["physical_page_count"])
    if form.get("viewer_page_count") != n:
        raise AnnotatorError(
            f"The viewer shows {form.get('viewer_page_count')} pages but the verified "
            f"PDF has {n}. Check page labels are disabled; do not continue until they match."
        )
    present = form.get("presence_state") == "PRESENT"
    if present:
        for key, question in SHARED_PAGE_QUESTIONS:
            if not isinstance(form.get(key), bool):
                raise AnnotatorError(f"{question} Answer Yes or No before you continue.")
    start_shared, end_shared = form.get("start_page_shared"), form.get("end_page_shared")
    derived_flags = {
        flag
        for flag, shared in (("mixed_start_page", start_shared), ("mixed_end_page", end_shared))
        if shared is True
    }
    anchor_text = {
        "start_anchor_text": _anchor_text(
            form.get("start_anchor_text"), present and start_shared is True,
            "Start-page anchor text",
        ),
        "end_anchor_text": _anchor_text(
            form.get("end_anchor_text"), present and end_shared is True,
            "End-page anchor text",
        ),
    }
    primary = form.get("primary_span_viewer")
    primary_span = None if primary is None else _span(primary[0], primary[1], n, "primary span")
    be = form.get("boundary_evidence_viewer", {}) or {}
    flag_pages = {
        flag: sorted({viewer_to_stored(p, n, f"flag page ({flag})") for p in pages})
        for flag, pages in (form.get("flag_pages_viewer") or {}).items()
    }
    record: dict[str, Any] = {
        "schema_version": "0.4",
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
        "flags": sorted((set(form.get("flags") or []) - set(DERIVED_FLAGS)) | derived_flags),
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
            "mixed_end_page": (
                primary_span["end_page"]
                if present and end_shared is True and primary_span
                else None
            ),
            "start_page_shared": start_shared,
            "end_page_shared": end_shared,
            "start_anchor_text": anchor_text["start_anchor_text"],
            "end_anchor_text": anchor_text["end_anchor_text"],
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
    """Numeric and cross-field checks GOLD_SCHEMA v0.3 assigns to the tool."""
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

    # Decisions 8.7: each shared-page answer, its mixed_* flag and mixed_end_page agree.
    for answer_key, flag in (
        ("start_page_shared", "mixed_start_page"),
        ("end_page_shared", "mixed_end_page"),
    ):
        answer = be.get(answer_key)
        if isinstance(answer, bool) and (flag in flags) != answer:
            errors.append(f"flag {flag!r} must be set exactly when {answer_key} is true")
    end_shared, mixed_end = be.get("end_page_shared"), be.get("mixed_end_page")
    if end_shared is True:
        if not isinstance(primary, dict) or mixed_end != primary.get("end_page"):
            errors.append(
                "boundary_evidence.mixed_end_page must equal the primary end page "
                "when end_page_shared is true"
            )
    elif end_shared is False and mixed_end is not None:
        errors.append("boundary_evidence.mixed_end_page must be null when end_page_shared is false")

    # GOLD_PROTOCOL v0.4 section 4: each shared-page answer agrees with its anchor text.
    for answer_key, anchor_key in ANCHOR_TEXT_FIELDS.items():
        answer, anchor = be.get(answer_key), be.get(anchor_key)
        if answer is True:
            if not isinstance(anchor, str) or anchor != anchor.strip() or not anchor:
                errors.append(
                    f"boundary_evidence.{anchor_key} must be a non-empty, stripped string "
                    f"when {answer_key} is true"
                )
        elif anchor is not None:
            errors.append(f"boundary_evidence.{anchor_key} must be null when {answer_key} is not true")

    ts = record.get("timestamps") or {}
    try:
        if _parse_ts(ts["completed_at"]) < _parse_ts(ts["started_at"]):
            errors.append("timestamps.completed_at is before started_at")
    except (KeyError, TypeError, ValueError):
        errors.append("timestamps are missing or unparseable")
    return errors


def _friendly_schema_error(err: Any, record: dict[str, Any]) -> str:
    """One short instruction per problem, naming the form box when known."""
    path = tuple(err.absolute_path)
    field = path[0] if path else "<record>"
    flags = record.get("flags") if isinstance(record.get("flags"), list) else []
    state = record.get("presence_state")
    mapped = {
        "ambiguity_code": (
            state in ("PRESENT", "ABSENT") and record.get("ambiguity_code") != "NONE",
            "Ambiguity code: choose NONE for PRESENT or ABSENT.",
        ),
        "annexure_identity": (
            "annexure" in flags and not record.get("annexure_identity"),
            "Annexure identity: type the printed identity, or untick annexure.",
        ),
        "parent_section": (
            "embedded_in_directors_report" in flags and not record.get("parent_section"),
            "Parent section: type the parent heading, or untick embedded_in_directors_report.",
        ),
        "csr_esg_pages": (
            "contains_csr_esg" in flags and not record.get("csr_esg_pages"),
            "CSR/ESG pages: enter the viewer pages, or untick contains_csr_esg.",
        ),
        "gap_pages": (
            "noncontiguous_hull" in flags and not record.get("gap_pages"),
            "Gap pages: enter the gap viewer pages, or untick noncontiguous_hull.",
        ),
        "admissible_spans": (
            state != "AMBIGUOUS" and bool(record.get("admissible_spans")),
            "Admissible spans: clear this box for PRESENT or ABSENT; use it only for AMBIGUOUS.",
        ),
        "presence_state": (
            "stub" in flags and state != "PRESENT",
            "Flags (stub): untick stub, or choose PRESENT if there is an MD&A body.",
        ),
    }
    if field in mapped and mapped[field][0]:
        return mapped[field][1]
    label = "/".join(str(part) for part in path) or "<record>"
    # JSON Schema messages can embed the invalid object: keep the fallback bounded.
    message = " ".join(err.message.split())
    if len(message) > 180:
        message = message[:177] + "..."
    return f"{label}: {message}"


def validate_record(record: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    """Short schema errors plus tool invariants; validation requirements are unchanged."""
    try:
        import jsonschema  # noqa: PLC0415 - optional at open time, required at submit
    except ImportError as exc:  # pragma: no cover - exercised via monkeypatch
        raise SchemaUnavailable(
            "jsonschema is not installed, so records cannot be validated or submitted."
        ) from exc
    # Select the declared record branch. The root oneOf otherwise prints the entire
    # record and adds irrelevant errors from the other role's branch.
    selected_schema = dict(schema)
    if "rawRecord" in schema.get("$defs", {}) and "adjudicatedRecord" in schema["$defs"]:
        selected_schema.pop("oneOf", None)
        kind = "adjudicatedRecord" if record.get("record_type") == "ADJUDICATED" else "rawRecord"
        selected_schema["$ref"] = f"#/$defs/{kind}"
    validator = jsonschema.Draft202012Validator(
        selected_schema, format_checker=jsonschema.FormatChecker()
    )
    schema_errors = sorted(validator.iter_errors(record), key=lambda e: tuple(str(p) for p in e.absolute_path))
    errors = list(dict.fromkeys(_friendly_schema_error(err, record) for err in schema_errors))
    # Invariants assume schema-typed fields; malformed collections should be reported,
    # not passed to numerical checks that would crash on them.
    return errors if errors else tool_invariant_errors(record)


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
    """Title-list seal guard (GOLD_PROTOCOL v0.4 section 6).

    Sealing is allowed only if the unfrozen placeholder is absent, the accepted title
    list is present in the bundle root, and BUNDLE_MANIFEST.json's recorded hash of that
    list still matches its current bytes (so a list edited after bundling is refused).
    """
    if allow_unfrozen_title_list:
        return
    bundle_root = Path(records_dir).parent
    if (bundle_root / TITLE_LIST_PLACEHOLDER).exists():
        raise AnnotatorError(
            "The title list is not frozen yet, so records cannot be sealed."
        )
    title_list = bundle_root / TITLE_LIST_FILENAME
    if not title_list.is_file():
        raise AnnotatorError(
            f"{TITLE_LIST_FILENAME} is missing from the bundle, so records cannot be sealed."
        )
    manifest_path = bundle_root / BUNDLE_MANIFEST_FILENAME
    if not manifest_path.is_file():
        raise AnnotatorError(
            f"{BUNDLE_MANIFEST_FILENAME} is missing from the bundle, so records cannot be sealed."
        )
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AnnotatorError(
            f"{BUNDLE_MANIFEST_FILENAME} is not readable JSON, so records cannot be sealed."
        ) from exc
    recorded = manifest.get("title_list_sha256") if isinstance(manifest, dict) else None
    if not isinstance(recorded, str) or recorded != sha256_file(title_list):
        raise AnnotatorError(
            f"{TITLE_LIST_FILENAME} does not match the hash sealed in "
            f"{BUNDLE_MANIFEST_FILENAME}, so records cannot be sealed."
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
