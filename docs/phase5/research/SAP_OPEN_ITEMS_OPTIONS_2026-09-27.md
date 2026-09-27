# SAP v0.1 OPEN items: options for author review

**Status:** `RESEARCH_OPTIONS_ONLY` — 2026-09-27. Every default below is a proposal
labelled `AUTHOR_DECISION`; none is adopted by this memo. Resolve the choices before
the relevant method freeze or scoring step. This memo uses only SAP v0.1, GOLD_SCHEMA
v0.1, and the scoring package's `__init__.py` and `__main__.py`. It uses no corpus row,
PDF, prediction, or outcome.

## Current boundary

- SAP §7 requires an author-selected interval sensitivity method before HOLDOUT scoring.
  Q8, as quoted there, fixes the exact census, per-issuer distribution, and all nine
  leave-one-issuer-out values. Q6, as quoted there, requires issuer weighting as a
  sensitivity. An interval cannot be presented as population generalization.
- SAP §8 asks for signed A/B differences, gap-set Jaccard, and non-comparable counts.
  `scoring.__init__.raw_ab_agreement` currently returns the state table, PRESENT/PRESENT
  IoU and boundary match indicators, plus reason and flag agreement; it does not yet
  return those three requested outputs. It refuses unmatched document sets, duplicate
  raw records, and source/protocol identity mismatches.
- `scoring.__main__._load_predictions` requires seven named CSV columns but permits
  additional columns and any header order. It parses `physical_page_count`, `span`,
  and `reasons` as JSON cells and groups rows by `claim_document_id`.

## Options

| Item | Option | Implication for results | Line touched |
|---|---|---|---|
| 1. Interval | **A. Issuer-cluster bootstrap** for the document-weighted primary mean: resample issuers with replacement and carry each selected issuer's eligible documents together. Keep the exact census result as headline; label any interval a sensitivity. | Respects within-issuer dependence. With only nine issuers, endpoints may be unstable; some resamples may have no PRESENT documents. The author must freeze confidence level, seed, replicate count, percentile/interpolation rule, treatment and count of empty resamples, weighting, and software version before scoring. | SAP §7, especially the Q8 census line, Q6 issuer-weighted line, and unsigned interval paragraph; SAP §13 method-freeze limit. |
| 1. Interval | **B. Exact census only; no interval.** | Reports the frozen HOLDOUT point estimate, per-issuer distribution, and leave-one-issuer-out values without a sampling interval. Avoids suggesting population inference. The current SAP §7 sentence requiring a chosen interval sensitivity method would need an explicit author-approved revision. | SAP §7 Q8 and unsigned interval paragraph; SAP §13. |
| 1. Interval | **C. Student-t interval over issuer means.** | Gives an interval for the mean of eligible issuer means, aligning with the issuer-weighted sensitivity rather than the document-weighted primary mean. Small eligible-issuer count and unequal eligible document counts should be visible. It must not be labelled an interval for the primary estimand. | SAP §§2, 7; SAP §7 names this candidate and defines zero-PRESENT issuer exclusion. |
| 2. Empty/empty gap Jaccard | **A. Define as 1.** For PRESENT/PRESENT pairs with both `gap_pages` sets empty, call the sets identical. | Raises the overall gap-agreement mean when contiguous cases are common. Report the count of empty/empty pairs so readers can see this contribution. | SAP §8 gap-set Jaccard; GOLD_SCHEMA §§2–3 `gap_pages` and `noncontiguous_hull`. |
| 2. Empty/empty gap Jaccard | **B. Mark undefined and omit from the Jaccard mean.** Report empty/empty count separately; for a nonempty union use `|A ∩ B| / |A ∪ B|`, including zero when just one set is empty. | Keeps the Jaccard denominator focused on pairs where at least one annotator marked a gap. The mean can be `NOT_ESTIMABLE` even when there are PRESENT/PRESENT pairs. | SAP §8 gap-set Jaccard and non-comparable counts; GOLD_SCHEMA §§2–3. |
| 3. Signed A−B boundaries | **A. Compute A minus B** separately for start and end on PRESENT/PRESENT pairs: `A.start_page - B.start_page`, `A.end_page - B.end_page`. | Negative means A placed that boundary earlier than B; positive means later. It matches the literal A−B label and the first-minus-reference sign convention used for prediction-minus-Gold errors. | SAP §8 signed differences; SAP §6 signed prediction-minus-Gold convention; GOLD_SCHEMA §2 zero-based physical pages. |
| 3. Signed A−B boundaries | **B. Compute B minus A**, with an explicit B−A label. | Reverses every nonzero sign while leaving absolute disagreement and match rates unchanged. Calling this A−B would mislabel the result. | SAP §8 signed differences; SAP §6 sign convention. |
| 4. Non-comparable A/B pairs | **A. Define comparability per metric.** Every identity-valid, paired raw record contributes to the 3×3 state table and reason/flag agreement. Only PRESENT/PRESENT contributes to span, signed-boundary, and gap metrics; count every other state cell as span/gap non-comparable, with a cell breakdown. Treat missing/duplicate/identity-mismatched raw records as input refusals, outside this count. | Preserves the full state denominator and gives an exact `pair_count - PRESENT/PRESENT_count` span-ineligible count. The label must specify the metric; it is not a count of invalid records. | SAP §8 full raw-pair state table and PRESENT/PRESENT endpoints; GOLD_SCHEMA §1 raw identity/lifecycle; `raw_ab_agreement` identity refusals. |
| 4. Non-comparable A/B pairs | **B. Reserve “non-comparable” for state-discordant pairs** (off-diagonal 3×3 cells); report same-state ABSENT/ABSENT and AMBIGUOUS/AMBIGUOUS as structurally ineligible for span/gap metrics. | Produces a smaller non-comparable count. Span/gap denominators still remain PRESENT/PRESENT only, so reports need both the discordance count and structural-ineligibility count to reconcile to all pairs. | SAP §8 state table, non-comparable counts, and PRESENT/PRESENT restriction; GOLD_SCHEMA §§2–3 state/span rules. |
| 5. Prediction CSV | **A. Confirm the current CLI transport:** `claim_document_id,document_id,source_pdf_sha256,disposition,physical_page_count,span,reasons`; the last three cells are JSON. The reader requires these names but accepts extra columns and any order. | Missing claim rows represent `NO_OUTPUT`; repeated claims remain visible as `DUPLICATE`; a claimed ID different from the row's own ID can be `IDENTITY_INVALID`. No parser change. Producers should emit the displayed canonical order and spell out the reader's permissive behavior. | SAP §3 status precedence and identity rule; `scoring.__main__` module header and `_load_predictions`. |
| 5. Prediction CSV | **B. Freeze an exact seven-column header in the displayed order.** | Preserves current status semantics while rejecting extra or reordered columns. Requires a CLI validation change and a documented sealed-output contract before use. | SAP §3; `scoring.__main__._load_predictions` currently uses subset validation. |
| 5. Prediction CSV | **C. Use one JSON object per prediction row (JSONL), retaining separate `claim_document_id` and row `document_id` keys.** | Keeps native types and duplicate claims, but requires a new parser/adapter and a revised sealed-output format. Omitting the separate claim key would lose the existing identity-mismatch distinction. | SAP §3 duplicate/identity/status rules; `scoring.__main__` CSV transport. |

## Proposed defaults awaiting author action

| Item | `AUTHOR_DECISION` — proposed default only | Required explicit follow-through if selected |
|---|---|---|
| 1 | **A. Issuer-cluster bootstrap**, labelled an interval sensitivity; retain exact census as headline. | Sign and freeze the full resampling specification listed above. Keep the issuer-weighted and leave-one-issuer-out displays independently of the interval. |
| 2 | **B. Undefined for empty/empty**, with its count reported separately. | State the Jaccard denominator and use `NOT_ESTIMABLE` if no eligible union is nonempty. |
| 3 | **A. A minus B** for both boundaries. | Label both signs and restrict numeric differences to PRESENT/PRESENT raw pairs. |
| 4 | **A. Per-metric comparability**, with all non-PRESENT/PRESENT cells span/gap non-comparable. | Report the cell breakdown and keep identity refusals separate from pair counts. |
| 5 | **A. Current seven-column CLI transport**, with producers emitting the displayed order. | Document that the current reader accepts extra columns and reordered headers, or choose B if strict input rejection is required. |

An author choice on any row changes the future method specification; this memo itself
does not change SAP, schema, scorer, or scoring authorization.
