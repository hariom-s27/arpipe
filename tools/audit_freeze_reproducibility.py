"""T0 audit: re-run freeze_extraction_corpus.py and verify every invariant
section 33 of the T0 brief requires, rather than relying on one-off shell
commands. Exits non-zero (and prints exactly what failed) if any check fails.

Usage:
    <venv>/python tools/audit_freeze_reproducibility.py --seed 20260918
"""
from __future__ import annotations

import argparse
import csv
import filecmp
import json
import os
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FREEZE_TOOL = os.path.join(REPO_ROOT, "tools", "freeze_extraction_corpus.py")


def run_freeze(out_dir: str, seed: int) -> None:
    subprocess.run(
        [sys.executable, FREEZE_TOOL, "--seed", str(seed), "--out-dir", out_dir],
        check=True, cwd=REPO_ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def read_ids(csv_path: str) -> set[str]:
    with open(csv_path, encoding="utf-8", newline="") as f:
        return {row["document_id"] for row in csv.DictReader(f)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260918)
    args = ap.parse_args()

    failures: list[str] = []

    with tempfile.TemporaryDirectory() as tmp:
        out_a = os.path.join(tmp, "run_a")
        out_b = os.path.join(tmp, "run_b")
        print(f"running freeze twice with seed={args.seed} ...", file=sys.stderr)
        run_freeze(out_a, args.seed)
        run_freeze(out_b, args.seed)

        cmp = filecmp.dircmp(out_a, out_b)
        if cmp.left_only or cmp.right_only or cmp.diff_files:
            failures.append(
                f"non-identical reruns: only_in_a={cmp.left_only} only_in_b={cmp.right_only} "
                f"differing={cmp.diff_files}"
            )
        hashes_a = filecmp.dircmp(os.path.join(out_a, "hashes"), os.path.join(out_b, "hashes"))
        if hashes_a.diff_files:
            failures.append(f"non-identical hash files: {hashes_a.diff_files}")

        with open(os.path.join(out_a, "freeze_summary.json"), encoding="utf-8") as f:
            summary = json.load(f)
        if not all(summary["issuer_disjoint_check"].values()):
            failures.append(f"issuer split leakage: {summary['issuer_disjoint_check']}")
        if not all(summary["subset_checks"].values()):
            failures.append(f"subset relation violated: {summary['subset_checks']}")

        dev_ids = read_ids(os.path.join(out_a, "development_manifest.csv"))
        val_ids = read_ids(os.path.join(out_a, "validation_manifest.csv"))
        hold_ids = read_ids(os.path.join(out_a, "holdout_manifest.csv"))
        roster_ids = read_ids(os.path.join(out_a, "annotation_roster.csv"))
        if dev_ids & val_ids or dev_ids & hold_ids:
            failures.append("development set overlaps VALIDATION/HOLDOUT")
        if not roster_ids.issubset(dev_ids):
            failures.append("annotation_roster is not a subset of development")

        with open(os.path.join(out_a, "annotation_roster.csv"), encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                for gold_field in ("mda_present", "mda_start_page", "mda_end_page"):
                    if row[gold_field]:
                        failures.append(f"annotation_roster row {row['document_id']} has a non-blank "
                                        f"gold field {gold_field}={row[gold_field]!r} -- T0 must not "
                                        f"create new gold labels")

    if failures:
        print("FAIL:", file=sys.stderr)
        for f_ in failures:
            print(f"  - {f_}", file=sys.stderr)
        return 1
    print("PASS: freeze is reproducible, issuer-disjoint, subset-consistent, and gold-label-free.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
