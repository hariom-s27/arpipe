"""P6 check: TOC folio-to-physical offset solver confidence vs candidate page error.

Measures whether low offset confidence predicts high page error.
Gating rule: if offset confidence < 0.50, TOC arbitration score is cut hard,
preventing it from winning outright over body_score or heading signals.

Usage:
    cd arpipe-0.1.0/arpipe ; $env:PYTHONPATH=".."
    .venv/Scripts/python.exe ../tools/check_toc_offset.py
    .venv/Scripts/python.exe ../tools/check_toc_offset.py --root live_store --dataset live_dataset
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import pymupdf

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from arpipe import segment, store, textlayer, triage  # noqa: E402
from arpipe.models import PageKind                      # noqa: E402


def _load_reference_spans(dataset_dir: str) -> dict[tuple[str, int], tuple[int, int]]:
    spans: dict[tuple[str, int], tuple[int, int]] = {}
    pattern = os.path.join(dataset_dir, "companies", "*", "*", "mda.json")
    for p in glob.glob(pattern):
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            span = data.get("span")
            if span and span.get("start_page") is not None and span.get("end_page") is not None:
                spans[(data["company_id"], data["fy_end"])] = (span["start_page"], span["end_page"])
        except Exception:
            continue
    return spans


def main() -> int:
    ap = argparse.ArgumentParser(description="Measure TOC offset confidence vs page error")
    ap.add_argument("--root", default="live_store", help="Path to live_store directory")
    ap.add_argument("--dataset", default="live_dataset", help="Path to live_dataset directory")
    args = ap.parse_args()

    # Normalize paths
    store_root = args.root
    if not os.path.isabs(store_root) and not os.path.exists(store_root):
        cand = os.path.join("arpipe", store_root)
        if os.path.exists(cand):
            store_root = cand

    dataset_root = args.dataset
    if not os.path.isabs(dataset_root) and not os.path.exists(dataset_root):
        cand = os.path.join("arpipe", dataset_root)
        if os.path.exists(cand):
            dataset_root = cand

    doc_manifest = os.path.join(store_root, "documents.jsonl")
    if not os.path.exists(doc_manifest):
        print(f"Error: {doc_manifest} not found", file=sys.stderr)
        return 1

    with open(doc_manifest, "r", encoding="utf-8") as f:
        doc_rows = [json.loads(line) for line in f if line.strip()]

    ref_spans = _load_reference_spans(dataset_root)

    print("=" * 105)
    print(f"{'Company':<15} {'FY':<6} {'TOC Candidate':<15} {'Final Span':<12} {'Page Error':<12} {'Offset Conf':<13} {'Solved':<8} {'Method'}")
    print("=" * 105)

    records = []
    for doc_meta in doc_rows:
        cid = doc_meta["company_id"]
        fy = doc_meta["fy_end"]
        blob = store.blob_abspath(store_root, doc_meta["path"])
        if not os.path.exists(blob):
            continue

        pdf = pymupdf.open(blob)
        try:
            profile = triage.profile_document(blob)
            digital = [p.page_no for p in profile.pages if p.kind is PageKind.DIGITAL]
            page_texts = textlayer.extract_pages(blob, digital)

            toc_span, offset_info = segment.from_toc(pdf, page_texts, return_info=True)
            solved = offset_info.get("solved")
            conf = offset_info.get("confidence", 0.0)
            method = offset_info.get("method", "not_run")

            # Final span from dataset or fallback locate
            final_span = ref_spans.get((cid, fy))
            if final_span is None:
                span, _ = segment.locate(pdf, profile, page_texts)
                if span:
                    span = segment.trim_span(span, page_texts)
                    final_span = (span.start_page, span.end_page)

            if toc_span is not None:
                toc_range_str = f"{toc_span.start_page}-{toc_span.end_page}"
                if final_span is not None:
                    page_err = abs(toc_span.start_page - final_span[0])
                else:
                    page_err = None
            else:
                toc_range_str = "None"
                page_err = None

            final_span_str = f"{final_span[0]}-{final_span[1]}" if final_span else "None"
            page_err_str = str(page_err) if page_err is not None else "-"
            solved_str = str(solved) if solved is not None else "-"

            records.append({
                "cid": cid,
                "fy": fy,
                "toc_range": toc_range_str,
                "final_span": final_span_str,
                "page_error": page_err,
                "confidence": conf,
                "solved": solved,
                "method": method,
            })

            print(f"{cid:<15} {fy:<6} {toc_range_str:<15} {final_span_str:<12} {page_err_str:<12} {conf:<13.3f} {solved_str:<8} {method}")
        finally:
            pdf.close()

    print("=" * 105)
    print("\nDiagnostic Summary:")
    toc_runs = [r for r in records if r["page_error"] is not None]
    if toc_runs:
        low_conf = [r for r in toc_runs if r["confidence"] < segment.TOC_OFFSET_CONFIDENCE_THRESHOLD]
        high_conf = [r for r in toc_runs if r["confidence"] >= segment.TOC_OFFSET_CONFIDENCE_THRESHOLD]
        print(f"  * Total documents with TOC matches: {len(toc_runs)}")
        print(f"  * Gated (low confidence < {segment.TOC_OFFSET_CONFIDENCE_THRESHOLD}): {len(low_conf)}")
        for r in low_conf:
            print(f"      - {r['cid']} FY{r['fy']}: error={r['page_error']} pages, conf={r['confidence']:.3f}, solved={r['solved']} ({r['method']})")
        if high_conf:
            print(f"  * Ungated (high confidence >= {segment.TOC_OFFSET_CONFIDENCE_THRESHOLD}): {len(high_conf)}")
            for r in high_conf:
                print(f"      - {r['cid']} FY{r['fy']}: error={r['page_error']} pages, conf={r['confidence']:.3f}, solved={r['solved']}")
        print(f"\n[NOTE] Threshold {segment.TOC_OFFSET_CONFIDENCE_THRESHOLD} is provisional and must be re-fit on the labelled 300.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
