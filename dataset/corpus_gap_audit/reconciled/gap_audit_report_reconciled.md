# T0 vs T0.1 reconciliation

This section documents the formal methodological reconciliation between the frozen T0 corpus baseline (`23d6228`) and the T0.1 RAW gap audit (`b6b76d9`).

Key definition and construct differences reconciled across phases:
- **Native representation**: T0 classified 151 whole documents as native digital; T0.1 measured presence of any native text page, detecting native text in 191 documents (36,988 pages) [CLAIM:C005] [CLAIM:C006]. Whole-document pure native representation comprises exactly 60 documents.
- **Scanned documents**: T0 marked 5 documents as scanned based on prior external ground truth. Canonical T0.1 evidence demonstrates that exactly 2 documents are fully scanned (91 pages: `INE002L01015_2012` [43 pgs], `INE003B01014_2011` [48 pgs]) [CLAIM:C029]. Reliance `INE002A01018_2018` is 447 native pages with 395 legacy font pages, not scanned. 63 documents contain at least 1 scanned page (284 pages).
- **Mixed representation**: In `gap_audit_document.csv`, mixed representation comprises exactly 132 documents (34 issuers, 30,132 pages) [CLAIM:C019]. The narrative report's figure of 101 reflected an ungrounded filter.
- **OCR text layer**: T0 inferred 17 OCR documents from producer software strings; T0.1 detected render mode 3 or OCR signatures on at least 1 page in 98 documents (189 pages) [CLAIM:C020] [CLAIM:C021]. This is an auxiliary heuristic proxy, not verified OCR layer quality.
- **Legacy fonts**: T0 inferred 24 legacy font documents; T0.1 expanded codepoint sweep to detect replacement characters or Private Use Area codepoints on 1,007 pages across 56 documents [CLAIM:C030] [CLAIM:C031].
- **Table of Contents**: T0 recorded 90 documents with PDF outline bookmarks; T0.1 searched printed text within the first 30 pages, detecting printed TOC keywords in 174 documents [CLAIM:C017]. Exactly 20 documents yielded no TOC keyword under the detector's search rule [CLAIM:C036].

# Claim audit summary

An exhaustive audit of all 58 material claims from the T0.1 audit report was performed. Results are recorded in `claim_audit.csv` with machine-executable calculations and semantic anchors.

| Audit Status | Claim Count | Description |
| :--- | :--- | :--- |
| **SUPPORTED** | 20 | Fully verified against canonical immutable artifacts |
| **SUPPORTED_WITH_QUALIFICATION** | 8 | Factually accurate but requires construct qualification |
| **CANDIDATE_ONLY** | 16 | Heuristic detector proxy signal; semantic ground truth unverified |
| **OVERSTATED** | 13 | Narrative assertion exceeded or contradicted canonical artifact evidence |
| **UNSUPPORTED** | 1 | Completely contradicted by underlying implementation evidence |
| **UNKNOWN / UNRESOLVED** | 0 | No unresolvable contradictions remain in canonical artifacts |

# Supported claims

- The executable corpus contains exactly 194 PDF files across 36 distinct corporate issuers [CLAIM:C001] [CLAIM:C002].
- Exactly 14 historical records exist in legacy logs but lack physical bytes [CLAIM:C003].
- Total physical pages verified equals 37,917 pages [CLAIM:C004].
- Two-column layout candidates occur in 184 documents (15,015 pages) [CLAIM:C007] [CLAIM:C008].
- Multi-column layout candidates occur in 191 documents (17,190 pages) [CLAIM:C009] [CLAIM:C010].
- Running header candidate pages number 6,980 pages across 84 documents [CLAIM:C014].
- Running footer candidate pages number 8,902 pages across 90 documents [CLAIM:C016].
- Devanagari script pages number 2 pages across 2 documents belonging to 1 single issuer [CLAIM:C023] [CLAIM:C024].
- Bilingual candidate pages number 2 pages across 2 documents [CLAIM:C026].
- Long report median is 165.0 pages, mean is 195.45 pages, Q1 is 92.75 pages, Q3 is 249.25 pages, max is 661 pages [CLAIM:C039] [CLAIM:C040] [CLAIM:C041] [CLAIM:C042] [CLAIM:C045].
- Devanagari script is completely absent from the Development set [CLAIM:C052].
- Zero PDF acquisition is required for the Core ARPipe Thesis [CLAIM:C056].
- Default posture for optional robustness extensions is additional audit before acquisition [CLAIM:C057].
- Exactly 2 stub filings exist in the corpus [CLAIM:C058].

# Candidate-only claims

- **Table candidates**: 190 documents (29,476 pages) exhibit vector lines or aligned numbers [CLAIM:C011] [CLAIM:C012]. These are candidate signals; semantic tabular topology remains unverified.
- **Annexure candidates**: 188 documents contain the word 'annexure' [CLAIM:C018]. Keyword presence does not prove structural annexure embedding of MD&A.
- **OCR layer candidates**: 98 documents (189 pages) trigger render mode 3 or OCR software metadata proxies [CLAIM:C020] [CLAIM:C021].
- **Legacy font candidates**: 56 documents (1,007 pages) trigger replacement character or PUA codepoint heuristics [CLAIM:C030] [CLAIM:C031].
- **Duplicate text candidates**: 35 documents (68 pages) exhibit bounding-box overlaps [CLAIM:C032] [CLAIM:C033].
- **Hidden text candidates**: 3 documents (4 pages) have sub-point font sizes (< 0.5 pt) [CLAIM:C027] [CLAIM:C028].
- **Combined MD&A candidates**: 44 documents have combined heading patterns [CLAIM:C037].

# Overstated claims corrected

- **Mixed document representation**: Corrected from narrative claim of 101 docs to 132 docs in `gap_audit_document.csv` [CLAIM:C019].
- **Fully scanned documents**: Corrected from narrative claim of 5 docs / 804 pages to exactly 2 documents (91 pages) in `gap_audit_document.csv` [CLAIM:C029].
- **Table dominance**: Corrected from 'tables dominate document area' to 'table-like signals occur on most pages under current heuristic; true table prevalence is unverified' [CLAIM:C049].
- **Running furniture universality**: Corrected from 'universal and alternating' to 'detected in about half of documents (84 headers, 90 footers)' [CLAIM:C050].
- **TOC offset resolution**: Corrected from '24 docs with >=3 matches' to exactly 2 documents with support >= 3 in `toc_offset_candidates.csv` [CLAIM:C034].
- **TOC offset unresolved**: Corrected from '150 diagnosed failures' to 4 unresolved cases in 45 assessed files; 149 documents were unassessed [CLAIM:C035].
- **Long report percentiles**: Corrected P90 from 332.80 to 387.3 pages, and P95 from 411.35 to 460.35 pages [CLAIM:C043] [CLAIM:C044].
- **Long report minimum**: Corrected min from 32 pages to 1 page (incorporating stub files) [CLAIM:C038].
- **Long reports count**: Corrected from narrative claim of 58 docs / 36 issuers to 48 docs across 20 issuers in `gap_audit_document.csv` [CLAIM:C046].
- **Annexure structural ubiquity**: Corrected from universal MD&A annexure structure to generic keyword occurrence [CLAIM:C053].
- **Model review status**: Corrected from verified MODEL_REVIEWED to NOT_REVIEWED [CLAIM:C054].
- **Acquisition recommendation**: Corrected from arbitrary recommendation of 10-12 PDFs to claim-dependent partition [CLAIM:C055].

# Unresolved evidence

All quantitative discrepancies between historical narrative text and machine-readable artifacts have been successfully reconciled against the canonical CSV/JSON artifacts.
Zero unresolvable quantitative contradictions remain within the canonical data. However, semantic ground truth for table cell spanning trees, actual text layer OCR accuracy on degraded scans, and complete TOC offsets across the 149 unassessed documents remain unmeasured and are preserved as unverified candidate evidence.

# Model-review provenance correction

Inspection of `tools/apply_model_review.py` revealed that candidate review records were automatically updated to `MODEL_REVIEWED` by formatting JSON string snippets without performing any active model inference or page image inspection [CLAIM:C054].
- Exactly 72 candidate records in `manual_review_results.csv` were affected by this automatic relabelling.
- In `manual_review_results_reconciled.csv`, each record was evaluated row-by-row and truthfully corrected to: `reconciled_verification_status = NOT_REVIEWED`, `reconciled_reviewer_type = NONE`, `review_provenance_issue = AUTO_RELABELLED_WITHOUT_MODEL_INSPECTION`.
- Actual human review metrics are truthfully reported: `human_reviewed_count = 0`, `human_confirmed_count = 0`, `human_false_positive_count = N/A`, `human_uncertain_count = N/A`.

# Table interpretation

The raw T0.1 heuristic detected table-like signals in 190 documents spanning 29,476 pages (77.7% of all corpus pages) [CLAIM:C011] [CLAIM:C012].
**Reconciled scientific interpretation**: Table-like vector lines or numeric-line signals occur on most pages and in most documents under the current heuristic; true semantic table prevalence is unverified [CLAIM:C049].
The prior assertion that 'tables dominate document area' is retracted as an unverified semantic conclusion. Quarantine logic is warranted as an architectural defense, but true table extraction benchmarks cannot be claimed.

# Annexure interpretation

The word 'annexure' was detected in 188 documents across 36 issuers [CLAIM:C018].
**Reconciled scientific interpretation**: The evidence confirms only that the keyword 'annexure' is ubiquitous in Indian annual reports. It does NOT prove that MD&A specifically is universally structured as an annexure [CLAIM:C053].
The illustrative heading 'Annexure A to the Directors Report: Management Discussion and Analysis' from the original report was an unverified narrative example and is retracted. MD&A-as-annexure remains an unverified candidate hypothesis.

# Header/footer interpretation

Repetitive running headers were detected in 84 documents (6,980 pages) [CLAIM:C013] [CLAIM:C014] and running footers in 90 documents (8,902 pages) [CLAIM:C015] [CLAIM:C016].
**Reconciled scientific interpretation**: Running header or footer candidates were detected in about half of documents under the current repetition heuristic [CLAIM:C050].
The original assertion that running furniture is 'universal' across all documents and 'alternating between left and right pages' is retracted as unsupported by the raw detector output.

# TOC interpretation

Printed TOC keywords were detected in 174 documents [CLAIM:C017], while 20 documents yielded no keyword match within the first 30 pages [CLAIM:C036].
In `toc_offset_candidates.csv`, only 45 documents were evaluated by the offset matcher:
- Exactly 2 documents have strong multi-entry support (>= 3 matches: `INE009A01021_2018` [support=5], `INE040A01034_2025` [support=6]) [CLAIM:C034].
- 22 documents produced preliminary candidate offsets (often supported by only 1 match).
- 4 documents were unresolved matcher cases [CLAIM:C035].
- 149 documents were unassessed by the offset matcher and must not be interpreted as diagnosed offset failures.
MD&A boundary discovery must operate independently of printed TOC resolution [CLAIM:C051].

# OCR/legacy interpretation

98 documents contain candidate OCR text layer proxies (189 pages) [CLAIM:C020] [CLAIM:C021], and 56 documents contain legacy font candidates (1,007 pages) [CLAIM:C030] [CLAIM:C031].
These signals remain at the candidate proxy level. An OCR layer proxy (render mode 3) indicates that invisible text exists over an image, but does not measure character recognition accuracy. Legacy font codepoint anomalies (U+FFFD, PUA) indicate font table corruption, but full font repair evaluation requires downstream parsing benchmarks.

# Scanned-document interpretation

Canonical evidence in `gap_audit_document.csv` confirms that exactly 2 documents are fully scanned (91 pages across 2 issuers: `INE002L01015_2012` [43 pgs] and `INE003B01014_2011` [48 pgs]) [CLAIM:C029].
63 documents contain at least 1 raster-scanned page (284 total scanned pages).
The narrative claim of '5 fully scanned documents / 804 pages' resulted from uncritically repeating prior unverified T0 labels. Reliance `INE002A01018_2018` is 447 native pages with legacy font issues, not scanned. `INE004C01028_2024` is mixed (67 scanned, 1 native). `INE009A01021_2013` is native digital prose.

# Hindi/bilingual interpretation

Devanagari script is confirmed in exactly 2 documents across 1 issuer (`INE002L01015_2024` and `INE002L01015_2025`), spanning exactly 2 physical pages [CLAIM:C022] [CLAIM:C023] [CLAIM:C024].
`language_candidates.csv` confirms that Devanagari is restricted to 116 characters on page index 0 (the cover page letterhead/statutory notice) of SJVN Limited. The remaining report body is entirely English prose. No fully bilingual annual report exists in the corpus.
Devanagari is completely absent from FIT, VALIDATION, and the Development set [CLAIM:C052].

# Interaction-metric semantics

In `interaction_gap_matrix_reconciled.csv`, the column previously labeled `page_count` has been renamed to `total_pages_in_docs_meeting_both` [CLAIM:C047] [CLAIM:C048].
This metric represents the sum of all physical pages across documents satisfying both document-level conditions; it is not a page-level intersection.
Furthermore, inspection of the frozen historical implementation in `tools/audit_corpus_gaps.py` (function `generate_audit_artifacts`) confirms that the interaction `ocr_layer_candidate x scanned_or_mixed` (98 docs, 23,877 pages) represents a **KNOWN_DEPENDENCY** (rather than an unassessed co-occurrence or a strict two-way tautology): `ocr_layer_candidate` (an auxiliary heuristic proxy, not a validated OCR detector) with `ocr_page_count > 0` definitionally entails `scanned_or_mixed` representation under the document classification rules, though the converse does not hold definitionally [CLAIM:C048].

# Stub/hygiene limitations

Under the frozen T0.1R reconciliation rules, documents with `total_pages <= 2` are classified as `STUB`, while documents with `total_pages > 2` are classified as `STANDARD`.
Exactly 2 stub filings exist in the corpus (`INE00FF01025_2015` [1 page] and `INE00LO01017_2015` [2 pages]) [CLAIM:C058].
These documents represent historical filing stubs or cover notices. In accordance with strict immutability, they are preserved as full members of the frozen T0 corpus and flagged as `corpus_hygiene_flag = STUB` in `gap_audit_document_reconciled.csv`.
All summary statistics and percentile distributions reported herein include these stub documents, yielding an authentic minimum page count of 1 [CLAIM:C038].

# Corpus findings that change design assumptions

1. **Table quarantine is essential, but table prevalence is unverified**: Table candidate signals occur widely (190 docs), requiring geometric quarantine to protect prose extraction streams, though semantic table topology remains unverified [CLAIM:C049].
2. **Running furniture removal requires coordinate stability**: Present in ~45% of corpus (84 headers, 90 footers); coordinate stability across adjacent pages is necessary, but multi-line alternating universality was unmeasured [CLAIM:C050].
3. **TOC cannot gate MD&A localization**: Only 2 documents have strong multi-entry candidate offsets (support >= 3); heading localization must proceed independently of TOC resolution [CLAIM:C051].
4. **Hindi support is irrelevant for core English extraction**: Confined to letterhead headers in 1 issuer; pipeline development for English MD&A requires zero Hindi capability [CLAIM:C052].
5. **Annexure grammar must anticipate compound titles**: Generic keyword prevalence (188 docs) warrants heading grammar supporting annexure prefixes, though MD&A-as-annexure remains candidate evidence [CLAIM:C053].

# Core-thesis acquisition decision

**DECISION: NO ACQUISITION JUSTIFIED FOR CORE ARPIPE THESIS [CLAIM:C056].**
The scientific goal of ARPipe is the robust boundary localization and clean text extraction of English-language MD&A sections from Indian corporate filings.
No additional acquisition is currently justified for the core thesis under the predefined claim scope and available evidence. Targeted acquisition may remain an optional robustness extension for explicitly defined edge-case claims.
The current corpus provides:
- 191 documents containing native digital prose across 36 diverse issuers and 8 fiscal years [CLAIM:C001] [CLAIM:C002] [CLAIM:C005].
- 191 multi-column layout documents challenging reading order reconstruction [CLAIM:C009].
- 190 table candidate documents challenging tabular quarantine [CLAIM:C011].
- 48 documents exceeding 250 pages (max 661 pages) challenging memory and document scaling [CLAIM:C045] [CLAIM:C046].
No additional acquisition is currently justified for the core thesis under the predefined claim scope and available evidence. Targeted acquisition may remain an optional robustness extension for explicitly defined edge-case claims.

# Optional robustness acquisition decision

**DECISION: ADDITIONAL AUDIT AND HYPOTHESIS SPECIFICATION REQUIRED BEFORE ANY ROBUSTNESS ACQUISITION [CLAIM:C057].**
If a future research phase elects to evaluate secondary robustness extensions beyond the core thesis:
- **Bilingual/Hindi extension**: Currently 2 documents (1 issuer) in HOLDOUT. Acquisition of bilingual filings is justified ONLY IF an explicit dual-script research hypothesis and pre-specified evaluation metric are formulated.
- **Historical scanned filings**: Currently 2 fully scanned documents + 63 documents with scanned pages. Acquisition of pre-2010 filings is justified ONLY IF existing scanned pages prove insufficient to benchmark the OCR ladder.
The previous recommendation of acquiring '10-12 PDFs' without a pre-specified hypothesis is retracted [CLAIM:C055].

# Exact limitations

1. **T0.1R is a reconciliation, not a new audit**: T0.1R performed zero raw PDF inspections and executed zero new detectors.
2. **Candidate signals are not ground truth**: Table, header, footer, TOC, annexure, and OCR counts represent heuristic proxy detections.
3. **Absence of human gold annotations**: Human review was not performed in T0.1 (`human_reviewed_count = 0`), and false positive rates remain unmeasured.
4. **TOC offset coverage**: Only 45 documents were evaluated by the historical offset matcher; offset accuracy across the remaining 149 documents is unknown.
5. **Statistical generalizability**: Findings characterize the frozen 194-PDF extraction corpus; generalization to the broader population of 5,000+ Indian public companies requires formal out-of-sample evaluation.
