# C1-D1 Level C amendment draft

**Document status:** `DRAFT_PENDING_AUTHOR_RATIFICATION`

**Method-package status:** `DRAFT_PENDING_PILOT`

**PROPOSED.** This file is a draft amendment record modeled on
`docs/identity/T0_4_AMENDMENT_01.md`. Nothing in it is effective, frozen, adopted, or an
authorization to score. The author fields remain blank.

**PROPOSED.** Every substantive paragraph or table row outside quoted source text is
prefixed with one of `VERIFIED`, `SOURCED`, `DERIVED`, `INFERRED`, or `PROPOSED`.
Headings, equations, and citations inherit the nearest explicit label.

## 1. Draft amendment text

**PROPOSED.** If the author approves an amended version, the finalized text between the
fences must be hash-sealed and recorded without silently editing any frozen T0.4 file.

~~~text
------------------------------------------------------------
C1-D1 LEVEL C AMENDMENT — FAILURE-INCLUSIVE DOCUMENT SCORING
(C_ARPIPE_DOCUMENT_TASK ONLY)
------------------------------------------------------------

STATUS: DRAFT_PENDING_AUTHOR_RATIFICATION
METHOD_PACKAGE_STATUS: DRAFT_PENDING_PILOT

1. ORIGINAL CONTRACT

SOURCED. configs/t0_4/metrics_spec.json lines 44-69 defines Level
C_ARPIPE_DOCUMENT_TASK with:

    unit = document
    primary = page_span_iou

and secondary metrics including present/absent accuracy, IoU thresholds,
exact and within-one start/end, boundary distances, overrun, underrun,
candidate recall, verification, and quality-gate metrics.

SOURCED. configs/t0_4/metrics_spec.json lines 120-122 says paired
differences use only units with both outputs and include that paired
denominator. The frozen Level C block itself states no eligibility denominator,
missing-prediction rule, invalid-prediction rule, quarantine rule, empty-Gold
IoU rule, or ambiguity-aware rule.

SOURCED. configs/t0_4/gold_schema.json lines 95-118 supplies a document
record with mda_present, start/end, a free boundary_ambiguity string, and
provenance, but no controlled ambiguity codes or admissible_spans.

2. EXACT CONFLICT / GAP

SOURCED. D1's operative claim is reproducible START-END page-span localization
in the defined corpus (docs/phase4/PHASE4_B1_B8_TRIAGE.md line 18).

VERIFIED. docs/phase4/PHASE4_B1_B8_TRIAGE.md lines 165-220 records finding
C1-D1: Level C cannot express missing and invalid output, has no absent-Gold
primary-denominator rule, has no structured ambiguity/admissible-span rule,
and would make paired results conditional on successful output.

SOURCED. Q6 now fixes a different, failure-inclusive estimand:

    document-weighted mean page-span IoU over HOLDOUT documents where Gold
    says MD&A is PRESENT;
    missing, invalid, and QUARANTINE predictions score zero;
    ABSENT Gold is excluded from IoU and evaluated through presence;
    pre-output AMBIGUOUS Gold is excluded from primary and receives a labelled
    optimistic admissible-span sensitivity.

Source: docs/governance/CURRENT_DECISIONS.md line 30 and
docs/governance/AUTHOR_RATIFICATION_2026-09-26.md lines 312-334.

DERIVED. Without an explicit amendment, a successful-output denominator could
silently discard the failures covered by D1, while assigning IoU to ABSENT or
AMBIGUOUS Gold would invent rules absent from the frozen contract.

3. AMENDED LEVEL C RULE

PROPOSED. This amendment is a normative overlay for C_ARPIPE_DOCUMENT_TASK; it
does not rewrite configs/t0_4/metrics_spec.json or configs/t0_4/gold_schema.json.

PROPOSED. Population and primary denominator:

    H_PRESENT = HOLDOUT documents whose frozen adjudicated Gold state is PRESENT
                with a valid inclusive primary span.

    primary_C1 = sum(i in H_PRESENT, IoU_i) / count(H_PRESENT)

The mean is document-weighted. If H_PRESENT is empty, report NOT_ESTIMABLE.
Report its denominator and counts of PRESENT, ABSENT, and AMBIGUOUS Gold.

PROPOSED. Inclusive span IoU for a valid prediction P=[p_s,p_e] and Gold
G=[g_s,g_e]:

    intersection = max(0, min(p_e,g_e) - max(p_s,g_s) + 1)
    union = (p_e-p_s+1) + (g_e-g_s+1) - intersection
    IoU = intersection / union

PROPOSED. Prediction validity requires exactly one sealed row matching the
document ID and source-PDF SHA-256, a positive integer physical page count N,
and non-Boolean JSON-integer boundaries satisfying 0 <= start <= end < N.

PROPOSED. No row is MISSING. After duplicate and identity checks, a sole
identity-matching QUARANTINE row is classified as QUARANTINE regardless of its
boundary fields. Otherwise a null/missing boundary is MISSING. Duplicate rows,
identity/hash mismatch, non-integer/Boolean boundaries, start > end, or a
boundary outside [0,N-1] is INVALID and is reported by subtype. No value is
coerced, clipped, reordered, selected from duplicates, or repaired.

SOURCED. For H_PRESENT, MISSING, INVALID, and QUARANTINE each receive IoU=0.
QUARANTINE is additionally reported as abstention. A numeric span attached to
QUARANTINE does not override the zero rule.

SOURCED. ABSENT Gold does not enter the IoU denominator and is never IoU=1.
Presence is a separate 2x2 endpoint on unambiguous Gold. A valid,
non-quarantined span means predicted present; missing, invalid, or quarantined
output means predicted absent.

SOURCED. AMBIGUOUS Gold is assigned before system output, excluded from the
primary with its count reported, and analyzed only in a labelled optimistic
sensitivity. For valid output the optimistic value is the maximum IoU over the
predeclared admissible spans; missing, invalid, or quarantine receives zero.

SOURCED. Secondary endpoints are presence accuracy, exact start, exact end,
within-one start, within-one end, exact full-span match, and signed start/end
errors as quantiles. Exact/within-one/span indicators use H_PRESENT and score
missing, invalid, and quarantine as false. Signed numeric errors are complete-
case only, with coverage and failures reported.

PROPOSED. Exact endpoint equations, type-7 quantiles, ambiguity sensitivity,
issuer reporting, agreement, and all denominators are fixed by the frozen
successor of docs/phase5/SAP_v0.md. The SAP cannot contradict the rules above.

4. REASON

SOURCED. D1 covers localization in the bounded population, and Q6 requires
failures to remain visible instead of disappearing. The amendment aligns the
Level C scoring contract with that claim and fixes absence/ambiguity treatment
before HOLDOUT output can influence the rules.

5. EFFECT ON SCORING

PROPOSED. The headline C1 value becomes failure-inclusive over H_PRESENT.
Missing/invalid/quarantine output can lower the primary instead of reducing its
denominator. ABSENT performance is visible only in presence metrics. Ambiguous
documents cannot change the primary and enter only the named optimistic
sensitivity. Complete-case metrics remain conditional secondaries with
coverage.

PROPOSED. This amendment changes no system prediction, document roster, Gold
decision, routing rule, PDF byte, or T0.4 benchmark result. It defines future
C1 accounting only.

6. FROZEN-MATERIAL CONFIRMATION

VERIFIED. P5-A does not edit configs/t0_4/, artifacts/t0_4/, tools/t0_4/,
tests/t0_4/, arpipe/, dataset/, or conftest.py. The original T0.4 contract and
schema remain byte-preserved. This draft is a separate future-facing record.

7. EFFECTIVE CONDITION

PROPOSED. This amendment has no effect unless the author fills the fields
below, explicitly ratifies the finalized text, the final protocol/SAP are
reviewed and frozen, and the resulting hashes are recorded before HOLDOUT
scoring. P5-A does not satisfy those conditions.

AUTHOR:

DATE:

CHANGES TO THIS DRAFT:

------------------------------------------------------------
END AMENDMENT DRAFT
------------------------------------------------------------
~~~

## Annex A — Evidence crosswalk

| Object | Exact repository evidence | Status |
|---|---|---|
| D1 scope | `docs/phase4/PHASE4_B1_B8_TRIAGE.md:18` | `SOURCED` |
| Frozen Level C unit/primary/secondaries | `configs/t0_4/metrics_spec.json:44-69` | `VERIFIED` |
| Frozen missing-pair policy | `configs/t0_4/metrics_spec.json:120-122` | `VERIFIED` |
| Frozen DocumentGold limitations | `configs/t0_4/gold_schema.json:95-118` | `VERIFIED` |
| C1-D1 conflict analysis | `docs/phase4/PHASE4_B1_B8_TRIAGE.md:165-220` | `VERIFIED` |
| Current Q6 rule | `docs/governance/CURRENT_DECISIONS.md:30` and `docs/governance/AUTHOR_RATIFICATION_2026-09-26.md:312-334` | `SOURCED` |
| Current CC-4 endpoint set | `docs/governance/CURRENT_DECISIONS.md:46` | `SOURCED` |
| Amendment remains future work | `docs/governance/CURRENT_DECISIONS.md:75-79` | `SOURCED` |

**DERIVED.** The conflict is limited to future C1 Level C accounting. It does not require
or authorize changing the T0.4 artifacts that exposed the gap.

## Annex B — Proposed machine-readable overlay

**PROPOSED.** The following is an informative representation for the future frozen
scorer. It is not a patch to `configs/t0_4/metrics_spec.json`.

```json
{
  "amends_level": "C_ARPIPE_DOCUMENT_TASK",
  "unit": "document",
  "primary": "document_weighted_mean_page_span_iou",
  "primary_gold_eligibility": "PRESENT",
  "interval_convention": "inclusive_zero_based_physical_pdf_pages",
  "missing_prediction_iou": 0,
  "invalid_prediction_iou": 0,
  "quarantine_prediction_iou": 0,
  "absent_gold_primary_membership": false,
  "absent_gold_endpoint": "presence_2x2",
  "ambiguous_gold_primary_membership": false,
  "ambiguous_gold_sensitivity": "maximum_iou_over_preoutput_admissible_spans",
  "complete_case_status": "conditional_secondary_with_coverage"
}
```

## Annex C — Decisions consumed and explicit non-effects

**SOURCED.** D1/PG-1 defines the claim; Q2 defines the headline population; Q6 defines the
estimand and failure/absence/ambiguity rules; CC-4 defines the endpoint set; Q5/B8 and Q8
constrain later execution/reporting; and Q7 defines the Gold page convention
(`docs/governance/CURRENT_DECISIONS.md:24,26,29-32,42,46`).

**SOURCED.** Q1b, Q3/Q4/B6, Q9, B1, and the B4 note remain operative around the amendment
but are not changed by it.

**SOURCED.** B3, the historical B4 Oracle, B5, B7, C2, As-Is, Q10's recipe, and C4 remain
deferred and receive no rule from this draft.

**PROPOSED.** Author ratification must occur later; P5-A leaves `AUTHOR`, `DATE`, and
`CHANGES TO THIS DRAFT` blank and makes no frozen modification.
