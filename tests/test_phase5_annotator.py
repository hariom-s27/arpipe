"""Synthetic-only tests for the P5-T offline annotation tool core.

No real PDF is opened and no real record is created: the "PDF" is a few generated
bytes, and all documents are synthetic.
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import stat
import zipfile
from pathlib import Path

import pytest

from tools.phase5.annotator import annotator_core as core
from tools.phase5.annotator import export_role as export_mod
from tools.phase5.annotator import make_bundle

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "docs" / "phase5" / "gold_schema_v0_1.json"
FAKE_PDF = b"%SYNTHETIC-NOT-A-PDF%\n" * 7
FAKE_SHA = hashlib.sha256(FAKE_PDF).hexdigest()
N = 40


@pytest.fixture()
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture()
def bundle(tmp_path: Path) -> Path:
    root = tmp_path / "bundle"
    root.mkdir()
    shutil.copy(SCHEMA_PATH, root / core.SCHEMA_FILENAME)
    (root / core.PROTOCOL_FILENAME).write_text("synthetic protocol\n", encoding="utf-8")
    (root / "records").mkdir()
    return root


def ctx(role: str = "ANNOTATOR_A", doc: str = "SYN-DOC-1") -> dict:
    return {
        "document_id": doc,
        "source_pdf_sha256": FAKE_SHA,
        "physical_page_count": N,
        "annotator_role": role,
        "workspace_id": "ws-" + "0" * 32,
        "protocol_version_hash": "a" * 64,
        "started_at": "2026-09-27T10:00:00+05:30",
        "completed_at": "2026-09-27T10:20:00+05:30",
    }


def present_form(**over) -> dict:
    form = {
        "viewer_page_count": N,
        "viewer_name": "SyntheticViewer",
        "viewer_version": "1.0",
        "presence_state": "PRESENT",
        "presence_reason_code": "BODY_QUALIFYING_TITLE",
        "primary_span_viewer": (10, 14),
        "boundary_evidence_viewer": {"heading_start_page": 10, "last_content_page": 14},
        "aids_used": ["PDF_VIEWER", "THUMBNAILS"],
        "search_queries": ["discussion"],
        "search_usable": True,
        "no_repository_access_attested": True,
        "no_system_output_access_attested": True,
    }
    form.update(over)
    return form


# -- schema pass / fail -------------------------------------------------------

def test_present_record_valid(schema):
    record = core.build_raw_record(present_form(), ctx())
    assert core.validate_record(record, schema) == []
    assert record["primary_span"] == {"start_page": 9, "end_page": 13}
    assert record["boundary_evidence"]["viewer_start_page_1based"] == 10


def test_absent_and_ambiguous_records_valid(schema):
    absent = core.build_raw_record(
        present_form(presence_state="ABSENT", presence_reason_code="NOT_AN_ANNUAL_REPORT",
                     primary_span_viewer=None, boundary_evidence_viewer={}), ctx())
    assert core.validate_record(absent, schema) == []
    amb = core.build_raw_record(
        present_form(presence_state="AMBIGUOUS", presence_reason_code="START_UNRESOLVABLE",
                     ambiguity_code="START_UNRESOLVABLE", primary_span_viewer=None,
                     admissible_spans_viewer=[(10, 14), (11, 14)],
                     boundary_evidence_viewer={}), ctx())
    assert core.validate_record(amb, schema) == []


@pytest.mark.parametrize(
    "over",
    [
        {"primary_span_viewer": None},                                  # PRESENT, no span
        {"presence_reason_code": "TOC_ONLY"},                           # wrong reason
        {"flags": ["annexure"]},                                        # annexure w/o identity
        {"flags": ["noncontiguous_hull"]},                              # flag w/o gaps
        {"gap_pages_viewer": [12]},                                     # gaps w/o flag
        {"no_repository_access_attested": False},                       # attestation const
        {"viewer_name": ""},                                            # empty viewer name
    ],
)
def test_schema_or_invariant_failures(schema, over):
    record = core.build_raw_record(present_form(**over), ctx())
    assert core.validate_record(record, schema), over


def test_tool_invariants(schema):
    good = core.build_raw_record(
        present_form(flags=["noncontiguous_hull"], gap_pages_viewer=[12]), ctx())
    assert core.validate_record(good, schema) == []
    bad_gap = core.build_raw_record(
        present_form(flags=["noncontiguous_hull"], gap_pages_viewer=[10]), ctx())
    assert any("strictly inside" in e for e in core.validate_record(bad_gap, schema))
    reversed_span = core.build_raw_record(present_form(primary_span_viewer=(14, 10)), ctx())
    assert any("start <= end" in e for e in core.validate_record(reversed_span, schema))
    late = core.build_raw_record(present_form(), {**ctx(), "completed_at": "2026-09-27T09:00:00+05:30"})
    assert any("completed_at" in e for e in core.validate_record(late, schema))
    stray = core.build_raw_record(present_form(flag_pages_viewer={"annexure": [11]}), ctx())
    assert any("not in flags" in e for e in core.validate_record(stray, schema))


def test_submit_refused_without_jsonschema(schema, monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "jsonschema":
            raise ImportError("synthetic")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    record = core.build_raw_record(present_form(), ctx())
    with pytest.raises(core.SchemaUnavailable):
        core.validate_record(record, schema)


# -- page conversion -------------------------------------------------------------

def test_one_based_to_zero_based():
    assert core.viewer_to_stored(1, N) == 0
    assert core.viewer_to_stored(N, N) == N - 1


@pytest.mark.parametrize("bad", [0, -1, N + 1, "3", 2.0, True])
def test_out_of_range_or_non_integer_rejected(bad):
    with pytest.raises(core.AnnotatorError):
        core.viewer_to_stored(bad, N)


def test_viewer_page_count_mismatch_rejected():
    with pytest.raises(core.AnnotatorError, match="pages"):
        core.build_raw_record(present_form(viewer_page_count=N + 2), ctx())


def test_parse_page_list():
    assert core.parse_page_list("3, 5-7;9") == [3, 5, 6, 7, 9]
    with pytest.raises(core.AnnotatorError):
        core.parse_page_list("7-5")


# -- sealing, overwrite refusal, supersession -----------------------------------

def test_seal_is_read_only_logged_and_not_overwritable(bundle, schema):
    records = bundle / "records"
    record = core.build_raw_record(present_form(), ctx())
    path, digest = core.seal_raw_record(records, record, schema)
    assert path.name == f"SYN-DOC-1__ANNOTATOR_A__{digest[:8]}.json"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    assert not path.stat().st_mode & stat.S_IWUSR
    assert core.read_hash_log(records) == [(digest, f"ANNOTATOR_A/{path.name}")]
    again = core.build_raw_record(present_form(primary_span_viewer=(10, 15),
                                               boundary_evidence_viewer={}), ctx())
    with pytest.raises(core.AnnotatorError, match="already exists"):
        core.seal_raw_record(records, again, schema)
    # the other role is independent
    core.seal_raw_record(records, core.build_raw_record(present_form(), ctx("ANNOTATOR_B")), schema)


def test_supersede_keeps_original_and_references_old_hash(bundle, schema):
    records = bundle / "records"
    first, old_sha = core.seal_raw_record(records, core.build_raw_record(present_form(), ctx()), schema)
    original_bytes = first.read_bytes()
    replacement = core.build_raw_record(
        present_form(primary_span_viewer=(10, 15), boundary_evidence_viewer={}), ctx())
    with pytest.raises(core.AnnotatorError, match="reason"):
        core.supersede(records, old_sha, replacement, "  ", schema, "ws-" + "0" * 32)
    new_path, new_sha, note_path, note_sha = core.supersede(
        records, old_sha, replacement, "end page misread", schema, "ws-" + "0" * 32)
    assert first.read_bytes() == original_bytes
    note = json.loads(note_path.read_text(encoding="utf-8"))
    assert note["superseded_raw_sha256"] == old_sha
    assert note["superseding_raw_sha256"] == new_sha
    assert [d for d, _ in core.read_hash_log(records)] == [old_sha, new_sha, note_sha]
    with pytest.raises(core.AnnotatorError, match="already been superseded"):
        core.supersede(records, old_sha,
                       core.build_raw_record(present_form(primary_span_viewer=(10, 16),
                                                          boundary_evidence_viewer={}), ctx()),
                       "again", schema, "ws-" + "0" * 32)


def test_export_locks_role_and_manifest_matches(bundle, schema, tmp_path):
    records = bundle / "records"
    core.load_or_create_workspace_id(records)
    _, digest = core.seal_raw_record(records, core.build_raw_record(present_form(), ctx()), schema)
    out = tmp_path / "A.zip"
    manifest = export_mod.export_role(records, "ANNOTATOR_A", out)
    names = [m[0] for m in manifest]
    assert core.HASH_LOG_NAME in names and core.WORKSPACE_ID_NAME in names
    assert digest in [m[2] for m in manifest]
    with zipfile.ZipFile(out) as zf:
        assert sorted(zf.namelist()) == sorted(names)
    with pytest.raises(core.AnnotatorError, match="exported"):
        core.seal_raw_record(
            records, core.build_raw_record(present_form(), ctx(doc="SYN-DOC-2")), schema)


def test_export_detects_tampering(bundle, schema, tmp_path):
    records = bundle / "records"
    path, _ = core.seal_raw_record(records, core.build_raw_record(present_form(), ctx()), schema)
    path.chmod(0o644)
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(core.AnnotatorError, match="HASH_LOG"):
        export_mod.export_role(records, "ANNOTATOR_A", tmp_path / "A.zip")


# -- isolation, assignment, PDF hash ------------------------------------------

def test_repo_detection_refusal(tmp_path):
    clean = tmp_path / "ws"
    clean.mkdir()
    assert core.workspace_refusals(clean, clean) == []
    (tmp_path / ".git").mkdir()
    assert any(".git" in r for r in core.workspace_refusals(clean, clean))


@pytest.mark.parametrize("make", ["arpipe", "reports", "docs/identity", "labels_fit.csv"])
def test_forbidden_content_refusal(tmp_path, make):
    root = tmp_path / "ws"
    target = root / make
    if make.endswith(".csv"):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("x", encoding="utf-8")
    else:
        target.mkdir(parents=True)
    assert core.workspace_refusals(root)
    with pytest.raises(core.AnnotatorError):
        core.assert_workspace_isolated(root)


def test_workspace_id_is_random_and_stable(tmp_path):
    a = core.load_or_create_workspace_id(tmp_path / "r1")
    b = core.load_or_create_workspace_id(tmp_path / "r2")
    assert a != b and a.startswith("ws-") and len(a) == 35
    assert core.load_or_create_workspace_id(tmp_path / "r1") == a


def write_assignment(path: Path, rows: list[list]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(core.ASSIGNMENT_COLUMNS)
        writer.writerows(rows)


def test_assignment_and_pdf_hash(tmp_path):
    fake = tmp_path / "doc.pdf"
    fake.write_bytes(FAKE_PDF)
    write_assignment(tmp_path / "a.csv", [["SYN-DOC-1", FAKE_SHA, N]])
    rows = core.load_assignment(tmp_path / "a.csv")
    assert core.verify_pdf(fake, rows["SYN-DOC-1"]["source_pdf_sha256"]) == FAKE_SHA
    fake.write_bytes(FAKE_PDF + b"x")
    with pytest.raises(core.AnnotatorError, match="mismatch"):
        core.verify_pdf(fake, FAKE_SHA)
    write_assignment(tmp_path / "b.csv", [["SYN-DOC-1", FAKE_SHA, N], ["SYN-DOC-1", FAKE_SHA, N]])
    with pytest.raises(core.AnnotatorError, match="duplicate"):
        core.load_assignment(tmp_path / "b.csv")


# -- canonical JSON and bundle -------------------------------------------------

def test_canonical_json_hash_stable():
    a = {"b": [1, 2], "a": {"y": "é", "x": None}}
    b = {"a": {"x": None, "y": "é"}, "b": [1, 2]}
    assert core.canonical_json_bytes(a) == core.canonical_json_bytes(b)
    data = core.canonical_json_bytes(a)
    assert b"\r" not in data and data.endswith(b"\n")
    assert all(not line.endswith(b" ") for line in data.split(b"\n"))
    assert hashlib.sha256(data).hexdigest() == hashlib.sha256(core.canonical_json_bytes(b)).hexdigest()


def test_schema_enums_come_from_schema(schema):
    enums = core.schema_enums(schema)
    assert "PRESENT" in enums["presence_state"]
    assert "HINDI_COPY" in enums["alternative_span_type"]


def test_bundle_contains_exactly_allowed_files(tmp_path):
    out = tmp_path / "annotator_bundle.zip"
    manifest = make_bundle.build_bundle(out)
    with zipfile.ZipFile(out) as zf:
        names = sorted(zf.namelist())
    assert names == make_bundle.expected_entries()
    assert sorted(m[0] for m in manifest) == names
    assert not any("arpipe/" in n.split("annotator_bundle/", 1)[1] for n in names)
    # deterministic
    out2 = tmp_path / "again.zip"
    make_bundle.build_bundle(out2)
    assert out.read_bytes() == out2.read_bytes()
