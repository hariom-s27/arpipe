"""Custodian builder for the deliberately small offline annotator ZIP."""

from __future__ import annotations

import hashlib
import sys
import zipfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[2]
TOOL_FILES = ("app.py", "core.py", "export_role.py")
OTHER_FILES = {
    "gold_schema_v0_1.json": REPOSITORY / "docs/phase5/gold_schema_v0_1.json",
    "GOLD_PROTOCOL_v0_1.md": REPOSITORY / "docs/phase5/GOLD_PROTOCOL_v0_1.md",
    "README.md": HERE / "README.md",
    "TITLE_LIST_NOT_YET_FROZEN.txt": HERE / "TITLE_LIST_NOT_YET_FROZEN.txt",
}
MEMBERS = tuple(sorted((*TOOL_FILES, *OTHER_FILES))) + ("records/",)


def build_bundle(output: Path) -> list[tuple[str, int, str]]:
    sources = {name: HERE / name for name in TOOL_FILES} | OTHER_FILES
    output = Path(output)
    manifest = []
    with zipfile.ZipFile(output, mode="x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in MEMBERS:
            data = b"" if name == "records/" else sources[name].read_bytes()
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if name.endswith("/") else 0o644) << 16
            archive.writestr(info, data)
            manifest.append((name, len(data), hashlib.sha256(data).hexdigest()))
    return manifest


def main() -> None:
    output = Path(sys.argv[1]) if len(sys.argv) == 2 else HERE / "annotator_bundle.zip"
    for path, size, digest in build_bundle(output):
        print(f"{path}\t{size}\t{digest}")


if __name__ == "__main__":
    main()
