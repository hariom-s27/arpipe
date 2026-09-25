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
from .verify import (_ALPHA_WORD_RE, _COMMON_ENGLISH_WORDS,
                     WRONG_LANGUAGE_MIN_TOKENS)

# --- tunable thresholds ---------------------------------------------------
# All thresholds provisional until re-fit against the labelled 300.
# provisional until re-fit against the labelled 300
MIN_CHARS_PER_PAGE = 120          # below this a page is "text-empty"
# provisional until re-fit against the labelled 300
MIN_CHARS_DENSE = 600             # above this a page is comfortably digital
# provisional until re-fit against the labelled 300
MAX_MOJIBAKE_RATIO = 0.02         # >2% undecodable glyphs => treat layer as junk
# provisional until re-fit against the labelled 300
BIG_IMAGE_AREA_FRAC = 0.55        # an image covering >55% of the page is a scan
# provisional until re-fit against the labelled 300
HYBRID_IMAGE_AREA_FRAC = 0.25     # image block big enough to hide real content
# provisional until re-fit against the labelled 300
BLANK_CHARS = 15
# provisional until re-fit against the labelled 300
VECTOR_PATH_TEXT_THRESHOLD = 400  # many tiny fill-paths + no text => vector text
# provisional until re-fit against the labelled 300
COLUMN_HIST_BINS = 120            # histogram bin count behind the reading-order bug
# provisional until re-fit against the labelled 300
GUTTER_MIN_RUN_FRAC = 0.025       # gutter fraction behind the reading-order bug (2.5%)
# provisional until re-fit against the labelled 300
GUTTER_PEAK_THRESHOLD = 0.15
# provisional until re-fit against the labelled 300
GUTTER_SEARCH_LO = 0.15
# provisional until re-fit against the labelled 300
GUTTER_SEARCH_HI = 0.85
# provisional until re-fit against the labelled 300
DOC_SCANNED_FRAC = 0.85
# provisional until re-fit against the labelled 300
DOC_DIGITAL_FRAC = 0.05


def configure(cfg: dict | None = None) -> None:
    """Update thresholds from resolved configuration."""
    global MIN_CHARS_PER_PAGE, MIN_CHARS_DENSE, MAX_MOJIBAKE_RATIO
    global BIG_IMAGE_AREA_FRAC, HYBRID_IMAGE_AREA_FRAC, BLANK_CHARS
    global VECTOR_PATH_TEXT_THRESHOLD, COLUMN_HIST_BINS, GUTTER_MIN_RUN_FRAC
    global GUTTER_PEAK_THRESHOLD, GUTTER_SEARCH_LO, GUTTER_SEARCH_HI
    global DOC_SCANNED_FRAC, DOC_DIGITAL_FRAC
    if not cfg:
        return
    MIN_CHARS_PER_PAGE = cfg.get("min_chars_per_page", MIN_CHARS_PER_PAGE)
    MIN_CHARS_DENSE = cfg.get("min_chars_dense", MIN_CHARS_DENSE)
    MAX_MOJIBAKE_RATIO = cfg.get("max_mojibake_ratio", MAX_MOJIBAKE_RATIO)
    BIG_IMAGE_AREA_FRAC = cfg.get("big_image_area_frac", BIG_IMAGE_AREA_FRAC)
    HYBRID_IMAGE_AREA_FRAC = cfg.get("hybrid_image_area_frac", HYBRID_IMAGE_AREA_FRAC)
    BLANK_CHARS = cfg.get("blank_chars", BLANK_CHARS)
    VECTOR_PATH_TEXT_THRESHOLD = cfg.get("vector_path_text_threshold", VECTOR_PATH_TEXT_THRESHOLD)
    COLUMN_HIST_BINS = cfg.get("column_hist_bins", COLUMN_HIST_BINS)
    GUTTER_MIN_RUN_FRAC = cfg.get("gutter_min_run_frac", GUTTER_MIN_RUN_FRAC)
    GUTTER_PEAK_THRESHOLD = cfg.get("gutter_peak_threshold", GUTTER_PEAK_THRESHOLD)
    GUTTER_SEARCH_LO = cfg.get("gutter_search_lo", GUTTER_SEARCH_LO)
    GUTTER_SEARCH_HI = cfg.get("gutter_search_hi", GUTTER_SEARCH_HI)
    DOC_SCANNED_FRAC = cfg.get("doc_scanned_frac", DOC_SCANNED_FRAC)
    DOC_DIGITAL_FRAC = cfg.get("doc_digital_frac", DOC_DIGITAL_FRAC)


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


def gutter_bands(spans_x: list[tuple[float, float]], page_width: float,
                 bins: int | None = None) -> list[tuple[float, float]]:
    """x-ranges (points, left to right) of vertical whitespace bands in the
    central 70% of the page: a band of x values crossed by very few text lines
    (only full-width headings and rules). This is the column-gutter detector;
    ``estimate_columns`` just counts what it returns, and ``textlayer.xy_cut``
    uses the positions to place its column split.

    Indian annual reports typically use an 18-30 pt gutter on A4, so the
    minimum band width is 2.5% of the page width rather than the 5% that would
    be right for a scientific two-column paper.
    """
    b_count = bins if bins is not None else COLUMN_HIST_BINS
    if len(spans_x) < 10 or page_width <= 0:
        return []
    cover = [0] * b_count
    for x0, x1 in spans_x:
        b0 = max(0, min(b_count - 1, int(x0 / page_width * b_count)))
        b1 = max(0, min(b_count - 1, int(x1 / page_width * b_count)))
        for b in range(b0, b1 + 1):
            cover[b] += 1
    peak = max(cover) or 1
    lo, hi = int(b_count * GUTTER_SEARCH_LO), int(b_count * GUTTER_SEARCH_HI)
    empty_at = max(1, int(peak * GUTTER_PEAK_THRESHOLD))     # full-width headings cross the gutter
    min_run = max(2, int(b_count * GUTTER_MIN_RUN_FRAC))     # ~15 pt on A4

    bands: list[tuple[float, float]] = []
    start = None
    for b in range(lo, hi):
        if cover[b] <= empty_at:
            if start is None:
                start = b
        elif start is not None:
            if b - start >= min_run:
                bands.append((start / b_count * page_width, b / b_count * page_width))
            start = None
    if start is not None and hi - start >= min_run:
        bands.append((start / b_count * page_width, hi / b_count * page_width))
    return bands


def estimate_columns(spans_x: list[tuple[float, float]], page_width: float,
                     bins: int | None = None) -> int:
    """Estimate column count from the x-extent histogram of text lines."""
    if len(spans_x) < 10 or page_width <= 0:
        return 1
    b_count = bins if bins is not None else COLUMN_HIST_BINS
    return min(3, len(gutter_bands(spans_x, page_width, b_count)) + 1)


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

    script_meta = _compute_page_script_meta(
        page_no=page.number,
        text=text,
        n_chars=n_chars,
        kind=kind,
        script=script,
        mojibake_ratio=mojibake_ratio,
    )

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
        script_meta=script_meta,
    )


def _compute_page_script_meta(
    page_no: int,
    text: str,
    n_chars: int,
    kind: PageKind,
    script: Script,
    mojibake_ratio: float,
) -> dict[str, Any]:
    """Derive page-level script/language telemetry reusing existing triage signals."""
    if not text.strip() or kind in (PageKind.BLANK, PageKind.SCANNED, PageKind.VECTOR_TEXT):
        devanagari_frac = None
        english_word_frac = None
        dominant_script = "unknown"
        script_confidence = "unknown"
    else:
        devanagari_frac = round(len(DEVANAGARI_RE.findall(text)) / len(text), 4)
        words = _ALPHA_WORD_RE.findall(text)
        lower_words = [w.lower() for w in words if len(w) >= 2]
        if len(lower_words) >= WRONG_LANGUAGE_MIN_TOKENS:
            english_word_frac = round(
                sum(1 for w in lower_words if w in _COMMON_ENGLISH_WORDS) / len(lower_words), 4
            )
        else:
            english_word_frac = None

        if script == Script.LATIN:
            dominant_script = "english"
        elif script == Script.DEVANAGARI:
            dominant_script = "devanagari"
        elif script == Script.MIXED:
            dominant_script = "bilingual"
        elif script == Script.OTHER_INDIC:
            dominant_script = "other"
        else:
            dominant_script = "unknown"

        if dominant_script == "unknown":
            script_confidence = "unknown"
        elif kind == PageKind.BROKEN_TEXT or mojibake_ratio > MAX_MOJIBAKE_RATIO:
            script_confidence = "low"
        elif kind == PageKind.DIGITAL and n_chars >= MIN_CHARS_DENSE:
            script_confidence = "high"
        elif kind == PageKind.HYBRID or n_chars >= MIN_CHARS_PER_PAGE:
            script_confidence = "medium"
        else:
            script_confidence = "low"

    return {
        "page_no": page_no,
        "devanagari_frac": devanagari_frac,
        "english_word_frac": english_word_frac,
        "legacy_font_suspected": "unknown",
        "dominant_script": dominant_script,
        "script_confidence": script_confidence,
        "measurement_source": "existing_triage_telemetry",
    }


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
        if frac >= DOC_SCANNED_FRAC:
            doc_kind = "scanned"
        elif frac <= DOC_DIGITAL_FRAC:
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

        script_map = [p.script_meta for p in pages if p.script_meta is not None]

        import hashlib
        with open(path, "rb") as fh:
            sha = hashlib.sha256(fh.read()).hexdigest()

        return DocProfile(
            sha256=sha, n_pages=doc.page_count, pages=pages, doc_kind=doc_kind,
            frac_needing_ocr=round(frac, 4), has_outline=bool(outline),
            outline_titles=outline, bilingual=bilingual, dominant_script=dominant,
            script_map=script_map,
        )
    finally:
        doc.close()


def ocr_page_numbers(profile: DocProfile) -> list[int]:
    return [p.page_no for p in profile.pages if p.kind in NEEDS_OCR]
