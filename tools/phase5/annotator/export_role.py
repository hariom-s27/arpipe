"""Custodian command: export one role's sealed records (P5-T).

Usage (run by the seal holder / custodian, not by an annotator)::

    python export_role.py --records <bundle>/records --role ANNOTATOR_A --out A_export.zip

It checks every sealed file against HASH_LOG.txt and its filename, writes a
deterministic zip of the role folder + HASH_LOG.txt + WORKSPACE_ID.txt, prints a
manifest (path, bytes, sha256), and then writes ``EXPORTED.lock`` in the role folder.
After the lock exists the tool refuses new records and supersessions for that role
(GOLD_PROTOCOL v0.1 section 9: no raw supersession after comparison).
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import zipfile
from pathlib import Path

try:  # package import (tests, repository)
    from . import annotator_core as core
except ImportError:  # run as a script from the bundle folder
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import annotator_core as core  # noqa: E402

FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def export_role(records_dir: Path, role: str, out_zip: Path) -> list[tuple[str, int, str]]:
    records_dir = Path(records_dir)
    if role not in core.RAW_ROLES:
        raise core.AnnotatorError(f"unknown role {role!r}")
    folder = records_dir / role
    if (folder / core.EXPORT_LOCK_NAME).exists():
        raise core.AnnotatorError(f"{role} was already exported")
    logged = {rel: digest for digest, rel in core.read_hash_log(records_dir)}
    files = list(core.iter_role_files(records_dir, role))
    if not files:
        raise core.AnnotatorError(f"no sealed records for {role}")
    for path in files:
        rel = path.relative_to(records_dir).as_posix()
        digest = core.sha256_file(path)
        if logged.get(rel) != digest:
            raise core.AnnotatorError(f"{rel}: hash does not match HASH_LOG.txt")
        if digest[:8] not in path.stem.rsplit("__", 1)[-1]:
            raise core.AnnotatorError(f"{rel}: filename hash prefix does not match content")
    members = [p.relative_to(records_dir).as_posix() for p in files]
    for extra in (core.HASH_LOG_NAME, core.WORKSPACE_ID_NAME):
        if (records_dir / extra).exists():
            members.append(extra)
    manifest: list[tuple[str, int, str]] = []
    out_zip = Path(out_zip)
    if out_zip.exists():
        raise core.AnnotatorError(f"refusing to overwrite {out_zip}")
    with zipfile.ZipFile(out_zip, "x", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel in sorted(members):
            data = (records_dir / rel).read_bytes()
            info = zipfile.ZipInfo(rel, date_time=FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o444 << 16
            zf.writestr(info, data)
            manifest.append((rel, len(data), hashlib.sha256(data).hexdigest()))
    (folder / core.EXPORT_LOCK_NAME).write_text(
        f"exported {core.now_rfc3339()} zip_sha256={core.sha256_file(out_zip)}\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--records", required=True, type=Path)
    parser.add_argument("--role", required=True, choices=core.RAW_ROLES)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        manifest = export_role(args.records, args.role, args.out)
    except core.AnnotatorError as exc:
        print(f"EXPORT REFUSED: {exc}", file=sys.stderr)
        return 2
    for rel, size, digest in manifest:
        print(f"{digest}  {size:>10}  {rel}")
    print(f"{core.sha256_file(args.out)}  {args.out.stat().st_size:>10}  <zip> {args.out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
