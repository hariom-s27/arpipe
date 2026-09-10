"""Prove that the text we extracted really is company X's FY-Y MD&A.

Three independent things get checked, because any one of them fails
routinely in the wild:

  identity  A file served from BSE under scrip 500325 is *usually* Reliance,
            but redirects, mis-filed attachments and merged-entity reports do
            happen. We look for hard identifiers inside the document (CIN,
            ISIN) and fall back to fuzzy name matching against the canonical
            name plus every former name.

  year      Filenames and exchange metadata carry the *filing* year, which is
            not the reporting year: an FY2014-15 report is filed in Aug 2015
            and companies sometimes file two years in one go after a lapse.
            So the year is read from the document itself.

  section   The extracted span must look like MD&A: Schedule V cues present,
            enough prose, and no leakage into the auditor's report or the
            financial statements.

Era rules that make the year check sharper:
  - The 8 mandated ratios (Debtors Turnover ... Return on Net Worth) are
    required only from FY2019-20. Their presence implies FY>=2020; their
    absence weakly implies FY<2020.
  - BRSR replaced the Business Responsibility Report for the top 1,000 listed
    entities from FY2022-23.
  - Ind AS became mandatory in phases from FY2016-17; "Ind AS" in the text
    implies FY>=2016 for phase-1 companies.
"""
from __future__ import annotations

import re
from collections import Counter

from rapidfuzz import fuzz

from .models import Company, VerificationReport
from .patterns import (AS_AT_RE, CIN_RE, FY_RANGE_RE, FY_SINGLE_RE, ISIN_RE,
                       MANDATED_RATIOS, YEAR_ENDED_RE)

NAME_MATCH_STRONG = 88
NAME_MATCH_WEAK = 72

# P17 reading-order gate. orphan_start_frac (see order_quality) is ~0 in
# correctly ordered prose and jumps when column interleaving splices
# sentences: > MAX caps the tier at medium, > 2*MAX forces low. PROVISIONAL -
# picked from four documents (clean 0.000-0.004, iLovePDF-shredded 0.079-0.102,
# empty gap between); must be re-fit against the labelled 300. Moves to config
# in P15.
ORPHAN_START_FRAC_MAX = 0.03

_SUFFIXES = re.compile(
    r"\b(limited|ltd|private|pvt|public|company|co|corporation|corp|"
    r"industries|india|the|and|&|incorporated|inc|plc)\b\.?", re.I)


def normalise_name(s: str) -> str:
    s = re.sub(r"[^\w\s&]", " ", s or "")
    s = _SUFFIXES.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def name_similarity(found: str, company: Company) -> tuple[float, str]:
    targets = [company.canonical_name, *company.aliases]
    best, who = 0.0, ""
    nf = normalise_name(found)
    if not nf:
        return 0.0, ""
    for t in targets:
        nt = normalise_name(t)
        if not nt:
            continue
        s = max(fuzz.token_set_ratio(nf, nt), fuzz.partial_ratio(nf, nt))
        if s > best:
            best, who = s, t
    return best, who


def find_company_name_mentions(text: str, company: Company,
                               window: int = 4000) -> tuple[float, str]:
    """Slide the canonical name over the head of the document."""
    head = text[:window]
    best, who = name_similarity(head, company)
    return best, who


# ------------------------------------------------------------------ fiscal year
def _norm_fy_end(y1: int, y2raw: str) -> int | None:
    y2 = int(y2raw)
    if len(y2raw) == 2:
        y2 = (y1 // 100) * 100 + y2
        if y2 < y1:
            y2 += 100
    if y2 - y1 != 1:
        return None
    return y2


def fy_candidates(text: str) -> Counter[int]:
    """Every plausible FY-end year mentioned, weighted by evidence strength."""
    c: Counter[int] = Counter()
    for m in FY_RANGE_RE.finditer(text):
        fy = _norm_fy_end(int(m.group(1)), m.group(2))
        if fy and 1995 <= fy <= 2100:
            c[fy] += 3
    for m in YEAR_ENDED_RE.finditer(text):
        month, yr = m.group(1).lower(), int(m.group(2))
        if month.startswith("mar"):
            c[yr] += 5                     # the Indian statutory year end
        else:
            c[yr] += 1                     # non-March year ends exist but are rare
    for m in AS_AT_RE.finditer(text):
        if m.group(1).lower().startswith("mar"):
            c[int(m.group(2))] += 2
    for m in FY_SINGLE_RE.finditer(text):
        y = int(m.group(1))
        if 1995 <= y <= 2100:
            c[y] += 2
    return c


def era_signals(text: str) -> dict[str, bool]:
    low = text.lower()
    ratios_present = sum(1 for r in MANDATED_RATIOS if r in low) >= 4
    return {
        "mandated_ratios": ratios_present,                       # => FY>=2020
        "brsr": bool(re.search(r"business\s+responsibility\s+and\s+sustainability", low)),  # FY>=2023
        "br_report": bool(re.search(r"business\s+responsibility\s+report", low)),           # FY>=2013
        "ind_as": bool(re.search(r"\bind\s*as\b", low)),                                    # FY>=2016
        "companies_act_2013": "companies act, 2013" in low or "companies act 2013" in low,  # FY>=2015
        "csr": bool(re.search(r"corporate\s+social\s+responsibility", low)),                # FY>=2015
    }


def check_era(fy_end: int, sig: dict[str, bool]) -> list[str]:
    notes = []
    if sig["mandated_ratios"] and fy_end < 2020:
        notes.append(f"ratio-table present but fy_end={fy_end} (<2020)")
    if sig["brsr"] and fy_end < 2023:
        notes.append(f"BRSR present but fy_end={fy_end} (<2023)")
    if sig["companies_act_2013"] and fy_end < 2015:
        notes.append(f"Companies Act 2013 cited but fy_end={fy_end}")
    if sig["ind_as"] and fy_end < 2016:
        notes.append(f"Ind AS cited but fy_end={fy_end}")
    return notes


# ---------------------------------------------------------------------- verdict
def verify(front_text: str, mda_text: str, company: Company,
           expected_fy_end: int) -> VerificationReport:
    rep = VerificationReport(company_ok=False, year_ok=False)
    whole = f"{front_text}\n{mda_text}"

    # --- identity -------------------------------------------------------
    cins = CIN_RE.findall(whole)
    if cins:
        cin = "".join(cins[0])
        rep.cin_found = cin
        rep.company_evidence.append(f"cin:{cin}")
        if company.cin and cin.upper() == company.cin.upper():
            rep.company_ok = True
            rep.company_evidence.append("cin:exact_match")
        elif company.cin:
            rep.notes.append(f"CIN mismatch: doc={cin} expected={company.cin}")

    isins = ISIN_RE.findall(whole)
    if isins:
        rep.isin_found = isins[0]
        rep.company_evidence.append(f"isin:{isins[0]}")
        if company.isin and isins[0] == company.isin:
            rep.company_ok = True
            rep.company_evidence.append("isin:exact_match")

    sim, matched = find_company_name_mentions(front_text, company)
    rep.name_similarity = sim
    if matched:
        rep.company_evidence.append(f"name:{matched}:{sim:.0f}")
    if not rep.company_ok:
        rep.company_ok = sim >= NAME_MATCH_STRONG
        if NAME_MATCH_WEAK <= sim < NAME_MATCH_STRONG:
            rep.notes.append(f"weak name match ({sim:.0f})")

    # --- fiscal year ----------------------------------------------------
    cands = fy_candidates(front_text[:20000]) + fy_candidates(mda_text[:20000])
    if cands:
        top, weight = cands.most_common(1)[0]
        rep.fy_found = top
        rep.year_evidence.append(f"modal_fy:{top}:w{weight}")
        rep.year_ok = top == expected_fy_end
        if not rep.year_ok and cands.get(expected_fy_end, 0) >= max(3, weight * 0.5):
            # the expected year is well attested even if not modal
            rep.year_ok = True
            rep.year_evidence.append(f"expected_fy_supported:{cands[expected_fy_end]}")
        if not rep.year_ok:
            rep.notes.append(f"year mismatch: doc={top} expected={expected_fy_end}")
    else:
        rep.notes.append("no fiscal-year evidence found")

    rep.notes.extend(check_era(expected_fy_end, era_signals(whole)))
    return rep


# ------------------------------------------------------------------ section QC
LEAK_PATTERNS = [
    (r"we\s+have\s+audited\s+the\s+accompanying", "auditor_report_leak"),
    (r"basis\s+for\s+opinion", "auditor_report_leak"),
    (r"notice\s+is\s+hereby\s+given\s+that", "agm_notice_leak"),
    (r"notes\s+forming\s+part\s+of\s+the\s+financial\s+statements", "notes_leak"),
    (r"composition\s+of\s+the\s+board\s+of\s+directors", "cg_report_leak"),
]


def section_qc(mda_text: str) -> dict:
    # mda_text is prose only from P18 on - chart/table number-soup has been
    # quarantined to mda_blocks.json before this runs, so n_words, n_chars and
    # digit_ratio here are not inflated by loose figures. pipeline.py records
    # blocks_quarantined / words_quarantined / n_words_note alongside.
    words = mda_text.split()
    n = len(words)
    low = mda_text.lower()
    leaks = [tag for pat, tag in LEAK_PATTERNS if re.search(pat, low)]
    cues = sum(1 for c in MANDATED_RATIOS if c in low)
    alpha = sum(1 for ch in mda_text if ch.isalpha())
    digits = sum(1 for ch in mda_text if ch.isdigit())
    long_tok = sum(1 for w in words if len(w) > 28)
    order = order_quality(mda_text)
    return {
        "n_words": n,
        "n_chars": len(mda_text),
        "alpha_ratio": round(alpha / max(1, len(mda_text)), 3),
        "digit_ratio": round(digits / max(1, len(mda_text)), 3),
        "avg_word_len": round(sum(len(w) for w in words) / max(1, n), 2),
        "long_token_frac": round(long_tok / max(1, n), 4),
        "ratio_cues": cues,
        "leaks": leaks,
        "too_short": n < 250,
        "too_long": n > 40000,
        # a page of a financial statement is >25% digits; MD&A prose is <12%
        "looks_like_tables": digits / max(1, alpha + digits) > 0.25,
        # reading-order signal - character ratios above are blind to it (P17)
        **{k: order[k] for k in ("orphan_start_frac", "dangling_end_frac",
                                 "orphan_starts", "dangling_ends", "n_paragraphs")},
    }


# ------------------------------------------------------------- reading order
# Everything in section_qc measures *what characters are present*. None of it
# measures *whether they are in the right order*. Column interleaving splices
# the bottom of one column onto the top of the next: the text reads fluently,
# passes every band above, and silently corrupts every order-sensitive
# downstream task. These two signals are near zero on correctly ordered prose
# and rise when sentences have been cut apart.

_SENT_END_RE = re.compile(r"""[.!?]["'”’)\]]*\s*$""")

# Lowercase words that routinely lead a heading; kept out of the Title-Case
# test so "Risk and Sustainability Outlook" still reads as a heading.
_HEADING_LEAD_WORDS = frozenset(
    "a an and or the of to in on for at by is as with from into over".split())

# A fragment ending on a bare function word ("...Policy Report, the") is far
# more likely a spurious wrap-break than a dropped column tail, which ends on
# a content word ("...challenges to monetary policy").
_FUNCTION_TAIL = frozenset(
    "the a an of and or to in for with by from as on at that which this".split())

_HEADING_MAX_CHARS = 60
_HEADING_MAX_WORDS = 8


def _reconstruct_paragraphs(text: str) -> list[str]:
    """Rebuild logical paragraphs from wrapped / shredded lines.

    Jain FY2025 came through iLovePDF, which shredded it into near-per-line
    (sometimes per-word) blocks, so raw lines cannot be scored - every wrap
    would read as an orphan. Accumulate consecutive non-blank lines into one
    paragraph, breaking only on a blank line or once a line has closed a
    sentence.
    """
    paras: list[str] = []
    cur: list[str] = []
    for raw in text.split("\n"):
        ln = raw.strip()
        if not ln:
            if cur:
                paras.append(" ".join(cur))
                cur = []
            continue
        cur.append(ln)
        if _SENT_END_RE.search(ln):
            paras.append(" ".join(cur))
            cur = []
    if cur:
        paras.append(" ".join(cur))
    return paras


def _looks_like_heading(p: str) -> bool:
    """A section-heading-shaped paragraph: short, no terminal punctuation,
    ALL CAPS or strict Title Case ("GLOBAL ECONOMY", "Global Economic
    Overview").

    The heading case is not optional: the worst splice in Jain FY2025 lands
    directly under "GLOBAL ECONOMY", which carries no full stop, so a rule
    that only checks for a preceding ". ! ?" misses the single most important
    case this metric exists to catch. Strict on purpose - a prose line with a
    few proper nouns ("At Jain Irrigation Systems Ltd., we recognize the")
    must not read as a heading, or the line that continues it is miscounted.
    """
    s = p.strip()
    if not s or len(s) > _HEADING_MAX_CHARS or s[-1] in ".!?:;,":
        return False
    words = s.split()
    if not (1 <= len(words) <= _HEADING_MAX_WORDS):
        return False
    letters = [c for c in s if c.isalpha()]
    if not letters:
        return False
    if sum(c.isupper() for c in letters) / len(letters) >= 0.7:
        return True                                     # ALL CAPS / near-all
    sig = [w for w in words
           if any(c.isalpha() for c in w) and w.lower() not in _HEADING_LEAD_WORDS]
    return bool(sig) and all(w[0].isupper() for w in sig)   # every content word


def _orphan_start(p: str) -> bool:
    """Begins with a lowercase letter, a comma, or a closing bracket."""
    c = p[:1]
    return c.islower() or c in ",)]}"


def _dangling_tail(p: str) -> bool:
    """Ends mid-phrase on a lowercase content word - the shape of a dropped
    column tail ("...challenges to monetary policy"). Excludes a capitalised
    last word (usually mid-name), a bare function-word tail, and a colon
    lead-in ("Several key drivers underpin this outlook:")."""
    s = p.rstrip()
    if s.endswith((":", ";")):
        return False
    toks = s.split()
    if len(toks) < 4:
        return False
    last = toks[-1].strip("""\"'”’)]}.,;:""")
    return bool(last) and last[0].islower() and last.lower() not in _FUNCTION_TAIL


def order_quality(mda_text: str) -> dict:
    """Reading-order signal the character-ratio bands cannot see.

      orphan_start_frac  paragraphs that begin mid-sentence, over total
      dangling_end_frac  paragraphs that stop mid-phrase with no continuation

    Both are ~0 in correctly ordered prose and rise when column interleaving
    has cut sentences apart. orphan_start_frac is the graded one - it puts the
    shredded documents (~0.08-0.10) and the clean ones (~0.00) on opposite
    sides of an empty gap. dangling_end_frac is recorded but not graded: it is
    noisier (sentence-case headings, tables flattened into the prose) until
    P18 quarantines the tables.
    """
    paras = _reconstruct_paragraphs(mda_text)
    total = len(paras)
    if total < 5:
        return {"orphan_start_frac": 0.0, "dangling_end_frac": 0.0,
                "orphan_starts": 0, "dangling_ends": 0, "n_paragraphs": total}

    orphans = danglers = 0
    for i, p in enumerate(paras):
        prev = paras[i - 1] if i else ""
        nxt = paras[i + 1] if i + 1 < total else ""
        if i and _orphan_start(p) and (
                _SENT_END_RE.search(prev) or _looks_like_heading(prev)):
            orphans += 1
        if (nxt and not _SENT_END_RE.search(p) and not _looks_like_heading(p)
                and _dangling_tail(p)
                and not (nxt[:1].islower() or nxt[:1].isdigit())):
            danglers += 1

    return {
        "orphan_start_frac": round(orphans / total, 4),
        "dangling_end_frac": round(danglers / total, 4),
        "orphan_starts": orphans,
        "dangling_ends": danglers,
        "n_paragraphs": total,
    }


def grade(rep: VerificationReport, qc: dict, span_score: float) -> str:
    osf = qc.get("orphan_start_frac", 0.0)
    if (not rep.company_ok or qc["too_short"] or qc["long_token_frac"] > 0.03
            or osf > 2 * ORPHAN_START_FRAC_MAX):     # P17: badly scrambled order
        return "low"
    if (rep.year_ok and span_score >= 0.8 and not qc["leaks"] and not rep.notes
            and osf <= ORPHAN_START_FRAC_MAX):       # P17: mild scramble -> medium
        return "high"
    if rep.year_ok and span_score >= 0.6 and len(qc["leaks"]) <= 1:
        return "medium"
    return "low"
