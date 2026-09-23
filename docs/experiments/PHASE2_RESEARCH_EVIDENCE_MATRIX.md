# Phase 2 evidence, literature, and prior-art matrix

**Search and retrieval date:** 2026-09-21<br>
**Research boundary:** repository evidence first; targeted external research second. External sources inform interpretation and future tests but do not overwrite frozen ARPipe facts.

## Search protocol actually used

Repository inspection preceded web research. External discovery then used broad and synonym searches, semantic paper-index searches, related-paper expansion, primary-source opening, and current official-documentation checks. Representative search groups were:

- `PDF parser benchmark digital-born financial reports layout text extraction`;
- `legacy font PDF ToUnicode extraction visible glyph OCR mojibake PUA`;
- `hybrid PDF native text OCR region merge source arbitration duplicate text`;
- `annual report section segmentation MD&A 10-K itemization document hierarchy ESG report`;
- `table of contents bookmarks noisy labels hierarchy section boundary long document`;
- `reading order relation annotation unitizing agreement document layout`;
- `double annotation sampling adjudication span boundary agreement`;
- `group holdout data leakage historical exposure document issuer split`;
- `content hash canonical serialization newline Git blob reproducibility provenance`;
- negative/prior-art variants combining `Indian annual report`, `management discussion and analysis`, `MD&A`, `page span`, `localization`, `OCR`, and `benchmark`.

More than ten paper-index queries and related-paper expansions, more than fourteen web-discovery queries, and direct inspection of authoritative specifications/documentation and the papers retained below were performed. Backward/forward exploration was practical rather than exhaustive: related-record expansion and cited/related work were used to locate closer task and methodology sources. Search-result snippets were not used as evidence. No complete patent, proprietary-product, dissertation, or all-language search was attempted; the novelty conclusion is bounded accordingly.

## Existing project research coverage

| Project record | Provenance | What it establishes | Findings/decisions covered | Residual limit |
|---|---|---|---|---|
| T0 corpus freeze (`freeze_protocol.md`, inventory, split manifests) | Frozen tree and T0 commit `23d6228` | 194 executable PDFs; 36 issuers; 37,917 pages; 92/48/54 issuer-disjoint split; 14 missing records | P2-14, P2-15, P2-24, P2-26, P2-27 | Does not prove pre-T0 document non-exposure. |
| T0.1 gap audit and page profile | T0.1 `b6b76d9` | Page conditions and candidate review queue | P2-03-P2-10, P2-13, P2-27 | Several names are proxies; raw queue falsely reported model review. |
| T0.1R reconciliation | T0.1R `879762a2f236b3aaa6df33b7ddacc60c01d633c1` | Corrects 72 rows to `NOT_REVIEWED`; records proxy dependencies; no acquisition | P2-03, P2-11, P2-13, P2-27 | Reconciliation does not validate proxy precision/recall. |
| T0.2 robustness gate | T0.2 `ef2e8c5` | Deterministic acquisition decision; scanned condition remains audit-required | P2-05, P2-11 | Not an OCR performance experiment. |
| T0.3A taxonomy and results | T0.3A `02bae11` | 10 dimensions, 35 categories, evidence labels, representation classes | P2-03, P2-07, P2-09-P2-13, P2-25 | Taxonomy and results share a commit; no premeasurement ordering proof. |
| T0.3A-R1 era extension | taxonomy `f0e5805`; results `ff030d9` | Pre/post-2015 entries and Git-verifiable ordering | P2-10, P2-12, P2-25 | Counts already existed in T0.3A. |
| T0.4 preregistration, configs, manifest | initial `b937b58`; final closure tree `63e3c04` | Dual-track design, declared routes/classes, sampling, metrics, HOLDOUT rules | P2-02, P2-04-P2-06, P2-08, P2-16-P2-20, P2-28; B1-B8 | No engine, annotation, or benchmark was run. |
| T0.4 final closure | `63e3c04` | Four conditions closed; two observations retained | P2-18, P2-22, P2-28; B1, B3 | Not a completed Gold-method decision record. |
| Phase-1 frozen-foundation verification | `e52166f:docs/experiments/PHASE1_FROZEN_FOUNDATION_VERIFICATION.md` | Valuable ancestry/object audit | P2-01, P2-21, P2-22 | Ten displayed hashes and the eight-question attribution are wrong. |
| Phase-2 integrity audit and JSON | base `13423c4` | Authoritative 28-finding reproduction and B1-B8 verification | All P2 and B items | Analysis/correction record; does not adopt methodology. |
| T0.4-LF preimplementation audit and routing clarification | local safety commits `d9f974b`, `916407d` | Legacy class overlap, current route facts, unadopted one-class OCR recommendation | B1, B2, B5; P2-07, P2-16, P2-17, P2-23 | Local-only post-closure research; no rule adopted. |
| Gold Method Research package | local commit `1c53c42` | PageGold/DocumentGold design, independent annotation/adjudication, MD&A protocol, tooling review, reliability recommendations | B5-B7; P2-19 | Exact rates, units, tooling, and author choices remain open. |

### Existing research that should be reused

The Gold package already supports all-page PageGold reference text for the primary CER denominator; structured DocumentGold with candidate/selected/admissible spans and ambiguity; immutable independent A/B records before adjudication; a separate adjudicated record; page-image-only Track A; document-context Track B; and a hybrid random-plus-diagnostic reliability design. Phase 2.1 should cite and convert these recommendations into decisions rather than commission another broad annotation-method review.

## External evidence matrix

Evidence strength describes relevance to the ARPipe decision, not publication prestige.

| ID | Source | Relevant evidence | ARPipe implication | Transfer limit | Strength |
|---|---|---|---|---|---|
| E01 | [ISO 32000-1:2008 PDF specification](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf) | Character codes may map to Unicode through `ToUnicode`; text rendering mode 3 is invisible; logical structure and outlines are distinct PDF facilities. | Pixels alone cannot establish hidden text-layer/font-mapping state; use source-side evidence for semantic route labels. | A specification defines mechanisms, not their corpus prevalence. | High |
| E02 | [PDF Association: why PDF/A conformance level B fails machine reading](https://pdfa.org/why-pdfas-conformance-level-b-fails-machine-reading/) | Correct visual rendering can coexist with failed character extraction; Unicode mapping matters. | Supports the category-mismatch finding in B5. | Explanatory industry source, not an ARPipe benchmark. | Medium-high |
| E03 | [pypdf text extraction guidance](https://pypdf.readthedocs.io/en/stable/user/extract-text.html) | Distinguishes digitally born, scanned, and OCRed PDFs; notes PDF's missing semantic layer and tradeoffs in always using OCR. | Supports explicit representation evidence and avoiding unconditional OCR. | Library guidance; no comparative ARPipe measurement. | Medium |
| E04 | [OCRmyPDF advanced features](https://ocrmypdf.readthedocs.io/en/latest/advanced.html) | Skip/redo/force policies differ; force rasterization can lose vector, interactive, or tagged structure; mixed PDFs require policy. | Confirms native-only/OCR-only/redo choices are materially different interventions. | Tool-specific behavior; not a prescribed ARPipe architecture. | Medium-high |
| E05 | [PyMuPDF text extraction recipes](https://pymupdf.readthedocs.io/en/latest/recipes-text.html) | Word/block coordinates are available; reading order is not inherently reliable; geometric sorting is a convenience. | Engine blocks must not silently define Gold reading order. | One library's interface and heuristics. | Medium |
| E06 | [OCR-D PAGE-XML specification](https://ocr-d.de/en/spec/page) | Represents regions and explicit reading-order groups/references. | Useful schema precedent for stable region IDs and declared order relations. | Reuse of concepts requires an ARPipe region/table policy. | Medium-high |
| E07 | [W3C PROV-DM (2013)](https://www.w3.org/TR/prov-dm/) | Models entities, activities, agents, generation, use, derivation, attribution, and association. | Supports provenance fields richer than one evidence-status token. | General model; ARPipe must choose its profile. | High |
| E08 | [ACM artifact review and badging definitions](https://www.acm.org/publications/policies/artifact-review-and-badging-current) | Separates repeatability, reproducibility, and replicability by team/artifact/setup conditions. | Avoid claiming independent reproduction where only same-artifact verification occurred. | Policy vocabulary, not a scientific result. | High |
| E09 | [NIST FIPS 180-4 (2015)](https://csrc.nist.gov/pubs/fips/180-4/upd1/final) | Defines secure hash algorithms. | A digest identifies the chosen byte string; the application must still define serialization and domain separation. | Does not define ARPipe's ranking key or canonical bytes. | High |
| E10 | [Git `hash-object`](https://git-scm.com/docs/git-hash-object) and [`git show`](https://git-scm.com/docs/git-show) | Git blobs are byte content objects; `--no-filters` hashes raw file content for the selected object type. | Record both Git object identity and external SHA-256 when both matter; newline changes are substantive for raw-byte hashes. | Git object IDs are not SHA-256 file checksums in this repository. | High |
| E11 | [scikit-learn GroupKFold](https://scikit-learn.org/stable/modules/cross_validation.html#cross-validation-iterators-for-grouped-data) | Keeps groups non-overlapping across train/test folds. | Supports the issuer-disjoint logic of T0 splits. | A grouping API does not establish historical non-exposure. | Medium |
| E12 | [scikit-learn common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage) | Leakage occurs when information unavailable at prediction time influences fitting/selection; split-before-preprocessing is recommended. | Require a demonstrated information pathway before alleging leakage; keep HOLDOUT out of method selection. | Generic ML guidance, not a forensic conclusion about this history. | Medium-high |
| E13 | [SEBI consolidated LODR circular, 2022](https://www.sebi.gov.in/sebi_data/attachdocs/jul-2022/1659096400607.pdf) | Regulation context places MD&A in annual-report/directors-report disclosure practice. | Supports the task's regulatory relevance, not physical page boundaries. | Consolidated 2022 source does not by itself define FY2010-2015 practice or annotation spans. | Medium |
| P01 | [Adhikari & Agarwal, benchmarking PDF information-extraction tools (2024)](https://arxiv.org/abs/2410.09871) | Compares ten PDF parsers over multiple DocLayNet domains and tasks; performance is tool/domain/task dependent. | Parser quality cannot be assumed from “digital PDF”; evaluate the selected task and representation. | Not an Indian MD&A benchmark and not a routing study. | Medium-high |
| P02 | [Vasantharajan et al., digitizing documents with legacy fonts (2021)](https://arxiv.org/abs/2109.05952) | Legacy Tamil/Sinhala font encodings can defeat extraction; rendering plus language-specific Tesseract adaptation improves error rates. | Genuine legacy failures are possible and source-side inspection is warranted. | Different scripts, fonts, and corpus; does not show ARPipe has the condition or that OCR is always best. | Medium |
| P03 | [ESGDoc (2023)](https://arxiv.org/abs/2310.18073) | Builds hierarchical trees for 1,093 ESG reports using reading order/font size and existing TOCs as reference labels. | Direct precedent for report hierarchy and TOC-conditioned structure extraction. | Existing TOCs are proxy/reference metadata; ESG structure is not Indian MD&A Gold. | High for prior art; medium for transfer |
| P04 | [Reading Order as a Latent Relation over Layout (2024)](https://arxiv.org/abs/2409.19672) | Treats reading order as relations among layout elements rather than only one flat permutation. | Supports relation-based Gold and explicit granularity. | ARPipe still must choose atomic regions, ties, and table treatment. | High |
| P05 | [Kapoor & Narayanan, leakage and reproducibility failures (2022)](https://arxiv.org/abs/2207.07048) | Taxonomizes leakage through non-independent samples, whole-data preprocessing/selection, temporal errors, and test-set misuse. | Separate split overlap facts from evidence of an information pathway; audit selection and preprocessing. | Does not determine ARPipe's historical exposure. | High |
| P06 | [Boundary agreement in PICO span annotation (2019)](https://arxiv.org/abs/1904.09557) | Exact span boundaries can disagree while relaxed region agreement remains substantially higher. | Report exact and tolerance/overlap measures; inspect boundary ambiguity. | Biomedical text spans differ from page-level MD&A sections; thresholds do not transfer. | Medium |
| P07 | [Form 10-K Itemization (2023)](https://arxiv.org/abs/2303.04688) | Locates SEC 10-K item sections using structural and textual signals and reports strong item retrieval. | Closest established task-family precedent for regulated financial-report section localization. | SEC HTML/plain text and item numbering differ from Indian PDFs and MD&A page spans. | High for prior art; medium for transfer |
| P08 | [BERT4ItemSeg (2025)](https://arxiv.org/abs/2502.08875) | Learns 10-K item segmentation on thousands of annotated filings. | Learned financial-section segmentation is directly relevant prior art. | Different regulator, document format, labels, and evaluation; recent preprint. | High for prior art |
| P09 | [HELD (2021)](https://arxiv.org/abs/2105.09297) | Learns hierarchical structure for long documents, including financial reports. | Supports hierarchy-based candidate generation beyond keyword matching. | Not a direct MD&A page-span or Indian-report evaluation. | Medium-high |
| P10 | [DocLayNet (2022)](https://arxiv.org/abs/2206.01062) | 80,000+ manually annotated pages across six domains, including financial reports; document-aware splits reduce layout leakage. | Strong layout prior and split-design precedent. | Page layout classes do not provide document-global section spans or Gold reading order. | High for infrastructure |
| P11 | [HiPS (2025)](https://arxiv.org/abs/2509.00909) | Uses TOCs when reliable and fallback parsing when metadata is absent/noisy for hierarchical segmentation. | TOC should be a conditional prior, not a mandatory ground-truth channel. | Law books, largely single-column; recent preprint and not financial reports. | Medium |
| P12 | [Agreement for complex annotation tasks (2022)](https://arxiv.org/abs/2212.09503) | Complex/unitizing annotation needs task-specific distances and decomposition of boundary, alignment, and label disagreement. | B6/B7 should report more than one aggregate agreement number. | Does not prescribe ARPipe's overlap rate or acceptance threshold. | Medium-high |
| P13 | [LayoutReader / ReadingBank (2021)](https://arxiv.org/abs/2108.11591) | Uses source-document metadata to generate large reading-order training data. | Demonstrates scalable weak supervision and is direct reading-order prior art. | Generated Word metadata is not human Gold for PDFs and can encode source bias. | Medium |

## Candidate tool and method suitability

This is a capability screen, not a tool selection. Maintenance status reflects the projects/pages inspected on 2026-09-21; no dependency version is frozen by this research.

| Candidate | Maturity / maintenance / license | Inputs, compute, offline/API, cost | Language / financial relevance | Failure modes and integration burden | ARPipe status |
|---|---|---|---|---|---|
| pypdf | Mature Python library; maintained documentation; BSD-family open-source license | PDF bytes; local CPU; offline; no API fee | Extracts encoded PDF text; domain-agnostic | Reading order and semantics are not guaranteed; scans need OCR; parser result is not ground truth | Useful fixed native baseline and diagnostics, not an oracle |
| PyMuPDF | Mature and actively documented; AGPL/commercial dual licensing requires project review | PDF bytes; local CPU; offline; no per-call fee | Word/block coordinates; domain-agnostic | Geometric `sort` is heuristic; license and engine-specific blocks complicate direct Gold reuse | Useful diagnostic/candidate infrastructure only |
| qpdf inspection/JSON | Mature PDF structural tool; maintained official docs; Apache-2.0 | PDF bytes; local CPU; offline; no API fee | Object/font/outline inspection; language-independent | Exposes structure, not intended text or MD&A semantics; JSON can be large | Good read-only forensic building block for X1, after authorization |
| OCRmyPDF | Mature maintained project; MPL-2.0; orchestrates established PDF/OCR tools | PDF plus local OCR/render stack; CPU/storage intensive at scale; offline; no API fee | Inherits Tesseract languages; generic, not finance-specific | Force/redo may rasterize or discard structure; mixed-page policies and duplicate layers need care | Design-space reference for X2; not selected or run |
| Tesseract | Mature maintained OCR engine; Apache-2.0; 100+ language data packs | Page images; mostly local CPU; offline; no API fee, compute/time cost | Broad scripts; financial-layout handling is not guaranteed | Layout, small fonts, tables, legacy glyphs, and domain text can fail; language packs/config affect reproducibility | Existing benchmark candidate only; not run |
| OCR-D PAGE-XML | Mature schema/ecosystem standard rather than a single engine | Structured regions/relations; local files; offline | Language-agnostic layout exchange | Mapping ARPipe tasks/tables to schema still requires policy; schema compliance is not annotation validity | Reusable schema precedent for B7 |
| Label Studio Community | Established open-source annotation platform; Apache-2.0; prior ARPipe review inspected it | Local/web server; modest hosting/admin cost; no required external API | Configurable, domain-agnostic | Prior review found peer-visibility/provenance and workflow gaps for the intended independent/adjudicated design | Candidate only; not selected; requires controlled configuration or extensions |
| Custom annotation UI | No existing mature ARPipe implementation | Development/hosting effort; can remain local/offline | Can match MD&A/reading-order protocol exactly | Highest engineering and validation burden; prior prototype lacked required authentication/provenance controls | Do not build until B5-B7 and X4 requirements are frozen |

Existence does not establish suitability. In particular, no row establishes performance on Indian annual reports, ARPipe's frozen corpus, or the MD&A localization endpoint. That requires the bounded FIT pilots in the experiment register.

## Evidence integration by open issue

| Issue | Project evidence | External evidence | Integrated conclusion |
|---|---|---|---|
| Genuine legacy fonts | Three incompatible proxies; no human review or font-table inspection | E01-E03, P02 show extraction/rendering divergence is possible | Occurrence remains unverified. Run source-side FIT forensics before route adoption. |
| Visual-only route oracle | Allowed evidence names rendered image; label semantics include NATIVE/LEGACY | E01-E02 show pixels cannot reveal mapping/invisible-text state | Either allow multi-channel PDF evidence or redefine labels as visible action requirements. |
| Hybrid extraction | Current code whole-page OCRs hybrid; prose claims read text plus OCR image | E03-E04 and P01 show meaningful tradeoffs and task dependence | Compare native, OCR, and merge/arbitration on FIT; no architecture decision yet. |
| TOC/outline role | ARPipe proxies are broad and near-saturated | P03, P09, P11 show TOC/hierarchy utility and metadata weakness | Candidate/annotation aid only; visible-content protocol remains Gold authority. |
| Reading order | Frozen pair strings lack unit | E05-E06, P04, P13 support explicit region relations | Define engine-independent atomic regions and directed relations; do not inherit engine blocks. |
| Reliability sampling | Only oracle route has an under-specified 25% rule | P06, P12 and prior Gold research support task-specific, decomposed agreement | Use a random population layer plus diagnostic rare cases; author chooses workload/rate. |
| Provenance and hashes | Wrong displayed hashes, newline identity issue, local-only PDFs | E07-E10 distinguish entity provenance, raw bytes, and reproducibility terms | Record source entity/activity/agent and exact serialization; append corrections. |
| HOLDOUT/leakage | Current issuer split sound; historical names overlap; exposure unknown | E11-E12, P05 distinguish group separation from information-pathway leakage | Do not allege leakage; retain forward default-deny and explicit access provenance. |

## Prior-art and novelty boundary

Classification:

- **A — directly implemented prior art:** same core task/method is already demonstrated.
- **B — partially transferable:** strong precedent with domain/unit differences.
- **C — reusable infrastructure/standard:** implementation or schema building block.
- **D — methodological precedent:** study-design or annotation principle.
- **E — inspiration only:** weakly transferable analogy.
- **F — contradicted assumption:** evidence warns against the proposed premise.

| ARPipe idea | Classification | Closest sources | Novelty-safe conclusion |
|---|---|---|---|
| Financial-report section localization | A/B | P07, P08 | Direct task-family prior art exists; Indian MD&A/PDF setting may differ. |
| Hierarchical report segmentation from headings/typography/TOC | A/B | P03, P09, P11 | Established approach; not algorithmically novel. |
| Relation-based reading-order Gold | A/D | E06, P04, P13 | Established representation; ARPipe must specialize the unit/table policy. |
| Layout analysis for financial pages | A/C | P10 | Public infrastructure/prior art exists. |
| Representation-aware parser/OCR routing | B/C | E03, E04, P01, P02 | Known design space; ARPipe-specific arbitration remains an empirical engineering question. |
| TOC or outline as ground truth | F | P03, P11 plus ARPipe saturation evidence | Useful weak supervision/prior, but ungrounded use as Gold is not supported. |
| Pixels diagnose PDF encoding semantics | F | E01, E02 | Category error unless label is redefined as a visual action. |
| Exact plus tolerant boundary metrics | D | P06, P12 | Established methodology; choose ARPipe-specific tolerances. |
| Issuer-disjoint evaluation | C/D | E11, P05, P10 | Sound grouped-split practice, not a novelty claim. |
| Explicit provenance and byte identities | C/D | E07-E10 | Standards-based research hygiene, not a novel method. |
| Indian FY2010-2025 MD&A corpus/evaluation | B/E | E13; no exact evaluated counterpart found | Potential dataset/evaluation differentiation only; novelty unproven and search not exhaustive of proprietary/non-indexed work. |

### Claim discipline

The research supports “no exact counterpart was identified in the searched sources as of 2026-09-21,” not “first” or “novel.” The search covered the paper index and authoritative web sources but was not a systematic review of every database, patent, commercial product, thesis, or non-English source. Any eventual novelty claim needs a separately registered and reproducible prior-art review tied to the exact implemented contribution.

## Source-quality notes

- Specifications and project bytes support mechanism and provenance claims most strongly.
- Peer-reviewed or indexed papers support prior-art and method-transfer claims, but domain differences are explicit.
- Recent arXiv preprints are corroborating evidence only and should not carry an architecture decision alone.
- Tool documentation describes capability/tradeoffs, not comparative performance on ARPipe.
- No source in this matrix supplies ARPipe Gold labels, proxy precision/recall, or benchmark results.
