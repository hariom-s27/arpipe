"""Page-level triage: decide, per page, how text must be recovered.

This is the routing layer the whole cost model hangs on. A 250-page annual
report where only the 12 MD&A pages are scanned should cost 12 OCR pages,
not 250. So triage is per-page, never per-document.

Signals used (all cheap, all from the PDF object model - no rendering):
  * characters extracted by the text layer, normalised by page area
  * fraction of page area covered by text boxes vs raster images
  * whether the extracted text decodes (mojibake / missing ToUnicode CMap)
  * whether glyphs are drawn as vector paths instead of text runs
  * script of the text (Latin vs Devanagari vs other Indic)
  * column count, estimated by projecting text-box x-centres

Rendering (the expensive part) happens only for pages triage marks as needing
OCR, and only at the DPI implied by the embedded image resolution.
"""
from __future__ import annotations

import math
import statistics
from typing import Iterable

import pymupdf  # PyMuPDF

from .models import DocProfile, PageKind, PageProfile, Script
from .patterns import DEVANAGARI_RE, INDIC_BLOCKS_RE, MOJIBAKE_RE

# --- tunable thresholds ---------------------------------------------------
# Calibrated against a stratified sample of Indian annual reports; keep them
# in one place so they can be re-fit from a labelled set (see tools/calibrate).
MIN_CHARS_PER_PAGE = 120          # below this a page is "text-empty"
MIN_CHARS_DENSE = 600             # above this a page is comfortably digital
MAX_MOJIBAKE_RATIO = 0.02         # >2% undecodable glyphs => treat layer as junk
BIG_IMAGE_AREA_FRAC = 0.55        # an image covering >55% of the page is a scan
HYBRID_IMAGE_AREA_FRAC = 0.25     # image block big enough to hide real content
BLANK_CHARS = 15
VECTOR_PATH_TEXT_THRESHOLD = 400  # many tiny fill-paths + no text => vector text


def _rect_area(r: pymupdf.Rect) -> float:
    return max(0.0, r.width) * max(0.0, r.height)


def _union_area(rects: Iterable[pymupdf.Rect], clip: pymupdf.Rect,
                grid: int = 40) -> float:
    """Approximate union area via a coarse occupancy grid (fast, no shapely)."""
    if clip.is_empty:
        return 0.0
    cw, ch = clip.width / grid, clip.height / grid
    if cw <= 0 or ch <= 0:
        return 0.0
    cells: set[tuple[int, int]] = set()
    for r in rects:
        r = r & clip
        if r.is_empty:
            continue
        x0 = max(0, int((r.x0 - clip.x0) / cw))
        x1 = min(grid - 1, int((r.x1 - clip.x0) / cw))
        y0 = max(0, int((r.y0 - clip.y0) / ch))
        y1 = min(grid - 1, int((r.y1 - clip.y0) / ch))
        for i in range(x0, x1 + 1):
            for j in range(y0, y1 + 1):
                cells.add((i, j))
    return len(cells) / float(grid * grid)


def detect_script(text: str) -> Script:
    if not text.strip():
        return Script.UNKNOWN
    dev = len(DEVANAGARI_RE.findall(text))
    ind = len(INDIC_BLOCKS_RE.findall(text))
    latin = sum(1 for c in text if "a" <= c.lower() <= "z")
    total = dev + ind + latin
    if total == 0:
        return Script.UNKNOWN
    ind_frac = ind / total
    if ind_frac < 0.05:
        return Script.LATIN
    if ind_frac > 0.85:
        return Script.DEVANAGARI if dev >= ind * 0.8 else Script.OTHER_INDIC
    return Script.MIXED


def estimate_columns(spans_x: list[tuple[float, float]], page_width: float,
                     bins: int = 120) -> int:
    """Estimate column count from the x-extent histogram of text lines.

    A multi-column page has a persistent vertical gutter: a band of x values
    crossed by very few lines (only full-width headings and rules). We look
    for such bands inside the central 70% of the page. Indian annual reports
    typically use a 18-30 pt gutter on A4, so the minimum band width is set
    at 2.5% of the page width rather than the 5% that would be right for a
    scientific two-column paper.
    """
    if len(spans_x) < 10 or page_width <= 0:
        return 1
    cover = [0] * bins
    for x0, x1 in spans_x:
        b0 = max(0, min(bins - 1, int(x0 / page_width * bins)))
        b1 = max(0, min(bins - 1, int(x1 / page_width * bins)))
        for b in range(b0, b1 + 1):
            cover[b] += 1
    peak = max(cover) or 1
    lo, hi = int(bins * 0.15), int(bins * 0.85)
    empty_at = max(1, int(peak * 0.15))     # full-width headings cross the gutter
    min_run = max(2, int(bins * 0.025))     # ~15 pt on A4

    runs, run = [], 0
    for b in range(lo, hi):
        if cover[b] <= empty_at:
            run += 1
        else:
            if run >= min_run:
                runs.append(run)
            run = 0
    if run >= min_run:
        runs.append(run)

    if not runs:
        return 1
    return min(3, len(runs) + 1)


def profile_page(page: pymupdf.Page) -> PageProfile:
    """Profile a page from the object model only.

    Deliberately avoids page.get_text("rawdict"/"dict"): on an image-only page
    those serialise the embedded image bytes into Python, which costs ~1 s and
    tens of MB per page. "blocks" gives text bboxes without pixels, and
    get_image_info() gives image geometry without decoding.
    """
    rect = page.rect

    text = page.get_text("text") or ""
    n_chars = len(text.strip())
    n_words = len(text.split())

    # TEXTFLAGS_TEXT excludes image blocks, so no pixel data is serialised.
    # Line-level boxes (not block-level) are what the gutter detector needs:
    # a two-column page is often just two blocks, which carries no signal.
    text_rects: list[pymupdf.Rect] = []
    spans_x: list[tuple[float, float]] = []
    try:
        d = page.get_text("dict", flags=pymupdf.TEXTFLAGS_TEXT)
    except Exception:
        d = {"blocks": []}
    for blk in d.get("blocks", []):
        if blk.get("type") != 0:
            continue
        text_rects.append(pymupdf.Rect(blk["bbox"]))
        for line in blk.get("lines", []):
            lb = line.get("bbox")
            if lb:
                spans_x.append((lb[0], lb[2]))

    img_rects: list[pymupdf.Rect] = []
    img_infos: list[dict] = []
    try:
        img_infos = page.get_image_info()
        img_rects = [pymupdf.Rect(i["bbox"]) for i in img_infos]
    except Exception:
        pass

    text_area = _union_area(text_rects, rect)
    image_area = _union_area(img_rects, rect)

    moji = len(MOJIBAKE_RE.findall(text))
    mojibake_ratio = moji / max(1, len(text))
    script = detect_script(text)
    n_columns = estimate_columns(spans_x, rect.width)

    n_drawings = 0
    if n_chars < MIN_CHARS_PER_PAGE and image_area < HYBRID_IMAGE_AREA_FRAC:
        try:
            n_drawings = len(page.get_drawings())
        except Exception:
            n_drawings = 0

    dpi = None
    if img_infos:
        try:
            best = max(img_infos, key=lambda i: i["width"] * i["height"])
            w_pt = max(1e-6, pymupdf.Rect(best["bbox"]).width)
            dpi = int(round(best["width"] / (w_pt / 72.0)))
        except Exception:
            dpi = None

    kind = _classify(n_chars, text_area, image_area, mojibake_ratio, n_drawings)

    return PageProfile(
        page_no=page.number,
        kind=kind,
        n_chars=n_chars,
        n_words=n_words,
        text_area_frac=round(text_area, 4),
        image_area_frac=round(image_area, 4),
        n_images=len(img_rects),
        n_columns=n_columns,
        script=script,
        mojibake_ratio=round(mojibake_ratio, 5),
        dpi_estimate=dpi,
        rotation=page.rotation,
    )


def _classify(n_chars: int, text_area: float, image_area: float,
              mojibake_ratio: float, n_drawings: int) -> PageKind:
    if n_chars < BLANK_CHARS and image_area < 0.05 and n_drawings < 20:
        return PageKind.BLANK
    if n_chars >= MIN_CHARS_PER_PAGE and mojibake_ratio > MAX_MOJIBAKE_RATIO:
        return PageKind.BROKEN_TEXT
    if n_chars < MIN_CHARS_PER_PAGE:
        if image_area >= BIG_IMAGE_AREA_FRAC:
            return PageKind.SCANNED
        if n_drawings >= VECTOR_PATH_TEXT_THRESHOLD:
            return PageKind.VECTOR_TEXT
        if image_area >= HYBRID_IMAGE_AREA_FRAC:
            return PageKind.SCANNED
        return PageKind.BLANK if n_chars < BLANK_CHARS else PageKind.DIGITAL
    # has usable text
    if image_area >= HYBRID_IMAGE_AREA_FRAC and n_chars < MIN_CHARS_DENSE:
        # e.g. a scanned certificate pasted into a digital report, or a page
        # whose body is an image with only a running header as real text
        return PageKind.HYBRID
    return PageKind.DIGITAL


NEEDS_OCR = {PageKind.SCANNED, PageKind.BROKEN_TEXT,
             PageKind.VECTOR_TEXT, PageKind.HYBRID}


def profile_document(path: str, max_pages: int | None = None) -> DocProfile:
    doc = pymupdf.open(path)
    try:
        pages: list[PageProfile] = []
        n = doc.page_count if max_pages is None else min(doc.page_count, max_pages)
        for i in range(n):
            pages.append(profile_page(doc.load_page(i)))

        outline: list[tuple[int, str, int]] = []
        try:
            for lvl, title, pno, *_ in doc.get_toc(simple=False):
                outline.append((lvl, title.strip(), max(0, pno - 1)))
        except Exception:
            outline = []

        content = [p for p in pages if p.kind is not PageKind.BLANK]
        ocr_pages = [p for p in content if p.kind in NEEDS_OCR]
        frac = len(ocr_pages) / max(1, len(content))
        if frac >= 0.85:
            doc_kind = "scanned"
        elif frac <= 0.05:
            doc_kind = "digital"
        else:
            doc_kind = "mixed"

        scripts = [p.script for p in content if p.script is not Script.UNKNOWN]
        dominant = Script.LATIN
        bilingual = False
        if scripts:
            indic = sum(1 for s in scripts
                        if s in (Script.DEVANAGARI, Script.OTHER_INDIC, Script.MIXED))
            frac_indic = indic / len(scripts)
            bilingual = 0.08 <= frac_indic <= 0.92
            dominant = Script.LATIN if frac_indic < 0.5 else Script.DEVANAGARI

        import hashlib
        with open(path, "rb") as fh:
            sha = hashlib.sha256(fh.read()).hexdigest()

        return DocProfile(
            sha256=sha, n_pages=doc.page_count, pages=pages, doc_kind=doc_kind,
            frac_needing_ocr=round(frac, 4), has_outline=bool(outline),
            outline_titles=outline, bilingual=bilingual, dominant_script=dominant,
        )
    finally:
        doc.close()


def ocr_page_numbers(profile: DocProfile) -> list[int]:
    return [p.page_no for p in profile.pages if p.kind in NEEDS_OCR]
