# ARPipe Gold annotation protocol v0.1

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
the qualifying MD&A heading. Include a mixed last-content/next-section page and set
`mixed_end_page`; do not extend to isolated later references.

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

### Rule 2 — multiple spans

**SOURCED.** Primary is the full English MD&A. Record all other copies or admissible
alternatives as self-contained `{start_page, end_page, type}` objects in document order.
Do not union distinct copies unless Rule 4 establishes one non-contiguous occurrence.

### Rule 3 — bilingual

**SOURCED.** English full MD&A is primary; list the Hindi copy and set `bilingual`.

**PROPOSED.** Rule 3 has not yet been tested on in-corpus data; FIT bilingual prevalence
is unknown because the frozen detectors cannot see legacy-encoded Hindi.

**VERIFIED.** `page_profile.csv` labels every FIT/VALIDATION page script `latin` or
`unknown`. Top-level `condition_document_map.csv` gives every FIT IDBI Bank row
`bilingual_candidate = NOT_OBSERVED`, `verification_status = NOT_REVIEWED`.
**INFERRED.** Author-supplied context says IDBI is government-controlled, so bilingual
reports are likely; detector non-observation is not evidence of absence.

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
`embedded_in_directors_report`. Apply the same-level-or-higher sibling rule, not the end
of the entire parent report.

### Rule 6 — annexure

**SOURCED.** A qualifying annexure counts as MD&A; record its printed identity and set
`annexure`. The governing basis is Clause 49 / LODR Regulation 34(2)(e) / Schedule V.

### Rule 7 — unclear start

**SOURCED.** Include the heading page; record the later substantive page. **PROPOSED.**
Set `unclear_start` only when at least two starts remain plausible under the heading rule.
If they remain equally admissible after all rules, use `AMBIGUOUS`.

### Rule 8 — unclear end

**SOURCED.** Include a mixed final MD&A/next-section page and flag it. Record last-content
and next-heading pages. If two ends remain admissible, use `AMBIGUOUS` rather than an
annotator preference.

### Rule 9 — unusual titles and unresolvable cases

**SOURCED.** An unusual title qualifies only through the incorporated title-equivalence
list. **PROPOSED.** Exhaust the written rules and aids, then record all still-admissible
spans without ranking them; never consult a developer, prediction, prior label, or
evaluation artifact.

## 6. Title-list intake and separation

**SOURCED.** Required provenance wording:

> Produced by an isolated AI-assisted reading, combining PDF text extraction and contact-sheet viewing, of the 60 FIT DEVELOPMENT documents, without access to the ARPipe repository or its heading patterns; classes assigned by a rule script; pending independent human spot-verification.

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
