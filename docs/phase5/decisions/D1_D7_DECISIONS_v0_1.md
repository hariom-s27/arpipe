# D1–D7 author decisions (v0.1)
Date: 2026-09-28. Status: DECIDED by author (in chat); §6–§7 added 2026-09-28. Evidence: `claude/round3/D1_D7_LITERATURE_CHECK.md`.
Applies to: title rules + Gold protocol. Does NOT by itself change the frozen review CSV (`2A362F03…`); see §3.

## 1. Decisions
| # | Decision | Extra rule / flag |
|---|---|---|
| D1 | English only; Hindi-only MD&A → ABSENT | new ABSENT reason `NO_ENGLISH_MDA`; fix protocol note N1 (bilingual docs exist in FIT) |
| D2 | A stub counts as PRESENT | flag `STUB` + word count. A pointer sentence ("refer to page X") is not a stub → follow the pointer |
| D3 | Divider / MD&A own-contents page is the start | only if it names MD&A alone. SAP reports exact-start and ±1-page start |
| D4 | Inside Directors' Report: end before the first statutory item *after* MD&A begins | closed list of statutory items (s.134(3) / Accounts Rules r.8). Shared topic (e.g. internal controls) stays in MD&A only if under an MD&A heading |
| D5 | TOC grouping does not decide which report a page belongs to | annotator note |
| D6 | Keep CSR pages (Welspun 2012) | flag `CONTAINS_CSR` so climate-word counts can exclude those pages → renamed `contains_csr_esg` with a page list, see §6–§7 |
| D7 | Exclude only the Board's-report "Subsidiary Companies" section (r.8(1)) | subsidiary discussion inside a standalone MD&A stays in |

## 2. Boundary hierarchy (ties D4, D6, D7 together)
1. MD&A has its own heading → heading-bounded (next heading of equal/higher level ends it). D6 follows from this.
2. MD&A embedded in Directors' Report → legal-content test (Sch V Part B in; s.134/r.8 items out). D4, D7 follow from this.
3. TOC grouping never overrides report identity (D5).

## 3. F1 result: CSV vs D1–D7 (checked 2026-09-28)
CSV `MDNA_TITLE_REVIEW_v0_1.csv`: 60 rows, 46,448 bytes, SHA-256 `2A362F03…B61A60E` (re-hashed here, matches log). All 59 Y rows: start ≤ end.

| Rule | Rows | Result |
|---|---|---|
| D1 | IDBI 2012, 2017, 2024 (`INE008A01015_*`) | English copy chosen in all 3. Hindi MD&A comes **before** English (2017, 2024) → the "English regardless of order" wording is needed. N1 confirmed wrong: 3 bilingual FIT docs. |
| D2 | Modern Steels 2024 (`INE001F01019_2024`) | PRESENT, start = end = 18. Needs STUB flag + word count (not in CSV). |
| D3 | Reliance 2018 (start 43 = MD&A own contents page; text starts 44); PVR 2025 (divider, title on it) | Consistent, **if** the Reliance p43 contents page names MD&A alone → author confirms by eye. PVR OK. |
| D4 | HDFC 2012/2013/2017 (end before "Statutory Disclosures"), 2018 (before "Subsidiary Companies"), 2024 (before "Performance of Subsidiary Companies"); INE004E01016 2012/2018/2024; INE004C01028 2017/2025; Modern Steels | All ends = before first statutory DR item after MD&A begins. HDFC 2012/13/17 have subsidiaries BEFORE MD&A → "after MD&A begins" wording confirmed. HDFC 2024 last topic "Internal Controls, Audit and Compliance" sits in the MD&A block → stays (tie-break). INE004C01028_2025 last item "Disclosure of Accounting Treatment" is a Sch V Part B item → correctly in. |
| D5 | IDBI 2012 | Ends 73, before "Corporate Governance" → excluded. OK. |
| D6 | Welspun 2012 | CSR pages kept (34–57). OK. |
| D7 | HDFC 2018, 2024 | Ends before subsidiaries → the UNSURE "alternative end" notes are now resolved. |

**No row needs a span change.** The CSV can stay v0.1 / `2A362F03…`.

New findings from the check:
- **CONTAINS_CSR applies to more than Welspun 2012:** IDBI 2017 (last MD&A topic is "Corporate Social Responsibility (CSR)") and Tata Communications 2017 (`INE151A01013_2017`, CSR key-deliverables table inside MD&A). Other CSR hits (Reliance 2013/2018, Tata Steel 2017/2018, Page 2013) are a CSR report *outside* MD&A → no flag. Related climate-heavy blocks without CSR label: IDBI 2024 last topic "ESG"; HDFC 2018 "Integrated Reporting" (natural capital). Decide if CONTAINS_CSR widens to CONTAINS_CSR_ESG.
- **Reliance 2025 UNSURE is moot for page-level Gold:** the disputed "10-Year Financial Highlights" is the left half of the same viewer page (31) as the MD&A start → page span identical either way. Note it; no rule needed.
- **IDBI 2012 has no MD&A body heading** (start = first TOC sub-entry, body title blank). Not a D3 case. Add one protocol line: "no body heading → start = page of first TOC sub-entry under MD&A".
- **Cosmetic data issue:** `INE004C01028_2017` has `REVIEWER_toc_source = TYPED` with no TOC title/page (should be blank). Fixing it changes the hash → either fix now as v0.1.1 or record as a known quirk in the commit message. Check schema/intake won't reject it.
- F4 (pointer to outside the report): no FIT row has this. Rule stays a priori.

## 4. Follow-ups (status updated 2026-09-28: F1a, F2, F4 DONE in §5–§6; F3 in progress; F5 open)
- ~~F1a~~ DONE (§5, §6). Author: eyeball Reliance 2018 p43 (names MD&A alone?); get Modern Steels 2024 word count; decide CSR vs CSR+ESG flag scope; decide the `toc_source` quirk.
- ~~F2~~ DONE (§5, §6 item 16). Write the D4 closed statutory-item list.
- F3 Schema/tool: add ABSENT reason `NO_ENGLISH_MDA`; flags `STUB`(word_count), `CONTAINS_CSR` (optional `EMBEDDED_IN_DR`). Needs schema version bump + P5-T annotator update + tests.
- ~~F4~~ DONE (§6: `EXTERNAL_REFERENCE_ONLY`). Decide: pointer target outside the report (e.g. website) → which outcome/reason code? (a priori; no FIT case)
- F5 Protocol: correct N1; add the §2 hierarchy; add the no-body-heading start line; SAP sensitivity with/without D3-divider and D6-CSR pages.
- Then: freeze title list; commit CSV as one planned commit.
## 5. F1a answers and F2 list (added 2026-09-28, coordinating chat)
- **Reliance 2018 p43:** confirmed from the author's screenshot. The page is MD&A's own contents page, titled "Management's Discussion and Analysis", listing only MD&A parts (Overview … Glossary). D3 applies; start 43 stands.
- **Modern Steels 2024 word count:** the section body is 25 words ("As the Members are aware that, the manufacturing business of the Company had been sold. The Company is working on the future course of business."), excluding the heading. STUB(word_count=25).
- **CSR vs CSR+ESG (proposed):** one page-set flag `CONTAINS_CSR_ESG`, covering CSR, ESG and integrated-reporting "natural capital" blocks inside MD&A. FIT rows: Welspun 2012, IDBI 2017, Tata Communications 2017, IDBI 2024, HDFC 2018. Author to confirm.
- **`toc_source` quirk (proposed):** keep the CSV at `2A362F03…`; record the quirk (`INE004C01028_2017`: `toc_source=TYPED` with blank TOC title/page) in the commit message; readers treat `toc_source` as blank when the TOC title is blank.
- **F4 (proposed):** MD&A given only outside the report (e.g. "available on our website") → ABSENT, reason `EXTERNAL_REFERENCE_ONLY`. No FIT case.

### F2: closed list of statutory Directors'/Board's Report items (D4)
Any of these headings, met after MD&A begins, ends an embedded MD&A:
1. Dividend; transfer to reserves; share capital / ESOP / sweat equity
2. Material changes after the balance-sheet date; change in nature of business
3. Subsidiaries, associates and joint ventures (r.8(1)); consolidated financial statements
4. Directors and key managerial personnel; independent directors' declaration; board evaluation; familiarisation
5. Board and committee meetings; nomination and remuneration policy
6. Directors' responsibility statement (s.134(5))
7. Auditors; auditors' report / qualifications; secretarial audit (s.204); cost audit / cost records
8. Deposits; loans, guarantees and investments (s.186); related party transactions (s.188, AOC-2)
9. Conservation of energy, technology absorption, foreign exchange earnings and outgo (s.134(3)(m), r.8(3))
10. Corporate social responsibility (as a Board's-report item, r.9 / CSR Rules)
11. Particulars of employees (s.197(12), r.5); median remuneration
12. Annual return (s.92(3)); vigil mechanism; sexual harassment (POSH) disclosure
13. Significant and material orders by regulators or courts; frauds reported by auditors
14. Corporate governance report (reference); business responsibility (and sustainability) report (reference)
15. "Other statutory disclosures"; acknowledgement / appreciation; conclusion; Board sign-off
16. IBC applications / one-time-settlement differences (r.8(5)(xi)–(xii)); compliance with secretarial standards; credit rating (as a DR item) — added by A3, §6

Tie-break: a topic in both lists (internal controls, financial performance) stays in MD&A only when it sits under an MD&A-labelled heading or block.

## 6. Amendments A1–A5 and open answers (DECIDED by author, 2026-09-28)
Author line: "CSR_ESG yes; F4 OK; A1–A3 yes; BROKEN_TEXT keep".
- **CSR/ESG:** one flag `contains_csr_esg` (replaces D6's `CONTAINS_CSR`), covering CSR, ESG and integrated-reporting "natural capital" blocks inside MD&A. FIT rows: Welspun 2012, IDBI 2017, Tata Communications 2017, IDBI 2024, HDFC 2018.
- **F4:** MD&A given only outside the report (e.g. "available on our website") → ABSENT, reason `EXTERNAL_REFERENCE_ONLY`.
- **A1:** risk management policy (s.134(3)(n)) → **tie-break list**: under an MD&A heading or block it stays in MD&A; as a separate Board's-report item it ends MD&A.
- **A2:** financial summary / highlights (r.8(5)(i)) → **tie-break list**.
- **A3:** added to the ending list (§5, item 16): IBC applications pending and one-time-settlement valuation differences (r.8(5)(xi)–(xii)); compliance with secretarial standards; credit rating (as a Directors' Report item).
- **A4:** `BROKEN_TEXT` kept, defined by code (§7.3).
- **A5:** nothing to fix: the merged commit message names the row by ID only.

Tie-break list (topics that appear in both MD&A and the Board's report): internal controls / internal financial controls; financial performance / financial summary / highlights; risk management. Each stays in MD&A only under an MD&A-labelled heading or block.

## 7. Field specifications for the schema update (F3)
### 7.1 New ABSENT reason codes
- `NO_ENGLISH_MDA`: the report has an MD&A only in a language other than English (D1). The Hindi copy of a bilingual report is recorded as an alternative span of type `HINDI_COPY` (already in v0.1); the primary span is always the English copy.
  - **Hindi-only (decided 2026-09-28):** v0.1 forbids any span on ABSENT. v0.2 makes one exception: ABSENT + `NO_ENGLISH_MDA` may carry alternative spans of type `HINDI_COPY` (and only that type), so the page location is kept. All other ABSENT records still have no spans.
- `EXTERNAL_REFERENCE_ONLY`: the report only points outside itself for MD&A (F4).

### 7.2 New annotator fields
- `stub` (flag): the annotator ticks it when the MD&A is visibly short (**at most about one page of body text**). Annotators do **not** count words. Only allowed when `presence_state = PRESENT`.
- `stub_word_count` (integer ≥ 0 or null): **optional**; filled by hand only when the text layer is broken (the script in §7.3 cannot count). Not required by the flag.
- The word count for every PRESENT span is computed by the §7.3 script, so downstream users apply their own cut-off (250 words, Loughran–McDonald; 450, Colak & Mai). No cut-off is part of Gold.
- `contains_csr_esg` (flag) + `csr_esg_pages` (array of unique 0-based page integers): required together. Every page must lie inside `primary_span` (start ≤ p ≤ end) and must not be in `gap_pages`. Purpose: text measures can drop exactly these pages. Only allowed when `presence_state = PRESENT`.

### 7.3 BROKEN_TEXT: computed by code, not by the annotator
Deterministic, per document, computed after Gold is sealed from the Gold record + the PDF text layer (PyMuPDF), stored in a separate derived file (not in the annotator record):
- `heading_in_text_layer` = the normalised Gold body title (casefold; "&"→"and"; drop "'s", "report", year suffixes, item/annexure labels; collapse whitespace and remove spaces) is a substring of the normalised text of the Gold start page, with the same normalisation. For a title wrapped over lines, joining the lines is covered by the space removal.
- `text_layer_broken` = on the start page, the share of characters that are U+FFFD, private-use (U+E000–U+F8FF) or control characters is > 5%, **or** fewer than 50% of the *counted* tokens are real Latin words, where:
  - tokens are split on whitespace and have leading/trailing punctuation stripped ("Company," → "Company", "(CSR)" → "CSR");
  - tokens containing any digit are **not counted** ("1,234.56", "FY2024");
  - tokens made only of non-Latin letters (e.g. Devanagari headers) are **not counted**;
  - of the remaining tokens with length ≥ 3, a "real Latin word" is purely ASCII letters, optionally with internal apostrophes or hyphens.
- **Calibration before use:** run once on the 60 FIT documents; it must flag the 8 documents the review marked as broken text and no clean ones. Adjust only the thresholds, record the result, then freeze the rule before any HOLDOUT use.
- The same script also records `mdna_word_count` for every PRESENT span (all pages start..end, minus gap pages; `csr_esg_word_count` separately).
- `BROKEN_TEXT` = `text_layer_broken`. `HEADING_NOT_IN_TEXT_LAYER` = not `heading_in_text_layer` (covers decorative / image headings too). SAP reports both as strata.
- The existing annotator flag `legacy_or_corrupted_boundary_heading` stays as the annotator's own observation; agreement between it and the computed `BROKEN_TEXT` is reported, not enforced.

### 7.4 Record version field
- v0.2 records carry a new required field `schema_version` with the constant value `"0.2"`. Records without it are v0.1. Scoring and tools pick the schema from this field; they never try both.

### 7.5 Keeping contested rules reversible
- Where D3, D4 or D7 decided a boundary, annotators also record the other admissible boundary as an alternative span of type `BOUNDARY_ALTERNATIVE` (already in v0.1). A later change to those rules, before HOLDOUT scoring, then means switching spans, not re-annotating. After HOLDOUT scoring a rule change is reported only as a sensitivity result.

## 8. Text-layer audit v0.2 rules and threshold rule (DECIDED 2026-09-28, before the recalibration rerun)
Evidence: FIT calibration v0.1 (`claude/round3/TEXT_AUDIT_CALIBRATION_v0_1.md`; output SHA-256 `B3AE60CF…F785A105`). At v0.1 defaults the body check gave one false positive (Reliance 2018, start page = MD&A own-contents page, bad share 0.060) and missed the two legacy-font-heading documents, which only the heading check caught.

### 8.1 Two checks on two pages
- **Heading check** (`heading_in_text_layer`): on the Gold start page, as in §7.3.
- **Body-quality check** (`text_layer_broken`): on the **quality page** = the first page in start..end (excluding gap pages) with **at least 50 tokens of length ≥ 3 counted before any quality filtering** (after edge-punctuation stripping only; digits and non-Latin tokens still count toward the 50). If no page reaches 50, use the start page and record `quality_page_fallback = true`. Output `quality_page_0based`.
- Shares (`bad_char_share`, `latin_word_share`) are computed on the quality page with the §7.3 definitions.

### 8.2 Reporting
- Report `heading_in_text_layer`, `text_layer_broken` and their union `BROKEN_TEXT` (= broken OR heading not found; NA = not flagged). The SAP reports each signal's own count as well as the union: legacy-font headings, image-only headings and garbage body text are different failure types.
- Report-only column `dictionary_word_share` (share of quality-page kept tokens that are in a pinned English word list, supplied by `--wordlist`, SHA-256 recorded in the output header; NA if no list is given). It does **not** feed any flag.

### 8.3 Word-count scope
- Every count carries `word_count_scope = PAGE_LEVEL`.
- `start_page_shared`: computed. The y-position of the first text line matching the heading; shared if it lies below 20% of the page height; NA if the heading is not found.
- `end_page_shared`: taken from the Gold record (`boundary_evidence.mixed_end_page` / `mixed_end_page` flag, already in schema v0.2) via an input column; NA if not supplied.
- The SAP uses word counts only when both shared values are false; stubs and shared-page sections use hand counts if needed. `csr_esg_word_count` is meaningful only when CSR/ESG pages are supplied.

### 8.4 Threshold rule (fixed now; the rerun only fills in the numbers)
On the FIT recalibration rerun, over the documents expected CLEAN or PARTIAL (i.e. all except the three expected BROKEN):
- `max_bad_char_share` = max(0.05, 2 × the highest bad_char_share among them)
- `min_latin_word_share` = min(0.50, 0.5 × the lowest latin_word_share among them)
The resulting values are written into SAP v0.2 and the script defaults **before any VALIDATION or HOLDOUT document is scored**. With 3 positives in FIT, the thesis states that the detector is only lightly tested and reports it separately on VALIDATION and HOLDOUT.

### 8.5 Clarifications (DECIDED 2026-09-28, before the rerun)
- **Clean set per check (§8.4).** Body check: clean = every FIT document whose body is not broken, i.e. all except Span 2018 (`INE004E01016_2018`); Jubilant 2013 and Gujarat Cotex 2017 have clean bodies and count as clean here. Heading check: the expected positives are the 3 listed (Span 2018, Jubilant 2013, Gujarat Cotex 2017).
- **Expected rerun values (stated in advance):** `min_latin_word_share` ≈ 0.40 (half of the lowest clean value, currently 0.796); `max_bad_char_share` likely stays 0.05 once Reliance 2018 is measured on a text page. Any other outcome is checked before the numbers are recorded.
- **`start_page_shared` validation.** In the same rerun, compare the computed flag with the review's mid-page-start labels (FIT notes). If decorative banners or photos above a full-page heading cause false "shared" flags, replace the 20% rule by "real body text (excluding running headers and page furniture) appears above the heading" before any VALIDATION use.
- **`end_page_shared` source.** Schema v0.2 requires `boundary_evidence.mixed_end_page` on every record (page or null). Rule: end_page_shared = (mixed_end_page is not null). The protocol tells annotators that null means "the end page is not shared".
- **Word list.** The Loughran–McDonald Master Dictionary (a versioned finance word list), with its version and file SHA-256 recorded in the output header. The script accepts either a one-word-per-line file or the dictionary CSV (column `Word`).
