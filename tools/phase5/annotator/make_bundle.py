"""Build ``annotator_bundle.zip`` for an isolated annotation workspace (P5-T).

Usage (run by the method owner in the repository)::

    python tools/phase5/annotator/make_bundle.py --out annotator_bundle.zip

The bundle contains ONLY the files in ``BUNDLE_SOURCES``, an empty ``records/``
folder and a placeholder saying the title list is not yet frozen. The accepted
annotator-facing title list and each annotator's ASSIGNMENT.csv are added later by
the custodian, after the author freezes the list. Prints the manifest
(path, bytes, sha256). The zip is deterministic (fixed timestamps, sorted entries).
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)
ROOT = "annotator_bundle"

# bundle path -> repository source path
BUNDLE_SOURCES = {
    "annotator_core.py": HERE / "annotator_core.py",
    "annotator_app.py": HERE / "annotator_app.py",
    "export_role.py": HERE / "export_role.py",
    "README.md": HERE / "BUNDLE_README.md",
    "gold_schema_v0_2.json": REPO_ROOT / "docs" / "phase5" / "gold_schema_v0_2.json",
    "GOLD_PROTOCOL_v0_2.md": REPO_ROOT / "docs" / "phase5" / "GOLD_PROTOCOL_v0_2.md",
}
PLACEHOLDER_NAME = "TITLE_LIST_NOT_YET_FROZEN.txt"
PLACEHOLDER_TEXT = (
    "The annotator-facing MD&A title list is not frozen yet.\n"
    "Do not start annotating. The custodian replaces this file with the accepted\n"
    "title list after the author freezes it (GOLD_PROTOCOL v0.1 section 6).\n"
)
RECORDS_DIR_ENTRY = "records/"


def expected_entries() -> list[str]:
    names = [*BUNDLE_SOURCES, PLACEHOLDER_NAME, RECORDS_DIR_ENTRY]
    return sorted(f"{ROOT}/{name}" for name in names)


def build_bundle(out_zip: Path) -> list[tuple[str, int, str]]:
    out_zip = Path(out_zip)
    if out_zip.exists():
        raise FileExistsError(f"refusing to overwrite {out_zip}")
    payload: dict[str, bytes] = {}
    for name, source in BUNDLE_SOURCES.items():
        payload[name] = source.read_bytes()
    payload[PLACEHOLDER_NAME] = PLACEHOLDER_TEXT.encode("utf-8")
    manifest: list[tuple[str, int, str]] = []
    with zipfile.ZipFile(out_zip, "x", compression=zipfile.ZIP_DEFLATED) as zf:
        entries = sorted([*payload, RECORDS_DIR_ENTRY])
        for name in entries:
            arc = f"{ROOT}/{name}"
            if name == RECORDS_DIR_ENTRY:
                info = zipfile.ZipInfo(arc, date_time=FIXED_ZIP_TIME)
                info.external_attr = (0o40755 << 16) | 0x10
                zf.writestr(info, b"")
                manifest.append((arc, 0, "-"))
                continue
            data = payload[name]
            info = zipfile.ZipInfo(arc, date_time=FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, data)
            manifest.append((arc, len(data), hashlib.sha256(data).hexdigest()))
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the offline annotator bundle.")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    manifest = build_bundle(args.out)
    for arc, size, digest in manifest:
        print(f"{digest:<64}  {size:>9}  {arc}")
    data = args.out.read_bytes()
    print(f"{hashlib.sha256(data).hexdigest():<64}  {len(data):>9}  <zip> {args.out.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
