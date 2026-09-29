# MD&A title list (TITLE_EQUIVALENCE_v0), pilot version v0.2

**Status: FROZEN FOR THE PILOT (2026-09-29, signed by the author).** The independent rules review and the 6-row spot-check are done by the adjudicator after the pilot and before any VALIDATION or HOLDOUT annotation (decisions §9.3). This list contains no company names, document IDs, hashes, pages, locations or counts.

**How to use it.** This list is an aid for *finding* the MD&A heading. It does not decide where MD&A starts or ends; the protocol's boundary rules (§4, Rules 1–12) and the page content decide. A heading that matches this list can still be a pointer or a running header, and a real MD&A can have a heading that is decorative, image-only or missing from the text layer, so search may miss it. Always confirm by looking at the page. Under Rule 9, an unusual title qualifies only through this list.

## 1. Reading a heading (normalisation)
Two headings are the same title when they are equal after these steps, applied in order:
1. Ignore letter case, extra spaces, and line breaks. A title wrapped over two or three lines is one title.
2. Ignore a label before the title: an annexure label ("Annexure 1:", "Annexure II", "Annexure to the Directors' Report") or an item number or letter ("4.", "12.", "B.", "a.").
3. Treat "&" as "and".
4. Ignore "'s" / "’s" ("Management's" = "Management").
5. Treat "Discussions" as "Discussion".
6. Ignore a short form in brackets: "(MD&A)", "(MDA)", "(MD&A Report)".
7. Ignore a trailing ":" or "–", a trailing year ("2023-24"), and a trailing "Report".
8. In a contents list, ignore the page number and dot leaders.

## 2. EQUIVALENT: these all name the MD&A
After §1, each of these is the same title, **Management Discussion and Analysis**:
- Management Discussion and Analysis
- Management Discussion and Analysis Report
- Management Discussion & Analysis (Report)
- Management's Discussion and Analysis (Report)
- Management Discussions and Analysis (Report)
- Management Discussion and Analysis 2023-24 (any year)
- Annexure 1: Management Discussion and Analysis; Annexure to the Directors' Report – Management Discussion and Analysis Report (any annexure label)
- B. Management Discussion and Analysis Report (any item number or letter)

Also EQUIVALENT (not seen in the review, but standard forms):
- **MD&A** or **MDA** used alone as a section heading (not inside a sentence).
- **Management's Discussion and Analysis of Financial Condition and Results of Operations** (the US form).

A contents entry and the body heading of the same MD&A often differ in wording; that is normal and they are still the same title.

Hindi copy: **प्रबंध विवेचना एवं विश्लेषण** is the Hindi title of the MD&A. In a bilingual report the primary span is always the English MD&A; the Hindi copy is recorded only as an alternative span of type `HINDI_COPY` (Rule 3).

## 3. CONDITIONAL: check what follows or what the report says
| Heading seen | It is the MD&A start only if… | Otherwise |
|---|---|---|
| A numbered or lettered item inside the Directors'/Board's Report ("N. Management Discussion and Analysis") | the text under it is the MD&A itself (industry, opportunities and threats, performance, risks, internal control, human resources, outlook…) | it is a **pointer**: one or two sentences saying MD&A is annexed, enclosed, attached, forms part of the report, or "kindly refer to" it. Follow the pointer; do not start there. |
| The title on a contents page | the page is the MD&A's **own** contents page and lists only MD&A parts (Rule 7 / D3) | it is the report's main contents: use it to find the page, not as the start |
| The title on a divider page (full-page photo or banner with the title) | the divider names MD&A alone | a divider naming several sections is not the start |
| A heading that names MD&A together with another report (Corporate Governance, the Directors' Report) | never by itself | find the MD&A's own heading; if there is none, apply Rule 7 (unclear start) |
| A different section name, such as "Business Review", "Operations Review", "Management Review", "Management Report" | the report itself says that this section is (or forms, or constitutes) the Management Discussion and Analysis, for example in the Directors' Report or on the section's first page | it is not MD&A |
| No MD&A heading in the body; the title appears only in the contents with sub-entries under it | — | the start is the page of the first contents sub-entry under MD&A (Rule 7) |

## 4. CONFUSABLE: never an MD&A start
- **Running headers and breadcrumbs** at the top or bottom of MD&A pages (they repeat the title on every page, sometimes in two languages).
- **The title repeated inside an MD&A that has already started** (a later part reusing the title).
- **Mentions** in other sections: the Corporate Governance Report ("the MD&A Report is given separately"), the Auditors' Report ("Other Information"), the Business Responsibility Report, or an assurance statement.
- **Sentences inside the MD&A** that name it (for example in the Cautionary Statement).
- **Pointer items** as in §3 row 1. A pointer item often uses exactly the MD&A title, so the words alone cannot tell a pointer from a start.

## 5. Hard cases to expect (types only)
- MD&A not named in the main contents (only "Annexures" or "Directors' Report" is listed); look inside that section.
- A heading that is decorative, on a photo, in a legacy font, or not found by text search.
- A broken text layer (copying gives boxes or garbage).
- MD&A inside the Directors' Report (Rule 5; the end is set by the content test).
- MD&A as an annexure to the Directors' Report.
- Two-page spreads: one viewer page shows two printed pages.
- A title wrapped over two or three lines.
- A divider page or the MD&A's own contents page as the start.
- A bilingual report with a Hindi MD&A before or after the English one.
- No MD&A heading in the body.

## Provenance
Drafted from the author's page-by-page human review of the 60 FIT DEVELOPMENT documents, with titles checked against page images. The normalisation in §1 was checked by script on every recorded heading and on the pre-fill strings (evidence note, method owner only). The §2 "not seen" forms and the §3 "different section name" row are added a priori (Rule 9). The earlier AI-assisted title ledger (P5-B) was rejected as a title record and is **not** a source for this list.
