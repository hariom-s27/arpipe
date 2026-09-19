# ARPipe T0.3A-R1 Report-Era Coverage Taxonomy Extension Plan & Report

## 1. Executive Summary & Baseline Verification

- **Base Commit**: `02bae116a6616d3a8637323dffe2fb27d36304f1`
- **Frozen Core-Thesis Invariant**: `NO_ACQUISITION`
- **Acquisition Status in T0.3A-R1**: `NO_ACQUISITION` (Coverage audit only; zero acquisition decisions)
- **Total Dimensions Analyzed**: 10
- **Total Taxonomy Categories**: 35
- **Dynamically Verified Non-Era Categories**: 33 (Preserved field-for-field against frozen T0.3A)
- **Status Counts**: `PRESENT` = 25, `SPARSE` = 6, `ABSENT` = 2, `NOT_ASSESSABLE` = 2

> [!IMPORTANT]
> **Coverage Does NOT Mean Sufficiency**:
> `coverage_status` describes observed representation only. It does not establish whether the representation is sufficient or insufficient for a robustness claim.
> T0.3A-R1 answers: What do we have? What is sparse? What is absent? What cannot be measured? It does NOT make acquisition recommendations.

## 2. Report-Era Coverage Dimension & Valid-Fiscal-Year Completeness

> The report-era coverage dimension uses two pre-specified complementary categories: pre-2015 and post-2015. Pre-2015 is directly relevant to the historical robustness scope inherited from T0.2. Post-2015 is included as the complementary category so that the era dimension describes the temporal composition of the full corpus. This statement applies to documents with valid fiscal_year values.

### Invariants & Non-Sufficiency Guarantees:
- **Coverage Extension Only**: Does NOT establish robustness sufficiency.
- **No Era Equivalence**: Does NOT claim that pre-2015 and post-2015 eras are equivalent or homogeneous.
- **No Era Superiority**: Does NOT claim that one era is better or more representative than the other.
- **No Acquisition Decision**: Zero acquisition decisions made.

### Valid-Fiscal-Year Empirical Completeness:
- **Total Corpus Documents**: 194
- **Documents with Valid Integer Fiscal Year**: 194
- **Missing or Invalid Fiscal Year Count**: 0
- **Era Disjointness (`pre_2015 ∩ post_2015`)**: 0 (Empty = True)
- **Valid-Fiscal-Year Union Completeness (`pre_2015 ∪ post_2015`)**: True
- `pre_2015` Derived: 58 docs, 6863 pages, 29 issuers (26 FIT / 14 VAL / 18 HOLDOUT)
- `post_2015` Derived: 136 docs, 31054 pages, 36 issuers (66 FIT / 34 VAL / 36 HOLDOUT)

## 3. Coverage Matrix Summary Table

| Dimension | Category | Evidence Level | Docs | Pages | Issuers | Split (F/V/H) | Status | Coverage Basis |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `document_representation` | `native` | `EXISTING_CONDITION` | 60 | 7694 | 29 | 30/16/14 | **PRESENT** | Observed in 60 documents across 29 issuers; no frozen source... |
| `document_representation` | `mixed` | `EXISTING_CONDITION` | 132 | 30132 | 34 | 61/32/39 | **PRESENT** | Observed in 132 documents across 34 issuers; no frozen sourc... |
| `document_representation` | `scanned` | `EXISTING_CONDITION` | 2 | 91 | 2 | 1/0/1 | **SPARSE** | Observed in 2 documents across 2 issuers; explicitly charact... |
| `fully_scanned_vs_mixed` | `fully_scanned_document` | `EXISTING_CONDITION` | 2 | 91 | 2 | 1/0/1 | **SPARSE** | Observed in 2 documents across 2 issuers; explicitly charact... |
| `fully_scanned_vs_mixed` | `mixed_scanned_pages` | `EXISTING_CONDITION` | 61 | 14150 | 29 | 27/15/19 | **PRESENT** | Observed in 61 documents across 29 issuers; no frozen source... |
| `fully_scanned_vs_mixed` | `scanned_pages_in_validation` | `EXISTING_CONDITION` | 0 | 0 | 0 | 0/0/0 | **ABSENT** | Zero instances observed in frozen corpus under predicate 'do... |
| `report_era` | `pre_2015` | `VALIDATED_METADATA` | 58 | 6863 | 29 | 26/14/18 | **PRESENT** | Observed in 58 documents across 29 issuers; no frozen source... |
| `report_era` | `post_2015` | `VALIDATED_METADATA` | 136 | 31054 | 36 | 66/34/36 | **PRESENT** | Observed in 136 documents across 36 issuers; no frozen sourc... |
| `ocr_layer_presence` | `has_ocr_layer_pages` | `CANDIDATE_PROXY` | 98 | 23877 | 31 | 47/24/27 | **PRESENT** | Observed in 98 documents across 31 issuers; no frozen source... |
| `ocr_layer_presence` | `no_ocr_layer_pages` | `CANDIDATE_PROXY` | 96 | 14040 | 34 | 45/24/27 | **PRESENT** | Observed in 96 documents across 34 issuers; no frozen source... |
| `language_script` | `devanagari_candidate` | `CANDIDATE_PROXY` | 2 | 494 | 1 | 0/0/2 | **SPARSE** | Observed in 2 documents across 1 issuers; explicitly charact... |
| `language_script` | `bilingual_candidate` | `CANDIDATE_PROXY` | 2 | 494 | 1 | 0/0/2 | **SPARSE** | Observed in 2 documents across 1 issuers; explicitly charact... |
| `language_script` | `no_devanagari_candidate` | `CANDIDATE_PROXY` | 192 | 37423 | 36 | 92/48/52 | **PRESENT** | Observed in 192 documents across 36 issuers; no frozen sourc... |
| `language_script` | `devanagari_in_fit_or_validation` | `CANDIDATE_PROXY` | 0 | 0 | 0 | 0/0/0 | **ABSENT** | Zero instances observed in frozen corpus under predicate 'in... |
| `legacy_or_broken_text` | `legacy_font_candidate` | `CANDIDATE_PROXY` | 56 | 13377 | 24 | 30/10/16 | **PRESENT** | Observed in 56 documents across 24 issuers; no frozen source... |
| `legacy_or_broken_text` | `duplicate_text_candidate` | `CANDIDATE_PROXY` | 35 | 8625 | 18 | 20/8/7 | **PRESENT** | Observed in 35 documents across 18 issuers; no frozen source... |
| `legacy_or_broken_text` | `hidden_text_candidate` | `CANDIDATE_PROXY` | 3 | 875 | 3 | 3/0/0 | **SPARSE** | Observed in 3 documents across 3 issuers; explicitly charact... |
| `document_size` | `size_short` | `VALIDATED_METADATA` | 49 | 2963 | 15 | 23/15/11 | **PRESENT** | Observed in 49 documents across 15 issuers; no frozen source... |
| `document_size` | `size_medium` | `VALIDATED_METADATA` | 96 | 16146 | 31 | 44/23/29 | **PRESENT** | Observed in 96 documents across 31 issuers; no frozen source... |
| `document_size` | `size_long` | `VALIDATED_METADATA` | 29 | 8977 | 17 | 12/8/9 | **PRESENT** | Observed in 29 documents across 17 issuers; no frozen source... |
| `document_size` | `size_very_long` | `VALIDATED_METADATA` | 10 | 4299 | 9 | 5/2/3 | **PRESENT** | Observed in 10 documents across 9 issuers; no frozen source ... |
| `document_size` | `size_extreme` | `VALIDATED_METADATA` | 10 | 5532 | 7 | 8/0/2 | **PRESENT** | Observed in 10 documents across 7 issuers; no frozen source ... |
| `document_size` | `stub_filing` | `VALIDATED_METADATA` | 2 | 3 | 2 | 2/0/0 | **SPARSE** | Observed in 2 documents across 2 issuers; explicitly charact... |
| `layout_and_structure` | `two_column_layout` | `CANDIDATE_PROXY` | 184 | 37278 | 36 | 87/47/50 | **PRESENT** | Observed in 184 documents across 36 issuers; no frozen sourc... |
| `layout_and_structure` | `multi_column_layout` | `CANDIDATE_PROXY` | 191 | 37667 | 36 | 91/47/53 | **PRESENT** | Observed in 191 documents across 36 issuers; no frozen sourc... |
| `layout_and_structure` | `table_candidate` | `CANDIDATE_PROXY` | 190 | 37599 | 36 | 90/47/53 | **PRESENT** | Observed in 190 documents across 36 issuers; no frozen sourc... |
| `layout_and_structure` | `running_furniture_candidate` | `CANDIDATE_PROXY` | 125 | 27718 | 34 | 54/34/37 | **PRESENT** | Observed in 125 documents across 34 issuers; no frozen sourc... |
| `layout_and_structure` | `combined_mdna_candidate` | `CANDIDATE_PROXY` | 44 | 10066 | 22 | 21/11/12 | **PRESENT** | Observed in 44 documents across 22 issuers; no frozen source... |
| `layout_and_structure` | `annexure_candidate` | `CANDIDATE_PROXY` | 188 | 37487 | 36 | 88/47/53 | **PRESENT** | Observed in 188 documents across 36 issuers; no frozen sourc... |
| `layout_and_structure` | `toc_candidate` | `CANDIDATE_PROXY` | 174 | 34924 | 36 | 81/45/48 | **PRESENT** | Observed in 174 documents across 36 issuers; no frozen sourc... |
| `layout_and_structure` | `no_toc_keyword_candidate` | `CANDIDATE_PROXY` | 20 | 2993 | 14 | 11/3/6 | **PRESENT** | Observed in 20 documents across 14 issuers; no frozen source... |
| `coverage_intersections` | `scanned_with_multi_column` | `DERIVED_INTERACTION` | 61 | 14150 | 29 | 27/15/19 | **PRESENT** | Observed in 61 documents across 29 issuers; no frozen source... |
| `coverage_intersections` | `scanned_with_table_candidate` | `DERIVED_INTERACTION` | 60 | 14082 | 28 | 26/15/19 | **PRESENT** | Observed in 60 documents across 28 issuers; no frozen source... |
| `evidence_limitations` | `ocr_transcription_quality` | `UNMEASURED` | 0 | 0 | 0 | 0/0/0 | **NOT_ASSESSABLE** | Property is unmeasured in frozen artifacts; requires future ... |
| `evidence_limitations` | `scanned_heading_localization_error` | `UNMEASURED` | 0 | 0 | 0 | 0/0/0 | **NOT_ASSESSABLE** | Property is unmeasured in frozen artifacts; requires future ... |

## 4. Gap Register & Limitations

| Dimension | Category | Status | Downstream Relevance | Known Limitation |
| :--- | :--- | :--- | :--- | :--- |
| `document_representation` | `native` | **PRESENT** | `CORE` | Whole-document representation assigned by T0.1R reconciliation based o... |
| `document_representation` | `mixed` | **PRESENT** | `ROBUSTNESS` | Document contains both native digital text and raster/scanned pages or... |
| `document_representation` | `scanned` | **SPARSE** | `ROBUSTNESS` | Document contains 100% scanned raster pages without native digital fon... |
| `fully_scanned_vs_mixed` | `fully_scanned_document` | **SPARSE** | `ROBUSTNESS` | Confirmed 100% scanned raster filings across full document extent (2 d... |
| `fully_scanned_vs_mixed` | `mixed_scanned_pages` | **PRESENT** | `ROBUSTNESS` | Documents classified as MIXED that contain at least 1 scanned raster p... |
| `fully_scanned_vs_mixed` | `scanned_pages_in_validation` | **ABSENT** | `ROBUSTNESS` | Intersection of document_representation == SCANNED and split == VALIDA... |
| `report_era` | `pre_2015` | **PRESENT** | `ROBUSTNESS` | Historical corporate reporting era prior to 2015; specifically identif... |
| `report_era` | `post_2015` | **PRESENT** | `CORE` | Modern corporate reporting era from fiscal year 2015 onward, included ... |
| `ocr_layer_presence` | `has_ocr_layer_pages` | **PRESENT** | `ROBUSTNESS` | Proxy heuristic detection based on PDF render mode 3 (invisible text l... |
| `ocr_layer_presence` | `no_ocr_layer_pages` | **PRESENT** | `ROBUSTNESS` | Documents with zero pages flagged by render mode 3 proxy heuristic.... |
| `language_script` | `devanagari_candidate` | **SPARSE** | `ROBUSTNESS` | Character code detection of Unicode Devanagari block (U+0900..U+097F);... |
| `language_script` | `bilingual_candidate` | **SPARSE** | `ROBUSTNESS` | Co-occurrence of Devanagari and Latin script characters on the same pa... |
| `language_script` | `no_devanagari_candidate` | **PRESENT** | `ROBUSTNESS` | No Devanagari candidate was observed under the frozen detector; does n... |
| `language_script` | `devanagari_in_fit_or_validation` | **ABSENT** | `ROBUSTNESS` | Intersection of devanagari_page_count > 0 and split in ('FIT', 'VALIDA... |
| `legacy_or_broken_text` | `legacy_font_candidate` | **PRESENT** | `ROBUSTNESS` | Detection of U+FFFD replacement characters or PUA codepoints indicatin... |
| `legacy_or_broken_text` | `duplicate_text_candidate` | **PRESENT** | `ROBUSTNESS` | Bounding-box text overlap heuristic (IoU >= 0.40); captures headers, f... |
| `legacy_or_broken_text` | `hidden_text_candidate` | **SPARSE** | `ROBUSTNESS` | Sub-point font text heuristic (< 0.5 pt); intentional hidden text inte... |
| `document_size` | `size_short` | **PRESENT** | `ROBUSTNESS` | Total physical pages <= 100 pages.... |
| `document_size` | `size_medium` | **PRESENT** | `ROBUSTNESS` | Total physical pages between 101 and 250 pages.... |
| `document_size` | `size_long` | **PRESENT** | `ROBUSTNESS` | Total physical pages between 251 and 350 pages.... |
| `document_size` | `size_very_long` | **PRESENT** | `ROBUSTNESS` | Total physical pages between 351 and 500 pages.... |
| `document_size` | `size_extreme` | **PRESENT** | `ROBUSTNESS` | Total physical pages > 500 pages (maximum observed 661 pages).... |
| `document_size` | `stub_filing` | **SPARSE** | `ROBUSTNESS` | Total physical pages <= 2; exactly 2 filings (INE00FF01025_2015 [1 pg]... |
| `layout_and_structure` | `two_column_layout` | **PRESENT** | `ROBUSTNESS` | Heuristic candidate detection of two-column layout bounding boxes.... |
| `layout_and_structure` | `multi_column_layout` | **PRESENT** | `ROBUSTNESS` | Heuristic candidate detection of 3+ column layout bounding boxes.... |
| `layout_and_structure` | `table_candidate` | **PRESENT** | `ROBUSTNESS` | Heuristic signal based on vector grids and aligned numeric lines; true... |
| `layout_and_structure` | `running_furniture_candidate` | **PRESENT** | `ROBUSTNESS` | Repetitive running header or footer coordinate detections across conse... |
| `layout_and_structure` | `combined_mdna_candidate` | **PRESENT** | `ROBUSTNESS` | Outline/heading candidate detection where MD&A is compounded with Dire... |
| `layout_and_structure` | `annexure_candidate` | **PRESENT** | `ROBUSTNESS` | Keyword regex match for 'annexure' in document outline or heading; doe... |
| `layout_and_structure` | `toc_candidate` | **PRESENT** | `ROBUSTNESS` | Printed keyword candidate detection within the first 30 pages of the d... |
| `layout_and_structure` | `no_toc_keyword_candidate` | **PRESENT** | `ROBUSTNESS` | Document yielded no printed TOC keyword candidate under search rule; d... |
| `coverage_intersections` | `scanned_with_multi_column` | **PRESENT** | `ROBUSTNESS` | Derived document-level intersection of scanned pages and multi-column ... |
| `coverage_intersections` | `scanned_with_table_candidate` | **PRESENT** | `ROBUSTNESS` | Derived document-level intersection of scanned pages and tabular candi... |
| `evidence_limitations` | `ocr_transcription_quality` | **NOT_ASSESSABLE** | `NOT_ASSESSABLE` | Character error rate (CER) and word error rate (WER) on OCR text layer... |
| `evidence_limitations` | `scanned_heading_localization_error` | **NOT_ASSESSABLE** | `NOT_ASSESSABLE` | MD&A heading boundary localization accuracy and error rate on scanned ... |

## 5. Important Gaps & Unresolved Questions

### Key Observed Coverage Gaps:
- **Zero Scanned Documents in Validation**: The 2 fully scanned documents are located in `HOLDOUT` (INE002L01015_2012) and `FIT` (INE003B01014_2011). The `VALIDATION` split contains zero fully scanned documents.
- **Thin Scanned Representation**: Only 2 fully scanned documents exist in the corpus, confirming the frozen characterization of `RARE` / thin representation.
- **Zero Devanagari in Development**: Devanagari text is 100% absent from FIT and VALIDATION splits (confined to cover letterheads of 1 HOLDOUT issuer).
- **Unmeasured Properties**: OCR character/word error rates and MD&A heading localization accuracy on scanned pages are unmeasured in frozen artifacts.

### Statement of Unresolved Questions:
> No implementation-blocking questions remain. OCR quality, heading-localization performance, and other unmeasured properties remain intentionally unresolved because T0.3A-R1 is a coverage audit rather than a performance benchmark.

