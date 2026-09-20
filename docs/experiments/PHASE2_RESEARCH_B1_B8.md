# B1-B8 decision package

**Status:** evidence integrated; recommendations are not adopted decisions<br>
**Decision authority:** project author<br>
**Gate:** all eight items must have a signed/versioned outcome before final Gold annotation or benchmark execution

## Decision matrix

| ID | Verified state | Principal status | Recommendation | Remaining author choice |
|---|---|---|---|---|
| B1 | No detector `legacy_font`; frozen candidate equals `broken_text`; actual broken text routes to OCR; REMAP exists only in prose; hybrid/blank lack T0.4 routing classes | AUTHOR_DECISION_REQUIRED | Use one current recoverability route (`OCR`) for broken-text/legacy candidates; keep “genuine legacy encoding” as a separate research attribute until verified | Approve one class/OCR, or define an operational REMAP class and its evidence |
| B2 | No frozen routing precedence; only sampling priority mentions legacy before broken text | AUTHOR_DECISION_REQUIRED | Do not reuse sampling priority. If B1 adopts one class, mark precedence not applicable; otherwise specify evidence-based overlap resolution | Collapse with B1 or approve an explicit precedence/error policy |
| B3 | `native_clean_control` has incompatible literal/stratum readings; the selected stratum is not clean-native | AUTHOR_DECISION_REQUIRED | Replace the name with a purpose-defined oracle population and enumerate it from canonical predicates | Choose the oracle's purpose and included representation classes |
| B4 | “first hex 0-3” gives 25% only for an independent uniform digest; seed/key/encoding are absent; `selection_rank` is demonstrably biased | AUTHOR_DECISION_REQUIRED with objective mathematical constraints | Create an independent domain-separated rank over canonical unit bytes; never reuse per-cell sampling rank | Approve canonical fields, encoding, domain key/seed, threshold, tie/collision rule |
| B5 | Adjudication allows rendered image plus protocol; primary evidence unspecified; pixels cannot reveal hidden PDF/font-mapping state | AUTHOR_DECISION_REQUIRED | Use a logged multi-channel evidence bundle for semantic labels, or redefine the oracle to visual action labels | Choose semantic PDF route labels versus visual-only action labels and allowed channels |
| B6 | PageGold/DocumentGold have no overlap rate or slice rule; oracle's 25% rule does not apply automatically | AUTHOR_DECISION_REQUIRED | Random population-reliability layer plus separately reported rare/difficult diagnostic overlap | Approve rate/sample size, stratification, stopping rule, and adjudication trigger |
| B7 | Pair strings have no atomic unit; bbox convention absent; engine blocks may be unavailable | AUTHOR_DECISION_REQUIRED | Annotator-defined atomic visual text regions with stable IDs and directed `PRECEDES` relations; state tie/table policy | Approve granularity and whether all eligible or only adjacent relations are labelled |
| B8 | `allowed_before_final_freeze=false`; annotation is neither explicitly allowed nor forbidden; no frozen HOLDOUT Gold exists | AUTHOR_DECISION_REQUIRED | Default deny before final protocol/tool freeze; afterwards permit only blinded final-reference annotation with access logs and no tuning use | Approve timing, authorized roles, blinding, access log, and permitted downstream uses |

## Required-question completeness matrix

| ID | Question and existing ARPipe research | External research needed / result | Options with principal advantages and limitations | Supported / not supported | What would change it / dependency |
|---|---|---|---|---|---|
| B1 | Is legacy a separate route? T0.4-LF reproduced identity with broken text and recommended one OCR class without adopting it. | Targeted only: PDF standards and legacy-font evidence show the failure is possible, not present here. | One OCR class: matches current producer/action, but may miss a future remap opportunity. Separate REMAP: potentially preserves native glyph semantics, but lacks detector/action/evidence. | Supports one-class recommendation; does not support confirmed legacy occurrence or REMAP rejection. | X1 reproducible class plus better defined remap; gates B2 and future routing. |
| B2 | Which action wins overlap? Existing research found only a sampling priority. | No further broad research; this is a contract decision. | Collapse: simple, no precedence. Specificity/fallback: expressive, more failure states. Run-both: diagnostic, costly and creates outcome-selection risk. Error/abstain: safest, lower coverage. | Supports “do not reuse sampling priority”; no ordering is frozen. | B1 class set and an approved error/fallback policy; gates benchmark route scoring. |
| B3 | What does `native_clean_control` select? Closure and audit establish incompatible readings and hybrid membership. | No external review needed; scientific purpose must be chosen. | Strict native negative control: interpretable, narrow. All route-discrimination sample: relevant to route accuracy, not “clean.” Existing stratum: reproducible, semantically mixed. | Supports retirement of ambiguous new use; does not select a purpose for the author. | Signed oracle estimand; gates B4 eligible units and annotation roster. |
| B4 | How is the 25% overlap selected? Audit independently reproduced a biased reuse candidate. | Hash standards clarify digest mechanics but cannot choose ARPipe bytes/key. | Independent full-digest threshold: exact expected fraction, requires canonicalization. Stratified independent ranks: balance, changes estimand/weights. Fixed-size top-k: exact count, not independent Bernoulli inclusion. | Supports prohibition on `selection_rank` reuse; does not support a particular salt/key. | Signed bytes/key/threshold and X5 reproduction; gates double annotation. |
| B5 | What evidence can establish route labels? Prior Gold research noted image-only Track A and full-report Track B. | PDF specification directly establishes the visual/text-object category boundary. | Semantic oracle with controlled multi-channel evidence: valid semantics, greater blinding/provenance burden. Visual action labels: observable from pixels, answer a narrower question. | Supports category-mismatch correction; does not choose the scientific construct. | Author's intended claim; gates Oracle schema and X1/X2 references. |
| B6 | How much PageGold/DocumentGold overlap? Prior package recommends random plus diagnostic layers. | Annotation literature supports decomposed, task-specific agreement; no universal percentage. | Uniform/random: interpretable population estimate, may miss rare cases. Diagnostic oversample: finds failures, biased if pooled. Hybrid: supports both, costs more. | Supports hybrid structure; not an exact rate or acceptance threshold. | Workload pilot and desired uncertainty; gates final roster/budget. |
| B7 | What is a reading-order unit? Prior package recommends atomic visual regions and directed pairs. | PAGE and relation-based reading-order work provide direct precedents. | All-pair region relations: complete, quadratic. Adjacent graph: cheaper, scoring/transitive closure choices. Line units: fine-grained, alignment-heavy. Blocks: cheaper, engine-dependence risk. | Supports explicit engine-independent units; not a final granularity. | X4 tool/calibration evidence and evaluator contract; gates schema/tool/metric. |
| B8 | When may HOLDOUT be annotated? Frozen flag supports default-deny; history cannot prove non-exposure. | Leakage/group-split literature supports forward separation, not a historical verdict. | Never annotate: strongest isolation, no final reference. Post-freeze blinded annotation: enables evaluation, governance burden. Pre-freeze annotation: flexible, contamination risk and conflicts with flag. | Supports post-freeze/default-deny recommendation; not authorization. | Signed governance record; gates any HOLDOUT label or final evaluation. |

## B1 — legacy route and class-to-route map

### Facts

- `PageKind` has no `legacy_font` producer.
- T0.4 `legacy_font_candidate` is identical to detector `broken_text` in the sampled record; broken text is in `NEEDS_OCR`.
- REMAP has no operational algorithm in the frozen code.
- The post-closure T0.4-LF report recommends one class/OCR, but explicitly records that no rule was adopted.
- External legacy-font research establishes that encoding failures can exist, not that they exist in this corpus.

### Recommendation

For the current contract, map the observed broken-text/legacy-candidate condition to OCR recovery and retain a separate nullable forensic attribute such as `legacy_encoding_evidence = UNKNOWN|SUPPORTED|NOT_SUPPORTED`. This avoids inventing a route with no detector or transformation. It is a methodology recommendation only; Phase 2 does not change production behavior.

### Rejection condition

Reject the one-class recommendation if the FIT-only forensic test finds a reproducible class whose text can be recovered by a defined remapping operation more accurately or faithfully than OCR and whose membership can be detected without Gold leakage. In that case, specify the detector, action, fallback, and evaluation level before adding REMAP.

## B2 — overlap and precedence

Sampling priority answers “which coverage stratum owns this unit?” Routing precedence answers “which action is executed?” They are different relations.

If B1 adopts one recoverability class, legacy-versus-broken precedence is `NOT_APPLICABLE`. If two actions remain, the contract must define:

1. the predicates and whether they may overlap;
2. whether more specific evidence wins, both actions are attempted, or overlap is an error;
3. how a failed remap falls back;
4. which action provenance is recorded; and
5. how the route is scored without selecting on Gold outcome.

No option should inherit `sampling_stratum_priority` by accident.

## B3 — intended oracle population

The phrase `native_clean_control` cannot select the oracle population safely: the closure records literal and stratum readings of 79 and 121, while the all-split selected stratum contains 60 units including 22 hybrid units. The mismatch is a semantic warning, not a number to vote on.

The author should first select the oracle purpose:

- **route-discrimination reliability:** sample across every proposed route and important overlap, not just native controls;
- **native false-positive control:** include only units satisfying an approved strict digital predicate with no scanned/OCR proxy evidence;
- **benchmark calibration:** select from the final Track-A population with a declared representation distribution.

Recommendation: define the population as an explicit predicate over immutable unit fields, publish its enumerated IDs and exclusions, and retire the ambiguous label in new artifacts. Do not change the frozen manifest.

## B4 — deterministic 25% double-annotation rank

### Objective constraints

- A uniformly distributed hexadecimal digest begins with `0`, `1`, `2`, or `3` with probability `4/16 = 0.25`.
- This expectation does not hold if the candidate digest was selected as a minimum over alternatives. The frozen `selection_rank` is such a per-cell minimum and yields 355/475 (74.7%) in the 0-3 band, not approximately 25%.
- The authoritative audit also reproduces 50/79 (63.3%) for its literal oracle-population reading. Neither observed rate is compatible with treating `selection_rank` as the intended independent selector.
- Eligibility must be fixed before ranking.
- The hash input must specify field order, encoding, separators/length-prefixing, normalization, missing values, version, and domain separation.
- The selection rule must specify a full threshold or exact prefix rule and deterministic tie/collision behavior.

### Recommended pattern, not an adopted value

Define a new field such as `oracle_double_annotation_rank = SHA256(canonical_bytes)` where `canonical_bytes` is a versioned, injective serialization of a stable unit identifier plus an author-approved domain tag/key. Select units whose 256-bit integer rank is below `floor(0.25 * 2^256)`. The full-digest rule avoids an unnecessary four-bit implementation dependency while retaining the exact target fraction in expectation.

The author must approve the domain tag/key and identifier field set. The selector must be enumerated and reviewed before annotations exist. Do not search for a seed that produces aesthetically balanced strata; if stratification is required, declare it first and rank independently within each stratum.

This is **not an identified implementation bug**, because the frozen tree contains no implemented oracle double-annotation selector using the incomplete rule. It is a methodological underspecification with one objective correction: the biased sampling `selection_rank` cannot satisfy the stated random-rank interpretation.

## B5 — evidence available to route annotators

### Objective evidence boundary

Rendered pixels expose visual content. They do not expose whether a PDF contains invisible text, whether a font character code has a correct `ToUnicode` mapping, or whether copied text matches visible glyphs. Therefore `NATIVE` versus `LEGACY` cannot be a validated PDF-semantic distinction when pixels are the sole evidence.

### Two coherent options

**Option A — semantic route oracle (recommended if the labels remain NATIVE/LEGACY/OCR).** Permit a controlled evidence bundle: rendered image, raw extraction result, PDF/font diagnostic summary, and protocol. Log every channel opened; keep engine outputs hidden; prohibit outcome-based choice. Adjudication receives the independent records, not an engine score.

**Option B — visual action oracle.** Keep image-only evidence but relabel the task in observable terms, such as `VISIBLE_TEXT_RECOVERABLE_WITHOUT_OCR`, `OCR_REQUIRED_FOR_VISIBLE_CONTENT`, or `ABSTAIN`. Do not claim a font-encoding diagnosis.

The author must choose which construct is scientifically needed. Mixing semantic labels with visual-only evidence is not acceptable.

### Evidence-channel observability

| Channel | Can directly observe | Cannot establish alone |
|---|---|---|
| Visual/rendered image | Visible glyphs, image regions, visual layout, apparent readability, headings | Hidden/invisible text, font code mapping, extractability, PDF object provenance |
| Extracted text layer | Parser-returned characters, order, replacement/PUA characters, copyability under that parser | Whether visible glyphs match without comparison; why extraction failed; parser-independent truth |
| PDF objects/font evidence | Font subtype, character codes, `ToUnicode` presence/content, text rendering mode, object relationships | Human-intended text or downstream usefulness without rendering/extraction comparison |
| Metadata | Producer, dates, declared structure/bookmarks, file identity | Correct content, correct Unicode, trustworthy MD&A boundaries |
| Human annotation | Protocol-defined judgment over the channels actually shown | Properties hidden from those channels; independence if system output is visible |

## B6 — PageGold and DocumentGold reliability design

The prior Gold research recommends a hybrid design:

1. draw a deterministic random overlap sample from each task's full eligible population for an unbiased reliability estimate;
2. add a separately labelled diagnostic layer for rare/difficult conditions (legacy candidates, hybrid, boundary ambiguity, complex layout, pre/post-2015); and
3. never pool the diagnostic oversample into the population estimate without weights and an explicit estimand.

Report pre-adjudication agreement separately for PageGold transcription, DocumentGold presence, start boundary, end boundary, span overlap, and categorical fields. Adjudicated Gold quality is not an inter-annotator agreement estimate.

The exact percentage is an author/resource decision after a small segregated FIT workload pilot. The frozen oracle 25% does not automatically govern PageGold or DocumentGold.

## B7 — reading-order reference unit

Recommendation: use **annotator-defined atomic visual text regions** with engine-independent IDs and normalized page coordinates. A relation record should at least carry `(page_id, predecessor_region_id, successor_region_id, relation, annotation_provenance)`, where `relation` supports `PRECEDES`, a declared tie/parallel value if allowed, and `NOT_APPLICABLE` for excluded structures.

The protocol must define:

- whether a region is paragraph, heading, list item, cell, caption, or another visible unit;
- coordinate origin, axes, units, page box, rotation handling, and allowed polygon/bbox geometry;
- whether tables are one region, cell regions, or outside the reading-order metric;
- treatment of headers, footers, marginalia, multi-column transitions, and continued sections;
- whether all non-tied pairs or only adjacent edges are annotated and how each is scored; and
- how split/merge alignment is handled when engine outputs differ from Gold regions.

All-pairs relations are the more complete reference and match the prior research recommendation, but their annotation cost can be quadratic. The author/evaluator must approve the unit and relation set before tooling is built.

## B8 — HOLDOUT Gold authorization

### Evidence-bounded policy recommendation

Interpret `allowed_before_final_freeze: false` as default deny. HOLDOUT annotation may be authorized only after all of the following are immutable and versioned:

- task definitions and inclusion/exclusion rules;
- schemas and validators;
- annotation UI and evidence channels;
- sampling and double-annotation selectors;
- adjudication protocol;
- metrics and analysis plan; and
- authorized people, access logging, and data-use rules.

Once authorized, HOLDOUT annotators should be blinded to model/detector outputs and validation results. HOLDOUT labels may create the final reference and support the single preregistered evaluation; they must not be used to choose routes, prompts, thresholds, engines, exclusions, or stopping rules. Any post-result change is labelled exploratory and cannot replace the frozen primary result.

Historical pre-T0 exposure remains `UNKNOWN`; this policy controls forward validity rather than pretending to repair history.

## Author decision record template

For each B item, record:

```yaml
decision_id: B1
status: ADOPTED | REJECTED | DEFERRED
selected_option: null
rationale: null
evidence_considered: []
effective_protocol_version: null
affected_artifacts: []
supersedes: []
author: null
timestamp: null
```

An implementation is not a substitute for this decision record. `DEFERRED` is valid only if the downstream work that depends on the item also remains blocked.
