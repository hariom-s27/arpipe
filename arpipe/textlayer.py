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

from dataclasses import dataclass

import pymupdf

from .patterns import LIGATURE_FIXES, PAGE_NUM_LINE_RE, REPEATED_HEADER_MIN_PAGES


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
