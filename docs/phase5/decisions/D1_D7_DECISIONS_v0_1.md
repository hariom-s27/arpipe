# D1–D7 author decisions (v0.1)
Date: 2026-09-28. Status: DECIDED by author (in chat). Evidence: `claude/round3/D1_D7_LITERATURE_CHECK.md`.
Applies to: title rules + Gold protocol. Does NOT by itself change the frozen review CSV (`2A362F03…`); see §3.

## 1. Decisions
| # | Decision | Extra rule / flag |
|---|---|---|
| D1 | English only; Hindi-only MD&A → ABSENT | new ABSENT reason `NO_ENGLISH_MDA`; fix protocol note N1 (bilingual docs exist in FIT) |
| D2 | A stub counts as PRESENT | flag `STUB` + word count. A pointer sentence ("refer to page X") is not a stub → follow the pointer |
| D3 | Divider / MD&A own-contents page is the start | only if it names MD&A alone. SAP reports exact-start and ±1-page start |
| D4 | Inside Directors' Report: end before the first statutory item *after* MD&A begins | closed list of statutory items (s.134(3) / Accounts Rules r.8). Shared topic (e.g. internal controls) stays in MD&A only if under an MD&A heading |
| D5 | TOC grouping does not decide which report a page belongs to | annotator note |
| D6 | Keep CSR pages (Welspun 2012) | flag `CONTAINS_CSR` so climate-word counts can exclude those pages |
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

## 4. Follow-ups (remaining)
- F1a Author: eyeball Reliance 2018 p43 (names MD&A alone?); get Modern Steels 2024 word count; decide CSR vs CSR+ESG flag scope; decide the `toc_source` quirk.
- F2 Write the D4 closed statutory-item list.
- F3 Schema/tool: add ABSENT reason `NO_ENGLISH_MDA`; flags `STUB`(word_count), `CONTAINS_CSR` (optional `EMBEDDED_IN_DR`). Needs schema version bump + P5-T annotator update + tests.
- F4 Decide: pointer target outside the report (e.g. website) → which outcome/reason code? (a priori; no FIT case)
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

Tie-break: a topic in both lists (internal controls, financial performance) stays in MD&A only when it sits under an MD&A-labelled heading or block.
