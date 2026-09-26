# P-B current author decisions — snapshot v1

**Purpose.** This is the single canonical P-B governance snapshot of decisions observable at **2026-09-26 08:49:29 UTC** in thesis repository `D:/sem_iitk/sem9/thesis`, `main` HEAD `313f00b7e8c364c056a5a9d284ff843128419e21`. It was prepared on dedicated branch `pb-governance-20260926` from that SHA. It is a historical observation, not a new author decision. Later ratification requires a separately dated addendum/version; this snapshot must not be silently rewritten. Source IDs below resolve through [the byte-level manifest](P-B_SOURCE_MANIFEST.md); search boundaries are in [coverage](P-B_SOURCE_COVERAGE_REGISTER.md). No P-B file is evidence for its own conclusions.

**Authority.** Tier A is explicit author input or ratified amendment within its scope; Tier B is formal project governance and frozen records; Tier C is research/recommendation; Tier D is historical/superseded. Implementation and a Git commit prove bytes or behavior, not approval. The project says the author is the sole decision authority (R05:31–37). R05 records D1–D10 as directly supplied author choices, but labels its quotations “verbatim, condensed” (R05:12–16); the full direct message/date is absent. All ten earlier R01 `AUTHOR CHOICE` fields remain blank (R05:31–37). Thus D choices below are **ratified as transcribed operative clauses, with PG-1 provenance qualification**. The full unabridged author wording is not asserted. R09 contains a later structured D6 selection, expressly not new verbatim prose (R09:37–51). R12 contains an exact dated author ratification of a narrow T0.4 Track A amendment (R12:14–87,178–188), not of the thesis comparator or B choices.

Status vocabulary: `RATIFIED`, `PROPOSED_UNRATIFIED`, `PENDING_AUTHOR_DECISION`, `DEFERRED`, `SUPERSEDED`, `CONTRADICTED`, `NOT_APPLICABLE`, `INSUFFICIENT_EVIDENCE`. A ratified clause can be conditional; condition and unmet gate are separate fields. “Proposed defer” is not `DEFERRED`. `INFERRED` describes evidence, not ratification. No active unconditional pair of contradictory ratified values was found.

## FACT / DECISION / IMPLICATION boundary

| Category | Snapshot statement | Source |
|---|---|---|
| FACT | P-A reproduced A at 411 passed/17 skipped/3 xfailed and B at 103 passed/1 skipped with qualification, and verified 10 document hashes, at pinned execution identity `28a67b63d890d8407fa9738a71ae37ad63148b73`. | P-B brief's closed P-A state; R11:521–536 for identity boundary. P-A was not rerun. |
| DECISION | The author chose the reconstructed 2026-09-17 executed state for **R1 runnability**, and selected “Not yet — verify drift first” for C2 use. | R09:43–51,198–206. |
| IMPLICATION | P-A reproduction does not ratify R1 as the thesis As-Is or upgrade C2 to unconditional. | Scope of R09 and R11:521–536. |
| FACT | `metrics_spec.json` Level C registers document `page_span_iou`, but lacks a single-arm C1 failure/absence/ambiguity denominator; its both-outputs-only policy applies to **paired differences**. | R14:44–69,105–122; R05:165–210. |
| DECISION | The author has not confirmed that registered metric as the C1 primary endpoint and has not selected the missing C1 estimand rules. | R05:92–102,135–140; R06:423–428. |
| IMPLICATION | A new failure-inclusive or ambiguity-aware metric contract requires a formal Gold Method evaluation-protocol amendment; B6 cannot make that amendment. | R05:198–211; R06:428. |

## D1–D10: independently reconstructed author choices

The quotation column reproduces the **operative text actually present in R05**, including its ellipses. It must not be mistaken for the missing unabridged message. All have evidence class **Tier A transcription with PG-1 gap**, are `RATIFIED` only at that scope, and remain subject to scientific evaluation. R01's blank fields are historical facts, not overwritten.

| ID | AUTHOR_VERBATIM_TEXT as recorded in R05 | NORMALIZED_DECISION; scope and open remainder | Evidence |
|---|---|---|---|
| D1 | “ARPipe is developed and evaluated for reproducible START–END page-span localization of MD&A sections in a defined Indian annual-report corpus.” | Primary bounded localization claim; does not pick metric or prove performance. | R05:18,64–67 |
| D2 | “Bounded to the declared frozen evaluation population. No claim of national representativeness, universal MD&A extraction, or SOTA. A baseline-relative methods claim is retained only if the As-Is comparator is later established coherently.” | No broad/SOTA claim; C2 conditional on coherent comparator. | R05:19,66–67 |
| D3 | “A contiguous physical-page START–END span, with explicit rules for absent, ambiguous, embedded, annexure, and other non-standard cases.” | One-span concept chosen; detailed exception rules unresolved. | R05:20,124–133; R16 |
| D4 | “The available-byte frozen evaluation frame… does not represent all Indian issuers or continuous FY2010–2025 coverage. Gold-based eligibility and exclusion rules will be fixed in the Gold Method phase.” | Available-byte frame chosen; C1 reporting partition, eligibility, weighting still open. | R05:21,104–122; R02:21–42 |
| D5 | “The 14 missing historical PDFs are not required for the primary bounded claim.” | Those unavailable bytes are outside the bounded claim; does not answer other acquisition aims. | R05:22,104–119 |
| D6 | “The coherent historical operational ARPipe system immediately before the specific change being evaluated… If the baseline cannot be established coherently, no baseline-relative improvement claim is made.” | Relational baseline definition; R09 later selects historical executed state for R1 only. C2 gate unmet. | R05:23; R09:28–51,198–206 |
| D7 | “Proportionate, issuer-aware evaluation… Do not freeze an arbitrary universal sample size here. Final Gold sample allocation is determined and frozen in the Gold Method phase.” | Issuer-aware planning; no fixed n or weighting choice. | R05:24,92–102 |
| D8 | “No acquisition is currently necessary.” | No acquisition for current bounded primary claim; separate telemetry/acquisition work does not supersede this scope. | R05:25; M01 |
| D9 | “A bounded downstream robustness/sensitivity analysis is **retained if** the downstream climate measure is used as a substantive thesis result.” | Conditional retention; substantive antecedent and fixed recipe unresolved. | R05:26,152–161 |
| D10 | “The primary thesis evaluates the extraction/localization **outcome, not** a specific internal routing mechanism. Routing, legacy-font, and REMAP mechanisms are investigated only if a later failure-driven claim explicitly requires them.” | Outcome scope; B1–B5 are separate unresolved votes, with proposed deferral triggers. | R05:27; R06:438–445 |

**D6 scoped later selection.** R09:47–51 records structured author choices: “Adopt the reconstructed 2026-09-17 executed state” (Phase 4 committed production code union E0 provider half) and “Not yet — verify drift first” for C2. These are recorded selections, **not presented as verbatim author prose** by R09. R09's own v1 §12 originally said no T0.4 amendment was required; R12:132–148 later records a scoped erratum and a ratified Track A amendment. The historical R09 text remains preserved. R12 neither resolves Track B nor authorizes B1–B8.

## Q1b–Q10: author-input inquiries

These Q labels come from the P-B brief; they are **not** equated by number to Phase 3 Q labels (see [crosswalk](P-B_DECISION_ID_CROSSWALK.md)). Every row is `PENDING_AUTHOR_DECISION` or author-provided fact; no answer was inferred from code or a recommendation. An evidence citation names the underlying gap, not an author answer.

| ID | Question / historical or proposed state | Current author-ratified answer | Evidence; dependency and consequence |
|---|---|---|---|
| Q1b | Development after final freeze? A09 proposes treating evaluated-system identity/development as a root. | **None** | A09:108–117 (Tier C); R09 only chooses R1 runnability. Affects prospective HOLDOUT protection and evaluation identity. |
| Q2 | C1 headline partition: HOLDOUT, frame, or separately labelled scopes? R02 proposes HOLDOUT; D4 chooses the available-byte frame only. | **None** | R02:21–42; R05:21; A01:215–216; A03:18–29. Affects C1 estimand/B8. |
| Q3 | Availability of independent second annotator, adjudicator, or independent rules reviewer? | **None** | R06:20–39 blank; A05:169–185. Needed to choose feasible B6/B8 structure. |
| Q4 | Which B6 raw annotation, overlap, adjudication and rules-review structure? | **None** | R06:153–185 blank; A06:126–142. Blocks Gold protocol/construction, not Phase 5 design entry by itself. |
| Q5 | Which B8 HOLDOUT sequence, custodian, sealing, rerun and access rule? | **None** | R06:250–329; A08:53–85. Blocks HOLDOUT access/evaluation. |
| Q6 | C1 estimand/weighting, denominator, missed/invalid outputs and quarantine treatment? | **None** | R05:92–102,165–210; R14; A03:195–204. Metric change requires C1-D1 formal amendment. **Not** Phase 3 D6/Q6. |
| Q7 | Detailed absent, multiple-span, bilingual, embedded, annexure and non-contiguous Gold rules? | **None beyond D3's broad concept** | R05:20; A05:102–117,178–185. Blocks final Gold protocol. |
| Q8 | Is the reported interval a finite-census description or superpopulation uncertainty, and is the registered method retained? | **None** | R14:105–122; A03:167,195–204. A registered bootstrap is not an author choice of interpretation. |
| Q9 | How to disclose documented pre-T0 HOLDOUT exposure and distinguish prospective leakage? | **None** | R06:385–394 (older wording); A01:221,238–245; A08:78–85 (proposal). Exposure is not “unseen”; its influence remains unquantified. |
| Q10 | Is the D9 climate measure a substantive result, and what fixed recipe applies? | **None** | R05:26,152–161. Conditions C4/B7/PageGold work. |

## B1–B8: independent current state

R05:3–5 says no B decision is adopted. R08 has `selected_option: null` for each B. R06:3–15 and 433–451 keeps its options proposed and author fields blank. Accordingly **each B status is `PENDING_AUTHOR_DECISION`**. “DEFER_UNTIL_TRIGGER” and “DECIDE_NOW” are Phase 4 *triage proposals*, not actual ratified deferrals. T08 and A01–A09 are research/recommendations, not later author votes.

| ID | Historical/factual state | Proposed state and trigger | Ratified state / consequence |
|---|---|---|---|
| B1 | `broken_text` routes to OCR; no REMAP route or verified legacy prevalence (R08:37–72). | R05:409–477 proposes defer; reopen for a retained legacy claim, attributable Phase-9 false-native failure, or material evaluation threat. A02:164–170 corrects predicate-sensitive VAL interpretation. | **No B1 selection.** Cannot call one-class contract ratified or impossible. |
| B2 | No frozen precedence; sampling priority is not routing precedence (R08:76–98). | R05:479–490 proposes deferral; reopens if B1 creates overlapping signals/route or execution priority changes. | **No B2 selection.** `NOT_APPLICABLE` would presuppose unchosen B1. |
| B3 | Oracle is a page-level route population; 79 literal, 121 stratum, 106 derived variant are distinct (R07:34–149; A03:63–71). | R05:352–366 proposes defer until a routing/Oracle claim needs the roster. | **No roster selected.** C1 document population is separate; no Oracle construction. |
| B4 | Frozen per-cell minimum rank cannot implement independent 25% overlap; no selector (R08:131–174; R05:323–350). | Proposed defer until B3/B5 or explicit DocumentGold mechanism reuse. Random B6 overlap needs its own predeclared serialization and selector if chosen. | **No byte/encoding/newline/field-order/hash/seed/input contract ratified.** No selector implementation. |
| B5 | Image-only Oracle cannot establish hidden text-layer/font mapping (R08:178–199). | R05:368–386 proposes defer with Oracle/routing trigger. | **No Oracle evidence policy selected.** No Oracle construction. |
| B6 | Gold schema lacks raw overlap/adjudication structure (R16; R08:203–226). | R06:153–215 proposes hybrid B6-C, fallback A if sole annotator; structure to decide now, n later. T08 proposes a conflicting 40-document all-double plan, also unratified. | **No B6 selection.** C1 DocumentGold protocol cannot be finalized until author chooses structure and personnel are known. |
| B7 | No ratified reading-order reference. C1 page-span IoU itself is order-invariant (R05:152–161). | R05:388–407 proposes defer; reopens only if D9 substantive **and** the fixed measure is order-sensitive, or an independent order outcome is adopted. | **No B7 selection.** Trigger not established; it is not automatically moot. |
| B8 | Frozen config defaults to deny HOLDOUT before final freeze; pre-T0 exposure is documented separately from future leakage (R08:256–280; A08:15–31). | R06:294–321 proposes decide now; B8-B and fallback D are options, not choices. Later A08 offers further variants and wording. | **No B8 selection.** HOLDOUT access/evaluation remains unauthorized under the current protocol; historical exposure does not make it unseen. |

## Separately tracked objects

| Object | FACT | DECISION / current status | IMPLICATION |
|---|---|---|---|
| As-Is thesis identity | R09 selects the reconstructed 2026-09-17 executed state for R1 runnability. R11 pins runnable R1 at `28a67b63d890d8407fa9738a71ae37ad63148b73`, and explicitly says it is not a byte-identical historical tree or C2 baseline (R11:521–536). | **PENDING_AUTHOR_DECISION** for adoption of a thesis C2 comparator and evaluated change. The scoped R1 selection is RATIFIED; C2 use is expressly “Not yet — verify drift first” (R09:43–51). | R1 execution reproduction supplies evidence, not As-Is ratification. Drift in `models/ocr/store/triage` remains the named gate (R09:198–206). |
| C1 | D1 gives the bounded primary claim; D4 gives the available-byte frozen frame of 194 reports, 36 issuers, 92 FIT + 48 VAL + 54 HOLDOUT (R05:104–122). R02's HOLDOUT-only final wording is PROPOSED. | **RATIFIED** as a bounded claim/frame only. Reporting/evaluation population, eligible Gold sample, estimand, weights, failure/absence/ambiguity/quarantine rules and interval interpretation are `PENDING_AUTHOR_DECISION`. | The target claim, sampling frame, evaluation partition, Gold sample, Oracle roster and double-annotation draw are six distinct populations. None may be filled from another's count. |
| C2 | R05:64–67 retains paired improvement conditionally; R09:198–206 says historical drift gate unmet; R11:529–536 says pinned R1 is not the C2 baseline. | **RATIFIED, CONDITIONALLY RETAINED; GATE UNMET.** No unconditional improvement claim or thesis As-Is identity. | P-A reproduction cannot open the C2 gate. C2 can remain conditional while C1 governance is addressed. |
| CC-4 | R14:44–69 registers `page_span_iou` as Level C primary and exact/boundary/presence secondaries. R05:135–140 says author did not name a primary metric. | **PENDING_AUTHOR_DECISION**; `page_span_iou` is **INFERRED — NOT RATIFIED** as the thesis primary; secondary endpoint role is likewise unconfirmed. | Author confirmation and C1-D1 failure/denominator amendment are separate actions. Frozen config unchanged. |

### C1 population and contract detail

| Layer | Definition at snapshot | Exhaustive/sampled; fixed-before-outcome state | Status |
|---|---|---|---|
| Target claim scope | Defined Indian annual-report corpus, not all Indian issuers or all FY2010–2025 (D1/D2/D4). | Bounded target, no national sampling model. | RATIFIED scope. |
| Available corpus / sampling frame | 194 byte-available reports, 36 issuers; 14 missing historical PDFs excluded (R05:104–122). | Frozen availability frame, not a probability sample. | RATIFIED D4 frame and D5 exclusion; counts FACT. |
| Evaluation / headline population | R02 proposes eligible HOLDOUT reports; A01/A03 notes frame-wide interpretation remains possible. | HOLDOUT 54 is partition fact, **not** a ratified headline denominator. | PENDING Q2/K12. |
| Gold annotation sample | No finalized eligible/sample roster; T08's 40-document all-double proposal and R06's hybrid proposal differ. | Size, selection, eligibility fixed later in Gold Method. | PENDING B6/Q7. |
| Oracle roster | Page-level FIT+VAL routing construct with 79/121/106 candidate readings. | No option selected; not the C1 document sample. | PENDING B3, proposed defer. |
| Double-annotation population | Raw A/B overlap population and random/diagnostic draw unspecified. | Must be fixed before assignment if random; not inherited from Oracle B4. | PENDING B6/B4-if-triggered. |
| Estimand and weighting | Document-weighted versus equal-issuer, and any year/page weighting, unselected (R05:92–102). | Must be chosen before outcome observation; issuer-aware is not issuer-weighted. | PENDING Q6/CC-1. |
| Primary and secondary endpoints | `page_span_iou` and secondary metrics are registered config fields, not author-confirmed thesis roles (R14; R05:135–140). | Outcome metric roles must be fixed before final evaluation. | INFERRED / PENDING CC-4. |
| Failure handling | No Level C missed/invalid/absent/ambiguity denominator rule; paired differences require both outputs (R05:165–210; R14:121). | Existing paired metric is conditional on both outputs; it cannot be described as failure-inclusive. | PENDING Q6/Q7; formal C1-D1 amendment required for a changed contract. |

### Conditions, historical relations and conflicts

| Item | Condition / reopen trigger | Relationship |
|---|---|---|
| D9/C4 | Substantive climate result and fixed recipe | D9 is ratified **conditional**, antecedent open (R05:152–161). |
| C2/As-Is | Coherent historical comparator, evaluated change, and bounded 2026-09-17→20 provider drift | C2 remains conditional; R1 runnable pin does not satisfy it (R09; R11). |
| B1/B2/B3/B4/B5/B7 | Triggers recorded above are **proposed triage**, not adopted deferrals. | No B decision is current `DEFERRED`/`NOT_APPLICABLE` merely because Phase 4 recommends it. |
| B8 | C1 final population and forward HOLDOUT protection choice | Earlier exposure is documented; influence unknown; future access remains default-denied (R08; A08). |
| R09 §12 vs R12 | R12 explicitly records a later T0.4 Track A amendment/erratum; Track B deferred by exact ratified text (R12:65–87,132–148). | Scoped supersession of R09's amendment-needed assertion, **not** of its D6 author selection. |
| T08 40-all-double vs R06 hybrid; T08 106-Oracle vs R07 79/121/106 | Different unratified recommendations or corrected arithmetic. | No active ratified contradiction; preserve proposals and factual errata. |
| Historical HOLDOUT exposure | A08/A01 document exposure that R06 had called undetermined. | Factual refinement, not an author B8 supersession. Exposure ≠ unseen ≠ prospective leakage. |

## Open author-ratification fields

No fields below have been completed on the author's behalf. Exact questions and alternatives are in [the Author Decision Pack](P-B_AUTHOR_DECISION_PACK.md).

| Field | State |
|---|---|
| PG-1: confirm/transcribe the D1–D10 clauses into an author-controlled record while preserving R01 blanks | **PENDING AUTHOR RATIFICATION** |
| Q1b–Q10 substantive answers, including C1 partition/estimand, people, Gold and HOLDOUT governance | **PENDING AUTHOR RATIFICATION** |
| B1–B8 selections or explicit trigger-based deferrals | **PENDING AUTHOR RATIFICATION**, dependency-scoped |
| Thesis As-Is/C2 adoption, if C2 will be pursued | **PENDING AUTHOR RATIFICATION** after evidence gate |
| CC-4 endpoint and any secondary endpoint roles | **PENDING AUTHOR RATIFICATION** |

## Machine-readable ledger

The JSON array below is the machine-readable companion to the tables above. `null` means no value was established, never an implied author choice. Source IDs resolve to path, blob/commit and SHA-256 in the manifest. The text field for D items is copied from R05's **condensed** transcription, not from an inaccessible original message.

<!-- P-B_LEDGER_JSON_START -->
```json
[
  {
    "historical_state": "R01 Phase 3 author-choice field blank; R05 later transcribes supplied choice",
    "proposed_state": "R01 alternatives remain historical proposals",
    "current_ratified_state": "Bounded MD&A physical-page span localization claim",
    "author_verbatim_text": "ARPipe is developed and evaluated for reproducible START–END page-span localization of MD&A sections in a defined Indian annual-report corpus.",
    "normalized_decision": "Bounded MD&A physical-page span localization claim",
    "ratification_evidence": "R05:12–37 states these clauses were supplied directly by the sole author and binding; text is condensed; original full message/date unavailable",
    "condition": null,
    "dependency": [],
    "reopen_trigger": null,
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": false,
    "required_amendment": false,
    "downstream_consequence": "C1 claim",
    "notes": "Scientific adequacy remains separate from ratification",
    "id": "D1",
    "title": "Main thesis claim",
    "decision_class": "author thesis scope",
    "current_status": "RATIFIED",
    "source_file": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
    "source_location": "§0 table line 18",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
      "blob": "47eb60155eecc2830bd6f1158f07a127b247684c",
      "sha256": "65206be41b74bd4069ee4b2ab10fa8aa9f21da059d22f295681e8ba26936de91",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "A — transcribed author input with PG-1 provenance qualification",
    "scope": "defined Indian annual-report corpus"
  },
  {
    "historical_state": "R01 Phase 3 author-choice field blank; R05 later transcribes supplied choice",
    "proposed_state": "R01 alternatives remain historical proposals",
    "current_ratified_state": "Bound claims to declared population; C2 only with coherent comparator",
    "author_verbatim_text": "Bounded to the declared frozen evaluation population. No claim of national representativeness, universal MD&A extraction, or SOTA. A baseline-relative methods claim is retained only if the As-Is comparator is later established coherently.",
    "normalized_decision": "Bound claims to declared population; C2 only with coherent comparator",
    "ratification_evidence": "R05:12–37 states these clauses were supplied directly by the sole author and binding; text is condensed; original full message/date unavailable",
    "condition": "Baseline-relative claim only with coherent As-Is",
    "dependency": [
      "As-Is",
      "C2"
    ],
    "reopen_trigger": null,
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "C2 condition; broad claims excluded",
    "notes": "Scientific adequacy remains separate from ratification",
    "id": "D2",
    "title": "Claim breadth",
    "decision_class": "author thesis scope",
    "current_status": "RATIFIED",
    "source_file": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
    "source_location": "§0 table line 19",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
      "blob": "47eb60155eecc2830bd6f1158f07a127b247684c",
      "sha256": "65206be41b74bd4069ee4b2ab10fa8aa9f21da059d22f295681e8ba26936de91",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "A — transcribed author input with PG-1 provenance qualification",
    "scope": "frozen evaluation population"
  },
  {
    "historical_state": "R01 Phase 3 author-choice field blank; R05 later transcribes supplied choice",
    "proposed_state": "R01 alternatives remain historical proposals",
    "current_ratified_state": "One contiguous physical-page span concept; exception rules to be specified",
    "author_verbatim_text": "A contiguous physical-page START–END span, with explicit rules for absent, ambiguous, embedded, annexure, and other non-standard cases.",
    "normalized_decision": "One contiguous physical-page span concept; exception rules to be specified",
    "ratification_evidence": "R05:12–37 states these clauses were supplied directly by the sole author and binding; text is condensed; original full message/date unavailable",
    "condition": null,
    "dependency": [
      "Q7",
      "B6"
    ],
    "reopen_trigger": null,
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "Gold protocol needs detailed rules",
    "notes": "Scientific adequacy remains separate from ratification",
    "id": "D3",
    "title": "Gold MD&A concept",
    "decision_class": "author thesis scope",
    "current_status": "RATIFIED",
    "source_file": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
    "source_location": "§0 table line 20",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
      "blob": "47eb60155eecc2830bd6f1158f07a127b247684c",
      "sha256": "65206be41b74bd4069ee4b2ab10fa8aa9f21da059d22f295681e8ba26936de91",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "A — transcribed author input with PG-1 provenance qualification",
    "scope": "DocumentGold concept"
  },
  {
    "historical_state": "R01 Phase 3 author-choice field blank; R05 later transcribes supplied choice",
    "proposed_state": "R01 alternatives remain historical proposals",
    "current_ratified_state": "Available-byte frozen frame; eligibility deferred to Gold Method",
    "author_verbatim_text": "The available-byte frozen evaluation frame… does not represent all Indian issuers or continuous FY2010–2025 coverage. Gold-based eligibility and exclusion rules will be fixed in the Gold Method phase.",
    "normalized_decision": "Available-byte frozen frame; eligibility deferred to Gold Method",
    "ratification_evidence": "R05:12–37 states these clauses were supplied directly by the sole author and binding; text is condensed; original full message/date unavailable",
    "condition": null,
    "dependency": [
      "Q2",
      "C1"
    ],
    "reopen_trigger": null,
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "C1 partition and eligibility still open",
    "notes": "194-frame fact does not decide HOLDOUT reporting partition",
    "id": "D4",
    "title": "Population frame",
    "decision_class": "author thesis scope",
    "current_status": "RATIFIED",
    "source_file": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
    "source_location": "§0 table line 21",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
      "blob": "47eb60155eecc2830bd6f1158f07a127b247684c",
      "sha256": "65206be41b74bd4069ee4b2ab10fa8aa9f21da059d22f295681e8ba26936de91",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "A — transcribed author input with PG-1 provenance qualification",
    "scope": "available-byte frame, not C1 headline partition"
  },
  {
    "historical_state": "R01 Phase 3 author-choice field blank; R05 later transcribes supplied choice",
    "proposed_state": "R01 alternatives remain historical proposals",
    "current_ratified_state": "Exclude fourteen unavailable PDFs from primary bounded claim",
    "author_verbatim_text": "The 14 missing historical PDFs are not required for the primary bounded claim.",
    "normalized_decision": "Exclude fourteen unavailable PDFs from primary bounded claim",
    "ratification_evidence": "R05:12–37 states these clauses were supplied directly by the sole author and binding; text is condensed; original full message/date unavailable",
    "condition": null,
    "dependency": [],
    "reopen_trigger": null,
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": false,
    "required_amendment": false,
    "downstream_consequence": "No acquisition needed for those bytes for C1",
    "notes": "Scientific adequacy remains separate from ratification",
    "id": "D5",
    "title": "Missing historical PDFs",
    "decision_class": "author thesis scope",
    "current_status": "RATIFIED",
    "source_file": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
    "source_location": "§0 table line 22",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
      "blob": "47eb60155eecc2830bd6f1158f07a127b247684c",
      "sha256": "65206be41b74bd4069ee4b2ab10fa8aa9f21da059d22f295681e8ba26936de91",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "A — transcribed author input with PG-1 provenance qualification",
    "scope": "primary bounded claim only"
  },
  {
    "historical_state": "R01 Phase 3 author-choice field blank; R05 later transcribes supplied choice",
    "proposed_state": "R01 alternatives remain historical proposals",
    "current_ratified_state": "Baseline must be coherent historical system preceding evaluated change; otherwise no C2 improvement claim",
    "author_verbatim_text": "The coherent historical operational ARPipe system immediately before the specific change being evaluated… If the baseline cannot be established coherently, no baseline-relative improvement claim is made.",
    "normalized_decision": "Baseline must be coherent historical system preceding evaluated change; otherwise no C2 improvement claim",
    "ratification_evidence": "R05:12–37 states these clauses were supplied directly by the sole author and binding; text is condensed; original full message/date unavailable",
    "condition": "If coherent baseline cannot be established, no baseline-relative claim",
    "dependency": [
      "As-Is",
      "C2"
    ],
    "reopen_trigger": null,
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "R1-only later choice does not open C2",
    "notes": "R09 later records structured R1-only selection; no C2 adoption",
    "id": "D6",
    "title": "Relational As-Is baseline",
    "decision_class": "author thesis scope",
    "current_status": "RATIFIED",
    "source_file": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
    "source_location": "§0 table line 23",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
      "blob": "47eb60155eecc2830bd6f1158f07a127b247684c",
      "sha256": "65206be41b74bd4069ee4b2ab10fa8aa9f21da059d22f295681e8ba26936de91",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "A — transcribed author input with PG-1 provenance qualification",
    "scope": "C2 baseline definition"
  },
  {
    "historical_state": "R01 Phase 3 author-choice field blank; R05 later transcribes supplied choice",
    "proposed_state": "R01 alternatives remain historical proposals",
    "current_ratified_state": "Issuer-aware planning; freeze sample allocation in Gold Method",
    "author_verbatim_text": "Proportionate, issuer-aware evaluation… Do not freeze an arbitrary universal sample size here. Final Gold sample allocation is determined and frozen in the Gold Method phase.",
    "normalized_decision": "Issuer-aware planning; freeze sample allocation in Gold Method",
    "ratification_evidence": "R05:12–37 states these clauses were supplied directly by the sole author and binding; text is condensed; original full message/date unavailable",
    "condition": null,
    "dependency": [
      "Q6",
      "B6"
    ],
    "reopen_trigger": null,
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "No fixed n or issuer weighting chosen",
    "notes": "Issuer-aware does not equal issuer-weighted",
    "id": "D7",
    "title": "Evidence and sample planning",
    "decision_class": "author thesis scope",
    "current_status": "RATIFIED",
    "source_file": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
    "source_location": "§0 table line 24",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
      "blob": "47eb60155eecc2830bd6f1158f07a127b247684c",
      "sha256": "65206be41b74bd4069ee4b2ab10fa8aa9f21da059d22f295681e8ba26936de91",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "A — transcribed author input with PG-1 provenance qualification",
    "scope": "Gold planning"
  },
  {
    "historical_state": "R01 Phase 3 author-choice field blank; R05 later transcribes supplied choice",
    "proposed_state": "R01 alternatives remain historical proposals",
    "current_ratified_state": "No acquisition for current bounded primary claim",
    "author_verbatim_text": "No acquisition is currently necessary.",
    "normalized_decision": "No acquisition for current bounded primary claim",
    "ratification_evidence": "R05:12–37 states these clauses were supplied directly by the sole author and binding; text is condensed; original full message/date unavailable",
    "condition": null,
    "dependency": [],
    "reopen_trigger": null,
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": false,
    "required_amendment": false,
    "downstream_consequence": "Separate acquisition research may proceed without contradiction",
    "notes": "Scientific adequacy remains separate from ratification",
    "id": "D8",
    "title": "Acquisition necessity",
    "decision_class": "author thesis scope",
    "current_status": "RATIFIED",
    "source_file": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
    "source_location": "§0 table line 25",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
      "blob": "47eb60155eecc2830bd6f1158f07a127b247684c",
      "sha256": "65206be41b74bd4069ee4b2ab10fa8aa9f21da059d22f295681e8ba26936de91",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "A — transcribed author input with PG-1 provenance qualification",
    "scope": "current primary claim"
  },
  {
    "historical_state": "R01 Phase 3 author-choice field blank; R05 later transcribes supplied choice",
    "proposed_state": "R01 alternatives remain historical proposals",
    "current_ratified_state": "Retain bounded downstream analysis only if climate measure is substantive",
    "author_verbatim_text": "A bounded downstream robustness/sensitivity analysis is retained if the downstream climate measure is used as a substantive thesis result.",
    "normalized_decision": "Retain bounded downstream analysis only if climate measure is substantive",
    "ratification_evidence": "R05:12–37 states these clauses were supplied directly by the sole author and binding; text is condensed; original full message/date unavailable",
    "condition": "Only if climate measure is substantive",
    "dependency": [
      "Q10",
      "B7"
    ],
    "reopen_trigger": "Q10 substantive climate answer",
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "Antecedent and recipe open",
    "notes": "Scientific adequacy remains separate from ratification",
    "id": "D9",
    "title": "Downstream climate analysis",
    "decision_class": "author thesis scope",
    "current_status": "RATIFIED",
    "source_file": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
    "source_location": "§0 table line 26",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
      "blob": "47eb60155eecc2830bd6f1158f07a127b247684c",
      "sha256": "65206be41b74bd4069ee4b2ab10fa8aa9f21da059d22f295681e8ba26936de91",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "A — transcribed author input with PG-1 provenance qualification",
    "scope": "C4/downstream analysis"
  },
  {
    "historical_state": "R01 Phase 3 author-choice field blank; R05 later transcribes supplied choice",
    "proposed_state": "R01 alternatives remain historical proposals",
    "current_ratified_state": "Primary thesis is outcome-focused; mechanism work requires later failure-driven claim",
    "author_verbatim_text": "The primary thesis evaluates the extraction/localization outcome, not a specific internal routing mechanism. Routing, legacy-font, and REMAP mechanisms are investigated only if a later failure-driven claim explicitly requires them.",
    "normalized_decision": "Primary thesis is outcome-focused; mechanism work requires later failure-driven claim",
    "ratification_evidence": "R05:12–37 states these clauses were supplied directly by the sole author and binding; text is condensed; original full message/date unavailable",
    "condition": "Mechanism research only after explicit failure-driven claim",
    "dependency": [
      "B1",
      "B2",
      "B3",
      "B4",
      "B5"
    ],
    "reopen_trigger": "later failure-driven mechanism claim",
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "B1-B5 triggers must not be presumed ratified",
    "notes": "Scientific adequacy remains separate from ratification",
    "id": "D10",
    "title": "Outcome versus mechanism",
    "decision_class": "author thesis scope",
    "current_status": "RATIFIED",
    "source_file": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
    "source_location": "§0 table line 27",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
      "blob": "47eb60155eecc2830bd6f1158f07a127b247684c",
      "sha256": "65206be41b74bd4069ee4b2ab10fa8aa9f21da059d22f295681e8ba26936de91",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "A — transcribed author input with PG-1 provenance qualification",
    "scope": "primary thesis versus mechanism research"
  },
  {
    "historical_state": "A09:108–117 proposes this as a root; R09 is R1-only",
    "proposed_state": "A09:108–117 proposes this as a root; R09 is R1-only",
    "current_ratified_state": null,
    "author_verbatim_text": null,
    "normalized_decision": null,
    "ratification_evidence": null,
    "condition": null,
    "dependency": [
      "As-Is",
      "B8"
    ],
    "reopen_trigger": null,
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "Choose evaluated-system freeze and whether development continues afterwards",
    "notes": "P-B inquiry number is not the same as Phase 3 Q number; see crosswalk",
    "id": "Q1b",
    "title": "Development after final freeze",
    "decision_class": "P-B author-input inquiry",
    "current_status": "PENDING_AUTHOR_DECISION",
    "source_file": "sep_week2/arpipe_doc_24sep/A09_CROSS_DEPENDENCY_SYNTHESIS.md",
    "source_location": "lines 108–117",
    "source_version_date": "thesis snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "sep_week2/arpipe_doc_24sep/A09_CROSS_DEPENDENCY_SYNTHESIS.md",
      "blob": "—",
      "sha256": "89e30599efca6bc8b19bb854cc1498f592ddc21648f54000e6ed27bb769cd725",
      "ref": "thesis U@main"
    },
    "evidence_class": "B/F — formal gap or contract fact; no author answer",
    "scope": "final evaluated system"
  },
  {
    "historical_state": "R02:21–42 proposes HOLDOUT; D4 chooses frame, not partition",
    "proposed_state": "R02:21–42 proposes HOLDOUT; D4 chooses frame, not partition",
    "current_ratified_state": null,
    "author_verbatim_text": null,
    "normalized_decision": null,
    "ratification_evidence": null,
    "condition": null,
    "dependency": [
      "D4",
      "C1",
      "B8"
    ],
    "reopen_trigger": null,
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "Choose headline evaluation partition",
    "notes": "P-B inquiry number is not the same as Phase 3 Q number; see crosswalk",
    "id": "Q2",
    "title": "C1 reporting partition",
    "decision_class": "P-B author-input inquiry",
    "current_status": "PENDING_AUTHOR_DECISION",
    "source_file": "docs/phase3/PHASE3_CLAIM_EVIDENCE_MATRIX.md",
    "source_location": "lines 21–42",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase3/PHASE3_CLAIM_EVIDENCE_MATRIX.md",
      "blob": "57f733a8cecd634db582c04bb5d43db784beab2e",
      "sha256": "5a112204d28a7b715cbc1f7be6264f727a277c7465c69e0acc0cd84593b5a080",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "B/F — formal gap or contract fact; no author answer",
    "scope": "C1 evaluation"
  },
  {
    "historical_state": "R06:20–39 has annotator availability blank",
    "proposed_state": "R06:20–39 has annotator availability blank",
    "current_ratified_state": null,
    "author_verbatim_text": null,
    "normalized_decision": null,
    "ratification_evidence": null,
    "condition": null,
    "dependency": [
      "B6",
      "B8"
    ],
    "reopen_trigger": null,
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "Supply availability of second annotator/adjudicator/rules reviewer",
    "notes": "P-B inquiry number is not the same as Phase 3 Q number; see crosswalk",
    "id": "Q3",
    "title": "Independent personnel availability",
    "decision_class": "P-B author-input inquiry",
    "current_status": "PENDING_AUTHOR_DECISION",
    "source_file": "docs/phase4/PHASE4_DECISION_SHEET.md",
    "source_location": "lines 20–39",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_DECISION_SHEET.md",
      "blob": "ec9841bf53f3cb3c79874a325bc37ceaace0276d",
      "sha256": "91bbe86eb9626233a057c49d47e20627078a46240eecf6460f82621e69dd75f3",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "B/F — formal gap or contract fact; no author answer",
    "scope": "Gold/HOLDOUT governance"
  },
  {
    "historical_state": "R06:153–185 proposes hybrid with fallback; choice blank",
    "proposed_state": "R06:153–185 proposes hybrid with fallback; choice blank",
    "current_ratified_state": null,
    "author_verbatim_text": null,
    "normalized_decision": null,
    "ratification_evidence": null,
    "condition": null,
    "dependency": [
      "Q3",
      "B6"
    ],
    "reopen_trigger": null,
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "Choose raw overlap, adjudication and review structure",
    "notes": "P-B inquiry number is not the same as Phase 3 Q number; see crosswalk",
    "id": "Q4",
    "title": "B6 annotation structure",
    "decision_class": "P-B author-input inquiry",
    "current_status": "PENDING_AUTHOR_DECISION",
    "source_file": "docs/phase4/PHASE4_DECISION_SHEET.md",
    "source_location": "lines 153–185",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_DECISION_SHEET.md",
      "blob": "ec9841bf53f3cb3c79874a325bc37ceaace0276d",
      "sha256": "91bbe86eb9626233a057c49d47e20627078a46240eecf6460f82621e69dd75f3",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "B/F — formal gap or contract fact; no author answer",
    "scope": "Gold/HOLDOUT governance"
  },
  {
    "historical_state": "R06:250–329 offers variants; no selection",
    "proposed_state": "R06:250–329 offers variants; no selection",
    "current_ratified_state": null,
    "author_verbatim_text": null,
    "normalized_decision": null,
    "ratification_evidence": null,
    "condition": null,
    "dependency": [
      "Q2",
      "Q3",
      "B8"
    ],
    "reopen_trigger": null,
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "Choose prospective HOLDOUT access/sealing/custody/rerun rule",
    "notes": "P-B inquiry number is not the same as Phase 3 Q number; see crosswalk",
    "id": "Q5",
    "title": "B8 HOLDOUT sequence",
    "decision_class": "P-B author-input inquiry",
    "current_status": "PENDING_AUTHOR_DECISION",
    "source_file": "docs/phase4/PHASE4_DECISION_SHEET.md",
    "source_location": "lines 250–329",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_DECISION_SHEET.md",
      "blob": "ec9841bf53f3cb3c79874a325bc37ceaace0276d",
      "sha256": "91bbe86eb9626233a057c49d47e20627078a46240eecf6460f82621e69dd75f3",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "B/F — formal gap or contract fact; no author answer",
    "scope": "Gold/HOLDOUT governance"
  },
  {
    "historical_state": "R05:92–102,165–210 identifies gaps; existing paired rule both-output-only",
    "proposed_state": "R05:92–102,165–210 identifies gaps; existing paired rule both-output-only",
    "current_ratified_state": null,
    "author_verbatim_text": null,
    "normalized_decision": null,
    "ratification_evidence": null,
    "condition": null,
    "dependency": [
      "C1",
      "CC-4"
    ],
    "reopen_trigger": null,
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": true,
    "downstream_consequence": "Choose weighting, eligibility, failure/abstention/quarantine accounting and authorize C1-D1 amendment",
    "notes": "P-B inquiry number is not the same as Phase 3 Q number; see crosswalk",
    "id": "Q6",
    "title": "C1 estimand, denominator and quarantine",
    "decision_class": "P-B author-input inquiry",
    "current_status": "PENDING_AUTHOR_DECISION",
    "source_file": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
    "source_location": "lines 92–102, 165–210",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
      "blob": "47eb60155eecc2830bd6f1158f07a127b247684c",
      "sha256": "65206be41b74bd4069ee4b2ab10fa8aa9f21da059d22f295681e8ba26936de91",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "B/F — formal gap or contract fact; no author answer",
    "scope": "C1 evaluation"
  },
  {
    "historical_state": "D3 gives one-span principle; A05 proposes exception handling",
    "proposed_state": "D3 gives one-span principle; A05 proposes exception handling",
    "current_ratified_state": null,
    "author_verbatim_text": null,
    "normalized_decision": null,
    "ratification_evidence": null,
    "condition": null,
    "dependency": [
      "D3",
      "B6"
    ],
    "reopen_trigger": null,
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "Choose absent/multiple/bilingual/embedded/annexure/noncontiguous rules",
    "notes": "P-B inquiry number is not the same as Phase 3 Q number; see crosswalk",
    "id": "Q7",
    "title": "Detailed Gold exception rules",
    "decision_class": "P-B author-input inquiry",
    "current_status": "PENDING_AUTHOR_DECISION",
    "source_file": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
    "source_location": "line 20; A05:102–117",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
      "blob": "47eb60155eecc2830bd6f1158f07a127b247684c",
      "sha256": "65206be41b74bd4069ee4b2ab10fa8aa9f21da059d22f295681e8ba26936de91",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "B/F — formal gap or contract fact; no author answer",
    "scope": "Gold/HOLDOUT governance"
  },
  {
    "historical_state": "R14 registers paired cluster bootstrap; interpretation unresolved in A03",
    "proposed_state": "R14 registers paired cluster bootstrap; interpretation unresolved in A03",
    "current_ratified_state": null,
    "author_verbatim_text": null,
    "normalized_decision": null,
    "ratification_evidence": null,
    "condition": null,
    "dependency": [
      "C1",
      "Q6"
    ],
    "reopen_trigger": null,
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "Choose census versus superpopulation reporting and interval contract",
    "notes": "P-B inquiry number is not the same as Phase 3 Q number; see crosswalk",
    "id": "Q8",
    "title": "Interval interpretation",
    "decision_class": "P-B author-input inquiry",
    "current_status": "PENDING_AUTHOR_DECISION",
    "source_file": "configs/t0_4/metrics_spec.json",
    "source_location": "lines 105–122; A03:195–204",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "configs/t0_4/metrics_spec.json",
      "blob": "e9e7b270afb3134d47ee2d707d732f9eb5c036c7",
      "sha256": "d7590bebe271163f2ad341cace35f4749754cf22da3018cef32b12ad09c66336",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "B/F — formal gap or contract fact; no author answer",
    "scope": "C1 evaluation"
  },
  {
    "historical_state": "R06 older UNKNOWN wording; A01/A08 document exposure and propose revision",
    "proposed_state": "R06 older UNKNOWN wording; A01/A08 document exposure and propose revision",
    "current_ratified_state": null,
    "author_verbatim_text": null,
    "normalized_decision": null,
    "ratification_evidence": null,
    "condition": null,
    "dependency": [
      "B8"
    ],
    "reopen_trigger": null,
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "Choose truthful disclosure of historical exposure and prospective leakage limits",
    "notes": "P-B inquiry number is not the same as Phase 3 Q number; see crosswalk",
    "id": "Q9",
    "title": "HOLDOUT exposure wording",
    "decision_class": "P-B author-input inquiry",
    "current_status": "PENDING_AUTHOR_DECISION",
    "source_file": "sep_week2/arpipe_doc_24sep/A08_B8_HOLDOUT_GOVERNANCE.md",
    "source_location": "lines 15–31, 78–85",
    "source_version_date": "thesis snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "sep_week2/arpipe_doc_24sep/A08_B8_HOLDOUT_GOVERNANCE.md",
      "blob": "—",
      "sha256": "069d3b57cd5fe78cf4cea1df4a5e3fc1cb3777fe35ff0f0b54e4c7d06a4486c5",
      "ref": "thesis U@main"
    },
    "evidence_class": "C — research proposal",
    "scope": "Gold/HOLDOUT governance"
  },
  {
    "historical_state": "R05:152–161 says antecedent undecided, recipe absent",
    "proposed_state": "R05:152–161 says antecedent undecided, recipe absent",
    "current_ratified_state": null,
    "author_verbatim_text": null,
    "normalized_decision": null,
    "ratification_evidence": null,
    "condition": null,
    "dependency": [
      "D9",
      "B7"
    ],
    "reopen_trigger": null,
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "Choose whether substantive climate result exists and fix recipe if yes",
    "notes": "P-B inquiry number is not the same as Phase 3 Q number; see crosswalk",
    "id": "Q10",
    "title": "D9 climate antecedent and recipe",
    "decision_class": "P-B author-input inquiry",
    "current_status": "PENDING_AUTHOR_DECISION",
    "source_file": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
    "source_location": "lines 152–161",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
      "blob": "47eb60155eecc2830bd6f1158f07a127b247684c",
      "sha256": "65206be41b74bd4069ee4b2ab10fa8aa9f21da059d22f295681e8ba26936de91",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "B/F — formal gap or contract fact; no author answer",
    "scope": "C4 downstream"
  },
  {
    "historical_state": "R08 selected_option:null; broken_text→OCR; no verified legacy prevalence",
    "proposed_state": "proposed DEFER_UNTIL_TRIGGER",
    "current_ratified_state": null,
    "author_verbatim_text": null,
    "normalized_decision": null,
    "ratification_evidence": null,
    "condition": null,
    "dependency": [
      "D10"
    ],
    "reopen_trigger": "retained legacy claim, attributable false-native failure, or material evaluation threat",
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "No one-class or REMAP choice adopted",
    "notes": "R05:3–5 says no B item adopted. Proposed deferral is not DEFERRED status. R08 selected_option null; T08/Axx are research.",
    "id": "B1",
    "title": "Legacy-font method/trigger",
    "decision_class": "B1–B8 governance choice",
    "current_status": "PENDING_AUTHOR_DECISION",
    "source_file": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
    "source_location": "lines 409–477",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
      "blob": "47eb60155eecc2830bd6f1158f07a127b247684c",
      "sha256": "65206be41b74bd4069ee4b2ab10fa8aa9f21da059d22f295681e8ba26936de91",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "B — formal decision preparation; no adoption",
    "scope": "Gold/HOLDOUT governance"
  },
  {
    "historical_state": "R08 selected_option:null; no frozen precedence; sampling priority differs",
    "proposed_state": "proposed DEFER_UNTIL_TRIGGER",
    "current_ratified_state": null,
    "author_verbatim_text": null,
    "normalized_decision": null,
    "ratification_evidence": null,
    "condition": null,
    "dependency": [
      "B1"
    ],
    "reopen_trigger": "B1 creates overlapping operational signals or priority changes",
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "No N/A without B1 vote",
    "notes": "R05:3–5 says no B item adopted. Proposed deferral is not DEFERRED status. R08 selected_option null; T08/Axx are research.",
    "id": "B2",
    "title": "Legacy/broken-text precedence",
    "decision_class": "B1–B8 governance choice",
    "current_status": "PENDING_AUTHOR_DECISION",
    "source_file": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
    "source_location": "lines 479–490",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
      "blob": "47eb60155eecc2830bd6f1158f07a127b247684c",
      "sha256": "65206be41b74bd4069ee4b2ab10fa8aa9f21da059d22f295681e8ba26936de91",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "B — formal decision preparation; no adoption",
    "scope": "Gold/HOLDOUT governance"
  },
  {
    "historical_state": "R08 selected_option:null; 79 literal / 121 stratum / 106 derived page-unit candidates",
    "proposed_state": "proposed DEFER_UNTIL_TRIGGER",
    "current_ratified_state": null,
    "author_verbatim_text": null,
    "normalized_decision": null,
    "ratification_evidence": null,
    "condition": null,
    "dependency": [
      "D10"
    ],
    "reopen_trigger": "retained routing/Oracle claim needs roster",
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "No Oracle roster constructed",
    "notes": "R05:3–5 says no B item adopted. Proposed deferral is not DEFERRED status. R08 selected_option null; T08/Axx are research.",
    "id": "B3",
    "title": "Oracle route population",
    "decision_class": "B1–B8 governance choice",
    "current_status": "PENDING_AUTHOR_DECISION",
    "source_file": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
    "source_location": "lines 352–366",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
      "blob": "47eb60155eecc2830bd6f1158f07a127b247684c",
      "sha256": "65206be41b74bd4069ee4b2ab10fa8aa9f21da059d22f295681e8ba26936de91",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "B — formal decision preparation; no adoption",
    "scope": "Oracle/routing; page level"
  },
  {
    "historical_state": "R08 selected_option:null; per-cell rank biased; no canonical byte contract",
    "proposed_state": "proposed DEFER_UNTIL_TRIGGER",
    "current_ratified_state": null,
    "author_verbatim_text": null,
    "normalized_decision": null,
    "ratification_evidence": null,
    "condition": null,
    "dependency": [
      "B3",
      "B5",
      "B6"
    ],
    "reopen_trigger": "Oracle reopening or explicit DocumentGold mechanism reuse",
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "No selector implementation",
    "notes": "R05:3–5 says no B item adopted. Proposed deferral is not DEFERRED status. R08 selected_option null; T08/Axx are research.",
    "id": "B4",
    "title": "Canonical serialization and selector",
    "decision_class": "B1–B8 governance choice",
    "current_status": "PENDING_AUTHOR_DECISION",
    "source_file": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
    "source_location": "lines 323–350",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
      "blob": "47eb60155eecc2830bd6f1158f07a127b247684c",
      "sha256": "65206be41b74bd4069ee4b2ab10fa8aa9f21da059d22f295681e8ba26936de91",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "B — formal decision preparation; no adoption",
    "scope": "Oracle/routing; page level"
  },
  {
    "historical_state": "R08 selected_option:null; image-only cannot reveal hidden text mapping",
    "proposed_state": "proposed DEFER_UNTIL_TRIGGER",
    "current_ratified_state": null,
    "author_verbatim_text": null,
    "normalized_decision": null,
    "ratification_evidence": null,
    "condition": null,
    "dependency": [
      "B3"
    ],
    "reopen_trigger": "Oracle route reopened",
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "No Oracle methodology adopted",
    "notes": "R05:3–5 says no B item adopted. Proposed deferral is not DEFERRED status. R08 selected_option null; T08/Axx are research.",
    "id": "B5",
    "title": "Oracle evidence policy",
    "decision_class": "B1–B8 governance choice",
    "current_status": "PENDING_AUTHOR_DECISION",
    "source_file": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
    "source_location": "lines 368–386",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
      "blob": "47eb60155eecc2830bd6f1158f07a127b247684c",
      "sha256": "65206be41b74bd4069ee4b2ab10fa8aa9f21da059d22f295681e8ba26936de91",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "B — formal decision preparation; no adoption",
    "scope": "Oracle/routing; page level"
  },
  {
    "historical_state": "R08 selected_option:null; schema has no raw overlap/adjudication design",
    "proposed_state": "proposed DECIDE_NOW; hybrid C versus sole-annotator A fallback",
    "current_ratified_state": null,
    "author_verbatim_text": null,
    "normalized_decision": null,
    "ratification_evidence": null,
    "condition": null,
    "dependency": [
      "D3",
      "Q3",
      "Q4",
      "Q7"
    ],
    "reopen_trigger": "C1 DocumentGold protocol design",
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "No Gold construction",
    "notes": "R05:3–5 says no B item adopted. Proposed deferral is not DEFERRED status. R08 selected_option null; T08/Axx are research.",
    "id": "B6",
    "title": "DocumentGold annotation design",
    "decision_class": "B1–B8 governance choice",
    "current_status": "PENDING_AUTHOR_DECISION",
    "source_file": "docs/phase4/PHASE4_DECISION_SHEET.md",
    "source_location": "lines 153–215",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_DECISION_SHEET.md",
      "blob": "ec9841bf53f3cb3c79874a325bc37ceaace0276d",
      "sha256": "91bbe86eb9626233a057c49d47e20627078a46240eecf6460f82621e69dd75f3",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "B — formal decision preparation; no adoption",
    "scope": "Gold/HOLDOUT governance"
  },
  {
    "historical_state": "R08 selected_option:null; no adopted order reference; C1 page IoU order-invariant",
    "proposed_state": "proposed DEFER_UNTIL_TRIGGER",
    "current_ratified_state": null,
    "author_verbatim_text": null,
    "normalized_decision": null,
    "ratification_evidence": null,
    "condition": null,
    "dependency": [
      "D9",
      "Q10"
    ],
    "reopen_trigger": "D9 substantive plus sequence-sensitive fixed recipe, or order claim",
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "Not moot without antecedent decision",
    "notes": "R05:3–5 says no B item adopted. Proposed deferral is not DEFERRED status. R08 selected_option null; T08/Axx are research.",
    "id": "B7",
    "title": "Reading order reference",
    "decision_class": "B1–B8 governance choice",
    "current_status": "PENDING_AUTHOR_DECISION",
    "source_file": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
    "source_location": "lines 388–407",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
      "blob": "47eb60155eecc2830bd6f1158f07a127b247684c",
      "sha256": "65206be41b74bd4069ee4b2ab10fa8aa9f21da059d22f295681e8ba26936de91",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "B — formal decision preparation; no adoption",
    "scope": "reading-order claim conditional on C4"
  },
  {
    "historical_state": "R08 selected_option:null; default-deny config; pre-T0 exposure documented",
    "proposed_state": "proposed DECIDE_NOW; variants open",
    "current_ratified_state": null,
    "author_verbatim_text": null,
    "normalized_decision": null,
    "ratification_evidence": null,
    "condition": null,
    "dependency": [
      "D4",
      "Q2",
      "Q5",
      "Q9"
    ],
    "reopen_trigger": "C1 population and forward access trigger",
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "HOLDOUT access/evaluation unauthorized",
    "notes": "R05:3–5 says no B item adopted. Proposed deferral is not DEFERRED status. R08 selected_option null; T08/Axx are research.",
    "id": "B8",
    "title": "HOLDOUT governance",
    "decision_class": "B1–B8 governance choice",
    "current_status": "PENDING_AUTHOR_DECISION",
    "source_file": "docs/phase4/PHASE4_DECISION_SHEET.md",
    "source_location": "lines 294–321",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_DECISION_SHEET.md",
      "blob": "ec9841bf53f3cb3c79874a325bc37ceaace0276d",
      "sha256": "91bbe86eb9626233a057c49d47e20627078a46240eecf6460f82621e69dd75f3",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "B — formal decision preparation; no adoption",
    "scope": "Gold/HOLDOUT governance"
  },
  {
    "historical_state": "R09 author selected reconstructed 2026-09-17 executed state for R1 runnability",
    "proposed_state": "R1 pin at 28a67b6 exists as runnable reconstruction; no thesis comparator adoption",
    "current_ratified_state": "R1 runnability identity only; thesis C2 comparator not adopted",
    "author_verbatim_text": "The coherent historical operational ARPipe system immediately before the specific change being evaluated… If the baseline cannot be established coherently, no baseline-relative improvement claim is made.",
    "normalized_decision": "C2 comparator must be coherent historical pre-change system; R1 is only a runnable reconstruction",
    "ratification_evidence": "R09:43–51 structured author selection explicitly says C2 'Not yet — verify drift first'",
    "condition": "C2 use awaits bounded 2026-09-17→20 provider drift and evaluated-change definition",
    "dependency": [
      "D6",
      "C2"
    ],
    "reopen_trigger": "Historical drift evidence and explicit author C2 comparator choice",
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "No baseline-relative C2 evaluation claim",
    "notes": "P-A reproduction is execution evidence, not comparator ratification",
    "id": "As-Is",
    "title": "Thesis As-Is identity",
    "decision_class": "separate thesis baseline object",
    "current_status": "PENDING_AUTHOR_DECISION",
    "source_file": "docs/decisions/D6_Q6_AS_IS_IDENTITY_DECISION_v1.md",
    "source_location": "lines 21–51, 198–206; R11:521–536",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/decisions/D6_Q6_AS_IS_IDENTITY_DECISION_v1.md",
      "blob": "08b357f57864b374d5bcb4e76c38353b7458c89c",
      "sha256": "286f5bb585d31fb8d59ce5cc58d9791500ac114183f16111935b9122ad47edc2",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "A scoped selection plus B identity fact",
    "scope": "R1 runnability versus thesis C2 comparator"
  },
  {
    "historical_state": "R02 candidate HOLDOUT C1 and failure-inclusive arithmetic were PROPOSED",
    "proposed_state": "R02 HOLDOUT-only wording; R06 Gold/metric proposals",
    "current_ratified_state": "D1 bounded localization claim and D4 available-byte frame only",
    "author_verbatim_text": "ARPipe is developed and evaluated for reproducible START–END page-span localization of MD&A sections in a defined Indian annual-report corpus.",
    "normalized_decision": "Bounded C1 claim/frame adopted; reporting partition, estimand and metric treatment open",
    "ratification_evidence": "R05:12–37 directly supplied author D1/D4 clauses, condensed; PG-1",
    "condition": "No final C1 result until Gold/metric protocol specified",
    "dependency": [
      "D1",
      "D3",
      "D4",
      "Q2",
      "Q6",
      "Q7",
      "Q8",
      "B6",
      "CC-4"
    ],
    "reopen_trigger": null,
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": true,
    "downstream_consequence": "Phase 5 may design methodology after governance prerequisites; Gold/final evaluation not ready",
    "notes": "Six population layers distinct; paired both-output rule is not a single-arm C1 denominator",
    "id": "C1",
    "title": "Primary bounded localization claim and evaluation contract",
    "decision_class": "separate primary claim",
    "current_status": "RATIFIED",
    "source_file": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
    "source_location": "lines 18,21,64–67,92–140,165–210",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
      "blob": "47eb60155eecc2830bd6f1158f07a127b247684c",
      "sha256": "65206be41b74bd4069ee4b2ab10fa8aa9f21da059d22f295681e8ba26936de91",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "A transcribed scope; B contract gaps",
    "scope": "194 available-byte reports as frame; C1 reporting partition unchosen"
  },
  {
    "historical_state": "R02 proposed baseline-relative comparison",
    "proposed_state": "Retained only if coherent As-Is comparator",
    "current_ratified_state": "Conditionally retained; gate unmet",
    "author_verbatim_text": "A baseline-relative methods claim is retained only if the As-Is comparator is later established coherently.",
    "normalized_decision": "No C2 improvement claim until coherent historical comparator and drift evidence",
    "ratification_evidence": "R05 direct author D2/D6 transcription; R09 structured 'Not yet — verify drift first'",
    "condition": "coherent As-Is, evaluated change, bounded provider drift; currently unmet",
    "dependency": [
      "D2",
      "D6",
      "As-Is"
    ],
    "reopen_trigger": "drift evidence and explicit comparator selection",
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "No unconditional C2 or baseline-relative result",
    "notes": "R1 pin/P-A execution do not open gate",
    "id": "C2",
    "title": "Conditional paired improvement claim",
    "decision_class": "separate comparative claim",
    "current_status": "RATIFIED",
    "source_file": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
    "source_location": "lines 19,23,64–67; R09:43–51,198–206",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
      "blob": "47eb60155eecc2830bd6f1158f07a127b247684c",
      "sha256": "65206be41b74bd4069ee4b2ab10fa8aa9f21da059d22f295681e8ba26936de91",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "A conditional author choice with B identity evidence",
    "scope": "paired baseline-relative methods claim"
  },
  {
    "historical_state": "R14 config registers page_span_iou primary and secondary metrics",
    "proposed_state": "R05 infers page_span_iou as presumptive C1 primary",
    "current_ratified_state": null,
    "author_verbatim_text": null,
    "normalized_decision": null,
    "ratification_evidence": null,
    "condition": null,
    "dependency": [
      "C1",
      "Q6"
    ],
    "reopen_trigger": null,
    "superseded_decision": null,
    "conflict": false,
    "open_author_choice": true,
    "required_amendment": false,
    "downstream_consequence": "Primary endpoint role cannot be stated as author-ratified",
    "notes": "Confirmation separate from C1-D1 metric-contract amendment",
    "id": "CC-4",
    "title": "C1 primary extraction endpoint",
    "decision_class": "separate endpoint confirmation",
    "current_status": "PENDING_AUTHOR_DECISION",
    "source_file": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
    "source_location": "lines 135–140; R06:426; R14:44–69",
    "source_version_date": "ARPipe r1-final snapshot 2026-09-26; see manifest",
    "source_hash_commit": {
      "path": "docs/phase4/PHASE4_B1_B8_TRIAGE.md",
      "blob": "47eb60155eecc2830bd6f1158f07a127b247684c",
      "sha256": "65206be41b74bd4069ee4b2ab10fa8aa9f21da059d22f295681e8ba26936de91",
      "ref": "ARPipe R@53dcab4"
    },
    "evidence_class": "B — explicit INFERRED endpoint plus F config fact",
    "scope": "C1 document-level primary/secondary metric roles"
  }
]
```
<!-- P-B_LEDGER_JSON_END -->
