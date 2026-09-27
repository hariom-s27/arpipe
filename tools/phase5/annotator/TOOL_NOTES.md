# P5-T offline annotation tool: implementation notes

**Status:** `DRAFT_PENDING_PILOT`. Built 2026-09-27 from `origin/phase5-a1` (`e1803fc`).
Only synthetic data was used: no real PDF was opened and no real record was created.
The tool imports nothing from `arpipe/`.

| File | Role |
|---|---|
| `annotator_core.py` | All logic: isolation check, workspace id, assignment, PDF hash, 1-based→0-based conversion, record build, schema + tool-invariant validation, canonical JSON, sealing, supersession |
| `annotator_app.py` | tkinter form over the core. No network, no PDF rendering |
| `export_role.py` | Custodian export of one role's sealed records, with manifest |
| `make_bundle.py` | Builds `annotator_bundle.zip` (deterministic) and prints its manifest |
| `BUNDLE_README.md` | Shipped in the bundle as `README.md` |

## Fields and invariants implemented
- **SOURCED** (schema v0.1): every RAW-record field, enum dropdowns read from the schema,
  presence rules, flag/field equivalences, attestation constants, timestamp pattern.
- **SOURCED** (GOLD_SCHEMA v0.1 §3 tool checks): `0 <= start <= end < N` for all spans;
  gaps strictly inside the primary hull; viewer audit pages = stored + 1; sorted lists;
  `completed_at >= started_at`; viewer page count must equal the assigned count
  (GOLD_PROTOCOL v0.1 §2).

## Choices made here (PROPOSED, reversible, for review at method freeze)
1. **Supersession record.** The schema has no supersession field, so a separate sealed
   `…__SUPERSEDE__<sha8>.json` names the old and new raw hashes and the reason. The
   original record stays byte-identical.
2. **"Before A/B comparison" boundary.** `export_role.py` writes `EXPORTED.lock`; after
   it, the tool refuses new records and supersessions for that role. So export is
   treated as the start of comparison.
3. **Which record counts.** GOLD_PROTOCOL v0.1 §9 says agreement uses "the first
   eligible sealed raw A/B records". The tool keeps every record and every
   supersession note but does **not** decide which one is eligible. That rule belongs
   in the SAP/comparison step.
4. **`flag_pages` keys** must be flags that are present in `flags`.
5. **Title list placeholder.** While `TITLE_LIST_NOT_YET_FROZEN.txt` is in the bundle
   folder, the form opens but cannot seal records.
6. **Isolation check** refuses `.git` in the bundle root, the working directory or any
   parent, and `arpipe/`, `reports/`, `docs/identity/`, `labels*.csv` under the bundle.

## Still open (not decided by this tool)
- Viewer product, version and the "page labels off" setting (method-freeze pin).
- Frozen annotator-facing title list (added by the custodian later).
- Per-annotator `ASSIGNMENT.csv` (from the selector, after freeze and commit-reveal).
