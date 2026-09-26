# ARPipe VALIDATION DocumentGold overlap selector v0

**Document status:** `DRAFT_PENDING_PILOT`

**PROPOSED.** This document specifies, but does not execute, the deterministic Q4 draw
for second-annotator overlap on VALIDATION. No roster output is created by P5-A.

**PROPOSED.** Every substantive paragraph or table row is prefixed with one of
`VERIFIED`, `SOURCED`, `DERIVED`, `INFERRED`, or `PROPOSED`. Headings, pseudocode,
constants, and citations inherit the nearest explicit label.

## 1. Authority and input boundary

**SOURCED.** Q4 requires the author to annotate all VALIDATION documents and the second
annotator to annotate a predeclared random overlap of at least one document per issuer;
raw records remain independent and immutable (`docs/governance/CURRENT_DECISIONS.md:28`).

**SOURCED.** The B4 note requires a **new** mechanically specified Phase 5 DocumentGold
selector and keeps the historical Oracle selector deferred
(`docs/governance/CURRENT_DECISIONS.md:38,53`).

**PROPOSED.** The sole input roster is
`dataset/corpus_freeze/validation_manifest.csv`. Consume only `document_id` and
`company_id`, where `company_id` is the issuer identifier. All other columns are ignored.
Do not consume predictions, labels, Gold, scores, model output, document content,
selection seeds/ranks, or any pre-existing sampling rank.

**VERIFIED.** At the P5-A start commit, the manifest has 48 data rows and 9 distinct
`company_id` values. The selector does not hard-code either count; it recomputes and
validates them from the declared roster when the later authorized draw runs.

## 2. Exact serialization and normalization

**PROPOSED.** Parse the input as RFC 4180 CSV decoded with strict UTF-8. A leading UTF-8
BOM is forbidden. The header must contain exactly one `document_id` column and exactly
one `company_id` column; additional columns are permitted and ignored. Quoting and CRLF/
LF input differences do not affect ranking because hashes are formed from parsed,
normalized identifiers, not raw CSV rows.

**PROPOSED.** Normalize each consumed identifier by this ASCII-only procedure:

1. **PROPOSED.** requiring a string field (CSV fields are strings);
2. **PROPOSED.** removing only leading and trailing U+0020 SPACE characters;
3. **PROPOSED.** rejecting an empty result;
4. **PROPOSED.** requiring every remaining character to match ASCII
   `[A-Za-z0-9._-]` (bytes `0x2D`, `0x2E`, `0x30-0x39`, `0x41-0x5A`, `0x5F`, or
   `0x61-0x7A`); tabs, non-ASCII, slashes, controls, and internal spaces are rejected;
5. **PROPOSED.** preserving case exactly, performing no case-folding or Unicode
   normalization, and encoding the result as strict UTF-8 with no BOM.

**PROPOSED.** Reject the complete draw before ranking if any row is blank or malformed,
has missing/extra CSV fields relative to the header, lacks either required value, has a
normalization error, or violates an identifier constraint. Do not skip or repair a row.

## 3. Roster validation and canonical ordering

**PROPOSED.** Reject the complete draw if:

- **PROPOSED.** no data rows exist;
- **PROPOSED.** two rows have the same normalized `document_id`, even if the issuer is
  also the same (duplicate roster row);
- **PROPOSED.** one normalized document maps to more than one issuer;
- **PROPOSED.** two distinct pre-normalization spellings collapse to the same normalized
  `document_id` or `company_id` (normalization alias collision);
- **PROPOSED.** any issuer has zero eligible documents after validation (which can arise
  only from an implementation defect because issuers are derived from rows).

**PROPOSED.** Repeated `company_id` across different documents is required grouping, not
a duplicate. The validated canonical roster order is ascending normalized
`company_id` UTF-8 byte sequence, then ascending normalized `document_id` UTF-8 byte
sequence. Bytewise order compares unsigned octets from left to right; a strict prefix
sorts before the longer sequence.

## 4. New hash construction

**PROPOSED.** Use SHA-256 and this exact ASCII domain tag:

```text
arpipe-documentgold-validation-overlap-v1
```

**PROPOSED.** This tag is new and is not `arpipe-oracle-double-v1`. For each canonical
row form the exact preimage:

```text
UTF8("arpipe-documentgold-validation-overlap-v1")
|| 0x00
|| UTF8(normalized_company_id)
|| 0x00
|| UTF8(normalized_document_id)
```

**PROPOSED.** `||` means byte concatenation and `0x00` is one NUL octet. Identifier
normalization rejects NUL, so fields are unambiguous. Hash the preimage with SHA-256 and
interpret the 32-byte digest as one unsigned 256-bit big-endian integer solely for
ranking. Retain the lowercase 64-hex digest in the future audit output.

## 5. Ranking and selection

**PROPOSED.** Independently within every issuer, sort rows by:

1. **PROPOSED.** ascending SHA-256 digest bytes (equivalently the unsigned big-endian
   integer);
2. **PROPOSED.** on a digest tie, ascending normalized `document_id` UTF-8 bytes.

**PROPOSED.** Select exactly the first-ranked document per issuer. Thus every issuer has
one selected document and the selection size equals the number of distinct validated
issuers. If an issuer has only one eligible document, select it; do not borrow or add a
document from another issuer.

**PROPOSED.** Do not consume or reuse any historical rank, random number, selection seed,
Oracle membership, document property, or prior draw. Do not promote the second-ranked
document because the first appears easy, hard, absent, ambiguous, or inconvenient. Do
not replace a selection after annotation or inspection.

## 6. Deterministic pseudocode

**PROPOSED.** An independent implementation must be equivalent to:

```text
rows = strict_parse_and_normalize(validation_manifest.csv)
validate_complete_roster(rows)
rows = sort(rows, key=(utf8(company_id), utf8(document_id)))

for row in rows:
    preimage = utf8(DOMAIN) + NUL + utf8(row.company_id) + NUL + utf8(row.document_id)
    row.digest = SHA256(preimage)

for issuer in sort(unique company_id, key=utf8_bytes):
    ranked = sort(rows_for_issuer, key=(digest_bytes, utf8(document_id)))
    emit ranked[0]
```

**PROPOSED.** Future audit output is ordered by issuer UTF-8 bytes and contains only
normalized issuer ID, normalized document ID, digest hex, rank `1`, source-manifest
SHA-256, selector-spec SHA-256, and execution timestamp. The timestamp is provenance only
and cannot affect selection.

## 7. Freeze and execution boundary

**PROPOSED.** Freeze this specification and its hashes before annotation. At the later
authorized draw, record the input-manifest hash, selector document hash, implementation
hash, software/runtime version, complete validation result, issuer count, selection count,
and emitted roster hash.

**PROPOSED.** The historical Phase 2.1 allowlist permits the Phase 5 documentation and an
exact schema-test path under the task's narrow exception, but it does not admit a new
selector implementation path. P5-A therefore supplies the fully executable
specification only; no product selector function or draw is created.

**PROPOSED.** The draw occurs only at protocol freeze. Running the pseudocode now,
calculating row digests now, or recording the selected documents now is prohibited.

## 8. Decisions consumed and deferrals

**SOURCED.** Q4 and B6 define independent VALIDATION overlap; B4-note requires this new
selector; Q3 defines the people; Q1b/Q2 restrict its use to development; and 0c permits a
protocol rather than a new governance ledger
(`docs/governance/CURRENT_DECISIONS.md:23,25-28,38,40,53`).

**SOURCED.** D1/PG-1, Q5/Q6/Q7/Q8/Q9, B1/B8, and CC-4 constrain the later wider Gold and
scoring process but do not enter this selector's bytes or rank.

**SOURCED.** B3, the historical B4 Oracle, B5, B7, C2, As-Is, Q10's recipe, and C4 remain
deferred and are not inputs or outputs of this selector.
