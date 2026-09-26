# ARPipe FIT Gold-method pilot plan v0

**Document status:** `DRAFT_PENDING_PILOT`

**PROPOSED.** This is a plan for a later P5-C session. It does not select documents,
open PDFs, annotate, adjudicate, revise the protocol, or construct Gold.

**PROPOSED.** Every substantive paragraph or table row is prefixed with one of
`VERIFIED`, `SOURCED`, `DERIVED`, `INFERRED`, or `PROPOSED`. Headings, constants,
pseudocode, and citations inherit the nearest explicit label.

## 1. Purpose and prerequisites

**SOURCED.** FIT may be used for rules, pilot, and error analysis; it is never pooled into
the HOLDOUT headline (`docs/governance/CURRENT_DECISIONS.md:26`; Q2).

**PROPOSED.** The pilot tests protocol usability, independent reproducibility, schema
fit, and offline-tool friction. It is diagnostic evidence for revision before freeze,
not an accuracy evaluation and not an optimization set for ARPipe.

**PROPOSED.** P5-C may begin only after: P5-A drafts are committed; the independent P5-B
title list has been transferred byte-for-byte; an independent rules reviewer has read
the protocol and title list; the author has reviewed the open draft questions; and both
annotators have isolated offline workspaces.

## 2. Pilot size and roles

**PROPOSED.** Select exactly **10 FIT documents**, within the required 8-12 range, from
exactly 5 issuers with 2 documents per selected issuer. Both Annotator A and Annotator B
independently annotate all 10. Neither sees the other's records or ARPipe output.

**SOURCED.** A separate person adjudicates and is neither the developer nor an annotator
on the documents concerned (`docs/governance/CURRENT_DECISIONS.md:27`; Q3). Pilot
adjudication may diagnose rule ambiguity but cannot manufacture agreement or alter raw
records.

**PROPOSED.** Roles are: pilot custodian (prepares isolated bytes and mechanical roster),
Annotator A, Annotator B, separate adjudicator, independent rules reviewer, and author/
method owner. One person may not combine roles where Q3 prohibits it.

## 3. Source roster and permitted metadata

**PROPOSED.** The sole selection roster is
`dataset/corpus_freeze/development_manifest.csv`, filtered to rows whose exact `split`
value is `FIT`. Consume only `document_id`, `company_id`, `fiscal_year`, `pdf_sha256`,
`split`, and `condition_coverage_summary`.

**VERIFIED.** At the P5-A start commit this roster has 60 FIT rows, 18 distinct
`company_id` values, and fiscal years ranging from 2012 to 2025. These values are
reported facts, not hard-coded selector constants.

**PROPOSED.** Permitted known metadata are identifier, issuer, fiscal year, source hash,
FIT membership, and the already-frozen condition-summary tokens. Do not use document
content, ARPipe predictions, eventual Gold labels, prior labels, evaluation output,
heading matches, candidate pages, scores, or hand inspection.

## 4. Pre-registered mechanical selection

**PROPOSED.** Use SHA-256, strict UTF-8, the ASCII-only identifier normalization, and the
same malformed/duplicate-row rejection rules as
`DOCUMENTGOLD_SELECTOR_v0.md`. Stop rather than repair if fewer than 5 issuers have at
least 2 distinct FIT fiscal years.

**PROPOSED.** Parse `fiscal_year` only if it is exactly four ASCII digits and represents
an integer from `1000` through `9999`; reject the complete selection otherwise. Serialize
it in the year-tie preimage as those same four digits, with no sign or whitespace.

**PROPOSED.** Use these exact new domain tags, none of which is an ARPipe production or
Oracle rank:

```text
arpipe-phase5-fit-pilot-hard-issuer-v1
arpipe-phase5-fit-pilot-issuer-v1
arpipe-phase5-fit-pilot-year-tie-v1
```

**PROPOSED.** A hash preimage is `UTF8(domain) || 0x00 || UTF8(company_id)`, except the
year-tie preimage, which is `UTF8(domain) || 0x00 || UTF8(company_id) || 0x00 ||
UTF8(decimal_fiscal_year) || 0x00 || UTF8(document_id)`. Rank SHA-256 digest bytes
ascending with normalized identifier UTF-8 bytes as the final tie-breaker.

**PROPOSED.** The predeclared hard/uncertain proxy token set is:

```text
annexure
bilingual
broken_text
hidden_text
image_heavy
legacy_font_candidate
mixed_page_sizes
toc_absent
```

**PROPOSED.** Tokenize `condition_coverage_summary` by semicolon, trim ASCII spaces from
each token, and compare exact lowercase strings. These are roster proxies only; they do
not establish a Gold edge case and must not be reported as verified document properties.

**PROPOSED.** Selection algorithm:

1. **PROPOSED.** For every issuer having at least two distinct FIT fiscal years, define
   its two-document year-spread pair as one document from its minimum fiscal year and one
   from its maximum fiscal year. If a boundary year has multiple documents, choose the
   lowest year-tie digest. This mechanically maximizes within-issuer fiscal-year spread.
2. **PROPOSED.** Mark a pair `hard_proxy = true` if either selected document has at least
   one token in the proxy set.
3. **PROPOSED.** If any eligible pair is `hard_proxy = true`, select the lowest
   hard-issuer digest among those issuers as the first issuer. If none is available,
   select no reserved hard issuer and record `HARD_PROXY_NOT_AVAILABLE`.
4. **PROPOSED.** Rank every remaining eligible issuer by the ordinary issuer digest and
   take the first issuers until 5 distinct issuers are selected. If no hard issuer was
   available, take the first 5 by ordinary issuer digest.
5. **PROPOSED.** Emit each selected issuer's two year-spread documents, ordered by issuer
   digest then fiscal year then document ID. The result is exactly 10 documents from 5
   issuers.

**PROPOSED.** This mechanism provides multiple issuers, explicit year spread, and—where a
pre-existing proxy makes it mechanically feasible—at least one hard/uncertain candidate.
No document may be substituted after inspection. If validation fails, stop P5-C and
revise/freeze the selection specification before any PDF is opened.

**PROPOSED.** P5-C records source-roster hash, algorithm document hash, selected roster,
all selection digests, normalized inputs, PDF hashes, and execution environment. The
selection roster is fixed before either annotator receives a PDF.

## 5. Offline tool and annotation procedure

**PROPOSED.** The annotation tool is offline, has no repository access, records 0-based
physical page indices, validates `gold_schema_v0.json`, and writes raw A/B records to
separate locations inaccessible to the other annotator.

**PROPOSED.** For each document the custodian verifies PDF SHA-256, then each annotator:

1. **PROPOSED.** starts the audit timer and records viewer/tool versions;
2. **PROPOSED.** reviews thumbnails, TOC/bookmarks, body, and approved search results;
3. **PROPOSED.** applies the frozen draft protocol/title list without developer help;
4. **PROPOSED.** submits one schema-valid raw record and stops the timer;
5. **PROPOSED.** seals the record; does not revise it after seeing the other record.

**PROPOSED.** The custodian compares records only after both are sealed, calculates raw
agreement measures from `SAP_v0.md`, and sends disagreements plus necessary source pages
to the separate adjudicator under the information barrier.

## 6. Measurements

**PROPOSED.** Measure and report, without pooling the pilot into any later accuracy
result:

- **PROPOSED.** minutes per document and per annotator (median, range, and raw values);
- **PROPOSED.** A-minus-B signed start and end differences plus exact and +/-1 agreement;
- **PROPOSED.** presence-state counts and raw prevalence of `ABSENT` and `AMBIGUOUS`;
- **PROPOSED.** raw-record counts of embedded, annexure, bilingual, multi-span,
  non-contiguous, unclear-boundary, and legacy/corrupted-heading flags;
- **PROPOSED.** rule-by-rule invocation and agreement for every numbered Q7 rule;
- **PROPOSED.** schema validation errors, fields needing free-text workarounds, and
  impossible/unclear invariants;
- **PROPOSED.** tool failures, search/viewer limitations, wrong-page-index attempts,
  save/seal friction, and workspace-isolation incidents;
- **PROPOSED.** adjudication reasons and whether the source or the written rule caused
  each disagreement;
- **PROPOSED.** any title-list item whose classification/context could not be applied
  reproducibly.

**PROPOSED.** A zero count is a result and remains visible. The roster condition proxy is
reported separately from what annotators actually observe.

## 7. Diagnostic revision rules

**PROPOSED.** Pilot observations may motivate a protocol, schema, title-list reference,
tool, or SAP revision. Every proposed revision must identify the observation, affected
rule/field, general wording change, scientific effect, and whether all future documents
receive the same treatment.

**PROPOSED.** Do not alter a rule selectively to improve agreement on one pilot document,
optimize the protocol to a PDF, add an unseen title from general knowledge, or consult
ARPipe behavior. Apply every accepted revision consistently to the entire future Gold
procedure before freeze and preserve a change log.

**PROPOSED.** After a material revision, use only mechanically selected fresh FIT cases
if a retest is required. Do not erase the initial pilot. A retest rule and fresh selector
must be documented before additional PDFs are opened.

## 8. Pre-freeze decision sheet

**PROPOSED.** The following sheet must be completed from pilot evidence and rules review.
Blank or unresolved blocking rows prevent freeze.

| Item to settle | Evidence required | Freeze outcome field |
|---|---|---|
| Title list usability | **PROPOSED.** Every invoked `EQUIVALENT`/`CONDITIONAL`/confusable entry has a reproducible application record. | `ACCEPT / REVISE / BLOCK` + reason |
| Presence decision | **PROPOSED.** All A/B state disagreements are reason-coded; protocol versus source ambiguity is distinguished. | final state rules/version |
| Start rule | **PROPOSED.** Heading versus substantive-start cases fit boundary fields without oral clarification. | final wording + example |
| End rule | **PROPOSED.** Mixed-page and next-heading cases fit boundary fields without oral clarification. | final wording + example |
| Multiple/bilingual/non-contiguous | **PROPOSED.** Primary, alternatives, types, and gaps have one consistent encoding. | final encoding |
| Embedded/annexure | **PROPOSED.** Parent/identity fields and qualifying rule are usable. | final encoding |
| Ambiguity | **PROPOSED.** Annotators can assign `AMBIGUOUS` and admissible spans before output without forced certainty. | final codes/rule |
| Legacy/corrupted flag | **PROPOSED.** Image-only flag can be applied without routing/OCR inference. | keep/revise/remove diagnostic field |
| Schema | **PROPOSED.** Every raw/adjudicated pilot record validates; any out-of-schema fact is dispositioned. | schema version/hash |
| Agreement calculations | **PROPOSED.** Raw-only measures run with declared denominators and non-estimable handling. | SAP version/hash |
| Tool | **PROPOSED.** 0-based pages, independent storage, hashing, offline operation, and audit logs work. | tool version/hash |
| Workload | **PROPOSED.** Observed minutes/document support a documented staffing schedule without changing scientific rules. | schedule/capacity note |
| Information barrier | **PROPOSED.** No repository, prediction, prior-label, internet, or cross-annotator access occurred. | signed attestation |
| Revisions | **PROPOSED.** Every accepted change is logged and generalized; rejected changes have reasons. | revision-log hash |
| Independent review | **PROPOSED.** Rules reviewer closes or explicitly blocks every comment. | review record/hash |
| Author-controlled items | **PROPOSED.** Interval sensitivity and C1-D1 amendment receive required pre-HOLDOUT author action. | author record references |

## 9. Stop boundary

**PROPOSED.** P5-C stops after FIT pilot evidence, adjudication diagnostics, revision
proposals, and the completed decision sheet. It does not annotate VALIDATION/HOLDOUT,
execute the DocumentGold selector, construct final Gold, score C1, run C4, or freeze a
system by implication.

## 10. Decisions consumed and deferrals

**SOURCED.** D1/PG-1 defines the span-localization purpose; Q1b/Q2 permit FIT development;
Q3/Q4/B6 define independent annotators/adjudicator and raw records; Q7 supplies the
rules; B1 supplies a later diagnostic concern; and CC-4 supplies agreement-compatible
boundary measures (`docs/governance/CURRENT_DECISIONS.md:24-28,31,35,40,46`).

**SOURCED.** Q5/B8, Q6, Q8, Q9, and the B4 note constrain what must be settled before the
future HOLDOUT process but are not executed by this pilot.

**SOURCED.** B3, the historical B4 Oracle, B5, B7, C2, As-Is, Q10's recipe, and C4 remain
deferred and cannot be activated by pilot observations.
