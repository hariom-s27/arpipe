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

import pymupdf

from .models import DocProfile, MDASpan
from .patterns import (ANNEXURE_HEADING_RE, MDA_ACRONYM_RE, MDA_BODY_CUE_RES,
                       MDA_COMBINED_RE, MDA_HEADING_RE, MDA_TERMINATOR_RE)

MAX_MDA_PAGES = 60          # sanity cap; real MD&A runs 3-25 pages
MIN_MDA_WORDS = 250


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


def page_headings(page: pymupdf.Page, min_rel: float = 1.12) -> list[HeadingHit]:
    """Return lines that look typographically like headings."""
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
        if rel >= min_rel or (bold and len(txt) <= 90) or txt.isupper():
            out.append(HeadingHit(page.number, txt, size, rel, y / h,
                                  is_standalone=len(txt) <= 110, bold=bold))
    return out


def _is_mda_title(t: str) -> bool:
    if MDA_HEADING_RE.search(t) or MDA_COMBINED_RE.search(t):
        return True
    s = t.strip()
    return bool(len(s) <= 24 and MDA_ACRONYM_RE.search(s))


# ------------------------------------------------------------------- S1 outline
def from_outline(profile: DocProfile) -> MDASpan | None:
    if not profile.outline_titles:
        return None
    entries = sorted(profile.outline_titles, key=lambda e: e[2])
    start_i = None
    for i, (_lvl, title, pno) in enumerate(entries):
        if _is_mda_title(title):
            start_i = i
            break
    if start_i is None:
        return None
    s_lvl, s_title, s_page = entries[start_i]
    end_page = profile.n_pages - 1
    term = None
    for _lvl, title, pno in entries[start_i + 1:]:
        if pno > s_page:
            end_page = pno - 1
            term = title
            break
    if end_page - s_page + 1 > MAX_MDA_PAGES:
        end_page = s_page + MAX_MDA_PAGES - 1
    return MDASpan(start_page=s_page, end_page=max(s_page, end_page),
                   method="outline", heading_text=s_title,
                   terminator_text=term, score=0.95)


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
        dotted = sum(1 for ln in t.split("\n") if TOC_LINE_RE.match(ln.strip()))
        if dotted >= 4 or (re.search(r"\bcontents\b", t, re.I) and dotted >= 2):
            hits.append(n)
    return hits


def _solve_label_offset(doc: pymupdf.Document, page_texts: dict[int, str],
                        sample: int = 40) -> int | None:
    """Find k such that physical_page = printed_folio + k.

    Reads the folio printed in the top/bottom margin of sampled pages and
    takes the modal difference. Robust to the many pages that print no folio.
    """
    diffs: defaultdict[int, int] = defaultdict(int)
    nos = sorted(page_texts)
    step = max(1, len(nos) // sample)
    for n in nos[::step]:
        lines = [l.strip() for l in page_texts[n].split("\n") if l.strip()]
        for cand in lines[:2] + lines[-3:]:
            m = re.fullmatch(r"\|?\s*(\d{1,4})\s*\|?", cand)
            if m:
                folio = int(m.group(1))
                if 0 < folio <= doc.page_count + 40:
                    diffs[n - folio] += 1
    if not diffs:
        return None
    k, c = max(diffs.items(), key=lambda kv: kv[1])
    return k if c >= 3 else None


def from_toc(doc: pymupdf.Document, page_texts: dict[int, str]) -> MDASpan | None:
    toc_pages = find_toc_pages(page_texts)
    if not toc_pages:
        return None
    entries: list[tuple[str, int]] = []
    for n in toc_pages:
        for ln in page_texts[n].split("\n"):
            m = TOC_LINE_RE.match(ln.strip())
            if m:
                entries.append((m.group("title").strip(), int(m.group("page"))))
    if not entries:
        return None
    offset = _solve_label_offset(doc, page_texts)
    if offset is None:
        # fall back: assume the TOC page itself is roughly folio 1-3
        offset = toc_pages[0]
    entries.sort(key=lambda e: e[1])
    for i, (title, folio) in enumerate(entries):
        if _is_mda_title(title):
            start = folio + offset
            end = doc.page_count - 1
            term = None
            for t2, f2 in entries[i + 1:]:
                if f2 > folio:
                    end = f2 + offset - 1
                    term = t2
                    break
            start = max(0, min(start, doc.page_count - 1))
            end = max(start, min(end, doc.page_count - 1))
            if end - start + 1 > MAX_MDA_PAGES:
                end = start + MAX_MDA_PAGES - 1
            return MDASpan(start, end, method="toc", heading_text=title,
                           terminator_text=term, score=0.8)
    return None


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
        for h in hits:
            if not _is_mda_title(h.text):
                continue
            sc = 0.45
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
    end = _find_terminator(doc, page_texts, h.page_no)
    return MDASpan(h.page_no, end, method="heading", heading_text=h.text,
                   score=min(0.92, sc))


def _find_terminator(doc: pymupdf.Document, page_texts: dict[int, str],
                     start: int) -> int:
    limit = min(start + MAX_MDA_PAGES, max(page_texts) if page_texts else start)
    for n in range(start + 1, limit + 1):
        txt = page_texts.get(n, "")
        if not txt:
            continue
        if ANNEXURE_HEADING_RE.search(txt):
            return max(start, n - 1)
        try:
            hits = page_headings(doc.load_page(n))
        except Exception:
            hits = []
        for h in hits:
            if MDA_TERMINATOR_RE.search(h.text) and h.y_frac < 0.6:
                return max(start, n - 1)
        head = "\n".join(txt.split("\n")[:6])
        if MDA_TERMINATOR_RE.search(head):
            return max(start, n - 1)
    return min(limit, start + MAX_MDA_PAGES - 1)


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


def from_body_scores(page_texts: dict[int, str]) -> MDASpan | None:
    nos = sorted(page_texts)
    if not nos:
        return None
    scores = {n: page_body_score(page_texts[n]) for n in nos}
    if max(scores.values(), default=0.0) < 0.35:
        return None
    # best contiguous run under a decay: allows one weak page inside a section
    best = (0.0, nos[0], nos[0])
    for i, s in enumerate(nos):
        acc, last_good = 0.0, s
        for j in range(i, min(i + MAX_MDA_PAGES, len(nos))):
            n = nos[j]
            acc += scores[n] - 0.12          # penalty keeps runs from sprawling
            if scores[n] > 0.2:
                last_good = n
            if acc > best[0]:
                best = (acc, s, last_good)
            if acc < -0.9:
                break
    if best[0] <= 0.0:
        return None
    return MDASpan(best[1], best[2], method="body_score",
                   score=min(0.72, 0.3 + best[0] / 6.0))


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
            if len(ln) > 110 or not _is_mda_title(ln):
                continue
            sc = 0.40 + 0.10 * (top_lines - i) / top_lines
            if len(ln) <= 60:
                sc += 0.10
            if ln.isupper():
                sc += 0.05
            # a contents page mentions every section; do not start there
            if sum(1 for l in lines if MDA_TERMINATOR_RE.search(l)) >= 3:
                sc -= 0.30
            if best is None or sc > best[0]:
                best = (sc, n, ln)
    if not best:
        return None
    sc, n, ln = best
    end = _find_terminator_text(page_texts, n)
    return MDASpan(n, end, method="heading_text", heading_text=ln,
                   score=min(0.78, sc))


def _find_terminator_text(page_texts: dict[int, str], start: int,
                          top_lines: int = 5) -> int:
    nos = [n for n in sorted(page_texts) if n > start]
    for n in nos[:MAX_MDA_PAGES]:
        lines = [l.strip() for l in page_texts[n].split("\n") if l.strip()]
        if ANNEXURE_HEADING_RE.search(page_texts[n]):
            return max(start, n - 1)
        for ln in lines[:top_lines]:
            if len(ln) <= 110 and MDA_TERMINATOR_RE.search(ln):
                return max(start, n - 1)
    return max(start, nos[-1] if nos else start)


def refine_end(span: MDASpan, page_texts: dict[int, str], fetch_text,
               max_extra: int = 12) -> MDASpan:
    """Walk forward past the end of a span found on a sparse page sample.

    `fetch_text(page_no) -> str` OCRs one page on demand. Used after the
    index-sample pass, where pages beyond the sample scored zero simply
    because they had not been read yet.
    """
    n = span.end_page
    for _ in range(max_extra):
        nxt = n + 1
        txt = page_texts.get(nxt)
        if txt is None:
            txt = fetch_text(nxt)
            if txt is None:
                break
            page_texts[nxt] = txt
        lines = [l.strip() for l in txt.split("\n") if l.strip()]
        head = lines[:5]
        if (ANNEXURE_HEADING_RE.search(txt)
                or any(len(l) <= 110 and MDA_TERMINATOR_RE.search(l)
                       for l in head)):
            break
        if page_body_score(txt) < 0.15 and len(txt.split()) < 60:
            break
        n = nxt
    return replace(span, end_page=n, method=span.method + "+refined")


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
            start = n
            break

    end = span.end_page
    for n in range(start + 1, span.end_page + 1):
        t = page_texts.get(n)
        if not t:
            continue
        lines = [l.strip() for l in t.split("\n") if l.strip()][:5]
        if (ANNEXURE_HEADING_RE.search(t)
                or any(len(l) <= 110 and MDA_TERMINATOR_RE.search(l)
                       for l in lines)):
            end = n - 1
            break
    end = max(start, end)
    return replace(span, start_page=start, end_page=end,
                   method=span.method + "+trimmed")


# ---------------------------------------------------------------------- arbiter
def _agree(a: MDASpan, b: MDASpan, tol: int = 2) -> bool:
    return abs(a.start_page - b.start_page) <= tol


def locate(doc: pymupdf.Document, profile: DocProfile,
           page_texts: dict[int, str], call_llm=None) -> tuple[MDASpan | None, dict]:
    cands: list[MDASpan] = []
    for fn in (lambda: from_outline(profile),
               lambda: from_toc(doc, page_texts),
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
                           for c in cands]}
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
    top.score = min(0.99, top.score + 0.06 * supporters)
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
    diag["span_words"] = words
    if words < MIN_MDA_WORDS:
        top.score *= 0.5
        diag["too_short"] = True
    return top, diag
