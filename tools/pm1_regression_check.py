"""PM1 M1.9: compare the after-PM1 extraction run against the frozen
reports/pm1_baseline.json. Every one of the 7 tracked fields must be
byte-identical for all 194 documents; any difference is a bug, not a result.

Usage (from arpipe-0.1.0/):
    PYTHONPATH=. arpipe/.venv/Scripts/python.exe tools/pm1_regression_check.py
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BASELINE = REPO / "reports" / "pm1_baseline.json"
AFTER_MANIFEST = REPO / "pm1_after_run" / "manifest.jsonl"
OUT = REPO / "reports" / "pm1_regression_result.json"

FIELDS = ["orphan_start_frac", "grade", "confidence", "failure_reasons",
         "mda_start_page", "mda_end_page", "accepted_or_rejected"]


def after_record(row: dict) -> dict:
    span = row.get("span") or {}
    qc = row.get("qc") or {}
    return {
        "orphan_start_frac": qc.get("orphan_start_frac"),
        "grade": row.get("confidence"),
        "confidence": row.get("confidence"),
        "failure_reasons": row.get("reasons", []),
        "mda_start_page": span.get("start_page"),
        "mda_end_page": span.get("end_page"),
        "accepted_or_rejected": "accepted" if row.get("ok") else "rejected",
    }


def main() -> int:
    baseline = json.load(open(BASELINE, encoding="utf-8"))
    after_rows = [json.loads(l) for l in open(AFTER_MANIFEST, encoding="utf-8") if l.strip()]
    after_by_id = {f"{r['company_id']}_{r['fy_end']}": after_record(r) for r in after_rows}

    base_by_id = {d["document_id"]: d for d in baseline["documents"]}
    assert set(base_by_id) == set(after_by_id), (
        f"document set differs: baseline has {len(base_by_id)}, after has "
        f"{len(after_by_id)}; symmetric diff = "
        f"{set(base_by_id) ^ set(after_by_id)}")

    per_field_changes = {f: 0 for f in FIELDS}
    diffs = []
    for doc_id, base in base_by_id.items():
        after = after_by_id[doc_id]
        row_diffs = {}
        for f in FIELDS:
            if base[f] != after[f]:
                per_field_changes[f] += 1
                row_diffs[f] = {"baseline": base[f], "after": after[f]}
        if row_diffs:
            diffs.append({"document_id": doc_id, "diffs": row_diffs})

    result = {
        "documents_compared": len(base_by_id),
        "orphan_document_score_changes": per_field_changes["orphan_start_frac"],
        "grade_changes": per_field_changes["grade"],
        "confidence_changes": per_field_changes["confidence"],
        "reason_changes": per_field_changes["failure_reasons"],
        "span_start_changes": per_field_changes["mda_start_page"],
        "span_end_changes": per_field_changes["mda_end_page"],
        "accept_reject_changes": per_field_changes["accepted_or_rejected"],
        "total_documents_with_any_diff": len(diffs),
        "diffs": diffs,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)

    print(json.dumps({k: v for k, v in result.items() if k != "diffs"}, indent=2))
    if diffs:
        print(f"\n!!! {len(diffs)} document(s) differ - see {OUT} for detail")
        for d in diffs[:10]:
            print(d)
    else:
        print("\nZero differences across all documents.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
