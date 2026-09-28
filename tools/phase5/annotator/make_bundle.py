"""Build ``annotator_bundle.zip`` for an isolated annotation workspace (P5-T).

Usage (run by the method owner in the repository)::

    python tools/phase5/annotator/make_bundle.py --out annotator_bundle.zip
    python tools/phase5/annotator/make_bundle.py --out annotator_bundle.zip \
        --title-list TITLE_EQUIVALENCE_v0.md --title-list-sha256 <hex>

The bundle contains ONLY the files in ``BUNDLE_SOURCES``, an empty ``records/``
folder, and a ``BUNDLE_MANIFEST.json``. Without ``--title-list``/``--title-list-sha256``
it also carries a placeholder saying the title list is not yet frozen, and the manifest
records ``title_list_sha256: null``; each annotator's ASSIGNMENT.csv is added later by
the custodian. With both title-list arguments (refused unless the hash matches), the
bundle instead ships the accepted title list as ``TITLE_EQUIVALENCE_v0.md`` and the
manifest records its hash, which the annotator tool's seal guard re-checks before
sealing any record. Prints the manifest (path, bytes, sha256). The zip is deterministic
(fixed timestamps, sorted entries).
"""

from __future__ import annotations

import argparse
import hashlib
import json
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
    "gold_schema_v0_4.json": REPO_ROOT / "docs" / "phase5" / "gold_schema_v0_4.json",
    "GOLD_PROTOCOL_v0_4.md": REPO_ROOT / "docs" / "phase5" / "GOLD_PROTOCOL_v0_4.md",
}
PLACEHOLDER_NAME = "TITLE_LIST_NOT_YET_FROZEN.txt"
PLACEHOLDER_TEXT = (
    "The annotator-facing MD&A title list is not frozen yet.\n"
    "Do not start annotating. The custodian replaces this file with the accepted\n"
    "title list after the author freezes it (GOLD_PROTOCOL v0.4 section 6).\n"
)
# Title-list seal guard (annotator_core._assert_title_list_frozen): the accepted title
# list ships under this name, with BUNDLE_MANIFEST.json recording its sha256 so a later
# edit to the list is caught before sealing.
TITLE_LIST_NAME = "TITLE_EQUIVALENCE_v0.md"
MANIFEST_NAME = "BUNDLE_MANIFEST.json"
RECORDS_DIR_ENTRY = "records/"


def expected_entries(*, with_title_list: bool = False) -> list[str]:
    names = [*BUNDLE_SOURCES, MANIFEST_NAME, RECORDS_DIR_ENTRY]
    names.append(TITLE_LIST_NAME if with_title_list else PLACEHOLDER_NAME)
    return sorted(f"{ROOT}/{name}" for name in names)


def build_bundle(
    out_zip: Path,
    *,
    title_list: Path | None = None,
    title_list_sha256: str | None = None,
) -> list[tuple[str, int, str]]:
    """Build the bundle.

    With neither title-list argument: today's placeholder-only bundle, plus a
    BUNDLE_MANIFEST.json recording ``title_list_sha256: null``. With both: refuses
    unless ``sha256(title_list) == title_list_sha256``, then ships ``title_list`` as
    TITLE_EQUIVALENCE_v0.md (no placeholder) and records its hash in
    BUNDLE_MANIFEST.json. The zip stays deterministic either way.
    """
    out_zip = Path(out_zip)
    if out_zip.exists():
        raise FileExistsError(f"refusing to overwrite {out_zip}")
    if (title_list is None) != (title_list_sha256 is None):
        raise ValueError("--title-list and --title-list-sha256 must be given together")
    payload: dict[str, bytes] = {}
    for name, source in BUNDLE_SOURCES.items():
        payload[name] = source.read_bytes()
    if title_list is None:
        payload[PLACEHOLDER_NAME] = PLACEHOLDER_TEXT.encode("utf-8")
        manifest_title_sha256 = None
    else:
        data = Path(title_list).read_bytes()
        actual = hashlib.sha256(data).hexdigest()
        if actual != title_list_sha256:
            raise ValueError(
                f"--title-list-sha256 {title_list_sha256} does not match the sha256 of "
                f"{title_list} ({actual})"
            )
        payload[TITLE_LIST_NAME] = data
        manifest_title_sha256 = title_list_sha256
    manifest_obj = {
        "bundle_format": 1,
        "title_list_sha256": manifest_title_sha256,
        "files": {name: hashlib.sha256(data).hexdigest() for name, data in payload.items()},
    }
    payload[MANIFEST_NAME] = (
        json.dumps(manifest_obj, sort_keys=True, indent=2, ensure_ascii=True) + "\n"
    ).encode("utf-8")
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
    parser.add_argument("--title-list", type=Path, help="accepted TITLE_EQUIVALENCE_v0.md to ship, sealed by --title-list-sha256")
    parser.add_argument("--title-list-sha256", help="sha256 of --title-list; both or neither must be given")
    args = parser.parse_args(argv)
    manifest = build_bundle(
        args.out, title_list=args.title_list, title_list_sha256=args.title_list_sha256
    )
    for arc, size, digest in manifest:
        print(f"{digest:<64}  {size:>9}  {arc}")
    data = args.out.read_bytes()
    print(f"{hashlib.sha256(data).hexdigest():<64}  {len(data):>9}  <zip> {args.out.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
