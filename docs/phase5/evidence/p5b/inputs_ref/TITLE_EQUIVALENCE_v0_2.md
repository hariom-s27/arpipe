# TITLE_EQUIVALENCE_v0_2.md
## Empirical Structural Heading Taxonomy & MD&A Equivalence Reference

> **Mandatory Protocol Disclaimers:**
> - "This list classifies titles only. Presence, boundaries, states and reason codes follow the Gold protocol."
> - "Produced without access to the ARPipe repository or its heading patterns."
> - "Produced by an isolated AI-assisted reading, combining PDF text extraction and contact-sheet viewing, of the 60 FIT DEVELOPMENT documents, without access to the ARPipe repository or its heading patterns; classes assigned by a rule script; pending independent human spot-verification."
> - *Status*: Working empirical taxonomy (v0.2). This document is NOT definitive and is subject to formal independent human spot-verification.

---

### 1. Purpose and Scope

This document classifies structural heading strings observed across the 60 FIT Development corporate annual reports. Its sole purpose is to document the empirical equivalence of observed headings to the statutory Management Discussion and Analysis (MD&A) section.

In accordance with Section Q of protocol P5-B.2:
- All annotation procedural instructions, decision trees, and commands directing annotators to modify evidence files have been removed.
- Invented annotation labels (e.g. sub-class tags) have been eliminated; all headings are strictly assigned to the four empirical classes.
- Every title listed in this document is mechanically derived from `TITLE_EVIDENCE_LEDGER_v0_2.csv` under declared normalization and is accompanied by exact document, TOC, and BODY counts.
- No assumptions regarding company sector, banking regulation, or statutory interpretation are made; conditional classifications state only observable structural context.

---

### 2. Four-Class Classification Taxonomy

Every heading observed in an annual report is assigned to exactly one of four empirical classes:
1. **EQUIVALENT**: Titles that directly and unambiguously denote the Management Discussion and Analysis section (as a standalone section body opener or direct Table of Contents entry).
2. **CONDITIONAL**: Titles that denote MD&A only under specific, verifiable structural conditions or contextual arrangements (e.g. embedded subsections inside the Directors’ Report, cross-reference notices, or combined section headings).
3. **NOT EQUIVALENT BUT CONFUSABLE**: Titles that appear similar or cover related operational and financial topics, but are legally, structurally, or semantically distinct from MD&A.
4. **UNRESOLVED**: Exceptional cases where document-level frame anomalies prevent determination.

---

### 3. Canonical Heading Inventory

#### 3.1 EQUIVALENT Headings (Direct MD&A Openers & TOC Entries)

Titles that directly and unambiguously denote the Management Discussion and Analysis section (either as the top-level section body opening heading, or as a direct Table of Contents entry pointing to the substantive section).

##### Standard Forms (English)

- `Management Discussion and Analysis`
  - **Class**: EQUIVALENT | **Docs**: 31 | **TOC**: 56 | **BODY**: 16 | Notes: Annexure prefixes observed: ANNEXURE - 1, ANNEXURE 2, Annexure - B
  - **Context**: Standard title; primary standalone section opener and TOC entry.
- `Management Discussion & Analysis`
  - **Class**: EQUIVALENT | **Docs**: 31 | **TOC**: 56 | **BODY**: 16
  - **Context**: Ampersand variant; standalone section opener and TOC entry.
- `MANAGEMENT DISCUSSION AND ANALYSIS`
  - **Class**: EQUIVALENT | **Docs**: 31 | **TOC**: 56 | **BODY**: 16 | Notes: Annexure prefixes observed: ANNEXURE 1
  - **Context**: All-caps standard title; standalone section opener and TOC entry.
- `MANAGEMENT DISCUSSION & ANALYSIS`
  - **Class**: EQUIVALENT | **Docs**: 31 | **TOC**: 56 | **BODY**: 16 | Notes: Annexure prefixes observed: Annexure - B
  - **Context**: All-caps ampersand variant; standalone section opener and TOC entry.
- `Management Discussion and Analysis Report`
  - **Class**: EQUIVALENT | **Docs**: 23 | **TOC**: 28 | **BODY**: 23 | Notes: Annexure prefixes observed: Annexure to the Directors’ Report
  - **Context**: Standard title with Report suffix; standalone section opener and TOC entry.
- `MANAGEMENT DISCUSSION AND ANALYSIS REPORT`
  - **Class**: EQUIVALENT | **Docs**: 23 | **TOC**: 28 | **BODY**: 23 | Notes: Annexure prefixes observed: ANNEXURE TO THE DIRECTORS' REPORT
  - **Context**: All-caps title with Report suffix; standalone section opener and TOC entry.
- `MANAGEMENT DISCUSSION AND ANALYSIS REPORT:`
  - **Class**: EQUIVALENT | **Docs**: 4 | **TOC**: 4 | **BODY**: 2
  - **Context**: All-caps title with Report suffix and trailing colon; standalone body opener.

##### Possessive Forms

- `Management's Discussion and Analysis`
  - **Class**: EQUIVALENT | **Docs**: 2 | **TOC**: 4 | **BODY**: 0
  - **Context**: Possessive form (straight quote); standalone section opener and TOC entry.
- `Management’s Discussion and Analysis`
  - **Class**: EQUIVALENT | **Docs**: 2 | **TOC**: 4 | **BODY**: 0
  - **Context**: Possessive form (curly quote); standalone section opener and TOC entry.
- `MANAGEMENT'S DISCUSSION AND ANALYSIS`
  - **Class**: EQUIVALENT | **Docs**: 2 | **TOC**: 4 | **BODY**: 0
  - **Context**: All-caps possessive form (straight quote); standalone section opener.
- `MANAGEMENT’S DISCUSSION AND ANALYSIS`
  - **Class**: EQUIVALENT | **Docs**: 2 | **TOC**: 4 | **BODY**: 0
  - **Context**: All-caps possessive form (curly quote); standalone section opener.
- `Management’s Discussion and Analysis Report`
  - **Class**: EQUIVALENT | **Docs**: 5 | **TOC**: 9 | **BODY**: 3 | Notes: Annexure prefixes observed: Annexure II
  - **Context**: Possessive form with Report suffix; standalone section opener.
- `MANAGEMENT'S DISCUSSION AND ANALYSIS REPORT`
  - **Class**: EQUIVALENT | **Docs**: 5 | **TOC**: 9 | **BODY**: 3
  - **Context**: All-caps possessive form with Report suffix; standalone section opener.

##### Plural Forms

- `MANAGEMENT DISCUSSIONS AND ANALYSIS`
  - **Class**: EQUIVALENT | **Docs**: 4 | **TOC**: 1 | **BODY**: 4
  - **Context**: Plural Discussions; standalone body opening heading.
- `MANAGEMENT DISCUSSIONS & ANALYSIS`
  - **Class**: EQUIVALENT | **Docs**: 4 | **TOC**: 1 | **BODY**: 4
  - **Context**: Plural Discussions with ampersand; standalone body opening heading.
- `MANAGEMENT DISCUSSIONS AND ANALYSIS REPORT`
  - **Class**: EQUIVALENT | **Docs**: 1 | **TOC**: 0 | **BODY**: 1
  - **Context**: Plural Discussions with Report suffix; standalone body opening heading.

##### Year-Suffixed Variants

- `Management Discussion and Analysis 2011-12`
  - **Class**: EQUIVALENT | **Docs**: 1 | **TOC**: 1 | **BODY**: 0
  - **Context**: Standalone TOC entry incorporating financial year.
- `Management Discussion and Analysis 2012-13`
  - **Class**: EQUIVALENT | **Docs**: 1 | **TOC**: 1 | **BODY**: 0
  - **Context**: Standalone TOC entry incorporating financial year.
- `Management Discussion and Analysis 2023-24`
  - **Class**: EQUIVALENT | **Docs**: 1 | **TOC**: 0 | **BODY**: 1 | Notes: Annexure prefixes observed: ANNEXURE 1
  - **Context**: Standalone body opener incorporating financial year.
- `Management Discussion and Analysis 2024-25`
  - **Class**: EQUIVALENT | **Docs**: 1 | **TOC**: 0 | **BODY**: 1 | Notes: Annexure prefixes observed: ANNEXURE 1
  - **Context**: Standalone body opener incorporating financial year.

##### Bilingual & Non-English Equivalents

- `प्रबंध विवेचना एवं विश्लेषण`
  - **Class**: EQUIVALENT | **Docs**: 2 | **TOC**: 5 | **BODY**: 0
  - **Context**: Standard Unicode Devanagari script; primary section opener and TOC entry in bilingual reports.

#### 3.2 CONDITIONAL Headings (Context-Dependent MD&A)

Titles that denote MD&A only under specific, verifiable structural conditions or contextual arrangements. Stated strictly with observable structural context.

##### Condition A: Substantive MD&A Subsection Embedded within Directors’ Report

- `Management Discussion and Analysis`
  - **Class**: CONDITIONAL | **Docs**: 31 | **TOC**: 56 | **BODY**: 16
  - **Context**: Observable context: Heading appears as an embedded major subsection within the Directors’ Report; contains multi-page operational and financial review where no standalone MD&A section exists.
- `MANAGEMENT DISCUSSION AND ANALYSIS`
  - **Class**: CONDITIONAL | **Docs**: 31 | **TOC**: 56 | **BODY**: 16
  - **Context**: Observable context: All-caps heading appears as an embedded major subsection within the Directors’ Report.
- `MANAGEMENT'S DISCUSSIONS AND ANALYSIS`
  - **Class**: CONDITIONAL | **Docs**: 2 | **TOC**: 1 | **BODY**: 2
  - **Context**: Observable context: Possessive plural heading appears as an embedded major content-bearing subsection within the Directors’ Report.

##### Condition B: Directors’ Report Cross-Reference Subsections

- `5. Management Discussion and Analysis`
  - **Class**: CONDITIONAL | **Docs**: 31 | **TOC**: 56 | **BODY**: 16
  - **Context**: Observable context: Numbered subsection heading within Directors’ Report followed immediately by a short referral sentence pointing to Annexure 2.
- `34. Management Discussion and Analysis Report`
  - **Class**: CONDITIONAL | **Docs**: 23 | **TOC**: 28 | **BODY**: 23
  - **Context**: Observable context: Numbered subsection heading within Board’s Report containing a single referral sentence pointing to separate section.
- `21. Management Discussion and Analysis Report:`
  - **Class**: CONDITIONAL | **Docs**: 4 | **TOC**: 4 | **BODY**: 2
  - **Context**: Observable context: Numbered subsection heading with trailing colon within Directors’ Report pointing to separate section.
- `17. MANAGEMENT DISCUSSION AND ANALYSIS REPORT:`
  - **Class**: CONDITIONAL | **Docs**: 4 | **TOC**: 4 | **BODY**: 2
  - **Context**: Observable context: Numbered all-caps subsection heading with trailing colon within Directors’ Report pointing to separate section.
- `J. MANAGEMENT'S DISCUSSION AND ANALYSIS REPORT`
  - **Class**: CONDITIONAL | **Docs**: 5 | **TOC**: 9 | **BODY**: 3
  - **Context**: Observable context: Lettered all-caps subsection heading within Directors’ Report containing statutory cross-reference statement.
- `Management Discussion and Analysis Report`
  - **Class**: CONDITIONAL | **Docs**: 23 | **TOC**: 28 | **BODY**: 23
  - **Context**: Observable context: Subsection heading within Directors’ Report or Board’s Report containing referral sentence to separate annexure.

##### Condition C: Combined Section Headings

- `CORPORATE GOVERNANCE AND MANAGEMENT DISCUSSIONS & ANALYSIS`
  - **Class**: CONDITIONAL | **Docs**: 5 | **TOC**: 0 | **BODY**: 8
  - **Context**: Observable context: Joint heading combining Corporate Governance and MD&A in Directors’ Report.
- `Management Discussion & Analysis Report (MD&A Report) –`
  - **Class**: CONDITIONAL | **Docs**: 2 | **TOC**: 4 | **BODY**: 0
  - **Context**: Observable context: Cross-reference subsection heading within Corporate Governance Report.

##### Condition D: Observed Alternative Opening Title

- `Business Environment`
  - **Class**: CONDITIONAL | **Docs**: 2 | **TOC**: 4 | **BODY**: 0
  - **Context**: Observable context: Appears as the top-level opening chapter heading of the operational review section where the section opens directly under Business Environment without a preceding Management Discussion and Analysis heading.

#### 3.3 NOT EQUIVALENT BUT CONFUSABLE Headings (Negative Controls)

Structural headings observed in the development documents that cover operational, governance, or financial matters but are legally, structurally, or semantically distinct from MD&A. Documented with empirical counts.

##### Category 1: Directors’ Report / Board’s Report

- `Directors' Report`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 43 | **TOC**: 59 | **BODY**: 30
  - **Context**: Statutory report by the Board of Directors; independent corporate instrument distinct from MD&A.
- `DIRECTORS' REPORT`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 43 | **TOC**: 59 | **BODY**: 30
  - **Context**: All-caps statutory report heading.
- `Board’s Report`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 11 | **TOC**: 19 | **BODY**: 6
  - **Context**: Statutory report by the Board; distinct from MD&A.
- `BOARD’S REPORT`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 11 | **TOC**: 19 | **BODY**: 6
  - **Context**: All-caps statutory report heading.

##### Category 2: Corporate Governance Report

- `Corporate Governance Report`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 30 | **TOC**: 37 | **BODY**: 24
  - **Context**: Statutory narrative section on board composition, committees, and compliance.
- `Report on Corporate Governance`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 16 | **TOC**: 28 | **BODY**: 7
  - **Context**: Statutory corporate governance section heading.
- `CORPORATE GOVERNANCE REPORT`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 30 | **TOC**: 37 | **BODY**: 24
  - **Context**: All-caps corporate governance section heading.
- `Auditors’ Certificate on Corporate Governance`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 8 | **TOC**: 8 | **BODY**: 3
  - **Context**: Auditor compliance certification; distinct from MD&A.

##### Category 3: Business Responsibility & Sustainability Reporting

- `Business Responsibility Report`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 7 | **TOC**: 15 | **BODY**: 3
  - **Context**: Statutory ESG / sustainability narrative distinct from MD&A.
- `Business Responsibility and Sustainability Report`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 13 | **TOC**: 22 | **BODY**: 7
  - **Context**: Statutory ESG report (BRSR).

##### Category 4: Executive Statements & Corporate Overview

- `Chairman’s Statement`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 4 | **TOC**: 7 | **BODY**: 0
  - **Context**: Executive communication in front matter; voluntary narrative.
- `Message from the Chairman`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 4 | **TOC**: 5 | **BODY**: 2
  - **Context**: Executive address in corporate overview.
- `Managing Director & CEO’s Message`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 1 | **TOC**: 1 | **BODY**: 0
  - **Context**: Executive address; distinct from statutory MD&A.
- `Message from MD & CEO`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 1 | **TOC**: 1 | **BODY**: 0
  - **Context**: Executive communication.
- `Corporate Overview`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 7 | **TOC**: 7 | **BODY**: 0
  - **Context**: Introductory corporate profile in front matter.
- `Business Model`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 2 | **TOC**: 2 | **BODY**: 1
  - **Context**: Strategic overview presentation.
- `Value Creation`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 1 | **TOC**: 1 | **BODY**: 1
  - **Context**: Integrated reporting narrative.
- `Performance Highlights`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 7 | **TOC**: 6 | **BODY**: 4
  - **Context**: Summary financial and operational metrics in front matter.
- `Key Performance Indicators`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 4 | **TOC**: 4 | **BODY**: 2
  - **Context**: Executive summary dashboard.

##### Category 5: MD&A Internal Subsections (Subordinate Components)

- `Global Economy`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 3 | **TOC**: 1 | **BODY**: 2
  - **Context**: Subordinate subsection topic within operational review; not a section boundary.
- `Indian Economy`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 2 | **TOC**: 1 | **BODY**: 1
  - **Context**: Subordinate macroeconomic subsection within MD&A.
- `Macroeconomic and Industry Development`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 1 | **TOC**: 0 | **BODY**: 1
  - **Context**: Subordinate macroeconomic review subsection.
- `Opportunities`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 2 | **TOC**: 0 | **BODY**: 4
  - **Context**: Subordinate review topic inside MD&A.
- `Threats`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 1 | **TOC**: 0 | **BODY**: 1
  - **Context**: Subordinate review topic inside MD&A.
- `Risks and Concerns`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 3 | **TOC**: 2 | **BODY**: 1
  - **Context**: Subordinate risk management subsection within MD&A.
- `Risk Management`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 9 | **TOC**: 7 | **BODY**: 4
  - **Context**: Subordinate risk section or standalone operational risk narrative.
- `Risks and Mitigation Strategies`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 1 | **TOC**: 0 | **BODY**: 1
  - **Context**: Subordinate subsection inside MD&A.
- `Internal Control Systems and their Adequacy`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 3 | **TOC**: 3 | **BODY**: 0
  - **Context**: Subordinate internal controls subsection within MD&A.
- `Financial Performance and Review`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 2 | **TOC**: 1 | **BODY**: 2
  - **Context**: Subordinate financial performance subsection within MD&A.
- `Retail Banking`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 3 | **TOC**: 2 | **BODY**: 1
  - **Context**: Segment-specific subsection topic inside MD&A.
- `Wholesale Banking`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 3 | **TOC**: 2 | **BODY**: 1
  - **Context**: Segment-specific subsection topic inside MD&A.
- `Treasury`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 3 | **TOC**: 2 | **BODY**: 1
  - **Context**: Segment-specific subsection topic inside MD&A.

##### Category 6: Financial Statements & Accounting Notes

- `Balance Sheet`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 24 | **TOC**: 20 | **BODY**: 10
  - **Context**: Primary audited financial statement.
- `Consolidated Balance Sheet`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 20 | **TOC**: 11 | **BODY**: 11
  - **Context**: Primary audited consolidated financial statement.
- `Statement of Profit and Loss`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 17 | **TOC**: 15 | **BODY**: 7
  - **Context**: Audited financial statement.
- `Consolidated Statement of Profit and Loss`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 13 | **TOC**: 5 | **BODY**: 9
  - **Context**: Audited consolidated financial statement.
- `Cash Flow Statement`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 19 | **TOC**: 18 | **BODY**: 5
  - **Context**: Audited financial statement.
- `Consolidated Cash Flow Statement`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 13 | **TOC**: 10 | **BODY**: 5
  - **Context**: Audited consolidated financial statement.
- `Statement of Changes in Equity`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 3 | **TOC**: 4 | **BODY**: 1
  - **Context**: Audited financial schedule.
- `Notes to the Financial Statements`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 4 | **TOC**: 4 | **BODY**: 0
  - **Context**: Audited quantitative accounting disclosures.
- `Schedules to the Financial Statements`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 3 | **TOC**: 3 | **BODY**: 0
  - **Context**: Accounting disclosure schedules.

##### Category 7: Shareholder Formalities & Ancillary Furniture

- `Notice of Annual General Meeting`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 9 | **TOC**: 7 | **BODY**: 4
  - **Context**: Shareholder meeting statutory notice.
- `Attendance Slip`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 17 | **TOC**: 5 | **BODY**: 14
  - **Context**: Shareholder meeting administrative slip.
- `Proxy Form`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 18 | **TOC**: 9 | **BODY**: 13
  - **Context**: Shareholder meeting statutory proxy form.
- `Route Map`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 1 | **TOC**: 1 | **BODY**: 0
  - **Context**: Meeting venue navigation map.
- `Shareholder Information`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 6 | **TOC**: 10 | **BODY**: 3
  - **Context**: Administrative investor information.
- `Company Information`
  - **Class**: NOT EQUIVALENT BUT CONFUSABLE | **Docs**: 2 | **TOC**: 1 | **BODY**: 1
  - **Context**: Corporate directory and registrar contacts.

#### 3.4 UNRESOLVED (Frame Anomalies)

Exceptional cases where document-level frame anomalies prevent a definitive determination. Presence or absence of MD&A cannot be evaluated.

##### Regulatory Filing Anomaly

- `FRAME_ANOMALY: NOT_AN_ANNUAL_REPORT`
  - **Class**: UNRESOLVED | **Docs**: 1 | **TOC**: 0 | **BODY**: 1
  - **Context**: Observable context: Document is a 1-page regulatory filing announcement letter, not a complete annual report. Evaluated in accordance with protocol; presence or absence of MD&A cannot be resolved.

---

### 4. Audit Trail: Deletions of Unsupported & Synthetic Titles from v0.1

In accordance with Section Q ("Delete any unsupported title and record it in the change log. Do not invent titles."), the following entries from v0.1 have been eliminated because they were synthetic templates, mojibake artifacts, invented sub-labels, or unobserved in the 60-document census:

| Deleted Title / String | Previous v0.1 Section | Deletion Rationale |
| :--- | :--- | :--- |
| `Management Discussion and Analysis (MD&A)` | 3.1 Standard Forms | Synthetic acronym expansion; not observed as standalone heading in ledger. |
| `Management Discussion and Analysis of Financial Condition and Results of Operations` | 3.1 Standard Forms | Full SEC-style statutory title; unobserved in frozen 60-doc census. |
| `Management Discussions & Analysis (MD&A) Report` | 3.1 Plural Forms | Unobserved combination; ledger contains singular Discussion. |
| `Management Discussion and Analysis YYYY-YY` | 3.1 Year-Suffixed Variants | Synthetic regex pattern template; replaced by concrete observed financial-year titles. |
| `ANNEXURE 1 / Management Discussion and Analysis` | 3.1 Annexure-Prefixed Openers | Annexure prefix separated as structural note in accordance with Section Q. |
| `Annexure - B / MANAGEMENT DISCUSSION & ANALYSIS` | 3.1 Annexure-Prefixed Openers | Annexure prefix separated as structural note in accordance with Section Q. |
| `à~§Y {ddoMZm Ed§ {dícofU` | 3.1 Bilingual Variants | Mojibake legacy text-layer artifact; eliminated per Section P (only visible text permitted). |
| `œÏ¤¸¿š¸ ¢¨¸¨¸½ ¸›¸¸ ‡¨¸¿ ¢¨¸©¥¸½«¸µ¸` | 3.1 Bilingual Variants | Mojibake legacy text-layer artifact; eliminated per Section P (only visible text permitted). |
| `MANAGEMENT DISCUSSION AND ANALYSIS REPORT & CORPORATE GOVERNANCE REPORT` | 3.2 Condition C | Unobserved synthetic title; replaced by observed joint heading string. |
| `Report of the Board of Directors` | 3.3 Category 1 | Unobserved variation; ledger records Directors' Report and Board's Report. |
| `Company’s Corporate Governance Philosophy` | 3.3 Category 2 | Unobserved heading variation in frozen development set. |
| `BRSR` | 3.3 Category 3 | Acronym unobserved as standalone heading; full title observed in ledger. |
| `Sustainability Highlights` | 3.3 Category 3 | Unobserved subsection title in frozen development set. |
| `Climate Change Report` | 3.3 Category 3 | Unobserved report title in frozen development set. |
| `A Dialogue with the CEO & CFO` | 3.3 Category 4 | Unobserved executive narrative heading. |
| `Company Profile` | 3.3 Category 4 | Unobserved introductory heading. |
| `Strategic Objectives and Enablers` | 3.3 Category 4 | Unobserved executive overview heading. |
| `Our Growth Drivers` | 3.3 Category 4 | Unobserved executive overview heading. |
| `Introducing Our Capitals` | 3.3 Category 4 | Unobserved integrated reporting heading. |
| `Industry Structure and Developments` | 3.3 Category 5 | Unobserved as independent heading in ledger snapshot. |
| `Opportunities and Threats` | 3.3 Category 5 | Unobserved combined heading; individual components observed. |
| `Segment-wise or Product-wise Performance` | 3.3 Category 5 | Generic statutory descriptor; concrete segment names observed. |
| `Discussion on Financial Performance` | 3.3 Category 5 | Unobserved variant; Financial Performance and Review observed. |
| `Material Developments in Human Resources / Industrial Relations` | 3.3 Category 5 | Unobserved verbatim heading string in census. |
| `Report on the Standalone Financial Statements` | 3.3 Category 6 | Unobserved auditor report variant. |
| `Notes forming part of the Financial Statements` | 3.3 Category 6 | Unobserved phrasing; Notes to the Financial Statements observed. |
| `Ballot Form` | 3.3 Category 7 | Unobserved shareholder administrative form in census. |
| `CONDITIONAL (SUBSTANTIVE_EMBEDDED)` | 3.2 Invented Labels | Invented annotation sub-label; removed in accordance with Section Q. |
| `CONDITIONAL (CROSS_REFERENCE)` | 3.2 Invented Labels | Invented annotation sub-label; removed in accordance with Section Q. |
| `CONDITIONAL (COMBINED_SECTION)` | 3.2 Invented Labels | Invented annotation sub-label; removed in accordance with Section Q. |
| `CONDITIONAL (ALTERNATIVE_TITLE)` | 3.2 Invented Labels | Invented annotation sub-label; removed in accordance with Section Q. |

---

### 5. Mechanical Builder Provenance

- **Builder Script**: `D:\gold_blind\output\v0_2\build_title_equivalence.py`
- **Normalization Version**: `declared_normalize_v0_2` (case-folded, whitespace-collapsed, curly-quotes normalized to straight, ampersands normalized to 'and', leading section numbers stripped, trailing page numbers stripped, Annexure prefixes recorded as notes)
- **Assertion Status**: 100% verified — every listed title exists in `TITLE_EVIDENCE_LEDGER_v0_2.csv`.
