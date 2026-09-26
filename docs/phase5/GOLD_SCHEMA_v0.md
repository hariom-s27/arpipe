# ARPipe Gold record schema v0

**Document status:** `DRAFT_PENDING_PILOT`

**PROPOSED.** The normative machine-readable companion is `gold_schema_v0.json`. This
document explains its lifecycle and cross-field rules. It neither contains real annual-
report content nor creates Gold.

**PROPOSED.** Every substantive paragraph or table row is prefixed with one of
`VERIFIED`, `SOURCED`, `DERIVED`, `INFERRED`, or `PROPOSED`. Headings, field names,
examples, and citations inherit the nearest explicit label.

## 1. Record types and immutability

**SOURCED.** Raw A/B records are immutable; agreement is computed from raw records only;
and adjudication follows independent annotation (`docs/governance/CURRENT_DECISIONS.md:28`;
Q4).

| Record | `record_type` | `annotator_role` | Lifecycle |
|---|---|---|---|
| Raw A | `RAW` | `ANNOTATOR_A` | **PROPOSED.** Validate, canonicalize, hash, and seal immediately on submission. Never overwrite. |
| Raw B | `RAW` | `ANNOTATOR_B` | **PROPOSED.** Validate, canonicalize, hash, and seal immediately on submission. Never overwrite. |
| Adjudicated | `ADJUDICATED` | `ADJUDICATED_RECORD` | **PROPOSED.** Create only after both raw records are sealed and disagreement handling is complete. |

**PROPOSED.** “Immutable” is a storage/lifecycle property rather than something JSON
Schema alone can enforce. The annotation tool must use write-once records. A correction
creates a new record with an explicit supersession link outside this v0 scientific
record; the original bytes and digest remain available.

**PROPOSED.** A raw record cannot carry any adjudication field. An adjudicated record must
carry `adjudication_status`, non-empty `adjudication_reason`, and
`adjudicator_role = SEPARATE_ADJUDICATOR`. Its provenance must reference exactly two
distinct raw-record SHA-256 values.

## 2. Required scientific and provenance fields

| Field | Meaning |
|---|---|
| `document_id` | **PROPOSED.** Exact frozen-roster identifier; never a display name. |
| `source_pdf_sha256` | **PROPOSED.** Lowercase 64-hex hash of the annotated PDF bytes. |
| `annotator_role` | **SOURCED.** Role only, never a person's name. |
| `presence_state` | **SOURCED.** Exactly `PRESENT`, `ABSENT`, or `AMBIGUOUS`. |
| `presence_reason_code` | **PROPOSED.** One controlled code from the protocol. |
| `primary_span` | **PROPOSED.** Inclusive 0-based physical-page span for `PRESENT`; otherwise `null`. |
| `alternative_spans` | **SOURCED.** Other observed copies/candidates in document order. |
| `alternative_span_type` | **PROPOSED.** Positional type array corresponding one-to-one with `alternative_spans`. |
| `gap_pages` | **SOURCED.** Sorted unique non-MD&A pages strictly inside a non-contiguous primary hull. |
| `flags` | **PROPOSED.** Controlled structural/image-only annotations; never free-text outcomes. |
| `ambiguity_code` | **PROPOSED.** `NONE` unless presence is `AMBIGUOUS`. |
| `admissible_spans` | **SOURCED.** Every still-admissible span for an ambiguous record, fixed before predictions. |
| `parent_section` | **SOURCED.** Parent identity for an embedded subsection, else `null`. |
| `annexure_identity` | **SOURCED.** Printed annexure identity when applicable, else `null`. |
| `boundary_evidence` | **SOURCED.** Heading/substantive-start/last-content/next-heading/mixed-page indices required by Q7 cases. |
| `timestamps` | **PROPOSED.** Audit-only start/completion timestamps. |
| `aids_used` | **PROPOSED.** Controlled list of approved aids actually used. |
| `structured_provenance` | **PROPOSED.** Workspace/viewer/search/access attestations and evidence metadata. |
| `protocol_version_hash` | **PROPOSED.** Lowercase SHA-256 of the frozen protocol bundle identifier defined at freeze. |

**PROPOSED.** `timestamps` are audit/provenance fields only. They are not scientific
variables, never enter an estimand, and must not define a subgroup or exclusion.

## 3. Cross-field invariants

**PROPOSED.** The JSON Schema enforces the principal state invariants:

- **PROPOSED.** `PRESENT` has a non-null primary span, `ambiguity_code = NONE`, and no
  admissible spans;
- **PROPOSED.** `ABSENT` has no primary, alternatives, gap pages, or admissible spans and
  has `ambiguity_code = NONE`;
- **PROPOSED.** `AMBIGUOUS` has no primary span, has a non-`NONE` ambiguity code, and has
  at least one admissible span;
- **PROPOSED.** pages are non-negative integers and SHA-256 strings are lowercase 64-hex;
- **PROPOSED.** raw and adjudicated record fields/roles are structurally distinct.

**PROPOSED.** The offline annotation tool must additionally enforce constraints not
expressed compactly in this schema:

1. **PROPOSED.** every span has `start_page <= end_page` and all pages are below the
   verified physical page count;
2. **PROPOSED.** `alternative_spans` and `alternative_span_type` have identical lengths
   and positional correspondence;
3. **PROPOSED.** `gap_pages`, bookmark pages, and flag pages are numerically sorted;
4. **PROPOSED.** every gap page lies strictly inside the primary hull;
5. **PROPOSED.** unclear-start and unclear-end fields/flags agree with boundary evidence;
6. **PROPOSED.** annexure, embedded, bilingual, and legacy/corrupted flags agree with
   their identity/provenance fields;
7. **PROPOSED.** completed time is not earlier than started time;
8. **PROPOSED.** raw-record hash references appear only in adjudicated provenance and
   reference the matching document/PDF/protocol tuple.

## 4. Controlled flag interpretation

**PROPOSED.** Structural flags describe the Gold source: `multiple_spans`, `bilingual`,
`bilingual_interleaved`, `noncontiguous_hull`, `embedded_in_directors_report`,
`annexure`, `unclear_start`, `unclear_end`, `mixed_end_page`, and
`conditional_title`.

**SOURCED.** `legacy_or_corrupted_boundary_heading` is image-only diagnostic metadata.
It does not define or change an OCR/routing decision; B1 keeps legacy as a research
attribute (`docs/governance/CURRENT_DECISIONS.md:35`).

## 5. Synthetic validation

**VERIFIED.** `tests/test_phase5_gold_schema.py` validates the schema itself and exactly
three wholly synthetic records: one raw A `PRESENT` record, one raw B `AMBIGUOUS` record,
and one `ADJUDICATED` record. The records use invented document IDs, hashes, page spans,
viewer/workspace values, and no annual-report content.

**PROPOSED.** Passing synthetic validation demonstrates structural executability only.
It does not validate the scientific rules, annotation usability, agreement, or Gold
quality; those remain FIT-pilot questions.

## 6. Decisions consumed and deferrals

**SOURCED.** D1/PG-1 supplies the document-span claim; Q3/Q4/B6 supply roles,
independence, immutability, and adjudication; Q6 supplies absence/ambiguity treatment; Q7
supplies the edge-case fields and page convention; B1 supplies the diagnostic-only legacy
flag; and CC-4 supplies downstream endpoint needs
(`docs/governance/CURRENT_DECISIONS.md:24,27-31,35,40,46`).

**SOURCED.** Q1b, Q2, Q5/B8, Q8, Q9, and the B4 note constrain the surrounding process
but do not alter raw field meaning (`docs/governance/CURRENT_DECISIONS.md:25-26,29,32-33,38,42`).

**SOURCED.** B3, the historical B4 Oracle, B5, B7, C2, As-Is, the Q10 recipe, and C4 are
not represented or resolved by this schema.

**PROPOSED.** Freeze requires successful FIT use, documented revisions, independent rules
review, applicable author action, and an explicit version/hash transition from v0.
