# Evaluation Report

**Total Documents Evaluated:** 6

## 1. Targets Comparison

| Metric / Target | Target Threshold | Actual Score | Status |
| :--- | :---: | :---: | :---: |
| Born-Digital (within 1 page) | &ge; 95% | 75.0% | FAIL |
| Scanned / Mixed (within 1 page) | &ge; 85% | 100.0% | PASS |
| Low Tier Fraction | &le; 6% | 33.3% | FAIL |
| Order Quality (orphan frac &le; 0.02) | &ge; 95% | 83.3% | FAIL |

## 2. Overall Metrics

| Metric | Score | Description |
| :--- | :---: | :--- |
| **Exact Start Accuracy** | 83.3% | Fraction where predicted start == true start |
| **Start Within 1 Page** | **83.3%** | Primary operational usability threshold |
| **Start Within 2 Pages** | 83.3% | Relaxed boundary tolerance |
| **Boundary IoU** | 0.8333 | Mean Intersection-over-Union across spans |
| **Pk Penalty** | 0.0750 | Beeferman windowed segmentation penalty (lower is better) |
| **WindowDiff Penalty** | 0.0750 | Pevzner-Hearst boundary difference penalty (lower is better) |
| **Mean Orphan Start Frac** | 0.0093 | Average fraction of lowercase/broken sentence starts |
| **Order Scrambled Frac** | 0.0% | Fraction flagged with reading order scrambling |

## 3. Metrics Per Stratum (Era x Cap Band x Doc Kind)

| Stratum (Era | Cap | Kind) | N | Exact Start | Within 1 Pg | Within 2 Pg | IoU | Pk | WindowDiff | Orphan Frac | Scrambled % |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 2010-2013 | large | digital    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2010-2013 | large | mixed      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2010-2013 | large | scanned    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2010-2013 | mid | digital      |  1 | 100.0% | 100.0% | 100.0% |  1.000 | 0.000 |  0.000 |  0.000 |   0.0% |
| 2010-2013 | mid | mixed        |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2010-2013 | mid | scanned      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2010-2013 | small | digital    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2010-2013 | small | mixed      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2010-2013 | small | scanned    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2010-2013 | micro | digital    |  3 |  66.7% |  66.7% |  66.7% |  0.667 | 0.150 |  0.150 |  0.000 |   0.0% |
| 2010-2013 | micro | mixed      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2010-2013 | micro | scanned    |  1 | 100.0% | 100.0% | 100.0% |  1.000 | 0.000 |  0.000 |  0.056 |   0.0% |
| 2014-2018 | large | digital    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | large | mixed      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | large | scanned    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | mid | digital      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | mid | mixed        |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | mid | scanned      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | small | digital    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | small | mixed      |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | small | scanned    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | micro | digital    |  0 |     -   |     -   |     -   |      - |     - |      - |      - |     -   |
| 2014-2018 | micro | mixed      |  1 | 100.0% | 100.0% | 100.0% |  1.000 | 0.000 |  0.000 |  0.000 |   0.0% |
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
| heading         |   1 |   1 | 100.0% |
| heading_text    |   1 |   1 | 100.0% |
| body_score      |   0 |   0 |   0.0% |
| none            |   4 |   3 |  75.0% |

## 5. Supporter Calibration

| Supporters | Documents (N) | Correct (&le; 1 pg) | Calibration Accuracy |
| :---: | :---: | :---: | :---: |
| 0          |   5 |   4 |  80.0% |
| 1          |   1 |   1 | 100.0% |
| 2          |   0 |   0 |   0.0% |
| 3+         |   0 |   0 |   0.0% |

## 6. Confidence Tier Precision

| Confidence Tier | Documents (N) | Exact Start | Within 1 Page | Mean IoU |
| :--- | :---: | :---: | :---: | :---: |
| high            |   0 |   0.0% |   0.0% | 0.0000 |
| medium          |   0 |   0.0% |   0.0% | 0.0000 |
| low             |   2 | 100.0% | 100.0% | 1.0000 |
| failed          |   1 | 100.0% | 100.0% | 1.0000 |

## 7. Worst Three Strata Analysis

### Rank 1: `2010-2013 | micro | digital` (N=3)
- **Performance:** Within 1 Page: `66.7%` | Mean IoU: `0.667` | Pk: `0.150` | WindowDiff: `0.150`
- **Diagnosis & Root Cause:** Micro-cap reports in this stratum frequently lack dedicated MD&A sections entirely, or contain only 1-paragraph disclosures inside the Corporate Governance report that trigger false positive terminations.

### Rank 2: `2010-2013 | mid | digital` (N=1)
- **Performance:** Within 1 Page: `100.0%` | Mean IoU: `1.000` | Pk: `0.000` | WindowDiff: `0.000`
- **Diagnosis & Root Cause:** Bookmark/outline corruption or premature termination on embedded consolidated statements within the Directors' Report truncated the predicted boundaries.

### Rank 3: `2010-2013 | micro | scanned` (N=1)
- **Performance:** Within 1 Page: `100.0%` | Mean IoU: `1.000` | Pk: `0.000` | WindowDiff: `0.000`
- **Diagnosis & Root Cause:** Scanned/mixed historical documents in this stratum suffer from absence of embedded text layers. Heading detection fails when scan noise introduces characters (e.g. `MANAGEMENT. DISCUSSION`), forcing fallback to index sampling or body scoring which frequently mistakes cross-reference notices for section starts.
