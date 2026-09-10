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
from dataclasses import asdict

from .models import ExtractionResult, StoredDoc, to_json

SAFE = re.compile(r"[^A-Za-z0-9._-]+")


def slug(name: str, maxlen: int = 80) -> str:
    s = SAFE.sub("_", (name or "").strip()).strip("_")
    return (s[:maxlen] or "UNKNOWN").upper()


def company_dir(root: str, company_name: str, company_id: str) -> str:
    return os.path.join(root, "companies", f"{slug(company_name)}__{company_id}")


def year_dir(root: str, company_name: str, company_id: str, fy_end: int) -> str:
    return os.path.join(company_dir(root, company_name, company_id), str(fy_end))


def link_pdf(blob_path: str, dest: str) -> None:
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.exists(dest):
        return
    try:
        os.link(blob_path, dest)             # hardlink: no extra bytes
    except OSError:
        try:
            os.symlink(os.path.relpath(blob_path, os.path.dirname(dest)), dest)
        except OSError:
            shutil.copy2(blob_path, dest)


def write_year(root: str, company_name: str, doc: StoredDoc,
               mda_text: str, result: ExtractionResult,
               page_texts: dict[int, str] | None = None,
               mda_blocks: list[dict] | None = None) -> str:
    d = year_dir(root, company_name, doc.company_id, doc.fy_end)
    os.makedirs(d, exist_ok=True)
    link_pdf(doc.path, os.path.join(d, "annual_report.pdf"))
    with open(os.path.join(d, "mda.txt"), "w", encoding="utf-8") as fh:
        fh.write(mda_text)
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
