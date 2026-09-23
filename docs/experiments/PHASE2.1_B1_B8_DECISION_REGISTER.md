# Phase 2.1 — B1–B8 Decision Register & Governance Specification

**Status:** authoritative decision preparation record  
**Decision Authority:** Project Author  
**Repository Basis:** `D:\sem_iitk\sem9\thesis\sep_week1\arpipe-phase2.1-foundation-normalization`  
**Base Commit:** `03a63f5d7d79bac6a0bab0ffc33af42004e78935`  
**Governance Guard:** `RECOMMENDATION cannot become ADOPTED without AUTHOR_RATIFICATION`. Every `ADOPTED` record must contain author, timestamp, selected option, rationale, and effective protocol version; otherwise it is `INVALID`.

---

## 1. Governance Overview & Status Summary

Phase 2 and post-closure audits identified eight unresolved methodological decisions (B1–B8) inherited from the T0.4 benchmark setup and gold-method research. 

Because the project author is the sole decision authority, **all eight items currently remain `PENDING_AUTHOR_DECISION`**. Recommendations are documented to provide objective constraints and clear handoffs, but are strictly prohibited from being treated as adopted policy.

### Overall Status Block:
```
PHASE2.1_STATUS = WAITING_FOR_AUTHOR_DECISIONS

DOWNSTREAM_EXECUTION_AUTHORIZED = NO

GOLD_ANNOTATION_AUTHORIZED = NO
OCR_EXECUTION_AUTHORIZED = NO
EXPERIMENT_X1_X7_AUTHORIZED = NO
HOLDOUT_ACCESS_AUTHORIZED = NO

AUTHOR_DECISIONS_REQUIRED = B1,B2,B3,B4,B5,B6,B7,B8

FORMAL_T0.4_AMENDMENT_EFFECTIVE = NO
```

---

## 2. Comprehensive B1–B8 Decision Records

### B1 — Legacy Route & Class-to-Route Map

- **decision_id:** `DEC-B1`
- **question:** Should legacy fonts be treated as an operational production routing class with a dedicated REMAP lane, or should legacy-candidate pages follow the verified production OCR route while retaining legacy font occurrence as a forensic research question?
- **verified_state:**
  - `PageKind` in `arpipe/models.py` has no `legacy_font` enum and no producer in `arpipe/triage.py`.
  - T0.4 sampling stratum `legacy_font_candidate` is byte-for-byte identical to detector `broken_text` across all 803 candidate pages (24 documents) and 20 sampled units.
  - In production code (`arpipe/triage.py`), `PageKind.BROKEN_TEXT` is an active member of `NEEDS_OCR` and routes directly to `_ocr_pages`.
  - The "REMAP lane" exists only in prose descriptions and schema placeholders; no operational code, font-table parser, or Unicode remapping table exists in the repository.
  - Post-closure T0.4-LF research recommended collapsing into one OCR class, but explicitly recorded status `T0.4_LF_BLOCKED` ("No rule was adopted").
  - External literature (ISO 32000, Vasantharajan et al. 2021) establishes that legacy font encoding failures are technically possible in non-standard PDFs, but does not establish their prevalence in the ARPipe Indian annual report corpus.
- **status:** `PENDING_AUTHOR_DECISION`
- **current_verified_production_fact:** `broken_text → OCR`
- **empirical_status:** genuine legacy-font occurrence remains unresolved.
- **recommended_current_contract:**
  - Do not create a production REMAP route.
  - Retain legacy as a separate forensic research attribute/track.
- **future_remap_consideration:**
  - Only after empirical work (X1) establishes:
    1. reproducible legacy class,
    2. reliable detector,
    3. reproducible remapping operation,
    4. measurable downstream advantage.
- **interpretation_constraint:**
  - This does not establish that REMAP is useless.
  - This does not establish that legacy-font pages are absent.
- **selected_option:** `null`
- **rationale:** Awaiting author decision. Adopting a non-existent REMAP route into production or benchmark scoring would introduce unexecutable sentinels.
- **estimand:** Not applicable.
- **dependencies:** Gates B2 (precedence) and future routing benchmarks.
- **effective_protocol_version:** `null`
- **affected_artifacts:** `configs/t0_4/benchmark_config.json`, `oracle_routing_spec.json`, `metrics_spec.json`
- **supersedes:** Historical prose references to an operational REMAP lane.
- **future_validation:** Forensic Experiment X1 (FIT-only source inspection).
- **owner:** Project Author
- **timestamp:** `PENDING`

---

### B2 — Route Precedence for Overlapping Classes

- **decision_id:** `DEC-B2`
- **question:** When a physical page satisfies multiple triage or condition predicates, what rule determines execution priority?
- **verified_state:**
  - The repository contains no frozen routing precedence.
  - `sampling_spec.json` contains `sampling_stratum_priority`, which places `legacy_font_candidate` above `broken_text`. However, this priority governs only primary sampling stratum assignment, NOT pipeline execution precedence.
  - Reusing sampling priority as routing precedence would be a severe category error.
  - In actual code (`arpipe/triage.py:_classify`), execution follows sequential `if/elif` blocks: `blank` -> `broken_text` -> text-empty branch (`scanned`, `vector_text`, `digital`) -> `hybrid` -> `digital`.
- **status:** `PENDING_AUTHOR_DECISION`
- **options:**
  - Option 1 (Dependent on B1): If an author decision formally adopts the recommended B1 contract (broken text routes to OCR; legacy retained as forensic attribute), B2 precedence between legacy and broken text becomes `NOT_APPLICABLE`.
  - Option 2: If an author decision adopts a separate operational REMAP route, define explicit deterministic precedence (e.g. Specificity/REMAP first with fallback to OCR on failure).
- **recommended_option:** Under the recommended B1 contract, legacy-vs-broken_text routing precedence is `NOT_APPLICABLE`. Final B2 status remains `PENDING_AUTHOR_DECISION` because B1 has not yet been ratified as an adopted author decision. Enforce that `sampling_stratum_priority` MUST NEVER be used as routing precedence.
- **selected_option:** `null`
- **rationale:** Awaiting author decision on B1 (preserving status `PENDING_AUTHOR_DECISION`).
- **dependencies:** Strictly dependent on B1.
- **effective_protocol_version:** `null`
- **affected_artifacts:** `arpipe/triage.py`, `configs/t0_4/benchmark_config.json`
- **supersedes:** None.
- **future_validation:** Static routing truth table verification (X0).
- **owner:** Project Author
- **timestamp:** `PENDING`

---

### B3 — Oracle Routing Population Specification

- **decision_id:** `DEC-B3`
- **question:** What exact population of units is eligible for Oracle Route annotation?
- **verified_state:**
  - `oracle_routing_spec.json` states that eligible units are selected from FIT and VALIDATION partitions where `condition_labels` include `scanned`, `broken_text`, `vector_text`, `legacy_font_candidate`, or `native_clean_control`.
  - However, `native_clean_control` is a **sampling stratum**, not a condition label. Exactly 0 of 475 units carry it as a condition label.
  - Literal reading: 79 units (FIT: 50, VALIDATION: 29) and completely excludes all 42 native-control units.
  - Stratum reading: 121 units (including 15 hybrid units that sit inside stratum `native_clean_control`).
  - The stratum `native_clean_control` is demonstrably not a clean native set (P2-04: contains 22 hybrid units across all splits).
- **status:** `PENDING_AUTHOR_DECISION`
- **options:**
  - Option 1 (Route-Discrimination Estimand): Sample across all proposed routes and key layout overlaps to evaluate routing classifier accuracy.
  - Option 2 (Strict Native False-Positive Estimand): Include strictly verified digital pages (`PAGE_TEXT_DIGITAL`) with zero scanned/image flags to measure false-OCR penalties.
  - Option 3 (Track-A Benchmark Calibration): Select from the Track-A population using an explicit representation-stratified quota.
- **recommended_option:** Retire the ambiguous label `native_clean_control` in new documentation. Define the oracle population by an explicit boolean predicate over immutable unit fields (`split in {'FIT', 'VALIDATION'}` and defined representation classes), publish an enumerated unit manifest, and state the exact estimand before annotation.
- **selected_option:** `null`
- **rationale:** Awaiting author decision on the intended scientific estimand.
- **estimand:** `PENDING_AUTHOR_SELECTION` (Route discrimination vs. native control vs. calibration).
- **dependencies:** Gates B4 (eligible unit set) and the annotation roster.
- **effective_protocol_version:** `null`
- **affected_artifacts:** `configs/t0_4/oracle_routing_spec.json`
- **supersedes:** Closure Observation 1.
- **future_validation:** Enumerated manifest check (X5).
- **owner:** Project Author
- **timestamp:** `PENDING`

---

### B4 — Deterministic Double-Annotation Selector

- **decision_id:** `DEC-B4`
- **question:** How is the deterministic 25% double-annotation subset selected without bias?
- **verified_state:**
  - `oracle_routing_spec.json` specifies: "deterministic 25% hash slice (SHA-256 rank starting with hex 0, 1, 2, or 3)".
  - The specification names no domain key, no seed, no field order, and no byte encoding.
  - The observed distribution shows that `selection_rank` does not implement the intended independent 25% double-annotation selector under the preregistered selection requirement: `selection_rank` is a per-cell minimum over available pages, resulting in 355 of 475 units (74.7%) and 50 of 79 literal oracle units (63.3%) beginning with hex 0–3.
  - The repository contains no implemented double-annotation selector.
- **status:** `PENDING_AUTHOR_DECISION`
- **hard_requirements:**
  1. Deterministic canonical serialization.
  2. Injective canonical serialization over eligible identifiers:
     $$\text{key}(u) \neq \text{key}(v) \iff u \neq v$$
  3. Fixed UTF-8 encoding.
  4. Fixed domain separation tag (e.g. `arpipe-oracle-double-v1`).
  5. Fixed threshold:
      Canonical form:
      $$\text{rank} = \text{uint256}(\text{SHA256}(\text{domain\_tag} \parallel \text{unit\_bytes}))$$
      selected iff:
      $$\text{rank} < \lfloor 0.25 \times 2^{256} \rfloor$$
      ASCII-safe equivalent:
      `rank = uint256(SHA256(domain_tag || unit_bytes))`
      selected iff `rank < floor(0.25 * 2^256)`.
   6. No duplicate canonical keys.
   7. No reuse of sampling `selection_rank`.
   8. No post-hoc key or threshold tuning after observing outcomes.
   9. Invariance: `same input -> same bytes -> same digest -> same selection`.
- **diagnostic_statistics:** (Evaluated for information only, NOT as pass/fail gates):
  - Overall selected fraction.
  - Distribution across strata.
  - Hex-prefix distribution.
- **recommended_option:** Adopt the injective formula:
  $$\text{canonical\_bytes} = \text{document\_id} \mathbin{\Vert} \text{0x00} \mathbin{\Vert} \text{page\_number\_decimal}$$
  with domain tag `arpipe-oracle-double-v1` and threshold $\lfloor 0.25 \times 2^{256} \rfloor$ (ASCII-safe: `rank < floor(0.25 * 2^256)`).
- **selected_option:** `null`
- **rationale:** Mathematical constraints are proven; author must approve domain key and eligible unit set.
- **dependencies:** Depends on B3 (eligibility pool); gates double annotation execution.
- **effective_protocol_version:** `null`
- **affected_artifacts:** `configs/t0_4/oracle_routing_spec.json`
- **supersedes:** Informal prefix descriptions.
- **future_validation:** Conformance test in `test_phase2_1_semantic_conformance.py` (X5).
- **owner:** Project Author
- **timestamp:** `PENDING`

---

### B5 — Oracle Scientific Construct & Evidence Channels

- **decision_id:** `DEC-B5`
- **question:** What evidence channels are permitted for route annotators, and what scientific construct do route labels represent?
- **verified_state:**
  - `oracle_routing_spec.json` states that adjudication evidence is "rendered page image plus the written route protocol"; primary annotator evidence is unstated.
  - Category mismatch: rendered pixels expose visual appearance. They DO NOT expose font character mapping, `ToUnicode` tables, invisible text layers, or PDF syntax (ISO 32000-1).
  - An annotator viewing only rendered pixels CANNOT reliably distinguish `NATIVE` (valid text layer) from `LEGACY` (corrupted text layer with correct visual rendering).
- **status:** `PENDING_AUTHOR_DECISION`
- **options:**
  - Option 1 (Semantic PDF Route Oracle): Retain labels `NATIVE`, `LEGACY`, `OCR`. Require a controlled multi-channel evidence bundle: rendered page image, raw extracted text layer, font/CMap diagnostic summary, and written protocol. Log all opened channels; keep OCR engine predictions hidden.
  - Option 2 (Visual Action Oracle): Keep image-only evidence, but re-define labels as observable visual actions: `VISIBLE_TEXT_RECOVERABLE_WITHOUT_OCR`, `OCR_REQUIRED_FOR_VISIBLE_CONTENT`, or `ABSTAIN`. Do not claim PDF encoding diagnosis.
- **recommended_option:** Option 1 if semantic routing evaluation is required; Option 2 if strict image-only blinding is required. Do not mix semantic labels with image-only evidence.
- **selected_option:** `null`
- **rationale:** Epistemological integrity: pixels cannot diagnose font encoding. Awaiting author choice of construct.
- **dependencies:** Gates Oracle Route schema, annotator guidelines, and Experiment X1.
- **effective_protocol_version:** `null`
- **affected_artifacts:** `configs/t0_4/oracle_routing_spec.json`, `configs/t0_4/gold_schema.json`
- **supersedes:** Historical visual-only assumptions for semantic labels.
- **future_validation:** Calibration review (X4).
- **owner:** Project Author
- **timestamp:** `PENDING`

---

### B6 — PageGold & DocumentGold Reliability Design

- **decision_id:** `DEC-B6`
- **question:** What double-annotation rate and sampling strategy govern PageGold and DocumentGold?
- **verified_state:**
  - A double-annotation rule exists only in `oracle_routing_spec.json` (25%).
  - `gold_schema.json` defines schemas for `page_gold` and `document_gold`, but includes no overlap rate, sampling rule, or stratification requirement.
  - The T0 annotation roster has only a single `annotator_id` column.
  - The 25% oracle rule does not automatically govern PageGold or DocumentGold.
- **status:** `PENDING_AUTHOR_DECISION`
- **options:**
  - Option 1 (Uniform Random Overlap): Fixed percentage (e.g. 15–20%) drawn uniformly from eligible units. Provides unbiased population agreement, but may miss rare difficult conditions.
  - Option 2 (Targeted Diagnostic Oversampling): Double-annotate all rare/complex conditions (scans, tables, multi-column, hybrid, pre-2015). Highly diagnostic, but cannot be pooled into a single population agreement metric without weighting.
  - Option 3 (Hybrid Random + Diagnostic): Uniform random sample for population reliability plus a separately reported diagnostic stratum for rare/complex failure modes.
- **recommended_option:** Option 3 (Hybrid design). Report pre-adjudication agreement decomposed into transcription, boundary, and presence metrics. Pre-adjudication raw annotations must be preserved immutably; adjudicated gold must never be used to compute inter-annotator agreement.
- **selected_option:** `null`
- **rationale:** Awaiting author decision on annotation budget, team size, and precision targets.
- **dependencies:** Gates annotation workload, budget, and final roster generation.
- **effective_protocol_version:** `null`
- **affected_artifacts:** `configs/t0_4/gold_schema.json`, `dataset/corpus_freeze/annotation_roster.csv`
- **supersedes:** None.
- **future_validation:** Segregated FIT calibration pilot (X4).
- **owner:** Project Author
- **timestamp:** `PENDING`

---

### B7 — Reading-Order Reference Unit & Representation

- **decision_id:** `DEC-B7`
- **question:** What semantic unit and relation structure represent reading-order ground truth?
- **verified_state:**
  - `gold_schema.json` defines `reading_order_pairs` as string pairs with no specified unit.
  - `metrics_spec.json` specifies reading-order unit as "page_or_document_as_declared".
  - Production code uses block-level coordinates from PyMuPDF, which are engine heuristics and unsuitable as reference gold.
- **status:** `PENDING_AUTHOR_DECISION`
- **options:**
  - Option 1 (Engine Block Pairs): Use parser/OCR block IDs. Fragile, violates input fairness, and couples gold to engine bugs.
  - Option 2 (Line-Level Sequence): Full text line permutation. Extremely high annotation burden, quadratic relation space ($O(N^2)$), alignment-heavy.
  - Option 3 (Annotator-Defined Visual Text Regions): Annotator defines atomic visual regions (paragraphs, headings, captions, table blocks) with stable IDs and directed `PRECEDES` relations.
- **recommended_option:** Option 3. Normalized page coordinates ($[0, 1000]$ or pt), engine-independent stable IDs, explicit directed pairwise relations (`(page_id, predecessor_id, successor_id, PRECEDES)`), with explicit tie, marginalia, and table policies.
- **selected_option:** `null`
- **rationale:** Awaiting author decision on region granularity and table exclusion policies.
- **dependencies:** Gates reading-order annotation schema, UI tooling, and Level B structure metrics.
- **effective_protocol_version:** `null`
- **affected_artifacts:** `configs/t0_4/gold_schema.json`, `configs/t0_4/metrics_spec.json`
- **supersedes:** Historical undefined string-pair definitions.
- **future_validation:** Reading-order calibration test (X4/X7).
- **owner:** Project Author
- **timestamp:** `PENDING`

---

### B8 — HOLDOUT Gold Annotation Governance

- **decision_id:** `DEC-B8`
- **question:** Under what conditions and timeline may documents in the T0 HOLDOUT partition be annotated or accessed?
- **verified_state:**
  - `benchmark_config.json` sets `holdout_policy: {allowed_before_final_freeze: false}`.
  - Permitted pre-freeze uses are restricted to: manifest predeclaration, schema validation, and split-integrity audit.
  - Prohibited uses include: tuning, thresholds, engine selection, sampling changes, error-driven methodology changes.
  - Annotation is neither explicitly listed under allowed uses nor forbidden uses; the `allowed_before_final_freeze: false` flag creates an unambiguous **default-deny** stance.
  - Historical pre-T0 exposure is `UNKNOWN` (P2-26); forward governance must enforce strict isolation.
- **status:** `PENDING_AUTHOR_DECISION`
- **options:**
  - Option 1 (Default Deny Before System Freeze): Zero HOLDOUT annotation or inspection permitted until the entire ARPipe pipeline, all algorithms, all thresholds, all schemas, and all FIT/VALIDATION evaluations are permanently frozen. HOLDOUT annotation occurs post-freeze under strict blinding for final reference evaluation only.
  - Option 2 (Pre-Freeze Blinded Annotation): Allow HOLDOUT annotation prior to freeze under blinded protocols. High risk of subtle methodological leakage or cognitive contamination.
  - Option 3 (Never Annotate HOLDOUT): Use HOLDOUT strictly for unsupervised distribution checks; evaluate zero ground truth on HOLDOUT. Eliminates final gold evaluation.
- **recommended_option:** Option 1 (Default Deny Before System Freeze). Maintain default-deny; permit HOLDOUT annotation only after a signed, immutable system freeze. Annotators must be blinded to engine predictions, and HOLDOUT results may support exactly one pre-registered evaluation run without post-hoc threshold adjustments.
- **selected_option:** `null`
- **rationale:** Scientific integrity: preserves HOLDOUT as an uncontaminated, final evaluation reference.
- **dependencies:** Gates all future HOLDOUT interaction and final thesis evaluation.
- **effective_protocol_version:** `null`
- **affected_artifacts:** `configs/t0_4/benchmark_config.json`, `sampling_spec.json`
- **supersedes:** Historical ambiguous holdout prose.
- **future_validation:** Metadata-only audit (X6); access log verification.
- **owner:** Project Author
- **timestamp:** `PENDING`
