# Phase 4 — B1–B8 triage against the adopted Phase 3 claims

**Status:** DECISION PREPARATION. **No B1–B8 decision is adopted, implemented or amended.**
All eight items remain `PENDING_AUTHOR_DECISION`. Every recommendation in the companion
[decision sheet](PHASE4_DECISION_SHEET.md) is PROPOSED until the author chooses it.

**Base commit:** `112d8297837f72881ead46ca2d9fb0735d10b3a1`. **Branch:** `phase4-b1-b8`.
**Companion:** [factual errata](PHASE4_B1_B3_FACTUAL_ERRATA.md) (commit 1).

---

## 0. Governing input — the author's Phase 3 decisions

Recorded verbatim as supplied. This is the binding input for everything below.

| # | Question as the author posed it | Author choice (verbatim, condensed to its operative clauses) |
|---|---|---|
| D1 | What is the main thesis claim? | "ARPipe is developed and evaluated for reproducible START–END page-span localization of MD&A sections in a defined Indian annual-report corpus." |
| D2 | How broad is the claim? | "Bounded to the declared frozen evaluation population. No claim of national representativeness, universal MD&A extraction, or SOTA. A baseline-relative methods claim is retained only if the As-Is comparator is later established coherently." |
| D3 | What exactly counts as Gold MD&A? | "A contiguous physical-page START–END span, with explicit rules for absent, ambiguous, embedded, annexure, and other non-standard cases." |
| D4 | What population does the result describe? | "The available-byte frozen evaluation frame… does not represent all Indian issuers or continuous FY2010–2025 coverage. Gold-based eligibility and exclusion rules will be fixed in the Gold Method phase." |
| D5 | Do missing PDFs matter? | "The 14 missing historical PDFs are not required for the primary bounded claim." |
| D6 | What exact system is the As-Is baseline? | "The coherent historical operational ARPipe system immediately before the specific change being evaluated… If the baseline cannot be established coherently, no baseline-relative improvement claim is made." |
| D7 | What evidence/sample size is needed? | "Proportionate, issuer-aware evaluation… Do not freeze an arbitrary universal sample size here. Final Gold sample allocation is determined and frozen in the Gold Method phase." |
| D8 | Is acquisition necessary? | "No acquisition is currently necessary." |
| D9 | Is downstream climate robustness part of the thesis? | "A bounded downstream robustness/sensitivity analysis is **retained if** the downstream climate measure is used as a substantive thesis result." |
| D10 | Outcome or mechanism? | "The primary thesis evaluates the extraction/localization **outcome, not** a specific internal routing mechanism. Routing, legacy-font, and REMAP mechanisms are investigated only if a later failure-driven claim explicitly requires them." |

### 0.1 Two provenance gaps recorded, not repaired

**PG-1 — the decisions are not yet written into the Phase 3 sheet.**
`docs/phase3/PHASE3_DECISION_SHEET.md` at `112d8297` still shows all ten
`**AUTHOR CHOICE:**` fields blank. The decisions above were supplied directly to this
task. They are treated as authoritative because the author is the sole decision
authority; but the repository record does not yet carry them. **Status: AUTHOR ACTION
REQUIRED** — write the choices into the Phase 3 sheet so the chain is auditable. This
task does not edit a Phase 3 artifact from a Phase 4 worktree.

**PG-2 — the author's D-numbering differs from the Phase 3 sheet's D-numbering.**
This is a labelling divergence only; each author answer carries its own question text, so
no content is ambiguous. Crosswalk (**REPO-VERIFIED** against the sheet's headings):

| Author's label | Author's topic | Phase 3 sheet heading |
|---|---|---|
| D1 | main thesis claim | D2 / Q2 (claims retained) + D1 / Q1 (role) |
| D2 | breadth | D2 / Q2 and D9 / Q9 (contribution wording) |
| D3 | Gold MD&A concept | **D5 / Q5** (MD&A definition) |
| D4 | population | **D3 / Q3** (population and weighting) |
| D5 | missing PDFs | **D8 / Q8** (missing historical PDFs) |
| D6 | As-Is baseline | D6 / Q6 (baseline identity) |
| D7 | sample size | D7 / Q7 (precision and Gold planning) |
| D8 | acquisition | D8 / Q8 (acquisition limb) |
| D9 | downstream climate | **D4 / Q4** (downstream sensitivity) |
| D10 | outcome vs mechanism | D10 / Q10–Q11 (unresolved tracks) |

Throughout this document, **Dn refers to the author's numbering above.**

### 0.2 Resulting C1–C5 status

C1–C5 are the Phase 3 candidate claims. The author did not use these labels, so each row
below carries its own evidence status. **Rows marked INFERRED require author
confirmation; they are not treated as adopted.**

| Claim | Phase 3 description | Status under D1–D10 | Evidence status |
|---|---|---|---|
| **C1** | corpus-bound MD&A span localization | **ADOPTED — PRIMARY** | **DIRECT.** D1 is a textual match for C1's endpoint. |
| **C2** | paired improvement vs As-Is baseline | **RETAINED — CONDITIONAL, gate unmet** | **DIRECT.** D2 and D6 both make it conditional on a coherent As-Is comparator. Phase 3 found the inherited P0b production files are *not* a coherent baseline identity, so the gate is currently **UNRESOLVED**. |
| **C3** | routing/Oracle contrast | **NOT ADOPTED — deferred** | **DIRECT.** D10 excludes routing mechanisms absent a later failure-driven claim. Independently, Phase 3 recorded C3 as NOT YET SUPPORTABLE (no page→document Oracle transformation). |
| **C4** | downstream climate stability | **CONDITIONAL — antecedent itself undecided** | **DIRECT but incomplete.** D9 retains it *if* the climate measure is a substantive thesis result. The author did not state whether it is. See CC-7. |
| **C5** | enumerated case-study aid | **NOT ADDRESSED — UNKNOWN** | **UNKNOWN.** The author neither adopted nor rejected C5. Not inferred here. C5 imposes no B-item requirement beyond a proportionate version of B6, so its status does not change any triage outcome below. |
| — | ARPipe role (sheet D1/Q1) | proportionate infrastructure + conditional bounded methods result = sheet option **B** | **INFERRED** from D1+D2+D6. Confirm. |

---

## 1. Step 1.5 — claim-chain consistency check

Chain: Claim → Estimand → Population/frame → Gold unit → MD&A boundary → Primary metric →
Failure/denominator rule → Baseline (if C2) → Downstream recipe (if C4).

| # | Link | State | Finding |
|---|---|---|---|
| 1 | Primary thesis claim | **DEFINED** | D1. |
| 2 | Estimand | **GAP — CC-1** | See below. |
| 3 | Population / frame | **DEFINED and internally coherent** | See CC-2 (positive finding). |
| 4 | Gold unit | **DEFINED (DocumentGold); PageGold status open — CC-3** | |
| 5 | MD&A boundary definition | **DEFINED in principle, rules not written** | Consistent with D7's deferral. Not a contradiction. |
| 6 | Primary evaluation metric | **INFERRED — CC-4** | |
| 7 | Failure / denominator rule | **CONTRADICTION — CC-5** | See section 2. |
| 8 | As-Is identity (C2) | **CORRECTLY GATED — CC-6** | Not a contradiction. |
| 9 | Downstream recipe (C4) | **GAP — CC-7** | |

### CC-1 — the estimand is not fixed (weighting)

D1 names the claim; it does not name the summary quantity. D4 selects the frame but not
the weighting. Phase 3's D3/Q3 option B explicitly required a choice between a
**document-weighted mean** and an **equal-issuer mean**, with the other reported as
sensitivity. The author's D4 answer does not make that choice, while D7 requires the
evaluation to be "issuer-aware" — which points at, but does not state, issuer weighting.

**Status: AUTHOR DECISION REQUIRED.** **Depends on it:** B6 (an issuer-weighted estimand
changes what the reliability sample must represent) and the Phase 5 sample allocation.
**Not repaired here.** No weighting is assumed anywhere in this document.

### CC-2 — the frame is coherent (positive finding; D4 and D5 agree)

**REPO-VERIFIED**, recomputed from `artifacts/t0_4/benchmark_manifest.json` (`track_b`,
208 document records):

| `input_status` | FIT | VALIDATION | HOLDOUT | UNASSIGNED_HISTORICAL | Total |
|---|---:|---:|---:|---:|---:|
| `PROFILED_LOCAL_INPUT` | 92 | 48 | 54 | 0 | **194** |
| `INPUT_UNAVAILABLE` | 2 | 4 | 0 | 8 | **14** |
| **Total** | 94 | 52 | 54 | 8 | **208** |

The **available-byte frozen evaluation frame of D4 is exactly the 194 `PROFILED_LOCAL_INPUT`
documents**, and the **14 missing PDFs of D5 are exactly the `INPUT_UNAVAILABLE` set**.
All 8 `UNASSIGNED_HISTORICAL` records are `INPUT_UNAVAILABLE`, so they fall outside the
frame automatically and raise no split-assignment question. D4 and D5 are mutually
consistent and jointly well-defined. No contradiction.

**One open sub-question follows from this, and it is a B8 question:** the frame as defined
includes HOLDOUT's **54** documents. See section 3 / B8.

### CC-3 — PageGold vs DocumentGold

D3 defines the Gold concept at document level (a contiguous page span) — that is
`document_gold`. The frozen `configs/t0_4/gold_schema.json` also defines `page_gold`
(reference text, lines, headings, reading-order pairs, factual fields, regions).

Under C1 alone, `page_gold` is **not required**. It is required only if a retained claim
needs page-level text fidelity — i.e. if C2 evaluates a text-quality change, or if C4
activates. **Status: CONDITIONAL.** Do not build PageGold for C1. Do not delete the
schema either; C4's antecedent (CC-7) is undecided.

### CC-4 — the primary metric is inferred, not stated

The frozen `configs/t0_4/metrics_spec.json` Level `C_ARPIPE_DOCUMENT_TASK` declares
`unit = "document"` and `primary = "page_span_iou"`. That is consistent with D1, but the
author did not name a metric. **Status: INFERRED.** Treated here as the presumptive
primary endpoint solely to expose the CC-5 mismatch; confirm before Gold Method.

### CC-6 — C2's gate is correctly constructed (not a contradiction)

D6 defines As-Is *relationally* ("the coherent historical operational ARPipe system
immediately before the specific change being evaluated") rather than by naming a commit,
and makes the claim self-cancelling if identity cannot be established. That is a sound
construction: it does **not** require choosing a convenient historical commit to unblock
Phase 4, and per the task's own §2 rule, unresolved baseline identity therefore does not
block this phase. C2's gate remains **UNRESOLVED**; no B-item decision below depends on
resolving it now.

### CC-7 — C4's antecedent is undecided, and the recipe does not exist

D9 retains a bounded downstream analysis **if** the climate measure is a substantive
thesis result. The author did not answer whether it is. Separately, no fixed
climate-text measure is identified in the repository at `112d8297`.

**Status: AUTHOR DECISION REQUIRED (antecedent) + UNRESOLVED (recipe).**
**Depends on it:** B7 (a sequence-aware score would need reading-order reference; an
order-invariant bag-of-words score would not) and CC-3 (PageGold). This is precisely why
B7 below is **DEFER**, not **MOOT** — calling B7 moot would silently resolve D9.

---

## 2. C1 failure and denominator check

C1 is the primary claim, so the five evaluation cases are checked explicitly against the
frozen metric contract (`configs/t0_4/metrics_spec.json`,
SHA-256 `d7590bebe271163f2ad341cace35f4749754cf22da3018cef32b12ad09c66336`) and the frozen
`gold_schema.json` (SHA-256 `e8b33a4a0e04da72c3572604ca3f82677920617607abe266717975ee3cc65247`).

| # | Case | Can Gold record it? | Can the frozen metric contract express it? |
|---|---|---|---|
| 1 | Gold present / prediction present | Yes — `mda_present=true`, `mda_start_page`, `mda_end_page` | **Yes.** `page_span_iou`, `exact_start`, `start_within_1`, `exact_end`, `end_within_1`, `overrun_pages`, `underrun_pages`. |
| 2 | Gold present / **prediction missing** | Yes (Gold side) | **NO RULE.** Level C declares no denominator and no failure/abstention metric. `failure_rate` exists only under `LEGACY_FONT_REMAP`. `denominators_required: true` is scoped **inside `A_OCR`**, not Level C. |
| 3 | Gold absent | Yes — `mda_present=false`, start/end `null` | **Partially.** `mda_present_absent_accuracy` is a *secondary* metric. `page_span_iou` has no defined value for an empty Gold span, and no rule says whether such documents enter or leave the primary denominator. |
| 4 | Ambiguous / non-standard Gold | **Weakly.** `boundary_ambiguity` is an **unconstrained free string** (`{"oneOf":[{"type":"string"},{"const":"NOT_YET_ANNOTATED"}]}`) — no controlled vocabulary, no reason codes. `excluded_neighbor_sections` is a free-string array. There is **no `admissible_spans` field**. | **No.** No tolerant or ambiguity-aware primary metric; no rule for scoring against an admissible set. |
| 5 | Invalid / out-of-range system output | n/a | **NO RULE.** No validity predicate, no out-of-range handling at Level C. |

### Finding C1-D1 — the frozen contract cannot express the adopted C1 estimand

**Evidence status: REPO-VERIFIED.** Cases 2, 4 and 5 have no expression at Level C, and
case 3's denominator membership is undefined. In addition,
`uncertainty.missing_pair_policy` reads:

> "Report missingness by engine and metric; paired differences use only units with both
> outputs and include the paired denominator."

So any paired comparison is **conditional on successful pairs** — system failures are
excluded from the compared quantity by construction. Phase 3 already flagged this
("the proposed failure-inclusive paired metric differs from the frozen both-outputs-only
missing-pair policy").

D1 claims **"reproducible … localization"** of a bounded population. A denominator that
silently drops the documents the system failed on does not measure that; it measures
performance conditional on not failing, which is a different and weaker claim.

**This is a mismatch between the adopted claim and the frozen protocol. It is NOT repaired
here.** Per the task's §7:

- The denominator is **not** silently changed.
- The mismatch is marked **REQUIRING A FORMAL EVALUATION-PROTOCOL AMENDMENT**.
- **Where it must be authorized:** the **Phase 5 Gold Method freeze**, as an explicit
  amendment to `configs/t0_4/metrics_spec.json` Level `C_ARPIPE_DOCUMENT_TASK`. It cannot
  be done inside B6, and B6 must not be used as a vehicle for it.
- Until amended, any C1 result must either state the successful-pair conditional estimand
  and disclose the selection effect, or wait for the amendment.

**Gold truth and the evaluation denominator are separate questions.** Deciding B6 settles
how Gold is produced; it does **not** settle case 2/4/5 accounting. Both are needed, and
they are authorized in different places.

**Consequence for B6 (this is why B6 is DECIDE_NOW, not deferrable):** case 4 shows the
frozen Gold schema cannot *record* the ambiguity structure D3 mandates ("explicit rules
for absent, ambiguous, embedded, annexure, and other non-standard cases"). `mda_present`
covers *absent*. Nothing covers *embedded*, *annexure*, or *repeated* MD&A sections
except two free-string fields. That is a Gold-design decision, and it is B6's.

---

## 3. 79-unit benchmark protection

Recorded explicitly, as required:

> **The corrected 79-unit benchmark is a historical benchmark record. Correcting its
> arithmetic does not authorize reuse as the Phase 4/5 Gold sample, final evaluation
> sample, or population denominator.**

Reinforcing facts, so the protection cannot be eroded by convenience:

- The 79 units are **page** units drawn from `track_a`. The adopted C1 Gold unit under D3
  is a **document-level** span. They are not the same unit.
- The 79 units are the **B3 Oracle-routing** eligibility set — a routing construct, and
  D10 defers routing.
- `track_a` covers only **173 of 194** documents; it is not a document-level frame.
- The corrected split (FIT 52 / VALIDATION 27) contains **no HOLDOUT units**, so it cannot
  serve a final evaluation population under any reading.
- The figures **121** and **106** are likewise not Gold populations; see errata E-2.

Reuse of any of these sets as Gold requires an explicit author-adopted sampling decision
taken in the Phase 5 Gold Method freeze. **No such decision is proposed here.**

---

## 4. Step 2 — B1–B8 triage

Every §9 hypothesis is tested individually below and explicitly confirmed or refuted.

| Item | Classification | One-line basis |
|---|---|---|
| **B1** | **DEFER_UNTIL_TRIGGER** | D10 defers mechanisms; and the legacy-evidence population is concentrated in FIT, absent from VALIDATION. |
| **B2** | **DEFER_UNTIL_TRIGGER** | Strictly dependent on B1 (register: "Strictly dependent on B1"). |
| **B3** | **DEFER_UNTIL_TRIGGER** | Oracle-routing population; D10 defers routing; C3 not adopted. |
| **B4** | **DEFER_UNTIL_TRIGGER** | Selector is bound to the B3 oracle population, which is deferred. |
| **B5** | **DEFER_UNTIL_TRIGGER** | Oracle evidence channels; no Oracle construct is adopted. |
| **B6** | **DECIDE_NOW** | C1 is primary and requires independent, reliable human DocumentGold spans. |
| **B7** | **DEFER_UNTIL_TRIGGER** | Reading order is not an adopted outcome — but C4's antecedent is open, so not moot. |
| **B8** | **DECIDE_NOW** | The adopted frame (CC-2) includes HOLDOUT's 54 documents; and delay forecloses the strongest governance option. |

**Two of eight are DECIDE_NOW.** No item was forced into DECIDE_NOW.

### B6 — DECIDE_NOW (hypothesis CONFIRMED)

*Hypothesis tested: "B6 may be DECIDE_NOW because C1 requires reliable independent human
Gold MD&A spans."*

**CONFIRMED.** Evidence:

- D1 adopts C1 as primary; D3 defines the Gold unit as a document-level contiguous page
  span. Level C's unit is `document` and its primary is `page_span_iou` — a metric
  computed **against DocumentGold**. Without DocumentGold there is no C1 result at all.
- **REPO-VERIFIED gaps that only B6 can close:**
  - `gold_schema.json` `document_gold` has **no overlap rate, no sampling rule, no
    stratification requirement** (register `DEC-B6.verified_state`, re-read and confirmed).
  - `dataset/corpus_freeze/annotation_roster.csv` has a **single `annotator_id` column**
    over **25 document rows**, all currently unannotated. A single-annotator column cannot
    represent independent double annotation.
  - The schema's `oneOf` admits exactly **two** record types — `page_gold` and
    `document_gold`. There is **no raw-independent-annotation record type and no separate
    adjudicated record type**, so "preserve pre-adjudication disagreement immutably"
    is currently unrepresentable.
  - `annotation_provenance` is declared as bare `{"type": "object"}` — unconstrained. No
    annotator identity, timestamp, independence marker or blinding field is required.
  - `boundary_ambiguity` is an unconstrained string (finding C1-D1, case 4), so D3's
    "explicit rules for absent, ambiguous, embedded, annexure, and other non-standard
    cases" cannot currently be *recorded*, only prose-described.
  - The roster carries fields the schema does not (`heading_form`, `per_page_text_quality`,
    `minutes_spent`, `saw_pipeline_output`) — a roster/schema divergence B6 must reconcile.
- Phase 3's impact map independently reached "C1 | B6 | YES for DocumentGold".

**Not deferrable:** every downstream step (Phase 5 allocation, annotation, evaluation)
consumes the B6 design. Deferring it blocks C1 entirely.

### B8 — DECIDE_NOW (hypothesis CONFIRMED)

*Hypothesis tested: "B8 may be DECIDE_NOW because final evaluation requires HOLDOUT
governance."*

**CONFIRMED, and on a stronger basis than the hypothesis states.** Evidence:

- **The adopted population already contains HOLDOUT.** D4 names "the available-byte frozen
  evaluation frame". CC-2 shows that frame is the 194 `PROFILED_LOCAL_INPUT` documents,
  of which **54 are HOLDOUT**. The author's own population choice therefore places
  HOLDOUT inside the primary evaluation population. This is a recomputed repository fact,
  not an inference about intent.
- **The decision is time-critical independently of when access happens.** The register's
  recommended Option 1 is "default deny **before system freeze**" — HOLDOUT annotation
  only after the pipeline, thresholds, schemas and FIT/VALIDATION evaluations are
  permanently frozen. That option constrains the *ordering* of all intervening work. It
  cannot be adopted retroactively: once development continues without a freeze discipline,
  the evidence that the system was frozen before HOLDOUT exposure can no longer be
  created. **Deferring B8 silently destroys its strongest option.** This is the decisive
  argument and it does not depend on any access occurring now.
- `benchmark_config.json` already sets `holdout_policy.allowed_before_final_freeze: false`,
  creating a default-deny stance — but annotation is listed under neither allowed nor
  forbidden uses, so the gap B8 exists to close is real and currently open.
- **`historical_pre_T0_exposure` remains `UNKNOWN`** (P2-26) and is treated as UNKNOWN
  throughout. It is not rewritten as CLEAN or CONTAMINATED.

**No HOLDOUT access, annotation, inspection or content read occurred in this task.** The
counts above come from `benchmark_manifest.json` metadata only.

### B4 — DEFER_UNTIL_TRIGGER (hypothesis CONFIRMED, conditional branch not taken)

*Hypothesis tested: "B4 may be DECIDE_NOW only if the adopted Gold design actually uses
the affected deterministic double-annotation selector."*

**CONFIRMED — and the condition is NOT met.** Evidence:

- The B4 selector is specified in `configs/t0_4/oracle_routing_spec.json`. Its
  `dependencies` field states it "Depends on B3 (eligibility pool)". It is bound to the
  **Oracle** population, which is deferred with B3.
- The register's `DEC-B6` states explicitly: **"The 25% oracle rule does not automatically
  govern PageGold or DocumentGold."** The adopted Gold design (D3, document spans) is
  therefore **not** the population the historical B4 selector selects from.
- Accordingly, per task §14, the historical serialization is **not resolved here**: no
  domain tag, `unit_bytes`, field order, separator, encoding, integer or ID
  representation, threshold or strictness rule is decided, and **no test vectors are
  computed**. Resolving them would be unnecessary work on a deferred item.

**Carry-forward constraint (a fact, not a B4 decision):** whatever selection mechanism B6
eventually uses, the frozen `selection_rank` is unsuitable — it is a per-cell minimum
yielding 355/475 (74.7%) in the hex 0–3 band, not ~25% (re-verified in errata E-1). This
constraint travels with B6 and is recorded in the decision sheet as a design constraint.

**Trigger:** (a) adoption of an Oracle-routing Gold layer (i.e. B3/B5 reopen), **or**
(b) an author decision in the Phase 5 Gold Method freeze to reuse the B4
canonical-serialization mechanism for DocumentGold double-annotation selection. Under (b)
the serialization questions listed in task §14 must be resolved *then*, together with
whether adopting a corrected serialization requires a formal T0.4 protocol amendment.

### B3 — DEFER_UNTIL_TRIGGER (hypothesis CONFIRMED)

*Hypothesis tested: "B3 may be deferred if it only supports the old page-level OCR/oracle
benchmark."*

**CONFIRMED.** `DEC-B3` defines the population "eligible for **Oracle Route** annotation"
— a routing construct at page unit. D10 defers routing mechanisms; C3 is not adopted; and
Phase 3 independently recorded C3 as NOT YET SUPPORTABLE for a separate reason (no
page→document Oracle transformation exists). The unit is also wrong for C1 (page, not
document — see section 3).

The errata correction (FIT 52 / VALIDATION 27) is a **documentation** correction and does
**not** activate B3. **Trigger:** adoption of a routing/Oracle claim under D10's
"later failure-driven claim explicitly requires them", or any retained claim that consumes
the Oracle population.

### B5 — DEFER_UNTIL_TRIGGER (hypothesis CONFIRMED)

*Hypothesis tested: "B5 may be deferred if Oracle/routing attribution is not an adopted
claim."*

**CONFIRMED.** `DEC-B5` governs "evidence channels **for route annotators**" and the
construct that **route labels** represent. No route-label Gold is adopted under D10.

**Checked explicitly — does B5's finding leak into B6?** B5's substantive finding is a
category mismatch: rendered pixels cannot reveal `ToUnicode` tables, invisible text layers
or font mapping, so pixels cannot support semantic `NATIVE`/`LEGACY` labels. **That
constraint does not transfer to MD&A span Gold.** An MD&A start/end boundary is determined
by *visible* content — headings, section transitions, printed structure — which is exactly
what a rendered page does expose. Image-based or document-context annotation is therefore
epistemically adequate for D3's Gold concept, and is in fact preferable: an annotator
reading the rendered page records the correct boundary even where the text layer is
corrupt, which keeps Gold independent of the extraction failure being measured.

B6 may therefore be decided without deciding B5. **Trigger:** same as B3.

### B7 — DEFER_UNTIL_TRIGGER (hypothesis PARTIALLY REFUTED)

*Hypothesis tested: "B7 may be moot/deferred if reading order is not an adopted outcome."*

**DEFER confirmed. MOOT refuted.** Evidence:

- D1's endpoint is a START–END page span. Reading order is not part of it, and
  `page_span_iou` is order-invariant. So B7 is not required for C1. Phase 3 concurs:
  "B7 … C1/C2/C5 only for an added order claim".
- **But it is not moot.** Phase 3 records "C4 | B7 | Sequence-aware scores can depend on
  reading order; bag-of-words scores may not | **Conditional on actual score recipe**".
  Per CC-7, D9's antecedent is undecided and no climate recipe is fixed. Declaring B7
  moot would therefore silently resolve an open author conditional — prohibited by the
  operating rules. `DEC-B7` is also the only item that would govern the frozen
  `reading_order_pairs` field, which still exists in `page_gold`.

**Trigger — either of:** (a) D9's antecedent is answered YES *and* the fixed climate-text
measure is shown to be sequence-sensitive; or (b) reading order is adopted as an outcome
in its own right. If D9 is answered NO, B7 can be re-triaged to MOOT at that point — but
that is a later classification, not this one.

### B1 — DEFER_UNTIL_TRIGGER (hypothesis PARTIALLY REFUTED)

*Hypothesis tested: "B1/B2 may be moot for the primary outcome claim if legacy routing is
not itself a thesis claim."*

**DEFER confirmed. MOOT refuted.** Two independent lines of evidence:

**(i) The claims do not require B1.** D10 states the thesis evaluates the localization
**outcome**, not the routing mechanism. A C1 outcome evaluation measures what the current
pipeline actually does, *including its failures* — it does not require a route contract to
be decided first. C2 is gated and, per D6, concerns "the specific change being evaluated";
nothing designates that change as a routing change. So no adopted claim requires B1 now.

**(ii) Why it is nevertheless NOT moot — and why it still does not fire now.** Errata
E-3.2 establishes that **225 of 437 (51.5%) `legacy_font_confirmed` pages carry detector
kind `digital`**, which is not in `NEEDS_OCR`. Those pages are read from a potentially
corrupt text layer. Since ARPipe localizes MD&A from extracted text, corrupt text is a
plausible failure mechanism **for C1's own primary outcome**. Legacy encoding is therefore
a live threat-to-validity for the adopted claim, not an irrelevance — which is exactly
what "moot" would assert.

**Whether that threat is material to the adopted population — computed, not assumed.**
Joining the historical P-B3 per-page record to `track_b` splits (join on the
`issuer_fiscalyear` key prefix, since P-B3 document IDs carry an extra hash suffix):

| Document (issuer_FY) | Split | Legacy-evidence pages |
|---|---|---:|
| INE008A01015_2025 | FIT | 584 |
| INE008A01015_2024 | FIT | 553 |
| INE008A01015_2017 | FIT | 386 |
| INE008A01015_2018 | FIT | 346 |
| INE008A01015_2012 | FIT | 192 |
| INE008A01015_2013 | FIT | 7 |
| INE001O01029_2013 | HOLDOUT | 4 |
| INE171A01029_2017 | HOLDOUT | 2 |
| INE171A01029_2025 | HOLDOUT | 1 |

**Split distribution: FIT 6 documents, HOLDOUT 3 documents, VALIDATION 0 documents.**
Issuer concentration: 3 issuers of 36; 6 of the 9 documents are a single issuer
(INE008A01015, IDBI Bank, 2,068 legacy pages = 99.66% of all corpus legacy pages).
The three HOLDOUT documents carry **7 legacy pages in total**.

**Reading of this, with limits preserved.** On the available historical evidence, legacy
encoding is concentrated in the **development** partition and is negligible-to-absent in
the partitions that carry the evaluation weight. So task §16's **trigger C** — "a required
document-quality audit shows unresolved legacy encoding materially threatens the adopted
primary evaluation population" — **does not currently fire.**

**Limits that must travel with that reading (do not drop them):** the P-B3 predicate is a
heuristic, not Gold; "no evidence in VALIDATION" is **not** proof of absence — genuine
legacy-font occurrence in the corpus remains **UNRESOLVED**, exactly as
`DEC-B1.empirical_status` records; and the join is on an ID prefix. This paragraph
bounds a *triage* decision. It is **not** a prevalence estimate and must never be cited as
one.

**Triggers (task §16), any one of which reopens B1:**

- **A** — a retained thesis claim explicitly concerns legacy-font prevalence or handling.
- **B** — Phase 9 failure analysis identifies a false-native or extraction failure
  attributable to legacy encoding.
- **C** — a required document-quality audit shows unresolved legacy encoding materially
  threatens the adopted primary evaluation population. *Given the split distribution
  above, the concrete form this would take is new evidence of legacy encoding in
  VALIDATION or in the 54 HOLDOUT documents beyond the 7 pages recorded.*

**P2-LF is NOT invoked.** No legacy-font research cycle was run and none is proposed. No
`PHASE4_LEGACY_E3_DESIGN.md` is produced, because §20 conditions it on B1 being genuinely
DECIDE_NOW, and it is not. The bounded Legacy E3/X1 forensic design remains available and
gated behind triggers A/B/C.

### B2 — DEFER_UNTIL_TRIGGER

`DEC-B2.dependencies` reads "**Strictly dependent on B1**", and its Option 1 makes
legacy-vs-broken_text precedence `NOT_APPLICABLE` under the recommended B1 contract. With
B1 deferred, B2 cannot be decided independently and no adopted claim requires it.

**Trigger:** B1 reopening under any of triggers A/B/C, **or** an adopted decision to change
execution priority among overlapping triage predicates.

**Standing constraint preserved (fact, not a decision):** `sampling_stratum_priority` from
`sampling_spec.json` **must never** be used as routing precedence — the register calls
reusing it "a severe category error". Deferring B2 does not weaken that prohibition.

---

## 5. D1–D10 → B1–B8 dependency audit

Evidence-based and built from this repository at `112d8297`, not from a prewritten
mapping. Dependency types: **REQUIRED NOW**, **CONDITIONAL**, **DEFERRED**, **MOOT**.

| Author decision | B item(s) | Why the dependency exists (evidence) | Type |
|---|---|---|---|
| **D1** primary claim = START–END span localization | **B6** | Level C `unit=document`, `primary=page_span_iou` is scored against DocumentGold; no DocumentGold ⇒ no C1 result | **REQUIRED NOW** |
| D1 | **B8** | "evaluated" implies a final reported result; the adopted frame contains 54 HOLDOUT documents (CC-2) | **REQUIRED NOW** |
| D1 | B7 | `page_span_iou` is order-invariant; order is outside the endpoint | **DEFERRED** |
| D1 | B3/B4/B5 | Oracle is a page-level routing construct outside the span endpoint | **DEFERRED** |
| **D2** bounded; C2 only if comparator coherent | **B6** | a paired comparison needs the *same* independent reference in both arms | **CONDITIONAL** (on C2 activating) |
| D2 | B1/B2 | a baseline-relative claim about a *routing* change would need route semantics; no such change is designated | **CONDITIONAL** |
| **D3** Gold = contiguous page span + rules for absent/ambiguous/embedded/annexure | **B6** | `boundary_ambiguity` is a free string, no `admissible_spans`, no adjudication record type — D3's rules are unrecordable today (finding C1-D1 case 4) | **REQUIRED NOW** |
| D3 | B7 | a page-span Gold unit does not entail an order reference | **DEFERRED** |
| **D4** population = available-byte frozen frame | **B8** | the frame demonstrably includes HOLDOUT's 54 documents | **REQUIRED NOW** |
| D4 | **B6** | the eligible Gold population and its issuer structure must be defined over that frame (36 issuers; D7 requires issuer-awareness) | **REQUIRED NOW** (design) / parameters **DEFERRED to Phase 5** |
| D4 | B3 | Oracle eligibility is a different, page-level population over 173 of 194 documents | **DEFERRED** |
| **D5** 14 missing PDFs not required | — | CC-2: the 14 are exactly `INPUT_UNAVAILABLE` and already outside the frame; no B item is engaged | **MOOT** (no B dependency) |
| **D6** As-Is = coherent system before the evaluated change | B6 | both arms need the same reference layer | **CONDITIONAL** (gate unmet) |
| D6 | B1/B2 | engaged only if the evaluated change is a routing change | **CONDITIONAL** |
| **D7** proportionate issuer-aware; no size frozen here | **B6** | B6 must define the reliability *design*; D7 explicitly withholds the *numbers* | **REQUIRED NOW** (design only) |
| D7 | B4 | a rate/selector is a Phase 5 parameter, and the oracle selector is the wrong population anyway | **DEFERRED** |
| **D8** no acquisition | — | acquisition engages no B item | **MOOT** (no B dependency) |
| **D9** downstream climate retained *if* substantive | **B7** | sequence-aware scores may need order reference; recipe unknown (CC-7) | **CONDITIONAL** |
| D9 | B6 (PageGold limb) | a text-level downstream comparison would need page-level reference text (CC-3) | **CONDITIONAL** |
| **D10** outcome not mechanism | **B1, B2, B3, B5** | routing/legacy/REMAP mechanisms are explicitly investigated only on a later failure-driven claim | **DEFERRED** |
| D10 | B4 | the selector exists to support Oracle route annotation | **DEFERRED** |

**Summary:** REQUIRED NOW appears only against **B6** and **B8**. This matches section 4
and was derived independently of it.

---

## 6. What the prior audits already settled

Conclusions already established by the completed B1–B8 audits (Phase 2 foundation
integrity audit + findings JSON; Phase 2 research B1–B8 package; Phase 2.1 register;
Phase 3 impact map). **These are not re-run and no new literature cycle was performed.**

### Established fact (REPO-VERIFIED)

- `PageKind` has six members and **no `legacy_font`**; no producer exists (`models.py:15-22`).
- `legacy_font_candidate` is **set-identical** to detector `broken_text` (errata E-3.1).
- `broken_text`, `scanned`, `vector_text` and `hybrid` are all in `NEEDS_OCR`; `digital` is not.
- The **REMAP lane exists in prose and schema placeholders only** — no code, no font-table
  parser, no remapping table.
- **No frozen routing precedence exists.** `sampling_stratum_priority` is a *sampling*
  relation and reusing it as routing precedence is a category error.
- `native_clean_control` is **0 of 475 as a condition label** and is **not a clean native
  set** as a stratum (22 hybrid units across all splits; 15 in FIT/VALIDATION).
- The frozen `selection_rank` is a **per-cell minimum** and is unsuitable as an
  independent 25% selector (355/475 = 74.7% in hex band 0–3).
- **Pixels cannot diagnose font encoding** (ISO 32000-1) — the B5 category mismatch.
- `gold_schema.json` defines PageGold/DocumentGold with **no overlap rate, sampling rule
  or stratification**; the roster has a **single `annotator_id`**.
- `reading_order_pairs` are **string pairs with no specified atomic unit**; PyMuPDF block
  coordinates are engine heuristics, unsuitable as reference Gold.
- `holdout_policy.allowed_before_final_freeze: false` creates **default-deny**; annotation
  is listed under neither allowed nor forbidden uses.
- **No implemented oracle double-annotation selector exists** in the frozen tree — B4 is a
  methodological underspecification, **not an implementation bug**.

### Unresolved question (UNKNOWN / UNRESOLVED — must stay that way)

- **Genuine legacy-font occurrence** in the ARPipe corpus — UNRESOLVED. Synthetic LF
  fixtures do not establish real prevalence.
- **Historical pre-T0 HOLDOUT exposure** — **UNKNOWN** (P2-26). Not ABSENT, not CLEAN,
  not CONTAMINATED.
- **Page→document Oracle transformation** — missing; C3 not supportable regardless of
  label count.
- **A coherent As-Is baseline identity** — unresolved (Phase 3).
- **Precision/recall of the table, TOC, annexure, OCR-layer, language and legacy proxies**
  against independent labels — unmeasured.

### Proposed recommendation (PROPOSED — never adopted)

One-class OCR contract for B1; precedence `NOT_APPLICABLE` for B2; purpose-defined
enumerated oracle population for B3; domain-separated full-digest threshold for B4;
multi-channel evidence bundle *or* visual-action relabelling for B5; hybrid
random-plus-diagnostic reliability for B6; annotator-defined atomic visual regions for B7;
default-deny-before-freeze for B8. **All eight remain `PENDING_AUTHOR_DECISION`.**

### Author decision required

All eight B items. Of these, only **B6** and **B8** are required now (section 4). Plus,
newly surfaced by this triage and **not** B-item decisions: **CC-1** (estimand weighting),
**CC-7** (D9 antecedent), **finding C1-D1** (metric-contract amendment), and **PG-1**
(write the Phase 3 choices into the sheet).

---

## 7. Research integration

From `PHASE2_RESEARCH_B1_B8.md` and `PHASE2_RESEARCH_EXPERIMENTS.md`. The complete Phase 2
research is **not** repeated.

### LIVE AFTER PHASE 3

| Item | Why it stays live |
|---|---|
| **X4 — Gold protocol/tool calibration** | Directly serves B6 (DECIDE_NOW). Register marks it "Required before Gold". Its outputs (invalid-rate, field-specific pre-adjudication agreement, reason-coded disagreement) are exactly what B6's design must be validated against. |
| **X7 — MD&A boundary ambiguity pilot** | Directly serves D3's "explicit rules for absent, ambiguous, embedded, annexure, non-standard" and finding C1-D1 case 4. It is the evidence that would show whether an admissible-span schema is needed or a simple heading-to-heading rule suffices. |
| **X6 — HOLDOUT provenance audit** | Serves B8's historical-exposure limb. Its stop rule ("exhausted records ⇒ retain UNKNOWN, do not equate missing logs with a clean history") is the correct discipline for `historical_pre_T0_exposure`. Remains **optional**. |
| **X5 — double-annotation selector verification** | Live **only in its generic form**: whatever selector B6 adopts must be enumerated and independently reproduced before annotation. Its B3/B4-specific framing is deferred with those items. |
| **X0 — semantic-contract conformance audit** | Live as the mechanism that would carry finding C1-D1's metric amendment and B6's schema changes without ambiguity. |
| **X3 — TOC/outline candidate-utility** | **Conditionally live.** `candidate_recall*` are Level C secondary metrics under C1, so this bears on the adopted claim — but it is not required for the primary endpoint. Lowest priority of the live set. |

### SUPERSEDED / NO LONGER NEEDED (under the adopted claims)

| Item | Why |
|---|---|
| **X1 — legacy-font forensic confirmation** | Superseded *for now* by the B1 DEFER. Not deleted: it is the designated instrument if trigger A/B/C fires. Do not run it now. |
| **X2 — hybrid native/OCR/arbitration pilot** | A routing-mechanism study. D10 excludes mechanism claims. Also the most expensive proposal (1–2 weeks + approved compute) with no adopted claim to serve. |
| **Oracle-routing research limb generally** (the B3/B4/B5 analysis) | No adopted claim consumes route labels. Retained as historical record; not a work item. |
| **Reading-order granularity research** (the B7 limb) | No adopted order outcome. Revisit only under B7's trigger. |
| **Further broad literature cycles** | The register's external evidence (ISO 32000-1, PDF/A conformance, annotation-reliability literature) already establishes what is needed for the live items. No new cycle is proposed. |

### The P2-LF legacy research module

Kept as a **separate, gated module**. It is not merged into Phase 4 and is **not invoked**.

- **Phase 4 answers:** *do we need this research?* — **Answer: NO, not now.** See B1 above:
  no adopted claim requires it, and the legacy-evidence population is concentrated in FIT
  with zero affected VALIDATION documents.
- **P2-LF answers:** *what does the targeted external research establish?* — unasked.
- **Invoke only if** B1 trigger A, B or C fires. At that point the bounded Legacy E3/X1
  forensic design (FIT-only scope, sample construction, evidence ladder, stop rule, cost,
  provenance, no production changes, no remapping, no candidate-set redefinition from
  experiment output) must be prepared **as design only**, before any execution.

---

## 8. Stop condition

This document and the [decision sheet](PHASE4_DECISION_SHEET.md) complete Phase 4.

No B decision is adopted. No production code, frozen T0–T0.4 artifact, Gold data, HOLDOUT
data, OCR output, REMAP output, corpus PDF, baseline implementation or experiment output
was modified. No Gold annotation was created. No HOLDOUT content was accessed. No OCR,
REMAP or LF experiment was run. No acquisition occurred. The roadmap was not redesigned.

**The next action is AUTHOR REVIEW of the Phase 4 decision sheet.**
