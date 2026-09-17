"""P-M2: does the 0.03 orphan_start_frac diagnostic band behave the same on
native-extracted text as it does on OCR-derived text?

Measurement-only. This script:
  * never imports/calls verify.configure() and never assigns to
    verify.ORPHAN_START_FRAC_MAX / verify.ORPHAN_BASIS - it reads them;
  * never recomputes orphan_start_frac from mda_text. Every value in the
    report is verify.order_quality()'s own number, read verbatim from the
    persisted mda.json qc block the real pipeline already wrote;
  * only ever opens a stored PDF read-only, via triage.profile_document(),
    to recover per-page PageKind (DIGITAL / SCANNED / HYBRID / ...) - that
    classification is not persisted in mda.json today, but the function that
    produces it is the exact one pipeline.py already calls, unchanged;
  * writes nothing back into the corpus it measures - only the three report
    files (--out-prefix) are touched.

Granularity note (read this before trusting the page-level sections below):
verify.order_quality() has only ever been a DOCUMENT/SPAN-level metric - one
number per extracted MD&A text, however many physical pages it spans. There
is no persisted per-physical-page breakdown in this corpus. A separate,
already-in-progress change (referred to below as "P-M1": it adds
verify.order_quality_by_page(), verify.PAGE_ORPHAN_DIAGNOSTIC_THRESHOLD, a
qc["orphan_start_frac_pages"] array and an `arpipe orderqc` command - not
committed as of this measurement, so unavailable in this worktree) is the
project's real per-page implementation. Building a second one here would be
exactly the "second implementation" P-M2's own instructions forbid, and would
almost certainly disagree with it at page boundaries. So:

  - the PRIMARY analysis in this report is at DOCUMENT (MD&A span) grain:
    one orphan_start_frac observation per located document, exactly as
    verify.grade()/build_reasons() already consume it, with the document
    labelled native / ocr / mixed / unknown by the provenance of the pages
    in its span;
  - a SECONDARY, page-counting view (not a page-level orphan_start_frac)
    reports how many physical pages within measured spans are native vs OCR
    vs unknown, and lists the physical OCR/native pages inside the
    highest-scoring documents, so the "top pages" ask in the brief has a
    concrete, inspectable answer without fabricating a metric.

Once P-M1 lands and a corpus is regenerated with qc["orphan_start_frac_pages"]
populated, re-run a true page-level version of this comparison by joining
that array with classify_span_pages() below - do not backfill it by
recomputing order_quality() per page here.

Usage:
    cd arpipe-pm2-native-vs-ocr
    arpipe/.venv/Scripts/python.exe tools/pm2_orphan_native_vs_ocr.py \
        --root "../arpipe-0.1.0/live_dataset" --out-dir reports
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from collections import Counter, defaultdict
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from arpipe import triage, verify              # noqa: E402
from arpipe.models import PageKind             # noqa: E402

try:
    import numpy as np
except ImportError:  # pragma: no cover - numpy is a project dependency
    np = None


# --------------------------------------------------------------- provenance

def classify_span_pages(span: dict[str, Any] | None,
                        ocr_stats: list[dict] | None,
                        page_kinds: dict[int, PageKind]) -> dict[int, str]:
    """Per physical page in `span`: 'native' | 'ocr' | 'blank' | 'unknown'.

    `ocr_stats` is qc["ocr_stats"] straight from mda.json: every OCR attempt
    made anywhere in process_document() (index sampling, refine_end probes,
    full-span OCR, front-matter fallback), not just the ones inside the
    final span - so only entries whose page_no falls inside [start, end] are
    used. A page is 'ocr' if the LARGEST word count any such attempt
    returned is > 0 (that is what got merged into page_texts and therefore
    into mda_text - see pipeline.py's `if res.text.strip(): got[n] = ...`).

    `page_kinds` is {page_no: PageKind}, freshly re-derived by
    triage.profile_document() on the stored PDF (read-only, no rendering).
    It is not persisted in mda.json, so it has to be recovered this way to
    tell a genuinely native page ('kind' DIGITAL, never sent to OCR) apart
    from a page whose provenance cannot be established (non-digital kind,
    but OCR never ran or ran and produced nothing) - the latter is left
    'unknown' rather than guessed either way, per the P-M2 brief.
    """
    if not span or span.get("start_page") is None or span.get("end_page") is None:
        return {}
    start, end = span["start_page"], span["end_page"]
    ocr_words: dict[int, int] = defaultdict(int)
    for s in ocr_stats or []:
        pno = s.get("page_no")
        if pno is None or not (start <= pno <= end):
            continue
        ocr_words[pno] = max(ocr_words[pno], s.get("words") or 0)

    out: dict[int, str] = {}
    for pno in range(start, end + 1):
        if ocr_words.get(pno, 0) > 0:
            out[pno] = "ocr"
            continue
        kind = page_kinds.get(pno)
        if kind is PageKind.DIGITAL:
            out[pno] = "native"
        elif kind is PageKind.BLANK:
            out[pno] = "blank"
        else:
            out[pno] = "unknown"
    return out


def document_provenance(page_classes: dict[int, str]) -> str:
    """'native' | 'ocr' | 'mixed' | 'unknown' | 'empty' for a whole document.

    Blank pages carry no text and never move the verdict either way. Any
    other page whose own provenance is 'unknown' makes the WHOLE document
    'unknown' for the native/ocr comparison - P-M2 rule 5 forbids silently
    folding an unresolved page into either bucket, and a single unresolved
    page inside the span means the span's one orphan_start_frac number can
    no longer be attributed cleanly to "native" or "ocr" text.
    """
    non_blank = [c for c in page_classes.values() if c != "blank"]
    if not non_blank:
        return "empty"
    if "unknown" in non_blank:
        return "unknown"
    kinds = set(non_blank)
    if kinds == {"native"}:
        return "native"
    if kinds == {"ocr"}:
        return "ocr"
    return "mixed"


# ------------------------------------------------------------ corpus loader

def load_corpus(root: str, *, profile_cache: dict[str, Any] | None = None,
                progress: bool = False) -> list[dict[str, Any]]:
    """One record per document under `root/companies/*/*/mda.json`, plus a
    record for every manifest row that never got that far (mda_not_located,
    profile_failed, quarantined pre-span) so the population accounting in
    section 2 of the report can be exact, not just "182 out of who knows
    what". Nothing under `root` is opened for writing.
    """
    records: list[dict[str, Any]] = []
    profile_cache = profile_cache if profile_cache is not None else {}

    seen_keys: set[tuple[str, int]] = set()
    mda_paths = sorted(glob.glob(os.path.join(root, "companies", "*", "*", "mda.json")))
    for i, mda_path in enumerate(mda_paths):
        if progress and i % 25 == 0:
            print(f"  ... {i}/{len(mda_paths)} mda.json", file=sys.stderr)
        doc_dir = os.path.dirname(mda_path)
        with open(mda_path, encoding="utf-8") as fh:
            mj = json.load(fh)
        key = (mj.get("company_id"), mj.get("fy_end"))
        seen_keys.add(key)
        records.append(_record_from_mda_json(mj, doc_dir, profile_cache))

    manifest_path = os.path.join(root, "manifest.jsonl")
    if os.path.exists(manifest_path):
        with open(manifest_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                key = (row.get("company_id"), row.get("fy_end"))
                if key in seen_keys:
                    continue                       # already loaded from its mda.json
                records.append({
                    "company_id": row.get("company_id"),
                    "fy_end": row.get("fy_end"),
                    "sha256": row.get("sha256"),
                    "doc_dir": None,
                    "span": None,
                    "orphan_start_frac": None,
                    "orphan_basis": None,
                    "orphan_gate_version": None,
                    "orphan_gate_max": None,
                    "n_paragraphs": None,
                    "provenance": "no_span",
                    "page_classes": {},
                    "ocr_engines": [],
                    "pdf_producer": None,
                    "grade": row.get("confidence"),
                    "reasons": row.get("reasons") or [],
                    "total_pages": row.get("total_pages"),
                    "mda_page_count": row.get("mda_page_count"),
                })
    return records


def _record_from_mda_json(mj: dict[str, Any], doc_dir: str,
                          profile_cache: dict[str, Any]) -> dict[str, Any]:
    span = mj.get("span")
    qc = mj.get("qc") or {}
    osf = qc.get("orphan_start_frac")

    base = {
        "company_id": mj.get("company_id"),
        "fy_end": mj.get("fy_end"),
        "sha256": mj.get("sha256"),
        "doc_dir": doc_dir,
        "span": span,
        "orphan_start_frac": osf,
        "orphan_basis": qc.get("orphan_basis"),
        "orphan_gate_version": qc.get("orphan_gate_version"),
        "orphan_gate_max": qc.get("orphan_gate_max"),
        "n_paragraphs": qc.get("n_paragraphs"),
        "pdf_producer": qc.get("pdf_producer"),
        "grade": mj.get("confidence"),
        "reasons": mj.get("reasons") or [],
        "total_pages": mj.get("total_pages"),
        "mda_page_count": mj.get("mda_page_count"),
    }

    if span is None or span.get("start_page") is None or osf is None:
        base.update(provenance="no_span", page_classes={}, ocr_engines=[])
        return base

    pdf_path = os.path.join(doc_dir, "annual_report.pdf")
    if pdf_path not in profile_cache:
        try:
            profile_cache[pdf_path] = triage.profile_document(pdf_path)
        except Exception:                          # noqa: BLE001 - diagnostic tool
            profile_cache[pdf_path] = None
    profile = profile_cache[pdf_path]

    if profile is None:
        base.update(provenance="unknown", page_classes={}, ocr_engines=[])
        return base

    page_kinds = {p.page_no: p.kind for p in profile.pages}
    page_classes = classify_span_pages(span, qc.get("ocr_stats"), page_kinds)
    ocr_engines = sorted({
        s.get("engine") for s in (qc.get("ocr_stats") or [])
        if s.get("engine") and page_classes.get(s.get("page_no")) == "ocr"
    })
    base.update(
        provenance=document_provenance(page_classes),
        page_classes=page_classes,
        ocr_engines=ocr_engines,
    )
    return base


# --------------------------------------------------------------- statistics

_PCTS = (0, 25, 50, 75, 90, 95, 100)
_PCT_LABELS = {0: "min", 25: "p25", 50: "median", 75: "p75", 90: "p90", 95: "p95", 100: "max"}


def _percentile(values: list[float], q: float) -> float:
    """numpy.percentile(values, q, method='linear') - the project has no
    prior percentile convention of its own (grep confirms no other module
    computes one), so this measurement adopts numpy's default linear
    interpolation explicitly and uses it for both populations, identically.
    A pure-Python fallback (same linear-interpolation definition) covers an
    environment without numpy so the tool degrades rather than crashes."""
    if np is not None:
        return float(np.percentile(values, q, method="linear"))
    s = sorted(values)
    n = len(s)
    if n == 1:
        return s[0]
    idx = q / 100 * (n - 1)
    lo, hi = int(idx // 1), min(n - 1, int(idx // 1) + 1)
    frac = idx - lo
    return s[lo] + (s[hi] - s[lo]) * frac


def distribution_stats(values: list[float]) -> dict[str, Any]:
    """N, min, P25, median, P75, P90, P95, max. Never fabricates a number:
    an empty `values` list returns N=0 and None for every statistic, not
    0.0 - the population itself may be exactly what section 6 is asking
    for, and 0.0 would silently misrepresent "no data" as "perfectly
    ordered"."""
    if not values:
        return {"N": 0, **{_PCT_LABELS[q]: None for q in _PCTS}}
    return {"N": len(values),
            **{_PCT_LABELS[q]: round(_percentile(values, q), 4) for q in _PCTS}}


def threshold_diagnostics(values: list[float], gate: float) -> dict[str, Any]:
    """Where the observed values sit relative to `gate`, using plain `<`,
    `==`, `>` on the same rounded-to-4dp floats verify.order_quality()
    already produced - 0.03 and 0.030000 are the same Python float literal,
    and every stored value went through the identical `round(x, 4)` call, so
    no epsilon/tolerance handling is needed for consistent gate comparison.
    """
    n = len(values)
    below = [v for v in values if v < gate]
    at = [v for v in values if v == gate]
    above = [v for v in values if v > gate]
    le_gate = [v for v in values if v <= gate]
    gt_gate = [v for v in values if v > gate]
    max_le = max(le_gate) if le_gate else None
    min_gt = min(gt_gate) if gt_gate else None
    gap = round(min_gt - max_le, 4) if (max_le is not None and min_gt is not None) else None
    return {
        "gate": gate,
        "n": n,
        "n_below": len(below),
        "n_at": len(at),
        "n_above": len(above),
        "frac_above": round(len(above) / n, 4) if n else None,
        "max_le_gate": round(max_le, 4) if max_le is not None else None,
        "min_gt_gate": round(min_gt, 4) if min_gt is not None else None,
        "gap": gap,
    }


def compare_distributions(native_stats: dict, ocr_stats: dict,
                          native_thresh: dict, ocr_thresh: dict) -> dict[str, Any]:
    def sub(a, b):
        return None if a is None or b is None else round(a - b, 4)
    return {
        "median_delta_ocr_minus_native": sub(ocr_stats.get("median"), native_stats.get("median")),
        "p95_delta_ocr_minus_native": sub(ocr_stats.get("p95"), native_stats.get("p95")),
        "frac_above_delta_ocr_minus_native": sub(ocr_thresh.get("frac_above"), native_thresh.get("frac_above")),
    }


def production_reason_crosscheck(records_subset: list[dict], gate: float) -> dict[str, Any]:
    """How many of the over-gate documents actually got flagged in production.

    verify.build_reasons() does not fire on `osf > gate` alone - it also
    requires `orphan_starts is None or orphan_starts > 1` (a floor against a
    short span where a single flagged paragraph produces a high fraction; see
    verify.py's `over_gate`). So "fraction > 0.03" (section C) can overstate
    how often the gate actually changed a document's reason codes. This is a
    read of the `reasons` list verify.build_reasons() already wrote into
    mda.json - not a second implementation of the gate."""
    over = [r for r in records_subset if r["orphan_start_frac"] is not None
           and r["orphan_start_frac"] > gate]
    flagged = [r for r in over
              if "source_shredded" in r["reasons"] or "order_scrambled" in r["reasons"]]
    return {
        "n_over_gate": len(over),
        "n_over_gate_and_flagged": len(flagged),
        "n_over_gate_but_not_flagged": len(over) - len(flagged),
    }


def sample_size_note(n: int) -> str:
    """Plain-language-only categorisation (the project defines no rigid N
    cutoffs for this, and P-M2's brief explicitly says not to invent one) -
    these are informal labels for the prose in the report, not a statistical
    test."""
    if n == 0:
        return "N = 0: impossible to evaluate"
    if n < 10:
        return f"N = {n}: very small - descriptive only, no stable distributional conclusion"
    if n < 30:
        return f"N = {n}: moderate - useful exploratory evidence"
    return f"N = {n}: large - stronger corpus-level descriptive evidence"


# ------------------------------------------------------------------ report

def build_report(records: list[dict[str, Any]], *, gate: float,
                 orphan_basis: str, top_n: int = 10) -> dict[str, Any]:
    total_docs = len(records)
    with_span = [r for r in records if r["provenance"] != "no_span"]

    by_basis: dict[str | None, list[dict]] = defaultdict(list)
    for r in with_span:
        by_basis[r["orphan_basis"]].append(r)
    other_basis = {k: len(v) for k, v in by_basis.items() if k != orphan_basis}
    primary = by_basis.get(orphan_basis, [])

    provenance_counts = Counter(r["provenance"] for r in primary)
    native_vals = [r["orphan_start_frac"] for r in primary if r["provenance"] == "native"]
    ocr_vals = [r["orphan_start_frac"] for r in primary if r["provenance"] == "ocr"]
    mixed_vals = [r["orphan_start_frac"] for r in primary if r["provenance"] == "mixed"]

    native_dist = distribution_stats(native_vals)
    ocr_dist = distribution_stats(ocr_vals)
    mixed_dist = distribution_stats(mixed_vals)
    native_thresh = threshold_diagnostics(native_vals, gate)
    ocr_thresh = threshold_diagnostics(ocr_vals, gate)
    mixed_thresh = threshold_diagnostics(mixed_vals, gate)

    page_totals = Counter()
    for r in primary:
        for cls in r["page_classes"].values():
            page_totals[cls] += 1

    unknown_docs = [{"company_id": r["company_id"], "fy_end": r["fy_end"]}
                    for r in primary if r["provenance"] == "unknown"]

    reason_crosscheck = {
        "native": production_reason_crosscheck([r for r in primary if r["provenance"] == "native"], gate),
        "ocr": production_reason_crosscheck([r for r in primary if r["provenance"] == "ocr"], gate),
        "mixed": production_reason_crosscheck([r for r in primary if r["provenance"] == "mixed"], gate),
    }

    def top(records_subset: list[dict], n: int) -> list[dict]:
        ranked = sorted(records_subset, key=lambda r: r["orphan_start_frac"], reverse=True)[:n]
        return [{
            "company_id": r["company_id"], "fy_end": r["fy_end"],
            "span": [r["span"]["start_page"], r["span"]["end_page"]] if r["span"] else None,
            "orphan_start_frac": r["orphan_start_frac"],
            "ocr_engines": r["ocr_engines"],
            "ocr_pages_in_span": sorted(p for p, c in r["page_classes"].items() if c == "ocr"),
            "native_pages_in_span": sorted(p for p, c in r["page_classes"].items() if c == "native"),
            "grade": r["grade"], "reasons": r["reasons"],
            "pdf_producer": r["pdf_producer"],
        } for r in ranked]

    report = {
        "methodology_note": (
            "Primary comparison is per-DOCUMENT (MD&A span), using "
            "verify.order_quality()'s own persisted number - see this "
            "script's module docstring for why per-physical-page "
            "orphan_start_frac is not (re)computed here."
        ),
        "orphan_gate": gate,
        "orphan_basis_used": orphan_basis,
        "population": {
            "total_manifest_records": total_docs,
            "documents_with_located_span": len(with_span),
            "documents_no_span_excluded": total_docs - len(with_span),
            "documents_other_basis_excluded": other_basis,
            "documents_primary_basis": len(primary),
            "provenance_counts": dict(provenance_counts),
            "span_pages_by_class": dict(page_totals),
            "unknown_provenance_documents": unknown_docs,
        },
        "distribution": {"native": native_dist, "ocr": ocr_dist, "mixed": mixed_dist},
        "threshold_diagnostics": {"native": native_thresh, "ocr": ocr_thresh, "mixed": mixed_thresh},
        "production_reason_crosscheck": reason_crosscheck,
        "comparison": compare_distributions(native_dist, ocr_dist, native_thresh, ocr_thresh),
        "sample_size_notes": {
            "native": sample_size_note(len(native_vals)),
            "ocr": sample_size_note(len(ocr_vals)),
            "mixed": sample_size_note(len(mixed_vals)),
        },
        "top_documents": {
            "ocr": top([r for r in primary if r["provenance"] == "ocr"], top_n),
            "native": top([r for r in primary if r["provenance"] == "native"], top_n),
            "mixed": top([r for r in primary if r["provenance"] == "mixed"], top_n),
        },
    }
    return report


# ------------------------------------------------------------------- plot

def render_plot(native_vals: list[float], ocr_vals: list[float], gate: float,
                out_path: str) -> bool:
    """Native as a histogram (left axis: document count), OCR as a rug plot
    (one full-height tick per observation) on the SAME x-axis and the SAME
    x-scale as native.

    A shared histogram would be misleading here: OCR N is small enough
    (single digits in this corpus) that its bars round to 0-1 count per bin
    and disappear under native's much taller bars at any shared y-scale
    that is not itself misleading (the brief explicitly rules out separate
    arbitrary scales). A rug plot has no y-scale to distort - each OCR
    document is drawn as one visible mark at its own x position, so N=5
    stays honestly legible instead of vanishing into rounding.

    Uses Pillow only (already a project dependency; no matplotlib install
    needed / no change to the shared environment). Returns False without
    writing anything if there is nothing to plot."""
    if not native_vals and not ocr_vals:
        return False
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return False

    W, H = 1000, 560
    margin_l, margin_r, margin_t, margin_b = 70, 30, 70, 90
    plot_w, plot_h = W - margin_l - margin_r, H - margin_t - margin_b

    all_vals = native_vals + ocr_vals
    x_max = max(0.06, max(all_vals) * 1.05 if all_vals else 0.06)
    n_bins = 30
    bin_w = x_max / n_bins

    def hist(vals: list[float]) -> list[int]:
        counts = [0] * n_bins
        for v in vals:
            b = min(n_bins - 1, int(v / bin_w)) if v >= 0 else 0
            counts[b] += 1
        return counts

    h_native = hist(native_vals)
    y_max = max([1] + h_native)

    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except Exception:                                # noqa: BLE001
        font = None

    def x_to_px(x: float) -> int:
        return margin_l + int(x / x_max * plot_w)

    def y_to_px(y: float) -> int:
        return margin_t + plot_h - int(y / y_max * plot_h)

    d.rectangle([margin_l, margin_t, margin_l + plot_w, margin_t + plot_h], outline="black")
    for i in range(n_bins):
        x0, x1 = x_to_px(i * bin_w), x_to_px((i + 1) * bin_w)
        if h_native[i]:
            d.rectangle([x0, y_to_px(h_native[i]), max(x0, x1 - 2), margin_t + plot_h],
                       fill=(70, 130, 180))

    # OCR rug: one full-height tick per observation, offset slightly so
    # coincident values are still individually countable.
    from collections import Counter as _Counter
    seen: _Counter = _Counter()
    for v in sorted(ocr_vals):
        x = x_to_px(v) + seen[round(v, 4)] * 3
        seen[round(v, 4)] += 1
        d.line([x, margin_t, x, margin_t + plot_h], fill=(220, 90, 40), width=2)
        d.polygon([(x - 4, margin_t - 2), (x + 4, margin_t - 2), (x, margin_t + 6)],
                  fill=(220, 90, 40))

    gate_x = x_to_px(gate)
    d.line([gate_x, margin_t, gate_x, margin_t + plot_h], fill="red", width=2)
    d.text((gate_x + 4, margin_t + 2), f"gate={gate}", fill="red", font=font)

    d.text((margin_l, 10),
          "orphan_start_frac: native = histogram (blue, left axis = document count); "
          "OCR = one tick per document (orange, rug plot - no y-scale)",
          fill="black", font=font)
    d.text((margin_l, 28),
          f"N native={len(native_vals)}  N ocr={len(ocr_vals)}  bin width={bin_w:.4f}  "
          f"same x-axis, same x-scale for both",
          fill="black", font=font)
    d.text((margin_l, margin_t + plot_h + 10), "orphan_start_frac ->", fill="black", font=font)
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        x = x_to_px(frac * x_max)
        d.line([x, margin_t + plot_h, x, margin_t + plot_h + 4], fill="black")
        d.text((x - 12, margin_t + plot_h + 26), f"{frac * x_max:.3f}", fill="black", font=font)
    d.text((10, margin_t + plot_h // 2), "native\ndoc\ncount", fill="black", font=font)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
    return True


# --------------------------------------------------------------- markdown

def render_markdown(report: dict[str, Any]) -> str:
    pop = report["population"]
    dist = report["distribution"]
    thr = report["threshold_diagnostics"]
    cmp_ = report["comparison"]
    notes = report["sample_size_notes"]
    top = report["top_documents"]

    def row(name: str, d: dict) -> str:
        def f(k):
            v = d.get(k)
            return "-" if v is None else f"{v:.4f}" if isinstance(v, float) else str(v)
        return (f"| {name} | {f('N')} | {f('min')} | {f('p25')} | {f('median')} "
               f"| {f('p75')} | {f('p90')} | {f('p95')} | {f('max')} |")

    def thr_block(name: str, d: dict, cross: dict | None = None) -> str:
        def f(k):
            v = d.get(k)
            return "-" if v is None else f"{v:.4f}" if isinstance(v, float) else str(v)
        out = (f"**{name}**  \n"
              f"score < {d['gate']}: {f('n_below')}  \n"
              f"score = {d['gate']}: {f('n_at')}  \n"
              f"score > {d['gate']}: {f('n_above')}  \n"
              f"fraction > {d['gate']}: {f('frac_above')}  \n"
              f"max <= {d['gate']}: {f('max_le_gate')}  \n"
              f"min > {d['gate']}: {f('min_gt_gate')}  \n"
              f"gap around {d['gate']}: {f('gap')}\n")
        if cross and cross["n_over_gate"]:
            out += (f"of the {cross['n_over_gate']} over-gate documents, "
                   f"{cross['n_over_gate_and_flagged']} actually carry "
                   f"`source_shredded`/`order_scrambled` in production's own `reasons` "
                   f"(verify.build_reasons() also requires orphan_starts > 1 - see "
                   f"methodology note); {cross['n_over_gate_but_not_flagged']} cross "
                   f"the {d['gate']} fraction without being flagged.\n")
        return out

    def top_table(rows: list[dict]) -> str:
        if not rows:
            return "_none in this population_\n"
        lines = ["| company | FY | span (pages) | orphan_start_frac | OCR engine(s) | "
                "OCR pages in span | native pages in span | grade | reasons |",
                "|---|---|---|---:|---|---|---|---|---|"]
        for r in rows:
            span = f"{r['span'][0]}-{r['span'][1]}" if r["span"] else "-"
            lines.append(
                f"| {r['company_id']} | {r['fy_end']} | {span} | {r['orphan_start_frac']:.4f} "
                f"| {', '.join(r['ocr_engines']) or '-'} "
                f"| {', '.join(map(str, r['ocr_pages_in_span'])) or '-'} "
                f"| {', '.join(map(str, r['native_pages_in_span'])) or '-'} "
                f"| {r['grade']} | {', '.join(r['reasons']) or '-'} |")
        return "\n".join(lines) + "\n"

    ocr_empty = dist["ocr"]["N"] == 0

    lines = []
    lines.append("# P-M2: native vs OCR `orphan_start_frac` distribution\n")
    lines.append(report["methodology_note"] + "\n")
    lines.append(f"Production gate measured against: `ORPHAN_START_FRAC_MAX = {report['orphan_gate']}` "
                "(read from `arpipe.verify`, never modified by this script).  \n"
                f"Metric basis: `orphan_basis = \"{report['orphan_basis_used']}\"` "
                "(the only basis pooled into the comparison below; any other basis is reported "
                "separately, never mixed in).\n")

    lines.append("## A. Population\n")
    lines.append(f"- Total manifest records: {pop['total_manifest_records']}")
    lines.append(f"- Documents with a located MD&A span: {pop['documents_with_located_span']}")
    lines.append(f"- Excluded - no located span (mda_not_located / profile_failed / pre-span quarantine): "
                 f"{pop['documents_no_span_excluded']}")
    lines.append(f"- Excluded - other/unrecorded orphan_basis: {pop['documents_other_basis_excluded'] or 'none'}")
    lines.append(f"- Documents on the primary basis (`{report['orphan_basis_used']}`): {pop['documents_primary_basis']}")
    lines.append(f"- Provenance counts (primary-basis documents): {pop['provenance_counts']}")
    lines.append(f"- Physical span-pages by class, summed across primary-basis documents: "
                 f"{pop['span_pages_by_class']}")
    if pop["unknown_provenance_documents"]:
        who = ", ".join(f"{d['company_id']}/{d['fy_end']}" for d in pop["unknown_provenance_documents"])
        lines.append(f"- Unknown-provenance documents (excluded from native/ocr/mixed): {who}\n")
    else:
        lines.append("- Unknown-provenance documents (excluded from native/ocr/mixed): none\n")

    lines.append("## B. Distribution (document / MD&A-span level)\n")
    lines.append("| Population | N | Min | P25 | Median | P75 | P90 | P95 | Max |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    lines.append(row("Native", dist["native"]))
    lines.append(row("OCR", dist["ocr"]))
    lines.append(row("Mixed", dist["mixed"]))
    lines.append("")
    lines.append(f"Percentile method: `numpy.percentile(values, q, method=\"linear\")` "
                "(pure-Python linear-interpolation fallback if numpy is absent), "
                "applied identically to both populations.\n")

    cross = report.get("production_reason_crosscheck", {})
    lines.append("## C. Threshold diagnostics\n")
    lines.append(thr_block("Native", thr["native"], cross.get("native")))
    lines.append(thr_block("OCR", thr["ocr"], cross.get("ocr")))
    lines.append(thr_block("Mixed", thr["mixed"], cross.get("mixed")))

    lines.append("## D. Interpretation\n")
    nthr, othr = thr["native"], thr["ocr"]
    lines.append("**Does 0.03 sit in an observed empty band for native text?**  ")
    if nthr["gap"] is not None:
        lines.append(f"Yes in the sense that there is an observed gap of {nthr['gap']:.4f} "
                     f"straddling the gate (max <= gate = {nthr['max_le_gate']}, "
                     f"min > gate = {nthr['min_gt_gate']}).\n")
    else:
        lines.append("Cannot say - the native population does not have observations on both "
                     "sides of the gate to measure a gap.\n")
    lines.append("**Does 0.03 sit in an observed empty band for OCR text?**  ")
    if ocr_empty:
        lines.append("Cannot say - OCR N = 0 in this corpus snapshot (see population above).\n")
    elif othr["gap"] is not None:
        lines.append(f"Observed gap of {othr['gap']:.4f} "
                     f"(max <= gate = {othr['max_le_gate']}, min > gate = {othr['min_gt_gate']}).\n")
    else:
        lines.append("Cannot say - the OCR population does not have observations on both "
                     "sides of the gate to measure a gap.\n")
    lines.append("**Is the OCR distribution materially different?**  ")
    if ocr_empty:
        lines.append("Not assessable - no OCR observations.\n")
    else:
        lines.append(f"median delta (OCR - native) = {cmp_['median_delta_ocr_minus_native']}, "
                     f"P95 delta = {cmp_['p95_delta_ocr_minus_native']}, "
                     f"fraction-above-gate delta = {cmp_['frac_above_delta_ocr_minus_native']}. "
                     "See section B/C for the full picture.\n")
    lines.append("**Is there enough OCR data to justify saying this?**  ")
    lines.append(f"{notes['ocr']}\n")
    lines.append("**Does the current evidence justify proposing a separate OCR band?**  ")
    lines.append("See section G (threshold recommendation) below.\n")

    lines.append("## E. Highest-scoring documents\n")
    lines.append("### OCR-provenance documents (top by orphan_start_frac)\n")
    lines.append(top_table(top["ocr"]))
    lines.append("\n### Native-provenance documents (top by orphan_start_frac)\n")
    lines.append(top_table(top["native"]))
    if top["mixed"]:
        lines.append("\n### Mixed-provenance documents (top by orphan_start_frac, for context)\n")
        lines.append(top_table(top["mixed"]))

    lines.append("\n## F. Regression\n")
    lines.append("```")
    lines.append("production behavior changed: NO")
    lines.append("threshold changed: NO")
    lines.append("OCR routing changed: NO")
    lines.append("grading changed: NO")
    lines.append("```\n")

    lines.append("## G. Threshold recommendation\n")
    if ocr_empty or dist["ocr"]["N"] < 10:
        lines.append("No alternate threshold can be justified from the available data "
                     f"({notes['ocr']}). `ORPHAN_START_FRAC_MAX` was not changed and no "
                     "OCR-specific band is proposed.\n")
    else:
        lines.append("PROPOSED / NOT IMPLEMENTED - review the distribution and gap figures "
                     "in sections B/C/D before proposing a number; this script does not "
                     "auto-propose one.\n")

    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------------ cli

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", required=True, help="dataset root (e.g. live_dataset)")
    ap.add_argument("--out-dir", default="reports")
    ap.add_argument("--out-prefix", default="pm2_orphan_native_vs_ocr")
    ap.add_argument("--top-n", type=int, default=10)
    a = ap.parse_args(argv)

    gate = verify.ORPHAN_START_FRAC_MAX
    basis = verify.ORPHAN_BASIS
    print(f"Loading corpus from {a.root} (gate={gate}, basis={basis}) ...", file=sys.stderr)
    records = load_corpus(a.root, progress=True)
    report = build_report(records, gate=gate, orphan_basis=basis, top_n=a.top_n)

    os.makedirs(a.out_dir, exist_ok=True)
    json_path = os.path.join(a.out_dir, f"{a.out_prefix}.json")
    md_path = os.path.join(a.out_dir, f"{a.out_prefix}.md")
    png_path = os.path.join(a.out_dir, f"{a.out_prefix}.png")

    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(render_markdown(report))

    native_vals = [r["orphan_start_frac"] for r in records
                  if r["provenance"] == "native" and r["orphan_basis"] == basis]
    ocr_vals = [r["orphan_start_frac"] for r in records
               if r["provenance"] == "ocr" and r["orphan_basis"] == basis]
    plotted = render_plot(native_vals, ocr_vals, gate, png_path)

    print(f"wrote {json_path}", file=sys.stderr)
    print(f"wrote {md_path}", file=sys.stderr)
    print(f"wrote {png_path}" if plotted else "no plot written (nothing to plot)", file=sys.stderr)
    print(f"native N={len(native_vals)} ocr N={len(ocr_vals)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
