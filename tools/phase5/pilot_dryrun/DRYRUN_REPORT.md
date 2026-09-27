# P5-C synthetic FIT dry run

**SYNTHETIC — not a result.** Four opaque byte files exercise tool interfaces only.

## Steps

- synthetic_inputs: PASS
- bundle: PASS
- workspaces: PASS
- ANNOTATOR_A_records: PASS
- ANNOTATOR_A_export_readback: PASS
- ANNOTATOR_B_records: PASS
- ANNOTATOR_B_export_readback: PASS
- raw_ab_agreement: PASS
- report: PASS

## Record SHA-256

- ANNOTATOR_A SYNTH_FIT_01: `587a5ff8dd7f13552636aa4724a137af6405bc2c80f092b12049dafbdfcf33f7`
- ANNOTATOR_A SYNTH_FIT_02: `51cf5a80583684e301ff7e66962534dfe789e23f229fe6a4a145a6ca89b21bfb`
- ANNOTATOR_A SYNTH_FIT_03: `ff7013ad6e4294bd447ae8ace0f56e1991fcc58cabd6d3fb5b14ffdde46531fb`
- ANNOTATOR_A SYNTH_FIT_04: `936010a3c605a554dd197a8d7bb971f0989c14a2cbc5a027498ddcf4709f1688`
- ANNOTATOR_B SYNTH_FIT_01: `36cbffa81e23f3f9bc5987598da6dfb979dbaf202b657787a2c5935715f68ef6`
- ANNOTATOR_B SYNTH_FIT_02: `3612da15b6ae534dd9fec71895ccd6397b8835a0f85aba39048c6714e1fbf01e`
- ANNOTATOR_B SYNTH_FIT_03: `1b8ba420a45e24b15d7e1084e94cdd1de4df497fc178146dbed7c2975a452b69`
- ANNOTATOR_B SYNTH_FIT_04: `586e62758674daa56682a9d747ff2daf35b5dba4d4a0358ff9556188dbefceed`

## Raw A/B agreement

- Exact state agreement: 3/4 = 0.75
- Cohen's kappa: 0.5; PABAK: 0.5
- PRESENT/PRESENT mean inclusive IoU: 0.8333333333333333
- Full-span matches: 1/2
- One-page boundary difference: SYNTH_FIT_03 (B starts one viewer page later).
- Presence difference: SYNTH_FIT_04 (A PRESENT, B ABSENT).

## PILOT_PLAN §6 soft triggers

- NOT_APPLICABLE: PILOT_PLAN v0.1/v0.1.1 §6 (identical in both; v0.1.1 changed only §3) states thresholds for the 10-document PILOT (e.g. presence disagreement on at least 2 of 10). They are not evaluated on 4 synthetic byte files; doing so would present a synthetic number as a trigger outcome.

## Test-only title-list handling

The bundle starts with TITLE_LIST_NOT_YET_FROZEN.txt. This runner refuses to continue unless its explicit synthetic title-list override is enabled. It replaces the placeholder only in temporary synthetic A/B workspaces before sealing; the real tools and repository title list are untouched.

## FINDINGS

- tools/phase5/annotator/make_bundle.py:36–40 ships an unfrozen-title placeholder; tools/phase5/annotator/annotator_core.py:477–496 has no title-list preflight in the direct sealing API. This synthetic runner adds an explicit temporary-workspace preflight; production tool code is unchanged.
- tools/phase5/scoring/__init__.py:294–353 returns no gap-set Jaccard or non-comparable counts, although docs/phase5/SAP_v0_1.md:131–140 calls for both in raw A/B agreement. The dry run records only values this API actually returns.
