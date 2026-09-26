"""Derive compact public P-A records from original, unmodified execution captures."""
import collections
import copy
import importlib.util
import json
import re
import shutil
import xml.etree.ElementTree as ET

from capture import ROOT, REPO, PIN, PRESERVATION, PUBLIC, SCRATCH, FIXTURE, digest, file_id, git, txt, write, now

executions = {c: json.loads((ROOT / f"claim-{c}-execution.json").read_text()) for c in "abc"}
environment = copy.deepcopy(executions["a"]["environment"])
environment.pop("sys_path")
environment["historical_environment_source"]["normalized_text_sha256"] = environment["historical_environment_source"].pop("sha256")
environment["historical_environment_source"]["sha256"] = digest((ROOT / "historical-environment.txt").read_bytes())
environment["historical_environment_source"]["hash_note"] = "Original capture hashed newline-normalized text. Public metadata separately records that derived hash and the exact source-byte hash; original capture is unchanged. No test result or input was changed."
environment["PUBLICATION_CLASSIFICATION"] = "PUBLIC_SAFE"
environment["omission"] = "Unneeded interpreter search-path inventory omitted from public environment; exact command, explicit overrides, executable and production import are retained."
write(PUBLIC / "environment.json", environment)
for helper in ("capture.py", "pa_observer.py", "package.py"):
    shutil.copyfile(ROOT / helper, PUBLIC / helper)

def compact_state(state):
    return {k: v for k, v in state.items() if k != "protected_working_file_manifest"}

initial = json.loads((ROOT / "initial.json").read_text())
write(PUBLIC / "worktree-identity.json", {
    "initial": compact_state(initial), "execution_before": compact_state(executions["a"]["before"]),
    "execution_after": compact_state(executions["c"]["after"]),
    "EXECUTION_COMMIT": PIN, "initial_documentation_commit": PRESERVATION,
    "new_worktree_created": False, "reason": "Existing clean worktree safely supported temporary detached checkout; original branch retained for restoration.",
    "statement": "No new worktree was necessary; reproduction was performed from the existing clean pinned worktree.",
    "protected_working_files_unchanged_all_claims": all(v["protected_working_files_unchanged"] for v in executions.values()),
    "thesis_repository": {"path": r"D:\sem_iitk\sem9\thesis", "HEAD": "313f00b7e8c364c056a5a9d284ff843128419e21",
        "branch": "main", "status": "Pre-existing untracked nested worktrees/evidence directories; no thesis governance work performed.",
        "role": "Not the execution repository. Historical private transcript read-only provenance source resides here."},
    "PUBLICATION_CLASSIFICATION": "PUBLIC_SAFE"})

protected = executions["a"]["before"]["protected_working_file_manifest"]
for f in protected:
    f["git_blob_sha256"] = digest(git("cat-file", "blob", f"{PIN}:{f['path']}"))
    f["matches_git_blob"] = f["sha256"] == f["git_blob_sha256"]
assert all(f["matches_git_blob"] for f in protected)
write(PUBLIC / "execution-inputs.json", {"EXECUTION_COMMIT": PIN, "files": protected,
    "file_count": len(protected), "scope": "All tracked arpipe/, configs/, tests/, tools/ and conftest.py files; working bytes equal pinned Git blobs.",
    "dataset_identity": executions["a"]["before"]["tree_hashes"]["dataset"],
    "dataset_handling": "Unmodified existing checkout; no regeneration or direct corpus rerun.",
    "PUBLICATION_CLASSIFICATION": "PUBLIC_SAFE"})

fixture = json.loads((PUBLIC / "fixture-identity.json").read_text())
fixture["PUBLICATION_CLASSIFICATION"] = "PUBLIC_SAFE"
fixture["postexecution_byte_verification"] = {str(p.relative_to(FIXTURE)): digest(p.read_bytes()) for p in sorted(FIXTURE.rglob("*")) if p.is_file()}
assert all(fixture["postexecution_byte_verification"][f["relative_path"].split("fixtures/",1)[1]] == f["sha256"] for f in fixture["files"])
fixture["postexecution_scripts_unchanged"] = all(digest(__import__('pathlib').Path(f["path"]).read_bytes()) == f["sha256"] for f in fixture["scripts"])
assert fixture["postexecution_scripts_unchanged"]
write(PUBLIC / "fixture-identity.json", fixture)

spec = importlib.util.spec_from_file_location("pa_hash_input_inspection", REPO / "tools/check_doc_hashes.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
docs = []
rows = []
for path in sorted(REPO.glob(module.DOCS_GLOB)):
    rel = path.relative_to(REPO).as_posix()
    entry = file_id(path, PIN, rel)
    entry["last_change_commit"] = txt("log", "-1", "--format=%H", PIN, "--", rel)
    parsed = module.extract_hash_rows(path, REPO)
    entry["recognized_hash_claims"] = len(parsed)
    docs.append(entry)
    for row in parsed:
        blob = git("cat-file", "blob", f"{row.source_commit}:{row.source_path}")
        rows.append({"document": row.doc, "line_number": row.line_no,
            "source_commit": row.source_commit, "source_path": row.source_path,
            "recorded_sha256": row.recorded_hash, "git_blob_sha256": digest(blob),
            "git_blob_bytes": len(blob), "matches": digest(blob) == row.recorded_hash})
scripts = []
for rel in ("tools/check_doc_hashes.py", "tools/check_doc_hashes_allowlist.json"):
    entry = file_id(REPO / rel, PIN, rel)
    entry["last_change_commit"] = txt("log", "-1", "--format=%H", PIN, "--", rel)
    scripts.append(entry)
assert len(rows) == 10 and all(r["matches"] for r in rows)
manifest_bytes = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
write(PUBLIC / "document-hash-inputs.json", {
    "EXECUTION_COMMIT": PIN, "scripts_and_allowlist": scripts, "scanned_documents": docs,
    "recognized_manifest_entries": rows, "derived_entry_manifest_sha256": digest(manifest_bytes),
    "manifest_recipe": "SHA-256 of UTF-8 json.dumps(recognized_manifest_entries, sort_keys=True, separators=(',', ':')); no trailing newline",
    "allowlist_exceptions": json.loads((REPO / "tools/check_doc_hashes_allowlist.json").read_text())["exceptions"],
    "one_check": "One recognized Markdown table row with Verified Git SHA-256, Source commit and Source path columns, a full 40-hex commit and 64-hex hash.",
    "pass": "SHA-256 of exact git cat-file blob bytes at the cited commit:path equals the recorded full SHA-256.",
    "unallowed_failure": "A mismatching or unreadable cited blob whose document::source_commit::source_path key is absent from the allowlist.",
    "allowed_failure": "A mismatch may be ALLOWED-FAIL if its key is in the allowlist; this execution used an empty allowlist and had none.",
    "scope": "Ten hash assertions in one provenance document, not ten PDFs. This is documentation-to-Git-blob integrity checking, not a historical provenance proof or current corpus validation.",
    "PUBLICATION_CLASSIFICATION": "PUBLIC_SAFE"})

private = []
def private_artifact(path, reason):
    entry = file_id(path)
    entry.update({"classification": "PRIVATE_ARCHIVE_REQUIRED", "reason": reason,
                  "off_machine_archive_performed": False, "retention": "Local original execution capture only; not durable preservation."})
    private.append(entry)

def reference(name):
    p = PUBLIC / name
    return {"path": name, "sha256": digest(p.read_bytes()), "bytes": p.stat().st_size,
            "classification": "PUBLIC_SAFE"}

for claim in "abc":
    ex = executions[claim]
    name = f"claim-{claim}"
    for stream in ("stdout", "stderr"):
        shutil.copyfile(ROOT / f"{name}.{stream}.txt", PUBLIC / f"{name}.{stream}.txt")
    stdout = (ROOT / f"{name}.stdout.txt").read_text()
    refs = [reference("environment.json"), reference("worktree-identity.json"), reference("execution-inputs.json"),
            reference("capture.py"), reference(f"{name}.stdout.txt"), reference(f"{name}.stderr.txt")]
    base = {"reproduction_id": "P-A-R1-20260926", "claim_id": claim.upper(), "EXECUTION_COMMIT": PIN,
        "worktree_state_before": compact_state(ex["before"]), "worktree_state_after": compact_state(ex["after"]),
        "environment": reference("environment.json"), "command_argv": ex["command_argv"],
        "command_windows": ex["command_windows"], "working_directory": ex["cwd"],
        "timestamp_start_utc": ex["timestamp_start_utc"], "timestamp_end_utc": ex["timestamp_end_utc"],
        "wall_seconds": ex["wall_seconds"], "exit_status": ex["exit_status"],
        "protected_working_files_unchanged": ex["protected_working_files_unchanged"],
        "historical_status": "TRANSCRIPT-ONLY", "PUBLICATION_CLASSIFICATION": "PUBLIC_SAFE",
        "preservation_status": "PRESERVED_BUT_NOT_YET_DURABLE"}
    base["historical_provenance"] = {
        "recovery_record": "docs/identity/R1_EVIDENCE_RECOVERY_REPORT.md",
        "INPUT_ARTIFACT_SOURCE_COMMIT": PRESERVATION,
        "section": "9" if claim in "ab" else "11",
        "production_effect": False,
        "transcript_sha256": "9352b967c0c6dc4d30b850420b2ac92da1773caf4113c6578fd9642e8055d217",
        "basis": "Preserved contemporaneous command/output records and the documented recovery chain; not inferred solely from matching hashes."}
    private_artifact(ROOT / f"{name}-execution.json", "Original environment capture includes unnecessary interpreter search-path inventory; compact public record retains execution identity, command, relevant environment and complete outcomes.")
    if claim in "ab":
        raw_xml = ROOT / f"{name}.xml"
        data = raw_xml.read_bytes()
        # Only remove machine hostname; retain every other byte and every test result.
        public_xml, removed = re.subn(rb' hostname="[^"]*"', b"", data)
        assert removed == 1
        (PUBLIC / f"{name}.junit.xml").write_bytes(public_xml)
        private_artifact(raw_xml, "Raw JUnit includes the private machine hostname. Public derivative removes only that attribute; all other bytes and all test evidence are retained.")
        obs = json.loads((ROOT / f"{name}-observer.json").read_text())
        private_artifact(ROOT / f"{name}-observer.json", "Original observer includes unnecessary interpreter search-path inventory; complete test outcomes are retained in public JUnit and compact independent observer evidence.")
        assert all(__import__('pathlib').Path(p).is_relative_to(REPO / 'arpipe') for p in obs["arpipe_modules"].values())
        xml_counts = collections.Counter()
        tree = ET.fromstring(data)
        for test in tree.iter("testcase"):
            if test.find("failure") is not None:
                xml_counts["failed"] += 1
            elif test.find("error") is not None:
                xml_counts["errors"] += 1
            elif test.find("skipped") is not None:
                xml_counts["xfailed" if test.find("skipped").get("type") == "pytest.xfail" else "skipped"] += 1
            else:
                xml_counts["passed"] += 1
        counts = obs["counts"]
        assert all(xml_counts[k] == counts[k] for k in ("passed", "skipped", "xfailed", "failed", "errors"))
        strict = sum("[XPASS(strict)]" in r.get("detail", "") for r in obs["reports"])
        assert strict == 0 and counts["xpassed"] == 0
        observation = {"counts": counts, "collected": obs["collected"], "strict_xpass_count": strict,
            "collection_errors": obs["collection_errors"], "exitstatus": obs["exitstatus"],
            "arpipe_modules": obs["arpipe_modules"], "all_production_imports_from_pinned_worktree": True,
            "nonpass_reports": [r for r in obs["reports"] if r["outcome"] != "passed" or r.get("wasxfail")],
            "report_count": len(obs["reports"]), "original_observer_sha256": digest((ROOT / f"{name}-observer.json").read_bytes()),
            "count_method": "pytest terminal reporter categories recorded by a read-only plugin; independent JUnit testcase parsing confirms pass/skip/xfail/fail/error; full report scan separately detects strict XPASS.",
            "junit_conversion": {"original_sha256": digest(data), "public_sha256": digest(public_xml),
                "only_change": "Removed one hostname attribute; all other bytes retained."},
            "PUBLICATION_CLASSIFICATION": "PUBLIC_SAFE"}
        write(PUBLIC / f"{name}-observed.json", observation)
        expected = {"total": 431, "passed": 411, "skipped": 17, "xfailed": 3, "xpassed": 0, "failed": 0, "errors": 0} if claim == "a" else {"total": 104, "passed": 103, "skipped": 1, "xfailed": 0, "xpassed": 0, "failed": 0, "errors": 0}
        observed = {"total": obs["collected"], **counts}
        assert observed == expected
        runtime = re.search(r" in ([0-9.]+)s", stdout)
        base.update({"execution_validity": {"collection_succeeded": True, "tests_executed": True,
                "process_completed": True, "infrastructure_crash": False},
            "observed_result": observed, "expected_historical_result": expected,
            "historical_equivalence": {"exact_counts_match": True, "execution_is_historical_session": False},
            "arithmetic": {"expression": "411 + 17 + 3 = 431" if claim == "a" else "103 + 1 = 104", "verified": True},
            "pytest_reported_seconds": float(runtime.group(1)),
            "observer_script": reference("pa_observer.py"),
            "reporting_only_additions": ["Read-only observer plugin", "External JUnit output", "External basetemp", "Bytecode writing disabled"],
            "input_identity": reference("execution-inputs.json") if claim == "a" else reference("fixture-identity.json"),
            "classification": "REPRODUCED" if claim == "a" else "REPRODUCED_WITH_QUALIFICATION",
            "limitations": ["Current execution independently reproduces the counts; it does not turn the historical transcript into a commit-embedded execution artifact."] if claim == "a" else [
                "Recovered fixtures match all seven preservation-manifest entries and the transcript identifies their build location and two test files. Contemporaneous per-fixture execution hashes are unavailable; the manifest was made during later preservation.",
                "Unchanged recovered test files were loaded from run-b to retain their hard-coded sibling fixture path; every loaded production arpipe module came from the clean pinned worktree. Historical execution imported production from the run-b Git export.",
                "The fixture builder was identified and hash-verified, not rerun. This is evidence machinery testing, not Track-A scientific evidence."],
            "INPUT_ARTIFACT_SOURCE_COMMIT": PIN if claim == "a" else {"test_files": PIN, "fixture_bytes": None, "preservation_manifest": PRESERVATION}})
        refs += [reference("pa_observer.py"), reference(f"{name}.junit.xml"), reference(f"{name}-observed.json")]
        if claim == "b": refs += [reference("fixture-identity.json"), reference("fixture-manifest.sha256")]
    else:
        observed = {"pass": stdout.count("[PASS]"), "allowed_failures": stdout.count("[ALLOWED-FAIL]"),
            "unallowed_failures": 0, "checks": 10, "documents": 1}
        assert "Checked 10 hash claim(s) across 1 doc(s); 0 unallowed failure(s)." in stdout
        assert observed["pass"] == 10 and "[FAIL]" not in stdout
        base.update({"execution_validity": {"script_completed": True, "infrastructure_crash": False},
            "observed_result": observed, "expected_historical_result": {"pass": 10, "checks": 10, "unallowed_failures": 0},
            "historical_equivalence": {"exact_result_match": True, "execution_is_historical_session": False},
            "classification": "REPRODUCED", "input_identity": reference("document-hash-inputs.json"),
            "INPUT_ARTIFACT_SOURCE_COMMIT": PIN,
            "limitations": ["Ten recognized hash claims across one document. Verifies cited Git blob integrity only; does not prove historical provenance or validate scientific outputs."]})
        refs += [reference("document-hash-inputs.json")]
    base["artifacts"] = refs
    write(PUBLIC / f"{name}.json", base)

write(PUBLIC / "private-artifact-inventory.json", {"reproduction_id": "P-A-R1-20260926",
    "artifacts": private, "PUBLICATION_CLASSIFICATION": "PUBLIC_SAFE",
    "scope": "Metadata only; no private contents published. No archive operation or archive destination approval implied.",
    "excluded": [{"path": str(FIXTURE), "classification": "EXCLUDE", "reason": "Original recovered synthetic PDF inputs retained in place; no PDFs are needed in the public evidence commit."},
        {"path_pattern": str(ROOT / 'claim-*-temp'), "classification": "EXCLUDE", "reason": "Disposable pytest runtime files; remove after preserving results."}]})
print(json.dumps({"prepared_public_files": len(list(PUBLIC.iterdir())), "classifications": {c: json.loads((PUBLIC / f'claim-{c}.json').read_text())["classification"] for c in "abc"}}))
