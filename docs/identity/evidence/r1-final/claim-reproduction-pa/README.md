# A. Execution identity

P-A reproduction ID: `P-A-R1-20260926`. Execution date: 2026-09-26.

ARPipe repository/worktree: `D:\sem_iitk\sem9\thesis\sep_week1\r1-final`.
Common Git directory: `D:/sem_iitk/sem9/thesis/sep_week1/arpipe-0.1.0/.git`.
The enclosing thesis repository is separate and is not the production identity.

`EXECUTION_COMMIT = 28a67b63d890d8407fa9738a71ae37ad63148b73`.
All three processes started and ended at this exact detached HEAD, with empty
Git status and unchanged protected working-file hashes. Every loaded production
`arpipe` module in both pytest runs resolved inside this worktree.

The worktree initially held branch `r1-final` at preservation commit
`2a42b97bdc09297eba92ae6a46cd6e7365a0e54a`. It was temporarily detached at the
execution commit, then restored to that branch after all executions. No history
was rewritten. Documentation commit `383fa79228d48bf39401936090b9cbe9c5509e95`
was not used as an execution target.

No new worktree was necessary; reproduction was performed from the existing clean pinned worktree.

| Tree | Git tree hash |
|---|---|
| `arpipe/` | `f6475922f2a6837c7e6a86cefb5fb30aef602e69` |
| `configs/` | `4b56d25b28c18132cb1fcf4f847e4582a195036a` |

Environment: Python 3.14.3, pytest 9.1.1, Windows 11 build 26200, AMD64.
PyMuPDF 1.28.2, numpy 2.5.3 and all other recorded historical package versions
match the current visible versions. The existing isolated test-only directory
supplied jsonschema 4.26.0, attrs 26.1.0, jsonschema-specifications 2025.9.1,
referencing 0.37.0 and rpds-py 2026.6.3. No package was installed or modified.
Sandbox preflight denied access to historical dependencies; approved execution
outside the sandbox used those existing files without alteration.

See [environment.json](environment.json), [worktree-identity.json](worktree-identity.json)
and [execution-inputs.json](execution-inputs.json) for exact identities and hashes.
Source/test/config/tool working bytes were checked against pinned Git blobs,
and their before/after manifests were identical for every claim.

Commands below use aliases for readability; each claim JSON contains the exact
executed Windows argv, cwd, environment, timestamps, process status and hashes.
`PY` is the historical `arpipe-0.1.0/arpipe/.venv/Scripts/python.exe`;
`OUT` is `C:\Users\hario\AppData\Local\Temp\arpipe-pa-20260926`;
`RECOVERED` is the historical session scratchpad's `run-b` directory, whose full
path is recorded in [fixture-identity.json](fixture-identity.json).
`PYTHONPATH` explicitly contains the pinned worktree, original isolated test
dependencies and the external observer directory. Bytecode writing is disabled.
The reporting helpers were created for P-A outside the repository; their hashes
identify their executed bytes. They have no earlier input source commit and
do not change selection, fixtures, assertions or outcomes. Their copies here
are execution evidence; do not run the capture helper in this documentation directory.

# B. Claim A — 431-test suite

Command: `PY -B -m pytest -q -p no:cacheprovider -p pa_observer -rxXfEs --junitxml=OUT/claim-a.xml --basetemp=OUT/claim-a-temp`.

Execution was valid: collection succeeded, all 431 tests received outcomes,
the process completed with exit 0, and no infrastructure crash occurred.
Observed: **411 passed, 17 skipped, 3 xfailed, 0 xpassed, 0 failed, 0 errors**.
Independent arithmetic: **411 + 17 + 3 = 431**. Pytest runtime: 59.60 seconds;
process wall time: 60.992 seconds. This matches every expected historical count.

Classification: **REPRODUCED**. The environment's recorded package versions
match. Reporting-only additions were an external observer, JUnit output,
external basetemp and disabled bytecode writing. JUnit testcase parsing and the
observer's pytest categories independently agree; strict XPASS was separately
checked and is zero. This is a new execution, not proof that the historical
process embedded its commit in its output. The old `pytest-full.xml` remains
historical 382-test evidence and was neither substituted nor changed.

Evidence: [claim-a.json](claim-a.json), [complete stdout](claim-a.stdout.txt),
[stderr](claim-a.stderr.txt), [JUnit](claim-a.junit.xml),
[independent observation](claim-a-observed.json). SHA-256 values are recorded
in the claim record and [artifact-manifest.json](artifact-manifest.json).

# C. Claim B — 103-test fixture

Command: `PY -B -m pytest -q -p no:cacheprovider -p pa_observer RECOVERED/arpipe/tests/test_pipeline.py RECOVERED/arpipe/tests/test_pm1_orderqc.py -rsfE --junitxml=OUT/claim-b.xml --basetemp=OUT/claim-b-temp`.

The fixture directory is the recovered historical `run-b/arpipe/fixtures`:
**7 files, 72,556,845 bytes**. Each PDF matches its entry in the preservation
manifest; none was rebuilt or copied into ARPipe. Deterministic fixture-manifest
SHA-256: `1c7c34827dab0c3f4312437618c1716837740bbb35dfb81bdb5b1cd9b7db3d93`.
The manifest records every material fixture's hash; fixture and test bytes were
also rechecked unchanged after execution.

The historical fixture builder is `arpipe/tests/make_fixtures.py`, SHA-256
`ca233ddfd8c5c1682c094e38f533045efe06e7081233df649a344c2c31081063`.
The two executed test files have SHA-256
`85e558d95d96274efa82c28f1a624a76f01ec5ac40a26d0a056602d5ca395f06` and
`5d5ba30ef365dc32bf23878fcfd8c895f4d7c1756fffb694461af8a0e3e23020`,
respectively. All three files match their blobs at `28a67b63` byte-for-byte.
The builder was identified, not executed.

Observed and expected: **103 passed, 1 skipped**; total 104, exit 0, no failures,
errors, XFAIL or XPASS. The remaining skip reports `live_store blobs not present`.
Pytest runtime: 3.93 seconds; process wall time: 4.786 seconds.

Classification: **REPRODUCED_WITH_QUALIFICATION**. The historical transcript
identifies this fixture build and the two test files (lines 703/708), and the
later preservation manifest identifies the surviving bytes. No contemporaneous
per-fixture hash was recorded during the historical execution. That temporal
provenance limit remains. Current test files were read from the recovered tree
to use their unchanged hard-coded sibling fixture path; all production imports
were independently recorded inside the pinned worktree. The original execution
used production imports from its `run-b` Git export.

`INPUT_ARTIFACT_SOURCE_COMMIT` for test scripts is `28a67b63`; fixture PDFs have
no Git source commit. The preservation-manifest source is `2a42b97`, separately
from execution identity. Its SHA-256 is
`52848e29071076c7893852c1ce0e88a04eac1795f387a91c6b5822d74b11017d`.
This is evidence-machinery testing and is not merged into Claim A or Track A.

Evidence: [claim-b.json](claim-b.json), [fixture identities](fixture-identity.json),
[fixture manifest](fixture-manifest.sha256), [complete stdout](claim-b.stdout.txt),
[stderr](claim-b.stderr.txt), [JUnit](claim-b.junit.xml), and
[independent observation](claim-b-observed.json). Full artifact hashes are in
[artifact-manifest.json](artifact-manifest.json).

# D. Claim C — document hashes

Command: `PY -B tools/check_doc_hashes.py` from the pinned worktree.
Script SHA-256: `75fae87742838632ef6770183127626138f9363c4ec1bfeca8069eb56d451996`.
Script and allowlist were taken from `28a67b63`; both were last changed in
`24520ce623037fde7c3b0a9d0d4e5f8fc5618831`.

The script scans six `PHASE2.1_*.md` files and recognizes ten table entries in
`docs/experiments/PHASE2.1_PROVENANCE_CORRECTIONS.md`, lines 63–72.
That input's SHA-256 is
`7634e5f9736a5807ff01c68cb12ad007cbd53358b11ec76c6f2e82cd61539a36`;
its last change is `af89939b603217c05b78b0a1dc9789204b70ab17`.
The derived ten-entry manifest hash is
`bc313386f72e6570a3e6f96476777a67124412f98e48434575c10291dcb7892c`.

One check is one recognized table row containing a full source commit, source
path and recorded SHA-256. PASS means the recorded SHA-256 equals SHA-256 of
the exact `git cat-file blob` bytes at that commit/path. An unallowed failure
is a mismatch or unreadable blob whose document/commit/path key is absent from
the allowlist. The allowlist can permit mismatches; it was empty in this run.

Observed and expected: **10/10 PASS across 1 document, 0 unallowed failures**;
also 0 allowed failures, exit 0, process wall time 0.773 seconds.
Classification: **REPRODUCED**. This checks documentation-to-Git-blob integrity,
not ten PDF documents, historical provenance, or current scientific validity.

Evidence: [claim-c.json](claim-c.json), [script and input identities](document-hash-inputs.json),
[complete stdout](claim-c.stdout.txt), [stderr](claim-c.stderr.txt), and full
SHA-256 values in [artifact-manifest.json](artifact-manifest.json).

# E. Evidence/provenance assessment

| Claim | Historical status | New execution | Classification | Evidence |
|---|---|---|---|---|
| 431-test final suite | TRANSCRIPT-ONLY | 411 pass / 17 skip / 3 xfail; all other counts zero | REPRODUCED | `claim-a.json` |
| 103-test fixture | TRANSCRIPT-ONLY | 103 pass / 1 skip | REPRODUCED_WITH_QUALIFICATION | `claim-b.json` |
| Document hashes | TRANSCRIPT-ONLY | 10/10 PASS; 0 unallowed failures | REPRODUCED | `claim-c.json` |

**Reproduced:** new commands, commit-bound before/after states, complete process
streams, JUnit outcomes, independent pytest counts, production import origins,
fixture identities and script-defined hash verification results.

**Historical:** existing records/transcript and preservation metadata remain
unchanged. New execution does not replace the historical session or retrospectively
embed identity in its artifacts. Private transcript contents are not published.

**Inferred:** continuity from the historical fixture build to later preservation
has no contemporaneous per-file hash seal. Matching preserved fixture bytes is
direct integrity evidence; it alone is not historical provenance.

**Unresolved:** that fixture provenance limit and approved off-machine private
preservation. There is no observed count mismatch or global identity ambiguity.
No governance interpretation was attempted.

Execution identity is always `28a67b63`. Later documentation commits supply
preservation/provenance inputs only. Integrity evidence establishes byte identity;
execution evidence establishes what ran; historical provenance comes separately
from the contemporaneous command record, repository history and recovery chain.

All committed artifacts are **PUBLIC_SAFE** after content inspection. Raw JUnit
is **PRIVATE_ARCHIVE_REQUIRED** because of its hostname; public copies remove
only that attribute, preserving every other byte. Raw capture/observer search-path
inventories are private-only; the public records retain commands, imports, relevant
environment and complete outcomes. See [private-artifact-inventory.json](private-artifact-inventory.json)
for hashes/locations. No load-bearing outcome was redacted. The copied historical
environment's exact-byte hash and normalized-text hash are explicitly distinguished.
Fixture PDFs and disposable pytest execution trees are **EXCLUDE** from publication.

Reproduction status: **ALL THREE CLAIMS REPRODUCED**.
Claim B retains the qualification stated above.

R1 identity status: **The existing R1 identity remains unchanged.**

Only these three claims are addressed. The existing Track-A evidence and its
qualifications still govern. This is not full R1 reproduction and establishes
no new MD&A/OCR accuracy, scientific validity, Gold/HOLDOUT validity, C1 validity,
or Phase 5 methodological validity.

# F. Repository impact

Only this new `docs/identity/evidence/r1-final/claim-reproduction-pa/` directory
is added. All original public evidence and historical commits are unchanged.
The evidence-only commit is a child of preservation commit `2a42b97`; Git history
binds this package to that commit. No push is authorized or performed.

No changes to `arpipe/`, `configs/`, `dataset/`, `tests/`, `tools/`, `conftest.py`,
HOLDOUT, Gold or scientific outputs. No corpus pipeline, historical comparison,
determinism experiment, Gold construction or methodology task was run.
Both P-A pytest temporary trees were removed after evidence capture. The existing
worktree was restored to `r1-final`; no worktree was created or removed.
The final commit and final Git status are reported in the task's final response.

# G. R1 preservation status

**PRESERVED_BUT_NOT_YET_DURABLE**

No off-machine archive operation occurred. Local original P-A captures and the
existing private transcript do not establish durable private preservation.

# H. Next authorized task

**P-B — Author-Decision / Governance Transcription**

Not begun. P-A stops with this report.
