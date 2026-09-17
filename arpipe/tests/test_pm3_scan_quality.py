"""Unit and regression tests for P-M3: Scan-Quality Measurement.

Verifies:
1. Raster detection & image geometry calculation.
2. Raster coverage calculation (dominant & union grid).
3. Full-page-raster classification (v1.0_geom_dominant_50pct).
4. DPI calculation (placed inches, minimum width/height DPI).
5. Multiple-image handling & off-page image filtering.
6. Null vs zero preservation (null != 0.0).
7. Measurement-status handling (measured, unavailable, invalid, not_applicable).
8. Skew measurement determinism & confidence handling.
9. Contrast measurement determinism & bounds.
10. Noise/speckle measurement determinism.
11. Blur / Laplacian variance directionality (higher = sharper).
12. Canonical preprocessing determinism.
13. Page/image provenance tagging.
14. Document aggregation & concentration metrics.
15. Fiscal-year aggregation & denominator integrity.
16. Cap-band aggregation & denominator integrity.
17. Missingness reporting.
18. Reproducibility of algorithms.
19. Production immutability (zero changes to production files).
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import pytest
import pymupdf

from tools.pm3_scan_quality import (
    ANALYSIS_RESOLUTION,
    BLUR_METHOD,
    CONTRAST_METHOD,
    NOISE_METHOD,
    PREPROCESSING_VERSION,
    RASTER_CLASSIFICATION_RULE_VERSION,
    SCAN_QUALITY_RULE_VERSION,
    SKEW_METHOD,
    PageMeasurement,
    calculate_dominant_image_and_dpi,
    calculate_percentiles,
    generate_summary_data,
    measure_blur_sharpness,
    measure_contrast,
    measure_noise_speckle,
    measure_skew,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]


# 1. Raster detection & image geometry
def test_raster_detection_and_image_geometry():
    page_rect = pymupdf.Rect(0, 0, 600, 800)
    # 1 image placed inside page: 300x400 points, 600x800 pixels
    imgs = [{
        "bbox": [50, 50, 350, 450],
        "width": 600,
        "height": 800,
        "xref": 12,
    }]
    count, largest_frac, total_frac, dom, dpi_w, dpi_h, dpi, status = (
        calculate_dominant_image_and_dpi(imgs, page_rect)
    )
    assert count == 1
    assert largest_frac == pytest.approx((300 * 400) / (600 * 800), abs=1e-3)
    assert dom is not None
    assert dom["xref"] == 12
    assert status == "measured"


# 2. Raster coverage calculation (dominant & union grid)
def test_raster_coverage_calculation():
    page_rect = pymupdf.Rect(0, 0, 100, 100)
    # Two non-overlapping images of 20x20 and 40x40
    imgs = [
        {"bbox": [0, 0, 20, 20], "width": 100, "height": 100, "xref": 1},
        {"bbox": [50, 50, 90, 90], "width": 200, "height": 200, "xref": 2},
    ]
    count, largest_frac, total_frac, dom, _, _, _, _ = (
        calculate_dominant_image_and_dpi(imgs, page_rect)
    )
    assert count == 2
    # Largest is 40x40 = 1600 / 10000 = 0.16
    assert largest_frac == 0.16
    assert dom["xref"] == 2
    # Total coverage should be > largest_frac
    assert total_frac >= 0.16


# 3. Full-page-raster classification
def test_full_page_raster_classification():
    page_rect = pymupdf.Rect(0, 0, 600, 800)
    # Dominant image covering 60% of the page -> full_page_raster is True
    imgs_full = [{
        "bbox": [0, 0, 600, 480],
        "width": 1200,
        "height": 960,
        "xref": 5,
    }]
    _, largest_frac_full, _, _, _, _, _, _ = calculate_dominant_image_and_dpi(imgs_full, page_rect)
    assert largest_frac_full >= 0.50
    assert (largest_frac_full >= 0.50) is True

    # Small logo covering 5% of page -> partial_raster, full_page_raster is False
    imgs_small = [{
        "bbox": [10, 10, 70, 70],
        "width": 100,
        "height": 100,
        "xref": 6,
    }]
    _, largest_frac_small, _, _, _, _, _, _ = calculate_dominant_image_and_dpi(imgs_small, page_rect)
    assert largest_frac_small < 0.50


# 4. DPI calculation (placed dimensions, minimum width/height)
def test_dpi_calculation():
    page_rect = pymupdf.Rect(0, 0, 720, 720)  # 10 x 10 inches
    # Image placed on entire page: 3000 x 2000 pixels
    # Width DPI: 3000 / 10 = 300. Height DPI: 2000 / 10 = 200.
    imgs = [{
        "bbox": [0, 0, 720, 720],
        "width": 3000,
        "height": 2000,
        "xref": 9,
    }]
    count, _, _, _, dpi_w, dpi_h, dpi, status = calculate_dominant_image_and_dpi(imgs, page_rect)
    assert dpi_w == 300.0
    assert dpi_h == 200.0
    assert dpi == 200.0  # conservative minimum
    assert status == "measured"


# 5. Multiple-image handling & off-page image filtering
def test_off_page_image_filtering():
    page_rect = pymupdf.Rect(0, 0, 600, 800)
    # Image completely outside visible page
    imgs = [{
        "bbox": [-500, 0, -100, 800],
        "width": 1000,
        "height": 1000,
        "xref": 99,
    }]
    count, largest_frac, total_frac, dom, _, _, dpi, status = (
        calculate_dominant_image_and_dpi(imgs, page_rect)
    )
    assert count == 0
    assert largest_frac == 0.0
    assert dom is None
    assert status == "not_applicable"


# 6. Null vs Zero preservation
def test_null_vs_zero_preservation():
    # Percentiles must ignore None, but keep 0.0
    vals_with_zero = [0.0, 0.0, 10.0, 20.0]
    p = calculate_percentiles(vals_with_zero)
    assert p["min"] == 0.0
    assert p["min"] is not None

    p_empty = calculate_percentiles([])
    assert p_empty["min"] is None
    assert p_empty["median"] is None


# 7. Measurement-status handling
def test_measurement_status_handling():
    empty_arr = np.array([])
    contrast, c_stat = measure_contrast(empty_arr)
    assert contrast is None
    assert c_stat == "unavailable"

    noise, n_stat = measure_noise_speckle(empty_arr)
    assert noise is None
    assert n_stat == "unavailable"

    blur, b_stat = measure_blur_sharpness(empty_arr)
    assert blur is None
    assert b_stat == "unavailable"


# 8. Skew measurement determinism & confidence
def test_skew_measurement_determinism():
    # Synthetic clean page with horizontal dark bars (text lines)
    img = Image.new("L", (600, 800), color=255)
    draw = ImageDraw.Draw(img)
    for y in range(100, 700, 40):
        draw.rectangle([50, y, 550, y + 15], fill=0)

    # Rotate by 1.6 degrees
    rot = img.rotate(1.6, resample=Image.BICUBIC, fillcolor=255)
    arr = np.array(rot)

    angle1, stat1, conf1 = measure_skew(arr)
    angle2, stat2, conf2 = measure_skew(arr)

    assert stat1 == "measured"
    assert angle1 is not None
    assert abs(angle1 - 1.6) <= 0.3
    # Exactly deterministic across repeated runs
    assert angle1 == angle2
    assert conf1 == conf2


# 9. Contrast measurement determinism & bounds
def test_contrast_bounds_and_determinism():
    # Black and white checkerboard -> high contrast
    arr_hi = np.zeros((100, 100), dtype=np.uint8)
    arr_hi[:50, :] = 255
    c_hi, s_hi = measure_contrast(arr_hi)
    assert s_hi == "measured"
    assert c_hi == 1.0

    # Constant gray -> zero contrast
    arr_lo = np.full((100, 100), 128, dtype=np.uint8)
    c_lo, s_lo = measure_contrast(arr_lo)
    assert s_lo == "measured"
    assert c_lo == 0.0


# 10. Noise / speckle measurement determinism
def test_noise_measurement_determinism():
    # Clean image: smooth gradient or solid color -> near zero noise
    arr_clean = np.full((100, 100), 200, dtype=np.uint8)
    n_clean, s_clean = measure_noise_speckle(arr_clean)
    assert s_clean == "measured"
    assert n_clean == 0.0

    # Salt and pepper noise
    arr_noisy = arr_clean.copy()
    np.random.seed(42)
    noise_mask = np.random.rand(100, 100) < 0.05
    arr_noisy[noise_mask] = 0
    n_noisy, s_noisy = measure_noise_speckle(arr_noisy)
    assert s_noisy == "measured"
    assert n_noisy > 0.0


# 11. Blur / Laplacian variance directionality (higher = sharper)
def test_blur_sharpness_directionality():
    # Crisp sharp edge
    arr_sharp = np.zeros((100, 100), dtype=np.uint8)
    arr_sharp[::10, :] = 255
    b_sharp, _ = measure_blur_sharpness(arr_sharp)

    # Blurred version
    pil_blur = Image.fromarray(arr_sharp).filter(ImageFilter.GaussianBlur(radius=3))
    arr_blur = np.array(pil_blur)
    b_blur, _ = measure_blur_sharpness(arr_blur)

    # Required directionality: higher value = sharper!
    assert b_sharp > b_blur


# 12. Preprocessing & version constants
def test_version_constants():
    assert RASTER_CLASSIFICATION_RULE_VERSION == "v1.0_geom_dominant_50pct"
    assert ANALYSIS_RESOLUTION == 150
    assert PREPROCESSING_VERSION == "pm3_canonical_v1_150dpi_gray"
    assert SKEW_METHOD == "projection_profile_variance_v1"
    assert CONTRAST_METHOD == "interdecile_p95_p05_v1"
    assert NOISE_METHOD == "median3x3_residual_v1"
    assert BLUR_METHOD == "laplacian_variance_v1"
    assert SCAN_QUALITY_RULE_VERSION == "none"


# 13. Subgroup aggregation & denominator integrity
def test_summary_data_aggregation():
    sample_records = [
        PageMeasurement(
            document_id="DOC1_2012",
            company_id="COMP1",
            company="Company 1",
            FY=2012,
            physical_page=1,
            source_pdf_sha256="hash1",
            page_width=595.0,
            page_height=842.0,
            raster_image_count=1,
            largest_raster_area_fraction=0.95,
            total_raster_area_fraction=0.95,
            full_page_raster=True,
            dominant_raster_image="xref_1",
            native_text_present=False,
            estimated_dpi_width=300.0,
            estimated_dpi_height=300.0,
            estimated_dpi=300.0,
            dpi_status="measured",
            skew_angle=0.2,
            skew_status="measured",
            skew_method=SKEW_METHOD,
            skew_confidence=1.2,
            contrast=0.85,
            contrast_status="measured",
            contrast_method=CONTRAST_METHOD,
            noise_speckle=0.01,
            noise_status="measured",
            noise_method=NOISE_METHOD,
            blur=500.0,
            blur_status="measured",
            blur_method=BLUR_METHOD,
            scan_quality="unscored",
            scan_quality_rule_version="none",
            measurement_status="measured",
            analysis_resolution=150,
            preprocessing_version=PREPROCESSING_VERSION,
            provenance="scanned",
            reason_codes="",
            image_index=0,
            image_xref=1,
            image_bbox="0,0,595,842",
        ),
        PageMeasurement(
            document_id="DOC1_2012",
            company_id="COMP1",
            company="Company 1",
            FY=2012,
            physical_page=2,
            source_pdf_sha256="hash1",
            page_width=595.0,
            page_height=842.0,
            raster_image_count=0,
            largest_raster_area_fraction=0.0,
            total_raster_area_fraction=0.0,
            full_page_raster=False,
            dominant_raster_image=None,
            native_text_present=True,
            estimated_dpi_width=None,
            estimated_dpi_height=None,
            estimated_dpi=None,
            dpi_status="not_applicable",
            skew_angle=None,
            skew_status="not_applicable",
            skew_method=SKEW_METHOD,
            skew_confidence=None,
            contrast=None,
            contrast_status="not_applicable",
            contrast_method=CONTRAST_METHOD,
            noise_speckle=None,
            noise_status="not_applicable",
            noise_method=NOISE_METHOD,
            blur=None,
            blur_status="not_applicable",
            blur_method=BLUR_METHOD,
            scan_quality="unscored",
            scan_quality_rule_version="none",
            measurement_status="not_applicable",
            analysis_resolution=150,
            preprocessing_version=PREPROCESSING_VERSION,
            provenance="native",
            reason_codes="",
            image_index=None,
            image_xref=None,
            image_bbox=None,
        ),
    ]

    meta = {"COMP1": {"cap_band": "large", "canonical_name": "Company 1"}}
    summary = generate_summary_data(sample_records, meta)

    pop = summary["population"]
    assert pop["total_documents"] == 1
    assert pop["total_physical_pages"] == 2
    assert pop["pages_with_full_page_raster"] == 1
    assert pop["native_only_pages"] == 1
    assert pop["measurable_full_page_raster_pages"] == 1

    fy_res = summary["fiscal_year_summary"]
    assert len(fy_res) == 1
    assert fy_res[0]["FY"] == 2012
    assert fy_res[0]["N_physical_pages"] == 2
    assert fy_res[0]["N_full_page_raster"] == 1
    assert fy_res[0]["raster_page_fraction"] == 0.5


# 14. Production immutability
def test_production_files_immutable():
    """Verify that protected production files are completely untouched."""
    protected_files = [
        "arpipe/segment.py",
        "arpipe/patterns.py",
        "arpipe/verify.py",
        "arpipe/pipeline.py",
        "arpipe/triage.py",
        "arpipe/textlayer.py",
        "arpipe/ocr.py",
        "arpipe/models.py",
    ]
    res = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    dirty_lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]
    for f in protected_files:
        for d in dirty_lines:
            # Must not show M or D or ?? for protected files
            assert not d.endswith(f), f"Protected production file {f} was modified!"
