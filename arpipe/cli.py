"""Command line: arpipe <stage> ...

Stages are separate commands on purpose. At 40k+ documents you will re-run
`extract` a dozen times while `fetch` runs once; coupling them wastes days.

  arpipe preflight  check tools, disk, network, and deps before a long run
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
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from . import config, discover, fetch, ocr, pipeline, store, triage, universe, verify
from .models import Company, ReportRef, StoredDoc, to_json


def _load_companies(path: str) -> list[Company]:
    return universe.from_csv(path)


def cmd_universe(a: argparse.Namespace) -> int:
    cap_bands = {}
    if not getattr(a, "no_cap_bands", False):
        try:
            cap_bands = universe.fetch_cap_bands()
            print(f"Fetched {len(cap_bands)} index-classified companies for cap bands (Nifty 100/150/250)")
        except Exception as exc:
            print(f"Warning: Failed to fetch market cap bands: {exc}")

    if getattr(a, "in_csv", None):
        collapsed, removed = universe.collapse_companies_file(a.in_csv, a.out, cap_bands=cap_bands)
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

    companies = universe.build_master(nse, bse, chains, cap_bands=cap_bands)
    universe.to_csv(companies, a.out)
    bse_only = sum(1 for c in companies if c.exchange == "bse")
    nse_only = sum(1 for c in companies if c.exchange == "nse")
    both = sum(1 for c in companies if c.exchange == "both")
    print(f"{len(companies)} companies -> {a.out} ({bse_only} BSE-only, {nse_only} NSE-only, {both} both)")
    return 0


def cmd_discover(a: argparse.Namespace) -> int:
    import httpx
    cfg = config.get_config()
    rate = getattr(a, "rate", None)
    if rate is None:
        try:
            rate = cfg.discover.get("min_interval_seconds", 1.5) if hasattr(cfg.discover, "get") else getattr(cfg.discover, "min_interval_seconds", 1.5)
        except Exception:
            rate = 1.5

    sources_val = getattr(a, "sources", None)
    if sources_val:
        sources = [s.strip().lower() for s in sources_val.split(",") if s.strip()]
    else:
        try:
            cfg_sources = cfg.discover.get("sources") if hasattr(cfg.discover, "get") else getattr(cfg.discover, "sources", None)
            sources = [s.strip().lower() for s in cfg_sources] if cfg_sources else ["nse", "bse", "screener"]
        except Exception:
            sources = ["nse", "bse", "screener"]

    use_nse = "nse" in sources
    use_bse = ("bse" in sources) and getattr(a, "use_bse", True)
    use_screener = ("screener" in sources) or getattr(a, "use_screener", False)

    companies = _load_companies(a.companies)
    if a.limit:
        companies = companies[: a.limit]
    years = range(a.from_year, a.to_year + 1)

    done_companies: set[str] = set()
    open_mode = "w"
    if getattr(a, "resume", False) and os.path.exists(a.out):
        open_mode = "a"
        with open(a.out, "r", encoding="utf-8") as rf:
            for line in rf:
                line = line.strip()
                if line:
                    try:
                        row = json.loads(line)
                        cid = row.get("company_id")
                        if cid:
                            done_companies.add(cid)
                    except Exception:
                        pass
        print(f"Resuming discovery: {len(done_companies)} companies already recorded in {a.out}")

    out = open(a.out, open_mode, encoding="utf-8")
    nse_cl = discover.nse_session() if use_nse else None
    gen_cl = httpx.Client(timeout=30, follow_redirects=True)
    try:
        total = len(companies)
        for i, c in enumerate(companies, 1):
            if getattr(a, "resume", False) and c.company_id in done_companies:
                continue
            refs: list[ReportRef] = []
            if use_nse and nse_cl:
                refs += discover.discover_nse(c, nse_cl, rate=rate)
            if use_bse:
                refs += discover.discover_bse(c, gen_cl)
                if rate > 0:
                    time.sleep(rate)
            if use_screener:
                refs += discover.discover_screener(c, gen_cl)
                if rate > 0:
                    time.sleep(rate)
            by_year = discover.reconcile(refs, years)
            cov = discover.coverage_report(by_year, years)
            for y in sorted(by_year):
                for r in by_year[y]:
                    out.write(to_json(r) + "\n")
            out.flush()
            if i % 25 == 0 or total <= 25:
                print(f"[{i}/{total}] {c.canonical_name[:40]:40s} "
                      f"coverage={cov['coverage']:.2f} ({len(refs)} refs)", file=sys.stderr)
    finally:
        out.close()
        if nse_cl:
            nse_cl.close()
        gen_cl.close()
    print(f"manifest -> {a.out}")
    return 0


def cmd_fetch(a: argparse.Namespace) -> int:
    import httpx
    raw_refs = [ReportRef(**json.loads(l)) for l in open(a.manifest, encoding="utf-8") if l.strip()]
    limiter = fetch.HostLimiter(min_interval=a.min_interval)
    os.makedirs(a.root, exist_ok=True)
    done: set[tuple[str, int]] = set()
    if os.path.exists(os.path.join(a.root, "documents.jsonl")):
        for l in open(os.path.join(a.root, "documents.jsonl"), encoding="utf-8"):
            d = json.loads(l)
            done.add((d["company_id"], d["fy_end"]))

    # Group candidate URLs by (company_id, fy_end), ordered by priority (NSE > BSE > Screener)
    by_pair: dict[tuple[str, int], list[ReportRef]] = {}
    for r in raw_refs:
        by_pair.setdefault((r.company_id, r.fy_end), []).append(r)
    for pair in by_pair:
        by_pair[pair].sort(key=lambda r: (r.priority, r.url))

    out = open(os.path.join(a.root, "documents.jsonl"), "a", encoding="utf-8")
    cl = httpx.Client(headers={"User-Agent": discover.UA}, timeout=120,
                      follow_redirects=True)
    ok = err = skip = 0

    def _fetch_pair(candidates: list[ReportRef]) -> StoredDoc | None:
        for r in candidates:
            try:
                doc = fetch.fetch_one(r, a.root, cl, limiter)
                if doc:
                    return doc
            except Exception as exc:
                print(f"WARN fetch failover {r.company_id} {r.fy_end} [{r.source}]: {type(exc).__name__}", file=sys.stderr)
        return None

    try:
        with ThreadPoolExecutor(a.workers) as ex:
            futs = {}
            for pair, candidates in by_pair.items():
                if pair in done:
                    skip += 1
                    continue
                futs[ex.submit(_fetch_pair, candidates)] = pair
            for f in as_completed(futs):
                pair = futs[f]
                try:
                    doc = f.result()
                except Exception as exc:              # noqa: BLE001
                    err += 1
                    print(f"ERR {pair[0]} {pair[1]} {type(exc).__name__}",
                          file=sys.stderr)
                    continue
                if doc is None:
                    err += 1
                    print(f"FAILED {pair[0]} {pair[1]} across all candidate sources",
                          file=sys.stderr)
                    continue
                out.write(to_json(doc) + "\n")
                out.flush()
                ok += 1
    finally:
        out.close()
        cl.close()
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
            rec["run_config"] = config.config_for_manifest()
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


def cmd_sample_for_labelling(a: argparse.Namespace) -> int:
    from . import labeller
    stores = []
    if a.store:
        stores = a.store if isinstance(a.store, list) else [a.store]
    else:
        candidates = [
            "p11_store", "pilot_store", "live_store", "store",
            os.path.join("arpipe", "p11_store"),
            os.path.join("arpipe", "pilot_store"),
            os.path.join("arpipe", "live_store"),
            os.path.join("arpipe", "store"),
        ]
        for s in candidates:
            if os.path.exists(s) and os.path.abspath(s) not in [os.path.abspath(x) for x in stores]:
                stores.append(s)
    comp_path = a.companies
    if not os.path.exists(comp_path) and os.path.exists(os.path.join("arpipe", comp_path)):
        comp_path = os.path.join("arpipe", comp_path)
    labeller.sample_for_labelling(
        store_roots=stores,
        companies_path=comp_path,
        n_samples=a.n,
        out_csv=a.out,
    )
    return 0


def cmd_label(a: argparse.Namespace) -> int:
    from . import labeller
    if a.pdf:
        labeller.label_single_pdf(
            pdf_path=a.pdf,
            out_csv=a.out,
            company_id=a.company_id,
            cin=a.cin,
            fy_end=a.fy_end,
            cap_band=a.cap_band,
            exchange=a.exchange,
            labeller=a.labeller,
        )
        return 0

    batch_file = a.batch or "to_label.csv"
    if os.path.exists(batch_file):
        labeller.label_batch_from_csv(
            batch_csv=batch_file,
            out_csv=a.out,
            labeller=a.labeller,
        )
        return 0

    print("Error: Specify --pdf <path> or provide a batch file (--batch / to_label.csv)", file=sys.stderr)
    return 1


def cmd_evaluate(a: argparse.Namespace) -> int:
    from . import evaluate
    dataset_roots = []
    if a.dataset:
        dataset_roots = a.dataset if isinstance(a.dataset, list) else [a.dataset]

    split = getattr(a, "split", "fit")

    if split in ("holdout", "both"):
        evaluate.log_holdout_access(split=split)

    if split == "both":
        fit_labels = a.labels or ("labels_fit.csv" if os.path.exists("labels_fit.csv") else "labels.csv")
        fit_out = a.out or "eval_report_fit.md"
        print(f"\n=== Evaluating Fit Split: {fit_labels} ===")
        ret1 = evaluate.evaluate_file(
            labels_csv=fit_labels,
            out_report_md=fit_out,
            dataset_roots=dataset_roots if dataset_roots else None,
        )

        holdout_labels = "labels_holdout.csv"
        holdout_out = "eval_report_holdout.md"
        print(f"\n=== Evaluating Holdout Split: {holdout_labels} ===")
        if not os.path.exists(holdout_labels):
            print(f"Holdout file not found: {holdout_labels} (0 holdout documents labelled).")
            ret2 = 0
        else:
            ret2 = evaluate.evaluate_file(
                labels_csv=holdout_labels,
                out_report_md=holdout_out,
                dataset_roots=dataset_roots if dataset_roots else None,
            )
        return 0 if (ret1 == 0 and ret2 == 0) else 1

    labels_csv = a.labels
    if not labels_csv:
        if split == "holdout":
            labels_csv = "labels_holdout.csv"
        else:
            labels_csv = "labels_fit.csv" if os.path.exists("labels_fit.csv") else "labels.csv"

    out_md = a.out
    if not out_md:
        out_md = "eval_report_holdout.md" if split == "holdout" else "eval_report.md"

    if not os.path.exists(labels_csv) and split == "holdout":
        print(f"Holdout file not found: {labels_csv} (no holdout documents labelled yet).")
        return 0

    return evaluate.evaluate_file(
        labels_csv=labels_csv,
        out_report_md=out_md,
        dataset_roots=dataset_roots if dataset_roots else None,
    )



def cmd_preflight(a: argparse.Namespace) -> int:
    from . import preflight
    return preflight.run_preflight(
        root=a.root,
        out=a.out,
        companies=a.companies,
        min_disk_tb=a.min_disk_tb,
        req_file=getattr(a, "req_file", None),
        vlm_url=a.vlm_url,
        vlm_model=a.vlm_model,
        gpu=a.gpu,
        textract=a.textract,
        aws_region=a.aws_region,
        fix_hints=a.fix_hints,
        no_network=a.no_network,
    )


def main(argv: list[str] | None = None) -> int:
    args_list = sys.argv[1:] if argv is None else argv
    subcmds = {"universe", "discover", "fetch", "triage", "extract", "audit",
               "sample-for-labelling", "label", "evaluate", "preflight"}

    # Top-level --print-config without requiring a subcommand
    if "--print-config" in args_list and not any(a in subcmds for a in args_list):
        c_path = None
        sets = []
        for i, a in enumerate(args_list):
            if a == "--config" and i + 1 < len(args_list):
                c_path = args_list[i + 1]
            elif a.startswith("--config="):
                c_path = a.split("=", 1)[1]
            elif a == "--set" and i + 1 < len(args_list):
                sets.append(args_list[i + 1])
            elif a.startswith("--set="):
                sets.append(a.split("=", 1)[1])
        cfg = config.load_config(config_path=c_path, cli_overrides={"set": sets})
        print(config.format_config_dump(cfg))
        return 0

    cfg_parent = argparse.ArgumentParser(add_help=False)
    cfg_parent.add_argument("--config", default=None, help="Path to YAML configuration file")
    cfg_parent.add_argument("--print-config", action="store_true",
                            help="Dump fully resolved config with sources and exit")
    cfg_parent.add_argument("--set", action="append", default=[],
                            help="Override config value: section.key=val")

    p = argparse.ArgumentParser("arpipe", parents=[cfg_parent])
    sub = p.add_subparsers(dest="cmd", required=True)

    u = sub.add_parser("universe", parents=[cfg_parent]); u.add_argument("--out", default="companies.csv")
    u.add_argument("--in-csv", default=None,
                   help="Rebuild/collapse an existing companies.csv without network fetch")
    u.add_argument("--bse-json", default=None)
    u.add_argument("--no-bse", action="store_true", help="Do not fetch or include BSE master")
    u.set_defaults(fn=cmd_universe)

    d = sub.add_parser("discover", parents=[cfg_parent])
    d.add_argument("--companies", default="companies.csv")
    d.add_argument("--out", default="reports.jsonl")
    d.add_argument("--from-year", type=int, default=2010)
    d.add_argument("--to-year", type=int, default=2025)
    d.add_argument("--limit", type=int, default=0)
    d.add_argument("--sources", default=None,
                   help="Comma-separated sources to query: nse,bse,screener (default: from config)")
    d.add_argument("--rate", type=float, default=None,
                   help="Request interval in seconds (default: from config, 1.5)")
    d.add_argument("--resume", action="store_true", default=False,
                   help="Resume discovery, skipping companies already present in --out")
    d.add_argument("--use-bse", action=argparse.BooleanOptionalAction, default=True,
                   help="Query BSE for annual reports (default: True, use --no-use-bse to disable)")
    d.add_argument("--use-screener", action="store_true",
                   help="Query Screener for annual reports")
    d.set_defaults(fn=cmd_discover)

    f = sub.add_parser("fetch", parents=[cfg_parent])
    f.add_argument("--manifest", default="reports.jsonl")
    f.add_argument("--root", default="store")
    f.add_argument("--workers", type=int, default=4)
    f.add_argument("--min-interval", type=float, default=1.5)
    f.set_defaults(fn=cmd_fetch)

    t = sub.add_parser("triage", parents=[cfg_parent]); t.add_argument("--root", default="store")
    t.set_defaults(fn=cmd_triage)

    e = sub.add_parser("extract", parents=[cfg_parent])
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

    a = sub.add_parser("audit", parents=[cfg_parent]); a.add_argument("--out", default="dataset")
    a.set_defaults(fn=cmd_audit)

    sfl = sub.add_parser("sample-for-labelling", parents=[cfg_parent])
    sfl.add_argument("--n", type=int, default=300, help="Number of documents to sample (stratified across 36 cells)")
    sfl.add_argument("--out", default="to_label.csv", help="Output to_label.csv path")
    sfl.add_argument("--store", action="append", default=None,
                     help="Store directory to sample from (can be passed multiple times)")
    sfl.add_argument("--companies", default="companies.csv")
    sfl.set_defaults(fn=cmd_sample_for_labelling)

    lbl = sub.add_parser("label", parents=[cfg_parent])
    lbl.add_argument("--pdf", default=None, help="Path to a single PDF to label")
    lbl.add_argument("--out", default="labels.csv", help="Output labels CSV path")
    lbl.add_argument("--batch", "--to-label", dest="batch", default=None,
                     help="Path to to_label.csv for batch labelling")
    lbl.add_argument("--labeller", default=None, help="Name of human labeller")
    lbl.add_argument("--company-id", default=None)
    lbl.add_argument("--cin", default=None)
    lbl.add_argument("--fy-end", type=int, default=None)
    lbl.add_argument("--cap-band", default=None)
    lbl.add_argument("--exchange", default=None)
    lbl.set_defaults(fn=cmd_label)

    evl = sub.add_parser("evaluate", parents=[cfg_parent])
    evl.add_argument("--labels", default=None, help="Path to labels CSV ground truth (default: inferred from --split)")
    evl.add_argument("--split", choices=["fit", "holdout", "both"], default="fit",
                     help="Dataset split to evaluate: fit (default), holdout, or both")
    evl.add_argument("--out", default=None, help="Path to output markdown report (default: eval_report.md or per-split)")
    evl.add_argument("--dataset", action="append", default=None,
                     help="Path to dataset folder containing manifest.jsonl (can be passed multiple times)")
    evl.set_defaults(fn=cmd_evaluate)

    pf = sub.add_parser("preflight", parents=[cfg_parent],
                        help="Check tools, disk, network, and deps before a long run")
    pf.add_argument("--root", default="store", help="Store directory")
    pf.add_argument("--out", default="dataset", help="Dataset output directory")
    pf.add_argument("--companies", default="companies.csv")
    pf.add_argument("--min-disk-tb", type=float, default=1.0,
                    help="Minimum free disk space in TB (default: 1.0)")
    pf.add_argument("--req-file", default=None,
                    help="Path to requirements.txt (auto-detected if omitted)")
    pf.add_argument("--vlm-url", default=os.environ.get("ARPIPE_VLM_URL"))
    pf.add_argument("--vlm-model", default=os.environ.get("ARPIPE_VLM_MODEL",
                                                           "PaddlePaddle/PaddleOCR-VL"))
    pf.add_argument("--gpu", action="store_true", help="Require GPU with >= 4 GB VRAM")
    pf.add_argument("--textract", action="store_true", help="Check AWS Textract credentials")
    pf.add_argument("--aws-region", default="ap-south-1")
    pf.add_argument("--fix-hints", action="store_true",
                    help="Print OS-specific install commands for anything missing")
    pf.add_argument("--no-network", action="store_true",
                    help="Skip network reachability checks")
    pf.set_defaults(fn=cmd_preflight)

    ns = p.parse_args(argv)

    # Load resolved config with 4-level precedence and apply to all modules
    cfg = config.load_config(config_path=getattr(ns, "config", None), cli_overrides=ns)
    config.set_active_config(cfg)

    if getattr(ns, "print_config", False):
        print(config.format_config_dump(cfg))
        return 0

    return ns.fn(ns)


if __name__ == "__main__":
    raise SystemExit(main())
