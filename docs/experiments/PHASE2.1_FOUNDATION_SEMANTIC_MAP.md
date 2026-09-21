# Phase 2.1 — Foundation Semantic Map, Predicate Catalog & Ontology Crosswalk

**Status:** normative semantic contract  
**Repository Basis:** `D:\sem_iitk\sem9\thesis\sep_week1\arpipe-phase2.1-foundation-normalization`  
**Base Commit:** `03a63f5d7d79bac6a0bab0ffc33af42004e78935`  
**Contract Version:** `2.1.0`

---

## 1. Core Semantic Axiom & Governing Principles

Phase 2 established that semantic drift across artifacts was the primary root cause of contradictory claims, broken denominator calculations, and mislabeled units (RC2, RC3, RC4).

### The Primary Semantic Axiom:
```
LABEL != PREDICATE != DERIVED_VARIABLE != EVIDENCE_CLASS != ROUTE != SAMPLING_STRATUM != ANNOTATION_LABEL != EVALUATION_ENDPOINT
```

1. **A label is not a definition:** A string like `native_ok` or `legacy_font` in a CSV or JSON file denotes a stored token, not an objective physical property of a document.
2. **A candidate proxy is not verified truth:**
   ```
   deterministic rule output != human verified fact != semantic truth != routing action
   ```
   Flagging a page via a regex or heuristic does not establish that the page embodies that condition in reality.
3. **Sampling priority is not routing precedence:** Stratum assignment in a coverage sample (such as prioritizing rare pages for a benchmark) does not dictate the operational execution order of an extraction pipeline.
4. **Representation class is not a route:** A document or page classification does not automatically define which OCR or parser engine must be executed.
5. **Anti-Semantic-Laundering Principle:** No historical count, narrative claim, or proxy heuristic may be converted into a validated canonical fact merely by assigning it a new predicate identifier or schema name.

---

## 2. Canonical Predicate Catalog

The catalog defines every active, historical, and derived predicate across 22 mandatory dimensions, with explicit relationships preventing false partitioning.

### 2.1 Document-Level Representation Predicates

#### `NATIVE_DOC_ANY_PAGE_HISTORICAL`
- **predicate_id:** `PRED-DOC-01`
- **canonical_name:** `NATIVE_DOC_ANY_PAGE_HISTORICAL`
- **contract_version:** `2.1.0`
- **status:** `HISTORICAL_RECONSTRUCTION_REQUIRED`
- **relationship_to_other_predicates:** `OVERLAPPING` (with `NATIVE_DOC_WHOLE_V1` and `MIXED_DOC_V1`); `HISTORICAL_ALIAS` to T0.1 `CLAIM:C005`
- **unit:** `document`
- **exact_predicate:** `document contains at least one page satisfying PAGE_TEXT_NATIVE_T01` (historical narrative: "191 native digital documents")
- **denominator:** `194 executable documents` (reported count: `191`)
- **source_artifact:** `dataset/corpus_gap_audit/reconciled/gap_audit_report_reconciled.md` (Claim C005)
- **derivation_method:** T0.1 page profiler aggregation
- **evidence_class:** `DETERMINISTIC_DERIVATION`
- **human_verified:** `NO`
- **route_meaning:** `NONE` (not an operational route)
- **sampling_use:** `NONE`
- **annotation_use:** `FORBIDDEN` (cannot serve as an annotation stratum)
- **evaluation_use:** `HISTORICAL_COMPARISON_ONLY`
- **historical_aliases:** `"191 native digital documents"`, `"native text documents"`
- **allowed_contexts:** Historical narrative context and reconciliation discussions
- **deprecated_contexts:** Any assertion that 191 documents are whole-document digital or pure native
- **limitations:** 131 of these 191 documents also contain scanned or OCR-layer pages and are classified as `MIXED_DOC_V1`
- **supersedes:** None
- **effective_from:** `2.1.0`

#### `NATIVE_DOC_WHOLE_V1`
- **predicate_id:** `PRED-DOC-02`
- **canonical_name:** `NATIVE_DOC_WHOLE_V1`
- **contract_version:** `2.1.0`
- **status:** `ACTIVE`
- **relationship_to_other_predicates:** `MUTUALLY_EXCLUSIVE` with `MIXED_DOC_V1` and `SCANNED_DOC_V1`; `NESTED` within `NATIVE_DOC_ANY_PAGE_HISTORICAL`
- **unit:** `document`
- **exact_predicate:** `scanned_page_count == 0 and ocr_page_count == 0`
- **denominator:** `194 executable documents` (verified count: `60`)
- **source_artifact:** `tools/reconcile_t0_1.py:499-506`; `dataset/corpus_gap_audit/reconciled/`
- **derivation_method:** Deterministic rule over T0.1 page profile counts
- **evidence_class:** `DETERMINISTIC_DERIVATION`
- **human_verified:** `NO`
- **route_meaning:** `TEXT_EXTRACTION` (default expectation for native documents)
- **sampling_use:** Stratification dimension in T0.3A/R1
- **annotation_use:** Document-level representation stratum
- **evaluation_use:** Baseline native pipeline evaluation
- **historical_aliases:** `NATIVE` (in T0.1R/T0.3A), `"native digital"` (in 60-doc tables)
- **allowed_contexts:** Representation reporting, stratified evaluation
- **deprecated_contexts:** Conflation with T0's 151 `digital` documents or T0.1's 191 documents
- **limitations:** Only 21 of the 60 documents have 100% of pages classified as pure text; 39 contain non-text/vector/empty pages without scanned/OCR flags
- **supersedes:** Ambiguous historical "native" labels
- **effective_from:** `2.1.0`

#### `MIXED_DOC_V1`
- **predicate_id:** `PRED-DOC-03`
- **canonical_name:** `MIXED_DOC_V1`
- **contract_version:** `2.1.0`
- **status:** `ACTIVE`
- **relationship_to_other_predicates:** `MUTUALLY_EXCLUSIVE` with `NATIVE_DOC_WHOLE_V1` and `SCANNED_DOC_V1`
- **unit:** `document`
- **exact_predicate:** `scanned_page_count > 0 or ocr_page_count > 0` (and `scanned_page_count < total_pages`)
- **denominator:** `194 executable documents` (verified count: `132`)
- **source_artifact:** `dataset/corpus_gap_audit/reconciled/`
- **derivation_method:** Deterministic rule over T0.1 page profile counts
- **evidence_class:** `DETERMINISTIC_DERIVATION`
- **human_verified:** `NO`
- **route_meaning:** `HYBRID_ROUTING_REQUIRED`
- **sampling_use:** Stratification dimension in T0.3A/R1 and T0.4 Track B
- **annotation_use:** Document-level representation stratum
- **evaluation_use:** Track-B document localization evaluation
- **historical_aliases:** `MIXED` (in T0.1R/T0.3A), `mixed_representation`
- **allowed_contexts:** Representation reporting, multi-page routing analysis
- **deprecated_contexts:** Conflation with T0's 38 `mixed` documents
- **limitations:** 71 of the 132 documents are classified MIXED solely due to the heuristic `ocr_layer_proxy`; 34 due to scanned pages only; 27 due to both
- **supersedes:** Historical 101-document and 38-document mixed definitions
- **effective_from:** `2.1.0`

#### `SCANNED_DOC_V1`
- **predicate_id:** `PRED-DOC-04`
- **canonical_name:** `SCANNED_DOC_V1`
- **contract_version:** `2.1.0`
- **status:** `ACTIVE`
- **relationship_to_other_predicates:** `MUTUALLY_EXCLUSIVE` with `NATIVE_DOC_WHOLE_V1` and `MIXED_DOC_V1`
- **unit:** `document`
- **exact_predicate:** `scanned_page_count == total_pages`
- **denominator:** `194 executable documents` (verified count: `2`: `INE002L01015_2012` [43 pgs], `INE003B01014_2011` [48 pgs]; 91 total pages)
- **source_artifact:** `dataset/corpus_gap_audit/reconciled/`
- **derivation_method:** Deterministic rule over T0.1 page profile counts
- **evidence_class:** `DETERMINISTIC_DERIVATION`
- **human_verified:** `NO`
- **route_meaning:** `WHOLE_DOCUMENT_OCR`
- **sampling_use:** Stratification dimension in T0.3A/R1
- **annotation_use:** Track-B full-scan stratum
- **evaluation_use:** Extreme recovery evaluation
- **historical_aliases:** `SCANNED` (in T0.1R/T0.3A), `fully_scanned_document`
- **allowed_contexts:** Representation reporting, robustness-gate audits
- **deprecated_contexts:** Conflation with T0's 5 `scanned` documents
- **limitations:** Population size is small ($N=2$, both in HOLDOUT/VALIDATION splits)
- **supersedes:** Historical 5-document scanned label
- **effective_from:** `2.1.0`

---

### 2.2 Page-Level Text & Representation Predicates

#### `PAGE_TEXT_DIGITAL`
- **predicate_id:** `PRED-PAGE-01`
- **canonical_name:** `PAGE_TEXT_DIGITAL`
- **contract_version:** `2.1.0`
- **status:** `ACTIVE`
- **relationship_to_other_predicates:** `MUTUALLY_EXCLUSIVE` with `SCANNED_PAGE_DETECTOR`, `BROKEN_TEXT_PAGE`, `VECTOR_TEXT_PAGE`, `HYBRID_PAGE`, `BLANK_PAGE` in `arpipe/triage.py`; `OVERLAPPING` with `PAGE_TEXT_NATIVE_T01`
- **unit:** `page`
- **exact_predicate:** `n_chars >= 120 and mojibake_ratio <= 0.02 and image_area_frac < 0.25` (or `15 <= n_chars < 120 and image < 0.25 and drawings < 400`)
- **denominator:** `37,917 profiled physical pages` (verified count: `35,580`)
- **source_artifact:** `arpipe/triage.py:_classify` (`PageKind.DIGITAL`)
- **derivation_method:** Single-page text/image/vector heuristic classifier
- **evidence_class:** `DETERMINISTIC_DERIVATION`
- **human_verified:** `NO`
- **route_meaning:** `TEXT_EXTRACTION` (routes to `textlayer.extract_pages`)
- **sampling_use:** T0.4 `representation_class` `native_ok`
- **annotation_use:** Track-A native candidate pool
- **evaluation_use:** OCR-avoidance baseline
- **historical_aliases:** `digital`, `representation_class: native_ok`
- **allowed_contexts:** Production routing, Track-A representation classification
- **deprecated_contexts:** Conflation with T0.1 `condition_labels: native_ok`
- **limitations:** Does not guarantee that font encodings map to valid Unicode (see B5)
- **supersedes:** Historical un-scoped "native" page labels
- **effective_from:** `2.1.0`

#### `PAGE_TEXT_NATIVE_T01`
- **predicate_id:** `PRED-PAGE-02`
- **canonical_name:** `PAGE_TEXT_NATIVE_T01`
- **contract_version:** `2.1.0`
- **status:** `ACTIVE`
- **relationship_to_other_predicates:** `OVERLAPPING` with `PAGE_TEXT_DIGITAL`, `HYBRID_PAGE`, `BROKEN_TEXT_PAGE`, `VECTOR_TEXT_PAGE`
- **unit:** `page`
- **exact_predicate:** `n_chars > 50 and not (n_chars <= 20 and image_area >= 0.85)`
- **denominator:** `37,917 profiled physical pages` (verified count: `36,988`)
- **source_artifact:** `dataset/corpus_gap_audit/condition_page_map.csv`
- **derivation_method:** T0.1 gap audit classifier
- **evidence_class:** `CANDIDATE_PROXY`
- **human_verified:** `NO`
- **route_meaning:** `NONE` (analytical condition label only)
- **sampling_use:** Generates T0.4 `condition_labels: native_ok` (157 units carry this label together with OCR-routed classes)
- **annotation_use:** Analytical label only
- **evaluation_use:** Coverage audit
- **historical_aliases:** `native_page`, `condition_labels: native_ok`
- **allowed_contexts:** T0.1 historical coverage matrices
- **deprecated_contexts:** Direct routing input (routes must use `representation_class`)
- **limitations:** Includes 803 broken_text pages, 483 hybrid pages, 194 scanned pages, 11 vector_text pages
- **supersedes:** None
- **effective_from:** `2.1.0`

#### `SCANNED_PAGE_DETECTOR` (Predicate A)
- **predicate_id:** `PRED-PAGE-03`
- **canonical_name:** `SCANNED_PAGE_DETECTOR`
- **contract_version:** `2.1.0`
- **status:** `ACTIVE`
- **relationship_to_other_predicates:** `MUTUALLY_EXCLUSIVE` with `PAGE_TEXT_DIGITAL`; `SUPERSET` of `SCANNED_PAGE_T01`
- **unit:** `page`
- **exact_predicate:** `n_chars < 120 and (image_area >= 0.55 or (image_area >= 0.25 and drawings < 400))`
- **denominator:** `37,917 profiled physical pages` (verified count: `804`)
- **source_artifact:** `arpipe/triage.py:_classify` (`PageKind.SCANNED`)
- **derivation_method:** Single-page detector heuristic
- **evidence_class:** `DETERMINISTIC_DERIVATION`
- **human_verified:** `NO`
- **route_meaning:** `OCR` (routes to `_ocr_pages`)
- **sampling_use:** T0.4 `sampling_stratum: scanned` and `representation_class: scanned` (72 units)
- **annotation_use:** Track-A scanned stratum
- **evaluation_use:** Primary OCR evaluation benchmark
- **historical_aliases:** `scanned` (detector), `PageKind.SCANNED`
- **allowed_contexts:** T0.4 sampling and routing
- **deprecated_contexts:** Conflation with T0.1 `scanned_page`
- **limitations:** May capture photo-heavy or diagram pages with sparse captions
- **supersedes:** Unqualified "scanned page" references in T0.4
- **effective_from:** `2.1.0`

#### `SCANNED_PAGE_T01` (Predicate B)
- **predicate_id:** `PRED-PAGE-04`
- **canonical_name:** `SCANNED_PAGE_T01`
- **contract_version:** `2.1.0`
- **status:** `ACTIVE`
- **relationship_to_other_predicates:** `NESTED` within `SCANNED_PAGE_DETECTOR` (strict subset: 284 inside 804)
- **unit:** `page`
- **exact_predicate:** `n_chars <= 20 and image_area >= 0.85`
- **denominator:** `37,917 profiled physical pages` (verified count: `284`)
- **source_artifact:** `dataset/corpus_gap_audit/`
- **derivation_method:** T0.1 strict image dominance rule
- **evidence_class:** `CANDIDATE_PROXY`
- **human_verified:** `NO`
- **route_meaning:** `NONE` (analytical audit predicate)
- **sampling_use:** Governs T0.3A document classification (`mixed_scanned_pages`)
- **annotation_use:** Strict image-only page candidate pool
- **evaluation_use:** Document scan-coverage audits
- **historical_aliases:** `scanned_page` (T0.1)
- **allowed_contexts:** T0.1, T0.1R, T0.3A document representation logic
- **deprecated_contexts:** Benchmark stratum sizing in T0.4
- **limitations:** Extremely strict; misses partial-page scans
- **supersedes:** None
- **effective_from:** `2.1.0`

#### `BROKEN_TEXT_PAGE`
- **predicate_id:** `PRED-PAGE-05`
- **canonical_name:** `BROKEN_TEXT_PAGE`
- **contract_version:** `2.1.0`
- **status:** `ACTIVE`
- **relationship_to_other_predicates:** `IDENTICAL` in population to T0.4 `legacy_font_candidate` (803 pages across 24 documents); `MUTUALLY_EXCLUSIVE` with `PAGE_TEXT_DIGITAL`
- **unit:** `page`
- **exact_predicate:** `n_chars >= 120 and mojibake_ratio > 0.02`
- **denominator:** `37,917 profiled physical pages` (verified count: `803`)
- **source_artifact:** `arpipe/triage.py:_classify` (`PageKind.BROKEN_TEXT`)
- **derivation_method:** Mojibake ratio thresholding
- **evidence_class:** `DETERMINISTIC_DERIVATION`
- **human_verified:** `NO`
- **route_meaning:** `OCR` (in production code: member of `NEEDS_OCR`)
- **sampling_use:** T0.4 `representation_class: broken_text` (20 units in manifest); empty sampling stratum due to priority preemption by `legacy_font_candidate`
- **annotation_use:** Track-A candidate pool
- **evaluation_use:** OCR text-recovery benchmark
- **historical_aliases:** `broken_text`, `PageKind.BROKEN_TEXT`, `cid_or_broken_text_indicator`
- **allowed_contexts:** Production triage, representation classification
- **deprecated_contexts:** Asserting that broken text is proven legacy Indian font encoding
- **limitations:** Captures encoding corruption, bad CMap, and CID mojibake indiscriminately
- **supersedes:** Historical conflation of broken text with verified legacy fonts
- **effective_from:** `2.1.0`

#### `VECTOR_TEXT_PAGE`
- **predicate_id:** `PRED-PAGE-06`
- **canonical_name:** `VECTOR_TEXT_PAGE`
- **contract_version:** `2.1.0`
- **status:** `ACTIVE`
- **relationship_to_other_predicates:** `MUTUALLY_EXCLUSIVE` with `PAGE_TEXT_DIGITAL` and `SCANNED_PAGE_DETECTOR`
- **unit:** `page`
- **exact_predicate:** `n_chars < 120 and image_area < 0.55 and drawing_paths >= 400`
- **denominator:** `37,917 profiled physical pages` (verified count: `32` pages across 17 cells, 9 singletons)
- **source_artifact:** `arpipe/triage.py:_classify` (`PageKind.VECTOR_TEXT`); T0.4 closure section 1
- **derivation_method:** Drawing path count thresholding
- **evidence_class:** `DETERMINISTIC_DERIVATION`
- **human_verified:** `NO`
- **route_meaning:** `OCR` (confirmed in code and T0.4 closure: member of `NEEDS_OCR`)
- **sampling_use:** T0.4 `sampling_stratum: vector_text` (17 units)
- **annotation_use:** Track-A vector recovery candidate pool
- **evaluation_use:** Vector-glyph OCR benchmark
- **historical_aliases:** `vector_text`, `PageKind.VECTOR_TEXT`
- **allowed_contexts:** Production triage, benchmark sampling
- **deprecated_contexts:** None
- **limitations:** Highly sparse ($N=32$ pages across entire 194-document corpus)
- **supersedes:** None
- **effective_from:** `2.1.0`

#### `HYBRID_PAGE`
- **predicate_id:** `PRED-PAGE-07`
- **canonical_name:** `HYBRID_PAGE`
- **contract_version:** `2.1.0`
- **status:** `ACTIVE`
- **relationship_to_other_predicates:** `MUTUALLY_EXCLUSIVE` with `PAGE_TEXT_DIGITAL` in triage; `OVERLAPPING` with `PAGE_TEXT_NATIVE_T01` (483 pages)
- **unit:** `page`
- **exact_predicate:** `n_chars >= 120 and n_chars < 600 and image_area >= 0.25`
- **denominator:** `37,917 profiled physical pages` (verified count: `483`)
- **source_artifact:** `arpipe/triage.py:_classify` (`PageKind.HYBRID`)
- **derivation_method:** Single-page char-density and image thresholding
- **evidence_class:** `DETERMINISTIC_DERIVATION`
- **semantic_status:** `RULE_DERIVED_REPRESENTATION`
- **human_verified:** `NO`
- **route_meaning:** `WHOLE_PAGE_OCR` (in production code: member of `NEEDS_OCR`, passes whole page to `_ocr_pages`)
- **sampling_use:** T0.4 representation class `hybrid` (102 units in manifest; absent from T0.4 ROUTING classes; 22 units sit inside stratum `native_clean_control`)
- **annotation_use:** Track-A hybrid recovery pool
- **evaluation_use:** Diagnostic hybrid pilot (X2)
- **historical_aliases:** `hybrid`, `PageKind.HYBRID`
- **allowed_contexts:** Triage classification, representation stratification
- **deprecated_contexts:** Claiming that production code implements "read text, OCR image" (code executes whole-page OCR)
- **limitations:** Prose documentation in `CLAUDE.md` contradicted implementation; normalized here
- **supersedes:** Narrative descriptions of hybrid extraction
- **effective_from:** `2.1.0`

#### `BLANK_PAGE`
- **predicate_id:** `PRED-PAGE-08`
- **canonical_name:** `BLANK_PAGE`
- **contract_version:** `2.1.0`
- **status:** `ACTIVE`
- **relationship_to_other_predicates:** `MUTUALLY_EXCLUSIVE` with all other page kinds in triage
- **unit:** `page`
- **exact_predicate:** `n_chars < 15 and image_area < 0.05 and drawing_paths < 20`
- **denominator:** `37,917 profiled physical pages` (verified count: `215`)
- **source_artifact:** `arpipe/triage.py:_classify` (`PageKind.BLANK`)
- **derivation_method:** Multi-signal sparsity check
- **evidence_class:** `DETERMINISTIC_DERIVATION`
- **semantic_status:** `RULE_DERIVED_REPRESENTATION`
- **human_verified:** `NO`
- **route_meaning:** `EXCLUDED_FROM_PIPELINE` (dropped implicitly from extraction and scoring)
- **sampling_use:** T0.4 representation class `blank` (55 units in manifest; absent from ROUTING classes)
- **annotation_use:** Candidate exclusion pool
- **evaluation_use:** Pipeline sparsity audit
- **historical_aliases:** `blank`, `PageKind.BLANK`
- **allowed_contexts:** Triage classification, document length calculation
- **deprecated_contexts:** Listing as an extraction target
- **limitations:** None
- **supersedes:** Historical omission from `CLAUDE.md` "five page classes"
- **effective_from:** `2.1.0`

---

### 2.3 Structural & Layout Candidate Proxies (Workstream E)

All candidate proxies adhere strictly to the rule:
```
deterministic rule output != human verified fact != semantic truth != routing action
```

| Predicate ID | Canonical Name | Status | Unit | Exact Predicate Expression | Denominator & Value | Evidence Class | Semantic Status | Human Verified? | Limitations & Downstream Guard |
|---|---|---|---|---|---|---|---|:---:|---|
| **PRED-PRX-01** | `OCR_LAYER_CANDIDATE_PROXY` | ACTIVE | page | `kind == 'scanned' and n_chars > 50` | 37,917 pages; **189 pages** across 98 documents | `CANDIDATE_PROXY` | `RULE_DERIVED_REPRESENTATION` | **NO** | Replaces all historical claims alleging detection of "PDF render mode 3 (invisible text layer)" or OCR producer signatures. No code inspects PDF render modes. |
| **PRED-PRX-02** | `TOC_CANDIDATE_PROXY` | ACTIVE | document / page | Page has keyword in `("contents", "index", "table of contents")` and `physical_page < 50` | 194 documents; **174 documents (89.7%)** flagged | `CANDIDATE_PROXY` | `RULE_DERIVED_REPRESENTATION` | **NO** | Register stated "first 30 pages"; implementation uses `< 50`. Keyword includes substring `index`. Near-saturated; useful as weak navigation prior only, NEVER as Gold authority. |
| **PRED-PRX-03** | `ANNEXURE_CANDIDATE_PROXY` | ACTIVE | document | Document contains `"annexure"` in full text of any page | 194 documents; **188 documents (96.9%)** flagged | `CANDIDATE_PROXY` | `RULE_DERIVED_REPRESENTATION` | **NO** | Register stated keyword match in outline or heading; implementation matches full page text. Near-saturated; candidate signal only. |
| **PRED-PRX-04** | `TABLE_CANDIDATE_PROXY` | ACTIVE | page | `has_vector_grid or numeric_lines_count >= 3` | 37,917 pages; **29,476 pages (77.7%)** flagged across 190 documents | `CANDIDATE_PROXY` | `RULE_DERIVED_REPRESENTATION` | **NO** | Captures all structured numeric layout; highly saturated. Largest T0.4 stratum (138 units) is a proxy stratum. |
| **PRED-PRX-05** | `MULTI_COLUMN_ESTIMATOR_T01` | ACTIVE | page | T0.1 column estimator: `n_columns >= 3` | 37,917 pages; **17,190 pages** across 191 documents | `CANDIDATE_PROXY` | `RULE_DERIVED_REPRESENTATION` | **NO** | Disagrees with detector `n_columns >= 2` (18,855 pages) and detector `n_columns == 2` (9,521 pages). Counts cannot be interchanged. |
| **PRED-PRX-06** | `LEGACY_FONT_CANDIDATE_T03A` | ACTIVE | page / document | `kind == broken_text or has_U_FFFD or pua_char_count > 5` | 194 documents; **56 documents (1,007 pages)** flagged | `CANDIDATE_PROXY` | `RULE_DERIVED_REPRESENTATION` | **NO** | Strict superset of detector `broken_text` (24 documents, 803 pages). Config parameter `broken_font_min_pua_or_mojibake_ratio` is never read in code. |
| **PRED-PRX-07** | `DUPLICATE_TEXT_CANDIDATE_PROXY`| ACTIVE | page | Bounding-box IoU >= 0.70 with identical text or IoU >= 0.40 with min 30 chars | 37,917 pages; **68 pages** across 35 documents | `CANDIDATE_PROXY` | `RULE_DERIVED_REPRESENTATION` | **NO** | Candidate extraction artifact; does not establish semantic defect without inspection. |
| **PRED-PRX-08** | `HIDDEN_TEXT_CANDIDATE_PROXY` | ACTIVE | page | Font size < 0.5 pt (`hidden_text_max_font_size`) | 37,917 pages; **4 pages** across 3 documents | `CANDIDATE_PROXY` | `RULE_DERIVED_REPRESENTATION` | **NO** | Sparse candidate indicator. |

---

## 3. Denominators, Reporting & Structural Zero Cells (Workstream D & P2-10, P2-18)

### 3.1 Resolving the Page-Count Denominator (P2-10)
In historical coverage matrices (T0.3A / T0.3A-R1), the column labeled `page_count` reported the **total page count of member documents**, not the pages exhibiting the condition. 
To eliminate 126x reporting distortions:
1. **`pages_in_member_documents`:** Total pages across documents that have at least one page meeting the condition (e.g. 23,877 pages in documents with an OCR-layer candidate).
2. **`pages_exhibiting_condition`:** Exact physical count of pages satisfying the predicate (e.g. 189 OCR-layer candidate pages; 1,007 legacy candidate pages; 17,190 multi-column pages).
3. **Mandatory Reporting Rule:** Every downstream metric, table, and analysis MUST explicitly declare whether its denominator is `all_corpus_documents (194)`, `pages_in_member_documents`, or `pages_exhibiting_condition`.

### 3.2 Normative Classification Procedure for the 16,157 Zero Cells (P2-18)
The T0.4 sampling Cartesian product declared:
```
36 issuers x 11 sampling strata x 2 eras x 3 length categories x 7 representation classes = 16,632 declared cells
```
The closure reported 475 observed cells and 16,157 zero-availability cells. These 16,157 zero-availability cells are NOT empirical coverage gaps. Rather than hard-coding counts from prior documentation, Phase 2.1 establishes an explicit, deterministic 4-way classification procedure over the declared cell space:

1. **`structurally_impossible`:** Cells where the Cartesian pairing of `(sampling_stratum, representation_class)` represents mutually incompatible logical conditions that contain zero pages by mathematical construction (e.g. `sampling_stratum == scanned` with `representation_class == digital`).
2. **`priority_preempted`:** Cells where physical pages exhibiting the condition are pre-empted by a higher-priority stratum during primary stratum assignment (e.g. `broken_text` pre-empted by `legacy_font_candidate`; `ocr_layer_proxy` pre-empted by `scanned`).
3. **`unobserved`:** Cells representing logically compatible conditions that simply did not occur empirically in the frozen 194-document corpus (e.g. Devanagari x OCR layer).
4. **`unclassified`:** Any cell that fails to resolve under rules 1–3.

**Normative Invariant & Terminal Condition:**
```
total_zero_cells = structurally_impossible + priority_preempted + unobserved = 16,157
unclassified = 0
```
No zero-cell count is authoritative merely because it appeared in prior documentation; any quoted breakdown must be verified under this explicit classification procedure.

---

## 4. Evidence Ontology Crosswalk (Workstream B & P2-12)

Standardizes the five historical vocabularies (T0, T0.1, T0.3A, T0.4, and production code) into seven normative evidence classes:

| Normative Evidence Class | Definition & Verification Requirement | Permitted Inferences | Forbidden Inferences | Historical Terms Mapped |
|---|---|---|---|---|
| **`SOURCE_METADATA`** | Metadata received directly from regulatory or exchange filing platforms (NSE/BSE). | Issuer identity, filing date, stated fiscal year. | Stated file size, correct content, internal layout. | `KNOWN_FROM_PRIOR`, `EXISTING_CORPUS_FIELD` |
| **`BYTE_VERIFIED`** | Direct cryptographic digest computed over stored file or Git blob. | File identity, exact byte immutability. | Semantic validity of internal text or layout. | `sha256_verified`, `VERIFIED_FACT` |
| **`DETERMINISTIC_DERIVATION`**| Rule-based or algorithmic output computed deterministically from verified bytes. | Consistent code behavior, reproducible metric values. | Human perceptual ground truth or semantic intent. | `DETERMINISTIC_DERIVED`, `DERIVED_INTERACTION` |
| **`CANDIDATE_PROXY`** | Heuristic or threshold-based detector flag indicating potential condition presence. | Screening, candidate queue generation, weak prior. | Prevalence, ground truth, verified defect, Gold label. | `CANDIDATE_PROXY`, `NOT_REVIEWED` |
| **`HUMAN_ANNOTATION`** | Single-annotator manual label generated under a written protocol. | Raw inter-annotator agreement input. | Final objective ground truth, consensus without adjudication. | `NOT_YET_ANNOTATED`, `annotation_roster` |
| **`ADJUDICATED_GOLD`** | Reference label finalized through formal independent double annotation and adjudication. | System evaluation endpoint, benchmark scoring. | Error-free metaphysical ground truth on ambiguous boundaries. | `PageGold`, `DocumentGold`, `OracleRouteGold` |
| **`UNKNOWN`** | Unobserved, unpersisted, or unverified historical state. | Preserving historical boundary and epistemic humility. | Assuming absence or manufacturing convenient historical facts. | `UNKNOWN`, `UNMEASURED`, `NOT_AVAILABLE` |

---

## 5. Historical Alias Translation Map (Workstream C)

Prevents superseded, ambiguous historical shorthand terms from silently regaining authority:

| Historical Alias | Canonical Predicate ID | Canonical Name | Unit | Allowed Context | Deprecated / Forbidden Context |
|---|---|---|---|---|---|
| `"191 native digital documents"` | `PRED-DOC-01` | `NATIVE_DOC_ANY_PAGE_HISTORICAL` | document | Historical narrative analysis only | Asserting that 191 documents are whole-document native |
| `NATIVE` (T0.1R / T0.3A) | `PRED-DOC-02` | `NATIVE_DOC_WHOLE_V1` | document | Document-level representation tables | Conflation with T0's 151 digital docs |
| `native_ok` (condition label) | `PRED-PAGE-02` | `PAGE_TEXT_NATIVE_T01` | page | T0.1 coverage tables | Production routing input |
| `native_ok` (representation class) | `PRED-PAGE-01` | `PAGE_TEXT_DIGITAL` | page | Track-A sampling and routing | Conflation with T0.1 native_ok label |
| `scanned` (T0.1) | `PRED-PAGE-04` | `SCANNED_PAGE_T01` | page | T0.1 gap audit tables | Sizing T0.4 benchmark strata |
| `scanned` (detector / T0.4) | `PRED-PAGE-03` | `SCANNED_PAGE_DETECTOR` | page | Production triage and T0.4 sampling | Conflation with T0.1 scanned_page |
| `legacy_font` (T0.4 route class) | `PRED-PAGE-05` | `BROKEN_TEXT_PAGE` | page | Historical representation class | Asserting a separate implemented REMAP route |
| `render mode 3` (proxy prose) | `PRED-PRX-01` | `OCR_LAYER_CANDIDATE_PROXY` | page | Historical prose analysis | Claiming direct PDF invisible text detection |
| `VALIDATED_METADATA` | `PRED-MET-01` | `SOURCE_METADATA_ERA_SPLIT` | document | Pinned era/split metadata | Imputing human review to unreviewed metadata |
