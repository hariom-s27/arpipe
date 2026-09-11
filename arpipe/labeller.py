"""Interactive ground-truth labelling tool and stratified sampler.

P12 requirement:
  - CLI: python -m arpipe.cli label --pdf <path> --out labels.csv
  - CLI: python -m arpipe.cli sample-for-labelling --n 300 --out to_label.csv
  - Reason codes: OK, WRONG_START, WRONG_END, BOTH, NOT_FOUND,
                  NO_MDA_IN_DOC, ORDER_SCRAMBLED
  - Resumes: skips already-labelled documents in labels.csv
  - Columns: sha256, company_id, cin, fy_end, doc_kind, cap_band, exchange,
             total_pages, proposed_start, proposed_end, true_start, true_end,
             reason_code, labeller, labelled_at
"""
from __future__ import annotations

import csv
import datetime as dt
import getpass
import hashlib
import json
import math
import os
import random
import sys
from collections import defaultdict
from typing import Callable

import pymupdf

from . import fetch, segment, store, textlayer, triage, universe
from .models import Company, DocProfile, PageKind, StoredDoc

REASON_CODES = [
    "OK",
    "WRONG_START",
    "WRONG_END",
    "BOTH",
    "NOT_FOUND",
    "NO_MDA_IN_DOC",
    "ORDER_SCRAMBLED",
]

ERAS = ["2010-2013", "2014-2018", "2019-2025"]
CAP_BANDS = ["large", "mid", "small", "micro"]
DOC_KINDS = ["digital", "mixed", "scanned"]

LABELS_COLUMNS = [
    "sha256",
    "company_id",
    "cin",
    "fy_end",
    "doc_kind",
    "cap_band",
    "exchange",
    "total_pages",
    "proposed_start",
    "proposed_end",
    "true_start",
    "true_end",
    "reason_code",
    "labeller",
    "labelled_at",
    "verified_by",
]

TO_LABEL_COLUMNS = [
    "sha256",
    "company_id",
    "cin",
    "fy_end",
    "doc_kind",
    "cap_band",
    "exchange",
    "total_pages",
    "path",
]

NIFTY_LARGE_SYMBOLS = {
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "ITC", "SBIN",
    "BHARTIARTL", "KOTAKBANK", "LT", "AXISBANK", "ASIANPAINT", "HCLTECH",
    "BAJFINANCE", "MARUTI", "TITAN", "SUNPHARMA", "TATASTEEL", "NTPC",
    "POWERGRID", "TATAMOTORS", "ONGC", "COALINDIA", "ULTRACEMCO", "WIPRO",
    "BAJAJFINSV", "NESTLEIND", "GRASIM", "JSWSTEEL", "ADANIENT", "ADANIPORTS",
    "TECHM", "HINDUNILVR", "M&M", "DRREDDY", "CIPLA", "HEROMOTOCO",
}


def era_for_year(fy_end: int | None) -> str:
    if fy_end is None:
        return "2019-2025"
    if 2010 <= fy_end <= 2013:
        return "2010-2013"
    if 2014 <= fy_end <= 2018:
        return "2014-2018"
    if 2019 <= fy_end <= 2025:
        return "2019-2025"
    return "2010-2013" if fy_end < 2010 else "2019-2025"


def cap_band_for_company(co: Company | None) -> str:
    if co:
        band = getattr(co, "cap_band_current", None) or co.cap_band
        if band and band.strip():
            b = band.strip().lower()
            if b in CAP_BANDS:
                return b
    if co is None:
        return "small"
    if co.exchange == "bse":
        return "micro"
    if co.exchange == "both":
        if co.nse_symbol and co.nse_symbol.upper() in NIFTY_LARGE_SYMBOLS:
            return "large"
        return "mid"
    return "small"


def load_existing_done(labels_path: str) -> set[str]:
    """Return set of sha256 already recorded in labels_path."""
    if not os.path.exists(labels_path) or os.path.getsize(labels_path) == 0:
        return set()
    done = set()
    with open(labels_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sha = row.get("sha256")
            if sha:
                done.add(sha.strip())
    return done


def append_label_row(labels_path: str, record: dict) -> None:
    exists = os.path.exists(labels_path) and os.path.getsize(labels_path) > 0
    with open(labels_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LABELS_COLUMNS)
        if not exists:
            writer.writeheader()
        writer.writerow({k: record.get(k, "") for k in LABELS_COLUMNS})


def sample_for_labelling(
        store_roots: list[str],
        companies_path: str = "companies.csv",
        n_samples: int = 300,
        out_csv: str = "to_label.csv",
        random_seed: int = 42) -> dict[str, object]:
    """Pick a stratified sample across era x cap_band x doc_kind.

    36 cells total (3 eras x 4 cap bands x 3 doc kinds).
    Target per cell: ceil(n_samples / 36) ~ 9.
    """
    companies = {c.company_id: c for c in universe.from_csv(companies_path)} if os.path.exists(companies_path) else {}

    candidates: list[dict] = []
    seen_sha: set[str] = set()

    for root in store_roots:
        doc_jsonl = os.path.join(root, "documents.jsonl")
        prof_jsonl = os.path.join(root, "profiles.jsonl")
        if not os.path.exists(doc_jsonl):
            continue

        profiles_by_sha: dict[str, dict] = {}
        if os.path.exists(prof_jsonl):
            for l in open(prof_jsonl, encoding="utf-8"):
                if l.strip():
                    p = json.loads(l)
                    profiles_by_sha[p.get("sha256")] = p

        for l in open(doc_jsonl, encoding="utf-8"):
            if not l.strip():
                continue
            d = json.loads(l)
            sha = d.get("sha256")
            if not sha or sha in seen_sha:
                continue
            seen_sha.add(sha)

            cid = d.get("company_id", "")
            co = companies.get(cid)
            fy = d.get("fy_end")
            p = profiles_by_sha.get(sha, {})

            # Document kind
            doc_kind = p.get("doc_kind")
            if not doc_kind:
                # fallback compute if missing
                try:
                    blob = store.blob_abspath(root, d.get("path", ""))
                    prof = triage.profile_document(blob)
                    doc_kind = prof.doc_kind
                except Exception:
                    doc_kind = "mixed"

            era = era_for_year(fy)
            cap_band = cap_band_for_company(co)
            exchange = getattr(co, "exchange", "both") if co else "both"
            cin = getattr(co, "cin", "") if co else ""

            blob_path = store.blob_abspath(root, d.get("path", ""))
            total_pages = d.get("n_pages") or p.get("n_pages", 0)

            candidates.append({
                "sha256": sha,
                "company_id": cid,
                "cin": cin,
                "fy_end": fy,
                "doc_kind": doc_kind,
                "cap_band": cap_band,
                "era": era,
                "exchange": exchange,
                "total_pages": total_pages,
                "path": blob_path,
            })

    # Group into the 36 cells: (era, cap_band, doc_kind)
    cells: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for c in candidates:
        key = (c["era"], c["cap_band"], c["doc_kind"])
        cells[key].append(c)

    rng = random.Random(random_seed)
    for k in cells:
        rng.shuffle(cells[k])

    target_per_cell = max(1, math.ceil(n_samples / 36))
    selected: list[dict] = []
    shortfalls: list[tuple[tuple[str, str, str], int, int]] = []
    cell_counts: dict[tuple[str, str, str], int] = {}

    for era in ERAS:
        for cap in CAP_BANDS:
            for kind in DOC_KINDS:
                key = (era, cap, kind)
                avail = cells[key]
                take = avail[:target_per_cell]
                selected.extend(take)
                cell_counts[key] = len(take)
                if len(avail) < target_per_cell:
                    shortfalls.append((key, len(avail), target_per_cell))

    # If selected > n_samples, trim down gracefully while preserving strata
    if len(selected) > n_samples:
        selected = selected[:n_samples]

    # Write to_label.csv
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TO_LABEL_COLUMNS)
        writer.writeheader()
        for s in selected:
            writer.writerow({k: s.get(k, "") for k in TO_LABEL_COLUMNS})

    # Print stratum summary
    print(f"\nStratified Sample: {len(selected)} documents selected across 36 cells -> {out_csv}")
    print(f"{'Era':<10} | {'Cap Band':<8} | {'Doc Kind':<8} | {'Sampled':<7} | {'Status'}")
    print("-" * 55)
    for era in ERAS:
        for cap in CAP_BANDS:
            for kind in DOC_KINDS:
                k = (era, cap, kind)
                cnt = cell_counts.get(k, 0)
                status = "OK" if cnt >= target_per_cell else ("EMPTY [!]" if cnt == 0 else f"Sparse ({cnt}/{target_per_cell})")
                print(f"{era:<10} | {cap:<8} | {kind:<8} | {cnt:<7} | {status}")

    if shortfalls:
        empty_cells = sum(1 for _, have, _ in shortfalls if have == 0)
        print(f"\n[NOTE] {len(shortfalls)} cells had fewer than {target_per_cell} available ({empty_cells} empty).")

    return {
        "total_selected": len(selected),
        "cells": {f"{k[0]}|{k[1]}|{k[2]}": cnt for k, cnt in cell_counts.items()},
        "shortfalls": len(shortfalls),
    }


def propose_span_for_pdf(pdf_path: str) -> dict:
    """Run lightweight triage + locate pass to get the pipeline's proposal."""
    profile = triage.profile_document(pdf_path)
    doc = pymupdf.open(pdf_path)
    try:
        digital = [p.page_no for p in profile.pages if p.kind is PageKind.DIGITAL]
        page_texts = textlayer.extract_pages(pdf_path, digital)
        span, diag = segment.locate(doc, profile, page_texts)
        if span is not None:
            def _fetch(n: int) -> str | None:
                if n >= profile.n_pages:
                    return None
                if profile.pages[n].kind is PageKind.DIGITAL:
                    return textlayer.extract_pages(pdf_path, [n]).get(n, "")
                return ""
            span = segment.refine_end(span, page_texts, _fetch)
            span = segment.trim_span(span, page_texts)
            return {
                "proposed_start": span.start_page,
                "proposed_end": span.end_page,
                "score": round(span.score, 3),
                "method": span.method,
                "supporters": span.supporters,
                "profile": profile,
                "page_texts": page_texts,
                "diag": diag,
            }
        else:
            return {
                "proposed_start": None,
                "proposed_end": None,
                "score": 0.0,
                "method": "none",
                "supporters": 0,
                "profile": profile,
                "page_texts": page_texts,
                "diag": diag,
            }
    finally:
        doc.close()


def pages_of_interest(profile: DocProfile, proposed_start: int | None,
                      proposed_end: int | None,
                      page_texts: dict[int, str]) -> list[int]:
    n_pages = profile.n_pages
    pages = set()
    # First 5 pages (TOC / front matter)
    for p in range(min(5, n_pages)):
        pages.add(p)
    # Proposed start context
    if proposed_start is not None:
        for p in range(max(0, proposed_start - 2), min(n_pages, proposed_start + 3)):
            pages.add(p)
    # Proposed end context
    if proposed_end is not None:
        for p in range(max(0, proposed_end - 1), min(n_pages, proposed_end + 3)):
            pages.add(p)
    # Any pages with "management discussion" mentions
    for pno, txt in page_texts.items():
        low = txt.lower()
        if "management discussion" in low or "management's discussion" in low:
            pages.add(pno)
    return sorted(p for p in pages if 0 <= p < n_pages)


def prompt_user_for_label(
        proposed_start: int | None,
        proposed_end: int | None,
        input_fn: Callable[[str], str] = input) -> tuple[int | None, int | None, str]:
    """Prompt the user for true start, true end, and reason code."""
    # 1. Start page
    def_start = str(proposed_start) if proposed_start is not None else "none"
    while True:
        raw = input_fn(f"True start page [default: {def_start}]: ").strip()
        if not raw:
            true_start = proposed_start
            break
        if raw.lower() in ("none", "null", "no", "n"):
            true_start = None
            break
        try:
            true_start = int(raw)
            break
        except ValueError:
            print("Invalid page number; enter an integer or 'none'.")

    # 2. End page
    def_end = str(proposed_end) if proposed_end is not None else "none"
    while True:
        raw = input_fn(f"True end page [default: {def_end}]: ").strip()
        if not raw:
            true_end = proposed_end
            break
        if raw.lower() in ("none", "null", "no", "n"):
            true_end = None
            break
        try:
            true_end = int(raw)
            break
        except ValueError:
            print("Invalid page number; enter an integer or 'none'.")

    # 3. Default reason code based on input comparison
    if true_start is None or true_end is None:
        def_reason = "NO_MDA_IN_DOC" if proposed_start is None else "NOT_FOUND"
    elif proposed_start is None:
        def_reason = "WRONG_START"
    elif true_start == proposed_start and true_end == proposed_end:
        def_reason = "OK"
    elif true_start != proposed_start and true_end == proposed_end:
        def_reason = "WRONG_START"
    elif true_start == proposed_start and true_end != proposed_end:
        def_reason = "WRONG_END"
    else:
        def_reason = "BOTH"

    while True:
        prompt_txt = (
            f"Reason code (OK/WRONG_START/WRONG_END/BOTH/NOT_FOUND/NO_MDA_IN_DOC/ORDER_SCRAMBLED) "
            f"[default: {def_reason}]: "
        )
        raw = input_fn(prompt_txt).strip().upper()
        if not raw:
            reason = def_reason
            break
        if raw in REASON_CODES:
            reason = raw
            break
        print(f"Invalid reason code '{raw}'. Allowed: {', '.join(REASON_CODES)}")

    return true_start, true_end, reason


def label_single_pdf(
        pdf_path: str,
        out_csv: str = "labels.csv",
        company_id: str | None = None,
        cin: str | None = None,
        fy_end: int | None = None,
        cap_band: str | None = None,
        exchange: str | None = None,
        labeller: str | None = None,
        input_fn: Callable[[str], str] = input) -> dict:
    """Label a single PDF document interactively."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    labeller = labeller or getpass.getuser()
    sha = fetch.sha256_file(pdf_path)

    # Check if already done
    done_shas = load_existing_done(out_csv)
    if sha in done_shas:
        print(f"Skipping already-labelled document: sha256={sha[:8]} ({os.path.basename(pdf_path)})")
        return {"status": "skipped", "sha256": sha}

    # Propose span
    prop = propose_span_for_pdf(pdf_path)
    profile: DocProfile = prop["profile"]
    page_texts: dict[int, str] = prop["page_texts"]
    p_start, p_end = prop["proposed_start"], prop["proposed_end"]
    score, method = prop["score"], prop["method"]

    print("\n" + "=" * 80)
    print(f"DOCUMENT: {os.path.basename(pdf_path)}")
    print(f"sha256: {sha[:12]} | total_pages: {profile.n_pages} | doc_kind: {profile.doc_kind}")
    if company_id:
        print(f"company_id: {company_id} | fy_end: {fy_end or '?'} | cap_band: {cap_band or '?'}")
    if p_start is not None and p_end is not None:
        print(f"PROPOSED SPAN: Pages {p_start} to {p_end} (method={method}, score={score:.3f}, supporters={prop['supporters']})")
    else:
        print("PROPOSED SPAN: None (pipeline could not locate MD&A)")
    print("=" * 80)

    # Show pages of interest
    interest = pages_of_interest(profile, p_start, p_end, page_texts)
    print(f"\nPages of interest ({len(interest)}): {interest}")
    print("-" * 80)

    doc = pymupdf.open(pdf_path)
    try:
        for pno in interest:
            tag = ""
            if pno == p_start and pno == p_end:
                tag = "  <-- PROPOSED START & END"
            elif pno == p_start:
                tag = "  <-- PROPOSED START"
            elif pno == p_end:
                tag = "  <-- PROPOSED END"

            txt = page_texts.get(pno)
            if not txt:
                try:
                    txt = doc.load_page(pno).get_text("text")
                except Exception:
                    txt = ""
            lines = [l.strip() for l in txt.split("\n") if l.strip()][:5]
            kind = profile.pages[pno].kind.value if pno < len(profile.pages) else "?"
            print(f"[Page {pno:3d}] (kind: {kind}){tag}")
            if lines:
                for ln in lines:
                    print(f"    {ln[:90]}")
            else:
                print("    (empty or unparsed text)")
            print()
    finally:
        doc.close()

    print("-" * 80)
    true_start, true_end, reason = prompt_user_for_label(p_start, p_end, input_fn=input_fn)

    record = {
        "sha256": sha,
        "company_id": company_id or "",
        "cin": cin or "",
        "fy_end": fy_end or "",
        "doc_kind": profile.doc_kind,
        "cap_band": cap_band or "",
        "exchange": exchange or "",
        "total_pages": profile.n_pages,
        "proposed_start": p_start if p_start is not None else "",
        "proposed_end": p_end if p_end is not None else "",
        "true_start": true_start if true_start is not None else "",
        "true_end": true_end if true_end is not None else "",
        "reason_code": reason,
        "labeller": labeller,
        "labelled_at": dt.datetime.now(dt.UTC).isoformat(),
        "verified_by": "read_pdf",
    }

    append_label_row(out_csv, record)
    print(f"Saved: true_span=[{true_start}..{true_end}], reason={reason} -> {out_csv}")
    return record


def label_batch_from_csv(
        batch_csv: str,
        out_csv: str = "labels.csv",
        labeller: str | None = None,
        input_fn: Callable[[str], str] = input) -> int:
    """Iterate through a batch CSV (e.g. to_label.csv) and label unlabelled items."""
    if not os.path.exists(batch_csv):
        raise FileNotFoundError(f"Batch file not found: {batch_csv}")

    done_shas = load_existing_done(out_csv)
    rows = []
    with open(batch_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    todo = [r for r in rows if r.get("sha256") not in done_shas]
    print(f"Batch labelling: {len(todo)} documents remaining ({len(rows) - len(todo)} already in {out_csv})")

    labelled_count = 0
    for i, r in enumerate(todo, 1):
        print(f"\n>>> [{i}/{len(todo)}] Labeling: {r.get('company_id')} (FY{r.get('fy_end')})")
        pdf_path = r.get("path")
        if not pdf_path or not os.path.exists(pdf_path):
            print(f"Warning: PDF file not found at path: {pdf_path}")
            continue

        try:
            fy = int(r.get("fy_end")) if r.get("fy_end") else None
        except ValueError:
            fy = None

        rec = label_single_pdf(
            pdf_path=pdf_path,
            out_csv=out_csv,
            company_id=r.get("company_id"),
            cin=r.get("cin"),
            fy_end=fy,
            cap_band=r.get("cap_band"),
            exchange=r.get("exchange"),
            labeller=labeller,
            input_fn=input_fn,
        )
        if rec.get("status") != "skipped":
            labelled_count += 1

    print(f"\nBatch labelling session finished: {labelled_count} documents labelled.")
    return labelled_count
