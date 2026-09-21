# Phase 2.1 — Provenance Correction Closeout

**Status:** downstream correction record (documentation/provenance layer only)  
**Applies on top of:** `ebf9e11b936687d4ab2a4f53058ef458cd2b68a2` (parent `813ba5badd75021263f0433d23ff217f6d764719`)  
**Claim labels:** VERIFIED = recomputed from Git objects/command output in this task; INFERRED / PROPOSED are not used for any adopted claim below.

---

## 1. Corrections made [VERIFIED]

| Record | Ledger row | What was wrong | Correction location |
|---|---|---|---|
| PC-05 (P2-20) | CHG-20 | Direction of the trailing-LF relationship was reversed ("plus one newline"); printed hashes were not hashes of any variant of the blob bytes. | `PHASE2.1_PROVENANCE_CORRECTIONS.md` PC-05 and Section 2A; `PHASE2.1_CHANGE_LEDGER.md` CHG-20 |
| PC-06 (P2-21) | CHG-21 | All 10 replacement SHA-256 values were not the hashes of the cited blobs; the "printed in Phase-1 report" column did not reproduce the report. | `PHASE2.1_PROVENANCE_CORRECTIONS.md` PC-06 and Section 3; `PHASE2.1_CHANGE_LEDGER.md` CHG-21 |
| PC-05 summary | — | `PHASE2.1_FOUNDATION_NORMALIZATION.md` Part B item 5 repeated the reversed "plus one newline" claim. One clause corrected; Part I untouched. | `PHASE2.1_FOUNDATION_NORMALIZATION.md` Part B |

PC↔CHG pairing used: by Finding ID, PC-05 = P2-20 = CHG-20 and PC-06 = P2-21 = CHG-21 (author decision). CHG-05 and CHG-06 were not touched. No record was renumbered, retyped, merged, split, created or deleted.

## 2. Explicitly deferred (not done in this commit)

- Hash-lint tooling and tests: deferred to a separate tooling/integrity task (author decision). Not added.
- Reconciliation of the Part I PC/CHG category counts in `PHASE2.1_FOUNDATION_NORMALIZATION.md`: deferred (author decision).
- `MASTER_FLOW_v1.md`: not created (no author-supplied master flow).
- Git bundle: `BUNDLE_STATUS = SKIPPED_NO_BACKUP_DIR_SPECIFIED`.
- B1–B8: untouched, all remain `PENDING_AUTHOR_DECISION`.

## 3. Roadmap / decision-sheet provenance [VERIFIED search result]

Search: `git log --all --full-history` for both names, name match across the tree of every ref, and a read-only filesystem search of the thesis root (including `ARPipe_Memory/`), `D:\sem_iitk`, Downloads, Documents, OneDrive and `.claude`.

| File | Result |
|---|---|
| `18_ROADMAP.md` | NOT FOUND (no Git object; no file on searched filesystem locations) |
| `17_B1_B8_DECISION_SHEET.md` | NOT FOUND (no Git object; no file on searched filesystem locations) |

`ROADMAP_GIT_PROVENANCE = UNVERIFIED`. If either exists only as a project/File Library artifact outside these locations, its existence is unrecorded here and it must not be treated as Git-authoritative. Unrelated `ROADMAP.md` files under a different project (`controlplane`) were not considered candidates. This record does not authorize Phase 3, Phase 4, Gold, OCR or any B1–B8 decision.

## 4. Repository inventory (read-only) [VERIFIED]

- The 194 corpus PDFs are content-addressed under `arpipe-0.1.0\live_store` (194 PDFs, 1,390,085,436 bytes) on drive D:. No same-named PDF (over 100 KB) was found on C: (the only other drive present). Sixteen are also duplicated elsewhere on D: (`pilot_store`, `arpipe-pr1x-execution\store`).
- E0 PDF directories under `arpipe-0.1.0` (PDF bytes): `pm1_after_run` 1,380,917,997; `pm1_baseline_run` 1,380,917,997; `scratch` 2,774,585,193; `arpipe/pnb_dataset` 95,041,694. Nothing was copied, deleted or modified.
- Local branch `main` is behind `origin/main` by 17; most other local branches have no upstream. Nothing was pushed.
