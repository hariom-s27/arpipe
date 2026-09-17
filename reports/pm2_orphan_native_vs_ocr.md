# P-M2: native vs OCR `orphan_start_frac` distribution

Primary comparison is per-DOCUMENT (MD&A span), using verify.order_quality()'s own persisted number - see this script's module docstring for why per-physical-page orphan_start_frac is not (re)computed here.

Production gate measured against: `ORPHAN_START_FRAC_MAX = 0.03` (read from `arpipe.verify`, never modified by this script).  
Metric basis: `orphan_basis = "prose_only"` (the only basis pooled into the comparison below; any other basis is reported separately, never mixed in).

## A. Population

- Total manifest records: 194
- Documents with a located MD&A span: 182
- Excluded - no located span (mda_not_located / profile_failed / pre-span quarantine): 12
- Excluded - other/unrecorded orphan_basis: none
- Documents on the primary basis (`prose_only`): 182
- Provenance counts (primary-basis documents): {'native': 160, 'mixed': 16, 'ocr': 5, 'unknown': 1}
- Physical span-pages by class, summed across primary-basis documents: {'native': 2592, 'ocr': 141, 'unknown': 1}
- Unknown-provenance documents (excluded from native/ocr/mixed): INE001B01026/2018

## B. Distribution (document / MD&A-span level)

| Population | N | Min | P25 | Median | P75 | P90 | P95 | Max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Native | 160 | 0.0000 | 0.0000 | 0.0146 | 0.0294 | 0.0516 | 0.0620 | 0.2060 |
| OCR | 5 | 0.0236 | 0.0383 | 0.0390 | 0.0526 | 0.0544 | 0.0550 | 0.0556 |
| Mixed | 16 | 0.0029 | 0.0103 | 0.0199 | 0.0380 | 0.0579 | 0.0714 | 0.0936 |

Percentile method: `numpy.percentile(values, q, method="linear")` (pure-Python linear-interpolation fallback if numpy is absent), applied identically to both populations.

## C. Threshold diagnostics

**Native**  
score < 0.03: 121  
score = 0.03: 0  
score > 0.03: 39  
fraction > 0.03: 0.2437  
max <= 0.03: 0.0299  
min > 0.03: 0.0302  
gap around 0.03: 0.0003
of the 39 over-gate documents, 38 actually carry `source_shredded`/`order_scrambled` in production's own `reasons` (verify.build_reasons() also requires orphan_starts > 1 - see methodology note); 1 cross the 0.03 fraction without being flagged.

**OCR**  
score < 0.03: 1  
score = 0.03: 0  
score > 0.03: 4  
fraction > 0.03: 0.8000  
max <= 0.03: 0.0236  
min > 0.03: 0.0383  
gap around 0.03: 0.0147
of the 4 over-gate documents, 3 actually carry `source_shredded`/`order_scrambled` in production's own `reasons` (verify.build_reasons() also requires orphan_starts > 1 - see methodology note); 1 cross the 0.03 fraction without being flagged.

**Mixed**  
score < 0.03: 9  
score = 0.03: 0  
score > 0.03: 7  
fraction > 0.03: 0.4375  
max <= 0.03: 0.0230  
min > 0.03: 0.0333  
gap around 0.03: 0.0103
of the 7 over-gate documents, 7 actually carry `source_shredded`/`order_scrambled` in production's own `reasons` (verify.build_reasons() also requires orphan_starts > 1 - see methodology note); 0 cross the 0.03 fraction without being flagged.

## D. Interpretation

**Does 0.03 sit in an observed empty band for native text?**  
Yes in the sense that there is an observed gap of 0.0003 straddling the gate (max <= gate = 0.0299, min > gate = 0.0302).

**Does 0.03 sit in an observed empty band for OCR text?**  
Observed gap of 0.0147 (max <= gate = 0.0236, min > gate = 0.0383).

**Is the OCR distribution materially different?**  
median delta (OCR - native) = 0.0244, P95 delta = -0.007, fraction-above-gate delta = 0.5563. See section B/C for the full picture.

**Is there enough OCR data to justify saying this?**  
N = 5: very small - descriptive only, no stable distributional conclusion

**Does the current evidence justify proposing a separate OCR band?**  
See section G (threshold recommendation) below.

## E. Highest-scoring documents

### OCR-provenance documents (top by orphan_start_frac)

| company | FY | span (pages) | orphan_start_frac | OCR engine(s) | OCR pages in span | native pages in span | grade | reasons |
|---|---|---|---:|---|---|---|---|---|
| INE003B01014 | 2011 | 15-15 | 0.0556 | tesseract:eng | 15 | - | low | - |
| INE002L01015 | 2012 | 8-11 | 0.0526 | tesseract:eng | 8, 9, 10, 11 | - | low | source_shredded, span_truncated |
| INE009A01021 | 2013 | 39-40 | 0.0390 | tesseract:eng | 39, 40 | - | medium | source_shredded, span_truncated |
| INE002A01018 | 2018 | 57-128 | 0.0383 | tesseract:eng | 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128 | - | low | source_shredded, span_truncated |
| INE004C01028 | 2024 | 60-66 | 0.0236 | tesseract:eng | 60, 61, 62, 63, 64, 65, 66 | - | low | source_shredded, span_truncated |


### Native-provenance documents (top by orphan_start_frac)

| company | FY | span (pages) | orphan_start_frac | OCR engine(s) | OCR pages in span | native pages in span | grade | reasons |
|---|---|---|---:|---|---|---|---|---|
| INE002L01015 | 2025 | 43-49 | 0.2060 | - | - | 43, 44, 45, 46, 47, 48, 49 | low | source_shredded, span_truncated |
| INE002S01010 | 2017 | 28-45 | 0.1531 | - | - | 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45 | low | source_shredded |
| INE119A01028 | 2018 | 53-59 | 0.1440 | - | - | 53, 54, 55, 56, 57, 58, 59 | low | source_shredded, span_truncated |
| INE009A01021 | 2018 | 96-97 | 0.1406 | - | - | 96, 97 | low | source_shredded, span_truncated |
| INE797F01020 | 2012 | 23-31 | 0.1038 | - | - | 23, 24, 25, 26, 27, 28, 29, 30, 31 | low | source_shredded, span_truncated |
| INE044A01036 | 2013 | 5-33 | 0.0838 | - | - | 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33 | low | source_shredded, span_truncated |
| INE008A01015 | 2024 | 72-143 | 0.0811 | - | - | 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143 | quarantine | source_shredded, span_truncated, WRONG_LANGUAGE_RISK |
| INE171A01029 | 2012 | 22-56 | 0.0691 | - | - | 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56 | low | section_leak, order_scrambled, span_truncated |
| INE002L01015 | 2024 | 39-45 | 0.0616 | - | - | 39, 40, 41, 42, 43, 44, 45 | low | source_shredded, span_truncated |
| INE008A01015 | 2013 | 53-82 | 0.0610 | - | - | 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82 | low | identity_unproven, order_scrambled, span_truncated |


### Mixed-provenance documents (top by orphan_start_frac, for context)

| company | FY | span (pages) | orphan_start_frac | OCR engine(s) | OCR pages in span | native pages in span | grade | reasons |
|---|---|---|---:|---|---|---|---|---|
| INE191H01014 | 2025 | 78-107 | 0.0936 | tesseract:eng | 81, 82, 84, 93 | 78, 79, 80, 83, 85, 86, 87, 88, 89, 90, 91, 92, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107 | low | source_shredded, span_truncated |
| INE040A01034 | 2017 | 20-34 | 0.0640 | tesseract:eng | 25 | 20, 21, 22, 23, 24, 26, 27, 28, 29, 30, 31, 32, 33, 34 | low | source_shredded, span_truncated |
| INE040A01034 | 2018 | 24-44 | 0.0518 | tesseract:eng | 24, 39, 40, 41 | 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 42, 43, 44 | medium | source_shredded, span_truncated |
| INE081A01020 | 2013 | 56-100 | 0.0387 | tesseract:eng | 59, 65 | 56, 57, 58, 60, 61, 62, 63, 64, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100 | medium | source_shredded, span_truncated |
| INE004C01028 | 2017 | 36-50 | 0.0378 | tesseract:eng | 39, 40, 43, 46 | 36, 37, 38, 41, 42, 44, 45, 47, 48, 49, 50 | low | year_unproven, order_scrambled, span_truncated |
| INE119A01028 | 2013 | 61-70 | 0.0339 | tesseract:eng | 68, 69 | 61, 62, 63, 64, 65, 66, 67, 70 | low | source_shredded, span_truncated |
| INE761H01022 | 2013 | 30-34 | 0.0333 | tesseract:eng | 31 | 30, 32, 33, 34 | medium | source_shredded |
| INE001B01026 | 2013 | 13-28 | 0.0230 | tesseract:eng | 13, 18, 21, 22, 23 | 14, 15, 16, 17, 19, 20, 24, 25, 26, 27, 28 | medium | - |
| INE044A01036 | 2012 | 9-29 | 0.0168 | tesseract:eng | 10, 12, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29 | 9, 11, 13, 19 | medium | span_truncated |
| INE171A01029 | 2018 | 49-91 | 0.0148 | tesseract:eng | 70 | 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91 | medium | section_leak, span_truncated |


## F. Regression

```
production behavior changed: NO
threshold changed: NO
OCR routing changed: NO
grading changed: NO
```

## G. Threshold recommendation

No alternate threshold can be justified from the available data (N = 5: very small - descriptive only, no stable distributional conclusion). `ORPHAN_START_FRAC_MAX` was not changed and no OCR-specific band is proposed.

