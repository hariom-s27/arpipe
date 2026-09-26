# ARPipe Gold record schema v0.1

**Document status:** `DRAFT_PENDING_PILOT`

**PROPOSED.** The normative machine-readable companion is
`docs/phase5/gold_schema_v0_1.json`. This revision is executable but does not create
Gold, authorize annotation, or settle any author-controlled method choice.

## 1. Record lifecycle

**SOURCED.** Q4 requires immutable independent raw A/B records, agreement computed from
those raw records, and separate-person adjudication
(`docs/governance/CURRENT_DECISIONS.md:28`). A raw record is sealed on submission. An
adjudicated record references exactly two distinct raw-record SHA-256 values.

**PROPOSED.** A raw record may be superseded only by its own annotator, with a reason,
before the A/B comparison is run. The original bytes and hash remain preserved. After
comparison there is no supersession; only a separately stored adjudicated record may be
created.

## 2. v0.1 fields and conventions

| Field | v0.1 rule |
|---|---|
| `document_id` | **PROPOSED.** Non-empty ASCII `[A-Za-z0-9._-]+`, matching selector normalization. |
| `presence_state` | **SOURCED.** Exactly `PRESENT`, `ABSENT`, or `AMBIGUOUS`. |
| `presence_reason_code` | **PROPOSED.** `PRESENT` uses only `BODY_QUALIFYING_TITLE` or `CONDITIONAL_TITLE_CONTEXT_MET`; structural cases are flags. `ABSENT` includes `NOT_AN_ANNUAL_REPORT`. |
| `primary_span` | **SOURCED.** Inclusive 0-based physical-page span for `PRESENT`; otherwise null. |
| `alternative_spans` | **PROPOSED.** Array of self-contained `{start_page, end_page, type}` objects; the v0 parallel type array is removed. |
| `gap_pages` | **SOURCED.** Sorted unique non-MD&A pages strictly inside a non-contiguous hull. |
| `viewer_start_page_1based`, `viewer_end_page_1based` | **PROPOSED.** Optional audit copies of the physical 1-based values entered from the viewer. |
| `viewer_page_convention` | **PROPOSED.** Required provenance constant `VIEWER_PHYSICAL_1_BASED_STORED_ZERO_BASED`. |
| `search_usable` | **PROPOSED.** Records whether viewer search was usable; search alone can never establish absence. |
| timestamps | **PROPOSED.** Audit-only RFC-3339-like strings; never an analysis variable. |

**SOURCED.** Stored and scored page boundaries remain 0-based physical page indices as
required by Q7. **PROPOSED.** The annotation tool takes the viewer's physical page number
with page labels disabled and stores `page_index_0based = viewer_page_1based - 1`. It
must reject a viewer page count that differs from verified PDF metadata.

## 3. Cross-field invariants

**PROPOSED.** The JSON Schema enforces all of the following:

- **PROPOSED.** `PRESENT` has a primary span, `ambiguity_code = NONE`, no admissible
  spans, and a PRESENT reason code.
- **PROPOSED.** `ABSENT` has no primary, alternative, gap, or admissible span and uses an
  ABSENT reason, including `NOT_AN_ANNUAL_REPORT` when applicable.
- **PROPOSED.** `AMBIGUOUS` has no primary, has a non-`NONE` ambiguity code, and has at
  least one admissible span.
- **PROPOSED.** A non-empty `gap_pages` list is equivalent to the
  `noncontiguous_hull` flag.
- **PROPOSED.** A non-null `annexure_identity` is equivalent to the `annexure` flag, and
  a non-null `parent_section` is equivalent to `embedded_in_directors_report`.
- **PROPOSED.** Raw records cannot contain adjudication fields; adjudicated records must
  contain their status, reason, separate-adjudicator role, and two raw-record hashes.

**PROPOSED.** The offline tool additionally checks numeric relations that are clearer in
code: `start <= end < physical_page_count`, every gap lies strictly inside its hull,
viewer-to-stored subtraction is exact, ordered lists are sorted, completion is not before
start, and referenced raw records match document, PDF, and protocol identities.

## 4. Synthetic validation

**VERIFIED.** `tests/test_phase5_gold_schema.py` retains the original v0 test and its
three synthetic records unchanged. It adds three corresponding v0.1 valid records and
ten must-fail records: PRESENT/null span, ABSENT/span, AMBIGUOUS/no admissible span,
RAW/adjudication field, adjudicated/no raw refs, malformed hash, malformed timestamp,
invalid identifier, annexure/no identity, and gap/no hull flag.

**VERIFIED.** The installed `jsonschema` `FormatChecker` does not register a `date-time`
checker in this environment, as proved by the first focused test run. The v0.1 schema
therefore also uses an explicit timestamp pattern; the malformed-timestamp record then
fails without editing frozen requirements.

## 5. Decisions and limits

**SOURCED.** Q3/Q4/B6 govern roles and immutability; Q6 governs state treatment; Q7
governs edge cases and physical pages; B1 keeps legacy/corruption diagnostic-only; CC-4
determines the downstream boundary fields.

**PROPOSED.** This schema does not settle the interval method, A1–A5, the viewer product
and version, the title-list intake, a PDF content judgment, or scoring. It has not been
used on corpus records. No prohibited prediction, label, P5-B evidence, or PDF content
was consulted in producing it.
