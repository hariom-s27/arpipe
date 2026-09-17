# P-B2 Phase 1 Source Recovery and Provenance Report

## Executive Summary

- **Task**: P-B2 Phase 1 Source Tree Provenance and Recovery
- **Final Verdict**: `P-B2 PHASE 1 SOURCE PARTIALLY RECOVERED`
- **Original Base SHA**: `0fb8cbf6d932f4190bdfe3b2a1fecf62170cca14`
- **Frozen Commit SHA**: `NONE` (Creation halted due to exact hash mismatches on required production files)
- **Phase 2R Status**: `BLOCKED` (P-B2 Phase 2R may NOT proceed)

---

## 1. Provenance Records Inspected

In accordance with recovery instructions, all extant Phase 1 and isolation records were located and examined:

1. `reports/pb2_phase2_frozen_snapshot/pb2_phase2_isolation_provenance.json`:
   - Identified base Git commit `0fb8cbf6d932f4190bdfe3b2a1fecf62170cca14` as dirty at baseline (`baseline_recorded_worktree_dirty: true`).
   - Documented production source drift: all 12 pinned production files changed subsequent to the Phase 1 baseline due to concurrent active modification in the shared `arpipe-0.1.0` tree.
   - Pinned config version `230222f37ad4ecab63989b99d66e701b6b3399ae08ff72fe8342b6c7e1d2ee62` and dataset manifest `8607cd29d9e660fee1b18ce9d980e0a39c217275201d72114e4ce0a9fe89a625`.

2. `reports/pb2_phase1_baseline.json`:
   - SHA-256: `6e4ae93727ef1be2f746ddf2f3d0b924139dff6836f232e84aaf481ff8247f6f` (VERIFIED MATCH).
   - Recorded the exact 12 production source file hashes at baseline (2026-09-16T21:51:09.434646+00:00).
   - Recorded baseline tool `tools/pb2_phase1_baseline.py` SHA-256 `2e312db0f5dc6a3ce4f989d6b2b1891f87f4c29680257a0a99db7367205f414b` (VERIFIED MATCH).

3. `scratch/pb2_phase1/after_run.json`:
   - Recorded the exact production source file hashes at the conclusion of the instrumented Phase 1 run (2026-09-16T22:18:47.462663+00:00).
   - Pinned `models.py` at `e40faa0b467c74bdc405f5d7de898633b07a3f2b5da425e8f3c1b05c6c2b2217` (VERIFIED MATCH).
   - Pinned `segment.py` at `6b1122cefdb63ce5d4fdaac0e8a1383b6213cb4d57c3a5d5cdd3c232bffb3837` (VERIFIED MATCH).
   - Pinned `textlayer.py` after-run snapshot at `6117552014bcc60f16e3884dcebb3c4e086acbe8a22066fed134aa2dc65c1c16`.

4. `scratch/pb2_phase1/concurrency_notes.md`:
   - Detailed contemporaneous forensic observation during the Phase 1 run:
     > *"While this task ran, another process was editing the same working tree — files outside P-B2's scope, with its own artifacts (`arpipe/tests/test_pm1_orderqc.py`, `tools/pm1_run_corpus.py`, `pm1_baseline_run.log`, and a sibling checkout `../arpipe-pm2-native-vs-ocr/`)... After those edits, byte-exact baseline copies of `verify.py` and `pipeline.py` were no longer recoverable anywhere on disk (their `__pycache__` entries had been recompiled from the other task's intermediate versions)..."*

5. `reports/pb2_phase1_candidate_body_script.csv`:
   - SHA-256: `57d227ee108a8b83cd06c3c38f1056c08dbf351a4012afa8cd6fa985e48cbba3` (VERIFIED MATCH).

6. `reports/pb2_phase1_candidate_body_script.md`:
   - SHA-256: `46fc067a10cd698e2460ef323cb80d403b176fa3c773d6496be2029abc4ba37d` (VERIFIED MATCH).

---

## 2. Git Object Database Inspection

A full inspection of the Git object database, commit history, unreachable objects, stashes, and sibling worktrees was conducted:
- `git fsck --full --no-reflogs --unreachable`: Identified 12 unreachable objects, including:
  - Commit `4671bde5f8bc754854e9cf6db32ea6f2712f27f7` ("On main: PM1 in-progress edits", stash working directory commit).
  - Commit `74dec2f900d0e015b2797f3b0f0ed57c2a2f8c9c` (stash index commit).
  - Commit `cf4050992b6594ce9ed49afd2f8023e5022d8cd7` (PM2 native vs OCR measurement).
  - Blobs for P-M2.1 documentation and tests.
  - None of the unreachable objects contained the missing baseline versions of `cli.py`, `pipeline.py`, or `verify.py`.
- `git rev-list --objects --all` and `git cat-file`:
  - 402 total objects were scanned byte-for-byte against all expected Phase 1 and baseline hashes.
  - Baseline `config.py` was recovered in git blob `6dfb8912dcdd2d872f12f29f5d1e3e348b656036`.
  - Baseline `textlayer.py` was recovered in git blob `731e4bf8b6d3cc2fdffc303890b65cfcce21b6ac`.
  - Pre-B2 `segment.py` baseline was recovered in git blob `f2e74bb216768e1f29c4f437774d3dea6f0975d8`.
  - The baseline versions of `cli.py` (`68c4ba...`), `pipeline.py` (`93c621...`), and `verify.py` (`88b7e6...`) do NOT exist as Git objects anywhere in the repository.

---

## 3. Forensic Inventory and Recovery Table

| File | Expected SHA-256 | Recovered SHA-256 | Status | Recovery Source |
| :--- | :--- | :--- | :--- | :--- |
| `arpipe/models.py` | `e40faa0b467c74bdc405f5d7de898633b07a3f2b5da425e8f3c1b05c6c2b2217` | `e40faa0b467c74bdc405f5d7de898633b07a3f2b5da425e8f3c1b05c6c2b2217` | **MATCH** | `arpipe-0.1.0/arpipe/models.py` |
| `arpipe/segment.py` | `6b1122cefdb63ce5d4fdaac0e8a1383b6213cb4d57c3a5d5cdd3c232bffb3837` | `6b1122cefdb63ce5d4fdaac0e8a1383b6213cb4d57c3a5d5cdd3c232bffb3837` | **MATCH** | `arpipe-0.1.0/arpipe/segment.py` |
| `arpipe/config.py` | `93aba31b53d4173bde3ad322bd5625416eca29e86b89887461f5bc2c7d760c7c` | `93aba31b53d4173bde3ad322bd5625416eca29e86b89887461f5bc2c7d760c7c` | **MATCH** | `arpipe-0.1.0/arpipe/config.py` / git blob `6dfb8912` |
| `arpipe/ocr.py` | `affec70f25339e20b5619afe7c7462cc2eb8700d19b4c34e155341e7c0f4b684` | `affec70f25339e20b5619afe7c7462cc2eb8700d19b4c34e155341e7c0f4b684` | **MATCH** | `arpipe-0.1.0/arpipe/ocr.py` |
| `arpipe/patterns.py` | `950400cdbe31d4b4548538f5750f32a97add41f958f7db3da75ded46beb6e83b` | `950400cdbe31d4b4548538f5750f32a97add41f958f7db3da75ded46beb6e83b` | **MATCH** | `arpipe-0.1.0/arpipe/patterns.py` |
| `arpipe/store.py` | `9f5a1b8ee3f979306bff6f4cd876083eadcdbe4bd7d1631a0f7f709167cd5bcd` | `9f5a1b8ee3f979306bff6f4cd876083eadcdbe4bd7d1631a0f7f709167cd5bcd` | **MATCH** | `arpipe-0.1.0/arpipe/store.py` |
| `arpipe/triage.py` | `351a4aac1efcee4899999b7c76899856a963d1687442fea4a75dcab9cc754892` | `351a4aac1efcee4899999b7c76899856a963d1687442fea4a75dcab9cc754892` | **MATCH** | `arpipe-0.1.0/arpipe/triage.py` |
| `arpipe/configs/default.yaml` | `fe7534793407a8f51fc89bab2371ee952acac55db6eb9353892b45a0c1a72d1a` | `fe7534793407a8f51fc89bab2371ee952acac55db6eb9353892b45a0c1a72d1a` | **MATCH** | `arpipe-0.1.0/arpipe/configs/default.yaml` |
| `arpipe/textlayer.py (baseline)` | `09c23e5c76d581924200f69396c6d9720d5cde3917400fb14fabaa4943556a85` | `09c23e5c76d581924200f69396c6d9720d5cde3917400fb14fabaa4943556a85` | **MATCH** | git blob `731e4bf8` (commit `0fb8cbf6`) |
| `arpipe/textlayer.py (after-run)` | `6117552014bcc60f16e3884dcebb3c4e086acbe8a22066fed134aa2dc65c1c16` | `02e868e011aa4d957f83d3b3d93ad16739f5b7d426dd18011de17786aac06f77` | **MISMATCH** | UNVERIFIED (overwritten by concurrent task) |
| `arpipe/cli.py` | `68c4ba0d8ccf383af718e5acb16e5c0d2717b6f99f30c5de585eeef949c45350` | `69c9d4519b7f3ba42c316f5395a9a2e21eb77053718458376ff32e6b7cbb48bb` | **MISMATCH** | UNVERIFIED (overwritten by concurrent task) |
| `arpipe/pipeline.py` | `93c62172f2b9aae0b92091352edabb389092baae9461f76cb1959b88b71f1bad` | `66ecf6cfa0d8a7ea46c928fbf646fbb06c4f5687a33e46555438e976bf76060d` | **MISMATCH** | UNVERIFIED (overwritten by concurrent task) |
| `arpipe/verify.py` | `88b7e69f3382059bb26eeeebbc8670bd29680d1850582165e78946b5482d733a` | `29dd0a415d58874a53e01d52c8b802ad2f9fb550eb2c2a50efa9525f780f4b63` | **MISMATCH** | UNVERIFIED (overwritten by concurrent task) |
| `arpipe/tests/test_pb2_candidate_body_script.py` | `b750e983a15dc9068601920ed2d0722e57f734e80753f704afbf60d09b7564e5` | `b750e983a15dc9068601920ed2d0722e57f734e80753f704afbf60d09b7564e5` | **MATCH** | `arpipe-0.1.0/arpipe/tests/test_pb2_candidate_body_script.py` |
| `tools/pb2_phase1_baseline.py` | `2e312db0f5dc6a3ce4f989d6b2b1891f87f4c29680257a0a99db7367205f414b` | `2e312db0f5dc6a3ce4f989d6b2b1891f87f4c29680257a0a99db7367205f414b` | **MATCH** | `arpipe-0.1.0/tools/pb2_phase1_baseline.py` |
| `tools/pb2_phase1_diagnostic.py` | `fa7834564b3fb7fe84346cf73e4e44e695ad7ea86770b71e825c385ab9161b8e` | `fa7834564b3fb7fe84346cf73e4e44e695ad7ea86770b71e825c385ab9161b8e` | **MATCH** | `arpipe-0.1.0/tools/pb2_phase1_diagnostic.py` |
| `scratch/pb2_phase1/pre_b2_sources/models.py` | `4f4c45bde8bc4e6ac558698606224a66dc9bdf9887fc6363afcd310b130586fc` | `4f4c45bde8bc4e6ac558698606224a66dc9bdf9887fc6363afcd310b130586fc` | **MATCH** | `arpipe-0.1.0/scratch/pb2_phase1/pre_b2_sources/models.py` |
| `scratch/pb2_phase1/pre_b2_sources/segment.py` | `e90c67b7d334fe896029a2960dc49b1782f1a1b9f692f0be9feec73890de96ba` | `e90c67b7d334fe896029a2960dc49b1782f1a1b9f692f0be9feec73890de96ba` | **MATCH** | git blob `f2e74bb2` / `pre_b2_sources/segment.py` |

---

## 4. Phase 1 Analytical Artifacts Verification

| Artifact | Expected SHA-256 | Actual SHA-256 | Status |
| :--- | :--- | :--- | :--- |
| `reports/pb2_phase1_baseline.json` | `6e4ae93727ef1be2f746ddf2f3d0b924139dff6836f232e84aaf481ff8247f6f` | `6e4ae93727ef1be2f746ddf2f3d0b924139dff6836f232e84aaf481ff8247f6f` | **VERIFIED MATCH** |
| `reports/pb2_phase1_candidate_body_script.csv` | `57d227ee108a8b83cd06c3c38f1056c08dbf351a4012afa8cd6fa985e48cbba3` | `57d227ee108a8b83cd06c3c38f1056c08dbf351a4012afa8cd6fa985e48cbba3` | **VERIFIED MATCH** |
| `reports/pb2_phase1_candidate_body_script.md` | `46fc067a10cd698e2460ef323cb80d403b176fa3c773d6496be2029abc4ba37d` | `46fc067a10cd698e2460ef323cb80d403b176fa3c773d6496be2029abc4ba37d` | **VERIFIED MATCH** |

---

## 5. Determination on Dependencies and Concurrent Modifications

1. **Did P-B2 Phase 1 depend on modifications to `verify.py`, `pipeline.py`, `triage.py`, `textlayer.py`, `cli.py`, `patterns.py`, or `ocr.py`?**
   - **No.** Phase 1 was strictly observational. As verified in Section 12 of `reports/pb2_phase1_candidate_body_script.md`, Phase 1 modified exactly two production files (`models.py` and `segment.py`), both insertion-only against authenticated pre-B2 baselines. Phase 1 did not modify `verify.py`, `pipeline.py`, `triage.py`, `textlayer.py`, `cli.py`, `patterns.py`, or `ocr.py`, and did not alter any candidate filtering, ranking, arbitration, quarantine gate, or OCR routing.
2. **Did Phase 1 execute against specific uncommitted versions of those files?**
   - **Yes.** Phase 1 was executed in the shared, dirty `arpipe-0.1.0` worktree. Its runtime import pool imported the resting versions of all modules at the start of the baseline and regression runs.
   - While `config.py`, `ocr.py`, `patterns.py`, `store.py`, `triage.py`, `default.yaml`, and `textlayer.py` (baseline) have been recovered with exact SHA-256 byte identity, the uncommitted resting versions of `cli.py`, `pipeline.py`, and `verify.py` were overwritten by another concurrent task during and immediately after the Phase 1 run.
   - Because these uncommitted versions were never committed to any Git ref, tree, or stash, their exact byte identity cannot be recovered from any repository object or disk artifact.

---

## 6. Stop Condition Enforcement

Per the task protocol:
> **STOP immediately if:**
> - *exact Phase 1 source bytes cannot be established*
> - *a required file has a hash mismatch*
> - *the frozen commit cannot reproduce the recovered hashes*
> - *the contaminated shared worktree must be modified to continue*
> - *the worker would need to infer missing source*
>
> **Do not downgrade an exact-hash requirement to a behavioral-equivalence test.**

Because `arpipe/cli.py`, `arpipe/pipeline.py`, and `arpipe/verify.py` have hash mismatches against their recorded baseline SHA-256 values and cannot be recovered without inferring missing source, the creation of a frozen commit on branch `pb2-p1-frozen` was **HALTED**.

The shared worktree `arpipe-0.1.0` was **NOT MODIFIED** in any way (no reset, clean, checkout, revert, stash, merge, rebase, overwrite, delete, or commit). All recovery inspection and reporting was conducted strictly via read-only inspection and the dedicated recovery worktree `arpipe-pb2-p1-recovery`.

---

## 7. Final Verdict

```text
P-B2 PHASE 1 SOURCE PARTIALLY RECOVERED
```

### Missing / Unverified Files:
1. `arpipe/cli.py` (expected `68c4ba0d8ccf383af718e5acb16e5c0d2717b6f99f30c5de585eeef949c45350`, current `69c9d4519b7f3ba42c316f5395a9a2e21eb77053718458376ff32e6b7cbb48bb` — MISMATCH)
2. `arpipe/pipeline.py` (expected `93c62172f2b9aae0b92091352edabb389092baae9461f76cb1959b88b71f1bad`, current `66ecf6cfa0d8a7ea46c928fbf646fbb06c4f5687a33e46555438e976bf76060d` — MISMATCH)
3. `arpipe/verify.py` (expected `88b7e69f3382059bb26eeeebbc8670bd29680d1850582165e78946b5482d733a`, current `29dd0a415d58874a53e01d52c8b802ad2f9fb550eb2c2a50efa9525f780f4b63` — MISMATCH)
4. `arpipe/textlayer.py (after-run snapshot)` (expected `6117552014bcc60f16e3884dcebb3c4e086acbe8a22066fed134aa2dc65c1c16`, current `02e868e011aa4d957f83d3b3d93ad16739f5b7d426dd18011de17786aac06f77` — MISMATCH; note baseline `09c23e5c...` is preserved in git blob `731e4bf8`)

**Phase 2R must NOT proceed.**

