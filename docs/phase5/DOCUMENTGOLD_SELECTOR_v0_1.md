# ARPipe VALIDATION DocumentGold overlap selector v0.1

**Document status:** `DRAFT_PENDING_PILOT`

**PROPOSED.** This document and `tools/phase5/documentgold_selector.py` specify the Q4
VALIDATION overlap draw. They do not run the real draw, read the real roster, create a
salt, or create Gold.

## 1. Authority and scope

**SOURCED.** Q4 requires a predeclared random second-annotator overlap of at least one
VALIDATION document per issuer. The B4 note requires a new Phase-5 selector and keeps the
historical Oracle selector deferred (`docs/governance/CURRENT_DECISIONS.md:28,38,53`).

**PROPOSED.** The future caller supplies parsed rows containing `document_id` and
`company_id` from `dataset/corpus_freeze/validation_manifest.csv`. Predictions, Gold,
labels, document content, HOLDOUT membership, Oracle artifacts, ranks, timestamps, and
all other fields are forbidden selector inputs.

## 2. Normalization and validation

**PROPOSED.** Each input is a string; remove only leading/trailing U+0020 spaces, reject
empty values, and require `[A-Za-z0-9._-]+`. Preserve case and encode strict UTF-8. Reject
invalid rows, duplicate normalized document IDs, a document mapped twice, and raw
spellings that collapse to the same normalized issuer or document. Do not skip or repair
a row.

**PROPOSED.** `documents_per_issuer` is a future method input. Its default is one. If two
is selected at method freeze, every issuer must have two eligible documents or the draw
fails closed. The open one-versus-two choice is A3 and is not decided here.

## 3. Commit–reveal

**PROPOSED.** Before any VALIDATION annotation, the independent seal holder generates a
cryptographically random 32-byte salt outside this implementation and publishes only
`SHA-256(salt)` as 64 lowercase hex characters. The salt stays secret until the author
has sealed every VALIDATION raw record. After reveal, the implementation verifies the
commitment and reproduces the draw.

**PROPOSED.** The exact ASCII domain is:

```text
arpipe-documentgold-validation-overlap-v2
```

**PROPOSED.** For each normalized row compute:

```text
SHA256(domain || 0x00 || salt || 0x00 || company_id || 0x00 || document_id)
```

**PROPOSED.** Within each issuer, order by digest bytes then `document_id` UTF-8 bytes
and take the requested prefix. Emit issuers in `company_id` UTF-8 byte order. This gives
determinism, domain separation, and at least one selected document per issuer while the
commitment prevents the author from knowing the overlap during annotation.

## 4. Pure implementation and audit

**VERIFIED.** `select_overlap` has no file, network, random, environment, clock, or other
I/O. Its only data inputs are the roster argument, revealed salt, and declared per-issuer
count. It returns normalized identities, lowercase digest, and within-issuer rank.

**VERIFIED.** `tests/test_phase5_documentgold_selector.py` uses an invented roster only.
It tests commitment verification, order-invariant determinism, one-per-issuer coverage,
the two-per-issuer fail-closed rule, invalid and aliasing identifiers, duplicate document
IDs, and salt length. It never reads `validation_manifest.csv`.

**PROPOSED.** At future execution, record the roster hash, specification hash,
implementation hash, commitment, later revealed salt, runtime version, validation
result, issuer count, selection count, and output hash. The salt itself must not be
committed before reveal. Two independent reproductions are required.

## 5. Execution boundary and open decisions

**PROPOSED.** A3 (one versus two per issuer) and A4 (author confirmation of this
commit–reveal design) remain unsigned. `AUTHOR: ______` `DATE: ______`. No real selector
draw, salt, VALIDATION overlap, HOLDOUT operation, or Oracle roster was produced in
P5-A.1.

**SOURCED.** This implementation path and its exact test path are admitted under
CURRENT_DECISIONS 0c and review item D3. No broader allowlist was added.
