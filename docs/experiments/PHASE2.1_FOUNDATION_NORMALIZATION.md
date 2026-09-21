# Phase 2.1 — Foundation Normalization, Provenance Correction & Decision Closure Preparation

**Status:** authoritative normalization closeout report  
**Repository Basis:** `D:\sem_iitk\sem9\thesis\sep_week1\arpipe-phase2.1-foundation-normalization`  
**Base Commit:** `03a63f5d7d79bac6a0bab0ffc33af42004e78935` (`docs(research): integrate Phase 2 findings and external evidence`)  
**Parent Lineage:** `b937b58` (T0.4) → `33ba76a` (T0.4-CLOSE audited) → `63e3c04` (T0.4-CLOSE final) → `13423c4` (Phase 2 audit) → `03a63f5` (Phase 2 research integration)  
**Effective Protocol Version:** `2.1.0`

---

## PART A — Phase-2 Starting State

Phase 2 completed the forensic integrity audit (28 findings, P2-01 to P2-28, across root causes RC1 to RC6) and research integration without mutating the frozen corpus, executing OCR, or running benchmarks.

All six required Phase-2 research artifacts are verified present and authoritative at base commit `03a63f5`:
1. `docs/experiments/PHASE2_RESEARCH_INTEGRATION.md` (Integrates findings, prior art, decisions, and boundaries)
2. `docs/experiments/PHASE2_RESEARCH_PROBLEM_REGISTER.md` (Preserves verbatim observed wording for all 28 findings)
3. `docs/experiments/PHASE2_RESEARCH_ROOT_CAUSE_MAP.md` (Maps findings uniquely to RC1–RC6 with falsifiers)
4. `docs/experiments/PHASE2_RESEARCH_EVIDENCE_MATRIX.md` (Integrates project lineage with external literature E01–E13, P01–P13)
5. `docs/experiments/PHASE2_RESEARCH_B1_B8.md` (Verifies facts, constraints, and recommendations for B1–B8)
6. `docs/experiments/PHASE2_RESEARCH_EXPERIMENTS.md` (Specifies future diagnostic experiments X0–X7; none executed)

The starting worktree is clean, isolated, and verified bitwise against Git tree objects.

---

## PART B — Objective Provenance Corrections

In accordance with Phase 2.1 safety rules, historical reports and Git commits remain immutable. All corrections are formally established in [`PHASE2.1_PROVENANCE_CORRECTIONS.md`](PHASE2.1_PROVENANCE_CORRECTIONS.md):

1. **PC-01 (P2-01):** Corrected task text typo in T0.1R commit SHA to `879762a2f236b3aaa6df33b7ddacc60c01d633c1`.
2. **PC-02 (P2-02):** Documented that T0.4 Markdown protocol files are identified by Git blobs at closure `63e3c04` (amended at `33ba76a`), while `config_hashes.json` hashes the 12 JSON configs.
3. **PC-03 (P2-14):** Established that `file_size_bytes` in the T0 inventory is unverified fetch metadata; file identity is governed exclusively by cryptographic SHA-256 (194/194 match).
4. **PC-04 (P2-15):** Clarified missing-byte record semantics: 8 records are `UNASSIGNED_HISTORICAL`, 6 are administrative `INPUT_UNAVAILABLE`; all 14 remain excluded from executable partitions (194 executable docs invariant).
5. **PC-05 (P2-20):** Resolved `configs/audit_config.sha256` delta: recorded hash matches blob plus one trailing newline (`\n`); pinned CRLF copy in `dataset/` matches its hash file.
6. **PC-06 (P2-21):** Corrected the 10 erroneous hash strings in `PHASE1_FROZEN_FOUNDATION_VERIFICATION.md` by publishing authoritative blob digests from `PHASE2_FOUNDATION_INTEGRITY_FINDINGS.json`.
7. **PC-07 (P2-22):** Formally decoupled T0.4 closure observations (2 items) from post-closure T0.4-GOLD research items (B1–B8).
8. **PC-08 (P2-23):** Classified snapshot branches `t0.4-gold` (`d9f974b`) and `t0.4-routing-clarification` (`916407d`) as local non-methodology commits (`T0.4_LF_BLOCKED`).
9. **PC-09 (P2-24):** Formally documented storage prerequisites: benchmark sampling is 100% Git-reproducible; raw PDF re-extraction requires local `live_store` (194 PDFs).
10. **PC-10 (P2-25):** Bounded pre-registration claims: T0.3A co-committed taxonomy and results; R1 pre-specification is verifiable for engine execution only.

---

## PART C — Canonical Semantic Contract

The semantic contract published in [`PHASE2.1_FOUNDATION_SEMANTIC_MAP.md`](PHASE2.1_FOUNDATION_SEMANTIC_MAP.md) establishes normative definitions across all representation, routing, and sampling layers.

### 1. The Semantic Axiom
```
LABEL != PREDICATE != DERIVED_VARIABLE != EVIDENCE_CLASS != ROUTE != SAMPLING_STRATUM != ANNOTATION_LABEL != EVALUATION_ENDPOINT
```

### 2. Document-Level Representation
- **`NATIVE_DOC_ANY_PAGE_HISTORICAL` (`PRED-DOC-01`):** Status `HISTORICAL_RECONSTRUCTION_REQUIRED`. Refers to historical claim of 191 documents containing at least one native page. Must not be cited as whole-document digital.
- **`NATIVE_DOC_WHOLE_V1` (`PRED-DOC-02`):** Status `ACTIVE`. 60 documents with zero scanned and zero OCR-layer pages (`scanned_page_count == 0 and ocr_page_count == 0`). Only 21 have 100% of pages as pure digital text.
- **`MIXED_DOC_V1` (`PRED-DOC-03`):** Status `ACTIVE`. 132 documents with at least one scanned or OCR-layer page.
- **`SCANNED_DOC_V1` (`PRED-DOC-04`):** Status `ACTIVE`. Exactly 2 fully scanned documents (91 pages).

### 3. Page-Level Text & Triage Classes
- **`PAGE_TEXT_DIGITAL` (`PRED-PAGE-01`):** 35,580 pages meeting detector digital threshold. Routes to `textlayer.extract_pages`.
- **`PAGE_TEXT_NATIVE_T01` (`PRED-PAGE-02`):** 36,988 pages meeting T0.1 condition. Analytical label only; cannot be used as routing input.
- **`SCANNED_PAGE_DETECTOR` (`PRED-PAGE-03`):** 804 pages. Routes to OCR.
- **`SCANNED_PAGE_T01` (`PRED-PAGE-04`):** 284 pages. Strict subset of detector scanned.
- **`BROKEN_TEXT_PAGE` (`PRED-PAGE-05`):** 803 pages across 24 documents. Routes to OCR in production code.
- **`VECTOR_TEXT_PAGE` (`PRED-PAGE-06`):** 32 pages across 17 cells (9 singletons). Confirmed route: OCR.
- **`HYBRID_PAGE` (`PRED-PAGE-07`):** 483 pages. Value = 483; Evidence Class = `DETERMINISTIC_DERIVATION`; Semantic Status = `RULE_DERIVED_REPRESENTATION`; Human Verified = `NO`. Production code executes whole-page OCR.
- **`BLANK_PAGE` (`PRED-PAGE-08`):** 215 pages. Value = 215; Evidence Class = `DETERMINISTIC_DERIVATION`; Semantic Status = `RULE_DERIVED_REPRESENTATION`; Human Verified = `NO`. Dropped implicitly from extraction.

### 4. Strict Proxy Separation
Every proxy flag satisfies:
```
deterministic rule output != human verified fact != semantic truth != routing action
```
- `OCR_LAYER_CANDIDATE_PROXY` (`PRED-PRX-01`): 189 pages. Defined strictly by `kind == 'scanned' and n_chars > 50`. Removes all invisible-text render mode claims.
- `TOC_CANDIDATE_PROXY` (`PRED-PRX-02`): 174 documents (89.7%). Evaluated on physical pages `< 50`. Saturated; weak navigation prior only.
- `ANNEXURE_CANDIDATE_PROXY` (`PRED-PRX-03`): 188 documents (96.9%). Full-text keyword match. Saturated.
- `TABLE_CANDIDATE_PROXY` (`PRED-PRX-04`): 29,476 pages (77.7%). Saturated structural layout proxy.

### 5. Denominators & Structural Zero Cells
- **Unit Denominators (P2-10):** All reporting must distinguish `pages_in_member_documents` (e.g. 23,877 pages in documents with an OCR-layer candidate) from `pages_exhibiting_condition` (189 OCR candidate pages).
- **Normative Zero-Cell Classification (P2-18):**
  The 16,157 zero-availability cells are partitioned via an explicit 4-way procedure:
  1. `structurally_impossible`: Incompatible Cartesian pairings of stratum and representation class.
  2. `priority_preempted`: Lower-priority condition pages pre-empted by higher-priority strata.
  3. `unobserved`: Logically compatible combinations that did not empirically occur.
  4. `unclassified`: Must equal 0 (`unclassified = 0`).

---

## PART D — Predicate & Evidence Ontology Crosswalk

Five historical evidence vocabularies are mapped into seven normative classes:
1. `SOURCE_METADATA`: Exchange/regulatory filing metadata (NSE/BSE).
2. `BYTE_VERIFIED`: Cryptographically authenticated file or blob digests.
3. `DETERMINISTIC_DERIVATION`: Code-derived algorithmic metrics and classifications.
4. `CANDIDATE_PROXY`: Heuristic, unreviewed detector flags.
5. `HUMAN_ANNOTATION`: Raw single-annotator judgments under written guidelines.
6. `ADJUDICATED_GOLD`: Reconciled multi-annotator reference truth for evaluation.
7. `UNKNOWN`: Unobserved or unpersisted historical states.

Historical aliases are permanently mapped in Section 5 of [`PHASE2.1_FOUNDATION_SEMANTIC_MAP.md`](PHASE2.1_FOUNDATION_SEMANTIC_MAP.md), precluding ambiguous terms from regaining authority.

---

## PART E — B1–B8 Status and Decisions

In accordance with specification Section 19 and Section 29, **all B1–B8 items remain `PENDING_AUTHOR_DECISION`**. Recommendations are documented below, but are NOT adopted policy:

### B1: Legacy Route & Class-to-Route Map
```
B1 STATUS: PENDING_AUTHOR_DECISION

Current verified production fact:
    broken_text → OCR

Empirical status:
    genuine legacy-font occurrence remains unresolved.

Recommended current contract:
    Do not create a production REMAP route.
    Retain legacy as a separate forensic research attribute/track.

Future REMAP consideration:
    Only after empirical work establishes:
      1. reproducible legacy class,
      2. reliable detector,
      3. reproducible remapping operation,
      4. measurable downstream advantage.

Interpretation constraint:
    This does not establish that REMAP is useless.
    This does not establish that legacy-font pages are absent.
```

### B2: Route Precedence for Overlapping Classes
- **Status:** `PENDING_AUTHOR_DECISION`
- **Fact:** No routing precedence exists in frozen code.
- **Rule:** `sampling_stratum_priority` MUST NOT be reused as routing precedence. Under recommended B1 contract, precedence between legacy and broken text is `NOT_APPLICABLE`.

### B3: Oracle Routing Population Specification
- **Status:** `PENDING_AUTHOR_DECISION`
- **Fact:** `native_clean_control` is a stratum, not a label (0 units carry it). Literal reading yields 79 units (0 native controls); stratum reading yields 121 units (22 hybrid units).
- **Rule:** Author must select intended estimand (route discrimination vs. native control vs. calibration) and publish an enumerated unit manifest.

### B4: Deterministic Double-Annotation Selector
- **Status:** `PENDING_AUTHOR_DECISION`
- **Fact:** `selection_rank` is biased (74.7% in hex 0–3) and cannot be reused as an independent 25% selector.
- **Hard Requirements:** Deterministic canonical serialization, injective serialization over eligible IDs, fixed UTF-8 encoding, fixed domain separation tag, fixed threshold ($\text{rank} < \lfloor 0.25 \times 2^{256} \rfloor$), no duplicate keys, no `selection_rank` reuse, no post-hoc tuning (`same input -> same bytes -> same digest -> same selection`). Diagnostic statistics (observed fraction, stratum distribution) reported separately, not as validity criteria.

### B5: Oracle Scientific Construct & Evidence Channels
- **Status:** `PENDING_AUTHOR_DECISION`
- **Fact:** Rendered pixels cannot expose font encoding, `ToUnicode` tables, or invisible text.
- **Rule:** Author must choose between Option 1 (Semantic PDF Route Oracle with multi-channel evidence) and Option 2 (Visual Action Oracle with observable action labels). Do not mix semantic labels with image-only evidence.

### B6: PageGold & DocumentGold Reliability Design
- **Status:** `PENDING_AUTHOR_DECISION`
- **Fact:** The 25% oracle rule does not govern PageGold or DocumentGold.
- **Rule:** Author must approve hybrid design (uniform random population overlap + targeted diagnostic oversampling) and workload budget. Pre-adjudication raw annotations must be preserved immutably.

### B7: Reading-Order Reference Unit & Representation
- **Status:** `PENDING_AUTHOR_DECISION`
- **Fact:** String pairs lack a defined unit; PyMuPDF blocks are engine heuristics.
- **Rule:** Author must approve annotator-defined atomic visual text regions with stable IDs, normalized coordinates, and directed `PRECEDES` relations.

### B8: HOLDOUT Gold Annotation Governance
- **Status:** `PENDING_AUTHOR_DECISION`
- **Fact:** `allowed_before_final_freeze: false` creates an unambiguous default-deny stance. Historical pre-T0 exposure is `UNKNOWN` (P2-26).
- **Rule:** Maintain `DEFAULT_DENY` before system freeze. Authorize HOLDOUT annotation only after complete system freeze under strict blinding for final reference evaluation only.

---

## PART F — Formal Amendments Log

Phase 2.1 does not make any author-adopted change to the effective T0.4 methodology. Its outputs are provenance corrections, semantic-contract definitions, terminology normalization, decision formalization, and conformance tests.

Therefore:
```
NO FORMAL T0.4 AMENDMENT REQUIRED.
NO T0.4 AMENDMENT EFFECTIVE.
```

### Potential Amendment Triggers (Documented for Future Author Action):
1. **B1 Ratification:** If author formally ratifies collapsing `legacy_font` into `broken_text -> OCR` or operationalizing a REMAP lane.
2. **B3 Ratification:** If author formally defines the eligible oracle population and enumeration rule.
3. **B4 Ratification:** If author formally ratifies the domain tag and injective serialization rule for double annotation.
4. **B5 Ratification:** If author formally adopts multi-channel evidence or visual action labels.
5. **B6/B7 Ratification:** If author formally adopts PageGold/DocumentGold overlap rates or reading-order region schemas.
6. **B8 Ratification:** If author formally authorizes post-freeze HOLDOUT annotation.

No amendment file is created until an author decision formally adopts one of these changes.

---

## PART G — Deferred Empirical Questions

Two central questions remain empirical unknowns and are strictly protected against convenient assumption:
1. **Genuine Legacy Font Occurrence (P2-07):** Whether PDFs in the corpus suffer from genuine font encoding / `ToUnicode` failures while rendering visibly intact text is unverified. Assigned to FIT-only forensic Experiment X1.
2. **Historical Pre-T0 HOLDOUT Exposure (P2-26):** Whether ARPipe development before T0 processed or inspected documents now in HOLDOUT cannot be proven from surviving records. Assigned to metadata-only audit X6. Forward isolation is enforced via `DEFAULT_DENY`.

---

## PART H — Future Experiment Dependencies

All future experiments X0–X7 remain strictly **UNEXECUTED** and un-authorized in Phase 2.1:
- **X0 (Semantic Conformance):** Validates Phase 2.1 semantic contract fixtures (implemented in Phase 2.1 test suite).
- **X1 (Legacy Font Forensics):** Requires B1 contract + B5 evidence protocol. FIT-only, no OCR.
- **X2 (Hybrid Native/OCR Pilot):** Requires X0 + B1 + B2 + B5 + separate OCR compute authorization.
- **X3 (TOC/Outline Utility):** Requires DocumentGold calibration spans.
- **X4 (Gold Protocol Calibration):** Requires B5 + B6 + B7 schemas. Segregated FIT pilot.
- **X5 (Double-Annotation Verification):** Requires B3 + B4 signed decisions. Deterministic simulation.
- **X6 (HOLDOUT Provenance Audit):** Requires B8 governance scope. Metadata only, no content access.
- **X7 (MD&A Boundary Pilot):** Requires DocumentGold protocol draft. Calibration only.

---

## PART I — Master Change Ledger Summary

The master change ledger in [`PHASE2.1_CHANGE_LEDGER.md`](PHASE2.1_CHANGE_LEDGER.md) records 30 distinct changes:
- 7 Objective Corrections (PC-01, PC-05, PC-06, PC-07, CHG-08, CHG-10, CHG-20)
- 9 Documentation Clarifications (PC-02, PC-03, PC-04, PC-08, PC-09, PC-10, CHG-09, CHG-14, CHG-15, CHG-28)
- 12 Semantic Normalizations (CHG-03, CHG-04, CHG-05, CHG-06, CHG-11, CHG-12, CHG-13, CHG-16, CHG-17, CHG-18, CHG-19, CHG-26, CHG-27)
- 1 Deferred Empirical Question (CHG-07)
- 1 Author Decision Governance Record (CHG-29)
- 1 Formal Amendment Status Record (CHG-30)

**Immutability Invariant:** Every single row confirms `historical_artifact_changed = NO`.

---

## PART J — Readiness Gate, Author Handoff Table & Terminal State

### 1. Mandatory Author Handoff Table

| B item | Evidence status | Recommendation | Author status | Blocks |
|---|---|---|---|---|
| **B1** | verified facts + unresolved empirical question | no production REMAP yet | `PENDING_AUTHOR_DECISION` | B2 |
| **B2** | depends on B1 | explicit routing precedence | `PENDING_AUTHOR_DECISION` | routing |
| **B3** | competing population interpretations | select estimand/population | `PENDING_AUTHOR_DECISION` | B4 |
| **B4** | selector defect identified | canonical domain-separated selector | `PENDING_AUTHOR_DECISION` | double annotation |
| **B5** | evidence-channel mismatch identified | choose observable/semantic evidence design | `PENDING_AUTHOR_DECISION` | Gold |
| **B6** | reliability design unresolved | population + diagnostic layers | `PENDING_AUTHOR_DECISION` | Gold |
| **B7** | evaluator unit unresolved | stable engine-independent regions/order | `PENDING_AUTHOR_DECISION` | reading order |
| **B8** | governance boundary unresolved | default-deny + final-only HOLDOUT | `PENDING_AUTHOR_DECISION` | HOLDOUT |

---

### 2. Mandatory Final Terminal Status Declaration

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

