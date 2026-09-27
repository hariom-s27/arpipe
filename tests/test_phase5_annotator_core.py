"""Synthetic-only checks for the offline annotation core and bundle."""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools/phase5/annotator"
sys.path.insert(0, str(TOOL))
import core  # noqa: E402
import make_bundle  # noqa: E402
import export_role  # noqa: E402


@pytest.fixture
def synthetic(tmp_path):
    root = tmp_path / "bundle"
    root.mkdir()
    for source, name in ((REPO / "docs/phase5/gold_schema_v0_1.json", core.SCHEMA_FILE),
                         (REPO / "docs/phase5/GOLD_PROTOCOL_v0_1.md", core.PROTOCOL_FILE)):
        (root / name).write_bytes(source.read_bytes())
    source = tmp_path / "synthetic-bytes.bin"
    source.write_bytes(b"synthetic bytes only; no PDF content")
    digest = core.sha256_file(source)
    assignment = {"document_id": "SYNTHETIC_001", "source_pdf_sha256": digest,
                  "physical_page_count": 12}
    record = {
        "record_type": "RAW", "document_id": assignment["document_id"],
        "source_pdf_sha256": digest, "annotator_role": "ANNOTATOR_A",
        "presence_state": "PRESENT", "presence_reason_code": "BODY_QUALIFYING_TITLE",
        "primary_span": {"start_page": 2, "end_page": 5},
        "alternative_spans": [], "gap_pages": [], "flags": [],
        "ambiguity_code": "NONE", "admissible_spans": [],
        "parent_section": None, "annexure_identity": None,
        "boundary_evidence": {
            "heading_start_page": 2, "substantive_start_page": 3,
            "last_content_page": 5, "next_section_heading_page": 6,
            "mixed_end_page": None,
            "viewer_start_page_1based": 3, "viewer_end_page_1based": 6,
        },
        "timestamps": {"started_at": "2026-01-01T10:00:00Z",
                       "completed_at": "2026-01-01T10:05:00Z"},
        "aids_used": ["PDF_VIEWER", "THUMBNAILS"],
        "structured_provenance": {
            "annotation_workspace_id": core.workspace_id(root),
            "viewer_name": "Synthetic viewer", "viewer_version": "1",
            "viewer_page_convention": core.PAGE_CONVENTION,
            "physical_page_count": 12, "search_queries": ["synthetic query"],
            "search_usable": True, "bookmark_pages": [], "flag_pages": {},
            "source_pdf_hash_verified": True, "no_repository_access_attested": True,
            "no_system_output_access_attested": True,
        },
        "protocol_version_hash": core.sha256_file(root / core.PROTOCOL_FILE),
    }
    return root, source, assignment, record


def test_schema_passes_valid_raw_synthetic_record(synthetic):
    root, _, assignment, record = synthetic
    core.validate_raw(record, core.load_schema(root), assignment)


@pytest.mark.parametrize("change", [
    lambda r: r.update(primary_span=None),
    lambda r: r["primary_span"].update(end_page=12),
    lambda r: r["primary_span"].update(start_page=7),
    lambda r: r.update(gap_pages=[2], flags=["noncontiguous_hull"]),
    lambda r: r.update(flags=["annexure"]),
    lambda r: r["timestamps"].update(completed_at="2026-01-01T09:00:00Z"),
    lambda r: r["boundary_evidence"].update(viewer_start_page_1based=4),
    lambda r: r.update(presence_state="AMBIGUOUS", primary_span=None,
                       presence_reason_code="START_UNRESOLVABLE",
                       ambiguity_code="START_UNRESOLVABLE"),
])
def test_schema_or_numeric_invariant_refuses_invalid_record(synthetic, change):
    root, _, assignment, record = synthetic
    change(record)
    with pytest.raises(core.AnnotationError):
        core.validate_raw(record, core.load_schema(root), assignment)


def test_viewer_pages_convert_to_zero_based_and_reject_out_of_range():
    assert core.viewer_to_index(1, 12) == 0
    assert core.viewer_to_index("12", 12) == 11
    for bad in (0, 13, "", "1.5", True):
        with pytest.raises(core.AnnotationError):
            core.viewer_to_index(bad, 12)


def test_pdf_hash_mismatch_refuses_synthetic_bytes(synthetic):
    _, source, assignment, _ = synthetic
    source.write_bytes(b"different synthetic bytes")
    with pytest.raises(core.AnnotationError, match="SHA-256"):
        core.verify_source(source, assignment, 12)
    with pytest.raises(core.AnnotationError, match="page count"):
        core.verify_source(source, assignment, 11)


def test_canonical_json_bytes_and_hash_are_stable():
    one = {"z": [2, 1], "a": "é"}
    two = {"a": "é", "z": [2, 1]}
    assert core.canonical_bytes(one) == core.canonical_bytes(two)
    assert core.canonical_bytes(one).endswith(b"\n")
    assert b" \n" not in core.canonical_bytes(one)
    assert hashlib.sha256(core.canonical_bytes(one)).hexdigest() == hashlib.sha256(core.canonical_bytes(two)).hexdigest()


def test_overwrite_refusal_and_explicit_supersede_preserve_old_record(synthetic):
    root, source, assignment, record = synthetic
    schema = core.load_schema(root)
    old_path, old_hash = core.submit_raw(root, record, assignment, source, 12, schema)
    assert old_path.read_bytes() == core.canonical_bytes(record)
    with pytest.raises(core.AnnotationError, match="supersede"):
        core.submit_raw(root, record, assignment, source, 12, schema)
    control_path, _ = core.create_supersede(root, assignment["document_id"], "ANNOTATOR_A",
                                            old_hash, "Synthetic correction")
    assert json.loads(control_path.read_text(encoding="utf-8"))["old_sha256"] == old_hash
    record["boundary_evidence"]["last_content_page"] = 4
    new_path, new_hash = core.submit_raw(root, record, assignment, source, 12, schema)
    assert new_path != old_path and new_hash != old_hash
    assert hashlib.sha256(old_path.read_bytes()).hexdigest() == old_hash
    assert len((root / "records/HASH_LOG.txt").read_text(encoding="utf-8").splitlines()) == 3
    core.create_supersede(root, assignment["document_id"], "ANNOTATOR_A", new_hash,
                          "Second synthetic correction")
    record["boundary_evidence"]["last_content_page"] = 5
    record["structured_provenance"]["search_queries"].append("second synthetic query")
    third_path, _ = core.submit_raw(root, record, assignment, source, 12, schema)
    assert third_path != new_path


def test_repo_ancestry_refuses_startup(tmp_path):
    repo = tmp_path / "synthetic_repo"
    bundle = repo / "bundle"
    bundle.mkdir(parents=True)
    (repo / ".git").mkdir()
    with pytest.raises(core.AnnotationError, match="Repository detected"):
        core.check_workspace(bundle, bundle)


def test_missing_jsonschema_refuses_submit_even_when_record_is_well_formed(synthetic, monkeypatch):
    root, _, assignment, record = synthetic
    original_import = __import__
    def missing(name, *args, **kwargs):
        if name == "jsonschema":
            raise ImportError("synthetic missing dependency")
        return original_import(name, *args, **kwargs)
    monkeypatch.setattr("builtins.__import__", missing)
    with pytest.raises(core.AnnotationError, match="jsonschema is required"):
        core.validate_raw(record, core.load_schema(root), assignment)


def test_role_export_contains_only_sealed_role_records_and_log(synthetic, tmp_path):
    root, source, assignment, record = synthetic
    path, digest = core.submit_raw(root, record, assignment, source, 12, core.load_schema(root))
    output = tmp_path / "role.zip"
    manifest = export_role.export_role(root, "ANNOTATOR_A", output)
    with zipfile.ZipFile(output) as archive:
        assert set(archive.namelist()) == {f"records/ANNOTATOR_A/{path.name}", "records/HASH_LOG.txt"}
        assert archive.read("records/HASH_LOG.txt") == f"{digest}  {path.name}\n".encode()
    assert len(manifest) == 2


def test_bundle_contains_exactly_allowed_members_and_hashes(tmp_path):
    output = tmp_path / "annotator_bundle.zip"
    manifest = make_bundle.build_bundle(output)
    allowed = {"app.py", "core.py", "export_role.py", "gold_schema_v0_1.json",
               "GOLD_PROTOCOL_v0_1.md", "README.md", "TITLE_LIST_NOT_YET_FROZEN.txt", "records/"}
    with zipfile.ZipFile(output) as archive:
        assert set(archive.namelist()) == allowed
        assert archive.read("records/") == b""
        for name, size, digest in manifest:
            data = archive.read(name)
            assert len(data) == size
            assert hashlib.sha256(data).hexdigest() == digest
