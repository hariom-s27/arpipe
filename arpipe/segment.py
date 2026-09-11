"""Locate the MD&A section inside an annual report.

Five strategies, tried in order of reliability and cost. Each returns a
candidate span with a score; the arbiter picks the best and records which
strategy won so precision can be measured per-strategy later.

  S1 outline   PDF bookmarks. Present in ~35-55% of post-2016 filings,
               almost never before 2013. Cheapest and most precise.
  S2 toc       The printed "Contents" page. Requires mapping printed folio
               numbers to physical page indices - the offset is rarely zero
               because of covers and inserts, so we solve for it.
  S3 heading   Typographic heading detection: the MD&A title rendered at a
               font size well above the page's body size, near the top of a
               page, on a line of its own.
  S4 body      Schedule V Part B sub-heading cues scored per page, then the
               best contiguous run. This is the workhorse for scanned
               reports where the heading itself was mangled by OCR.
  S5 llm       An LLM adjudicates a small window of candidate pages. Used
               only when S1-S4 disagree or all score low. Costs ~2-6k tokens
               per document, so it must stay a minority path.

End of section = first *terminator* heading (Corporate Governance report,
auditor's report, financial statements, AGM notice...) at or after the start.
"""
from __future__ import annotations

import re
import statistics
from collections import defaultdict
from dataclasses import dataclass, replace
from typing import Any

import pymupdf

from .models import DocProfile, MDASpan
from .patterns import (ANNEXURE_HEADING_RE, MDA_ACRONYM_RE, MDA_BODY_CUE_RES,
                       MDA_COMBINED_RE, MDA_HEADING_RE, MDA_POINTER_RE,
                       MDA_TERMINATOR_RE)

# --- tunable thresholds ---------------------------------------------------
# All thresholds provisional until re-fit against the labelled 300.
# provisional until re-fit against the labelled 300
MAX_MDA_PAGES = 60          # sanity cap; real MD&A runs 3-25 pages
# provisional until re-fit against the labelled 300
MIN_MDA_WORDS = 250
# provisional until re-fit against the labelled 300
HEADING_MIN_REL_SIZE = 1.12
# provisional until re-fit against the labelled 300
HEADING_BASE_SCORE = 0.45
# provisional until re-fit against the labelled 300
OUTLINE_BASE_SCORE = 0.95
# provisional until re-fit against the labelled 300
TOC_OFFSET_CONFIDENCE_THRESHOLD = 0.50
# provisional until re-fit against the labelled 300
TOC_HIGH_SCORE = 0.80
# provisional until re-fit against the labelled 300
BODY_SCORE_PAGE_PENALTY = 0.12
# provisional until re-fit against the labelled 300
BODY_SCORE_MIN_PEAK = 0.35
# provisional until re-fit against the labelled 300
BODY_SCORE_MAX = 0.72
# provisional until re-fit against the labelled 300
TEXT_HEADING_MAX_SCORE = 0.78
# provisional until re-fit against the labelled 300
SUPPORTER_WEIGHT = 0.06
# provisional until re-fit against the labelled 300
LLM_ENABLED = False
# provisional until re-fit against the labelled 300
LLM_MODEL = "claude-sonnet"
# provisional until re-fit against the labelled 300
LLM_MAX_PAGES_IN_WINDOW = 24


def configure(cfg: dict | None = None) -> None:
    """Update thresholds from resolved configuration."""
    global MAX_MDA_PAGES, MIN_MDA_WORDS, HEADING_MIN_REL_SIZE, HEADING_BASE_SCORE
    global OUTLINE_BASE_SCORE, TOC_OFFSET_CONFIDENCE_THRESHOLD, TOC_HIGH_SCORE
    global BODY_SCORE_PAGE_PENALTY, BODY_SCORE_MIN_PEAK, BODY_SCORE_MAX
    global TEXT_HEADING_MAX_SCORE, SUPPORTER_WEIGHT, LLM_ENABLED, LLM_MODEL, LLM_MAX_PAGES_IN_WINDOW
    if not cfg:
        return
    MAX_MDA_PAGES = cfg.get("max_mda_pages", MAX_MDA_PAGES)
    MIN_MDA_WORDS = cfg.get("min_mda_words", MIN_MDA_WORDS)
    HEADING_MIN_REL_SIZE = cfg.get("heading_min_rel_size", HEADING_MIN_REL_SIZE)
    HEADING_BASE_SCORE = cfg.get("heading_base_score", HEADING_BASE_SCORE)
    OUTLINE_BASE_SCORE = cfg.get("outline_base_score", OUTLINE_BASE_SCORE)
    TOC_OFFSET_CONFIDENCE_THRESHOLD = cfg.get("toc_offset_confidence_threshold", TOC_OFFSET_CONFIDENCE_THRESHOLD)
    TOC_HIGH_SCORE = cfg.get("toc_high_score", TOC_HIGH_SCORE)
    BODY_SCORE_PAGE_PENALTY = cfg.get("body_score_page_penalty", BODY_SCORE_PAGE_PENALTY)
    BODY_SCORE_MIN_PEAK = cfg.get("body_score_min_peak", BODY_SCORE_MIN_PEAK)
    BODY_SCORE_MAX = cfg.get("body_score_max", BODY_SCORE_MAX)
    TEXT_HEADING_MAX_SCORE = cfg.get("text_heading_max_score", TEXT_HEADING_MAX_SCORE)
    SUPPORTER_WEIGHT = cfg.get("supporter_weight", SUPPORTER_WEIGHT)
    llm_cfg = cfg.get("llm", {})
    if isinstance(llm_cfg, dict):
        LLM_ENABLED = llm_cfg.get("enabled", LLM_ENABLED)
        LLM_MODEL = llm_cfg.get("model", LLM_MODEL)
        LLM_MAX_PAGES_IN_WINDOW = llm_cfg.get("max_pages_in_window", LLM_MAX_PAGES_IN_WINDOW)


# ---------------------------------------------------------------- heading find
@dataclass(slots=True)
class HeadingHit:
    page_no: int
    text: str
    size: float
    rel_size: float          # size / page body size
    y_frac: float            # vertical position, 0 = top
    is_standalone: bool
    bold: bool


def page_headings(page: pymupdf.Page, min_rel: float | None = None) -> list[HeadingHit]:
    """Return lines that look typographically like headings."""
    rel_cut = min_rel if min_rel is not None else HEADING_MIN_REL_SIZE
    d = page.get_text("dict")
    sizes: list[float] = []
    lines: list[tuple[str, float, float, bool]] = []   # text, size, y, bold
    for blk in d.get("blocks", []):
        if blk.get("type") != 0:
            continue
        for line in blk.get("lines", []):
            txt = "".join(s.get("text", "") for s in line.get("spans", [])).strip()
            if not txt:
                continue
            szs = [s.get("size", 0.0) for s in line.get("spans", []) if s.get("text", "").strip()]
            if not szs:
                continue
            size = max(szs)
            bold = any("bold" in (s.get("font", "").lower()) or (s.get("flags", 0) & 2 ** 4)
                       for s in line.get("spans", []))
            sizes.extend(szs)
            lines.append((txt, size, line["bbox"][1], bold))
    if not lines:
        return []
    body = statistics.median(sizes) or 1.0
    h = page.rect.height or 1.0
    out: list[HeadingHit] = []
    for txt, size, y, bold in lines:
        rel = size / body
        if rel >= rel_cut or (bold and len(txt) <= 90) or txt.isupper():
            out.append(HeadingHit(page.number, txt, size, rel, y / h,
                                  is_standalone=len(txt) <= 110, bold=bold))
    return out


def _is_mda_title(t: str) -> bool:
    if MDA_HEADING_RE.search(t) or MDA_COMBINED_RE.search(t):
        return True
    s = t.strip()
    return bool(len(s) <= 24 and MDA_ACRONYM_RE.search(s))


_TITLE_STOPWORDS = {
    "and", "or", "the", "of", "in", "on", "at", "to", "for", "with",
    "a", "an", "by", "as", "&", "from", "into", "through", "over",
    "st", "nd", "rd", "th",
}


def _is_title_or_caps(s: str) -> bool:
    """True if s is ALL CAPS or Title Case (allowing lowercase stopwords)."""
    s = s.strip()
    if not s:
        return False
    if s.isupper():
        return True
    words = re.findall(r"[A-Za-z]+", s)
    if not words:
        return False
    if not any(w[0].isupper() for w in words):
        return False
    for i, w in enumerate(words):
        if i == 0 or w.lower() not in _TITLE_STOPWORDS:
            if not w[0].isupper():
                return False
    return True


def is_cross_reference_pointer(page_text: str, heading_text: str) -> bool:
    """True if a heading mention is merely a cross-reference pointer in the Directors' Report.

    Indian annual reports commonly contain cross-reference statements like:
      'The Management Discussion & Analysis Report covering the performance
       and outlook of the Company is enclosed.'
      'The Management Discussion and Analysis Report forms part of the Annual Report.'
      'Management Discussion and Analysis is given in Annexure A.'
    followed immediately by the next statutory heading (e.g. AUDITORS' REPORT).
    Such pointers are not the actual start of the MD&A section.
    """
    if not page_text or not heading_text:
        return False

    if MDA_POINTER_RE.search(heading_text):
        return True

    lower_page = page_text.lower()
    lower_hdg = heading_text.lower()
    idx = lower_page.find(lower_hdg)
    if idx < 0:
        clean_hdg = " ".join(lower_hdg.split())
        clean_page = " ".join(lower_page.split())
        idx = clean_page.find(clean_hdg)
        if idx >= 0:
            after = clean_page[idx + len(clean_hdg):]
        else:
            return False
    else:
        after = page_text[idx + len(heading_text):]

    words = after.split()
    snippet = " ".join(words[:80])
    full_snippet = " ".join(page_text[idx:].split()[:80])
    if MDA_POINTER_RE.search(snippet) or MDA_POINTER_RE.search(full_snippet):
        if MDA_TERMINATOR_RE.search(snippet) or MDA_TERMINATOR_RE.search(full_snippet):
            return True
        if len(words) < 60:
            return True

    return False


def check_terminator_line(
    line: str,
    page_no: int,
    line_idx: int,
    raw_lines: list[str],
    heading_hit: HeadingHit | None = None,
) -> dict[str, Any] | None:
    """Validate that a candidate line satisfies all heading shape criteria.

    Criteria (all must be satisfied):
      1. Short: len(line) <= 80 characters.
      2. Whole line: the match represents the entire heading line, not an
         embedded substring inside a longer sentence.
      3. Position: sits in the top third of the page, OR has blank space above it.
      4. Typography: Title Case or ALL CAPS, OR bold / larger font
         (on OCR'd pages, falls back to the Title Case / ALL CAPS shape test).
    """
    line_str = line.strip()
    if not line_str:
        return None

    # Criterion 1: Short line (<= 80 characters)
    if len(line_str) > 80:
        return None

    # Must match terminator regex or annexure regex
    m = MDA_TERMINATOR_RE.search(line_str)
    if not m and not ANNEXURE_HEADING_RE.search(line_str):
        return None

    # Criterion 2: Whole line (not a substring inside a longer sentence)
    if line_str.endswith(",") or line_str.endswith(";"):
        return None
    if line_str.endswith(".") and not re.search(r"\b(?:Co|Ltd|Inc|Corp|No)\.$", line_str, re.I):
        return None

    if m:
        prefix = line_str[:m.start()].strip()
        suffix = line_str[m.end():].strip()
        if prefix:
            prefix_words = re.findall(r"[A-Za-z]+", prefix)
            if any(not w[0].isupper() for w in prefix_words if w.lower() not in _TITLE_STOPWORDS):
                return None
            if len(prefix_words) > 3:
                return None
        if suffix:
            suffix_words = re.findall(r"[A-Za-z]+", suffix)
            if any(not w[0].isupper() for w in suffix_words if w.lower() not in _TITLE_STOPWORDS):
                return None
            if len(suffix_words) > 3:
                return None

    # Criterion 3: Top third of page OR blank space above it
    if heading_hit is not None:
        in_top_third = heading_hit.y_frac < 0.35
        has_blank_above = (line_idx == 0 or (line_idx > 0 and line_idx - 1 < len(raw_lines) and raw_lines[line_idx - 1].strip() == ""))
    else:
        total_lines = len(raw_lines) if raw_lines else 1
        in_top_third = line_idx < max(4, total_lines // 3)
        has_blank_above = (line_idx > 0 and raw_lines[line_idx - 1].strip() == "")

    if not (in_top_third or has_blank_above):
        return None

    # Criterion 4: Title Case or ALL CAPS, OR bold / larger font
    font_signal = "none"
    if heading_hit is not None:
        if heading_hit.bold:
            font_signal = "bold"
        elif heading_hit.rel_size >= 1.12:
            font_signal = "larger"

    title_or_caps = _is_title_or_caps(line_str)
    if not (title_or_caps or font_signal in ("bold", "larger")):
        return None

    if font_signal == "none":
        font_signal = "all_caps" if line_str.isupper() else "title_case"

    y_frac = heading_hit.y_frac if heading_hit is not None else (line_idx / max(1, len(raw_lines)))
    return {
        "text": line_str,
        "page": page_no,
        "line_index": line_idx,
        "y_frac": round(y_frac, 3),
        "shape_ok": True,
        "font_signal": font_signal,
    }


def find_terminator_match_on_page(
    page_no: int,
    text: str,
    headings: list[HeadingHit] | None = None,
) -> dict[str, Any] | None:
    """Find the first line on page satisfying all terminator shape requirements."""
    if not text:
        return None

    raw_lines = text.split("\n")

    # 1. Check typographic headings if available
    if headings:
        for h in headings:
            if h.page_no != page_no:
                continue
            l_idx = 0
            for i, l in enumerate(raw_lines):
                if h.text in l:
                    l_idx = i
                    break
            match = check_terminator_line(h.text, page_no, l_idx, raw_lines, heading_hit=h)
            if match:
                return match

    # 2. Text-based scan over page lines (first half of page unless blank space above)
    for i, line in enumerate(raw_lines):
        if i > max(8, len(raw_lines) // 2) and (i == 0 or raw_lines[i - 1].strip() != ""):
            continue
        line_s = line.strip()
        if not line_s:
            continue
        match = check_terminator_line(line_s, page_no, i, raw_lines, heading_hit=None)
        if match:
            return match

    return None


# ------------------------------------------------------------------- S1 outline
def _is_outline_prose(p: int, page_texts: dict[int, str]) -> bool:
    """Validate that page p contains genuine MD&A prose."""
    txt = page_texts.get(p, "")
    if not txt:
        return False
    words = len(txt.split())
    if words < 120:
        return False
    alpha = sum(1 for ch in txt if ch.isalpha())
    alpha_ratio = alpha / max(1, len(txt))
    if not (0.60 <= alpha_ratio <= 0.92):
        return False
    nxt_txt = page_texts.get(p + 1, "")
    has_cue = any(r.search(txt) for r in MDA_BODY_CUE_RES) or (
        bool(nxt_txt) and any(r.search(nxt_txt) for r in MDA_BODY_CUE_RES)
    )
    return has_cue


def from_outline(
    profile: DocProfile,
    page_texts: dict[int, str] | None = None,
    return_info: bool = False,
) -> MDASpan | tuple[MDASpan | None, dict] | None:
    if not profile.outline_titles:
        return (None, {}) if return_info else None
    entries = sorted(profile.outline_titles, key=lambda e: e[2])
    start_i = None
    for i, (_lvl, title, pno) in enumerate(entries):
        if _is_mda_title(title):
            start_i = i
            break
    if start_i is None:
        return (None, {}) if return_info else None
    s_lvl, s_title, s_page = entries[start_i]
    end_page = profile.n_pages - 1
    term = None
    term_match = None
    for _lvl, title, pno in entries[start_i + 1:]:
        if pno > s_page:
            end_page = pno - 1
            term = title
            term_match = {
                "text": title,
                "page": pno,
                "line_index": 0,
                "shape_ok": True,
                "font_signal": "outline",
            }
            break
    if end_page - s_page + 1 > MAX_MDA_PAGES:
        end_page = s_page + MAX_MDA_PAGES - 1

    score = OUTLINE_BASE_SCORE
    val_info: dict[str, Any] = {
        "proposed_start": s_page,
        "accepted_start": s_page,
        "walked": 0,
        "outcome": "accepted",
        "reason": "valid_prose_at_target",
    }

    if page_texts is not None:
        if _is_outline_prose(s_page, page_texts):
            val_info["accepted_start"] = s_page
            val_info["walked"] = 0
            val_info["outcome"] = "accepted"
            val_info["reason"] = "valid_prose_at_target"
        else:
            accepted_p = None
            walked_count = 0
            for step in range(1, 9):
                cand_p = s_page + step
                if cand_p > end_page or cand_p >= profile.n_pages:
                    break
                walked_count = step
                if _is_outline_prose(cand_p, page_texts):
                    accepted_p = cand_p
                    break
            if accepted_p is not None:
                val_info["accepted_start"] = accepted_p
                val_info["walked"] = walked_count
                val_info["outcome"] = "accepted_with_walk"
                val_info["reason"] = "prose_found_at_walk"
                s_page = accepted_p
                score = OUTLINE_BASE_SCORE - 0.05
            else:
                val_info["accepted_start"] = None
                val_info["walked"] = 8
                val_info["outcome"] = "invalidated"
                val_info["reason"] = "no_prose_within_cap"
                if return_info:
                    return None, val_info
                return None

    span = MDASpan(
        start_page=s_page,
        end_page=max(s_page, end_page),
        method="outline",
        heading_text=s_title,
        terminator_text=term,
        terminator_match=term_match,
        score=score,
    )
    if return_info:
        return span, val_info
    return span


# ----------------------------------------------------------------------- S2 toc
# Tolerant of OCR damage to dot leaders: real scans turn "......... 6" into
# ".........:::::0+ 4" or "..............:006". The separator class is
# therefore "any run of non-alphanumerics", and leading zeros are allowed.
TOC_LINE_RE = re.compile(
    r"^(?P<title>[A-Za-z][^\d]{2,88}?)[^A-Za-z0-9]{2,}(?P<page>\d{1,4})\s*$")
# Same line without a usable folio: still tells us the section ORDER, which is
# enough to name the section that terminates MD&A.
TOC_TITLE_ONLY_RE = re.compile(r"^(?P<title>[A-Za-z][^\d]{4,88}?)[^A-Za-z0-9]{3,}\s*$")


def find_toc_pages(page_texts: dict[int, str], search_first: int = 20) -> list[int]:
    hits = []
    for n in sorted(page_texts)[:search_first]:
        t = page_texts[n]
        dotted = 0
        for ln in t.split("\n"):
            m = TOC_LINE_RE.match(ln.strip())
            if m:
                title = m.group("title").strip()
                if len(title) <= 80 and _is_title_or_caps(title):
                    dotted += 1
        if dotted >= 4 or (re.search(r"\bcontents\b", t, re.I) and dotted >= 2):
            hits.append(n)
    return hits



def _solve_label_offset(doc: pymupdf.Document, page_texts: dict[int, str],
                        toc_pages: list[int] | None = None,
                        sample: int = 40) -> tuple[int | None, dict[str, Any]]:
    """Find k such that physical_page = printed_folio + k.

    Reads the folio printed in the top/bottom margin of sampled pages and
    takes the modal difference. Robust to the many pages that print no folio.
    Returns (offset, toc_offset_diag).
    """
    if not toc_pages:
        return None, {
            "solved": None,
            "confidence": 0.0,
            "samples_used": 0,
            "modal_agreement": 0.0,
            "method": "not_run",
        }

    diffs: defaultdict[int, int] = defaultdict(int)
    page_diffs: dict[int, list[int]] = {}
    nos = sorted(page_texts)
    step = max(1, len(nos) // sample)
    for n in nos[::step]:
        lines = [l.strip() for l in page_texts[n].split("\n") if l.strip()]
        matched = []
        for cand in lines[:2] + lines[-3:]:
            m = re.fullmatch(r"\|?\s*(\d{1,4})\s*\|?", cand)
            if m:
                folio = int(m.group(1))
                if 0 < folio <= doc.page_count + 40:
                    matched.append(n - folio)
        if matched:
            page_diffs[n] = matched
            for d in set(matched):
                diffs[d] += 1

    samples_used = len(page_diffs)
    fallback_offset = toc_pages[0]

    if not diffs or samples_used < 3:
        info = {
            "solved": fallback_offset,
            "confidence": 0.0,
            "samples_used": samples_used,
            "modal_agreement": 0.0,
            "method": "toc_page_fallback",
        }
        return fallback_offset, info

    k, c = max(diffs.items(), key=lambda kv: kv[1])
    modal_agreement = round(c / samples_used, 3)

    if c < 3:
        info = {
            "solved": fallback_offset,
            "confidence": modal_agreement,
            "samples_used": samples_used,
            "modal_agreement": modal_agreement,
            "method": "toc_page_fallback",
        }
        return fallback_offset, info

    # Check local agreement in the front of the book (where TOC lives and points)
    toc_first = toc_pages[0]
    front_bound = min(doc.page_count, max(50, toc_first + 40))
    front_pages = [n for n in page_diffs if n <= front_bound]
    if front_pages:
        front_c = sum(1 for n in front_pages if k in page_diffs[n])
        front_agreement = front_c / len(front_pages)
    else:
        front_agreement = modal_agreement

    # In book pagination, physical page >= printed folio, so k >= -2.
    # Large negative offset indicates severe pagination drift or skipped sections.
    plausibility = 1.0 if k >= -2 else 0.5

    confidence = modal_agreement * (0.3 + 0.7 * front_agreement) * plausibility
    confidence = round(min(1.0, max(0.0, confidence)), 3)

    info = {
        "solved": k,
        "confidence": confidence,
        "samples_used": samples_used,
        "modal_agreement": modal_agreement,
        "method": "margin_folio_mode",
    }
    return k, info


def from_toc(doc: pymupdf.Document, page_texts: dict[int, str],
             return_info: bool = False) -> MDASpan | tuple[MDASpan | None, dict[str, Any]] | None:
    toc_pages = find_toc_pages(page_texts)
    if not toc_pages:
        info = {
            "solved": None,
            "confidence": 0.0,
            "samples_used": 0,
            "modal_agreement": 0.0,
            "method": "not_run",
        }
        return (None, info) if return_info else None

    entries: list[tuple[str, int]] = []
    for n in toc_pages:
        for ln in page_texts[n].split("\n"):
            m = TOC_LINE_RE.match(ln.strip())
            if m:
                title = m.group("title").strip()
                if len(title) <= 80 and _is_title_or_caps(title):
                    entries.append((title, int(m.group("page"))))

    offset, offset_info = _solve_label_offset(doc, page_texts, toc_pages=toc_pages)
    if offset is None:
        offset = toc_pages[0]

    if not entries:
        return (None, offset_info) if return_info else None

    confidence = offset_info.get("confidence", 0.0)
    if confidence >= TOC_OFFSET_CONFIDENCE_THRESHOLD:
        score = TOC_HIGH_SCORE
    else:
        # P6: Cut score hard if offset confidence is below threshold so TOC cannot win
        # outright over actual heading/body signals, but can still act as a supporter.
        score = round(max(0.15, min(0.40, TOC_HIGH_SCORE * confidence)), 3)

    entries.sort(key=lambda e: e[1])
    res_span = None
    for i, (title, folio) in enumerate(entries):
        if _is_mda_title(title):
            start = folio + offset
            end = doc.page_count - 1
            term = None
            term_match = None
            for t2, f2 in entries[i + 1:]:
                if f2 > folio:
                    if len(t2) <= 80 and _is_title_or_caps(t2):
                        end = f2 + offset - 1
                        term = t2
                        term_match = {
                            "text": t2,
                            "page": max(0, min(f2 + offset, doc.page_count - 1)),
                            "line_index": 0,
                            "shape_ok": True,
                            "font_signal": "title_case" if not t2.isupper() else "all_caps",
                        }
                        break
            start = max(0, min(start, doc.page_count - 1))
            end = max(start, min(end, doc.page_count - 1))
            if end - start + 1 > MAX_MDA_PAGES:
                end = start + MAX_MDA_PAGES - 1
            res_span = MDASpan(start, end, method="toc", heading_text=title,
                               terminator_text=term, terminator_match=term_match,
                               score=score, toc_offset=offset_info)
            break

    if return_info:
        return res_span, offset_info
    return res_span


# ------------------------------------------------------------------- S3 heading
def from_headings(doc: pymupdf.Document, page_texts: dict[int, str],
                  skip_first: int = 1) -> MDASpan | None:
    best: tuple[float, HeadingHit] | None = None
    for n in sorted(page_texts):
        if n < skip_first:
            continue
        try:
            hits = page_headings(doc.load_page(n))
        except Exception:
            continue
        cand_hits: list[HeadingHit] = []
        for i, h in enumerate(hits):
            if _is_mda_title(h.text):
                cand_hits.append(h)
            elif i + 1 < len(hits) and not _is_mda_title(hits[i + 1].text):
                h2 = hits[i + 1]
                if (h.bold or h.rel_size >= 1.2) and 0.0 <= (h2.y_frac - h.y_frac) <= 0.10:
                    comb = f"{h.text} {h2.text}"
                    if _is_mda_title(comb):
                        cand_hits.append(HeadingHit(
                            page_no=n, text=comb, size=max(h.size, h2.size),
                            rel_size=max(h.rel_size, h2.rel_size), y_frac=h.y_frac,
                            is_standalone=True, bold=h.bold or h2.bold,
                        ))

        for h in cand_hits:
            if is_cross_reference_pointer(page_texts.get(n, ""), h.text):
                continue
            sc = HEADING_BASE_SCORE
            sc += 0.25 * min(1.0, (h.rel_size - 1.0) / 0.6)
            if h.y_frac < 0.35:
                sc += 0.18
            if h.is_standalone:
                sc += 0.12
            if h.bold:
                sc += 0.05
            # a mention deep in a TOC-like page is not a section start
            if len(page_texts[n].split()) < 60:
                sc += 0.05
            if best is None or sc > best[0]:
                best = (sc, h)
    if not best:
        return None
    sc, h = best
    end, term_match = _find_terminator(doc, page_texts, h.page_no)
    term_text = term_match["text"] if term_match else None
    return MDASpan(h.page_no, end, method="heading", heading_text=h.text,
                   terminator_text=term_text, terminator_match=term_match,
                   score=min(0.92, sc))


# ---------------------------------------------------------------------- S4 body
def page_body_score(text: str) -> float:
    if not text.strip():
        return 0.0
    hits = sum(1 for r in MDA_BODY_CUE_RES if r.search(text))
    sc = min(1.0, hits / 4.0)
    if MDA_HEADING_RE.search(text):
        sc += 0.35
    if re.search(r"cautionary\s+statement", text, re.I):
        sc += 0.15
    return min(1.6, sc)


def _terminator_end_page(start: int, page_no: int, match: dict[str, Any] | None,
                         page_text: str = "") -> int:
    """Determine the MD&A end page when a terminator match is found on page_no.

    If the terminator is at the top of the page (line_index < 5, y_frac < 0.35),
    page_no belongs to the next section and MD&A ended on page_no - 1.
    If the terminator is mid-page or lower and page_no contains MD&A prose
    (body score >= 0.25), page_no contains the conclusion of MD&A and is included.
    """
    if not match:
        return max(start, page_no - 1)
    line_idx = match.get("line_index", 0)
    y_frac = match.get("y_frac", 0.0)
    if (line_idx >= 5 or y_frac >= 0.35) and page_body_score(page_text) >= 0.25:
        return max(start, page_no)
    return max(start, page_no - 1)


def _find_terminator(doc: pymupdf.Document, page_texts: dict[int, str],
                     start: int) -> tuple[int, dict | None]:
    limit = min(start + MAX_MDA_PAGES, max(page_texts) if page_texts else start)
    for n in range(start + 1, limit + 1):
        txt = page_texts.get(n, "")
        if not txt:
            continue
        try:
            hits = page_headings(doc.load_page(n))
        except Exception:
            hits = []
        match = find_terminator_match_on_page(n, txt, hits)
        if match:
            return _terminator_end_page(start, n, match, txt), match
    return min(limit, start + MAX_MDA_PAGES - 1), None


def from_body_scores(page_texts: dict[int, str]) -> MDASpan | None:
    nos = sorted(page_texts)
    if not nos:
        return None
    scores = {n: page_body_score(page_texts[n]) for n in nos}
    if max(scores.values(), default=0.0) < BODY_SCORE_MIN_PEAK:
        return None
    # best contiguous run under a decay: allows one weak page inside a section
    best = (0.0, nos[0], nos[0])
    for i, s in enumerate(nos):
        acc, last_good = 0.0, s
        for j in range(i, min(i + MAX_MDA_PAGES, len(nos))):
            n = nos[j]
            acc += scores[n] - BODY_SCORE_PAGE_PENALTY  # penalty keeps runs from sprawling
            if scores[n] > 0.2:
                last_good = n
            if acc > best[0]:
                best = (acc, s, last_good)
            if acc < -0.9:
                break
    if best[0] <= 0.0:
        return None
    return MDASpan(best[1], best[2], method="body_score",
                   score=min(BODY_SCORE_MAX, 0.3 + best[0] / 6.0))


# ----------------------------------------------------------------------- S5 llm
LLM_PROMPT = """You are given page-by-page excerpts from an Indian listed
company's annual report. Identify the page range of the "Management
Discussion and Analysis" section (SEBI LODR Regulation 34(2)(e), Schedule V
Part B). It may be titled "Management Discussion & Analysis", "Management's
Discussion and Analysis Report", "MD&A", or be folded into the Directors'
Report. It ENDS immediately before the Corporate Governance Report, the
Business Responsibility Report, the Auditor's Report, the financial
statements, or the AGM notice - whichever comes first.

Answer with strict JSON only:
{"start_page": <int>, "end_page": <int>, "heading": "<verbatim heading>", "confidence": <0..1>}
Use the page numbers shown in the excerpt markers. If the section is absent,
return {"start_page": -1, "end_page": -1, "heading": "", "confidence": 0}.

EXCERPTS:
"""


def build_llm_window(page_texts: dict[int, str], candidates: list[MDASpan],
                     radius: int = 4, per_page_chars: int = 1200) -> str:
    want: set[int] = set()
    for c in candidates:
        for n in range(c.start_page - radius, c.end_page + radius + 1):
            want.add(n)
    want &= set(page_texts)
    parts = []
    for n in sorted(want):
        head = page_texts[n][:per_page_chars]
        parts.append(f"--- PAGE {n} ---\n{head}")
    return "\n\n".join(parts)


def from_llm(page_texts: dict[int, str], candidates: list[MDASpan],
             call_llm) -> MDASpan | None:
    """`call_llm(prompt: str) -> str` is injected so this module stays
    dependency-free and unit-testable."""
    import json
    window = build_llm_window(page_texts, candidates)
    if not window:
        return None
    raw = call_llm(LLM_PROMPT + window)
    try:
        m = re.search(r"\{.*\}", raw, re.S)
        obj = json.loads(m.group(0)) if m else json.loads(raw)
    except Exception:
        return None
    s, e = int(obj.get("start_page", -1)), int(obj.get("end_page", -1))
    if s < 0 or e < s:
        return None
    return MDASpan(s, min(e, s + MAX_MDA_PAGES - 1), method="llm",
                   heading_text=obj.get("heading") or None,
                   score=float(obj.get("confidence", 0.6)) * 0.9)


# -------------------------------------------------- S3b heading, text-only
# Scanned pages carry no font metadata, so S3 cannot run on them. This variant
# uses position-in-page and line shape instead: a section title is a short
# line among the first few non-empty lines of a page.
def from_text_headings(page_texts: dict[int, str], skip_first: int = 2,
                       top_lines: int = 5) -> MDASpan | None:
    best: tuple[float, int, str] | None = None
    for n in sorted(page_texts):
        if n < skip_first:
            continue
        lines = [l.strip() for l in page_texts[n].split("\n") if l.strip()]
        if not lines:
            continue
        for i, ln in enumerate(lines[:top_lines]):
            cand_ln = None
            if len(ln) <= 110 and _is_mda_title(ln):
                cand_ln = ln
            elif i + 1 < len(lines[:top_lines]) and not _is_mda_title(lines[i + 1]):
                two = f"{ln} {lines[i + 1]}"
                if len(two) <= 110 and _is_mda_title(two):
                    cand_ln = two
            if not cand_ln:
                continue
            if is_cross_reference_pointer(page_texts[n], cand_ln):
                continue
            sc = 0.40 + 0.10 * (top_lines - i) / top_lines
            if len(cand_ln) <= 60:
                sc += 0.10
            if cand_ln.isupper():
                sc += 0.05
            # a contents page mentions every section; do not start there
            if sum(1 for l in lines if MDA_TERMINATOR_RE.search(l)) >= 3:
                sc -= 0.30
            if best is None or sc > best[0]:
                best = (sc, n, cand_ln)
    if not best:
        return None
    sc, n, ln = best
    end, term_match = _find_terminator_text(page_texts, n)
    term_text = term_match["text"] if term_match else None
    return MDASpan(n, end, method="heading_text", heading_text=ln,
                   terminator_text=term_text, terminator_match=term_match,
                   score=min(TEXT_HEADING_MAX_SCORE, sc))


def _find_terminator_text(page_texts: dict[int, str], start: int,
                          top_lines: int = 5) -> tuple[int, dict | None]:
    nos = [n for n in sorted(page_texts) if n > start]
    for n in nos[:MAX_MDA_PAGES]:
        txt = page_texts.get(n, "")
        if not txt:
            continue
        match = find_terminator_match_on_page(n, txt)
        if match:
            return _terminator_end_page(start, n, match, txt), match
    return max(start, nos[-1] if nos else start), None


def refine_end(span: MDASpan, page_texts: dict[int, str], fetch_text,
               max_extra: int = 12) -> MDASpan:
    """Walk forward past the end of a span found on a sparse page sample.

    `fetch_text(page_no) -> str` OCRs one page on demand. Used after the
    index-sample pass, where pages beyond the sample scored zero simply
    because they had not been read yet.
    """
    if span.terminator_match is not None:
        return span

    n = span.end_page
    term_match = span.terminator_match
    term_text = span.terminator_text
    for _ in range(max_extra):
        nxt = n + 1
        txt = page_texts.get(nxt)
        if txt is None:
            txt = fetch_text(nxt)
            if txt is None:
                break
            page_texts[nxt] = txt
        match = find_terminator_match_on_page(nxt, txt)
        if match:
            term_match = match
            term_text = match["text"]
            break
        if page_body_score(txt) < 0.15 and len(txt.split()) < 60:
            break
        n = nxt
    return replace(span, end_page=n,
                   terminator_text=term_text,
                   terminator_match=term_match,
                   method=span.method + "+refined")


def trim_span(span: MDASpan, page_texts: dict[int, str]) -> MDASpan:
    """Re-derive exact boundaries once every page in the span has been read.

    The locate() pass runs on whatever text was free (digital pages, plus a
    1-in-N OCR sample of scanned ones), so its end boundary is only as precise
    as the sample. After the span itself has been OCR'd at full quality the
    terminator heading is visible and the span can be trimmed to it. Without
    this step a scanned report reliably over-runs into the Corporate
    Governance report and the auditor's report.
    """
    start = span.start_page
    # TOC folio offsets can be approximate, and designed reports often split
    # the title across two lines ("Management" / "Discussion & Analysis").
    # Search a small forward window and join the top lines before matching.
    start_search_end = min(span.end_page, start + 12)
    for n in range(max(0, start - 2), start_search_end + 1):
        t = page_texts.get(n)
        if not t:
            continue
        lines = [l.strip() for l in t.split("\n") if l.strip()][:8]
        heading_window = " ".join(lines)[:500]
        if (any(len(l) <= 110 and _is_mda_title(l) for l in lines)
                or MDA_HEADING_RE.search(heading_window)):
            if not is_cross_reference_pointer(t, heading_window):
                start = n
                break

    end = span.end_page
    term_match = span.terminator_match
    term_text = span.terminator_text
    for n in range(start + 1, span.end_page + 1):
        t = page_texts.get(n)
        if not t:
            continue
        match = find_terminator_match_on_page(n, t)
        if match:
            end = _terminator_end_page(start, n, match, t)
            term_match = match
            term_text = match["text"]
            break
    end = max(start, end)
    return replace(span, start_page=start, end_page=end,
                   terminator_text=term_text,
                   terminator_match=term_match,
                   method=span.method + "+trimmed")


# ---------------------------------------------------------------------- arbiter
def _agree(a: MDASpan, b: MDASpan, tol: int = 2) -> bool:
    return abs(a.start_page - b.start_page) <= tol


def locate(doc: pymupdf.Document, profile: DocProfile,
           page_texts: dict[int, str], call_llm=None) -> tuple[MDASpan | None, dict]:
    outline_res = from_outline(profile, page_texts, True)
    if isinstance(outline_res, tuple):
        outline_span, outline_val_info = outline_res
    else:
        outline_span, outline_val_info = outline_res, {}
    toc_span, toc_offset_info = from_toc(doc, page_texts, return_info=True)
    cands: list[MDASpan] = []
    for fn in (lambda: outline_span,
               lambda: toc_span,
               lambda: from_headings(doc, page_texts),
               lambda: from_text_headings(page_texts),
               lambda: from_body_scores(page_texts)):
        try:
            c = fn()
        except Exception:
            c = None
        if c:
            cands.append(c)

    diag = {"candidates": [(c.method, c.start_page, c.end_page, round(c.score, 3))
                           for c in cands],
            "toc_offset": toc_offset_info,
            "outline_validation": outline_val_info}
    if not cands:
        if call_llm:
            whole = MDASpan(0, min(len(page_texts) - 1, 80), method="scan")
            got = from_llm(page_texts, [whole], call_llm)
            diag["llm_used"] = True
            return got, diag
        return None, diag

    cands.sort(key=lambda c: -c.score)
    top = cands[0]
    supporters = sum(1 for c in cands[1:] if _agree(top, c))
    top.score = min(0.99, top.score + SUPPORTER_WEIGHT * supporters)
    top.supporters = supporters
    diag["supporters"] = supporters

    ambiguous = top.score < 0.7 or (len(cands) > 1 and supporters == 0)
    if ambiguous and call_llm:
        got = from_llm(page_texts, cands, call_llm)
        diag["llm_used"] = True
        if got and got.score >= top.score:
            top = got
    # a span must actually contain prose
    words = sum(len(page_texts.get(n, "").split())
                for n in range(top.start_page, top.end_page + 1))
    diag["candidate_span_words"] = words
    diag["span_words"] = words
    if words < MIN_MDA_WORDS:
        top.score *= 0.5
        diag["too_short"] = True
    return top, diag
