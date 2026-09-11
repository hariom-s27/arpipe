# Evaluation Report

**Total Documents Evaluated:** 20

## 1. Targets Comparison

| Metric / Target | Target Threshold | Actual Score | Status |
| :--- | :---: | :---: | :---: |
| Born-Digital (within 1 page) | &ge; 95% | 90.0% | FAIL |
| Scanned / Mixed (within 1 page) | &ge; 85% | 90.0% | PASS |
| Low Tier Fraction | &le; 6% | 10.0% | FAIL |
| Order Quality (orphan frac &le; 0.02) | &ge; 95% | 85.0% | FAIL |

## 2. Overall Metrics

| Metric | Score | Description |
| :--- | :---: | :--- |
| **Exact Start Accuracy** | 90.0% | Fraction where predicted start == true start |
| **Start Within 1 Page** | **90.0%** | Primary operational usability threshold |
| **Start Within 2 Pages** | 90.0% | Relaxed boundary tolerance |
| **Boundary IoU** | 0.8267 | Mean Intersection-over-Union across spans |
| **Pk Penalty** | 0.0403 | Beeferman windowed segmentation penalty (lower is better) |
| **WindowDiff Penalty** | 0.0411 | Pevzner-Hearst boundary difference penalty (lower is better) |
| **Mean Orphan Start Frac** | 0.0059 | Average fraction of lowercase/broken sentence starts |
| **Order Scrambled Frac** | 0.0% | Fraction flagged with reading order scrambling |

## 3. Metrics Per Stratum (Era x Cap Band x Doc Kind)

| Stratum (Era | Cap | Kind) | N | Exact Start | Within 1 Pg | Within 2 Pg | IoU | Pk | WindowDiff | Orphan Frac | Scrambled % |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 2010-2013 | large | digital    |  3 | 100.0% | 100.0% | 100.0% |  0.785 | 0.043 |  0.045 |  0.013 |   0.0% |
| 2010-2013 | large | mixed      |  2 | 100.0% | 100.0% | 100.0% |  1.000 | 0.000 |  0.000 |  0.000 |   0.0% |
| 2010-2013 | large | scanned    |  1 |   0.0% |   0.0% |   0.0% |  0.000 | 0.080 |  0.080 |  0.000 |   0.0% |
| 2010-2013 | mid | digital      |  1 | 100.0% | 100.0% | 100.0% |  1.000 | 0.000 |  0.000 |  0.000 |   0.0% |
| 2010-2013 | mid | mixed        |  1 | 100.0% | 100.0% | 100.0% |  1.000 | 0.000 |  0.000 |  0.000 |   0.0% |
| 2010-2013 | mid | scanned      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2010-2013 | small | digital    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2010-2013 | small | mixed      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2010-2013 | small | scanned    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2010-2013 | micro | digital    |  4 |  75.0% |  75.0% |  75.0% |  0.607 | 0.134 |  0.138 |  0.000 |   0.0% |
| 2010-2013 | micro | mixed      |  2 | 100.0% | 100.0% | 100.0% |  0.875 | 0.029 |  0.029 |  0.011 |   0.0% |
| 2010-2013 | micro | scanned    |  1 | 100.0% | 100.0% | 100.0% |  1.000 | 0.000 |  0.000 |  0.056 |   0.0% |
| 2014-2018 | large | digital    |  1 | 100.0% | 100.0% | 100.0% |  1.000 | 0.000 |  0.000 |  0.000 |   0.0% |
| 2014-2018 | large | mixed      |  1 | 100.0% | 100.0% | 100.0% |  1.000 | 0.000 |  0.000 |  0.000 |   0.0% |
| 2014-2018 | large | scanned    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | mid | digital      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | mid | mixed        |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | mid | scanned      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | small | digital    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | small | mixed      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | small | scanned    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | micro | digital    |  1 | 100.0% | 100.0% | 100.0% |  1.000 | 0.000 |  0.000 |  0.000 |   0.0% |
| 2014-2018 | micro | mixed      |  2 | 100.0% | 100.0% | 100.0% |  1.000 | 0.000 |  0.000 |  0.000 |   0.0% |
| 2014-2018 | micro | scanned    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2019-2025 | large | digital    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2019-2025 | large | mixed      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2019-2025 | large | scanned    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2019-2025 | mid | digital      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2019-2025 | mid | mixed        |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2019-2025 | mid | scanned      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2019-2025 | small | digital    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2019-2025 | small | mixed      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2019-2025 | small | scanned    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2019-2025 | micro | digital    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2019-2025 | micro | mixed      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2019-2025 | micro | scanned    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |

## 4. Per-Method Precision (S1..S5)

| Method | Predictions (N) | Correct (&le; 1 pg) | Precision |
| :--- | :---: | :---: | :---: |
| outline         |   0 |   0 |   0.0% |
| toc             |   0 |   0 |   0.0% |
| heading         |   4 |   4 | 100.0% |
| heading_text    |   1 |   1 | 100.0% |
| body_score      |   0 |   0 |   0.0% |
| none            |  15 |  13 |  86.7% |

## 5. Supporter Calibration

| Supporters | Documents (N) | Correct (&le; 1 pg) | Calibration Accuracy |
| :---: | :---: | :---: | :---: |
| 0          |  16 |  14 |  87.5% |
| 1          |   3 |   3 | 100.0% |
| 2          |   1 |   1 | 100.0% |
| 3+         |   0 |   0 |   0.0% |

## 6. Confidence Tier Precision

| Confidence Tier | Documents (N) | Exact Start | Within 1 Page | Mean IoU |
| :--- | :---: | :---: | :---: | :---: |
| high            |   0 |   0.0% |   0.0% | 0.0000 |
| medium          |   3 | 100.0% | 100.0% | 0.9758 |
| low             |   2 | 100.0% | 100.0% | 1.0000 |
| failed          |   1 | 100.0% | 100.0% | 1.0000 |

## 7. Worst Three Strata Analysis

### Rank 1: `2010-2013 | large | scanned` (N=1)
- **Performance:** Within 1 Page: `0.0%` | Mean IoU: `0.000` | Pk: `0.080` | WindowDiff: `0.080`
- **Diagnosis & Root Cause:** Scanned/mixed historical documents in this stratum suffer from absence of embedded text layers. Heading detection fails when scan noise introduces characters (e.g. `MANAGEMENT. DISCUSSION`), forcing fallback to index sampling or body scoring which frequently mistakes cross-reference notices for section starts.

### Rank 2: `2010-2013 | micro | digital` (N=4)
- **Performance:** Within 1 Page: `75.0%` | Mean IoU: `0.607` | Pk: `0.134` | WindowDiff: `0.138`
- **Diagnosis & Root Cause:** Micro-cap reports in this stratum frequently lack dedicated MD&A sections entirely, or contain only 1-paragraph disclosures inside the Corporate Governance report that trigger false positive terminations.

### Rank 3: `2010-2013 | large | digital` (N=3)
- **Performance:** Within 1 Page: `100.0%` | Mean IoU: `0.785` | Pk: `0.043` | WindowDiff: `0.045`
- **Diagnosis & Root Cause:** Bookmark/outline corruption or premature termination on embedded consolidated statements within the Directors' Report truncated the predicted boundaries.
