# ARPipe: targeted gap research on the legacy-font problem and B1–B8

Prepared 23 September 2026. This is research only. It makes no author decisions, changes no frozen artifact, and does not authorize Gold, OCR runs or HOLDOUT access.

## 0. What this is based on

**Repository.** I read the public repo `hariom-s27/arpipe`, `main` at `52ff2fe`. The Phase 2.1 anchor `a45a640` is an ancestor of it. The files that matter here are `arpipe/triage.py`, `arpipe/patterns.py`, `configs/t0_4/*.json`, `artifacts/t0_4/benchmark_manifest.json`, `dataset/corpus_freeze/page_profile.csv`, `docs/experiments/PHASE2.1_B1_B8_DECISION_REGISTER.md`, `PHASE2_RESEARCH_B1_B8.md`, `PHASE2_RESEARCH_EVIDENCE_MATRIX.md`, `T0.4-routing-clarification.md` and `research_source_register.csv`. The repo has no corpus PDFs, so **no ARPipe page, font object or /ToUnicode map was inspected.**

**Project documents.** From the thesis project I used `LF_T0.4-LF-RECON.md` and `17_B1_B8_DECISION_SHEET.md`.

**P-B3 figures in the brief.** The brief quotes 437 "confirmed" pages, of which about 225 were digital and about 211 broken_text. Those figures are not in the repo. I treat them as *user-supplied historical evidence* and never as corpus fact.

**New evidence produced for this report:**
- **(E-LOCAL-1)** A synthetic forensic fixture suite of 14 PDFs. I ran ARPipe's frozen, unmodified `triage.profile_page` on it, plus PyMuPDF 1.28.2, pdfminer.six, Tesseract 5 (eng and hin) and two recovery methods. It uses no corpus data. The suite ships as `lf_fixture_suite.zip`: scripts, PDFs and `results.md`.
- **(E-LOCAL-2)** Metadata-only recounts from the frozen `page_profile.csv` and `benchmark_manifest.json`. They are restricted to FIT and VALIDATION. HOLDOUT rows were excluded from every new analysis.

**Evidence tags.** Every finding carries one strength tag: **A** established externally · **B** supported but context-dependent · **C** plausible or inferred · **D** unresolved · **E** contradicted. ARPipe-specific claims also carry one status tag: **[REPO-VERIFIED]** · **[LOCAL-EXPERIMENT]** (synthetic, not corpus) · **[NOT VERIFIED]** · **[EXTERNAL ONLY]**.

---

## 1. Executive research verdict

**New evidence.** The most consequential new evidence is local, not literature. ARPipe's `broken_text` detector is narrower than the project documents assume. It is a page-level ratio of U+FFFD plus C0 control characters above 2% (`patterns.MOJIBAKE_RE`, `triage._classify`) [REPO-VERIFIED]. On synthetic fixtures it catches only one corruption family, a missing /ToUnicode where raw glyph codes land below U+0020. Even that works partly by accident: the space glyph has ID 3, so every space becomes U+0003 [LOCAL-EXPERIMENT].

It routes the following to **NATIVE_READ**, even though native text is 27–99% wrong (CER 0.27–0.99):
- a present-but-wrong /ToUnicode (CER 0.83);
- Private Use Area (PUA) mappings (0.99);
- an ASCII-slot "Kruti-Dev-type" Devanagari font (0.72);
- a bilingual half-legacy page (0.27);
- a page image with a wrong invisible text layer (0.83).

It also routes three mixed pages to NATIVE_READ. Each has a clean body and a corrupted MD&A heading, and each has a whole-page CER of only 0.02–0.05. On two of them the lost text is exactly the MD&A heading that `MDA_HEADING_RE` needs [LOCAL-EXPERIMENT]. Tesseract recovered every one of these fixtures at CER 0.00–0.09.

**What it supports:**
- "Legacy font" is not one class. It is at least five mechanisms, and only some of them produce the detector's symptom.
- The one-class-OCR contract (the B1 recommendation) is safe for the pages it catches.
- The 803/803 identity is a definition, not evidence (already known).

**What it weakens:**
- The implicit reading that "broken_text → OCR covers legacy-font pages". It covers one mechanism only; the others are routed to native read. This coverage gap is **independent of the REMAP question**.
- The LF-RECON statement that a U+FFFD detector at default PyMuPDF flags "detects nothing at all". ARPipe's regex also counts C0 controls, and those do fire on raw low codes. The detector works, but for a narrower class than intended.
- The historical P-B3 figure of about 225 "confirmed" pages classified digital is *mechanistically expected*. Several mechanisms are invisible to this detector by construction. That does not make the P-B3 labels correct.

**New project-internal evidence of localized corruption [REPO-VERIFIED, metadata only]:**
- 6,423 of 27,764 FIT+VAL pages (89 of 140 documents) carry non-zero sub-threshold `mojibake_ratio` values; most are probably benign symbol-font glyphs.
- 138 pages classed `digital` sit at 0.01–0.02. Of these, 129 sit in documents that also contain `broken_text` pages. The fixed 2% threshold appears to split one mechanism inside the same document.

**Still unresolved:**
- Whether any ARPipe page is a genuine ASCII-slot legacy page.
- Which mechanisms produced the 803 pages.
- Whether any affected page falls in an MD&A span or heading.
- All three need source-side inspection of FIT PDFs. Nothing external can settle them.

**Effect on B1–B8 readiness.**
- **B1** gains a sharper structural distinction: a *mechanism attribute*, a *detector symptom* and a *route* are three separate things. It also gains a new issue that is separate from REMAP: false-native routing.
- **B3/B6** gain a concrete estimand consequence. Under the literal 79-unit reading the oracle contains **0** native_ok units. The false-native rate, which is where every silent failure above lives, is then unestimable.
- **B7** gains a quantified mismatch. The oracle labels about 1.5 pages per document (121 units across 82 documents). In the 20 documents with historical spans, **0 of 6** oracle units fall inside the span.
- **B2, B4, B5, B8** need only narrow clarifications.

---

## 2. New findings only

Material already covered by the repo register (E01–E09, P01–P09, S01–S13) or by LF-RECON is not repeated. That covers: ISO 32000 /ToUnicode and invisible text; Vasantharajan 2021; Kruti-Dev-type ASCII-slot fonts; converter tools; Raj & Prahallad 2007; `TEXT_USE_CID_FOR_UNKNOWN_UNICODE` existing; agreement literature; PAGE-XML; leakage taxonomy.

| ID | Finding | Project issue affected | Evidence strength | Why it matters |
|---|---|---|---|---|
| N1 | The frozen `broken_text` predicate is `n_chars ≥ 120 AND count([U+FFFD, C0 except \t \n \r]) / len > 0.02`. PUA characters, printable wrong letters and Latin-coded Devanagari are not counted, and script detection sees only codepoints. | B1, B2, A3/A4 | A [REPO-VERIFIED] (code) | Fixes exactly which mechanism class the OCR route can ever receive via `broken_text`. |
| N2 | PyMuPDF's default extraction flags emit **raw character codes** for unmapped glyphs, not U+FFFD. U+FFFD appears only if the flag is switched off. | B1 detector semantics | A (official docs) | ARPipe catches missing-ToUnicode pages only when raw codes fall below U+0020. Detection depends on glyph numbering (fonts that renumber compactly from 1 fall below U+0020), not on the mapping itself. |
| N3 | On fixtures, ARPipe routed 9 of 11 corrupted-text pages to NATIVE_READ, including every wrong-mapping, PUA, ASCII-slot, invisible-layer and mixed-font case. It caught only the two missing-ToUnicode cases and correctly passed both clean controls. The 12th case, shaped Devanagari (N6), was also read natively. | B1 coverage, A4 | B [LOCAL-EXPERIMENT] | "broken_text → OCR" is not coverage of the corrupted-text class. The gap concerns *detection*, independent of REMAP. |
| N4 | **Mixed-font pages:** a single corrupted heading font on a clean page gives mojibake 0.0047 or 0.0 and a whole-page lexicon hit rate of 0.95–0.97. Both are far from any page threshold. The lost string was the MD&A heading, and `MDA_HEADING_RE` failed on it. | A4, B1, section localisation | B [LOCAL-EXPERIMENT]; also C for real reports | Page-level statistics cannot see span or font-level corruption *in principle*, because the corrupt share is diluted by the page. Headings are the most MD&A-relevant, lowest-volume text. |
| N5 | Frozen metadata: 138 FIT+VAL `digital` pages have mojibake ratio 0.01–0.02, spread over 16 documents, and 129 of them sit in documents that also hold `broken_text` pages. 6,423 pages in 89 documents carry some non-zero ratio. | A4, B1, B6 sampling | B [REPO-VERIFIED] (metadata); mechanism D | Direct corpus evidence that the 2% cut splits a within-document mechanism. The low-level mass is probably benign (bullets and symbol fonts), and that separation is unverified. |
| N6 | A **valid Unicode** Devanagari font, shaped normally (conjuncts, reph, pre-base matra), extracted at CER 0.30. Reph and conjunct glyphs came out as raw codes such as `⼯` and `Ⱂ`, and matras were reordered. ARPipe called it digital. Hindi OCR scored CER 0.00. | A1 terminology, A8, Devanagari evidence | B [LOCAL-EXPERIMENT]; the mechanism is A: per-glyph /ToUnicode cannot express cluster reordering, and ActualText is required (W3C WAI thread, Cunningham 2016) | The one verified corpus Devanagari garble (`कार्ाािर्`, SJVN letterhead, HOLDOUT) matches this *Unicode-shaping* class at least as well as the ASCII-slot class. "Garbled Devanagari" alone does not show a legacy font. |
| N7 | MuPDF font subsetting drops the embedded `cmap` and glyph names. Cross-checking /ToUnicode against the font's own cmap is then impossible. On full fonts that check separates clean text (agreement 1.00) from a wrong /ToUnicode (0.19) and restores the text exactly (CER 0.00). | A3, A5 (remap preconditions) | B [LOCAL-EXPERIMENT]; cmap optional in CIDFontType2 programs: C (spec text not retrieved) | Deterministic remapping from the embedded font is possible only when the font program keeps its cmap. Subset fonts are the norm, so availability must be measured per font, not assumed. |
| N8 | A published font-mapping repair system (REPDF, 2026) uses a reference-font database and chooses the candidate mapping that gives the most dictionary-plausible words. It reports about 90% text recovery on font-corruption scenarios. It was evaluated on Microsoft Word PDFs only and fails where word forms vary (Arabic). | A5, A6 | B (peer-reviewed; one producer family) | Current state of the art *selects mappings by plausibility*, which is the "plausible-but-wrong" risk made explicit. No comparison with OCR is reported. |
| N9 | A commercial extractor (PDFlib TET; patent US7636885) resolves Unicode per glyph through an ordered cascade: external CMap, internal /ToUnicode, embedded font cmap, glyph names / Adobe Glyph List, heuristics. It maps unmappable glyphs to a replacement character, and documents that some PDFs "do not contain enough information" without user-supplied mapping tables. | A5, A6 | B (vendor docs + patent; not independent) | A defensible REMAP is per-glyph provenance: which source supplied each character. Auxiliary tables must be supplied by a person, so remapping is not automatic. |
| N10 | Designs that sample confirmed cases plus separately chosen controls inflate accuracy. Lijmer et al. 1999 found case-control diagnostic studies overestimated performance, with relative diagnostic odds ratio (RDOR) ≈ 3.0. Rutjes et al. 2006 found "severe cases + healthy controls" gave RDOR 4.9 (CI 0.6–37.3). Stratified evaluation needs inverse-inclusion weights to support population claims (Bennett & Carvalho 2010). | B3, B6 | A | The 79/121 oracle populations are two-gate / enriched designs. Population-level route accuracy claims need weights and a declared control spectrum. |
| N11 | Incorporation bias (QUADAS-2, domain 3; Rutjes 2006): if the reference standard shares information with the test being scored, agreement is inflated. | B5 | A | A "semantic route oracle" that shows annotators the same extracted-text channel the detector scores partly incorporates the index test. |
| N12 | Oracle units average 1.48 pages per document (121 units / 82 documents, stratum reading). Across the 20 historically labelled FIT documents, 6 oracle units exist and 0 fall inside the historical MD&A span. | B7, primary routing metric | B [REPO-VERIFIED]; historical spans are not Gold | Under ORACLE_ROUTING the document-level `page_span_iou` difference can move only through labelled pages. As registered, it is structurally near zero or undefined. |
| N13 | Large open PDF pretraining corpora now exist. FinePDFs (2025) has about 3T tokens and 475M documents from Common Crawl 2013–Feb 2025, including about 850k Hindi documents. Membership-inference tests on LLMs perform near chance (Duan et al., COLM 2024). | B8 | A (existence); D (ARPipe exposure) | Public-web exposure of annual reports is plausible. Model-training exposure of a *specific* PDF cannot be established or excluded with current tools, so it stays UNKNOWN. |
| N14 | NIST SP 800-185 standardizes injective tuple hashing (TupleHash) and domain separation (customization string). | B4 | A | A standard answer to the "canonical bytes" underspecification. It changes nothing material. |

---

## 3. Legacy-font / corrupted-text technical taxonomy

"Detection level" is the lowest level at which the mechanism is observable. "ARPipe today" is the frozen detector's behaviour, checked on fixtures where marked.

| # | PDF mechanism | Observable symptom (PyMuPDF default) | Detection level | Likely false-negative mode | Possible recovery | OCR suitability | Research status |
|---|---|---|---|---|---|---|---|
| M1 | **No /ToUnicode**, composite font (Type0 Identity-H/V), font program keeps cmap | Raw glyph codes as characters: printable shifted Latin plus some C0 controls | Font (code→Unicode map); page only if controls exceed 2% | Glyph IDs of 32 or more give printable garbage, so there are no controls. A mixed page dilutes the ratio. | Deterministic: glyph code → font cmap (R1). Fixture CER 0.00. | High (fixture CER 0.00) | A (spec); B [LOCAL]; corpus prevalence D |
| M2 | **No /ToUnicode**, subset font without cmap or glyph names | As M1 | Font | As M1 | None deterministic from PDF alone. Needs a glyph-shape match against a reference font, or OCR. | High | B [LOCAL]; corpus D |
| M3 | **Wrong /ToUnicode** (present and complete, maps to wrong Unicode; includes deliberate obfuscation) | Fluent-looking wrong letters, no controls | Font (/ToUnicode vs font cmap disagreement, needs cmap); span (lexicon) | Invisible to U+FFFD/control ratio and to script detection. Page lexicon rate dilutes on mixed pages. | R1 if cmap kept (fixture CER 0.00). Otherwise glyph-shape match or OCR. | High | B [LOCAL]; A that a wrong CMap renders correctly while extracting wrongly (E02 in repo) |
| M4 | **/ToUnicode to PUA** (or font cmap in PUA / symbol encoding) | PUA characters | Span/font (PUA share) | Not counted by `MOJIBAKE_RE`; the T0.1 proxy (>5 PUA) counts them but is swamped by benign icon/bullet PUA | Per-font table if the font is known, else OCR | High for text; icons have no text | B [LOCAL]; corpus benign share D |
| M5 | **ASCII-slot legacy script font** (Kruti Dev, Chanakya, Shusha…; cmap and /ToUnicode *agree* on Latin) | Fluent Latin-letter gibberish, `script=latin` | Font (family name, glyph names, rendering vs extraction); span (lexicon) | Invisible to ratio, script and cmap cross-check (all agree) | Per-family context-sensitive converter (LF-RECON §10–11); only if the family is identified | High with a Hindi model (fixture CER 0.09); Devanagari OCR is weaker on real scans (LF-RECON §13) | A (mechanism, LF-RECON); B [LOCAL]; corpus D |
| M6 | **Unicode complex-script font, correct but lossy /ToUnicode** (conjunct or reph glyphs unmapped; visual-order matras; ActualText absent) | Partly correct Devanagari with stray codepoints and wrong matra order | Span (script-aware validity checks on clusters) | Page often `digital`; script `mixed`/`devanagari` | Only via ActualText if present; otherwise OCR or a script-aware repair | High (fixture CER 0.00, hin) | A (W3C/Cunningham) + B [LOCAL]; matches the one verified corpus garble, C |
| M7 | **Ligature / multi-glyph mapping errors** (one glyph for several characters, or the reverse; presentation forms) | `ﬁ` or dropped letters | Span | Low per-page share, so undetectable at page level | Normalisation table (ARPipe `LIGATURE_FIXES` covers U+FB00–FB04 only) | High | A; ARPipe partial [REPO-VERIFIED] |
| M8 | **Simple font with custom /Encoding or /Differences and non-standard glyph names**, no /ToUnicode | Varies: correct via the Adobe Glyph List if names are standard; codes pass through if names are `g123`/`cid12`; ASCII-slot if names mislead | Font (/Differences names vs AGL) | Pass-through codes look like Latin | Glyph-name→Unicode via AGL; else as M2/M5 | High | A (PDF text-extraction cascade, patent N9); corpus D |
| M9 | **Type3 fonts** (glyphs as procedures) | Often no Unicode; codes or U+FFFD | Font | As M1 | Usually none; render + OCR | High | A (general); corpus D |
| M10 | **Pre-existing OCR text layer, invisible (render mode 3), wrong** (e.g. OmniPage, "Paper Capture") | Wrong but printable text over an image; page image-covered | Page (image area + invisible text); span (lexicon) | If ≥600 characters, `_classify` returns `digital` or `hybrid`; a wrong layer is read natively | Re-OCR; discard the layer | High | B [LOCAL] (fixture routed NATIVE); corpus: the INE008A01015_2025 broken pages are OmniPage-produced, C |
| M11 | **Glyphs drawn as vector paths** | No text | Page | Covered (`vector_text`) | None | High | Covered in repo |
| M12 | **Extractor-dependent failure** (a malformed-but-renderable CMap; library bug) | One library correct, another crashes or garbles | Library × font | Silent if only one library is used | Switch extractor or repair the CMap | High | B [LOCAL]: pypdf 3.17.4 crashed on MuPDF's 5-hex-digit /ToUnicode entries; pdfminer.six crashed on the full-font F02. "Broken" is partly extractor-relative. |
| M13 | **Mixed page**: any of M1–M10 in one font or region only | Mostly clean text | Font / span / region | Page ratio and page lexicon both dilute (N4) | As the underlying mechanism | High, if OCR is triggered | B [LOCAL]; corpus hint N5 |

**Is "legacy font" technically defensible?** (A1) As a *class name for a route*, no. It mixes four things:
- a historical font technology (M5);
- a PDF structural state (M1–M4, M8);
- a text symptom (gibberish);
- a detector category (`kind == broken_text`).

The external record (spec, vendor cascade, converter literature) supports it only as a **mechanism label for M5**, meaning a pre-Unicode ASCII-slot script font. If the name is kept, a defensible operational definition would be: *"a page region whose text-showing font is identified, by name, glyph names or rendered-vs-extracted comparison, as an ASCII-slot encoding of a non-Latin script."* Everything else in the table is **corrupted text-layer mapping**, not "legacy". Whether to rename is the author's call.

---

## 4. Legacy coverage gap analysis

Statuses: COVERED · PARTIALLY COVERED · UNCLEAR · NOT COVERED · NOT VERIFIED. "Covered" is never granted because a proxy label matches by definition.

| Historical/possible class | Current project classification | Current route | Coverage status | Evidence | What must be tested |
|---|---|---|---|---|---|
| `legacy_font_candidate` (T0.4, 803 pages) | ≡ `broken_text` by construction | OCR | COVERED *as a set*; mechanism content NOT VERIFIED | 803/803 [REPO-VERIFIED]; FIT+VAL 750 pages, 17 docs, 11 issuers, all `script=latin`; 395 from INE002A01018_2018 (Distiller 15), 188 from INE008A01015_2012 (Distiller 10) [REPO-VERIFIED] | Which of M1/M2/M9/M10 produced them. The Distiller-made pages are likely M1/M2 subset CID fonts, which is C. |
| M1/M2 missing /ToUnicode, glyph codes < 0x20 | `broken_text` | OCR | COVERED when the ratio exceeds 2% | Fixtures F01/F02 [LOCAL] | Nothing new |
| M1/M2 with codes ≥ 0x20, or diluted | `digital` | NATIVE_READ | NOT COVERED | N2, N5 [REPO-VERIFIED metadata; LOCAL] | Share of `digital` pages with a font lacking /ToUnicode (FIT) |
| M3 wrong /ToUnicode | `digital` | NATIVE_READ | NOT COVERED | F03/F03b [LOCAL] | Prevalence in FIT via cmap cross-check or lexicon-by-font |
| M4 PUA | `digital` | NATIVE_READ | NOT COVERED (text); benign icon PUA fine | F04 [LOCAL]; T0.1 audit: PUA mostly bullets (LF-RECON) | Separate text-PUA from icon-PUA by font |
| M5 ASCII-slot legacy (the P-B3 hypothesis) | `digital`, `script=latin` | NATIVE_READ | NOT COVERED | F05/F08/F09 [LOCAL]; user-supplied: ~225 of 437 P-B3 "confirmed" pages were `digital` [NOT VERIFIED] | Font family / glyph-name inspection on FIT (IDBI 2013–2024 is FIT and all-Latin by script; C) |
| M6 shaped Unicode Devanagari | `digital` (mixed/devanagari script) | NATIVE_READ | NOT COVERED | F11 [LOCAL]; corpus Devanagari only in HOLDOUT (2 docs) [REPO-VERIFIED via LF-RECON] | Nothing on HOLDOUT. Relevant only if FIT/VAL has Devanagari, which the frozen record says it does not. |
| M10 wrong invisible OCR layer | `digital`/`hybrid` | NATIVE_READ / OCR | PARTIALLY COVERED (only if chars < 600 → `hybrid`) | F10 [LOCAL]; OCR_layer proxy 189 pages / 98 docs (repo audit) | Lexicon or rendered-vs-text check on OCR-layer-proxy pages (FIT) |
| M13 mixed-font page (heading) | `digital` | NATIVE_READ | NOT COVERED | F06–F08 [LOCAL]; N5 [REPO-VERIFIED] | Font-level scan of candidate MD&A heading pages (FIT/VAL) |
| P-B3 "confirmed" & `broken_text` (~211) | `broken_text` | OCR | UNCLEAR (P-B3 definition unknown) | user-supplied [NOT VERIFIED] | Re-run P-B3 on frozen FIT, commit it |
| P-B3 "confirmed" & `digital` (~225) | `digital` | NATIVE_READ | UNCLEAR: consistent with M5/M3/M4 *or* with P-B3 false positives | user-supplied [NOT VERIFIED]; mechanism plausibility C | The same re-run plus independent font inspection of a sample |

**The contradiction (A9), stated precisely.** There are three claims:
1. `legacy_font_candidate == broken_text` [REPO-VERIFIED].
2. P-B3 font evidence flags pages across both `digital` and `broken_text` [user-supplied].
3. `broken_text → OCR` [REPO-VERIFIED].

They are **not inconsistent**, because they are about different predicates: a detector symptom, a font-evidence rule of unknown definition, and a route.

What *can* be claimed:
- every page the detector calls broken goes to OCR;
- mechanisms M3/M4/M5/M10/M13 cannot reach OCR through the current predicate (a code fact, confirmed on fixtures).

What *cannot* be claimed:
- that P-B3 "confirmed" pages are genuinely legacy;
- that the ~225 digital ones are misrouted;
- that the corpus contains M5 at all.

External research cannot resolve this. Only the P-B3 re-run and FIT font inspection can.

---

## 5. REMAP vs OCR evidence review

**Remapping is technically possible when** the correct character for each glyph code can be derived from evidence in the file or a known table, with provenance per glyph:
- **M1 and M3**, full font: the embedded cmap inverts glyph → Unicode. Fixture CER 0.00, fully deterministic.
- **M8**: standard glyph names map through the Adobe Glyph List.
- **M5**: the font family is identified and a context-sensitive converter exists (LF-RECON). Not possible when the family is unknown.

**It is unsafe when:**
- **The mapping is chosen by output plausibility** (REPDF-style dictionary selection, N8). That is exactly how plausible-but-wrong text is produced, and it cannot be audited against the source.
- **A table is applied beyond its precondition.** The fixture's own ASCII-slot table turned a clean English page into CER 0.52.
- **Glyphs never had cmap entries**: conjunct, reph and ligature glyphs produced by shaping (M6). A cmap inversion then has nothing to return.
- **The apparent corruption is an extractor bug** (M12). Remapping then "repairs" valid data.

**OCR is preferable when:**
- the font is subset without cmap or glyph names (M2);
- the script is shaped (M6);
- there is a Type3 font (M9) or an invisible OCR layer (M10);
- the corrupted text sits in a region of an otherwise clean page. Mixed pages need OCR of that region only; whole-page OCR is acceptable but wasteful.

On all fixtures OCR was as good as or better than native text (CER 0.00–0.09).

**Neither can be trusted without visual validation** for M5 when the family is unidentified, for ASCII-slot Devanagari where the OCR model is weak, and for numbers (the FinCriticalED note in `CLAUDE.md` already covers numeric risk).

**Preconditions that a REMAP experiment would need.** These are supported by the evidence above; they are not decisions.
1. **Verified corruption per font**, established without using the remap output. That avoids the circularity LF-RECON §12 already flags.
2. **A declared mechanism** (M1/M3/M5/M8) with its structural precondition checked: cmap present, glyph names standard, or family identified.
3. **Per-glyph provenance** recording which source supplied each character: the TET/PDFlib cascade model, N9.
4. **Abstention** on any glyph without a deterministic source. No plausibility-based filling.
5. **A round-trip check**, re-rendering or comparing against OCR on the same span, and a before/after diff.
6. **A negative-control run** on clean fonts of the same producer family, to show that remapping leaves them unchanged.
7. **A downstream endpoint**: heading recovery and MD&A boundary error, not only CER.

**What would justify opening LF-1.** It is already justified on the new evidence, and it can be read-only and metadata-plus-font only. The reason is no longer "is there a legacy font?". It is *"does the detector route corrupted text to native read on FIT pages?"*, which matters whether or not REMAP ever exists.

**What would justify leaving REMAP research-only permanently:**
- LF-1 finds no M5 in FIT, and the M1/M3 pages it finds are fully recovered by OCR;
- or no affected page intersects an MD&A candidate window or heading.

Either outcome makes REMAP a cost with no measurable downstream gain.

---

## 6. B1–B8 research delta

| B item | Already covered | New external / local evidence | Does anything materially change? | Remaining decision/question |
|---|---|---|---|---|
| B1 | No legacy class, identity with `broken_text`, no REMAP, one-class-OCR recommendation, forensic attribute proposal | N1–N7, taxonomy M1–M13 | **Yes, structurally.** The register and LF-RECON frame B1 as "legacy route vs OCR". The evidence adds a separate problem, **false-native routing of corrupted text**, which exists under every B1 option. A future "legacy" attribute should be a *font-level mechanism attribute*, distinct from the page detector symptom and from the route. | Whether B1's scope includes detector coverage (M3/M4/M5/M10/M13), or whether that becomes a separate item. The "REMAP research-only" choice is unaffected. |
| B2 | Precedence is not applicable under one class; do not reuse sampling priority | Mechanisms overlap on one page (M13); corrupted text can also sit on `hybrid` pages (M10) | Minor. If a font-level signal is ever added, a page can be `digital` by page detector and "corrupt" by font signal. A precedence or abstain rule is then needed. | Only if B1 adds any font-level signal. One OCR fallback can absorb every non-remappable mechanism (all fixtures OCR ≤ 0.09). |
| B3 | 79 vs 121; `native_clean_control` is not clean; estimand must be chosen | N10; recount: literal 79 has **0 native_ok units**; stratum 121 has 27 native_ok + 15 hybrid [REPO-VERIFIED] | **Yes.** Under the literal reading the false-NATIVE rate is inestimable, and that is where N3's failures live. Both readings are two-gate designs, so population accuracy claims need weights. | Choose the estimand: (a) route accuracy on detector-flagged pages; (b) false-native rate among detector-`digital` pages; (c) population route accuracy (needs weights). These are three different populations. |
| B4 | Independent full-digest rank; canonical bytes; no reuse of `selection_rank` | N14 (TupleHash / domain separation) | No | Only which canonical form. The two supplied documents disagree on the form (see Appendix A). |
| B5 | Pixels cannot diagnose encoding; semantic vs visual oracle | N11 incorporation bias; N6 (a shaped Unicode page looks perfect in pixels, like M5) | Small but real. A semantic oracle that shows the extracted-text channel partly incorporates what the detector scores. | Whether the detector's *input* channel may be shown to route annotators. If yes, report detector-vs-oracle agreement as not independent. |
| B6 | Hybrid random + diagnostic; do not pool unweighted | N10, N5 | Minor. It adds *what* the diagnostic stratum should be enriched on: an **independent font-level signal** (not the page detector), plus the 0.01–0.02 near-threshold band. | Rates and sizes remain author and budget decisions. |
| B7 | Region units with PRECEDES (reading order) | N12 | **Yes, for the routing ablation.** It is separate from the reading-order unit question. Page-level sparse oracle labels cannot drive a document-level `page_span_iou` contrast without an explicit page→document rule. | See section 7. |
| B8 | Default-deny forward governance; historical exposure UNKNOWN | N13 | No change to status. It sharpens *what kind* of unknown (section 8). | Whether any LLM/VLM component is in the evaluated system at all. If not, model exposure is irrelevant to ARPipe's claims. |

---

## 7. Annotation / evaluation alignment

**The mismatch, quantified [REPO-VERIFIED]:**
- `oracle_routing_spec.json` labels **pages** (Track A units: one lowest-rank page per coverage cell).
- The registered primary contrast is `paired page_span_iou difference ORACLE_ROUTING − ACTUAL_ROUTING`, a **document** metric.
- Stratum reading: 121 units in 82 documents, mean 1.48 labelled pages per document (max 3).
- In the 20 FIT documents with historical spans, **0 of 6** labelled pages are inside the span. Those historical spans are not Gold; this is a feasibility signal, not a result.

**Consequence.** ORACLE_ROUTING must assign a route to *every* page ARPipe reads. Unlabelled pages must default to ACTUAL, so the document difference can change only through the one to three labelled pages. Those pages are chosen by coverage cell, not by relevance to the span. The expected contrast is therefore close to zero by design, and a null result would say nothing about routing. **An explicit page→document transformation is required.** Three coherent alternatives follow; the choice is the author's.

1. **Dense window labels.** For documents in the ablation, route-label *every page in the MD&A candidate window* (for example candidate start − k to candidate end + k, fixed before routing). Document gold state = labelled window ∪ ACTUAL elsewhere, declared. The metric stays `page_span_iou`. Cost: roughly 15–40 pages per document instead of 1–3.
2. **Match the unit to the metric.** Make the primary routing metric page-level (route accuracy, false-NATIVE rate, weighted if a population claim is intended). Report the document-level ablation only as secondary, on the densely labelled subset.
3. **Sensitivity bound.** Keep sparse labels, and report the contrast only as "effect of correcting the labelled pages", with the number of labelled pages inside the predicted or gold span as a mandatory denominator.

**Other alignment points:**
- **Agreement.** For page routes, use a chance-corrected nominal coefficient on the double-annotated slice (S01–S03 in repo). For spans, boundary-based measures (S04–S06 in repo) such as start and end distance and boundary similarity are appropriate when the *number* of spans can differ (0, 1 or split MD&A). Plain page-IoU agreement is undefined when one annotator marks "absent", so presence needs its own agreement statistic. This is already recommended in the repo, and it still holds.
- **Sparse labels.** Do not impute unlabelled pages as NATIVE. Doing so hard-codes the detector's blind spot (section 4) into the gold.
- **Estimand.** Every routing number should state its population: detector-flagged, detector-digital, or weighted corpus (see B3).

---

## 8. HOLDOUT / contamination implications

| Category | Relevant to ARPipe? | What can be known | What cannot |
|---|---|---|---|
| 1. Project workflow (people saw HOLDOUT documents or outputs) | Yes | P2-26: at least three "holdout" referents; legacy eval queues and log exist; `labels_fit.csv` carries a `contaminated` column [REPO-VERIFIED]. Forward access can be logged. | Whether anyone's pre-T0 work informed current thresholds, heuristics or regexes (e.g. regex refinements made against named documents, as recorded for P33 in `CLAUDE.md`). History is UNKNOWN and stays so. |
| 2. Repository/history | Yes | Git history is auditable: which commits touched HOLDOUT document IDs or labels, and when | Whether an uncommitted local analysis used HOLDOUT |
| 3. Public-web exposure | Yes (documents are public by regulation) | Exchange and company sites host the PDFs. PDF-derived corpora exist at scale (FinePDFs: Common Crawl 2013–2025, about 850k Hindi docs). A **URL lookup** of HOLDOUT source locators in such a corpus's metadata is possible and metadata-only. | Presence in any closed model's training set |
| 4. Model-training exposure | **Only if an LLM/VLM is in the evaluated pipeline**: the LLM adjudication rung (no provider) and rung-3 Gemini OCR in `CLAUDE.md` | Nothing reliable: membership inference on LLMs is near chance (Duan 2024) | Whether a given model saw a given report or its MD&A. This is **unknowable**; state it as a limitation, not a yes or no. |
| 5. Evaluation-time leakage | Yes | Fully controllable forward: default-deny, blinded annotation, a single preregistered run (register B8 Option 1) | — |

For a deterministic heuristic system (regexes, XY-cut, heading rules), category 4 does not apply. It becomes relevant the moment an LLM or VLM locates or verifies spans. The same applies to exposure of *layout conventions*: a model may know typical Indian MD&A structure without having seen the specific PDF.

---

## 9. Genuinely necessary additions

Each item passes the test "omitting it risks a false coverage claim, an invalid evaluation or a wrong B1/B3/B7 conclusion".

1. **LF-1, re-scoped as a detector-coverage forensic (FIT only, read-only).**
   - **Why:** N3–N5 show the gap is detector coverage, not only legacy-vs-OCR.
   - **Question:** on FIT pages, what share of fonts, and of MD&A-candidate pages, carry each mechanism M1–M5, M10 and M13, and what route does ARPipe give them?
   - **Minimum evidence, per font on a sample of about 40–60 pages:**
     - /BaseFont, Subtype, /Encoding and /Differences names;
     - /ToUnicode presence and coverage;
     - whether cmap and glyph names are present, and the /ToUnicode-vs-cmap agreement;
     - font-grouped lexicon hit rate and PUA/control counts;
     - a rendered crop.
   - **Sample strata:**
     - pages from the 16 near-threshold documents (N5);
     - IDBI 2013–2024 FIT pages, which the historical record flags and which are all-Latin by script;
     - INE002A01018_2018 `broken_text`;
     - native controls.
   - **Deliverable:** a per-font mechanism table plus a crosswalk to route.
   - **Blocks:** closing B1; the B3 estimand choice; LF-2.
2. **Commit and re-run P-B3 on the frozen FIT corpus.**
   - **Why:** the only independent legacy signal is uncommitted, and its 437/225/211 split cannot be checked.
   - **Question:** what is P-B3's predicate, and how does it cross-tabulate with `kind` and with LF-1 mechanisms?
   - **Deliverable:** committed code, output and a confusion table against LF-1 labels.
   - **Blocks:** any claim that uses P-B3.
3. **Freeze the page→document rule for the routing ablation** (section 7) before Oracle annotation.
   - **Why:** otherwise the primary contrast is uninterpretable (N12).
   - **Deliverable:** one of the three alternatives, written into the spec.
   - **Blocks:** Oracle annotation roster and the B3/B7 records.
4. **Declare the estimand population for every routing number** (flagged / digital / weighted).
   - **Why:** N10, and the zero native_ok units under the literal reading.
   - **Deliverable:** a sentence per metric in `metrics_spec`.
   - **Blocks:** B3.
5. **Keep the synthetic fixture suite as a regression test** (the zip provided).
   - **Why:** any future detector or REMAP change must be shown against M1–M13 with known ground truth, and the suite exists now.
   - **Deliverable:** add it as a tests/fixtures module when authorized.
   - **Blocks:** nothing now; a prerequisite for LF-2.

Optional, not blocking: a metadata-only URL lookup of HOLDOUT source locators in FinePDFs, to characterise category 3 in section 8.

---

## 10. Explicit "do not add" list

- Generic OCR engine benchmarking, VLM comparisons, Devanagari OCR literature: covered by T0.4 preregistration and LF-RECON.
- More converter-tool surveys (lipi, krutiextract, SIL, Raj & Prahallad): covered in LF-RECON §10–12. Nothing changes until LF-1 finds M5.
- More ISO 32000 exposition beyond the taxonomy above: E01–E03 plus this table suffice.
- Agreement-coefficient literature (S01–S06), PAGE-XML / reading-order relations (E06, P04), annotation tooling (S09–S13): covered.
- More B4 hashing research: the constraints are proven; only a choice of form remains.
- A broad LLM-contamination review: category 4 is unknowable, and irrelevant unless an LLM/VLM is in the system.
- Any legacy-prevalence estimate from external literature: not transferable to the corpus by design.
- HOLDOUT Devanagari inspection: prohibited pre-freeze, and not needed for B1.

---

## 11. Final research queue

This is a research-order recommendation, not a ranking of methods.

| # | Task | Purpose | Input required | Output | Blocking status |
|---|---|---|---|---|---|
| 1 | Author scoping note for B1 | Decide whether detector coverage (false-native) is in B1 or a new item | This report §1–4 | One-line scope record | Blocks framing of LF-1 |
| 2 | P-B3 commit + re-run (FIT) | Make the only independent legacy signal auditable | P-B3 code, frozen FIT PDFs | Committed output + cross-tab vs `kind` | Blocks any P-B3-based claim |
| 3 | LF-1 re-scoped font forensic (FIT) | Mechanism prevalence and route per font; MD&A-relevance | FIT PDFs, the fixture suite as a validated instrument | Per-font mechanism table; crosswalk; decision rule result | Blocks B1 closure, B3 estimand, LF-2 |
| 4 | Page→document rule + estimand statements | Make the routing ablation interpretable | §7 alternatives, B3 choice | Spec amendment text (author-approved) | Blocks Oracle roster / annotation |
| 5 | LF-2 (conditional) REMAP-vs-OCR on verified M1/M3/M5 pages | Only if #3 finds remappable, MD&A-relevant pages | Verified pages; preconditions §5 | Paired CER + heading + boundary error | Non-blocking for the main thesis |

---

## 12. Source register

New sources only (not already in `research_source_register.csv` or the evidence matrix).

| Title | Authors / org | Year | Type | URL/DOI | Used for |
|---|---|---|---|---|---|
| PyMuPDF Constants: `TEXT_USE_CID_FOR_UNKNOWN_UNICODE` | Artifex / PyMuPDF | 2026 (live docs) | Official documentation | https://pymupdf.readthedocs.io/en/latest/vars.html | N2: raw codes are the default; U+FFFD only when toggled |
| PyMuPDF Discussion #3801 (garbled extraction) | PyMuPDF maintainers | 2024 | Issue tracker (maintainer statement) | https://github.com/pymupdf/PyMuPDF/discussions/3801 | "no way to determine the Unicode" without a back-reference; OCR as the way out |
| W3C WAI-GL: fonts without ToUnicode | L. Guarino Reid (Adobe) | 2004 | Standards mailing list | https://lists.w3.org/Archives/Public/w3c-wai-gl/2004JanMar/0249.html | Missing /ToUnicode leaves the glyph's character undeterminable |
| W3C WAI-IG: complex scripts, ActualText | A. Cunningham | 2016 | Expert mailing list (lead-level) | https://lists.w3.org/Archives/Public/w3c-wai-ig/2016JanMar/0037.html | M6: glyphs without Unicode values; cluster reordering; ActualText needed |
| US7636885B2: determining Unicode values for text in digital documents | PDFlib GmbH | 2005/2009 | Patent | https://patents.google.com/patent/US7636885 | N9: per-glyph source cascade |
| TET 5.3 manual | PDFlib GmbH | — | Vendor documentation | https://www.pdflib.com/fileadmin/pdflib/pdf/manuals/TET-5.3-manual.pdf | N9: unmapped → replacement; auxiliary tables needed |
| REPDF: Repairing corrupted PDF files through font mapping and object relationship reconstruction | Park, Jeong, Kim, Park; FSI: Digital Investigation 56 | 2026 | Peer-reviewed | https://www.sciencedirect.com/science/article/pii/S2666281726000181 | N8: plausibility-selected mapping; Word-only evaluation |
| Empirical evidence of design-related bias in studies of diagnostic tests | Lijmer et al., JAMA 282:1061 | 1999 | Peer-reviewed | https://pubmed.ncbi.nlm.nih.gov/10493205/ | N10: case-control designs overestimate accuracy (RDOR ≈ 3.0; figure from memory, abstract page not retrievable here, so verify before citing) |
| Evidence of bias and variation in diagnostic accuracy studies | Rutjes et al., CMAJ 174(4):469 | 2006 | Peer-reviewed | https://www.cmaj.ca/content/174/4/469 | N10/N11: severe-cases-plus-healthy-controls RDOR 4.9; reference standard independence |
| QUADAS-2 | Whiting et al., Ann Intern Med 155:529 | 2011 | Peer-reviewed tool | https://www.acpjournals.org/doi/10.7326/0003-4819-155-8-201110180-00009 | N11: reference-standard independence and incorporation (not fetched, 403; cited from standard knowledge, verify) |
| Online stratified sampling: evaluating classifiers at web-scale | Bennett & Carvalho, CIKM | 2010 | Peer-reviewed | https://dl.acm.org/doi/10.1145/1871437.1871677 | N10: weighted estimation under stratified evaluation samples |
| Do Membership Inference Attacks Work on Large Language Models? | Duan et al., COLM | 2024 | Peer-reviewed | https://arxiv.org/abs/2402.07841 | N13: MIAs near chance; apparent success from temporal shift |
| FinePDFs dataset card | Hugging Face FineWeb team | 2025 | Dataset documentation | https://huggingface.co/datasets/HuggingFaceFW/finepdfs | N13: PDF-derived pretraining corpora at scale, incl. Hindi |
| NIST SP 800-185 (cSHAKE, TupleHash) | NIST | 2016 | Standard | https://nvlpubs.nist.gov/nistpubs/specialpublications/nist.sp.800-185.pdf | N14 |
| Local fixture suite (`lf_fixture_suite.zip`) | this work | 2026 | Reproducible local experiment (synthetic) | attached | N3, N4, N6, N7, M12 |

ISO 32000-1 §9.10.2 (the order of Unicode derivation methods) and §9.9 (which TrueType tables CIDFontType2 needs) could not be retrieved in this session: the network blocked the download. The taxonomy relies on E01 already in the repo for /ToUnicode. The claim that a cmap is optional in embedded CIDFontType2 programs is marked C until checked against the spec text.

---

## Appendix A: contradictions between supplied documents

Reported, not resolved.

| # | Claim 1 (source) | Claim 2 (source) | Why it matters | Resolvable externally? |
|---|---|---|---|---|
| C1 | A U+FFFD detector at default PyMuPDF flags "detects nothing at all" (LF-RECON §7) | The detector regex also counts C0 controls, which fire on raw low codes (`patterns.py`); fixtures F01/F02 detected; 803 corpus pages detected (repo) | Overstating the detector's blindness hides *which* class it does catch | Resolved by code and fixture: LF-RECON is overstated. Its core point, that the detector cannot see M5, stands. |
| C2 | B4 "is not a decision. It is a bug" (Decision Sheet 17) | "This is not an identified implementation bug" (Register B4 / PHASE2_RESEARCH_B1_B8) | Governance: a "bug fix" framing bypasses author ratification | No; wording and governance. Both agree `selection_rank` must not be reused. |
| C3 | B4 form: first 4 bytes, `< 0.25·2^32`, `unit_id + "|" + salt` (Sheet) | Full 256-bit digest, `domain_tag ∥ document_id ∥ 0x00 ∥ page` (Register) | Both are valid. They must not be mixed. | No; author choice |
| C4 | B7 recommendation: LINE (Sheet) | Annotator-defined regions + PRECEDES (Register) | Tooling and metric definitions diverge | No; author choice |
| C5 | B3 recommendation: 106 units (Sheet) | Choose the estimand first; no number (Register) | 106 presumes the estimand (native control) | No; author choice. Note that 106 still has 27 native_ok units and no detector-digital enrichment. |
| C6 | P-B3: 2,075 pages; 78.3% clean native (routing clarification); 2,075 pages / 9 docs / 3 issuers, IDBI 99.66% (LF-RECON) | 437 confirmed; ~225 digital / ~211 broken (brief) | Different P-B3 subsets or definitions; 225 + 211 = 436 ≠ 437 | No; needs the P-B3 commit (queue #2) |
| C7 | Devanagari only in 2 HOLDOUT docs; 0 bilingual docs in T0 (LF-RECON) | Historical PNB/IDBI bilingual quarantine (8 docs) before the freeze (LF-RECON §2) | Corpus selection may have removed the documents most likely to hold M5 or M6. Frozen-corpus prevalence ≠ population prevalence. | No; a corpus-scope limitation to state |

## Appendix B: quality check

1. Repeated covered literature? No. Items covered in the repo or LF-RECON are referenced, not re-reviewed.
2. New legacy-font evidence? Yes: N1–N7 and M12. They are local and synthetic, not corpus evidence.
3. Legacy vs corrupted encoding distinguished? Yes (§3, A1).
4. Missing / malformed / wrong /ToUnicode? Yes: M1–M4, M12.
5. Mixed healthy/corrupted fonts? Yes: M13, F06–F09, N5.
6. Page vs font/region detection? Yes: N4, §3 detection-level column.
7. Remap vs OCR? Yes (§5).
8. Remap failure modes? Yes: blind table, plausibility selection, shaped glyphs, extractor bugs.
9. Synthetic suite useful? Yes. It is built, and it already changed a conclusion (C1).
10. External prevalence kept separate from corpus? Yes. Every corpus prevalence stays D.
11. Page-level oracle vs document metric? Yes: N12, §7.
12. Annotation/agreement only where needed? Yes.
13. B8 exposure kept UNKNOWN? Yes (§8).
14. No B1–B8 decisions made? Yes. Options only.
15. Only necessary additions? Five, each with a blocking rationale.
16. No general ARPipe literature review? Yes.
