# R1 Evidence Preservation 01 — durable coverage addendum

Date: 2026-09-26
Branch: `r1-final`
Identity commit: `383fa79228d48bf39401936090b9cbe9c5509e95`
Archive: `docs/identity/evidence/r1-final/`

## Purpose and standing

`RUNNABLE_IDENTITY_v1.md` §22 lists nine evidence files with SHA-256. That record
is **historical and unchanged**. This addendum does not revise it, does not add
entries to it, and must not be read as though the artifacts listed below had
been hash-listed originally. They were not. §22 said the evidence was "retained
outside the repository, under this session's scratchpad", and at the time that
was true and was the whole of the record.

This addendum exists because the R1 Evidence Recovery task established that a
larger set of artifacts is required to make the recovered provenance chain
auditable, and because the evidence has now been copied out of the temporary
directories it was sitting in. Its job is to extend *durable coverage*, not to
rewrite history.

**Preservation is not reproduction.** No R1 execution was repeated. Nothing here
is a new scientific result.

## 1. What §22 already covered

Nine files, all re-verified byte-exact during recovery and again during
preservation: `universe.json`, `profile_base.json`, `profile_cand.json`,
`comparison.json`, `evidence_compact.json`, `suite_pin.txt`, `suite_pin.xml`,
`negative_tests.out`, `historical-comparison.json`.

Their §22 hashes are unchanged and are reproduced in the archive manifest.

## 2. Extended durable coverage

The following were **not** hash-listed in §22 and are now covered.

### 2.1 Determinism evidence

| Artifact | Bytes | SHA-256 |
|---|---|---|
| `r1-final-evidence/determinism-comparison.json` | 2,261 | `142990c9054b10b18cb895497e28ed7669f9a969d4af1c83e8627ba301df7bb8` |
| `r1-final-evidence/preregistration.json` | 2,858 | `e613eb85dedef358ba1eb1b5812744c70150829aeb79fc2cbe1898a17a7bb95f` |
| `r1-final-evidence/preregistration.txt` | 2,958 | `477ff7d8cda9398bb1c127a3e20da010187a5f3da2c2b66e771d00d3beb6a1e1` |
| `r1-final-evidence/smoke-a-batch.json` | 64 | see manifest |
| `r1-final-evidence/smoke-b-batch.json` | 64 | see manifest |
| `r1-final-evidence/smoke-a/<doc>/result.json`, `execution.json` | 4 × 2 | see manifest |
| `r1-final-evidence/smoke-b/<doc>/result.json`, `execution.json` | 4 × 2 | see manifest |
| `r1-final-evidence/smoke-a-logs/`, `smoke-b-logs/` | 4 + 4 | see manifest |

Where a row says "see manifest", the per-file SHA-256 is recorded in
`docs/identity/evidence/r1-final/r1-final-evidence-manifest.json`, which is the
authoritative hash record for every preserved artifact. Nothing is left unhashed;
values are quoted in these tables only where a reader is likely to want them
inline, and are never restated from prose without being recomputed from bytes.

The determinism limitation is unchanged and is restated, not softened: this is a
**4-document, 2-run pipeline** result with `per_page_kind: UNAVAILABLE_BOTH` ×4
and `fully_comparable_documents: 0`. **It is not Track-A evidence.**

### 2.2 `run-a` / `run-b` and their outputs

Required by the recovery chain for §17's three-run agreement on
`INE00LO01017_2025`.

| Artifact | Bytes | SHA-256 |
|---|---|---|
| `scratchpad/run-a.log` | 1,183 | `50b74cc5424f2fead0053a9cbb65f9f8a9aacb5c7c2e9eda2e0139a1e936555d` |
| `scratchpad/run-b.log` | 1,183 | `d551fd14bfce3cae5713f72374dc5080e5538cb639f7e2fafbbef20c64c06cf8` |
| `scratchpad/out-run-a/result.json` | 8,355 | `e186824781e75f532899ac75d1fbc65fcb3fc3c19b732c8f258548753a00dc93` |
| `scratchpad/out-run-b/result.json` | 8,355 | `e186824781e75f532899ac75d1fbc65fcb3fc3c19b732c8f258548753a00dc93` |
| `scratchpad/out-run-a/summary.json` | 837 | `8078aeed01ae6f0da9ec9ea3e8c179229ad11e2c9950274198dcccca6b7b962b` |
| `scratchpad/out-run-b/summary.json` | 837 | `fb40ecac5cc157dee68fbabc2c942f4251305412e2a6452ea7615556b8939f36` |
| `scratchpad/run_pipeline_doc.py` | 3,390 | `c0f2dee0eb7911ffa16abefd9eaca88afce4b01c1409aaa297c9062c44c2a79d` |

The `run-a/` and `run-b/` execution trees themselves are **not** copied into the
archive. Both are `git archive` exports of `28a67b63d890d8407fa9738a71ae37ad63148b73`
(`run-b` additionally holds a 70 MB built fixtures directory), and both were
byte-verified 59/59 against that commit during recovery. Durable coverage is
provided instead by per-file SHA-256 listings:
`docs/identity/evidence/r1-final/tree-manifests/run-a.sha256`
(`b16efc21e7b13263a9a77c2d11c65cf2e884a469e7f03905dce7a1a7fcfc988e`) and
`tree-manifests/run-b.sha256`
(`52848e29071076c7893852c1ce0e88a04eac1795f387a91c6b5822d74b11017d`).

**A qualification must not be lost here.** The two `result.json` files are
byte-identical to each other — that is a direct observation from preservation
hashing. It does **not** upgrade §17's three-run claim. The comparison against
the earlier session's run #1 was a **JSON-object equality** test, not a byte
comparison, and the R1 record's phrase "byte-identical `result.json`" still
overstates the test that was actually performed across all three runs.

### 2.3 Base and candidate execution trees

| Tree | Commit | Files | Listing SHA-256 |
|---|---|---|---|
| `base-t04/` | `ff030d97c13c8a2a977521bf91be2aca0cbf3034` | 76 | `34e08bf55c22fda2618a89540bf61524d08de67bdc265692db16be8fbaf7950e` |
| `cand-t04/` | `28a67b63d890d8407fa9738a71ae37ad63148b73` | 89 | `623ddfaf9477b66456ca04debbf1c9b39e8d58c07400b6077e45474a651139a4` |
| `run-a/` | `28a67b63d890d8407fa9738a71ae37ad63148b73` | 90 | `b16efc21e7b13263a9a77c2d11c65cf2e884a469e7f03905dce7a1a7fcfc988e` |
| `run-b/` | `28a67b63d890d8407fa9738a71ae37ad63148b73` | 103 | `52848e29071076c7893852c1ce0e88a04eac1795f387a91c6b5822d74b11017d` |

These listings are **derivative preservation metadata**, created by this task.
They are not R1-FINAL artifacts and are labelled as such in their own headers.

### 2.4 Historical 58-document comparison inputs and outputs

| Artifact | Bytes | SHA-256 |
|---|---|---|
| `r1-final-evidence/fit-inputs.json` | 3,986,960 | `831bd3e712dbf53ff711e1bae3eeabcdc40ece1f55f3f30f2eda701ba96fae77` |
| `r1-final-evidence/primary-batch.json` | 65 | `aed9cb31a408b13108ba4a86db04ea2a29d3e6cf59a3f3098f286a88ae659c8f` |
| `r1-final-evidence/compare_outputs.py` | 5,989 | `3e97dc51b92e93f9ac173507387603a333489d93e732fa4b112a5ffd504b2662` |
| `r1-final-evidence/run_document.py` | 3,153 | `2248c6b3207f84825147312a2be1ba67b1d6cb34bed198b3fa7e3f6b6256787a` |
| `r1-final-evidence/run_batch.py` | 1,374 | `8865822942cebb327f88addb91b1a03180402548734df580bf0a39348041bdc0` |
| `r1-final-evidence/prepare_run.py` | 2,689 | `ce8356613b231d9f8e4ffba86da5a3a5d01ac475de8b8e137b49e29301ae0e30` |
| `r1-final-evidence/primary/<doc>/result.json`, `execution.json` | 58 × 2 | see manifest |
| `r1-final-evidence/primary-logs/*.log` | 58 | see manifest |
| `historical-baseline/pm1_baseline_run/manifest.jsonl` | 1,312,546 | `a2d0243c7cd1b282ed002503c40891b6c9e9ef0a11fdb8741c792d5516fe370c` |
| `historical-baseline/pm1_after_run/manifest.jsonl` | 1,548,426 | `5d8bed2aeb0af4c16e1bb86b61756b579eb4e1bdd43e9df47ccf79b678993552` |
| `historical-baseline/pm1_baseline_run.log` | 7,967 | `27bd26944101ea35298b45c128771da4612b763b4026fc8d4d69cf92c255ac4e` |
| `historical-baseline/pm1_after_run.log` | 7,967 | `a062d1827005e089920f644513dfcbe0e363baf1f99185575603eccd639cea7f` |

Unchanged qualification: historical per-page kinds were never serialised, so
`per_page_kind` is `UNAVAILABLE_BOTH` ×58 and `fully_comparable_documents: 0`.
The "57/58 exact" figure rests on six comparable fields, not seven.

### 2.5 Generating scripts and run metadata for the governing comparison

| Artifact | Bytes | SHA-256 |
|---|---|---|
| `scratchpad/build_universe.py` | 3,736 | `6af0a519a45e31b9f32d82075c377650e028da87f82dfbe30c273edf63b42745` |
| `scratchpad/profile_docs.py` | 3,500 | `41804798fcd389d63e1004ad810769d2754fe23a97c0015f99a85a1d5f394bbf` |
| `scratchpad/compare_profiles.py` | 8,045 | `fcd4b158cda62c0a42fc2286500dae6b2ffc796d997927479839c5f42aa3c163` |
| `scratchpad/gen_identity.py` | 4,085 | `5ff6ccee268ff85108e6748249db67423bb31c57344a7a510bfc8e5306f55495` |
| `scratchpad/identity_template.md` | 24,104 | `8c14153e2c4862b201d91aa06a03269cfd1fbd0f0fe8e658143222fde128dd2a` |
| `scratchpad/identity_universe.json` | 9,561 | `ff99ed2bfb5ce8880c5dafd75fb90a2896cc216f6cad5268324bbd891f011471` |
| `scratchpad/environment_final.txt` | 4,232 | `b732263472d3e6abe30a3291fd6fe54564f0691925ad267143eef6c833a7f4bf` |
| `scratchpad/profile_base.log` | 7,472 | `c908e4875c38d13cb440e27f259ec91521b4ba5005c7dfeb8ac63b36c5b6ac28` |
| `scratchpad/profile_cand.log` | 7,474 | `8cd12ffc1d340f84223b974615076d99d0a3a132d9f35ecf95500686dc6292d1` |

`profile_docs.py` is the file that **excludes `script_meta` from serialisation**.
`script_meta` was therefore never compared, rather than compared and found
identical. §13's phrasing is accurate only under that reading.

### 2.6 Negative-test evidence

| Artifact | Bytes | SHA-256 |
|---|---|---|
| `scratchpad/negative_tests.sh` | 6,301 | `edff8050baea041cea5a43a91640ebed2df6bd21d2c71b2e4f6aa17499f781b9` |

`negative_tests.out` (§22-listed) is the **post-fix** run. The first control run
failed 27/22; `_working_bytes()` was then introduced, relaxing the byte
comparison to undo a checkout-time LF→CRLF conversion, after which the control
passed 49/49. The file-byte binding to blob `6f1185d4…` remains **INFERRED** and
is not upgraded by this preservation.

### 2.7 Test-suite evidence

| Artifact | Bytes | SHA-256 |
|---|---|---|
| `r1-final-evidence/pytest-full.xml` | 64,618 | `437dfbdf992df953d264ecf9493c2bb0c793a0ddf4a25552bad16a7d7f49731a` |
| `r1-final-evidence/pytest-exit.txt` | 1 | `6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b` |

`pytest-full.xml` is the **older 382-test execution** (`tests="382" failures="5"`,
exit code 1). It is preserved as what it is. It is **not** the final 431-test
result and must not be relabelled as such; the 431-test result is
`suite_pin.txt` / `suite_pin.xml`, already §22-listed.

### 2.8 Identity and environment captures

`r1-final-evidence/identityMaterial0.txt` (`383de3ef…`),
`identityMaterial1.txt` (`1f3370e0…`), `environment0.txt` (`e2bf31ad…`),
`environment1.txt` (`74238926…`), `provenance-session.txt` (`be5c3cc8…`),
`A1Commit.txt` … `A5AndSmokeCommit.txt`. Full values in the manifest.

### 2.9 Transcript

`948b3666-670c-4ce4-951f-ff0d9a9b4562.jsonl`, 3,388,079 bytes, 915 lines,
SHA-256 `9352b967c0c6dc4d30b850420b2ac92da1773caf4113c6578fd9642e8055d217`,
plus two referenced tool-result files.

Classified `PRIVATE_ARCHIVE_REQUIRED` (private conversation content) and held
**outside this repository**. Only its hash, inventory and provenance are
recorded here. See §4 below.

It remains the sole evidence for three claims — the 431-test run at the final
tip `383fa79`, the 103-test scratch-fixture run, and the document-hash checks.
Preserving it does not convert TRANSCRIPT-ONLY evidence into artifact evidence.

## 3. Coverage that is still absent

Recorded so the gaps stay visible, not to suggest they have been closed:

- The `r1-final-suite` worktree that produced `suite_pin.*` was deleted and is
  `NOT_RECOVERABLE`. Its `suite_pin.*` → commit binding stays TRANSCRIPT-ONLY.
- The session that produced `r1-final-evidence/` left **no transcript**. Its
  command history is gone.
- The executed 2026-09-17 `arpipe/patterns.py` bytes are `NOT_RECOVERABLE`.
- No historical Tesseract version is recorded anywhere; §17's OCR-drift question
  stays NOT VERIFIABLE.
- The negative-test file-byte binding stays INFERRED.

## 4. Preservation state

| Tier | Contents | State |
|---|---|---|
| Public, versioned | 251 files under `docs/identity/evidence/r1-final/` | `PRESERVED_AND_VERSIONED` once this commit exists |
| Private | transcript + 2 tool-result files, 3,477,325 bytes | `PRESERVED_BUT_NOT_YET_DURABLE` |

The private tier is currently a local staging copy at
`D:\sem_iitk\sem9\thesis\_r1_private_archive\r1-final\`. It is outside the
temporary execution environment and its integrity is re-establishable from the
manifest hashes, but it is a single copy on one machine and **no off-machine
archive has been approved by the author**. The manifest carries
`archive_reference.approved_archive_identifier: null` for this tier.

Because the transcript is load-bearing for three recovered claims, the
**overall** preservation state is `PRESERVED_BUT_NOT_YET_DURABLE` until that
field is filled in.

## 5. Verification performed

| Measure | Result |
|---|---|
| source files snapshotted | 593 |
| files copied | 254 |
| files verified | 254 |
| hash mismatches | 0 |
| source changes during preservation | 0 |
| missing files | 0 |
| unexpected files | 0 |
| corpus / HOLDOUT contamination in the public archive | 0 |
| §22 key hashes re-verified against source bytes | 14 / 14 MATCH |

No original byte was altered. No line ending was normalised, no JSON
reformatted, no path rewritten, no artifact renamed, no historical artifact
redacted.

## 6. Administrative status

Current author ratification dated 2026-09-26 is recorded in
`docs/governance/AUTHOR_RATIFICATION_2026-09-26.md`. It authorizes this later
administrative disposition without changing the historical preservation facts
or upgrading the private preservation tier.

| Item | Current authorized record |
|---|---|
| Claim A | `REPRODUCED` |
| Claim B | `REPRODUCED_WITH_QUALIFICATION` |
| Claim C | `REPRODUCED` |
| Reproduction evidence | `docs/identity/evidence/r1-final/claim-reproduction-pa/` |
| Evidence anchor | `53dcab40c374b499637ad3f68596549540ef1c42` |
| Private transcript | `SUPPLEMENTARY` |
| Private-copy status | `not yet` |
| Administrative state | `CLOSED` |

Claim B's qualification is kept exactly:

> The historical transcript identifies this fixture build and the two test
> files (lines 703/708), and the later preservation manifest identifies the
> surviving bytes. No contemporaneous per-fixture hash was recorded during the
> historical execution. That temporal provenance limit remains. Current test
> files were read from the recovered tree to use their unchanged hard-coded
> sibling fixture path; all production imports were independently recorded
> inside the pinned worktree. The original execution used production imports
> from its `run-b` Git export.

`CLOSED` means only that the authorized R1 administrative/reproduction task is
closed. Private-copy status independently remains `not yet`: no approved
private archive is claimed, the transcript is not claimed to be durably
archived, and the historical `PRESERVED_BUT_NOT_YET_DURABLE` classification is
not upgraded. Administrative closure is not scientific completion.
