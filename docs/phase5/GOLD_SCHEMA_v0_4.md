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

## Changes in v0.2

The normative v0.2 companion is `docs/phase5/gold_schema_v0_2.json`. Under
`D1_D7_DECISIONS_v0_1.md` §§6–7, v0.2 adds the required constant
`schema_version = "0.2"`; adds ABSENT reasons `NO_ENGLISH_MDA` and
`EXTERNAL_REFERENCE_ONLY`; and permits ABSENT + `NO_ENGLISH_MDA` to retain only
`HINDI_COPY` alternative spans. All other ABSENT records continue to forbid alternative
spans (§7.1, §7.4).

Section 7.2 adds PRESENT-only flags `stub` and `contains_csr_esg`, optional
`stub_word_count` (integer at least zero, or null), and optional `csr_esg_pages` (unique
0-based page integers). A non-null stub count requires the `stub` flag, but the flag does
not require a count. The `contains_csr_esg` flag is equivalent to a non-empty
`csr_esg_pages` list. At tool level, every `csr_esg_pages` entry must lie within
`primary_span` and must not occur in `gap_pages`; these numeric relations are deliberately
not duplicated in JSON Schema.

The BROKEN_TEXT/word-count derivation in §7.3 and the BOUNDARY_ALTERNATIVE protocol
guidance in §7.5 remain outside this revision.

## Changes in v0.3

The normative v0.3 companion is `docs/phase5/gold_schema_v0_3.json`. Under
`D1_D7_DECISIONS_v0_1.md` §8.7 (shared start/end pages, author choice (a)), v0.3 changes
only what is listed below. v0.1 and v0.2 are unchanged and keep validating their own
records: a record's `schema_version` selects its schema (absent = v0.1, `"0.2"`, `"0.3"`)
and no tool tries a second schema. This file is cumulative: sections 1–5 are the v0.1 text,
and the two "Changes" sections add v0.2 and v0.3.

`schema_version` is the constant `"0.3"`. `boundary_evidence` gains two required keys,
`start_page_shared` and `end_page_shared`, each `true`, `false` or `null`. They record the
annotator's judgement that the primary start page, or the primary end page, also carries
text from another section (definition: `GOLD_PROTOCOL_v0_3.md` §4). A `PRESENT` record
requires both to be booleans, never null. An `ABSENT` or `AMBIGUOUS` record requires both
to be null.

The flag enum gains `mixed_start_page`. JSON Schema ties each flag to its answer:
`mixed_start_page` is present exactly when `start_page_shared` is true, and
`mixed_end_page` is present exactly when `end_page_shared` is true.

At tool level, the relations that are numeric or clearer in code are not duplicated in
JSON Schema: `end_page_shared = true` is equivalent to `boundary_evidence.mixed_end_page`
equalling the primary end page, and `end_page_shared = false` is equivalent to
`mixed_end_page` being null. The offline tool sets both flags and `mixed_end_page` from the
two answers, so they cannot disagree, and it refuses a `PRESENT` record until both answers
are Yes or No (no default). It also re-checks the flag/answer coupling, so a hand-edited
record fails with a readable message.

Not settled by §8.7 and therefore not enforced: the value of
`boundary_evidence.mixed_end_page` on `ABSENT` and `AMBIGUOUS` records (the tool writes
null). The SAP use of the two answers (PAGE_LEVEL word counts only when both are false;
descriptive raw A/B agreement) is §8.7's SAP bullet. Scoring dispatches on `schema_version`
as before, accepts `"0.3"`, changes no metric, and adds only a descriptive A/B agreement
on the two answers.

## Changes in v0.4

The normative v0.4 companion is `docs/phase5/gold_schema_v0_4.json`. v0.4 changes only what
is listed below; v0.1, v0.2 and v0.3 are unchanged and keep validating their own records: a
record's `schema_version` selects its schema (absent = v0.1, `"0.2"`, `"0.3"`, `"0.4"`) and
no tool tries a second schema.

`schema_version` is the constant `"0.4"`. `boundary_evidence` gains two required keys,
`start_anchor_text` and `end_anchor_text`, each a string or null. They record the heading
line the annotator copied from a shared boundary page, under the shared-page definition of
`GOLD_PROTOCOL_v0_4.md` §4.

The rules key off the existing `start_page_shared` / `end_page_shared` answers, each
independently: on `start_page_shared = true`, `start_anchor_text` must be a string
containing a non-space character; on `start_page_shared = false`, it must be null. The same
pairing ties `end_anchor_text` to `end_page_shared`. `ABSENT` and `AMBIGUOUS` records
already require both shared-page answers to be null (v0.3), so this same pairing leaves
both anchor fields null there too, with no separate presence-state clause needed.

At tool level: the offline tool takes the anchor text from the form, strips it, and refuses
an empty value when the matching page is marked shared; it writes null and ignores any
value sent when the matching page is not shared. On `ABSENT` and `AMBIGUOUS` records the
tool now forces `boundary_evidence.mixed_end_page` to null unconditionally on
`presence_state`, rather than as an incidental effect of the primary span being absent
(closing the v0.3 open item above). Scoring dispatches on `schema_version` as before,
accepts `"0.4"` under the v0.3 rules plus the anchor rule, changes no metric, and
`shared_page_agreement` counts `"0.4"` records alongside `"0.3"`.
