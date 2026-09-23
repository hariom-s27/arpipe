#!/usr/bin/env python3
"""Verify SHA-256 hash claims recorded in Phase 2.1 docs against actual Git blobs.

Scans ``docs/experiments/PHASE2.1_*.md`` for markdown tables that carry a
"Verified Git SHA-256" column alongside "Source commit" and "Source path"
columns (the format PHASE2.1_PROVENANCE_CORRECTIONS.md Section 3 introduced
for PC-06), recomputes each cited blob's SHA-256 via ``git cat-file blob``,
and fails if any row's recorded hash does not match the recomputed value
unless the row is listed in the allowlist.

This guards against the exact error class PC-05/PC-06 corrected: a hash
printed in a frozen doc silently drifting from the Git blob it cites.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_GLOB = "docs/experiments/PHASE2.1_*.md"
DEFAULT_ALLOWLIST = Path(__file__).resolve().parent / "check_doc_hashes_allowlist.json"

HEX40_RE = re.compile(r"^[0-9a-fA-F]{40}$")
HEX64_RE = re.compile(r"^[0-9a-fA-F]{64}$")

HASH_COL_MARKERS = ("verified git sha-256",)
COMMIT_COL_MARKERS = ("source commit",)
PATH_COL_MARKERS = ("source path",)


class HashRow:
    def __init__(self, doc, line_no, artifact_path, source_commit, source_path, recorded_hash):
        self.doc = doc
        self.line_no = line_no
        self.artifact_path = artifact_path
        self.source_commit = source_commit
        self.source_path = source_path
        self.recorded_hash = recorded_hash

    def key(self):
        return f"{self.doc}::{self.source_commit}::{self.source_path}"


def _split_row(line):
    """Split a markdown table row into stripped cells, dropping the outer empties."""
    cells = line.strip().split("|")
    if cells and cells[0].strip() == "":
        cells = cells[1:]
    if cells and cells[-1].strip() == "":
        cells = cells[:-1]
    return [c.strip() for c in cells]


def _clean_cell(cell):
    return cell.strip().strip("`").strip()


def _find_col(headers, markers):
    for idx, header in enumerate(headers):
        low = header.lower()
        if any(marker in low for marker in markers):
            return idx
    return None


def _is_separator_row(cells):
    stripped = [c.strip() for c in cells if c.strip()]
    return bool(stripped) and all(re.fullmatch(r":?-{2,}:?", c) for c in stripped)


def extract_hash_rows(doc_path, repo_root=REPO_ROOT):
    """Parse `doc_path` for tables carrying Verified Git SHA-256 / Source commit / Source path columns."""
    rows = []
    lines = doc_path.read_text(encoding="utf-8").splitlines()
    n = len(lines)
    doc_rel = str(doc_path.relative_to(repo_root)).replace("\\", "/")
    i = 0
    while i < n:
        line = lines[i]
        if "|" not in line:
            i += 1
            continue
        headers = _split_row(line)
        hash_idx = _find_col(headers, HASH_COL_MARKERS)
        commit_idx = _find_col(headers, COMMIT_COL_MARKERS)
        path_idx = _find_col(headers, PATH_COL_MARKERS)
        if hash_idx is None or commit_idx is None or path_idx is None:
            i += 1
            continue

        j = i + 1
        if j < n and "|" in lines[j] and _is_separator_row(_split_row(lines[j])):
            j += 1
        while j < n and lines[j].strip().startswith("|"):
            cells = _split_row(lines[j])
            if len(cells) > max(hash_idx, commit_idx, path_idx):
                commit = _clean_cell(cells[commit_idx])
                source_path = _clean_cell(cells[path_idx])
                recorded_hash = _clean_cell(cells[hash_idx])
                if HEX40_RE.match(commit) and HEX64_RE.match(recorded_hash) and source_path:
                    rows.append(HashRow(
                        doc=doc_rel,
                        line_no=j + 1,
                        artifact_path=_clean_cell(cells[0]),
                        source_commit=commit,
                        source_path=source_path,
                        recorded_hash=recorded_hash.lower(),
                    ))
            j += 1
        i = j
    return rows


def git_blob_sha256(commit, path, repo_root):
    """Return the SHA-256 of the exact Git blob bytes at commit:path (binary-safe)."""
    result = subprocess.run(
        ["git", "-C", str(repo_root), "cat-file", "blob", f"{commit}:{path}"],
        capture_output=True,
        check=True,
    )
    return hashlib.sha256(result.stdout).hexdigest()


def load_allowlist(path):
    if not path.exists():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        f"{entry['doc']}::{entry['source_commit']}::{entry['source_path']}"
        for entry in data.get("exceptions", [])
    }


def check_docs(repo_root=REPO_ROOT, allowlist_path=DEFAULT_ALLOWLIST):
    allowlist = load_allowlist(allowlist_path)
    results = []
    for doc_path in sorted(repo_root.glob(DOCS_GLOB)):
        for row in extract_hash_rows(doc_path, repo_root):
            try:
                actual = git_blob_sha256(row.source_commit, row.source_path, repo_root)
                error = None
            except subprocess.CalledProcessError as exc:
                actual = None
                error = exc.stderr.decode("utf-8", "replace").strip()
            results.append({
                "row": row,
                "actual": actual,
                "error": error,
                "ok": actual == row.recorded_hash,
                "allowed": row.key() in allowlist,
            })
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--allowlist", type=Path, default=DEFAULT_ALLOWLIST)
    args = parser.parse_args(argv)

    results = check_docs(repo_root=args.repo_root, allowlist_path=args.allowlist)
    failures = [r for r in results if not r["ok"] and not r["allowed"]]

    for r in results:
        row = r["row"]
        if r["ok"]:
            status = "PASS"
        elif r["allowed"]:
            status = "ALLOWED-FAIL"
        else:
            status = "FAIL"
        detail = f"ERROR: {r['error']}" if r["error"] else f"actual={r['actual'][:12]}"
        print(f"[{status}] {row.doc}:{row.line_no} {row.source_path}@{row.source_commit[:7]} "
              f"recorded={row.recorded_hash[:12]} {detail}")

    docs_touched = len({r["row"].doc for r in results})
    print(f"\nChecked {len(results)} hash claim(s) across {docs_touched} doc(s); "
          f"{len(failures)} unallowed failure(s).")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
