# Phase 3 / P1 — Claims and scope research

**Status: PROPOSED decision package; AUTHOR DECISION REQUIRED. Nothing is adopted.**

**Date:** 2026-09-23. **START_SHA / completed P0b:** `24520ce623037fde7c3b0a9d0d4e5f8fc5618831`. **Starting parent:** `a45a6406b9f30e0822d847c2df289652f6ca83b8`.

## Starting-state receipt

**REPO-VERIFIED.** Worktree `D:\sem_iitk\sem9\thesis\sep_week1\phase3-claims-scope`, branch `phase3-claims-scope`, created from the command-derived HEAD of the clean `arpipe-phase2.1-foundation-normalization` worktree. The outer thesis repository is a different repository and was not used as the ARPipe base.

Commands after creation returned:

```text
git rev-parse HEAD
24520ce623037fde7c3b0a9d0d4e5f8fc5618831
git rev-parse HEAD^
a45a6406b9f30e0822d847c2df289652f6ca83b8
git status --short --branch
## phase3-claims-scope
git log -1 --oneline --decorate
24520ce (HEAD -> phase3-claims-scope, phase2.1-foundation-normalization) test(experiments): add Phase 2.1 P0b hash-lint tooling and tests
```

**REPO-VERIFIED.** `git rev-parse --show-toplevel` returned the worktree above. The working tree was clean; `git diff --name-only HEAD -- arpipe/ dataset/ configs/t0_4/ artifacts/t0_4/` was empty. The starting commit's inspected subject, diff and ancestry identify completed P0b, including the hash checker and its tests. No P0b work is repeated or changed.

## Evidence conventions

Each substantive paragraph/table row inherits its explicit label. **REPO-VERIFIED** means repository evidence was inspected, not that historical measurements were rerun. **SOURCED** means the external source was opened in P1. **VERIFIED** is reserved for command-reproduced arithmetic/checks. **INFERRED**, **PROPOSED**, **AUTHOR DECISION REQUIRED**, **EXPERIMENT REQUIRED**, **UNRESOLVED**, and **HISTORICAL / NOT CURRENTLY REPRODUCIBLE** preserve the distinction between evidence and decisions. Missing artifacts are **UNRESOLVED — UNVERIFIED**. Planning quantities are assumptions/estimates, not measured corpus outcomes.

## Research-coverage audit — recorded before new external research

| Question | Already established | Evidence quality | Remaining gap | New research required? |
|---|---|---|---|---|
| Q1 thesis role | Existing work supports an extraction infrastructure task; no validated methods advantage or downstream validity result | REPO-VERIFIED: Phase 2 integration, Gold decision memo | Author objective and proportionate evidence burden | INFERRED: planning synthesis; no broad review |
| Q2 claims | Document span and page text/structure endpoints; unresolved routing and Gold contracts | REPO-VERIFIED: metric/oracle specs, B register | Complete claim-to-estimand chain, falsifiers and denominators | PROPOSED claim drafting; reuse evidence |
| Q3 population | Availability-conditioned corpus; issuer-disjoint partitions; proxies differ from truth | REPO-VERIFIED: freeze construction, audit V07/V08, normalization | Target, selection probabilities, scope versus weights | INFERRED estimand algebra and frame audit |
| Q4 downstream | Extraction fidelity not demonstrated; prior research does not validate climate score | REPO-VERIFIED: integration and experiments | When error matters for score or regression claims | Narrow financial text-measurement sources needed |
| Q5 regulation | Earlier LODR context does not establish historical applicability or page boundaries | REPO-VERIFIED: Phase 2 E13 and Gold MD&A memo | Official s.134, Reg.34/Schedule V, clause 49, BRR/BRSR eras | Targeted official provisions needed |
| Q6 baseline | Multiple snapshots; recovery was not canonical; P0b is a docs/testing base | REPO-VERIFIED: worktree/history and provenance | Code/config/prompt differences and intended As-Is identity | Repository inspection needed; external sources cannot choose |
| Q7 precision | Document endpoint, issuer clustering, unresolved Gold reliability design | REPO-VERIFIED: metric spec and B6 | Small clusters, imbalance, missed spans, effort | Hypothetical arithmetic plus narrow statistical sources needed |
| Q8 missing PDFs | Missing historical bytes differ from executable documents | REPO-VERIFIED: PC-04 and P2-15 | Claim-dependent denominator/acquisition triggers | PROPOSED decision rule; no acquisition/research needed |
| Q9 prior art | Financial itemization, hierarchy, layout, annotation, legacy already reviewed | REPO-VERIFIED: Phase 2 matrix and Gold register/memos | Reopen retained citations; FinTOC and Indian AR/BRSR task gaps; citation identity | Targeted verification and gap closure only |

**REPO-VERIFIED.** LF report, stored results, truth and scripts add synthetic mechanism constraints, not real-corpus prevalence. Q10 checks and Q11 dependencies use inspected project evidence rather than another research cycle.

## Executive summary

**INFERRED / PROPOSED.** The strongest proportionate planning position is ARPipe as explicitly scoped extraction infrastructure, with a methods claim only if an identifiable comparator and independent paired evaluation justify it. This is a recommendation for author consideration, not the thesis role or claim selection. Neither extraction accuracy nor downstream climate validity is established by P1. The five candidate claims are C1 corpus-bound localization description, C2 paired improvement, C3 routing contribution, C4 downstream stability, and C5 an intentionally narrower case-study aid. Their complete chains and falsifiers are in the [claim matrix](PHASE3_CLAIM_EVIDENCE_MATRIX.md).

**REPO-VERIFIED / UNRESOLVED.** P0b is the correct documentation starting state, but its inherited production files are not a coherent automatically acceptable As-Is comparator. Oracle page labels do not presently define a document-level intervention. Legacy coverage is incomplete by construction and by synthetic counterexample. Historical HOLDOUT exposure remains UNKNOWN. These limit claims; none authorizes changing the frozen Master Flow or B register.

**PROPOSED.** The [decision sheet](PHASE3_DECISION_SHEET.md) leaves every AUTHOR CHOICE blank. The [impact map](PHASE3_B1_B8_IMPACT.md) distinguishes claim-specific dependencies from mandatory author ratification under the existing flow. The [population and sampling analysis](PHASE3_POPULATION_SAMPLING.md) contains reproducible planning arithmetic and the missing-PDF decision rule. No thresholds, sampling targets or decisions are frozen here.

## Evidence inventory and unresolved artifact identity

All current repository references in this section are **REPO-VERIFIED** at START_SHA unless another revision is explicit. They support what the documents/code contain; historical results retain their original limitations.

| Evidence inspected | Use and limitation |
|---|---|
| `docs/experiments/PHASE2_FOUNDATION_INTEGRITY_AUDIT.md`; `PHASE2_FOUNDATION_INTEGRITY_FINDINGS.json` | Audit findings, denominators, unresolved interpretation; no rerun of corpus/Oracle/HOLDOUT analysis. |
| `PHASE2_RESEARCH_INTEGRATION.md`, `PHASE2_RESEARCH_EVIDENCE_MATRIX.md`, `PHASE2_RESEARCH_B1_B8.md`, `PHASE2_RESEARCH_EXPERIMENTS.md` | Completed research baseline, contradiction register and future experiments. Their cited sources are not automatically SOURCED in P1. |
| `PHASE2.1_FOUNDATION_NORMALIZATION.md`, `PHASE2.1_FOUNDATION_SEMANTIC_MAP.md`, `PHASE2.1_PROVENANCE_CORRECTIONS.md`, `PHASE2.1_CLOSEOUT.md`, `PHASE2.1_B1_B8_DECISION_REGISTER.md` | Normalized facts and pending decisions; no amendments. |
| `configs/t0_4/metrics_spec.json`, `oracle_routing_spec.json`, `gold_schema.json`; `tools/t0_4/core.py`; production triage/models/pipeline | Endpoint units, detector aliases and current executable structure. Config registration is not validation. |
| `dataset/corpus_freeze/freeze_protocol.md`, `stratification_report.md`; `tools/freeze_extraction_corpus.py` | Construction and published aggregate coverage only. No HOLDOUT document, unit roster, PDF or output opened. |
| Historical Gold research at `1c53c42129b68259698143b6c13bc2d0d073fbf6`, including `docs/experiments/T0.4-GOLD-METHOD-DECISION-MEMO.md`, MD&A research and `research_source_register.csv` | Prior annotation/boundary research reused; recommendations remain proposals. Routing clarification history also inspected. |
| E0, main, P-M1 and separate Step0A histories and recovery receipts | Baseline comparison below. No recovery snapshot promoted to canonical. |
| Local LF suite at `D:\sem_iitk\sem9\thesis\sep_week2\lf_fixture_suite` | `20_LF_B1B8_TARGETED_GAP_RESEARCH.md`, stored results, truth, build/evaluation scripts and font metadata inspected read-only. Synthetic evidence only. |
| Supplied Master Flow; `18_ROADMAP.md`; `17_B1_B8_DECISION_SHEET.md`; consolidated readiness report | **UNRESOLVED — UNVERIFIED / NOT PRESENT IN WORKTREE.** Named files not located in the searched local project documentation. Author clarified they were supplied as task/project context: that context is authoritative. No reconstructed document or invented repository path. |

**REPO-VERIFIED.** P0b added documentation hash checking and tests. No actual hash-lint defect was found; no tooling change is made. An overbroad historical statement that routing has “no precedence” needs interpretation: the code has ordered branches; what is unresolved is an author-ratified routing contract. Sampling priority is not execution precedence.

## New gap-closure findings only

**REPO-VERIFIED / INFERRED.** The baseline comparison separates a documentation base, a saved later implementation and a curated unadopted candidate. Treating them as interchangeable would change the scientific comparator. Static incompatibilities in START predate P1 and do not invalidate its authorized P0b documentation ancestry.

**REPO-VERIFIED / UNRESOLVED.** The LF bundle has a truth/results/build coverage discrepancy and an unavailable reported code revision. Its synthetic examples constrain universal claims, but the delivered bundle is not evidence of a newly reproduced complete suite or real-corpus mechanism prevalence.

**SOURCED / INFERRED.** Targeted source checks distinguish Indian MD&A placement from substantive report contents and distinguish named-section localization from heading/layout/text-classification tasks. They support narrower boundary and prior-art wording, not national representativeness or a novelty claim.

**VERIFIED arithmetic / INFERRED assumptions.** Precision depends on issuer count, issuer imbalance, within-issuer dependence, endpoint variance and missed spans. The supporting document reproduces a sensitivity grid; no universal document count or approved Gold size follows.

## Q1: thesis role and proportionate rigor

All effort figures below are **AUTHOR-EFFORT ESTIMATE — planning estimate, not measured fact**. A researcher-day means concentrated author work, excluding waiting for an independent annotator, API/compute queues and acquisition. Ranges assume accessible FIT references, familiar tooling and no major runtime repair. They are rough end-to-end incremental evaluation effort; do not add the smaller decision-sheet planning estimates to them.

| Role option | Expected examiner-facing evidence / rigor | Effort estimate and dependencies | Implications for existing flow, conditional on author approval |
|---|---|---|---|
| A: infrastructure for the climate measure | Reproducible identity, MD&A definition, denominator accounting, independent span checks; text/score sensitivity if substantive climate conclusions depend on extraction | 10–20 researcher-days plus independent annotation; coherent system, B6, B8 if final evidence, fixed climate recipe for C4 | Detailed route ablations, exhaustive engine rankings, full reading-order Gold and REMAP are unnecessary for a span-only C1/C5. C4 makes downstream checks necessary. Span accuracy alone is insufficient evidence for score/regression validity. |
| B: methods contribution | Clearly specified intervention/comparator, paired independent evaluation, reliable references, uncertainty and relevant task-matched prior art; mechanism attribution only with valid intervention | 20–40 days plus annotation/compute; baseline identity, B6/B8 and route-dependent B1–B5 if C3 pursued | A general OCR benchmark can be excessive if only localization changes. A routing effect requires the missing Oracle transformation. Neither synthetic LF cases nor a code delta alone establishes methods advantage. |
| C: both infrastructure and methods | All necessary parts of paired methods validation plus downstream error sensitivity; two distinct estimands, not one score standing for both | 30–60 days plus annotation/compute; dependencies of both roles and a frozen downstream model | Existing extraction checks are insufficient for substantive regression robustness. Broadening every optional track is unnecessary; preserve only evidence required by selected claims. |

**PROPOSED recommendation.** Prefer infrastructure with C1 and a clearly bounded C5 fallback; add C2 only when As-Is identity and a substantive paired comparison are feasible. Select C4 if the thesis asserts extraction-induced score or regression stability. Confidence is moderate because thesis priorities, annotator access and runtime readiness are unresolved. Evidence changing this recommendation: a mandatory methodological thesis objective, a coherent attributable baseline, a large repeatable FIT improvement, or demonstrated downstream sensitivity making the infrastructure burden substantial. These are planning implications, not changes to the frozen Master Flow. Its exact local text remains UNVERIFIED.

## Q2/Q3: claims and scope

**PROPOSED.** The [matrix](PHASE3_CLAIM_EVIDENCE_MATRIX.md) gives exact wording, target, estimand, unit, numerator, denominator, exclusions and their timing, evidence, Gold, metric, uncertainty, sample implication, producing phase, supporting result, falsifier and B dependencies for each C1–C5. C1 is an honest description, so poor accuracy defeats a usefulness interpretation rather than a correctly reported low result. C2 and C4 require prospective success criteria; P1 chooses none. C3 is currently **CLAIM NOT YET SUPPORTABLE**. C5 makes no population accuracy or untouched-test claim.

**REPO-VERIFIED / INFERRED.** The frozen available-byte corpus is availability- and selection-conditioned, not a random sample of Indian companies. The published aggregate count of 194 documents / 36 issuers is not a national sampling frame. The [supporting analysis](PHASE3_POPULATION_SAMPLING.md) separates target population, operational frame, observed corpus, Gold sample and final population, with provenance for every project count. The observed fiscal-year set is discontinuous. Document weighting, equal-issuer weighting and a chosen year mix answer different questions; none recovers missing population support without selection evidence. Explicit scope is the recommended planning approach, not an adopted population.

## Q4: downstream sensitivity

**SOURCED.** Loughran and McDonald show that financial text measures can change materially with domain-appropriate word definitions; their opened publisher abstract supports caution about measurement validity, not the magnitude of ARPipe boundary/OCR error or a particular climate dictionary. [R01](https://doi.org/10.1111/j.1540-6261.2010.01625.x)

**INFERRED.** Wrong section boundaries can add unrelated governance/BRSR text or omit climate passages; corrupted text can change matching on a correct span. Missed documents can select the financial panel. Such error may covary with issuer, year or report quality; neither classical random error nor simple attenuation is established. Good page overlap does not guarantee an unchanged sparse climate score, and unchanged aggregate score does not guarantee stable regression conclusions.

| Claim | PROPOSED classification | Reason |
|---|---|---|
| C1 | USEFUL BUT OPTIONAL | Independent localization description alone does not assert downstream validity. Becomes REQUIRED if used to justify climate scores. |
| C2 | USEFUL BUT OPTIONAL | Localizer improvement is measurable without a downstream model; becomes REQUIRED for a downstream-benefit extension. |
| C3 | USEFUL BUT OPTIONAL | A valid routing effect on a declared extraction metric suffices for its narrow wording; score attribution adds C4 obligations. |
| C4 | REQUIRED | Score/regression stability is the claim itself. |
| C5 | UNNECESSARY UNDER NARROWER CLAIMS | Enumerated-case extraction aid carries no score validity assertion. |

**PROPOSED minimum future experiment for C4 — EXPERIMENT REQUIRED.** On an independently reviewed, prospectively selected subset of the declared financial-analysis population, keep the text-measure recipe fixed and compare: original extraction; corrected boundaries with the same extraction method; corrected text within the chosen reference span; and both corrections. Preserve missed-span and missing-score cases in coverage accounting. This separates section-selection and text corruption effects as far as the paired design permits. Report document score changes, issuer/year concentration and rank/coverage changes. A fixed downstream regression is rerun only if regression robustness is claimed, using the identical outcome/covariates/eligible panel and separately reporting panel changes. Predeclare substantive tolerances later; favorable sign alone is insufficient. Plausible boundary perturbations can supplement observed-error corrections but cannot substitute for them. No experiment, scoring, regression or reference annotation occurs in P1.

## Q5: official regulatory evidence for future boundary rules

Each regulatory row is **SOURCED**; its boundary implication is **INFERRED**, not a Gold rule. Exact issuer applicability still depends on listing category, financial year and, where relevant, size ranking. A consolidated law's current text must not be backdated to every report.

| Source / exact provision | Applicable period established by opened evidence | Implication for ARPipe boundaries |
|---|---|---|
| [R03: Companies Act 2013 s.134(3), (6), (7)](https://www.incometaxindia.gov.in/w/section-134-81) | 2013 Act regime; [R04 MCA General Circular 8/2014](https://www.incometaxindia.gov.in/hi/w/appendix-iii) distinguishes financial years commencing before versus on/after 1 April 2014 | Board report accompanies financial statements and can have annexures. Section 134 does not itself establish a uniquely titled, fixed-page MD&A section. A generic “annexure” or Board-report heading cannot alone end/start MD&A. |
| [R05: Clause 49, Annexure I IV(F)(i), 2004 circular](https://www.sebi.gov.in/sebi_data/attachdocs/1293168356651.pdf) | Pre-LODR listing-agreement lineage, subject to then-applicable issuer requirements/amendments | MD&A can be part of directors' report or an addition, with specified discussion themes. Avoid imposing a separate-section layout on earlier reports. This source is not a complete issuer-specific compliance history. |
| [R06: LODR 2015 Reg.34(2)(e), 34(3), Schedule V B](https://www.sebi.gov.in/sebi_data/attachdocs/1441284401427.pdf) | 2015 regulations; Reg.1 commencement provisions. Opened early consolidation includes later-2015 amendments, not a claim of pristine original gazette text | MD&A placement may be within directors' report or additional. Schedule V states topics, not physical page delimiters. Substantive overlap with other report sections does not merge them into MD&A. |
| [R09: Schedule V B(1)(i),(j), footnote 696](https://www.sebi.gov.in/sebi_data/attachdocs/dec-2025/1766551151465.pdf) | Footnote identifies 2018 amendment effective 1 April 2019; opened December 2025 consolidation used only for this annotated history | Financial-ratio-change and return-on-net-worth discussion can belong inside MD&A; a ratio table is not automatically the section end. Do not impose these later contents on earlier FY reports. |
| [R07: BRSR circular 10 May 2021, paras 2, 7](https://www.sebi.gov.in/sebi_data/attachdocs/may-2021/1620655793598.pdf) | Voluntary FY2021–22; mandatory for top 1,000 listed companies by market capitalization from FY2022–23, replacing BRR | Distinguish BRSR/BRR from MD&A even when themes overlap. Actual sampled-issuer applicability has not been determined. A BRSR heading is evidence of another section, not a universal delimiter absent layout context. |
| [R08: circular 28 March 2025, paras 3.1–3.2, 3.6, 3.12–3.13](https://www.sebi.gov.in/sebi_data/attachdocs/mar-2025/1743159419610.pdf) | Green-credit disclosure voluntary from FY2024–25; BRSR Core assessment/assurance phased by size; value-chain disclosure voluntary from FY2025–26 and its assessment/assurance from FY2026–27 | These alter sustainability disclosures, not an MD&A physical boundary mandate. Do not backdate later requirements or infer all observed reports contain comparable BRSR sections. |

**PROPOSED.** Future Gold Method should use visible heading hierarchy, continuation pages and substantive section ownership, allowing MD&A as a Board-report annexure or embedded section. Decide front-matter contents entries, signed endings, mixed transition pages, multi-span cases and admissible ambiguity independently of predictions. Law supplies context, not per-document Gold. The relevant observed FY eras and incomplete yearly coverage are in the sampling document. No broad corporate-law review or issuer compliance audit is needed for P1.

## Q6: As-Is baseline identity audit

**REPO-VERIFIED.** All revisions below were obtained from Git output and inspected read-only. Full hashes identify the evidence, not an adopted baseline.

| Candidate / actual revision | Contents and differences | Scientific / reproducibility consequence; intended As-Is? |
|---|---|---|
| main: `0fb8cbf6d932f4190bdfe3b2a1fecf62170cca14` | Earlier P33 implementation; lacks later script-map/quarantine pipeline additions | A pre-change comparator is possible only if that is the author's intended historical system. It is not the later saved live implementation. Runtime equivalence untested. |
| P-M1 / pm1-canonical: `c9d71bb127fcc46d690a8fbd9e5088b7049b6c05` | Pipeline changes include behavior as well as telemetry, but dependent model/OCR/store additions are absent | Mixed snapshot, not a purely diagnostic patch. Incoherent execution contracts make direct evaluation inappropriate without later authorized identity resolution. |
| Completed P0b / START: `24520ce623037fde7c3b0a9d0d4e5f8fc5618831` | Correct documentation/testing base; inherits the mixed production contracts below | P0b completion does not certify pipeline executability. Do not silently designate the documentation base as the scientific baseline. |
| E0 saved checkout: `e8517ee57365fc0799052d696f851fc25906a6b5` | Saved later implementation includes counterpart models/triage/OCR/store; additional body-script/segmentation handling and configuration changes | More complete representation of the saved later system, but changes affect behavior. Candidate if “As-Is” means this saved state; author intent and runtime evidence remain unresolved. |
| Separate `arpipe-step0a-candidate`: `0d39395dfb81c987e05546471fbb80947c8fdce8` | Clean curated candidate based on main; selected OCR preflight/quarantine changes, earlier triage/segment behavior, different pipeline/verify | A constructed candidate, not automatically the original live system. Recovery receipt says no accepted canonical SHA. |
| Step0A recovery/snapshot; Step0B recovery receipts | Step0A halted after external FETCH_HEAD change; accepted canonical SHA null. Step0B candidate_created false and canonical SHA null | No additional author-adopted baseline exists in these receipts. Not interchangeable with the separate clean candidate. |
| R1 fetch-telemetry work | Static difference from main is fetch/CLI/telemetry/test related | Fetch provenance experiment is not evidence of an author-selected extraction baseline. |
| Referenced P-X1 external snapshot; LF report revision `52ff2fe` | Referenced external snapshot not recovered as current evidence; Git could not resolve the LF revision | **UNRESOLVED — UNVERIFIED / REPOSITORY EVIDENCE NOT AVAILABLE.** Do not invent code or historical runtime identity. No fetch performed. |

**REPO-VERIFIED static defect evidence.** At START, `arpipe/pipeline.py:167` accesses `profile.script_map`, absent from its `DocProfile`; line 385 references absent `Confidence.QUARANTINE`; line 392 passes unsupported `write_span` to `store.write_year`; line 396 references absent `ocr_mod.OcrEngineUnavailable`. E0 has the same pipeline content but provides those counterparts. Step0A has quarantine/error/store counterparts and omits the script-map call. These are inspected interface conflicts, not a baseline execution result. No repair is made.

**REPO-VERIFIED config/prompt/dependency comparison.** Main, P-M1, START and E0 share `arpipe/config.py` and `requirements.txt` content. Main/P-M1/START default YAML agrees; E0 and Step0A add wrong-language-related configuration. Main/P-M1/START segmentation agrees; E0 segmentation differs. The inspected segment LLM prompt and VLM transcription prompt are unchanged across main/START/E0; method changes therefore cannot be dismissed as prompt changes alone. Optional segment LLM is disabled by default and uses alias `claude-sonnet`; Tesseract uses configured English/Hindi languages, VLM points to `PaddlePaddle/PaddleOCR-VL` with configurable service endpoint, and Textract is another supported engine. These are static defaults, not proof of the engine/model used in any historical run. CLI/environment overrides, model revisions, external binaries and package versions need an eventual run manifest. Dependency lower bounds do not constitute a locked environment.

**REPO-VERIFIED working-state distinction.** The inspected E0 checkout had tracked edits in `docs/experiments/E0_CLOSURE.md` and `E0_REPOSITORY_SAFETY.md`, plus untracked dataset/run/scratch directories; it was not globally clean. No tracked production-code dirty change was shown by status. Those untracked data/run contents were not used as evidence. The Step0A candidate was clean. P1 worktree started clean. Post-freeze production differences are historical candidate differences, not P1 changes.

**PROPOSED recommendation / confidence.** First ratify the intended historical meaning of “As-Is.” If it means the saved later state, E0 is the leading candidate for a later explicit freeze and attributable readiness check; if it means the pre-change implementation, main answers a different legitimate comparison. Confidence is high in static differences, moderate in relative suitability, and unresolved for exact historical reproducibility. **WHAT EVIDENCE WOULD CHANGE THIS:** author definition/timestamp; contemporaneous command/config/runtime logs; full dependency and model pinning; independently attributable functional checks in a later authorized stage; an available missing snapshot establishing a different canonical identity. No candidate is adopted and no baseline is run in P1.

## Q7/Q8: precision and missing documents

**PROPOSED.** The [sampling analysis](PHASE3_POPULATION_SAMPLING.md) is the complete Q7/Q8 record: document and issuer counts are separate; pages are nested; issuer imbalance, endpoint performance, interval width, tIoU dispersion and missed spans vary in the planning grid. Nine final issuers can support bounded descriptive reporting, but not a promised precise population or small-effect claim. FIT/VALIDATION Gold adequacy depends on reference design and purpose, not roster size alone. Formal sample selection remains Gold Method work.

**PROPOSED / AUTHOR DECISION REQUIRED.** The 14 missing historical PDFs remain outside the current executable available-byte denominator. Their importance is claim-dependent: panel completeness or reproduction of historical inputs can trigger bounded future acquisition; a present-byte localization or case-study claim need not. The supporting decision rule considers each claim, validation, Gold and final evaluation separately. Nothing is acquired or silently reclassified.

## Q9: targeted prior-art audit

Every row is **SOURCED** to the opened primary text or explicitly identified model card; ARPipe relevance is **INFERRED**. Counts and performance scores are deliberately omitted where they do not affect positioning.

| Source | Task / population | Annotation unit; start/end availability | Metric; named-section localization? | Relevance and limit |
|---|---|---|---|---|
| [P01 Zhang et al., Form 10-K Itemization](https://arxiv.org/pdf/2303.04688) | Itemization of US SEC HTML/TXT filings, with text/format/visual strategies | Item title positions and derived item segments; item boundaries, not Indian PDF physical-page Gold | Document retrieval correctness based on item-start recovery; YES named SEC items | Direct precedent against broad novelty claims. Task format and evaluation contract differ. |
| [P02 Lu et al., 10-K Items Segmentation](https://arxiv.org/pdf/2502.08875) | Pretrained/large models on annotated SEC 10-K reports | Item-specific BIO line labels with derivable boundaries; GPT predicts starting LineIDs; no PDF page-end Gold | Precision/recall/F1/accuracy for item segmentation; YES | More direct methodological comparator literature; transfer or SOTA claims require task-matched evidence. |
| [P03 FinTOC 2022](https://aclanthology.org/2022.fnp-1.12.pdf) | Financial ToC structure; English/French prospectuses and Spanish annual reports | Heading text, page and hierarchy level; heading location available, no independently annotated content-end spans | Title F1, ToC matching F1 and hierarchy accuracy; NO specific MD&A localization | Useful heading/hierarchy supervision; cannot substitute for DocumentGold end boundaries. |
| [P04 ESGDoc](https://aclanthology.org/2023.emnlp-main.816.pdf) | ToC extraction from ESG annual reports | Heading/text-block hierarchy and ToC references; no named MD&A end-span Gold | Heading F1/tree similarity (TEDS); NO named MD&A task | Relevant structure/reading-order approach, not a validated ARPipe boundary comparator. |
| [P05 DocLayNet](https://arxiv.org/pdf/2206.01062) | Diverse document-page layout, including financial material | Human bounding boxes and layout categories; no semantic MD&A start/end | COCO-style mAP; NO named-section localization | Layout evidence only; region detection is not section-span accuracy. |
| [P06 Vaishampayan et al.](https://aclanthology.org/2023.finnlp-2.4.pdf) | Indian company audit-report coverage, year 2014 data | Multi-label sentence classes; no full-report MD&A boundary reference | Classification F1/precision/recall; NO named-section localization | Confirms Indian financial-report NLP exists; adjacent task, not evidence of MD&A-localization novelty. |
| [P07 Gaurav BRSR model card](https://huggingface.co/gaurav0506/brsr-greenwashing-roberta-base) | Claimed Indian BRSR greenwashing snippet classification | Binary snippet labels; semi-automatic labelling described; no page boundaries | Self-reported classification metrics; NO localization | Low-quality prior-art existence evidence only. Not peer reviewed, not an independent reliable benchmark or reason to recommend its model. |

**PROPOSED positioning.** A defensible prospective contribution is an explicitly evaluated extraction workflow for the declared Indian annual-report frame, with transparent reference and routing limitations. Existing literature already performs financial named-section segmentation and hierarchy extraction. This search cannot establish “first,” “unique,” “no prior Indian work,” or SOTA. Evidence of a directly comparable Indian MD&A span dataset would change comparator/novelty planning.

**UNRESOLVED.** Publisher/full-text access failed for the discovered Indian annual-report sentiment conference study (Chaithra/Mohan, DOI 10.1109/INOCON60754.2024.10511489) and the discovered ESG intentions/performance SSRN paper (DOI 10.2139/ssrn.5087087). They do not support any recommendation; dataset, annotation and metric details are UNVERIFIED. This is a bounded coverage limitation, not evidence of absence. The opened Indian audit-report paper and BRSR card close only the task-distinction gap.

## Q10: foundation constraints

### Q10a — detector coverage and LF evidence

**REPO-VERIFIED.** `tools/t0_4/core.py` constructs `legacy_font_candidate` from the broken-text predicate; this is not an independently established font diagnosis. Production `PageKind` has no main legacy class. The safe current description is **legacy_font is NOT currently a main routing class; broken_text → OCR; REMAP → separate registered research track**. Unknown legacy status remains unresolved until forensic evidence supports VERIFIED_LEGACY.

**REPO-VERIFIED.** Static triage detects sufficiently long text with excessive replacement/control characters; readable-but-wrong printable mappings, PUA, or a corrupted heading diluted by a largely clean page need not trigger that predicate. Local LF stored results illustrate wrong /ToUnicode, PUA, constructed ASCII-slot Devanagari, mixed-font headings and invisible wrong OCR layers remaining digital → NATIVE_READ. This constrains universal detector/handling claims. It does not establish that any such mechanism occurs in the real corpus.

**REPO-VERIFIED / HISTORICAL / NOT CURRENTLY REPRODUCIBLE.** The inspected bundle has 13 machine-result entries, while truth contains an additional F11 shaped-Devanagari entry; the build script ends at F10 and the Markdown report includes supplemental F11 discussion. This is a delivered-bundle coverage gap, not a newly reproduced complete fixture run. Scripts contain external /home/claude paths, and reported code revision 52ff2fe is unavailable locally. Build/evaluation/OCR were not executed. SlotDevaDemo is a constructed ASCII-slot mechanism, not Kruti Dev, DevLys, Akruti or another historical commercial font.

**REPO-VERIFIED provenance receipt.** SHA-256 read-only hashes: `results.json = cb317457f98b09a4ee327657675fd5920704879084f14f890ed1b28db94b8874`; build script content `56a472ff5e60c6eb0ade69f8bfc604f512de8635a212f4eddd0d2427f62e4e55`; evaluation script content `afe6822edb7d4d7fef6c5a7b38ba3ad966d11ea8676a6ecf28c04986734d61c7`. Counts come from reading result/truth keys and script construction, not detector reruns. Read-only font metadata and representative fixture PDF dictionaries were additionally inspected; no text extraction, rendering, detector or OCR execution was performed.

**REPO-VERIFIED / HISTORICAL / NOT CURRENTLY REPRODUCIBLE IN P1.** Historical P-B3 predicate and output are available in E0 history (`tools/legacy_font_measurement.py`, `reports/legacy_font_corpus_measurement.*`). Thus “no predicate is available anywhere” would be inaccurate. Its “confirmed” category combines a font-name heuristic with page-level corruption; that is not forensic proof that the named font caused the corruption. Historical counts were not reproduced from exact inputs/runtime in P1 and are not promoted to VERIFIED or Gold. Keep separate historical detector output, the current ARPipe detector, synthetic known-mechanism fixtures and real-corpus forensic evidence. The last remains UNRESOLVED.

**PROPOSED.** Real-corpus LF investigation is EXPERIMENT REQUIRED later if the author seeks actual prevalence, verified legacy handling, universal corrupted-text coverage or a REMAP benefit claim. It can be deferred under C5 or a carefully limited C1/C2 without those assertions. Diagnostic inspection of FIT boundary failures may still be useful. No LF-1, new real-corpus LF experiment or P-B3 rerun is performed in P1.

### Q10b — Oracle and metric alignment

**REPO-VERIFIED.** Current Oracle labels are sparse and page-level; registered routing contrast is document-level. The inspected specs do not supply an explicit transformation determining interventions for all relevant pages of a document, unlabelled-page handling, eligibility and paired outcomes. C3 is therefore **CLAIM NOT YET SUPPORTABLE**, regardless of the number of annotated Oracle pages.

**AUTHOR DECISION REQUIRED / EXPERIMENT REQUIRED.** B3–B5 must establish the scientific construct, population and independent labels; the later intervention protocol must establish the page→document transformation and test it before a document routing contrast. P1 does not invent it. A page-level classification estimand would be a different claim with a different denominator.

### Q10c — HOLDOUT history

**REPO-VERIFIED / UNRESOLVED.** Current split/protocol evidence provides forward controls, not a complete account of historical pre-T0 exposure. The latter remains **UNKNOWN**. Do not describe HOLDOUT as never processed, uncontaminated or contaminated. P1 used only previously published aggregate counts and repository metadata and did not access HOLDOUT content, rows or outputs. B8 remains pending; final evaluation is not authorized by this package.

## Source register

**SOURCED.** Access date for every opened source below: **2026-09-23**. “Opened” means inspected content, not just a search listing. Full text was read for task/provision details except R01, whose publisher abstract only was accessible. Firecrawl skills were consulted and CLI retrieval was attempted; when live retrieval stalled, built-in web access supplied the primary sources. No external source was used merely because an older report cited it.

| ID | Title; author/organization; year; type | URL/DOI | Exact question supported / inspected scope |
|---|---|---|---|
| R01 | When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks; Tim Loughran & Bill McDonald; 2011; journal article, publisher abstract | [DOI](https://doi.org/10.1111/j.1540-6261.2010.01625.x) | Q4: why finance-specific measurement definitions matter; no ARPipe error magnitude. |
| R02 | Use of the bootstrap in analysing cost data from cluster randomised trials: some simulation results; Terry N. Flynn & Tim J. Peters; 2004; peer-reviewed simulation study | [Full article](https://link.springer.com/article/10.1186/1472-6963-4-33) | Q7: cluster-bootstrap coverage depends on cluster design/distribution; no portable minimum n. |
| R03 | Companies Act 2013, section 134; Government of India, official Income Tax Department statutory republication (content attribution on host includes Taxmann); 2013, consolidated web text; statute | [Section](https://www.incometaxindia.gov.in/w/section-134-81) | Q5: Board report and annexures, not physical MD&A delimiters. |
| R04 | General Circular No. 8/2014, 4 April 2014; Ministry of Corporate Affairs, reproduced on official Income Tax Department Appendix III; 2014; official circular | [Appendix](https://www.incometaxindia.gov.in/hi/w/appendix-iii) | Q5: financial-year transition between 1956 and 2013 regimes. |
| R05 | Corporate Governance in listed companies — Clause 49 of the Listing Agreement, SEBI/CFD/DIL/CG/1/2004/12/10; SEBI; 2004; official circular/annexure | [PDF](https://www.sebi.gov.in/sebi_data/attachdocs/1293168356651.pdf) | Q5: predecessor MD&A placement/themes, IV(F)(i). |
| R06 | Listing Obligations and Disclosure Requirements Regulations 2015, early consolidated text; SEBI; 2015; official regulations | [PDF](https://www.sebi.gov.in/sebi_data/attachdocs/1441284401427.pdf) | Q5: Reg.34 and Schedule V B, commencement context; includes amendments, no vintage extrapolation. |
| R07 | Business responsibility and sustainability reporting by listed entities, SEBI/HO/CFD/CMD-2/P/CIR/2021/562; SEBI; 2021; official circular | [PDF](https://www.sebi.gov.in/sebi_data/attachdocs/may-2021/1620655793598.pdf) | Q5: BRSR versus BRR and applicability period. |
| R08 | Measures to facilitate ease of doing business with respect to framework for assurance or assessment, ESG disclosures for value chain, and introduction of voluntary disclosure on green credits, SEBI/HO/CFD/CFD-PoD-1/P/CIR/2025/42; SEBI; 2025; official circular | [PDF](https://www.sebi.gov.in/sebi_data/attachdocs/mar-2025/1743159419610.pdf) | Q5: recent BRSR changes and timing; not MD&A boundary law. |
| R09 | LODR Regulations, December 2025 consolidation; SEBI; 2025 annotated consolidation; official regulations | [PDF](https://www.sebi.gov.in/sebi_data/attachdocs/dec-2025/1766551151465.pdf) | Q5: Schedule V B(1)(i),(j), footnote 696 effective-date evidence only. |
| P01 | Form 10-K Itemization; Yanci Zhang et al.; 2023; arXiv preprint | [Paper](https://arxiv.org/pdf/2303.04688) | Q9: existing named-item extraction, units and metric mismatch with page IoU. |
| P02 | Utilizing Pre-trained Language Models and Large Language Models for 10-K Items Segmentation; Hsin-Min Lu, Yu-Tai Chien, Huan-Hsun Yen & Yen-Hsiu Chen; 2025 preprint, inspected revision 2026; arXiv manuscript | [Paper](https://arxiv.org/pdf/2502.08875) | Q9: annotated line-level named-item segmentation and endpoints. |
| P03 | The Financial Document Structure Extraction Shared Task (FinTOC 2022); Abderrahim Ait Azzi et al.; 2022; ACL workshop shared-task paper | [Paper](https://aclanthology.org/2022.fnp-1.12.pdf) | Q9: heading/page/hierarchy labels, not independent content-end spans. |
| P04 | A Scalable Framework for Table of Contents Extraction from Complex ESG Annual Reports; Xinyu Wang, Lin Gui & Yulan He; 2023; EMNLP paper | [Paper](https://aclanthology.org/2023.emnlp-main.816.pdf) | Q9: ESG structure extraction and tree metrics. |
| P05 | DocLayNet: A Large Human-Annotated Dataset for Document-Layout Segmentation; Birgit Pfitzmann, Christoph Auer, Michele Dolfi, Ahmed S. Nassar & Peter Staar; 2022; research paper | [Paper](https://arxiv.org/pdf/2206.01062) | Q9: page-layout bounding boxes versus semantic section localization. |
| P06 | Audit Report Coverage Assessment using Sentence Classification; Sushodhan Vaishampayan, Nitin Ramrakhiyani, Sachin Pawar, Aditi Pawde, Manoj Apte & Girish Keshav Palshikar; 2023; FinNLP workshop paper | [Paper](https://aclanthology.org/2023.finnlp-2.4.pdf) | Q9: Indian financial-report sentence-classification precedent. |
| P07 | BRSR Greenwashing Detection Model (RoBERTa-base); Gaurav / gaurav0506; 2024 as stated by model card; self-published model card | [Card](https://huggingface.co/gaurav0506/brsr-greenwashing-roberta-base) | Q9: existence of BRSR snippet classification only; low evidence quality. |

## What was deliberately not researched again

**REPO-VERIFIED / PROPOSED.** P1 reused completed B1–B8 and targeted legacy research, Phase 2 audit/integration/experiments, and Gold-method/source-register work. It did not restart general OCR-engine comparisons, font-remapping literature, annotation-agreement surveys, broad layout-model reviews, the corporate-law literature or downstream econometrics. Sources were reopened only where they support retained recommendations or close the specific task/period gap. No new roadmap, recursive roadmap audit or claim of novelty from a sparse search is produced.

## What we may have missed and expert pre-mortem

**UNRESOLVED.** Exact local Master Flow/readiness artifacts remain unavailable; authoritative supplied context constrains the stopping point. Unavailable baseline/fixture revisions, incomplete historical runtime provenance, exact sampled-issuer legal applicability, directly comparable Indian MD&A research, actual outcome variances, annotator speed and real-corpus font mechanisms remain gaps. These are not negative findings.

**PROPOSED.** The matrix and decision sheet record the examiner challenge, questionable denominator/population, missing evidence, metric mismatch, failure condition and consequences of a wrong choice for each major plan. Most choices are reversible before protocol/Gold freeze; exposure of final material cannot be undone. Baseline relabelling after seeing results, output-conditioned exclusions, a page-to-document Oracle leap, or treating synthetic mechanisms as prevalence would undermine future experiments. Deferring unused tracks is safe only through author-approved scope; no pending B item is silently closed.

## P1 validation and boundary receipt

**VERIFIED.** Inspected actual hash-lint interface, then ran `python tools/check_doc_hashes.py --repo-root .`: PASS, 10 claims across 1 document, zero failures. Relevant semantic and checker tests passed: **23 passed, 1 deselected**, using a fresh temporary pytest base directory after the sandbox prevented fixture writes. The deselected `historical_immutability_strict_allowlist` is a Phase 2.1-stage changed-path allowlist against its older base that intentionally does not permit new Phase 3 documents; it is not an applicable P1 authorization check. No test was edited. The final pre-commit checks passed: git diff --check; empty staged and worktree frozen-path differences against START_SHA; and an exact whitelist of the five intended docs/phase3 Markdown files. Thus there are no code, B-register, T0/E0/Phase 1/Phase 2 document, PDF or HOLDOUT modifications. The embedded planning arithmetic was independently reproduced, and local links, table structure, UTF-8 and blank author-choice fields were checked. Post-commit checks are reported in the commit handoff.

**PROPOSED execution boundary.** All candidate decisions remain blank and no claim is adopted. P1 ends with the documentation commit and checks. Next permitted action is author review/selection from this package under the supplied frozen Master Flow. P2 or any baseline, Gold, OCR, LF, REMAP, acquisition or HOLDOUT work requires its later stage authorization; P1 does not start it.
