# Phase 2 root-cause and dependency map

## Classification method

The map assigns one primary root to each authoritative finding. A root is accepted only when it explains several observations without turning an unknown into a fact. For every root, the strongest alternative explanation, disconfirming evidence, falsifier, and cheapest useful test are stated explicitly.

## Coverage map

| Root | Findings assigned exactly once | Count |
|---|---|---:|
| RC1 — provenance and frozen-record overclaim | P2-01, P2-02, P2-14, P2-15, P2-20, P2-21, P2-22, P2-23, P2-24, P2-25 | 10 |
| RC2 — predicate namespace and denominator drift | P2-03, P2-04, P2-05, P2-06, P2-08, P2-09, P2-10, P2-13, P2-18 | 9 |
| RC3 — proxy/evidence ontology gap | P2-11, P2-12 | 2 |
| RC4 — routing and PDF-semantic contract gap | P2-07, P2-16, P2-17 | 3 |
| RC5 — Gold and evaluation interface gap | P2-19, P2-28 | 2 |
| RC6 — HOLDOUT semantics and historical-governance gap | P2-26, P2-27 | 2 |
| **Total** | **P2-01 through P2-28** | **28** |

## Root-by-root research-output crosswalk

This table supplies the required A-L view; the detailed sections below provide the arguments and the evidence matrix supplies source-level traceability.

| Root | A-C — problem, ARPipe evidence, existing research | D-H — external knowledge, solutions, applicability, limits, prior art | I-L — falsification, smallest action, decision impact, final status |
|---|---|---|---|
| RC1 | Later prose/hash tables overclaim exact byte, Git, or timing evidence. Phase-2 byte/object reproductions are sufficient; Phase-1 ancestry work remains useful but is contradicted on ten hashes/two-vs-eight attribution. | W3C PROV, Git docs, FIPS, and ACM vocabulary supply identity/provenance/reproducibility conventions. They apply directly to records, but cannot reconstruct absent history. Standards-based correction is prior art, not a contribution. | Falsified if recorded values resolve under a documented serialization. Smallest action: append-only correction ledger. Affects citation/reproduction, not extraction. **OBJECTIVE_CORRECTION**. |
| RC2 | Same names denote different predicates/units; deterministic overlap checks establish the problem. Existing T0.1R/Phase-2 work is sufficient to catalog it. | Parser/OCR docs and benchmarks reinforce representation/task distinctions; no external method can decide which historical predicate was intended. Naming/versioned predicate catalogs are ordinary engineering practice. | Falsified by a pre-existing normative crosswalk. Smallest action: freeze catalog and validator X0. Affects routing, sampling, reporting. **OBJECTIVE_CORRECTION**. |
| RC3 | Proxies remain labelled as proxies, but five evidence vocabularies and undefined `VALIDATED_METADATA` lack a crosswalk. Existing evidence is partly sufficient. | W3C PROV and annotation methodology support source/activity/agent and human-versus-derived distinctions. They are applicable as a profile, not a ready ARPipe vocabulary. | Falsified by an existing complete normative mapping. Smallest action: author-approved ontology plus X0 comprehension/validation. Affects every scientific claim. **AUTHOR_DECISION_REQUIRED**. |
| RC4 | Route taxonomy, detector kinds, production actions, and oracle labels are unreconciled. T0.4-LF is recommendation-only; genuine legacy remains unknown. | PDF standards, parser docs, OCRmyPDF, parser benchmarks, and legacy-font research define mechanisms/design alternatives. None establishes ARPipe prevalence or a winning hybrid policy. All candidate architectures have extensive prior art. | Changed by X1 verified encoding class or X2 preregistered arbitration gain. Smallest action first: static contract truth table and B1-B5 decisions. Affects Phase 4/5 and OCR selection. Principal status: **AUTHOR_DECISION_REQUIRED**; occurrence/performance remain subordinate empirical dependencies. |
| RC5 | T0.4 closed four checks, not Gold methodology; schemas omit essential units/provenance. The prior Gold package is strong but unadopted. | PAGE, relation-based reading order, span agreement, and annotation literature offer direct precedents. Transfer needs an ARPipe task/region/estimand choice; sophisticated auxiliary labels may not improve MD&A localization. | Changed by X4/X7 showing rules unusable or unnecessary. Smallest action: sign B4/B6/B7 and validate synthetic/calibration records. Affects annotation and benchmark validity. **AUTHOR_DECISION_REQUIRED**. |
| RC6 | Three “holdout” referents overlap historically; current issuer split is sound; pre-T0 exposure is unknown and no leakage path is shown. Existing forensic evidence is near the historical limit. | Grouped CV and leakage taxonomy support forward isolation and pathway-specific claims, not retrospective proof. Standard safeguards apply; they cannot manufacture absent logs. | Changed only by X6 concrete retained-log pathway. Smallest action: qualify names and sign the separate B8 policy. Affects final evaluation validity. Principal status: **UNRESOLVED**. |

## RC1 — provenance and frozen-record overclaim

**Principal status:** OBJECTIVE_CORRECTION.

**Working explanation.** Several later summaries copied prefixes, fetch-stage metadata, or post-closure questions into stronger “verified” statements without rechecking exact bytes, Git location, or historical timing. This explains the bad SHA, the ten wrong hash strings, the newline-dependent `audit_config` value, the two-to-eight attribution error, and the ambiguity around local-only records.

**Competing explanations.** Historical rewriting; missing Git objects; different PDF bytes; line-ending normalization; or two semantically identical JSON files being mistaken for byte-identical files.

**Strongest evidence against the working explanation.** The Phase-1 report performed extensive ancestry checks and correctly verified 17 of 27 displayed artifact hashes. Most lineage claims are sound, so the problem is not general carelessness or repository corruption.

**What would falsify it.** An exact recorded value resolving to a named historical blob or a demonstrated Git filter/serialization rule that reproduces every apparently wrong value from the cited object would move those entries from reporting overclaim to a documented identity convention.

**Cheapest useful test.** For each claim, record `(repository, commit, path, object type, Git blob ID, raw-byte SHA-256, serialization rule)`, then reproduce it with `git show`/`git hash-object --no-filters` and a byte hash. This is deterministic and requires no PDF processing.

**Phase-2.1 action.** Add an append-only correction ledger. Never “repair” the historical commit. State explicitly whether identity means raw file bytes, canonical JSON, a Git blob, or an external PDF SHA-256.

## RC2 — predicate namespace and denominator drift

**Principal status:** OBJECTIVE_CORRECTION.

**Working explanation.** Concepts were named for intended meaning (“native,” “scanned,” “multi-column,” “OCR layer”) while implementations evolved independently. Later reports reused the short names and mixed page predicates, document membership, detector classes, sampling strata, and representation classes.

**Competing explanations.** The differences could be intentional views of one latent concept rather than drift; a looser screen and a stricter confirmation predicate can legitimately coexist.

**Strongest evidence against the working explanation.** Some artifacts correctly state their local limitations, and P2-11 found no proxy-to-Gold promotion. Distinct predicates are not themselves defective if they are named and scoped.

**What would falsify it.** A frozen, versioned crosswalk predating the measurements that explicitly declares the variants, units, denominators, containment relations, and intended uses would show controlled multi-view design rather than drift. No such crosswalk was found.

**Cheapest useful test.** Mechanically enumerate each predicate's source expression and compute pairwise equality/subset/overlap on the existing frozen CSVs. This was already done for the Phase-2 findings; Phase 2.1 need only freeze the resulting catalog.

**Phase-2.1 action.** Give every predicate an immutable ID and fields for unit, denominator, source columns, exact expression, evidence status, intended use, and historical aliases. Report `pages_exhibiting_condition` separately from `pages_in_documents_with_condition`.

## RC3 — proxy/evidence ontology gap

**Principal status:** AUTHOR_DECISION_REQUIRED.

**Working explanation.** The project has local evidence labels but no common semantics. Undefined `VALIDATED_METADATA` and five vocabularies make it easy for readers to infer human validation from deterministic or inherited metadata.

**Competing explanations.** The local vocabularies may be adequate because each phase had a distinct purpose and the proxy labels were consistently cautious.

**Strongest evidence against the working explanation.** P2-11 is strong: all 17 T0.3A proxies remain `CANDIDATE_PROXY`, candidate rows remain `NOT_REVIEWED`, and no false promotion was found. The gap is interpretive risk, not observed label corruption.

**What would falsify it.** A normative existing document defining every status, source, verifier, unit, and allowed inference across phases would eliminate the need for a new crosswalk. None was located.

**Cheapest useful test.** Ask two informed readers to classify a small set of era, size, table, language, OCR-layer, and route values using only the frozen documentation. Disagreement on whether “validated” means byte-derived, source-confirmed, or human-reviewed would demonstrate the ambiguity. This is a protocol comprehension check, not Gold annotation.

**Phase-2.1 action.** Adopt explicit classes such as `SOURCE_METADATA`, `BYTE_VERIFIED`, `DETERMINISTIC_DERIVATION`, `CANDIDATE_PROXY`, `HUMAN_ANNOTATION`, `ADJUDICATED_GOLD`, and `UNKNOWN`, with provenance fields rather than status words alone.

## RC4 — routing and PDF-semantic contract gap

**Principal status:** AUTHOR_DECISION_REQUIRED.

**Working explanation.** Sampling taxonomy, detector kinds, production behavior, and proposed oracle labels were developed for different purposes but never reconciled. As a result, a non-produced `legacy_font` route coexists with actual `broken_text -> OCR`, hybrid prose differs from code, and blank behavior is implicit.

**Competing explanations.** The prose could describe intended future architecture while code represents an interim implementation; the apparent mismatch would then be planned rather than defective.

**Strongest evidence against the working explanation.** The actual digital/scanned/broken/vector route rows are internally consistent, and the T0.4-LF record explicitly says its one-class OCR option is only a recommendation. The gap is concentrated in unadopted or omitted cases.

**What would falsify it.** A frozen normative mapping that covers all six `PageKind` members, defines REMAP operationally, specifies overlaps and precedence, and identifies the implementation version would show the contract already exists. No such mapping was found.

**Cheapest useful test.** First perform a static truth-table review—no OCR—covering all detector kinds, proxy labels, representation classes, current code actions, oracle labels, and evidence allowed. Only then run the FIT-only legacy and hybrid experiments if authorized.

**Phase-2.1 action.** Decide B1, B2, B3, and B5 together. Do not derive route precedence from sampling priority. Keep “is genuine legacy encoding present?” separate from “what action should a suspicious page take?”

## RC5 — Gold and evaluation interface gap

**Principal status:** AUTHOR_DECISION_REQUIRED.

**Working explanation.** T0.4 closed four preregistration checks while deliberately leaving Gold implementation for later. Post-closure research specified useful principles but did not adopt schemas or author choices, leaving oracle validation, blinding, provenance, bbox, and reading-order units incomplete.

**Competing explanations.** Existing JSON fields may be sufficient for a pilot, with conventions supplied in annotator training rather than schemas.

**Strongest evidence against the working explanation.** The existing Gold-method research is substantial: it recommends independent raw annotations, separate adjudication, all-page PageGold text, structured DocumentGold spans, and a hybrid reliability sample. The project is not starting from zero.

**What would falsify it.** A versioned protocol and validator covering OracleRoute, PageGold, and DocumentGold—including blinding, evidence, bbox, reading-order unit, independent annotation, and adjudication—would mean the interface is complete. Those frozen artifacts do not exist at the base commit.

**Cheapest useful test.** Validate synthetic records and conduct a segregated FIT calibration after author choices, checking inter-annotator interpretation and schema rejection behavior. Do not annotate HOLDOUT or final Gold during protocol design.

**Phase-2.1 action.** Reuse the prior Gold research at commit `1c53c42`; close B4, B6, B7, and B8; then version both protocol and schema before any final labels.

## RC6 — HOLDOUT semantics and historical-governance gap

**Principal status:** UNRESOLVED.

**Working explanation.** The name “holdout” was reused for a legacy random queue, an external P-X1 partition, and the later issuer-disjoint T0 split. Retrospective prose then implied a stronger “unseen” history than the records prove.

**Competing explanations.** T0 HOLDOUT may in fact have been unseen by developers despite overlapping old queue membership, because membership alone does not establish that the documents were opened, labelled, or used for tuning.

**Strongest evidence against the working explanation.** No historical label maps to T0 HOLDOUT, all false model-review labels were corrected, and coverage selection is not evaluation. There is no demonstrated leakage pathway into a fitted model or chosen method.

**What would falsify it.** Complete pre-T0 access, execution, prompt, label, and tuning logs could establish either exposure or non-exposure. The frozen repository does not contain a complete record of that kind.

**Cheapest useful test.** Continue the metadata-only audit of commits, manifests, historical label hashes, and any independently retained access logs. Do not inspect HOLDOUT document content to answer a historical question. Stop when the available records are exhausted; absence of logs is not proof of absence.

**Phase-2.1 action.** Use qualified names (`LEGACY_RANDOM_HOLDOUT`, `PX1_HOLDOUT`, `T0_ISSUER_HOLDOUT`) and preserve `pre_T0_exposure = UNKNOWN`. Apply a forward default-deny policy until B8 is explicitly authorized.

## Cross-root causal graph

```text
RC1 exact provenance -----------+--------------------------+
                                |                          |
RC2 predicate contract ---------+--> RC4 route contract ---+--> RC5 Gold/evaluation contract
                                |                          |             |
RC3 evidence ontology ----------+--------------------------+             |
                                                                         v
RC6 HOLDOUT governance ----------------------------------------> annotation authorization
```

The graph expresses prerequisites, not implementation order alone. RC1-RC3 can be normalized objectively. RC4-RC6 contain author choices. No downstream schema should obscure an upstream ambiguity with a default value.

## Decision dependency register

| Downstream decision | Required upstream facts/choices | Must not be reused as a substitute |
|---|---|---|
| B1 route/class mapping | RC2 predicate IDs; RC3 evidence classes; genuine-legacy status marked unknown | Sampling strata; proxy name |
| B2 precedence | B1 class set; explicit overlap policy | `sampling_stratum_priority` |
| B3 oracle population | Purpose of oracle; representation and condition semantics | The phrase `native_clean_control` alone |
| B4 25% selection | Eligible-unit set; canonical serialization; independent domain key; threshold/tie rule | Per-cell `selection_rank` |
| B5 evidence policy | Whether labels describe visible action or PDF semantics | Rendered pixels for hidden PDF properties |
| B6 reliability design | Gold task/unit; workload; reporting purpose | Oracle route's 25% rule |
| B7 reading order | Atomic region definition; IDs; table policy; relation semantics | Engine blocks or unspecified strings |
| B8 HOLDOUT annotation | Final protocol/tool freeze; blinding; access log; permitted use | Historical “holdout” prose |

## Root-cause conclusion

The most economical explanation is six interacting contract/provenance gaps, not corrupted corpus bytes and not one defective detector. A semantic correction layer can repair future interpretation while preserving the historical record. Empirical execution becomes useful only after those contracts make its observations unambiguous.
