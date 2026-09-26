# ARPipe Gold annotation protocol v0

**Document status:** `DRAFT_PENDING_PILOT`

**PROPOSED.** This document is an executable draft for independent DocumentGold
annotation. It is not frozen Gold, does not authorize annotation, and becomes usable only
after the blind P5-B title list is transferred, reviewed, and referenced at freeze.

**PROPOSED.** Every substantive paragraph or table row is prefixed with one of
`VERIFIED`, `SOURCED`, `DERIVED`, `INFERRED`, or `PROPOSED`. Headings, field names,
equations, examples, and citations inherit the nearest explicit label.

## 1. Authority, scope, and blindness

**SOURCED.** The governing claim is reproducible START-END physical-page localization of
MD&A in the declared Indian annual-report corpus
(`docs/phase4/PHASE4_B1_B8_TRIAGE.md:18`). D1-D10 in that Phase 4 section are the operative
wording (`docs/governance/CURRENT_DECISIONS.md:24`; PG-1).

**SOURCED.** Gold uses independent A/B records, a separate-person adjudicator, full double
annotation on HOLDOUT, and a predeclared VALIDATION overlap
(`docs/governance/CURRENT_DECISIONS.md:27-28,40`; Q3, Q4, B6). This draft neither selects
the overlap nor opens any evaluation document.

**SOURCED.** Gold is blind: annotators have no repository access and see no ARPipe output;
the adjudicator is also barred from predictions, hashes, reports, scores, repository
contents, and prior labels/predictions (`docs/governance/CURRENT_DECISIONS.md:60-68`).

**VERIFIED.** While this protocol was written, the author of this draft did not consult
`arpipe/patterns.py`, `MDA_HEADING_RE`, the heading logic in `segment.py`, ARPipe
prediction files, ARPipe Gold/label files, or ARPipe evaluation outputs. The title rules
below therefore do not reproduce implementation patterns.

**PROPOSED.** This protocol covers only whether MD&A is present and, when resolvable, its
physical PDF page span and structured edge-case metadata. It does not define PageGold,
text transcription, reading order, OCR routing, a climate recipe, an Oracle population,
or system behavior.

## 2. Annotation unit and page convention

**SOURCED.** The unit is one PDF document and page references use **0-based physical PDF
page indices** (`docs/governance/AUTHOR_RATIFICATION_2026-09-26.md:382-386`; Q7). The first
physical PDF page shown by a viewer is index `0`, irrespective of a printed page number,
cover numbering, Roman numerals, omitted printed numbers, or viewer display labels.

**PROPOSED.** Before annotation, the tool records the PDF page count `N`. Every recorded
page must be an integer in `[0, N-1]`. A span `[start, end]` is inclusive and must satisfy
`0 <= start <= end < N`.

**PROPOSED.** A qualifying body occurrence, rather than a table-of-contents entry or
cross-reference, is the evidence unit. Use the frozen P5-B title-equivalence list and the
rules in section 5 to decide whether an observed body section qualifies.

### 2.1 General start rule

**PROPOSED.** The start is the first physical page carrying the qualifying MD&A body
heading. Include a standalone opening page bearing that heading even when substantive
prose begins on the next physical page. If no qualifying heading is visible but the
frozen title list has a conditional entry whose stated observed context is satisfied,
apply that condition exactly and record the evidence in `structured_provenance`.

### 2.2 General end rule

**PROPOSED.** The end is the last physical page containing MD&A content before the next
sibling section begins. If the next section begins on the same physical page as the last
MD&A content, include that mixed page and set `mixed_end_page`. Do not extend the span
merely because later pages contain isolated references to MD&A.

**PROPOSED.** A section break is evidenced by a visible next-section heading and the
change in substantive content. Page furniture such as running headers, footers, page
numbers, or a repeated report title does not by itself start or end the span.

### 2.3 Invented worked examples

**PROPOSED.** These examples are synthetic and contain no text copied from an annual
report.

1. **PROPOSED.** A qualifying heading appears on physical page `7`, the prose begins on
   page `8`, and the next sibling section begins on page `12` after the final MD&A
   paragraph on that page. Record primary span `[7, 12]`,
   `substantive_start_page = 8`, and `mixed_end_page = 12`.
2. **PROPOSED.** Qualifying content occurs on pages `20-22` and `24-25`; page `23` is a
   full-page unrelated insert. Record the contiguous hull `[20, 25]` and
   `gap_pages = [23]`.
3. **PROPOSED.** The contents page at index `2` lists a qualifying title, but a complete
   review finds no body occurrence. Record `ABSENT` with `TOC_ONLY`.
4. **PROPOSED.** Two boundary readings, `[31, 36]` and `[31, 37]`, remain equally
   admissible after applying every rule. Record `AMBIGUOUS`, no primary span, and both
   spans in `admissible_spans`.

## 3. Presence states and reason codes

**SOURCED.** Use exactly the presence states `PRESENT`, `ABSENT`, and `AMBIGUOUS`; an
unresolvable case is `AMBIGUOUS` and is decided before any system output is viewed
(`docs/governance/AUTHOR_RATIFICATION_2026-09-26.md:342-380`; Q7).

**PROPOSED.** Select one `presence_reason_code`. Edge cases beyond the primary code are
captured as flags; a code must not be selected merely to describe system behavior.

| State | Reason code | Operational meaning |
|---|---|---|
| `PRESENT` | `BODY_QUALIFYING_TITLE` | **PROPOSED.** A qualifying body occurrence has a resolvable span. |
| `PRESENT` | `MULTIPLE_SPANS_PRIMARY_SELECTED` | **PROPOSED.** Multiple occurrences exist and rule 2 selects a primary. |
| `PRESENT` | `BILINGUAL_ENGLISH_PRIMARY` | **SOURCED.** English is primary and the Hindi copy is separately listed. |
| `PRESENT` | `NONCONTIGUOUS_HULL` | **SOURCED.** The primary is a contiguous hull with gap pages. |
| `PRESENT` | `EMBEDDED_SUBSECTION` | **SOURCED.** MD&A is a subsection of the Directors' Report. |
| `PRESENT` | `ANNEXURE` | **SOURCED.** A qualifying annexure counts as MD&A. |
| `PRESENT` | `UNCLEAR_START_RULE_APPLIED` | **SOURCED.** The heading-page start rule resolves the start. |
| `PRESENT` | `UNCLEAR_END_MIXED_PAGE_INCLUDED` | **SOURCED.** The mixed last-content page is included. |
| `PRESENT` | `CONDITIONAL_TITLE_CONTEXT_MET` | **PROPOSED.** A P5-B conditional title's frozen context is met. |
| `ABSENT` | `NO_QUALIFYING_BODY_SECTION` | **PROPOSED.** Full review finds neither a qualifying body occurrence nor a narrower absence reason. |
| `ABSENT` | `TOC_ONLY` | **SOURCED.** A TOC entry exists without body content. |
| `ABSENT` | `POINTER_ONLY` | **SOURCED.** A statement that MD&A forms part of the Directors' Report exists without MD&A body content. |
| `ABSENT` | `CONFUSABLE_SECTION_ONLY` | **PROPOSED.** Only a P5-B `NOT EQUIVALENT BUT CONFUSABLE` section is found. |
| `AMBIGUOUS` | `PRESENCE_UNRESOLVABLE` | **PROPOSED.** Evidence cannot resolve presence under the frozen rules. |
| `AMBIGUOUS` | `START_UNRESOLVABLE` | **PROPOSED.** Two or more starts remain admissible. |
| `AMBIGUOUS` | `END_UNRESOLVABLE` | **PROPOSED.** Two or more ends remain admissible. |
| `AMBIGUOUS` | `SPAN_UNRESOLVABLE` | **PROPOSED.** Two or more complete spans remain admissible. |
| `AMBIGUOUS` | `TITLE_CONTEXT_UNRESOLVABLE` | **PROPOSED.** A conditional title's required context cannot be resolved. |

**PROPOSED.** `PRESENT` requires one primary span. `ABSENT` requires no primary,
alternative, or admissible span. `AMBIGUOUS` requires no primary span and at least one
admissible span; when presence itself is uncertain, the admissible interval(s) encode the
present interpretation and `PRESENCE_UNRESOLVABLE` records that absence is also
admissible.

## 4. Numbered Q7 edge-case rules

### Rule 1 — ABSENT

**SOURCED.** A TOC entry alone does not establish presence. A statement such as “forms
part of Directors' Report” alone does not establish presence. Record `ABSENT` with
`TOC_ONLY`, `POINTER_ONLY`, or the more general applicable absence code
(`docs/governance/AUTHOR_RATIFICATION_2026-09-26.md:342-344`).

**PROPOSED.** “Full review” means reviewing the complete thumbnail sequence, following
any TOC or pointer destination, using approved in-PDF search where available, and
visually checking candidate body pages. Log all aids used.

### Rule 2 — Multiple spans

**SOURCED.** Primary is the full English MD&A; every other occurrence is recorded in
`alternative_spans` with its positional `alternative_span_type`
(`docs/governance/AUTHOR_RATIFICATION_2026-09-26.md:346-348`).

**PROPOSED.** Do not union separate occurrences into one span unless rule 4 establishes
that they are one non-contiguous occurrence. Record each separate copy or candidate in
document order.

### Rule 3 — Bilingual

**SOURCED.** The English MD&A is primary. The Hindi copy is separately listed with its
pages and `alternative_span_type = HINDI_COPY`; set `bilingual`
(`docs/governance/AUTHOR_RATIFICATION_2026-09-26.md:350-352`).

**PROPOSED.** Do not merge the two language copies. If the English and Hindi material
alternate within a single inseparable span, use the hull, list the other-language page
set as alternatives where representable, set `bilingual_interleaved`, and use
`AMBIGUOUS` only if a primary span remains genuinely unresolvable.

### Rule 4 — Non-contiguous

**SOURCED.** Record the smallest contiguous hull covering the qualifying MD&A occurrence
as `primary_span`; list every non-MD&A page strictly inside that hull in ascending order
as `gap_pages` (`docs/governance/AUTHOR_RATIFICATION_2026-09-26.md:354-356`).

**PROPOSED.** A gap page must lie strictly between the hull endpoints. Pages before or
after the hull are never gap pages. Set `noncontiguous_hull`.

### Rule 5 — Embedded in Directors' Report

**SOURCED.** Record only the MD&A subsection span, not the complete Directors' Report,
and record the parent section (`docs/governance/AUTHOR_RATIFICATION_2026-09-26.md:358-360`).

**PROPOSED.** Use `parent_section = "Directors' Report"` as the controlled identity and
preserve the visibly printed parent heading separately in `structured_provenance` if it
differs.

### Rule 6 — Annexure

**SOURCED.** A qualifying MD&A annexure counts as MD&A; record its annexure identity. The
approved legal basis is Clause 49 / LODR Regulation 34(2)(e) / Schedule V, under which
MD&A may form part of, or be an addition to, the Directors' Report
(`docs/governance/AUTHOR_RATIFICATION_2026-09-26.md:362-364`).

**PROPOSED.** Record the printed annexure identifier verbatim in `annexure_identity`, set
`annexure`, and apply the same start/end rules as for a non-annexure occurrence.

### Rule 7 — Unclear start

**SOURCED.** Start on the first page carrying the qualifying MD&A heading. If substantive
content starts later, record both pages (`docs/governance/AUTHOR_RATIFICATION_2026-09-26.md:366-368`).

**PROPOSED.** Put the heading page in `primary_span.start`, record it as
`heading_start_page`, record the later page as `substantive_start_page`, and set
`unclear_start`. A decorative section-opening page is therefore included.

### Rule 8 — Unclear end

**SOURCED.** End on the last page with MD&A content before the next section heading. A
mixed page is included and flagged (`docs/governance/AUTHOR_RATIFICATION_2026-09-26.md:370-372`).

**PROPOSED.** Record that page as `last_content_page` and `mixed_end_page`; record the
next visible sibling heading page as `next_section_heading_page`. If the next heading is
on the following page, the last MD&A page remains the end and no mixed-page flag is set.

### Rule 9 — Unresolvable

**SOURCED.** Use `AMBIGUOUS`, record the reason and admissible spans, and make the
ambiguity decision before seeing any system output
(`docs/governance/AUTHOR_RATIFICATION_2026-09-26.md:378-380`).

**PROPOSED.** Exhaust the written rules and approved aids, then record every still-
admissible inclusive span without ranking them. Do not consult a developer, prediction,
previous label, or evaluation artifact. The adjudicator may resolve A/B disagreement but
may preserve `AMBIGUOUS` when the source itself does not support one span.

## 5. Unusual titles — P5-B placeholder

**SOURCED.** An unusual title counts only if it appears on a title-equivalence list made
by blind reading of FIT PDFs before consulting ARPipe patterns
(`docs/governance/AUTHOR_RATIFICATION_2026-09-26.md:374-376`).

**PROPOSED.** `docs/phase5/TITLE_EQUIVALENCE_v0.md` will be supplied byte-for-byte by the
independent P5-B session. Until that file exists, passes blindness checks, and is
formally incorporated at protocol freeze, **no title-equivalence list is defined here**.
The future list's `EQUIVALENT`, `CONDITIONAL`, and `NOT EQUIVALENT BUT CONFUSABLE`
classifications must be applied exactly; this document must not add unseen titles.

## 6. Legacy or corrupted boundary heading

**SOURCED.** Legacy is a research attribute, the operational route remains
`broken_text -> OCR`, and later Phase 9 checks cover corrupted-heading and bilingual-copy
boundary failures (`docs/governance/CURRENT_DECISIONS.md:35`; B1).

**PROPOSED.** Set the image-only flag
`legacy_or_corrupted_boundary_heading` only when the rendered page image shows that a
start or end boundary heading is visibly corrupted, substituted, missing glyphs, or
otherwise unreadable. Base the flag on pixels visible in the approved viewer, not on
extracted characters, font inspection, code, route metadata, or OCR output. Log the
physical page in `structured_provenance.flag_pages`.

**PROPOSED.** This flag does not choose `NATIVE`, `OCR`, `REMAP`, or any other route and
does not change the presence or span rule. It is diagnostic metadata only.

## 7. Permitted aids and logging

**PROPOSED.** The annotation workstation is offline and may contain only the assigned
PDFs, the frozen protocol/title list, the offline annotation form, and its blank/output
record directory. Permitted aids are:

- **PROPOSED.** an offline PDF viewer;
- **PROPOSED.** physical-page thumbnails;
- **PROPOSED.** in-PDF text search supplied by that viewer;
- **PROPOSED.** bookmark/outline navigation;
- **PROPOSED.** zoom, rotate, and fit-page controls;
- **PROPOSED.** the viewer's page-count display.

**PROPOSED.** No OCR engine, generative assistant, web search, external annual report,
repository tool, custom heading finder, script, regex, or prior annotation is an approved
aid. A new aid requires a protocol revision before use across the full future procedure.

**PROPOSED.** For each document record `aids_used`, viewer name/version, search queries
verbatim, pages reached through bookmarks, started/completed timestamps, protocol hash,
PDF hash verification result, and any aid failure. Timestamps are audit fields only, not
scientific variables.

## 8. Information barriers and isolated workspace

**SOURCED.** Q3/Q4 require independent annotation with no ARPipe output and no repository
access (`docs/governance/AUTHOR_RATIFICATION_2026-09-26.md:228-252,258-274`).

**PROPOSED.** The annotation workspace must not mount, copy, search, or expose the ARPipe
repository. At minimum it excludes all paths matching or naming:

- **PROPOSED.** `labels*.csv` and `labels_*_queue.csv`;
- **PROPOSED.** `eval_report*.md`, including `arpipe/eval_report.md`;
- **PROPOSED.** `eval_holdout_log.csv` and `live_eval_report.md`;
- **PROPOSED.** `reports/pm2_2_page_input_snapshot.csv`;
- **PROPOSED.** the P33 prediction-bearing fixture;
- **PROPOSED.** `pm1_*_run/` outputs and their manifests/logs;
- **PROPOSED.** every `reports/pm1_*` and `reports/pm2_*` artifact;
- **PROPOSED.** `docs/identity/evidence/**/result.json`,
  `docs/identity/evidence/**/execution.json`, and preserved run manifests;
- **PROPOSED.** any file or directory whose purpose or name indicates predictions,
  evaluation, scoring, Gold, labels, model output, or run output;
- **PROPOSED.** prediction hashes and seal-holder materials.

**VERIFIED.** The additional named paths above were found using filename/path listing and
existing documentation only. Their contents were not opened for protocol drafting.

**PROPOSED.** Workspace preparation is verified by a custodian who is not an annotator:
copy only the approved PDFs, frozen method files, and offline tool; record a manifest of
those files; confirm no network and no repository mount; then hand the workspace to the
annotator. The annotator signs the access attestation in the record provenance.

## 9. Annotator briefing

**PROPOSED.** **Annotator A and Annotator B** must not access the repository, ARPipe
outputs, predictions or hashes, labels, reports, scores, the other annotator's record,
adjudication material, or external title sources. They annotate independently from the
same frozen protocol and PDF bytes.

**PROPOSED.** **The second annotator** must additionally not receive the developer/
author's notes, labels, candidate pages, search history, or verbal hints. Assignment
metadata may identify only the document and approved source hash.

**SOURCED.** **The adjudicator** is neither the developer nor an annotator on the document
concerned. Before adjudication completes, the adjudicator may access only the frozen Gold
rules, the independent A and B records, the source PDF/pages necessary to resolve the
disagreement, and the adjudication form. The adjudicator must not access predictions,
prediction hashes, evaluation reports, C1 scores, HOLDOUT system outputs, repository
contents, or prior ARPipe labels/predictions
(`docs/governance/CURRENT_DECISIONS.md:27,64-68`).

## 10. Record lifecycle

**SOURCED.** Raw A/B records are immutable; agreement is computed from raw records; and
disagreements go to the separate adjudicator with reasons
(`docs/governance/CURRENT_DECISIONS.md:28`).

**PROPOSED.** On submission, serialize each raw record, validate it against
`gold_schema_v0.json`, hash-seal it, and make it read-only. Corrections are new superseding
records; the original bytes and hash remain preserved. Never overwrite a raw record.

**PROPOSED.** Compare A and B only after both raw records are sealed. Create an
adjudicated record only after disagreement handling. The adjudicated record references
the two raw hashes in `structured_provenance`; it does not replace them and is never used
to calculate raw agreement.

**PROPOSED.** Any protocol revision after the FIT pilot receives a new version/hash,
documents the observation and consistent change, and applies to the entire future Gold
procedure before freeze. No document-specific exception is permitted.

## 11. Decisions consumed and explicit deferrals

| Decision | Consumed operative line |
|---|---|
| D1 / PG-1 | **SOURCED.** START-END localization is the primary bounded claim; Phase 4's condensed wording is operative (`docs/phase4/PHASE4_B1_B8_TRIAGE.md:18`; `docs/governance/CURRENT_DECISIONS.md:24`). |
| Q1b | **SOURCED.** Pre-freeze development uses FIT/VALIDATION; no system change follows final freeze before HOLDOUT scoring (`CURRENT_DECISIONS.md:25`). |
| Q2 | **SOURCED.** FIT supports rules/pilot; VALIDATION is development; HOLDOUT is the headline (`CURRENT_DECISIONS.md:26`). |
| Q3, Q4, B6 | **SOURCED.** Independent roles, full HOLDOUT double annotation, VALIDATION overlap, immutable raw records, separate adjudication (`CURRENT_DECISIONS.md:27-28,40`). |
| Q5, B8 | **SOURCED.** Prediction-first sealing and blind Gold sequence (`CURRENT_DECISIONS.md:29,42`). |
| Q6 | **SOURCED.** Present/absent/ambiguous and failure handling inform the record states (`CURRENT_DECISIONS.md:30`). |
| Q7 | **SOURCED.** Edge rules and 0-based physical page convention (`CURRENT_DECISIONS.md:31`). |
| Q8 | **SOURCED.** Census framing constrains later reporting, not annotation (`CURRENT_DECISIONS.md:32`). |
| Q9 | **SOURCED.** HOLDOUT is historically exposed and must not be described as unseen (`CURRENT_DECISIONS.md:33`). |
| B1 | **SOURCED.** Legacy is diagnostic, not a new annotation route (`CURRENT_DECISIONS.md:35`). |
| B4 note | **SOURCED.** VALIDATION overlap uses a new mechanically specified selector (`CURRENT_DECISIONS.md:38,53`). |
| CC-4 | **SOURCED.** Page-span IoU and boundary endpoints determine fields needed later (`CURRENT_DECISIONS.md:46`). |

**SOURCED.** B3, the historical B4 Oracle, B5, B7, C2, As-Is, the Q10 recipe, and C4
remain outside this protocol. No rule above resolves them
(`docs/governance/CURRENT_DECISIONS.md:34,37-39,41,43,45`).

**PROPOSED.** No annotation may begin under this v0 draft. P5-B, independent rules review,
author review, the FIT pilot, documented consistent revision, applicable author
ratification, and an explicit freeze remain prerequisites.
