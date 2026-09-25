# R1 A1–A6 Decision Record

Recorded 2026-09-26 by R1-FINAL v3 on branch `r1-final`. This file closes the six decisions
that `docs/identity/R1_RESUME_GATE_BLOCKER.md` section 6 listed as required to resume R1. It
records where each one was resolved and what the repository can verify about it. It does not
create authorization; it points at the authorization that exists.

Evidence labels: **VERIFIED** (repository content or command output), **DERIVED** (mechanical
consequence of verified facts), **INFERRED** (interpretation not stated by the repository),
**NOT VERIFIABLE** (required evidence is absent).

## 1. Provenance of the authorization

A1–A5 were first applied as commits on 2026-09-26 with subjects citing "A1" … "A5". At the time
of the T0.4 guard forensic audit, the authorizing text itself could not be found in the
repository: `docs/identity/T0_4_GUARD_FORENSICS.md` section 5 records that the citation
"D6/Q6 amendment A5" appears only in a test comment, and section 11 lists "the A1–A5
authorization text" as **NOT VERIFIABLE**.

That gap is now closed for the production reconstruction: **T0.4 Amendment 01**
(`docs/identity/T0_4_AMENDMENT_01.md`), ratified verbatim by the author Hariom Singh on
2026-09-26, authorizes exactly the A1–A4 four-file reconstruction by commit and by path, and
requires the exact-path Phase 2.1 admission that A5 performs. **VERIFIED**

The amendment is prospective governance of the reconstruction; it does not retroactively supply
an authorization that existed at the time those commits were made. The historical sequence
stands as recorded. **DERIVED**

## 2. The six decisions

### A1 — `arpipe/models.py`

**Question:** authorize `models.py` = E0 verbatim (including `body_script`, `script_meta`),
which amends D6 section 9.5, or a subset, which contradicts evidence E3.

**Resolved: E0 verbatim.** Commit `d5513859a5315800a7b6c68711756798129ab8ee`
("fix(r1): restore authorized model provider fields (A1)"), +9 lines, one file. The resulting
blob `e91c73c8d537a7873a765933bd959feed0aa9fd9` is byte-identical to the E0 snapshot's
`arpipe/models.py` at `dea3ae5399be50872768c8703c878c907ee6818b`. **VERIFIED**

It adds `Confidence.QUARANTINE` and the optional fields `StoredDoc.script_map`,
`PageProfile.script_meta`, `DocProfile.script_map`, `MDASpan.body_script`. Two of those —
`MDASpan.body_script` and `PageProfile.script_meta` — are named in D6 section 9.5 as *not*
authorized by D6. The conflict the resume-gate blocker identified was real, and it is resolved
by the author's ratification of T0.4 Amendment 01, whose section 1 admits this commit by SHA.
**VERIFIED**

Supporting evidence that the historical run carried these fields: all 364 `mda.json` files in
the preserved runs contain `span.body_script: null`, and the per-page `script_map` entries
carry exactly the keys the E0 `triage` computation emits (blocker evidence E1, E3).

### A2 — `arpipe/triage.py`

**Question:** authorize `triage.py` = E0 verbatim, which the R1 STOP list and D6 section 11.2
required to be explicit.

**Resolved: E0 verbatim.** Commit `ca1498f75f14495bfc6ec829ef2b5ef728da2d3d`, +73 lines, one
file; blob `de9d528924db97f733f9f2ee985e6d1a8be406af`, byte-identical to E0's. **VERIFIED**

The explicit authorization D6 section 11.2 demanded is T0.4 Amendment 01 section 1, which names
this commit. The amendment also constrains it: the Track-A protected symbols must stay
byte-identical to the T0.4 base, and the behavioural requirement is identical page kinds and
OCR-page sets. Both are now enforced by `tests/test_t0_4_amendment_01.py` and demonstrated over
20 950 FIT and VALIDATION pages with 0 mismatches (`docs/identity/RUNNABLE_IDENTITY_v1.md`
section 13). **VERIFIED**

### A3 — `arpipe/ocr.py`

**Question:** class only, or E0 verbatim including the P-B5 raise path.

**Resolved: class only.** Commit `ab9666b032a5838be3ae3a24a58aae68a4fd46b0`, +17 lines, one
file. It adds the `OcrEngineUnavailable` class and nothing else; the file is a strict subset of
E0's version, which adds 59 further lines (the `_ensure_ready` and `Escalator.run_page` raise
paths) that are **not** taken. **VERIFIED**

This is the conservative branch of the choice. The blocker classed "whether the 2026-09-17 tree
had the P-B5 raise path" as **INFERRED** and therefore a stop condition; taking the class only
avoids resting on that inference, and matches D6 section 9.5, which does not authorize the
P-B5 raise behaviour. The cost is recorded honestly: the reconstruction is not claimed to be
byte-identical to the executed `ocr.py`. **DERIVED**

### A4 — `arpipe/store.py`

**Question:** `write_span` hunk only, or E0 verbatim.

**Resolved: the `write_span` hunk only.** Commit `24b8e000f23d18faabd16f828bd20eeb5328ddf7`,
+19 −6 lines, one file. A strict subset of E0's version, which adds 70 further lines (the
`open_state` / `import_manifest_state` / `snapshot_state` hooks and a `rows=` kwarg) that are
**not** taken, consistent with D6 section 9.5 excluding `state.py`. **VERIFIED**

### A5 — Phase 2.1 allowlist amendment

**Question:** amend `test_historical_immutability_strict_allowlist`, which already failed at
START and which any `arpipe/` change or new `docs/identity/` file would fail further.

**Resolved: exact-path admission, twice.**

1. Commit `c779c2e471ef8c3455c827de9ef571443f41911c` ("test(r1): admit exact reconstruction
   paths under A5") admitted the four A1–A4 production paths, `tests/test_import_smoke.py`, and
   the `docs/phase3/`, `docs/phase4/`, `docs/decisions/`, `docs/identity/` directories.
2. This task's enforcement commit admitted, by exact path only,
   `docs/identity/T0_4_AMENDMENT_01.md`, `tests/test_t0_4_amendment_01.py` and `conftest.py`,
   as T0.4 Amendment 01 section 6 requires.

Neither edit weakens the original T0.4 guards, which are untouched. The test passes at the
pinned tip. **VERIFIED**

### A6 — `jsonschema`

**Question:** add `jsonschema` to `arpipe/requirements.txt` or not.

**Resolved: not.** `jsonschema` is a **TEST-ONLY** dependency. It is installed into a scratch
directory outside the repository and supplied on `PYTHONPATH` for test runs. It is absent from
the virtual environment, absent from `arpipe/requirements.txt`, and imported by no `arpipe/`
module. `arpipe/requirements.txt` is byte-identical to the T0.4 base. **VERIFIED**

The instruction under which R1-FINAL ran states this directly: "Use jsonschema only as a
test-environment dependency. Do not modify `arpipe/requirements.txt`."

## 3. Summary

| # | Subject | Resolution | Authorizing record |
|---|---|---|---|
| A1 | `arpipe/models.py` | E0 verbatim | T0.4 Amendment 01 section 1 (commit `d5513859a5315800a7b6c68711756798129ab8ee`) |
| A2 | `arpipe/triage.py` | E0 verbatim | T0.4 Amendment 01 section 1 (commit `ca1498f75f14495bfc6ec829ef2b5ef728da2d3d`) |
| A3 | `arpipe/ocr.py` | class only, no raise paths | T0.4 Amendment 01 section 1 (commit `ab9666b032a5838be3ae3a24a58aae68a4fd46b0`) |
| A4 | `arpipe/store.py` | `write_span` hunk only | T0.4 Amendment 01 section 1 (commit `24b8e000f23d18faabd16f828bd20eeb5328ddf7`) |
| A5 | Phase 2.1 allowlist | exact-path admission, no guard edited | T0.4 Amendment 01 section 6; commit `c779c2e471ef8c3455c827de9ef571443f41911c` and this task's enforcement commit |
| A6 | `jsonschema` | TEST-ONLY; `arpipe/requirements.txt` unchanged | R1-FINAL v3 Step 5 instruction |

## 4. What this record does not establish

1. It does not establish byte-identity between this reconstruction and the tree that executed
   on 2026-09-17. `arpipe/ocr.py` and `arpipe/store.py` are deliberate strict subsets of the
   preserved E0 provider half, and `arpipe/patterns.py` was dirty on 2026-09-17 with
   unrecoverable bytes. **DERIVED**
2. It does not resolve C2. C2 remains **CONDITIONAL**, per D6 section 10.
3. It does not resolve Track B, which remains **UNRESOLVED / DEFERRED**.
4. It does not retroactively supply an authorization that existed when A1–A5 were first
   committed. **DERIVED**
