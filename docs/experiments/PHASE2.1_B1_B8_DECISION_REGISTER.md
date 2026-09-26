# Phase 2.1 — B1–B8 Decision Register & Governance Specification

**Status:** current author-ratified register

**Decision authority:** Hariom Singh

**Ratification date:** 2026-09-26

**Ratification source:** `docs/governance/AUTHOR_RATIFICATION_2026-09-26.md`

**Current-governance index:** `docs/governance/CURRENT_DECISIONS.md`

**Historical preparation base:** `03a63f5d7d79bac6a0bab0ffc33af42004e78935`

The signed ratification supersedes this register's prior all-pending
preparation state. It authorizes governance bookkeeping only. It does not
authorize Gold construction, OCR execution, Oracle construction, experiments,
HOLDOUT access, C1, C4, B7 implementation, or Phase 5 execution.

## 1. Current status summary

```text
PHASE2.1_STATUS = AUTHOR_RATIFICATION_RECORDED

DOWNSTREAM_EXECUTION_AUTHORIZED = NO
GOLD_ANNOTATION_AUTHORIZED = NO
OCR_EXECUTION_AUTHORIZED = NO
EXPERIMENT_X1_X7_AUTHORIZED = NO
HOLDOUT_ACCESS_AUTHORIZED = NO

B1_STATUS = RATIFIED
B2_STATUS = NOT_APPLICABLE
B3_STATUS = DEFERRED
B4_STATUS = DEFERRED
B5_STATUS = DEFERRED
B6_STATUS = RATIFIED
B7_STATUS = DEFERRED
B8_STATUS = RATIFIED

FORMAL_T0.4_AMENDMENT_EFFECTIVE = NO
```

## 2. Current B1–B8 records

### B1 — Legacy Route & Class-to-Route Map

- **decision_id:** `DEC-B1`
- **status:** `RATIFIED`
- **author:** Hariom Singh
- **timestamp:** `2026-09-26`
- **selected_option:** Keep `broken_text → OCR` as the only operational route.
- **decision:** Legacy is a research attribute; REMAP is a registered research
  track. Disclose that corrupted text layers passing the control-character test
  are read natively. Pre-commit a Phase 9 check of every MD&A boundary failure
  for bilingual-copy and corrupted-heading causes.
- **interpretation_constraint:** Do not create a production REMAP route.
- Retain legacy as a separate forensic research attribute/track.
- This does not establish that REMAP is useless.
- This does not establish that legacy-font pages are absent.
- Genuine legacy-font occurrence remains unresolved.
- **effective_protocol_version:** `governance-closeout-2026-09-26`
- **dependencies:** B2 remains N/A while this single operational route stands.

### B2 — Route Precedence for Overlapping Classes

- **decision_id:** `DEC-B2`
- **status:** `NOT_APPLICABLE`
- **author:** Hariom Singh
- **timestamp:** `2026-09-26`
- **condition:** N/A while B1 stands.
- **reopen_trigger:** A second operational route or signal is added.
- **constraint:** Sampling priority is never routing precedence.
- **effective_protocol_version:** `governance-closeout-2026-09-26`
- **dependencies:** Strictly dependent on B1.

### B3 — Oracle Routing Population Specification

- **decision_id:** `DEC-B3`
- **status:** `DEFERRED`
- **author:** Hariom Singh
- **timestamp:** `2026-09-26`
- **reopen_trigger:** A routing or Oracle claim is adopted.
- **decision:** Do not construct an Oracle population now.
- **effective_protocol_version:** `governance-closeout-2026-09-26`
- **dependencies:** If triggered, defines the historical Oracle population and
  reopens B4/B5.

### B4 — Deterministic Double-Annotation Selector

- **decision_id:** `DEC-B4`
- **status:** `DEFERRED`
- **author:** Hariom Singh
- **timestamp:** `2026-09-26`
- **reopen_trigger:** Same as B3 — a routing or Oracle claim is adopted.
- **decision:** The historical Oracle selector is deferred. Do not construct it
  now. Separately, Q4's random VALIDATION overlap requires a new DocumentGold
  selector, specified mechanically in Phase 5 from the predeclared roster.
- **effective_protocol_version:** `governance-closeout-2026-09-26`
- **dependencies:** Historical selector depends on B3; the distinct future
  DocumentGold selector depends on Q4.

### B5 — Oracle Scientific Construct & Evidence Channels

- **decision_id:** `DEC-B5`
- **status:** `DEFERRED`
- **author:** Hariom Singh
- **timestamp:** `2026-09-26`
- **reopen_trigger:** Same as B3 — a routing or Oracle claim is adopted.
- **decision:** Do not construct Oracle evidence now.
- **effective_protocol_version:** `governance-closeout-2026-09-26`
- **dependencies:** Depends on B3 and any activated Oracle claim.

### B6 — PageGold & DocumentGold Reliability Design

- **decision_id:** `DEC-B6`
- **status:** `RATIFIED`
- **author:** Hariom Singh
- **timestamp:** `2026-09-26`
- **selected_option:** Full double annotation on HOLDOUT; overlap on VALIDATION.
- **decision:** The author and second annotator independently annotate all 54
  HOLDOUT documents. The author annotates all VALIDATION documents; the second
  annotator independently annotates a random overlap of at least one document
  per issuer, drawn from the predeclared roster before annotation. Raw A/B
  records are immutable; agreement is computed from raw records; disagreements
  go to the separate adjudicator with independently recorded reasons. Hard FIT
  cases remain diagnostic and are never pooled into Gold.
- **information_barrier:** Annotators see no ARPipe output and have no repository
  access. The adjudicator sees only frozen rules, A and B annotations, and
  information necessary to resolve the disagreement until adjudication ends.
- **effective_protocol_version:** `governance-closeout-2026-09-26`
- **dependencies:** Q3 + Q4. This ratifies design; it does not authorize Gold.

### B7 — Reading-Order Reference Unit & Representation

- **decision_id:** `DEC-B7`
- **status:** `DEFERRED`
- **author:** Hariom Singh
- **timestamp:** `2026-09-26`
- **reopen_trigger:** The Q10 recipe is fixed and is order-sensitive.
- **decision:** Reading-order reference work is deferred and is not moot. Do not
  implement B7 during governance closeout.
- **effective_protocol_version:** `governance-closeout-2026-09-26`
- **dependencies:** Q10.

### B8 — HOLDOUT Gold Annotation Governance

- **decision_id:** `DEC-B8`
- **status:** `RATIFIED`
- **author:** Hariom Singh
- **timestamp:** `2026-09-26`
- **selected_option:** Q5 prediction-first, hash-sealed custody sequence with Q9
  truthful historical-exposure wording.
- **decision:** Freeze and push governance, then freeze and push the system; run
  the frozen system once on HOLDOUT; hash-seal unopened outputs; push and give
  hashes to the seal holder; create blind HOLDOUT Gold outside repository
  access; freeze Gold; score once; publish. Rerun only for infrastructure
  failure producing no output, with the failure log published.
- **effective_protocol_version:** `governance-closeout-2026-09-26`
- **dependencies:** Q5 + Q9. This ratifies future governance; it does not
  authorize HOLDOUT access in this closeout.

## 3. Adjudicator barrier

Before adjudication is complete, the adjudicator may see only frozen Gold
rules, independent A annotation, independent B annotation, and information
necessary to resolve disagreement. The adjudicator must not see ARPipe
predictions, prediction hashes, evaluation reports, C1 scores, HOLDOUT system
outputs, repository contents, or prior ARPipe labels/predictions. Reasons are
recorded independently.

## 4. Historical and future-work boundary

This register does not alter frozen T0/T0.4 artifacts. It does not implement a
DocumentGold selector, Gold protocol, SAP, C1-D1 amendment, Gold annotations,
OCR, C1, C4, B7 or HOLDOUT execution. The prior preparation recommendations
remain historical evidence in Git history; the statuses above are the current
author-ratified dispositions.
