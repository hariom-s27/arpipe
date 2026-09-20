# Phase 2 canonical problem register

**Source of finding text:** `PHASE2_FOUNDATION_INTEGRITY_FINDINGS.json` at base commit `13423c400d9236c1e25a3df6ea3ca20166befefa`<br>
**Rule:** every P2 finding has one primary root and one principal disposition. Secondary implications do not create duplicate findings. Text under **Exact observed wording** is reproduced verbatim from the authoritative JSON.

Disposition vocabulary: `OBJECTIVE_CORRECTION`, `AUTHOR_DECISION_REQUIRED`, `EMPIRICAL_QUESTION`, `DOCUMENTATION_ONLY`, `NO_ACTION_REQUIRED`, `ALREADY_RESOLVED`, or `UNRESOLVED`.

## Summary

| ID | Primary root | Principal disposition | Phase relevance | Blocks Phase 2.1 closure? |
|---|---|---|---|:---:|
| P2-01 | RC1 | OBJECTIVE_CORRECTION | Phase 2.1 correction ledger | No |
| P2-02 | RC1 | DOCUMENTATION_ONLY | Provenance convention | No |
| P2-03 | RC2 | OBJECTIVE_CORRECTION | Predicate catalog | Yes |
| P2-04 | RC2 | OBJECTIVE_CORRECTION | Predicate catalog; B3 input | Yes |
| P2-05 | RC2 | OBJECTIVE_CORRECTION | Predicate catalog | Yes |
| P2-06 | RC2 | OBJECTIVE_CORRECTION | Predicate catalog | Yes |
| P2-07 | RC4 | EMPIRICAL_QUESTION | Future FIT forensics | No |
| P2-08 | RC2 | OBJECTIVE_CORRECTION | Predicate catalog | Yes |
| P2-09 | RC2 | DOCUMENTATION_ONLY | Proxy interpretation | No |
| P2-10 | RC2 | OBJECTIVE_CORRECTION | Unit/denominator contract | Yes |
| P2-11 | RC3 | NO_ACTION_REQUIRED | Guardrail retained | No |
| P2-12 | RC3 | AUTHOR_DECISION_REQUIRED | Evidence ontology | Yes |
| P2-13 | RC2 | DOCUMENTATION_ONLY | Representation limitation | No |
| P2-14 | RC1 | DOCUMENTATION_ONLY | Descriptive metadata | No |
| P2-15 | RC1 | DOCUMENTATION_ONLY | Missing-record terminology | No |
| P2-16 | RC4 | AUTHOR_DECISION_REQUIRED | B1 route vocabulary | Yes |
| P2-17 | RC4 | AUTHOR_DECISION_REQUIRED | Routing contract | Yes |
| P2-18 | RC2 | OBJECTIVE_CORRECTION | Sampling interpretation | Yes |
| P2-19 | RC5 | AUTHOR_DECISION_REQUIRED | Gold schema/protocol | Yes |
| P2-20 | RC1 | OBJECTIVE_CORRECTION | Correction ledger | No |
| P2-21 | RC1 | OBJECTIVE_CORRECTION | Correction ledger | No |
| P2-22 | RC1 | OBJECTIVE_CORRECTION | Historical attribution | No |
| P2-23 | RC1 | DOCUMENTATION_ONLY | Provenance boundary | No |
| P2-24 | RC1 | NO_ACTION_REQUIRED | Reproduction prerequisite | No |
| P2-25 | RC1 | DOCUMENTATION_ONLY | Preregistration claim limit | No |
| P2-26 | RC6 | UNRESOLVED | Historical limitation | No |
| P2-27 | RC6 | NO_ACTION_REQUIRED | Forward HOLDOUT guard | No |
| P2-28 | RC5 | ALREADY_RESOLVED | Closure-scope interpretation | No |

“Blocks” means the item must be settled to **close** Phase 2.1 and authorize downstream Gold/benchmark work. None prevents Phase 2.1 from starting.

## Authoritative metadata

These fields reproduce the JSON's recorded classification. `TARGETED_ISSUE` is a recorded severity label, not this integration's blocking judgment.

| ID | Area / affected component | Artifact or path | Evidence class | Recorded status / severity | Recorded owner phase / bucket |
|---|---|---|---|---|---|
| P2-01 | A/L Lineage | Task milestone registry: T0.1R SHA | VERIFIED_FACT | INCONSISTENT / NON_BLOCKING | Task author (registry text) / SHOULD_FIX |
| P2-02 | A Lineage | T0.4 preregistration; P-X1 audit; `tools/audit_t0_4_setup.py`; `tools/t0_4/README.md` | DOCUMENTED_CLAIM | CONSISTENT / NON_BLOCKING | Phase 3 citation rule / DEFERRED_P3 |
| P2-03 | B/D Consistency | T0.3A/R1 `core_relevance_summary`; `tools/run_t0_3a_document_coverage.py` | DETERMINISTIC_DERIVED | INCONSISTENT / TARGETED_ISSUE | Amendment/Phase 3 / SHOULD_FIX |
| P2-04 | D/C Predicates | T0.4 `condition_labels`/`representation_class`; T0.1 `native_page`; `tools/t0_4/core.py`; metrics spec | DETERMINISTIC_DERIVED | INCONSISTENT / TARGETED_ISSUE | Phase 3/4 / SHOULD_FIX |
| P2-05 | D/C Predicates | T0.1, detector, T0.3A and T0.4 `scanned` predicates | DETERMINISTIC_DERIVED | INCONSISTENT / NON_BLOCKING | Phase 3 / DEFERRED_P3 |
| P2-06 | D/C Predicates | T0.1/T0.3A and T0.4 `multi_column` predicates | DETERMINISTIC_DERIVED | INCONSISTENT / NON_BLOCKING | Phase 3 / DEFERRED_P3 |
| P2-07 | D Predicates | T0/T0.1/T0.3A/T0.4 legacy-font predicates and taxonomy | DETERMINISTIC_DERIVED | INCONSISTENT / TARGETED_ISSUE | Phase 4/5 after author decision / DEFERRED_P45 |
| P2-08 | D Predicates | OCR-layer proxy in freeze/audit/reconciliation tools and reports | PROXY_OR_CANDIDATE | INCONSISTENT / TARGETED_ISSUE | Amendment/Phase 3 wording / SHOULD_FIX |
| P2-09 | D Predicates | TOC/annexure taxonomy, audit config, and audit tool | DETERMINISTIC_DERIVED | INCONSISTENT / TARGETED_ISSUE | Amendment/Phase 3 wording / SHOULD_FIX |
| P2-10 | C Terminology | T0.3A/R1 coverage matrices `page_count` | DETERMINISTIC_DERIVED | INCONSISTENT / TARGETED_ISSUE | Amendment/Phase 3 wording / SHOULD_FIX |
| P2-11 | E Evidence | Table, annexure, TOC, MD&A, OCR-layer, legacy, hidden/duplicate-text proxies | PROXY_OR_CANDIDATE | CONSISTENT / NON_BLOCKING | Phase 3 wording / DEFERRED_P3 |
| P2-12 | C/E Evidence | Evidence vocabularies and `VALIDATED_METADATA` | DOCUMENTED_CLAIM | UNVERIFIED / NON_BLOCKING | Phase 3 / DEFERRED_P3 |
| P2-13 | D/E Predicates | Reconciled `document_representation`; T0.3A native/mixed register | DETERMINISTIC_DERIVED | CONSISTENT / NON_BLOCKING | Phase 3 wording / DEFERRED_P3 |
| P2-14 | B Consistency | T0 `corpus_inventory.csv:file_size_bytes`; freeze tool | VERIFIED_FACT | INCONSISTENT / NON_BLOCKING | Phase 3 / DEFERRED_P3 |
| P2-15 | B/C Consistency | Missing-byte records in T0 versus T0.4 Track B | DETERMINISTIC_DERIVED | INCONSISTENT / NON_BLOCKING | Phase 3 / DEFERRED_P3 |
| P2-16 | C Terminology | Legacy/REMAP terms in metrics, future-results, oracle, T0.4/P-X1 docs | DOCUMENTED_CLAIM | INCONSISTENT / NON_BLOCKING | Phase 4/5 / DEFERRED_P45 |
| P2-17 | G Routing | `CLAUDE.md`, models, triage, pipeline, OCR, and T0.4 routing classes | DOCUMENTED_CLAIM | INCONSISTENT / TARGETED_ISSUE | Author B1 then Phase 4/5 / SHOULD_FIX |
| P2-18 | F/G Sampling | Closure section 5; sampling priority; T0.4 core | DETERMINISTIC_DERIVED | INCONSISTENT / NON_BLOCKING | Phase 3 wording / DEFERRED_P3 |
| P2-19 | H Gold/oracle | Gold schema, oracle routing spec, annotation roster | VERIFIED_FACT | INCONSISTENT / NON_BLOCKING | Phase 4/5 / DEFERRED_P45 |
| P2-20 | I Hash | `configs/audit_config.sha256` versus JSON | DETERMINISTIC_DERIVED | INCONSISTENT / TARGETED_ISSUE | Amendment / SHOULD_FIX |
| P2-21 | I/K Hash | Phase-1 verification artifact table | DOCUMENTED_CLAIM | INCONSISTENT / TARGETED_ISSUE | Phase-1 document owner / SHOULD_FIX |
| P2-22 | K Provenance | Phase-1 verification Issues section 2 | DOCUMENTED_CLAIM | INCONSISTENT / TARGETED_ISSUE | Phase-1 document owner / SHOULD_FIX |
| P2-23 | K Provenance | B1-B8 and routing records at `d9f974b`/`916407d` | HISTORICAL_CONTEXT | UNVERIFIED / NON_BLOCKING | Author publication; Phase 3 citation / DEFERRED_P3 |
| P2-24 | K Provenance | Ignored local PDFs, inventory locators, external P-X1 snapshot | DOCUMENTED_CLAIM | CONSISTENT / NON_BLOCKING | Phase 3 dependency note / DEFERRED_P3 |
| P2-25 | K Provenance | T0.3A versus R1 taxonomy/measurement ordering | DOCUMENTED_CLAIM | UNVERIFIED / NON_BLOCKING | Phase 3 wording / DEFERRED_P3 |
| P2-26 | J HOLDOUT | Legacy evaluation protocol/queues/log versus T0 HOLDOUT | DETERMINISTIC_DERIVED | UNVERIFIED / TARGETED_ISSUE | Phase 3 scope/claims / DEFERRED_P3 |
| P2-27 | J HOLDOUT | Challenge set, manual-review queue/results, Devanagari candidate | DETERMINISTIC_DERIVED | UNVERIFIED / NON_BLOCKING | Phase 3/4 guard / DEFERRED_P3 |
| P2-28 | B/K Consistency | `CLOSED_FOR_GOLD_PHASE` closure wording | DOCUMENTED_CLAIM | CONSISTENT / NON_BLOCKING | Phase 3 wording / DEFERRED_P3 |

## Research and dependency classification

“Existing evidence” describes the state after inspecting the project record but before external synthesis. “External” is `TARGETED` only where the field can materially clarify a method/mechanism; it is not a request for another broad review.

| ID | Existing evidence | Integration relevance | External | Future experiment | Downstream dependency |
|---|---|---|---|---|---|
| P2-01 | SUFFICIENT | DOCUMENTATION_ONLY | NONE | None | Correct registry citation |
| P2-02 | SUFFICIENT | NON_BLOCKING | NONE | None | Freeze identity convention |
| P2-03 | SUFFICIENT | BLOCKING | NONE | X0 validation only | Predicate catalog |
| P2-04 | SUFFICIENT | BLOCKING | NONE | X0; B3 population check | B3 and route/Gold universes |
| P2-05 | SUFFICIENT | BLOCKING | NONE | X0 validation only | Predicate catalog and stratified reports |
| P2-06 | SUFFICIENT | BLOCKING | NONE | X0 validation only | Predicate catalog and layout strata |
| P2-07 | PARTIALLY_SUFFICIENT | PHASE_RELEVANT | TARGETED | X1 | B1/B2 and possible future recovery route |
| P2-08 | SUFFICIENT | BLOCKING | TARGETED mechanism only | X0; no detector experiment required now | Proxy description/evidence ontology |
| P2-09 | SUFFICIENT | NON_BLOCKING | TARGETED | X3 | Candidate generation and DocumentGold aids |
| P2-10 | SUFFICIENT | BLOCKING | NONE | X0 validation only | Denominator-correct reporting |
| P2-11 | SUFFICIENT | NON_BLOCKING | NONE now | Future proxy-validation studies only if needed | Claim discipline |
| P2-12 | PARTIALLY_SUFFICIENT | BLOCKING | TARGETED standards | X0 | Evidence/provenance ontology |
| P2-13 | SUFFICIENT | NON_BLOCKING | NONE | X0 description check | Representation-stratified analysis |
| P2-14 | SUFFICIENT | DOCUMENTATION_ONLY | NONE | None | File identity/integrity wording |
| P2-15 | SUFFICIENT | DOCUMENTATION_ONLY | NONE | None | Track-B missing-record semantics |
| P2-16 | RECOMMENDATION_ONLY | BLOCKING | TARGETED | X1 only if separate class retained | B1/B2 route vocabulary |
| P2-17 | PARTIALLY_SUFFICIENT | BLOCKING | TARGETED | X2 after contract decisions | Production/benchmark routing contract |
| P2-18 | SUFFICIENT | BLOCKING | NONE | X0 feasibility validation | Sampling coverage interpretation |
| P2-19 | PARTIALLY_SUFFICIENT | BLOCKING | TARGETED methodology | X4, X5, X7 | B4-B7 and Gold readiness |
| P2-20 | SUFFICIENT | NON_BLOCKING | NONE | None | Correction ledger / byte convention |
| P2-21 | SUFFICIENT | NON_BLOCKING | NONE | None | Correction ledger / citation trust |
| P2-22 | SUFFICIENT | NON_BLOCKING | NONE | None | B1-B8 provenance |
| P2-23 | SUFFICIENT | NON_BLOCKING | NONE | None | Publication/provenance boundary |
| P2-24 | SUFFICIENT | NON_BLOCKING | NONE | None | Reproduction prerequisites |
| P2-25 | SUFFICIENT | DOCUMENTATION_ONLY | NONE | None | Preregistration claim limits |
| P2-26 | UNRESOLVED | PHASE_RELEVANT | TARGETED leakage concepts | X6 metadata only | B8 and evaluation limitations |
| P2-27 | SUFFICIENT | NON_BLOCKING | NONE | No content experiment | B8 forward protection |
| P2-28 | SUFFICIENT | NON_BLOCKING | NONE | None | Closure-scope wording |

The exact wording and resolution under each finding below jointly provide the current project evidence and current interpretation. The Phase-2 audit reproduced all checkable B1-B8 facts; external evidence changes interpretation only where noted in the evidence matrix.

## Finding records

### P2-01 — malformed T0.1R SHA

- **Primary root:** RC1
- **Principal disposition:** OBJECTIVE_CORRECTION
- **Resolution:** Record `879762a2f236b3aaa6df33b7ddacc60c01d633c1`; no historical object changes.
- **Exact observed wording:**

> The T0.1R SHA in the Phase-2 task text is 41 hex characters (`...df33db7dd...`) and does not resolve as a Git object. The 7-character prefix `879762a` resolves uniquely to the 40-character SHA `879762a2f236b3aaa6df33b7ddacc60c01d633c1` (`...df33b7dd...`, one `d` fewer), which is the tip of branch `t0.1-reconcile`, the sole parent of T0.2, and the value in the Phase-1 registry.

### P2-02 — configuration-freeze identity convention

- **Primary root:** RC1
- **Principal disposition:** DOCUMENTATION_ONLY
- **Resolution:** State that the twelve JSON configs use recorded SHA-256 values while the amended Markdown records are identified by their final Git blobs at `63e3c04`; “frozen” means the final pre-execution tree, not never amended.
- **Exact observed wording:**

> The preregistration says it is 'frozen before execution' and the P-X1 audit 'frozen before benchmark execution', yet both were amended at 33ba76a (documented in closure sections 1 and 9). The preregistration names these two docs as part of the configuration freeze, but `artifacts/t0_4/config_hashes.json` hashes only the 12 JSON configs; the two docs are identified by Git blob only.

### P2-03 — “191 native digital documents” conflation

- **Primary root:** RC2
- **Principal disposition:** OBJECTIVE_CORRECTION
- **Resolution:** Reserve “contains at least one T0.1 native page” for 191; do not call those 191 whole-document native. Record the distinct 60/132/2 representation counts and the historical T0 count separately.
- **Exact observed wording:**

> The sentence 'Core English MD&A extraction is 100% supported by native digital documents (191 docs, 36 issuers)' is a hard-coded string literal, not derived from the register. The same artifacts' coverage matrix gives native=60, mixed=132, scanned=2 documents. 191 is T0.1's count of documents containing at least one native text page (CLAIM:C005); T0 classified 151 documents `digital`; T0.1R explicitly separated '191 docs containing native pages' from '60 whole-document native representation' (tools/reconcile_t0_1.py:499-506).

### P2-04 — `native_ok` namespace collision

- **Primary root:** RC2
- **Principal disposition:** OBJECTIVE_CORRECTION
- **Resolution:** Give the T0.1 page predicate and T0.4 detector class different canonical names. Do not infer route or oracle cleanliness from a `condition_labels.native_ok` value. B3 still needs an author decision about its intended population.
- **Exact observed wording:**

> The label `native_ok` in `condition_labels` comes from T0.1 `native_page` (char_count > 50 and not (chars <= 20 and image >= 0.85)), which also covers hybrid, broken_text and vector_text pages. The routing-class name `native_ok` is the detector kind `digital`. Detector digital = 35,580 pages; T0.1 native_page = 36,988. In the 475-unit manifest 157 units carry the label `native_ok` together with an OCR-routed representation class: hybrid 102/102, broken_text 20/20, scanned 28/72, vector_text 7/17. Stratum `native_clean_control` (60 units, all splits) contains 22 hybrid units.

### P2-05 — two `scanned` predicates

- **Primary root:** RC2
- **Principal disposition:** OBJECTIVE_CORRECTION
- **Resolution:** Name A and B separately and require every count/stratum to cite the predicate version. Do not retroactively change either frozen computation.
- **Exact observed wording:**

> Predicate A (detector `scanned`): n_chars < 120 and image area >= 0.55, or >= 0.25 when drawings < 400 -> 804 pages. Predicate B (T0.1 `scanned_page`): chars <= 20 and image >= 0.85 -> 284 pages, a strict subset of A (A-only 520, B-only 0). T0.3A categories (`scanned`, `fully_scanned_document`, `mixed_scanned_pages`) use B; the T0.4 stratum and representation class `scanned` use A (72 units).

### P2-06 — two `multi_column` estimators

- **Primary root:** RC2
- **Principal disposition:** OBJECTIVE_CORRECTION
- **Resolution:** Version the T0.1 estimator and T0.4 detector predicate separately; their counts are not interchangeable.
- **Exact observed wording:**

> T0.1/T0.3A `multi_column` = T0.1 estimator with >= 3 columns (17,190 pages, 191 documents). T0.4 label `multi_column` = detector `n_columns >= 2` (18,855 pages) OR T0.1 `two_column_page` (15,015 pages). The two estimators disagree: T0.1 `two_column_page` is not equal to detector `n_columns == 2` (9,521) and is not a subset of `n_columns >= 2`.

### P2-07 — three legacy-font operationalizations

- **Primary root:** RC4
- **Principal disposition:** EMPIRICAL_QUESTION
- **Resolution:** Preserve all three as historically named proxies, rename them in the semantic catalog, and do not assert genuine legacy encoding. Use the FIT-only forensic experiment before adopting a legacy route.
- **Exact observed wording:**

> Three operationalizations share one name. (a) T0 document-level `legacy_font` = document has >= 1 detector `broken_text` page: 24 documents, evidence INFERRED. (b) T0.3A `legacy_font_candidate` = `legacy_candidate_page_count > 0`, where a page is a candidate if detector broken_text OR any U+FFFD OR more than 5 private-use characters: 56 documents, 1,007 pages; the register describes only 'U+FFFD or PUA', and the config key `broken_font_min_pua_or_mojibake_ratio` (0.05) is never read. (c) T0.4 label/stratum = `cid_or_broken_text_indicator`, identical to `kind == broken_text` (803/803 pages; 20/20 units). Overlap: the 24 documents in (a) and (c) are inside the 56 in (b); 32 documents are (b)-only.

### P2-08 — OCR-layer proxy description differs from code

- **Primary root:** RC2
- **Principal disposition:** OBJECTIVE_CORRECTION
- **Resolution:** Define it only as the implemented `kind == scanned and n_chars > 50` candidate proxy. Remove render-mode/signature language from future descriptions unless a new detector is separately specified and tested.
- **Exact observed wording:**

> About eight frozen artifacts describe the OCR-layer proxy as detection of 'PDF render mode 3 (invisible text layer)' or OCR producer signatures. The implemented predicate is `kind == 'scanned' and n_chars > 50` (T0 page profile); T0.1 consumes it unchanged (`is_t0_ocr`, line 249) and no code inspects PDF text render modes. 189 pages, all detector-`scanned`, none in T0.1 `scanned_page`. The evidence label stays CANDIDATE_PROXY.

### P2-09 — TOC and annexure proxy overbreadth

- **Primary root:** RC2
- **Principal disposition:** DOCUMENTATION_ONLY
- **Resolution:** Retain the frozen proxy results but state the actual full-text/first-50-page predicates and their saturation. Treat them as candidate-generation signals, never Gold.
- **Exact observed wording:**

> (a) TOC: the register says the keyword is sought 'within the first 30 pages'; the implementation flags any page with a keyword and `physical_page < 50` (`toc_max_start_page_search`). The keyword list includes the substring `index`, and `toc_min_entries` is not applied to candidate flagging: 174 of 194 documents flagged (89.7%). (b) Annexure: the register says a keyword match 'in document outline or heading'; the implementation flags a document when any page's full text contains 'annexure' (`has_annexure_keyword`): 188 of 194 documents (96.9%). `combined_mdna_candidate` matches its register description (outline title or heading line), apart from two extra trigger words (`board`, `annexure`).

### P2-10 — T0.3A/R1 page-count denominator

- **Primary root:** RC2
- **Principal disposition:** OBJECTIVE_CORRECTION
- **Resolution:** Rename the matrix quantity to `pages_in_member_documents` (or define it equivalently) and keep condition-bearing-page counts separate.
- **Exact observed wording:**

> In the T0.3A/R1 matrices `page_count` is the total pages of member documents, not the pages exhibiting the condition (verified by summing `total_pages`): legacy_font_candidate 13,377 vs 1,007 candidate pages; has_ocr_layer_pages 23,877 vs 189 OCR-layer pages; multi_column_layout 37,667 vs 17,190; native 7,694 = total pages of the 60 NATIVE documents. The audit plan does not define the column, and T0.1 uses the suffix `_page_count` for pages that exhibit the condition.

### P2-11 — proxies remained proxies

- **Primary root:** RC3
- **Principal disposition:** NO_ACTION_REQUIRED
- **Resolution:** Preserve the existing non-promotion guard. Add precision/recall only if a future human-labelled validation study is authorized; prevalence is not validity.
- **Exact observed wording:**

> Every proxy is labelled CANDIDATE_PROXY (T0.3A register: 17 categories) and NOT_REVIEWED at page level (condition_page_map 52,478 rows, table_candidates 29,476, language_candidates 2); T0.1R records human_reviewed_count = 0. No promotion to VERIFIED was found. Flagged prevalence is near-saturated: table_candidate 29,476 of 37,917 pages (77.7%); annexure_candidate 188/194 documents; toc_candidate 174/194. Not human-verified; no precision or recall exists.

### P2-12 — unmapped evidence vocabularies

- **Primary root:** RC3
- **Principal disposition:** AUTHOR_DECISION_REQUIRED
- **Resolution:** Adopt a crosswalk that distinguishes source metadata, byte-verified metadata, deterministic derivation, candidate proxy, human annotation, adjudicated Gold, and unknown. Do not use `VALIDATED_METADATA` until “validated,” by whom, against what source, and at what unit are defined.
- **Exact observed wording:**

> `VALIDATED_METADATA` labels era, size, stub and split metadata in T0.3A and T0.4 but is defined nowhere, and the T0 inventory has no `fiscal_year_evidence` column. Five vocabularies coexist without a mapping: T0 (KNOWN_FROM_PRIOR / OBSERVED / INFERRED / UNKNOWN), T0.1 (NOT_REVIEWED / MODEL_REVIEWED), T0.3A (EXISTING_CONDITION / EXISTING_CORPUS_FIELD / VALIDATED_METADATA / CANDIDATE_PROXY / DERIVED_INTERACTION / UNMEASURED), T0.4 (VALIDATED_METADATA / CANDIDATE_PROXY / NOT_YET_ANNOTATED), and the T0.4 sentinels.

### P2-13 — representation classes depend on proxies

- **Primary root:** RC2
- **Principal disposition:** DOCUMENTATION_ONLY
- **Resolution:** Keep the 60/132/2 outputs reproducible, but describe NATIVE/MIXED/SCANNED as rule-derived representation classes, not verified PDF ontology.
- **Exact observed wording:**

> Verified rule: NATIVE = scanned_page_count == 0 and ocr_page_count == 0 (60 documents; only 21 of them have every page native); MIXED = scanned > 0 or ocr > 0 (132 documents: 71 via the OCR-layer proxy only, 34 via scanned pages only, 27 via both); SCANNED = fully scanned (2). All 189 OCR-layer pages are detector-`scanned`. T0.1R documented the ocr-to-MIXED dependency (KNOWN_DEPENDENCY). The T0.3A register limit for `native` mentions only 'absence of scanned pages', and the category is labelled EXISTING_CONDITION, not proxy.

### P2-14 — stale fetch-stage file sizes

- **Primary root:** RC1
- **Principal disposition:** DOCUMENTATION_ONLY
- **Resolution:** Treat stored-byte SHA-256 as identity. Label `file_size_bytes` as fetch-stage metadata and do not use it as an integrity check unless remeasured from the identified blob.
- **Exact observed wording:**

> For 83 of 194 documents the recorded `file_size_bytes` differs from the size of the stored PDF (deltas -7.29 MB to +15.48 MB, median +222 KB, both signs) although the SHA-256 matches for 194/194. The tool copies `n_bytes` from the fetch-stage manifest instead of measuring the stored blob; the reason for the difference is not recorded.

### P2-15 — meaning of “excluded from every split”

- **Primary root:** RC1
- **Principal disposition:** DOCUMENTATION_ONLY
- **Resolution:** Distinguish executable split membership from administrative issuer association. The 14 missing records are not executable members; six inherit an issuer split for `INPUT_UNAVAILABLE`, while eight are unassigned.
- **Exact observed wording:**

> T0 says the 14 MISSING records are 'excluded from every split'. In the T0.4 Track-B manifest 6 of the 14 carry their issuer's split with role INPUT_UNAVAILABLE (FIT 2, VALIDATION 4) and 8 are UNASSIGNED_HISTORICAL; the preregistration says records 'deliberately excluded from all frozen partitions remain UNASSIGNED_HISTORICAL'. The two statements agree for 8 records and are ambiguous for 6. Document counts (194 = 92 + 48 + 54) are unaffected.

### P2-16 — seven legacy/REMAP names

- **Primary root:** RC4
- **Principal disposition:** AUTHOR_DECISION_REQUIRED
- **Resolution:** Choose one route vocabulary and explicitly map historical proxies to it. A schema symbol or prose lane is not an implemented route.
- **Exact observed wording:**

> One concept has seven names: `legacy_font` (routing class), `legacy_font_candidate` (label/stratum), `LEGACY` (oracle route), 'REMAP lane' (preregistration), `LEGACY_FONT_REMAP` (metrics level), `LEGACY_REMAP` (future-results track), 'legacy-font lane' (P-X1 audit). REMAP is never defined operationally; no code implements it (about a dozen non-CSV mentions, all prose, schema names or guard regexes).

### P2-17 — hybrid/blank contract and code mismatch

- **Primary root:** RC4
- **Principal disposition:** AUTHOR_DECISION_REQUIRED
- **Resolution:** Specify actual current behavior and desired future behavior separately. Phase 2 recommends no code change; B1/B2/B5 and a later FIT-only pilot must precede architecture changes.
- **Exact observed wording:**

> Hybrid: CLAUDE.md and models.py say 'read text, OCR the image'; the code puts HYBRID in NEEDS_OCR, reads the text layer only for DIGITAL pages, and OCRs whole pages (`_ocr_pages`); no code branches on HYBRID (only docstring hints). Blank: PageKind has six members but CLAUDE.md lists 'five page classes'; blank is excluded implicitly at triage.py:303 and pipeline.py:247 with no documented route. T0.4 ROUTING.classes (native_ok, legacy_font, broken_text, scanned, vector_text) omit hybrid and blank: 157 of 475 units (33%) sit in representation classes with no ROUTING class, and `legacy_font` is a ROUTING class with no PageKind and no producer. Route rows verified consistent: digital -> text layer; scanned, broken_text, vector_text -> OCR.

### P2-18 — structural zero cells

- **Primary root:** RC2
- **Principal disposition:** OBJECTIVE_CORRECTION
- **Resolution:** Classify impossible, structurally pre-empted, and observed-but-unsampled cells separately. Do not report all 16,157 zero-availability cells as empirical coverage gaps.
- **Exact observed wording:**

> The closure attributes the empty `broken_text` and `ocr_layer_proxy` strata to 'the corpus and priority order'. Both are structural: `legacy_font_candidate` (identical to broken_text, higher priority) always pre-empts `broken_text`, and the OCR-layer indicator is defined as `kind == scanned and ...`, so `scanned` always pre-empts `ocr_layer_proxy`. Only 15 of 77 declared (stratum, representation) pairs occur on any page; 13,392 of the 16,632 declared cells lie in the other 62 pairs, so most of the 16,157 zero-availability cells are structurally impossible combinations, not coverage gaps.

### P2-19 — incomplete Gold/oracle interface

- **Primary root:** RC5
- **Principal disposition:** AUTHOR_DECISION_REQUIRED
- **Resolution:** Before annotation, version an Oracle schema and complete blinding, provenance, bbox, and reading-order contracts. Keep Oracle route labels separate from PageGold and DocumentGold unless an explicit schema mapping is approved.
- **Exact observed wording:**

> (a) `OracleRouteGold` is not a frozen name: the oracle record exists only as `oracle_routing_spec.json:annotation_fields` and is not validated by `gold_schema.json`, whose `oneOf` has only page_gold and document_gold. (b) No T0.4 schema has a blinding field; `saw_pipeline_output` exists only in the T0 roster header (25 rows, all blank); blinding of primary annotators to detector output is unspecified (only the adjudicator is 'blind to all engine outputs'). (c) PageGold `annotation_provenance` requires annotator_id, protocol_version and adjudication_status; DocumentGold `annotation_provenance` is an unconstrained object. (d) `reading_order_pairs` are string-ID pairs with no reference unit. (e) The `bbox` coordinate convention is unspecified.

### P2-20 — `audit_config` newline/hash mismatch

- **Primary root:** RC1
- **Principal disposition:** OBJECTIVE_CORRECTION
- **Resolution:** Add the actual blob hash and state that the recorded value identifies blob-plus-one-newline. Preserve the correctly pinned CRLF dataset copy and distinguish semantic JSON equality from byte identity.
- **Exact observed wording:**

> Recorded `8e26bec124a34806...`; actual blob `a3a575cda1ec7345...`. The recorded value is reproduced exactly by the blob plus one trailing newline, so the hashed content is identifiable. The two `audit_config.json` copies parse to identical JSON (same canonical hash); the dataset copy is CRLF, its `.sha256` matches (`65ed1a7e...`), and T0.1R's raw_input_manifest pins that copy. History shows a single commit for both files.

### P2-21 — ten incorrect Phase-1 hash-table values

- **Primary root:** RC1
- **Principal disposition:** OBJECTIVE_CORRECTION
- **Resolution:** Publish a correction table sourced from the cited manifests and current blobs. Do not claim the erroneous strings verify any blob, and do not rewrite the Phase-1 report.
- **Exact observed wording:**

> 10 of the 27 SHA-256 strings in the table are marked 'Matches / VERIFIED' but do not equal the SHA-256 of the cited blob (issuer_split.csv, page_profile.csv, audit_config.json, gap_audit_document.csv, condition_page_map.csv, table_candidates.csv, language_candidates.csv, manual_review_manifest.csv, manual_review_results.csv, toc_offset_candidates.csv). None equals the SHA-256 of any of the 252 blobs in the closure tree or of the Phase-1 worktree file. Five share only the 8-character prefix printed in the closure report. The cited pin sources (raw_input_manifest.json, final_closure_audit.json) record the correct values. The other 17 rows match.

### P2-22 — two closure observations became eight questions

- **Primary root:** RC1
- **Principal disposition:** OBJECTIVE_CORRECTION
- **Resolution:** Attribute only two observations to T0.4 closure and attribute B1-B8 to the post-closure Gold register. Preserve the distinction between integrity audit Phase 2 and later Gold-method integration.
- **Exact observed wording:**

> Phase 1 says the T0.4 closure report 'documents 8 methodological questions'. The closure (markdown and JSON) documents two observations (native_clean_control reading; class-to-route map) and contains none of the double-annotation, adjudication, reading-order, HOLDOUT-authorization, hash-rank or precedence topics. The list of eight is the post-closure T0.4-GOLD register (B1-B8), renumbered and lossy in Phase 1 (no precedence item; 'route-class to oracle-class mapping' as item 8), and it defers them to 'Phase 2 (Gold Method Research and Integration)', whereas this Phase 2 is the integrity audit.

### P2-23 — post-closure/local-only provenance

- **Primary root:** RC1
- **Principal disposition:** DOCUMENTATION_ONLY
- **Resolution:** Use the records as research inputs with explicit commit provenance. Do not present the T0.4-LF recommendation as adopted or remote-published policy.
- **Exact observed wording:**

> The register exists only in post-closure safety-snapshot commits (subject 'REPOSITORY SAFETY SNAPSHOT - NOT A SCIENTIFIC METHODOLOGY COMMIT') on local branches; `origin/t0.4-gold` and `origin/t0.4-routing-clarification` still point at 63e3c04. The T0.4-LF record contains an unadopted recommendation ('A. One class, OCR route (recommended)', status T0.4_LF_BLOCKED, 'No rule was adopted'). Every checkable fact in the register was reproduced (see Audit results, B1-B8).

### P2-24 — local PDF and external P-X1 dependency

- **Primary root:** RC1
- **Principal disposition:** NO_ACTION_REQUIRED
- **Resolution:** Record prerequisites. T0/T0.1 independent reproduction needs the identified local PDF store; T0.4 sampling does not. Keep P-X1 harness descriptions `UNVERIFIED_FROM_TREE` unless its snapshot is separately acquired and pinned.
- **Exact observed wording:**

> PDF bytes are not in Git. Read-only byte hashing of the 194 local PDFs found 194/194 SHA-256 matches with the inventory and 0 missing. T0/T0.1 independent re-derivation therefore needs the local store; the T0.4 sampling reproduction needs only Git-tracked CSVs. The P-X1 reuse audit's description of the P-X1 harness rests on an external snapshot the audit itself says is 'not present in the T0.3A-R1 Git tree'; those descriptions are UNVERIFIED from the tree.

### P2-25 — taxonomy/measurement ordering claim

- **Primary root:** RC1
- **Principal disposition:** DOCUMENTATION_ONLY
- **Resolution:** Do not claim Git-demonstrated preregistration for T0.3A. R1 ordering is demonstrable, but the era counts were not newly measured there.
- **Exact observed wording:**

> T0.3A's subject says 'frozen taxonomy input', but the register and the measurement outputs are in one commit, so Git cannot show that the register preceded the measurement. For R1, f0e5805 adds only configs/t0_3a_r1/taxonomy_register.json and is an ancestor of ff030d9, so that ordering is Git-verifiable; however both era categories had already been measured in T0.3A (58/6,863/29 and 136/31,054/36, identical in R1), and R1 changed only the justification text of `post_2015`.

### P2-26 — three historical “holdout” referents

- **Primary root:** RC6
- **Principal disposition:** UNRESOLVED
- **Resolution:** Use “T0 HOLDOUT” for the current frozen split and qualify all earlier partitions. Record `historical_pre_T0_exposure = UNKNOWN`; do not infer either cleanliness or leakage.
- **Exact observed wording:**

> 'Holdout' has at least three referents in the frozen tree: (1) T0 frozen `HOLDOUT` (54 documents, 9 issuers, issuer-disjoint, seed 20260918); (2) the legacy holdout of `configs/eval_protocol.md` (45-document queue, document-level random split, seed 20260912, `contaminated` flag, 4 holdout-scoring log entries on 2026-09-11 at commit bc5f174); (3) P-X1's historical development/holdout page partitions (external snapshot). T0 and T0.4 never reference the legacy protocol. By SHA-256, the 45 legacy-holdout documents fall in T0 FIT 18 / VALIDATION 13 / HOLDOUT 14, and 26 of the 92 legacy-FIT-queue documents fall in T0 HOLDOUT. `labels_holdout.csv` has no data rows, and none of the 20 historical labels maps to a T0 HOLDOUT document. The raw T0.1 report says the HOLDOUT has '9 issuers completely unseen during development'; T0.1R's claim audit (58 claims) neither audits nor retracts it. Whether ARPipe development before T0 (2026-09-18) processed HOLDOUT documents is not established by the frozen record.

### P2-27 — HOLDOUT in historical coverage selections

- **Primary root:** RC6
- **Principal disposition:** NO_ACTION_REQUIRED
- **Resolution:** The reconciled record already corrects the false review status. Preserve these selections as coverage history, not evaluation, and apply a forward default-deny policy until B8 is decided.
- **Exact observed wording:**

> HOLDOUT documents took part in coverage-oriented selections, all before T0.4: the challenge set has 8 HOLDOUT documents (T0 documents it as overlapping and 'never an independent test set'); T0.1's 72-item manual-review queue has 26 HOLDOUT items, and the raw results labelled all 72 `MODEL_REVIEWED` by `gemini_assistant_model` with notes that only restate the detector's own fields (e.g. 'Model inspected: vector_grid=True, aligned_numeric_rows=1'); T0.1R re-labelled all 72 `NOT_REVIEWED` ('auto-relabelled from json snippet without model inspection'). The only Devanagari documents (2, one issuer) are both HOLDOUT (FIT 0, VALIDATION 0).

### P2-28 — meaning of `CLOSED_FOR_GOLD_PHASE`

- **Primary root:** RC5
- **Principal disposition:** ALREADY_RESOLVED
- **Resolution:** Keep the label scoped to its four closure conditions. Do not paraphrase it as “Gold protocol complete” or “B1-B8 resolved.”
- **Exact observed wording:**

> The decision is defined by four closure conditions (vector_text_route, sampling_cell_inspection, sampling_metadata_provenance, held_out_terminology); the closure itself lists two observations to settle 'before oracle annotation'. The post-closure register (B1-B8) later lists eight open items. The label is accurate for its four conditions.

## Register-level conclusion

There are no integrity blockers to beginning Phase 2.1. The principal P2 author-decision entries—P2-12, P2-16, P2-17, and P2-19—expand into the complete B1-B8 choice set that must be closed before Phase 2.1 can authorize downstream annotation or benchmarking. P2-07 and P2-26 remain empirical/historical unknowns and must not be converted into convenient assumptions.
