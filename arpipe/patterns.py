"""Regex/lexicon assets for Indian annual-report parsing.

Everything here is data, not logic, so it can be tuned without touching code.
Sources of the vocabulary: SEBI LODR Reg. 34(2)(e) + Schedule V Part B (MD&A),
Companies Act 2013 s.134 (Board's Report), and empirical variation observed
across FY2010-FY2025 filings on BSE/NSE.
"""
from __future__ import annotations

import re

# --------------------------------------------------------------------------
# 1. MD&A heading variants
# --------------------------------------------------------------------------
# Written as a single tolerant pattern rather than a list of literals because
# the same section is titled ~40 different ways across issuers and years.
#   "Management Discussion and Analysis"
#   "Management's Discussion & Analysis Report"
#   "Managements Discussion and Analysis of Financial Condition ..."
#   "MANAGEMENT DISCUSSION AND ANALYSIS (MD&A)"
#   "Management Discussion & Analysis Report (Annexure C to the Board's Report)"
_MD = r"Manage(?:ment|rial)(?:['’]?s)?"
_AND = r"(?:and|&|and/or|cum)"
MDA_HEADING_RE = re.compile(
    rf"{_MD}\s*[-–—:]?\s*Discussion\s*{_AND}?\s*Analysis"
    rf"(?:\s*(?:Report|Statement|Section))?",
    re.IGNORECASE,
)

# Some issuers only print the acronym in the running head / TOC.
MDA_ACRONYM_RE = re.compile(r"\bMD\s*&\s*A\b|\bMDA\b(?!\w)", re.IGNORECASE)

# Combined-section headings: MD&A folded into the Directors'/Board's Report.
MDA_COMBINED_RE = re.compile(
    rf"(?:Directors|Board)['’]?s?\s+Report\s+{_AND}\s+{_MD}\s*Discussion",
    re.IGNORECASE,
)

# Headings that reliably *terminate* an MD&A section. Ordered roughly by how
# often they follow MD&A in real reports.
MDA_TERMINATOR_PATTERNS = [
    r"Report\s+on\s+Corporate\s+Governance",
    r"Corporate\s+Governance\s+Report",
    r"Business\s+Responsibility\s*(?:and\s+Sustainability)?\s*Report",
    r"\bBRSR\s+Report\b",
    r"Independent\s+Auditor(?:'s|s'|’s|s’|s)?\s+Report",
    r"Auditor(?:'s|s'|’s|s’|s)?\s+Report",
    r"(?:Standalone|Consolidated)\s+Financial\s+Statements?",
    r"Balance\s+Sheet\s+as\s+at",
    r"Statement\s+of\s+Profit\s+(?:and|&)\s+Loss",
    r"Notice\s+of\s+(?:the\s+)?(?:\d+\w*\s+)?Annual\s+General\s+Meeting",
    r"Notice\s+of\s+(?:the\s+)?AGM\b",
    r"Directors(?:'|’)?\s+Report",
    r"Board(?:'s|’s)?\s+Report",
    # MD&A is often itself an annexure to the Board's Report. A following
    # standalone "ANNEXURE VI"/"ANNEXURE 6" heading starts the next section.
    r"\bAnnexure\s+(?:[IVXLCDM]+|\d+)\b",
    r"Annexure\s+[A-Z0-9]+\s+to\s+the\s+(?:Board|Directors)",
    r"Secretarial\s+Audit\s+Report",
    r"Shareholder(?:s)?\s+Information",
    r"General\s+Shareholder\s+Information",
    r"Consolidated\s+Accounts",
    r"Ten\s+Year\s+Financial\s+Highlights",
]
MDA_TERMINATOR_RE = re.compile("|".join(f"(?:{p})" for p in MDA_TERMINATOR_PATTERNS),
                               re.IGNORECASE)

# Kept separate because multi-column reading-order recovery can place this
# heading late in the page text. Requiring a complete standalone line avoids
# confusing prose references such as "details are given in Annexure VI" with
# a real section boundary.
ANNEXURE_HEADING_RE = re.compile(
    r"^\s*Annexure\s+(?:[IVXLCDM]+|\d+)\s*$", re.IGNORECASE | re.MULTILINE)

# --------------------------------------------------------------------------
# 2. Schedule V Part B mandated sub-headings -> used as *body* evidence.
#    Presence of >=3 of these on a page is strong evidence we are inside MD&A
#    even when the heading itself was lost to OCR.
# --------------------------------------------------------------------------
MDA_BODY_CUES = [
    r"Industry\s+Structure\s+(?:and|&)\s+Developments?",
    r"Opportunities\s+(?:and|&)\s+Threats",
    r"(?:Segment|Product)[\s\-–]*wise\s+(?:or\s+product[\s\-]*wise\s+)?[Pp]erformance",
    r"\bOutlook\b",
    r"Risks?\s+(?:and|&)\s+Concerns?",
    r"Internal\s+Control\s+Systems?\s+(?:and|&)\s+(?:their\s+)?Adequacy",
    r"Discussion\s+on\s+[Ff]inancial\s+[Pp]erformance",
    r"Material\s+[Dd]evelopments?\s+in\s+Human\s+Resources",
    r"Human\s+Resources?\s*/?\s*Industrial\s+Relations",
    r"Key\s+[Ff]inancial\s+[Rr]atios",
    r"Details\s+of\s+[Ss]ignificant\s+[Cc]hanges.{0,40}[Rr]atios",
    r"Return\s+on\s+Net\s+Worth",
    r"Cautionary\s+Statement",
    r"[Dd]ebtors?\s+[Tt]urnover",
    r"[Ii]nterest\s+[Cc]overage\s+[Rr]atio",
    r"[Oo]perating\s+[Pp]rofit\s+[Mm]argin",
]
MDA_BODY_CUE_RES = [re.compile(p) for p in MDA_BODY_CUES]

# The 8 ratios SEBI made mandatory from FY2019-20 (LODR amendment, May 2018).
# Their presence is an era signal AND an MD&A signal.
# P7: Tolerant regex patterns for singular/plural, optional "ratio" suffix,
# case, hyphen-vs-space, optional "(%)".
MANDATED_RATIO_PATTERNS = [
    r"\bdebtors?\s+turnover(?:\s+ratio)?\b",
    r"\binventor(?:y|ies)\s+turnover(?:\s+ratio)?\b",
    r"\binterest\s+coverage(?:\s+ratio)?\b",
    r"\bcurrent\s+ratio\b",
    r"\bdebt\s*(?:[-/]|to|\s+)\s*equity(?:\s+ratio)?\b",
    r"\boperating\s+profit\s+margin(?:\s*\(?%\)?|\s+ratio)?\b",
    r"\bnet\s+profit\s+margin(?:\s*\(?%\)?|\s+ratio)?\b",
    r"\breturn\s+on\s+net\s*worth\b",
]
MANDATED_RATIO_RES = [re.compile(p, re.I) for p in MANDATED_RATIO_PATTERNS]
MANDATED_RATIOS = MANDATED_RATIO_RES

# --------------------------------------------------------------------------
# 3. Identity anchors
# --------------------------------------------------------------------------
# Corporate Identity Number: L/U + 5-digit industry + 2-letter state
#   + 4-digit incorporation year + 3-letter ownership + 6-digit reg no.
CIN_RE = re.compile(
    r"\b([LU])(\d{5})([A-Z]{2})(\d{4})"
    r"(PLC|PTC|FTC|GAP|GAT|GOI|NPL|OPC|SGC|ULL|ULT|FLC|PLN)"
    r"(\d{6})\b"
)
# ISIN (ISO 6166): IN prefix + security type (E=equity, 9=DVR, F=mutual fund,
# C/D=debt) + 8 alphanumeric + 1 numeric check digit.
ISIN_RE = re.compile(r"\bIN[EF9CD][0-9A-Z]{8}[0-9]\b")


def is_valid_isin(isin: str) -> bool:
    """Validate ISO 6166 Luhn mod-10 check digit."""
    if len(isin) != 12 or not isin[:2].isalpha() or not isin[2:].isalnum():
        return False
    converted = []
    for ch in isin:
        converted.append(str(ord(ch.upper()) - 55) if ch.isalpha() else ch)
    digits = "".join(converted)
    total = 0
    for i, ch in enumerate(digits[::-1]):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


PAN_RE = re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b")

# --------------------------------------------------------------------------
# 4. Financial-year anchors
# --------------------------------------------------------------------------
# Matches: 2014-15, 2014-2015, 2014–15, FY2015, FY 14-15, F.Y. 2014-15,
#          fiscal 2015, year ended 31st March, 2015
FY_RANGE_RE = re.compile(
    r"\b(?:F\.?\s?Y\.?|FY|Financial\s+Year|Fiscal\s+Year|fiscal)?\s*"
    r"(19[89]\d|20\d{2})\s*[-–—/]\s*(\d{2}|\d{4})\b",
    re.IGNORECASE,
)
FY_SINGLE_RE = re.compile(r"\bF\.?\s?Y\.?\s?(19[89]\d|20\d{2})\b", re.IGNORECASE)
YEAR_ENDED_RE = re.compile(
    r"(?:year|period)\s+ended\s+(?:on\s+)?(?:31\s*(?:st)?|30\s*(?:th)?)?\s*"
    r"(?:st|nd|rd|th)?\s*(?:day\s+of\s+)?"
    r"(March|Mar|June|Jun|September|Sep|December|Dec)\s*,?\s*(19[89]\d|20\d{2})",
    re.IGNORECASE,
)
AS_AT_RE = re.compile(
    r"as\s+at\s+(?:31\s*(?:st)?|30\s*(?:th)?)\s*(?:st|nd|rd|th)?\s*"
    r"(March|Mar|June|Jun|September|Sep|December|Dec)\s*,?\s*(19[89]\d|20\d{2})",
    re.IGNORECASE,
)
ANNUAL_REPORT_TITLE_RE = re.compile(
    r"Annual\s+Report\s*[,:\-–]?\s*(?:for\s+(?:the\s+)?(?:F\.?Y\.?|year)?\s*)?"
    r"(19[89]\d|20\d{2})?\s*[-–—/]?\s*(\d{2}|\d{4})?",
    re.IGNORECASE,
)

# --------------------------------------------------------------------------
# 5. Junk / noise filters applied to extracted MD&A text
# --------------------------------------------------------------------------
PAGE_NUM_LINE_RE = re.compile(r"^\s*(?:page\s*)?\|?\s*\d{1,4}\s*\|?\s*$", re.IGNORECASE)
REPEATED_HEADER_MIN_PAGES = 4     # a line must recur on >=N pages to be a header
LIGATURE_FIXES = {
    "ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi",
    "ﬄ": "ffl", " ": " ", "‘": "'", "’": "'",
    "“": '"', "”": '"', "–": "-", "—": "-",
    "•": "* ", "﻿": "",
}

# Devanagari / Indic block detection for bilingual PSU reports.
DEVANAGARI_RE = re.compile(r"[ऀ-ॿ]")
INDIC_BLOCKS_RE = re.compile(
    r"[ऀ-ॿ"   # Devanagari (Hindi, Marathi)
    r"ঀ-৿"    # Bengali
    r"਀-੿"    # Gurmukhi
    r"઀-૿"    # Gujarati
    r"଀-୿"    # Oriya
    r"஀-௿"    # Tamil
    r"ఀ-౿"    # Telugu
    r"ಀ-೿"    # Kannada
    r"ഀ-ൿ]"   # Malayalam
)

# Glyphs that indicate a broken/ToUnicode-less embedded font: the page has a
# text layer but it decodes to garbage. Very common in 2010-2014 filings
# produced by old DTP software.
MOJIBAKE_RE = re.compile(r"[�\x00-\x08\x0b\x0c\x0e-\x1f]")

# --------------------------------------------------------------------------
# 6. Table / chart cell detection (P18)
# --------------------------------------------------------------------------
# Chart axis dumps and table cells arrive in the text layer as loose numbers
# ("283.68", "21,442.95 22,003.14", "9.54%"). NUMERIC_LINE_RE matches a line
# whose content is only figures, currency marks, separators and arithmetic
# punctuation - it must contain at least one digit and no run of letters.
NUMERIC_LINE_RE = re.compile(
    r"^[\s\d.,;:%()\[\]/\\+\-*x×~^'\"₹$€£¥]*\d[\s\d.,;:%()\[\]/\\+\-*x×~^'\"₹$€£¥]*$")

# Short axis / period / column labels that sit inside a chart or table block
# without themselves being numeric ("FY 18", "31st Mar", "Q3", "%", "Change").
# Used only to BRIDGE a run of numeric lines that is already anchored by a
# numeric line at both ends - never to start or extend one. Callers also cap
# the length and word count, so this stays deliberately loose.
TABLE_LABEL_RE = re.compile(
    r"^(?:FY\s?\d{2,4}(?:\s*-\s*\d{2,4})?"
    r"|\d{1,2}(?:st|nd|rd|th)?\s+[A-Z][a-z]{2,8}\.?"
    r"|Q[1-4]|H[12]|CY\s?\d{2,4}|YoY|QoQ|%"
    r"|[A-Za-z][A-Za-z&/().'’\-]*(?:[ ,][A-Za-z&/().'’\-]+){0,2}[.,]?)$")
