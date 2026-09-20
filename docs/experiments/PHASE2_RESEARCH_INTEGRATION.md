# ARPipe Phase 2 research integration

**Status:** research complete; decisions separated from recommendations<br>
**Research date:** 2026-09-21<br>
**Repository basis:** commit `13423c400d9236c1e25a3df6ea3ca20166befefa`<br>
**Scope:** integrate the 28 Phase-2 integrity findings, B1-B8, prior project research, and targeted external evidence before Phase 2.1<br>
**Non-execution boundary:** no PDF acquisition, OCR run, benchmark run, Gold annotation, corpus mutation, production-code change, or Phase-3 implementation was performed

## Executive conclusion

Phase 2 found no new evidence that invalidates the 194-document frozen corpus, the issuer-disjoint T0 split, or the decision to avoid acquisition. It did find that later reports sometimes gave the same word to different predicates, treated a proxy as if its name described what it measured, or described historical records more strongly than the Git and byte evidence permits. The dominant root cause is therefore **semantic-contract drift across artifacts**, compounded by incomplete Gold and routing interfaces. It is not a single detector defect.

Phase 2.1 can start without new OCR or annotation. Its first deliverable should be a versioned semantic contract and correction ledger: unique predicate names, explicit units and denominators, an evidence-status crosswalk, an exact source-of-truth rule for bytes and Git blobs, and a route/oracle/Gold interface whose unresolved choices remain visibly unresolved. The frozen T0-T0.4 artifacts should not be rewritten.

No external source justifies changing production behavior now. External evidence does strengthen three conclusions:

1. rendered appearance and PDF text semantics are different evidence channels, so a visual-only oracle cannot claim to diagnose `ToUnicode`, invisible-text, or font-encoding failure;
2. TOCs, outlines, font sizes, and extracted text are useful candidate signals but are not Gold by themselves; and
3. native extraction, whole-page OCR, and native/OCR merging are design alternatives whose value must be tested on ARPipe's own FIT material before an architecture choice.

## What is authoritative

The authoritative Phase-2 record is `PHASE2_FOUNDATION_INTEGRITY_FINDINGS.json`, supported by `PHASE2_FOUNDATION_INTEGRITY_AUDIT.md` and its read-only reproduction scripts. The Phase-1 verification report at commit `e52166f` is historical evidence, not an authority over reproduced bytes: P2-21 shows that 10 of its 27 displayed SHA-256 values are wrong despite being marked verified, and P2-22 shows that it attributed eight post-closure questions to a closure record containing two observations.

The integration artifacts are:

- [canonical problem register](PHASE2_RESEARCH_PROBLEM_REGISTER.md), preserving the exact observed wording and assigning one principal disposition to every P2 finding;
- [root-cause and dependency map](PHASE2_RESEARCH_ROOT_CAUSE_MAP.md), including competing explanations and falsifiers;
- [evidence and prior-art matrix](PHASE2_RESEARCH_EVIDENCE_MATRIX.md), covering existing project research, external sources, and novelty boundaries;
- [B1-B8 decision package](PHASE2_RESEARCH_B1_B8.md), separating facts, objective constraints, recommendations, and author choices;
- [proposed experiment register](PHASE2_RESEARCH_EXPERIMENTS.md), containing future tests only—none were executed.

## Root-cause synthesis

| Root | Primary findings | Synthesis | Phase-2.1 consequence |
|---|---|---|---|
| RC1 — provenance and frozen-record overclaim | P2-01, P2-02, P2-14, P2-15, P2-20-P2-25 | Some prose and hash tables outran the underlying byte/Git evidence. The underlying frozen objects remain recoverable. | Add an append-only correction ledger and exact byte-vs-Git identity rules; do not amend historical artifacts. |
| RC2 — predicate namespace and denominator drift | P2-03-P2-06, P2-08-P2-10, P2-13, P2-18 | Reused names hide different page/document predicates, and counts mix condition pages with pages of member documents. | Publish a predicate catalog with symbol, implementation, unit, denominator, evidence class, and lifecycle. |
| RC3 — proxy/evidence ontology gap | P2-11, P2-12 | Proxies were not actually promoted, but undefined status words and saturated signals invite overinterpretation. | Freeze a crosswalk that distinguishes measured metadata, deterministic derivation, candidate proxy, annotation, adjudicated Gold, and unknown. |
| RC4 — routing and PDF-semantic contract gap | P2-07, P2-16, P2-17 | Legacy/REMAP has seven names and no implementation; hybrid/blank behavior is incompletely specified; documentation and code differ. | Decide the contract before Gold labels or routing benchmarks. Keep legacy occurrence empirical and separate from route naming. |
| RC5 — Gold and evaluation interface gap | P2-19, P2-28 | Closure was valid for four named checks, not a completed Gold method. Oracle, provenance, blinding, bbox, and reading-order units remain incomplete. | Adopt a schema/versioning decision package before annotation. Reuse the prior Gold-method research rather than repeating it. |
| RC6 — HOLDOUT semantics and historical-governance gap | P2-26, P2-27 | Three historical meanings of “holdout” were conflated. Current T0 split integrity is demonstrable; pre-T0 exposure cannot be reconstructed completely. | Keep T0 HOLDOUT sealed for method choice. Record the historical limitation without alleging leakage that is not evidenced. |

Each P2 finding has exactly one primary root in the problem register. Cross-links are explanatory only and do not double-count findings.

## Decisions and dependencies

```text
append-only correction ledger (RC1) -----------+
predicate catalog + evidence ontology (RC2/3) -+--> routing/oracle contract (B1-B5)
                                                |          |
                                                |          +--> Gold schemas and protocol (B6-B7)
HOLDOUT authorization and history (RC6/B8) -----+--------------------+
                                                                           |
                                                                           v
                                                           final protocol/tool freeze
                                                                           |
                                                                           v
                                                          annotation / benchmark execution
```

The graph is intentionally one-way. Sampling priority is not routing precedence; the existing per-cell `selection_rank` is not a double-annotation rank; and a historical proxy name must not become a Gold label merely because a schema needs a value.

## What blocks Phase 2.1

Nothing blocks **starting** Phase 2.1. Most objective corrections can be drafted immediately from frozen evidence.

Closing Phase 2.1 and authorizing Gold creation does require recorded author decisions for B1-B8 and for the evidence-status vocabulary. In particular, route labels, the oracle population, independent double-annotation selection, allowed evidence, general overlap design, reading-order units, and HOLDOUT authorization cannot be silently selected by an implementation agent.

Two unknowns need not block semantic normalization:

- whether genuine legacy-font encoding failures occur in this corpus; and
- whether any T0 HOLDOUT documents were processed before the T0 split existed.

The first is a future FIT-only forensic question. The second may remain historically unresolvable; current controls should address forward use rather than manufacture proof of non-exposure.

## Objective corrections versus author choices

Objective corrections are limited to statements mechanically fixed by the record: the T0.1R SHA typo; predicate definitions and counts; units/denominators; the `audit_config` hash/newline explanation; the Phase-1 hash-table correction; the two-versus-eight closure attribution; and the fact that hybrid/blank are absent from T0.4 routing classes. These can be entered in a correction ledger without scientific discretion.

Author choices include: evidence-status names; whether legacy and broken-text are one route or two; the intended oracle subset; double-annotation rank serialization and domain key; permissible annotation evidence; PageGold/DocumentGold reliability design; reading-order unit; and HOLDOUT annotation authorization. The B1-B8 report gives recommendations, but labels them as recommendations rather than adopted policy.

## Evidence-bounded answers to the central research questions

### Is a separate legacy-font route justified?

Not yet. The corpus contains three incompatible legacy-candidate operationalizations, none of which verifies an encoding defect. External work shows that legacy-font PDFs can fail Unicode extraction while rendering correctly, but that establishes possibility, not occurrence in ARPipe. Keep legacy-font occurrence as an empirical question. The smallest test is FIT-only inspection of font dictionaries, `ToUnicode` mappings, extracted code points, and rendered text on a predeclared candidate sample.

### Can a rendered image distinguish NATIVE from LEGACY?

No, not when the distinction is defined by hidden PDF state or extracted character mapping. ISO 32000 separates text rendering from character-to-Unicode mapping, and visible rendering may remain correct when machine extraction fails. A visual annotator can label an action such as “image is readable without OCR” or “OCR is needed for visible content”; that annotator cannot establish the PDF's text-layer semantics from pixels alone.

### Should TOC or outline data define MD&A Gold?

No. It may generate candidates, provide a navigation prior, or help an annotator locate visible headings. Prior systems do use TOCs, typography, and hierarchy to segment reports, but those signals may be missing, noisy, or derived from the same source being evaluated. ARPipe's own TOC and annexure keyword proxies are near-saturated. Final page spans must be grounded in the visible document and a written MD&A inclusion/exclusion protocol.

### Which hybrid strategy should ARPipe adopt?

The evidence supports a design space, not a winner: native-only, OCR-only, region merge, page/block arbitration, and visual-first recovery. Whole-page OCR can discard vector/tag structure and degrade correct native text; native-only extraction misses scans and broken mappings; merging introduces duplication and order conflicts. Run the FIT-only hybrid pilot specified in the experiment register before architecture work. No production change is warranted in Phase 2.

### Does the historical holdout overlap prove leakage?

No. It proves that the word “holdout” referred to different partitions and that old queues overlap the later T0 split. No historical labels map to a T0 HOLDOUT document, while pre-T0 processing exposure is not established either way. The correct statement is **historical exposure unknown, no leakage pathway demonstrated**. Current HOLDOUT use should remain default-deny until B8 is resolved.

## Prior-art and novelty conclusion

ARPipe should make no “first,” “novel,” or state-of-the-art claim from this research. Closest work already covers financial-report section extraction, document hierarchy, relation-based reading order, layout annotation, OCR/PDF parser comparison, and double-annotation methodology. No searched source directly evaluates MD&A page-span localization across the frozen Indian annual-report corpus and ARPipe routing conditions, but failure to find an exact match is not proof of novelty.

At most, the following are **potentially differentiated and unvalidated**:

- the application population: Indian annual-report MD&A across FY2010-2025;
- the evaluation combination: representation-aware routing plus document-level MD&A span metrics under issuer-disjoint splits; and
- the integration discipline: explicit proxy/provenance/Gold contracts attached to a frozen corpus.

These are dataset/evaluation/engineering distinctions, not evidence of a new algorithm or scientific method. The evidence matrix records directly implemented, partially transferable, inspiration-only, and contradicted assumptions.

## Recommended Phase-2.1 order

1. Create an append-only correction ledger for the objective items; leave historical frozen files intact.
2. Freeze the predicate catalog and evidence-status crosswalk.
3. Record B1-B5 author decisions and update the route/oracle contract on paper.
4. Record B6-B8 decisions and finish versioned Gold schemas, blinding, bbox, reading-order, and provenance rules.
5. Validate schemas and selectors on synthetic or segregated FIT calibration records.
6. Only after those gates, separately authorize any FIT experiment, Gold annotation, or benchmark execution.

## Final readiness statement

**READY FOR PHASE 2.1 CONTRACT NORMALIZATION; NOT READY FOR GOLD COLLECTION OR BENCHMARK EXECUTION.**

The frozen foundation remains usable with documented corrections. Phase 2.1 should normalize meaning and obtain author choices, not tune extraction, inspect HOLDOUT content, or execute the preregistered benchmark.

## Required final synthesis

1. **What problems are real?** Exact hash/citation errors, predicate/name/denominator collisions, an undefined evidence crosswalk, incomplete route coverage, incomplete Gold interfaces, and ambiguous historical HOLDOUT terminology are all reproduced. The corpus bytes and current split are not shown to be corrupt.
2. **Which are documentation/provenance problems?** P2-01, P2-02, P2-14, P2-15, and P2-20-P2-25 primarily require correction records, scoped wording, or prerequisite notes rather than pipeline changes.
3. **Which are symptoms of larger semantic problems?** P2-03-P2-10, P2-13, and P2-18 share predicate/unit drift; P2-07/P2-16/P2-17 share the route/PDF-semantic gap; P2-19/P2-28 share incomplete Gold-scope interpretation.
4. **What is already sufficiently researched?** Frozen lineage and bytes, predicate overlaps/counts, structural zero cells, current route behavior, proxy non-promotion, the provenance errors, and core Gold design principles. Repeating broad reviews of these topics would add little.
5. **What genuinely needed external research?** PDF evidence-channel limits, hybrid extraction tradeoffs, TOC/hierarchy prior art, reading-order representations, annotation agreement, leakage taxonomy, provenance standards, and the closest financial-section prior art. This targeted review is now sufficient for Phase 2.1 decisions; it does not answer corpus-specific performance.
6. **What can be corrected deterministically?** The SHA typo; hash/newline and Phase-1 tables; two-versus-eight attribution; exact predicate definitions/names; page/document denominators; structural-zero interpretation; and actual-vs-proposed route descriptions.
7. **What requires explicit author decisions?** The evidence ontology and all B1-B8 contract choices: route set/precedence, oracle population, independent rank bytes/key, allowed evidence, reliability design, reading-order unit, and HOLDOUT authorization.
8. **What requires empirical experiments?** Genuine legacy occurrence/detectability, hybrid policy performance, TOC/outline incremental utility, tool/protocol usability, MD&A boundary ambiguity, and—if retained logs exist—specific historical exposure pathways.
9. **What blocks Phase 2.1?** Nothing blocks starting normalization. Closing it for downstream execution requires the blocking predicate/evidence corrections and signed B1-B8 decisions. X1/X2 performance results need not block contract normalization when their values remain explicitly unknown.
10. **What should not change?** T0-T0.4 history, corpus PDFs/manifests, the 194-document freeze, the 92/48/54 issuer split, no-acquisition decision, proxy labels, current production behavior, or HOLDOUT membership/use.
11. **What should not be researched again?** Another generic legacy Architecture A/B/C debate; another broad Gold-method review; another proof that the frozen sampling is deterministic; or another claim-level lineage audit without new evidence. Use the existing T0.4-LF, Gold package, and Phase-2 reproductions.
12. **What is the minimum next measurement?** No measurement is needed for the first Phase-2.1 correction ledger and semantic catalog. After author decisions, the first empirical action should be X1's small FIT-only, no-OCR legacy forensic test; X4's segregated FIT protocol calibration is the minimum before final Gold. Hybrid OCR X2 comes later under separate authorization.
