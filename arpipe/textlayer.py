"""Reading-order-aware text extraction from born-digital pages.

PyMuPDF's `sort=True` sorts blocks by (y, x), which shreds two-column
pages: it interleaves left and right columns line by line. Indian annual
reports are heavily two-column (MD&A and Corporate Governance especially),
so we run a recursive XY-cut over the block boxes instead. XY-cut is the
classical Nagy algorithm; it is cheap, deterministic and - unlike a learned
reading-order model - has no failure mode where it invents text.

For pages that are neither cleanly one- nor two-column (magazine-style
"About us" spreads), we fall back to column clustering on x-centres.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

import pymupdf

from . import triage
from .patterns import (LIGATURE_FIXES, NUMERIC_LINE_RE, PAGE_NUM_LINE_RE,
                       REPEATED_HEADER_MIN_PAGES, TABLE_LABEL_RE)

# --- column-split recovery (P16B) ---------------------------------------------
# A single full-width block (running head, footer, rule, full-width heading)
# collapses the widest block-x interval to ~0, so _gap_cut never fires and
# xy_cut falls back to the naive (y, x) sort that interleaves the two columns.
# _column_cut recovers the split from the blocks that are NOT full-width.
#
# Both constants are PROVISIONAL - picked from the four sample documents, to be
# re-fit against the labelled 300 and moved to config in P15.
COLUMN_FULLWIDTH_FRAC = 0.60   # a block wider than this * the text band spans
                               # the page and is not evidence of a column
COLUMN_CENTRE_GAP_FRAC = 0.14  # min gap between two clusters of block centres,
                               # as a fraction of page width, to call them
                               # separate columns. The iLovePDF-shredded Jain
                               # reports have a real ~15 pt (2.5%) gutter that
                               # the projection-profile min-run just misses;
                               # the centre-to-centre gap is far wider and
                               # clears cleanly.


@dataclass(slots=True)
class Block:
    x0: float
    y0: float
    x1: float
    y1: float
    text: str

    @property
    def w(self) -> float: return self.x1 - self.x0
    @property
    def h(self) -> float: return self.y1 - self.y0


def _blocks(page: pymupdf.Page) -> list[Block]:
    out: list[Block] = []
    for b in page.get_text("blocks"):
        x0, y0, x1, y1, txt, _no, btype = b[:7]
        if btype != 0:
            continue
        txt = (txt or "").strip()
        if txt:
            out.append(Block(x0, y0, x1, y1, txt))
    return out


def _gap_cut(vals: list[tuple[float, float]], lo: float, hi: float,
             min_gap: float) -> float | None:
    """Find the widest empty interval in [lo,hi] given (start,end) spans."""
    if not vals:
        return None
    spans = sorted(vals)
    cur = spans[0][1]
    best_gap, best_at = 0.0, None
    for s, e in spans[1:]:
        if s - cur > best_gap:
            best_gap, best_at = s - cur, (cur + s) / 2.0
        cur = max(cur, e)
    if best_at is None or best_gap < min_gap:
        return None
    # ignore cuts too close to the page edge (margins, side tabs)
    if not (lo + 0.12 * (hi - lo) < best_at < hi - 0.12 * (hi - lo)):
        return None
    return best_at


def _column_cut(blocks: list[Block], page: pymupdf.Rect,
                depth: int) -> list[Block] | None:
    """Split into columns when a full-width block has masked the gutter from
    _gap_cut. The non-full-width blocks are split, each column is ordered
    recursively, and the full-width blocks are re-inserted at their y position.

    Two ways to find the split, tried in order:
      1. the triage projection-profile gutter over the non-full-width block
         x-spans (the well-tested path; fires on wide-gutter layouts)
      2. the widest gap between block centres (catches the ~2.5% gutter on
         line-shredded pages, which the projection-profile min-run just misses)

    Returns the ordered block list, or None if no column split was found.
    """
    if len(blocks) < 4:
        return None
    text_w = max(b.x1 for b in blocks) - min(b.x0 for b in blocks)
    if text_w <= 0:
        return None
    voting = [b for b in blocks if b.w <= COLUMN_FULLWIDTH_FRAC * text_w]
    wide = [b for b in blocks if b.w > COLUMN_FULLWIDTH_FRAC * text_w]
    if len(voting) < 4:
        return None

    split_x: float | None = None
    bands = triage.gutter_bands([(b.x0, b.x1) for b in voting], page.width)
    if bands:
        split_x = min(((lo + hi) / 2 for lo, hi in bands),
                      key=lambda x: abs(x - page.width / 2))
    else:
        centres = sorted((b.x0 + b.x1) / 2 for b in voting)
        gap, at = 0.0, None
        for lo, hi in zip(centres, centres[1:]):
            if hi - lo > gap:
                gap, at = hi - lo, (lo + hi) / 2
        if at is not None and gap >= COLUMN_CENTRE_GAP_FRAC * page.width:
            split_x = at
    if split_x is None:
        return None

    left = [b for b in voting if (b.x0 + b.x1) / 2 < split_x]
    right = [b for b in voting if (b.x0 + b.x1) / 2 >= split_x]
    if min(len(left), len(right)) < 2:
        return None

    ordered = xy_cut(left, page, depth + 1) + xy_cut(right, page, depth + 1)
    for wb in sorted(wide, key=lambda b: b.y0):
        pos = next((i for i, b in enumerate(ordered) if b.y0 >= wb.y0),
                   len(ordered))
        ordered.insert(pos, wb)
    return ordered


def xy_cut(blocks: list[Block], page: pymupdf.Rect, depth: int = 0) -> list[Block]:
    """Recursively split on the widest vertical then horizontal whitespace."""
    if len(blocks) <= 1 or depth > 6:
        return sorted(blocks, key=lambda b: (round(b.y0, 1), b.x0))

    min_v_gap = max(10.0, page.width * 0.025)   # a real gutter, not word spacing
    xs = [(b.x0, b.x1) for b in blocks]
    x_at = _gap_cut(xs, min(b.x0 for b in blocks), max(b.x1 for b in blocks), min_v_gap)
    if x_at is not None:
        left = [b for b in blocks if (b.x0 + b.x1) / 2 < x_at]
        right = [b for b in blocks if (b.x0 + b.x1) / 2 >= x_at]
        if left and right:
            return xy_cut(left, page, depth + 1) + xy_cut(right, page, depth + 1)

    if depth <= 4:
        col = _column_cut(blocks, page, depth)
        if col is not None:
            return col

    min_h_gap = max(8.0, page.height * 0.02)
    ys = [(b.y0, b.y1) for b in blocks]
    y_at = _gap_cut(ys, min(b.y0 for b in blocks), max(b.y1 for b in blocks), min_h_gap)
    if y_at is not None:
        top = [b for b in blocks if (b.y0 + b.y1) / 2 < y_at]
        bot = [b for b in blocks if (b.y0 + b.y1) / 2 >= y_at]
        if top and bot:
            return xy_cut(top, page, depth + 1) + xy_cut(bot, page, depth + 1)

    return sorted(blocks, key=lambda b: (round(b.y0, 1), b.x0))


def page_text(page: pymupdf.Page, reading_order: bool = True) -> str:
    blocks = _blocks(page)
    if not blocks:
        return ""
    if reading_order:
        blocks = xy_cut(blocks, page.rect)
    else:
        blocks.sort(key=lambda b: (round(b.y0, 1), b.x0))
    return "\n\n".join(b.text for b in blocks)


# --- table / chart quarantine (P18) -----------------------------------------
# Chart axis dumps and table cells arrive in the text layer as loose numbers
# ("283.68", "21,442.95 22,003.14", "9.54%"). A document-level digit ratio
# cannot see them - a few hundred characters of table diluted in a
# 15,000-word section. Detect them per block, lift consecutive numeric runs
# into a sidecar (mda_blocks.json), and keep the figures out of the prose word
# and digit counts.
#
# The pass is deliberately conservative on prose, not on tables. A quarantined
# run must be anchored by a numeric block at each end and hold >= TABLE_MIN_RUN
# numeric lines. Row / column / axis labels ("FY 18", "Change",
# "Material Cost/Total Income (%)") only BRIDGE a run that numeric lines
# already anchor at both ends - a label never starts a run or extends one past
# its last figure. A block is prose (digits and all) if any line runs over
# TABLE_PROSE_LINE_WORDS words, if a short line carries two-plus stop-words, or
# if it is a lone long word (a shredded heading). Column interleaving on the
# iLovePDF-sourced Jain filings still drops the odd table header
# ("Particulars 31st Mar", "m) Shareholder's Fund") between two numeric cells;
# a header on its own line stays in the prose, one wedged inside a run rides
# to the sidecar with that table (recoverable there, never deleted). Cleaning
# that fully means repairing the shredded fetch source upstream.
#
# PROVISIONAL constants - picked from the four sample documents, to be re-fit
# against the labelled 300 and moved to config in P15.
TABLE_DIGIT_RATIO = 0.40       # digits / (letters + digits) within a block
TABLE_MAX_WORDS_PER_LINE = 6   # a data row is short; wrapped prose runs long
TABLE_MIN_RUN = 3              # numeric lines in a run to call it a region
TABLE_LABEL_MAX_CHARS = 44     # a row / column label is short
TABLE_LABEL_MAX_WORDS = 6
TABLE_PROSE_LINE_WORDS = 12    # a line this long is a sentence, not a cell

_LABEL_STOPWORDS = frozenset(
    "a an the is are was were be been of to and or in on for with as at from "
    "that this it we our their has have had will would than by".split())


def _digit_letter_ratio(s: str) -> float:
    d = sum(c.isdigit() for c in s)
    a = sum(c.isalpha() for c in s)
    return d / (d + a) if (d + a) else 0.0


def _nonblank_lines(text: str) -> list[str]:
    return [ln.strip() for ln in text.split("\n") if ln.strip()]


def _numeric_line_count(text: str) -> int:
    return sum(1 for ln in _nonblank_lines(text) if NUMERIC_LINE_RE.match(ln))


def _is_data_block(b: Block) -> bool:
    """A table/chart data block: three-plus numeric-only lines stacked in one
    block, or mostly digits with short lines (SEBI Schedule V ratio rows,
    chart axis dumps, cell fragments). A block that also carries a full
    sentence is prose, never data - a shredded cell line is short."""
    lines = _nonblank_lines(b.text)
    if not lines or any(len(ln.split()) > TABLE_PROSE_LINE_WORDS for ln in lines):
        return False
    if _numeric_line_count(b.text) >= TABLE_MIN_RUN:
        return True
    words = b.text.split()
    wpl = len(words) / len(lines)
    return (_digit_letter_ratio(b.text) >= TABLE_DIGIT_RATIO
            and wpl < TABLE_MAX_WORDS_PER_LINE)


def _is_label_block(b: Block) -> bool:
    """A row / column / axis label ('FY 18', '31st Mar', 'Change',
    'Material Cost/Total Income (%)'). Short and not sentence-shaped. Bridges a
    numeric run only; never anchors, extends or carries one."""
    s = " ".join(_nonblank_lines(b.text)).strip()
    words = s.split()
    if (not s or len(s) > TABLE_LABEL_MAX_CHARS or not words
            or len(words) > TABLE_LABEL_MAX_WORDS or s[-1] in ".:;!?"):
        return False
    if _is_data_block(b):
        return False                                    # figures -> data
    if TABLE_LABEL_RE.match(s):
        return True
    letters = [c for c in s if c.isalpha()]
    if not letters:
        return False                                    # bare punctuation
    if sum(1 for w in words if w.lower().strip(".,()%/") in _LABEL_STOPWORDS) >= 2:
        return False                                    # sentence-shaped
    if len(words) >= 2 and all(c.isupper() for c in letters):
        return False                                    # ALL-CAPS heading
    if len(words) == 1 and len(s.strip(".,)")) > 10:
        return False                                    # a lone long word is a
                                                        # shredded heading, not
                                                        # a column label
    return True


_PERIOD_LABEL_RE = re.compile(
    r"^(?:FY\s?\d{2,4}(?:\s*-\s*\d{2,4})?|Q[1-4]|H[12]|CY\s?\d{2,4}"
    r"|\d{1,2}(?:st|nd|rd|th)?\s+[A-Z][a-z]{2,8}\.?|%|YoY|QoQ)$")


def _quarantine_entry(page_no: int, run: list[Block]) -> dict:
    joined = "\n".join(b.text.strip() for b in run)
    lines = _nonblank_lines(joined)
    # a chart is a bare axis/series dump: single-value numeric lines and, at
    # most, period labels (FY 18, Q3). A row/column word label ("Net Block",
    # "Total Income") or a multi-value line ("21,442.95 22,003.14") means it
    # is a table.
    word_label = any(not NUMERIC_LINE_RE.match(ln)
                     and not _PERIOD_LABEL_RE.match(ln)
                     and sum(c.isalpha() for c in ln) >= 3
                     for ln in lines)
    multi = any(len(ln.split()) > 1 for ln in lines if NUMERIC_LINE_RE.match(ln))
    geom = [b for b in run if (b.x1 - b.x0) or (b.y1 - b.y0)]
    bbox = ([round(min(b.x0 for b in geom), 1), round(min(b.y0 for b in geom), 1),
             round(max(b.x1 for b in geom), 1), round(max(b.y1 for b in geom), 1)]
            if geom else None)
    return {
        "page": page_no,
        "bbox": bbox,
        "kind": "table" if (word_label or multi) else "chart",
        "text": joined,
        "digit_ratio": round(_digit_letter_ratio(joined), 3),
        "n_lines": len(lines),
    }


def _quarantine_page(page_no: int, blocks: list[Block]) -> tuple[list[Block],
                                                                list[dict]]:
    """Split one page's ordered blocks into (prose blocks, quarantined runs)."""
    tag = ["d" if _is_data_block(b) else "l" if _is_label_block(b) else "p"
           for b in blocks]
    kept: list[Block] = []
    entries: list[dict] = []
    i, n = 0, len(blocks)
    while i < n:
        if tag[i] != "d":
            kept.append(blocks[i])
            i += 1
            continue
        j, last_data = i, i
        while j < n and tag[j] in ("d", "l"):
            if tag[j] == "d":
                last_data = j
            j += 1
        run = blocks[i:last_data + 1]                 # trim trailing labels
        numeric_lines = sum(_numeric_line_count(b.text) for b in run)
        if numeric_lines >= TABLE_MIN_RUN:
            entries.append(_quarantine_entry(page_no, run))
            kept.extend(blocks[last_data + 1:j])      # bridging labels -> prose
        else:
            kept.extend(blocks[i:j])                  # not enough figures -> prose
        i = j
    return kept, entries


def extract_prose_and_tables(
        path: str, span_pages: list[int], page_texts: dict[int, str],
        digital_pages: set[int]) -> tuple[list[str], list[dict]]:
    """Per span page, return (prose text with tables/charts removed,
    quarantined block records). Digital pages are re-read for block geometry;
    OCR / fetched pages fall back to splitting the extracted string on blank
    lines, so their quarantined records carry no bbox.
    """
    doc = pymupdf.open(path)
    try:
        prose: list[str] = []
        quarantined: list[dict] = []
        for pno in span_pages:
            if pno in digital_pages:
                page = doc.load_page(pno)
                blocks = xy_cut(_blocks(page), page.rect)
            else:
                blocks = [Block(0.0, 0.0, 0.0, 0.0, seg)
                          for seg in re.split(r"\n\s*\n", page_texts.get(pno, ""))
                          if seg.strip()]
            kept, entries = _quarantine_page(pno, blocks)
            prose.append(normalise("\n\n".join(b.text for b in kept)))
            quarantined.extend(entries)
        return prose, quarantined
    finally:
        doc.close()


def normalise(text: str) -> str:
    for a, b in LIGATURE_FIXES.items():
        text = text.replace(a, b)
    # de-hyphenate words broken across lines: "manage-\nment" -> "management"
    out, lines = [], text.split("\n")
    i = 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if ln.endswith("-") and i + 1 < len(lines) and lines[i + 1][:1].islower():
            nxt = lines[i + 1].lstrip()
            head, _, tail = nxt.partition(" ")
            out.append(ln[:-1] + head)
            lines[i + 1] = tail
            i += 1
            continue
        out.append(ln)
        i += 1
    return "\n".join(out)


def strip_running_furniture(pages: list[str],
                            min_pages: int = REPEATED_HEADER_MIN_PAGES) -> list[str]:
    """Remove headers/footers/page numbers that repeat across many pages.

    Running heads in Indian annual reports frequently contain the company
    name, which would otherwise dominate any 'does this page belong to X'
    check and also pollute the MD&A text.
    """
    from collections import Counter

    def cand(p: str) -> list[str]:
        ls = [l.strip() for l in p.split("\n") if l.strip()]
        return ls[:2] + ls[-2:]

    counts: Counter[str] = Counter()
    for p in pages:
        counts.update(set(cand(p)))

    thresh = max(min_pages, int(0.35 * len(pages)))
    furniture = {k for k, v in counts.items() if v >= thresh and len(k) < 120}

    cleaned = []
    for p in pages:
        keep = []
        for ln in p.split("\n"):
            s = ln.strip()
            if s in furniture:
                continue
            if PAGE_NUM_LINE_RE.match(s):
                continue
            keep.append(ln)
        cleaned.append("\n".join(keep))
    return cleaned


def extract_pages(path: str, page_nos: list[int] | None = None,
                  reading_order: bool = True) -> dict[int, str]:
    doc = pymupdf.open(path)
    try:
        nos = page_nos if page_nos is not None else range(doc.page_count)
        return {n: normalise(page_text(doc.load_page(n), reading_order))
                for n in nos if 0 <= n < doc.page_count}
    finally:
        doc.close()
