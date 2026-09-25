"""Output layout and manifests.

Two layers, on purpose:

  blobs/          content-addressed PDFs (sha256). Deduplicated, immutable,
                  and the only place bytes are stored.
  Company/<FY>/   the human-facing tree the brief asks for. `annual_report.pdf`
                  is a hardlink (or symlink) into blobs/, so the tree costs
                  nothing extra and can be rebuilt from the manifest at will.

Alongside every mda.txt we write mda.json: the span, the method that found
it, the verification report and the QC metrics. A text file with no
provenance is not a dataset - the moment somebody asks "is this really
FY2013 and really this company?" you need the answer on disk.

The manifest is JSONL (append-only, greppable, crash-safe) with a Parquet
snapshot built on demand for analysis.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
from dataclasses import asdict

from .models import ExtractionResult, StoredDoc, to_json

SAFE = re.compile(r"[^A-Za-z0-9._-]+")


def rel_to_root(path: str, root: str) -> str:
    """A path expressed relative to `root`, forward slashes, so it stays valid
    when the tree is moved to another directory or drive."""
    return os.path.relpath(path, root).replace(os.sep, "/")


def blob_abspath(root: str, stored_path: str) -> str:
    """Resolve a StoredDoc.path to an absolute filesystem path.

    The current format is root-relative with forward slashes
    (``blobs/47/74/<sha>.pdf``); this also tolerates the legacy formats still on
    disk: an absolute path, and a path written relative to the store's parent
    that carries the store dir's own name as a leading component
    (``live_store/blobs/...``)."""
    if os.path.isabs(stored_path):
        return stored_path
    p = stored_path.replace("\\", "/").lstrip("/")
    candidates = [os.path.join(root, p)]
    rootname = os.path.basename(os.path.normpath(root))
    if rootname and p.startswith(rootname + "/"):
        candidates.append(os.path.join(root, p[len(rootname) + 1:]))
    candidates.append(p)                          # last resort: relative to cwd
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    return os.path.abspath(candidates[0])


def slug(name: str, maxlen: int = 80) -> str:
    s = SAFE.sub("_", (name or "").strip()).strip("_")
    return (s[:maxlen] or "UNKNOWN").upper()


def company_dir(root: str, company_name: str, company_id: str) -> str:
    return os.path.join(root, "companies", f"{slug(company_name)}__{company_id}")


def year_dir(root: str, company_name: str, company_id: str, fy_end: int) -> str:
    return os.path.join(company_dir(root, company_name, company_id), str(fy_end))


def link_pdf(blob_path: str, dest: str) -> str:
    """Materialise `dest` from `blob_path` as cheaply as the filesystem allows,
    and report which mechanism was used.

      hardlink  free, but same volume only
      symlink   free across volumes, but needs privilege / Developer Mode on Windows
      copy      always works, costs a full second copy of the bytes

    A cross-drive `--out` makes os.path.relpath raise ValueError (not OSError),
    so the symlink branch has to catch both. If `dest` already exists from a
    prior run, the mode is re-derived from the inode / islink."""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.lexists(dest):                             # a prior run made it
        if os.path.islink(dest):
            return "symlink"
        try:
            a, b = os.stat(dest), os.stat(blob_path)
            same = a.st_ino != 0 and (a.st_ino, a.st_dev) == (b.st_ino, b.st_dev)
            return "hardlink" if same else "copy"
        except OSError:
            return "copy"
    try:
        os.link(blob_path, dest)                          # hardlink: no extra bytes
        return "hardlink"
    except OSError:
        pass
    try:
        rel = os.path.relpath(blob_path, os.path.dirname(dest))
        os.symlink(rel, dest)
        return "symlink"
    except (OSError, ValueError):
        pass
    shutil.copy2(blob_path, dest)
    print(f"WARN link_pdf: copied {os.path.basename(blob_path)} into the tree "
          f"(no hardlink/symlink available) -> {dest}", file=sys.stderr)
    return "copy"


def write_year(root: str, company_name: str, doc: StoredDoc,
               mda_text: str, result: ExtractionResult,
               page_texts: dict[int, str] | None = None,
               mda_blocks: list[dict] | None = None,
               blob_path: str | None = None,
               store_root: str | None = None,
               write_span: bool = True) -> str:
    d = year_dir(root, company_name, doc.company_id, doc.fy_end)
    os.makedirs(d, exist_ok=True)
    blob_path = blob_path or doc.path
    doc.link_mode = link_pdf(blob_path, os.path.join(d, "annual_report.pdf"))
    # Normalise doc.path in document.json to the current store-root-relative
    # form, so the record is portable even when documents.jsonl still holds a
    # legacy path. Skipped if the blob is on another drive from the store root.
    if store_root and os.path.isabs(blob_path):
        try:
            doc.path = rel_to_root(blob_path, store_root)
        except ValueError:
            pass
    # P34: a quarantined row (write_span=False, e.g. WRONG_LANGUAGE_RISK) does
    # not put its span text in the research corpus at all - mda.txt is not
    # created, and result.path stays null so mda.json cannot point at prose
    # that isn't there. mda.json / document.json are still written below with
    # the full diagnosis (rule 3: failures produce rows, never absences).
    if write_span:
        # mda.txt path, relative to the dataset root so the manifest and
        # mda.json stay valid if the tree is moved. Set BEFORE mda.json is
        # serialised.
        result.path = rel_to_root(os.path.join(d, "mda.txt"), root)
        with open(os.path.join(d, "mda.txt"), "w", encoding="utf-8") as fh:
            fh.write(mda_text)
    else:
        result.path = None
        stale = os.path.join(d, "mda.txt")
        if os.path.exists(stale):
            os.remove(stale)
    # P18: tables and charts lifted out of the prose. Always written (even
    # empty) so a downstream reader can tell "no tables" from "not processed".
    with open(os.path.join(d, "mda_blocks.json"), "w", encoding="utf-8") as fh:
        json.dump(mda_blocks or [], fh, ensure_ascii=False, indent=2)
    with open(os.path.join(d, "mda.json"), "w", encoding="utf-8") as fh:
        fh.write(to_json(result, indent=2))
    with open(os.path.join(d, "document.json"), "w", encoding="utf-8") as fh:
        fh.write(to_json(doc, indent=2))
    if page_texts:
        os.makedirs(os.path.join(d, "pages"), exist_ok=True)
        for n, t in page_texts.items():
            with open(os.path.join(d, "pages", f"{n:04d}.txt"), "w",
                      encoding="utf-8") as fh:
                fh.write(t)
    return d


def append_manifest(root: str, record: dict) -> None:
    os.makedirs(root, exist_ok=True)
    with open(os.path.join(root, "manifest.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_manifest(root: str) -> list[dict]:
    p = os.path.join(root, "manifest.jsonl")
    if not os.path.exists(p):
        return []
    out = []
    with open(p, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return out


def done_keys(root: str) -> set[tuple[str, int]]:
    """Resumability: (company_id, fy_end) pairs already completed."""
    return {(r["company_id"], r["fy_end"]) for r in load_manifest(root)
            if r.get("ok")}


def snapshot_parquet(root: str, out: str | None = None) -> str | None:
    try:
        import pandas as pd
    except ImportError:
        return None
    rows = load_manifest(root)
    if not rows:
        return None
    out = out or os.path.join(root, "manifest.parquet")
    # PyArrow cannot reliably infer a single schema for deeply nested audit
    # fields such as qc.diag.candidates, whose arrays intentionally contain
    # strings, integers and floats. Keep those fields lossless and portable
    # by storing them as JSON strings in the analytical snapshot. The JSONL
    # manifest remains the canonical nested representation.
    flat_rows = [
        {
            key: (json.dumps(value, ensure_ascii=False, sort_keys=True)
                  if isinstance(value, (dict, list, tuple)) else value)
            for key, value in row.items()
        }
        for row in rows
    ]
    pd.DataFrame(flat_rows).to_parquet(out, index=False)
    return out
