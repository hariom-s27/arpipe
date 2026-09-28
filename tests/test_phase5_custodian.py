"""Synthetic-only tests for the P5-C custodian workspace builder."""

from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path

import pytest

from tools.phase5.annotator import annotator_core
from tools.phase5.custodian import build_workspaces as builder


FAKE_PDFS = {
    "SYNTH_A": b"synthetic PDF bytes A\n",
    "SYNTH_B": b"synthetic PDF bytes B\n",
}


def write_roster(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=builder.ROSTER_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def synthetic_case():
    # Outside the checkout: workspace_refusals intentionally checks every parent.
    with tempfile.TemporaryDirectory(prefix="p5c_synthetic_") as temporary:
        root = Path(temporary)
        pdf_dir = root / "pdfs"
        pdf_dir.mkdir()
        rows = []
        for doc, data in FAKE_PDFS.items():
            (pdf_dir / f"{doc}.pdf").write_bytes(data)
            rows.append({
                "document_id": doc,
                "source_pdf_sha256": hashlib.sha256(data).hexdigest(),
                "physical_page_count": "2",
                "split": "FIT",
            })
        roster = root / "roster.csv"
        write_roster(roster, rows)
        bundle = root / "bundle.zip"
        with zipfile.ZipFile(bundle, "w") as archive:
            archive.writestr("annotator_bundle/README.md", "Synthetic bundle\n")
            archive.writestr("annotator_bundle/annotator_core.py", "# synthetic tool payload\n")
            archive.writestr("annotator_bundle/records/", b"")
        yield root, roster, pdf_dir, bundle, rows


def run_build(case, out: Path, allow_split: str | None = None) -> str:
    _, roster, pdf_dir, bundle, _ = case
    return builder.build_workspaces(roster, pdf_dir, bundle, out, allow_split=allow_split)


def test_happy_path_builds_two_isolated_roles(synthetic_case, capsys):
    root, roster, pdf_dir, bundle, rows = synthetic_case
    out = root / "workspaces"
    assert builder.main([
        "--roster", str(roster), "--pdf-dir", str(pdf_dir),
        "--bundle", str(bundle), "--out", str(out),
        "--roles", "ANNOTATOR_A,ANNOTATOR_B",
    ]) == 0
    manifest_bytes = (out / "WORKSPACE_MANIFEST.json").read_bytes()
    assert capsys.readouterr().out.strip() == hashlib.sha256(manifest_bytes).hexdigest()
    assert {p.name for p in out.iterdir()} == {"ANNOTATOR_A", "ANNOTATOR_B", "WORKSPACE_MANIFEST.json"}
    for role in builder.ROLES:
        workspace = out / role
        assert {p.name for p in workspace.iterdir()} == {
            "README.md", "annotator_core.py", "pdfs", "ASSIGNMENT.csv", "records", "ROLE.txt",
        }
        assert list((workspace / "records").iterdir()) == []
        assert annotator_core.workspace_refusals(workspace, workspace) == []
        for row in rows:
            assert (workspace / "pdfs" / f"{row['document_id']}.pdf").read_bytes() == FAKE_PDFS[row["document_id"]]
    manifest = json.loads(manifest_bytes)
    assert [entry["path"] for entry in manifest] == sorted(entry["path"] for entry in manifest)
    assert all(set(entry) == {"role", "path", "bytes", "sha256"} for entry in manifest)
    assert all((out / entry["path"]).stat().st_size == entry["bytes"] for entry in manifest)
    assert all(builder.sha256_file(out / entry["path"]) == entry["sha256"] for entry in manifest)


def test_hash_mismatch_refuses_without_output(synthetic_case):
    root, _, pdf_dir, _, _ = synthetic_case
    (pdf_dir / "SYNTH_B.pdf").write_bytes(b"changed synthetic bytes")
    out = root / "workspaces"
    with pytest.raises(builder.WorkspaceBuildError, match="SHA-256 mismatch"):
        run_build(synthetic_case, out)
    assert not out.exists()


def test_holdout_row_is_always_refused(synthetic_case):
    root, roster, _, _, rows = synthetic_case
    rows[0]["split"] = "HOLDOUT"
    write_roster(roster, rows)
    out = root / "workspaces"
    with pytest.raises(builder.WorkspaceBuildError, match="disallowed split"):
        run_build(synthetic_case, out, allow_split="VALIDATION")
    assert not out.exists()


def test_validation_requires_explicit_flag(synthetic_case):
    root, roster, _, _, rows = synthetic_case
    rows[0]["split"] = "VALIDATION"
    write_roster(roster, rows)
    out = root / "workspaces"
    with pytest.raises(builder.WorkspaceBuildError, match="disallowed split"):
        run_build(synthetic_case, out)
    assert not out.exists()
    run_build(synthetic_case, out, allow_split="VALIDATION")
    assert (out / "ANNOTATOR_A" / "ASSIGNMENT.csv").is_file()


def test_out_inside_fake_repository_is_refused(synthetic_case):
    root, *_ = synthetic_case
    fake_repo = root / "fake_repo"
    (fake_repo / ".git").mkdir(parents=True)
    out = fake_repo / "workspaces"
    with pytest.raises(builder.WorkspaceBuildError, match="git repository"):
        run_build(synthetic_case, out)
    assert not out.exists()


def test_duplicate_roster_row_is_refused(synthetic_case):
    root, roster, _, _, rows = synthetic_case
    write_roster(roster, [*rows, rows[0]])
    out = root / "workspaces"
    with pytest.raises(builder.WorkspaceBuildError, match="duplicate document_id"):
        run_build(synthetic_case, out)
    assert not out.exists()


def test_malformed_document_id_is_refused(synthetic_case):
    root, roster, _, _, rows = synthetic_case
    rows[0]["document_id"] = "../SYNTH_A"
    write_roster(roster, rows)
    out = root / "workspaces"
    with pytest.raises(builder.WorkspaceBuildError, match="invalid document_id"):
        run_build(synthetic_case, out)
    assert not out.exists()


def test_annotator_isolation_refusal_removes_output(synthetic_case):
    root, _, _, bundle, _ = synthetic_case
    with zipfile.ZipFile(bundle, "a") as archive:
        archive.writestr("annotator_bundle/.git/config", "synthetic marker\n")
    out = root / "workspaces"
    with pytest.raises(builder.WorkspaceBuildError, match="isolation refusal"):
        run_build(synthetic_case, out)
    assert not out.exists()


def test_manifest_is_deterministic_across_output_directories(synthetic_case):
    root, *_ = synthetic_case
    first = root / "first"
    second = root / "second"
    first_hash = run_build(synthetic_case, first)
    second_hash = run_build(synthetic_case, second)
    assert first_hash == second_hash
    assert (first / "WORKSPACE_MANIFEST.json").read_bytes() == (second / "WORKSPACE_MANIFEST.json").read_bytes()


def test_assignment_is_accepted_by_annotator_core(synthetic_case):
    root, _, _, _, rows = synthetic_case
    out = root / "workspaces"
    run_build(synthetic_case, out)
    for role in builder.ROLES:
        assignment = annotator_core.load_assignment(out / role / "ASSIGNMENT.csv")
        assert set(assignment) == {row["document_id"] for row in rows}
        assert all(assignment[row["document_id"]]["physical_page_count"] == 2 for row in rows)


# -- exe and ROLE.txt (F7) ----------------------------------------------------------

def test_role_txt_is_always_written(synthetic_case):
    root, roster, pdf_dir, bundle, _ = synthetic_case
    out = root / "workspaces"
    run_build(synthetic_case, out)
    for role in builder.ROLES:
        assert (out / role / "ROLE.txt").read_text(encoding="utf-8") == role + "\n"


def test_exe_is_copied_and_hashed_into_both_workspaces(synthetic_case):
    root, roster, pdf_dir, bundle, _ = synthetic_case
    exe = root / "annotator_app.exe"
    exe_bytes = b"synthetic exe payload, not a real executable\n"
    exe.write_bytes(exe_bytes)
    exe_sha256 = hashlib.sha256(exe_bytes).hexdigest()
    out = root / "workspaces"
    assert builder.main([
        "--roster", str(roster), "--pdf-dir", str(pdf_dir),
        "--bundle", str(bundle), "--out", str(out),
        "--roles", "ANNOTATOR_A,ANNOTATOR_B",
        "--exe", str(exe), "--exe-sha256", exe_sha256,
    ]) == 0
    manifest = json.loads((out / "WORKSPACE_MANIFEST.json").read_bytes())
    manifest_by_path = {(entry["role"], entry["path"]): entry for entry in manifest}
    for role in builder.ROLES:
        destination = out / role / "annotator_app.exe"
        assert destination.read_bytes() == exe_bytes
        entry = manifest_by_path[(role, f"{role}/annotator_app.exe")]
        assert entry["sha256"] == exe_sha256
        assert entry["bytes"] == len(exe_bytes)


def test_wrong_exe_sha256_is_refused_without_output(synthetic_case):
    root, roster, pdf_dir, bundle, _ = synthetic_case
    exe = root / "annotator_app.exe"
    exe.write_bytes(b"synthetic exe payload\n")
    out = root / "workspaces"
    with pytest.raises(builder.WorkspaceBuildError, match="does not match"):
        builder.build_workspaces(
            roster, pdf_dir, bundle, out, exe=exe, exe_sha256="0" * 64,
        )
    assert not out.exists()


def test_exe_and_exe_sha256_must_be_given_together(synthetic_case):
    root, roster, pdf_dir, bundle, _ = synthetic_case
    exe = root / "annotator_app.exe"
    exe.write_bytes(b"synthetic exe payload\n")
    out = root / "workspaces"
    with pytest.raises(builder.WorkspaceBuildError, match="together"):
        builder.build_workspaces(roster, pdf_dir, bundle, out, exe=exe)
    assert not out.exists()
    with pytest.raises(builder.WorkspaceBuildError, match="together"):
        builder.build_workspaces(roster, pdf_dir, bundle, out, exe_sha256="0" * 64)
    assert not out.exists()


def test_without_exe_no_exe_is_written_but_role_txt_still_is(synthetic_case):
    root, roster, pdf_dir, bundle, _ = synthetic_case
    out = root / "workspaces"
    run_build(synthetic_case, out)
    for role in builder.ROLES:
        assert not (out / role / "annotator_app.exe").exists()
        assert (out / role / "ROLE.txt").is_file()


@pytest.mark.parametrize("reserved_name", ["ROLE.txt", "role.txt", "annotator_app.exe", "ANNOTATOR_APP.EXE"])
def test_bundle_member_colliding_with_role_or_exe_name_is_refused(synthetic_case, reserved_name):
    root, _, pdf_dir, bundle, _ = synthetic_case
    with zipfile.ZipFile(bundle, "a") as archive:
        archive.writestr(f"annotator_bundle/{reserved_name}", "collision\n")
    out = root / "workspaces"
    with pytest.raises(builder.WorkspaceBuildError, match="collides"):
        run_build(synthetic_case, out)
    assert not out.exists()


def test_bundle_manifest_json_does_not_collide_with_reserved_workspace_names(synthetic_case):
    """A real bundle-shipped BUNDLE_MANIFEST.json (make_bundle.py) must reach the
    workspace root untouched, exactly like README.md or annotator_core.py, and not be
    treated as a reserved name collision (F6: it sits alongside the renamed ASSIGNMENT.csv)."""
    root, _, pdf_dir, bundle, _ = synthetic_case
    with zipfile.ZipFile(bundle, "a") as archive:
        archive.writestr("annotator_bundle/BUNDLE_MANIFEST.json", '{"bundle_format": 1}\n')
    out = root / "workspaces"
    run_build(synthetic_case, out)
    for role in builder.ROLES:
        manifest_path = out / role / "BUNDLE_MANIFEST.json"
        assert manifest_path.is_file()
        assert manifest_path.read_text(encoding="utf-8") == '{"bundle_format": 1}\n'
        assert (out / role / "ASSIGNMENT.csv").is_file()
