"""Command line: arpipe <stage> ...

Stages are separate commands on purpose. At 40k+ documents you will re-run
`extract` a dozen times while `fetch` runs once; coupling them wastes days.

  arpipe universe   build/refresh the company master
  arpipe discover   company master -> report manifest (URLs, no downloads)
  arpipe fetch      manifest -> content-addressed PDF store
  arpipe triage     PDFs -> per-page routing decisions (cheap, no OCR)
  arpipe extract    PDFs -> Company/<FY>/mda.txt + mda.json
  arpipe audit      manifest -> coverage and quality report
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from . import discover, fetch, ocr, pipeline, store, triage, universe, verify
from .models import Company, ReportRef, StoredDoc, to_json


def _load_companies(path: str) -> list[Company]:
    return universe.from_csv(path)


def cmd_universe(a: argparse.Namespace) -> int:
    if getattr(a, "in_csv", None):
        collapsed, removed = universe.collapse_companies_file(a.in_csv, a.out)
        print(f"Rebuilt {a.out}: {len(collapsed)} companies ({removed} rows removed by DVR/duplicate collapse)")
        return 0

    import httpx
    with httpx.Client(headers=discover.NSE_HEADERS, timeout=60,
                      follow_redirects=True) as cl:
        cl.get(discover.NSE_HOME)
        nse = universe.parse_nse_equity_master(cl.get(universe.NSE_EQUITY_L).text)
        chains = universe.parse_symbol_changes(cl.get(universe.NSE_SYMBOL_CHANGE).text)
    bse = {}
    if getattr(a, "no_bse", False):
        pass
    elif a.bse_json and os.path.exists(a.bse_json):
        bse = universe.parse_bse_master(json.load(open(a.bse_json)))
    else:
        try:
            bse_rows = universe.fetch_bse_master()
            bse = universe.parse_bse_master(bse_rows)
            print(f"Fetched {len(bse_rows)} scrips ({len(bse)} distinct ISINs) from BSE master")
        except Exception as exc:
            print(f"Warning: Failed to fetch live BSE master: {exc}")

    companies = universe.build_master(nse, bse, chains)
    universe.to_csv(companies, a.out)
    bse_only = sum(1 for c in companies if c.exchange == "bse")
    nse_only = sum(1 for c in companies if c.exchange == "nse")
    both = sum(1 for c in companies if c.exchange == "both")
    print(f"{len(companies)} companies -> {a.out} ({bse_only} BSE-only, {nse_only} NSE-only, {both} both)")
    return 0


def cmd_discover(a: argparse.Namespace) -> int:
    import httpx
    companies = _load_companies(a.companies)
    if a.limit:
        companies = companies[: a.limit]
    years = range(a.from_year, a.to_year + 1)
    out = open(a.out, "w", encoding="utf-8")
    nse_cl = discover.nse_session()
    gen_cl = httpx.Client(timeout=30, follow_redirects=True)
    try:
        for i, c in enumerate(companies, 1):
            refs: list[ReportRef] = []
            refs += discover.discover_nse(c, nse_cl)
            if a.use_bse:
                refs += discover.discover_bse(c, gen_cl)
            if a.use_screener:
                refs += discover.discover_screener(c, gen_cl)
            by_year = discover.reconcile(refs, years)
            cov = discover.coverage_report(by_year, years)
            for y in sorted(by_year):
                for r in by_year[y]:
                    out.write(to_json(r) + "\n")
            if i % 25 == 0:
                print(f"[{i}/{len(companies)}] {c.canonical_name[:40]:40s} "
                      f"coverage={cov['coverage']:.2f}", file=sys.stderr)
    finally:
        out.close(); nse_cl.close(); gen_cl.close()
    print(f"manifest -> {a.out}")
    return 0


def cmd_fetch(a: argparse.Namespace) -> int:
    import httpx
    refs = [ReportRef(**json.loads(l)) for l in open(a.manifest) if l.strip()]
    limiter = fetch.HostLimiter(min_interval=a.min_interval)
    os.makedirs(a.root, exist_ok=True)
    done: set[tuple[str, int]] = set()
    if os.path.exists(os.path.join(a.root, "documents.jsonl")):
        for l in open(os.path.join(a.root, "documents.jsonl")):
            d = json.loads(l)
            done.add((d["company_id"], d["fy_end"]))
    out = open(os.path.join(a.root, "documents.jsonl"), "a", encoding="utf-8")
    cl = httpx.Client(headers={"User-Agent": discover.UA}, timeout=120,
                      follow_redirects=True)
    ok = err = skip = 0
    try:
        with ThreadPoolExecutor(a.workers) as ex:
            futs = {}
            for r in refs:
                if (r.company_id, r.fy_end) in done:
                    skip += 1
                    continue
                futs[ex.submit(fetch.fetch_one, r, a.root, cl, limiter)] = r
            for f in as_completed(futs):
                r = futs[f]
                try:
                    doc = f.result()
                except Exception as exc:              # noqa: BLE001
                    err += 1
                    print(f"ERR {r.company_id} {r.fy_end} {type(exc).__name__}",
                          file=sys.stderr)
                    continue
                if doc is None:
                    err += 1
                    continue
                out.write(to_json(doc) + "\n"); out.flush()
                ok += 1
    finally:
        out.close(); cl.close()
    print(f"fetched ok={ok} err={err} skipped={skip}")
    return 0


def cmd_triage(a: argparse.Namespace) -> int:
    docs = [StoredDoc(**json.loads(l))
            for l in open(os.path.join(a.root, "documents.jsonl")) if l.strip()]
    counts = {"digital": 0, "mixed": 0, "scanned": 0}
    pages_total = pages_ocr = 0
    with open(os.path.join(a.root, "profiles.jsonl"), "w", encoding="utf-8") as fh:
        for d in docs:
            try:
                p = triage.profile_document(store.blob_abspath(a.root, d.path))
            except Exception as exc:                  # noqa: BLE001
                print(f"ERR {d.sha256[:8]} {exc}", file=sys.stderr)
                continue
            counts[p.doc_kind] = counts.get(p.doc_kind, 0) + 1
            pages_total += p.n_pages
            pages_ocr += len(triage.ocr_page_numbers(p))
            fh.write(to_json(p) + "\n")
    print(json.dumps({"documents": counts, "pages": pages_total,
                      "pages_needing_ocr": pages_ocr,
                      "ocr_fraction": round(pages_ocr / max(1, pages_total), 4)},
                     indent=2))
    return 0


def _make_escalator(a: argparse.Namespace) -> ocr.Escalator:
    rungs: list[ocr.OcrBackend] = [ocr.TesseractBackend()]
    if a.vlm_url:
        rungs.append(ocr.VlmServerBackend(a.vlm_url, a.vlm_model))
    if a.textract:
        rungs.append(ocr.TextractBackend(region=a.aws_region))
    return ocr.Escalator(rungs)


def cmd_extract(a: argparse.Namespace) -> int:
    loaded = _load_companies(a.companies)
    companies: dict[str, Company] = {}
    for c in loaded:
        companies[c.company_id] = c
        if c.isin:
            companies[c.isin] = c
        for alt in c.alternate_isins:
            companies[alt] = c
    docs = [StoredDoc(**json.loads(l))
            for l in open(os.path.join(a.root, "documents.jsonl")) if l.strip()]
    already = store.done_keys(a.out) if a.resume else set()
    esc = _make_escalator(a)
    todo = [d for d in docs if (d.company_id, d.fy_end) not in already]
    print(f"{len(todo)} documents to process ({len(docs) - len(todo)} already done)")

    def work(d: StoredDoc):
        co = companies.get(d.company_id)
        if co is None:
            return d, None
        try:
            return d, pipeline.process_document(d, co, a.out, escalator=esc,
                                                keep_pages=a.keep_pages,
                                                store_root=a.root)
        except Exception as exc:
            import traceback
            tb = traceback.format_exc()
            print(f"CRASH {d.company_id} {d.fy_end}: {type(exc).__name__}: {exc}\n{tb}", file=sys.stderr)
            res = pipeline.ExtractionResult(
                company_id=d.company_id, fy_end=d.fy_end, sha256=d.sha256,
                ok=False, confidence=pipeline.Confidence.FAILED,
                pipeline_version=pipeline.PIPELINE_VERSION)
            res.errors.append(f"crash:{type(exc).__name__}:{exc}")
            res.reasons = ["crash"]
            return d, res

    n_ok = 0
    with ThreadPoolExecutor(a.workers) as ex:
        for d, res in ex.map(work, todo):
            if res is None:
                continue
            rec = json.loads(to_json(res))   # already carries "path" (rel to --out)
            store.append_manifest(a.out, rec)
            n_ok += int(res.ok)
    print(f"extracted ok={n_ok}/{len(todo)}")
    store.snapshot_parquet(a.out)
    return 0


def cmd_audit(a: argparse.Namespace) -> int:
    rows = store.load_manifest(a.out)
    if not rows:
        print("empty manifest"); return 1

    # Assert 1 row per sha256 in final manifest
    by_sha: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        sha = r.get("sha256")
        if sha:
            by_sha[sha].append(r)
    dup_shas = {sha: rlist for sha, rlist in by_sha.items() if len(rlist) > 1}
    if dup_shas:
        print(f"AUDIT ERROR: {len(dup_shas)} duplicate sha256 in manifest:", file=sys.stderr)
        for sha, rlist in dup_shas.items():
            for r in rlist:
                print(f"  sha256={sha} company_id={r.get('company_id')} fy_end={r.get('fy_end')} path={r.get('path')}", file=sys.stderr)

    # Assert 1 row per (cin, fy_end)
    by_cin_fy: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for r in rows:
        cin = r.get("cin") or (r.get("verification") or {}).get("cin_found")
        fy = r.get("fy_end")
        if cin and fy:
            by_cin_fy[(cin, fy)].append(r)
    dup_cin_fy = {k: rlist for k, rlist in by_cin_fy.items() if len(rlist) > 1}
    if dup_cin_fy:
        print(f"AUDIT ERROR: {len(dup_cin_fy)} duplicate (cin, fy_end) in manifest:", file=sys.stderr)
        for (cin, fy), rlist in dup_cin_fy.items():
            for r in rlist:
                print(f"  cin={cin} fy_end={fy} company_id={r.get('company_id')} sha256={r.get('sha256')} path={r.get('path')}", file=sys.stderr)

    assert not dup_shas, f"Found {len(dup_shas)} duplicate sha256 in manifest: {list(dup_shas.keys())}"
    assert not dup_cin_fy, f"Found {len(dup_cin_fy)} duplicate (cin, fy_end) in manifest: {list(dup_cin_fy.keys())}"

    by_conf: dict[str, int] = {}
    by_method: dict[str, int] = {}
    years: dict[int, int] = {}
    for r in rows:
        by_conf[r.get("confidence", "?")] = by_conf.get(r.get("confidence", "?"), 0) + 1
        m = (r.get("span") or {}).get("method", "none")
        by_method[m] = by_method.get(m, 0) + 1
        if r.get("ok"):
            years[r["fy_end"]] = years.get(r["fy_end"], 0) + 1
    print(json.dumps({
        "documents": len(rows),
        "ok": sum(1 for r in rows if r.get("ok")),
        "by_confidence": by_conf,
        "by_method": dict(sorted(by_method.items(), key=lambda kv: -kv[1])),
        "ok_by_year": dict(sorted(years.items())),
        "mean_words": round(sum(r.get("n_words", 0) for r in rows) / len(rows), 1),
        "ocr_pages_total": sum(r.get("ocr_pages", 0) for r in rows),
        # P22: how much of the corpus came through a text-layer shredder
        "by_producer": verify.producer_summary(rows),
        "reprocessor_sourced": sum(
            1 for r in rows
            if verify.is_reprocessor((r.get("qc") or {}).get("pdf_producer"))),
    }, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser("arpipe")
    sub = p.add_subparsers(dest="cmd", required=True)

    u = sub.add_parser("universe"); u.add_argument("--out", default="companies.csv")
    u.add_argument("--in-csv", default=None,
                   help="Rebuild/collapse an existing companies.csv without network fetch")
    u.add_argument("--bse-json", default=None)
    u.add_argument("--no-bse", action="store_true", help="Do not fetch or include BSE master")
    u.set_defaults(fn=cmd_universe)

    d = sub.add_parser("discover")
    d.add_argument("--companies", default="companies.csv")
    d.add_argument("--out", default="reports.jsonl")
    d.add_argument("--from-year", type=int, default=2010)
    d.add_argument("--to-year", type=int, default=2025)
    d.add_argument("--limit", type=int, default=0)
    d.add_argument("--use-bse", action="store_true", default=True)
    d.add_argument("--use-screener", action="store_true")
    d.set_defaults(fn=cmd_discover)

    f = sub.add_parser("fetch")
    f.add_argument("--manifest", default="reports.jsonl")
    f.add_argument("--root", default="store")
    f.add_argument("--workers", type=int, default=4)
    f.add_argument("--min-interval", type=float, default=1.5)
    f.set_defaults(fn=cmd_fetch)

    t = sub.add_parser("triage"); t.add_argument("--root", default="store")
    t.set_defaults(fn=cmd_triage)

    e = sub.add_parser("extract")
    e.add_argument("--root", default="store")
    e.add_argument("--out", default="dataset")
    e.add_argument("--companies", default="companies.csv")
    e.add_argument("--workers", type=int, default=4)
    e.add_argument("--resume", action="store_true", default=True)
    e.add_argument("--keep-pages", action="store_true")
    e.add_argument("--vlm-url", default=os.environ.get("ARPIPE_VLM_URL"))
    e.add_argument("--vlm-model", default=os.environ.get("ARPIPE_VLM_MODEL",
                                                         "PaddlePaddle/PaddleOCR-VL"))
    e.add_argument("--textract", action="store_true")
    e.add_argument("--aws-region", default="ap-south-1")
    e.set_defaults(fn=cmd_extract)

    a = sub.add_parser("audit"); a.add_argument("--out", default="dataset")
    a.set_defaults(fn=cmd_audit)

    ns = p.parse_args(argv)
    return ns.fn(ns)


if __name__ == "__main__":
    raise SystemExit(main())
