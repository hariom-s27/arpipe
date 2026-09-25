# T0.4 Guard Forensics

Task type: READ-ONLY FORENSIC AUDIT (F). Recorded 2026-09-26 on branch `t04-guard-forensics`.
This file is the only repository change made by this task. Nothing in it is adopted.

Evidence labels: **VERIFIED** (repository content or command output), **DERIVED**
(mechanical consequence of verified facts), **INFERRED** (interpretation not stated by the
repository), **NOT VERIFIABLE** (required evidence is absent). Line numbers refer to the
files as committed at HEAD `588b6e60b20922e1f0986df492e370ac435c0747` unless another
commit is named.

## Plain-English Summary

1. T0.4 freezes all of `arpipe/` by path, in two places: `PROTECTED_PATHS` (diffed against the T0.4 base) and `FROZEN_SINCE_AUDIT` (diffed against the audited closure commit). The three R1 failures come from exactly these two lists. The guards work as written. They are not misfiring.
2. No T0.4 document says why the *whole* `arpipe/` directory is frozen for every later commit. The written prohibitions only apply to the T0.4 setup and closure worktrees ("This worktree … must not … change production ARPipe behavior").
3. What T0.4 actually relies on from `arpipe/` is narrow: the `PageKind` vocabulary, the `NEEDS_OCR` set and the `vector_text` classifier branch, and the detector page kinds already frozen in `page_profile.csv`.
4. A1–A4 leave all of those byte-identical: `_classify`, all 14 thresholds, `configure`, `NEEDS_OCR`, `ocr_page_numbers`, `PageKind`, and `arpipe/configs/default.yaml`.
5. The closure change allowance is not a mechanism R1 forgot to use. It covers one fixed historical window, and a test requires that it never cover `arpipe/`. This is **not Case 1**.
6. No commit after the T0.4 base touched a protected path before A1–A4, so there is no precedent.
7. The Phase 2.1 "amendment contract" is thin. It gives a trigger rule and a negative filename test, and defines no metadata fields. Creating an amendment file would itself fail an existing test.
8. Classification: **MIXED**. Case 3 holds for T0.4's stated Track-A, sampling and routing invariant. One piece is unresolved: T0.4's Track-B "same frozen sequence" names no version, so Case 2 cannot be ruled out there.
9. §10 is a draft for the author to ratify or reject. It is **NOT ADOPTED**, and all ratification fields are blank.
10. Also found: at the T0.4 base itself, `arpipe/pipeline.py` already called the four symbols A1–A4 supply, but nothing provided them. The "frozen" production tree was the partial-commit state that D6 identified.

## 1. Starting State

All values are from command output in the new worktree `sep_week1/t04-guard-forensics`, which was created with `git worktree add -b t04-guard-forensics ../t04-guard-forensics r1-resume-2-final`. **VERIFIED**

| Item | Value |
|---|---|
| Source branch resolved | `r1-resume-2-final` → `588b6e60b20922e1f0986df492e370ac435c0747` (`git for-each-ref --contains`) |
| Branch | `t04-guard-forensics` |
| HEAD | `588b6e60b20922e1f0986df492e370ac435c0747` |
| Parent | `c779c2e471ef8c3455c827de9ef571443f41911c` (single parent) |
| Subject | `test(r1): verify every arpipe module imports` |
| Tree | `91700aabfa1fb2df910f3f55916d9ff2bf0f2194` |
| Status | clean (`git status --porcelain` = 0 lines) |

The resolved tip matches the stated R1 tip. **VERIFIED**

## 2. Q1 — Frozen Objects

### 2.1 Exact definitions (VERIFIED)

`tools/t0_4/core.py:17` — `BASE_COMMIT = "ff030d97c13c8a2a977521bf91be2aca0cbf3034"`

`tools/t0_4/core.py:54-68`:
```python
PROTECTED_PATHS = (
    "arpipe",
    "configs/t0_1r",
    "configs/t0_3a",
    "configs/t0_3a_r1",
    "dataset/corpus_freeze",
    "dataset/corpus_gap_audit",
    "tests/t0_1",
    "tests/t0_2",
    "tests/t0_3a",
    "tests/t0_3a_r1",
    "tools/run_t0_2_robustness_gate.py",
    "tools/run_t0_3a_document_coverage.py",
    "tools/run_t0_3a_r1_document_coverage.py",
)
```
`tools/t0_4/core.py:173-177`:
```python
def verify_protected_paths_unchanged(repo_root: Path) -> None:
    command = ["git", "-C", str(repo_root), "diff", "--name-only", BASE_COMMIT, "--", *PROTECTED_PATHS]
    changed = subprocess.check_output(command, text=True).strip().splitlines()
    if changed:
        raise SetupInvariantError(f"frozen historical paths changed: {changed}")
```
`tests/t0_4/test_t0_4_closure_record.py:18-26`:
```python
FROZEN_SINCE_AUDIT = (
    "configs/t0_4",
    "artifacts/t0_4/benchmark_manifest.json",
    "artifacts/t0_4/config_hashes.json",
    "artifacts/t0_4/setup_audit.json",
    "dataset/corpus_freeze",
    "dataset/corpus_gap_audit",
    "arpipe",
)
```
`tests/t0_4/test_t0_4_closure_record.py:63-66`:
```python
def test_frozen_inputs_are_unchanged_since_the_audited_commit(record):
    changed = _git("diff", "--name-only", record["final_commit_after_audit"], "--", *FROZEN_SINCE_AUDIT)
    assert changed.returncode == 0
    assert changed.stdout.split() == []
```
`artifacts/t0_4/final_closure_audit.json` records `"final_commit_after_audit": "33ba76acf9da13d25027e39414e724dfa1170b59"`. **VERIFIED**

How the three failing guards are wired (**VERIFIED**):
- `tests/t0_4/test_t0_4_setup.py:79-80` calls `verify_protected_paths_unchanged(ROOT)`.
- `tests/t0_4/test_t0_4_setup.py:367-370` calls `run_audit(ROOT)`, and `tools/audit_t0_4_setup.py:100-102` calls `verify_protected_paths_unchanged(repo_root)`. That test uses the same mechanism as the previous one.
- `test_frozen_inputs_are_unchanged_since_the_audited_commit` uses `FROZEN_SINCE_AUDIT`, as quoted above.

Neither diff uses a merge base. Both compare **the working tree** against a fixed commit, so every descendant commit and every uncommitted change is in scope. **DERIVED**, from `git diff --name-only <commit> -- <paths>` with no second revision.

### 2.2 Why the three guards fail at HEAD (VERIFIED)

`git diff --name-status ff030d97c13c8a2a977521bf91be2aca0cbf3034 HEAD -- <PROTECTED_PATHS>` and `git diff --name-status 33ba76acf9da13d25027e39414e724dfa1170b59 HEAD -- <FROZEN_SINCE_AUDIT>` both return exactly:
```
M	arpipe/models.py
M	arpipe/ocr.py
M	arpipe/store.py
M	arpipe/triage.py
```
No other protected or frozen path differs. The guards are enforcing their literal definitions correctly. **DERIVED**

### 2.3 Provenance table

| Object | Exact definition | Introduced by | Commit subject | Stated purpose | Evidence label |
|---|---|---|---|---|---|
| `BASE_COMMIT` | `ff030d97c13c8a2a977521bf91be2aca0cbf3034` (`core.py:17`) | `b937b58298930114de08d9b0236714c564c6da02` (only commit touching `core.py`) | `T0.4: preregister dual-track OCR benchmark` | Prereg line 21: "The base is `ff030d9…` (T0.3A-R1). T0, T0.1R, T0.2, T0.3A, and T0.3A-R1 artifacts are protected." | VERIFIED |
| `PROTECTED_PATHS` | the 13 entries above (`core.py:54-68`) | `b937b58298930114de08d9b0236714c564c6da02` (`git log -S'PROTECTED_PATHS = ('`) | same | No adjacent comment. The raised message is "frozen historical paths changed". The commit body is empty. No statement explains why `arpipe` is in the list. | VERIFIED (absence of comment); NOT VERIFIABLE (reason for `arpipe`) |
| `FROZEN_SINCE_AUDIT` | the 7 entries above (`test_t0_4_closure_record.py:18-26`) | `63e3c047a09044d9c3bd9c61e3b56a01612f3d11` (only commit touching the file) | `T0.4-CLOSE: record final closure audit; T0.4 closed for the gold phase` | No adjacent comment. Closure report line 3: "The frozen corpus, T0.4 configurations, manifests, and production ARPipe are unchanged." | VERIFIED |
| `ALLOWED_CLOSURE_CHANGES` | `closure.py:74-84` (see §4) | `33ba76acf9da13d25027e39414e724dfa1170b59` | `T0.4-CLOSE: register vector_text route, fix held-out wording, add closure audit engine` | `closure.py:74`: "# The only paths the closure work may change relative to the audited base." | VERIFIED |
| `SNAPSHOT_PATHS` | `closure.py:86-102`. It includes `arpipe/CLAUDE.md`, `arpipe/README.md`, `arpipe/configs/default.yaml`, `arpipe/models.py`, `arpipe/triage.py`, `tools/t0_4`, `tests/t0_4`, `tools/audit_t0_4_setup.py` and others. | `33ba76acf9da13d25027e39414e724dfa1170b59` | same | These are the files the closure engine reads **from git objects of the audited commit** (`closure.py:147-154`). | VERIFIED |

**Was `arpipe` protected before T0.4 closure?** Yes. It was already in `PROTECTED_PATHS` at `b937b58298930114de08d9b0236714c564c6da02`, which is the setup commit, before closure. Closure then added it a second time, in `FROZEN_SINCE_AUDIT` at `63e3c047a09044d9c3bd9c61e3b56a01612f3d11`. **VERIFIED**

Earlier stages also have base guards. `tools/audit_t0_2_robustness_gate.py:38`, `tools/audit_t0_3a_document_coverage.py:32` and `tools/audit_t0_3a_r1_document_coverage.py:37` each pin a `BASE_COMMIT`. This audit did not trace whether those earlier guards protect `arpipe/` (see §11). **VERIFIED** that they exist; **NOT VERIFIABLE** in this audit whether they cover `arpipe/`.

## 3. Q2 — Why T0.4 Freezes Them

### 3.1 Every T0.4 statement bearing on production `arpipe/` (VERIFIED quotes)

| Source | Line | Exact text | Scope of the statement |
|---|---|---|---|
| `docs/experiments/T0.4_ocr_benchmark_preregistration.md` | 21 | "T0, T0.1R, T0.2, T0.3A, and T0.3A-R1 artifacts are protected. Corpus policy remains `NO_ACQUISITION`." | historical stage **artifacts**; `arpipe/` not named |
| same | 25 | "Detector output is `CANDIDATE_PROXY`" | evidence level of detector labels |
| same | 88-90 | "After recovery every engine uses the same frozen sequence: `document profile → routing → recovery → standardized reading order → heading inventory → candidate generation → span resolution → verification → quality gate`." | Track-B downstream. **No commit or version is named.** |
| same | 102 | "`vector_text` is routed to OCR, exactly as in the frozen ARPipe triage (`arpipe/triage.py`: `PageKind.VECTOR_TEXT` is a member of `NEEDS_OCR`)." | the route of one class |
| same | 140 | "This worktree may inspect repository metadata … It must not … change production ARPipe behavior; or modify frozen corpus/history." | **"This worktree"**, i.e. the T0.4 setup worktree |
| same | 142 | "Benchmark execution must occur only in a later, separately authorized worktree after T0.4 is committed and frozen." | benchmark execution |
| `tools/t0_4/README.md` | 32 | "The following are prohibited here: … benchmark-result creation, HOLDOUT tuning, and production-pipeline edits." | **"here"**, i.e. the closure work |
| `docs/experiments/T0.4_final_closure_audit.md` | 3 | "The frozen corpus, T0.4 configurations, manifests, and production ARPipe are unchanged." | a factual attestation about the closure range |
| same | 29 | "Frozen rationale, quoted from the frozen sources: \"glyphs drawn as vector paths -> OCR\" (`arpipe/models.py`) …" | the rationale for the `vector_text` **route** |
| same | 47 | "7 representation classes (the six detector page kinds mapped by the frozen builder, plus its `other` fallback)" | sampling cells depend on the `PageKind` vocabulary |

### 3.2 Rationale classification

- **(A) "The detector must not change because Track A sampling and representation classes were derived from it."** This is **not stated as the reason for the freeze**. The underlying *dependency* is documented as fact: closure report lines 47 and 102, and `closure.py:334-337`, which reads `class PageKind` from `arpipe/models.py` to declare representation levels. No text connects that dependency to freezing `arpipe/` as a whole. The dependency is **VERIFIED**; A as a stated rationale is **NOT VERIFIABLE**.
- **(B) "The whole ARPipe system must remain frozen until/through the OCR benchmark."** **Not stated.** The closest text is prereg lines 88-90, "the same frozen sequence". That sentence requires the downstream sequence to be identical for all engines. It does not say that sequence equals the `arpipe/` tree at `ff030d97c13c8a2a977521bf91be2aca0cbf3034`, and it does not say when the freeze begins. **VERIFIED** (text); B as stated is **NOT VERIFIABLE**.
- **(C) Another explicitly stated rationale.** **Yes, for the worktree-scoped prohibition.** Prereg line 140 and README line 32 state a non-execution / setup-only boundary for the T0.4 and T0.4-CLOSE worktrees. **VERIFIED**
- **(D) No rationale stated.** **Yes, for the implemented descendant-wide, whole-directory freeze.** `PROTECTED_PATHS` and `FROZEN_SINCE_AUDIT` carry no comment, and their introducing commits (`b937b58298930114de08d9b0236714c564c6da02` has an empty body; `63e3c047a09044d9c3bd9c61e3b56a01612f3d11`) give no reason for extending the freeze to later work. **VERIFIED** (absence)

**Result: (C) for the prose prohibition, and (D) for the implemented guard.** **DERIVED**

### 3.3 Explicit scope vs implemented scope

| Scope | What it covers | Label |
|---|---|---|
| **Explicitly protected (prose)** | Historical T0–T0.3A-R1 artifacts (prereg 21). No change to production behaviour **within the T0.4 setup/closure worktrees** (prereg 140; README 32). The `vector_text → OCR` route "exactly as in the frozen ARPipe triage" (prereg 102). A Track-B downstream sequence that is "the same frozen sequence" for every engine, version unspecified (prereg 88-90). | VERIFIED |
| **Scientifically depended on (implementation)** | The closure engine reads `arpipe/models.py` (`PageKind` members and the `VECTOR_TEXT` comment) and `arpipe/triage.py` (`NEEDS_OCR`, the `ocr_page_numbers` return, and the `VECTOR_PATH_TEXT_THRESHOLD` classifier branch) from the **audited commit's blobs** (`closure.py:194-209`, `334-337`). Representation class is mapped from the `kind` column of `dataset/corpus_freeze/page_profile.csv` (`core.py:290-298`, `389`), which "reuses the already-committed page/document text-layer profile (live_store/profiles.jsonl, produced by arpipe.triage/textlayer during an earlier, frozen pipeline stage)" (`tools/freeze_extraction_corpus.py:11-13`). | VERIFIED |
| **Enforced (implementation)** | Every byte of every file under `arpipe/`, for every descendant commit and working tree (`core.py:173-177`; `test_t0_4_closure_record.py:63-66`). | VERIFIED |

**The scopes are not identical.** The enforced scope, the whole directory for all descendants, is strictly larger than the explicit prose scope (worktree-scoped) and larger than the scientific dependency (classifier vocabulary and routing). **DERIVED**

## 4. Q3 — Closure Change Allowance

`tools/t0_4/closure.py:74-84` (**VERIFIED**):
```python
# The only paths the closure work may change relative to the audited base.
ALLOWED_CLOSURE_CHANGES = frozenset({
    PREREGISTRATION,
    "docs/experiments/T0.4_p-x1_reuse_audit.md",
    "tools/audit_t0_4_final_closure.py",
    "tools/audit_t0_4_setup.py",
    "tools/t0_4/README.md",
    "tools/t0_4/closure.py",
    "tests/t0_4/test_t0_4_final_closure.py",
    *CLOSURE_RECORD_FILES,
})
```
`CLOSURE_RECORD_FILES` (`closure.py:62-66`) contains `artifacts/t0_4/final_closure_audit.json`, `docs/experiments/T0.4_final_closure_audit.md` and `tests/t0_4/test_t0_4_closure_record.py`. **VERIFIED**

Where the allowance is used, `closure.py:744-752` (**VERIFIED**):
```python
    after = resolve_commit(repo_root, audited_rev)
    before = resolve_commit(repo_root, PRE_CLOSURE_COMMIT)
    ...
    changed = changed_paths(repo_root, before, after)
    unexpected = sorted(set(changed) - ALLOWED_CLOSURE_CHANGES)
    if unexpected:
        raise SetupInvariantError(f"closure changed paths outside its allowance: {unexpected}")
```
with `PRE_CLOSURE_COMMIT = "b937b58298930114de08d9b0236714c564c6da02"` (`closure.py:40`).

The guard test, `tests/t0_4/test_t0_4_final_closure.py:284-287` (**VERIFIED**):
```python
def test_closure_change_allowance_never_covers_frozen_inputs():
    frozen_prefixes = ("configs/t0_4/", "dataset/", "arpipe/")
    frozen_files = {K.MANIFEST, K.CONFIG_HASHES, "artifacts/t0_4/setup_audit.json", "tools/t0_4/core.py"}
    assert not [p for p in K.ALLOWED_CLOSURE_CHANGES if p.startswith(frozen_prefixes) or p in frozen_files]
```

Answers:
1. **What it can cover:** exactly the 10 enumerated files above. It is an exact-file allowlist. **VERIFIED**
2. **What it can never cover:** any path starting with `configs/t0_4/`, `dataset/` or `arpipe/`, plus the files `artifacts/t0_4/benchmark_manifest.json`, `artifacts/t0_4/config_hashes.json`, `artifacts/t0_4/setup_audit.json` and `tools/t0_4/core.py`. **VERIFIED**
3. **Does it exclude `arpipe/` explicitly?** Yes, by the prefix `"arpipe/"` in the guard test. **VERIFIED**
4. **Form of exclusion:** a prefix test (`startswith`) plus an exact-file set. The allowance itself is an exact-file set. **VERIFIED**
5. **Intended use:** the T0.4-CLOSE work window only. It is evaluated over `b937b58298930114de08d9b0236714c564c6da02 → audited_rev`. The committed record test fixes `audited_rev` to `33ba76acf9da13d25027e39414e724dfa1170b59` (`test_t0_4_closure_record.py:49`). It is not a post-closure amendment mechanism, not ordinary development, and not a documentation channel. **VERIFIED** (code); "not intended for post-closure amendments" is **DERIVED** from the fixed endpoints and the comment "the closure work".

**Did R1 fail to invoke an existing mechanism? No.** The allowance cannot legally include any `arpipe/` path, because a committed test forbids it. It also does not feed `PROTECTED_PATHS` or `FROZEN_SINCE_AUDIT`, so even a (forbidden) entry would not silence the three failing guards. **DERIVED**

## 5. Q4 — Are the Guards Frozen?

Mechanisms checked for each file: `FROZEN_SINCE_AUDIT`, `PROTECTED_PATHS`, `ALLOWED_CLOSURE_CHANGES` / the closure "frozen_files", `SNAPSHOT_PATHS`, hashes in `artifacts/t0_4/*.json`, the closure record's byte-for-byte reproduction, `REQUIRED_DELIVERABLES`, and the Phase 2.1 allowlist test. **VERIFIED** unless noted.

Common facts:
- None of the four files is in `FROZEN_SINCE_AUDIT` or `PROTECTED_PATHS`.
- No `artifacts/t0_4/*.json` or `configs/t0_4/*.json` file stores a **hash** of any of them. `final_closure_audit.json` mentions `tools/t0_4/core.py`, `tools/audit_t0_4_setup.py` and `tests/t0_4/test_t0_4_setup.py` only as terminology-scan keys, `changed_paths` entries or harness `sources`. Those values are computed from the **audited snapshot** (`closure.py:147-154`), not from HEAD.
- `tests/test_phase2_1_semantic_conformance.py:211-231` fails on any path that differs from `03a63f5d7d79bac6a0bab0ffc33af42004e78935` and does not match `ALLOWED_PHASE2_1_PATTERNS` (lines 39-53). None of `tools/t0_4/`, `tools/audit_t0_4_setup.py` or `tests/t0_4/` matches any pattern. **DERIVED:** any edit to any of the four files, or any new file under `tools/t0_4/` or `tests/t0_4/`, fails that Phase 2.1 test unless the allowlist is amended.
- Precedent: `c779c2e471ef8c3455c827de9ef571443f41911c` ("test(r1): admit exact reconstruction paths under A5") edited an existing guard test, the Phase 2.1 allowlist, to admit exact paths. The authorization it cites ("D6/Q6 amendment A5", test line 31) does not appear in `docs/decisions/D6_Q6_AS_IS_IDENTITY_DECISION_v1.md` or anywhere else in the committed tree (`git grep` for `A[1-5]` hits only this test). **VERIFIED** (edit); **NOT VERIFIABLE** (authorization text).

| File | In `FROZEN_SINCE_AUDIT` / `PROTECTED_PATHS` | Closure allowance / closure frozen-files | Hashed / byte-reproduced | Other binding | Determination |
|---|---|---|---|---|---|
| `tools/t0_4/core.py` | No / No | **Explicitly frozen** during closure: listed in `frozen_files` (`test_t0_4_final_closure.py:286`). Not in allowance. | No stored hash. Its functions (`build_manifest`, `_representation_class`, …) are imported by `closure.py:20-36` and re-run by `test_record_is_reproduced_byte_for_byte_from_the_audited_commit` (`test_t0_4_closure_record.py:48-50`), so a *behavioural* change to those functions would break reproduction. `PROTECTED_PATHS` and `verify_protected_paths_unchanged` are **not** imported by `closure.py`. | `REQUIRED_DELIVERABLES` (`audit_t0_4_setup.py:42`); Phase 2.1 allowlist; Phase 2 audit calls the closure engine "the frozen closure engine" (`PHASE2_FOUNDATION_INTEGRITY_AUDIT.md:253`) | **Frozen by T0.4-CLOSE's own declaration** and blocked by the Phase 2.1 allowlist. Editing `PROTECTED_PATHS` in place would contradict `test_t0_4_final_closure.py:286`. **VERIFIED** (declaration); whether that declaration binds descendants and not just the closure window is **INFERRED** |
| `tools/audit_t0_4_setup.py` | No / No | **In the allowance** (edited by `33ba76acf9da13d25027e39414e724dfa1170b59`: +1 line) | No stored hash | `REQUIRED_DELIVERABLES`; Phase 2.1 allowlist | **Not frozen by T0.4 after closure; blocked by the Phase 2.1 allowlist.** Its failing path is the call into `core.verify_protected_paths_unchanged` (line 102), so fixing it without touching `core.py` would mean removing or bypassing that call. **VERIFIED / DERIVED** |
| `tests/t0_4/test_t0_4_closure_record.py` | No / No (it *defines* `FROZEN_SINCE_AUDIT`) | In `CLOSURE_RECORD_FILES` and the allowance; committed after the audited commit (`63e3c047a09044d9c3bd9c61e3b56a01612f3d11`). Not in the audited snapshot. | No stored hash | Phase 2.1 allowlist. It is one of the three files that make up the closure record (`closure.py:62-66`; README line 30). | **Part of the closure record itself.** Editing it changes the record's content. **VERIFIED** (membership); "editing it alters the closure record" is **DERIVED** |
| `tests/t0_4/test_t0_4_setup.py` | No / No | Not in allowance; not in `frozen_files` | No stored hash | `REQUIRED_DELIVERABLES` (`audit_t0_4_setup.py:46`); Phase 2.1 allowlist | **Not declared frozen by T0.4; blocked by the Phase 2.1 allowlist.** **VERIFIED** |

**Consequence for a future amendment (DERIVED):**
- Option (A), "edit the existing guard", is legally closed for `core.py` without contradicting T0.4-CLOSE's explicit frozen-file declaration.
- `test_t0_4_closure_record.py` is part of the closure record.
- All four files are blocked by the Phase 2.1 allowlist, which could only be widened the way `c779c2e471ef8c3455c827de9ef571443f41911c` widened it.
- On this evidence, a conservative amendment takes route (B): leave the original guards untouched and add a new mechanism alongside them. Under (B) the three original guards **keep failing as written**. Their disposition has to be decided explicitly (§10.1, item 6).

## 6. Q5 — Amendment Contract

Governing text (**VERIFIED**):

`tests/test_phase2_1_semantic_conformance.py:197-208`:
```python
def test_conditional_t0_4_amendment_rule() -> None:
    """Verify no provisional amendment file exists and Part F declares NO FORMAL AMENDMENT."""
    ...
    assert "NO FORMAL T0.4 AMENDMENT REQUIRED." in text
    assert "NO T0.4 AMENDMENT EFFECTIVE." in text
    # Verify no amendment file was created
    amendment_files = list(REPO_ROOT.glob("docs/experiments/PHASE2.1_T0.4_AMENDMENT_*.md"))
    assert len(amendment_files) == 0, f"Provisional amendment file unexpectedly exists: {amendment_files}"
```
`docs/experiments/PHASE2.1_FOUNDATION_NORMALIZATION.md:174-190`:
> Phase 2.1 does not make any author-adopted change to the effective T0.4 methodology. … `NO FORMAL T0.4 AMENDMENT REQUIRED.` `NO T0.4 AMENDMENT EFFECTIVE.`
> ### Potential Amendment Triggers (Documented for Future Author Action):
> 1. **B1 Ratification:** … 6. **B8 Ratification:** If author formally authorizes post-freeze HOLDOUT annotation.
> No amendment file is created until an author decision formally adopts one of these changes.

`docs/experiments/PHASE2.1_CHANGE_LEDGER.md:43` (CHG-30): "Normative rule: amendment created ONLY upon author-adopted methodological change. `NO FORMAL T0.4 AMENDMENT REQUIRED`."

Status assertions that an amendment would contradict: `PHASE2.1_FOUNDATION_NORMALIZATION.md:267`, `PHASE2.1_B1_B8_DECISION_REGISTER.md:30` and `docs/phase4/PHASE4_DECISION_SHEET.md:453` all read `FORMAL_T0.4_AMENDMENT_EFFECTIVE = NO`.

| Contract element | What the repository specifies | Label |
|---|---|---|
| Filename pattern | `docs/experiments/PHASE2.1_T0.4_AMENDMENT_*.md`. This is implied only by the negative glob at test line 207; the suffix is undefined. | VERIFIED (glob); suffix NOT VERIFIABLE |
| Trigger / precondition | Created "ONLY upon author-adopted methodological change" (CHG-30); "No amendment file is created until an author decision formally adopts one of these changes" (Part F:190) | VERIFIED |
| Enumerated triggers | B1, B3, B4, B5, B6/B7, B8 ratifications only. **No trigger concerns production code or guard scope.** | VERIFIED |
| Required metadata fields | None defined | NOT VERIFIABLE |
| Author-ratification fields | None defined | NOT VERIFIABLE |
| Date requirements | None defined | NOT VERIFIABLE |
| Amendment status fields | Only the global flag `FORMAL_T0.4_AMENDMENT_EFFECTIVE = NO/…` (Part J:267) and the Part F strings | VERIFIED |
| Effective-commit requirement | None defined | NOT VERIFIABLE |
| Must reference prior T0.4 closure | Not stated | NOT VERIFIABLE |
| May change enforcement code | Not stated | NOT VERIFIABLE |
| Before/after semantics | Not stated | NOT VERIFIABLE |
| Evidence / approval fields | Not stated beyond "author decision formally adopts" | NOT VERIFIABLE |

Mechanical consequences of adopting any amendment (**DERIVED**):
1. Creating any file matching the glob fails `test_conditional_t0_4_amendment_rule` (line 208).
2. The Part F strings at lines 178-179 are asserted present, so declaring the amendment effective means editing `PHASE2.1_FOUNDATION_NORMALIZATION.md` and the test. Both paths are inside `ALLOWED_PHASE2_1_PATTERNS` (lines 40-41), so the allowlist itself does not block them. The amendment-rule test does.
3. Because narrowing the production-code guard is not one of the enumerated triggers, whether it counts as a "methodological change" under CHG-30 is itself an author determination. **INFERRED**

The only comparable ratification format in the repository is D6's: `recorded_on`, "Decision date supplied by author", "AUTHOR DECISION — VERBATIM", "AUTHOR SELECTION", and a label key (`D6_Q6_AS_IS_IDENTITY_DECISION_v1.md:1-6, 21-43, 270-278`). That is precedent, not a requirement. **VERIFIED** (existence); its applicability is **INFERRED**.

## 7. Q6 — Post-Closure Change Model

The T0.4 setup, closure and README texts were searched for post-closure changes, amendments, system/production/benchmark-phase freezes, later implementation, Gold-phase changes, reopening, descendants and effective commits. Relevant findings (**VERIFIED** quotes):

- Later work is anticipated **for execution artifacts only**. Prereg line 58: "A later execution worktree must render once, freeze the real 64-character image hash…". Prereg line 142: "Benchmark execution must occur only in a later, separately authorized worktree after T0.4 is committed and frozen."
- Descendants are anticipated **mechanically**. `test_t0_4_closure_record.py:45` asserts `final_commit_after_audit` is an ancestor of `HEAD`. Both path guards diff the working tree of any descendant.
- The closure decision is phase-scoped. `final_closure_audit.json` records `"closure_decision": "CLOSED_FOR_GOLD_PHASE"`, and closure report line 106 says: "Benchmark execution still requires a separately authorized worktree."
- Production-code change is prohibited only in scoped prose: prereg line 140 ("This worktree … must not … change production ARPipe behavior") and README line 32 ("prohibited here: … production-pipeline edits").
- No T0.4 text mentions amendments, reopening, effective commits, or any permitted later production-code change.
- Outside T0.4, Phase 2.1 Part F (after T0.4) is the only conditional amendment mechanism. `PHASE2.1_B1_B8_DECISION_REGISTER.md:271` recommends HOLDOUT annotation "only after a signed, immutable system freeze". That is a pending B8 recommendation, not a T0.4 rule.

**Outcome:**
- **VERIFIED:** production changes are explicitly prohibited *within the T0.4 setup/closure worktrees*.
- **NOT VERIFIABLE:** no T0.4 language anticipates, permits or prohibits later production-code change in *other* worktrees. The descendant-wide prohibition exists only in code (`core.py:173-177`, `test_t0_4_closure_record.py:63-66`).
- **VERIFIED:** T0.4 itself contains no conditional mechanism. The only one in the repository is Phase 2.1 Part F.

## 8. Q7 — Historical Protected-Path Changes

`git rev-list --count --ancestry-path ff030d97c13c8a2a977521bf91be2aca0cbf3034..HEAD` = 21 commits. `git log ff030d97c13c8a2a977521bf91be2aca0cbf3034..HEAD -- <all 13 PROTECTED_PATHS>` returns exactly (**VERIFIED**):

| Full SHA | Date | Subject | Changed |
|---|---|---|---|
| `d5513859a5315800a7b6c68711756798129ab8ee` | 2026-09-26 00:29:56 +0530 | `fix(r1): restore authorized model provider fields (A1)` | `arpipe/models.py` (+9) |
| `ca1498f75f14495bfc6ec829ef2b5ef728da2d3d` | 2026-09-26 00:30:26 +0530 | `fix(r1): restore observed script telemetry provider (A2)` | `arpipe/triage.py` (+73) |
| `ab9666b032a5838be3ae3a24a58aae68a4fd46b0` | 2026-09-26 00:30:49 +0530 | `fix(r1): supply OCR exception type without raise paths (A3)` | `arpipe/ocr.py` (+17) |
| `24b8e000f23d18faabd16f828bd20eeb5328ddf7` | 2026-09-26 00:31:42 +0530 | `fix(r1): restore quarantine span suppression (A4)` | `arpipe/store.py` (+19 −6) |

- The 16 earlier commits on the path, from `b937b58298930114de08d9b0236714c564c6da02` through `755c5519b9ab9484ab033685e563350a0cd0d685`, touched **no** protected path. **VERIFIED**
- No commit after `63e3c047a09044d9c3bd9c61e3b56a01612f3d11` touched `tools/t0_4`, `tests/t0_4`, `tools/audit_t0_4_*`, `artifacts/t0_4`, `configs/t0_4` or the T0.4 docs. **VERIFIED**
- Among local branch refs descending from `ff030d97c13c8a2a977521bf91be2aca0cbf3034`, only `r1-resume-2-final` (and this branch) differ under `arpipe/`. `dea3ae5399be50872768c8703c878c907ee6818b`, the E0 provider-half source named by D6, is **not** a descendant of the T0.4 base and not an ancestor of HEAD. **VERIFIED**

**Did any earlier post-T0.4 change pass the guards?** None exists, so there is **no precedent** showing the contract tolerated a protected-path change. **DERIVED.** Test results for intermediate commits were not re-run (per instruction). The Phase 2 audit records "tests/t0_4 96 passed" at its audit point (`PHASE2_FOUNDATION_INTEGRITY_AUDIT.md:376`, V13). **VERIFIED** (recorded claim).

### 8.1 Related fact: the base `arpipe/` tree was internally inconsistent (VERIFIED / DERIVED)

At `ff030d97c13c8a2a977521bf91be2aca0cbf3034` itself, `git grep` finds these consumers in `arpipe/pipeline.py`:
- line 167: `doc.script_map = profile.script_map`
- line 385: `"quarantine": Confidence.QUARANTINE}[grade]`
- line 392: `write_span=(grade != "quarantine"))`
- line 396: `except ocr_mod.OcrEngineUnavailable as exc:`

At that base, `models.py`, `triage.py`, `ocr.py` and `store.py` provide none of these symbols. **VERIFIED.** `arpipe/pipeline.py` was last changed at `c9d71bb127fcc46d690a8fbd9e5088b7049b6c05` (2026-09-17, P-M1), which D6 identifies as the partial commit. **VERIFIED**

**DERIVED:** the `arpipe/` bytes that T0.4 froze contained a pipeline that could not run end-to-end. A1–A4 add exactly the four missing providers. T0.4 never executed `arpipe/`; its tools read text only (`core.py:1-5`, `closure.py:1-7`). **VERIFIED**

## 9. Classification

**MIXED.** Each case is assessed separately below.

**Not Case 1. VERIFIED / DERIVED (§4).** The only T0.4 change allowance is fixed to the closure window and is forbidden by test from covering `arpipe/`. R1 did not skip an available mechanism.

**Case 3 holds for the stated Track-A / sampling / routing invariant. DERIVED.**
- T0.4's explicitly documented dependencies on `arpipe/` are listed in §3.3.
- The path guard (§2) is coarser: whole directory, all descendants, no stated rationale (§3.2 D).
- A symbol-level comparison of `arpipe/triage.py` and `arpipe/models.py` between `ff030d97c13c8a2a977521bf91be2aca0cbf3034` and HEAD, done by extracting source segments with Python `ast` and comparing bytes, shows the following **byte-identical**: `_classify`; all 14 threshold assignments (`MIN_CHARS_PER_PAGE`, `MIN_CHARS_DENSE`, `MAX_MOJIBAKE_RATIO`, `BIG_IMAGE_AREA_FRAC`, `HYBRID_IMAGE_AREA_FRAC`, `BLANK_CHARS`, `VECTOR_PATH_TEXT_THRESHOLD`, `COLUMN_HIST_BINS`, `GUTTER_MIN_RUN_FRAC`, `GUTTER_PEAK_THRESHOLD`, `GUTTER_SEARCH_LO`, `GUTTER_SEARCH_HI`, `DOC_SCANNED_FRAC`, `DOC_DIGITAL_FRAC`); `configure`; `NEEDS_OCR`; `ocr_page_numbers`; `detect_script`; `estimate_columns`; `gutter_bands`; `PageKind`; `Script`. **VERIFIED**
- `arpipe/configs/default.yaml`, which `configure` loads thresholds from (`triage.py:63-85`), is unchanged. **VERIFIED**
- Changed are: `profile_page` (a new `script_meta` computed **after** `kind = _classify(...)` at line 246, plus one constructor kwarg); `profile_document` (a new `script_map` field); the new function `_compute_page_script_meta`; a new import `from .verify import (_ALPHA_WORD_RE, _COMMON_ENGLISH_WORDS, WRONG_LANGUAGE_MIN_TOKENS)`; and in `models.py`, `Confidence` (+`QUARANTINE`), `StoredDoc`, `PageProfile`, `DocProfile` and `MDASpan` (+optional fields). **VERIFIED**
- A3 (`ocr.py`, +`OcrEngineUnavailable` class only) and A4 (`store.py`, `write_year(..., write_span=True)`) touch nothing that any T0.4 file references. `git grep` across `tools/t0_4`, `tests/t0_4`, `configs/t0_4`, the T0.4 docs and `artifacts/t0_4/setup_audit.json` for `ocr.py|store.py|write_span|OcrEngineUnavailable|QUARANTINE|script_map|script_meta` returns nothing. **VERIFIED**
- **So A1–A4 change the files but, at source level, not the objects T0.4 documents depending on. DERIVED.** Whether the *behaviour* of `profile_page(...).kind` is unchanged at runtime has not been demonstrated. The new code runs after `kind` is computed, but a new exception path (for example from the new `verify` import or from `_compute_page_script_meta`) would stop `profile_page` from returning at all. **INFERRED.** This is why §10 also requires behavioural reproduction.

**Case-2 residue (unresolved): Track B's "same frozen sequence".** Prereg lines 88-90 require every engine to use "the same frozen sequence" through "verification → quality gate", but T0.4 never identifies which code state that sequence is. **VERIFIED** (text); the identity is **NOT VERIFIABLE**.
- A4 changes what is written for quarantine-graded rows, and A1 adds `Confidence.QUARANTINE`. Both could fall inside the "verification → quality gate" stages. **INFERRED**
- The base tree could not execute that sequence at all (§8.1). **DERIVED**
- If the author reads "frozen sequence" as "the `arpipe/` bytes at `ff030d97c13c8a2a977521bf91be2aca0cbf3034`", Case 2 applies to Track B. If the author reads it as "whatever single downstream state is fixed before Track-B execution", it does not. The repository does not decide this. **NOT VERIFIABLE**
- Track B has not been executed. `artifacts/t0_4/` holds setup and closure artifacts only (`audit_t0_4_setup.py:30-35`). **VERIFIED**

**Also in the mix, a scope mismatch that predates D6:**
- D6 §12 (`D6_Q6_AS_IS_IDENTITY_DECISION_v1.md:236-239`) says: "**No T0.4 amendment required.** No preregistered T0.4 rule references As-Is identity, baseline identity, or system identity". That assessed T0.4's *rules about identity*, not T0.4's *path guards*. **VERIFIED** (text)
- D6 §11 (lines 222-229) flagged `triage.py`'s STOP-list status and the Phase 2.1 allowlist blocker, but not `PROTECTED_PATHS` or `FROZEN_SINCE_AUDIT`. **VERIFIED**

## 10. DRAFT — NOT ADOPTED

> **DRAFT — NOT ADOPTED.** This section is not an amendment, is not an author decision and has no effect. No amendment file was created. All ratification fields are blank on purpose. It exists so the author can ratify it, change it or reject it.

### 10.1 Case-3 draft: proposed narrowing amendment

**Proposed file (not created):** `docs/experiments/PHASE2.1_T0.4_AMENDMENT_<ID>.md`. The filename prefix comes from the Q5 glob; `<ID>` is undefined by the repository and is left for the author. Fields marked *(Q5)* come from the repository contract. Fields marked *(proposed)* are **not required by any repository rule** and follow D6's precedent format.

```
# PHASE2.1_T0.4_AMENDMENT_<ID> — Narrow T0.4 production-code guard to the classifier invariant

amendment_status (proposed):            DRAFT — NOT ADOPTED
trigger (Q5, CHG-30):                   author-adopted methodological change — author to confirm this
                                        change qualifies; it is not among the enumerated Part F triggers
recorded_on (proposed):                 ____________
AUTHOR DECISION — VERBATIM (proposed):  ____________
author_ratified (proposed):             ____________
author_ratification_date (proposed):    ____________
effective_commit (proposed):            ____________   (the commit that lands the enforcement below)
prior_closure_reference (proposed):     T0.4 base ff030d97c13c8a2a977521bf91be2aca0cbf3034;
                                        final_commit_before_audit b937b58298930114de08d9b0236714c564c6da02;
                                        final_commit_after_audit 33ba76acf9da13d25027e39414e724dfa1170b59;
                                        closure record commit 63e3c047a09044d9c3bd9c61e3b56a01612f3d11;
                                        closure_decision CLOSED_FOR_GOLD_PHASE
```

**1. The conflict.**
- T0.4 path guards: `tools/t0_4/core.py:54-68` and `173-177`; `tests/t0_4/test_t0_4_closure_record.py:18-26` and `63-66`.
- Failing: `test_t0_4_setup.py::test_frozen_corpus_and_history_are_unchanged`, `test_t0_4_setup.py::test_fail_closed_setup_audit_passes` and `test_t0_4_closure_record.py::test_frozen_inputs_are_unchanged_since_the_audited_commit`.
- D6/Q6: `755c5519b9ab9484ab033685e563350a0cd0d685`, `docs/decisions/D6_Q6_AS_IS_IDENTITY_DECISION_v1.md` §11 (R1 authorized to establish runnable identity) and §12 ("No T0.4 amendment required").
- A1–A4: `d5513859a5315800a7b6c68711756798129ab8ee`, `ca1498f75f14495bfc6ec829ef2b5ef728da2d3d`, `ab9666b032a5838be3ae3a24a58aae68a4fd46b0`, `24b8e000f23d18faabd16f828bd20eeb5328ddf7`.
- A5: `c779c2e471ef8c3455c827de9ef571443f41911c`. The A1–A5 authorization text itself is not in the repository (§5).
- Changed production files: exactly `arpipe/models.py`, `arpipe/triage.py`, `arpipe/ocr.py`, `arpipe/store.py`.

**2. The object T0.4 states it protects.**
- The `vector_text → OCR` route "exactly as in the frozen ARPipe triage" (prereg 102).
- Representation classes derived from "the six detector page kinds" (closure report 47).
- Detector labels frozen in `dataset/corpus_freeze/page_profile.csv` (already protected under `dataset/corpus_freeze`).
- Historical T0–T0.3A-R1 artifacts (prereg 21), which are unchanged here.

**3. Proposed scope.**
- `arpipe/models.py` may change only as A1 authorizes: `Confidence.QUARANTINE`; optional fields `StoredDoc.script_map`, `PageProfile.script_meta`, `DocProfile.script_map`, `MDASpan.body_script`.
- `arpipe/triage.py` may change only as A2 authorizes: the `verify` import, `_compute_page_script_meta`, `script_meta` in `profile_page` after `kind` is assigned, and `script_map` in `profile_document`.
- `arpipe/ocr.py` may change only as A3 authorizes: the `OcrEngineUnavailable` class, with no raise paths.
- `arpipe/store.py` may change only as A4 authorizes: the `write_year` `write_span` parameter and its branch.
- **No other production change.** Every other path under `arpipe/` stays byte-identical to `ff030d97c13c8a2a977521bf91be2aca0cbf3034`.
- The protected set in `PROTECTED_PATHS` and `FROZEN_SINCE_AUDIT` other than `arpipe` is unaffected.

**4. Protected classifier invariants.** Evidence-backed per §3.3 and §9, **byte-identical source** against `ff030d97c13c8a2a977521bf91be2aca0cbf3034`:
- `arpipe/triage.py`: `_classify`; the 14 threshold assignments listed in §9; `configure` (it rebinds all 14); `NEEDS_OCR`; `ocr_page_numbers`. The closure engine reads `NEEDS_OCR`, `ocr_page_numbers` and the `VECTOR_PATH_TEXT_THRESHOLD` branch at `closure.py:202-209`.
- `arpipe/models.py`: `PageKind`, including its member comments. The closure engine regexes the `VECTOR_TEXT` comment (`closure.py:208`) and the member list (`closure.py:335-336`).
- `arpipe/configs/default.yaml`: whole file. `configure` overrides thresholds from its `triage` section, and the closure engine reads it (`closure.py:198`, `222`). *(Added on evidence; not in the task's minimum list.)*
- `arpipe/CLAUDE.md` and `arpipe/README.md`: whole files. They are closure `SNAPSHOT_PATHS` sources of the frozen `vector_text` rationale (`closure.py:196-197`, `210`). *(Added on evidence.)*
- `profile_page`: every line up to and including `kind = _classify(n_chars, text_area, image_area, mojibake_ratio, n_drawings)` byte-identical. The diff after that point must be additive only (`script_meta`). *(This is DERIVED. The function as a whole cannot be byte-identical under A2.)*

**Behavioural reproduction** (where evidence supports it). For every FIT page, `profile_page(...).kind` from the candidate triage must equal the `kind` column of `dataset/corpus_freeze/page_profile.csv`.
- Safeguard *(proposed, INFERRED rationale)*: also run the base-commit triage and require candidate == base page for page. `page_profile.csv` was produced by an earlier triage run (`tools/freeze_extraction_corpus.py:11-13`), and this audit cannot verify that run's code equals the base code. A base-vs-`page_profile` mismatch would therefore not be attributable to A1–A4.
- FIT membership is taken only from `dataset/corpus_freeze/issuer_split.csv`. No HOLDOUT page is opened.

**5. Proposed replacement enforcement** (not executed in F).
- (a) **Source-level test.** Using `git show ff030d97c13c8a2a977521bf91be2aca0cbf3034:<path>` and `ast` segment extraction, assert byte equality for every symbol or file in item 4. Assert that `git diff --name-only ff030d97c13c8a2a977521bf91be2aca0cbf3034 -- arpipe` ⊆ {the four files}, and that each file's changed top-level symbols ⊆ its A1–A4 scope.
- (b) **Page-kind reproduction check** over FIT pages against `dataset/corpus_freeze/page_profile.csv`, as above. This check opens FIT PDFs, so it needs the executing task's own authorization. It is not run here.

**6. Implementation location, which depends on Q4.**
- Per §5, `tools/t0_4/core.py` is explicitly frozen by T0.4-CLOSE (`test_t0_4_final_closure.py:286`), and `test_t0_4_closure_record.py` is part of the closure record. **The amendment must NOT edit the original guards:** not `core.py`, not `audit_t0_4_setup.py`, and neither `tests/t0_4/*` file.
- New enforcement goes in a **new file outside `tools/t0_4/` and `tests/t0_4/`**, for example `tests/test_t0_4_classifier_invariant.py` (name illustrative). It must be admitted to `ALLOWED_PHASE2_1_PATTERNS` by an exact-path entry, as `c779c2e471ef8c3455c827de9ef571443f41911c` did for `tests/test_import_smoke.py`. Without that entry, the new file fails `test_historical_immutability_strict_allowlist`.
- **Open item for the author** (listed, not chosen): because the original guards are left untouched, the three original tests will **continue to fail** as written. The amendment must say how that is recorded, for example:
  - (i) keep them failing and name them, by exact node ID, as superseded by this amendment;
  - (ii) add a new, separately admitted collection-level mechanism that marks those exact node IDs as expected failures referencing this amendment;
  - (iii) another mechanism the author specifies.
  Options (ii) and (iii) change the guards' *effect* without changing their bytes. That trade-off is the author's call.
- Consequential edits the amendment cannot avoid (Q5): creating the amendment file fails `test_conditional_t0_4_amendment_rule` (line 207-208). The strings `NO FORMAL T0.4 AMENDMENT REQUIRED.` / `NO T0.4 AMENDMENT EFFECTIVE.` (Part F:178-179) and `FORMAL_T0.4_AMENDMENT_EFFECTIVE = NO` (Part J:267; B1-B8 register:30; Phase 4 decision sheet:453) would become false. Each needs an explicit, authorized update.

**7. D6 erratum (draft text; not applied).**
```
ERRATUM to docs/decisions/D6_Q6_AS_IS_IDENTITY_DECISION_v1.md §12 — DRAFT, NOT ADOPTED

§12 states "No T0.4 amendment required" on the ground that no preregistered T0.4 rule
references As-Is, baseline, or system identity. That assessment did not account for the
T0.4 path-level guards: tools/t0_4/core.py PROTECTED_PATHS (includes "arpipe", diffed
against ff030d97c13c8a2a977521bf91be2aca0cbf3034) and
tests/t0_4/test_t0_4_closure_record.py FROZEN_SINCE_AUDIT (includes "arpipe", diffed
against 33ba76acf9da13d25027e39414e724dfa1170b59). Any R1 composition that changes a
file under arpipe/ — as §11 anticipates — fails those guards. This erratum corrects the
scope of §12's assessment only; it does not state that D6 adopted any amendment, and it
does not alter D6's identity decision.

erratum_recorded_on:   ____________
author_ratified:       ____________
```

**8. Ratification fields:** blank, as shown in the header block and erratum above. No author approval is simulated.

### 10.2 Case-2 residue: Track-B "frozen sequence" (options only; no recommendation)

This applies only if the author reads prereg lines 88-90 as freezing the `arpipe/` bytes at `ff030d97c13c8a2a977521bf91be2aca0cbf3034` for Track B.

- **Option A: keep the T0.4 freeze; abandon the R1 reconstruction for Track-B purposes.**
  - What changes: A1–A4 are not used for any T0.4 Track-B run.
  - What stays protected: the literal base `arpipe/` bytes.
  - Consequences: the base tree cannot execute the downstream sequence (§8.1), so Track B has no runnable frozen pipeline without further authorized work. D6's runnability purpose is not served for T0.4. **DERIVED**
- **Option B: amend or override through the Q5 mechanism.**
  - What changes: an amendment defines the Track-B frozen sequence as a named state, for example the R1 composition at a named commit, fixed before any Track-B execution.
  - What stays protected: identity of the downstream sequence across all engines (prereg 88-90).
  - Consequences: C2 remains governed separately by D6 §10. The amendment carries the same Q5 consequential edits as §10.1 item 6.

## 11. Evidence Gaps

- **NOT VERIFIABLE:** why `arpipe` (the whole directory) was placed in `PROTECTED_PATHS`. There is no comment, the commit body is empty, and no document states it.
- **NOT VERIFIABLE:** the A1–A5 authorization text. Only commit subjects and test comments (`test_phase2_1_semantic_conformance.py:31-52`) exist. D6 v1 contains no A1–A5.
- **NOT VERIFIABLE:** which code state T0.4's Track-B "same frozen sequence" denotes.
- **NOT VERIFIABLE:** that the triage code which produced `page_profile.csv` (via `live_store/profiles.jsonl`) equals `arpipe/triage.py` at `ff030d97c13c8a2a977521bf91be2aca0cbf3034`.
- **NOT VERIFIABLE:** the amendment metadata schema. None is defined (§6).
- **Not established:** runtime behavioural equivalence of `profile_page(...).kind`. This is source-level only; no execution was performed.
- **Not traced:** whether the T0.2 / T0.3A / T0.3A-R1 base guards also cover `arpipe/`.
- **Not re-run:** test results at intermediate commits (instruction R5 / Q7).

## 12. Scope Boundary

This audit did **not**:
- run R1 or any test suite;
- open, render or OCR any PDF;
- inspect any HOLDOUT file, output or annotation;
- read `page_profile.csv` beyond its header row;
- attribute the INE00LO01017_2025 drift;
- reproduce the page-kind experiment;
- modify production code, tests, configs, artifacts, D6 or any T0.4 guard;
- create an amendment file;
- inspect other branches' uncommitted work, such as `t0.4-gold` or `t0.4-routing-clarification`;
- push anything.

It did **not decide**:
- whether to ratify §10;
- whether narrowing the guard qualifies as a "methodological change" under CHG-30;
- how the Track-B frozen sequence should be read;
- how the three original failing guards should be disposed of;
- whether R1 is pinned;
- whether C2's gate is met.

Scratch analysis, the `ast` symbol comparison, ran on blob copies in the session scratchpad outside the repository.
