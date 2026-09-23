# Phase 3 / P1 — Candidate claim–evidence matrix

**PROPOSED — AUTHOR DECISION REQUIRED. No claim, threshold, baseline or sample size is adopted.**

**Repository basis / START_SHA:** `24520ce623037fde7c3b0a9d0d4e5f8fc5618831` (completed P0b). Read with [research](PHASE3_CLAIMS_SCOPE_RESEARCH.md), [choice sheet](PHASE3_DECISION_SHEET.md), [sampling analysis](PHASE3_POPULATION_SAMPLING.md), and [B dependencies](PHASE3_B1_B8_IMPACT.md).

## Shared metric and denominator contract — proposed, not effective

**REPO-VERIFIED.** `configs/t0_4/metrics_spec.json` registers document `page_span_iou`, exact start/end and within-one-page start/end, with issuer-clustered paired uncertainty for Track B. It does not make sparse page Oracle labels into document interventions. `gold_schema.json` and the historical Gold research leave substantive boundary/ambiguity decisions open.

**PROPOSED.** In this package, tIoU denotes the page-span IoU endpoint, not token IoU. For an author-approved single contiguous Gold span G and prediction P, use |P∩G|/|P∪G| over physical pages, with a declared inclusive endpoint convention. Document absence is a separate presence endpoint. Multi-span union, choice among admissible spans, mixed transition pages and ambiguous cases require the future Gold Method contract; choosing the most favorable Gold span after predictions is forbidden.

**PROPOSED.** Define E as all bytes-available documents in the chosen evaluation population with a qualifying present, adjudicable MD&A under a blind, predeclared protocol. Each present document with no output, no span, or a failed extraction stays in E with zero IoU and failed boundary indicators. Do not compute primary accuracy only among successfully returned spans. Define A separately for adjudicated absence; report false-positive presence |predicted-present ∩ A|/|A| and presence confusion counts over E∪A. Undefined absent-span distances must not become perfect localization. Report ambiguous/non-standard/input-unavailable counts separately, with pessimistic bounds if their exclusion is material.

**AUTHOR DECISION REQUIRED.** Exclusion *rules* must be fixed before evaluation and annotations made without predictions; which documents satisfy Gold-based rules is only known after annotation. Byte availability and administrative split are known beforehand. Engine failure is not an exclusion. An alternative treating ambiguity as admissible references must be predeclared and reported separately. Every future report must distinguish intended N, eligible |E|, Gold completed, output returned and paired counts.

**PROPOSED.** Primary document-weighted mean is ΣᵢΣⱼ yᵢⱼ/N; equal-issuer mean is (1/K)Σᵢ(Σⱼ yᵢⱼ/mᵢ). These are different estimands. Cluster resampling alone does not convert the former into the latter. Pages nested within documents do not add independent document spans. Intervals for the five endpoints are pointwise unless a later multiplicity plan says otherwise.

**REPO-VERIFIED / PROPOSED AMENDMENT REQUIRED.** The frozen metrics specification currently pairs only units with outputs from both arms (`uncertainty.missing_pair_policy`). The failure-inclusive primary comparison proposed here changes that estimand and requires a later author-approved formal protocol amendment. Without that amendment, report the successful-pair conditional estimand and its missingness/selection limitations; do not silently execute the proposal.

## C1 — Corpus-bound localization description

| Field | Candidate specification — all entries PROPOSED unless explicitly labelled |
|---|---|
| Exact wording | “For eligible, bytes-available reports in the frozen T0 HOLDOUT partition, the selected ARPipe version's MD&A localization is characterized by the reported mean page-span IoU, exact and within-one-page start/end rates, including missed spans as failures.” |
| Claim type | Descriptive; no assertion of high accuracy before results. |
| Target population | The eligible reports in the existing frozen final-evaluation partition, conditional on available bytes and the author-approved MD&A definition. Not all Indian listed companies, future filings, or all financial years. |
| Estimand | Document-weighted mean tIoU and the four document-level boundary success probabilities within E; presence error separately. Equal-issuer average is a clearly named sensitivity estimand if selected. |
| Unit of analysis | One document (issuer–report–FY identity); issuer is uncertainty cluster, page is boundary coordinate. |
| Numerator | Sum of tIoU across E; number in E with exact start, \|start error\|≤1, exact end, \|end error\|≤1, respectively. |
| Denominator | \|E\| for each primary localization endpoint, including missing system spans. Counts of A and ambiguity are additional explicit denominators. No division by the full corpus page count. |
| Exclusions / rationale / timing | Byte-unavailable records lie outside this available-byte target before evaluation. Adjudicated absence belongs to separate endpoint. Blind protocol-based non-standard/ambiguous classification may define E later; no observed system outcome determines exclusion. |
| Required evidence | Pinned coherent code/config/prompt/runtime identity, immutable outputs, independent DocumentGold, coverage/accounting of every planned final document, metric implementation validation, reporting of errors and difficult representations. |
| Gold required | DocumentGold presence, candidate/selected or admissible spans, physical-page convention, ambiguity, start/end evidence and pre-adjudication reliability under B6. Full-page transcription/order is unnecessary for this claim alone. |
| Metric | Mean tIoU; exact start; ±1 start; exact end; ±1 end; presence confusion; misses; distribution and over/underrun. No threshold is frozen here. |
| Uncertainty | Existing issuer-clustered bootstrap is the registered starting point; few-cluster warning and issuer influence/dispersion. A census of a fixed finite partition is descriptive; bootstrap describes a model-based cluster-resampling distribution, not uncertainty from sampling that census. Annotation and historical-exposure uncertainty remain separate. |
| Sample-size implication | Use issuer and document counts, anticipated variance and target width scenarios in sampling document. Available aggregate final budget is 9 issuers/54 documents (REPO-VERIFIED: Phase 2 audit V07, not newly accessed). Adequacy for a narrow description does not imply precision for national claims. |
| Producing phase | Future authorized final evaluation after Gold Method, protocol/system freeze and B8; no result produced in P1. |
| Generalization boundary | Finite available-byte, selected-issuer/year frame; current forward split separation only. Historical pre-T0 exposure UNKNOWN. No universal corrupted-text coverage. |
| Supporting result | Complete denominator accounting, independent reliable reference, valid implementation, and transparently reported estimates/intervals support the descriptive wording regardless of whether accuracy is good. |
| Failure / falsifier | Biased output-conditioned exclusions, inadequate Gold, ambiguous version identity or incorrect metric invalidate description. A later “adequate quality” extension would require a separately selected acceptance margin and may fail. Low accuracy defeats any usefulness inference, not an honest low-accuracy description. |
| B dependencies | B6 and B8 directly; B1/B2 only if changing routes or claiming route semantics; B3/B4/B5/B7 are not required for span-only description. |

## C2 — Comparative localization benefit

| Field | Candidate specification — PROPOSED |
|---|---|
| Exact wording | “On the declared final-evaluation population, the selected ARPipe revision improves mean MD&A page-span IoU relative to the author-identified As-Is ARPipe baseline under paired, otherwise matched evaluation.” |
| Claim type | Confirmatory methodological comparison; an effect on this task/population, not an algorithmic novelty or national-population claim. |
| Target population / estimand | Same available-byte E as C1 unless the author explicitly chooses a different frame; mean paired difference Δ=E[tIoU_new−tIoU_AsIs]. Secondary differences in four boundary rates. |
| Unit | Document pair; issuer cluster retained jointly across arms. |
| Numerator / denominator | Σ(difference) / \|E\|. Count boundary discordant pairs and each arm's successes over the same \|E\|. Failures receive predeclared failure outcomes, not deletion; available-case paired analysis only a labelled sensitivity. |
| Exclusions | Same blind Gold-defined eligibility for both arms; no engine-dependent exclusions. Known-before distinction follows shared contract. |
| Required evidence | Author-ratified baseline identity, complete change ledger separating engineering fixes from methodology, same inputs/Gold/budget where required, frozen comparator/run settings, independent final outcomes. Static audit alone cannot establish executable equivalence. |
| Gold / metric | Independent DocumentGold and B6 reliability; paired ΔtIoU primary, paired differences exact/±1 start/end secondary, misses in denominator; cost only as a separate endpoint if claimed. |
| Uncertainty | Paired issuer bootstrap, paired issuer-level effect distribution and small-K sensitivity; meaningful margin and multiplicity policy chosen before outcomes. |
| Sample-size implication | Power depends on variance of paired differences and baseline/new correlation, not two independent proportions. Nine issuers may reveal large, consistent effects but cannot guarantee narrow intervals or detection of small improvements. FIT pilot variance is needed before any planning target is ratified. |
| Producing phase | Future authorized baseline and final comparison stages after explicit identity selection and frozen protocol. |
| Boundary | Effect of the complete declared revision over the comparator in this frame. No “routing caused benefit” without a separately valid intervention; no SOTA claim without task-matched comparators. |
| Supporting result | Paired interval above zero, and above any later predeclared practical improvement margin where that is claimed, with acceptable reliability and failure accounting. |
| Failure / falsification | Negative difference contradicts improvement; interval crossing zero is inconclusive; differences explained by unequal outputs/exclusions/budgets or an incoherent comparator defeat attribution. |
| B dependencies | B6/B8 direct; B1/B2 for route-changing methods; B3–B5 only if Oracle-based attribution is added; B7 only if order benefit is claimed. |

## C3 — Routing contribution within a registered intervention

| Field | Candidate specification — PROPOSED; currently CLAIM NOT YET SUPPORTABLE |
|---|---|
| Exact wording | “Within an explicitly defined FIT/VALIDATION document intervention, replacing actual routing with an independently adjudicated route assignment changes mean MD&A page-span IoU by the reported paired amount while all downstream stages are held fixed.” |
| Claim type | Exploratory methodological ablation; no general causal claim. |
| Target / estimand / unit | Eligible FIT/VALIDATION documents covered by a future explicit page-to-document intervention; mean document ΔtIoU_oracle−actual; document pair, issuer cluster. Population currently UNRESOLVED. |
| Numerator / denominator | Sum paired differences / all protocol-eligible intervention documents. Page Oracle sample size is never the document denominator. Unlabelled pages cannot silently inherit an invented perfect route. |
| Exclusions | Future intervention coverage and abstention rules before outputs; unknown-page handling must be explicit. System failure stays in denominator. Present/absence rules as shared contract. |
| Required evidence | Explicit transformation defining labelled pages, unlabelled pages, action execution and fallback; coverage of pages relevant to localization; semantic evidence channels; executable routes; downstream identity; independent reference. None is invented here. |
| Gold | DocumentGold plus the additional page-route reference required by the chosen transformation; multi-channel semantic evidence if encoding is diagnosed. Sparse image-only page labels are insufficient. |
| Metric / uncertainty | Paired document tIoU contrast with issuer-clustered uncertainty; page-route accuracy/false-native rate are separate endpoints over their own eligible page denominators. |
| Sample-size implication | Both route coverage within each document and issuer count constrain power; more isolated labelled pages do not ensure an identifiable document effect. No defensible n until construct/population/transform exists. |
| Producing phase | Only a separately authorized future routing experiment after B1–B6 and explicit transformation; not P1. |
| Boundary | Defined intervention/population only, no guarantee of handling all legacy cases or real-corpus prevalence. |
| Supporting result | Auditable matched intervention and adequate independent route/span references make even a null contrast interpretable. A benefit claim additionally needs a positive, sufficiently precise difference. |
| Failure / falsification | Undefined page→document transformation, absence of an executable action if the selected intervention requires it (including LEGACY/REMAP only if selected), index-test incorporation or uncovered pages defeat claim support; a null/negative result defeats a positive routing-benefit extension. |
| B dependencies | B1/B2 route set/actions; B3 eligible Oracle population; B4 selector; B5 construct/channels; B6 span reliability; B7 only for order endpoint; B8 only if later expanded to final HOLDOUT. |

## C4 — Downstream climate-measure robustness

| Field | Candidate specification — PROPOSED |
|---|---|
| Exact wording | “For the declared financial-text analysis sample and fixed climate-measure recipe, replacing independently corrected MD&A spans/text with ARPipe output changes scores and the specified regression conclusions by less than the tolerances fixed before testing.” |
| Claim type | Confirmatory measurement-robustness/equivalence claim, only if tolerances and conclusions are chosen prospectively; otherwise exploratory sensitivity. |
| Target / estimand / unit | Declared available report–FY analysis sample, with financial-variable eligibility disclosed; score error distribution, rank/order changes, and coefficient/interval differences under the fixed model. Report–FY documents nested in issuer; regression analysis unit explicitly matched to the thesis design. |
| Numerator / denominator | Σ\|score_AR−score_reference\| / number with the declared reference; signed error and RMSE components likewise. Exceedance count / all eligible sampled document–FY units. Regression uses its declared complete-case or missing-data population; no “% valid regressions” denominator. |
| Exclusions | Financial-variable missingness, document absence and reference ambiguity distinguished; rules fixed before outcomes, actual counts known after data/reference assembly. Extraction failures are measured missingness, not conveniently dropped scores. |
| Required evidence | Independent boundary/text reference on a justified sample, fixed scoring/normalization/model spec, paired perturbations isolating section error from text error, coverage analysis and influence of correlated issuer/year errors. |
| Gold / metric | DocumentGold; targeted independent reference text for measurement-relevant content, sufficient to evaluate the chosen score. CER alone is inadequate. Mean/quantile score error, rank stability, coefficient/CI changes and sign/material-conclusion changes. |
| Uncertainty | Paired issuer-aware intervals/perturbation uncertainty, uncertainty in the correction sample and financial model, equivalence margins fixed by substantive meaning. Non-significant difference is not proof of equivalence. |
| Sample-size implication | Driven by score/regression sensitivity and issuer variation; localization sample size cannot be borrowed automatically. Nine issuers alone are not sufficient evidence for broad panel-regression stability. |
| Producing phase | Later explicitly authorized downstream sensitivity study after measure/model and reference definitions; not an extra P1 experiment. |
| Boundary | Only fixed recipe, declared sample and tested perturbations; no guarantee for other climate dictionaries, models, eras, languages or unavailable PDFs. |
| Supporting result | Prospective equivalence tolerances met with appropriate uncertainty, and predefined substantive conclusions stable under plausible observed errors. |
| Failure / falsification | Tolerance exceeded, materially changed coefficient/conclusion, selection from extraction failures, or reference built from the same unchecked output. |
| B dependencies | B6 reference reliability; B7 if reading order affects recipe or an order claim is made; B1/B2 only if route changes tested; B8 for any final partition use. No inherent Oracle requirement. |

## C5 — Deliberately narrower “do less” claim

| Field | Candidate specification — PROPOSED |
|---|---|
| Exact wording | “ARPipe is a versioned extraction aid for the explicitly enumerated FIT/VALIDATION case set; independent review documents its MD&A boundary successes, failures and limitations. These cases provide no population accuracy or universal recovery claim.” |
| Claim type | Descriptive/exploratory infrastructure case study. |
| Target / estimand / unit | The prospectively chosen, disclosed FIT/VALIDATION case set only; finite-case outcomes and failure taxonomy; one document per recorded case with issuer context. |
| Numerator / denominator | Case successes for each declared endpoint / all selected eligible cases; sum case IoUs / eligible cases if summarized. Include failed outputs; presence/ambiguity separate. No extrapolation denominator. |
| Exclusions | Predeclared purposeful selection (e.g. era/structure contrast) and blind eligibility; disclose every selected/missing/ambiguous case. Purposeful selection itself limits the claim. |
| Required evidence / Gold | Pinned coherent executable identity; independently reviewed spans and retained disagreements sufficient for case claims. If calling the reference formal DocumentGold, B6 protocol applies; otherwise call it independent case review and limit reliability claims. No whole-page PageGold/order/Oracle layer by default. |
| Metric / uncertainty | Case tIoU and exact/±1 boundaries if available, explicit failures; descriptive spread, no nominal population CI on convenience cases. Reviewer disagreement/uncertainty recorded. |
| Sample-size implication | Selected for coverage and review feasibility, not precision. Planning volume chosen after workload evidence; no universal minimum. More cases increase diagnostic breadth, not representative inference. |
| Producing phase | A later authorized FIT/VALIDATION review/evaluation task under the existing flow; P1 drafts wording only. |
| Boundary | Enumerated cases only, with historical exposure caveat. Does not validate the downstream climate measure or permit replacement of final evaluation with tuned cases. |
| Supporting result | Traceable independent case references, reproducible case output and honest limitations, including negative outcomes. |
| Failure / falsification | Irreproducible identity, fabricated independence, cherry-picking successful outputs, or extrapolation beyond the cases. |
| B dependencies | B6 proportionate reference/reliability contract; B1/B2 only if routes changed; B3/B4/B5/B7 deferred unless those claims added; B8 remains pending; HOLDOUT access remains unauthorized and is unnecessary for this FIT/VALIDATION candidate. |

## Candidate-plan options and pre-mortem

**PROPOSED.** Full-rigor (A): C1+C2 and, only if the thesis makes those assertions, C3/C4. Proportionate (B): C1 as the extraction result plus a tightly bounded C4 check if downstream climate inference is retained; C2 only with a defensible comparator. Do-less (C): C5. These are alternatives for author selection, not a cumulative list of required work. Effort and validity tradeoffs are in the decision sheet.

| Candidate | Examiner challenge / missing evidence | Questionable denominator or population | Metric/reference mismatch | Falsifier / future experiment at risk | Irreversible point / safe deferral |
|---|---|---|---|---|---|
| C1 | INFERRED: “Why should these documents represent India?”; independent Gold and coherent runtime missing | Available selected issuers/years; E cannot silently mean returned spans | Page labels cannot establish document spans | Bad Gold or exclusions invalidate final description; low quality defeats adequacy | Final partition exposure/Gold use is irreversible; defer order/Oracle layers |
| C2 | INFERRED: “Is the baseline truly As-Is, and what changed?” | Equal matched denominator, failed outputs retained | Comparing different Gold/scoring conventions is not improvement | Comparator/runtime mismatch invalidates final contrast | Baseline selection after results damages validity; defer architecture claims |
| C3 | INFERRED: “How do sampled page labels change a whole document?” | Unknown eligible intervention documents | Sparse page Oracle versus document tIoU | No transformation means CLAIM NOT YET SUPPORTABLE | Outcome-informed transform invalidates ablation; defer the whole claim |
| C4 | INFERRED: “Can small text errors alter rare climate terms or selection?” | Financial-data and extraction missingness can change analysis population | CER/tIoU cannot prove score or coefficient equivalence | Material score/regression shifts defeat robustness | Post-result tolerance selection invalidates confirmation; defer full econometrics until recipe fixed |
| C5 | INFERRED: “Are these favorable examples?” | All purposefully selected cases, including failure | No inferential CI can cure convenience selection | Selective reporting or unverifiable reference | Presenting exploratory cases as untouched test is irreversible; defer final evaluation and broad claims |
