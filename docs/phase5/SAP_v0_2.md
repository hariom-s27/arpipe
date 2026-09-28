# ARPipe C1 Statistical Analysis Plan v0.2

> **What changed from v0.1.** This revision applies
> `docs/phase5/decisions/D1_D7_DECISIONS_v0_1.md` §§1 and 6–7: it fixes presence
> treatment for the new absence reasons, predeclares D3 start reporting and descriptive
> strata, and adds page-exclusion and reversible-boundary sensitivities.

**Document status:** `DRAFT_PENDING_PILOT`

**PROPOSED.** This is a pre-scoring draft. It reports no result, authorizes no HOLDOUT
access, and intentionally leaves the interval sensitivity method unsigned.

## 1. Populations and Gold states

**SOURCED.** HOLDOUT is the single headline census: 54 documents, 9 issuers × 6.
VALIDATION is separate and labelled a development check; FIT supports rules, PILOT, and
error analysis (`docs/governance/CURRENT_DECISIONS.md:26`; Q2).

**PROPOSED.** Before outputs are opened, assign adjudicated records to `H_PRESENT`
(PRESENT with valid primary span), `H_ABSENT` (including absence reason
`NOT_AN_ANNUAL_REPORT`), or `H_AMBIGUOUS` (AMBIGUOUS with admissible spans). Invalid Gold
blocks scoring; it is not silently reassigned.

## 2. Primary estimand

**SOURCED.** Primary is the document-weighted mean inclusive page-span IoU among
`H_PRESENT`. For `E = H_PRESENT`:

```text
theta_H = sum(Y_i for i in E) / |E|
```

**PROPOSED.** A `VALID` prediction receives its inclusive IoU. `NO_OUTPUT`,
`NOT_LOCATED`, `QUARANTINE`, and every invalid subtype receive zero. If `|E| = 0`, report
`NOT_ESTIMABLE`. Report all Gold and prediction-status counts. ABSENT never receives
IoU 1 and never enters this denominator.

## 3. Prediction status and not-located representation

**VERIFIED.** `arpipe/models.py:176` declares `ExtractionResult.span: MDASpan | None`;
lines 194–195 document reason code `mda_not_located` in `reasons: list[str]`. v0.1 uses
that existing representation and invents no field.

**PROPOSED.** Assign exactly one status in this order:

1. **PROPOSED.** `NO_OUTPUT`: no sealed row exists. If no row exists, the status is
   `NO_OUTPUT`.
2. **PROPOSED.** `DUPLICATE`: more than one row claims the document.
3. **PROPOSED.** `IDENTITY_INVALID`: the sole row's document ID or source hash mismatches.
4. **PROPOSED.** `QUARANTINE`: identity matches and disposition is QUARANTINE, regardless
   of numeric fields.
5. **PROPOSED.** `NOT_LOCATED`: identity-valid, non-quarantined row has `span is None`
   and its reasons contain `mda_not_located`.
6. **PROPOSED.** `TYPE_INVALID`: inconsistent null/not-located representation, Boolean or
   non-integer boundary, or non-positive/non-integer page count.
7. **PROPOSED.** `ORDER_INVALID`: `start > end`.
8. **PROPOSED.** `RANGE_INVALID`: either boundary is outside `[0,N-1]`.
9. **PROPOSED.** `VALID`: exactly one identity-matching, non-quarantined row has integer
   boundaries satisfying `0 <= start <= end < N`.

**PROPOSED.** Preserve duplicate → identity → quarantine → boundaries ordering. Never
choose from duplicates, clip, coerce, reorder, or repair. Any output byte means the Q5
no-output rerun condition is not met.

## 4. Inclusive span IoU

**SOURCED.** With predicted `P=[p_s,p_e]` and Gold `G=[g_s,g_e]`, all stored endpoints
are 0-based and inclusive:

```text
I = max(0, min(p_e,g_e) - max(p_s,g_s) + 1)
U = (p_e-p_s+1) + (g_e-g_s+1) - I
IoU = I / U
```

**PROPOSED.** `[2,4]` versus `[3,5]` gives `2/4 = 0.5`. For a non-contiguous Gold
occurrence, score the declared contiguous hull; gap pages stay listed but are not removed
from the IoU interval.

## 5. Presence endpoint

**PROPOSED.** `NO_ENGLISH_MDA` and `EXTERNAL_REFERENCE_ONLY` are Gold ABSENT outcomes.
Alternative spans of type `HINDI_COPY` are never scored
(`D1_D7_DECISIONS_v0_1.md` §§6 and 7.1).

**PROPOSED.** The full primary presence display is this 2×3 count table over
`H_PRESENT ∪ H_ABSENT`; report `H_AMBIGUOUS` separately:

| Gold state | predicted `PRESENT` (`VALID`) | predicted `NOT_LOCATED` | `FAILED_OR_ABSTAINED` |
|---|---:|---:|---:|
| `PRESENT` | **PROPOSED.** count | **PROPOSED.** count | **PROPOSED.** `NO_OUTPUT` + invalid subtypes + `QUARANTINE` |
| `ABSENT` | **PROPOSED.** count | **PROPOSED.** count; the only true-negative cell | **PROPOSED.** `NO_OUTPUT` + invalid subtypes + `QUARANTINE` |

**PROPOSED.** Also report an error-penalized collapsed 2×2. For Gold PRESENT, combine
`NOT_LOCATED` and failures into the predicted-absent/FN cell. For Gold ABSENT, combine
`VALID` and failures into the predicted-present/FP cell. Thus every failure is wrong and
only `NOT_LOCATED` on ABSENT is a true negative; this scoring collapse does not relabel a
failure as a system absence claim. Report counts, accuracy, sensitivity, specificity,
and every denominator; zero denominators yield `NOT_ESTIMABLE`.

## 6. Secondary endpoints and ambiguity

**SOURCED.** Over `H_PRESENT`, report start accuracy both as exact and within ±1 page,
plus exact end, within-one end, exact full-span, and signed boundary errors. Every
non-VALID prediction receives indicator zero; signed numeric errors are defined for
VALID predictions only with coverage (`D1_D7_DECISIONS_v0_1.md` §1 D3).

**PROPOSED.** Signed error is prediction minus Gold; negative is early, positive is late.
Report type-7 quantiles at `{0,.25,.5,.75,1}`. Type 7 uses
`h=1+(n-1)p`, `j=floor(h)`, and linear interpolation; `n=0` is `NOT_ESTIMABLE`.

**SOURCED.** `H_AMBIGUOUS` is excluded from primary and analyzed only in a labelled
optimistic sensitivity fixed before output. For valid span output, use maximum IoU over
admissible spans; failed/abstained output is zero. **PROPOSED.** For reason
`PRESENCE_UNRESOLVABLE`, `NOT_LOCATED` receives optimistic value 1 because absence is an
admissible reading; report this special count explicitly.

**PROPOSED.** Count cases where a prediction overlaps a recorded alternative span but
not the primary span. This is descriptive and does not replace primary scoring against
the English primary.

## 7. Census, issuer weighting, and interval sensitivity

**SOURCED.** Q8 fixes `CENSUS`: exact frozen-HOLDOUT result, per-issuer distribution, and
all nine leave-one-issuer-out values. It cannot support generalization to all Indian
companies.

**SOURCED.** Q6 states: “Issuer-weighted is reported as a sensitivity.”

**PROPOSED.** For each issuer with at least one `H_PRESENT` document, compute its mean
failure-inclusive IoU; then compute the unweighted mean of those issuer means. Exclude
issuers with zero eligible PRESENT documents and report their count and identities. This
is `theta_issuer`, separate from the document-weighted primary.

**PROPOSED.** The author must choose the interval sensitivity method before HOLDOUT
scoring. No method is selected here. Candidate methods remain issuer-cluster bootstrap,
Student-t over issuer means, or hierarchical bootstrap; the signed choice must fix unit,
seed, replicates, interpolation, empty-resample handling, weighting, and software version.

## 8. Raw A/B agreement

**SOURCED.** Compute agreement from immutable raw A/B records before adjudication,
separately for all HOLDOUT documents and the predeclared VALIDATION overlap.

**PROPOSED.** Report the 3×3 state table and exact agreement as primary agreement
evidence, plus Cohen's kappa and PABAK (`2 * observed_agreement - 1`). If kappa is
undefined, retain the count table and report `NOT_ESTIMABLE`. For PRESENT/PRESENT pairs,
report A-vs-B IoU, exact/within-one boundaries, full-span match, and signed differences.
Also report exact reason/flag agreement, gap-set Jaccard, and non-comparable counts.

**PROPOSED.** Report an Annotator-B-only Gold sensitivity: rescore the primary against
Annotator B's sealed raw primary spans wherever B says PRESENT, with its own denominator
and all failure rules unchanged. This tests dependence on the developer/Annotator A's
labels and never replaces adjudicated primary Gold.

## 9. Descriptive subgroups

**PROPOSED.** Predeclared descriptive groups are issuer; fiscal-year era `<2015` versus
`>=2015`; Gold structural flags; Gold state; prediction status as failure audit; computed
`BROKEN_TEXT`; computed `HEADING_NOT_IN_TEXT_LAYER`; `stub`;
`embedded_in_directors_report`; and `bilingual`. Every subgroup analysis is descriptive
(`D1_D7_DECISIONS_v0_1.md` §§7.2–7.3). LODR 2015 and the Companies Act 2013 transition
motivate the era boundary. Before method freeze, verify that roster `fiscal_year` means
year ending March; on that convention FY2015 is pre-LODR because LODR took effect in
December 2015.

**PROPOSED.** Report definition, numerator, denominator, document and issuer counts.
The bilingual HOLDOUT subgroup is descriptive only. Do not rename or create a subgroup
after results are viewed.

## 10. Development-partition use and unsigned lines

| ID | Proposed line | AUTHOR | DATE | Due |
|---|---|---|---|---|
| A1 | **PROPOSED.** FIT development Gold is single-annotated by the author, used for rules and error analysis only, never reported as accuracy. |  |  | method freeze |
| A2 | **PROPOSED.** VALIDATION Gold is scored once per Phase-10 KEEP decision and reported as “development check (used for model selection)”. |  |  | method freeze |
| A3 | **PROPOSED.** Choose VALIDATION overlap of one or two documents per issuer. |  |  | before selector commitment |
| A4 | **PROPOSED.** Use the selector salt commit–reveal procedure. |  |  | method freeze |
| A5 | **PROPOSED.** Report the Annotator-B-only sensitivity. |  |  | method freeze |

**PROPOSED.** A1–A5 are not stop triggers for P5-A.1 or PILOT and remain unsigned. C1-D1
author ratification is separately due at method freeze.

## 11. Rerun rule and operational order

**SOURCED.** Rerun only after an infrastructure failure that produced no output, with the
failure log published. **PROPOSED.** Any output byte, partial prediction, score, or opened
result disqualifies the no-output rerun. Reuse the same system, inputs, environment, and
command when a rerun is authorized.

**SOURCED.** Required later order is method freeze; system freeze; one HOLDOUT run;
hash-seal unopened outputs and transfer hashes; blind independent Gold; Gold freeze; one
score; publish. Q1b prohibits system/configuration/threshold/pattern/model changes after
the system freeze and before scoring.

**PROPOSED.** Phase 7 Gold work is limited to FIT and VALIDATION. HOLDOUT Gold is created
inside Phase 14 only after the final system and unopened predictions have been sealed, as
required by Q5.

## 12. HOLDOUT disclosure and publication prerequisite

**SOURCED.** The required Q9 wording is reproduced byte-for-byte:

> "The HOLDOUT partition was defined at T0 (18 September 2026). Since T0, under a default-deny policy, HOLDOUT has not been used for development, tuning, threshold selection or method selection. Before T0, ARPipe development processed documents that were later assigned to HOLDOUT, including committed MD&A-span predictions for 53 of the 54 HOLDOUT documents. After T0, a small number of documented metadata and audit accesses occurred; none led to a system change. The influence of this exposure on the frozen system is not quantified. A leave-one-issuer-out analysis is reported."

**PROPOSED.** A HOLDOUT exposure inventory that substantiates every count in this wording
is required before publication. Do not invent counts. The inventory is not a blocker for
P5-A.1 or PILOT.

## 13. Decisions consumed and limits

**SOURCED.** Decisions consumed: D1/PG-1, Q1b, Q2–Q10, B1, B4-note, B6, B8, and CC-4.
The amendment supplies the future Level-C overlay; it cannot contradict Q6 or this SAP.

**PROPOSED.** No HOLDOUT row, system output, prediction, label, P5-B evidence, or PDF
content was consulted. This draft must receive PILOT evidence, rules review, author action
where specified, and an explicit future method-freeze transition before scoring.

## 14. Predeclared page and rule sensitivities

**PROPOSED.** Recompute the primary metrics as labelled sensitivities (i) without a D3
divider or MD&A-own-contents start page and (ii) without pages recorded under
`contains_csr_esg` (`D1_D7_DECISIONS_v0_1.md` §§1 D3, 6, and 7.2). Neither recomputation
replaces the primary result.

**PROPOSED (formula, added 2026-09-28; resolves the F5 OPEN item).**
- (i) D3 sensitivity: replace the Gold start by `boundary_evidence.substantive_start_page`
  (the first text page after a divider or MD&A-own-contents page) wherever it differs from
  the Gold start; score with the §4 inclusive span IoU unchanged. Predictions are not altered.
- (ii) CSR/ESG sensitivity: score by page sets. Let `X` = the Gold record's `csr_esg_pages`
  plus its `gap_pages`; `G' = {g_s..g_e} \ X`, `P' = {p_s..p_e} \ X`;
  `IoU' = |G' ∩ P'| / |G' ∪ P'|`. Documents without `contains_csr_esg` keep their §4 IoU.
  If `G'` is empty the document is dropped from this sensitivity and counted.

**PROPOSED.** Text-measure users receive `mdna_word_count` and `csr_esg_word_count` from
the §7.3 post-seal derived file. Gold defines no word cut-off
(`D1_D7_DECISIONS_v0_1.md` §7.3).

**PROPOSED.** Before HOLDOUT scoring, a change to D3, D4, or D7 switches the primary to
the recorded `BOUNDARY_ALTERNATIVE` span. After HOLDOUT scoring, the changed rule is
reported only as a sensitivity result (`D1_D7_DECISIONS_v0_1.md` §7.5).

**DECIDED (2026-09-28, `D1_D7_DECISIONS_v0_1.md` §8.6; before any VALIDATION or HOLDOUT scoring).** The text-layer audit runs with `--max-bad-char-share 0.1207 --min-latin-word-share 0.3980` (computed by the pre-registered §8.4 rule on FIT). Strata reported: `text_layer_broken`, `heading_in_text_layer = false`, and their union `broken_text_group`, each with its own count. With 3 positives in FIT the detector is only lightly tested; results on VALIDATION and HOLDOUT are reported separately. The computed `start_page_shared` is not used. Until schema v0.3 records exist, word counts (`PAGE_LEVEL`) are analysed only for standalone MD&As whose Gold `mixed_end_page` is null; from v0.3 on, only when the Gold `start_page_shared` and `end_page_shared` are both false (`D1_D7_DECISIONS_v0_1.md` §8.7). Raw A/B agreement on both flags is reported descriptively.
