"""Synthetic-only adjudication tests: every raw record is made in tmp_path."""

from __future__ import annotations

import copy
import csv
import json
import stat
import subprocess

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from tools.phase5 import adjudicate, pilot_compare as compare
from tools.phase5.annotator import annotator_core as core
from tests.test_phase5_pilot_compare import (
    PINNED_PYTHON, add_supersession, make_case, run_case, sheet_rows,
)


def write_sheet(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=compare.SHEET_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def filled_case(tmp_path):
    case = make_case(tmp_path, count=3, changes_b={
        1: {"presence_state": "ABSENT", "presence_reason_code": "TOC_ONLY"},
        2: {"primary_span_viewer": (10, 19)},
    })
    run_case(case)
    sheet = tmp_path / "comparison/ADJUDICATION_SHEET.csv"
    rows = sheet_rows(sheet)
    rows[0].update(adj_status="AGREEMENT_CONFIRMED", adj_reason="Both synthetic annotations agree.", adj_cause="OTHER")
    rows[1].update(adj_status="DISAGREEMENT_RESOLVED", adj_presence_state="PRESENT",
                   adj_reason_code="BODY_QUALIFYING_TITLE", adj_start_viewer="10", adj_end_viewer="18",
                   adj_start_shared="Yes", adj_end_shared="Yes", adj_start_anchor="Synthetic MD&A",
                   adj_end_anchor="Synthetic next section", adj_flags="stub",
                   adj_reason="Resolved the synthetic presence disagreement.", adj_cause="ANNOTATOR_MISSED_RULE")
    rows[2].update(adj_status="AMBIGUITY_PRESERVED", adj_presence_state="AMBIGUOUS",
                   adj_reason_code="END_UNRESOLVABLE", adj_admissible_spans_viewer="10-18;10-19",
                   adj_flags="unclear_end", adj_reason="Both synthetic ends remain admissible.", adj_cause="RULE_UNCLEAR")
    write_sheet(sheet, rows)
    return case, sheet, rows


def adjudicate_case(case, sheet, name="adjudicated", policy=None):
    return adjudicate.run_adjudication(sheet, case.a, case.b, case.roster, case.root / name,
                                       adjudicator_attest=True, supersession_policy=policy)


def test_confirmed_resolved_and_ambiguity_records_seal_and_validate(tmp_path):
    case, sheet, rows = filled_case(tmp_path)
    sealed = adjudicate_case(case, sheet)
    assert len(sealed) == 3
    validator = Draft202012Validator(case.schema, format_checker=FormatChecker())
    records = []
    for path, digest in sealed:
        record = json.loads(path.read_text(encoding="utf-8"))
        records.append(record)
        assert list(validator.iter_errors(record)) == []
        assert core.tool_invariant_errors(record) == []
        assert path.read_bytes() == core.canonical_json_bytes(record)
        assert core.sha256_file(path) == digest and path.stem.endswith(digest[:8])
        assert not path.stat().st_mode & stat.S_IWUSR
        assert record["record_type"] == "ADJUDICATED"
        assert record["annotator_role"] == "ADJUDICATED_RECORD"
        assert record["adjudicator_role"] == "SEPARATE_ADJUDICATOR"
        assert record["adjudication_reason"] == rows[len(records) - 1]["adj_reason"]
        assert record["structured_provenance"]["raw_record_sha256_refs"] == [
            case.seals[(record["document_id"], "ANNOTATOR_A")][1],
            case.seals[(record["document_id"], "ANNOTATOR_B")][1],
        ]
    assert compare.annotation_content(records[0]) == compare.annotation_content(case.raw[("SYN-00", "ANNOTATOR_A")])
    assert records[1]["primary_span"] == {"start_page": 9, "end_page": 17}
    assert records[1]["boundary_evidence"]["mixed_end_page"] == 17
    assert records[1]["flags"] == ["mixed_end_page", "mixed_start_page", "stub"]
    assert records[2]["primary_span"] is None
    assert records[2]["admissible_spans"] == [{"start_page": 9, "end_page": 17}, {"start_page": 9, "end_page": 18}]
    assert records[2]["ambiguity_code"] == "END_UNRESOLVABLE"
    log = core.read_hash_log(tmp_path / "adjudicated/ADJUDICATED")
    assert log == [(digest, path.name) for path, digest in sealed]
    summary = (tmp_path / "adjudicated/ADJUDICATION_SUMMARY.md").read_text(encoding="utf-8")
    for status in compare.ADJ_STATUSES:
        assert f"| {status} | 1 |" in summary
    assert "| ANNOTATOR_MISSED_RULE | 1 |" in summary and "| RULE_UNCLEAR | 1 |" in summary


@pytest.mark.parametrize("field,value,expected", [
    ("adj_start_viewer", "0", "outside 1..40"),
    ("adj_end_viewer", "9", "start <= end"),
    ("adj_start_shared", "", "choose Yes or No"),
    ("adj_start_anchor", "", "heading line"),
    ("adj_reason", "  ", "adj_reason needs a written explanation"),
    ("adj_status", "", "adj_status is empty or invalid"),
    ("adj_cause", "unexpected", "adj_cause must be one of"),
    ("adj_flags", "annexure", "Annexure identity"),
    ("adj_other_fields_json", "{", "Expecting"),
    ("adj_other_fields_json", '{"source_pdf_sha256":"wrong"}', "supporting form fields"),
])
def test_invalid_row_blocks_entire_run_without_creating_output(tmp_path, field, value, expected):
    case, sheet, rows = filled_case(tmp_path)
    rows[1][field] = value
    write_sheet(sheet, rows)
    with pytest.raises(adjudicate.AdjudicationError, match=expected):
        adjudicate_case(case, sheet)
    assert not (tmp_path / "adjudicated").exists()


def test_every_problem_row_is_listed_and_existing_empty_output_stays_empty(tmp_path):
    case, sheet, rows = filled_case(tmp_path)
    rows[0]["adj_reason"] = ""
    rows[1]["adj_status"] = ""
    rows[2]["adj_admissible_spans_viewer"] = ""
    write_sheet(sheet, rows)
    out = tmp_path / "adjudicated"
    out.mkdir()
    with pytest.raises(adjudicate.AdjudicationError) as failure:
        adjudicate_case(case, sheet)
    assert all(doc in str(failure.value) for doc in ("SYN-00", "SYN-01", "SYN-02"))
    assert list(out.iterdir()) == []


@pytest.mark.parametrize("changes", [
    {"presence_state": "ABSENT", "presence_reason_code": "TOC_ONLY"},
    {"primary_span_viewer": (11, 18)},
    {"start_page_shared": True},
    {"flags": ["stub"]},
    {"presence_reason_code": "CONDITIONAL_TITLE_CONTEXT_MET"},
])
def test_agreement_confirmation_refuses_actual_raw_disagreement(tmp_path, changes):
    case = make_case(tmp_path, count=1, changes_b={0: changes})
    run_case(case)
    sheet = tmp_path / "comparison/ADJUDICATION_SHEET.csv"
    rows = sheet_rows(sheet)
    rows[0].update(adj_status="AGREEMENT_CONFIRMED", adj_reason="Attempted synthetic confirmation", adj_cause="OTHER")
    write_sheet(sheet, rows)
    with pytest.raises(adjudicate.AdjudicationError, match="annotation content does not agree"):
        adjudicate_case(case, sheet)
    assert not (tmp_path / "adjudicated").exists()


def test_derived_mixed_flags_cannot_be_set_by_the_flags_cell(tmp_path):
    case, sheet, rows = filled_case(tmp_path)
    rows[1].update(adj_start_shared="No", adj_end_shared="No", adj_start_anchor="", adj_end_anchor="",
                   adj_flags="mixed_start_page;mixed_end_page;stub")
    write_sheet(sheet, rows)
    records = [json.loads(path.read_text(encoding="utf-8")) for path, _ in adjudicate_case(case, sheet)]
    assert records[1]["flags"] == ["stub"]
    assert records[1]["boundary_evidence"]["mixed_end_page"] is None
    assert records[1]["boundary_evidence"]["start_anchor_text"] is None


def test_optional_supporting_fields_convert_viewer_pages_and_validate(tmp_path):
    case, sheet, rows = filled_case(tmp_path)
    rows[1]["adj_flags"] = "annexure;embedded_in_directors_report;noncontiguous_hull;contains_csr_esg"
    rows[1]["adj_other_fields_json"] = json.dumps({
        "annexure_identity": "Synthetic Annexure A", "parent_section": "Synthetic Board report",
        "gap_pages_viewer": [12], "csr_esg_pages_viewer": [14],
        "boundary_evidence_viewer": {"heading_start_page": 10, "last_content_page": 18},
        "alternative_spans_viewer": [[10, 19, "BOUNDARY_ALTERNATIVE"]],
    })
    write_sheet(sheet, rows)
    record = json.loads(adjudicate_case(case, sheet)[1][0].read_text(encoding="utf-8"))
    assert record["gap_pages"] == [11] and record["csr_esg_pages"] == [13]
    assert record["alternative_spans"] == [{"start_page": 9, "end_page": 18, "type": "BOUNDARY_ALTERNATIVE"}]
    assert record["boundary_evidence"]["heading_start_page"] == 9
    assert record["annexure_identity"] == "Synthetic Annexure A"


def test_resolved_absence_has_no_primary_or_shared_fields(tmp_path):
    case, sheet, rows = filled_case(tmp_path)
    rows[1].update(adj_presence_state="ABSENT", adj_reason_code="TOC_ONLY", adj_start_viewer="",
                   adj_end_viewer="", adj_start_shared="", adj_end_shared="", adj_start_anchor="",
                   adj_end_anchor="", adj_flags="")
    write_sheet(sheet, rows)
    record = json.loads(adjudicate_case(case, sheet)[1][0].read_text(encoding="utf-8"))
    assert record["presence_state"] == "ABSENT" and record["primary_span"] is None
    assert record["flags"] == []
    assert record["boundary_evidence"]["start_page_shared"] is None


@pytest.mark.parametrize("damage", ["changed_readonly", "duplicate", "missing", "unknown", "blank_row"])
def test_sheet_identity_and_roster_coverage(tmp_path, damage):
    case, sheet, rows = filled_case(tmp_path)
    if damage == "changed_readonly":
        rows[0]["a_start_viewer"] = "11"
    elif damage == "duplicate":
        rows.append(copy.deepcopy(rows[0]))
    elif damage == "missing":
        rows.pop()
    elif damage == "unknown":
        rows[0]["document_id"] = "SYN-unknown"
    else:
        rows.append({key: "" for key in compare.SHEET_COLUMNS})
    write_sheet(sheet, rows)
    with pytest.raises(adjudicate.AdjudicationError):
        adjudicate_case(case, sheet)
    assert not (tmp_path / "adjudicated").exists()


def test_missing_raw_record_prevents_adjudication(tmp_path):
    case = make_case(tmp_path, count=1, missing=((0, "ANNOTATOR_B"),))
    run_case(case)
    sheet = tmp_path / "comparison/ADJUDICATION_SHEET.csv"
    rows = sheet_rows(sheet)
    rows[0].update(adj_status="AGREEMENT_CONFIRMED", adj_reason="Synthetic reason", adj_cause="OTHER")
    write_sheet(sheet, rows)
    with pytest.raises(adjudicate.AdjudicationError, match="MISSING raw A or B"):
        adjudicate_case(case, sheet)


def test_supersession_policy_must_match_the_sheet_and_raw_refs(tmp_path):
    case = make_case(tmp_path, count=1)
    _, replacement, _, _ = add_supersession(case)
    run_case(case, policy="replacement")
    sheet = tmp_path / "comparison/ADJUDICATION_SHEET.csv"
    rows = sheet_rows(sheet)
    rows[0].update(adj_status="DISAGREEMENT_RESOLVED", adj_presence_state="PRESENT",
                   adj_reason_code="BODY_QUALIFYING_TITLE", adj_start_viewer="13", adj_end_viewer="18",
                   adj_start_shared="No", adj_end_shared="No", adj_reason="Synthetic replacement chosen", adj_cause="TYPING_SLIP")
    write_sheet(sheet, rows)
    with pytest.raises(compare.ComparisonError, match="supersession-policy.*required"):
        adjudicate_case(case, sheet)
    with pytest.raises(adjudicate.AdjudicationError, match="read-only columns changed"):
        adjudicate_case(case, sheet, policy="first")
    sealed = adjudicate_case(case, sheet, policy="replacement")
    record = json.loads(sealed[0][0].read_text(encoding="utf-8"))
    assert record["structured_provenance"]["raw_record_sha256_refs"][0] == replacement


def test_refuses_overwrite_even_if_a_later_run_would_have_a_different_hash(tmp_path, monkeypatch):
    case, sheet, _ = filled_case(tmp_path)
    adjudicate_case(case, sheet)
    paths = list((tmp_path / "adjudicated").rglob("*"))
    before = {path: path.read_bytes() for path in paths if path.is_file()}
    monkeypatch.setattr(core, "now_rfc3339", lambda: "2026-10-02T13:00:00+05:30")
    with pytest.raises(compare.ComparisonError, match="refusing to overwrite"):
        adjudicate_case(case, sheet)
    assert before == {path: path.read_bytes() for path in before}


def test_attestation_required_before_inputs_are_read(tmp_path, monkeypatch):
    monkeypatch.setattr(compare, "load_inputs", lambda *_: pytest.fail("must not read inputs"))
    with pytest.raises(adjudicate.AdjudicationError, match="adjudicator-attest is required"):
        adjudicate.run_adjudication(tmp_path / "sheet", tmp_path / "a", tmp_path / "b",
                                    tmp_path / "roster", tmp_path / "out")


def test_adjudication_output_inside_repo_is_refused(tmp_path):
    out = compare.REPO_ROOT / "synthetic-refused-adjudication"
    with pytest.raises(compare.ComparisonError, match="outside the repository"):
        adjudicate.run_adjudication(tmp_path / "sheet", tmp_path / "a", tmp_path / "b",
                                    tmp_path / "roster", out, True)
    assert not out.exists()


@pytest.mark.parametrize("option", ["sheet", "records-a", "records-b", "roster", "out-dir"])
def test_adjudication_cli_reserved_path_guard_runs_before_reading(tmp_path, monkeypatch, capsys, option):
    monkeypatch.setattr(compare, "load_inputs", lambda *_: pytest.fail("must not read inputs"))
    values = {key: str(tmp_path / key) for key in ("sheet", "records-a", "records-b", "roster", "out-dir")}
    values[option] = str(tmp_path / "HoLdOuT-synthetic-only")
    args = [value for key, val in values.items() for value in ("--" + key, val)] + ["--adjudicator-attest"]
    assert adjudicate.main(args) == 2
    assert "HOLDOUT path refused" in capsys.readouterr().err


def test_adjudication_cli_with_pinned_interpreter(tmp_path):
    if not PINNED_PYTHON.is_file():
        pytest.skip("the required Windows interpreter is not available")
    case, sheet, _ = filled_case(tmp_path)
    command = [str(PINNED_PYTHON), "-m", "tools.phase5.adjudicate", "--sheet", str(sheet),
               "--records-a", str(case.a), "--records-b", str(case.b), "--roster", str(case.roster),
               "--out-dir", str(tmp_path / "cli"), "--adjudicator-attest"]
    result = subprocess.run(command, cwd=compare.REPO_ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "ADJUDICATION_SUMMARY.md" in result.stdout
