"""Validate every pilot adjudication row, then seal v0.4 adjudicated records.

No PDF is opened. The left side of the sheet is verified against the sealed raw
exports; the separate adjudicator must confirm every row and attest explicitly.
Supporting JSON uses annotator form fields with viewer (1-based) page values;
see PILOT_COMPARISON.md for the allowed fields and syntax.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.phase5 import pilot_compare as compare
from tools.phase5.annotator import annotator_core as core
from tools.phase5.scoring.__main__ import _guard_paths

TOOL_VERSION = compare.TOOL_VERSION
OTHER_FORM_FIELDS = {
    "parent_section", "annexure_identity", "ambiguity_code", "stub_word_count",
    "gap_pages_viewer", "csr_esg_pages_viewer", "alternative_spans_viewer",
    "boundary_evidence_viewer", "flag_pages_viewer", "visible_parent_heading",
    "conditional_title_context",
}


class AdjudicationError(ValueError):
    """Refuse the entire run, listing the problem rows."""


def _viewer_int(value: str, label: str) -> int | None:
    if not value:
        return None
    if not value.isdigit():
        raise AdjudicationError(f"{label}: type a whole viewer page number")
    return int(value)


def _shared(value: str, label: str, present: bool) -> bool | None:
    if not present:
        if value:
            raise AdjudicationError(f"{label}: leave blank for ABSENT or AMBIGUOUS")
        return None
    if value not in ("Yes", "No"):
        raise AdjudicationError(f"{label}: choose Yes or No")
    return value == "Yes"


def _admissible_spans(text: str) -> list[tuple[int, int]]:
    spans = []
    for item in text.split(";"):
        if not item.strip():
            continue
        ends = [end.strip() for end in item.strip().split("-")]
        if len(ends) != 2 or not all(end.isdigit() for end in ends):
            raise AdjudicationError("Admissible spans: use viewer start-end pairs separated by semicolons")
        spans.append((int(ends[0]), int(ends[1])))
    return spans


def _resolved_record(row: dict, a: dict, workspace_id: str, timestamp: str) -> dict:
    state = row["adj_presence_state"]
    if state not in ("PRESENT", "ABSENT", "AMBIGUOUS"):
        raise AdjudicationError("Presence state: choose PRESENT, ABSENT or AMBIGUOUS")
    present = state == "PRESENT"
    start = _viewer_int(row["adj_start_viewer"], "Start page")
    end = _viewer_int(row["adj_end_viewer"], "End page")
    if (start is None) != (end is None):
        raise AdjudicationError("Primary span: enter both viewer start and end, or neither")
    if present and start is None:
        raise AdjudicationError("Primary span: PRESENT needs viewer start and end")
    if not present and start is not None:
        raise AdjudicationError("Primary span: leave blank for ABSENT or AMBIGUOUS")
    start_shared = _shared(row["adj_start_shared"], "Start page shared", present)
    end_shared = _shared(row["adj_end_shared"], "End page shared", present)
    for shared, key, label in ((start_shared, "adj_start_anchor", "Start anchor"),
                               (end_shared, "adj_end_anchor", "End anchor")):
        if shared is not True and row[key]:
            raise AdjudicationError(f"{label}: leave blank when this page is not shared")
    other = json.loads(row["adj_other_fields_json"] or "{}")
    if not isinstance(other, dict) or set(other) - OTHER_FORM_FIELDS:
        raise AdjudicationError("Other fields JSON: use only the supporting form fields listed in PILOT_COMPARISON.md")
    prov = a["structured_provenance"]
    form = {
        "viewer_page_count": prov["physical_page_count"],
        "viewer_name": prov["viewer_name"], "viewer_version": prov["viewer_version"],
        "presence_state": state, "presence_reason_code": row["adj_reason_code"],
        "primary_span_viewer": (start, end) if present else None,
        "start_page_shared": start_shared, "end_page_shared": end_shared,
        "start_anchor_text": row["adj_start_anchor"], "end_anchor_text": row["adj_end_anchor"],
        "flags": [flag.strip() for flag in row["adj_flags"].split(";") if flag.strip()],
        "admissible_spans_viewer": _admissible_spans(row["adj_admissible_spans_viewer"]),
        "ambiguity_code": row["adj_reason_code"] if state == "AMBIGUOUS" else "NONE",
        "aids_used": a["aids_used"], "search_queries": prov["search_queries"],
        "search_usable": prov["search_usable"],
        "bookmark_pages_viewer": [page + 1 for page in prov["bookmark_pages"]],
        "no_repository_access_attested": prov["no_repository_access_attested"],
        "no_system_output_access_attested": prov["no_system_output_access_attested"],
        **other,
    }
    # Keep page conversion, shared answers, anchors and derived flags in one implementation.
    return core.build_raw_record(form, {
        "document_id": a["document_id"], "source_pdf_sha256": a["source_pdf_sha256"],
        "physical_page_count": prov["physical_page_count"], "annotator_role": "ANNOTATOR_A",
        "workspace_id": workspace_id, "protocol_version_hash": a["protocol_version_hash"],
        "started_at": timestamp, "completed_at": timestamp,
    })


def build_row(row: dict, inputs: dict, workspace_id: str, timestamp: str) -> dict:
    doc, status = row["document_id"], row["adj_status"]
    a, b = inputs["a"].get(doc), inputs["b"].get(doc)
    if a is None or b is None:
        raise AdjudicationError("MISSING raw A or B record: both sealed records are required")
    ar, br = a["record"], b["record"]
    if ar["protocol_version_hash"] != br["protocol_version_hash"]:
        raise AdjudicationError("Raw A/B protocol hashes differ")
    if status == "AGREEMENT_CONFIRMED":
        if not compare.agreement(ar, br)["agree_fully"]:
            raise AdjudicationError("AGREEMENT_CONFIRMED refused: A and B annotation content does not agree")
        record = copy.deepcopy(ar)
        record["timestamps"] = {"started_at": timestamp, "completed_at": timestamp}
        record["structured_provenance"]["annotation_workspace_id"] = workspace_id
        # Confirmation copies the agreed raw content. Reject unnoticed edits on the right.
        if any(row[key] for key in compare.ADJ_COLUMNS if key not in ("adj_status", "adj_reason", "adj_cause")):
            raise AdjudicationError("AGREEMENT_CONFIRMED: leave decision fields blank; the agreed raw content is copied")
    else:
        record = _resolved_record(row, ar, workspace_id, timestamp)
    if status == "AMBIGUITY_PRESERVED" and record["presence_state"] != "AMBIGUOUS":
        raise AdjudicationError("AMBIGUITY_PRESERVED requires an AMBIGUOUS presence state")
    if status == "DISAGREEMENT_RESOLVED" and record["presence_state"] == "AMBIGUOUS":
        raise AdjudicationError("Use AMBIGUITY_PRESERVED when the presence state remains AMBIGUOUS")
    record.update({
        "record_type": "ADJUDICATED", "annotator_role": "ADJUDICATED_RECORD",
        "adjudicator_role": "SEPARATE_ADJUDICATOR", "adjudication_status": status,
        "adjudication_reason": row["adj_reason"],
    })
    record["structured_provenance"]["raw_record_sha256_refs"] = [a["sha256"], b["sha256"]]
    errors = core.validate_record(record, inputs["schema"])
    if errors:
        raise AdjudicationError("; ".join(errors))
    return record


def _read_sheet(sheet: Path, inputs: dict) -> tuple[list[dict], list[str]]:
    rows, problems, seen = [], [], set()
    with sheet.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != compare.SHEET_COLUMNS:
            raise AdjudicationError("Sheet columns differ from ADJUDICATION_SHEET.csv; keep all columns in their original order")
        for line, row in enumerate(reader, 2):
            doc = row.get("document_id") or "missing document_id"
            label = f"row {line} ({doc})"
            if None in row or any(value is None for value in row.values()):
                problems.append(f"{label}: wrong number of cells")
                continue
            if doc not in inputs["roster"]:
                problems.append(f"{label}: document is not in the roster")
                continue
            if doc in seen:
                problems.append(f"{label}: duplicate document")
                continue
            seen.add(doc)
            expected = compare.sheet_row(doc, inputs)
            changed = [key for key in compare.READONLY_COLUMNS if row[key] != expected[key]]
            if changed:
                problems.append(f"{label}: read-only columns changed: {', '.join(changed)}")
            row = {key: value.strip() if key in compare.ADJ_COLUMNS else value for key, value in row.items()}
            if row["adj_status"] not in compare.ADJ_STATUSES:
                problems.append(f"{label}: adj_status is empty or invalid; confirm every row")
            if not row["adj_reason"]:
                problems.append(f"{label}: adj_reason needs a written explanation")
            if row["adj_cause"] not in compare.ADJ_CAUSES:
                problems.append(f"{label}: adj_cause must be one of {', '.join(compare.ADJ_CAUSES)}")
            rows.append(row)
    for doc in sorted(set(inputs["roster"]) - seen):
        problems.append(f"{doc}: MISSING adjudication sheet row")
    return rows, problems


def run_adjudication(sheet: Path, records_a: Path, records_b: Path, roster: Path,
                     out_dir: Path, adjudicator_attest: bool = False,
                     supersession_policy: str | None = None) -> list[tuple[Path, str]]:
    paths = [sheet, records_a, records_b, roster, out_dir]
    _guard_paths(paths, approved=False)
    compare.guard_paths(paths)
    if not adjudicator_attest:
        raise AdjudicationError("--adjudicator-attest is required: confirm you are a separate person who did not annotate A or B")
    out = compare.check_out_dir(out_dir)
    inputs = compare.load_inputs(records_a, records_b, roster, supersession_policy)
    rows, problems = _read_sheet(sheet, inputs)
    timestamp = core.now_rfc3339()
    sheet_hash = core.sha256_file(sheet)
    workspace_id = "adjudication-" + sheet_hash[:32]
    built = []
    for row in sorted(rows, key=lambda item: item["document_id"]):
        if row["adj_status"] not in compare.ADJ_STATUSES or not row["adj_reason"]:
            continue
        try:
            built.append(build_row(row, inputs, workspace_id, timestamp))
        except (ValueError, TypeError, KeyError, IndexError, AttributeError, core.AnnotatorError) as exc:
            problems.append(f"{row['document_id']}: {exc}")
    if problems:
        raise AdjudicationError("Nothing was written. Problem rows:\n- " + "\n- ".join(problems))
    # No filesystem mutations precede validation of the entire sheet.
    folder = out / "ADJUDICATED"
    statuses, causes = Counter(row["adj_status"] for row in rows), Counter(row["adj_cause"] for row in rows)
    summary = ["# Adjudication summary", "", f"Tool: {TOOL_VERSION}; annotator core: {core.TOOL_VERSION}",
               f"Sheet SHA-256: {sheet_hash}", f"Supersession policy: {supersession_policy or 'Not needed'}",
               "Separate adjudicator attested: Yes.", f"Sealed records: {len(built)}", "",
               "## Status counts", "", "| Status | Count |", "|---|---|"]
    summary += [f"| {status} | {statuses[status]} |" for status in compare.ADJ_STATUSES]
    summary += ["", "## Cause counts", "", "| Cause | Count |", "|---|---|"]
    summary += [f"| {cause} | {causes[cause]} |" for cause in compare.ADJ_CAUSES]
    summary += ["", "## Sealed records", "", "| Document | SHA-256 |", "|---|---|"]
    sealed = []
    for record in built:
        data = core.canonical_json_bytes(record)
        digest = hashlib.sha256(data).hexdigest()
        name = f"{record['document_id']}__ADJUDICATED_RECORD__{digest[:8]}.json"
        sealed.append(core._write_sealed(folder, name, data, folder))
        summary.append(f"| {record['document_id']} | {digest} |")
    with (out / "ADJUDICATION_SUMMARY.md").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write("\n".join(summary) + "\n")
    return sealed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ("sheet", "records-a", "records-b", "roster", "out-dir"):
        parser.add_argument(f"--{option}", required=True, type=Path)
    parser.add_argument("--adjudicator-attest", action="store_true",
                        help="confirm you are a separate person who did not annotate A or B")
    parser.add_argument("--supersession-policy", choices=("first", "replacement"),
                        help="use the policy used to generate the sheet; required when supersession exists")
    args = parser.parse_args(argv)
    try:
        sealed = run_adjudication(args.sheet, args.records_a, args.records_b, args.roster,
                                  args.out_dir, args.adjudicator_attest, args.supersession_policy)
    except (ValueError, OSError, TypeError, KeyError, core.AnnotatorError) as exc:
        print(f"ADJUDICATION REFUSED: {exc}", file=sys.stderr)
        return 2
    for path, digest in sealed:
        print(f"{digest}  ADJUDICATED/{path.name}")
    print(f"{core.sha256_file(args.out_dir / 'ADJUDICATION_SUMMARY.md')}  ADJUDICATION_SUMMARY.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
