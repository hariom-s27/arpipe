"""Custodian export of one role's sealed records and matching hash log."""

from __future__ import annotations

import argparse
import hashlib
import re
import zipfile
from pathlib import Path

from core import AnnotationError, ROLES


def export_role(bundle_root: Path, role: str, output: Path) -> list[tuple[str, int, str]]:
    if role not in ROLES:
        raise AnnotationError("Export role must be ANNOTATOR_A or ANNOTATOR_B")
    root = Path(bundle_root)
    folder = root / "records" / role
    if not folder.is_dir():
        raise AnnotationError("No sealed records for that role")
    log = root / "records" / "HASH_LOG.txt"
    if not log.is_file():
        raise AnnotationError("Missing HASH_LOG.txt")
    files = sorted(folder.glob("*.json"))
    role_names = {path.name for path in files}
    expected = {}
    for line in log.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9._-]+\.json)", line)
        if not match:
            raise AnnotationError("Malformed HASH_LOG.txt")
        digest, name = match.groups()
        if name in role_names:
            if name in expected:
                raise AnnotationError("Duplicate hash-log filename")
            expected[name] = digest
    if role_names != set(expected):
        raise AnnotationError("Role files do not match HASH_LOG.txt")
    entries = {}
    for path in files:
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != expected[path.name]:
            raise AnnotationError(f"Sealed record hash mismatch: {path.name}")
        entries[f"records/{role}/{path.name}"] = data
    role_log = "".join(f"{expected[path.name]}  {path.name}\n" for path in files).encode("utf-8")
    entries["records/HASH_LOG.txt"] = role_log
    manifest = []
    with zipfile.ZipFile(output, mode="x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(entries.items()):
            archive.writestr(name, data)
            manifest.append((name, len(data), hashlib.sha256(data).hexdigest()))
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle_root", type=Path)
    parser.add_argument("role", choices=ROLES)
    parser.add_argument("output_zip", type=Path)
    args = parser.parse_args()
    for path, size, digest in export_role(args.bundle_root, args.role, args.output_zip):
        print(f"{path}\t{size}\t{digest}")


if __name__ == "__main__":
    main()
