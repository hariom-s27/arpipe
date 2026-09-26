"""T0.4 Amendment 01 enforcement: R1 provider reconstruction, Track A scope.

Governing record: docs/identity/T0_4_AMENDMENT_01.md. This module is the source-level
regression guard the amendment calls for. The behavioural reproduction (identical page
kinds and OCR-page sets for every FIT and VALIDATION page) is the governing evidence and is
recorded in docs/identity/RUNNABLE_IDENTITY_v1.md. It is not re-run here.

Verifies:
1. The amendment record is ratified (non-blank author and date), its ratified text is
   unaltered, and it does not match the Phase 2.1 amendment glob.
2. The T0.4 base commit is read from that record and agrees with tools/t0_4/core.py.
3. The four authorized commits resolve, are full SHAs, and each touches one authorized path.
4. The set of changed arpipe/ paths against the T0.4 base is exactly the four A1-A4 paths.
5. Each authorized file equals its authorizing commit, so it differs from the T0.4 base only
   by the hunks admitted under A1-A4.
6. The Track-A protected symbols and files are byte-identical to the T0.4 base.
7. The original T0.4 guards and frozen T0.4 paths are unchanged since the forensic commit.
8. The strict expected-failure registration is complete and behaves as specified.
"""

from __future__ import annotations

import ast
import fnmatch
import hashlib
import importlib.util
import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
RECORD_PATH = "docs/identity/T0_4_AMENDMENT_01.md"
FORBIDDEN_AMENDMENT_GLOB = "docs/experiments/PHASE2.1_T0.4_AMENDMENT_*.md"

AUTHORIZED_PATHS = frozenset({
    "arpipe/models.py",
    "arpipe/triage.py",
    "arpipe/ocr.py",
    "arpipe/store.py",
})

# Authorizing commit -> the one production path it may touch (amendment section 1 order).
AUTHORIZING_COMMITS = (
    ("A1_COMMIT", "arpipe/models.py"),
    ("A2_COMMIT", "arpipe/triage.py"),
    ("A3_COMMIT", "arpipe/ocr.py"),
    ("A4_COMMIT", "arpipe/store.py"),
)

THRESHOLDS = (
    "MIN_CHARS_PER_PAGE", "MIN_CHARS_DENSE", "MAX_MOJIBAKE_RATIO", "BIG_IMAGE_AREA_FRAC",
    "HYBRID_IMAGE_AREA_FRAC", "BLANK_CHARS", "VECTOR_PATH_TEXT_THRESHOLD", "COLUMN_HIST_BINS",
    "GUTTER_MIN_RUN_FRAC", "GUTTER_PEAK_THRESHOLD", "GUTTER_SEARCH_LO", "GUTTER_SEARCH_HI",
    "DOC_SCANNED_FRAC", "DOC_DIGITAL_FRAC",
)

# (id, path, kind, name). Forensic record T0_4_GUARD_FORENSICS.md section 10.1 item 4.
PROTECTED = (
    ("triage._classify", "arpipe/triage.py", "def", "_classify"),
    ("triage.configure", "arpipe/triage.py", "def", "configure"),
    ("triage.NEEDS_OCR", "arpipe/triage.py", "assign", "NEEDS_OCR"),
    ("triage.ocr_page_numbers", "arpipe/triage.py", "def", "ocr_page_numbers"),
    *(("triage." + name, "arpipe/triage.py", "assign", name) for name in THRESHOLDS),
    ("models.PageKind", "arpipe/models.py", "class", "PageKind"),
    ("file:arpipe/configs/default.yaml", "arpipe/configs/default.yaml", "file", ""),
    ("file:arpipe/CLAUDE.md", "arpipe/CLAUDE.md", "file", ""),
    ("file:arpipe/README.md", "arpipe/README.md", "file", ""),
)

# Paths that must stay byte-identical to the forensic commit: the original T0.4 guards and
# every frozen T0.4 directory, plus the T0.4 closure record.
T0_4_FROZEN_PATHS = (
    "tools/t0_4",
    "tests/t0_4",
    "configs/t0_4",
    "artifacts/t0_4",
    "tools/audit_t0_4_setup.py",
    "tools/audit_t0_4_final_closure.py",
    "tools/build_t0_4_manifest.py",
    "docs/experiments/T0.4_final_closure_audit.md",
    "docs/experiments/T0.4_ocr_benchmark_preregistration.md",
    "docs/experiments/T0.4_p-x1_reuse_audit.md",
)

ANNEX_A_KEYS = (
    "T0_4_BASE_COMMIT", "A1_COMMIT", "A2_COMMIT", "A3_COMMIT", "A4_COMMIT",
    "FORENSIC_COMMIT", "RATIFIED_TEXT_SHA256",
)


def _git(*args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args], capture_output=True, check=True
    ).stdout


def _git_names(subcommand: str, *args: str) -> set[str]:
    out = _git(subcommand, "-z", *args).decode("utf-8")
    return {name for name in out.split("\0") if name}


def _base_blob(base: str, path: str) -> bytes:
    return _git("show", f"{base}:{path}")


def _working_bytes(path: str) -> bytes:
    """Working-tree bytes as Git would commit them.

    Undoes only a checkout-time LF -> CRLF conversion (core.autocrlf), and only when the
    committed blob itself contains no CR. Nothing else is normalised.
    """
    data = (REPO_ROOT / path).read_bytes()
    if b"\r" not in _git("show", f"HEAD:{path}"):
        data = data.replace(b"\r\n", b"\n")
    return data


def _record_text() -> str:
    return (REPO_ROOT / RECORD_PATH).read_bytes().decode("utf-8").replace("\r\n", "\n")


def _ratified_block(text: str) -> str:
    lines = text.split("\n")
    start = lines.index("~~~text")
    end = lines.index("~~~", start + 1)
    return "\n".join(lines[start + 1 : end]) + "\n"


@pytest.fixture(scope="module")
def record() -> dict[str, str]:
    text = _record_text()
    found = re.findall(r"^([A-Z0-9_]+): ([0-9a-f]{40}|[0-9a-f]{64})$", text, re.M)
    values: dict[str, str] = {}
    for key, value in found:
        assert key not in values, f"Annex A key repeated: {key}"
        values[key] = value
    assert set(values) == set(ANNEX_A_KEYS), f"Annex A keys: {sorted(values)}"
    return values


def test_amendment_record_is_ratified_and_its_text_is_unaltered(record) -> None:
    block = _ratified_block(_record_text())
    author = re.search(r"^AUTHOR:[ \t]*(\S.*)$", block, re.M)
    date = re.search(r"^DATE:[ \t]*(\d{4}-\d{2}-\d{2})[ \t]*$", block, re.M)
    changes = re.search(r"^CHANGES TO THIS DRAFT:[ \t]*(\S.*)$", block, re.M)
    assert author, "amendment record has a blank AUTHOR"
    assert date, "amendment record has a blank or malformed DATE"
    assert changes, "amendment record has a blank CHANGES TO THIS DRAFT"
    assert hashlib.sha256(block.encode("utf-8")).hexdigest() == record["RATIFIED_TEXT_SHA256"], (
        "ratified text differs from the hash recorded in Annex A"
    )
    listed_commits = re.findall(r"^    ([0-9a-f]{40})$", block, re.M)
    assert listed_commits == [record[key] for key, _ in AUTHORIZING_COMMITS]
    listed_paths = set(re.findall(r"^    (arpipe/[A-Za-z0-9_./]+\.py)$", block, re.M))
    assert listed_paths == AUTHORIZED_PATHS


def test_amendment_record_is_not_a_phase2_1_amendment_file() -> None:
    assert (REPO_ROOT / RECORD_PATH).is_file()
    assert not fnmatch.fnmatch(RECORD_PATH, FORBIDDEN_AMENDMENT_GLOB)
    assert list(REPO_ROOT.glob(FORBIDDEN_AMENDMENT_GLOB)) == []


def test_t0_4_base_commit_from_record_agrees_with_core_and_git(record) -> None:
    base = record["T0_4_BASE_COMMIT"]
    core = (REPO_ROOT / "tools/t0_4/core.py").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert re.search(rf'^BASE_COMMIT = "{base}"$', core, re.M), "record base differs from tools/t0_4/core.py"
    assert _git("rev-parse", "--verify", f"{base}^{{commit}}").decode().strip() == base
    subprocess.run(["git", "-C", str(REPO_ROOT), "merge-base", "--is-ancestor", base, "HEAD"], check=True)


@pytest.mark.parametrize(("key", "path"), AUTHORIZING_COMMITS, ids=[key for key, _ in AUTHORIZING_COMMITS])
def test_authorizing_commit_resolves_and_touches_only_its_path(record, key: str, path: str) -> None:
    sha = record[key]
    assert _git("rev-parse", "--verify", f"{sha}^{{commit}}").decode().strip() == sha, "not a full commit SHA"
    subprocess.run(["git", "-C", str(REPO_ROOT), "merge-base", "--is-ancestor", sha, "HEAD"], check=True)
    assert _git_names("diff-tree", "--no-commit-id", "--name-only", "-r", "--no-renames", sha) == {path}


def test_arpipe_change_set_is_exactly_the_four_authorized_paths(record) -> None:
    base = record["T0_4_BASE_COMMIT"]
    committed = _git_names("diff", "--name-only", "--no-renames", base, "HEAD", "--", "arpipe/")
    assert committed == AUTHORIZED_PATHS, (
        f"unauthorized: {sorted(committed - AUTHORIZED_PATHS)}; missing: {sorted(AUTHORIZED_PATHS - committed)}"
    )
    working = _git_names("diff", "--name-only", "--no-renames", base, "--", "arpipe/")
    untracked = _git_names("ls-files", "--others", "--exclude-standard", "--", "arpipe/")
    assert working <= AUTHORIZED_PATHS, f"working tree changes outside A1-A4: {sorted(working - AUTHORIZED_PATHS)}"
    assert not untracked, f"untracked files under arpipe/: {sorted(untracked)}"


@pytest.mark.parametrize(("key", "path"), AUTHORIZING_COMMITS, ids=[path for _, path in AUTHORIZING_COMMITS])
def test_authorized_file_differs_from_base_only_by_its_authorized_hunks(record, key: str, path: str) -> None:
    base, sha = record["T0_4_BASE_COMMIT"], record[key]
    assert _base_blob(f"{sha}^", path) == _base_blob(base, path), "authorizing commit did not start from the T0.4 base file"
    assert _working_bytes(path) == _base_blob(sha, path), "file differs from its authorizing commit"


def _require_uniform_newlines(data: bytes) -> None:
    assert data.count(b"\r") == data.count(b"\r\n"), "lone CR in source; line numbers would be ambiguous"


def _target_names(node: ast.AST) -> set[str]:
    if isinstance(node, ast.Assign):
        return {t.id for t in node.targets if isinstance(t, ast.Name)}
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return {node.target.id}
    return set()


def _segments(data: bytes, kind: str, name: str) -> bytes:
    """Whole source lines (trailing comments included) of every top-level definition of name."""
    _require_uniform_newlines(data)
    lines = data.split(b"\n")
    found = []
    for node in ast.parse(data).body:
        if kind == "def" and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            start = min([node.lineno, *(d.lineno for d in node.decorator_list)])
        elif kind == "class" and isinstance(node, ast.ClassDef) and node.name == name:
            start = min([node.lineno, *(d.lineno for d in node.decorator_list)])
        elif kind == "assign" and name in _target_names(node):
            start = node.lineno
        else:
            continue
        found.append(b"\n".join(lines[start - 1 : node.end_lineno]))
    return b"\n=====\n".join(found)


@pytest.mark.parametrize(("path", "kind", "name"), [p[1:] for p in PROTECTED], ids=[p[0] for p in PROTECTED])
def test_protected_source_is_byte_identical_to_the_t0_4_base(record, path: str, kind: str, name: str) -> None:
    base_data = _base_blob(record["T0_4_BASE_COMMIT"], path)
    candidate_data = _working_bytes(path)
    if kind == "file":
        assert candidate_data == base_data, f"{path} differs from the T0.4 base"
        return
    base_segment = _segments(base_data, kind, name)
    assert base_segment, f"{name} not found in the T0.4 base {path}"
    assert _segments(candidate_data, kind, name) == base_segment, f"{name} in {path} differs from the T0.4 base"


def _profile_page_parts(data: bytes) -> tuple[list[bytes], list[bytes]]:
    """Lines of profile_page up to and including 'kind = _classify(...)', and the lines after."""
    _require_uniform_newlines(data)
    lines = data.split(b"\n")
    function = next(
        n for n in ast.parse(data).body if isinstance(n, ast.FunctionDef) and n.name == "profile_page"
    )
    cut = None
    for stmt in function.body:
        if (
            isinstance(stmt, ast.Assign)
            and "kind" in _target_names(stmt)
            and isinstance(stmt.value, ast.Call)
            and isinstance(stmt.value.func, ast.Name)
            and stmt.value.func.id == "_classify"
        ):
            cut = stmt.end_lineno
    assert cut is not None, "profile_page has no 'kind = _classify(...)' statement"
    start = min([function.lineno, *(d.lineno for d in function.decorator_list)])
    return lines[start - 1 : cut], lines[cut : function.end_lineno]


def test_profile_page_classification_is_identical_and_the_rest_only_grows(record) -> None:
    base_data = _base_blob(record["T0_4_BASE_COMMIT"], "arpipe/triage.py")
    base_prefix, base_suffix = _profile_page_parts(base_data)
    cand_prefix, cand_suffix = _profile_page_parts(_working_bytes("arpipe/triage.py"))
    assert cand_prefix == base_prefix, "profile_page differs from the T0.4 base up to the classification"
    remaining = iter(cand_suffix)
    missing = [line for line in base_suffix if not any(line == other for other in remaining)]
    assert not missing, f"profile_page after classification lost or changed base lines: {missing[:3]}"


def test_original_t0_4_guards_and_frozen_paths_are_unchanged_since_the_forensic_commit(record) -> None:
    forensic = record["FORENSIC_COMMIT"]
    changed = _git_names("diff", "--name-only", "--no-renames", forensic, "--", *T0_4_FROZEN_PATHS)
    untracked = _git_names("ls-files", "--others", "--exclude-standard", "--", *T0_4_FROZEN_PATHS)
    assert not changed, f"T0.4 frozen paths changed since the forensic commit: {sorted(changed)}"
    assert not untracked, f"untracked files in frozen T0.4 paths: {sorted(untracked)}"


def _load_registration():
    spec = importlib.util.spec_from_file_location("t0_4_amendment_01_registration", REPO_ROOT / "conftest.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_expected_failure_registration_is_complete_and_cites_the_amendment() -> None:
    registration = _load_registration()
    assert registration.AUTHORIZED_A1_A4_PATHS == AUTHORIZED_PATHS
    assert set(registration.STRICT_EXPECTED_FAILURES) == {
        "tests/t0_4/test_t0_4_setup.py::test_frozen_corpus_and_history_are_unchanged",
        "tests/t0_4/test_t0_4_setup.py::test_fail_closed_setup_audit_passes",
        "tests/t0_4/test_t0_4_closure_record.py::test_frozen_inputs_are_unchanged_since_the_audited_commit",
    }
    assert "T0.4 Amendment 01" in registration.XFAIL_REASON
    assert RECORD_PATH in registration.XFAIL_REASON
    assert all(path in registration.XFAIL_REASON for path in AUTHORIZED_PATHS)
    for node_id in registration.STRICT_EXPECTED_FAILURES:
        file_part, function_name = node_id.split("::")
        tree = ast.parse((REPO_ROOT / file_part).read_bytes())
        defined = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
        assert function_name in defined, f"registered guard {node_id} no longer exists"


_FOUR = sorted(AUTHORIZED_PATHS)
_FIVE = sorted({*AUTHORIZED_PATHS, "arpipe/verify.py"})
_PROTECTED_MESSAGE = "frozen historical paths changed: " + repr(_FOUR)
_AUDIT_STATEMENT = "assert changed.stdout.split() == []"


@pytest.mark.parametrize(
    ("kind", "exc_type", "message", "statement", "violation", "expected"),
    [
        ("protected_paths", "SetupInvariantError", _PROTECTED_MESSAGE, "", _FOUR, "xfail"),
        ("frozen_since_audit", "AssertionError", "", _AUDIT_STATEMENT, _FOUR, "xfail"),
        ("protected_paths", None, "", "", None, "xpass"),
        ("frozen_since_audit", None, "", "", None, "xpass"),
        ("protected_paths", "SetupInvariantError", "frozen historical paths changed: " + repr(_FIVE), "", _FIVE, "fail"),
        ("frozen_since_audit", "AssertionError", "", _AUDIT_STATEMENT, _FIVE, "fail"),
        ("protected_paths", "SetupInvariantError", "frozen historical paths changed: " + repr(_FOUR[:3]), "", _FOUR[:3], "fail"),
        ("protected_paths", "KeyError", _PROTECTED_MESSAGE, "", _FOUR, "fail"),
        ("protected_paths", "SetupInvariantError", "another invariant failed", "", _FOUR, "fail"),
        ("protected_paths", "SetupInvariantError", _PROTECTED_MESSAGE, "", None, "fail"),
        ("frozen_since_audit", "AssertionError", "", "assert changed.returncode == 0", _FOUR, "fail"),
        ("frozen_since_audit", "KeyError", "", _AUDIT_STATEMENT, _FOUR, "fail"),
    ],
    ids=[
        "protected-violation-is-xfail", "audit-violation-is-xfail", "protected-pass-is-xpass",
        "audit-pass-is-xpass", "protected-fifth-path-fails", "audit-fifth-path-fails",
        "protected-missing-path-fails", "protected-wrong-exception-fails", "protected-other-message-fails",
        "protected-unknown-violation-fails", "audit-other-assertion-fails", "audit-wrong-exception-fails",
    ],
)
def test_strict_expected_failure_semantics(kind, exc_type, message, statement, violation, expected) -> None:
    verdict = _load_registration().judge_guard(kind, exc_type, message, statement, violation)
    assert verdict == expected
