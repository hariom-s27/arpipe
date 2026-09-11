# Audit of Post-P25 Patterns, Regexes, Thresholds, and Heuristics

*Date: 12 September 2026*  
*Scope: Measure-only false positive audit across all 194 documents in `live_dataset/manifest.jsonl`.*  
*Status: Complete. Zero pipeline or segmentation behavior modified.*

---

## 1. Executive Summary & Audit Scope

This report presents the empirical measurement and false-positive audit of all rules, regexes, patterns, thresholds, and heuristics introduced to `arpipe/segment.py`, `arpipe/patterns.py`, and `arpipe/verify.py` since commit **P25** (`3550103`).

### Key Audit Numbers
- **Total Documents Audited:** 194
- **Total Unique Companies:** 36
- **Post-P25 Rules Evaluated:** 16 distinct rules/heuristics
- **Rules Exceeding 10% Frequency (>19 documents):** 5 rules
- **Deep Dive A (`is_cross_reference_pointer`):** 88 documents (45.4%) had heading mentions rejected (119 total rejection events). 110 events were true positive cross-reference rejections; 8 events across 2 companies (Sar Auto Products, Craftsman Automation) were **false positives** where actual MD&A section headings were rejected due to phrases like `is given below` or `as Annexure ... is given below` (plus 1 benign rejection on post-MD&A table text in Crisil FY2012).
- **Deep Dive B (`To the Members of` terminator):** Fired in 13 documents (6.7%). Exactly 1 document (**SJVN Limited FY2017**) fired within 3 pages of start (`128 - 126 = 2` pages).

---

## 2. Inventory of Post-P25 Rules & Provenance

Provenance was established using commit histories (`git log -p`) and test fixtures/comments in `arpipe/tests/test_pipeline.py`. If a rule could not be linked to a real document modeled in test mock text or comments, it is classified as `no identifiable source document`.

| # | Rule / Pattern / Heuristic | File & Line | Introduced In | Source Document / Provenance | Description / Logic |
|---|----------------------------|-------------|---------------|------------------------------|---------------------|
| 1 | `outline_validation` prose check & walk | `arpipe/segment.py:380-396, 412-446` | Commit `3550103` (P25) | KRBL Limited FY2014 (`INE001B01026`) | Target page must have >=120 words, alpha in [0.60, 0.92], and body cues. Walk forward up to 8 pages; invalidate if no prose. |
| 2 | Expanded Auditor's Report terminators | `arpipe/patterns.py:46-47` | Commit `0cc2047` (P26) | Inter State Oil Carrier FY2011 (`INE003B01014`) | Added punctuation/spelling variants `(?:'s\|s'\|’s\|s’\|s)?` to `Independent Auditor's Report` and `Auditor's Report`. |
| 3 | Ten Year Financial Summary terminators | `arpipe/patterns.py:65-66` | Commit `a3d00f2` (P27) | SAIL FY2011 (`INE114A01011`) | Added `Ten Years?(?:'s\|'s)?\s+(?:at a glance\|Financial Highlights\|Summary)` and `Ten Year Financial Highlights`. |
| 4 | `MDA_POINTER_PATTERNS` / `MDA_POINTER_RE` | `arpipe/patterns.py:73-85` | Commit `a3d00f2` (P27), expanded P28/5e536a9/12fa58a | SAIL FY2011 (`INE114A01011`), CEAT Limited (`INE482A01020`) | Patterns matching cross-reference pointer phrases (e.g. `forms part of`, `is enclosed`, `separately given`, `is given`). |
| 5 | `is_cross_reference_pointer` heuristic | `arpipe/segment.py:180-221` | Commit `a3d00f2` (P27), modified P28/5e536a9 | SAIL FY2011, Modern Steels FY2013 (`INE001F01019`) | Rejects candidate heading if heading text or following 80-word snippet contains `MDA_POINTER_RE`. |
| 6 | Multi-line heading concatenation | `arpipe/segment.py:694-707, 882-885` | Commit `a3d00f2` (P27), refined P28 | SAIL FY2011 (`INE114A01011`) | Combines two consecutive lines/headings if first is bold/large and vertical gap <= 0.10, matching `_is_mda_title`. |
| 7 | `refine_end` terminator short-circuit | `arpipe/segment.py:933-934` | Commit `a3d00f2` (P27) | no identifiable source document | Early return `if span.terminator_match is not None: return span` to prevent unnecessary refinement walk. |
| 8 | `trim_span` cross-reference pointer check | `arpipe/segment.py:986` | Commit `a3d00f2` (P27) | SAIL FY2011 (`INE114A01011`) | Checks `not is_cross_reference_pointer(t, heading_window)` when scanning forward window during trim. |
| 9 | Plural `Discussions` in heading regexes | `arpipe/patterns.py:25, 35` | Commit `a1fb57f` (P28) | Modern Steels Limited FY2013 (`INE001F01019`) | Matches `Discussions?` in `MDA_HEADING_RE` and `MDA_COMBINED_RE`. |
| 10 | Case-insensitive `MDA_BODY_CUE_RES` | `arpipe/patterns.py:111` | Commit `a1fb57f` (P28) | Modern Steels Limited FY2013 (`INE001F01019`) | Added `re.IGNORECASE` to Schedule V body cue patterns. |
| 11 | Mid-page terminator inclusion `_terminator_end_page` | `arpipe/segment.py:747-763` | Commit `a1fb57f` (P28) | Modern Steels Limited FY2013 (`INE001F01019`) | Includes terminator page in MD&A span if `(line_idx >= 5 or y_frac >= 0.35)` and `body_score >= 0.25`. |
| 12 | Orphan starts gate (`starts is None or starts > 1`) | `arpipe/verify.py:654, 687-689` | Commit `19d5e6e` (P29) | no identifiable source document | Prevents a single orphan sentence start from classifying a document as scrambled reading order. |
| 13 | `Report on Financial Statements` terminator | `arpipe/patterns.py:63` | Commit `5e536a9` | no identifiable source document | Added `Report\s+on\s+the\s+(?:Standalone\s+\|Consolidated\s+)?Financial\s+Statements?`. |
| 14 | Umbrella running-header suppression | `arpipe/segment.py:314-328, 355-358` | Commit `5e536a9` | HDFC Bank Limited FY2012 (`INE040A01034`) | Extracts top lines of start page (`_extract_start_headers`); ignores matching top-band terminators on later pages. |
| 15 | `To the Members of` terminator pattern | `arpipe/patterns.py:48` | Commit `12fa58a` (and `5e536a9`) | HDFC Bank Limited FY2012 (`INE040A01034`) | Matches statutory auditor report opening line `To\s+the\s+Members\s+of`. |
| 16 | TOC page suppression in `from_headings` | `arpipe/segment.py:686-688` | Commit `12fa58a` | no identifiable source document | Skips candidate heading extraction on pages where `>= 3` lines match `MDA_TERMINATOR_RE`. |

---

## 3. Corpus-Wide Measurement Results (194 Documents)

Each rule was measured across all 194 documents in `live_dataset/manifest.jsonl`. Rules firing on more than 10% (>19 documents) are flagged.

| Rule / Pattern / Heuristic | Docs Fired | % of Corpus | >10% Flag (>19 Docs) | Unique Companies | Company IDs |
|----------------------------|------------|-------------|----------------------|------------------|-------------|
| outline_validation (all evaluated) | 12 | 6.2% | No | 6 | INE001B01026, INE009A01021, INE044A01036, INE226A01021, INE482A01020 (+1 more) |
| outline_validation: walked forward > 0 | 4 | 2.1% | No | 4 | INE001B01026, INE044A01036, INE226A01021, INE797F01020 |
| outline_validation: invalidated | 0 | 0.0% | No | 0 | None |
| auditor_expansion_p26 (P26 spelling variants only) | 6 | 3.1% | No | 5 | INE003B01014, INE004C01028, INE005E01013, INE006C01015, INE006I01046 |
| ten_year_summary_p27 (Ten Years at a glance) | 0 | 0.0% | No | 0 | None |
| is_cross_reference_pointer (rejected mentions) | 88 | 45.4% | **FLAG (>10%)** | 27 | INE001B01026, INE001F01019, INE001O01029, INE002A01018, INE002B01016 (+22 more) |
| multiline_headings (concatenated heading matches) | 42 | 21.6% | **FLAG (>10%)** | 18 | INE001B01026, INE001F01019, INE001O01029, INE002A01018, INE005E01013 (+13 more) |
| refine_end_short_circuit (terminator present) | 0 | 0.0% | No | 0 | None |
| trim_span_pointer_rejections | 0 | 0.0% | No | 0 | None |
| plural_discussions_p28 ('Discussions' match) | 12 | 6.2% | No | 4 | INE001F01019, INE002B01016, INE005E01013, INE040A01034 |
| case_insensitive_cues_p28 (case-insensitive cue hits) | 159 | 82.0% | **FLAG (>10%)** | 35 | INE001B01026, INE001F01019, INE001O01029, INE002A01018, INE002B01016 (+30 more) |
| midpage_terminator_inclusion_p28 (end page included) | 20 | 10.3% | **FLAG (>10%)** | 10 | INE001F01019, INE002S01010, INE004E01016, INE005E01013, INE006C01015 (+5 more) |
| orphan_starts_gate_p29 (single orphan start protected) | 3 | 1.5% | No | 3 | INE001F01019, INE002E01010, INE003B01014 |
| report_on_fin_statements (terminator match) | 0 | 0.0% | No | 0 | None |
| umbrella_running_header_suppression | 4 | 2.1% | No | 1 | INE040A01034 |
| to_members_terminator ('To the Members of' match) | 13 | 6.7% | No | 7 | INE002L01015, INE007A01025, INE040A01034, INE081A01020, INE171A01029 (+2 more) |
| to_members_within_3_pages (fired within 3 pages of start) | 1 | 0.5% | No | 1 | INE002L01015 |
| toc_page_suppression (TOC page heading suppressed) | 83 | 42.8% | **FLAG (>10%)** | 32 | INE001B01026, INE001F01019, INE001O01029, INE002A01018, INE002B01016 (+27 more) |

---

## 4. Deep Dive A: `is_cross_reference_pointer`

### Summary Statistics
- **Total Documents where rule fired:** 88 / 194 (45.4%) — **FLAGGED (>10%)**
- **Total Rejection Events Logged:** 119
- **Unique Companies:** 27 companies
- **True Positives (Genuine Cross-Reference Pointers in Directors' Report):** 110 events
- **False Positives (Actual MD&A Headings Erroneously Rejected):** 8 events across 2 companies (Sar Auto Products Limited and Craftsman Automation Limited) where genuine MD&A section headings were rejected due to preamble phrases matching `is given below` (plus 1 benign candidate rejection on post-MD&A table text in Crisil FY2012).

### Mechanism of False Positive Rejections
The heuristic `is_cross_reference_pointer` searches the candidate heading text and the following 80 words for any occurrence of `MDA_POINTER_RE`. In Indian annual reports, companies frequently begin their genuine MD&A section with formal regulatory preamble clauses such as:
- *"Pursuant to Regulation 34(2)(e) of SEBI LODR Regulations 2015, a Management Discussion and Analysis report **is given below**:- [Section Body]"*
- *"ANNEXURE - 1 / Management Discussion and Analysis: Pursuant to Schedule V ... a Management Discussion and Analysis Report ... **is given below**:"*

Because `MDA_POINTER_RE` includes `(?:is|are)\s+(?:enclosed|attached|annexed|given|presented|provided)`, matching `is given` without requiring that the text refer elsewhere, it triggers on `is given below` and rejects the actual heading on the genuine section start page.

### Detailed Inventory of False Positive Events

| Document | Page | Span Start | Method | Heading Text | Matched Pattern | Impact / Drift |
|----------|------|------------|--------|--------------|-----------------|----------------|
| Sar Auto Products FY2013 (`INE002E01010`) | 8 | 8 | `body_score+refined+trimmed` | `MANAGEMENT DISCUSSION AND ANALYSIS REPORT` | `is given` | `from_headings` suppressed; recovered via body score |
| Sar Auto Products FY2013 (`INE002E01010`) | 8 | 8 | `body_score+refined+trimmed` | `Pursuant to Clause 49... MD&A report is` | `is given` | `from_text_headings` suppressed |
| Sar Auto Products FY2017 (`INE002E01010`) | 9 | 9 | `body_score+refined+trimmed` | `MANAGEMENT DISCUSSION AND ANALYSIS REPORT` | `is given` | `from_headings` suppressed; recovered via body score |
| Sar Auto Products FY2018 (`INE002E01010`) | 9 | **12** | `body_score+refined+trimmed` | `MANAGEMENT DISCUSSION AND ANALYSIS REPORT` | `is given` | **Section Truncation: Heading on p.9 rejected; `body_score` started at p.12, truncating first 3 pages!** |
| Sar Auto Products FY2024 (`INE002E01010`) | 40 | 40 | `body_score+refined+trimmed` | `MANAGEMENT DISCUSSION AND ANALYSIS REPORT` | `is given` | `from_headings` suppressed; recovered via body score |
| Sar Auto Products FY2025 (`INE002E01010`) | 38 | 38 | `body_score+refined+trimmed` | `MANAGEMENT DISCUSSION AND ANALYSIS REPORT` | `is given` | `from_headings` suppressed; recovered via body score |
| Craftsman Automation FY2024 (`INE00LO01017`) | 27 | 27 | `body_score+refined+trimmed` | `Management Discussion and Analysis:` (Annexure - 1) | `is given` | `from_headings` suppressed; recovered via body score |
| Craftsman Automation FY2025 (`INE00LO01017`) | 16 | **15** | `body_score+refined+trimmed` | `MANAGEMENT DISCUSSION AND ANALYSIS` (Annexure - 1) | `is given` | **Boundary Drift: Real heading on p.16 rejected; `body_score` started on p.15 (Directors' Report)!** |
| Modern Steels Limited FY2012 (`INE001F01019`) | 5 | 5 | `heading+trimmed` | `Management Discussions & Analysis is attached` | `is attached` | Secondary heading candidate on p.5 rejected |

### Complete List of True Positive Rejections (110 Events)
In the remaining 110 events, `is_cross_reference_pointer` functioned as intended, correctly rejecting mentions of MD&A embedded within Directors' Reports where the actual MD&A section was located elsewhere in the document:
- **Modern Steels Limited (`INE001F01019`):** FY2012 p.5, FY2013 p.9, FY2017 p.3, FY2025 p.14 (mentions like *"a separate report on MD&A is attached herewith"* in Directors' Report).
- **Page Industries Limited (`INE761H01022`):** FY2012 p.18 (start=24), FY2013 p.24 (start=30), FY2017 p.15,18 (start=44), FY2018 p.18 (start=48), FY2024 p.31 (start=88), FY2025 p.30 (start=88). All rejected mentions in Directors' Report prior to the separate MD&A section.
- **Jubilant Foodworks Limited (`INE797F01020`):** FY2012 p.33 (start=23), FY2013 p.35 (start=25), FY2017 p.35 (start=23), FY2018 p.36 (start=23), FY2025 p.42 (start=33). All mentions in Directors' Report referring back to earlier MD&A section.
- **CEAT Limited (`INE482A01020`):** FY2017 p.83 (start=30), FY2024 p.52 (start=40), FY2025 p.49 (start=38).
- **Welspun Living Limited (`INE192B01031`):** FY2012 p.28 (start=34), FY2013 p.19 (start=26), FY2017 p.63 (start=33).
- **PVR INOX Limited (`INE191H01014`):** FY2012 p.4,16 (start=9), FY2013 p.5,18 (start=10), FY2017 p.30, FY2018 p.77, FY2024 p.54, FY2025 p.59.
- **Tata Steel Limited (`INE081A01020`):** FY2018 p.77 (start=88).
- **Sun Pharmaceutical Industries Limited (`INE044A01036`):** FY2012 p.31, FY2013 p.35, FY2017 p.38, FY2018 p.30, FY2024 p.40.
- **The Federal Bank Limited (`INE171A01029`):** FY2017 p.23 (start=49), FY2018 p.23 (start=49), FY2024 p.93 (start=106).
- **Tata Communications Limited (`INE151A01013`):** FY2018 p.20 (start=32).
- **Infosys Limited (`INE009A01021`):** FY2012 p.83 (start=87).
- **Astral Limited (`INE006I01046`):** FY2012 p.20 (start=24).

---

## 5. Deep Dive B: `"To the Members of"` Terminator

### Summary Statistics
- **Total Documents where rule fired:** 13 / 194 (6.7%)
- **Unique Companies:** 7 companies (`INE002L01015`, `INE007A01025`, `INE040A01034`, `INE081A01020`, `INE171A01029`, `INE191H01014`, `INE482A01020`)
- **Documents Fired <= 3 Pages of Start:** **1 document** (SJVN Limited FY2017)

### All 13 Documents Where `"To the Members of"` Fired

| Document | Start Page | Terminator Page | Page Distance | Safety Flag (<= 3 Pages) | Terminator Verbatim Text |
|----------|------------|-----------------|---------------|--------------------------|--------------------------|
| INE002L01015 FY2017 (SJVN Limited) | 126 | 128 | 2 | **FLAGGED (<= 3 pages)** | `TO THE MEMBERS OF` |
| INE007A01025 FY2017 (Crisil Limited) | 88 | 100 | 12 | OK (> 3 pages) | `To the Members of CRISIL Limited` |
| INE007A01025 FY2018 (Crisil Limited) | 70 | 82 | 12 | OK (> 3 pages) | `To the members of CRISIL Limited` |
| INE007A01025 FY2024 (Crisil Limited) | 64 | 75 | 11 | OK (> 3 pages) | `To the Members of Crisil Limited` |
| INE007A01025 FY2025 (Crisil Limited) | 100 | 111 | 11 | OK (> 3 pages) | `To the Members of Crisil Limited` |
| INE040A01034 FY2012 (HDFC Bank Limited) | 17 | 30 | 13 | OK (> 3 pages) | `To the Members of HDFC Bank Limited` |
| INE081A01020 FY2012 (Tata Steel Limited) | 88 | 133 | 45 | OK (> 3 pages) | `To the Members of` |
| INE081A01020 FY2013 (Tata Steel Limited) | 56 | 101 | 45 | OK (> 3 pages) | `To the Members of` |
| INE171A01029 FY2017 (The Federal Bank  Limited) | 49 | 92 | 43 | OK (> 3 pages) | `To The Members of` |
| INE171A01029 FY2018 (The Federal Bank  Limited) | 49 | 92 | 43 | OK (> 3 pages) | `To The Members of` |
| INE191H01014 FY2012 (PVR INOX Limited) | 9 | 21 | 12 | OK (> 3 pages) | `To the Members of PVR Limited` |
| INE191H01014 FY2013 (PVR INOX Limited) | 10 | 24 | 14 | OK (> 3 pages) | `To the Members of PVR Limited` |
| INE482A01020 FY2012 (CEAT Limited) | 35 | 55 | 20 | OK (> 3 pages) | `To The Members of` |

### Inspection of the Flagged Document: SJVN Limited FY2017 (`INE002L01015`)
- **Start Page:** 126 (`heading+trimmed`, heading: `MANAGEMENT DISCUSSION AND ANALYSIS`)
- **End Page:** 127
- **Terminator Page:** 128 (line 2: `TO THE MEMBERS OF / SJVN THERMAL PRIVATE LIMITED`)
- **Page Distance:** 2 pages (`128 - 126 = 2 <= 3`)
- **Document Context:** Page 126 contains `Annexure – I / MANAGEMENT DISCUSSION AND ANALYSIS / INDUSTRY OVERVIEW` for SJVN's wholly owned subsidiary (SJVN Thermal Private Limited). The section spans exactly pages 126-127. Page 128 immediately begins the subsidiary's Independent Auditor's Report (`TO THE MEMBERS OF SJVN THERMAL PRIVATE LIMITED`).
- **Finding:** While the terminator correctly identified the true boundary of this 2-page subsidiary section, the section length of 2 pages triggers the safety audit threshold.

---

## 6. Analysis of Rules Exceeding 10% Frequency Threshold

Five rules fired on more than 10% (>19) of the 194 documents:

### 1. `case_insensitive_cues_p28` — 159 Documents (82.0%)
- **Location:** `arpipe/patterns.py:111`
- **Detail:** `MDA_BODY_CUE_RES = [re.compile(p, re.IGNORECASE) for p in MDA_BODY_CUES]`
- **Observation:** Fired across 35 of 36 companies. Real annual reports frequently use title case (`Industry Structure and Developments`), all caps (`INDUSTRY STRUCTURE AND DEVELOPMENTS`), or sentence case (`Industry structure and developments`). Case insensitivity matches legitimate formatting variations across issuers.

### 2. `is_cross_reference_pointer` — 88 Documents (45.4%)
- **Location:** `arpipe/segment.py:180-221`
- **Detail:** Fired on 88 documents across 27 companies.
- **Observation:** While successfully eliminating 110 false start candidates in Directors' Reports, it caused 9 false positive rejections of genuine MD&A section starts that contained `is given below` or `as Annexure ... is given below`.

### 3. `toc_page_suppression` in `from_headings` — 83 Documents (42.8%)
- **Location:** `arpipe/segment.py:686-688`
- **Detail:** `if sum(1 for l in page_lines if MDA_TERMINATOR_RE.search(l)) >= 3: continue`
- **Observation:** Suppressed candidate heading extraction on Table of Contents pages containing multiple section titles across 32 companies.

### 4. `multiline_headings` Concatenation — 42 Documents (21.6%)
- **Location:** `arpipe/segment.py:694-707, 882-885`
- **Detail:** Combines two consecutive lines/headings if vertical gap <= 0.10.
- **Observation:** Fired across 18 companies where designed typography splits `Management Discussion` and `and Analysis Report` across separate text boxes or lines.

### 5. `midpage_terminator_inclusion_p28` — 20 Documents (10.3%)
- **Location:** `arpipe/segment.py:747-763` (`_terminator_end_page`)
- **Detail:** `if (line_idx >= 5 or y_frac >= 0.35) and page_body_score(page_text) >= 0.25: return max(start, page_no)`
- **Observation:** Included the terminator page in the MD&A span for 20 documents across 10 companies where the section concluded mid-page followed by a subsequent annexure or report on the lower half of the page.

---

## 7. Audit Conclusion

All post-P25 patterns, regexes, thresholds, and heuristics have been measured against the complete live corpus of 194 documents without modifying any pipeline or segmentation behavior.
