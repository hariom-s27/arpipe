"""PM1: run the UNMODIFIED production extraction path over the authoritative
194-document live_store corpus, with process-level parallelism.

`arpipe extract`'s own ThreadPoolExecutor serializes almost entirely on the
GIL for this workload (segment/verify/textlayer are regex- and pure-Python-
heavy) - far too slow for a 194-document run. This script calls exactly the
same `pipeline.process_document` production entry point cmd_extract calls,
with the identical configuration convention pb2_phase1_baseline.py uses
(STORE_ROOT="live_store", cohort_companies.csv, ARPIPE_OCR_WORKERS=1,
Tesseract-only escalator), just distributed across worker PROCESSES instead
of threads. Nothing about extraction, segmentation, verification, grading or
OCR routing is touched here - this is a measurement/orchestration script only.

Manifest rows are appended from the main process ONLY (worker processes
return records, never write the shared manifest.jsonl themselves), so
concurrent writers can never interleave or duplicate a line.

Usage (from arpipe-0.1.0/):
    PYTHONPATH=. arpipe/.venv/Scripts/python.exe tools/pm1_run_corpus.py --out pm1_baseline_run
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STORE_ROOT = "live_store"
COMPANIES = REPO / "cohort_companies.csv"
RUN_ENV = {"ARPIPE_OCR_WORKERS": "1"}

_COMPANIES: dict = {}


def _worker_init(out_root: str) -> None:
    os.environ.update(RUN_ENV)
    os.chdir(REPO)
    sys.path.insert(0, str(REPO))
    from arpipe import config, universe

    cfg = config.load_config(cli_overrides={"root": STORE_ROOT, "out": out_root, "workers": 1})
    config.set_active_config(cfg)
    comps = {}
    for c in universe.from_csv(str(COMPANIES)):
        comps[c.company_id] = c
        if c.isin:
            comps[c.isin] = c
        for alt in c.alternate_isins:
            comps[alt] = c
    global _COMPANIES
    _COMPANIES = comps


def run_one(doc_row: dict, out_root: str, keep_pages: bool) -> dict:
    from arpipe import ocr as ocr_mod
    from arpipe import pipeline
    from arpipe.models import Confidence, StoredDoc, to_json

    doc = StoredDoc(**doc_row)
    co = _COMPANIES.get(doc.company_id)
    if co is None:
        return {"company_id": doc.company_id, "fy_end": doc.fy_end,
               "sha256": doc.sha256, "ok": False, "confidence": "failed",
               "errors": ["company_not_in_companies_file"], "reasons": ["crash"],
               "qc": {}}
    try:
        res = pipeline.process_document(
            doc, co, out_root,
            escalator=ocr_mod.Escalator([ocr_mod.TesseractBackend()]),
            keep_pages=keep_pages, store_root=STORE_ROOT)
    except Exception as exc:                              # noqa: BLE001
        import traceback
        tb = traceback.format_exc()
        print(f"CRASH {doc.company_id} {doc.fy_end}: {type(exc).__name__}: {exc}\n{tb}",
             file=sys.stderr)
        res = pipeline.ExtractionResult(
            company_id=doc.company_id, fy_end=doc.fy_end, sha256=doc.sha256,
            ok=False, confidence=Confidence.FAILED,
            pipeline_version=pipeline.PIPELINE_VERSION)
        res.errors.append(f"crash:{type(exc).__name__}:{exc}")
        res.reasons = ["crash"]
    rec = json.loads(to_json(res))
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="Output dataset root, relative to arpipe-0.1.0/")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--keep-pages", action="store_true")
    a = ap.parse_args()

    os.chdir(REPO)
    sys.path.insert(0, str(REPO))
    from arpipe import config, store

    docs = [json.loads(l) for l in open(os.path.join(STORE_ROOT, "documents.jsonl"),
                                        encoding="utf-8") if l.strip()]
    already = store.done_keys(a.out) if os.path.exists(a.out) else set()
    todo = [d for d in docs if (d["company_id"], d["fy_end"]) not in already]
    print(f"{len(todo)} documents to process ({len(docs) - len(todo)} already done), "
         f"{a.workers} worker processes", flush=True)

    t0 = time.time()
    n_ok = 0
    with ProcessPoolExecutor(max_workers=a.workers, initializer=_worker_init,
                             initargs=(a.out,)) as ex:
        futs = {ex.submit(run_one, d, a.out, a.keep_pages): d for d in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            rec = fut.result()
            rec["run_config"] = config.config_for_manifest()
            store.append_manifest(a.out, rec)
            n_ok += int(bool(rec.get("ok")))
            if i % 10 == 0 or i == len(todo):
                print(f"  [{i}/{len(todo)}] {round(time.time() - t0, 1)}s elapsed", flush=True)

    print(f"extracted ok={n_ok}/{len(todo)} in {round(time.time() - t0, 1)}s")
    store.snapshot_parquet(a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
