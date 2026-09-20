"""Final T0.4 closure audit; reads committed metadata only and executes nothing."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.t0_4.closure import run_closure_audit
from tools.t0_4.core import canonical_json, write_canonical_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--audited-commit",
        default="HEAD",
        help="Commit whose committed tree is audited (default: HEAD).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/t0_4/final_closure_audit.json"),
        help="Repository-relative deterministic audit record.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Recompute and compare with the existing record instead of writing it.",
    )
    args = parser.parse_args()
    report = run_closure_audit(REPO_ROOT, args.audited_commit)
    destination = REPO_ROOT / args.output
    if args.check:
        if not destination.is_file() or destination.read_text(encoding="utf-8") != canonical_json(report):
            print("T0.4 closure audit: recorded audit differs from recomputation")
            return 1
    else:
        write_canonical_json(destination, report)
    for name in ("vector_text_route", "sampling_cell_inspection", "sampling_metadata_provenance", "held_out_terminology"):
        print(f"{name}: {report[name]}")
    print(f"closure_decision: {report['closure_decision']}")
    print(f"final_commit_before_audit: {report['final_commit_before_audit']}")
    print(f"final_commit_after_audit: {report['final_commit_after_audit']}")
    print("No benchmark execution, PDF acquisition or rendering, OCR invocation, or API call occurred.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
