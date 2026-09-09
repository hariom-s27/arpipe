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
    words = mda_text.split()
    n = len(words)
    low = mda_text.lower()
    leaks = [tag for pat, tag in LEAK_PATTERNS if re.search(pat, low)]
    cues = sum(1 for c in MANDATED_RATIOS if c in low)
    alpha = sum(1 for ch in mda_text if ch.isalpha())
    digits = sum(1 for ch in mda_text if ch.isdigit())
    long_tok = sum(1 for w in words if len(w) > 28)
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
    }


def grade(rep: VerificationReport, qc: dict, span_score: float) -> str:
    if not rep.company_ok or qc["too_short"] or qc["long_token_frac"] > 0.03:
        return "low"
    if rep.year_ok and span_score >= 0.8 and not qc["leaks"] and not rep.notes:
        return "high"
    if rep.year_ok and span_score >= 0.6 and len(qc["leaks"]) <= 1:
        return "medium"
    return "low"
