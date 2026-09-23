# Phase 2 proposed experiment register

**Status:** proposals only; none executed<br>
**Authorization boundary:** this register does not authorize PDF inspection, OCR, annotation, benchmark execution, production changes, or HOLDOUT access<br>
**Default population:** T0 FIT only unless a later signed protocol says otherwise

## Priority and dependency overview

| ID | Proposal | Kind | Earliest dependency | Uses OCR? | Uses final Gold? | HOLDOUT? | Priority |
|---|---|---|---|:---:|:---:|:---:|---|
| X0 | Semantic-contract conformance audit | Deterministic validation | Phase-2.1 predicate/evidence decisions | No | No | Metadata only | Required |
| X1 | Legacy-font forensic confirmation | FIT diagnostic | B1/B5 evidence protocol | No initially | No | No | High |
| X2 | Hybrid native/OCR/arbitration pilot | FIT comparative pilot | X0; B1/B2/B5; separate OCR authorization | Yes | Calibration reference | No | High, later |
| X3 | TOC/outline candidate-utility study | FIT ablation | DocumentGold protocol and FIT calibration spans | No new OCR | FIT spans | No | Medium |
| X4 | Gold protocol/tool calibration | Segregated FIT pilot | B5-B7; schemas and validator | No requirement | Creates calibration only | No | Required before Gold |
| X5 | Double-annotation selector verification | Deterministic simulation | B3/B4 signed decisions | No | No | IDs only if permitted | Required |
| X6 | HOLDOUT provenance audit | Historical metadata audit | B8 governance scope | No | No | No content | Optional |
| X7 | MD&A boundary ambiguity pilot | FIT annotation-method pilot | DocumentGold protocol draft | No requirement | Calibration only | No | Medium |

“Calibration reference” and “calibration only” are not final Gold and must be stored separately so they cannot enter final evaluation unnoticed.

## Minimum execution specifications

The quantities below are **minimum diagnostic scopes**, not powered prevalence estimates and not authorization. A later preregistration may increase them but must not reduce controls after outcomes are inspected.

| ID | Required inputs and minimum diagnostic scope | Controls | Primary metric / decision rule | Result that changes architecture | Result that leaves it unchanged | Estimated effort |
|---|---|---|---|---|---|---|
| X0 | Every canonical predicate/status plus one valid and one deliberately invalid fixture per rule | Frozen artifact values and alias map | 100% valid fixtures pass; 100% deliberate violations fail | Validation cannot distinguish two meanings → redesign contract, not pipeline | Complete discrimination → freeze catalog | Low, 1-2 researcher-days |
| X1 | 12 FIT pages from distinct documents where feasible: 4 broken-text, 4 U+FFFD/PUA-only, 4 strict-digital negatives | Negative controls; fixed parser/inspection versions; blinded visible-string transcription | Reproducible rendered-glyph/extracted-codepoint mismatch with source-side font evidence | Verified recurring class enables a separately preregistered remap-vs-OCR comparison | No confirmed class → retain OCR structural treatment and `UNKNOWN` prevalence | Low-medium, 2-4 days |
| X2 | At least 25 FIT calibration pages, 5 each from digital/hybrid/scanned/broken/vector classes, across at least 10 documents; increase before inferential claims | Strict-native negative control; fixed native/OCR policies; document-grouped analysis | Preregistered fidelity endpoint plus duplicate/order/failure/cost guardrails | Arbitration beats best simple policy and all guardrails on fresh calibration cases | No material gain or guardrail breach → keep simpler policy | Medium-high, 1-2 weeks plus approved compute |
| X3 | At least 20 FIT documents with frozen calibration spans and representation/era coverage | Same localizer/candidate budget; signal ablations only | Candidate recall at fixed budget, with false candidates/pages searched | Qualified outline/TOC signal improves recall/efficiency without subgroup harm | No gain or systematic misses → keep it annotation aid only | Medium, 3-5 days after spans exist |
| X4 | Two independent annotators; at least 8 FIT documents and 20 PageGold pages spanning common and diagnostic cases; fresh cases after revision | Independent/blinded raw records; separate adjudication; schema validator | Invalid-rate, time, field-specific pre-adjudication agreement, reason-coded disagreement | Persistent endpoint-affecting ambiguity → revise/simplify protocol/tool before Gold | Fresh cases meet signed acceptance criteria → freeze version | Medium-high, 1-2 weeks |
| X5 | Entire approved eligible-unit enumeration, not a sample | Independent clean-checkout reproduction; collision and eligibility checks | Byte-identical ranks/selections; no key collision or `selection_rank` reuse | Any mismatch/collision/post-hoc key choice → block annotation and repair selector spec | Exact reproduction → accept selector mechanism | Low, 1 day after decision |
| X6 | All named Git/manifests/labels/logs and any already retained independent access logs | Hash/time correlation; no document-content access | Presence of a concrete document-derived-information → selection/fitting pathway | Demonstrated pathway → bounded contamination finding and evaluation caveat/redesign | Exhausted records with no pathway → retain `UNKNOWN`, not “never exposed” | Low-medium, 2-5 days depending logs |
| X7 | Two independent annotators; at least 12 FIT documents, with 6 pre-2015 and 6 post-2015 diagnostic cases where available, plus representation diversity | Fresh cases after protocol revision; independent raw records | Exact/±1 boundaries, span IoU, ambiguity prevalence and reasons | Material structured ambiguity → retain admissible spans/reason fields and tolerant metrics | Near-unanimous exact fresh-case boundaries → simplify schema | Medium, about 1 week |

## X0 — semantic-contract conformance audit

**Question.** Can every field/count in the next-phase manifests be traced to exactly one predicate version, unit, denominator, evidence class, and source entity?

**Hypothesis.** A machine-readable catalog plus validation rules will eliminate the observed name/unit ambiguities without modifying frozen data.

**Strongest evidence against.** Some ambiguity is inherently methodological (for example, intended oracle population) and cannot be solved by schema validation alone.

**Smallest test.** Build a hand-reviewed fixture containing one instance of every canonical predicate/evidence class and validate a generated manifest against it. Include deliberate failures for name collision, missing denominator, undefined evidence status, and incompatible unit.

**Falsifier.** If two scientifically different meanings still validate under the same catalog entry, the contract is not discriminating enough.

**Success gate.** Every new manifest field resolves to a catalog ID; no historical alias is accepted without an explicit mapping; impossible sampling cells are marked structural rather than merely empty.

## X1 — legacy-font forensic confirmation

**Question.** Do any FIT documents exhibit a genuine font-encoding/text-mapping failure distinct from general broken extraction?

**Hypothesis.** At least one high-signal FIT candidate will show visible glyphs whose character codes lack or misuse Unicode mapping, producing a reproducible mismatch between rendered and extracted text.

**Strongest evidence against.** All three historical operationalizations are detector/proxy constructs. Broken text may arise from layout, parser behavior, or image representation rather than a legacy encoding.

**Predeclared population.** FIT documents only, sampled separately from: detector `broken_text`; U+FFFD/PUA-only candidates not broken-text; and a strict digital negative control. Do not use T0 HOLDOUT or choose examples after looking at an OCR result.

**Smallest initial test—no OCR.** For a bounded predeclared page sample, capture:

- PDF object/font identifiers and subtype;
- presence/absence and relevant summary of `ToUnicode` mapping;
- extracted character/codepoint sequence from a fixed parser version;
- rendered crop and a human transcription of a short, protocol-selected visible string;
- discrepancy class and reviewer provenance.

Use read-only inspection tooling. The test concerns representation, not OCR quality.

**Falsifier.** No sampled high-signal FIT page shows a reproducible glyph-to-Unicode/extraction mismatch under the frozen parser evidence. This does not prove corpus-wide absence; it rejects the sampled operationalization as a useful high-yield detector.

**Architecture trigger.** Only if a reproducible class exists should a second experiment compare defined remapping versus OCR. A REMAP route requires a detector, action, fallback, and advantage on held-back FIT calibration cases.

## X2 — hybrid native/OCR/arbitration pilot

**Question.** On mixed/hybrid FIT pages, does page- or region-level arbitration improve faithful text recovery and heading/reading-order preservation enough to justify complexity?

**Alternatives.** Fixed native extraction; fixed whole-page OCR; native plus OCR region merge; page/block arbitration; and, only if independently justified, visual-first extraction.

**Hypothesis.** Region-aware arbitration improves damaged/image regions while retaining correct native text, with fewer duplicates and order failures than unconditional merge or whole-page OCR.

**Strongest evidence against.** Hybrid detection itself may be noisy; region merge can duplicate text, break order, and increase operational cost. The gain may be too small for the added failure surface.

**Predeclared population.** FIT only. Sample from canonical digital, hybrid, scanned, broken-text, and vector-text predicates with document grouping. Keep a separate strict-native negative control. Do not select on engine outputs.

**Reference.** A small calibration set created under the approved B5-B7 protocol, never reused as final Gold. Reference source and adjudication provenance must be independent of tested outputs.

**Outcomes.** Character/word error on eligible text; duplicate-token rate; omission rate; heading retention; order-relation accuracy; layout/table damage; abstention/failure rate; latency and compute. Report by canonical representation predicate, not only pooled.

**Falsifier.** Arbitration fails to improve the preregistered primary fidelity outcome over the simpler best fixed policy, or improvement is offset by a preregistered unacceptable duplication/order/cost threshold.

**Stop rule.** No production change from pilot evidence alone. A later change needs an implementation plan, regression suite, and decision record.

## X3 — TOC/outline candidate-utility study

**Question.** Does outline/printed-TOC evidence improve MD&A candidate recall or search cost once visible-content Gold is fixed?

**Hypothesis.** A qualified structural prior improves candidate efficiency but should not alter the final boundary rule.

**Strongest evidence against.** ARPipe's broad keyword proxies flag 89.7% and 96.9% of documents; near saturation may add little discrimination. TOC entries can be missing, stale, or differently named.

**Design.** On FIT DocumentGold calibration documents, compare an identical localizer with and without separately logged signals: PDF outline, printed-TOC candidate, and broad keyword proxy. Freeze downstream thresholds first.

**Outcomes.** Candidate recall at a fixed candidate budget; pages searched; false candidate count; start/end boundary error. Never score “agreement with TOC” as correctness.

**Falsifier.** No meaningful recall/efficiency gain at the fixed budget, or systematic exclusion of Gold spans when the TOC is absent/wrong.

## X4 — Gold protocol and tool calibration

**Question.** Can independent annotators apply the versioned PageGold, DocumentGold, Oracle, provenance, blinding, bbox, and reading-order rules consistently in the candidate tool?

**Hypothesis.** Most disagreements will be classifiable into protocol ambiguities that can be resolved before final annotation.

**Strongest evidence against.** Tool affordances and document complexity may create irreducible unitizing/boundary disagreement; changing the protocol after seeing disagreements can overfit a tiny calibration sample.

**Population.** Segregated FIT calibration documents selected before annotation. Include planned difficult-condition cases, but report them separately from a small random population layer.

**Procedure.** Independent raw A/B annotation; no visibility of the other annotator or tested system output; immutable raw exports; reason-coded adjudication into a separate record; structured debrief. Revise only the protocol/tool version, then use fresh calibration cases for the next round.

**Outcomes.** Schema validity; completion time; missing/invalid records; exact and tolerant boundaries; region alignment; field-specific pre-adjudication agreement; adjudication reasons; evidence-channel use; blinding violations.

**Falsifier.** Fresh cases continue to produce unresolved disagreements that affect primary endpoints or the tool cannot preserve independent/provenance-complete records.

**Success gate.** Author signs a final protocol/tool/schema version and freezes it before final PageGold/DocumentGold or any HOLDOUT annotation.

## X5 — independent double-annotation selector verification

**Question.** Does the adopted B4 selector produce a deterministic, independent 25% expected overlap over the approved B3 population?

**Hypothesis.** A domain-separated SHA-256 threshold over canonical unit bytes is reproducible and not associated with existing sampling ranks or representation labels except for chance.

**Strongest evidence against.** A small/structured population can show chance imbalance; malformed serialization can collide; post hoc seed choice can encode desired balance.

**Smallest test.** Before annotation, enumerate every eligible unit with canonical bytes, digest, threshold decision, and protocol version. Independently reproduce the file in a clean checkout. Run exact checks for duplicate canonical keys, digest mismatch, eligibility drift, and accidental reuse of `selection_rank`. Report overall and prespecified stratum counts without changing the seed/key in response.

**Falsifier.** Reproduction differs; canonical keys collide; eligibility is ambiguous; or the chosen key was selected after inspecting assignment balance.

**Success gate.** Byte-identical selector output from two independent executions and signed author approval. Statistical closeness to exactly 25% is not a validity requirement for a finite sample; independence and preregistration are.

## X6 — historical HOLDOUT provenance audit

**Question.** Can retained metadata establish any specific pre-T0 information pathway from a later T0 HOLDOUT document into model fitting, prompt/rule selection, thresholding, or method choice?

**Hypothesis.** The available record will remain incomplete: it may show membership/operations but not enough to prove either exposure or non-exposure.

**Strongest evidence against.** Additional independently retained access logs, prompts, run manifests, notebooks, or service records might identify a concrete pathway.

**Scope.** Git objects, manifests, hashes, historical labels, execution logs, and already retained external-access metadata. Do not open HOLDOUT PDFs or create new outputs from them.

**Falsifier.** A timestamped trace links an identified T0 HOLDOUT document or derived content to a concrete pre-evaluation selection/fitting action. That would replace `UNKNOWN` with a bounded exposure finding; it still would not imply every HOLDOUT unit was exposed.

**Stop rule.** Once named repositories/log stores are exhausted, retain `UNKNOWN`. Do not equate missing logs with a clean history.

## X7 — MD&A boundary ambiguity pilot

**Question.** Which inclusion/exclusion rules drive start/end disagreement for Indian annual reports across eras and layouts?

**Hypothesis.** Most consequential disagreement will involve title/cover pages, substantive start after a heading, mixed transition pages, repeated MD&A sections, annexures, and end transitions.

**Strongest evidence against.** A simple heading-to-heading rule may cover nearly all sampled FIT reports, making a complex admissible-span schema unnecessary.

**Design.** On a small predeclared FIT calibration set balanced by era and canonical representation class, collect independent candidate span(s), selected span, admissible alternatives, substantive-start marker, end-transition evidence, and reason codes. Report exact start/end, ±1-page agreement, page-span overlap, and ambiguity prevalence.

**Falsifier.** Fresh calibration cases show near-unanimous exact boundaries with no endpoint impact from the additional fields; simplify the protocol rather than preserving unused complexity.

## Open empirical questions not answered by Phase 2

1. Does genuine legacy encoding occur in FIT, and can it be detected reliably?
2. Which extraction policy is best for ARPipe's hybrid pages under task-relevant fidelity measures?
3. What are the precision/recall values of table, TOC, annexure, OCR-layer, language, and legacy proxies against independent labels?
4. Does structural metadata improve MD&A localization after controlling the candidate budget?
5. What PageGold/DocumentGold annotation effort achieves adequate uncertainty for the intended estimands?
6. Which reading-order granularity is both reliable and aligned with the engine comparison?
7. How frequent are genuinely ambiguous MD&A boundaries by era/representation?
8. Is a specific historical pre-T0 HOLDOUT information pathway recoverable from retained metadata?

These questions are explicitly open. None should be answered by renaming a proxy, inspecting HOLDOUT content, or treating absence of evidence as evidence of absence.

## Global safeguards for any future execution

- Register the question, population, exclusions, outcomes, and stopping rule before inspecting results.
- Use FIT for method development and protocol calibration; keep VALIDATION/HOLDOUT uses consistent with the final governance decision.
- Preserve immutable raw outputs and independent annotations with entity/activity/agent provenance.
- Keep diagnostic oversamples separate from population estimates.
- Report failures, abstentions, and structurally impossible cells.
- Do not modify frozen T0-T0.4 artifacts; create versioned downstream records.
- Treat every experiment above as separately authorized work. This document is research planning only.
