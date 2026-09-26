# ARPipe C1 Statistical Analysis Plan v0

**Document status:** `DRAFT_PENDING_PILOT`

**PROPOSED.** This is a pre-scoring draft. It does not authorize HOLDOUT access, choose
an interval sensitivity method, implement scoring, or report a result.

**PROPOSED.** Every substantive paragraph or table row is prefixed with one of
`VERIFIED`, `SOURCED`, `DERIVED`, `INFERRED`, or `PROPOSED`. Headings, definitions,
equations, examples, and citations inherit the nearest explicit label.

## 1. Population and analysis sets

**SOURCED.** HOLDOUT is the single headline population: 54 documents from 9 issuers, 6
documents per issuer. VALIDATION is reported separately as a **development check** and is
never pooled with HOLDOUT. FIT is development and pilot material only
(`docs/governance/CURRENT_DECISIONS.md:26`; Q2).

**SOURCED.** The primary result is bounded to the declared frozen evaluation population;
it is not a national-representativeness, universal-extraction, or state-of-the-art claim
(`docs/phase4/PHASE4_B1_B8_TRIAGE.md:18-20`; D1-D2).

**PROPOSED.** Define the following disjoint Gold analysis states before system output is
viewed:

- **PROPOSED.** `H_PRESENT`: adjudicated Gold is `PRESENT` with a valid primary span;
- **PROPOSED.** `H_ABSENT`: adjudicated Gold is `ABSENT`;
- **PROPOSED.** `H_AMBIGUOUS`: adjudicated Gold is `AMBIGUOUS` with its admissible spans.

**PROPOSED.** A document with a missing/invalid Gold record is a Gold-process failure, is
not silently assigned to any state, blocks final scoring until handled under the frozen
Gold process, and is reported if it cannot be resolved without breaking the freeze.

## 2. Primary estimand

**SOURCED.** The primary estimand is the **document-weighted mean inclusive physical-page
span IoU among HOLDOUT documents where Gold says MD&A is present**
(`docs/governance/CURRENT_DECISIONS.md:30` and
`docs/governance/AUTHOR_RATIFICATION_2026-09-26.md:316-330`; Q6).

**PROPOSED.** Let `E = H_PRESENT` and `n_E = |E|`. For document `i` let `Y_i` be the IoU
defined below, including zero for missing, invalid, or quarantined predictions. The
primary value is:

```text
theta_H = (1 / n_E) * sum_{i in E} Y_i
```

**PROPOSED.** If `n_E = 0`, the primary value is `NOT_ESTIMABLE`; do not substitute zero
or change the denominator. Report `n_E`, the total 54, counts in all Gold states, and all
prediction-status counts.

**SOURCED.** Gold `ABSENT` documents are never assigned IoU `1` and never enter `E`.
Absence is evaluated through the separate presence endpoint
(`docs/governance/AUTHOR_RATIFICATION_2026-09-26.md:320`).

## 3. Prediction status and validity predicate

**PROPOSED.** Evaluate prediction status in this order for every frozen HOLDOUT roster
document. Exactly one status is assigned.

1. **PROPOSED.** `MISSING`: no sealed prediction row exists.
2. **PROPOSED.** `DUPLICATE`: more than one sealed prediction row claims the document.
3. **PROPOSED.** `IDENTITY_INVALID`: the sole prediction row's `document_id` or
   source-PDF SHA-256 does not exactly match the frozen roster/Gold identity.
4. **PROPOSED.** `QUARANTINE`: the sole identity-matching row's frozen system disposition
   is `QUARANTINE`, regardless of whether numeric boundaries are present or valid.
5. **PROPOSED.** `MISSING`: either boundary in the sole identity-matching,
   non-quarantined row is null/absent.
6. **PROPOSED.** `TYPE_INVALID`: start or end is not a JSON integer, is a Boolean, or the
   document page count is not a positive integer.
7. **PROPOSED.** `ORDER_INVALID`: `start > end`.
8. **PROPOSED.** `RANGE_INVALID`: `start < 0`, `end < 0`, `start >= N`, or `end >= N` for
   physical page count `N`.
9. **PROPOSED.** `VALID`: exactly one identity-matching, non-quarantined prediction has
   integer boundaries satisfying `0 <= start <= end < N`.

**SOURCED.** Missing, invalid, and `QUARANTINE` predictions receive IoU `0` in the
primary. Quarantine is additionally reported as abstention, and invalid predictions are
reported by type (`docs/governance/AUTHOR_RATIFICATION_2026-09-26.md:322-326`; Q6).

**PROPOSED.** `DUPLICATE`, `IDENTITY_INVALID`, `TYPE_INVALID`, `ORDER_INVALID`, and
`RANGE_INVALID` are invalid prediction subtypes. Do not choose a convenient row from a
duplicate and do not clip, coerce, round, reorder, or otherwise repair boundaries.

## 4. Inclusive page-span IoU

**SOURCED.** CC-4 makes page-span IoU primary and requires an inclusive-interval
definition (`docs/governance/AUTHOR_RATIFICATION_2026-09-26.md:472-489`).

**PROPOSED.** For valid predicted interval `P = [p_s, p_e]` and Gold interval
`G = [g_s, g_e]`, all endpoints are 0-based and inclusive:

```text
I = max(0, min(p_e, g_e) - max(p_s, g_s) + 1)
L_P = p_e - p_s + 1
L_G = g_e - g_s + 1
U = L_P + L_G - I
IoU(P, G) = I / U
```

**PROPOSED.** Small synthetic examples: `[2,4]` versus `[3,5]` has intersection `2`,
union `4`, and IoU `0.5`; `[6,8]` versus `[6,8]` has IoU `1`; `[1,2]` versus `[4,5]`
has IoU `0`. A missing, invalid, or quarantined prediction has IoU `0` by rule, without
constructing a fictitious interval.

## 5. Secondary endpoints

**SOURCED.** The fixed endpoint set is presence accuracy, exact start, exact end, +/-1
start, +/-1 end, exact full-span match, and signed start/end errors as quantiles
(`docs/governance/CURRENT_DECISIONS.md:46`; CC-4).

### 5.1 Presence endpoint

**PROPOSED.** The presence-analysis set is `H_PRESENT union H_ABSENT`; exclude
`H_AMBIGUOUS` and report its count. Gold presence is `1` for `H_PRESENT`, `0` for
`H_ABSENT`. Predicted presence is `1` only for prediction status `VALID` and `0` for
`MISSING`, every invalid subtype, and `QUARANTINE`.

**PROPOSED.** Report the full 2x2 count table (`TP`, `FP`, `TN`, `FN`), accuracy
`(TP + TN) / (TP + FP + TN + FN)`, sensitivity `TP / (TP + FN)`, specificity
`TN / (TN + FP)`, and every denominator. A zero denominator yields `NOT_ESTIMABLE`.

### 5.2 Boundary and span indicators

**PROPOSED.** Use `H_PRESENT` as the denominator for each of the following. A missing,
invalid, or quarantined prediction receives indicator `0`:

```text
exact_start_i = 1[p_s = g_s]
exact_end_i = 1[p_e = g_e]
start_within_1_i = 1[abs(p_s - g_s) <= 1]
end_within_1_i = 1[abs(p_e - g_e) <= 1]
exact_span_i = 1[(p_s = g_s) and (p_e = g_e)]
```

**PROPOSED.** Report each document-weighted mean with numerator and denominator. The
`+/-1` rule includes exact agreement and a one-page error in either direction; it is not
a one-page expansion of both intervals and it is not an IoU threshold.

### 5.3 Signed boundary errors and quantiles

**PROPOSED.** Signed errors are defined only for status `VALID` within `H_PRESENT`:

```text
signed_start_error_i = p_s - g_s
signed_end_error_i = p_e - g_e
```

**PROPOSED.** Negative means the prediction is earlier; positive means later. Report
valid-prediction coverage `n_valid / n_E`, failure/abstention counts, and quantiles at
`p in {0, 0.25, 0.5, 0.75, 1}`. Do not impute a numeric error for a failed prediction.

**PROPOSED.** Use Hyndman-Fan type 7 quantiles. For sorted errors
`x_(1) <= ... <= x_(n)`, let `h = 1 + (n - 1)p`, `j = floor(h)`, and
`gamma = h - j`; return `x_(1)` at `p=0`, `x_(n)` at `p=1`, otherwise
`(1-gamma)x_(j) + gamma*x_(j+1)`. If `n=0`, report `NOT_ESTIMABLE`.

### 5.4 Complete-case accuracy

**SOURCED.** Complete-case accuracy is conditional secondary and must carry coverage
(`docs/governance/CURRENT_DECISIONS.md:30`; Q6).

**PROPOSED.** “Complete case” means `H_PRESENT` with prediction status `VALID`. Report
mean IoU and the boundary indicators within that subset, explicitly labelled
“conditional on a valid non-quarantined prediction,” together with `n_valid/n_E`. It
must never replace or be visually presented as the primary failure-inclusive result.

## 6. Gold ambiguity

**SOURCED.** `AMBIGUOUS` is assigned before seeing system output, excluded from the
primary with its count reported, and included only in a labelled optimistic sensitivity
against admissible spans (`docs/governance/AUTHOR_RATIFICATION_2026-09-26.md:328`; Q6).

**PROPOSED.** For an ambiguous document with admissible spans `A_i`, define:

```text
optimistic_i = max_{G in A_i} IoU(P_i, G_i)
```

**PROPOSED.** A missing, invalid, or quarantined prediction has `optimistic_i = 0`.
Report the mean over ambiguous documents separately and, as an additional sensitivity,
the mean over `H_PRESENT union H_AMBIGUOUS` using ordinary primary IoU for present
documents and optimistic IoU for ambiguous documents. Label both “optimistic
admissible-span sensitivity”; report their denominators. Do not retroactively change the
Gold state or admissible set after predictions are opened.

## 7. Census framing and uncertainty

**SOURCED.** The primary framing is **`CENSUS`**: report the exact frozen-HOLDOUT value,
the per-issuer distribution, and leave-one-issuer-out analysis. Any interval is a
preplanned sensitivity only and cannot support generalization to all Indian companies
(`docs/governance/CURRENT_DECISIONS.md:32`; Q8).

**PROPOSED.** For each issuer, report its eligible-present count and document-weighted
mean IoU, plus presence-state and prediction-status counts. The “per-issuer
distribution” is the table and empirical distribution of those issuer means; do not
pool VALIDATION.

**PROPOSED.** For each of the 9 issuers, recompute the primary document-weighted mean
after removing that issuer's documents. Report all nine values, the omitted issuer, and
the remaining eligible denominator. If an omitted issuer has no eligible-present
document, report the unchanged value rather than dropping the analysis.

**PROPOSED.** The author must select and freeze one sensitivity interval method before
HOLDOUT scoring. This draft deliberately does not select one. Candidate methods are:

| Candidate | Status | Advantages | Limitations |
|---|---|---|---|
| Percentile nonparametric bootstrap resampling issuers as clusters | `PROPOSED` | Preserves within-issuer clustering and needs no normal-outcome model. | Only 9 clusters; discrete/unstable tails; describes a resampling sensitivity, not population representativeness. |
| Student-t interval over issuer-level mean IoUs | `PROPOSED` | Transparent and directly issuer-aware; simple to reproduce. | Strong small-sample shape assumptions; issuer means may be bounded/skewed and have unequal eligible counts. |
| Hierarchical bootstrap, issuer then eligible documents within issuer | `PROPOSED` | Reflects both issuer and within-issuer variation. | Adds modeling choices and instability with 9 issuers; can imply a superpopulation not justified by the frozen frame. |

**PROPOSED.** Whichever method is later selected must specify resampling unit, random
seed, replicate count, quantile/interpolation rule, empty-resample handling, weighting,
and software version before outputs are opened. The interval remains secondary and must
not be described as a confidence statement about all Indian companies.

## 8. Raw A/B agreement

**SOURCED.** Agreement is computed from immutable raw A/B records only, never from
adjudicated labels (`docs/governance/CURRENT_DECISIONS.md:28`; Q4).

**PROPOSED.** The unit is the document. Compute HOLDOUT agreement on all 54 paired raw
records and VALIDATION agreement only on the predeclared DocumentGold overlap; report
the two partitions separately and never pool the hard FIT pilot layer.

**PROPOSED.** Represent every A/B pair in a disagreement table containing document ID,
A and B presence states/reason codes, primary spans, admissible/alternative spans, gaps,
flags, and field-level difference codes. This comparison table is derived from sealed
raw bytes and contains no adjudicated value.

**PROPOSED.** Report:

- **PROPOSED.** a 3x3 `PRESENT`/`ABSENT`/`AMBIGUOUS` count table, exact presence-state
  agreement, and Cohen's kappa; if the kappa expected-agreement denominator is zero,
  report `NOT_ESTIMABLE` and retain the count table;
- **PROPOSED.** among pairs where A and B both say `PRESENT`, A-vs-B inclusive span IoU
  per document, its mean/median/full distribution, exact start/end/span, and +/-1
  start/end rates;
- **PROPOSED.** signed A-minus-B start and end differences with the type 7 quantiles
  defined in section 5.3;
- **PROPOSED.** exact agreement for reason code and each Boolean/controlled flag;
- **PROPOSED.** exact set agreement and Jaccard similarity for `gap_pages`, with two empty
  sets defined as Jaccard `1`;
- **PROPOSED.** counts of pairs not boundary-comparable because either raw state is not
  `PRESENT`.

**PROPOSED.** Adjudication begins only after this raw comparison is fixed. Adjudication
status/reasons may be summarized separately but are not inputs to any raw agreement
measure.

## 9. Predeclared descriptive subgroups

**PROPOSED.** Report subgroup results only when the subgroup definition below can be
assigned without system output. These analyses are descriptive and do not replace the
primary:

- **PROPOSED.** issuer;
- **PROPOSED.** fiscal-year era: `< 2015` versus `>= 2015`, from frozen roster metadata;
- **PROPOSED.** Gold structure flags: embedded, annexure, bilingual, multiple-span,
  non-contiguous, unclear-start, unclear-end, and
  `legacy_or_corrupted_boundary_heading`;
- **PROPOSED.** Gold presence state for the separate presence endpoint;
- **PROPOSED.** prediction status as a failure/abstention audit, not as an alternative
  accuracy population.

**PROPOSED.** For every subgroup report the definition, numerator, denominator, document
count, issuer count, and metric. Sparse cells remain visible and are labelled descriptive.
Do not create or rename subgroups after viewing HOLDOUT results; an unanticipated pattern
may be described only as exploratory and cannot become a preregistered result.

## 10. Rerun rule

**SOURCED.** A rerun is allowed only after an infrastructure failure that produced **no
output**, and the failure log must be published. No rerun is allowed to improve a
substantive result (`docs/governance/CURRENT_DECISIONS.md:29`; Q5/B8).

**PROPOSED.** Any output byte, partial prediction, score, or opened result means the
“produced no output” condition is not met. Stop and seek a formal governance resolution;
do not silently delete output or restart. A permitted no-output rerun must reuse the same
frozen system, inputs, environment, and command and publish timestamps, operator,
command, failure evidence, output-directory check, and authorization.

## 11. Q5 operational sequence and roles

**SOURCED.** The required order is method freeze, system freeze, one HOLDOUT run and
unopened hash seal, blind Gold, Gold freeze, one score, and publication
(`docs/governance/AUTHOR_RATIFICATION_2026-09-26.md:286-306`; Q5).

1. **PROPOSED — method owner + author.** Complete P5-B, rules review, FIT pilot and
   consistent revisions; the author handles applicable author-controlled decisions and
   the C1-D1 amendment. Freeze and hash the Gold protocol, schema, SAP, selector, and
   amendment; push them. No HOLDOUT access occurs.
2. **PROPOSED — system custodian.** Freeze the final system, manifest, scoring code, and
   environment lock; push. Q1b then prohibits code/configuration/threshold/pattern/model
   changes before the single HOLDOUT score.
3. **PROPOSED — authorized system runner.** Run the frozen system once on the exact
   HOLDOUT roster. Do not open or summarize outputs.
4. **PROPOSED — output custodian.** Hash-seal unopened output bytes, push the hash list,
   and give the identical list to the independent seal holder. Record custody transfer.
5. **PROPOSED — Annotator A and Annotator B.** In isolated, repository-free workspaces,
   independently annotate all 54 HOLDOUT PDFs without outputs, labels, or each other's
   records; seal raw records.
6. **PROPOSED — separate adjudicator.** Resolve A/B disagreements from frozen rules, raw
   records, and necessary PDF evidence only; record reasons; see no system information.
7. **PROPOSED — Gold custodian.** Validate and freeze adjudicated Gold, hash it, publish
   its manifest, and confirm all ambiguity decisions predate output access.
8. **PROPOSED — authorized scorer.** Verify all method/system/output/Gold hashes and run
   the frozen scoring script once. Write one immutable score package.
9. **PROPOSED — author/reporter.** Publish the exact census result, presence endpoint,
   secondaries, agreement, issuer/leave-one-out analyses, failures, abstentions, any
   preselected interval sensitivity, and the exact Q9 exposure wording from
   `docs/governance/AUTHOR_RATIFICATION_2026-09-26.md:396-404`. Label anything later
   exploratory.

## 12. Decisions consumed and deferrals

| Decision | Consumption |
|---|---|
| D1 / PG-1 | **SOURCED.** Defines the bounded START-END localization claim and its operative provenance. |
| Q1b | **SOURCED.** Fixes the no-change period after final system freeze. |
| Q2 | **SOURCED.** Defines HOLDOUT headline, VALIDATION development check, and FIT-only development role. |
| Q3, Q4, B6 | **SOURCED.** Define roles, double annotation, raw agreement, and adjudication. |
| Q5, B8 | **SOURCED.** Define the single-run/seal/blind-Gold/score sequence and rerun rule. |
| Q6 | **SOURCED.** Defines primary denominator, failure zeros, absence, ambiguity, and conditional secondary. |
| Q7 | **SOURCED.** Supplies Gold states and physical-page convention used by the estimand. |
| Q8 | **SOURCED.** Defines census, issuer, leave-one-out, and interval-sensitivity framing. |
| Q9 | **SOURCED.** Supplies the mandatory historically exposed HOLDOUT disclosure. |
| B1 | **SOURCED.** Legacy remains diagnostic and cannot silently become a scoring route. |
| B4 note | **SOURCED.** Requires the new VALIDATION-overlap selector. |
| CC-4 | **SOURCED.** Defines the endpoint family made exact here. |

**SOURCED.** B3, the historical B4 Oracle, B5, B7, C2, As-Is, the Q10 recipe, and C4
remain deferred/out of scope (`docs/governance/CURRENT_DECISIONS.md:34,37-39,41,43,45`).

**PROPOSED.** This SAP must be revised from pilot evidence, independently reviewed,
author-resolved where required, and explicitly frozen before any HOLDOUT scoring.
