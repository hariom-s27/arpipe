# Phase 4 — author decision sheet

**PROPOSED — AUTHOR DECISION REQUIRED. Nothing is adopted. Every `Author choice` field is
deliberately blank.**

**Base commit:** `112d8297837f72881ead46ca2d9fb0735d10b3a1`. **Branch:** `phase4-b1-b8`.
Read with the [triage](PHASE4_B1_B8_TRIAGE.md) and the [factual errata](PHASE4_B1_B3_FACTUAL_ERRATA.md).

**B1–B8 all remain `PENDING_AUTHOR_DECISION`.** This sheet changes no status. Choosing an
option below does not itself ratify it: per the register's governance guard, an `ADOPTED`
record requires author, timestamp, selected option, rationale and effective protocol
version, or it is `INVALID`.

**Triage outcome:** only **B6** and **B8** are DECIDE_NOW. Decision analysis is provided
for those two only. B1, B2, B3, B4, B5 and B7 are deferred with named triggers (section 3)
and deliberately carry **no** option analysis.

---

## 0. Cross-cutting constraint affecting both decisions

**UNRESOLVED — AUTHOR INPUT REQUIRED: independent annotator availability.**

Phase 3 recorded "independent annotator availability" as unresolved. Both decisions below
change shape depending on whether a **second independent annotator** exists:

- If a second annotator is available, independent double annotation and blinding are
  straightforwardly achievable.
- If the author is the sole annotator *and* the developer, then independence and blinding
  are structurally compromised, because the same person holds both the Gold labels and the
  system under evaluation. This does not make Gold impossible, but it changes which
  options are honestly defensible and it must be disclosed in the thesis.

**This is an input, not a decision to be inferred.** No option below assumes an answer;
each states how it behaves under both cases. Please answer it alongside B6.

    Annotator availability (author input):

    [BLANK]

---

## 1. B6 — PageGold / DocumentGold reliability design

### 1.1 Why it is required now

C1 is the adopted primary claim (D1). Its frozen primary metric is `page_span_iou` at
`unit = "document"`, which is scored **against DocumentGold** — so without a DocumentGold
design there is no C1 result at all. The frozen artifacts cannot currently support D3's
Gold concept:

- `gold_schema.json` `document_gold` has **no overlap rate, no sampling rule, no
  stratification requirement**.
- Its `oneOf` admits exactly two record types — there is **no raw-independent-annotation
  type and no separate adjudicated type**, so pre-adjudication disagreement cannot be
  preserved immutably.
- `annotation_provenance` is bare `{"type": "object"}` — no required annotator identity,
  timestamp, independence marker or blinding field.
- `boundary_ambiguity` is an **unconstrained string**; there is no `admissible_spans`
  field. D3 mandates "explicit rules for absent, ambiguous, embedded, annexure, and other
  non-standard cases" — `mda_present` covers *absent*; nothing covers *embedded*,
  *annexure* or *repeated* sections.
- `dataset/corpus_freeze/annotation_roster.csv` has a **single `annotator_id` column**
  over 25 rows, and carries fields the schema does not (`heading_form`,
  `per_page_text_quality`, `minutes_spent`, `saw_pipeline_output`).

Every downstream step consumes this design. Deferring it blocks C1 entirely.

### 1.2 The exact decision question

> **What reliability design governs DocumentGold MD&A spans: who annotates, how many units
> receive a second independent annotation and by what mechanism they are selected, how raw
> disagreement is preserved and adjudicated, how ambiguous / absent / embedded / annexure
> cases are recorded, and when Gold is frozen — such that the adopted C1 claim is
> supported by an auditable reliability estimate?**

Scope note: this question decides the **design**. It does **not** decide numeric rates —
see section 1.8.

### 1.3 Options

All four express the *structure* only; every rate and count is deferred (section 1.8).

**B6-A — Single-pass Gold, diagnostic double annotation only** *(cheapest defensible)*
Single annotator produces DocumentGold for the whole eligible set. A second independent
annotation is taken **only** on a deliberately selected difficult/rare stratum
(pre-2015, hybrid, scanned, known-ambiguous boundaries). Agreement is reported
descriptively on that stratum only, with an explicit statement that **no population-level
reliability estimate is claimed**.

**B6-B — Uniform random double-annotation layer**
A deterministic random subset of the eligible population receives a second independent
annotation. Yields an unbiased population agreement estimate. Rare/difficult conditions
appear only at their natural (low) frequency, so it may produce near-zero information
about exactly the cases most likely to fail.

**B6-C — Hybrid: random population layer + separately reported diagnostic layer**
*(the register's recommended Option 3)*
Both layers, kept separate and never pooled without explicit weights and a declared
estimand. Population agreement comes from the random layer; failure-mode insight from the
diagnostic layer.

**B6-D — Full independent double annotation of the entire eligible Gold set**
Every unit annotated twice independently, all disagreements adjudicated. Maximal
reliability evidence; no sampling decision needed at all.

### 1.4 Advantages and disadvantages

| | Advantages | Disadvantages |
|---|---|---|
| **B6-A** | Lowest cost; feasible with one annotator plus limited second-pass help; targets the cases most likely to be wrong; honest if the limitation is stated | **No population reliability estimate** — a thesis claim of "reproducible" localization then rests on unquantified single-annotator Gold; an examiner can attack this directly; diagnostic agreement is not generalizable |
| **B6-B** | Unbiased, interpretable population agreement; simplest to describe and defend; selection mechanism is clean | May return almost no difficult cases, so it can report high agreement while saying nothing about failure modes; wastes second-annotation effort on easy documents |
| **B6-C** | Answers both questions the thesis needs — "how reliable overall" and "where does it break"; matches the register's and the Gold research package's recommendation; decomposable by presence / start / end / span overlap | Highest design complexity; two estimands to keep separate; pooling them by mistake silently biases the headline number; costs more than A or B |
| **B6-D** | Strongest possible reliability evidence; no sampling or selector decision; every disagreement surfaced | Cost scales with the whole eligible set; likely infeasible for a single-author thesis; over-engineered relative to D7's "proportionate"; may delay everything downstream |

### 1.5 Pre-mortem for each option

**B6-A fails when:** the thesis is examined and the primary reliability question is
"how do you know your Gold is right?" The honest answer is a diagnostic-stratum number
that cannot be generalized. Worse: because the diagnostic stratum is chosen by expected
difficulty, its agreement is a *lower bound* of unknown tightness — it can be argued
either way, which is the weakest rhetorical position. Failure mode: a defensible
localization result is undermined by an unquantifiable reference layer.

**B6-B fails when:** the random layer returns a set dominated by clean post-2015
single-column digital reports, agreement comes back near-perfect, and the estimate is
technically correct but substantively uninformative. The reported reliability then
overstates confidence in exactly the pre-2015 and hybrid documents where C1 is most likely
to fail — and nothing in the design reveals this. Failure mode: a confident number that
conceals the real risk.

**B6-C fails when:** the two layers are pooled — in a script, a table, or a sentence —
and the diagnostic oversample contaminates the population estimate downward. This is an
easy mistake to make late, under time pressure, and it is hard to detect after the fact.
Second failure mode: the design is specified but the diagnostic layer is quietly dropped
when the annotation budget runs out, leaving B6-B with extra complexity and no benefit.

**B6-D fails when:** annotation does not finish. The whole-set double pass consumes the
time budget, Gold is frozen late or incomplete, and the evaluation is compressed or
skipped. It also interacts badly with B8: if the system freeze waits on complete Gold, the
HOLDOUT run may be pushed past the thesis deadline. Failure mode: the best design that is
never delivered.

### 1.6 Comparison

| | Population reliability estimate | Failure-mode insight | Cost | Feasible with one annotator | Risk of a misleading headline number |
|---|---|---|---|---|---|
| **B6-A** | No | Good | Lowest | Yes | Low (nothing is claimed) but the claim is weak |
| **B6-B** | Yes, unbiased | Poor | Low–medium | Marginal | **High** — confident but uninformative |
| **B6-C** | Yes, unbiased | Good | Medium | Marginal | Medium — pooling error is the hazard |
| **B6-D** | Yes (census) | Complete | Highest | No | Low |

### 1.7 Recommendation

**PROPOSED: B6-C (hybrid), with B6-A as the explicit fallback if the annotator-availability
answer in section 0 is "sole annotator".**

Rationale: C1 is the *primary* claim, so its reference layer carries the whole thesis; D7
asks for a "proportionate, issuer-aware" evaluation, and the hybrid design is the smallest
structure that answers both the reliability question and the failure-mode question. It is
also what the existing Phase 2 research and the Gold Method package independently
recommended, so adopting it reuses prior work rather than commissioning more.

The fallback matters: if there is genuinely no second annotator, B6-B and B6-C become
partly performative — "independent" double annotation by the same person who built the
system is not independent. In that case B6-A with a frankly stated limitation is more
honest than a reliability number that does not mean what it appears to mean.

Whichever is chosen, the following should hold (all are design, not parameters):
raw independent annotations preserved immutably **before** adjudication; adjudicated Gold
stored as a **separate record**, never used to compute inter-annotator agreement;
agreement decomposed into **presence / start boundary / end boundary / span overlap**;
annotators blinded to pipeline output (the roster's existing `saw_pipeline_output` field
records this); a controlled vocabulary replacing the free-string `boundary_ambiguity`;
and explicit recorded categories for **absent, ambiguous, embedded, annexure and repeated**
MD&A sections, as D3 requires.

**Confidence: moderate.** High that the *structure* (independent double annotation,
preserved raw disagreement, separate adjudication, decomposed agreement) is required for a
defensible C1. Moderate on hybrid-vs-cheapest, because that turns on annotator
availability and time budget, which are author facts not repository facts.

    Author choice:

    [BLANK]

### 1.8 Immediate decision vs Phase 5 parameter

Per D7 ("Do not freeze an arbitrary universal sample size here") the following are
**deliberately not proposed** and carry no suggested value:

| Belongs to B6 **now** (methodological) | `DEFERRED_TO_PHASE_5_GOLD_METHOD_FREEZE` (parameter) |
|---|---|
| Gold unit = document-level contiguous page span (D3) | Gold sample size |
| Whether a population random layer exists at all | Double-annotation percentage |
| Whether a diagnostic layer exists, and that layers are never pooled unweighted | Stratum allocation |
| That double annotation is **independent** and raw records are immutable | Exact annotator count |
| That adjudication is a separate record and never feeds agreement | Exact workload / time budget |
| Which agreement dimensions are reported (presence/start/end/overlap) | Numerical agreement acceptance thresholds |
| That the selection mechanism is deterministic, pre-declared and enumerable | The specific selector key, domain tag and threshold |
| Controlled vocabulary for ambiguity; required categories for absent/embedded/annexure/repeated | Boundary tolerance values (exact vs ±1 page) |
| Blinding requirement and provenance fields | Calibration-pilot size |
| When Gold is frozen, and that it is frozen before HOLDOUT work | — |

**Design constraint carried forward from B4 (a fact, not a B4 decision):** whatever
selection mechanism is adopted, the frozen `selection_rank` **must not** be reused — it is
a per-cell minimum yielding 355/475 (74.7%) in the hex 0–3 band, not ~25%. A fresh
domain-separated deterministic rank over canonical unit bytes is required. The specific
serialization is a Phase 5 parameter.

**Relationship between PageGold and DocumentGold.** Under C1 alone, **only DocumentGold is
required**; PageGold is CONDITIONAL on C2 evaluating a text-quality change or on C4
activating (triage CC-3). Recommendation: decide the DocumentGold design now and mark
PageGold `CONDITIONAL — not built for C1`. Do not delete the PageGold schema, because
D9's antecedent is undecided.

**Not in scope and not done here:** no annotation tooling was implemented, no Gold
annotation was created, and no numerical Gold parameter was invented.

---

## 2. B8 — HOLDOUT Gold annotation governance

### 2.1 Why it is required now

Two independent reasons:

1. **The adopted population already contains HOLDOUT.** D4 names "the available-byte
   frozen evaluation frame". Recomputed from `benchmark_manifest.json`, that frame is the
   194 `PROFILED_LOCAL_INPUT` documents = 92 FIT + 48 VALIDATION + **54 HOLDOUT**. The
   author's own population choice therefore places HOLDOUT inside the primary evaluation
   population.
2. **Delay forecloses the strongest option.** The register's Option 1 is default-deny until
   the entire system is frozen. That constrains the *ordering* of all intervening work and
   **cannot be adopted retroactively** — once development proceeds without freeze
   discipline, the evidence that the system was frozen before HOLDOUT exposure can no
   longer be created. This reason holds even if no access occurs for months.

`holdout_policy.allowed_before_final_freeze: false` already establishes default-deny, but
annotation is listed under **neither** allowed nor forbidden uses — the gap is real.

### 2.2 The exact decision question

> **Under what authorization, at what point in the freeze sequence, and under what
> blinding, logging and sealing controls may the 54 HOLDOUT documents be annotated and
> evaluated — and how is the UNKNOWN historical pre-T0 exposure reported in the thesis?**

### 2.3 Options

**B8-A — Never annotate HOLDOUT** *(cheapest defensible)*
HOLDOUT is used only for unsupervised distribution checks. C1 is reported on FIT +
VALIDATION, and the claimed population is narrowed accordingly. **Requires amending D4**,
since the frame as chosen includes HOLDOUT.

**B8-B — Default deny until full system freeze, then blinded annotation and exactly one
pre-registered evaluation run** *(the register's recommended Option 1)*
Nothing touches HOLDOUT until pipeline, thresholds, schemas, prompts, Gold method and all
FIT/VALIDATION evaluation are permanently frozen and signed. Then HOLDOUT is annotated
under blinding, evaluated once, and sealed.

**B8-C — Pre-freeze blinded annotation** *(the register's Option 2)*
HOLDOUT annotation proceeds before system freeze under blinded protocols, to parallelize
the schedule.

**B8-D — Staged freeze: annotate after *protocol* freeze, evaluate after *system* freeze**
Freeze the Gold method, schema and evaluation protocol first; permit HOLDOUT **annotation**
by an annotator blinded to system output at that point; keep the **evaluation run** gated
behind the full system freeze. Decouples annotation lead time from system freeze timing.

### 2.4 Advantages and disadvantages

| | Advantages | Disadvantages |
|---|---|---|
| **B8-A** | Zero leakage risk by construction; no annotation cost for 54 documents; no freeze-sequencing burden | Eliminates the final unseen-data evaluation — the strongest evidence C1 could have; contradicts D4 as written, so the population claim must be narrowed and re-stated; 54 of 194 documents become unusable for the headline result |
| **B8-B** | Strongest scientific integrity; the reported result is a genuine held-out evaluation; matches the existing frozen default-deny flag; simplest story to defend | Serializes the schedule — all annotation of 54 documents happens after everything else is frozen, at the point where time is scarcest; a failed or disappointing run cannot be repaired |
| **B8-C** | Most schedule flexibility | Highest contamination risk; conflicts with the spirit of the existing frozen flag; **with a single author who is both developer and annotator, "blinded" is not credible** — reading 54 HOLDOUT documents inevitably informs later method choices; an examiner can reasonably discount the final result entirely |
| **B8-D** | Recovers most of B8-C's schedule benefit at much lower risk, because the *evaluation* remains gated; annotation is a human labelling act that does not by itself tune the system | Still requires real annotator independence to be safe; if the author annotates, the same cognitive-contamination objection as B8-C applies, only weaker; adds a second freeze event to define and evidence |

### 2.5 Pre-mortem for each option

**B8-A fails when:** the examiner asks what the system achieves on data never used in
development, and there is no answer. The thesis then rests entirely on FIT/VALIDATION,
where FIT was used for tuning — and the claim of "reproducible localization" is weaker
than the work actually done supports. Failure mode: discarding the project's best
available evidence to avoid a governance burden.

**B8-B fails when:** the freeze happens late, 54 documents still need annotating, and the
schedule collapses — so either the HOLDOUT evaluation is dropped at the end (arriving at
B8-A's outcome after paying B8-B's sequencing cost), or the freeze is quietly relaxed to
make it fit, which destroys the guarantee it existed to provide. Second failure mode: the
single permitted run returns a poor number and there is pressure to rerun; the protocol
must state in advance that reruns are not permitted, or the guarantee is worthless.

**B8-C fails when:** the author annotates HOLDOUT, notices a systematic failure pattern
while doing so, and — entirely honestly — later fixes it. Nothing records this, and the
final HOLDOUT number is no longer a held-out measurement. The damage is undetectable after
the fact, which is what makes it serious. Failure mode: silent, unfalsifiable
contamination.

**B8-D fails when:** the protocol freeze turns out to be incomplete — a schema or metric
gap is discovered after HOLDOUT annotation has begun (finding C1-D1 shows the metric
contract already has known gaps), forcing either a protocol change after exposure or
discarding the annotation work. Failure mode: freezing the wrong things first.

### 2.6 Comparison

| | Final held-out result | Leakage risk | Schedule risk | Survives a single-annotator setup | Consistent with D4 as written |
|---|---|---|---|---|---|
| **B8-A** | None | None | Lowest | Yes | **No** — requires narrowing D4 |
| **B8-B** | Yes, strongest | Lowest (of those producing a result) | **Highest** | Yes | Yes |
| **B8-C** | Yes, but discountable | **Highest** | Lowest | **No** | Yes |
| **B8-D** | Yes, strong | Low–medium | Medium | Weakly | Yes |

### 2.7 Recommendation

**PROPOSED: B8-B (default deny until full system freeze, then blinded annotation and
exactly one pre-registered evaluation run).**

Rationale: it is the only option that both preserves a genuine held-out result and is
consistent with D4 as the author wrote it. It matches the already-frozen
`allowed_before_final_freeze: false` flag, so it requires no reinterpretation of existing
artifacts. Its real cost is schedule risk, and that cost is manageable if the freeze date
is set deliberately rather than arrived at.

**If schedule risk proves unacceptable, B8-D is the better fallback than B8-C**, because it
gates the evaluation run rather than the annotation, and the evaluation run is where
contamination actually converts into an invalid number.

**Confidence: high** on B8-B over B8-C — with a single author, pre-freeze exposure is very
hard to defend, and the register, the Phase 2 research and the frozen config all point the
same way. **Moderate** on B8-B over B8-A and B8-D, because that trade-off depends on the
author's remaining time budget, which is not a repository fact.

    Author choice:

    [BLANK]

### 2.8 Controls to be specified under whichever option is chosen

Per task §15, addressed as design requirements — **no HOLDOUT access occurred in this task**:

- **Default-deny access** — retain `allowed_before_final_freeze: false` as the governing
  default; annotation must be added explicitly to the allowed-uses list or it stays denied.
- **Authorization** — a signed, timestamped author record naming who may access HOLDOUT,
  for what purpose, and under which protocol version.
- **Final system freeze** — an immutable, signed manifest of pipeline code, thresholds,
  schemas, prompt/model versions and the completed FIT/VALIDATION evaluation, created
  **before** any HOLDOUT access.
- **Leakage checks** — verify no HOLDOUT document, derived text or statistic appears in
  any tuning, threshold-selection or prompt-selection input.
- **Access logging** — every HOLDOUT read logged with identity, timestamp, artifact and
  purpose; logs retained as evidence, not as a formality.
- **Input identity** — exact `document_id` and `source_pdf_sha256` for each of the 54
  documents evaluated.
- **Run identity** — see the run manifest below.
- **One final evaluation run** — exactly one, pre-registered. **Reruns are not permitted
  merely because the first result is inconvenient.** The frozen protocol contains no rerun
  rule; unless the author adds one explicitly and in advance, a second run is exploratory
  and cannot replace the primary result.
- **Post-run sealing** — hash and seal all outputs immediately; any subsequent analysis is
  labelled exploratory.

### 2.9 Required run manifest for the eventual authorized HOLDOUT run

| Field | Content |
|---|---|
| System identity | commit SHA of the frozen pipeline; SHA-256 of every `arpipe/` source file |
| Configuration | SHA-256 of every `configs/` file in force; all threshold values, recorded explicitly not by reference |
| Prompt / model versions | exact prompt text hashes and model identifiers with version pins, where the pipeline uses a model |
| Input artifact identity | the 54 `document_id` values and their `source_pdf_sha256`; the Gold artifact hash |
| Timestamp / environment | UTC start and end; OS, Python and key library versions; hardware where it affects determinism |
| Output artifact hashes | SHA-256 of every produced output, hashed before any inspection |
| Access log | the complete HOLDOUT access log covering the run and all preceding annotation |
| Post-run sealing | signed statement that outputs were hashed and sealed prior to analysis |
| Rerun status | explicit statement that this is the single pre-registered run |

### 2.10 Historical pre-T0 exposure — reporting requirement

`historical_pre_T0_exposure` is **UNKNOWN** (P2-26) and is treated as UNKNOWN throughout.
It is **not** rewritten as CLEAN, ABSENT or CONTAMINATED, and absence of a documented
breach is **not** evidence of cleanliness.

**How this must later be reported in the thesis** — as a stated limitation, not a footnote:

> The HOLDOUT partition was defined at T0. Whether any HOLDOUT document influenced
> pre-T0 development of ARPipe cannot be determined from the retained record: the
> available metadata is incomplete, and the project therefore records historical pre-T0
> exposure as UNKNOWN rather than asserting that no exposure occurred. The governance
> controls described here establish **forward** isolation from the point of the system
> freeze onward; they do not and cannot repair the historical record. The HOLDOUT result
> should accordingly be read as a held-out evaluation with respect to post-T0 development,
> with this limitation stated.

If experiment **X6** (historical HOLDOUT provenance audit) is later authorized, its stop
rule governs: once the named repositories and log stores are exhausted, **retain UNKNOWN**
— do not equate missing logs with a clean history. X6 can only ever convert UNKNOWN into a
*bounded exposure finding*; it cannot establish non-exposure.

---

## 3. Deferred and moot items

No option analysis is provided for these, by design.

| Item | Classification | Trigger / reason |
|---|---|---|
| **B1** legacy route & class-to-route map | **DEFER_UNTIL_TRIGGER** | D10 defers mechanisms; and legacy evidence is concentrated in FIT (6 docs, all one issuer), **0 documents in VALIDATION**, 3 HOLDOUT documents totalling 7 pages — so §16 trigger C does not fire. **Reopens on:** (A) a retained claim about legacy prevalence/handling; (B) Phase 9 failure analysis attributing a false-native or extraction failure to legacy encoding; (C) a document-quality audit showing legacy encoding materially threatens the evaluation population — concretely, new evidence of legacy encoding in VALIDATION or in HOLDOUT beyond the 7 recorded pages. **Not moot:** 225 of 437 confirmed legacy pages route as `digital`, so legacy remains a live threat-to-validity for C1. |
| **B2** route precedence | **DEFER_UNTIL_TRIGGER** | Register: "Strictly dependent on B1." **Reopens on:** B1 reopening, or an adopted change to execution priority among overlapping triage predicates. Standing constraint preserved: `sampling_stratum_priority` must never be used as routing precedence. |
| **B3** Oracle routing population | **DEFER_UNTIL_TRIGGER** | Page-level Oracle-routing construct; D10 defers routing, C3 not adopted, and the unit is wrong for C1. The errata arithmetic correction does **not** activate it. **Reopens on:** adoption of a routing/Oracle claim, or any retained claim consuming the Oracle population. |
| **B4** double-annotation selector | **DEFER_UNTIL_TRIGGER** | Bound to the B3 Oracle population; the register states the 25% oracle rule does not govern PageGold/DocumentGold. Historical serialization deliberately **not** resolved and **no test vectors computed**. **Reopens on:** (a) B3/B5 reopening, or (b) an author decision at the Phase 5 Gold Method freeze to reuse the B4 canonical-serialization mechanism for DocumentGold selection — at which point the serialization questions, and whether a formal T0.4 protocol amendment is required, must be resolved. |
| **B5** Oracle construct & evidence channels | **DEFER_UNTIL_TRIGGER** | Governs route-annotator evidence; no route-label Gold is adopted. Its category-mismatch finding does **not** transfer to B6: MD&A boundaries are determined by visible content, which rendered pages do expose. **Reopens on:** same trigger as B3. |
| **B7** reading-order reference unit | **DEFER_UNTIL_TRIGGER** | `page_span_iou` is order-invariant, so C1 does not need it. **Explicitly NOT moot** — D9's antecedent is undecided and a sequence-aware climate score could require an order reference; declaring it moot would silently resolve an open author conditional. **Reopens on:** (a) D9 answered YES *and* the fixed climate measure shown to be sequence-sensitive, or (b) reading order adopted as an outcome. If D9 is answered NO, B7 may be re-triaged to MOOT then. |

---

## 4. Additional author decisions surfaced by this triage

These are **not** B1–B8 items and must not be recorded as such. They are listed so they
are not lost.

| Ref | Question | Status | Where it must be resolved |
|---|---|---|---|
| **PG-1** | Write the D1–D10 choices into `docs/phase3/PHASE3_DECISION_SHEET.md`, where all ten fields are still blank | AUTHOR ACTION REQUIRED | A Phase 3 record update, not this worktree |
| **PG-2** | The author's D-numbering differs from the Phase 3 sheet's; a crosswalk is recorded in the triage | DOCUMENTATION RECONCILIATION | Alongside PG-1 |
| **CC-1** | Estimand weighting: document-weighted mean or equal-issuer mean? D7 asks for "issuer-aware" but does not choose | AUTHOR DECISION REQUIRED | Before the Phase 5 sample allocation; it changes what B6's reliability sample must represent |
| **CC-4** | Confirm `page_span_iou` as the C1 primary endpoint (currently INFERRED from the frozen spec, not author-stated) | AUTHOR CONFIRMATION REQUIRED | Phase 5 Gold Method freeze |
| **CC-7** | Is the downstream climate measure a substantive thesis result? D9's antecedent is unanswered, and no fixed climate recipe exists in the repository | AUTHOR DECISION REQUIRED | Determines C4, and gates B7 and the PageGold limb of B6 |
| **C1-D1** | The frozen Level C metric contract cannot express the adopted C1 estimand: no denominator rule, no failure/abstention metric, no ambiguity-aware scoring, and `missing_pair_policy` restricts paired differences to units with both outputs | **REQUIRES A FORMAL EVALUATION-PROTOCOL AMENDMENT** | **Phase 5 Gold Method freeze**, as an explicit amendment to `metrics_spec.json` Level `C_ARPIPE_DOCUMENT_TASK`. **Not** inside B6. Until amended, any C1 result must state the successful-pair conditional estimand and disclose the selection effect. |
| **§0** | Independent annotator availability | UNRESOLVED — AUTHOR INPUT REQUIRED | Alongside B6; changes which B6 option is honestly defensible |

---

## 5. Status block

```
PHASE4_STATUS = WAITING_FOR_AUTHOR_DECISIONS

B1 = PENDING_AUTHOR_DECISION   (triage: DEFER_UNTIL_TRIGGER)
B2 = PENDING_AUTHOR_DECISION   (triage: DEFER_UNTIL_TRIGGER)
B3 = PENDING_AUTHOR_DECISION   (triage: DEFER_UNTIL_TRIGGER)
B4 = PENDING_AUTHOR_DECISION   (triage: DEFER_UNTIL_TRIGGER)
B5 = PENDING_AUTHOR_DECISION   (triage: DEFER_UNTIL_TRIGGER)
B6 = PENDING_AUTHOR_DECISION   (triage: DECIDE_NOW)
B7 = PENDING_AUTHOR_DECISION   (triage: DEFER_UNTIL_TRIGGER)
B8 = PENDING_AUTHOR_DECISION   (triage: DECIDE_NOW)

DOWNSTREAM_EXECUTION_AUTHORIZED = NO
GOLD_ANNOTATION_AUTHORIZED      = NO
OCR_EXECUTION_AUTHORIZED        = NO
EXPERIMENT_X1_X7_AUTHORIZED     = NO
HOLDOUT_ACCESS_AUTHORIZED       = NO
P2_LF_INVOKED                   = NO
FORMAL_T0.4_AMENDMENT_EFFECTIVE = NO

NEXT_ACTION = AUTHOR_REVIEW_OF_THIS_SHEET
```
