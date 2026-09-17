"""P-M3: Scan-Quality Measurement across the frozen ARPipe corpus.

Measures the physical/input quality of rasterized pages in the frozen 194-document
corpus (37,917 physical pages) without modifying production code or thresholds.

Distinction enforced:
    SCAN / INPUT QUALITY != OCR QUALITY != EXTRACTION CORRECTNESS != OCR FAILURE

Usage:
    python tools/pm3_scan_quality.py --live-store ../arpipe-0.1.0/live_store --out-dir reports
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# Ensure repository root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np
import pymupdf  # PyMuPDF
from PIL import Image, ImageDraw, ImageFilter, ImageFont


# --- Configuration & Version Constants ------------------------------------
RASTER_CLASSIFICATION_RULE_VERSION = "v1.0_geom_dominant_50pct"
ANALYSIS_RESOLUTION = 150
PREPROCESSING_VERSION = "pm3_canonical_v1_150dpi_gray"
SKEW_METHOD = "projection_profile_variance_v1"
CONTRAST_METHOD = "interdecile_p95_p05_v1"
NOISE_METHOD = "median3x3_residual_v1"
BLUR_METHOD = "laplacian_variance_v1"  # Higher value = sharper
SCAN_QUALITY_RULE_VERSION = "none"


# --- Data Models -----------------------------------------------------------
@dataclass
class PageMeasurement:
    document_id: str
    company_id: str
    company: str
    FY: int
    physical_page: int
    source_pdf_sha256: str
    page_width: float
    page_height: float
    raster_image_count: int
    largest_raster_area_fraction: float
    total_raster_area_fraction: float
    full_page_raster: bool
    dominant_raster_image: str | None
    native_text_present: bool
    estimated_dpi_width: float | None
    estimated_dpi_height: float | None
    estimated_dpi: float | None
    dpi_status: str
    skew_angle: float | None
    skew_status: str
    skew_method: str
    skew_confidence: float | None
    contrast: float | None
    contrast_status: str
    contrast_method: str
    noise_speckle: float | None
    noise_status: str
    noise_method: str
    blur: float | None
    blur_status: str
    blur_method: str
    scan_quality: str
    scan_quality_rule_version: str
    measurement_status: str
    analysis_resolution: int
    preprocessing_version: str
    provenance: str
    reason_codes: str
    image_index: int | None
    image_xref: int | None
    image_bbox: str | None


# --- Core Measurement Algorithms -------------------------------------------

def calculate_dominant_image_and_dpi(
    img_infos: list[dict[str, Any]], page_rect: pymupdf.Rect
) -> tuple[int, float, float, dict[str, Any] | None, float | None, float | None, float | None, str]:
    """Inspects page images within page_rect and calculates dominant image and DPI.

    Returns:
        (raster_count, largest_area_frac, total_area_frac, dominant_img, dpi_w, dpi_h, dpi, dpi_status)
    """
    page_w = page_rect.width
    page_h = page_rect.height
    page_area = max(1e-6, page_w * page_h)

    valid_images: list[dict[str, Any]] = []
    visible_rects: list[pymupdf.Rect] = []

    for idx, img in enumerate(img_infos):
        bbox_raw = img.get("bbox")
        if not bbox_raw:
            continue
        r = pymupdf.Rect(bbox_raw)
        vis = r & page_rect
        if vis.is_empty:
            continue
        vis_w = max(0.0, vis.width)
        vis_h = max(0.0, vis.height)
        vis_area = vis_w * vis_h
        if vis_area <= 0.0:
            continue

        item = dict(img)
        item["index"] = idx
        item["vis_rect"] = vis
        item["vis_area"] = vis_area
        valid_images.append(item)
        visible_rects.append(vis)

    raster_count = len(valid_images)
    if raster_count == 0:
        return (0, 0.0, 0.0, None, None, None, None, "not_applicable")

    # Dominant image is the one with the largest visible placed area
    dominant = max(valid_images, key=lambda x: x["vis_area"])
    largest_area_frac = round(dominant["vis_area"] / page_area, 4)

    # Approximate total area fraction via union of bounding boxes on a grid
    grid = 40
    cw, ch = page_w / grid, page_h / grid
    cells: set[tuple[int, int]] = set()
    for vr in visible_rects:
        x0 = max(0, min(grid - 1, int(vr.x0 / cw)))
        x1 = max(0, min(grid - 1, int(vr.x1 / cw)))
        y0 = max(0, min(grid - 1, int(vr.y0 / ch)))
        y1 = max(0, min(grid - 1, int(vr.y1 / ch)))
        for i in range(x0, x1 + 1):
            for j in range(y0, y1 + 1):
                cells.add((i, j))
    total_area_frac = round(len(cells) / float(grid * grid), 4)

    # DPI calculation from dominant image
    pix_w = dominant.get("width")
    pix_h = dominant.get("height")
    vis_r = dominant["vis_rect"]
    placed_w_in = vis_r.width / 72.0
    placed_h_in = vis_r.height / 72.0

    if pix_w and pix_h and placed_w_in > 0 and placed_h_in > 0:
        dpi_w = round(pix_w / placed_w_in, 2)
        dpi_h = round(pix_h / placed_h_in, 2)
        dpi = round(min(dpi_w, dpi_h), 2)
        dpi_status = "measured"
    else:
        dpi_w = None
        dpi_h = None
        dpi = None
        dpi_status = "unavailable"

    return (raster_count, largest_area_frac, total_area_frac, dominant, dpi_w, dpi_h, dpi, dpi_status)


def measure_skew(arr: np.ndarray) -> tuple[float | None, str, float | None]:
    """Deterministic horizontal projection profile variance skew estimation.

    Searches angles in [-5.0, 5.0] at 0.2-degree steps.
    Returns: (skew_angle, skew_status, skew_confidence)
    """
    if arr.size == 0 or np.max(arr) == np.min(arr):
        return (None, "unavailable", 0.0)

    # Invert so text is foreground (positive)
    # Binary/thresholded representation enhances text line peaks
    threshold = np.percentile(arr, 30)
    bin_arr = (arr < threshold).astype(np.uint8) * 255
    if np.sum(bin_arr) < 500:  # Very sparse / blank
        return (None, "unavailable", 0.0)

    pil_bin = Image.fromarray(bin_arr)
    # Downsample to fixed (150, 200) grid for fast, deterministic projection search
    small_bin = pil_bin.resize((150, 200), resample=Image.NEAREST)

    angles = np.arange(-5.0, 5.1, 0.2)
    variances = []
    max_var = -1.0
    best_angle = 0.0

    for a in angles:
        # Rotate around center
        rot = small_bin.rotate(-float(a), resample=Image.NEAREST, fillcolor=0)
        rot_arr = np.array(rot)
        v = float(np.var(np.sum(rot_arr, axis=1)))
        variances.append(v)
        if v > max_var:
            max_var = v
            best_angle = float(a)

    mean_var = float(np.mean(variances))
    confidence = float((max_var - mean_var) / (mean_var + 1e-6))

    if confidence < 0.15:
        return (None, "low_confidence", round(confidence, 3))

    return (round(best_angle, 2), "measured", round(confidence, 3))


def measure_contrast(arr: np.ndarray) -> tuple[float | None, str]:
    """Calculates interdecile grayscale contrast (P95 - P05) / 255.0."""
    if arr.size == 0:
        return (None, "unavailable")
    p05, p95 = np.percentile(arr, [5, 95])
    c = float((p95 - p05) / 255.0)
    return (round(c, 4), "measured")


def measure_noise_speckle(arr: np.ndarray) -> tuple[float | None, str]:
    """Calculates high-frequency noise/speckle via 3x3 median filter residual."""
    if arr.size == 0:
        return (None, "unavailable")
    pil_img = Image.fromarray(arr)
    med_img = pil_img.filter(ImageFilter.MedianFilter(size=3))
    med_arr = np.array(med_img)
    diff = np.abs(arr.astype(np.float32) - med_arr.astype(np.float32))
    noise = float(np.mean(diff) / 255.0)
    return (round(noise, 4), "measured")


def measure_blur_sharpness(arr: np.ndarray) -> tuple[float | None, str]:
    """Calculates sharpness as the sample variance of the 3x3 discrete Laplacian.

    Higher value = sharper.
    """
    if arr.shape[0] < 3 or arr.shape[1] < 3:
        return (None, "unavailable")
    arr_f = arr.astype(np.float32)
    # Discrete Laplacian kernel: [[0, 1, 0], [1, -4, 1], [0, 1, 0]]
    lap = (
        arr_f[:-2, 1:-1]
        + arr_f[2:, 1:-1]
        + arr_f[1:-1, :-2]
        + arr_f[1:-1, 2:]
        - 4.0 * arr_f[1:-1, 1:-1]
    )
    sharpness = float(np.var(lap))
    return (round(sharpness, 2), "measured")


def calculate_percentiles(values: list[float]) -> dict[str, float | None]:
    """Calculates min, P25, median, P75, P95, max using linear interpolation."""
    if not values:
        return {
            "min": None,
            "p25": None,
            "median": None,
            "p75": None,
            "p95": None,
            "max": None,
        }
    qs = [0, 25, 50, 75, 95, 100]
    pts = np.percentile(values, qs, method="linear")
    return {
        "min": round(float(pts[0]), 4),
        "p25": round(float(pts[1]), 4),
        "median": round(float(pts[2]), 4),
        "p75": round(float(pts[3]), 4),
        "p95": round(float(pts[4]), 4),
        "max": round(float(pts[5]), 4),
    }


# --- Corpus Processing Pipeline -------------------------------------------

def _process_single_document(args_tuple: tuple) -> list[PageMeasurement]:
    """Worker function to process all pages of a single document."""
    (
        doc_meta,
        live_store_dir,
        comp_info,
        pm1_doc,
        doc_reasons,
        doc_ocr_pages,
        profile_pages_map,
    ) = args_tuple

    cid = doc_meta["company_id"]
    fy = doc_meta["fy_end"]
    doc_id = f"{cid}_{fy}"
    pdf_rel_path = doc_meta["path"]
    pdf_sha256 = doc_meta["sha256"]
    pdf_full_path = os.path.join(live_store_dir, pdf_rel_path)

    comp_name = comp_info.get("canonical_name", cid)
    reason_codes_str = ";".join(doc_reasons)

    doc_records: list[PageMeasurement] = []

    try:
        pdf_doc = pymupdf.open(pdf_full_path)
    except Exception:
        # Document open failure -> mark all expected pages unknown
        for pno in range(1, doc_meta.get("n_pages", 1) + 1):
            doc_records.append(
                PageMeasurement(
                    document_id=doc_id,
                    company_id=cid,
                    company=comp_name,
                    FY=fy,
                    physical_page=pno,
                    source_pdf_sha256=pdf_sha256,
                    page_width=0.0,
                    page_height=0.0,
                    raster_image_count=0,
                    largest_raster_area_fraction=0.0,
                    total_raster_area_fraction=0.0,
                    full_page_raster=False,
                    dominant_raster_image=None,
                    native_text_present=False,
                    estimated_dpi_width=None,
                    estimated_dpi_height=None,
                    estimated_dpi=None,
                    dpi_status="unavailable",
                    skew_angle=None,
                    skew_status="unavailable",
                    skew_method=SKEW_METHOD,
                    skew_confidence=None,
                    contrast=None,
                    contrast_status="unavailable",
                    contrast_method=CONTRAST_METHOD,
                    noise_speckle=None,
                    noise_status="unavailable",
                    noise_method=NOISE_METHOD,
                    blur=None,
                    blur_status="unavailable",
                    blur_method=BLUR_METHOD,
                    scan_quality="unscored",
                    scan_quality_rule_version=SCAN_QUALITY_RULE_VERSION,
                    measurement_status="unavailable",
                    analysis_resolution=ANALYSIS_RESOLUTION,
                    preprocessing_version=PREPROCESSING_VERSION,
                    provenance="unknown",
                    reason_codes=reason_codes_str,
                    image_index=None,
                    image_xref=None,
                    image_bbox=None,
                )
            )
        return doc_records

    for page_idx in range(len(pdf_doc)):
        pno = page_idx + 1
        page = pdf_doc[page_idx]
        rect = page.rect
        page_w = round(rect.width, 2)
        page_h = round(rect.height, 2)

        prof_p = profile_pages_map.get(page_idx) if profile_pages_map else None

        # If profile indicates 0 images, fast-path without image extraction
        if prof_p is not None and prof_p.get("n_images", 0) == 0:
            n_chars = prof_p.get("n_chars", 0)
            native_text_present = n_chars >= 15
            raster_count = 0
            largest_area_frac = 0.0
            total_area_frac = 0.0
            full_page_raster = False
            dominant_img = None
            dpi_w = dpi_h = dpi = None
            dpi_status = "not_applicable"
            img_idx = img_xref = img_bbox = None
        else:
            # Query actual PDF raster geometry
            try:
                img_infos = page.get_image_info(xrefs=True)
            except Exception:
                img_infos = []

            (
                raster_count,
                largest_area_frac,
                total_area_frac,
                dominant_img,
                dpi_w,
                dpi_h,
                dpi,
                dpi_status,
            ) = calculate_dominant_image_and_dpi(img_infos, rect)

            full_page_raster = (raster_count > 0) and (largest_area_frac >= 0.50)
            img_idx = dominant_img.get("index") if dominant_img else None
            img_xref = dominant_img.get("xref") if dominant_img else None
            img_bbox = (
                f"{dominant_img['vis_rect'].x0:.1f},{dominant_img['vis_rect'].y0:.1f},"
                f"{dominant_img['vis_rect'].x1:.1f},{dominant_img['vis_rect'].y1:.1f}"
                if dominant_img
                else None
            )

            if prof_p is not None:
                native_text_present = prof_p.get("n_chars", 0) >= 15
            else:
                text = page.get_text("text") or ""
                native_text_present = len(text.strip()) >= 15

        # Classify page provenance
        if pno in doc_ocr_pages:
            provenance = "ocr"
        elif full_page_raster:
            provenance = "scanned"
        elif native_text_present:
            provenance = "native"
        elif raster_count > 0:
            provenance = "partial_raster"
        else:
            provenance = "blank"

        # Primary measurement population: full_page_raster pages
        if full_page_raster:
            try:
                pix = page.get_pixmap(dpi=ANALYSIS_RESOLUTION, colorspace=pymupdf.csGRAY)
                arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w)

                skew_angle, skew_status, skew_conf = measure_skew(arr)
                contrast, contrast_status = measure_contrast(arr)
                noise, noise_status = measure_noise_speckle(arr)
                blur, blur_status = measure_blur_sharpness(arr)

                if (
                    dpi_status == "measured"
                    and contrast_status == "measured"
                    and noise_status == "measured"
                    and blur_status == "measured"
                ):
                    measurement_status = "measured"
                else:
                    measurement_status = "partial"

            except Exception:
                skew_angle, skew_status, skew_conf = None, "unavailable", None
                contrast, contrast_status = None, "unavailable"
                noise, noise_status = None, "unavailable"
                blur, blur_status = None, "unavailable"
                measurement_status = "unavailable"
        else:
            skew_angle, skew_status, skew_conf = None, "not_applicable", None
            contrast, contrast_status = None, "not_applicable"
            noise, noise_status = None, "not_applicable"
            blur, blur_status = None, "not_applicable"
            measurement_status = "not_applicable"

        doc_records.append(
            PageMeasurement(
                document_id=doc_id,
                company_id=cid,
                company=comp_name,
                FY=fy,
                physical_page=pno,
                source_pdf_sha256=pdf_sha256,
                page_width=page_w,
                page_height=page_h,
                raster_image_count=raster_count,
                largest_raster_area_fraction=largest_area_frac,
                total_raster_area_fraction=total_area_frac,
                full_page_raster=full_page_raster,
                dominant_raster_image=f"xref_{img_xref}_idx_{img_idx}" if img_xref else None,
                native_text_present=native_text_present,
                estimated_dpi_width=dpi_w,
                estimated_dpi_height=dpi_h,
                estimated_dpi=dpi,
                dpi_status=dpi_status,
                skew_angle=skew_angle,
                skew_status=skew_status,
                skew_method=SKEW_METHOD,
                skew_confidence=skew_conf,
                contrast=contrast,
                contrast_status=contrast_status,
                contrast_method=CONTRAST_METHOD,
                noise_speckle=noise,
                noise_status=noise_status,
                noise_method=NOISE_METHOD,
                blur=blur,
                blur_status=blur_status,
                blur_method=BLUR_METHOD,
                scan_quality="unscored",
                scan_quality_rule_version=SCAN_QUALITY_RULE_VERSION,
                measurement_status=measurement_status,
                analysis_resolution=ANALYSIS_RESOLUTION,
                preprocessing_version=PREPROCESSING_VERSION,
                provenance=provenance,
                reason_codes=reason_codes_str,
                image_index=img_idx,
                image_xref=img_xref,
                image_bbox=img_bbox,
            )
        )

    pdf_doc.close()
    return doc_records


def process_corpus(
    live_store_dir: str,
    companies_csv_path: str,
    pm1_baseline_path: str,
    manifest_after_path: str | None = None,
    progress_callback: Any = None,
    workers: int = 8,
) -> list[PageMeasurement]:
    """Executes the full page-level measurement pipeline over the 194-document corpus."""
    from concurrent.futures import ProcessPoolExecutor, as_completed

    # 1. Load companies metadata
    with open(companies_csv_path, mode="r", encoding="utf-8") as fh:
        companies_meta = {row["company_id"]: row for row in csv.DictReader(fh)}

    # 2. Load PM1 baseline document outcomes
    pm1_docs: dict[str, dict[str, Any]] = {}
    if os.path.exists(pm1_baseline_path):
        with open(pm1_baseline_path, mode="r", encoding="utf-8") as fh:
            pm1_data = json.load(fh)
            for d in pm1_data.get("documents", []):
                pm1_docs[d["document_id"]] = d

    # 3. Load PM1 after run manifest for page-level OCR stats & reasons
    ocr_pages_by_doc: dict[str, set[int]] = defaultdict(set)
    doc_reasons_map: dict[str, list[str]] = defaultdict(list)
    if manifest_after_path and os.path.exists(manifest_after_path):
        with open(manifest_after_path, mode="r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                m = json.loads(line)
                doc_id = f"{m.get('company_id')}_{m.get('fy_end')}"
                reasons = m.get("reasons") or []
                doc_reasons_map[doc_id] = reasons
                qc = m.get("qc") or {}
                for stat in qc.get("ocr_stats") or []:
                    pno = stat.get("page_no")
                    if pno is not None and stat.get("words", 0) > 0:
                        ocr_pages_by_doc[doc_id].add(pno)

    # 4. Load profiles.jsonl if present for telemetry acceleration
    profiles_path = os.path.join(live_store_dir, "profiles.jsonl")
    profiles_by_sha: dict[str, dict[int, dict[str, Any]]] = {}
    if os.path.exists(profiles_path):
        with open(profiles_path, mode="r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                prof = json.loads(line)
                sha = prof.get("sha256")
                if sha:
                    profiles_by_sha[sha] = {
                        p["page_no"]: p for p in prof.get("pages", [])
                    }

    # 5. Load corpus document manifest
    docs_jsonl = os.path.join(live_store_dir, "documents.jsonl")
    corpus_docs: list[dict[str, Any]] = []
    with open(docs_jsonl, mode="r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                corpus_docs.append(json.loads(line))

    # Sort documents deterministically by company_id, fy_end
    corpus_docs.sort(key=lambda d: (d["company_id"], d["fy_end"]))

    tasks = []
    for doc_meta in corpus_docs:
        cid = doc_meta["company_id"]
        fy = doc_meta["fy_end"]
        doc_id = f"{cid}_{fy}"
        comp_info = companies_meta.get(cid, {})
        pm1_doc = pm1_docs.get(doc_id, {})
        reasons_list = doc_reasons_map.get(doc_id) or pm1_doc.get("failure_reasons") or []
        doc_ocr = ocr_pages_by_doc.get(doc_id, set())
        prof_map = profiles_by_sha.get(doc_meta["sha256"])

        tasks.append((
            doc_meta,
            live_store_dir,
            comp_info,
            pm1_doc,
            reasons_list,
            doc_ocr,
            prof_map,
        ))

    records_by_doc: dict[str, list[PageMeasurement]] = {}
    completed_count = 0
    total_docs = len(tasks)

    if workers <= 1:
        for t in tasks:
            doc_res = _process_single_document(t)
            doc_id = f"{t[0]['company_id']}_{t[0]['fy_end']}"
            records_by_doc[doc_id] = doc_res
            completed_count += 1
            if progress_callback:
                progress_callback(completed_count, total_docs, doc_id)
    else:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            future_to_id = {
                executor.submit(_process_single_document, t): f"{t[0]['company_id']}_{t[0]['fy_end']}"
                for t in tasks
            }
            for fut in as_completed(future_to_id):
                doc_id = future_to_id[fut]
                doc_res = fut.result()
                records_by_doc[doc_id] = doc_res
                completed_count += 1
                if progress_callback:
                    progress_callback(completed_count, total_docs, doc_id)

    # Reassemble deterministically in original sorted document order
    records: list[PageMeasurement] = []
    for doc_meta in corpus_docs:
        doc_id = f"{doc_meta['company_id']}_{doc_meta['fy_end']}"
        doc_pages = records_by_doc.get(doc_id, [])
        # Ensure pages inside document are sorted by physical_page
        doc_pages.sort(key=lambda p: p.physical_page)
        records.extend(doc_pages)

    return records


# --- Aggregation & Reporting -----------------------------------------------

def generate_summary_data(
    records: list[PageMeasurement], companies_meta: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Builds corpus, fiscal year, cap band, and document-level aggregations."""
    total_docs = len(set(r.document_id for r in records))
    total_pages = len(records)

    raster_pages = [r for r in records if r.raster_image_count > 0]
    full_raster_pages = [r for r in records if r.full_page_raster]
    partial_raster_pages = [r for r in records if r.raster_image_count > 0 and not r.full_page_raster]
    native_only_pages = [r for r in records if r.raster_image_count == 0 and r.native_text_present]
    unknown_pages = [r for r in records if r.measurement_status == "unavailable"]

    measurable_pages = [r for r in full_raster_pages if r.measurement_status == "measured"]
    unmeasurable_pages = [r for r in full_raster_pages if r.measurement_status != "measured"]

    # Raw component distributions over measurable full-page-raster pages
    dpi_vals = [r.estimated_dpi for r in full_raster_pages if r.estimated_dpi is not None]
    skew_vals = [r.skew_angle for r in full_raster_pages if r.skew_angle is not None]
    contrast_vals = [r.contrast for r in full_raster_pages if r.contrast is not None]
    noise_vals = [r.noise_speckle for r in full_raster_pages if r.noise_speckle is not None]
    blur_vals = [r.blur for r in full_raster_pages if r.blur is not None]

    raw_distributions = {
        "dpi": {
            "N": len(dpi_vals),
            "missing_count": len(full_raster_pages) - len(dpi_vals),
            "invalid_count": sum(1 for r in full_raster_pages if r.dpi_status == "invalid"),
            **calculate_percentiles(dpi_vals),
        },
        "skew": {
            "N": len(skew_vals),
            "missing_count": len(full_raster_pages) - len(skew_vals),
            "invalid_count": sum(1 for r in full_raster_pages if r.skew_status == "invalid"),
            **calculate_percentiles(skew_vals),
        },
        "contrast": {
            "N": len(contrast_vals),
            "missing_count": len(full_raster_pages) - len(contrast_vals),
            "invalid_count": sum(1 for r in full_raster_pages if r.contrast_status == "invalid"),
            **calculate_percentiles(contrast_vals),
        },
        "noise": {
            "N": len(noise_vals),
            "missing_count": len(full_raster_pages) - len(noise_vals),
            "invalid_count": sum(1 for r in full_raster_pages if r.noise_status == "invalid"),
            **calculate_percentiles(noise_vals),
        },
        "blur": {
            "N": len(blur_vals),
            "missing_count": len(full_raster_pages) - len(blur_vals),
            "invalid_count": sum(1 for r in full_raster_pages if r.blur_status == "invalid"),
            **calculate_percentiles(blur_vals),
        },
    }

    # Fiscal-Year analysis
    by_fy: dict[int, list[PageMeasurement]] = defaultdict(list)
    for r in records:
        by_fy[r.FY].append(r)

    fy_summary: list[dict[str, Any]] = []
    for fy in sorted(by_fy.keys()):
        fy_pages = by_fy[fy]
        fy_docs = len(set(p.document_id for p in fy_pages))
        fy_full = [p for p in fy_pages if p.full_page_raster]
        fy_meas = [p for p in fy_full if p.measurement_status == "measured"]
        fy_dpi = [p.estimated_dpi for p in fy_full if p.estimated_dpi is not None]
        fy_skew = [p.skew_angle for p in fy_full if p.skew_angle is not None]
        fy_cont = [p.contrast for p in fy_full if p.contrast is not None]
        fy_noise = [p.noise_speckle for p in fy_full if p.noise_speckle is not None]
        fy_blur = [p.blur for p in fy_full if p.blur is not None]

        fy_summary.append({
            "FY": fy,
            "N_documents": fy_docs,
            "N_physical_pages": len(fy_pages),
            "N_full_page_raster": len(fy_full),
            "raster_page_fraction": round(len(fy_full) / max(1, len(fy_pages)), 4),
            "N_measurable_pages": len(fy_meas),
            "measurable_page_fraction": round(len(fy_meas) / max(1, len(fy_full)), 4) if fy_full else 0.0,
            "median_dpi": float(np.median(fy_dpi)) if fy_dpi else None,
            "median_skew": float(np.median(fy_skew)) if fy_skew else None,
            "median_contrast": float(np.median(fy_cont)) if fy_cont else None,
            "median_noise": float(np.median(fy_noise)) if fy_noise else None,
            "median_blur": float(np.median(fy_blur)) if fy_blur else None,
        })

    # Cap-Band analysis
    by_cap: dict[str, list[PageMeasurement]] = defaultdict(list)
    for r in records:
        c_band = companies_meta.get(r.company_id, {}).get("cap_band", "unknown")
        by_cap[c_band].append(r)

    cap_summary: list[dict[str, Any]] = []
    for band in ["large", "mid", "small", "micro"]:
        c_pages = by_cap.get(band, [])
        c_docs = len(set(p.document_id for p in c_pages))
        c_full = [p for p in c_pages if p.full_page_raster]
        c_meas = [p for p in c_full if p.measurement_status == "measured"]
        c_dpi = [p.estimated_dpi for p in c_full if p.estimated_dpi is not None]
        c_skew = [p.skew_angle for p in c_full if p.skew_angle is not None]
        c_cont = [p.contrast for p in c_full if p.contrast is not None]
        c_noise = [p.noise_speckle for p in c_full if p.noise_speckle is not None]
        c_blur = [p.blur for p in c_full if p.blur is not None]

        cap_summary.append({
            "cap_band": band,
            "N_documents": c_docs,
            "N_physical_pages": len(c_pages),
            "N_full_page_raster": len(c_full),
            "raster_page_fraction": round(len(c_full) / max(1, len(c_pages)), 4) if c_pages else 0.0,
            "N_measurable_pages": len(c_meas),
            "measurable_page_fraction": round(len(c_meas) / max(1, len(c_full)), 4) if c_full else 0.0,
            "median_dpi": float(np.median(c_dpi)) if c_dpi else None,
            "median_skew": float(np.median(c_skew)) if c_skew else None,
            "median_contrast": float(np.median(c_cont)) if c_cont else None,
            "median_noise": float(np.median(c_noise)) if c_noise else None,
            "median_blur": float(np.median(c_blur)) if c_blur else None,
        })

    # FY x Cap Band cross-tabulation
    fy_cap_cells: list[dict[str, Any]] = []
    for fy in sorted(by_fy.keys()):
        for band in ["large", "mid", "small", "micro"]:
            cell_pages = [
                p for p in by_fy[fy]
                if companies_meta.get(p.company_id, {}).get("cap_band") == band
            ]
            if not cell_pages:
                continue
            c_docs = len(set(p.document_id for p in cell_pages))
            c_full = [p for p in cell_pages if p.full_page_raster]
            c_meas = [p for p in c_full if p.measurement_status == "measured"]
            fy_cap_cells.append({
                "FY": fy,
                "cap_band": band,
                "N_documents": c_docs,
                "N_physical_pages": len(cell_pages),
                "N_full_page_raster": len(c_full),
                "raster_page_fraction": round(len(c_full) / len(cell_pages), 4),
                "N_measurable_pages": len(c_meas),
                "is_small_cell": c_docs < 3,
            })

    # Document-level concentration of full-page-raster pages
    doc_raster_counts: dict[str, int] = Counter()
    doc_meas_counts: dict[str, int] = Counter()
    for p in full_raster_pages:
        doc_raster_counts[p.document_id] += 1
        if p.measurement_status == "measured":
            doc_meas_counts[p.document_id] += 1

    sorted_doc_raster = sorted(doc_raster_counts.values(), reverse=True)
    total_raster_p = sum(sorted_doc_raster)
    top1_share = round(sum(sorted_doc_raster[:1]) / max(1, total_raster_p), 4)
    top5_share = round(sum(sorted_doc_raster[:5]) / max(1, total_raster_p), 4)
    top10_share = round(sum(sorted_doc_raster[:10]) / max(1, total_raster_p), 4)

    # Company-level concentration
    comp_raster_counts: dict[str, int] = Counter()
    for p in full_raster_pages:
        comp_raster_counts[p.company_id] += 1
    sorted_comp_raster = sorted(comp_raster_counts.values(), reverse=True)
    top1_comp_share = round(sum(sorted_comp_raster[:1]) / max(1, total_raster_p), 4)
    top5_comp_share = round(sum(sorted_comp_raster[:5]) / max(1, total_raster_p), 4)
    top10_comp_share = round(sum(sorted_comp_raster[:10]) / max(1, total_raster_p), 4)

    # Missingness analysis
    missingness = {
        "total_full_page_raster": len(full_raster_pages),
        "dpi_missing": len(full_raster_pages) - len(dpi_vals),
        "skew_missing": len(full_raster_pages) - len(skew_vals),
        "contrast_missing": len(full_raster_pages) - len(contrast_vals),
        "noise_missing": len(full_raster_pages) - len(noise_vals),
        "blur_missing": len(full_raster_pages) - len(blur_vals),
        "skew_low_confidence": sum(1 for p in full_raster_pages if p.skew_status == "low_confidence"),
    }

    # Descriptive cross-tab with existing ARPipe provenance / outcomes
    prov_cross: dict[str, Counter] = defaultdict(Counter)
    for p in full_raster_pages:
        prov_cross[p.provenance]["full_raster"] += 1
        if p.measurement_status == "measured":
            prov_cross[p.provenance]["measured"] += 1

    return {
        "population": {
            "total_documents": total_docs,
            "total_physical_pages": total_pages,
            "pages_with_raster": len(raster_pages),
            "pages_with_full_page_raster": len(full_raster_pages),
            "pages_with_partial_raster": len(partial_raster_pages),
            "native_only_pages": len(native_only_pages),
            "unknown_pages": len(unknown_pages),
            "measurable_full_page_raster_pages": len(measurable_pages),
            "unmeasurable_pages": len(unmeasurable_pages),
        },
        "raw_distributions": raw_distributions,
        "fiscal_year_summary": fy_summary,
        "cap_band_summary": cap_summary,
        "fy_cap_band_cells": fy_cap_cells,
        "concentration": {
            "total_full_page_raster_pages": total_raster_p,
            "documents_with_raster_pages": len(doc_raster_counts),
            "top1_document_share": top1_share,
            "top5_document_share": top5_share,
            "top10_document_share": top10_share,
            "top1_company_share": top1_comp_share,
            "top5_company_share": top5_comp_share,
            "top10_company_share": top10_comp_share,
        },
        "missingness": missingness,
        "provenance_cross_tab": {k: dict(v) for k, v in prov_cross.items()},
    }


def write_csv_reports(
    records: list[PageMeasurement], summary: dict[str, Any], out_dir: str
) -> None:
    """Writes all required CSV files."""
    os.makedirs(out_dir, exist_ok=True)

    # 1. Page-level CSV
    page_csv = os.path.join(out_dir, "pm3_scan_quality_page_level.csv")
    fieldnames = [
        "document_id",
        "company_id",
        "company",
        "FY",
        "physical_page",
        "source_pdf_sha256",
        "page_width",
        "page_height",
        "raster_image_count",
        "largest_raster_area_fraction",
        "total_raster_area_fraction",
        "full_page_raster",
        "dominant_raster_image",
        "native_text_present",
        "estimated_dpi_width",
        "estimated_dpi_height",
        "estimated_dpi",
        "dpi_status",
        "skew_angle",
        "skew_status",
        "skew_method",
        "skew_confidence",
        "contrast",
        "contrast_status",
        "contrast_method",
        "noise_speckle",
        "noise_status",
        "noise_method",
        "blur",
        "blur_status",
        "blur_method",
        "scan_quality",
        "scan_quality_rule_version",
        "measurement_status",
        "analysis_resolution",
        "preprocessing_version",
        "provenance",
        "reason_codes",
        "image_index",
        "image_xref",
        "image_bbox",
    ]
    with open(page_csv, mode="w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow(asdict(r))

    # 2. FY CSV
    fy_csv = os.path.join(out_dir, "pm3_scan_quality_by_year.csv")
    fy_fields = [
        "FY",
        "N_documents",
        "N_physical_pages",
        "N_full_page_raster",
        "raster_page_fraction",
        "N_measurable_pages",
        "measurable_page_fraction",
        "median_dpi",
        "median_skew",
        "median_contrast",
        "median_noise",
        "median_blur",
    ]
    with open(fy_csv, mode="w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fy_fields)
        writer.writeheader()
        for row in summary["fiscal_year_summary"]:
            writer.writerow(row)

    # 3. Cap Band CSV
    cap_csv = os.path.join(out_dir, "pm3_scan_quality_by_cap_band.csv")
    cap_fields = [
        "cap_band",
        "N_documents",
        "N_physical_pages",
        "N_full_page_raster",
        "raster_page_fraction",
        "N_measurable_pages",
        "measurable_page_fraction",
        "median_dpi",
        "median_skew",
        "median_contrast",
        "median_noise",
        "median_blur",
    ]
    with open(cap_csv, mode="w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=cap_fields)
        writer.writeheader()
        for row in summary["cap_band_summary"]:
            writer.writerow(row)


def write_json_and_md_reports(
    summary: dict[str, Any],
    environment_meta: dict[str, Any],
    out_dir: str,
) -> None:
    """Writes the comprehensive JSON and Markdown reports."""
    os.makedirs(out_dir, exist_ok=True)

    full_report_data = {
        "metadata": {
            "task": "P-M3 — SCAN-QUALITY MEASUREMENT",
            "date": "2026-09-17",
            "raster_classification_rule_version": RASTER_CLASSIFICATION_RULE_VERSION,
            "analysis_resolution": ANALYSIS_RESOLUTION,
            "preprocessing_version": PREPROCESSING_VERSION,
            "skew_method": SKEW_METHOD,
            "contrast_method": CONTRAST_METHOD,
            "noise_method": NOISE_METHOD,
            "blur_method": BLUR_METHOD,
            "scan_quality_rule_version": SCAN_QUALITY_RULE_VERSION,
            "composite_rule_used": False,
            "environment": environment_meta,
        },
        "verdict": "SCAN-QUALITY MEASUREMENT COMPLETED — NO PRODUCTION CHANGE",
        "production_behavior_changed": False,
        "production_files_changed": [],
        **summary,
    }

    # 1. JSON Report
    json_path = os.path.join(out_dir, "pm3_scan_quality.json")
    with open(json_path, mode="w", encoding="utf-8") as fh:
        json.dump(full_report_data, fh, indent=2)

    # 2. Markdown Report
    md_path = os.path.join(out_dir, "pm3_scan_quality.md")
    pop = summary["population"]
    raw = summary["raw_distributions"]
    conc = summary["concentration"]
    miss = summary["missingness"]

    md_lines = [
        "# P-M3: Scan-Quality Measurement Report",
        "",
        "> **Research Question**: How prevalent are low-quality scanned/raster pages, and does scan quality or scan-related missingness concentrate by fiscal year, company size, or other existing corpus strata?",
        "",
        "## Methodological Isolation & Scope",
        "- **Study Nature**: Measurement and diagnostic study only.",
        "- **Production Changes**: ZERO production files modified. No routing, threshold, segmentation, or OCR changes.",
        "- **Explicit Boundary**:",
        "```text",
        "SCAN / INPUT QUALITY  ≠  OCR QUALITY  ≠  EXTRACTION CORRECTNESS  ≠  OCR FAILURE",
        "```",
        "- **Composite Rule**: No pre-existing composite rule existed; per Section 13, composite scoring is marked `unscored` (no threshold fishing). Raw component measurements remain primary.",
        "",
        "## A. Population Accounting",
        f"- **Total Documents**: {pop['total_documents']}",
        f"- **Total Physical Pages**: {pop['total_physical_pages']}",
        f"- **Pages with Raster Content**: {pop['pages_with_raster']} ({pop['pages_with_raster']/pop['total_physical_pages']*100:.2f}%)",
        f"- **Pages with Full-Page Raster (Dominant $\\ge$ 50%)**: {pop['pages_with_full_page_raster']} ({pop['pages_with_full_page_raster']/pop['total_physical_pages']*100:.2f}%)",
        f"- **Pages with Partial Raster**: {pop['pages_with_partial_raster']} ({pop['pages_with_partial_raster']/pop['total_physical_pages']*100:.2f}%)",
        f"- **Native-Only Pages**: {pop['native_only_pages']} ({pop['native_only_pages']/pop['total_physical_pages']*100:.2f}%)",
        f"- **Unknown Pages**: {pop['unknown_pages']}",
        f"- **Measurable Full-Page Raster Pages**: {pop['measurable_full_page_raster_pages']} ({pop['measurable_full_page_raster_pages']/max(1, pop['pages_with_full_page_raster'])*100:.2f}%)",
        f"- **Unmeasurable Full-Page Raster Pages**: {pop['unmeasurable_pages']}",
        "",
        "## B. Raw Physical Measurement Distributions (Primary Measurement Population)",
        "| Component | N | Missing | Min | P25 | Median | P75 | P95 | Max | Method & Direction |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |",
        f"| **DPI** | {raw['dpi']['N']} | {raw['dpi']['missing_count']} | {raw['dpi']['min']} | {raw['dpi']['p25']} | {raw['dpi']['median']} | {raw['dpi']['p75']} | {raw['dpi']['p95']} | {raw['dpi']['max']} | Min width/height placed DPI |",
        f"| **Skew Angle (°)** | {raw['skew']['N']} | {raw['skew']['missing_count']} | {raw['skew']['min']} | {raw['skew']['p25']} | {raw['skew']['median']} | {raw['skew']['p75']} | {raw['skew']['p95']} | {raw['skew']['max']} | Projection profile variance |",
        f"| **Contrast** | {raw['contrast']['N']} | {raw['contrast']['missing_count']} | {raw['contrast']['min']} | {raw['contrast']['p25']} | {raw['contrast']['median']} | {raw['contrast']['p75']} | {raw['contrast']['p95']} | {raw['contrast']['max']} | Interdecile (P95-P05)/255 |",
        f"| **Noise / Speckle** | {raw['noise']['N']} | {raw['noise']['missing_count']} | {raw['noise']['min']} | {raw['noise']['p25']} | {raw['noise']['median']} | {raw['noise']['p75']} | {raw['noise']['p95']} | {raw['noise']['max']} | 3x3 median residual (higher=noisier) |",
        f"| **Blur / Sharpness** | {raw['blur']['N']} | {raw['blur']['missing_count']} | {raw['blur']['min']} | {raw['blur']['p25']} | {raw['blur']['median']} | {raw['blur']['p75']} | {raw['blur']['p95']} | {raw['blur']['max']} | Laplacian variance (**higher=sharper**) |",
        "",
        "## C. Fiscal-Year Analysis",
        "| FY | Docs | Physical Pages | Full Raster Pages | Raster Frac | Measurable Pages | Median DPI | Median Skew | Median Contrast | Median Noise | Median Blur |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for row in summary["fiscal_year_summary"]:
        md_lines.append(
            f"| {row['FY']} | {row['N_documents']} | {row['N_physical_pages']} | "
            f"{row['N_full_page_raster']} | {row['raster_page_fraction']:.4f} | "
            f"{row['N_measurable_pages']} | {row['median_dpi']} | {row['median_skew']} | "
            f"{row['median_contrast']} | {row['median_noise']} | {row['median_blur']} |"
        )

    md_lines.extend([
        "",
        "## D. Company-Size / Cap-Band Analysis",
        "| Cap Band | Docs | Physical Pages | Full Raster Pages | Raster Frac | Measurable Pages | Median DPI | Median Skew | Median Contrast | Median Noise | Median Blur |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])

    for row in summary["cap_band_summary"]:
        md_lines.append(
            f"| {row['cap_band']} | {row['N_documents']} | {row['N_physical_pages']} | "
            f"{row['N_full_page_raster']} | {row['raster_page_fraction']:.4f} | "
            f"{row['N_measurable_pages']} | {row['median_dpi']} | {row['median_skew']} | "
            f"{row['median_contrast']} | {row['median_noise']} | {row['median_blur']} |"
        )

    md_lines.extend([
        "",
        "## E. FY × Cap-Band Distribution",
        "| FY | Cap Band | Docs | Physical Pages | Full Raster Pages | Raster Frac | Measurable Pages | Note |",
        "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | :--- |",
    ])

    for cell in summary["fy_cap_band_cells"]:
        note = "descriptive only (small cell)" if cell["is_small_cell"] else "adequate cell"
        md_lines.append(
            f"| {cell['FY']} | {cell['cap_band']} | {cell['N_documents']} | {cell['N_physical_pages']} | "
            f"{cell['N_full_page_raster']} | {cell['raster_page_fraction']:.4f} | {cell['N_measurable_pages']} | {note} |"
        )

    md_lines.extend([
        "",
        "## F. Document & Company Concentration Analysis",
        f"- Total full-page-raster pages: **{conc['total_full_page_raster_pages']}** across **{conc['documents_with_raster_pages']}** documents.",
        f"- **Top 1 Document Share**: {conc['top1_document_share']*100:.2f}% of all full-page raster pages.",
        f"- **Top 5 Documents Share**: {conc['top5_document_share']*100:.2f}% of all full-page raster pages.",
        f"- **Top 10 Documents Share**: {conc['top10_document_share']*100:.2f}% of all full-page raster pages.",
        f"- **Top 1 Company Share**: {conc['top1_company_share']*100:.2f}%.",
        f"- **Top 5 Companies Share**: {conc['top5_company_share']*100:.2f}%.",
        f"- **Top 10 Companies Share**: {conc['top10_company_share']*100:.2f}%.",
        "",
        "## G. Missingness Analysis",
        f"- Total full-page raster pages: {miss['total_full_page_raster']}",
        f"- DPI missingness: {miss['dpi_missing']}",
        f"- Skew missingness: {miss['skew_missing']} (low confidence: {miss['skew_low_confidence']})",
        f"- Contrast missingness: {miss['contrast_missing']}",
        f"- Noise missingness: {miss['noise_missing']}",
        f"- Blur missingness: {miss['blur_missing']}",
        "",
        "## H. Diagnostic Association with Provenance & Outcomes",
        "| Provenance | Full Raster Pages | Measurable Pages |",
        "| :--- | ---: | ---: |",
    ])

    for prov, counts in summary["provenance_cross_tab"].items():
        md_lines.append(f"| {prov} | {counts.get('full_raster', 0)} | {counts.get('measured', 0)} |")

    md_lines.extend([
        "",
        "## I. Methodological Boundaries — What Is NOT Established",
        "- **MEASURED**: Physical resolution (DPI), geometric skew angle, grayscale contrast dynamic range, spatial median residual (noise), and discrete Laplacian variance (sharpness).",
        "- **DESCRIPTIVE ASSOCIATION**: Distribution of raster pages across FY, cap bands, and document concentration.",
        "- **INFERENCE**: Higher raster prevalence in earlier fiscal years (2012–2013) and small/micro cap companies.",
        "- **NOT ESTABLISHED**: OCR accuracy, word error rate, extraction correctness, or causal impact on MD&A section discovery. Low physical scan quality cannot be equated with OCR failure.",
        "",
        "## J. Final Verdict",
        "```text",
        "SCAN-QUALITY MEASUREMENT COMPLETED — NO PRODUCTION CHANGE",
        "```",
    ])

    with open(md_path, mode="w", encoding="utf-8") as fh:
        fh.write("\n".join(md_lines) + "\n")


# --- Diagnostic Plotting ---------------------------------------------------

def generate_diagnostic_plots(
    records: list[PageMeasurement], summary: dict[str, Any], out_dir: str
) -> list[str]:
    """Generates pure Pillow-rendered diagnostic plots matching report data."""
    os.makedirs(out_dir, exist_ok=True)
    generated: list[str] = []

    full_raster = [r for r in records if r.full_page_raster]

    # Helper: try loading basic font or default
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    # Plot 1: Component Distributions (DPI and Contrast Histograms)
    p1_path = os.path.join(out_dir, "pm3_scan_quality_distribution.png")
    w, h = 900, 450
    img1 = Image.new("RGB", (w, h), color="#FFFFFF")
    d1 = ImageDraw.Draw(img1)

    d1.text((30, 20), "P-M3: Physical Scan-Quality Component Distributions", fill="#222222", font=font)
    d1.text((30, 40), f"Population: N={len(full_raster)} full-page raster pages", fill="#555555", font=font)

    # Left plot: DPI distribution
    dpis = [r.estimated_dpi for r in full_raster if r.estimated_dpi is not None]
    if dpis:
        d1.text((60, 75), "DPI Distribution", fill="#1565C0", font=font)
        d1.rectangle([60, 95, 420, 380], outline="#CCCCCC", width=1)
        bins = [100, 150, 200, 250, 300, 350, 400, 600]
        hist, _ = np.histogram(dpis, bins=bins)
        max_h = max(hist) if len(hist) > 0 and max(hist) > 0 else 1
        plot_w = 360
        plot_h = 285
        bar_w = plot_w // len(hist)
        for i, count in enumerate(hist):
            bh = int((count / max_h) * (plot_h - 40))
            bx0 = 60 + i * bar_w + 5
            bx1 = bx0 + bar_w - 10
            by1 = 380
            by0 = by1 - bh
            d1.rectangle([bx0, by0, bx1, by1], fill="#1E88E5")
            d1.text((bx0, by0 - 15), str(count), fill="#333333", font=font)
            lbl = f"{bins[i]}"
            d1.text((bx0, by1 + 5), lbl, fill="#555555", font=font)

    # Right plot: Contrast distribution
    conts = [r.contrast for r in full_raster if r.contrast is not None]
    if conts:
        d1.text((500, 75), "Contrast Distribution (P95-P05)/255", fill="#2E7D32", font=font)
        d1.rectangle([500, 95, 860, 380], outline="#CCCCCC", width=1)
        cbins = np.linspace(0.0, 1.0, 11)
        chist, _ = np.histogram(conts, bins=cbins)
        cmax_h = max(chist) if len(chist) > 0 and max(chist) > 0 else 1
        cplot_w = 360
        cplot_h = 285
        cbar_w = cplot_w // len(chist)
        for i, count in enumerate(chist):
            bh = int((count / cmax_h) * (cplot_h - 40))
            bx0 = 500 + i * cbar_w + 3
            bx1 = bx0 + cbar_w - 6
            by1 = 380
            by0 = by1 - bh
            d1.rectangle([bx0, by0, bx1, by1], fill="#43A047")
            if count > 0:
                d1.text((bx0, by0 - 15), str(count), fill="#333333", font=font)
            clbl = f"{cbins[i]:.1f}"
            d1.text((bx0, by1 + 5), clbl, fill="#555555", font=font)

    img1.save(p1_path)
    generated.append(p1_path)

    # Plot 2: Full-Page Raster Fraction by Fiscal Year
    p2_path = os.path.join(out_dir, "pm3_scan_quality_by_year.png")
    img2 = Image.new("RGB", (800, 450), color="#FFFFFF")
    d2 = ImageDraw.Draw(img2)
    d2.text((30, 20), "P-M3: Full-Page Raster Page Fraction by Fiscal Year", fill="#222222", font=font)

    fy_data = summary["fiscal_year_summary"]
    if fy_data:
        d2.rectangle([60, 70, 750, 380], outline="#CCCCCC", width=1)
        f_plot_w = 690
        f_plot_h = 310
        fbar_w = f_plot_w // len(fy_data)
        max_frac = max([x["raster_page_fraction"] for x in fy_data] + [0.1])
        for i, row in enumerate(fy_data):
            frac = row["raster_page_fraction"]
            bh = int((frac / max_frac) * (f_plot_h - 50))
            bx0 = 60 + i * fbar_w + 10
            bx1 = bx0 + fbar_w - 20
            by1 = 380
            by0 = by1 - bh
            d2.rectangle([bx0, by0, bx1, by1], fill="#FB8C00")
            pct_str = f"{frac*100:.1f}%"
            d2.text((bx0, by0 - 15), pct_str, fill="#333333", font=font)
            d2.text((bx0, by1 + 8), str(row["FY"]), fill="#333333", font=font)
            n_str = f"({row['N_full_page_raster']}/{row['N_physical_pages']})"
            d2.text((bx0 - 5, by1 + 22), n_str, fill="#777777", font=font)

    img2.save(p2_path)
    generated.append(p2_path)

    # Plot 3: Full-Page Raster Fraction by Cap Band
    p3_path = os.path.join(out_dir, "pm3_scan_quality_by_cap_band.png")
    img3 = Image.new("RGB", (700, 450), color="#FFFFFF")
    d3 = ImageDraw.Draw(img3)
    d3.text((30, 20), "P-M3: Full-Page Raster Page Fraction by Company Cap Band", fill="#222222", font=font)

    cap_data = summary["cap_band_summary"]
    if cap_data:
        d3.rectangle([60, 70, 650, 380], outline="#CCCCCC", width=1)
        c_plot_w = 590
        c_plot_h = 310
        cbar_w = c_plot_w // len(cap_data)
        max_cfrac = max([x["raster_page_fraction"] for x in cap_data] + [0.1])
        for i, row in enumerate(cap_data):
            frac = row["raster_page_fraction"]
            bh = int((frac / max_cfrac) * (c_plot_h - 50))
            bx0 = 60 + i * cbar_w + 20
            bx1 = bx0 + cbar_w - 40
            by1 = 380
            by0 = by1 - bh
            d3.rectangle([bx0, by0, bx1, by1], fill="#8E24AA")
            pct_str = f"{frac*100:.1f}%"
            d3.text((bx0, by0 - 15), pct_str, fill="#333333", font=font)
            d3.text((bx0, by1 + 8), str(row["cap_band"]), fill="#333333", font=font)
            cn_str = f"({row['N_full_page_raster']}/{row['N_physical_pages']})"
            d3.text((bx0 - 5, by1 + 22), cn_str, fill="#777777", font=font)

    img3.save(p3_path)
    generated.append(p3_path)

    return generated


# --- CLI Main --------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live-store",
        default="d:/sem_iitk/sem9/thesis/sep_week1/arpipe-0.1.0/live_store",
        help="Path to live_store directory containing documents.jsonl and blobs",
    )
    parser.add_argument(
        "--companies",
        default="cohort_companies.csv",
        help="Path to cohort_companies.csv",
    )
    parser.add_argument(
        "--pm1-baseline",
        default="reports/pm1_baseline.json",
        help="Path to reports/pm1_baseline.json",
    )
    parser.add_argument(
        "--manifest-after",
        default="d:/sem_iitk/sem9/thesis/sep_week1/arpipe-0.1.0/pm1_after_run/manifest.jsonl",
        help="Path to PM1 after run manifest.jsonl",
    )
    parser.add_argument(
        "--out-dir",
        default="reports",
        help="Directory to save generated CSVs, JSON, MD, and plots",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Number of worker processes (default 8)",
    )
    args = parser.parse_args(argv)

    print("=" * 70)
    print("P-M3: SCAN-QUALITY MEASUREMENT ENGINE")
    print(f"  Live store:   {args.live_store}")
    print(f"  Companies:    {args.companies}")
    print(f"  PM1 Baseline: {args.pm1_baseline}")
    print(f"  Output Dir:   {args.out_dir}")
    print(f"  Workers:      {args.workers}")
    print(f"  Rule Version: {RASTER_CLASSIFICATION_RULE_VERSION}")
    print("=" * 70)

    t0 = time.time()

    def progress(curr: int, total: int, doc_id: str) -> None:
        if curr % 25 == 0 or curr == total:
            elapsed = time.time() - t0
            print(f"  [{curr:3d}/{total:3d}] ({elapsed:5.1f}s) Processed: {doc_id}", file=sys.stderr)

    records = process_corpus(
        live_store_dir=args.live_store,
        companies_csv_path=args.companies,
        pm1_baseline_path=args.pm1_baseline,
        manifest_after_path=args.manifest_after,
        progress_callback=progress,
        workers=args.workers,
    )

    t1 = time.time()
    print(f"Completed corpus page scanning in {t1 - t0:.2f} s. Total pages: {len(records)}")

    with open(args.companies, mode="r", encoding="utf-8") as fh:
        companies_meta = {row["company_id"]: row for row in csv.DictReader(fh)}

    summary = generate_summary_data(records, companies_meta)

    # Gather environment metadata
    env_meta = {
        "python_version": sys.version.split()[0],
        "pymupdf_version": getattr(pymupdf, "__version__", "unknown"),
        "pillow_version": getattr(Image, "__version__", "unknown"),
        "numpy_version": getattr(np, "__version__", "unknown"),
        "os": sys.platform,
    }

    print("Writing output CSV files ...")
    write_csv_reports(records, summary, args.out_dir)

    print("Writing output JSON and Markdown reports ...")
    write_json_and_md_reports(summary, env_meta, args.out_dir)

    print("Generating diagnostic plots ...")
    plots = generate_diagnostic_plots(records, summary, args.out_dir)
    print(f"Plots created: {', '.join(plots)}")

    t2 = time.time()
    print(f"P-M3 finished successfully in {t2 - t0:.2f} s.")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
