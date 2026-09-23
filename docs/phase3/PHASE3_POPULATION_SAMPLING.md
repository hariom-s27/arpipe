# Phase 3 / P1 — Population and precision planning

**PROPOSED — AUTHOR DECISION REQUIRED. Planning targets only; formal sampling is frozen later in Gold Method.**

**START_SHA / completed P0b:** `24520ce623037fde7c3b0a9d0d4e5f8fc5618831`. This supporting document is necessary to preserve the reproducible sensitivity calculation without overwhelming the author-choice sheet. No corpus analysis, Gold creation, baseline run or HOLDOUT access was performed.

## Q3: population, frame and estimands

**REPO-VERIFIED (documented aggregates, not newly reprofiled).** Inspected `dataset/corpus_freeze/freeze_protocol.md`, `stratification_report.md`, `tools/freeze_extraction_corpus.py`, Phase 2 audit V07/V08 and Phase 2.1 PC-04. The corpus was assembled from the existing local content-addressed store and historical metadata, with separate historical-label records whose bytes were unavailable. It was not a probability sample of Indian listed issuers. Development and annotation-roster selection maximize heuristic diversity; the challenge set overlaps partitions and is not an independent evaluation population.

| Layer | REPO-VERIFIED record or PROPOSED interpretation |
|---|---|
| Possible scientific target | AUTHOR DECISION REQUIRED: available frozen reports, enumerated cases, a specified issuer/FY universe, or downstream financial-analysis sample. These differ. |
| Operational sampling frame | REPO-VERIFIED: frozen inventory and issuer split, conditional on local byte availability. No national inclusion probabilities were established. |
| Observed/frozen corpus | REPO-VERIFIED: 194 unique available documents, 36 issuers, 37,917 pages. Total administrative inventory 208 records = 194 available + 14 missing historical records. |
| Observed FY coverage | REPO-VERIFIED: stratification report §1–6 lists 2011, 2012, 2013, 2015, 2017, 2018, 2024, 2025. “FY2010–2025” is a range in the intended universe, not continuous observed coverage. |
| Fixed partitions | REPO-VERIFIED: audit V07 documents FIT 92/18, VALIDATION 48/9, HOLDOUT 54/9 (documents/issuers). These are previously published aggregates only; no HOLDOUT rows/files/content were opened for this analysis. |
| Development / old roster | REPO-VERIFIED: audit V07 records 60 development documents within FIT, 25 roster documents within development. Diversity selection does not give representative accuracy or agreement without a new declared design. |
| Gold sample | UNRESOLVED: which units receive which reference layers under an approved protocol. Neither all frozen documents nor an old roster is automatically adequate Gold. |
| Final evaluation population | AUTHOR DECISION REQUIRED: eligible reference-complete final documents under frozen inclusion/ambiguity rules, with misses retained. No additional issuer or missing document enters silently. |

**INFERRED.** Explicit scope is preferable to unsupported reweighting. Document mean weights each available report equally and overrepresents issuers with more reports; equal-issuer mean averages within issuer first and answers the average-observed-issuer question. Year standardization answers an author-chosen year-mixture question. None repairs absent issuer/year support or unknown availability-selection probabilities. Inverse-probability weights would require defensible inclusion probabilities and positivity; guessed market-cap weights change the target rather than correct selection bias. Report observed issuer imbalance and sensitivity of a declared estimand when permitted later.

**PROPOSED.** C1 is conditional on the final partition's available reports, C2 on a matched eligible comparison population, C3 on a future intervention-defined FIT/VALIDATION population, C4 on a separately declared financial-analysis panel, C5 on explicitly enumerated cases. Do not report a pooled tuned-plus-final mean as untouched generalization to all 194 reports.

## Q7: sensitivity analysis, not a universal n

**INFERRED — planning model.** For K independent issuers and m reports per issuer on average, assume exchangeable within-issuer outcome correlation rho and common marginal variance. With unequal cluster-size coefficient of variation CV, the variance of the document mean implies
`DEFF = 1 + (((1+CV^2)*m)-1)*rho`,
`n_eff = K*m/DEFF`.
This follows from `Var(sum Y)=sigma^2[(1-rho)N+rho*sum(m_i^2)]`; it is a planning approximation, not measured ARPipe ICC or a guarantee of bootstrap coverage. For a binary endpoint, use sigma²=p(1−p); for tIoU use a hypothesized SD. Screening half-width `h=t(.975,K-1)*sigma/sqrt(n_eff)` adds a small-cluster critical value but remains a heuristic, not an approved interval estimator. No finite-population correction is used for these superpopulation-style scenarios.

**SOURCED.** Flynn & Peters (2004), [primary cluster-bootstrap simulation](https://link.springer.com/article/10.1186/1472-6963-4-33), finds that cluster bootstrap coverage depends on cluster count and distribution. Its health-cost setting and numerical sample recommendations do not transfer to bounded ARPipe outcomes. The registered percentile paired cluster bootstrap should not be described as reliable merely because it has many replicates.

All numeric rows below are **VERIFIED arithmetic under INFERRED hypothetical assumptions**, reproduced by the fenced Python code. “Width” is a full nominal 95% interval width in probability units, before clipping at 0/1; it is not an observed interval.

| K | m | rho | CV | p | N | DEFF | n_eff | Width |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 9 | 6 | 0 | 0 | .80 | 54 | 1.00 | 54.0 | .251 |
| 9 | 6 | .20 | 0 | .80 | 54 | 2.00 | 27.0 | .355 |
| 9 | 6 | .50 | 0 | .80 | 54 | 3.50 | 15.4 | .470 |
| 9 | 6 | .20 | .50 | .80 | 54 | 2.30 | 23.5 | .381 |
| 9 | 6 | .20 | 0 | .50 | 54 | 2.00 | 27.0 | .444 |
| 9 | 6 | .20 | 0 | .95 | 54 | 2.00 | 27.0 | .193 |
| 18 | 5 | .20 | 0 | .80 | 90 | 1.80 | 50.0 | .239 |
| 27 | 5 | .20 | 0 | .80 | 135 | 1.80 | 75.0 | .190 |
| 36 | 5 | .20 | 0 | .80 | 180 | 1.80 | 100.0 | .162 |
| 9 | 3 | .20 | 0 | .80 | 27 | 1.40 | 19.3 | .420 |
| 18 | 3 | .20 | 0 | .80 | 54 | 1.40 | 38.6 | .272 |

**INFERRED.** Apply the binary rows separately to exact start, ±1 start, exact end and ±1 end, using a different p/rho when warranted. Tolerant success must be at least exact success on the same denominator, but none of their actual p values is known. Dependence between the four metrics does not provide four independent samples. At p near 1 and small K, boundary effects/zero observed failures make the approximation optimistic; bootstrap replication cannot discover unobserved failures.

| Expected p (assumed) | Issuers needed for width .10 | Width .20 | Width .30 |
|---:|---:|---:|---:|
| .50 | 141 | 38 | 18 |
| .80 | 91 | 25 | 13 |
| .95 | 29 | 10 | 6 |

**VERIFIED arithmetic / INFERRED target assumptions.** This table solves the same heuristic for K with m=5, rho=.20 and CV=0. It is not an acquisition proposal, allocation to existing splits, or powered prescription. Targets exceeding the available independent final issuers require a narrower precision claim or a later separately authorized new evaluation design, not moving FIT issuers into HOLDOUT.

| tIoU marginal SD assumed | Width at K=9, m=6, rho=.20 |
|---:|---:|
| .15 | .133 |
| .25 | .222 |
| .35 | .311 |

**INFERRED.** Mean tIoU alone cannot determine its variance: mass at zero from missed spans and mass at one from exact spans matter. For C2/C3 use the SD of paired differences, including covariance between arms, rather than independent-arm binomial variance. A future segregated FIT calibration may inform these assumptions; it cannot inspect final outcomes to choose precision goals.

**VERIFIED arithmetic / INFERRED missing-span scenario.** If conditional boundary success among found spans is .80 and missed-span fractions are .00/.10/.20, unconditional rates are .80/.72/.64. Excluding misses would hide deterioration. Missing spans also reduce mean IoU when scored zero. Gold ambiguity, true absence and unavailable bytes are distinct states, not interchangeable missing spans.

## What can nine final issuers support?

**INFERRED.** Nine issuers and 54 documents are the available aggregate maximum, not a verified count of present, adjudicable MD&A spans. Blind Gold eligibility and reference completion may reduce both K and N; the resulting uncertainty may be wider.

| Claim | INFERRED assessment of adequacy; no final data inspected |
|---|---|
| C1 descriptive | Defensible for a carefully bounded finite-partition description with all eligible documents and honest uncertainty. Insufficient to promise narrow population precision or rare-condition performance. |
| C2 improvement | May show a large consistent paired effect; small/moderate effects or narrow superiority margins may be inconclusive. Requires pilot paired variance, influence analysis, baseline identity and B6/B8. |
| C3 Oracle contribution | NOT YET SUPPORTABLE regardless of n: page→document transformation missing. Current Oracle is FIT/VALIDATION; nine HOLDOUT issuers do not repair it. |
| C4 downstream stability | Not a blanket basis for national panel/regression robustness; depends on actual financial sample, score-error structure and model. A bounded descriptive perturbation study may still be useful. |
| C5 case study | Does not require HOLDOUT. Use later authorized FIT/VALIDATION cases and make no population accuracy claim. |

**INFERRED.** FIT/VALIDATION offers development capacity, not proven Gold adequacy. FIT is suitable for protocol calibration and diagnosis; validation can compare a limited predeclared set of choices. Existing diversity-selected roster and sparse page samples cannot guarantee document-span reliability, rare failure coverage or independent population agreement. More pages within the same report cannot substitute for more independent document spans/issuers. Repeated validation-driven tuning should be disclosed; final Gold decisions remain prospective.

## Q7 options

All effort values: **AUTHOR-EFFORT ESTIMATE — planning estimate, not measured fact**; incremental analysis/protocol effort excluding actual annotation and model execution.

| Option | Validity and defensibility | Effort / assumptions | Reversibility | Dependencies / likely examiner challenge |
|---|---|---|---|---|
| A — full-rigor | Define target width/effect, pilot paired variance and issuer concentration, assess interval coverage under plausible bounded outcome distributions; retain independent agreement sample | 4–7 researcher-days, assuming statistical tooling and segregated FIT references available | Reversible before sampling/protocol freeze; final exposure irreversible | B6/B8, baseline for C2, transformation for C3; “Do you have enough independent issuers?” |
| B — proportionate | Plan against wide precision scenarios; report document and issuer estimates/influence, no unsupported tight interval claim; calibrate reliability | 2–4 days with existing coding environment; Gold effort separate | Reversible before Gold Method freeze | B6/B8; “Why is this precision enough for the thesis wording?” |
| C — do-less | C5 purposeful case set, transparent misses and disagreement; no representative rate/CI | 1–2 days to design case reporting, plus independent review | Easy to expand before final exposure; cannot relabel tuned cases as unseen | Proportionate B6; “What can the selected examples actually establish?” |

## Q8: decision rule for the 14 missing PDFs

**REPO-VERIFIED.** PC-04/P2-15: the missing records are historical-label entries without available bytes; eight are UNASSIGNED_HISTORICAL and six administratively INPUT_UNAVAILABLE (two FIT, four VALIDATION). They do not enlarge the executable denominator. Historical labels are not newly adjudicated Gold.

| Candidate | PROPOSED decision rule / trigger | Frame, validation, Gold and final consequence |
|---|---|---|
| C1 | If target is bytes-available frozen final reports, acquisition unnecessary. If author expands to all inventory records, account for missing outcomes and revise claim before evaluation. | Available-byte denominator excludes them by definition; national/population coverage still unresolved. Existing final population unchanged. |
| C2 | If comparison concerns present frozen bytes, no acquisition. If “reproduces historical As-Is performance” depends on missing historically scored documents, authentic bytes/runtime/provenance become required evidence. | Historical reproduction becomes unavailable unless matched inputs recovered; failure to recover narrows claim, not zero accuracy. New bytes need an authorized frame/protocol amendment. |
| C3 | No acquisition merely to increase Oracle pages. Trigger only if the chosen intervention population explicitly includes a missing record or a justified, otherwise unsupported mechanism. | Requires full reference/transform design first; newly retrieved cases remain diagnostic unless sampling eligibility legitimately changes. |
| C4 | If the downstream financial panel includes these report–FY records, evaluate whether selective missingness changes score/regression coverage; bounded acquisition may become necessary. | Missing score is not zero; financial eligibility and extraction availability both affect denominator. Independent new references required; no auto-entry to final partition. |
| C5 | No acquisition for present enumerated cases. Trigger only if an explicitly named indispensable historical case is central to the chosen case study. | Otherwise disclose inability to inspect it and choose/narrow cases prospectively; no representative inference. |

**PROPOSED.** Bounded future acquisition, if triggered, means only the exact historically identified report–FY items needed by the chosen claim, beginning with those necessary to test the disputed historical comparison or panel coverage; record source/version, byte identity and split eligibility. Do not acquire all missing files automatically or recast a recovered variant as the original. If original identity cannot be established, use UNVERIFIED rather than claiming reproduction. P1 neither changes the existing no-acquisition position nor fetches PDFs.

## Reproduction receipt

**VERIFIED.** Python 3.14.3 / SciPy 1.18.0 produced the numeric tables above on 2026-09-23. Run the following as standalone planning arithmetic; it imports no ARPipe modules and reads no project data:

```python
from math import sqrt
from scipy.stats import t
rows = [(9,6,0,0,.8),(9,6,.2,0,.8),(9,6,.5,0,.8),
        (9,6,.2,.5,.8),(9,6,.2,0,.5),(9,6,.2,0,.95),
        (18,5,.2,0,.8),(27,5,.2,0,.8),(36,5,.2,0,.8),
        (9,3,.2,0,.8),(18,3,.2,0,.8)]
for K,m,rho,cv,p in rows:
    n = K*m
    deff = 1 + ((1+cv**2)*m-1)*rho
    neff = n/deff
    width = 2*t.ppf(.975,K-1)*sqrt(p*(1-p)/neff)
    print(K,m,rho,cv,p,n,round(deff,2),round(neff,1),round(width,3))
for p in [.5,.8,.95]:
    print(p, [(w,next(K for K in range(3,10000)
          if 2*t.ppf(.975,K-1)*sqrt(p*(1-p)*1.8/(K*5)) <= w))
          for w in [.1,.2,.3]])
for sd in [.15,.25,.35]:
    print(sd,round(2*t.ppf(.975,8)*sd/sqrt(54/2),3))
print([(q,round(.8*(1-q),2)) for q in [0,.1,.2]])
```

**REPO-VERIFIED provenance commands** for the project numbers (read published aggregate reports only; no new HOLDOUT access):

```powershell
$START_SHA = '24520ce623037fde7c3b0a9d0d4e5f8fc5618831' # command-derived starting receipt
git rev-parse $START_SHA
git show "${START_SHA}:dataset/corpus_freeze/stratification_report.md"
git show "${START_SHA}:docs/experiments/PHASE2_FOUNDATION_INTEGRITY_AUDIT.md"
git show "${START_SHA}:docs/experiments/PHASE2.1_PROVENANCE_CORRECTIONS.md"
```

**UNRESOLVED.** Actual endpoint distributions, issuer ICC, per-claim eligible Gold counts, annotator speed, baseline paired correlation and the intended national/panel target are not measured in P1. No table value is a frozen sampling requirement.
