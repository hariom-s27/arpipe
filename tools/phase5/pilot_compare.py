"""Read-only pilot comparison of sealed raw A/B exports; never opens a PDF.

Run as ``python -m tools.phase5.pilot_compare``. Supersession requires an explicit
policy: replacement is the author's primary analysis, first is the sensitivity.
Missing records remain visible and are excluded from paired agreement measures.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

if __package__ in (None, ""):  # also support running the file directly
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.phase5.annotator import annotator_core as core
from tools.phase5.scoring import inclusive_iou, raw_ab_agreement
from tools.phase5.scoring.__main__ import _guard_paths

TOOL_VERSION = "p5f8-0.1.0"
REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "docs/phase5/gold_schema_v0_4.json"
ROSTER_COLUMNS = ["document_id", "source_pdf_sha256", "physical_page_count", "split"]
ADJ_STATUSES = ("AGREEMENT_CONFIRMED", "DISAGREEMENT_RESOLVED", "AMBIGUITY_PRESERVED")
ADJ_CAUSES = ("ANNOTATOR_MISSED_RULE", "RULE_UNCLEAR", "TYPING_SLIP", "VIEWER_OR_TOOL", "OTHER")
ADJ_COLUMNS = [
    "adj_status", "adj_presence_state", "adj_reason_code", "adj_start_viewer",
    "adj_end_viewer", "adj_start_shared", "adj_start_anchor", "adj_end_shared",
    "adj_end_anchor", "adj_flags", "adj_admissible_spans_viewer",
    "adj_other_fields_json", "adj_reason", "adj_cause",
]
ROLE_FIELDS = [
    "raw_record_sha256", "state", "reason", "start_viewer", "end_viewer",
    "start_shared", "start_anchor", "end_shared", "end_anchor", "flags",
    "ambiguity_code", "admissible_spans_viewer", "alternative_spans_viewer",
    "gap_pages_viewer", "csr_esg_pages_viewer", "minutes", "content_json",
]
READONLY_COLUMNS = (
    ROSTER_COLUMNS + ["supersession_policy"]
    + [f"{role}_{field}" for role in ("a", "b") for field in ROLE_FIELDS]
    + ["agree_state", "agree_span_exact", "agree_shared_answers", "agree_flags", "suggested_status"]
)
SHEET_COLUMNS = READONLY_COLUMNS + ADJ_COLUMNS
# Annotation content, excluding the two people's viewer, timing and access metadata.
CONTENT_FIELDS = (
    "presence_state", "presence_reason_code", "primary_span", "alternative_spans",
    "gap_pages", "flags", "stub_word_count", "csr_esg_pages", "ambiguity_code",
    "admissible_spans", "parent_section", "annexure_identity", "boundary_evidence",
)


class ComparisonError(ValueError):
    """A clear refusal before any output is written."""


def guard_paths(paths: list[Path]) -> None:
    """Keep scoring's HOLDOUT guard, including resolved targets; no override here."""
    _guard_paths(paths, approved=False)
    _guard_paths([path.resolve() for path in paths], approved=False)


def check_out_dir(out_dir: Path) -> Path:
    """Check without creating anything: callers validate the entire run first."""
    guard_paths([out_dir])
    out = out_dir.resolve()
    if out == REPO_ROOT or REPO_ROOT in out.parents:
        raise ComparisonError("--out-dir must be outside the repository")
    for directory in (out, *out.parents):
        if (directory / ".git").exists():
            raise ComparisonError("--out-dir must be outside the repository")
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise ComparisonError("refusing to overwrite: --out-dir exists and is not empty")
    return out


def load_roster(path: Path) -> dict[str, dict[str, Any]]:
    guard_paths([path])
    roster = {}
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ROSTER_COLUMNS:
            raise ComparisonError(f"roster columns must be exactly {', '.join(ROSTER_COLUMNS)}")
        for line, row in enumerate(reader, 2):
            if None in row or any(value is None for value in row.values()):
                raise ComparisonError(f"roster row {line}: wrong number of cells")
            doc, sha, count, split = (row[key] for key in ROSTER_COLUMNS)
            if split.casefold() == "holdout":
                raise ComparisonError(f"roster row {line}: HOLDOUT split refused")
            if not core.DOC_ID_RE.fullmatch(doc) or doc in roster:
                raise ComparisonError(f"roster row {line}: invalid or duplicate document_id")
            if not core.SHA256_RE.fullmatch(sha):
                raise ComparisonError(f"roster row {line}: invalid source_pdf_sha256")
            if not count.isdigit() or int(count) < 1 or split not in ("FIT", "VALIDATION"):
                raise ComparisonError(f"roster row {line}: invalid page count or split (use FIT or VALIDATION)")
            roster[doc] = {**row, "physical_page_count": int(count)}
    if not roster:
        raise ComparisonError("roster has no documents")
    return dict(sorted(roster.items()))


@dataclass
class RawExport:
    records: dict[str, dict[str, Any]]  # full hash -> raw record
    by_document: dict[str, list[str]]  # HASH_LOG seal order
    supersessions: list[dict[str, Any]]
    input_hashes: dict[str, str]


def load_export(root: Path, role: str, roster: dict, schema: dict) -> RawExport:
    guard_paths([root, root / core.HASH_LOG_NAME, root / role])
    if not (root / core.HASH_LOG_NAME).is_file():
        raise ComparisonError(f"{role}: missing HASH_LOG.txt")
    folder = root / role
    if not folder.is_dir():
        raise ComparisonError(f"wrong role folder: expected {role} under {root.name}")
    logged = {}
    order = []
    for digest, rel in core.read_hash_log(root):
        parts = PurePosixPath(rel)
        # The export log may also list the other role, whose bytes were not exported.
        if parts.is_absolute() or ".." in parts.parts or "\\" in rel or ":" in rel:
            raise ComparisonError(f"{role}: unsafe path in HASH_LOG.txt")
        if rel in logged:
            raise ComparisonError(f"{role}: duplicate HASH_LOG.txt entry for {rel}")
        logged[rel] = digest
        if parts.parts and parts.parts[0] == role:
            if len(parts.parts) != 2 or parts.suffix != ".json":
                raise ComparisonError(f"{role}: malformed record path in HASH_LOG.txt")
            guard_paths([root / rel])
            order.append(rel)
    files = sorted(folder.glob("*.json"))
    guard_paths(files)
    actual_paths = {path.relative_to(root).as_posix(): path for path in files}
    if set(order) != set(actual_paths):
        missing = sorted(set(order) - set(actual_paths))
        unlogged = sorted(set(actual_paths) - set(order))
        raise ComparisonError(f"{role}: HASH_LOG.txt file list mismatch; missing={missing}, unlisted={unlogged}")
    records, by_document, notes = {}, {}, []
    hashes = {f"{role}/HASH_LOG.txt": core.sha256_file(root / core.HASH_LOG_NAME)}
    invalid = []
    for rel in order:
        path = actual_paths[rel]
        if path.is_symlink() or path.resolve().parent != folder.resolve():
            raise ComparisonError(f"{rel}: record must be inside its role folder, without links")
        digest = core.sha256_file(path)
        if digest != logged[rel]:
            raise ComparisonError(f"{rel}: SHA-256 hash mismatch with HASH_LOG.txt")
        if path.stem.rsplit("__", 1)[-1] != digest[:8]:
            raise ComparisonError(f"{rel}: filename hash prefix does not match")
        record = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(record, dict):
            raise ComparisonError(f"{rel}: JSON record must be an object")
        doc = record.get("document_id")
        if record.get("annotator_role") != role:
            raise ComparisonError(f"{rel}: annotator_role does not equal folder role {role}")
        if doc not in roster:
            raise ComparisonError(f"{rel}: document_id is not in the roster")
        is_note = path.name.startswith(f"{doc}__{role}__SUPERSEDE__")
        expected_name = f"{doc}__{role}__{'SUPERSEDE__' if is_note else ''}{digest[:8]}.json"
        if path.name != expected_name:
            raise ComparisonError(f"{rel}: filename does not match document and role")
        hashes[f"{role}/{rel}"] = digest
        if is_note:
            required = {
                "record_kind", "tool_version", "document_id", "annotator_role",
                "superseded_raw_sha256", "superseding_raw_sha256", "reason",
                "created_at", "annotation_workspace_id",
            }
            if (set(record) != required or record.get("record_kind") != "SUPERSESSION"
                    or not isinstance(record.get("reason"), str) or not record["reason"].strip()
                    or not all(isinstance(record.get(key), str) and record[key].strip()
                               for key in ("tool_version", "annotation_workspace_id"))
                    or not all(core.SHA256_RE.fullmatch(str(record.get(key, "")))
                               for key in ("superseded_raw_sha256", "superseding_raw_sha256"))):
                raise ComparisonError(f"{rel}: invalid supersession note")
            try:
                if core._parse_ts(record["created_at"]).tzinfo is None:
                    raise ValueError("timestamp needs an offset")
            except (ValueError, TypeError) as exc:
                raise ComparisonError(f"{rel}: invalid supersession timestamp") from exc
            notes.append({**record, "note_sha256": digest})
            continue
        errors = core.validate_record(record, schema)
        if record.get("record_type") != "RAW":
            errors.append("record_type must be RAW")
        if errors:
            invalid.append(f"{doc} ({role}): " + "; ".join(errors))
            continue
        if record["source_pdf_sha256"] != roster[doc]["source_pdf_sha256"]:
            raise ComparisonError(f"{doc} ({role}): source_pdf_sha256 does not match roster")
        if record["structured_provenance"]["physical_page_count"] != roster[doc]["physical_page_count"]:
            raise ComparisonError(f"{doc} ({role}): physical_page_count does not match roster")
        records[digest] = record
        by_document.setdefault(doc, []).append(digest)
    if invalid:
        raise ComparisonError(
            f"schema/tool-invalid record trigger: FIRED; count={len(invalid)}, threshold=1\n"
            + "\n".join(invalid)
        )
    return RawExport(records, by_document, notes, hashes)


def select_records(export: RawExport, policy: str | None) -> tuple[dict, list[dict]]:
    if policy not in (None, "first", "replacement"):
        raise ComparisonError("supersession policy must be first or replacement")
    if export.supersessions and policy is None:
        raise ComparisonError("supersession exists: --supersession-policy first|replacement is required")
    links, incoming = {}, {}
    for note in export.supersessions:
        old, new = note["superseded_raw_sha256"], note["superseding_raw_sha256"]
        if old not in export.records or new not in export.records:
            raise ComparisonError("supersession refers to a missing raw hash")
        if old in links or new in incoming:
            raise ComparisonError("supersession chain branches or repeats a replacement")
        for digest in (old, new):
            raw = export.records[digest]
            if raw["document_id"] != note["document_id"] or raw["annotator_role"] != note["annotator_role"]:
                raise ComparisonError("supersession document or role differs from the raw record")
        seals = export.by_document[note["document_id"]]
        if seals.index(old) >= seals.index(new):
            raise ComparisonError("supersession replacement was sealed before the original")
        links[old], incoming[new] = new, old
    selected, audit = {}, []
    for doc, hashes in sorted(export.by_document.items()):
        roots = [digest for digest in hashes if digest not in incoming]
        if len(roots) != 1:
            raise ComparisonError(f"{doc}: raw records do not form one supersession chain")
        chain = [roots[0]]
        while chain[-1] in links:
            next_hash = links[chain[-1]]
            if next_hash in chain:
                raise ComparisonError(f"{doc}: supersession cycle")
            chain.append(next_hash)
        if set(chain) != set(hashes):
            raise ComparisonError(f"{doc}: unlinked raw records or supersession cycle")
        chosen = chain[-1] if policy == "replacement" else chain[0]
        selected[doc] = {"sha256": chosen, "record": export.records[chosen]}
        if len(chain) > 1:
            audit.append({
                "document_id": doc, "role": export.records[chosen]["annotator_role"],
                "original_sha256": chain[0], "replacement_sha256": chain[-1],
                "chain_sha256": chain, "selected_sha256": chosen,
                "notes": [note for note in export.supersessions if note["document_id"] == doc],
            })
    return selected, audit


def load_inputs(records_a: Path, records_b: Path, roster_path: Path, policy: str | None) -> dict:
    guard_paths([records_a, records_b, roster_path, SCHEMA_PATH])
    roster = load_roster(roster_path)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    a = load_export(records_a, "ANNOTATOR_A", roster, schema)
    b = load_export(records_b, "ANNOTATOR_B", roster, schema)
    selected_a, notes_a = select_records(a, policy)
    selected_b, notes_b = select_records(b, policy)
    return {
        "roster": roster, "schema": schema, "a": selected_a, "b": selected_b,
        "supersessions": notes_a + notes_b, "supersession_policy": policy,
        "input_hashes": {
            "roster.csv": core.sha256_file(roster_path), "schema.json": core.sha256_file(SCHEMA_PATH),
            **a.input_hashes, **b.input_hashes,
        },
    }


def annotation_content(record: dict) -> dict:
    content = {key: record.get(key) for key in CONTENT_FIELDS}
    content["flags"] = sorted(record["flags"])
    content["structured_content"] = {
        key: record["structured_provenance"].get(key)
        for key in ("flag_pages", "visible_parent_heading", "conditional_title_context")
    }
    return content


def agreement(a: dict | None, b: dict | None) -> dict:
    if a is None or b is None:
        return {key: None for key in ("agree_state", "agree_span_exact", "agree_shared_answers", "agree_flags", "agree_fully")}
    return {
        "agree_state": a["presence_state"] == b["presence_state"],
        "agree_span_exact": a["primary_span"] == b["primary_span"],
        "agree_shared_answers": all(a["boundary_evidence"][key] == b["boundary_evidence"][key]
                                    for key, _ in core.SHARED_PAGE_QUESTIONS),
        "agree_flags": set(a["flags"]) == set(b["flags"]),
        "agree_fully": annotation_content(a) == annotation_content(b),
    }


def viewer_span(span: dict | None) -> dict | None:
    return None if span is None else {key: value + 1 for key, value in span.items() if key in ("start_page", "end_page")}


def minutes(record: dict) -> float:
    ts = record["timestamps"]
    return round((core._parse_ts(ts["completed_at"]) - core._parse_ts(ts["started_at"])).total_seconds() / 60, 1)


def snapshot(selected: dict | None) -> dict:
    if selected is None:
        return {"state": "MISSING"}
    record = selected["record"]
    be = record["boundary_evidence"]
    return {
        "raw_record_sha256": selected["sha256"], "state": record["presence_state"],
        "reason": record["presence_reason_code"], "span_0based": record["primary_span"],
        "span_viewer_1based": viewer_span(record["primary_span"]),
        "shared_answers": {key: be[key] for key, _ in core.SHARED_PAGE_QUESTIONS},
        "anchors": {key: be[key] for key in core.ANCHOR_TEXT_FIELDS.values()},
        "flags": sorted(record["flags"]), "minutes": minutes(record),
        "content": annotation_content(record),
    }


def comparison_report(inputs: dict) -> dict:
    paired = sorted(set(inputs["a"]) & set(inputs["b"]))
    result = raw_ab_agreement([inputs["a"][doc]["record"] for doc in paired],
                              [inputs["b"][doc]["record"] for doc in paired])
    documents = []
    for doc in inputs["roster"]:
        a, b = inputs["a"].get(doc), inputs["b"].get(doc)
        ar, br = (item["record"] if item else None for item in (a, b))
        comparable = ar is not None and br is not None
        pp = comparable and ar["presence_state"] == br["presence_state"] == "PRESENT"
        documents.append({
            "document_id": doc, "a": snapshot(a), "b": snapshot(b), **agreement(ar, br),
            "start_diff_a_minus_b": ar["primary_span"]["start_page"] - br["primary_span"]["start_page"] if pp else None,
            "end_diff_a_minus_b": ar["primary_span"]["end_page"] - br["primary_span"]["end_page"] if pp else None,
            "iou": inclusive_iou(ar["primary_span"], br["primary_span"]) if pp else None,
            "flags_symmetric_difference": sorted(set(ar["flags"]) ^ set(br["flags"])) if comparable else None,
        })
    presence_count = sum(row["agree_state"] is False for row in documents)
    boundary_count = sum(any(row[key] is not None and abs(row[key]) > 1
                             for key in ("start_diff_a_minus_b", "end_diff_a_minus_b")) for row in documents)
    def trigger(name: str, count: int, threshold: int) -> dict:
        return {"trigger": name, "status": "FIRED" if count >= threshold else "NOT_FIRED",
                "count": count, "threshold": threshold, "planned_documents": 10,
                "available_pairs": len(paired)}
    triggers = [
        trigger("presence disagreement", presence_count, 2),
        trigger("start or end differs by more than one page", boundary_count, 3),
        trigger("schema-invalid record", 0, 1),
        {"trigger": "information-barrier breach", "status": "NEEDS_HUMAN_CHECK", "count": None, "threshold": 1},
        {"trigger": "title intake error", "status": "NEEDS_HUMAN_CHECK", "count": None, "threshold": ">5% of intake sample"},
    ]
    return {
        "tool_version": TOOL_VERSION, "annotator_tool_version": core.TOOL_VERSION,
        "input_file_sha256": inputs["input_hashes"], "raw_ab_agreement": result,
        "documents": documents, "triggers": triggers, "supersessions": inputs["supersessions"],
        "supersession_policy": inputs["supersession_policy"],
        "roster_document_count": len(inputs["roster"]), "paired_document_count": len(paired),
        "missing_documents": [row["document_id"] for row in documents if row["a"]["state"] == "MISSING" or row["b"]["state"] == "MISSING"],
    }


def _cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return str(value)


def _compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sheet_row(doc: str, inputs: dict) -> dict[str, str]:
    row = {key: "" for key in SHEET_COLUMNS}
    row.update({key: str(value) for key, value in inputs["roster"][doc].items()})
    row["supersession_policy"] = inputs["supersession_policy"] or ""
    records = []
    for role in ("a", "b"):
        selected = inputs[role].get(doc)
        record = selected["record"] if selected else None
        records.append(record)
        row[f"{role}_state"] = record["presence_state"] if record else "MISSING"
        if record is None:
            continue
        be, span = record["boundary_evidence"], viewer_span(record["primary_span"])
        values = {
            "raw_record_sha256": selected["sha256"], "reason": record["presence_reason_code"],
            "start_viewer": span["start_page"] if span else None, "end_viewer": span["end_page"] if span else None,
            "start_shared": be["start_page_shared"], "end_shared": be["end_page_shared"],
            "start_anchor": be["start_anchor_text"], "end_anchor": be["end_anchor_text"],
            "flags": ";".join(sorted(record["flags"])), "ambiguity_code": record["ambiguity_code"],
            "admissible_spans_viewer": ";".join(f"{s['start_page'] + 1}-{s['end_page'] + 1}" for s in record["admissible_spans"]),
            "alternative_spans_viewer": ";".join(f"{s['start_page'] + 1}-{s['end_page'] + 1} {s['type']}" for s in record["alternative_spans"]),
            "gap_pages_viewer": ";".join(str(p + 1) for p in record["gap_pages"]),
            "csr_esg_pages_viewer": ";".join(str(p + 1) for p in record.get("csr_esg_pages", [])),
            "minutes": f"{minutes(record):.1f}", "content_json": _compact(annotation_content(record)),
        }
        row.update({f"{role}_{key}": _cell(value) for key, value in values.items()})
    agreements = agreement(*records)
    row.update({key: _cell(agreements[key]) for key in READONLY_COLUMNS if key.startswith("agree_")})
    if agreements["agree_fully"]:
        row["suggested_status"] = "AGREEMENT_CONFIRMED"
    return row


def sheet_bytes(inputs: dict) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=SHEET_COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(sheet_row(doc, inputs) for doc in inputs["roster"])
    return stream.getvalue().encode("utf-8")


def _md(value: Any) -> str:
    return _cell(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ") or "Not applicable"


def _span_text(span: dict | None) -> str:
    return "Not applicable" if span is None else f"{span['start_page']}-{span['end_page']}"


def _supporting_details(content: dict) -> list[tuple[str, Any]]:
    """Render supporting content in plain words, converting every stored page."""
    details = [("Ambiguity code", content["ambiguity_code"]),
               ("Parent section", content["parent_section"]),
               ("Annexure identity", content["annexure_identity"]),
               ("Stub word count", content["stub_word_count"])]
    for field, label in (("alternative_spans", "Other spans"), ("admissible_spans", "Admissible spans")):
        spans = [_span_text(viewer_span(span)) + (f" ({span['type']})" if "type" in span else "")
                 for span in content[field]]
        details.append((label, "; ".join(spans) or "None"))
    for field, label in (("gap_pages", "Gap pages"), ("csr_esg_pages", "CSR/ESG pages")):
        details.append((label, "; ".join(str(page + 1) for page in content[field] or []) or "None"))
    be = content["boundary_evidence"]
    for field, label in (("heading_start_page", "Heading page"),
                         ("substantive_start_page", "Substantive start page"),
                         ("last_content_page", "Last content page"),
                         ("next_section_heading_page", "Next section heading page"),
                         ("mixed_end_page", "Shared end page")):
        details.append((label, be[field] + 1 if be[field] is not None else None))
    supporting = content["structured_content"]
    details += [("Visible parent heading", supporting["visible_parent_heading"]),
                ("Conditional title context", supporting["conditional_title_context"])]
    flag_pages = supporting["flag_pages"] or {}
    for flag, pages in sorted(flag_pages.items()):
        details.append((f"Pages for {flag}", "; ".join(str(page + 1) for page in pages)))
    return details


def markdown_report(report: dict) -> bytes:
    lines = [
        "# Pilot comparison", "", f"Tool: {report['tool_version']}; annotator: {report['annotator_tool_version']}", "",
        f"Roster documents: {report['roster_document_count']}; available A/B pairs: {report['paired_document_count']}.",
        "All page numbers in tables are physical viewer pages (1-based). Differences are A minus B.",
        "Missing records are excluded from agreement. Trigger counts use available pairs; missing evidence cannot establish that a trigger is absent.",
        "Missing documents: " + (", ".join(report["missing_documents"]) or "None") + ".",
        "This is agreement between people, not system accuracy.", "",
        f"Supersession policy: {report['supersession_policy'] or 'No supersession policy needed'}.",
        "The author specifies replacement for the primary comparison and first for the sensitivity.", "",
        "## Documents", "",
        "| Document | State A | State B | Reason A | Reason B | Span A | Span B | Start difference | End difference | IoU | Minutes A | Minutes B |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in report["documents"]:
        a, b = row["a"], row["b"]
        values = [row["document_id"], a["state"], b["state"], a.get("reason"), b.get("reason"),
                  _span_text(a.get("span_viewer_1based")), _span_text(b.get("span_viewer_1based")),
                  row["start_diff_a_minus_b"], row["end_diff_a_minus_b"], row["iou"], a.get("minutes"), b.get("minutes")]
        lines.append("| " + " | ".join(_md(value) for value in values) + " |")
    lines += ["", "## Agreement by document", "",
              "| Document | Same state | Same span | Same shared answers | Same flags | All annotation content agrees |",
              "|---|---|---|---|---|---|"]
    for row in report["documents"]:
        values = [row["document_id"]] + [row[key] for key in (
            "agree_state", "agree_span_exact", "agree_shared_answers", "agree_flags", "agree_fully")]
        lines.append("| " + " | ".join(_md(value) for value in values) + " |")
    lines += ["", "## Raw record hashes and anchors", "",
              "| Document | Role | Selected raw SHA-256 | Start anchor | End anchor |",
              "|---|---|---|---|---|"]
    for row in report["documents"]:
        for role in ("a", "b"):
            item = row[role]
            anchors = item.get("anchors", {})
            values = [row["document_id"], role.upper(), item.get("raw_record_sha256", "MISSING"),
                      anchors.get("start_anchor_text"), anchors.get("end_anchor_text")]
            lines.append("| " + " | ".join(_md(value) for value in values) + " |")
    lines += ["", "## Shared pages and flags", "",
              "| Document | Start shared A | Start shared B | End shared A | End shared B | Flags A | Flags B | Flags that differ |",
              "|---|---|---|---|---|---|---|---|"]
    for row in report["documents"]:
        a, b = row["a"], row["b"]
        sa, sb = a.get("shared_answers", {}), b.get("shared_answers", {})
        values = [row["document_id"], sa.get("start_page_shared"), sb.get("start_page_shared"),
                  sa.get("end_page_shared"), sb.get("end_page_shared"),
                  "; ".join(a.get("flags", [])) or "None", "; ".join(b.get("flags", [])) or "None",
                  "; ".join(row["flags_symmetric_difference"] or []) or "None"]
        lines.append("| " + " | ".join(_md(value) for value in values) + " |")
    lines += ["", "## Supporting annotation fields", "",
              "| Document | Role | Field | Value |", "|---|---|---|---|"]
    for row in report["documents"]:
        for role in ("a", "b"):
            if "content" in row[role]:
                for field, value in _supporting_details(row[role]["content"]):
                    lines.append("| " + " | ".join(_md(item) for item in (row["document_id"], role.upper(), field, value)) + " |")
    lines += ["", "## Raw A/B agreement", "", "| Measure | Value |", "|---|---|"]
    def measures(value: Any, name: str = "") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                measures(child, (name + " / " if name else "") + key.replace("_", " "))
        else:
            lines.append(f"| {_md(name)} | {_md(value)} |")
    measures(report["raw_ab_agreement"])
    lines += ["", "## Revision triggers", "", "| Trigger | Result | Count | Threshold |", "|---|---|---|---|"]
    for trigger in report["triggers"]:
        lines.append("| " + " | ".join(_md(trigger[key]) for key in ("trigger", "status", "count", "threshold")) + " |")
    lines += ["", "Presence threshold is 2 of the planned 10; boundary threshold is 3 of the planned 10.",
              "Schema-invalid inputs are refused before output; a refusal reports the fired schema/tool trigger.",
              "Information barriers and the title intake sample require human review.", "", "## Supersessions", ""]
    if not report["supersessions"]:
        lines.append("None.")
    for item in report["supersessions"]:
        lines += [f"- {item['document_id']} ({item['role']}): original {item['original_sha256']}; replacement {item['replacement_sha256']}; selected {item['selected_sha256']}."]
        for note in item["notes"]:
            lines.append(f"  - Note {note['note_sha256']}: {note['superseded_raw_sha256']} to {note['superseding_raw_sha256']}; {_md(note['reason'])}.")
    lines += ["", "## Adjudication sheet", "",
              "Keep the left columns unchanged. Every row needs an explicit adj_status, adj_reason and adj_cause; suggested_status is only a suggestion.",
              "Statuses: " + ", ".join(ADJ_STATUSES) + ". Causes: " + ", ".join(ADJ_CAUSES) + ".",
              "For resolved or preserved rows enter the state and reason, viewer start/end and Yes/No shared answers (PRESENT only), anchors when shared, and semicolon-separated flags.",
              "For ambiguity use semicolon-separated admissible viewer spans, for example 10-14;11-14. No primary span or shared answers applies to ABSENT or AMBIGUOUS.",
              "adj_other_fields_json is an optional object of supporting form fields: parent_section, annexure_identity, ambiguity_code, stub_word_count, gap_pages_viewer, csr_esg_pages_viewer, alternative_spans_viewer, boundary_evidence_viewer, flag_pages_viewer, visible_parent_heading, conditional_title_context. All pages there are viewer pages; alternative spans are [start,end,type].",
              "Agreement confirmation requires all annotation content to agree, including reasons, anchors and supporting fields. Viewer and timing metadata may differ.",
              "Adjudicated records retain source/protocol and viewer metadata from A; their timestamps and workspace identify this adjudication run.",
              "Run adjudicate with the same supersession policy used for this sheet and --adjudicator-attest.", "", "## Input file hashes", "",
              "| Input | SHA-256 |", "|---|---|"]
    for name, digest in sorted(report["input_file_sha256"].items()):
        lines.append(f"| {_md(name)} | {digest} |")
    return ("\n".join(lines) + "\n").encode("utf-8")


def run_comparison(records_a: Path, records_b: Path, roster: Path, out_dir: Path,
                   supersession_policy: str | None = None) -> dict:
    guard_paths([records_a, records_b, roster, out_dir])
    out = check_out_dir(out_dir)
    inputs = load_inputs(records_a, records_b, roster, supersession_policy)
    report = comparison_report(inputs)
    outputs = {"PILOT_COMPARISON.json": core.canonical_json_bytes(report),
               "PILOT_COMPARISON.md": markdown_report(report), "ADJUDICATION_SHEET.csv": sheet_bytes(inputs)}
    out.mkdir(parents=True, exist_ok=True)
    for name, data in outputs.items():
        with (out / name).open("xb") as stream:
            stream.write(data)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ("records-a", "records-b", "roster", "out-dir"):
        parser.add_argument(f"--{option}", required=True, type=Path)
    parser.add_argument("--supersession-policy", choices=("first", "replacement"),
                        help="required only when supersession exists; author primary=replacement, sensitivity=first")
    args = parser.parse_args(argv)
    try:
        run_comparison(args.records_a, args.records_b, args.roster, args.out_dir, args.supersession_policy)
    except (ValueError, OSError, TypeError, KeyError, core.AnnotatorError) as exc:
        print(f"COMPARISON REFUSED: {exc}", file=sys.stderr)
        return 2
    for name in ("PILOT_COMPARISON.json", "PILOT_COMPARISON.md", "ADJUDICATION_SHEET.csv"):
        print(f"{core.sha256_file(args.out_dir / name)}  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
