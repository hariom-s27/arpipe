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
from .patterns import (AS_AT_RE, CIN_RE, DEVANAGARI_RE, FY_RANGE_RE,
                       FY_SINGLE_RE, ISIN_RE, MANDATED_RATIOS, MDA_HEADING_RE,
                       YEAR_ENDED_RE, is_valid_isin)

# --- tunable thresholds ---------------------------------------------------
# All thresholds provisional until re-fit against the labelled 300.
# provisional until re-fit against the labelled 300
NAME_MATCH_STRONG = 88
# provisional until re-fit against the labelled 300
NAME_MATCH_WEAK = 72
# provisional until re-fit against the labelled 300
REQUIRE_YEAR_EVIDENCE = True
# provisional until re-fit against the labelled 300
ORPHAN_START_FRAC_MAX = 0.03
# PM1: diagnostic-only threshold for the per-physical-page orphan_start_frac
# telemetry (arpipe orderqc). Deliberately a separate constant from
# ORPHAN_START_FRAC_MAX above - it exists to describe how often the page-level
# signal exceeds the historical gate value, even if that gate is ever retuned.
# Never read by grade(), build_reasons(), or any acceptance/rejection path.
PAGE_ORPHAN_DIAGNOSTIC_THRESHOLD = 0.03
# PM1: a page attributed only 0 or 1 reconstructed paragraphs cannot support a
# rate estimate (0/1 or 1/1 is not a fraction, it is a coin flip) - such pages
# report None ("not measured"), never a fabricated 0.0 or 1.0.
PAGE_ORPHAN_MIN_PARAGRAPHS = 2
# provisional until re-fit against the labelled 300
FY_WEIGHT_FLOOR = 15
# provisional until re-fit against the labelled 300
TOO_SHORT_WORDS = 250
# provisional until re-fit against the labelled 300
TOO_LONG_WORDS = 40000
# provisional until re-fit against the labelled 300
LOOKS_LIKE_TABLES_DIGIT_RATIO = 0.25
# provisional until re-fit against the labelled 300
GRADE_HIGH_MIN_SUPPORTERS = 2
# provisional until re-fit against the labelled 300
GRADE_HIGH_MIN_SCORE = 0.80
# provisional until re-fit against the labelled 300
GRADE_MEDIUM_MIN_SCORE = 0.60
# provisional until re-fit against the labelled 300
GRADE_SOLO_MIN_SCORE = 0.70
# provisional until re-fit against the labelled 300
REPROCESSOR_CAP_GRADE = "medium"

ORPHAN_BASIS = "prose_only"          # or "prose_and_tables" (pre-P18)
ORPHAN_GATE_VERSION = "p17.1"        # p17 gate + p16b column-cut fire signal

# P34: wrong-language quarantine (looks_like_wrong_language / page_has_bilingual_heading).
# provisional until re-fit against the labelled 300
DEVANAGARI_FRAC_MIN = 0.10
# provisional until re-fit against the labelled 300
ENGLISH_WORD_FRAC_MAX = 0.30
# provisional until re-fit against the labelled 300
RARE_PUNCT_FREQ_MIN = 0.020
# provisional until re-fit against the labelled 300
DIGIT_EMBEDDED_FRAC_MIN = 0.02
# provisional until re-fit against the labelled 300
HIGH_CODEPOINT_FREQ_MIN = 0.15
# provisional until re-fit against the labelled 300
LONG_WORD_FRAC_MIN = 0.10
# provisional until re-fit against the labelled 300
WRONG_LANGUAGE_WINDOW = 2000
# provisional until re-fit against the labelled 300
WRONG_LANGUAGE_MIN_TOKENS = 15


def configure(cfg: dict | None = None) -> None:
    """Update thresholds from resolved configuration."""
    global NAME_MATCH_STRONG, NAME_MATCH_WEAK, REQUIRE_YEAR_EVIDENCE
    global ORPHAN_START_FRAC_MAX, FY_WEIGHT_FLOOR, TOO_SHORT_WORDS, TOO_LONG_WORDS
    global LOOKS_LIKE_TABLES_DIGIT_RATIO, GRADE_HIGH_MIN_SUPPORTERS, GRADE_HIGH_MIN_SCORE
    global GRADE_MEDIUM_MIN_SCORE, GRADE_SOLO_MIN_SCORE, REPROCESSOR_CAP_GRADE
    global DEVANAGARI_FRAC_MIN, ENGLISH_WORD_FRAC_MAX, RARE_PUNCT_FREQ_MIN
    global DIGIT_EMBEDDED_FRAC_MIN, HIGH_CODEPOINT_FREQ_MIN, LONG_WORD_FRAC_MIN
    global WRONG_LANGUAGE_WINDOW, WRONG_LANGUAGE_MIN_TOKENS
    if not cfg:
        return
    NAME_MATCH_STRONG = cfg.get("name_match_strong", NAME_MATCH_STRONG)
    NAME_MATCH_WEAK = cfg.get("name_match_weak", NAME_MATCH_WEAK)
    REQUIRE_YEAR_EVIDENCE = cfg.get("require_year_evidence", REQUIRE_YEAR_EVIDENCE)
    ORPHAN_START_FRAC_MAX = cfg.get("orphan_start_frac_max", ORPHAN_START_FRAC_MAX)
    FY_WEIGHT_FLOOR = cfg.get("fy_weight_floor", FY_WEIGHT_FLOOR)
    TOO_SHORT_WORDS = cfg.get("too_short_words", TOO_SHORT_WORDS)
    TOO_LONG_WORDS = cfg.get("too_long_words", TOO_LONG_WORDS)
    LOOKS_LIKE_TABLES_DIGIT_RATIO = cfg.get("looks_like_tables_digit_ratio", LOOKS_LIKE_TABLES_DIGIT_RATIO)
    GRADE_HIGH_MIN_SUPPORTERS = cfg.get("grade_high_min_supporters", GRADE_HIGH_MIN_SUPPORTERS)
    GRADE_HIGH_MIN_SCORE = cfg.get("grade_high_min_score", GRADE_HIGH_MIN_SCORE)
    GRADE_MEDIUM_MIN_SCORE = cfg.get("grade_medium_min_score", GRADE_MEDIUM_MIN_SCORE)
    GRADE_SOLO_MIN_SCORE = cfg.get("grade_solo_min_score", GRADE_SOLO_MIN_SCORE)
    REPROCESSOR_CAP_GRADE = cfg.get("reprocessor_cap_grade", REPROCESSOR_CAP_GRADE)
    DEVANAGARI_FRAC_MIN = cfg.get("devanagari_frac_min", DEVANAGARI_FRAC_MIN)
    ENGLISH_WORD_FRAC_MAX = cfg.get("english_word_frac_max", ENGLISH_WORD_FRAC_MAX)
    RARE_PUNCT_FREQ_MIN = cfg.get("rare_punct_freq_min", RARE_PUNCT_FREQ_MIN)
    DIGIT_EMBEDDED_FRAC_MIN = cfg.get("digit_embedded_frac_min", DIGIT_EMBEDDED_FRAC_MIN)
    HIGH_CODEPOINT_FREQ_MIN = cfg.get("high_codepoint_freq_min", HIGH_CODEPOINT_FREQ_MIN)
    LONG_WORD_FRAC_MIN = cfg.get("long_word_frac_min", LONG_WORD_FRAC_MIN)
    WRONG_LANGUAGE_WINDOW = cfg.get("wrong_language_window", WRONG_LANGUAGE_WINDOW)
    WRONG_LANGUAGE_MIN_TOKENS = cfg.get("wrong_language_min_tokens", WRONG_LANGUAGE_MIN_TOKENS)

# P22: free web PDF compressors / converters that re-lay the text layer into
# near-per-line fragments (the iLovePDF-shredded Jain reports are the known
# case). A document from one of these is labelled `source_shredded` and capped
# at `medium` regardless of how well xy_cut reassembled it, until P11 has >= 5
# such documents showing the reassembly holds. PROVISIONAL - extend from the
# P11 pdf_producer tally (audit `by_producer`).
REPROCESSOR_PRODUCERS = (
    "ilovepdf", "smallpdf", "pdf24", "sejda", "soda pdf", "online2pdf",
    "pdfescape", "pdf compressor", "compress pdf", "nitro",
)


def is_reprocessor(producer: str | None) -> bool:
    p = (producer or "").lower()
    return any(k in p for k in REPROCESSOR_PRODUCERS)

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
    ratios_present = sum(1 for r in MANDATED_RATIOS if (r.search(text) if hasattr(r, "search") else r in low)) >= 4
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
    if not sig["mandated_ratios"] and fy_end >= 2020:
        notes.append(f"mandated ratios table absent from document (disclosure finding for fy_end={fy_end} >= 2020)")
    if sig["brsr"] and fy_end < 2023:
        notes.append(f"BRSR present but fy_end={fy_end} (<2023)")
    if sig["companies_act_2013"] and fy_end < 2015:
        notes.append(f"Companies Act 2013 cited but fy_end={fy_end}")
    if sig["ind_as"] and fy_end < 2016:
        notes.append(f"Ind AS cited but fy_end={fy_end}")
    return notes


# ---------------------------------------------------------------------- ISIN (P3)
_ISIN_SECTION_KEYWORDS = (
    "general shareholder information",
    "shareholder information",
    "shareholders information",
    "corporate governance",
    "depository system",
    "corporate information",
    "company information",
    "statutory report",
)


def _isin_priority(isin: str) -> int:
    """P4 preference: INE (equity) > IN9 (DVR) > INF (mutual fund) > others."""
    prefix = isin[:3].upper()
    if prefix.startswith("INE"):
        return 1
    if prefix.startswith("IN9"):
        return 2
    if prefix.startswith("INF"):
        return 3
    if prefix.startswith(("INC", "IND")):
        return 4
    return 5


def extract_isin(page_texts: dict[int, str] | None = None,
                 whole: str = "",
                 company: Company | None = None) -> tuple[str | None, int | None, list[str]]:
    """Find and validate ISINs across annual report pages.

    Scans section-anchored pages (General Shareholder Information, Corporate
    Governance, Depository System, etc.) and front matter (pages 0-19), with
    whole-document fallback if unlocated. Every candidate is verified against
    the ISO 6166 Luhn mod-10 check digit.

    Returns:
        (best_isin, page_no, isins_seen)
    """
    pairs: list[tuple[int | None, str]] = []

    if page_texts:
        # Pass 1: candidate pages (front matter + section-anchored pages)
        candidate_pages: set[int] = set()
        for pno, txt in page_texts.items():
            if pno < 20:
                candidate_pages.add(pno)
                continue
            head = txt[:600].lower()
            if any(kw in head for kw in _ISIN_SECTION_KEYWORDS) or "isin" in head:
                candidate_pages.add(pno)

        for pno in sorted(candidate_pages):
            for m in ISIN_RE.finditer(page_texts[pno]):
                cand = m.group()
                if is_valid_isin(cand):
                    pairs.append((pno, cand))

        # Pass 2: fallback to all remaining pages if none found yet
        if not pairs:
            for pno in sorted(page_texts):
                if pno in candidate_pages:
                    continue
                for m in ISIN_RE.finditer(page_texts[pno]):
                    cand = m.group()
                    if is_valid_isin(cand):
                        pairs.append((pno, cand))

    # Pass 3: fallback on whole string if page_texts was not provided
    if not pairs and whole:
        for m in ISIN_RE.finditer(whole):
            cand = m.group()
            if is_valid_isin(cand):
                pairs.append((None, cand))

    if not pairs:
        return None, None, []

    # All distinct valid ISINs in the order first seen
    seen: list[str] = []
    for _, isin in pairs:
        if isin not in seen:
            seen.append(isin)

    # Pick best: declared company.isin wins immediately; else P4 priority
    best_isin: str | None = None
    best_pno: int | None = None

    if company and company.isin and company.isin in seen:
        best_isin = company.isin
        best_pno = next((p for p, i in pairs if i == company.isin), None)
    else:
        sorted_isins = sorted(seen, key=_isin_priority)
        best_isin = sorted_isins[0]
        best_pno = next((p for p, i in pairs if i == best_isin), None)

    return best_isin, best_pno, seen


# ---------------------------------------------------------------------- verdict
def verify(front_text: str, mda_text: str, company: Company,
           expected_fy_end: int,
           page_texts: dict[int, str] | None = None,
           full_text: str | None = None) -> VerificationReport:
    rep = VerificationReport(company_ok=False, year_ok=False)
    whole = f"{front_text}\n{mda_text}"

    # --- identity: CIN --------------------------------------------------
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

    # --- identity: ISIN (P3) -------------------------------------------
    best_isin, isin_page, isins_seen = extract_isin(
        page_texts, whole=whole, company=company
    )
    rep.isins_seen = isins_seen
    if best_isin:
        rep.isin_found = best_isin
        rep.isin_found_on_page = isin_page
        rep.company_evidence.append(f"isin:{best_isin}")
        if company.isin and company.isin in isins_seen:
            rep.company_ok = True
            rep.company_evidence.append("isin:exact_match")
        elif company.isin:
            rep.notes.append(f"ISIN mismatch: doc={best_isin} expected={company.isin}")

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

    # --- era rules (P20: run on full document) -------------------------
    if full_text is not None:
        doc_text = full_text
    elif page_texts:
        doc_text = "\n".join(page_texts[n] for n in sorted(page_texts))
    else:
        doc_text = whole

    rep.era_signals_in_document = era_signals(doc_text)
    rep.notes.extend(check_era(expected_fy_end, rep.era_signals_in_document))
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
    cues = sum(1 for c in MANDATED_RATIOS if (c.search(mda_text) if hasattr(c, "search") else c in low))
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
        "ratio_cues_in_span": cues,
        "leaks": leaks,
        "too_short": n < TOO_SHORT_WORDS,
        "too_long": n > TOO_LONG_WORDS,
        # a page of a financial statement is >25% digits; MD&A prose is <12%
        "looks_like_tables": digits / max(1, alpha + digits) > LOOKS_LIKE_TABLES_DIGIT_RATIO,
        # reading-order signal - character ratios above are blind to it (P17)
        **{k: order[k] for k in ("orphan_start_frac", "dangling_end_frac",
                                 "orphan_starts", "dangling_ends", "n_paragraphs")},
        # P21: label the score so it stays interpretable across metric changes
        "orphan_basis": ORPHAN_BASIS,
        "orphan_gate_version": ORPHAN_GATE_VERSION,
        "orphan_gate_max": ORPHAN_START_FRAC_MAX,
    }


# --------------------------------------------------------- wrong-language QC
# P34: PSU bank reports print the full report twice - Hindi, then English -
# behind a single bilingual heading line ("प्रबंधन विचार-विमर्श ... Management
# Discussion and Analysis"). MDA_HEADING_RE only needs to match the Latin
# half, so it can lock onto the Hindi copy. Confirmed on real filings (PNB
# 2010-2015, IDBI 2024-2025), the mis-located body decodes as one of:
#   - a legacy Hindi font with no ToUnicode CMap -> Latin-range noise
#     ("çca/ku fopkj&foe'kZ") or Latin-1-extended noise ("Ÿ¸Ê „›í¸Ê›¸½")
#   - a scanned Hindi page OCR'd with the wrong language pack -> pseudo-English
#     lowercase noise ("wae faugt sit fascraut")
# All three are plain Latin/extended-Latin codepoints, so a script check
# (triage.detect_script) sees Latin and passes clean, and every existing QC
# band (word count, orphan_start_frac, confidence) measures prose *shape*,
# not language, so it is silent too - hence a dedicated gate.
_RARE_PUNCT_CHARS = frozenset("'/;][&~`")
# Letter-digit(s)-letter *within one token* ("H1N1"). Deliberately excludes a
# leading digit followed by letters ("21st", "2.2MMTA") - ordinal-date suffixes
# and number+unit notation are routine in Indian financial prose and are not
# a language signal.
_DIGIT_SANDWICH_RE = re.compile(r"[A-Za-z]\d+[A-Za-z]")
_ALPHA_WORD_RE = re.compile(r"[A-Za-z]+")
_TOKEN_RE = re.compile(r"\S+")

# Not a dictionary - the ~150 English function/common words that dominate any
# real English paragraph by raw token count, plus MD&A/annual-report domain
# vocabulary, so genuine but jargon- or number-heavy financial prose does not
# read as "not English". Evaluated per-window (see looks_like_wrong_language):
# a whole-document average dilutes below any sane threshold once a scrambled
# reading order interleaves short gibberish runs into real English pages.
_COMMON_ENGLISH_WORDS = frozenset("""
    the of and a to in is you that it he was for on are as with his they i at
    be this have from or one had by word but not what all were we when your
    can said there use an each which she do how their if will up other about
    out many then them these so some her would make like him into time has
    look two more write go see number no way could people my than first
    water been call who oil its now find long down day did get come made may
    part over new sound take only little work know place year live me back
    give most very after thing our just name good sentence man think say
    great where help through much before line right too mean old any same
    tell boy follow came want show also around form three small set put end
    does another well large must big even such because turn here why ask
    went men read need land different home us move try kind hand picture
    again change off play air away animal house point page letter mother
    answer found study still learn should world high every near add food
    between own below country plant last school father keep tree never start
    city earth eye light thought head under story saw left few while along
    might close something seem next hard open example begin life always
    those both paper together got group often run important until children
    side feet car mile night walk white began grow took river four carry
    state once book hear stop without second later miss idea enough eat face
    watch far west grand sun today report annual financial company management
    discussion analysis business bank banking growth increase decrease
    decreased increased performance total net profit loss income expense
    expenses expenditure capital market industry sector government policy
    economic economy international national development investment credit
    deposit deposits advances asset assets liability liabilities risk
    operation operations service services customer customers branch branches
    employee employees board director directors shareholder shareholders
    statement statements rate percent crore lakh india indian global domestic
    rural urban technology digital infrastructure sustainable corporate
    governance compliance audit review outlook strategy initiative
    initiatives ratio ratios turnover margin equity debt interest revenue
    budget fiscal quarter half previous current future significant various
    several including following above below during within across through
    among such also well further however therefore thus accordingly
    moreover overall continued continues remained remains expected achieved
    recorded reported noted observed particularly especially since period
    ended march comparison compared million billion crores lakhs section
    chapter table figure percentage gross public private limited companies
    scheme schemes fund funds reserve reserves provision provisions measures
    taken committee committees meeting held members member chairman managing
    executive officer officers staff human resources training system systems
    process processes framework product products segment segments region
    regions unit units plan plans project projects programme programmes
""".split())


def _wrong_language_window(chunk: str) -> dict | None:
    """Character/token statistics for one chunk of text. None if too short
    (fewer than WRONG_LANGUAGE_MIN_TOKENS alphabetic tokens) to score."""
    words = _ALPHA_WORD_RE.findall(chunk)
    lower_words = [w.lower() for w in words if len(w) >= 2]
    if len(lower_words) < WRONG_LANGUAGE_MIN_TOKENS:
        return None
    tokens = _TOKEN_RE.findall(chunk)
    return {
        "english_word_frac": round(
            sum(1 for w in lower_words if w in _COMMON_ENGLISH_WORDS) / len(lower_words), 4),
        "long_word_frac": round(
            sum(1 for w in words if len(w) >= 7) / len(words), 4),
        "rare_punct_freq": round(
            sum(1 for c in chunk if c in _RARE_PUNCT_CHARS) / max(1, len(chunk)), 4),
        "high_codepoint_freq": round(
            sum(1 for c in chunk if ord(c) > 127) / max(1, len(chunk)), 4),
        "digit_embedded_frac": round(
            sum(1 for t in tokens if _DIGIT_SANDWICH_RE.search(t)) / max(1, len(tokens)), 4),
    }


def _window_is_legacy_font(m: dict) -> bool:
    if m["english_word_frac"] >= ENGLISH_WORD_FRAC_MAX:
        return False
    # "unusual frequency of characters rare in English prose": the literal
    # punctuation + digit-sandwich signal catches the ASCII-heavy 2010-2014
    # PNB font; high_codepoint_freq generalises it to the Latin-1-extended
    # IDBI font, and long_word_frac catches wrong-language-OCR noise, which
    # uses almost no punctuation at all (PNB 2015) - real English prose (even
    # terse infographic/table fragments; see live_dataset false-positive
    # sweep) reliably clears at least one of these.
    return (m["rare_punct_freq"] > RARE_PUNCT_FREQ_MIN
            or m["digit_embedded_frac"] > DIGIT_EMBEDDED_FRAC_MIN
            or m["high_codepoint_freq"] > HIGH_CODEPOINT_FREQ_MIN
            or m["long_word_frac"] < LONG_WORD_FRAC_MIN)


def looks_like_wrong_language(text: str) -> dict:
    """Detect MD&A text that is actually the Hindi copy of a bilingual PSU
    report (see module comment above for the three observed encodings).

    Two independent signals, either is sufficient:
      (a) real Unicode Devanagari (U+0900-U+097F) above DEVANAGARI_FRAC_MIN
          of all characters.
      (b) "legacy font" heuristic, scored per WRONG_LANGUAGE_WINDOW-character
          window rather than over the whole text: fewer than
          ENGLISH_WORD_FRAC_MAX of a window's tokens are common English words
          AND the window's characters are anomalous for English prose. Windowing
          matters because a scrambled reading order interleaves short gibberish
          runs into an otherwise-real-English document; a whole-document
          average dilutes below any sane threshold (verified: PNB 2011 is only
          ~12% contaminated by character count).

    Returns every measured value, not just the verdict, so a quarantined row
    can be diagnosed from mda.json without re-deriving it.
    """
    if not text:
        return {"wrong_language_risk": False, "devanagari_frac": 0.0,
                "devanagari_hit": False, "legacy_font_hit": False,
                "windows_scored": 0, "windows_fired": 0, "worst_window": None}

    devanagari_frac = len(DEVANAGARI_RE.findall(text)) / len(text)
    devanagari_hit = devanagari_frac > DEVANAGARI_FRAC_MIN

    worst: tuple[tuple[int, float], int, dict, bool] | None = None
    windows_scored = windows_fired = 0
    for i in range(0, len(text), WRONG_LANGUAGE_WINDOW):
        m = _wrong_language_window(text[i:i + WRONG_LANGUAGE_WINDOW])
        if m is None:
            continue
        windows_scored += 1
        fired = _window_is_legacy_font(m)
        if fired:
            windows_fired += 1
        # worst = the fired window with the lowest english_word_frac; if none
        # fired, the lowest-scoring window overall (still useful for review).
        key = (0 if fired else 1, m["english_word_frac"])
        if worst is None or key < worst[0]:
            worst = (key, i, m, fired)

    legacy_font_hit = windows_fired > 0
    return {
        "wrong_language_risk": bool(devanagari_hit or legacy_font_hit),
        "devanagari_frac": round(devanagari_frac, 4),
        "devanagari_hit": devanagari_hit,
        "legacy_font_hit": legacy_font_hit,
        "windows_scored": windows_scored,
        "windows_fired": windows_fired,
        "worst_window": ({"offset": worst[1], "fired": worst[3], **worst[2]}
                         if worst else None),
    }


def page_has_bilingual_heading(page_text: str) -> dict:
    """True if a single page carries both an MD&A heading match and a
    substantial fraction of real Devanagari - the bilingual heading line
    itself, as opposed to looks_like_wrong_language's mis-decoded legacy-font
    body text. Complementary signal: fires even when the heading page's
    Hindi is properly Unicode-encoded (so devanagari_frac reads real, unlike
    the legacy-font case) but the body afterwards is not (yet) sampled."""
    if not page_text:
        return {"bilingual_heading_page": False, "heading_match": False,
                "devanagari_frac": 0.0}
    heading_match = bool(MDA_HEADING_RE.search(page_text))
    devanagari_frac = len(DEVANAGARI_RE.findall(page_text)) / len(page_text)
    return {
        "bilingual_heading_page": heading_match and devanagari_frac > DEVANAGARI_FRAC_MIN,
        "heading_match": heading_match,
        "devanagari_frac": round(devanagari_frac, 4),
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


def _reconstruct_paragraphs_tagged(
        lines: list[tuple[str, int | None]]) -> list[tuple[str, int | None]]:
    """Same reconstruction algorithm as _reconstruct_paragraphs, generalised to
    carry an opaque per-line tag (PM1: the physical page a line came from).

    Each returned paragraph carries the tag of its FIRST line - the
    physical-page attribution rule: a reconstructed paragraph belongs to the
    page containing its first non-whitespace source line. A blank tagged line
    (tag=None) forces a paragraph break exactly like a blank text line does,
    so this is a drop-in generalisation, not a new algorithm.
    """
    paras: list[tuple[str, int | None]] = []
    cur: list[str] = []
    cur_tag: int | None = None
    for raw, tag in lines:
        ln = raw.strip()
        if not ln:
            if cur:
                paras.append((" ".join(cur), cur_tag))
                cur = []
                cur_tag = None
            continue
        if not cur:
            cur_tag = tag
        cur.append(ln)
        if _SENT_END_RE.search(ln):
            paras.append((" ".join(cur), cur_tag))
            cur = []
            cur_tag = None
    if cur:
        paras.append((" ".join(cur), cur_tag))
    return paras


def _reconstruct_paragraphs(text: str) -> list[str]:
    """Rebuild logical paragraphs from wrapped / shredded lines.

    Jain FY2025 came through iLovePDF, which shredded it into near-per-line
    (sometimes per-word) blocks, so raw lines cannot be scored - every wrap
    would read as an orphan. Accumulate consecutive non-blank lines into one
    paragraph, breaking only on a blank line or once a line has closed a
    sentence.
    """
    return [p for p, _ in
            _reconstruct_paragraphs_tagged([(ln, None) for ln in text.split("\n")])]


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


# A paragraph that opens with an ordered-list marker - "a)", "(b)", "iv.",
# "3." - is a list item, not a splice. _reconstruct_paragraphs breaks a run-in
# list ("a) ... . b) ... . c) ...") into one paragraph per item, and every item
# after the first then "begins with a lowercase letter" - which was 80%+ of the
# flagged orphans on Jain FY2024/25 (P22). A real column-tail splice opens on a
# word ("formulation, while posing..."), never on "x)".
_LIST_MARKER_RE = re.compile(r"^\s*\(?(?:[a-z]|[ivx]{2,3}|\d{1,2})[.)]\s")


def _orphan_start(p: str) -> bool:
    """Begins mid-sentence - a lowercase letter, a comma, or a closing bracket -
    but not an ordered-list marker."""
    if _LIST_MARKER_RE.match(p):
        return False
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


def _score_paragraphs(paras: list[str]) -> tuple[int, int, list[bool], list[bool]]:
    """The orphan/dangling test, shared verbatim by order_quality (document
    level) and order_quality_by_page (PM1, physical-page level) so the two can
    never compute the test differently. Returns (orphans, danglers,
    orphan_flags, dangling_flags), the flag lists aligned index-for-index with
    `paras`."""
    total = len(paras)
    orphan_flags = [False] * total
    dangling_flags = [False] * total
    orphans = danglers = 0
    for i, p in enumerate(paras):
        prev = paras[i - 1] if i else ""
        nxt = paras[i + 1] if i + 1 < total else ""
        if i and _orphan_start(p) and (
                _SENT_END_RE.search(prev) or _looks_like_heading(prev)):
            orphan_flags[i] = True
            orphans += 1
        if (nxt and not _SENT_END_RE.search(p) and not _looks_like_heading(p)
                and _dangling_tail(p)
                and not (nxt[:1].islower() or nxt[:1].isdigit())):
            dangling_flags[i] = True
            danglers += 1
    return orphans, danglers, orphan_flags, dangling_flags


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

    orphans, danglers, _, _ = _score_paragraphs(paras)
    return {
        "orphan_start_frac": round(orphans / total, 4),
        "dangling_end_frac": round(danglers / total, 4),
        "orphan_starts": orphans,
        "dangling_ends": danglers,
        "n_paragraphs": total,
    }


# --------------------------------------------------------- PM1: per-page QC
# Everything above measures orphan_start_frac for the WHOLE MD&A span as one
# string. That document-level number can hide a single badly-scrambled page
# inside an otherwise-clean span (a 12-page span with one bad page averages to
# a small fraction). This section exposes the identical metric per physical
# PDF page, purely as diagnostic telemetry for `arpipe orderqc` - it must
# never feed grade(), build_reasons(), or any accept/reject decision, and it
# must never change what order_quality() returns for the same text.
#
# Page attribution rule: a reconstructed paragraph belongs to the physical
# page containing its first non-whitespace source line/character. Page
# provenance is threaded through paragraph reconstruction itself (each source
# line carries its page tag before reconstruction), never recovered later by
# searching offsets in the joined text - see _reconstruct_paragraphs_tagged.


def order_quality_by_page(pages: list[tuple[int, str]],
                          min_paragraphs: int = PAGE_ORPHAN_MIN_PARAGRAPHS) -> dict:
    """orphan_start_frac, computed per physical page instead of per document.

    `pages` is [(physical_page, prose_text), ...] for every page that
    contributed prose to the MD&A span, IN DOCUMENT ORDER - the same
    per-page prose strings (post furniture-strip/xy_cut/table-quarantine)
    that the caller already joins with "\\n\\n" to build the document-level
    mda_text, so this reproduces the exact same paragraph boundaries
    order_quality(mda_text) would see (see pipeline.py: `ordered` paired with
    `span_pages`). `physical_page` is caller-defined (PM1 callers pass
    1-based physical PDF page numbers); a page with an empty/blank prose
    string is dropped before scoring, same as the document-level join drops
    it via `if t.strip()`.

    Returns:
      pages               {physical_page: frac | None}. None means the page
                          was not scored: either it never appears here (no
                          prose at all - "not measured"), or it scored fewer
                          than `min_paragraphs` reconstructed paragraphs
                          ("insufficient qualifying prose" - a rate from 0 or
                          1 paragraphs is not a stable estimate, so it is
                          reported as unavailable, never a fabricated 0.0).
      n_paragraphs_total  paragraph count across all pages passed in, for
                          cross-checking against order_quality()'s own count.
      min_paragraphs      the threshold used, echoed for reproducibility.
    """
    kept = [(pg, t) for pg, t in pages if t and t.strip()]
    tagged_lines: list[tuple[str, int | None]] = []
    for i, (pg, t) in enumerate(kept):
        tagged_lines.extend((ln, pg) for ln in t.split("\n"))
        if i != len(kept) - 1:
            tagged_lines.append(("", None))     # the blank line "\n\n".join inserts
    tagged_paras = _reconstruct_paragraphs_tagged(tagged_lines)
    paras = [p for p, _ in tagged_paras]
    owners = [pg for _, pg in tagged_paras]
    total = len(paras)

    per_page: dict[int, dict[str, int]] = {pg: {"orphans": 0, "paragraphs": 0}
                                           for pg, _ in kept}
    if total >= 5:                       # same floor order_quality() uses
        _, _, orphan_flags, _ = _score_paragraphs(paras)
        for pg, flagged in zip(owners, orphan_flags):
            if pg is None:
                continue
            per_page[pg]["paragraphs"] += 1
            per_page[pg]["orphans"] += int(flagged)

    page_scores: dict[int, float | None] = {
        pg: (round(v["orphans"] / v["paragraphs"], 4)
             if v["paragraphs"] >= min_paragraphs else None)
        for pg, v in per_page.items()
    }
    return {
        "pages": page_scores,
        "n_paragraphs_total": total,
        "min_paragraphs": min_paragraphs,
    }


def pages_over_diagnostic_threshold(
        orphan_start_frac_pages: list[float | None],
        threshold: float = PAGE_ORPHAN_DIAGNOSTIC_THRESHOLD) -> list[tuple[int, float]]:
    """(physical_page, score) pairs from a page-aligned array (as stored in
    qc["orphan_start_frac_pages"], index i = physical page i+1) whose score is
    STRICTLY over `threshold`. Ascending by physical page - the array is
    already page-ordered, so this is deterministic for free. `arpipe orderqc`
    is the only intended caller; a diagnostic listing, never a gate."""
    return [(i + 1, v) for i, v in enumerate(orphan_start_frac_pages)
            if v is not None and v > threshold]


def document_hides_bad_page(
        doc_orphan_start_frac: float,
        orphan_start_frac_pages: list[float | None],
        threshold: float = PAGE_ORPHAN_DIAGNOSTIC_THRESHOLD) -> bool:
    """PM1's aggregate-hiding measure (see M1.7): true exactly when the
    document-level score reads clean (<= threshold) while at least one page
    does not - i.e. the document average hid a page-level spike. A
    descriptive count, not a quality score and not a gate; a document already
    flagged bad at the document level does not count as "hidden" here even if
    it also has bad pages."""
    return (doc_orphan_start_frac <= threshold
            and bool(pages_over_diagnostic_threshold(orphan_start_frac_pages, threshold)))


# ------------------------------------------------------------- reason codes
# P21: a `low` row with no reason is only half a row. Every non-`high` grade
# carries machine-readable codes so next month nobody has to re-diagnose why a
# document was demoted (or go back into xy_cut looking for a bug that P16B
# already fixed).

# A real MD&A closes with a cautionary / forward-looking / disclaimer
# paragraph (SEBI convention). Its absence in the last ~15 lines means the span
# stopped early - the terminator matched a body word, or the section end was
# never found. PROVISIONAL phrasing set - re-fit against the labelled 300.
_CAUTIONARY_TAIL_RE = re.compile(
    r"forward[\s-]?looking"
    r"|cautionary\s+statement"
    r"|\bdisclaimer\b"
    r"|undue\s+reliance"
    r"|\bcaution(?:s|ed|ary)?\b"
    r"|actual\s+(?:results?|outcomes?)"
    r"|statements?\s+(?:are\s+)?(?:based\s+on|subject\s+to|forward)"
    r"|beyond\s+the\s+(?:control|management)"
    r"|risks?,?\s+(?:and\s+)?concerns?", re.I)


def tail_has_cautionary(mda_text: str, n_lines: int = 15) -> bool:
    lines = [ln.strip() for ln in mda_text.splitlines() if ln.strip()]
    if not lines:
        return False
    return bool(_CAUTIONARY_TAIL_RE.search(" ".join(lines[-n_lines:])))


def _fy_weight(rep: VerificationReport) -> int | None:
    for e in rep.year_evidence:
        m = re.match(r"modal_fy:\d+:w(\d+)", e)
        if m:
            return int(m.group(1))
    return None


def build_reasons(rep: VerificationReport, qc: dict, *,
                  column_cut_fire_frac: float | None = None,
                  pdf_producer: str | None = None,
                  mda_text: str = "",
                  ocr_budget_exhausted: bool = False) -> list[str]:
    """Machine-readable codes for why a row is not `high` (or why a `high` row
    still needs an eye).

    `source_shredded` (the text layer was re-laid by a web compressor /
    converter - pair it with pdf_producer in qc) fires when EITHER:
      - the producer is a known reprocessor (P22) - the shredding is a fact
        about the source, independent of how well xy_cut reassembled it, OR
      - orphan_start_frac is over the gate AND the P16B column splitter fired
        on most digital span pages (column_cut_fire_frac >= 0.5), i.e. the
        ordering is already as good as we can make it.
    A high orphan_start_frac with the splitter idle is `order_scrambled`
    instead - the columns are still interleaved and xy_cut can do better.
    """
    reasons: list[str] = []
    if not rep.company_ok:
        reasons.append("identity_unproven")
    w = _fy_weight(rep)
    if not rep.year_ok or (w is not None and w < FY_WEIGHT_FLOOR):
        reasons.append("year_unproven")
    if qc.get("leaks"):
        reasons.append("section_leak")
    if qc.get("too_short"):
        reasons.append("too_short")
    if qc.get("too_long"):
        reasons.append("too_long")

    osf = qc.get("orphan_start_frac", 0.0)
    starts = qc.get("orphan_starts")
    over_gate = (osf > qc.get("orphan_gate_max", ORPHAN_START_FRAC_MAX)
                 and (starts is None or starts > 1))
    fired_most = (column_cut_fire_frac is not None
                  and column_cut_fire_frac >= 0.5)
    if is_reprocessor(pdf_producer) or (over_gate and fired_most):
        reasons.append("source_shredded")
    elif over_gate:
        reasons.append("order_scrambled")

    if mda_text and not tail_has_cautionary(mda_text):
        reasons.append("span_truncated")
    if ocr_budget_exhausted:
        reasons.append("ocr_budget_exhausted")
    return reasons


def grade(rep: VerificationReport, qc: dict, span_score: float,
          *, supporters: int = 0, pdf_producer: str | None = None) -> str:
    """high / medium / low.

    Method agreement IS the confidence measure (CLAUDE.md rule 4), so the
    supporter count -- how many other location methods landed on the same
    span -- is a hard gate, not a tie-breaker:

        supporters >= 2  AND span_score >= 0.80  AND no leaks   -> high
        supporters == 1  AND span_score >= 0.60  AND <=1 leak   -> medium
        supporters == 0  AND span_score >= 0.70  AND no leaks   -> medium
        supporters == 0  AND span_score <  0.70                 -> low

    Identity unproven, span too short, long-token soup, or badly scrambled
    reading order still force `low` regardless of supporters.
    """
    osf = qc.get("orphan_start_frac", 0.0)
    starts = qc.get("orphan_starts")
    is_scrambled = (osf > ORPHAN_START_FRAC_MAX) and (starts is None or starts > 1)
    is_badly_scrambled = (osf > 2 * ORPHAN_START_FRAC_MAX) and (starts is None or starts > 1)
    if (not rep.company_ok or qc["too_short"] or qc["long_token_frac"] > 0.03
            or is_badly_scrambled):     # P17: badly scrambled order
        return "low"
    verif_errors = [n for n in rep.notes if not n.startswith("mandated ratios table absent") and "disclosure finding" not in n]
    if (supporters >= GRADE_HIGH_MIN_SUPPORTERS and rep.year_ok and span_score >= GRADE_HIGH_MIN_SCORE
            and not qc["leaks"] and not verif_errors
            and not is_scrambled):       # P17: mild scramble -> medium
        # P22: a reprocessor-sourced PDF has been re-laid line by line; the span
        # can look clean and still hide a splice xy_cut could not catch. Cap it
        # at `medium` (+ source_shredded) until P11 has >= 5 such docs proving
        # the reassembly holds.
        return REPROCESSOR_CAP_GRADE if is_reprocessor(pdf_producer) else "high"
    if (supporters >= 1 and rep.year_ok and span_score >= GRADE_MEDIUM_MIN_SCORE
            and len(qc["leaks"]) <= 1):
        return "medium"
    if (supporters == 0 and rep.year_ok and span_score >= GRADE_SOLO_MIN_SCORE
            and not qc["leaks"] and not is_scrambled):
        return "medium"
    return "low"


def producer_summary(rows: list[dict]) -> dict:
    """Tally pdf_producer across manifest rows, flagging the web
    compressors / converters that shred the text layer (P22). The absolute
    reprocessor count is the number that says how much of a corpus went
    through one."""
    out: dict[str, dict] = {}
    for r in rows:
        p = (r.get("qc") or {}).get("pdf_producer") or "unknown"
        d = out.setdefault(p, {"n": 0, "reprocessor": is_reprocessor(p)})
        d["n"] += 1
    return dict(sorted(out.items(), key=lambda kv: (-kv[1]["n"], kv[0])))
