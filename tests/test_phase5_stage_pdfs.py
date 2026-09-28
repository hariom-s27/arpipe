"""Synthetic-only tests for staging PDFs from the live_store blob layout."""

from __future__ import annotations

import csv
import hashlib
import tempfile
from pathlib import Path

import pytest

from tools.phase5 import stage_pdfs


@pytest.fixture()
def outside_repo():
    # Not tmp_path: with --basetemp inside the checkout, tmp_path sits under the real
    # .git, so the outside-repository check would always refuse it.
    with tempfile.TemporaryDirectory(prefix="p5_stage_pdfs_") as temporary:
        yield Path(temporary)


def write_roster(path: Path, rows: list[dict[str, str]]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=stage_pdfs.ROSTER_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_blob(live_store: Path, data: bytes) -> str:
    sha = hashlib.sha256(data).hexdigest()
    blob = live_store / "blobs" / sha[0:2] / sha[2:4] / f"{sha}.pdf"
    blob.parent.mkdir(parents=True, exist_ok=True)
    blob.write_bytes(data)
    return sha


@pytest.fixture()
def synthetic_case(outside_repo):
    live_store = outside_repo / "live_store"
    live_store.mkdir()
    rows = []
    payloads = {"DOC_A": b"synthetic pdf bytes A\n", "DOC_B": b"synthetic pdf bytes B\n"}
    for document_id, data in payloads.items():
        sha = write_blob(live_store, data)
        rows.append({
            "document_id": document_id, "source_pdf_sha256": sha,
            "physical_page_count": "3", "split": "FIT",
        })
    roster = outside_repo / "roster.csv"
    write_roster(roster, rows)
    return outside_repo, roster, live_store, rows, payloads


def test_copies_and_verifies_every_document(synthetic_case):
    outside_repo, roster, live_store, rows, payloads = synthetic_case
    out = outside_repo / "staged"
    manifest = stage_pdfs.stage_pdfs(roster, live_store, out)
    assert {entry["document_id"] for entry in manifest} == {"DOC_A", "DOC_B"}
    for document_id, data in payloads.items():
        assert (out / f"{document_id}.pdf").read_bytes() == data
    with open(out / "STAGE_MANIFEST.csv", encoding="utf-8", newline="") as handle:
        on_disk = list(csv.DictReader(handle))
    assert list(on_disk[0]) == ["document_id", "sha256", "bytes"]
    assert {row["document_id"] for row in on_disk} == {"DOC_A", "DOC_B"}
    for row in on_disk:
        assert row["sha256"] == hashlib.sha256(payloads[row["document_id"]]).hexdigest()
        assert int(row["bytes"]) == len(payloads[row["document_id"]])


def test_missing_blob_is_refused_and_output_is_removed(synthetic_case):
    outside_repo, roster, live_store, rows, _ = synthetic_case
    # Remove DOC_B's blob entirely.
    sha_b = next(r["source_pdf_sha256"] for r in rows if r["document_id"] == "DOC_B")
    blob = live_store / "blobs" / sha_b[0:2] / sha_b[2:4] / f"{sha_b}.pdf"
    blob.unlink()
    out = outside_repo / "staged"
    with pytest.raises(stage_pdfs.StagePdfsError, match="missing blob"):
        stage_pdfs.stage_pdfs(roster, live_store, out)
    assert not out.exists()


def test_wrong_blob_hash_is_refused_and_output_is_removed(synthetic_case):
    outside_repo, roster, live_store, rows, _ = synthetic_case
    sha_a = next(r["source_pdf_sha256"] for r in rows if r["document_id"] == "DOC_A")
    blob = live_store / "blobs" / sha_a[0:2] / sha_a[2:4] / f"{sha_a}.pdf"
    blob.write_bytes(b"tampered bytes, wrong hash now\n")
    out = outside_repo / "staged"
    with pytest.raises(stage_pdfs.StagePdfsError, match="hash mismatch"):
        stage_pdfs.stage_pdfs(roster, live_store, out)
    assert not out.exists()


def test_out_inside_a_repository_is_refused(synthetic_case):
    outside_repo, roster, live_store, _, _ = synthetic_case
    fake_repo = outside_repo / "fake_repo"
    (fake_repo / ".git").mkdir(parents=True)
    out = fake_repo / "staged"
    with pytest.raises(stage_pdfs.StagePdfsError, match="outside the repository"):
        stage_pdfs.stage_pdfs(roster, live_store, out)
    assert not out.exists()


def test_out_must_be_new_or_empty(synthetic_case):
    outside_repo, roster, live_store, _, _ = synthetic_case
    out = outside_repo / "staged"
    out.mkdir()
    (out / "stray.txt").write_text("x", encoding="utf-8")
    with pytest.raises(stage_pdfs.StagePdfsError, match="not empty"):
        stage_pdfs.stage_pdfs(roster, live_store, out)


def test_reuses_an_existing_empty_out_dir(synthetic_case):
    outside_repo, roster, live_store, rows, payloads = synthetic_case
    out = outside_repo / "staged"
    out.mkdir()
    manifest = stage_pdfs.stage_pdfs(roster, live_store, out)
    assert len(manifest) == 2
    assert out.exists()


def test_malformed_roster_is_refused(synthetic_case):
    outside_repo, roster, live_store, rows, _ = synthetic_case
    bad_roster = outside_repo / "bad_roster.csv"
    write_roster(bad_roster, [{**rows[0], "document_id": "../etc"}])
    out = outside_repo / "staged"
    with pytest.raises(stage_pdfs.StagePdfsError, match="invalid document_id"):
        stage_pdfs.stage_pdfs(bad_roster, live_store, out)


def test_main_cli_refuses_with_exit_code_one(synthetic_case, capsys):
    outside_repo, roster, live_store, rows, _ = synthetic_case
    sha_b = next(r["source_pdf_sha256"] for r in rows if r["document_id"] == "DOC_B")
    blob = live_store / "blobs" / sha_b[0:2] / sha_b[2:4] / f"{sha_b}.pdf"
    blob.unlink()
    with pytest.raises(SystemExit) as excinfo:
        stage_pdfs.main([
            "--roster", str(roster), "--live-store", str(live_store),
            "--out", str(outside_repo / "staged"),
        ])
    assert excinfo.value.code == 1
    assert "refused" in capsys.readouterr().err


def test_main_cli_happy_path_prints_count(synthetic_case, capsys):
    outside_repo, roster, live_store, _, _ = synthetic_case
    assert stage_pdfs.main([
        "--roster", str(roster), "--live-store", str(live_store),
        "--out", str(outside_repo / "staged"),
    ]) == 0
    assert "2" in capsys.readouterr().out
