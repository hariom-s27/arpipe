# P-M3: Scan-Quality Measurement Report

> **Research Question**: How prevalent are low-quality scanned/raster pages, and does scan quality or scan-related missingness concentrate by fiscal year, company size, or other existing corpus strata?

## Methodological Isolation & Scope
- **Study Nature**: Measurement and diagnostic study only.
- **Production Changes**: ZERO production files modified. No routing, threshold, segmentation, or OCR changes.
- **Explicit Boundary**:
```text
SCAN / INPUT QUALITY  ≠  OCR QUALITY  ≠  EXTRACTION CORRECTNESS  ≠  OCR FAILURE
```
- **Composite Rule**: No pre-existing composite rule existed; per Section 13, composite scoring is marked `unscored` (no threshold fishing). Raw component measurements remain primary.

## A. Population Accounting
- **Total Documents**: 194
- **Total Physical Pages**: 37917
- **Pages with Raster Content**: 12464 (32.87%)
- **Pages with Full-Page Raster (Dominant $\ge$ 50%)**: 2909 (7.67%)
- **Pages with Partial Raster**: 9555 (25.20%)
- **Native-Only Pages**: 25257 (66.61%)
- **Unknown Pages**: 0
- **Measurable Full-Page Raster Pages**: 2909 (100.00%)
- **Unmeasurable Full-Page Raster Pages**: 0

## B. Raw Physical Measurement Distributions (Primary Measurement Population)
| Component | N | Missing | Min | P25 | Median | P75 | P95 | Max | Method & Direction |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| **DPI** | 2909 | 0 | 0.09 | 96.24 | 150.0 | 165.55 | 300.0 | 600.88 | Min width/height placed DPI |
| **Skew Angle (°)** | 1827 | 1082 | -5.0 | -0.4 | -0.2 | -0.2 | 0.4 | 5.0 | Projection profile variance |
| **Contrast** | 2909 | 0 | 0.0 | 0.3569 | 0.5412 | 0.7176 | 0.9216 | 1.0 | Interdecile (P95-P05)/255 |
| **Noise / Speckle** | 2909 | 0 | 0.0 | 0.0058 | 0.0102 | 0.0155 | 0.0261 | 0.0622 | 3x3 median residual (higher=noisier) |
| **Blur / Sharpness** | 2909 | 0 | 0.59 | 1261.26 | 2690.9 | 5245.9 | 10324.178 | 31994.88 | Laplacian variance (**higher=sharper**) |

## C. Fiscal-Year Analysis
| FY | Docs | Physical Pages | Full Raster Pages | Raster Frac | Measurable Pages | Median DPI | Median Skew | Median Contrast | Median Noise | Median Blur |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2011 | 1 | 48 | 48 | 1.0000 | 48 | 146.18 | -0.4 | 0.60195 | 0.0086 | 4801.55 |
| 2012 | 28 | 3298 | 243 | 0.0737 | 243 | 299.99 | -0.4 | 0.5451 | 0.011 | 3645.06 |
| 2013 | 29 | 3517 | 757 | 0.2152 | 757 | 165.55 | -0.2 | 0.4667 | 0.0135 | 4804.57 |
| 2015 | 2 | 3 | 1 | 0.3333 | 1 | 152.0 | -0.2 | 0.349 | 0.0062 | 1854.49 |
| 2017 | 31 | 6469 | 437 | 0.0676 | 437 | 156.6 | -0.2 | 0.4667 | 0.0118 | 2822.9 |
| 2018 | 31 | 6240 | 193 | 0.0309 | 193 | 100.32 | -0.2 | 0.6471 | 0.0043 | 892.08 |
| 2024 | 36 | 8825 | 537 | 0.0608 | 537 | 144.05 | -0.4 | 0.6314 | 0.0077 | 2007.22 |
| 2025 | 36 | 9517 | 693 | 0.0728 | 693 | 96.16 | -0.2 | 0.5686 | 0.0098 | 1967.24 |

## D. Company-Size / Cap-Band Analysis
| Cap Band | Docs | Physical Pages | Full Raster Pages | Raster Frac | Measurable Pages | Median DPI | Median Skew | Median Contrast | Median Noise | Median Blur |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| large | 36 | 10988 | 438 | 0.0399 | 438 | 165.55 | -0.4 | 0.6745 | 0.0094 | 2995.665 |
| mid | 48 | 10251 | 969 | 0.0945 | 969 | 150.0 | -0.2 | 0.4902 | 0.012 | 3083.84 |
| small | 44 | 10728 | 619 | 0.0577 | 619 | 144.02 | -0.2 | 0.5098 | 0.0073 | 1847.74 |
| micro | 66 | 5950 | 883 | 0.1484 | 883 | 152.0 | -0.4 | 0.5569 | 0.0104 | 2965.72 |

## E. FY × Cap-Band Distribution
| FY | Cap Band | Docs | Physical Pages | Full Raster Pages | Raster Frac | Measurable Pages | Note |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| 2011 | micro | 1 | 48 | 48 | 1.0000 | 48 | descriptive only (small cell) |
| 2012 | large | 6 | 1086 | 14 | 0.0129 | 14 | adequate cell |
| 2012 | mid | 8 | 959 | 50 | 0.0521 | 50 | adequate cell |
| 2012 | small | 5 | 731 | 19 | 0.0260 | 19 | adequate cell |
| 2012 | micro | 9 | 522 | 160 | 0.3065 | 160 | adequate cell |
| 2013 | large | 6 | 1165 | 170 | 0.1459 | 170 | adequate cell |
| 2013 | mid | 8 | 1031 | 147 | 0.1426 | 147 | adequate cell |
| 2013 | small | 5 | 709 | 255 | 0.3597 | 255 | adequate cell |
| 2013 | micro | 10 | 612 | 185 | 0.3023 | 185 | adequate cell |
| 2015 | small | 2 | 3 | 1 | 0.3333 | 1 | descriptive only (small cell) |
| 2017 | large | 6 | 1980 | 34 | 0.0172 | 34 | adequate cell |
| 2017 | mid | 8 | 1843 | 335 | 0.1818 | 335 | adequate cell |
| 2017 | small | 6 | 1689 | 46 | 0.0272 | 46 | adequate cell |
| 2017 | micro | 11 | 957 | 22 | 0.0230 | 22 | adequate cell |
| 2018 | large | 6 | 1818 | 41 | 0.0226 | 41 | adequate cell |
| 2018 | mid | 8 | 1741 | 48 | 0.0276 | 48 | adequate cell |
| 2018 | small | 6 | 1517 | 50 | 0.0330 | 50 | adequate cell |
| 2018 | micro | 11 | 1164 | 54 | 0.0464 | 54 | adequate cell |
| 2024 | large | 6 | 2495 | 109 | 0.0437 | 109 | adequate cell |
| 2024 | mid | 8 | 2324 | 109 | 0.0469 | 109 | adequate cell |
| 2024 | small | 10 | 2732 | 111 | 0.0406 | 111 | adequate cell |
| 2024 | micro | 12 | 1274 | 208 | 0.1633 | 208 | adequate cell |
| 2025 | large | 6 | 2444 | 70 | 0.0286 | 70 | adequate cell |
| 2025 | mid | 8 | 2353 | 280 | 0.1190 | 280 | adequate cell |
| 2025 | small | 10 | 3347 | 137 | 0.0409 | 137 | adequate cell |
| 2025 | micro | 12 | 1373 | 206 | 0.1500 | 206 | adequate cell |

## F. Document & Company Concentration Analysis
- Total full-page-raster pages: **2909** across **170** documents.
- **Top 1 Document Share**: 10.14% of all full-page raster pages.
- **Top 5 Documents Share**: 33.07% of all full-page raster pages.
- **Top 10 Documents Share**: 47.61% of all full-page raster pages.
- **Top 1 Company Share**: 15.33%.
- **Top 5 Companies Share**: 43.90%.
- **Top 10 Companies Share**: 66.28%.

## G. Missingness Analysis
- Total full-page raster pages: 2909
- DPI missingness: 0
- Skew missingness: 1082 (low confidence: 1075)
- Contrast missingness: 0
- Noise missingness: 0
- Blur missingness: 0

## H. Diagnostic Association with Provenance & Outcomes
| Provenance | Full Raster Pages | Measurable Pages |
| :--- | ---: | ---: |
| scanned | 2694 | 2694 |
| ocr | 215 | 215 |

## I. Methodological Boundaries — What Is NOT Established
- **MEASURED**: Physical resolution (DPI), geometric skew angle, grayscale contrast dynamic range, spatial median residual (noise), and discrete Laplacian variance (sharpness).
- **DESCRIPTIVE ASSOCIATION**: Distribution of raster pages across FY, cap bands, and document concentration.
- **INFERENCE**: Higher raster prevalence in earlier fiscal years (2012–2013) and small/micro cap companies.
- **NOT ESTABLISHED**: OCR accuracy, word error rate, extraction correctness, or causal impact on MD&A section discovery. Low physical scan quality cannot be equated with OCR failure.

## J. Final Verdict
```text
SCAN-QUALITY MEASUREMENT COMPLETED — NO PRODUCTION CHANGE
```
