"""Build isolated annotator workspaces from a verified, synthetic-or-real roster.

The builder inspects PDF bytes only to hash and copy them. It never parses pages.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.phase5.annotator import annotator_core


ROSTER_COLUMNS = ["document_id", "source_pdf_sha256", "physical_page_count", "split"]
ASSIGNMENT_COLUMNS = annotator_core.ASSIGNMENT_COLUMNS
ROLES = ("ANNOTATOR_A", "ANNOTATOR_B")
# Match documentgold_selector._normalize_identifier: strip ASCII outer spaces,
# then require this ASCII identifier syntax.
DOCUMENT_ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
BUNDLE_ROOT = "annotator_bundle"
RESERVED_ROOT_NAMES = {"assignment.csv", "pdfs", "records", "WORKSPACE_MANIFEST.json"}


class WorkspaceBuildError(ValueError):
    """The requested workspace cannot be built safely."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _check_out(out: Path) -> Path:
    if out.exists() or out.is_symlink():
        raise WorkspaceBuildError("output already exists")
    out = out.resolve(strict=False)
    if out.exists() or out.is_symlink():
        raise WorkspaceBuildError("output already exists")
    for directory in (out, *out.parents):
        marker = directory / ".git"
        if marker.exists() or marker.is_symlink():
            raise WorkspaceBuildError("output is inside a git repository")
    if not out.parent.is_dir():
        raise WorkspaceBuildError("output parent directory does not exist")
    return out


def _read_roster(path: Path, allow_split: str | None) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        if next(reader, None) != ROSTER_COLUMNS:
            raise WorkspaceBuildError("roster columns must be exactly document_id, source_pdf_sha256, physical_page_count, split")
        for line_no, fields in enumerate(reader, start=2):
            if len(fields) != len(ROSTER_COLUMNS):
                raise WorkspaceBuildError(f"roster line {line_no}: malformed row")
            doc, sha, count, split = fields
            doc = doc.strip(" ")
            if DOCUMENT_ID_RE.fullmatch(doc) is None:
                raise WorkspaceBuildError(f"roster line {line_no}: invalid document_id")
            if doc in seen:
                raise WorkspaceBuildError(f"roster line {line_no}: duplicate document_id {doc}")
            seen.add(doc)
            if SHA256_RE.fullmatch(sha) is None:
                raise WorkspaceBuildError(f"roster line {line_no}: invalid source_pdf_sha256 for {doc}")
            if not count.isdigit() or int(count) < 1:
                raise WorkspaceBuildError(f"roster line {line_no}: invalid physical_page_count for {doc}")
            if split == "HOLDOUT" or split not in ({"FIT", allow_split} if allow_split else {"FIT"}):
                raise WorkspaceBuildError(f"roster line {line_no}: disallowed split for {doc}")
            rows.append(dict(zip(ROSTER_COLUMNS, (doc, sha, str(int(count)), split))))
    if not rows:
        raise WorkspaceBuildError("roster has no documents")
    return sorted(rows, key=lambda row: row["document_id"])


def _read_bundle(path: Path) -> dict[str, bytes]:
    """Read a flat, safe bundle before creating the output directory."""
    payload: dict[str, bytes] = {}
    seen: set[str] = set()
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            name = info.filename
            if "\\" in name or ":" in name or name.startswith("/"):
                raise WorkspaceBuildError("unsafe bundle member")
            parts = PurePosixPath(name).parts
            if not parts or parts[0] != BUNDLE_ROOT or any(part in {".", ".."} for part in parts):
                raise WorkspaceBuildError("unexpected bundle root or path")
            if len(parts) == 1:
                if not info.is_dir():
                    raise WorkspaceBuildError("bundle root must be a directory")
                continue
            relative = "/".join(parts[1:])
            folded = relative.casefold()
            if folded in seen:
                raise WorkspaceBuildError("duplicate bundle member")
            seen.add(folded)
            if parts[1].casefold() in RESERVED_ROOT_NAMES:
                if relative == "records" and info.is_dir():
                    continue
                raise WorkspaceBuildError("bundle member collides with workspace files")
            if stat.S_ISLNK(info.external_attr >> 16):
                raise WorkspaceBuildError("bundle symlink refused")
            if info.is_dir():
                continue
            payload[relative] = archive.read(info)
    if not payload:
        raise WorkspaceBuildError("bundle has no files")
    return payload


def _assignment_bytes(rows: list[dict[str, str]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(ASSIGNMENT_COLUMNS)
    for row in rows:
        writer.writerow([row[column] for column in ASSIGNMENT_COLUMNS])
    return stream.getvalue().encode("utf-8")


def _manifest_bytes(out: Path) -> bytes:
    entries = []
    for role in ROLES:
        for path in (out / role).rglob("*"):
            if path.is_file():
                entries.append({
                    "role": role,
                    "path": path.relative_to(out).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                })
    entries.sort(key=lambda entry: (entry["role"], entry["path"]))
    return (json.dumps(entries, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")


def build_workspaces(
    roster: Path, pdf_dir: Path, bundle: Path, out: Path,
    roles: tuple[str, ...] = ROLES, allow_split: str | None = None,
) -> str:
    """Build both role folders and return the manifest's SHA-256 digest."""
    if tuple(roles) != ROLES:
        raise WorkspaceBuildError("roles must be ANNOTATOR_A,ANNOTATOR_B")
    if allow_split not in (None, "VALIDATION"):
        raise WorkspaceBuildError("only VALIDATION may be allowed in addition to FIT")
    out = _check_out(Path(out))
    rows = _read_roster(Path(roster), allow_split)
    pdf_dir = Path(pdf_dir)
    for row in rows:
        pdf = pdf_dir / (row["document_id"] + ".pdf")
        if not pdf.is_file():
            raise WorkspaceBuildError(f"missing PDF for {row['document_id']}")
        if sha256_file(pdf) != row["source_pdf_sha256"]:
            raise WorkspaceBuildError(f"PDF SHA-256 mismatch for {row['document_id']}")
    payload = _read_bundle(Path(bundle))
    assignment = _assignment_bytes(rows)
    created = False
    try:
        out.mkdir()
        created = True
        for role in ROLES:
            root = out / role
            root.mkdir()
            for name, data in sorted(payload.items()):
                destination = root.joinpath(*PurePosixPath(name).parts)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
            pdfs = root / "pdfs"
            pdfs.mkdir()
            for row in rows:
                name = row["document_id"] + ".pdf"
                destination = pdfs / name
                shutil.copyfile(pdf_dir / name, destination)
                if sha256_file(destination) != row["source_pdf_sha256"]:
                    raise WorkspaceBuildError(f"PDF changed during copy for {row['document_id']}")
            (root / "assignment.csv").write_bytes(assignment)
            (root / "records").mkdir()
            refusals = annotator_core.workspace_refusals(root, root)
            if refusals:
                raise WorkspaceBuildError("annotator workspace isolation refusal: " + "; ".join(refusals))
        manifest = _manifest_bytes(out)
        (out / "WORKSPACE_MANIFEST.json").write_bytes(manifest)
        return hashlib.sha256(manifest).hexdigest()
    except BaseException:
        if created:
            shutil.rmtree(out)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build isolated annotator workspaces.")
    parser.add_argument("--roster", required=True, type=Path)
    parser.add_argument("--pdf-dir", required=True, type=Path)
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--roles", required=True)
    parser.add_argument("--allow-split", choices=["VALIDATION"])
    args = parser.parse_args(argv)
    try:
        digest = build_workspaces(
            args.roster, args.pdf_dir, args.bundle, args.out,
            tuple(args.roles.split(",")), args.allow_split,
        )
    except (OSError, ValueError, csv.Error, zipfile.BadZipFile) as exc:
        parser.exit(1, f"refused: {exc}\n")
    print(digest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
