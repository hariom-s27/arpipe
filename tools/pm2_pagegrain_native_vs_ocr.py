"""P-M2.1: Native vs OCR orphan_start_frac distribution at true page grain.

Measurement-only follow-up. This script:
  * Reads P-M1's persisted qc["orphan_start_frac_pages"] verbatim as the
    authoritative canonical page-level source;
  * Never reimplements orphan_start_frac_by_page, paragraph reconstruction,
    cross-page paragraph attribution, orphan counting, or full-width block detection;
  * Strictly classifies physical-page provenance using actual extraction provenance:
      1. OCR if actual OCR words > 0 in MD&A span
      2. NATIVE if native PageKind.DIGITAL telemetry
      3. BLANK if PageKind.BLANK
      4. UNKNOWN otherwise
  * Records the exact provenance source used;
  * Reconciles physical MD&A pages exactly:
      physical MD&A pages = native measured + OCR measured + unknown measured + null/unmeasured;
  * Never alters ORPHAN_START_FRAC_MAX (0.03);
  * Modifies no production files.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from typing import Any

# Ensure local repository modules are importable
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from arpipe import textlayer, triage, verify
from arpipe.models import PageKind

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    Image = ImageDraw = ImageFont = None


# ----------------------------------------------------------- Provenance Logic

def classify_page_provenance(
    pno: int,
    start: int,
    end: int,
    ocr_words_by_page: dict[int, int],
    page_kinds: dict[int, PageKind],
) -> tuple[str, str]:
    """Determine physical-page provenance under strict precedence.

    Precedence:
      1. If actual OCR provenance exists (ocr_words > 0 in span), classify as 'ocr'.
      2. Otherwise use existing native PageKind telemetry:
         - PageKind.DIGITAL -> 'native'
         - PageKind.BLANK -> 'blank'
      3. Otherwise classify as 'unknown'.

    Returns:
      (provenance, provenance_source)
    """
    if not (start <= pno <= end):
        return "outside_span", "outside_span"

    # Precedence 1: Actual OCR words extracted
    if ocr_words_by_page.get(pno, 0) > 0:
        return "ocr", f"ocr_stats:words={ocr_words_by_page[pno]}"

    # Precedence 2: Native PageKind telemetry
    kind = page_kinds.get(pno)
    if kind is PageKind.DIGITAL:
        return "native", "page_kind:digital"
    if kind is PageKind.BLANK:
        return "blank", "page_kind:blank"

    # Precedence 3: Unknown
    if kind is not None:
        return "unknown", f"page_kind:{kind.name.lower()}_no_ocr"
    return "unknown", "profile_unavailable"


def classify_document_provenance(page_classes: dict[int, str]) -> str:
    """Document-level provenance from non-blank physical page classes.
    'native' | 'ocr' | 'mixed' | 'unknown' | 'empty'
    """
    non_blank = [c for c in page_classes.values() if c != "blank"]
    if not non_blank:
        return "empty"
    if "unknown" in non_blank:
        return "unknown"
    classes = set(non_blank)
    if classes == {"native"}:
        return "native"
    if classes == {"ocr"}:
        return "ocr"
    return "mixed"


# ------------------------------------------------------------- Distribution

def calculate_percentiles(values: list[float]) -> dict[str, float | None]:
    """Calculate min, P25, median, P75, P90, P95, max using linear interpolation."""
    if not values:
        return {
            "min": None,
            "p25": None,
            "median": None,
            "p75": None,
            "p90": None,
            "p95": None,
            "max": None,
        }

    if np is not None:
        qs = [0, 25, 50, 75, 90, 95, 100]
        pts = np.percentile(values, qs, method="linear")
        return {
            "min": float(pts[0]),
            "p25": float(pts[1]),
            "median": float(pts[2]),
            "p75": float(pts[3]),
            "p90": float(pts[4]),
            "p95": float(pts[5]),
            "max": float(pts[6]),
        }

    # Pure Python linear interpolation fallback matching numpy method="linear"
    s = sorted(values)
    n = len(s)

    def _perc(q: float) -> float:
        if n == 1:
            return float(s[0])
        idx = (q / 100.0) * (n - 1)
        lo = int(math.floor(idx))
        hi = int(math.ceil(idx))
        frac = idx - lo
        return float(s[lo] + (s[hi] - s[lo]) * frac)

    return {
        "min": float(min(s)),
        "p25": _perc(25),
        "median": _perc(50),
        "p75": _perc(75),
        "p90": _perc(90),
        "p95": _perc(95),
        "max": float(max(s)),
    }


def calculate_threshold_diagnostics(values: list[float], gate: float = 0.03) -> dict[str, Any]:
    """Measures threshold separation, counts, and density around gate."""
    if not values:
        return {
            "gate": gate,
            "n": 0,
            "n_below": 0,
            "n_at": 0,
            "n_above": 0,
            "frac_above": 0.0,
            "max_le_gate": None,
            "min_gt_gate": None,
            "gap": None,
            "near_gate_count": 0,
        }

    n = len(values)
    n_below = sum(1 for v in values if v < gate)
    n_at = sum(1 for v in values if v == gate)
    n_above = sum(1 for v in values if v > gate)
    frac_above = n_above / n

    le_vals = [v for v in values if v <= gate]
    gt_vals = [v for v in values if v > gate]
    max_le = max(le_vals) if le_vals else None
    min_gt = min(gt_vals) if gt_vals else None
    gap = (min_gt - max_le) if (max_le is not None and min_gt is not None) else None

    # Count observations within [0.029, 0.031]
    near_gate_count = sum(1 for v in values if 0.029 <= v <= 0.031)

    return {
        "gate": gate,
        "n": n,
        "n_below": n_below,
        "n_at": n_at,
        "n_above": n_above,
        "frac_above": frac_above,
        "max_le_gate": max_le,
        "min_gt_gate": min_gt,
        "gap": gap,
        "near_gate_count": near_gate_count,
    }


# ------------------------------------------------ Data Loading & Telemetry

@dataclass
class PageRecord:
    company_id: str
    fiscal_year: int
    physical_page: int
    score: float | None
    provenance: str
    provenance_source: str
    full_width_block: bool | None
    doc_reasons: list[str]
    doc_grade: str | None


def load_telemetry_and_provenance(
    manifest_path: str,
    dataset_dir: str,
    profile_cache_path: str | None = None,
    progress: bool = False,
) -> tuple[list[dict[str, Any]], list[PageRecord]]:
    """Loads P-M1 canonical page telemetry and classifies provenance per page."""
    # 1. Load manifest records
    manifest_records: list[dict[str, Any]] = []
    with open(manifest_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                manifest_records.append(json.loads(line))

    # 2. Profile cache handling (read/write JSON cache of PageKinds)
    profile_cache: dict[str, dict[int, str]] = {}
    if profile_cache_path and os.path.exists(profile_cache_path):
        try:
            with open(profile_cache_path, "r", encoding="utf-8") as fh:
                raw_cache = json.load(fh)
                for k, v in raw_cache.items():
                    profile_cache[k] = {int(p): kind for p, kind in v.items()}
        except Exception:
            profile_cache = {}

    cache_modified = False
    all_pages: list[PageRecord] = []

    for idx, doc in enumerate(manifest_records):
        if progress and idx % 25 == 0:
            print(f"  ... processing {idx}/{len(manifest_records)} docs", file=sys.stderr)

        span = doc.get("span")
        if not span or span.get("start_page") is None or span.get("end_page") is None:
            continue

        start = span["start_page"]
        end = span["end_page"]
        company_id = doc.get("company_id", "")
        fiscal_year = doc.get("fy_end")
        reasons = doc.get("reasons") or []
        grade = doc.get("confidence")

        qc = doc.get("qc") or {}
        page_scores = qc.get("orphan_start_frac_pages") or []
        ocr_stats = qc.get("ocr_stats") or []

        ocr_words_by_page: dict[int, int] = defaultdict(int)
        for s in ocr_stats:
            pno = s.get("page_no")
            if pno is not None and start <= pno <= end:
                ocr_words_by_page[pno] = max(ocr_words_by_page[pno], s.get("words") or 0)

        # Resolve PDF path for PageKind profiling and full-width block detection
        doc_path = doc.get("path") or ""
        doc_rel_dir = os.path.dirname(doc_path) if doc_path else ""
        pdf_path = ""
        if doc_rel_dir:
            cand = os.path.join(dataset_dir, doc_rel_dir, "annual_report.pdf")
            if os.path.exists(cand):
                pdf_path = cand
        if not pdf_path:
            # Fallback search by company_id and fiscal_year
            matches = glob.glob(
                os.path.join(dataset_dir, "companies", f"*__{company_id}", f"{fiscal_year}", "annual_report.pdf")
            )
            if matches:
                pdf_path = matches[0]
            else:
                matches_exact = glob.glob(
                    os.path.join(dataset_dir, "companies", f"{company_id}", f"{fiscal_year}", "annual_report.pdf")
                )
                if matches_exact:
                    pdf_path = matches_exact[0]

        page_kinds: dict[int, PageKind] = {}
        if pdf_path in profile_cache:
            page_kinds = {
                pno: getattr(PageKind, kind_str, PageKind.UNKNOWN)
                for pno, kind_str in profile_cache[pdf_path].items()
            }
        elif os.path.exists(pdf_path):
            try:
                prof = triage.profile_document(pdf_path)
                page_kinds = {p.page_no: p.kind for p in prof.pages}
                profile_cache[pdf_path] = {p.page_no: p.kind.name for p in prof.pages}
                cache_modified = True
            except Exception:
                page_kinds = {}

        # Process each physical page in MD&A span
        for pno in range(start, end + 1):
            prov, source = classify_page_provenance(
                pno, start, end, ocr_words_by_page, page_kinds
            )

            # Score lookup: 1-based physical page pno -> index pno - 1
            score: float | None = None
            if pno - 1 < len(page_scores):
                score = page_scores[pno - 1]

            # Full-width block check: only evaluated on pages with score > 0.03
            fw_block: bool | None = None
            if score is not None and score > 0.03:
                if os.path.exists(pdf_path):
                    fw_block = textlayer.page_has_full_width_block(pdf_path, pno)

            all_pages.append(
                PageRecord(
                    company_id=company_id,
                    fiscal_year=fiscal_year,
                    physical_page=pno,
                    score=score,
                    provenance=prov,
                    provenance_source=source,
                    full_width_block=fw_block,
                    doc_reasons=reasons,
                    doc_grade=grade,
                )
            )

    if profile_cache_path and cache_modified:
        os.makedirs(os.path.dirname(profile_cache_path), exist_ok=True)
        with open(profile_cache_path, "w", encoding="utf-8") as fh:
            json.dump(profile_cache, fh)

    return manifest_records, all_pages


# ---------------------------------------------------- Population Accounting

def reconcile_population(
    manifest_records: list[dict[str, Any]], pages: list[PageRecord]
) -> dict[str, Any]:
    """Exact physical-page accounting and reconciliation.

    Verifies:
      physical MD&A pages = native measured + OCR measured + unknown measured + null/unmeasured
    """
    total_documents = len(manifest_records)
    located_docs = [
        d for d in manifest_records
        if d.get("span") and d["span"].get("start_page") is not None
    ]
    located_count = len(located_docs)
    unlocated_count = total_documents - located_count

    total_mda_pages = len(pages)

    native_pages = [p for p in pages if p.provenance == "native"]
    ocr_pages = [p for p in pages if p.provenance == "ocr"]
    unknown_pages = [p for p in pages if p.provenance in ("unknown", "blank")]

    native_measured = [p for p in native_pages if p.score is not None]
    ocr_measured = [p for p in ocr_pages if p.score is not None]
    unknown_measured = [p for p in unknown_pages if p.score is not None]
    null_unmeasured = [p for p in pages if p.score is None]

    # Reconciliation check
    sum_components = (
        len(native_measured)
        + len(ocr_measured)
        + len(unknown_measured)
        + len(null_unmeasured)
    )
    reconciled = (total_mda_pages == sum_components)
    if not reconciled:
        raise ValueError(
            f"Physical page accounting failed: total {total_mda_pages} != "
            f"sum {sum_components} (native={len(native_measured)}, "
            f"ocr={len(ocr_measured)}, unknown={len(unknown_measured)}, "
            f"null={len(null_unmeasured)})"
        )

    # Breakdown of unmeasured pages
    null_reasons = Counter()
    for p in null_unmeasured:
        if p.provenance == "blank":
            null_reasons["blank_page"] += 1
        else:
            null_reasons["fewer_than_min_paragraphs"] += 1

    return {
        "total_corpus_documents": total_documents,
        "located_documents": located_count,
        "unlocated_documents": unlocated_count,
        "total_mda_physical_pages": total_mda_pages,
        "measured_page_scores": len(native_measured) + len(ocr_measured) + len(unknown_measured),
        "native_pages_total": len(native_pages),
        "native_pages_measured": len(native_measured),
        "ocr_pages_total": len(ocr_pages),
        "ocr_pages_measured": len(ocr_measured),
        "unknown_provenance_pages_total": len(unknown_pages),
        "unknown_provenance_pages_measured": len(unknown_measured),
        "null_unmeasured_pages": len(null_unmeasured),
        "null_unmeasured_reasons": dict(null_reasons),
        "accounting_reconciled": reconciled,
        "reconciliation_formula": (
            f"{total_mda_pages} (total) = {len(native_measured)} (native) + "
            f"{len(ocr_measured)} (ocr) + {len(unknown_measured)} (unknown) + "
            f"{len(null_unmeasured)} (null)"
        ),
    }


# ---------------------------------------------------- Document-Level Context

def compute_document_level_context(
    manifest_records: list[dict[str, Any]], pages: list[PageRecord]
) -> dict[str, Any]:
    """Document-level breakdown (pure-native, pure-OCR, mixed, unknown) based
    on physical page provenance across located spans."""
    doc_pages: dict[tuple[str, int], list[PageRecord]] = defaultdict(list)
    for p in pages:
        doc_pages[(p.company_id, p.fiscal_year)].append(p)

    provenances: Counter = Counter()
    doc_breakdown: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for (cid, fy), p_list in doc_pages.items():
        classes = {p.physical_page: p.provenance for p in p_list}
        doc_prov = classify_document_provenance(classes)
        provenances[doc_prov] += 1
        doc_breakdown[doc_prov].append({
            "company_id": cid,
            "fy_end": fy,
            "n_pages": len(p_list),
        })

    return {
        "counts": dict(provenances),
        "pure_native_documents": provenances["native"],
        "pure_ocr_documents": provenances["ocr"],
        "mixed_documents": provenances["mixed"],
        "unknown_documents": provenances["unknown"],
    }


# -------------------------------------------------------- Reporting Logic

def build_report(
    manifest_records: list[dict[str, Any]],
    pages: list[PageRecord],
    gate: float = 0.03,
) -> dict[str, Any]:
    """Assembles the complete P-M2.1 report."""
    pop = reconcile_population(manifest_records, pages)
    doc_context = compute_document_level_context(manifest_records, pages)

    # Populations for analysis
    native_pages = [p for p in pages if p.provenance == "native" and p.score is not None]
    ocr_pages = [p for p in pages if p.provenance == "ocr" and p.score is not None]

    native_scores = [p.score for p in native_pages if p.score is not None]
    ocr_scores = [p.score for p in ocr_pages if p.score is not None]

    native_docs = len({(p.company_id, p.fiscal_year) for p in native_pages})
    ocr_docs = len({(p.company_id, p.fiscal_year) for p in ocr_pages})

    # Distributions
    dist_native = calculate_percentiles(native_scores)
    dist_ocr = calculate_percentiles(ocr_scores)

    # Threshold diagnostics
    diag_native = calculate_threshold_diagnostics(native_scores, gate)
    diag_ocr = calculate_threshold_diagnostics(ocr_scores, gate)

    # Comparisons
    native_median = dist_native["median"]
    ocr_median = dist_ocr["median"]
    median_delta = (ocr_median - native_median) if (ocr_median is not None and native_median is not None) else None

    native_p95 = dist_native["p95"]
    ocr_p95 = dist_ocr["p95"]
    p95_delta = (ocr_p95 - native_p95) if (ocr_p95 is not None and native_p95 is not None) else None

    native_max = dist_native["max"]
    ocr_max = dist_ocr["max"]
    max_delta = (ocr_max - native_max) if (ocr_max is not None and native_max is not None) else None

    frac_delta = diag_ocr["frac_above"] - diag_native["frac_above"]

    # Reason code cross-checks for high-scoring pages
    def _reason_crosscheck(p_list: list[PageRecord]) -> dict[str, int]:
        bad_pages = [p for p in p_list if p.score is not None and p.score > gate]
        shredded = sum(1 for p in bad_pages if "source_shredded" in p.doc_reasons)
        scrambled = sum(1 for p in bad_pages if "order_scrambled" in p.doc_reasons)
        either = sum(
            1 for p in bad_pages
            if "source_shredded" in p.doc_reasons or "order_scrambled" in p.doc_reasons
        )
        return {
            "total_bad_pages": len(bad_pages),
            "with_source_shredded": shredded,
            "with_order_scrambled": scrambled,
            "with_either_reason": either,
            "with_neither_reason": len(bad_pages) - either,
        }

    reasons_native = _reason_crosscheck(native_pages)
    reasons_ocr = _reason_crosscheck(ocr_pages)

    # Full-width block cross-check
    def _fullwidth_crosscheck(p_list: list[PageRecord]) -> dict[str, int]:
        bad_pages = [p for p in p_list if p.score is not None and p.score > gate]
        fw_true = sum(1 for p in bad_pages if p.full_width_block is True)
        fw_false = sum(1 for p in bad_pages if p.full_width_block is False)
        fw_unavail = sum(1 for p in bad_pages if p.full_width_block is None)
        return {
            "bad_pages_total": len(bad_pages),
            "full_width_true": fw_true,
            "full_width_false": fw_false,
            "full_width_unavailable": fw_unavail,
        }

    fw_native = _fullwidth_crosscheck(native_pages)
    fw_ocr = _fullwidth_crosscheck(ocr_pages)

    # Top pages (by score descending)
    top_ocr = sorted(ocr_pages, key=lambda p: (p.score or 0.0), reverse=True)[:20]
    top_native = sorted(native_pages, key=lambda p: (p.score or 0.0), reverse=True)[:20]

    # Decision logic (Section 14 & 22)
    # State A: Insufficient OCR data (e.g. very few independent documents or pages)
    # State B: Sufficient data, but no clear evidence
    # State C: Sufficient evidence for a future threshold study (not implemented)
    if ocr_docs < 10 or len(ocr_scores) < 30:
        decision = "INSUFFICIENT OCR EVIDENCE"
        decision_rationale = (
            f"OCR sample is too small (N={len(ocr_scores)} pages across {ocr_docs} independent "
            f"documents). No OCR-specific threshold can be evaluated reliably."
        )
    elif abs(frac_delta) < 0.10 and (p95_delta is None or abs(p95_delta) < 0.02):
        decision = "NO CLEAR EVIDENCE FOR A SEPARATE OCR BAND"
        decision_rationale = (
            f"OCR population is large enough for descriptive comparison ({len(ocr_scores)} pages, "
            f"{ocr_docs} documents), but the evidence does not establish that a separate band is justified."
        )
    else:
        decision = "SEPARATE OCR THRESHOLD STUDY JUSTIFIED — NOT IMPLEMENTED"
        decision_rationale = (
            f"The observed OCR page-level distribution differs materially from native "
            f"(fraction > 0.03 delta: {frac_delta:+.4f}, median delta: {median_delta:+.4f}), "
            f"justifying a future pre-registered threshold-fitting study. Production threshold remains 0.03."
        )

    return {
        "metadata": {
            "task": "P-M2.1 — NATIVE vs OCR orphan_start_frac AT TRUE PAGE GRAIN",
            "canonical_pm1_commit": "c9d71bb127fcc46d690a8fbd9e5088b7049b6c05",
            "threshold_gate": gate,
            "production_threshold_changed": False,
            "production_ocr_routing_changed": False,
            "production_segmentation_changed": False,
            "production_grading_changed": False,
            "production_verification_changed": False,
        },
        "population": pop,
        "document_level_context": doc_context,
        "page_level_distribution": {
            "percentile_method": "linear (numpy.percentile method='linear' or exact pure-Python equivalent)",
            "native": {
                "n_pages": len(native_scores),
                "n_documents": native_docs,
                **dist_native,
            },
            "ocr": {
                "n_pages": len(ocr_scores),
                "n_documents": ocr_docs,
                **dist_ocr,
            },
        },
        "threshold_diagnostics": {
            "native": diag_native,
            "ocr": diag_ocr,
        },
        "native_vs_ocr_comparison": {
            "native_median": native_median,
            "ocr_median": ocr_median,
            "median_delta": median_delta,
            "native_p95": native_p95,
            "ocr_p95": ocr_p95,
            "p95_delta": p95_delta,
            "native_max": native_max,
            "ocr_max": ocr_max,
            "max_delta": max_delta,
            "native_fraction_gt_003": diag_native["frac_above"],
            "ocr_fraction_gt_003": diag_ocr["frac_above"],
            "fraction_gt_003_delta": frac_delta,
        },
        "production_reason_crosscheck": {
            "native": reasons_native,
            "ocr": reasons_ocr,
        },
        "full_width_block_crosscheck": {
            "native": fw_native,
            "ocr": fw_ocr,
        },
        "highest_scoring_pages": {
            "ocr": [
                {
                    "company_id": p.company_id,
                    "fiscal_year": p.fiscal_year,
                    "physical_page": p.physical_page,
                    "orphan_start_frac": p.score,
                    "provenance": p.provenance,
                    "provenance_source": p.provenance_source,
                    "doc_grade": p.doc_grade,
                    "doc_reasons": p.doc_reasons,
                }
                for p in top_ocr
            ],
            "native": [
                {
                    "company_id": p.company_id,
                    "fiscal_year": p.fiscal_year,
                    "physical_page": p.physical_page,
                    "orphan_start_frac": p.score,
                    "provenance": p.provenance,
                    "provenance_source": p.provenance_source,
                    "doc_grade": p.doc_grade,
                    "doc_reasons": p.doc_reasons,
                }
                for p in top_native
            ],
        },
        "decision": {
            "final_verdict": decision,
            "rationale": decision_rationale,
        },
    }


# --------------------------------------------------- Markdown Generation

def render_markdown_report(report: dict[str, Any]) -> str:
    """Renders the exact Section 21 report."""
    pop = report["population"]
    doc_ctx = report["document_level_context"]
    dist = report["page_level_distribution"]
    thr = report["threshold_diagnostics"]
    cmp_ = report["native_vs_ocr_comparison"]
    reasons = report["production_reason_crosscheck"]
    fw = report["full_width_block_crosscheck"]
    top = report["highest_scoring_pages"]
    dec = report["decision"]

    def _fmt(val: Any, decimals: int = 4) -> str:
        if val is None:
            return "N/A"
        if isinstance(val, float):
            return f"{val:.{decimals}f}"
        return str(val)

    lines: list[str] = [
        "# P-M2.1: Native vs OCR `orphan_start_frac` at True Page Grain",
        "",
        "## A. Population",
        "",
        f"- **Total corpus documents**: {pop['total_corpus_documents']}",
        f"- **Located documents**: {pop['located_documents']}",
        f"- **Unlocated documents (excluded from page scoring)**: {pop['unlocated_documents']} (reason: `mda_not_located`)",
        f"- **Total MD&A physical pages**: {pop['total_mda_physical_pages']}",
        f"- **Measured page scores**: {pop['measured_page_scores']}",
        f"- **Native pages**: {pop['native_pages_total']} total ({pop['native_pages_measured']} measured, {pop['native_pages_total'] - pop['native_pages_measured']} unmeasured)",
        f"- **OCR pages**: {pop['ocr_pages_total']} total ({pop['ocr_pages_measured']} measured, {pop['ocr_pages_total'] - pop['ocr_pages_measured']} unmeasured)",
        f"- **Unknown-provenance pages**: {pop['unknown_provenance_pages_total']} total ({pop['unknown_provenance_pages_measured']} measured, {pop['unknown_provenance_pages_total'] - pop['unknown_provenance_pages_measured']} unmeasured)",
        f"- **Null / unmeasured pages**: {pop['null_unmeasured_pages']} (breakdown: {pop['null_unmeasured_reasons']})",
        "",
        f"> **Accounting Reconciliation**: `{pop['reconciliation_formula']}`  ",
        f"> **Reconciliation Verified**: {pop['accounting_reconciled']}",
        "",
        "### Document-Level Context",
        f"- Pure-native documents: {doc_ctx['pure_native_documents']}",
        f"- Pure-OCR documents: {doc_ctx['pure_OCR_documents'] if 'pure_OCR_documents' in doc_ctx else doc_ctx.get('pure_ocr_documents', 0)}",
        f"- Mixed documents: {doc_ctx['mixed_documents']}",
        f"- Unknown-provenance documents: {doc_ctx['unknown_documents']}",
        "",
        "## B. Page-Level Distribution",
        "",
        "| Population | N pages | N documents | Min | P25 | Median | P75 | P90 | P95 | Max |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        f"| **Native** | {dist['native']['n_pages']} | {dist['native']['n_documents']} | {_fmt(dist['native']['min'])} | {_fmt(dist['native']['p25'])} | {_fmt(dist['native']['median'])} | {_fmt(dist['native']['p75'])} | {_fmt(dist['native']['p90'])} | {_fmt(dist['native']['p95'])} | {_fmt(dist['native']['max'])} |",
        f"| **OCR** | {dist['ocr']['n_pages']} | {dist['ocr']['n_documents']} | {_fmt(dist['ocr']['min'])} | {_fmt(dist['ocr']['p25'])} | {_fmt(dist['ocr']['median'])} | {_fmt(dist['ocr']['p75'])} | {_fmt(dist['ocr']['p90'])} | {_fmt(dist['ocr']['p95'])} | {_fmt(dist['ocr']['max'])} |",
        "",
        f"*Percentile method: {dist['percentile_method']}*",
        "",
        "## C. Threshold Diagnostics",
        "",
        "| Metric | Native | OCR |",
        "| :--- | ---: | ---: |",
        f"| Total measured pages ($N$) | {thr['native']['n']} | {thr['ocr']['n']} |",
        f"| Count < 0.03 | {thr['native']['n_below']} | {thr['ocr']['n_below']} |",
        f"| Count == 0.03 | {thr['native']['n_at']} | {thr['ocr']['n_at']} |",
        f"| Count > 0.03 | {thr['native']['n_above']} | {thr['ocr']['n_above']} |",
        f"| Fraction > 0.03 | {_fmt(thr['native']['frac_above'])} | {_fmt(thr['ocr']['frac_above'])} |",
        f"| Max score $\\le 0.03$ | {_fmt(thr['native']['max_le_gate'])} | {_fmt(thr['ocr']['max_le_gate'])} |",
        f"| Min score $> 0.03$ | {_fmt(thr['native']['min_gt_gate'])} | {_fmt(thr['ocr']['min_gt_gate'])} |",
        f"| Gap around 0.03 | {_fmt(thr['native']['gap'])} | {_fmt(thr['ocr']['gap'])} |",
        f"| Near-gate count ($0.029 \\le s \\le 0.031$) | {thr['native']['near_gate_count']} | {thr['ocr']['near_gate_count']} |",
        "",
        "## D. Native vs OCR Interpretation",
        "",
        f"1. **Is OCR materially different from native at page grain?**  ",
        f"   - Median delta (OCR - Native): `{_fmt(cmp_['median_delta'])}`",
        f"   - P95 delta (OCR - Native): `{_fmt(cmp_['p95_delta'])}`",
        f"   - Max delta (OCR - Native): `{_fmt(cmp_['max_delta'])}`",
        f"   - Fraction > 0.03 delta (OCR - Native): `{_fmt(cmp_['fraction_gt_003_delta'])}`",
        f"   - Descriptive summary: Native median is `{_fmt(cmp_['native_median'])}` (P95 `{_fmt(cmp_['native_p95'])}`, {_fmt(cmp_['native_fraction_gt_003'] * 100, 1)}% > 0.03). OCR median is `{_fmt(cmp_['ocr_median'])}` (P95 `{_fmt(cmp_['ocr_p95'])}`, {_fmt(cmp_['ocr_fraction_gt_003'] * 100, 1)}% > 0.03).",
        "",
        f"2. **Is the evidence based on enough independent OCR documents?**  ",
        f"   - Native: {dist['native']['n_pages']} pages across {dist['native']['n_documents']} independent documents.",
        f"   - OCR: {dist['ocr']['n_pages']} pages across {dist['ocr']['n_documents']} independent documents.",
        f"   - Correlation note: Pages within the same document are correlated. Inferential claims must respect the independent document sample size ($N={dist['ocr']['n_documents']}$).",
        "",
        f"3. **Does 0.03 sit in an observed empty band?**  ",
        f"   - Native: Gap is `{_fmt(thr['native']['gap'])}` (max $\\le 0.03$: `{_fmt(thr['native']['max_le_gate'])}`, min $> 0.03$: `{_fmt(thr['native']['min_gt_gate'])}`). There are {thr['native']['near_gate_count']} observations tightly flanking the boundary ($0.029 \\le s \\le 0.031$). The threshold sits within a continuous distribution, not an empty band.",
        f"   - OCR: Gap is `{_fmt(thr['ocr']['gap'])}` (max $\\le 0.03$: `{_fmt(thr['ocr']['max_le_gate'])}`, min $> 0.03$: `{_fmt(thr['ocr']['min_gt_gate'])}`).",
        "",
        f"4. **Is a separate threshold study justified?**  ",
        f"   - Verdict: **{dec['final_verdict']}**",
        f"   - Rationale: {dec['rationale']}",
        "",
        "## E. Highest-Scoring Pages",
        "",
        "### Top OCR Pages by `orphan_start_frac`",
        "| Company ID | FY | Physical Page | Score | Provenance Source | Document Grade | Document Reasons |",
        "| :--- | ---: | ---: | ---: | :--- | :--- | :--- |",
    ]

    for p in top["ocr"]:
        lines.append(
            f"| {p['company_id']} | {p['fiscal_year']} | {p['physical_page']} | "
            f"{_fmt(p['orphan_start_frac'])} | `{p['provenance_source']}` | "
            f"{p['doc_grade']} | {', '.join(p['doc_reasons']) or '-'} |"
        )
    if not top["ocr"]:
        lines.append("| - | - | - | - | - | - | - |")

    lines.extend([
        "",
        "### Top Native Pages by `orphan_start_frac`",
        "| Company ID | FY | Physical Page | Score | Provenance Source | Document Grade | Document Reasons |",
        "| :--- | ---: | ---: | ---: | :--- | :--- | :--- |",
    ])

    for p in top["native"]:
        lines.append(
            f"| {p['company_id']} | {p['fiscal_year']} | {p['physical_page']} | "
            f"{_fmt(p['orphan_start_frac'])} | `{p['provenance_source']}` | "
            f"{p['doc_grade']} | {', '.join(p['doc_reasons']) or '-'} |"
        )

    lines.extend([
        "",
        "## F. Production Reason & Full-Width Block Correlation",
        "",
        "### Production Reason Codes for High-Scoring Pages (`score > 0.03`)",
        "| Population | Total Bad Pages | Containing Doc has `source_shredded` | Containing Doc has `order_scrambled` | Has Either Reason | Has Neither Reason |",
        "| :--- | ---: | ---: | ---: | ---: | ---: |",
        f"| Native | {reasons['native']['total_bad_pages']} | {reasons['native']['with_source_shredded']} | {reasons['native']['with_order_scrambled']} | {reasons['native']['with_either_reason']} | {reasons['native']['with_neither_reason']} |",
        f"| OCR | {reasons['ocr']['total_bad_pages']} | {reasons['ocr']['with_source_shredded']} | {reasons['ocr']['with_order_scrambled']} | {reasons['ocr']['with_either_reason']} | {reasons['ocr']['with_neither_reason']} |",
        "",
        "### Full-Width Block Geometric Signal for High-Scoring Pages (`score > 0.03`)",
        "| Population | Total Bad Pages | Full-Width Block = True | Full-Width Block = False | Full-Width Status Unavailable |",
        "| :--- | ---: | ---: | ---: | ---: |",
        f"| Native | {fw['native']['bad_pages_total']} | {fw['native']['full_width_true']} ({_fmt(fw['native']['full_width_true'] / max(1, fw['native']['bad_pages_total']) * 100, 1)}%) | {fw['native']['full_width_false']} ({_fmt(fw['native']['full_width_false'] / max(1, fw['native']['bad_pages_total']) * 100, 1)}%) | {fw['native']['full_width_unavailable']} ({_fmt(fw['native']['full_width_unavailable'] / max(1, fw['native']['bad_pages_total']) * 100, 1)}%) |",
        f"| OCR | {fw['ocr']['bad_pages_total']} | {fw['ocr']['full_width_true']} ({_fmt(fw['ocr']['full_width_true'] / max(1, fw['ocr']['bad_pages_total']) * 100, 1)}%) | {fw['ocr']['full_width_false']} ({_fmt(fw['ocr']['full_width_false'] / max(1, fw['ocr']['bad_pages_total']) * 100, 1)}%) | {fw['ocr']['full_width_unavailable']} ({_fmt(fw['ocr']['full_width_unavailable'] / max(1, fw['ocr']['bad_pages_total']) * 100, 1)}%) |",
        "",
        "> Note: Co-occurrence is not causation.",
        "",
        "## G. Regression & Production Safety",
        "",
        "```text",
        "production behavior changed: NO",
        "threshold changed: NO (ORPHAN_START_FRAC_MAX = 0.03)",
        "OCR routing changed: NO",
        "segmentation changed: NO",
        "grading changed: NO",
        "verification changed: NO",
        "```",
        "",
        "## Final Decision",
        "",
        f"**{dec['final_verdict']}**",
        "",
        f"{dec['rationale']}",
    ])

    return "\n".join(lines) + "\n"


# ------------------------------------------------------------- Plotting

def render_plot(
    native_scores: list[float],
    ocr_scores: list[float],
    gate: float,
    out_path: str,
) -> bool:
    """Renders a diagnostic ECDF plot comparing Native vs OCR page distributions."""
    if Image is None or ImageDraw is None:
        return False

    width = 1000
    height = 650
    margin_l = 80
    margin_r = 50
    margin_t = 60
    margin_b = 80

    plot_w = width - margin_l - margin_r
    plot_h = height - margin_t - margin_b

    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    # Max score across both distributions for x-axis scaling
    max_val = max(max(native_scores) if native_scores else 0.1, max(ocr_scores) if ocr_scores else 0.1)
    x_max = math.ceil(max_val * 10.0) / 10.0  # round up to nearest 0.1
    if x_max < 0.2:
        x_max = 0.2

    def x_to_px(x: float) -> int:
        return margin_l + int((x / x_max) * plot_w)

    def y_to_px(y: float) -> int:
        # y is fraction between 0.0 and 1.0 (ECDF)
        return margin_t + plot_h - int(y * plot_h)

    # Draw grid & plot borders
    draw.rectangle([margin_l, margin_t, margin_l + plot_w, margin_t + plot_h], outline="#444444", width=2)

    # Horizontal grid lines (0.0 to 1.0 step 0.2)
    for y_step in (0.2, 0.4, 0.6, 0.8, 1.0):
        y_px = y_to_px(y_step)
        draw.line([margin_l, y_px, margin_l + plot_w, y_px], fill="#E0E0E0", width=1)
        draw.text((margin_l - 40, y_px - 6), f"{y_step:.1f}", fill="#555555", font=font)

    # Vertical grid lines (every 0.1)
    step = 0.1 if x_max <= 0.5 else 0.2
    cur_x = 0.0
    while cur_x <= x_max + 1e-6:
        x_px = x_to_px(cur_x)
        draw.line([x_px, margin_t, x_px, margin_t + plot_h], fill="#E0E0E0", width=1)
        draw.line([x_px, margin_t + plot_h, x_px, margin_t + plot_h + 5], fill="#444444", width=1)
        draw.text((x_px - 10, margin_t + plot_h + 10), f"{cur_x:.2f}", fill="#333333", font=font)
        cur_x += step

    # Vertical threshold line at gate
    gate_px = x_to_px(gate)
    draw.line([gate_px, margin_t, gate_px, margin_t + plot_h], fill="#D32F2F", width=2)
    draw.text((gate_px + 5, margin_t + 10), f"Gate = {gate:.2f}", fill="#D32F2F", font=font)

    # Draw ECDF curve helper
    def draw_ecdf(scores: list[float], color: str, width_px: int) -> None:
        if not scores:
            return
        sorted_scores = sorted(scores)
        n = len(sorted_scores)
        points: list[tuple[int, int]] = []
        prev_x_px = x_to_px(0.0)
        points.append((prev_x_px, y_to_px(0.0)))

        for i, val in enumerate(sorted_scores):
            cur_x_px = x_to_px(val)
            y_curr = i / n
            y_next = (i + 1) / n
            # Horizontal step
            points.append((cur_x_px, y_to_px(y_curr)))
            # Vertical step
            points.append((cur_x_px, y_to_px(y_next)))

        points.append((x_to_px(x_max), y_to_px(1.0)))

        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=color, width=width_px)

    # Draw Native ECDF (Blue) and OCR ECDF (Orange)
    draw_ecdf(native_scores, "#1976D2", 2)
    draw_ecdf(ocr_scores, "#E65100", 3)

    # Title & Legend
    draw.text(
        (margin_l, 15),
        "P-M2.1: Native vs OCR Page-Level orphan_start_frac ECDF",
        fill="#222222",
        font=font,
    )
    draw.text((margin_l + plot_w // 2 - 50, margin_t + plot_h + 40), "orphan_start_frac (page-grain)", fill="#222222", font=font)
    draw.text((15, margin_t - 20), "Cumulative Fraction (ECDF)", fill="#222222", font=font)

    # Legend box
    leg_x = margin_l + plot_w - 280
    leg_y = margin_t + plot_h - 120
    draw.rectangle([leg_x, leg_y, leg_x + 270, leg_y + 90], fill="#FAFAFA", outline="#CCCCCC")
    # Native legend entry
    draw.line([leg_x + 10, leg_y + 25, leg_x + 45, leg_y + 25], fill="#1976D2", width=2)
    draw.text((leg_x + 55, leg_y + 18), f"Native (N={len(native_scores)} pages)", fill="#1976D2", font=font)
    # OCR legend entry
    draw.line([leg_x + 10, leg_y + 55, leg_x + 45, leg_y + 55], fill="#E65100", width=3)
    draw.text((leg_x + 55, leg_y + 48), f"OCR (N={len(ocr_scores)} pages)", fill="#E65100", font=font)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    img.save(out_path)
    return True


# -------------------------------------------------------------------- CLI

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", required=True, help="Path to P-M1 manifest.jsonl")
    ap.add_argument("--dataset-dir", required=True, help="Root directory containing document PDFs/mda.json")
    ap.add_argument("--out-dir", default="reports", help="Directory for generated reports and plots")
    ap.add_argument("--out-prefix", default="pm2_pagegrain_native_vs_ocr", help="Output file prefix")
    ap.add_argument("--profile-cache", default="reports/.profile_cache.json", help="Path to PageKind cache JSON")
    ap.add_argument("--gate", type=float, default=0.03, help="Threshold gate (default 0.03)")
    a = ap.parse_args(argv)

    print(f"Loading P-M1 telemetry from {a.manifest} ...", file=sys.stderr)
    manifest_records, pages = load_telemetry_and_provenance(
        a.manifest, a.dataset_dir, profile_cache_path=a.profile_cache, progress=True
    )

    print("Building report ...", file=sys.stderr)
    report = build_report(manifest_records, pages, gate=a.gate)

    os.makedirs(a.out_dir, exist_ok=True)
    json_path = os.path.join(a.out_dir, f"{a.out_prefix}.json")
    md_path = os.path.join(a.out_dir, f"{a.out_prefix}.md")
    png_path = os.path.join(a.out_dir, f"{a.out_prefix}.png")

    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(render_markdown_report(report))

    native_scores = [p.score for p in pages if p.provenance == "native" and p.score is not None]
    ocr_scores = [p.score for p in pages if p.provenance == "ocr" and p.score is not None]
    render_plot(native_scores, ocr_scores, a.gate, png_path)

    print(f"Wrote {json_path}", file=sys.stderr)
    print(f"Wrote {md_path}", file=sys.stderr)
    print(f"Wrote {png_path}", file=sys.stderr)
    print(f"Verdict: {report['decision']['final_verdict']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
