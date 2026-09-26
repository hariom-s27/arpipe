# ARPipe FIT Gold-method pilot plan v0.1

**Document status:** `DRAFT_PENDING_PILOT`

**PROPOSED.** This is a specification for later pilot work. P5-A.1 did not select a
document, open a PDF, build Gold, run the pilot or retest, adjudicate, or revise a method
from results.

## 1. Purpose and prerequisites

**SOURCED.** FIT supports rules, pilot, and error analysis and is never pooled with the
HOLDOUT headline (`docs/governance/CURRENT_DECISIONS.md:26`; Q2).

**PROPOSED.** Before roster execution: P5-T builds and tests the offline annotation tool;
the v0.1 protocol/schema/SAP receive rules review; the viewer name, version, and physical-
page setting are pinned; A1–A5 receive the required author action for their later stage;
and the title-list intake gate below is satisfied.

**PROPOSED.** The title list enters the method only after (i) the intake spot-check meets
its pre-declared acceptance rule—if more than 5% of sampled rows are wrong in page, text
or class, the affected scope is redone—and (ii) the rules review is complete. Annotators
receive only the annotator-facing list; no evidence ledger or P5-B method note enters an
annotation workspace.

## 2. Source frame

**DERIVED.** Construct the roster by joining
`dataset/corpus_freeze/corpus_inventory.csv.company_id` to
`dataset/corpus_freeze/issuer_split.csv.issuer_id`, retaining `split = FIT`, removing IDs
in `dataset/corpus_freeze/development_manifest.csv`, and removing IDs ending `_MISSING`.
Consume only `document_id`, `company_id`, `fiscal_year`, `pdf_sha256`, and derived
`split`. `CORPUS_FRAME_CHECK_v0.md` records **32 documents / 16 issuers**, with all 32
PDF hashes matching. The count is never hard-coded in selection logic.

**PROPOSED.** PILOT is exactly 10 documents: 5 issuers × 2 documents when the frame makes
that feasible. RETEST is a separately fixed, disjoint slice of up to 6 documents from up
to 3 further issuers, 2 per issuer when feasible. No document in either slice may be
replaced after inspection.

## 3. Hard-proxy source

**SOURCED.** T0.1R commit
`879762a2f236b3aaa6df33b7ddacc60c01d633c1` is recorded as promoting the final verified
reconciled artifacts (`docs/experiments/PHASE2_FOUNDATION_INTEGRITY_AUDIT.md:46`), and
`dataset/corpus_gap_audit/reconciled/reconciliation_manifest.json` hashes
`condition_document_map_reconciled.csv`. Therefore the operative proxy source is
`dataset/corpus_gap_audit/reconciled/condition_document_map_reconciled.csv`, not the
top-level preliminary map.

**PROPOSED.** Restrict that map to the already-derived 32 roster IDs, then consume only
rows whose exact status is `CANDIDATE`. The proxy-token set is:

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

**PROPOSED.** These are frozen detector proxies used only for mechanical sampling. They
are not document properties, verified conditions, Gold labels, or prevalence evidence.
In particular, retain both `bilingual` and `legacy_font_candidate`; the frozen detectors
cannot establish FIT bilingual prevalence.

**PROPOSED.** The 60-document DEVELOPMENT subset was constructed for diversity, not FIT
representativeness. Any title or structure counts from that subset must be labelled
DEVELOPMENT-subset counts and never reported as FIT prevalence.

## 4. Mechanical PILOT and RETEST specification

**PROPOSED.** Normalize identifiers with the selector's ASCII rule and reject the whole
operation on a malformed or duplicate row. Require a four-digit `fiscal_year`. Use
SHA-256 and exact domain-separated preimages with NUL delimiters:

```text
arpipe-phase5-fit-pilot-pair-v2
arpipe-phase5-fit-pilot-hard-issuer-v2
arpipe-phase5-fit-pilot-issuer-v2
arpipe-phase5-fit-retest-issuer-v2
```

**PROPOSED.** For each issuer with at least two roster documents, choose the pair with
maximum fiscal-year separation. Resolve boundary-year ties using the lowest
`SHA256(pair-domain || 0x00 || company_id || 0x00 || fiscal_year || 0x00 || document_id)`;
then mark the pair `hard_proxy` when either member has a retained candidate token.

**PROPOSED.** For PILOT, reserve the lowest hard-issuer digest when any hard pair exists,
then fill to five issuers by the ordinary issuer digest, excluding the reserved issuer
from the second ranking. Emit both pair documents per selected issuer. If fewer than five
two-document issuers exist, stop before opening PDFs and revise this specification.

**PROPOSED.** For RETEST, remove every PILOT document and issuer, rank remaining eligible
issuer pairs with the retest domain, and reserve the first three pairs (up to six
documents). If fewer are available, reserve all available pairs and report the count.
This makes PILOT and RETEST disjoint without adapting to pilot results.

**PROPOSED.** The later authorized selector records source hashes, normalized inputs,
all digests, emitted roster, PDF verification, and runtime. This task did not execute any
of these rankings.

## 5. Annotation procedure

**PROPOSED.** Both annotators independently annotate all ten PILOT documents. They enter
the viewer's 1-based physical page numbers with page labels disabled; the tool stores
0-based indices by subtracting one, checks the viewer page count, validates v0.1 records,
and seals separate raw outputs before comparison.

**PROPOSED.** Search is an aid but never sufficient evidence of absence. The annotator
makes a complete thumbnail pass, logs search usability, applies the frozen title list
and rules, and receives no developer hint, repository material, system output, evidence
ledger, or other annotator's record.

## 6. Measurements and predeclared soft triggers

**PROPOSED.** Report time per document, presence-state agreement, boundary differences,
span IoU between raw A/B records, reason/flag agreement, schema/tool failures, rule
invocations, title-list application, viewer/search limitations, and adjudication reasons.
Do not report PILOT as system accuracy.

| Observation | Predeclared action |
|---|---|
| **PROPOSED.** Presence-state disagreement on at least 2 of 10 | `REVISE` the presence rules and use only the reserved RETEST for any retest. |
| **PROPOSED.** Start or end differs by more than one page on at least 3 of 10 | `REVISE` the applicable boundary rule before RETEST. |
| **PROPOSED.** Any submitted record is schema-invalid | `REVISE` the tool before further annotation. |
| **PROPOSED.** Any information-barrier breach | `BLOCK` affected evidence and seek method-owner disposition before continuing. |
| **PROPOSED.** Title intake sample exceeds 5% error in page, text, or class | Redo the affected title-list scope before annotation. |

**PROPOSED.** These are revision triggers, not pass/fail claims about Gold quality.
Preserve the initial raw records; apply accepted changes consistently; never optimize a
rule to one PDF.

## 7. Workload and stop boundary

**PROPOSED.** Planning range: about 20–40 hours for the author and 13–26 hours for
Annotator B across PILOT, RETEST, VALIDATION, and HOLDOUT, assuming 10–20 minutes per
document. PILOT timing replaces this estimate for scheduling, not for scientific rules.

**PROPOSED.** This plan stops after PILOT evidence and, if triggered, the already-reserved
RETEST. It does not annotate VALIDATION/HOLDOUT, execute the DocumentGold overlap draw,
freeze a system, score C1, run C4, or start P5-B work.
