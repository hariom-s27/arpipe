# Main drift diagnosis — 2026-09-27

**Verdict: `DRIFT_DIAG_DONE` (report only).** This is a read-only diagnosis of the fetched `origin/main` ref against the Phase 5 A.1 code line. No source, test, configuration, dataset, or HOLDOUT material was changed. The author-fetched refs were used because this linked worktree's Git directory is outside the writable sandbox. No fetch, worktree, commit, or push was attempted after that constraint was supplied.

## Summary table

“Changes output?” covers extraction results **and the upstream acquisition/universe that determines which documents can be extracted**. `UNSURE` means the diff does not prove output equivalence in every condition. Test references are to the full `origin/main` archive run in Q5; a pass means that file's named tests did not appear in its failure list, not that output equivalence was established.

| File | Changed by | Changes output? Y/N/UNSURE | Tests |
|---|---|---|---|
| `arpipe/cli.py` | `5649772` via PR #8 (`3cffb05`) | UNSURE | R1 fetch telemetry tests did not fail; acquisition equivalence tested only in their mocked cases. |
| `arpipe/fetch.py` | `5649772` via PR #8 | UNSURE | R1 fetch telemetry tests did not fail. |
| `arpipe/models.py` | `f574f1e` direct main; PR #27 merge `e32f0eb` | UNSURE | R1 authorized-byte test for this file **failed** on main. |
| `arpipe/telemetry.py` | `5649772` via PR #8 | N, sidecar only | R1 fetch telemetry tests did not fail. |
| `arpipe/tests/test_pm2_2_threshold_study.py` | `6d91dfa` via PR #3 (`6362eb5`) | N | Its tests did not fail. |
| `arpipe/tests/test_pm2_orphan_native_vs_ocr.py` | `f53f9cd` via PR #6 (`7d37f18`) | N | Its tests did not fail. |
| `arpipe/tests/test_pm3_scan_quality.py` | `ec48e64` via PR #1 (`275cec4`) | N | Its tests did not fail. |
| `arpipe/tests/test_pm4_annexure_audit.py` | `e387d6b` via PR #4 (`086e5ec`) | N | `test_reproducibility_run_twice` failed on a write into `reports/` in the archive environment. |
| `arpipe/tests/test_r1_fetch_telemetry.py` | `5649772` via PR #8 | N | Its tests did not fail. |
| `arpipe/triage.py` | `9480475` direct main | N for this hunk | R1 authorized-byte test for this file **failed** on main. |
| `arpipe/universe.py` | `ac0301d` direct main | **Y** | No universe test appeared in the failure list; the changed exchange rule needs a targeted equivalence check. |

## Q1 — Commit identity and ancestry

`git rev-parse origin/main origin/phase5-a1 28a67b63d890d8407fa9738a71ae37ad63148b73 e143222` and `git log -1 --format="%H | %aI | %cI | %s" <ref>` returned the following full hashes and dates. Author and committer dates were equal for each row.

| Ref | Commit | Date (UTC offset +05:30) | Subject |
|---|---|---|---|
| `origin/main` | `2fb2718c5b8f3f087ee24f742816963d79d3f9bd` | `2026-09-27T19:19:33+05:30` | Merge pull request #32 from hariom-s27/phase5-b-intake |
| `origin/phase5-a1` | `e1803fcea7ebc7ee5f8c4acebf76333c8b8d2650` | `2026-09-27T05:14:06+05:30` | P5-A.1: revise Gold method to v0.1 |
| R1 pin | `28a67b63d890d8407fa9738a71ae37ad63148b73` | `2026-09-26T01:45:43+05:30` | test(r1): enforce T0.4 Amendment 01 and register strict expected failures |
| `e143222` | `e1432222451ed5cb7c455436545e06e204c2269f` | `2026-09-26T20:43:19+05:30` | docs(phase5): draft gold method package |

`git merge-base origin/main origin/phase5-a1` returned `e1803fcea7ebc7ee5f8c4acebf76333c8b8d2650`; `git merge-base origin/main 28a67b63d890d8407fa9738a71ae37ad63148b73` returned `28a67b63d890d8407fa9738a71ae37ad63148b73`. Thus both comparison commits are ancestors of fetched main.

## Q2 — Which `arpipe/` files differ and how they reached main

`git diff --stat e1803fc origin/main -- arpipe/` returned:

```text
 arpipe/cli.py                                 |   6 +-
 arpipe/fetch.py                               |  96 ++++-
 arpipe/models.py                              |   6 +-
 arpipe/telemetry.py                           | 263 ++++++++++++++
 arpipe/tests/test_pm2_2_threshold_study.py    | 205 +++++++++++
 arpipe/tests/test_pm2_orphan_native_vs_ocr.py | 281 +++++++++++++++
 arpipe/tests/test_pm3_scan_quality.py         | 405 +++++++++++++++++++++
 arpipe/tests/test_pm4_annexure_audit.py       | 149 ++++++++
 arpipe/tests/test_r1_fetch_telemetry.py       | 499 ++++++++++++++++++++++++++
 arpipe/triage.py                              |   2 +-
 arpipe/universe.py                            | 209 ++---------
 11 files changed, 1938 insertions(+), 183 deletions(-)
```

`git diff --stat 28a67b6 origin/main -- arpipe/` returned the **same eleven file lines and totals**. `git log --oneline e1803fc..origin/main -- <file>` was run for each file. The introducing commits and carrying merges are in the summary table. In detail, the path log for `cli.py` also prints PR #8's merge `3cffb05`; the path logs for `fetch.py`, `telemetry.py`, and the R1 telemetry test print `5649772`. `models.py` prints `f574f1e` and merge `e32f0eb`; `triage.py` prints `9480475`; `universe.py` prints `ac0301d`. The four P-M path logs print `6d91dfa`, `f53f9cd`, `ec48e64`, and `e387d6b`, respectively. `git log --first-parent -m --format="%h %s" --name-only e1803fc..origin/main -- arpipe/` confirms the listed carrying PR merges and the three direct main fixes. Earlier first-parent changes to `cli.py` in PR #1 do not account for its final net hunk; the final net hunk is PR #8 telemetry.

## Q3 — Nature and output relevance of each net change

These descriptions come from `git diff --no-ext-diff --unified=3 e1803fc origin/main -- arpipe/<file>` and, for new tests, `git show origin/main:<file>` test declarations.

| File | Nature of the net diff |
|---|---|
| `cli.py` | New optional `fetch --telemetry-path` flag constructs a telemetry writer and passes it to `fetch_one`. No extraction command hunk changes; with the flag enabled, acquisition now has an extra operation, so universal output equivalence is unproven. |
| `fetch.py` | Adds per-attempt failure telemetry for retryable HTTP failures, exceptions, bad ZIPs, and failed PDF repair; preserves the visible success and retry branches in the diff. The added classifier/emission work in exception paths makes acquisition behavior an `UNSURE` risk outside tested cases. |
| `models.py` | Replaces `datetime.UTC` with `datetime.timezone.utc` in two timestamp defaults for Python 3.10 compatibility and widens the `ExtractionResult.toc_offset` annotation to allow `None`. On compatible runtimes the timestamp value/default dictionary is unchanged; cross-version runnable behavior differs. |
| `telemetry.py` | New JSONL failure record, URL redaction, error classification, and non-raising writer. It is a sidecar to acquisition, with no direct span or result calculation. |
| `tests/test_pm2_2_threshold_study.py` | Test-only threshold, denominator, provenance, repeatability, and production immutability checks. |
| `tests/test_pm2_orphan_native_vs_ocr.py` | Test-only checks for native/OCR provenance separation, unknown cases, persisted metric use, statistics, and mutation avoidance. |
| `tests/test_pm3_scan_quality.py` | Test-only raster, DPI, skew, contrast, noise, blur, aggregation, and immutability checks. |
| `tests/test_pm4_annexure_audit.py` | Test-only audit math, population, split hash, reproducibility, and immutability checks. |
| `tests/test_r1_fetch_telemetry.py` | Test-only redaction, classification, mocked pre/post acquisition equivalence, writer-failure, and retry checks. |
| `triage.py` | Adds `Any` to a `typing` import to resolve Flake8 F821. No classification, OCR routing, or page-profile logic changes in this net hunk; its bytes do differ from the R1 authorized file. |
| `universe.py` | Mostly a condensed refactor plus missing `sys`/`Any` imports, but `collapse_universe` changes the merged `exchange` rule. The old rule returned `both` if separate group members reported `nse` and `bse`; the new rule can return `nse` where those reports exist but merged symbol/scrip fields do not both exist. That can change universe output and downstream document selection. |

The direct output-risk flags are therefore `universe.py` (**Y**) and the acquisition/metadata paths `cli.py`, `fetch.py`, and `models.py` (**UNSURE**). The `triage.py` path is important for byte identity but its sole net hunk is an import. These are judgments from the diff, not a proof of behavioral equivalence.

## Q4 — Phase 5 A.1 versus the R1 pin

`git diff --stat 28a67b6 e1803fc -- arpipe/` returned **no output**. `git rev-parse 28a67b6:arpipe e1803fc:arpipe origin/main:arpipe` returned, in order, `f6475922f2a6837c7e6a86cefb5fb30aef602e69`, the same `f6475922f2a6837c7e6a86cefb5fb30aef602e69`, and `d21b8d30ffc78a9990a6efb6f895d767582556da`. Thus the tracked `arpipe/` tree is byte-identical between R1 and A.1, but main's is different.

This does **not** make the whole runnable identity byte-identical: `git diff --stat 28a67b6 e1803fc -- configs/` reports `configs/phase2_1/semantic_fixtures.json | 43 ++++++++++++++++++++++++++++++++-` (42 insertions, 1 deletion), while `git diff --stat e1803fc origin/main -- configs/` is empty. The added configuration block records B decisions with `execution_authorized: false`; it is outside this `arpipe/` comparison. The R1 identity document pins both `arpipe/` and `configs/` (see Q7).

## Q5 — Full pytest comparison

The branch baseline command was `python -m pytest -q -p no:cacheprovider --basetemp=.pytest_tmp_run` from this worktree at `e1803fc`. Output: **`425 passed, 17 skipped, 3 xfailed in 125.06s`**, exit 0. There were no failed tests. `git status --short` afterward was empty. The temp directory was removed.

Because Git writes to the external Git directory are disallowed, `origin/main` was tested from an ignored archive instead of a detached worktree. PowerShell's binary `git archive origin/main | tar -x -C .pytest_tmp_main` pipeline produced a damaged tar stream; that partial extraction was removed. The successful extraction used `git archive --format=tar --output=.pytest_tmp_main/snapshot.tar origin/main` followed by `tar -xf .pytest_tmp_main/snapshot.tar -C .pytest_tmp_main`, then removed the tar file. The first pytest attempt placed `--basetemp` inside the archive and failed to create that directory. The completed full comparison used `python -m pytest -q -p no:cacheprovider --basetemp=../.pytest_tmp_main_run --tb=line` from `.pytest_tmp_main`.

Corrected archive-run output: **`12 failed, 495 passed, 17 skipped in 42.20s`**, exit 1. The failed tests were:

```text
arpipe/tests/test_pm4_annexure_audit.py::test_reproducibility_run_twice
tests/t0_1/test_audit_corpus_gaps.py::TestCorpusGapAudit::test_single_file_mapping_and_sha
tests/t0_1/test_audit_corpus_gaps.py::TestCorpusGapAudit::test_total_page_count_assertion
tests/t0_4/test_t0_4_closure_record.py::test_record_is_reproduced_byte_for_byte_from_the_audited_commit
tests/t0_4/test_t0_4_closure_record.py::test_frozen_inputs_are_unchanged_since_the_audited_commit
tests/t0_4/test_t0_4_final_closure.py::test_every_selected_page_has_complete_derivable_provenance
tests/t0_4/test_t0_4_final_closure.py::test_provenance_fails_closed_on_tampered_rank_or_source_hash
tests/t0_4/test_t0_4_setup.py::test_frozen_corpus_and_history_are_unchanged
tests/t0_4/test_t0_4_setup.py::test_fail_closed_setup_audit_passes
tests/test_t0_4_amendment_01.py::test_arpipe_change_set_is_exactly_the_four_authorized_paths
tests/test_t0_4_amendment_01.py::test_authorized_file_differs_from_base_only_by_its_authorized_hunks[arpipe/models.py]
tests/test_t0_4_amendment_01.py::test_authorized_file_differs_from_base_only_by_its_authorized_hunks[arpipe/triage.py]
```

**Interpretation limit:** The archive has no `.git` metadata. Git-history and `HEAD`-based guards therefore ran against the enclosing A.1 worktree or lacked archive provenance, so their failures cannot be read as a clean-checkout main result. The two T0.1 failures reference a missing external `live_store` PDF; the P-M4 failure is a denied write into the extracted archive's `reports/`. Three original T0.4 strict expected failures became `XPASS(strict)` on this run. The two per-file authorized-byte failures for `models.py` and `triage.py` directly reflect main's changed bytes. This comparison diagnoses drift but does not establish a clean, isolated main test pass rate. Neither archive temp folder remains.

## Q6 — Merge/PR history in the requested range

`git log --merges --oneline e143222..origin/main` returned the following PR merges, with the branch/topic supplied by each merge subject. The range is **topological**, not a chronological “after 2026-09-26 20:43” filter: `git log --merges --format="%h %cI %s" e143222..origin/main` dates PRs #1–#29 before `e143222`'s timestamp, and PRs #30–#32 after it. They appear because the Phase 5 draft commit did not contain those earlier main-line merges. This distinction matters when saying “since e143222.”

| Merge | PR | Merged branch/topic |
|---|---:|---|
| `275cec4` | #1 | `pm3-scan-quality` |
| `9c64c3c` | #2 | `pb2-p1-recovery` |
| `6362eb5` | #3 | `pm2.2-threshold-sensitivity` |
| `086e5ec` | #4 | `pm4-annexure-audit` |
| `7d37f18` | #6 | `pm2-native-vs-ocr-orphan` |
| `ea896c9` | #5 | `pm5-coverage-funnel` |
| `3cffb05` | #8 | `pr1x-historical-audit` |
| `f94c3f8` | #9 | `r1-telemetry-analysis` |
| `1a5012d` | #10 | `t0.3a-document-coverage` |
| `57a0fb0` | #11 | `t0.4-routing-clarification` |
| `a2990db` | #13 | `phase1-frozen-foundation-verification` |
| `9e37506` | #14 | `t0.4-routing-clarification` |
| `40e15f2` | #15 | `t0.4-gold-method-research` |
| `dcaa814` | #16 | `phase2-research-integration` |
| `a9a033b` | #17 | `phase2.1-foundation-normalization` |
| `52ff2fe` | #18 | `t0.4-gold` |
| `e44073f` | #19 | `phase2.1-foundation-normalization` |
| `637904a` | #20 | `phase3-claims-scope` |
| `b34922e` | #21 | `phase4-b1-b8` |
| `5924f33` | #22 | `lf-fixture-suite` |
| `8abe696` | #23 | `pc0-diagnostic-base` |
| `271b6a0` | #24 | `pc0r-acquisition-pilot` |
| `2673d1e` | #25 | `pc0-coverage-diag` |
| `e32f0eb` | #27 | `r1-resume-2-final` |
| `47464f4` | #26 | `t04-guard-forensics` |
| `4accea5` | #28 | `r1-final` |
| `a6eefe7` | #29 | `governance-closeout` |
| `170fc8d` | #30 | `phase5-gold-method-v01` |
| `b31855c` | #31 | `phase5-a1` |
| `2fb2718` | #32 | `phase5-b-intake` |

The merge titles show branch topics, not a complete file inventory. The first-parent path log cited in Q2 identifies the merges that actually carried `arpipe/` changes. It has no `arpipe/` entry for PRs #30–#32, including the A.1 merge #31: that merge did not replace main's already drifted code. The same log shows direct main commits `ac0301d`, `f574f1e`, and `9480475` that are absent from a merges-only list.

## Q7 — HOLDOUT identity and risk

The operative records say:

> `docs/identity/RUNNABLE_IDENTITY_v1.md:15`: | Tip SHA | `28a67b63d890d8407fa9738a71ae37ad63148b73` |
>
> `docs/identity/RUNNABLE_IDENTITY_v1.md:20`: | `arpipe/` tree at the tip | `f6475922f2a6837c7e6a86cefb5fb30aef602e69` |
>
> `docs/identity/RUNNABLE_IDENTITY_v1.md:21`: | `configs/` tree at the tip | `4b56d25b28c18132cb1fcf4f847e4582a195036a` |
>
> `docs/identity/RUNNABLE_IDENTITY_v1.md:23`: “The identity is pinned at the tip above.”
>
> `docs/identity/RUNNABLE_IDENTITY_v1.md:525`: “a runnable reconstruction of the As-Is provider half on the Phase-4 consumers.”
>
> `docs/governance/CURRENT_DECISIONS.md:25` (Q1b): “After final system freeze, make no code, configuration, threshold, pattern or model change before the single HOLDOUT scoring run. A later change is a separately evaluated version. Pre-freeze development uses FIT and VALIDATION only.”
>
> `docs/governance/CURRENT_DECISIONS.md:29` (Q5): “Freeze and push governance; freeze and push the system; run HOLDOUT once; hash-seal unopened outputs; push/give hashes to seal holder; create blind Gold; freeze Gold; score once; publish. Rerun only after infrastructure failure producing no output, with failure log.”
>
> `docs/governance/CURRENT_DECISIONS.md:43` (As-Is): “No 2026-09-17 baseline is adopted. R1 at `28a67b63d890d8407fa9738a71ae37ad63148b73` is runnable identity, not a thesis comparator. Trigger: Phase 10 experiment marked KEEP.”

The required HOLDOUT **execution** identity is the specifically frozen and pushed system version under Q1b/Q5; the cited decisions do not say that this future freeze has already occurred or that the R1 pin itself is irrevocably the final HOLDOUT system. R1 is the current documented runnable identity, and A.1 shares its `arpipe/` tree but differs in a root `configs/` fixture. `origin/main` has a different `arpipe/` tree from both, including the universe behavior change, and so cannot be silently substituted for the pinned/frozen version. `git diff --stat e1803fc origin/main -- docs/governance/CURRENT_DECISIONS.md docs/identity/RUNNABLE_IDENTITY_v1.md` was empty: main does not change or explicitly contradict the policy text. Its code drift creates an identity decision that must be resolved **before** a future freeze; if introduced **after** freeze, Q1b calls it a separately evaluated version. No HOLDOUT row or PDF was inspected.

## Recommendation options

Author decision required; this report does not select an option.

1. Restore main's `arpipe/` to the chosen Phase 5 code tree, and record a new exact frozen system identity after checking root `configs/` and tests.
2. Keep main as a separate development line; freeze and run HOLDOUT only from an explicitly identified Phase 5 system commit, while evaluating main separately.
3. Cherry-pick selected main changes onto the Phase 5 line after targeted output-equivalence review (especially `universe.py`), then freeze the resulting exact tree as a new version.

## Final checks and handoff

The correction disallows Git writes, so this report is deliberately **uncommitted**. Final branch command `python -m pytest -q -p no:cacheprovider --basetemp=.pytest_tmp_run` returned **`425 passed, 17 skipped, 3 xfailed in 48.32s`**, exit 0: the same pass/skip/xfail counts as baseline, with no new tests or failures. The final pytest temp directory was removed.

`git diff --name-only e1803fc` cannot list an untracked report; final `git status --short` shows only `?? docs/decisions/MAIN_DRIFT_DIAGNOSIS_2026-09-27.md`. `git diff --check` returned no output, exit 0; `git diff --no-index --check -- /dev/null <report>` emitted no whitespace diagnostics (its exit 1 means the new file differs from `/dev/null`). The present HEAD is `e1803fcea7ebc7ee5f8c4acebf76333c8b8d2650`; there is no new commit hash or remote verification from this session. The temporary archive and pytest directories were removed.

After review, the author can run:

```powershell
git add docs/decisions/MAIN_DRIFT_DIAGNOSIS_2026-09-27.md
git commit -m "Diagnosis: origin/main vs Phase 5 code line (read-only report)"
git push -u origin main-drift-diagnosis
git ls-remote origin main-drift-diagnosis
```
