"""Synthetic-only pilot comparison and post-pilot annotator tests.

All annotation records are generated in tmp_path. No actual PDF or Gold is used.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

from tools.phase5 import pilot_compare as compare
from tools.phase5.annotator import annotator_core as core
from tools.phase5.scoring import raw_ab_agreement

PINNED_PYTHON = Path("D:/sem_iitk/sem9/thesis/.venv/Scripts/python.exe")


def synthetic_record(schema: dict, doc: str, role: str, **changes) -> dict:
    form = {
        "viewer_page_count": 40, "viewer_name": "SyntheticViewer", "viewer_version": "1.0",
        "presence_state": "PRESENT", "presence_reason_code": "BODY_QUALIFYING_TITLE",
        "primary_span_viewer": (10, 18), "start_page_shared": False, "end_page_shared": False,
        "boundary_evidence_viewer": {"heading_start_page": 10, "last_content_page": 18},
        "aids_used": ["PDF_VIEWER"], "no_repository_access_attested": True,
        "no_system_output_access_attested": True, **changes,
    }
    if form["presence_state"] != "PRESENT":
        form.update(primary_span_viewer=None, start_page_shared=None, end_page_shared=None,
                    boundary_evidence_viewer={})
    for key, anchor in core.ANCHOR_TEXT_FIELDS.items():
        if form[key] is True:
            form.setdefault(anchor, "Synthetic heading")
    record = core.build_raw_record(form, {
        "document_id": doc, "source_pdf_sha256": hashlib.sha256(doc.encode()).hexdigest(),
        "physical_page_count": 40, "annotator_role": role, "workspace_id": "synthetic-" + role,
        "protocol_version_hash": hashlib.sha256(b"synthetic protocol").hexdigest(),
        "started_at": "2026-10-01T09:00:00+05:30", "completed_at": "2026-10-01T09:12:34+05:30",
    })
    assert not core.validate_record(record, schema)
    return record


def write_roster(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=compare.ROSTER_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


@dataclass
class SyntheticCase:
    root: Path
    a: Path
    b: Path
    roster: Path
    schema: dict
    raw: dict
    seals: dict


def make_case(tmp_path: Path, count: int = 10, changes_a: dict | None = None,
              changes_b: dict | None = None, missing: tuple = ()) -> SyntheticCase:
    schema = json.loads(compare.SCHEMA_PATH.read_text(encoding="utf-8"))
    a, b = tmp_path / "records-a", tmp_path / "records-b"
    for root, role in ((a, "ANNOTATOR_A"), (b, "ANNOTATOR_B")):
        (root / role).mkdir(parents=True)
        (root / core.HASH_LOG_NAME).write_text("", encoding="utf-8")
    rows, raw, seals = [], {}, {}
    for index in range(count):
        doc = f"SYN-{index:02d}"
        rows.append({"document_id": doc, "source_pdf_sha256": hashlib.sha256(doc.encode()).hexdigest(),
                     "physical_page_count": 40, "split": "FIT"})
        for root, role, changes in ((a, "ANNOTATOR_A", changes_a), (b, "ANNOTATOR_B", changes_b)):
            if (index, role) in missing:
                continue
            record = synthetic_record(schema, doc, role, **(changes or {}).get(index, {}))
            raw[(doc, role)] = record
            seals[(doc, role)] = core.seal_raw_record(root, record, schema, allow_unfrozen_title_list=True)
    roster = tmp_path / "PILOT_ROSTER.csv"
    write_roster(roster, rows)
    return SyntheticCase(tmp_path, a, b, roster, schema, raw, seals)


def run_case(case: SyntheticCase, name: str = "comparison", policy: str | None = None) -> dict:
    return compare.run_comparison(case.a, case.b, case.roster, case.root / name, policy)


def sheet_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def reseal_changed(case: SyntheticCase, doc: str, role: str, record: dict,
                   filename: str | None = None) -> tuple[Path, str]:
    """Replace a synthetic test fixture's bytes/log, bypassing validation deliberately."""
    old_path, _ = case.seals[(doc, role)]
    root = case.a if role == "ANNOTATOR_A" else case.b
    data = core.canonical_json_bytes(record)
    digest = hashlib.sha256(data).hexdigest()
    old_path.chmod(stat.S_IWRITE | stat.S_IREAD)
    old_path.unlink()
    new_path = old_path.parent / (filename or f"{doc}__{role}__{digest[:8]}.json")
    new_path.write_bytes(data)
    log = root / core.HASH_LOG_NAME
    original = old_path.relative_to(root).as_posix()
    lines = [line for line in log.read_text(encoding="utf-8").splitlines() if not line.endswith("  " + original)]
    lines.append(f"{digest}  {new_path.relative_to(root).as_posix()}")
    log.write_text("\n".join(lines) + "\n", encoding="utf-8")
    case.seals[(doc, role)] = (new_path, digest)
    return new_path, digest


def add_supersession(case: SyntheticCase, doc: str = "SYN-00", role: str = "ANNOTATOR_A", start: int = 13):
    root = case.a if role == "ANNOTATOR_A" else case.b
    replacement = synthetic_record(case.schema, doc, role, primary_span_viewer=(start, 18))
    return core.supersede(root, case.seals[(doc, role)][1], replacement,
                          "Synthetic typing correction", case.schema, "synthetic-workspace",
                          allow_unfrozen_title_list=True)


def test_agreement_reuses_scoring_and_keeps_all_decisions_empty(tmp_path):
    case = make_case(tmp_path)
    report = run_case(case)
    assert report["raw_ab_agreement"] == raw_ab_agreement(
        [case.raw[(f"SYN-{i:02d}", "ANNOTATOR_A")] for i in range(10)],
        [case.raw[(f"SYN-{i:02d}", "ANNOTATOR_B")] for i in range(10)])
    row = report["documents"][0]
    assert row["a"]["span_0based"] == {"start_page": 9, "end_page": 17}
    assert row["a"]["span_viewer_1based"] == {"start_page": 10, "end_page": 18}
    assert row["a"]["minutes"] == 12.6
    assert row["iou"] == 1 and row["agree_fully"]
    assert row["start_diff_a_minus_b"] == row["end_diff_a_minus_b"] == 0
    sheet = sheet_rows(tmp_path / "comparison/ADJUDICATION_SHEET.csv")
    assert all(row["suggested_status"] == "AGREEMENT_CONFIRMED" for row in sheet)
    assert all(not row[key] for row in sheet for key in compare.ADJ_COLUMNS)
    assert report["triggers"][3]["status"] == "NEEDS_HUMAN_CHECK"
    for label, digest in report["input_file_sha256"].items():
        assert core.SHA256_RE.fullmatch(digest), label
    markdown = (tmp_path / "comparison/PILOT_COMPARISON.md").read_text(encoding="utf-8")
    assert "| SYN-00 | A | Heading page | 10 |" in markdown
    assert "| SYN-00 | A | Last content page | 18 |" in markdown
    assert "| SYN-00 | Yes | Yes | Yes | Yes | Yes |" in markdown
    assert row["a"]["raw_record_sha256"] in markdown


def test_presence_disagreement_and_noncomparable_span(tmp_path):
    case = make_case(tmp_path, changes_b={0: {"presence_state": "ABSENT", "presence_reason_code": "TOC_ONLY"}})
    report = run_case(case)
    row = report["documents"][0]
    assert not row["agree_state"] and row["iou"] is None
    assert row["start_diff_a_minus_b"] is None and row["b"]["state"] == "ABSENT"
    assert report["raw_ab_agreement"]["exact_state_agreement"]["count"] == 9


@pytest.mark.parametrize("difference", [1, 3])
@pytest.mark.parametrize("boundary", ["start", "end"])
def test_boundary_differences_are_signed_inclusive_and_count_once(tmp_path, difference, boundary):
    span = (10 + difference, 18) if boundary == "start" else (10, 18 + difference)
    case = make_case(tmp_path, count=1, changes_b={0: {"primary_span_viewer": span}})
    report = run_case(case)
    row = report["documents"][0]
    assert row[f"{boundary}_diff_a_minus_b"] == -difference
    assert 0 < row["iou"] < 1
    assert report["triggers"][1]["count"] == (1 if difference > 1 else 0)


def test_shared_answer_and_flag_disagreement(tmp_path):
    case = make_case(tmp_path, count=1, changes_b={0: {"start_page_shared": True}})
    row = run_case(case)["documents"][0]
    assert not row["agree_shared_answers"] and not row["agree_flags"]
    assert row["flags_symmetric_difference"] == ["mixed_start_page"]
    assert not sheet_rows(tmp_path / "comparison/ADJUDICATION_SHEET.csv")[0]["suggested_status"]


def test_reason_and_anchor_differences_prevent_full_agreement_suggestion(tmp_path):
    case = make_case(tmp_path, count=1,
                     changes_a={0: {"start_page_shared": True, "start_anchor_text": "Synthetic A"}},
                     changes_b={0: {"start_page_shared": True, "start_anchor_text": "Synthetic B"}})
    row = run_case(case)["documents"][0]
    assert row["agree_state"] and row["agree_span_exact"] and row["agree_flags"]
    assert not row["agree_fully"]


@pytest.mark.parametrize("missing", [((0, "ANNOTATOR_B"),), ((0, "ANNOTATOR_A"), (0, "ANNOTATOR_B"))])
def test_missing_records_are_visible_and_do_not_crash(tmp_path, missing):
    case = make_case(tmp_path, count=1, missing=missing)
    report = run_case(case)
    assert report["paired_document_count"] == report["raw_ab_agreement"]["pair_count"] == 0
    assert report["missing_documents"] == ["SYN-00"]
    assert report["documents"][0]["b"]["state"] == "MISSING"
    assert report["documents"][0]["agree_flags"] is None
    assert sheet_rows(tmp_path / "comparison/ADJUDICATION_SHEET.csv")[0]["b_state"] == "MISSING"


def test_tampered_record_is_refused_before_any_output(tmp_path):
    case = make_case(tmp_path, count=1)
    path, _ = case.seals[("SYN-00", "ANNOTATOR_A")]
    path.chmod(stat.S_IWRITE | stat.S_IREAD)
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(compare.ComparisonError, match="hash mismatch"):
        run_case(case)
    assert not (tmp_path / "comparison").exists()


@pytest.mark.parametrize("field", ["source_pdf_sha256", "physical_page_count"])
def test_roster_identity_mismatch(tmp_path, field):
    case = make_case(tmp_path, count=1)
    rows = sheet_rows(case.roster)
    rows[0][field] = hashlib.sha256(b"wrong synthetic identity").hexdigest() if field == "source_pdf_sha256" else "39"
    write_roster(case.roster, rows)
    with pytest.raises(compare.ComparisonError, match=field + " does not match roster"):
        run_case(case)


def test_wrong_role_folder_and_role_value_are_refused(tmp_path):
    case = make_case(tmp_path, count=1)
    raw = copy.deepcopy(case.raw[("SYN-00", "ANNOTATOR_A")])
    raw["annotator_role"] = "ANNOTATOR_B"
    reseal_changed(case, "SYN-00", "ANNOTATOR_A", raw)
    with pytest.raises(compare.ComparisonError, match="annotator_role does not equal folder role"):
        run_case(case)
    (case.b / "ANNOTATOR_B").rename(case.b / "ANNOTATOR_A")
    with pytest.raises(compare.ComparisonError, match="wrong role folder"):
        compare.load_export(case.b, "ANNOTATOR_B", compare.load_roster(case.roster), case.schema)


@pytest.mark.parametrize("damage", ["unlisted", "missing_logged_file", "filename_prefix", "unsafe_log", "duplicate_log"])
def test_export_log_and_filename_integrity(tmp_path, damage):
    case = make_case(tmp_path, count=1)
    path, digest = case.seals[("SYN-00", "ANNOTATOR_A")]
    log = case.a / core.HASH_LOG_NAME
    if damage == "unlisted":
        (path.parent / "extra.json").write_text("{}", encoding="utf-8")
    elif damage == "missing_logged_file":
        path.chmod(stat.S_IWRITE | stat.S_IREAD)
        path.unlink()
    elif damage == "filename_prefix":
        reseal_changed(case, "SYN-00", "ANNOTATOR_A", case.raw[("SYN-00", "ANNOTATOR_A")], "SYN-00__ANNOTATOR_A__00000000.json")
    elif damage == "unsafe_log":
        log.write_text(f"{digest}  ../outside.json\n", encoding="utf-8")
    else:
        log.write_text(log.read_text(encoding="utf-8") * 2, encoding="utf-8")
    with pytest.raises(compare.ComparisonError):
        run_case(case)
    assert not (tmp_path / "comparison").exists()


def test_schema_invalid_record_refuses_and_reports_fired_trigger(tmp_path, capsys):
    case = make_case(tmp_path, count=1)
    raw = copy.deepcopy(case.raw[("SYN-00", "ANNOTATOR_A")])
    raw["ambiguity_code"] = "START_UNRESOLVABLE"
    reseal_changed(case, "SYN-00", "ANNOTATOR_A", raw)
    assert compare.main(["--records-a", str(case.a), "--records-b", str(case.b),
                         "--roster", str(case.roster), "--out-dir", str(tmp_path / "comparison")]) == 2
    error = capsys.readouterr().err
    assert "FIRED; count=1, threshold=1" in error and "SYN-00" in error and "Ambiguity code" in error
    assert not (tmp_path / "comparison").exists()


def test_supersession_requires_policy_and_reports_original_replacement(tmp_path):
    case = make_case(tmp_path, count=1)
    replacement_path, replacement_hash, note_path, note_hash = add_supersession(case)
    with pytest.raises(compare.ComparisonError, match="supersession-policy.*required"):
        run_case(case)
    first = run_case(case, "first", "first")
    replacement = run_case(case, "replacement", "replacement")
    original = case.seals[("SYN-00", "ANNOTATOR_A")][1]
    assert first["documents"][0]["a"]["raw_record_sha256"] == original
    assert replacement["documents"][0]["a"]["raw_record_sha256"] == replacement_hash
    audit = replacement["supersessions"][0]
    assert audit["original_sha256"] == original and audit["replacement_sha256"] == replacement_hash
    assert audit["notes"][0]["note_sha256"] == note_hash
    assert replacement_path.exists() and note_path.exists()


def test_supersession_chain_uses_first_and_terminal_not_hash_sort_order(tmp_path):
    case = make_case(tmp_path, count=1)
    _, middle_hash, _, _ = add_supersession(case)
    new_record = synthetic_record(case.schema, "SYN-00", "ANNOTATOR_A", primary_span_viewer=(15, 18))
    _, last_hash, _, _ = core.supersede(case.a, middle_hash, new_record, "Second synthetic correction",
                                       case.schema, "synthetic", allow_unfrozen_title_list=True)
    report = run_case(case, policy="replacement")
    assert report["supersessions"][0]["chain_sha256"] == [case.seals[("SYN-00", "ANNOTATOR_A")][1], middle_hash, last_hash]


def test_unlinked_second_raw_is_refused(tmp_path):
    case = make_case(tmp_path, count=1)
    record = synthetic_record(case.schema, "SYN-00", "ANNOTATOR_A", primary_span_viewer=(13, 18))
    data = core.canonical_json_bytes(record)
    digest = hashlib.sha256(data).hexdigest()
    core._write_sealed(case.a / "ANNOTATOR_A", f"SYN-00__ANNOTATOR_A__{digest[:8]}.json", data, case.a)
    with pytest.raises(compare.ComparisonError, match="one supersession chain"):
        run_case(case)


@pytest.mark.parametrize("presence_count,boundary_count,status_presence,status_boundary", [
    (1, 2, "NOT_FIRED", "NOT_FIRED"), (2, 3, "FIRED", "FIRED"), (3, 4, "FIRED", "FIRED"),
])
def test_trigger_thresholds_are_document_counts(tmp_path, presence_count, boundary_count, status_presence, status_boundary):
    changes = {i: {"presence_state": "ABSENT", "presence_reason_code": "TOC_ONLY"} for i in range(presence_count)}
    changes.update({i: {"primary_span_viewer": (13, 21)} for i in range(presence_count, presence_count + boundary_count)})
    report = run_case(make_case(tmp_path, changes_b=changes))
    presence, boundary, invalid = report["triggers"][:3]
    assert (presence["count"], presence["threshold"], presence["status"]) == (presence_count, 2, status_presence)
    assert (boundary["count"], boundary["threshold"], boundary["status"]) == (boundary_count, 3, status_boundary)
    assert invalid["count"] == 0 and invalid["status"] == "NOT_FIRED"


def test_outputs_are_byte_identical_and_inputs_unchanged(tmp_path):
    case = make_case(tmp_path, count=2)
    paths = [case.roster, case.a / core.HASH_LOG_NAME, case.b / core.HASH_LOG_NAME]
    paths += [path for path, _ in case.seals.values()]
    before = {path: path.read_bytes() for path in paths}
    run_case(case, "one")
    run_case(case, "two")
    for filename in ("PILOT_COMPARISON.json", "PILOT_COMPARISON.md", "ADJUDICATION_SHEET.csv"):
        assert (tmp_path / "one" / filename).read_bytes() == (tmp_path / "two" / filename).read_bytes()
    assert before == {path: path.read_bytes() for path in paths}


def test_inside_repo_output_refused_before_loading_inputs(tmp_path, monkeypatch):
    monkeypatch.setattr(compare, "load_inputs", lambda *_: pytest.fail("must not read inputs"))
    out = compare.REPO_ROOT / "synthetic-refused-output"
    with pytest.raises(compare.ComparisonError, match="outside the repository"):
        compare.run_comparison(tmp_path / "a", tmp_path / "b", tmp_path / "roster.csv", out)
    assert not out.exists()


@pytest.mark.parametrize("option", ["records-a", "records-b", "roster", "out-dir"])
def test_reserved_path_refused_before_reading_any_input(tmp_path, monkeypatch, capsys, option):
    monkeypatch.setattr(compare, "load_inputs", lambda *_: pytest.fail("must not read inputs"))
    values = {key: str(tmp_path / key) for key in ("records-a", "records-b", "roster", "out-dir")}
    values[option] = str(tmp_path / "HoLdOuT-synthetic-only")
    args = [value for key, val in values.items() for value in ("--" + key, val)]
    assert compare.main(args) == 2
    assert "HOLDOUT path refused" in capsys.readouterr().err


def test_reserved_roster_split_refused_on_synthetic_metadata(tmp_path):
    case = make_case(tmp_path, count=1)
    rows = sheet_rows(case.roster)
    rows[0]["split"] = "HOLDOUT"
    write_roster(case.roster, rows)
    with pytest.raises(compare.ComparisonError, match="HOLDOUT split refused"):
        run_case(case)


def test_cli_runs_with_pinned_interpreter_and_prints_output_hashes(tmp_path):
    if not PINNED_PYTHON.is_file():
        pytest.skip("the required Windows interpreter is not available")
    case = make_case(tmp_path, count=1)
    command = [str(PINNED_PYTHON), "-m", "tools.phase5.pilot_compare", "--records-a", str(case.a),
               "--records-b", str(case.b), "--roster", str(case.roster), "--out-dir", str(tmp_path / "cli")]
    result = subprocess.run(command, cwd=compare.REPO_ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    for filename in ("PILOT_COMPARISON.json", "PILOT_COMPARISON.md", "ADJUDICATION_SHEET.csv"):
        assert f"{core.sha256_file(tmp_path / 'cli' / filename)}  {filename}" in result.stdout


@pytest.mark.parametrize("changes,expected", [
    ({"ambiguity_code": "START_UNRESOLVABLE"}, "Ambiguity code: choose NONE"),
    ({"presence_state": "ABSENT", "presence_reason_code": "TOC_ONLY", "primary_span": None,
      "ambiguity_code": "START_UNRESOLVABLE"}, "Ambiguity code: choose NONE"),
    ({"flags": ["annexure"]}, "Annexure identity: type the printed identity"),
    ({"flags": ["embedded_in_directors_report"]}, "Parent section: type the parent heading"),
    ({"flags": ["contains_csr_esg"]}, "CSR/ESG pages: enter the viewer pages"),
    ({"flags": ["noncontiguous_hull"]}, "Gap pages: enter the gap viewer pages"),
    ({"admissible_spans": [{"start_page": 9, "end_page": 17}]}, "Admissible spans: clear this box"),
    ({"presence_state": "ABSENT", "flags": ["stub"]}, "Flags (stub): untick stub"),
])
def test_each_friendly_error_mapping(tmp_path, changes, expected):
    case = make_case(tmp_path, count=1)
    record = copy.deepcopy(case.raw[("SYN-00", "ANNOTATOR_A")])
    record.update(changes)
    errors = core.validate_record(record, case.schema)
    assert any(expected in error for error in errors), errors
    assert all("\n" not in error and len(error) < 260 for error in errors)
    assert not any("source_pdf_sha256':" in error for error in errors)


def test_unmapped_error_uses_field_path_and_short_schema_message(tmp_path):
    case = make_case(tmp_path, count=1)
    record = copy.deepcopy(case.raw[("SYN-00", "ANNOTATOR_A")])
    record["structured_provenance"]["viewer_name"] = ""
    errors = core.validate_record(record, case.schema)
    assert any("structured_provenance/viewer_name:" in error and "non-empty" in error for error in errors)


@pytest.mark.parametrize("filename", [core.SCHEMA_FILENAME, core.PROTOCOL_FILENAME, "ASSIGNMENT.csv"])
def test_missing_bundle_file_names_file_and_gives_start_instruction(tmp_path, filename):
    with pytest.raises(core.AnnotatorError, match=filename) as error:
        core.require_bundle_file(tmp_path / filename)
    assert "start annotator_app.exe from inside your annotation folder" in str(error.value)
    if filename == core.SCHEMA_FILENAME:
        with pytest.raises(core.AnnotatorError):
            core.load_schema(tmp_path)
    if filename == core.PROTOCOL_FILENAME:
        with pytest.raises(core.AnnotatorError):
            core.protocol_version_hash(tmp_path)


@pytest.mark.parametrize("method", ["check", "submit"])
def test_gui_check_and_submit_show_friendly_errors_without_saving(tmp_path, monkeypatch, method):
    pytest.importorskip("tkinter")
    from tools.phase5.annotator import annotator_app as app

    case = make_case(tmp_path, count=1)
    record = copy.deepcopy(case.raw[("SYN-00", "ANNOTATOR_A")])
    record["flags"] = ["annexure"]
    messages = []
    form = app.AnnotatorApp.__new__(app.AnnotatorApp)
    form.schema = case.schema
    form._record = lambda: record
    form._refuse_if_placeholder = lambda: False
    monkeypatch.setattr(app.messagebox, "showerror", lambda title, message: messages.append(message))
    monkeypatch.setattr(app.core, "_assert_title_list_frozen", lambda *_: None)
    monkeypatch.setattr(app, "RECORDS_DIR", tmp_path / "no-save")
    getattr(form, method)()
    assert "Annexure identity: type the printed identity" in messages[0]
    assert "source_pdf_sha256':" not in messages[0]
    assert not (tmp_path / "no-save").exists()


def test_annotator_startup_missing_file_is_friendly_without_creating_records(tmp_path, monkeypatch):
    pytest.importorskip("tkinter")
    from tools.phase5.annotator import annotator_app as app

    class FakeRoot:
        def title(self, *_): pass
        def winfo_screenwidth(self): return 1920
        def winfo_screenheight(self): return 1080
        def geometry(self, *_): pass
        def minsize(self, *_): pass

    monkeypatch.setattr(app, "BUNDLE_ROOT", tmp_path)
    monkeypatch.setattr(app, "RECORDS_DIR", tmp_path / "records")
    with pytest.raises(core.AnnotatorError, match="gold_schema_v0_4.json.*start annotator_app.exe"):
        app.AnnotatorApp(FakeRoot())
    assert not (tmp_path / "records").exists()


@pytest.mark.parametrize("test_name", ["test_fit_geometry_keeps_defaults_on_a_large_screen", "test_fit_geometry_shrinks_to_a_small_screen"])
def test_geometry_tests_skip_when_tkinter_is_missing(monkeypatch, test_name):
    from tests import test_phase5_annotator as geometry_tests

    monkeypatch.setitem(sys.modules, "tkinter", None)
    with pytest.raises(pytest.skip.Exception):
        getattr(geometry_tests, test_name)()
