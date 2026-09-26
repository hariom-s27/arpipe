# C1-D1 Level C amendment draft v0.1

**Document status:** `DRAFT_PENDING_AUTHOR_RATIFICATION`

**Method-package status:** `DRAFT_PENDING_PILOT`

**PROPOSED.** This is a future-facing amendment record. Nothing in it is effective and
it does not edit any T0.4 object or authorize scoring. The block below contains no
evidence labels or source line numbers so a later signed hash does not freeze mutable
citation positions; evidence is in the annexes.

## 1. To-be-signed block

~~~text
------------------------------------------------------------
C1-D1 LEVEL C AMENDMENT — FAILURE-INCLUSIVE DOCUMENT SCORING
(C_ARPIPE_DOCUMENT_TASK ONLY)
------------------------------------------------------------

STATUS: DRAFT_PENDING_AUTHOR_RATIFICATION
METHOD_PACKAGE_STATUS: DRAFT_PENDING_PILOT

1. PURPOSE AND SCOPE

This amendment is a normative overlay for future C_ARPIPE_DOCUMENT_TASK scoring. It
does not rewrite the T0.4 metric specification or Gold schema, change any system output,
or change the document population.

2. GOLD ANALYSIS STATES

H_PRESENT contains HOLDOUT documents whose adjudicated Gold is PRESENT with a valid
inclusive primary span. H_ABSENT contains adjudicated ABSENT records. H_AMBIGUOUS
contains pre-output AMBIGUOUS records with admissible spans.

3. PREDICTION STATUS

Assign one status in this order:

    NO_OUTPUT: no sealed row exists. If no row exists, the status is NO_OUTPUT.
    DUPLICATE: more than one row claims the document.
    IDENTITY_INVALID: document ID or source-PDF hash does not match.
    QUARANTINE: the identity-matching row is quarantined, regardless of boundaries.
    NOT_LOCATED: the identity-matching non-quarantined result has a null span and the
                 existing mda_not_located reason.
    TYPE_INVALID: boundaries/page count have invalid types, or null-span representation
                  contradicts the not-located reason.
    ORDER_INVALID: start is greater than end.
    RANGE_INVALID: a boundary is outside [0,N-1].
    VALID: exactly one identity-matching, non-quarantined row has integer boundaries
           satisfying 0 <= start <= end < N.

Do not select from duplicates, clip, coerce, reorder or repair values.

4. PRIMARY

For valid prediction P=[p_s,p_e] and Gold G=[g_s,g_e], endpoints are inclusive:

    intersection = max(0, min(p_e,g_e) - max(p_s,g_s) + 1)
    union = (p_e-p_s+1) + (g_e-g_s+1) - intersection
    IoU = intersection / union

    primary_C1 = sum(IoU_i for i in H_PRESENT) / count(H_PRESENT)

The mean is document-weighted. If H_PRESENT is empty, report NOT_ESTIMABLE. For
H_PRESENT, NO_OUTPUT, NOT_LOCATED, QUARANTINE and every invalid subtype receive IoU=0.
Report the denominator and every Gold-state and prediction-status count.

5. PRESENCE

ABSENT Gold is excluded from IoU and is never IoU=1. Report the full 2x3 table with Gold
PRESENT/ABSENT as rows and predicted PRESENT / NOT_LOCATED / FAILED_OR_ABSTAINED as
columns. Only NOT_LOCATED on ABSENT Gold is a true negative.

Also report a collapsed 2x2 in which every FAILED_OR_ABSTAINED result is wrong: failures
on PRESENT enter the false-negative cell; failures on ABSENT enter the false-positive
cell. This scoring collapse does not turn a failure into an absence claim.

6. AMBIGUITY AND SECONDARIES

AMBIGUOUS is assigned before viewing output, excluded from primary, and analyzed in a
labelled optimistic sensitivity over the predeclared admissible readings. A valid span
uses maximum admissible-span IoU. Failed or abstained output receives zero. For
PRESENCE_UNRESOLVABLE, NOT_LOCATED receives optimistic value one because absence is an
admissible reading.

Secondaries are exact start, exact end, within-one start, within-one end, exact full-span
match, signed start/end errors as type-7 quantiles, complete-case accuracy with coverage,
presence, failures and abstentions.

7. ISSUER SENSITIVITY

Issuer-weighted is reported as a sensitivity. Compute each issuer's mean over its
H_PRESENT documents using the same failure-inclusive IoU, then take the unweighted mean
of eligible issuer means. Exclude and count issuers with no eligible PRESENT document.

8. EFFECT

This overlay keeps failures visible instead of shrinking the denominator, separates an
explicit not-located claim from failure or abstention, and makes presence failure-
penalized. It changes no prediction, roster, Gold decision, route, PDF byte, or historical
benchmark result.

9. EFFECTIVE CONDITION

This amendment has no effect unless the author fills the fields below, explicitly signs
the completed text, the protocol and SAP complete their required review and freeze, and
all resulting hashes are recorded before HOLDOUT scoring.

AUTHOR:

DATE:

CHANGES TO THIS DRAFT:

------------------------------------------------------------
END AMENDMENT DRAFT
------------------------------------------------------------
~~~

## Annex A — evidence crosswalk

| Object | Repository source | Evidence status |
|---|---|---|
| D1 localization scope | `docs/phase4/PHASE4_B1_B8_TRIAGE.md:18` | `SOURCED` |
| Frozen Level-C primary/secondaries | `configs/t0_4/metrics_spec.json:44-69` | `VERIFIED` |
| Frozen paired-output policy | `configs/t0_4/metrics_spec.json:120-122` | `VERIFIED` |
| Frozen DocumentGold limitations | `configs/t0_4/gold_schema.json:95-118` | `VERIFIED` |
| Current Q6 rule | `docs/governance/CURRENT_DECISIONS.md:30`; `docs/governance/AUTHOR_RATIFICATION_2026-09-26.md:312-334` | `SOURCED` |
| Current CC-4 endpoint set | `docs/governance/CURRENT_DECISIONS.md:46` | `SOURCED` |
| Existing not-located representation | `arpipe/models.py:176,194-195` | `VERIFIED` |

## Annex B — informative overlay

**PROPOSED.** This JSON-shaped summary is informative for a future scorer and does not
patch frozen configuration:

```json
{
  "primary": "document_weighted_mean_page_span_iou",
  "primary_gold_eligibility": "PRESENT",
  "no_output_iou": 0,
  "not_located_iou": 0,
  "invalid_iou": 0,
  "quarantine_iou": 0,
  "presence_display": "2x3_plus_failure_penalized_2x2",
  "issuer_weighted": "sensitivity",
  "ambiguous": "preoutput_optimistic_sensitivity"
}
```

## Annex C — preservation and open status

**VERIFIED.** P5-A.1 did not modify T0.4 material, `arpipe/`, dataset files, or the
original C1-D1 draft. **PROPOSED.** Author ratification remains due at method freeze;
`AUTHOR`, `DATE`, and `CHANGES TO THIS DRAFT` are intentionally blank.
