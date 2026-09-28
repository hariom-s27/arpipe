"""Stage PDFs from the live_store content-addressed store into a flat verified folder.

Standard library only. Reads a roster CSV (document_id, source_pdf_sha256,
physical_page_count, split), copies each document's blob from
``<live_store>/blobs/<sha[0:2]>/<sha[2:4]>/<sha>.pdf`` to ``<out>/<document_id>.pdf``,
and verifies the SHA-256 of every copy. Refuses on any hash mismatch or missing blob.
It never reads PDF content beyond hashing bytes.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import shutil
import sys
from pathlib import Path

ROSTER_COLUMNS = ["document_id", "source_pdf_sha256", "physical_page_count", "split"]
MANIFEST_COLUMNS = ["document_id", "sha256", "bytes"]
DOCUMENT_ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class StagePdfsError(ValueError):
    """The stage cannot proceed safely; nothing already copied is trusted."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_roster(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    with open(path, encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, strict=True)
        if next(reader, None) != ROSTER_COLUMNS:
            raise StagePdfsError(f"roster columns must be exactly {ROSTER_COLUMNS}")
        for line_no, fields in enumerate(reader, start=2):
            if len(fields) != len(ROSTER_COLUMNS):
                raise StagePdfsError(f"roster line {line_no}: malformed row")
            doc, sha, count, split = fields
            doc = doc.strip(" ")
            if DOCUMENT_ID_RE.fullmatch(doc) is None:
                raise StagePdfsError(f"roster line {line_no}: invalid document_id")
            if doc in seen:
                raise StagePdfsError(f"roster line {line_no}: duplicate document_id {doc}")
            seen.add(doc)
            if SHA256_RE.fullmatch(sha) is None:
                raise StagePdfsError(f"roster line {line_no}: invalid source_pdf_sha256 for {doc}")
            if not count.isdigit() or int(count) < 1:
                raise StagePdfsError(f"roster line {line_no}: invalid physical_page_count for {doc}")
            if not split:
                raise StagePdfsError(f"roster line {line_no}: empty split for {doc}")
            rows.append({"document_id": doc, "source_pdf_sha256": sha})
    if not rows:
        raise StagePdfsError("roster has no documents")
    return sorted(rows, key=lambda row: row["document_id"])


def _check_out_dir(out: Path) -> tuple[Path, bool]:
    out = Path(out).resolve(strict=False)
    for directory in (out, *out.parents):
        if (directory / ".git").exists():
            raise StagePdfsError(f"--out must be outside the repository (found {directory / '.git'})")
    if out.exists():
        if any(out.iterdir()):
            raise StagePdfsError("--out exists and is not empty")
        return out, False
    return out, True


def _blob_path(live_store: Path, sha256: str) -> Path:
    return live_store / "blobs" / sha256[0:2] / sha256[2:4] / f"{sha256}.pdf"


def _write_manifest(path: Path, rows: list[dict[str, object]]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for row in sorted(rows, key=lambda r: r["document_id"]):
            writer.writerow(row)


def stage_pdfs(roster: Path, live_store: Path, out: Path) -> list[dict[str, object]]:
    """Copy and verify every roster document's PDF; write STAGE_MANIFEST.csv in ``out``."""
    rows = _read_roster(Path(roster))
    live_store = Path(live_store)
    out, created = _check_out_dir(Path(out))
    manifest: list[dict[str, object]] = []
    try:
        if created:
            out.mkdir(parents=True)
        for row in rows:
            document_id, sha256 = row["document_id"], row["source_pdf_sha256"]
            blob = _blob_path(live_store, sha256)
            if not blob.is_file():
                raise StagePdfsError(f"missing blob for {document_id}: {blob}")
            destination = out / f"{document_id}.pdf"
            shutil.copyfile(blob, destination)
            actual = sha256_file(destination)
            if actual != sha256:
                raise StagePdfsError(f"hash mismatch after copy for {document_id}")
            manifest.append({"document_id": document_id, "sha256": actual, "bytes": destination.stat().st_size})
        _write_manifest(out / "STAGE_MANIFEST.csv", manifest)
        return manifest
    except BaseException:
        if created:
            shutil.rmtree(out, ignore_errors=True)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Stage roster PDFs from the live_store blob layout.")
    parser.add_argument("--roster", required=True, type=Path)
    parser.add_argument("--live-store", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        manifest = stage_pdfs(args.roster, args.live_store, args.out)
    except (StagePdfsError, OSError, csv.Error) as exc:
        parser.exit(1, f"refused: {exc}\n")
    print(f"staged {len(manifest)} document(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
