# ARPipe Gold annotation protocol v0.4

> **What changed from v0.3.** This revision adds anchor-text capture on shared boundary
> pages (§4): when the start page or the end page of the primary span is shared with
> another section, the annotator also copies that page's heading line into a required
> text field, so the shared-page answer carries the evidence for it. §6's provenance
> wording is replaced to describe the author's page-by-page human review of the title
> list in place of the earlier AI-assisted ledger. §2 adds the pilot viewer pin: Adobe
> Acrobat Reader with "Use logical page numbers" switched off. Every other rule is as
> in v0.3.

**Document status:** `DRAFT_PENDING_PILOT`

**PROPOSED.** This executable draft defines DocumentGold annotation rules. It does not
authorize annotation, create Gold, settle unsigned choices, or permit HOLDOUT access.

## 1. Authority, scope, and blindness

**SOURCED.** D1/PG-1 bounds the claim to reproducible START–END physical-page
localization. Q3/Q4/B6 require independent raw A/B records, full HOLDOUT double
annotation, predeclared VALIDATION overlap, and a separate-person adjudicator. Q7 governs
every edge case (`docs/governance/CURRENT_DECISIONS.md:24,27-31,40`).

**VERIFIED.** This revision did not consult `arpipe/patterns.py`, `MDA_HEADING_RE`, heading
or terminator logic in `segment.py`/`verify.py`, `arpipe/tests/`, predictions, labels,
evaluation outputs, `reports/`, run outputs, any PDF content, `D:/gold_blind`, or any
P5-B evidence/method artifact. The only `arpipe/` content read was field names/types at
`arpipe/models.py:170-195`. PDF use was byte hashing only, as recorded in
`CORPUS_FRAME_CHECK_v0.md`.

**PROPOSED.** The protocol decides only MD&A presence, inclusive physical-page span, and
structured source features. It does not choose OCR routing, PageGold, reading order,
climate measurement, an Oracle population, a system behavior, or a score.

## 2. Unit and page entry

**SOURCED.** Gold stores and scores **0-based physical PDF page indices** (Q7). Printed
page labels, Roman numerals, and viewer-defined labels never enter the record.

**PROPOSED.** Annotators enter the viewer's **physical page number (1-based, as shown in
the page box, with page labels disabled)**. The tool records the 1-based audit value and
stores `page_index_0based = viewer_page_1based - 1`. It rejects a viewer page count that
does not equal the verified metadata count and enforces `0 <= start <= end < N`.

**PROPOSED.** Viewer product, version, and the setting “show physical page numbers, not
page labels” remain to be pinned at method freeze. Until then:
`VIEWER: ______` `VERSION: ______` `SETTING VERIFIED BY: ______`.

**PROPOSED.** Pilot viewer: Adobe Acrobat Reader (record the version), Edit > Preferences
> Page Display > "Use logical page numbers" switched OFF.

## 3. States, reasons, and structural flags

**SOURCED.** States are `PRESENT`, `ABSENT`, and `AMBIGUOUS`. A TOC entry or pointer is
not presence. `AMBIGUOUS` and its admissible spans are assigned before any system output
for the document is viewed.

| State | Allowed reason | Meaning |
|---|---|---|
| `PRESENT` | `BODY_QUALIFYING_TITLE` | **PROPOSED.** Qualifying body heading and resolvable span. |
| `PRESENT` | `CONDITIONAL_TITLE_CONTEXT_MET` | **PROPOSED.** Frozen observable condition for a CONDITIONAL title is satisfied. |
| `ABSENT` | `NO_QUALIFYING_BODY_SECTION` | **PROPOSED.** Complete review finds no narrower absence reason. |
| `ABSENT` | `TOC_ONLY` | **SOURCED.** TOC occurrence without qualifying body content. |
| `ABSENT` | `POINTER_ONLY` | **SOURCED.** Pointer without qualifying body content. |
| `ABSENT` | `CONFUSABLE_SECTION_ONLY` | **PROPOSED.** Only a title classified as confusable is present. |
| `ABSENT` | `NOT_AN_ANNUAL_REPORT` | **PROPOSED.** The supplied file is not an annual report. |
| `ABSENT` | `NO_ENGLISH_MDA` | **PROPOSED.** The report has MD&A only in a language other than English (`D1_D7_DECISIONS_v0_1.md` §7.1). |
| `ABSENT` | `EXTERNAL_REFERENCE_ONLY` | **PROPOSED.** The report provides MD&A only outside itself (`D1_D7_DECISIONS_v0_1.md` §6). |
| `AMBIGUOUS` | `PRESENCE_UNRESOLVABLE`, `START_UNRESOLVABLE`, `END_UNRESOLVABLE`, `SPAN_UNRESOLVABLE`, `TITLE_CONTEXT_UNRESOLVABLE` | **PROPOSED.** Written rules leave the named uncertainty unresolved. |

**PROPOSED.** PRESENT reason codes describe the presence basis only. Multiple spans,
bilingual, non-contiguous, embedded, annexure, unclear boundaries, mixed end pages, and
legacy/corrupted boundary headings are recorded as flags and associated fields, so
stacking structures do not force annotators to choose competing “primary” reasons.

## 4. General boundary rule

**PROPOSED.** Start is the first physical page carrying the qualifying body heading.
Record a later `substantive_start_page` when appropriate. Set `unclear_start` only when
two or more pages could plausibly be the start after applying the heading rule; a
heading-page/substantive-page difference alone is not unclear.

**PROPOSED.** End is the last page containing MD&A content before the next sibling
heading. “Next sibling” means the next heading at the same or higher structural level as
the qualifying MD&A heading. Include the last content page even when another section
shares it (next paragraph); do not extend to isolated later references.

**PROPOSED.** A boundary page is **shared** when the viewer page also carries text from
another section, ignoring running headers, footers and page numbers
(`D1_D7_DECISIONS_v0_1.md` §8.7). This covers (i) another section above or below on the
same page, (ii) another section in the other column, and (iii) the other half of a
two-page spread. The definition applies to **both** boundary pages: answer *Start page
shared with another section?* for the primary start page and *End page shared with another
section?* for the primary end page. Both answers are **required, Yes or No, on every
PRESENT record**: the tool has no default and refuses submission until both are answered.
On ABSENT and AMBIGUOUS records, which have no primary span, both stay blank (null). The
tool sets the flags from the answers: Yes on the start page sets `mixed_start_page`; Yes on
the end page sets `mixed_end_page` and records the primary end page as
`boundary_evidence.mixed_end_page`; No sets no flag and leaves `mixed_end_page` null.

**PROPOSED.** When the start page is shared, copy the MD&A heading line exactly as printed
(if there is no body heading, the first sub-entry heading under MD&A). When the end page is
shared, copy the heading line of the section that follows the MD&A on that page. Copy from
the text layer if possible; if copying gives boxes or garbage, type it from the page image.
Leave both blank when the page is not shared.

**PROPOSED.** Apply this boundary hierarchy (`D1_D7_DECISIONS_v0_1.md` §2):

1. When MD&A has its own heading, it is heading-bounded: the next heading of equal or
   higher level ends it.
2. When MD&A is embedded in a Directors' or Board's Report, apply the legal-content
   test: Schedule V Part B content is in; Companies Act section 134 / Accounts Rules
   rule 8 statutory items are out.
3. TOC grouping never overrides which report a page belongs to (D5).

**PROPOSED.** Synthetic examples: (1) viewer pages 8–13 contain a heading through a mixed
end page; store `[7,12]`, record substantive start index 8, and do not set
`unclear_start`; (2) embedded MD&A inside a Directors' Report ends before the next
Directors' Report subheading at the same level; (3) lettered item B ends before lettered
item C at the same level; (4) equally admissible `[31,36]` and `[31,37]` produce
`AMBIGUOUS` with both spans and no primary.

## 5. Numbered Q7 rules

### Rule 1 — absence

**SOURCED.** Record `ABSENT` with a reason. A TOC entry or “forms part of” pointer without
body content is not presence. **PROPOSED.** In-PDF search is never sufficient evidence of
absence. Absence requires a thumbnail pass of every page, following TOC/pointer
destinations, and logging whether search was usable.

**PROPOSED.** Use `NO_ENGLISH_MDA` when MD&A exists only in a language other than
English (`D1_D7_DECISIONS_v0_1.md` §§1 D1 and 7.1). Use
`EXTERNAL_REFERENCE_ONLY` when the report gives MD&A only through a reference outside
the report (`D1_D7_DECISIONS_v0_1.md` §6 F4). A pointer sentence is not a stub: follow
the pointer before assigning presence or an absence reason (`D1_D7_DECISIONS_v0_1.md`
§1 D2).

### Rule 2 — multiple spans

**SOURCED.** Primary is the full English MD&A. Record all other copies or admissible
alternatives as self-contained `{start_page, end_page, type}` objects in document order.
Do not union distinct copies unless Rule 4 establishes one non-contiguous occurrence.

### Rule 3 — bilingual

**SOURCED.** The English full MD&A is primary regardless of whether it appears before or
after the Hindi copy. Record the Hindi copy as an alternative span of type `HINDI_COPY`
and set `bilingual` (`D1_D7_DECISIONS_v0_1.md` §§1 D1 and 7.1).

**VERIFIED.** Bilingual reports do occur in FIT: three IDBI documents were found in the
2026-09-28 title review. This corrects changelog note N1/C1
(`D1_D7_DECISIONS_v0_1.md` §3).

**PROPOSED.** For Hindi-only MD&A, record `ABSENT` + `NO_ENGLISH_MDA` and retain the Hindi
copy as an alternative span of type `HINDI_COPY` (`D1_D7_DECISIONS_v0_1.md` §7.1).

**PROPOSED.** The bilingual rule is a priori. Any HOLDOUT bilingual subgroup is
descriptive only. A bilingual disagreement is adjudicated strictly under this written
rule, which is never revised after HOLDOUT is seen. One or two out-of-corpus bilingual
annual reports may optionally be used as logged training aids; they are never Gold,
never scored, and never used to add titles or revise corpus facts.

### Rule 4 — non-contiguous

**SOURCED.** Primary is the contiguous hull; list every non-MD&A gap page strictly inside
it and set `noncontiguous_hull`. Pages outside the endpoints are not gaps.

### Rule 5 — embedded

**SOURCED.** Record only the MD&A subsection, list the parent section, and set
`embedded_in_directors_report`.

**PROPOSED.** Under D4, an MD&A embedded in a Directors' or Board's Report ends before
the **first** statutory item encountered **after** MD&A begins
(`D1_D7_DECISIONS_v0_1.md` §§1 D4 and 5). The closed statutory list is:

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
15. “Other statutory disclosures”; acknowledgement / appreciation; conclusion; Board sign-off
16. IBC applications / one-time-settlement differences (r.8(5)(xi)–(xii)); compliance with secretarial standards; credit rating (as a Directors' Report item)

**PROPOSED.** The tie-break topics are internal controls / internal financial controls;
financial performance / financial summary / highlights; and risk management. A
tie-break topic stays in MD&A only when it is under an MD&A-labelled heading or block
(`D1_D7_DECISIONS_v0_1.md` §6 A1–A3).

**PROPOSED.** Under D7, exclude only the Board's-report “Subsidiary Companies” section.
Subsidiary discussion inside a standalone MD&A remains inside the MD&A span
(`D1_D7_DECISIONS_v0_1.md` §§1 D7 and 2).

### Rule 6 — annexure

**SOURCED.** A qualifying annexure counts as MD&A; record its printed identity and set
`annexure`. The governing basis is Clause 49 / LODR Regulation 34(2)(e) / Schedule V.

### Rule 7 — unclear start

**SOURCED.** Include the heading page; record the later substantive page. **PROPOSED.**
A divider or MD&A's own contents page is the start only when it names MD&A alone (D3).
If MD&A has no body heading, start at the page of the first TOC sub-entry under MD&A, as
in the IDBI 2012 finding (`D1_D7_DECISIONS_v0_1.md` §§1 D3, 3, and 5). Set
`unclear_start` only when at least two starts remain plausible after these rules. If they
remain equally admissible after all rules, use `AMBIGUOUS`.

### Rule 8 — unclear end

**SOURCED.** Include the final MD&A page even when another section shares it, and flag it
through the *End page shared* answer under the §4 definition (`D1_D7_DECISIONS_v0_1.md`
§8.7). Record last-content and next-heading pages. If two ends remain admissible, use
`AMBIGUOUS` rather than an annotator preference.

### Rule 9 — unusual titles and unresolvable cases

**SOURCED.** An unusual title qualifies only through the incorporated title-equivalence
list. **PROPOSED.** Exhaust the written rules and aids, then record all still-admissible
spans without ranking them; never consult a developer, prediction, prior label, or
evaluation artifact.

### Rule 10 — stub

**PROPOSED.** Tick `stub` when the MD&A body is visibly short—about one page or less. Do
not count words. Only when the text layer is broken, type `stub_word_count` by hand
(`D1_D7_DECISIONS_v0_1.md` §7.2).

### Rule 11 — CSR/ESG pages

**PROPOSED.** Tick `contains_csr_esg` and list the viewer pages containing CSR, ESG, or
integrated-reporting “natural capital” blocks inside the MD&A span. The tool stores each
viewer page minus one. Every listed page must be inside the primary span and must not be
a gap page (`D1_D7_DECISIONS_v0_1.md` §§6 and 7.2).

### Rule 12 — reversible boundary decisions

**PROPOSED.** Wherever D3, D4, or D7 decided a boundary, also record the other admissible
boundary as an alternative span of type `BOUNDARY_ALTERNATIVE`
(`D1_D7_DECISIONS_v0_1.md` §7.5).

**PROPOSED.** `BROKEN_TEXT`, `HEADING_NOT_IN_TEXT_LAYER`, `mdna_word_count`, and
`csr_esg_word_count` are computed by a script after Gold is sealed, not by annotators.
The annotator flag `legacy_or_corrupted_boundary_heading` remains the annotator's own
observation (`D1_D7_DECISIONS_v0_1.md` §7.3).

## 6. Title-list intake and separation

**SOURCED.** Required provenance wording:

> Drafted from the author's page-by-page human review of the 60 FIT DEVELOPMENT documents, with titles checked against page images; normalisation checked by script on every recorded heading. The earlier AI-assisted title ledger (P5-B) was rejected as a title record and is not a source. Independent rules review: after the pilot, before any VALIDATION or HOLDOUT annotation.

**PROPOSED.** `TITLE_EQUIVALENCE_v0.md` is the annotator-facing artifact: title strings,
class (`EQUIVALENT`, `CONDITIONAL`, `CONFUSABLE`), observable condition for each
`CONDITIONAL`, and counts only. Every condition describes observable title context and
never an issuer or document identity. It contains no company names, document IDs, hashes,
pages, or observation locations.

**PROPOSED.** `TITLE_EVIDENCE_LEDGER_v0.csv` is method-owner/rules-reviewer evidence only.
The list enters the method only after its predeclared intake spot-check passes—more than
5% sampled error in page, text, or class triggers redo of the affected scope—and the
rules review is complete. Annotators receive only the annotator-facing list.

## 7. Permitted aids

**PROPOSED.** An isolated offline workspace may contain assigned PDFs, the current
protocol, the accepted annotator-facing title list, and the offline annotation tool. The
permitted aids are the pinned offline PDF viewer, thumbnails, viewer search, bookmarks,
zoom/rotate/fit-page controls, and page-count display.

**PROPOSED.** Record viewer/version, page convention, page count, search queries,
`search_usable`, bookmark pages, aids used, timestamps, PDF/protocol hashes, and access
attestations. A generative assistant, OCR engine, web search, external report, repository
tool, custom heading finder, regex, or prior record is not an annotation aid.

## 8. Workspace exclusions and memory limitation

**PROPOSED.** Exclude every repository/output/label/prediction/score/run artifact,
including `labels*.csv`, `labels_*_queue.csv`, `to_label.csv`, `eval_report*.md`,
`eval_holdout_log.csv`, `live_eval_report.md`, `reports/`, `*_run/`, prediction hashes,
and seal-holder material. Also exclude `TITLE_EVIDENCE_LEDGER_*` (all versions),
`docs/phase5/evidence/`, and all P5-B method notes.

**SOURCED.** The author is Annotator A and has historical exposure that workspace
isolation cannot erase. **PROPOSED.** The SAP therefore predeclares an Annotator-B-only
Gold sensitivity; the limitation and sensitivity are reported together.

**SOURCED.** Before adjudication completes, the separate adjudicator may see only the
rules, independent records, and PDF/pages necessary to resolve the disagreement—not
predictions, hashes, evaluation reports, scores, repository contents, or prior labels.

## 9. Lifecycle

**PROPOSED.** Only an annotator may supersede their own raw record, only before A/B
comparison, and only with a recorded reason. Preserve original bytes/hash. After the
comparison is run, no raw supersession is allowed; disagreements proceed only to
separate adjudication. Agreement always uses the first eligible sealed raw A/B records.

**PROPOSED.** A protocol change after PILOT records its evidence and scientific effect,
applies consistently to every future document, and uses only the pre-reserved RETEST when
retest is needed. No document-specific exception is permitted.

## 10. Open author-controlled lines

| ID | Proposed line | AUTHOR | DATE |
|---|---|---|---|
| A1 | **PROPOSED.** FIT development Gold is single-annotated by the author, used for rules and error analysis only, never reported as accuracy. |  |  |
| A2 | **PROPOSED.** VALIDATION Gold is scored once per Phase-10 KEEP decision and reported as “development check (used for model selection)”. |  |  |
| A3 | **PROPOSED.** Choose VALIDATION overlap of one or two documents per issuer before freeze. |  |  |
| A4 | **PROPOSED.** Use the v0.1 selector commit–reveal procedure. |  |  |
| A5 | **PROPOSED.** Report the Annotator-B-only sensitivity defined in the SAP. |  |  |

**PROPOSED.** These lines are unsigned and do not block PILOT. A1–A5 and C1-D1 require
author action at method freeze. The viewer pin is also due at freeze.

## 11. Decisions consumed and explicit limits

**SOURCED.** Decisions consumed: D1/PG-1, Q1b, Q2–Q10, B1, B4-note, B6, B8, and CC-4.
Q1b confines development to FIT/VALIDATION; Q2 separates partitions; Q3/Q4/B6 set roles;
Q5/B8 set the later prediction-first sequence; Q6/CC-4 set scoring needs; Q7 sets these
rules; Q8 keeps census framing; Q9 requires truthful historical-exposure wording; B1
keeps legacy diagnostic-only.

**PROPOSED.** The interval sensitivity, exposure-inventory counts beyond ratified wording,
Q10 climate recipe, C4, historical Oracle work, final viewer pin, and A1–A5 remain outside
this draft's authority. No annotation may begin until the applicable intake, review,
pilot/tool, author, and explicit method-freeze prerequisites are satisfied.
