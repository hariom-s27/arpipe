# R1-FINAL evidence archive

Durable archive of the execution evidence behind the R1-FINAL runnable-identity
record (`docs/identity/RUNNABLE_IDENTITY_v1.md`), created by the R1 Evidence
Preservation task on 2026-09-26.

**Preservation is not reproduction.** Nothing in this archive was produced by
running ARPipe. Every artifact under `scratchpad/`, `r1-final-evidence/` and
`historical-baseline/` is a byte-exact copy of a file that already existed when
this task began, copied without normalisation of line endings, encoding, JSON
formatting, paths or timestamps-inside-files. The archive does not create,
strengthen or re-endorse any R1 result; it makes the existing evidence survive
the disappearance of the temporary directories it was sitting in.

Governing identity of the evidence in this archive:

| Item | Value |
|---|---|
| Branch | `r1-final` |
| Final commit | `383fa79228d48bf39401936090b9cbe9c5509e95` |
| Parent | `28a67b63d890d8407fa9738a71ae37ad63148b73` |
| Identity universe | 59 tracked files under `arpipe/` + `configs/` at `28a67b6` |
| Combined identity digest | `de250c36a660d94a2e28b49b82860f77e130b04a6fdcfc3ebf444043f57ef203` |

---

## 1. Evidence layers

The archive mixes material of four different evidential weights plus the
metadata this task itself produced. They are not interchangeable.

### 1.1 HISTORICAL R1-FINAL EVIDENCE

Original output of the R1-FINAL execution session, produced 2026-09-26
01:45–02:06 IST in the session scratchpad. This is the governing layer.

- `scratchpad/universe.json` — the 108-document input population
- `scratchpad/profile_base.json`, `scratchpad/profile_cand.json` — the two triage profiles
- `scratchpad/comparison.json`, `scratchpad/evidence_compact.json` — the Track-A comparison
- `scratchpad/suite_pin.txt`, `scratchpad/suite_pin.xml` — the 431-test suite pin
- `scratchpad/negative_tests.out` — the six negative-test outcomes

All eight are hash-listed in `RUNNABLE_IDENTITY_v1.md` §22 and all eight
hash-match here.

### 1.2 SUPPORTING EVIDENCE

Real artifacts of the same executions that §22 did not hash-list, plus the
separate 58-document and 4-document sessions under `r1-final-evidence/`:

- the generating scripts (`build_universe.py`, `profile_docs.py`,
  `compare_profiles.py`, `run_pipeline_doc.py`, `negative_tests.sh`,
  `gen_identity.py`; `prepare_run.py`, `run_document.py`, `run_batch.py`,
  `compare_outputs.py`)
- run logs (`profile_base.log`, `profile_cand.log`, `run-a.log`, `run-b.log`,
  66 per-document logs)
- `r1-final-evidence/historical-comparison.json` (§22-listed),
  `determinism-comparison.json`, `preregistration.json/.txt`, `fit-inputs.json`
- 58 + 4 + 4 pairs of `result.json` / `execution.json`
- `scratchpad/out-run-a/`, `scratchpad/out-run-b/` result and summary JSON
- identity and environment captures

`r1-final-evidence/pytest-full.xml` belongs to this layer and is **the older
382-test execution** (`tests="382" failures="5"`, exit code 1, timestamp
2026-09-26T00:43:03). It is **not** the final 431-test result and must not be
relabelled as such. The 431-test result is `scratchpad/suite_pin.*`.

### 1.3 TRANSCRIPT EVIDENCE

The R1-FINAL session transcript. It is the **only** evidence for three recovered
claims: the 431-test run against the final tip `383fa79`, the 103-test
scratch-fixture run, and the `tools/check_doc_hashes.py` document-hash checks.

The transcript is **not in this archive.** It is private conversation content
and is held in the private tier described in §4 below. Its identity is pinned
here and in the manifest:

```
948b3666-670c-4ce4-951f-ff0d9a9b4562.jsonl
3,388,079 bytes, 915 lines
sha256 9352b967c0c6dc4d30b850420b2ac92da1773caf4113c6578fd9642e8055d217
```

Transcript evidence stays transcript evidence. It is not promoted to ordinary
artifact evidence by having been preserved.

### 1.4 HISTORICAL BASELINE EVIDENCE

`historical-baseline/` holds the 2026-09-17 baseline span results that the
58-document historical comparison was run against — `pm1_baseline_run/` and
`pm1_after_run/` manifests plus their run logs. Only the manifests and logs are
preserved; the surrounding 1.4 GB of run output is excluded (see the omission
register).

### 1.5 CURRENT PRESERVATION METADATA

Produced by this preservation task, not by R1. Clearly derivative:

- `r1-final-evidence-manifest.json` / `.txt` / `.sha256`
- `tree-manifests/*.sha256` — per-file SHA-256 listings of the four execution
  trees, which are themselves not copied here
- this `README.md` and `OMISSION_REGISTER.md`

---

## 2. Layout

```
docs/identity/evidence/r1-final/
    README.md                            this file
    OMISSION_REGISTER.md                 what was considered and not preserved
    r1-final-evidence-manifest.json      machine-readable manifest
    r1-final-evidence-manifest.txt       human-readable companion
    r1-final-evidence-manifest.sha256    hash of the JSON manifest
    scratchpad/                          R1-FINAL session scratchpad artifacts
        out-run-a/, out-run-b/           third-run outputs for INE00LO01017_2025
    r1-final-evidence/                   repository-side evidence directory
        primary/<doc>/                   58 x result.json + execution.json
        primary-logs/                    58 per-document logs
        smoke-a/, smoke-b/               4 x 2 determinism outputs each
        smoke-a-logs/, smoke-b-logs/
    historical-baseline/                 2026-09-17 baseline manifests and logs
    tree-manifests/                      hash listings of the execution trees
```

Original directory relationships are preserved. Every file's original absolute
path is recorded in the manifest.

---

## 3. Release classification

The ARPipe repository is public. Every artifact was classified before being
placed here.

| Class | Count | Disposition |
|---|---|---|
| `PUBLIC_SAFE` | 253 | 251 copied here; 2 excluded as superseded drafts |
| `PRIVATE_ARCHIVE_REQUIRED` | 272 | 3 copied to the private tier; 269 excluded as not required for provenance |
| `EXCLUDE` | 68 | raw annual-report PDFs; never copied anywhere |

A credential scan over all 251 published files found **no** API keys, tokens,
passwords, authorization headers or private-key blocks.

Two disclosures were accepted deliberately rather than redacted, because §10 of
the preservation scope forbids altering a historical artifact to make it
publishable:

1. **Absolute local filesystem paths** (`D:\sem_iitk\...`, `C:\Users\hario\...`)
   appear in 149 published files. These are load-bearing provenance, not
   incidental: the `checkout` and `arpipe_file` fields in `profile_base.json`
   and `profile_cand.json` are exactly what demonstrates that base and candidate
   were profiled from two separate export trees. Removing them would destroy the
   evidence. They expose a directory layout and the Windows account name
   `hario`, which is already the public GitHub identity `hariom-s27`.
2. **The author's institutional email** appears three times in
   `r1-final-evidence/provenance-session.txt`, which quotes `git log` output.
   It is already the author and committer email on every commit in this public
   repository, so preserving it discloses nothing new.

If either is unacceptable, the correct remedy is to move the affected file to
the private tier — not to edit it.

---

## 4. Private tier

Three files are `PRIVATE_ARCHIVE_REQUIRED` and are preserved outside this
repository, because they are private conversation content:

- `948b3666-670c-4ce4-951f-ff0d9a9b4562.jsonl` (the R1-FINAL transcript)
- two referenced tool-result files

They are currently held at:

```
D:\sem_iitk\sem9\thesis\_r1_private_archive\r1-final\
```

**This location is a local staging copy, not an approved durable archive.** It
is outside the temporary execution environment, so it survives Temp cleanup, and
its integrity can be re-established from the hashes in the manifest — but it is
a single copy on one machine, and no off-machine archive has been approved by
the author. Until one is, the preservation state of the transcript tier is
`PRESERVED_BUT_NOT_YET_DURABLE`.

The manifest carries an `archive_reference` field for the private tier with
`approved_archive_identifier: null`. Filling that in is the remaining step.

---

## 5. Governing provenance chain

The Track-A chain, with each link classified. Link classifications are carried
over from the R1 Evidence Recovery Report unchanged; preservation does not
upgrade any of them.

```
source/tree
    -> execution tree
        -> execution metadata
            -> input population
                -> profile_base / profile_cand
                    -> comparison.json
                        -> evidence_compact.json
                            -> R1 identity record
```

| Link | Evidence in this archive | Class |
|---|---|---|
| source (base) `ff030d9…` | `scratchpad/evidence_compact.json: base_commit` | EXPLICIT |
| source (candidate) `28a67b6…` | `scratchpad/evidence_compact.json: candidate_commit` | EXPLICIT |
| source -> execution tree | `tree-manifests/base-t04.sha256`, `cand-t04.sha256`; both trees were byte-verified against their Git blobs during recovery (46/46 and 59/59) | EXPLICIT |
| execution tree -> execution metadata | distinct `checkout`, `arpipe_file`, `python`, `seconds` headers in each profile; `profile_*.log` print `sys.path` rooted in each export | EXPLICIT |
| execution metadata -> input population | `scratchpad/universe.json`; manifests committed `23d6228` on 2026-09-18 | EXPLICIT |
| input population -> output | `scratchpad/profile_base.json`, `scratchpad/profile_cand.json` | EXPLICIT |
| output -> comparison | `scratchpad/comparison.json`, `scratchpad/compare_profiles.py` | EXPLICIT |
| comparison -> claim | `scratchpad/evidence_compact.json`, `scratchpad/gen_identity.py`, `scratchpad/identity_template.md` | EXPLICIT |

Links that are **not** EXPLICIT, and are not upgraded here:

| Link | Class | Why it stays there |
|---|---|---|
| `suite_pin.*` -> commit `28a67b6` | TRANSCRIPT-ONLY | neither `suite_pin` file records a commit, and the `r1-final-suite` worktree that produced them was deleted |
| 431-test run at the final tip `383fa79` | TRANSCRIPT-ONLY | no artifact was written |
| 103-test scratch-fixture run | TRANSCRIPT-ONLY | no artifact was written |
| `tools/check_doc_hashes.py` results | TRANSCRIPT-ONLY | no artifact was written |
| negative-test bytes -> blob `6f1185d4…` | INFERRED | the tested files were uncommitted at test time; nothing hashes them at that moment |

Hash identity is not historical provenance. Every §22 hash match recorded here
is a statement that the bytes are unchanged since recovery, not a statement
about where they came from.

---

## 6. Historical qualifications carried forward

These are part of the record and are preserved without reinterpretation. The
full statements are in `docs/identity/R1_EVIDENCE_RECOVERY_REPORT.md`.

1. The **first** universe build located only **100 of 108** PDFs by company
   directory; the remaining 8 were then found in the content-addressed store.
2. Content-addressed PDF resolution was adopted **mid-task**, before any triage
   ran — so the §13 method was adopted during execution, not pre-registered.
3. No document was excluded because of a triage or result outcome; the roster is
   the complete frozen manifest population.
4. The **first negative-test control run failed** (27 failed, 22 passed).
5. A `_working_bytes()` helper was then introduced, relaxing the byte comparison
   to undo a checkout-time LF→CRLF conversion.
6. The post-fix control passed 49/49; `negative_tests.out` is the post-fix run.
7. A **first secondary comparison produced 959 mismatches**, a setup iteration
   resolved before the governing comparison.
8. `script_meta` is **not serialised** by `profile_docs.py`, so it was never
   compared rather than compared-and-identical.
9. Historical **per-page kinds were unavailable** on both sides of the
   58-document comparison (`per_page_kind: UNAVAILABLE_BOTH` ×58,
   `fully_comparable_documents: 0`).
10. The four-document determinism result is a 4-document, 2-run pipeline result.
    **It is not Track-A evidence.**
11. The three-run agreement on `INE00LO01017_2025` was tested as **JSON-object
    equality**, not byte equality; the record's "byte-identical `result.json`"
    overstates the test performed. (Preservation hashing does show
    `out-run-a/result.json` and `out-run-b/result.json` are byte-identical to
    each other — `e186824781e7…` — but the comparison against the earlier
    session's run #1 remains an object-equality test, and that is what the
    qualification is about.)
12. The `r1-final-suite` worktree that produced `suite_pin.*` was **deleted**.
13. The executed 2026-09-17 `arpipe/patterns.py` bytes are **unrecoverable**.
14. **No historical Tesseract version** is recorded anywhere, so the §17 OCR-drift
    question stays NOT VERIFIABLE.
15. **Track B remains UNRESOLVED / DEFERRED.**
16. **C2 remains CONDITIONAL.**

---

## 7. Verifying this archive

```
# every artifact except the manifest itself
python - <<'EOF'
import hashlib, json, pathlib
root = pathlib.Path("docs/identity/evidence/r1-final")
m = json.loads((root / "r1-final-evidence-manifest.json").read_text(encoding="utf-8"))
bad = [a["archive_relative_path"] for a in m["artifacts"]
       if a["tier"] == "PUBLIC"
       and hashlib.sha256((root / a["archive_relative_path"]).read_bytes()).hexdigest() != a["sha256"]]
print("mismatches:", bad)
EOF

# the manifest itself
sha256sum docs/identity/evidence/r1-final/r1-final-evidence-manifest.json
cat      docs/identity/evidence/r1-final/r1-final-evidence-manifest.sha256
```

Related records: `docs/identity/R1_EVIDENCE_PRESERVATION_01.md` (the §22 coverage
addendum) and `docs/identity/R1_EVIDENCE_RECOVERY_REPORT.md` (the forensic
recovery record this archive implements).
