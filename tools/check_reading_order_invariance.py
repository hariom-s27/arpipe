"""P23 check: running-furniture removal does not depend on the reading-order sort.

`textlayer.strip_running_furniture` used to key on the first / last two *emitted*
lines of each page, so the reading-order sort chose which lines counted as
furniture - reordering moved KRBL's word count by -7 / +28 (see the P16B commit).
P23 moved furniture detection onto block geometry + repetition, before the sort.

This script re-runs `extract_prose_and_tables` on every document in the store
with the sort ON (xy_cut) and OFF (naive y0,x0), using the MD&A spans from a
reference run, and checks:

  * furniture_blocks_removed and furniture_strings are IDENTICAL either way
    (the P23 guarantee - furniture no longer tracks the sort), and
  * the prose word count moves by < 1% (any residual is the P18 table
    quarantine, which legitimately tracks reading order - a table's cells are
    contiguous only in the reading order).

    cd arpipe-0.1.0/arpipe ; $env:PYTHONPATH=".."
    .venv/Scripts/python.exe ../tools/check_reading_order_invariance.py
    .venv/Scripts/python.exe ../tools/check_reading_order_invariance.py --root live_store --ref _prior_runs/live_dataset_p22check

Exit code is non-zero if furniture differs on any document, or word count moves
by 1% or more.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from arpipe import store, textlayer, triage           # noqa: E402
from arpipe.models import PageKind                     # noqa: E402


def _wordcount(prose: list[str]) -> int:
    return len("\n\n".join(t for t in prose if t.strip()).split())


def _spans_from_ref(ref_root: str) -> dict[tuple[str, int], tuple[int, int]]:
    out: dict[tuple[str, int], tuple[int, int]] = {}
    for path in glob.glob(os.path.join(ref_root, "companies", "*", "*", "mda.json")):
        mj = json.load(open(path, encoding="utf-8"))
        span = mj.get("span") or {}
        if span.get("start_page") is None:
            continue
        out[(mj["company_id"], mj["fy_end"])] = (span["start_page"], span["end_page"])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="live_store", help="blob store")
    ap.add_argument("--ref", default="_prior_runs/live_dataset_p22check",
                    help="dataset dir to take MD&A spans from")
    a = ap.parse_args()

    spans = _spans_from_ref(a.ref)
    docs = [json.loads(l) for l in open(os.path.join(a.root, "documents.jsonl"))
            if l.strip()]

    print(f"{'company / fy':22s} {'words ON':>9s} {'words OFF':>9s} {'d%':>7s} "
          f"{'furn ON/OFF':>11s}  furniture identical?")
    print("-" * 90)
    bad = 0
    for d in sorted(docs, key=lambda d: (d["company_id"], d["fy_end"])):
        key = (d["company_id"], d["fy_end"])
        if key not in spans:
            print(f"{d['company_id']} {d['fy_end']}  -- no span in ref, skipped")
            continue
        blob = store.blob_abspath(a.root, d["path"])
        prof = triage.profile_document(blob)
        s, e = spans[key]
        span_pages = list(range(s, e + 1))
        digital = {n for n in span_pages
                   if n < len(prof.pages) and prof.pages[n].kind is PageKind.DIGITAL}
        non_digital = [n for n in span_pages if n not in digital]
        page_texts = textlayer.extract_pages(blob, non_digital) if non_digital else {}

        on_prose, _, on_diag = textlayer.extract_prose_and_tables(
            blob, span_pages, page_texts, digital, reading_order=True)
        off_prose, _, off_diag = textlayer.extract_prose_and_tables(
            blob, span_pages, page_texts, digital, reading_order=False)

        w_on, w_off = _wordcount(on_prose), _wordcount(off_prose)
        dpct = (w_off - w_on) / w_on * 100 if w_on else 0.0
        furn_same = (on_diag["furniture_blocks_removed"] == off_diag["furniture_blocks_removed"]
                     and on_diag["furniture_strings"] == off_diag["furniture_strings"])
        row_bad = (not furn_same) or abs(dpct) >= 1.0
        bad += row_bad
        label = f"{d['company_id']} {d['fy_end']}"
        print(f"{label:22s} {w_on:9d} {w_off:9d} {dpct:+7.2f} "
              f"{on_diag['furniture_blocks_removed']:5d}/{off_diag['furniture_blocks_removed']:<5d}  "
              f"{'yes' if furn_same else 'NO'}"
              f"{'' if not row_bad else '   <-- FAIL'}")

    print("-" * 90)
    print("PASS - furniture removal is sort-independent on every document; "
          "word count within 1%"
          if not bad else f"FAIL - {bad} document(s) out of tolerance")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
