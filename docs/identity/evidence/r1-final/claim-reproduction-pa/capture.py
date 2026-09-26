"""P-A evidence collector. No source, fixture, dependency or result modifications."""
import datetime
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
REPO = Path(r"D:\sem_iitk\sem9\thesis\sep_week1\r1-final")
PIN = "28a67b63d890d8407fa9738a71ae37ad63148b73"
PRESERVATION = "2a42b97bdc09297eba92ae6a46cd6e7365a0e54a"
SCRATCH = Path(r"C:\Users\hario\AppData\Local\Temp\claude\d--sem-iitk-sem9-thesis\948b3666-670c-4ce4-951f-ff0d9a9b4562\scratchpad")
DEPS = SCRATCH / "test-deps"
FIXTURE = SCRATCH / "run-b/arpipe/fixtures"
PYTHON = Path(r"D:\sem_iitk\sem9\thesis\sep_week1\arpipe-0.1.0\arpipe\.venv\Scripts\python.exe")
PUBLIC = ROOT / "public"
PUBLIC.mkdir(exist_ok=True)


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def git(*args):
    proc = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, check=True)
    return proc.stdout


def txt(*args):
    return git(*args).decode("utf-8").strip()


def file_id(path, source_commit=None, rel=None):
    data = path.read_bytes()
    entry = {"path": str(path), "bytes": len(data), "sha256": digest(data),
             "INPUT_ARTIFACT_SOURCE_COMMIT": source_commit}
    if rel and source_commit:
        blob = git("cat-file", "blob", f"{source_commit}:{rel}")
        entry.update({"git_path": rel, "git_blob_sha256": digest(blob),
                      "working_bytes_equal_git_blob": data == blob})
    return entry


def snapshot():
    paths = git("ls-files", "-z", "--", "arpipe", "configs", "tests", "tools", "conftest.py").decode().split("\0")
    files = [{"path": p, "sha256": digest((REPO / p).read_bytes())} for p in sorted(filter(None, paths))]
    return {"timestamp": now(), "repository": str(REPO), "worktree": str(REPO),
        "HEAD": txt("rev-parse", "HEAD"), "branch": txt("branch", "--show-current") or "DETACHED_HEAD",
        "status_porcelain": txt("status", "--porcelain=v1", "--untracked-files=all"),
        "git_common_dir": txt("rev-parse", "--git-common-dir"),
        "tree_hashes": {p: txt("rev-parse", f"HEAD:{p}") for p in ("arpipe", "configs", "dataset", "tests", "tools")},
        "protected_working_file_manifest": files,
        "protected_working_file_manifest_sha256": digest("".join(f"{p['sha256']}  {p['path']}\n" for p in files).encode())}


def prepare():
    initial = snapshot()
    assert initial["HEAD"] == PRESERVATION and not initial["status_porcelain"]
    write(ROOT / "initial.json", initial)
    manifest_path = "docs/identity/evidence/r1-final/tree-manifests/run-b.sha256"
    manifest = git("cat-file", "blob", f"{PRESERVATION}:{manifest_path}")
    expected = dict((p, h) for h, p in re.findall(r"^([0-9a-f]{64})  (.+)$", manifest.decode(), re.M))
    fixtures = []
    for path in sorted(FIXTURE.rglob("*")):
        if path.is_file():
            entry = file_id(path)
            rel = path.relative_to(SCRATCH / "run-b").as_posix()
            entry.update({"relative_path": rel, "preserved_sha256": expected.get(rel),
                          "matches_preservation_manifest": entry["sha256"] == expected.get(rel)})
            fixtures.append(entry)
    assert len(fixtures) == 7 and all(f["matches_preservation_manifest"] for f in fixtures)
    fixture_manifest = "".join(f"{f['sha256']}  {f['relative_path']}\n" for f in fixtures)
    scripts = []
    for rel in ("arpipe/tests/make_fixtures.py", "arpipe/tests/test_pipeline.py", "arpipe/tests/test_pm1_orderqc.py"):
        scripts.append(file_id(SCRATCH / "run-b" / rel, PIN, rel))
    assert all(f["working_bytes_equal_git_blob"] for f in scripts)
    write(PUBLIC / "fixture-identity.json", {
        "fixture_directory": str(FIXTURE), "file_count": len(fixtures),
        "total_bytes": sum(f["bytes"] for f in fixtures), "files": fixtures,
        "deterministic_manifest_recipe": "SHA-256 of UTF-8 '<sha256>  <run-b-relative path>\\n' lines sorted by path",
        "deterministic_manifest_sha256": digest(fixture_manifest.encode()),
        "preservation_manifest": {"path": manifest_path, "sha256": digest(manifest),
            "INPUT_ARTIFACT_SOURCE_COMMIT": PRESERVATION, "affects_production_code": False},
        "scripts": scripts, "fixture_regenerated": False,
        "historical_provenance": {"transcript_sha256": "9352b967c0c6dc4d30b850420b2ac92da1773caf4113c6578fd9642e8055d217",
            "command_line": 703, "output_line": 708,
            "command_timestamp_utc": "2026-09-25T20:29:07.786Z",
            "basis": "Contemporaneous transcript identifies this run-b fixture build and exact two test files; preservation commit records each surviving fixture hash. Hashes alone do not establish provenance."},
        "limitations": ["Fixtures have no Git source commit; preserved manifest has a later source commit.",
            "No contemporaneous per-fixture hash was recorded at the historical execution; preservation hashes postdate execution."]})
    (PUBLIC / "fixture-manifest.sha256").write_text(fixture_manifest, encoding="utf-8")
    hist_env = git("cat-file", "blob", f"{PRESERVATION}:docs/identity/evidence/r1-final/scratchpad/environment_final.txt")
    (ROOT / "historical-environment.txt").write_bytes(hist_env)
    print(json.dumps({"initial_HEAD": initial["HEAD"], "clean": True,
                      "fixtures": len(fixtures), "bytes": sum(f["bytes"] for f in fixtures),
                      "manifest_sha256": digest(fixture_manifest.encode()), "scripts_match_pin": True}))


def environment():
    proc_env = os.environ.copy()
    proc_env["PYTHONPATH"] = os.pathsep.join((str(REPO), str(DEPS), str(ROOT)))
    proc_env["PYTHONDONTWRITEBYTECODE"] = "1"
    code = "import json,sys,platform,importlib.metadata as m,arpipe,pytest,jsonschema; print(json.dumps({'python_version':sys.version,'python_executable':sys.executable,'os':platform.platform(),'os_version':platform.version(),'architecture':platform.machine(),'arpipe_import':arpipe.__file__,'pytest_version':pytest.__version__,'jsonschema_version':m.version('jsonschema'),'jsonschema_import':jsonschema.__file__,'packages':{d.metadata['Name']:d.version for d in m.distributions()},'sys_path':sys.path}))"
    proc = subprocess.run([str(PYTHON), "-B", "-c", code], cwd=REPO, env=proc_env, capture_output=True, check=True)
    current = json.loads(proc.stdout)
    assert Path(current["arpipe_import"]).resolve() == (REPO / "arpipe/__init__.py").resolve()
    current["explicit_environment_overrides"] = {k: proc_env[k] for k in ("PYTHONPATH", "PYTHONDONTWRITEBYTECODE")}
    current["pytest_environment_controls"] = {k: proc_env.get(k) for k in ("PYTEST_ADDOPTS", "PYTEST_PLUGINS", "PYTEST_DISABLE_PLUGIN_AUTOLOAD")}
    current["test_only_dependency_directory"] = str(DEPS)
    current["test_only_packages"] = {d.metadata["Name"]: d.version for d in importlib.metadata.distributions(path=[str(DEPS)])}
    current["production_dependencies_installed_or_modified"] = False
    historical = (ROOT / "historical-environment.txt").read_text(encoding="utf-8")
    section = historical.split("### pip freeze (venv + TEST-ONLY PYTHONPATH)")
    hist_packages = dict(re.findall(r"^([^=\s]+)==([^\s]+)$", historical, re.M))
    canonical = lambda name: re.sub(r"[-_.]+", "-", name).lower()
    visible = {canonical(k): v for k, v in current["packages"].items()}
    current["historical_recorded_package_differences"] = {k: {"historical": v, "current": visible.get(canonical(k))}
        for k, v in hist_packages.items() if visible.get(canonical(k)) != v}
    current["historical_environment_source"] = {"commit": PRESERVATION,
        "path": "docs/identity/evidence/r1-final/scratchpad/environment_final.txt", "sha256": digest(historical.encode())}
    current["permissions_note"] = "Sandbox preflight could not read original jsonschema; approved unsandboxed execution reads existing dependencies without modification. No target claim ran during that preflight."
    return current, proc_env


def run_claim(claim):
    before = snapshot()
    assert before["HEAD"] == PIN and before["branch"] == "DETACHED_HEAD" and not before["status_porcelain"]
    env_record, proc_env = environment()
    name = "claim-" + claim.lower()
    if claim in ("A", "B"):
        cmd = [str(PYTHON), "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "-p", "pa_observer"]
        if claim == "B":
            cmd += [str(SCRATCH / "run-b/arpipe/tests/test_pipeline.py"), str(SCRATCH / "run-b/arpipe/tests/test_pm1_orderqc.py"), "-rsfE"]
        else:
            cmd += ["-rxXfEs"]
        cmd += ["--junitxml=" + str(ROOT / (name + ".xml")), "--basetemp=" + str(ROOT / (name + "-temp"))]
        proc_env["PA_OBSERVER_OUTPUT"] = str(ROOT / (name + "-observer.json"))
    else:
        cmd = [str(PYTHON), "-B", "tools/check_doc_hashes.py"]
    metadata = {"reproduction_id": "P-A-R1-20260926", "claim_id": claim,
                "EXECUTION_COMMIT": PIN, "before": before, "environment": env_record,
                "command_argv": cmd, "command_windows": subprocess.list2cmdline(cmd),
                "cwd": str(REPO), "timestamp_start_utc": now()}
    write(ROOT / (name + "-execution.json"), metadata)
    start = time.monotonic()
    with (ROOT / (name + ".stdout.txt")).open("wb") as out, (ROOT / (name + ".stderr.txt")).open("wb") as err:
        proc = subprocess.run(cmd, cwd=REPO, env=proc_env, stdout=out, stderr=err)
    metadata.update({"exit_status": proc.returncode, "wall_seconds": time.monotonic() - start,
                     "timestamp_end_utc": now(), "after": snapshot()})
    metadata["protected_working_files_unchanged"] = before["protected_working_file_manifest"] == metadata["after"]["protected_working_file_manifest"]
    write(ROOT / (name + "-execution.json"), metadata)
    print(json.dumps({"claim": claim, "exit": proc.returncode, "wall_seconds": metadata["wall_seconds"],
                      "after_HEAD": metadata["after"]["HEAD"], "after_status": metadata["after"]["status_porcelain"],
                      "protected_unchanged": metadata["protected_working_files_unchanged"]}))
    print((ROOT / (name + ".stdout.txt")).read_text(encoding="utf-8", errors="replace")[-6500:])


if __name__ == "__main__":
    if sys.argv[1] == "prepare":
        prepare()
    elif sys.argv[1] in ("A", "B", "C"):
        run_claim(sys.argv[1])
