"""Synthetic-only tests for the P5-T offline annotation tool core.

No real PDF is opened and no real record is created: the "PDF" is a few generated
bytes, and all documents are synthetic.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import re
import shutil
import stat
import zipfile
from pathlib import Path

import pytest

from tools.phase5.annotator import annotator_core as core
from tools.phase5.annotator import export_role as export_mod
from tools.phase5.annotator import make_bundle

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "docs" / "phase5" / "gold_schema_v0_4.json"
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
    (root / core.TITLE_LIST_PLACEHOLDER).write_text(
        "synthetic title-list placeholder\n", encoding="utf-8"
    )
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
    if form["presence_state"] == "PRESENT":
        # v0.3: both shared-page answers are required on PRESENT; ABSENT/AMBIGUOUS leave them null
        form.setdefault("start_page_shared", False)
        form.setdefault("end_page_shared", False)
        # v0.4: a page marked shared needs anchor text; default one so existing PRESENT
        # cases that set start/end_page_shared=True don't each have to supply it.
        if form["start_page_shared"] is True:
            form.setdefault("start_anchor_text", "Management's Discussion and Analysis")
        if form["end_page_shared"] is True:
            form.setdefault("end_anchor_text", "Corporate Governance Report")
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


def test_absent_no_english_mda_keeps_hindi_copy_span(schema):
    record = core.build_raw_record(
        present_form(
            presence_state="ABSENT",
            presence_reason_code="NO_ENGLISH_MDA",
            primary_span_viewer=None,
            alternative_spans_viewer=[(10, 14, "HINDI_COPY")],
            boundary_evidence_viewer={},
        ),
        ctx(),
    )
    assert record["alternative_spans"] == [
        {"start_page": 9, "end_page": 13, "type": "HINDI_COPY"}
    ]
    assert core.validate_record(record, schema) == []


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


def test_csr_esg_viewer_pages_are_stored_zero_based(schema):
    record = core.build_raw_record(
        present_form(
            flags=["contains_csr_esg"],
            csr_esg_pages_viewer=[10, 12, 14],
        ),
        ctx(),
    )
    assert record["csr_esg_pages"] == [9, 11, 13]
    assert core.validate_record(record, schema) == []


def test_csr_esg_page_outside_primary_span_is_refused(schema):
    record = core.build_raw_record(
        present_form(flags=["contains_csr_esg"], csr_esg_pages_viewer=[15]),
        ctx(),
    )
    assert any("outside primary_span" in error for error in core.validate_record(record, schema))


def test_csr_esg_page_cannot_also_be_a_gap(schema):
    record = core.build_raw_record(
        present_form(
            flags=["contains_csr_esg", "noncontiguous_hull"],
            csr_esg_pages_viewer=[12],
            gap_pages_viewer=[12],
        ),
        ctx(),
    )
    assert any("also gap_pages" in error for error in core.validate_record(record, schema))


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

def test_title_list_placeholder_blocks_seal_and_supersede_unless_explicitly_allowed(
    bundle, schema
):
    records = bundle / "records"
    record = core.build_raw_record(present_form(), ctx())
    with pytest.raises(core.AnnotatorError, match="title list is not frozen"):
        core.seal_raw_record(records, record, schema)

    _, old_sha = core.seal_raw_record(
        records, record, schema, allow_unfrozen_title_list=True
    )
    replacement = core.build_raw_record(
        present_form(primary_span_viewer=(10, 15), boundary_evidence_viewer={}),
        ctx(),
    )
    with pytest.raises(core.AnnotatorError, match="title list is not frozen"):
        core.supersede(
            records,
            old_sha,
            replacement,
            "synthetic correction",
            schema,
            "ws-" + "0" * 32,
        )


# -- title-list seal guard (schema/protocol v0.4) --------------------------------

def test_seal_guard_refuses_when_title_list_is_missing(bundle, schema):
    records = bundle / "records"
    (bundle / core.TITLE_LIST_PLACEHOLDER).unlink()
    record = core.build_raw_record(present_form(), ctx())
    with pytest.raises(core.AnnotatorError, match=re.escape(core.TITLE_LIST_FILENAME)):
        core.seal_raw_record(records, record, schema)


def test_seal_guard_refuses_when_manifest_is_missing(bundle, schema):
    records = bundle / "records"
    (bundle / core.TITLE_LIST_PLACEHOLDER).unlink()
    (bundle / core.TITLE_LIST_FILENAME).write_text(
        "Management's Discussion and Analysis\n", encoding="utf-8"
    )
    record = core.build_raw_record(present_form(), ctx())
    with pytest.raises(core.AnnotatorError, match=re.escape(core.BUNDLE_MANIFEST_FILENAME)):
        core.seal_raw_record(records, record, schema)


def test_seal_guard_refuses_when_title_list_was_edited_after_bundling(bundle, schema):
    records = bundle / "records"
    (bundle / core.TITLE_LIST_PLACEHOLDER).unlink()
    title_list = bundle / core.TITLE_LIST_FILENAME
    title_list.write_text("Management's Discussion and Analysis\n", encoding="utf-8")
    (bundle / core.BUNDLE_MANIFEST_FILENAME).write_text(
        json.dumps({"bundle_format": 1, "title_list_sha256": core.sha256_file(title_list), "files": {}}),
        encoding="utf-8",
    )
    title_list.write_text("Management's Discussion and Analysis - EDITED\n", encoding="utf-8")
    record = core.build_raw_record(present_form(), ctx())
    with pytest.raises(core.AnnotatorError, match="does not match"):
        core.seal_raw_record(records, record, schema)


def test_seal_guard_allows_sealing_with_a_correct_list_and_manifest(bundle, schema):
    records = bundle / "records"
    (bundle / core.TITLE_LIST_PLACEHOLDER).unlink()
    title_list = bundle / core.TITLE_LIST_FILENAME
    title_list.write_text("Management's Discussion and Analysis\n", encoding="utf-8")
    (bundle / core.BUNDLE_MANIFEST_FILENAME).write_text(
        json.dumps({"bundle_format": 1, "title_list_sha256": core.sha256_file(title_list), "files": {}}),
        encoding="utf-8",
    )
    record = core.build_raw_record(present_form(), ctx())
    path, digest = core.seal_raw_record(records, record, schema)
    assert path.is_file()
    assert core.sha256_file(path) == digest


def test_seal_guard_override_still_bypasses_every_check(bundle, schema):
    records = bundle / "records"
    # Only the placeholder exists (no title list, no manifest); the override still seals.
    record = core.build_raw_record(present_form(), ctx())
    path, _ = core.seal_raw_record(records, record, schema, allow_unfrozen_title_list=True)
    assert path.is_file()


def test_seal_is_read_only_logged_and_not_overwritable(bundle, schema):
    records = bundle / "records"
    record = core.build_raw_record(present_form(), ctx())
    path, digest = core.seal_raw_record(
        records, record, schema, allow_unfrozen_title_list=True
    )
    assert path.name == f"SYN-DOC-1__ANNOTATOR_A__{digest[:8]}.json"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    assert not path.stat().st_mode & stat.S_IWUSR
    assert core.read_hash_log(records) == [(digest, f"ANNOTATOR_A/{path.name}")]
    again = core.build_raw_record(present_form(primary_span_viewer=(10, 15),
                                               boundary_evidence_viewer={}), ctx())
    with pytest.raises(core.AnnotatorError, match="already exists"):
        core.seal_raw_record(records, again, schema, allow_unfrozen_title_list=True)
    # the other role is independent
    core.seal_raw_record(
        records,
        core.build_raw_record(present_form(), ctx("ANNOTATOR_B")),
        schema,
        allow_unfrozen_title_list=True,
    )


def test_supersede_keeps_original_and_references_old_hash(bundle, schema):
    records = bundle / "records"
    first, old_sha = core.seal_raw_record(
        records,
        core.build_raw_record(present_form(), ctx()),
        schema,
        allow_unfrozen_title_list=True,
    )
    original_bytes = first.read_bytes()
    replacement = core.build_raw_record(
        present_form(primary_span_viewer=(10, 15), boundary_evidence_viewer={}), ctx())
    with pytest.raises(core.AnnotatorError, match="reason"):
        core.supersede(
            records,
            old_sha,
            replacement,
            "  ",
            schema,
            "ws-" + "0" * 32,
            allow_unfrozen_title_list=True,
        )
    new_path, new_sha, note_path, note_sha = core.supersede(
        records,
        old_sha,
        replacement,
        "end page misread",
        schema,
        "ws-" + "0" * 32,
        allow_unfrozen_title_list=True,
    )
    assert first.read_bytes() == original_bytes
    note = json.loads(note_path.read_text(encoding="utf-8"))
    assert note["superseded_raw_sha256"] == old_sha
    assert note["superseding_raw_sha256"] == new_sha
    assert [d for d, _ in core.read_hash_log(records)] == [old_sha, new_sha, note_sha]
    with pytest.raises(core.AnnotatorError, match="already been superseded"):
        core.supersede(records, old_sha,
                       core.build_raw_record(present_form(primary_span_viewer=(10, 16),
                                                          boundary_evidence_viewer={}), ctx()),
                       "again", schema, "ws-" + "0" * 32,
                       allow_unfrozen_title_list=True)


def test_export_locks_role_and_manifest_matches(bundle, schema, tmp_path):
    records = bundle / "records"
    core.load_or_create_workspace_id(records)
    _, digest = core.seal_raw_record(
        records,
        core.build_raw_record(present_form(), ctx()),
        schema,
        allow_unfrozen_title_list=True,
    )
    out = tmp_path / "A.zip"
    manifest = export_mod.export_role(records, "ANNOTATOR_A", out)
    names = [m[0] for m in manifest]
    assert core.HASH_LOG_NAME in names and core.WORKSPACE_ID_NAME in names
    assert digest in [m[2] for m in manifest]
    with zipfile.ZipFile(out) as zf:
        assert sorted(zf.namelist()) == sorted(names)
    with pytest.raises(core.AnnotatorError, match="exported"):
        core.seal_raw_record(
            records,
            core.build_raw_record(present_form(), ctx(doc="SYN-DOC-2")),
            schema,
            allow_unfrozen_title_list=True,
        )


def test_export_detects_tampering(bundle, schema, tmp_path):
    records = bundle / "records"
    path, _ = core.seal_raw_record(
        records,
        core.build_raw_record(present_form(), ctx()),
        schema,
        allow_unfrozen_title_list=True,
    )
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
    assert "annotator_bundle/gold_schema_v0_4.json" in names
    assert "annotator_bundle/gold_schema_v0_3.json" not in names
    assert "annotator_bundle/gold_schema_v0_2.json" not in names
    assert "annotator_bundle/gold_schema_v0_1.json" not in names
    assert "annotator_bundle/GOLD_PROTOCOL_v0_4.md" in names
    assert "annotator_bundle/GOLD_PROTOCOL_v0_3.md" not in names
    assert "annotator_bundle/GOLD_PROTOCOL_v0_2.md" not in names
    assert "annotator_bundle/GOLD_PROTOCOL_v0_1.md" not in names
    assert "annotator_bundle/BUNDLE_MANIFEST.json" in names
    assert not any("arpipe/" in n.split("annotator_bundle/", 1)[1] for n in names)
    # deterministic
    out2 = tmp_path / "again.zip"
    make_bundle.build_bundle(out2)
    assert out.read_bytes() == out2.read_bytes()


def test_bundle_manifest_records_null_title_hash_without_a_title_list(tmp_path):
    out = tmp_path / "annotator_bundle.zip"
    make_bundle.build_bundle(out)
    with zipfile.ZipFile(out) as zf:
        manifest = json.loads(zf.read(f"annotator_bundle/{make_bundle.MANIFEST_NAME}"))
    assert manifest == {
        "bundle_format": 1,
        "title_list_sha256": None,
        "files": manifest["files"],
    }
    assert make_bundle.PLACEHOLDER_NAME in manifest["files"]
    assert make_bundle.TITLE_LIST_NAME not in manifest["files"]


def test_bundle_with_title_list_ships_it_sealed_and_drops_the_placeholder(tmp_path):
    title_list = tmp_path / "TITLE_EQUIVALENCE_v0.md"
    title_list.write_text("Management's Discussion and Analysis: EQUIVALENT\n", encoding="utf-8")
    digest = hashlib.sha256(title_list.read_bytes()).hexdigest()
    out = tmp_path / "annotator_bundle.zip"
    make_bundle.build_bundle(out, title_list=title_list, title_list_sha256=digest)
    with zipfile.ZipFile(out) as zf:
        names = sorted(zf.namelist())
        manifest = json.loads(zf.read(f"annotator_bundle/{make_bundle.MANIFEST_NAME}"))
        assert zf.read(f"annotator_bundle/{make_bundle.TITLE_LIST_NAME}") == title_list.read_bytes()
    assert names == make_bundle.expected_entries(with_title_list=True)
    assert f"annotator_bundle/{make_bundle.PLACEHOLDER_NAME}" not in names
    assert manifest["title_list_sha256"] == digest
    assert manifest["files"][make_bundle.TITLE_LIST_NAME] == digest
    # deterministic
    out2 = tmp_path / "again.zip"
    make_bundle.build_bundle(out2, title_list=title_list, title_list_sha256=digest)
    assert out.read_bytes() == out2.read_bytes()


def test_bundle_refuses_a_wrong_title_list_sha256(tmp_path):
    title_list = tmp_path / "TITLE_EQUIVALENCE_v0.md"
    title_list.write_text("Management's Discussion and Analysis: EQUIVALENT\n", encoding="utf-8")
    out = tmp_path / "annotator_bundle.zip"
    with pytest.raises(ValueError, match="does not match"):
        make_bundle.build_bundle(out, title_list=title_list, title_list_sha256="0" * 64)
    assert not out.exists()


def test_bundle_title_list_arguments_are_both_or_neither(tmp_path):
    title_list = tmp_path / "TITLE_EQUIVALENCE_v0.md"
    title_list.write_text("x\n", encoding="utf-8")
    out = tmp_path / "annotator_bundle.zip"
    with pytest.raises(ValueError, match="given together"):
        make_bundle.build_bundle(out, title_list=title_list)
    assert not out.exists()


def test_bundle_ships_the_v0_4_files_under_the_names_the_core_loads(tmp_path):
    out = tmp_path / "annotator_bundle.zip"
    make_bundle.build_bundle(out)
    with zipfile.ZipFile(out) as zf:
        names = {n.split("/", 1)[1] for n in zf.namelist() if n.split("/", 1)[1]}
        assert {core.SCHEMA_FILENAME, core.PROTOCOL_FILENAME} <= names
        assert zf.read(f"annotator_bundle/{core.SCHEMA_FILENAME}") == SCHEMA_PATH.read_bytes()
        protocol = REPO_ROOT / "docs" / "phase5" / "GOLD_PROTOCOL_v0_4.md"
        assert zf.read(f"annotator_bundle/{core.PROTOCOL_FILENAME}") == protocol.read_bytes()


# -- shared start/end pages (schema v0.4, decisions 8.7, F6 anchor text) -----------

def test_core_targets_schema_and_protocol_v0_4(schema):
    assert core.SCHEMA_FILENAME == "gold_schema_v0_4.json"
    assert core.PROTOCOL_FILENAME == "GOLD_PROTOCOL_v0_4.md"
    record = core.build_raw_record(present_form(), ctx())
    assert record["schema_version"] == "0.4"
    assert core.validate_record(record, schema) == []


@pytest.mark.parametrize(("key", "question"), core.SHARED_PAGE_QUESTIONS)
@pytest.mark.parametrize("answer", [None, "Yes", "No", 1, 0])
def test_present_form_without_a_yes_no_answer_is_refused(key, question, answer):
    with pytest.raises(core.AnnotatorError, match=re.escape(question)):
        core.build_raw_record(present_form(**{key: answer}), ctx())


@pytest.mark.parametrize(("key", "question"), core.SHARED_PAGE_QUESTIONS)
def test_present_form_missing_an_answer_key_is_refused(key, question):
    form = present_form()
    del form[key]
    with pytest.raises(core.AnnotatorError, match=re.escape(question)):
        core.build_raw_record(form, ctx())


def test_end_page_shared_sets_mixed_end_page_field_and_flag(schema):
    record = core.build_raw_record(present_form(end_page_shared=True), ctx())
    evidence = record["boundary_evidence"]
    assert evidence["end_page_shared"] is True and evidence["start_page_shared"] is False
    assert evidence["mixed_end_page"] == record["primary_span"]["end_page"] == 13
    assert "mixed_end_page" in record["flags"]
    assert "mixed_start_page" not in record["flags"]
    assert core.validate_record(record, schema) == []


def test_end_page_not_shared_leaves_mixed_end_page_null_and_no_flag(schema):
    record = core.build_raw_record(present_form(end_page_shared=False), ctx())
    assert record["boundary_evidence"]["end_page_shared"] is False
    assert record["boundary_evidence"]["mixed_end_page"] is None
    assert "mixed_end_page" not in record["flags"]
    assert core.validate_record(record, schema) == []


def test_start_page_shared_sets_mixed_start_page_flag(schema):
    record = core.build_raw_record(present_form(start_page_shared=True), ctx())
    assert record["boundary_evidence"]["start_page_shared"] is True
    assert "mixed_start_page" in record["flags"]
    assert "mixed_end_page" not in record["flags"]
    assert record["boundary_evidence"]["mixed_end_page"] is None
    assert core.validate_record(record, schema) == []


def test_both_pages_shared_sets_both_flags(schema):
    record = core.build_raw_record(
        present_form(start_page_shared=True, end_page_shared=True), ctx())
    assert {"mixed_start_page", "mixed_end_page"} <= set(record["flags"])
    assert record["boundary_evidence"]["mixed_end_page"] == 13
    assert core.validate_record(record, schema) == []


def test_flags_and_mixed_end_page_come_only_from_the_answers(schema):
    # Values a form supplies for the derived fields cannot make them disagree with the answers.
    record = core.build_raw_record(
        present_form(
            flags=["mixed_start_page", "mixed_end_page", "stub"],
            boundary_evidence_viewer={"heading_start_page": 10, "mixed_end_page": 12},
        ),
        ctx(),
    )
    assert record["flags"] == ["stub"]
    assert record["boundary_evidence"]["mixed_end_page"] is None
    assert core.validate_record(record, schema) == []


def test_absent_and_ambiguous_records_carry_null_shared_answers(schema):
    absent = core.build_raw_record(
        present_form(presence_state="ABSENT", presence_reason_code="NOT_AN_ANNUAL_REPORT",
                     primary_span_viewer=None, boundary_evidence_viewer={}), ctx())
    ambiguous = core.build_raw_record(
        present_form(presence_state="AMBIGUOUS", presence_reason_code="START_UNRESOLVABLE",
                     ambiguity_code="START_UNRESOLVABLE", primary_span_viewer=None,
                     admissible_spans_viewer=[(10, 14), (11, 14)],
                     boundary_evidence_viewer={}), ctx())
    for record in (absent, ambiguous):
        evidence = record["boundary_evidence"]
        assert evidence["start_page_shared"] is None and evidence["end_page_shared"] is None
        assert evidence["mixed_end_page"] is None
        assert evidence["start_anchor_text"] is None and evidence["end_anchor_text"] is None
        assert not set(core.DERIVED_FLAGS) & set(record["flags"])
        assert core.validate_record(record, schema) == []


@pytest.mark.parametrize("key", [key for key, _ in core.SHARED_PAGE_QUESTIONS])
@pytest.mark.parametrize("answer", [True, False])
def test_absent_record_with_a_shared_answer_is_refused(schema, key, answer):
    record = core.build_raw_record(
        present_form(presence_state="ABSENT", presence_reason_code="NOT_AN_ANNUAL_REPORT",
                     primary_span_viewer=None, boundary_evidence_viewer={}, **{key: answer}),
        ctx())
    assert core.validate_record(record, schema)


def test_tool_invariants_check_mixed_end_page_against_the_answer():
    shared = core.build_raw_record(present_form(end_page_shared=True), ctx())
    assert core.tool_invariant_errors(shared) == []
    for wrong in (12, None):
        moved = copy.deepcopy(shared)
        moved["boundary_evidence"]["mixed_end_page"] = wrong
        assert any("must equal the primary end page" in e
                   for e in core.tool_invariant_errors(moved)), wrong
    unshared = core.build_raw_record(present_form(end_page_shared=False), ctx())
    assert core.tool_invariant_errors(unshared) == []
    unshared["boundary_evidence"]["mixed_end_page"] = 13
    assert any("must be null" in e for e in core.tool_invariant_errors(unshared))


@pytest.mark.parametrize(
    ("answer_key", "flag"),
    [("start_page_shared", "mixed_start_page"), ("end_page_shared", "mixed_end_page")],
)
def test_tool_invariants_couple_each_flag_to_its_answer(schema, answer_key, flag):
    shared = core.build_raw_record(present_form(**{answer_key: True}), ctx())
    assert core.validate_record(shared, schema) == []
    shared["flags"].remove(flag)
    assert any(flag in e for e in core.tool_invariant_errors(shared))
    assert core.validate_record(shared, schema)
    unshared = core.build_raw_record(present_form(**{answer_key: False}), ctx())
    assert core.validate_record(unshared, schema) == []
    unshared["flags"].append(flag)
    assert any(flag in e for e in core.tool_invariant_errors(unshared))
    assert core.validate_record(unshared, schema)


def test_derived_flags_are_schema_flags_the_core_sets_itself(schema):
    assert set(core.DERIVED_FLAGS) == {"mixed_start_page", "mixed_end_page"}
    assert set(core.DERIVED_FLAGS) <= set(core.schema_enums(schema)["flags"])


# -- anchor text on shared start/end pages (schema/protocol v0.4) ------------------

def test_anchor_text_is_stored_stripped_when_the_page_is_shared(schema):
    record = core.build_raw_record(
        present_form(start_page_shared=True,
                     start_anchor_text="  Management's Discussion and Analysis  "),
        ctx(),
    )
    assert record["boundary_evidence"]["start_anchor_text"] == "Management's Discussion and Analysis"
    assert core.validate_record(record, schema) == []


@pytest.mark.parametrize("blank", ["", "   ", None])
def test_empty_anchor_text_on_a_shared_page_is_refused(blank):
    with pytest.raises(core.AnnotatorError, match="anchor text"):
        core.build_raw_record(
            present_form(end_page_shared=True, end_anchor_text=blank), ctx()
        )


def test_anchor_text_is_ignored_when_the_page_is_not_shared(schema):
    record = core.build_raw_record(
        present_form(end_page_shared=False, end_anchor_text="stray text nobody asked for"),
        ctx(),
    )
    assert record["boundary_evidence"]["end_anchor_text"] is None
    assert core.validate_record(record, schema) == []


def test_absent_forces_mixed_end_page_and_anchors_null_even_if_the_form_sends_values(schema):
    record = core.build_raw_record(
        present_form(presence_state="ABSENT", presence_reason_code="NOT_AN_ANNUAL_REPORT",
                     primary_span_viewer=None, boundary_evidence_viewer={},
                     end_page_shared=True, end_anchor_text="stray anchor text"),
        ctx(),
    )
    evidence = record["boundary_evidence"]
    assert evidence["mixed_end_page"] is None
    assert evidence["end_anchor_text"] is None
    # still schema-invalid overall (ABSENT requires a null end_page_shared answer, §8.7)
    assert core.validate_record(record, schema)


def test_form_has_no_default_answer_and_present_is_refused_until_both_are_chosen(schema):
    tk = pytest.importorskip("tkinter")
    from tools.phase5.annotator import annotator_app as app

    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("no display available for tkinter")
    root.withdraw()
    try:
        doc = {"document_id": "SYN-DOC-1", "source_pdf_sha256": FAKE_SHA, "physical_page_count": N}
        form = app.AnnotatorApp.__new__(app.AnnotatorApp)  # only the form: no dialogs, no workspace
        form.root, form.role, form.workspace_id = root, "ANNOTATOR_A", "ws-" + "0" * 32
        form.role_from_file = False
        form.assignment, form.enums, form.schema = {"SYN-DOC-1": doc}, core.schema_enums(schema), schema
        form.protocol_hash, form.started_at, form.doc = "a" * 64, "2026-09-27T10:00:00+05:30", doc
        form._build()
        for var, value in (
            (form.doc_var, "SYN-DOC-1"), (form.viewer_name, "SyntheticViewer"),
            (form.viewer_version, "1.0"), (form.viewer_count, str(N)),
            (form.presence, "PRESENT"), (form.reason, "BODY_QUALIFYING_TITLE"),
            (form.p_start, "10"), (form.p_end, "14"),
            (form.att_repo, True), (form.att_output, True),
        ):
            var.set(value)

        # derived flags and the old free-text entry are gone from the form
        assert not set(core.DERIVED_FLAGS) & set(form.flag_vars)
        assert "mixed_end_page" not in form.boundary_vars
        # no default: nothing is selected, so PRESENT is refused
        assert [v.get() for v in form.shared_vars.values()] == ["", ""]
        assert form._form()["start_page_shared"] is None
        with pytest.raises(core.AnnotatorError, match="Answer Yes or No"):
            form._record()
        form.shared_vars["start_page_shared"].set("Yes")
        with pytest.raises(core.AnnotatorError, match="End page shared"):
            form._record()
        form.shared_vars["end_page_shared"].set("No")
        # anchor text is also new in v0.4: required once the matching answer is Yes
        assert form.anchor_vars["start_anchor_text"].get() == ""
        with pytest.raises(core.AnnotatorError, match="anchor text"):
            form._record()
        form.anchor_vars["start_anchor_text"].set("Management's Discussion and Analysis")
        record = form._record()
        assert core.validate_record(record, schema) == []
        assert record["boundary_evidence"]["start_page_shared"] is True
        assert record["boundary_evidence"]["end_page_shared"] is False
        assert record["boundary_evidence"]["start_anchor_text"] == "Management's Discussion and Analysis"
        assert record["boundary_evidence"]["end_anchor_text"] is None
        assert "mixed_start_page" in record["flags"] and "mixed_end_page" not in record["flags"]
        # answers only apply to PRESENT: an ABSENT record gets nulls whatever is selected
        form.presence.set("ABSENT")
        form.reason.set("NOT_AN_ANNUAL_REPORT")
        form.p_start.set("")
        form.p_end.set("")
        absent = form._record()
        assert absent["boundary_evidence"]["start_page_shared"] is None
        assert absent["boundary_evidence"]["end_page_shared"] is None
        assert absent["boundary_evidence"]["start_anchor_text"] is None
        assert absent["boundary_evidence"]["end_anchor_text"] is None
        assert core.validate_record(absent, schema) == []
    finally:
        root.destroy()



# -- role per folder (F7) ----------------------------------------------------------

def test_read_role_file_absent_returns_none(tmp_path):
    assert core.read_role_file(tmp_path) is None


@pytest.mark.parametrize("role", core.RAW_ROLES)
def test_read_role_file_valid_returns_role(tmp_path, role):
    (tmp_path / core.ROLE_FILENAME).write_text(role + "\n", encoding="utf-8")
    assert core.read_role_file(tmp_path) == role


@pytest.mark.parametrize(
    "content", ["", "ANNOTATOR_C\n", "ANNOTATOR_A\nANNOTATOR_B\n", "  \n\n", "annotator_a\n"]
)
def test_read_role_file_invalid_is_refused(tmp_path, content):
    (tmp_path / core.ROLE_FILENAME).write_text(content, encoding="utf-8")
    with pytest.raises(core.AnnotatorError, match=re.escape(core.ROLE_FILENAME)):
        core.read_role_file(tmp_path)


def test_ask_role_uses_role_file_without_prompting(tmp_path, monkeypatch):
    pytest.importorskip("tkinter")
    from tools.phase5.annotator import annotator_app as app

    monkeypatch.setattr(app, "BUNDLE_ROOT", tmp_path)
    (tmp_path / core.ROLE_FILENAME).write_text("ANNOTATOR_B\n", encoding="utf-8")

    def _fail_prompt(*_a, **_kw):
        raise AssertionError("must not prompt when ROLE.txt is present")

    monkeypatch.setattr(app.simpledialog, "askstring", _fail_prompt)
    form = app.AnnotatorApp.__new__(app.AnnotatorApp)
    form.root = None
    assert form._ask_role() == ("ANNOTATOR_B", True)


def test_ask_role_falls_through_to_prompt_when_no_role_file(tmp_path, monkeypatch):
    pytest.importorskip("tkinter")
    from tools.phase5.annotator import annotator_app as app

    monkeypatch.setattr(app, "BUNDLE_ROOT", tmp_path)
    monkeypatch.setattr(app.simpledialog, "askstring", lambda *_a, **_kw: "ANNOTATOR_A")
    form = app.AnnotatorApp.__new__(app.AnnotatorApp)
    form.root = None
    assert form._ask_role() == ("ANNOTATOR_A", False)


def test_ask_role_rejects_an_invalid_prompt_answer(tmp_path, monkeypatch):
    pytest.importorskip("tkinter")
    from tools.phase5.annotator import annotator_app as app

    monkeypatch.setattr(app, "BUNDLE_ROOT", tmp_path)
    monkeypatch.setattr(app.simpledialog, "askstring", lambda *_a, **_kw: "nope")
    form = app.AnnotatorApp.__new__(app.AnnotatorApp)
    form.root = None
    with pytest.raises(core.AnnotatorError, match="ANNOTATOR_A or ANNOTATOR_B"):
        form._ask_role()


# -- window geometry and layout (F7) -----------------------------------------------

def test_fit_geometry_keeps_defaults_on_a_large_screen():
    pytest.importorskip("tkinter")
    from tools.phase5.annotator import annotator_app as app

    assert app._fit_geometry(1920, 1080) == ((1100, 800), (900, 600))


def test_fit_geometry_shrinks_to_a_small_screen():
    pytest.importorskip("tkinter")
    from tools.phase5.annotator import annotator_app as app

    assert app._fit_geometry(800, 500) == ((800, 500), (800, 500))


def test_layout_wraps_labels_and_has_dual_scrollbars(schema):
    tk = pytest.importorskip("tkinter")
    from tkinter import ttk
    from tools.phase5.annotator import annotator_app as app

    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("no display available for tkinter")
    root.withdraw()
    try:
        doc = {"document_id": "SYN-DOC-1", "source_pdf_sha256": FAKE_SHA, "physical_page_count": N}
        form = app.AnnotatorApp.__new__(app.AnnotatorApp)
        form.root, form.role, form.role_from_file = root, "ANNOTATOR_A", False
        form.workspace_id = "ws-" + "0" * 32
        form.assignment, form.enums, form.schema = {"SYN-DOC-1": doc}, core.schema_enums(schema), schema
        form.protocol_hash, form.started_at, form.doc = "a" * 64, "2026-09-27T10:00:00+05:30", doc
        form._build()
        assert isinstance(form.canvas, tk.Canvas)
        assert form.canvas.cget("xscrollcommand") and form.canvas.cget("yscrollcommand")
        assert str(form.hbar.cget("orient")) == "horizontal"
        assert str(form.vbar.cget("orient")) == "vertical"
        labels = [w for w in form.form.winfo_children() if isinstance(w, ttk.Label)]
        assert labels, "expected at least one prompt label"
        assert all(int(str(w.cget("wraplength"))) == app.LABEL_WRAP_PX for w in labels)
        assert form.form.winfo_parent() == str(form.canvas)  # the form frame is inside the canvas
        assert form.form.grid_columnconfigure(1)["weight"] == 1
    finally:
        root.destroy()


def test_role_label_shows_set_by_this_folder_only_when_from_a_role_file(schema):
    tk = pytest.importorskip("tkinter")
    from tkinter import ttk
    from tools.phase5.annotator import annotator_app as app

    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("no display available for tkinter")
    root.withdraw()
    try:
        doc = {"document_id": "SYN-DOC-1", "source_pdf_sha256": FAKE_SHA, "physical_page_count": N}
        form = app.AnnotatorApp.__new__(app.AnnotatorApp)
        form.root, form.role, form.role_from_file = root, "ANNOTATOR_B", True
        form.workspace_id = "ws-" + "0" * 32
        form.assignment, form.enums, form.schema = {"SYN-DOC-1": doc}, core.schema_enums(schema), schema
        form.protocol_hash, form.started_at, form.doc = "a" * 64, "2026-09-27T10:00:00+05:30", doc
        form._build()
        texts = [
            str(w.cget("text")) for w in form.form.winfo_children() if isinstance(w, ttk.Label)
        ]
        assert any("Role: ANNOTATOR_B (set by this folder)" in t for t in texts)
    finally:
        root.destroy()


def test_bundle_root_is_the_exe_folder_when_frozen_else_the_file_folder(monkeypatch):
    pytest.importorskip("tkinter")  # annotator_app imports tkinter at module level
    from tools.phase5.annotator import annotator_app as app

    monkeypatch.setattr(app.sys, "frozen", True, raising=False)
    monkeypatch.setattr(app.sys, "executable", str(Path("C:/pilot/annotator_app.exe")))
    assert app._bundle_root() == Path("C:/pilot").resolve()

    monkeypatch.delattr(app.sys, "frozen", raising=False)
    assert app._bundle_root() == Path(app.__file__).resolve().parent
