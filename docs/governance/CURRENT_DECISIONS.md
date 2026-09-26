# ARPipe current governance decisions

**Governance version/date:** 2026-09-26 author-ratified closeout

**Canonical status:** CURRENT

**Ratification:** [AUTHOR_RATIFICATION_2026-09-26.md](AUTHOR_RATIFICATION_2026-09-26.md)

**Historical observation point:** [pb-snapshot-2026-09-26](pb-snapshot-2026-09-26/README.md), source commit `15c9debefe1c43c1d5e63842eb87fa5aacf73df4`

**R1 evidence anchor:** `53dcab40c374b499637ad3f68596549540ef1c42`

Future tasks must use this file for current governance. The dated addendum is
the authoritative detailed record and contains the complete signed v3 source.
The P-B snapshot is historical and must not be edited.

## Current-status ledger

| id | current status | operative decision or condition |
|---|---|---|
| 0a | RATIFIED | Private-copy status is `not yet`; do not claim an approved or durable private archive. |
| 0b | RATIFIED | ARPipe `docs/governance/` is the single canonical current-governance home. |
| 0c | RATIFIED | After this closeout, create no new ledger/snapshot unless an author decision changes; use protocols, SAP and amendments normally. |
| PG-1 | RATIFIED | D1–D10, as condensed in Phase 4 §0 and preserved in P-B, are the author's operative wording. Original messages are unavailable and must not be reconstructed. |
| Q1b | RATIFIED | After final system freeze, make no code, configuration, threshold, pattern or model change before the single HOLDOUT scoring run. A later change is a separately evaluated version. Pre-freeze development uses FIT and VALIDATION only. |
| Q2 | RATIFIED | HOLDOUT is the single headline result: 54 documents, 9 issuers × 6 documents. VALIDATION is separately labelled “development check” and never pooled. FIT supports rules, pilot and error analysis. |
| Q3 | RATIFIED | Second annotator, independent rules reviewer, seal holder and separate adjudicator are available. The adjudicator is neither developer nor annotator on the documents concerned. |
| Q4 | RATIFIED | HOLDOUT receives full independent double annotation by author and second annotator. VALIDATION receives author annotation plus predeclared random second-annotator overlap of at least one document per issuer. Raw A/B records are immutable; agreement uses raw records; disagreements go to the separate adjudicator with reasons. |
| Q5 | RATIFIED | Freeze and push governance; freeze and push the system; run HOLDOUT once; hash-seal unopened outputs; push/give hashes to seal holder; create blind Gold; freeze Gold; score once; publish. Rerun only after infrastructure failure producing no output, with failure log. |
| Q6 | RATIFIED | Primary is document-weighted mean page-span IoU over HOLDOUT documents whose Gold says MD&A present. Missing, invalid and quarantined predictions score 0. Absent Gold is excluded from IoU and evaluated via presence. Pre-output ambiguous Gold is excluded from primary and used in labelled optimistic sensitivity. Complete-case accuracy is conditional secondary with coverage. |
| Q7 | RATIFIED | Accepted Gold edge-case rules cover absence, multiple spans, bilingual, non-contiguous, embedded, annexure, uncertain boundaries, unusual titles and unresolvable cases. Page convention is 0-based physical page index. |
| Q8 | RATIFIED | `CENSUS`: report exact frozen-HOLDOUT performance, per-issuer distribution and leave-one-issuer-out analysis. Any interval is a SAP-fixed sensitivity only and cannot support generalisation to all Indian companies. |
| Q9 | RATIFIED | Use the exact historically exposed HOLDOUT wording in the signed ratification. Do not call HOLDOUT historically unseen. Any further counts must come from the exposure inventory. |
| Q10 | RATIFIED | Climate exposure is substantive. Intended measure is Sautner-style and bigram-based, hence order-sensitive. Fix the exact recipe before C4. C4 and B7 wait; C1 does not. |
| B1 | RATIFIED | Operational route is `broken_text → OCR`. Legacy is a research attribute; REMAP is a registered research track. Disclose native reading of corrupted text layers that pass the control-character test. Pre-commit Phase 9 checks of MD&A boundary failures for bilingual-copy and corrupted-heading causes. |
| B2 | NOT_APPLICABLE | N/A while B1 stands. Reopens only if a second operational route or signal is added. Sampling priority is never routing precedence. |
| B3 | DEFERRED | Trigger: routing or Oracle claim adopted. Do not construct the Oracle population now. |
| B4 | DEFERRED | Trigger: same as B3. Separately, Q4 random overlap requires a new Phase 5 DocumentGold selector specified mechanically from the predeclared roster. Do not construct it in closeout. |
| B5 | DEFERRED | Trigger: same as B3. Do not construct Oracle evidence now. |
| B6 | RATIFIED | Gold structure is accepted as Q3 + Q4: separate-person adjudicator, full HOLDOUT double annotation and VALIDATION overlap. |
| B7 | DEFERRED | Trigger: Q10 recipe fixed and order-sensitive. B7 is not moot. |
| B8 | RATIFIED | HOLDOUT governance is accepted as Q5 plus Q9. |
| As-Is | DEFERRED | No 2026-09-17 baseline is adopted. R1 at `28a67b63d890d8407fa9738a71ae37ad63148b73` is runnable identity, not a thesis comparator. Trigger: Phase 10 experiment marked KEEP. |
| C1 | PENDING_AUTHOR_DECISION | No standalone C1 author line exists. Its operative components are separately ratified through D1, Q2, Q6 and CC-4. This provenance status is not an extra Phase 5 governance-entry prerequisite. |
| C2 | DEFERRED | Trigger: Phase 10 experiment marked KEEP. Comparator is the pinned system immediately preceding that change under D6; without a coherent comparator, make no baseline-relative improvement claim. |
| CC-4 | RATIFIED | Primary endpoint is page-span IoU. Secondaries: presence accuracy, exact start/end, ±1 start/end, exact full-span match, and signed start/end errors reported as quantiles. Exact definitions belong in the Phase 5 metric protocol. |

## Key dependencies

| dependency | current consequence |
|---|---|
| B2 ↔ B1 | B2 remains N/A while the single B1 route stands. |
| B4 ↔ Q4 | Historical Oracle selector stays deferred; Q4 overlap uses a new Phase 5 DocumentGold selector. |
| B6 ↔ Q3 + Q4 | Personnel and full/overlap structure jointly define the ratified Gold design. |
| B8 ↔ Q5 + Q9 | Prospective sequence and truthful exposure disclosure jointly define HOLDOUT governance. |
| B7 ↔ Q10 | Reading-order reference waits for a fixed, order-sensitive climate recipe. |
| C2 ↔ As-Is | Both remain deferred until a Phase 10 experiment is marked KEEP. |
| C1 components | D1 scope + Q2 population + Q6 scoring + CC-4 endpoint are separately ratified. |

## Information barriers

Gold must be blind. Annotators have no repository access and see no ARPipe
output. `AMBIGUOUS` is assigned before system output is viewed. Before
adjudication completes, the adjudicator may see only frozen Gold rules,
independent A and B annotations, and information needed to resolve the
disagreement. The adjudicator may not see predictions, prediction hashes,
evaluation reports, C1 scores, HOLDOUT system outputs, repository contents, or
prior ARPipe labels/predictions. Reasons are recorded independently.

## Phase 5 governance entry

**Verdict: `ENTRY_SATISFIED`.** Governance prerequisites for Phase 5 entry are
ratified: Q2, Q3, Q4/B6, Q6, CC-4, Q5/B8 and Q9 are each satisfied.

This verdict does **not** mean Gold is ready or exists, methodology is
scientifically validated, C1 has been measured, ARPipe has a measured accuracy,
a HOLDOUT result exists, or the climate result is complete. Q6 still requires
the formal C1-D1 Level C amendment at the Phase 5 Gold freeze; that amendment is
future work and is not implemented here.
