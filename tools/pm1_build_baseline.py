"""PM1 M1.1: freeze reports/pm1_baseline.json from a completed extraction run
over the pre-PM1 code. Refuses to overwrite an existing baseline (immutable
per M1.1 - "Do not regenerate or overwrite it after implementation").

Usage (from arpipe-0.1.0/):
    PYTHONPATH=. arpipe/.venv/Scripts/python.exe tools/pm1_build_baseline.py
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUN_DIR = REPO / "pm1_baseline_run"
OUT = REPO / "reports" / "pm1_baseline.json"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True,
                          text=True, check=True).stdout.strip()


def main() -> int:
    if OUT.exists():
        print(f"REFUSING: {OUT} already exists and is immutable per M1.1.")
        return 2

    rows = [json.loads(l) for l in open(RUN_DIR / "manifest.jsonl", encoding="utf-8")
           if l.strip()]
    assert len({(r["company_id"], r["fy_end"]) for r in rows}) == len(rows) == 194, (
        f"expected exactly 194 unique documents, got {len(rows)} rows / "
        f"{len({(r['company_id'], r['fy_end']) for r in rows})} unique keys")

    documents = []
    for r in sorted(rows, key=lambda r: (r["company_id"], r["fy_end"])):
        span = r.get("span") or {}
        qc = r.get("qc") or {}
        documents.append({
            "document_id": f"{r['company_id']}_{r['fy_end']}",
            "company_id": r["company_id"],
            "fiscal_year": r["fy_end"],
            "sha256": r["sha256"],
            "orphan_start_frac": qc.get("orphan_start_frac"),
            "grade": r.get("confidence"),
            "confidence": r.get("confidence"),
            "failure_reasons": r.get("reasons", []),
            "mda_start_page": span.get("start_page"),
            "mda_end_page": span.get("end_page"),
            "accepted_or_rejected": "accepted" if r.get("ok") else "rejected",
        })

    status_lines = git("status", "--porcelain").splitlines()
    header = {
        "task": "PM1 M1.1 - immutable pre-implementation baseline",
        "git_sha": git("rev-parse", "HEAD"),
        "git_worktree_dirty": bool(status_lines),
        "git_status_porcelain": status_lines,
        "note_on_git_state": (
            "The working tree already carried substantial uncommitted work "
            "(P34 wrong-language quarantine, P-B7 state.py, script-map "
            "telemetry, etc.) before PM1 started, on top of commit "
            "0fb8cbf (P33). This baseline was captured from that exact "
            "pre-PM1 state: PM1's own edits to verify.py/textlayer.py/"
            "pipeline.py/cli.py were reversed (restoring the four files to "
            "their pre-PM1 content byte-for-byte, verified by re-running the "
            "full test suite and by grep for PM1-only symbols returning "
            "nothing) immediately before this run, then reapplied afterward."
        ),
        "corpus_source": "live_store/documents.jsonl",
        "corpus_sha256": sha256_file(REPO / "live_store" / "documents.jsonl"),
        "corpus_document_count": len(rows),
        "companies_file": "cohort_companies.csv",
        "companies_file_sha256": sha256_file(REPO / "cohort_companies.csv"),
        "extraction_tool": "tools/pm1_run_corpus.py",
        "extraction_tool_sha256": sha256_file(REPO / "tools" / "pm1_run_corpus.py"),
        "extraction_config": {"root": "live_store", "workers": 1,
                              "escalator": ["tesseract"],
                              "ARPIPE_OCR_WORKERS": "1"},
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "grade_distribution": {g: sum(1 for d in documents if d["grade"] == g)
                               for g in sorted({d["grade"] for d in documents})},
        "accepted_count": sum(1 for d in documents if d["accepted_or_rejected"] == "accepted"),
        "rejected_count": sum(1 for d in documents if d["accepted_or_rejected"] == "rejected"),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({**header, "documents": documents}, fh, indent=2)
    print(f"wrote {OUT} ({len(documents)} documents) sha256={sha256_file(OUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
