# Phase 3 / P1 — Author-choice package

**PROPOSED — AUTHOR DECISION REQUIRED. Nothing is adopted. Every AUTHOR CHOICE field is deliberately blank.**

**START_SHA / completed P0b:** `24520ce623037fde7c3b0a9d0d4e5f8fc5618831`. Evidence is in the [research report](PHASE3_CLAIMS_SCOPE_RESEARCH.md), complete [claim matrix](PHASE3_CLAIM_EVIDENCE_MATRIX.md), [sampling analysis](PHASE3_POPULATION_SAMPLING.md), and [B impact map](PHASE3_B1_B8_IMPACT.md). Choices below are proposed alternatives, not additional stages or a replacement roadmap.

**REPO-VERIFIED.** All B1–B8 decisions remain pending in the unchanged register. Local `18_ROADMAP.md` and `17_B1_B8_DECISION_SHEET.md` were not found; **UNVERIFIED / NOT PRESENT IN WORKTREE**. Per author clarification, the supplied task/Master Flow context is authoritative.

## D1 / Q1 — What role should ARPipe have in the thesis?

**Evidence — REPO-VERIFIED / INFERRED.** Existing work establishes infrastructure, contracts and open questions; it has not established a methods advantage or downstream validity. Research Q1 separates infrastructure, methods and both. A thesis role is not recoverable from implementation history alone.

All effort values here and below are **AUTHOR-EFFORT ESTIMATE — planning estimate, not measured fact**. A day denotes focused author work. D1 estimates evaluation work; D2/D6/D7 are component planning estimates and are not additive to D1. Annotation/compute costs are additional unless stated.

| Option | Validity / implications and defensibility | Effort / assumptions | Reversibility | Dependencies / likely examiner challenge |
|---|---|---|---|---|
| A — full-rigor: both infrastructure and methods | Support separately an extraction comparison and any downstream stability assertion; stronger breadth with a larger evidence burden | 30–60 days plus annotation/compute, assuming coherent comparator and fixed climate recipe | Role reversible before Gold/protocol freeze; final exposure cannot be reversed | C2/C4 dependencies and relevant B items; “Which evidence supports the method, and which supports the economic result?” |
| B — proportionate: infrastructure, conditional bounded methods result | C1 primary; C2 only if a defensible comparator and paired experiment are feasible; C4 only when downstream validity is asserted | 10–20 days for infrastructure evidence, 20–40 if a substantial methods track is retained; independent annotation access assumed | May expand prospectively; cannot retrospectively turn tuned cases into unseen evaluation | B6/B8 for final evidence; “Is the extraction quality sufficient for the stated use?” |
| C — do-less: documented aid / C5 | Valid for versioned enumerated cases and disclosed limitations; no representative accuracy, superiority or score-robustness claim | 3–7 days plus independent case review, assuming executable candidate later becomes available | Easily expanded before final access; reduced contribution must be accepted | Proportionate reference reliability; “Is this adequate as thesis infrastructure without a broader validation claim?” |

**PROPOSED recommendation:** B, with C5 fallback. **Confidence:** moderate. **UNRESOLVED:** thesis contribution expectations, author time and independent annotator availability. **What evidence would change this:** examiner/supervisor requirement for a methods contribution; attributable large improvement on permitted development data; a downstream result sensitive to extraction error. Unused engine/REMAP/order tracks may be excessive for narrow claims, but only the author can approve scope within the frozen flow.

**AUTHOR CHOICE:**

## D2 / Q2 — Which candidate claims should be retained?

**Evidence — PROPOSED.** C1 describes corpus-bound localization; C2 asserts paired improvement; C3 explores a routing intervention and is currently NOT YET SUPPORTABLE; C4 asserts downstream stability; C5 is a narrow case-study aid. Exact wording and full evidence chains are in the matrix.

| Option | Validity / implications and defensibility | Effort / assumptions | Reversibility | Dependencies / likely examiner challenge |
|---|---|---|---|---|
| A — full-rigor | Retain distinct C1/C2/C4 questions; retain C3 only after its independent intervention definition. No need to promise positive outcomes | 3–5 days to preregister separate estimands/falsifiers plus future studies; assumes all reference layers feasible | Reversible before evidence collection; post-result claim switching must be disclosed | Baseline, downstream recipe, B6/B8 and B1–B5 if routing; “Are you testing several claims until one succeeds?” |
| B — proportionate | C1 as bounded descriptive endpoint, C2 conditional on identity; C4 required if the downstream thesis uses a validity assertion; defer C3 | 1–3 days for claim/denominator protocol; independent reference planning available | Additional claims can be registered prospectively | B6/B8, conditional route dependencies; “Does a page-span result establish the downstream conclusion?” |
| C — do-less | C5 only, explicit enumerated cases, no claim of population accuracy or improvement | 0.5–1 day for reporting contract, plus case review | High reversibility before final access | Limited reference reliability; “Were the cases selected because they work?” |

**PROPOSED recommendation:** B, with C3 deferred unless a routing claim is essential. **Confidence:** high that separate claims require separate evidence; moderate on preferred breadth. **UNRESOLVED:** selection of primary endpoint, practical margin, ambiguity/presence handling and multiplicity. **What evidence would change this:** a missing scientific question that cannot be answered by C1/C2, feasible independent downstream references, or inability to establish reliable spans.

**PROPOSED contract caveat.** The matrix includes missed predictions as failures and proposes unconditional paired comparisons. The frozen metric specification currently restricts paired uncertainty to units with both outputs. A future author-approved protocol amendment is required before changing that policy; P1 does not implement it. Otherwise the claim must explicitly describe the successful-pair conditional estimand and disclose selection effects.

**AUTHOR CHOICE:**

## D3 / Q3 — What population and weighting should the claims name?

**Evidence — REPO-VERIFIED.** Available corpus construction is conditioned on local bytes and selected issuers/years. Published aggregates and discontinuous FY coverage are in the sampling document. No national inclusion probabilities were established.

**PROPOSED options and implications:**

- A: defined issuer/FY or national universe, with a documented frame and missingness/selection model. Potential broader scope, but current evidence cannot identify that target mean; reweighting without support is not a solution.
- B: explicit available-byte frozen-frame scope. Choose document-weighted or equal-issuer mean by the question; report the alternative as sensitivity if useful. This is defensible with the existing selection limitations.
- C: enumerated FIT/VALIDATION cases only; no population mean.

**PROPOSED recommendation:** B for C1/C2; C for C5. **Confidence:** high about limited current support. **Dependencies:** claim selection, Gold eligibility, split controls/B8 for final work. **UNRESOLVED:** author target; how ambiguity/absence define the eligible population; issuer weights. **What evidence would change this:** a credible external sampling frame, known inclusion probabilities, or a separately specified downstream panel whose target differs. **Pre-mortem:** reporting all Indian issuers or continuous FY coverage would overstate the frame; selecting weights after favorable outcomes would compromise interpretation. Population wording can be deferred to author review, but must precede Gold sampling/final analysis.

**AUTHOR CHOICE:**

## D4 / Q4 — Is downstream sensitivity part of the thesis claim?

**Evidence — SOURCED / INFERRED.** Financial text-measure definitions affect inference; the opened financial-measurement source supports the need to validate the intended construct, not a numerical error model for ARPipe. Research Q4 describes separate boundary, text, score and panel/regression consequences.

**PROPOSED options and implications:**

- A: retain C4 or another downstream robustness assertion. Sensitivity is REQUIRED: future paired original/corrected boundary/text comparisons with fixed scoring; fixed regression only if its conclusions are claimed robust.
- B: C1/C2 extraction claim only. Score sensitivity is USEFUL BUT OPTIONAL unless extraction accuracy is used to justify economic conclusions.
- C: C5 only without score-validity assertion. Downstream sensitivity is UNNECESSARY UNDER NARROWER CLAIMS.

**PROPOSED recommendation:** match necessity to wording; select A if economic conclusions rely on asserted extraction fidelity. **Confidence:** high on logical dependence, low on actual error magnitude. **Dependencies:** fixed score recipe and model, financial panel identity, independent correction protocol, B6; no full econometric redesign is proposed. **UNRESOLVED:** tolerances and actual error correlations. **What evidence would change this:** the thesis does not use the output in substantive inference, or permitted development evidence shows errors concentrated in influential score/issuer-year observations. **Pre-mortem:** high tIoU can hide deletion of rare climate terms; score stability on selected successful cases can hide panel selection. Freeze correction sample and model before results; no downstream experiment in P1.

**AUTHOR CHOICE:**

## D5 / Q5 — What MD&A definition should Gold Method resolve?

**Evidence — SOURCED / INFERRED.** Official provisions permit MD&A within the directors' report or as an addition; legal content requirements do not provide physical page boundaries. BRSR/BRR is distinct. Regulatory periods and exact provisions are in research Q5.

**PROPOSED options and implications:**

- A: admissible span/ambiguity reference allowing embedded, annexure and nonstandard cases; more annotation complexity, better faithful coverage.
- B: a primary contiguous page span with explicit exceptions, presence/absence and ambiguity accounting; efficient if prospectively justified.
- C: standard, unambiguous enumerated cases only; narrow claim and disclosed excluded-case denominator.

**PROPOSED recommendation:** B as protocol starting point, with A if FIT evidence shows material genuine multi-span ambiguity. **Confidence:** moderate; no new report-level boundary study performed. **Dependencies:** B6, claim denominator and future Gold Method; law cannot decide each span. **UNRESOLVED:** mixed pages, ToC false starts, appendices, signed endings and noncontiguity. **What evidence would change this:** independently reviewed FIT examples where contiguous Gold misrepresents section ownership. **Pre-mortem:** prediction-informed Gold or excluding difficult cases after scoring invalidates future evaluation. Rule choices remain reversible before annotation; preserve raw annotations for later re-analysis.

**AUTHOR CHOICE:**

## D6 / Q6 — Which identity, if any, is intended “As-Is ARPipe”?

**Evidence — REPO-VERIFIED.** Research Q6 records full command-derived revisions, code/config/prompt changes, uncommitted documentation and runtime limits. START is the correct P0b documentation base but has static pipeline/interface conflicts. E0 is a more complete saved later implementation; main is earlier; Step0A is curated and unadopted. Step0B has no candidate. Missing referenced revisions remain UNVERIFIED.

| Option | Validity / implications and defensibility | Effort / assumptions | Reversibility | Dependencies / likely examiner challenge |
|---|---|---|---|---|
| A — full-rigor | Reconcile scientifically relevant changes and intended historical state; freeze exact code/runtime/config/prompt identity later, with attributable readiness evidence | 3–7 days assuming provenance and dependencies available; excludes baseline evaluation | Reversible before comparison; fixes become an explicit new identity | Author definition/timepoint and immutable logs; “Were favorable fixes chosen after seeing outcomes?” |
| B — proportionate | Author selects a coherent explicit committed snapshot matching the intended meaning, with complete differences and failure accounting; validate later only for chosen claims | 1–3 days assuming one candidate is acceptable and environment recoverable | Reversible before outcomes; changing comparator afterwards compromises confirmatory claims | Baseline registration and later authorized checks; “Why this snapshot rather than another?” |
| C — do-less | Do not assert baseline-relative improvement; C5 or a later identifiable single-system description only | 0.5–1 day for identity limits and narrow wording | High, before final exposure | C2 dropped/deferred by author; “What performance contribution remains?” |

**PROPOSED recommendation:** B as an identity-resolution process, not selection of a SHA. If “As-Is” means the saved later system, investigate E0's suitability in the authorized later stage; if it means pre-change behavior, main may fit that different question. Do not choose START for convenience. **Confidence:** high on differences, moderate on suitability, unresolved historical fidelity. **Dependencies:** C2, C3 if coupled to routing; system identity also needed for C1/C4/C5 outputs. **UNRESOLVED:** intended timestamp, historical runtime, model binaries and change attribution. **What evidence would change this:** author ratification, recovered immutable manifests or missing revisions, or later authorized readiness checks contradicting static expectations. **Pre-mortem:** an incoherent baseline can make apparent improvement mere repair. No code fix or baseline execution is authorized in P1.

**AUTHOR CHOICE:**

## D7 / Q7 — What precision and Gold planning target is proportionate?

**Evidence — VERIFIED arithmetic / INFERRED assumptions.** The reproducible grid varies issuer count, reports per issuer, within-issuer correlation, imbalance, expected success and target width; no actual ARPipe performance/ICC was estimated. Current final aggregate capacity is 9 issuers/54 documents, a maximum before eligibility/reference completion. Sparse page labels do not enlarge document-span n.

| Option | Validity / implications and defensibility | Effort / assumptions | Reversibility | Dependencies / likely examiner challenge |
|---|---|---|---|---|
| A — full-rigor | Select precision/effect target, estimate paired variance on permitted FIT reference data later, examine interval coverage and issuer influence; independent agreement design | 4–7 days statistical/protocol work excluding annotation, assuming FIT calibration feasible | Reversible before sampling/protocol freeze | B6/B8, identity for C2, intervention for C3; “Do independent clusters support the desired claim?” |
| B — proportionate | Bounded description and paired effects with honest wide uncertainty, document/issuer weighting sensitivity, independent reliability checks | 2–4 days plus Gold, existing tooling assumed | Reversible before Gold Method | B6/B8; “Why is this width adequate for your stated conclusion?” |
| C — do-less | Enumerated reviewed cases; no representative accuracy CI or small-effect superiority claim | 1–2 days plus independent case review | Easy to expand prospectively | C5; “What do selected cases establish?” |

**PROPOSED recommendation:** B for C1; C2 needs later paired-variance evidence before superiority planning. **Confidence:** high that a universal n is unsupported; moderate on prospective precision. **UNRESOLVED:** eligible document/issuer counts, endpoint distributions, missing spans, disagreement and annotator speed. **What evidence would change this:** FIT variance and agreement, target precision required by thesis role, or an author-approved different population. A need for more issuers does not authorize moving FIT issuers into final evaluation or acquiring data. **Pre-mortem:** many bootstrap replicates do not compensate for few issuers; pages are not independent span observations. Sample sizes remain planning targets; Gold Method freezes sampling later.

**AUTHOR CHOICE:**

## D8 / Q8 — What rule governs the missing historical PDFs?

**Evidence — REPO-VERIFIED.** Fourteen historical records lack bytes; they differ from failed extraction, absent MD&A and missing Gold. The supporting Q8 table covers every claim and denominator.

**PROPOSED options and implications:**

- A: if the selected panel/historical reproduction requires an exact missing report–FY item, bounded future acquisition may become necessary after identity and eligibility requirements are specified.
- B: retain available-byte C1/C2 scope and disclose missing-frame limitations; no acquisition needed for that estimand.
- C: enumerated existing C5 cases only; missing historical examples remain unverified.

**PROPOSED recommendation:** apply the rule, not a blanket acquire/do-not-acquire decision. **Confidence:** high on denominator distinction, unresolved claim-specific necessity. **Dependencies:** D2/D3/D6 and financial panel identity for C4. **UNRESOLVED:** authentic original byte recovery and selective panel missingness. **What evidence would change this:** an exact indispensable historical input or panel record becomes part of an author-selected estimand. **Pre-mortem:** recovering a variant does not reproduce original bytes; newly acquired files do not silently enter frozen Gold/final partitions. No acquisition in P1.

**AUTHOR CHOICE:**

## D9 / Q9 — How strong should contribution and novelty wording be?

**Evidence — SOURCED.** Named 10-K section extraction exists; FinTOC/ESGDoc address hierarchy; DocLayNet addresses page layout; Indian audit-report and BRSR work includes adjacent text classification. These are different reference units and metrics. The opened source register records evidence quality and inaccessible sources.

**PROPOSED options and implications:**

- A: a new method/SOTA claim would require direct task-matched comparator evidence and a more specific novelty argument; current research cannot establish it.
- B: application/evaluation contribution in the declared Indian report frame with explicit baseline and evidence contracts.
- C: infrastructure case-study contribution only.

**PROPOSED recommendation:** B if paired evaluation is feasible, otherwise C. **Confidence:** high against broad “first/no prior art” wording; moderate about landscape completeness. **Dependencies:** claim/role/baseline selection. **UNRESOLVED:** directly comparable Indian MD&A datasets and inaccessible full texts. **What evidence would change this:** an opened exact-task dataset/system or a demonstrably novel technique supported by controlled evidence. **Pre-mortem:** comparing heading F1 or layout mAP with page-span IoU is invalid. Further targeted reading can be deferred until it affects a retained claim; no broad new review is prescribed.

**AUTHOR CHOICE:**

## D10 / Q10–Q11 — Which unresolved tracks are actually necessary?

**Evidence — REPO-VERIFIED / UNRESOLVED.** LF fixtures demonstrate synthetic detector blind spots, not real prevalence. The legacy alias is not forensic truth. Sparse Oracle pages do not define a document intervention. Historical HOLDOUT exposure is UNKNOWN. The unchanged B register retains author authority.

**PROPOSED options and implications:**

- A: retain routing/legacy coverage questions. B1–B5 plus an explicit intervention and separately authorized forensic work become necessary before those claims; no automatic REMAP.
- B: retain span-only C1/C2 and disclose coverage limits. Route facts can be named without making a new class/precedence decision effective. B6/B8 remain essential for final span evidence.
- C: C5 on permitted development cases; no HOLDOUT or universal coverage claim, with proportionate independent review.

**PROPOSED recommendation:** B unless mechanism attribution is central; do not silently close unused B items. **Confidence:** high on current constraints. **UNRESOLVED:** real-corpus mechanisms, Oracle transformation, historical exposure. **What evidence would change this:** forensic evidence, author-selected routing estimand, or authentic historical exposure records. **Pre-mortem:** absence of evidence is not evidence of no legacy or of a clean/contaminated final set. The [impact map](PHASE3_B1_B8_IMPACT.md) states required decisions, predicates, experiments and deadlines by claim.

**AUTHOR CHOICE:**

## Stop and next permitted action

**PROPOSED / AUTHOR DECISION REQUIRED.** Review and record author choices through the existing frozen Master Flow. This package grants no downstream execution. No B record is ratified or changed, no new roadmap is created, and P2 is not started. Later author-authorized stages must establish their own exact scope before any baseline, Gold, OCR, LF, REMAP, HOLDOUT or acquisition work.
