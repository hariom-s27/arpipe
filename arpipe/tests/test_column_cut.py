"""Synthetic-block tests for _column_cut and xy_cut.

_column_cut is the single most important function in the pipeline: it is
what P16B added, it is what stops the corpus being scrambled.  These tests
exercise it (and the xy_cut wrapper) on synthetic block lists — no PDFs,
no fixtures, millisecond runtimes.

Run:  python -m pytest arpipe/tests/test_column_cut.py -v
"""
from __future__ import annotations

import os
import random
import sys
from collections import Counter

import pymupdf
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from arpipe.textlayer import (                                    # noqa: E402
    Block, _column_cut, xy_cut,
    COLUMN_FULLWIDTH_FRAC, COLUMN_CENTRE_GAP_FRAC,
)

# ── helpers ──────────────────────────────────────────────────────────

_A4 = pymupdf.Rect(0, 0, 595, 842)


def _b(x0: float, y0: float, x1: float, y1: float, text: str = "") -> Block:
    """Build a Block with optional auto-generated text."""
    return Block(x0, y0, x1, y1, text or f"blk_{x0:.0f}_{y0:.0f}")


def _words(blocks: list[Block]) -> Counter:
    """Multiset of tokens across a block list."""
    return Counter(w for b in blocks for w in b.text.split())


def _all_left_before_right(ordered: list[Block],
                           left_x1: float, right_x0: float) -> bool:
    """True if every block with x1 ≤ left_x1 precedes every block with
    x0 ≥ right_x0 in the ordered list."""
    last_left_idx = -1
    first_right_idx = len(ordered)
    for i, b in enumerate(ordered):
        if b.x1 <= left_x1 + 1:          # +1 for float tolerance
            last_left_idx = i
        if b.x0 >= right_x0 - 1:
            first_right_idx = min(first_right_idx, i)
    return last_left_idx < first_right_idx


# ── layout builders ─────────────────────────────────────────────────
# Every builder returns a plain list[Block] with realistic geometry on an
# A4 page (595 × 842 pt).  All text is unique so word-conservation tests
# can diff inputs vs outputs token-by-token.

def _two_col_blocks(n_per_col: int = 6, y_start: float = 100,
                    y_step: float = 40) -> list[Block]:
    """Clean two-column: left x[56,288], right x[303,540], 595pt page."""
    blocks: list[Block] = []
    for i in range(n_per_col):
        y = y_start + i * y_step
        blocks.append(_b(56, y, 288, y + 30, f"left_{i}"))
        blocks.append(_b(303, y, 540, y + 30, f"right_{i}"))
    return blocks


def _jain_blocks() -> list[Block]:
    """The Jain case: two columns PLUS a full-width footer at x[62,577].

    The footer spans 86 % of the page width.  Before P16B the full-width
    block collapsed the projection-profile gutter to zero, _gap_cut never
    fired, and xy_cut fell back to the naive (y,x) sort that interleaves
    left and right columns line by line.  _column_cut recovers the split
    by filtering out the full-width block before gutter detection.

    IF THIS LAYOUT DOES NOT SPLIT, THE CORPUS IS SILENTLY SCRAMBLED.
    """
    blocks = _two_col_blocks()
    blocks.append(_b(62, 700, 577, 730,
                     "Statutory Reports Corporate Overview Financial Statements"))
    return blocks


def _single_col_blocks(n: int = 8) -> list[Block]:
    """Genuine single column: all blocks span x[56,540]."""
    return [_b(56, 100 + i * 50, 540, 140 + i * 50, f"para_{i}")
            for i in range(n)]


def _narrow_gutter_blocks(n_per_col: int = 6) -> list[Block]:
    """14.8 pt gutter on a 595 pt page (2.49 % — Jain's real measurement).

    The projection-profile histogram path (gutter_bands) needs ≥ 3 empty
    bins (~15 pt) to register a band; this gutter is 2 bins wide and falls
    just below.  The centre-gap fallback must still detect and split it
    because the block *centres* are ~250 pt apart, far above the 0.14 ×
    595 = 83 pt threshold.
    """
    blocks: list[Block] = []
    for i in range(n_per_col):
        y = 100 + i * 40
        blocks.append(_b(56, y, 290, y + 30, f"nleft_{i}"))
        blocks.append(_b(304.8, y, 540, y + 30, f"nright_{i}"))
    return blocks


def _shredded_blocks(n_per_col: int = 20) -> list[Block]:
    """Two columns but ~40 tiny per-line blocks (iLovePDF shredding).

    Each block is one line — the extreme case that iLovePDF produces on
    every page.  The gutter is the same 15 pt as a normal two-column
    layout, but each block is only ~12 pt tall.
    """
    blocks: list[Block] = []
    for i in range(n_per_col):
        y = 80 + i * 14
        blocks.append(_b(56, y, 288, y + 12, f"shredL_{i}"))
        blocks.append(_b(303, y, 540, y + 12, f"shredR_{i}"))
    return blocks


def _heading_plus_columns() -> list[Block]:
    """Full-width heading block above two columns."""
    heading = _b(56, 50, 540, 80, "MANAGEMENT DISCUSSION AND ANALYSIS")
    cols = _two_col_blocks(n_per_col=6, y_start=120)
    return [heading] + cols


def _three_col_blocks(n_per_col: int = 6) -> list[Block]:
    """Three columns with ~40 pt gutters."""
    blocks: list[Block] = []
    for i in range(n_per_col):
        y = 100 + i * 40
        blocks.append(_b(56, y, 170, y + 30, f"col1_{i}"))
        blocks.append(_b(210, y, 380, y + 30, f"col2_{i}"))
        blocks.append(_b(420, y, 540, y + 30, f"col3_{i}"))
    return blocks


# ── parametrised layout table (for the word-conservation cross-cut) ──

_LAYOUTS = [
    ("two_col",   _two_col_blocks,       _A4),
    ("jain",      _jain_blocks,           _A4),
    ("single",    _single_col_blocks,     _A4),
    ("narrow",    _narrow_gutter_blocks,  _A4),
    ("shredded",  _shredded_blocks,       _A4),
    ("heading",   _heading_plus_columns,  _A4),
    ("three_col", _three_col_blocks,      _A4),
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Case 1: clean two-column
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestCleanTwoColumn:
    """Left blocks x[56,288], right x[303,540], 595 pt page.
    Must split; left-then-right order."""

    def test_splits_left_then_right(self):
        blocks = _two_col_blocks()
        ordered = xy_cut(blocks, _A4)
        assert _all_left_before_right(ordered, 288, 303)

    def test_columns_are_internally_top_to_bottom(self):
        blocks = _two_col_blocks()
        ordered = xy_cut(blocks, _A4)
        left_out = [b for b in ordered if b.x1 <= 289]
        right_out = [b for b in ordered if b.x0 >= 302]
        assert len(left_out) == 6
        assert len(right_out) == 6
        assert all(left_out[i].y0 <= left_out[i + 1].y0
                   for i in range(len(left_out) - 1))
        assert all(right_out[i].y0 <= right_out[i + 1].y0
                   for i in range(len(right_out) - 1))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Case 2: THE JAIN CASE — the load-bearing regression test
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestJainCase:
    """Two columns plus a full-width footer x[62,577] (86 % of width).

    This is the exact regression P16B fixed.  If _column_cut cannot
    recover the column split in the presence of a full-width block,
    the entire corpus is silently scrambled — left-column and
    right-column lines interleave and the text reads as word soup.

    ┌─────────────────────────────────────┐
    │ ┌──────────┐    ┌──────────────────┐│
    │ │ left col │    │   right col      ││
    │ │  56‥288  │    │   303‥540        ││
    │ └──────────┘    └──────────────────┘│
    │ ┌──────────────────────────────────┐│
    │ │     full-width footer 62‥577     ││
    │ └──────────────────────────────────┘│
    └─────────────────────────────────────┘

    IF THIS TEST FAILS, THE CORPUS IS BROKEN.
    """

    def test_must_still_split(self):
        blocks = _jain_blocks()
        ordered = xy_cut(blocks, _A4)
        left = [b for b in ordered if b.x1 <= 289]
        right = [b for b in ordered if b.x0 >= 302 and b.x1 <= 541]
        assert len(left) == 6, "left column blocks must be grouped"
        assert len(right) == 6, "right column blocks must be grouped"
        assert _all_left_before_right(ordered, 288, 303)

    def test_column_cut_fires_directly(self):
        """_column_cut must return an ordered list (not None) when a
        full-width block is present."""
        blocks = _jain_blocks()
        result = _column_cut(blocks, _A4, depth=0)
        assert result is not None, "_column_cut must find the column split"

    def test_footer_survives_in_output(self):
        blocks = _jain_blocks()
        ordered = xy_cut(blocks, _A4)
        footer = [b for b in ordered if "Statutory" in b.text]
        assert len(footer) == 1, "full-width footer must not be dropped"

    def test_footer_appears_after_columns(self):
        """The full-width footer at y=700 is below both columns (y ≤ 330),
        so it must appear last in the reading order."""
        blocks = _jain_blocks()
        ordered = xy_cut(blocks, _A4)
        footer_idx = next(i for i, b in enumerate(ordered)
                          if "Statutory" in b.text)
        assert footer_idx == len(ordered) - 1


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Case 3: genuine single column
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestGenuineSingleColumn:
    """One column of blocks x[56,540] — must NOT split."""

    def test_column_cut_returns_none(self):
        blocks = _single_col_blocks()
        result = _column_cut(blocks, _A4, depth=0)
        assert result is None, "single-column layout must not split"

    def test_xy_cut_preserves_top_to_bottom(self):
        blocks = _single_col_blocks()
        ordered = xy_cut(blocks, _A4)
        assert all(ordered[i].y0 <= ordered[i + 1].y0
                   for i in range(len(ordered) - 1))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Case 4: narrow gutter
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestNarrowGutter:
    """14.8 pt gutter on a 595 pt page (2.49 %, Jain's real measurement).

    The histogram path (gutter_bands) needs ≥ 3 bins (~15 pt) to detect a
    band; 14.8 pt spans only 2 bins and just misses.  The split must still
    fire via the centre-gap fallback because block centres are ~250 pt
    apart — well above the COLUMN_CENTRE_GAP_FRAC × 595 = 83 pt threshold.
    """

    def test_splits_via_centre_gap(self):
        blocks = _narrow_gutter_blocks()
        ordered = xy_cut(blocks, _A4)
        assert _all_left_before_right(ordered, 290, 304.8)

    def test_column_cut_fires(self):
        """_column_cut must detect the split even with a tight gutter."""
        blocks = _narrow_gutter_blocks()
        result = _column_cut(blocks, _A4, depth=0)
        assert result is not None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Case 5: shredded blocks
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestShreddedBlocks:
    """~40 tiny per-line blocks instead of 6 paragraph blocks.

    This is what iLovePDF produces — one text block per visual line.
    Must still split."""

    def test_still_splits(self):
        blocks = _shredded_blocks()
        ordered = xy_cut(blocks, _A4)
        left = [b for b in ordered if b.x1 <= 289]
        right = [b for b in ordered if b.x0 >= 302]
        assert len(left) == 20
        assert len(right) == 20
        assert _all_left_before_right(ordered, 288, 303)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Case 6: full-width heading above two columns
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestFullWidthHeading:
    """A title block spanning the page above two columns.
    Heading first, then left column, then right column."""

    def test_heading_before_left_before_right(self):
        blocks = _heading_plus_columns()
        ordered = xy_cut(blocks, _A4)

        heading = [b for b in ordered if "MANAGEMENT" in b.text]
        left = [b for b in ordered if b.text.startswith("left_")]
        right = [b for b in ordered if b.text.startswith("right_")]

        assert len(heading) == 1, "heading must be present"
        assert len(left) == 6
        assert len(right) == 6

        h_idx = ordered.index(heading[0])
        first_left = min(ordered.index(b) for b in left)
        last_left = max(ordered.index(b) for b in left)
        first_right = min(ordered.index(b) for b in right)

        assert h_idx < first_left, "heading must come before left column"
        assert h_idx < first_right, "heading must come before right column"
        assert last_left < first_right, "left column must precede right column"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Case 7: three columns
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestThreeColumns:
    """Three column layout: must either split correctly or decline to
    split, but must NOT interleave (no col-A → col-B → col-A pattern
    within a single y-band)."""

    @staticmethod
    def _col_id(b: Block) -> int:
        cx = (b.x0 + b.x1) / 2
        if cx < 150:
            return 1
        elif cx < 400:
            return 2
        else:
            return 3

    def test_no_interleave(self):
        blocks = _three_col_blocks()
        ordered = xy_cut(blocks, _A4)
        cols = [self._col_id(b) for b in ordered]

        # Once we leave column C for column D, we must never return to C.
        seen_transitions: set[tuple[int, int]] = set()
        for i in range(len(cols) - 1):
            if cols[i] != cols[i + 1]:
                reverse = (cols[i + 1], cols[i])
                assert reverse not in seen_transitions, (
                    f"interleave: went col {cols[i]}→{cols[i+1]} "
                    f"but {reverse} already seen in {cols}")
                seen_transitions.add((cols[i], cols[i + 1]))

    def test_all_blocks_assigned(self):
        blocks = _three_col_blocks()
        ordered = xy_cut(blocks, _A4)
        assert len(ordered) == len(blocks)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Case 8: word conservation — the one that matters most
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestWordConservation:
    """For every layout: the multiset of words in equals the multiset out.
    xy_cut must never add or drop a token."""

    @pytest.mark.parametrize("name,builder,page", _LAYOUTS,
                             ids=[t[0] for t in _LAYOUTS])
    def test_words_in_equals_words_out(self, name, builder, page):
        blocks_in = builder()
        blocks_out = xy_cut(list(blocks_in), page)
        assert _words(blocks_in) == _words(blocks_out), (
            f"word mismatch on layout '{name}': "
            f"in has {len(blocks_in)} blocks / {sum(_words(blocks_in).values())} words, "
            f"out has {len(blocks_out)} blocks / {sum(_words(blocks_out).values())} words")

    @pytest.mark.parametrize("name,builder,page", _LAYOUTS,
                             ids=[t[0] for t in _LAYOUTS])
    def test_block_count_preserved(self, name, builder, page):
        blocks_in = builder()
        blocks_out = xy_cut(list(blocks_in), page)
        assert len(blocks_out) == len(blocks_in), (
            f"block count mismatch on '{name}': {len(blocks_in)} → {len(blocks_out)}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Boundary: COLUMN_FULLWIDTH_FRAC (0.60)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestFullwidthFracBoundary:
    """A block at 0.59 vs 0.61 of body width.

    If COLUMN_FULLWIDTH_FRAC is changed, this test tells the developer
    exactly what behaviour they altered: whether a spanning block is
    treated as column evidence (voting) or full-width (skipped).

    text_w in both cases = 540 − 56 = 484 pt (the right column already
    extends to x=540, so the test block cannot widen the text band).
    """

    def _layout_with_test_block(self, frac: float) -> list[Block]:
        cols = _two_col_blocks(n_per_col=6)
        text_w = 540 - 56                           # 484
        block_w = frac * text_w
        # test block on the left side, above the columns
        return cols + [_b(56, 60, 56 + block_w, 90, "boundary_block")]

    def test_059_is_below_threshold(self):
        """0.59 × text_w < COLUMN_FULLWIDTH_FRAC × text_w → block votes
        as column evidence (not skipped)."""
        blocks = self._layout_with_test_block(0.59)
        text_w = max(b.x1 for b in blocks) - min(b.x0 for b in blocks)
        test_b = next(b for b in blocks if b.text == "boundary_block")
        assert test_b.w < COLUMN_FULLWIDTH_FRAC * text_w, (
            f"block width {test_b.w:.1f} should be < threshold "
            f"{COLUMN_FULLWIDTH_FRAC * text_w:.1f}")
        # xy_cut still produces a valid ordering
        ordered = xy_cut(blocks, _A4)
        assert _words(blocks) == _words(ordered)

    def test_061_is_above_threshold(self):
        """0.61 × text_w > COLUMN_FULLWIDTH_FRAC × text_w → block is
        full-width, excluded from column voting."""
        blocks = self._layout_with_test_block(0.61)
        text_w = max(b.x1 for b in blocks) - min(b.x0 for b in blocks)
        test_b = next(b for b in blocks if b.text == "boundary_block")
        assert test_b.w > COLUMN_FULLWIDTH_FRAC * text_w, (
            f"block width {test_b.w:.1f} should be > threshold "
            f"{COLUMN_FULLWIDTH_FRAC * text_w:.1f}")
        ordered = xy_cut(blocks, _A4)
        assert _words(blocks) == _words(ordered)

    def test_both_sides_still_split(self):
        """Whether the borderline block is voting or wide, the two-column
        layout must still split (the 6+6 column blocks are sufficient
        evidence either way)."""
        for frac in (0.59, 0.61):
            blocks = self._layout_with_test_block(frac)
            ordered = xy_cut(blocks, _A4)
            assert _all_left_before_right(ordered, 288, 303), (
                f"split failed at frac={frac}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Boundary: COLUMN_CENTRE_GAP_FRAC (0.14)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestCentreGapFracBoundary:
    """A centre gap at 0.13 vs 0.15 of page width.

    Uses exactly 4 + 4 = 8 blocks (< 10 spans) so gutter_bands returns []
    and the ONLY path _column_cut can use is the centre-gap comparison.
    This isolates the constant under test.

    If COLUMN_CENTRE_GAP_FRAC is changed, this test tells the developer
    exactly what behaviour they altered: whether a given centre-to-centre
    gap is wide enough to call two clusters separate columns.
    """

    def _layout_with_gap(self, frac: float) -> list[Block]:
        """Two clusters of 4 narrow blocks (width 40 pt) whose centres
        are separated by ``frac × 595`` pt."""
        gap = frac * 595
        left_cx, right_cx = 200, 200 + gap
        blocks: list[Block] = []
        for i in range(4):
            y = 100 + i * 50
            blocks.append(_b(left_cx - 20, y, left_cx + 20, y + 30,
                             f"gap_L{i}"))
            blocks.append(_b(right_cx - 20, y, right_cx + 20, y + 30,
                             f"gap_R{i}"))
        return blocks

    def test_013_below_threshold_no_split(self):
        """0.13 × page_width = 77.4 pt gap < 0.14 × 595 = 83.3 pt
        threshold → centre-gap path does NOT fire."""
        blocks = self._layout_with_gap(0.13)
        result = _column_cut(blocks, _A4, depth=0)
        assert result is None, (
            f"gap at 0.13 × page_width should be below "
            f"COLUMN_CENTRE_GAP_FRAC={COLUMN_CENTRE_GAP_FRAC}")

    def test_015_above_threshold_splits(self):
        """0.15 × page_width = 89.3 pt gap ≥ 83.3 pt threshold
        → centre-gap path fires and returns an ordered list."""
        blocks = self._layout_with_gap(0.15)
        result = _column_cut(blocks, _A4, depth=0)
        assert result is not None, (
            f"gap at 0.15 × page_width should be above "
            f"COLUMN_CENTRE_GAP_FRAC={COLUMN_CENTRE_GAP_FRAC}")
        # Word conservation on the split result
        assert _words(blocks) == _words(result)

