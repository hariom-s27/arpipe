# Evaluation Report

**Total Documents Evaluated:** 13

## 1. Targets Comparison

| Metric / Target | Target Threshold | Actual Score | Status |
| :--- | :---: | :---: | :---: |
| Born-Digital (within 1 page) | &ge; 95% | 44.4% | FAIL |
| Scanned / Mixed (within 1 page) | &ge; 85% | 50.0% | FAIL |
| Low Tier Fraction | &le; 6% | 30.8% | FAIL |
| Order Quality (orphan frac &le; 0.02) | &ge; 95% | 84.6% | FAIL |

## 2. Overall Metrics

| Metric | Score | Description |
| :--- | :---: | :--- |
| **Exact Start Accuracy** | 46.2% | Fraction where predicted start == true start |
| **Start Within 1 Page** | **46.2%** | Primary operational usability threshold |
| **Start Within 2 Pages** | 46.2% | Relaxed boundary tolerance |
| **Boundary IoU** | 0.4670 | Mean Intersection-over-Union across spans |
| **Pk Penalty** | 0.0672 | Beeferman windowed segmentation penalty (lower is better) |
| **WindowDiff Penalty** | 0.0678 | Pevzner-Hearst boundary difference penalty (lower is better) |
| **Mean Orphan Start Frac** | 0.0063 | Average fraction of lowercase/broken sentence starts |
| **Order Scrambled Frac** | 15.4% | Fraction flagged with reading order scrambling |

## 3. Metrics Per Stratum (Era x Cap Band x Doc Kind)

| Stratum (Era | Cap | Kind) | N | Exact Start | Within 1 Pg | Within 2 Pg | IoU | Pk | WindowDiff | Orphan Frac | Scrambled % |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 2010-2013 | large | digital    |  4 |  50.0% |  50.0% |  50.0% |  0.500 | 0.058 |  0.060 |  0.000 |   0.0% |
| 2010-2013 | large | mixed      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2010-2013 | large | scanned    |  2 |  50.0% |  50.0% |  50.0% |  0.500 | 0.043 |  0.043 |  0.039 | 100.0% |
| 2010-2013 | mid | digital      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2010-2013 | mid | mixed        |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2010-2013 | mid | scanned      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2010-2013 | small | digital    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2010-2013 | small | mixed      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2010-2013 | small | scanned    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2010-2013 | micro | digital    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2010-2013 | micro | mixed      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2010-2013 | micro | scanned    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | large | digital    |  1 | 100.0% | 100.0% | 100.0% |  1.000 | 0.000 |  0.000 |  0.000 |   0.0% |
| 2014-2018 | large | mixed      |  2 |  50.0% |  50.0% |  50.0% |  0.500 | 0.071 |  0.071 |  0.000 |   0.0% |
| 2014-2018 | large | scanned    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | mid | digital      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | mid | mixed        |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | mid | scanned      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | small | digital    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | small | mixed      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | small | scanned    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | micro | digital    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | micro | mixed      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | micro | scanned    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2019-2025 | large | digital    |  4 |  25.0% |  25.0% |  25.0% |  0.268 | 0.103 |  0.103 |  0.001 |   0.0% |
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
| outline         |   1 |   0 |   0.0% |
| toc             |   1 |   1 | 100.0% |
| heading         |   5 |   2 |  40.0% |
| heading_text    |   1 |   1 | 100.0% |
| body_score      |   1 |   0 |   0.0% |
| none            |   4 |   2 |  50.0% |

## 5. Supporter Calibration

| Supporters | Documents (N) | Correct (&le; 1 pg) | Calibration Accuracy |
| :---: | :---: | :---: | :---: |
| 0          |  11 |   4 |  36.4% |
| 1          |   0 |   0 |   0.0% |
| 2          |   2 |   2 | 100.0% |
| 3+         |   0 |   0 |   0.0% |

## 6. Confidence Tier Precision

| Confidence Tier | Documents (N) | Exact Start | Within 1 Page | Mean IoU |
| :--- | :---: | :---: | :---: | :---: |
| high            |   2 |  50.0% |  50.0% | 0.5357 |
| medium          |   3 |  66.7% |  66.7% | 0.6667 |
| low             |   4 |  25.0% |  25.0% | 0.2500 |
| failed          |   2 | 100.0% | 100.0% | 1.0000 |

## 7. Worst Three Strata Analysis

### Rank 1: `2019-2025 | large | digital` (N=4)
- **Performance:** Within 1 Page: `25.0%` | Mean IoU: `0.268` | Pk: `0.103` | WindowDiff: `0.103`
- **Diagnosis & Root Cause:** Bookmark/outline corruption or premature termination on embedded consolidated statements within the Directors' Report truncated the predicted boundaries.

### Rank 2: `2014-2018 | large | mixed` (N=2)
- **Performance:** Within 1 Page: `50.0%` | Mean IoU: `0.500` | Pk: `0.071` | WindowDiff: `0.071`
- **Diagnosis & Root Cause:** Scanned/mixed historical documents in this stratum suffer from absence of embedded text layers. Heading detection fails when scan noise introduces characters (e.g. `MANAGEMENT. DISCUSSION`), forcing fallback to index sampling or body scoring which frequently mistakes cross-reference notices for section starts.

### Rank 3: `2010-2013 | large | digital` (N=4)
- **Performance:** Within 1 Page: `50.0%` | Mean IoU: `0.500` | Pk: `0.058` | WindowDiff: `0.060`
- **Diagnosis & Root Cause:** Bookmark/outline corruption or premature termination on embedded consolidated statements within the Directors' Report truncated the predicted boundaries.
