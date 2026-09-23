"""Tests for tools/check_doc_hashes.py (Phase 2.1 P0b hash-lint)."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOL_PATH = REPO_ROOT / "tools" / "check_doc_hashes.py"

_spec = importlib.util.spec_from_file_location("check_doc_hashes", TOOL_PATH)
check_doc_hashes = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = check_doc_hashes
_spec.loader.exec_module(check_doc_hashes)


def _init_git_repo(root: Path) -> None:
    for cmd in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "test@example.com"],
        ["git", "config", "user.name", "Test"],
    ):
        subprocess.run(cmd, cwd=root, check=True, capture_output=True)


def _commit_file(root: Path, rel_path: str, content: bytes) -> str:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    subprocess.run(["git", "add", rel_path], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-q", "-m", f"add {rel_path}"], cwd=root, check=True, capture_output=True)
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _write_doc(root: Path, artifact_path: str, source_commit: str, source_path: str, recorded_hash: str) -> Path:
    doc_path = root / "docs" / "experiments" / "PHASE2.1_FIXTURE.md"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(
        "# Fixture\n\n"
        "| Artifact path | Verified Git SHA-256 | Source commit | Source path | Status |\n"
        "|---|---|---|---|---|\n"
        f"| `{artifact_path}` | `{recorded_hash}` | `{source_commit}` | `{source_path}` | test |\n",
        encoding="utf-8",
    )
    return doc_path


def _write_allowlist(root: Path, doc_rel: str, source_commit: str, source_path: str, reason: str = "test") -> Path:
    allowlist_path = root / "allowlist.json"
    allowlist_path.write_text(json.dumps({
        "exceptions": [{
            "doc": doc_rel,
            "source_commit": source_commit,
            "source_path": source_path,
            "reason": reason,
        }]
    }), encoding="utf-8")
    return allowlist_path


# --- helper unit tests ---------------------------------------------------

def test_split_row_strips_outer_pipes_and_whitespace():
    cells = check_doc_hashes._split_row("| a | b | c |")
    assert cells == ["a", "b", "c"]


def test_clean_cell_strips_backticks_and_whitespace():
    assert check_doc_hashes._clean_cell(" `abc123` ") == "abc123"


def test_find_col_matches_case_insensitively():
    headers = ["Artifact path", "Verified Git SHA-256", "Source commit", "Source path"]
    assert check_doc_hashes._find_col(headers, check_doc_hashes.HASH_COL_MARKERS) == 1
    assert check_doc_hashes._find_col(headers, check_doc_hashes.COMMIT_COL_MARKERS) == 2
    assert check_doc_hashes._find_col(headers, check_doc_hashes.PATH_COL_MARKERS) == 3


def test_find_col_returns_none_when_absent():
    headers = ["Quantity", "Value"]
    assert check_doc_hashes._find_col(headers, check_doc_hashes.HASH_COL_MARKERS) is None


def test_is_separator_row_detects_dashes():
    assert check_doc_hashes._is_separator_row(["---", ":---", "---:", "---"])
    assert not check_doc_hashes._is_separator_row(["abc", "---"])


# --- extract_hash_rows -----------------------------------------------------

def test_extract_hash_rows_parses_pc06_style_table(tmp_path):
    commit = "a" * 40
    digest = "b" * 64
    _write_doc(tmp_path, "some/file.csv", commit, "some/file.csv", digest)

    rows = check_doc_hashes.extract_hash_rows(
        tmp_path / "docs" / "experiments" / "PHASE2.1_FIXTURE.md", tmp_path
    )

    assert len(rows) == 1
    row = rows[0]
    assert row.source_commit == commit
    assert row.source_path == "some/file.csv"
    assert row.recorded_hash == digest
    assert row.artifact_path == "some/file.csv"


def test_extract_hash_rows_ignores_tables_without_required_columns(tmp_path):
    doc_path = tmp_path / "docs" / "experiments" / "PHASE2.1_OTHER.md"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(
        "| Quantity | Value |\n|---|---|\n| Blob length | 2905 bytes |\n",
        encoding="utf-8",
    )
    assert check_doc_hashes.extract_hash_rows(doc_path, tmp_path) == []


def test_extract_hash_rows_skips_rows_with_malformed_commit_or_hash(tmp_path):
    doc_path = tmp_path / "docs" / "experiments" / "PHASE2.1_BAD.md"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(
        "| Artifact path | Verified Git SHA-256 | Source commit | Source path | Status |\n"
        "|---|---|---|---|---|\n"
        "| `f` | `not-a-hash` | `not-a-commit` | `f` | test |\n",
        encoding="utf-8",
    )
    assert check_doc_hashes.extract_hash_rows(doc_path, tmp_path) == []


# --- git_blob_sha256 ---------------------------------------------------

def test_git_blob_sha256_matches_recomputed_hash(tmp_path):
    _init_git_repo(tmp_path)
    content = b"hello world\n"
    commit = _commit_file(tmp_path, "greeting.txt", content)

    import hashlib
    expected = hashlib.sha256(content).hexdigest()

    assert check_doc_hashes.git_blob_sha256(commit, "greeting.txt", tmp_path) == expected


def test_git_blob_sha256_raises_on_missing_path(tmp_path):
    _init_git_repo(tmp_path)
    commit = _commit_file(tmp_path, "greeting.txt", b"hi\n")
    with pytest.raises(subprocess.CalledProcessError):
        check_doc_hashes.git_blob_sha256(commit, "does_not_exist.txt", tmp_path)


# --- check_docs / allowlist / main --------------------------------------

def test_check_docs_passes_when_recorded_hash_matches(tmp_path):
    _init_git_repo(tmp_path)
    content = b"consistent bytes\n"
    commit = _commit_file(tmp_path, "data.csv", content)
    import hashlib
    digest = hashlib.sha256(content).hexdigest()
    _write_doc(tmp_path, "data.csv", commit, "data.csv", digest)

    results = check_doc_hashes.check_docs(repo_root=tmp_path, allowlist_path=tmp_path / "missing_allowlist.json")

    assert len(results) == 1
    assert results[0]["ok"] is True
    assert results[0]["allowed"] is False


def test_check_docs_fails_when_recorded_hash_is_wrong(tmp_path):
    _init_git_repo(tmp_path)
    content = b"consistent bytes\n"
    commit = _commit_file(tmp_path, "data.csv", content)
    wrong_digest = "0" * 64
    _write_doc(tmp_path, "data.csv", commit, "data.csv", wrong_digest)

    results = check_doc_hashes.check_docs(repo_root=tmp_path, allowlist_path=tmp_path / "missing_allowlist.json")

    assert len(results) == 1
    assert results[0]["ok"] is False
    assert results[0]["allowed"] is False


def test_check_docs_allowlisted_mismatch_is_not_an_unallowed_failure(tmp_path):
    _init_git_repo(tmp_path)
    content = b"consistent bytes\n"
    commit = _commit_file(tmp_path, "data.csv", content)
    wrong_digest = "0" * 64
    _write_doc(tmp_path, "data.csv", commit, "data.csv", wrong_digest)
    allowlist_path = _write_allowlist(tmp_path, "docs/experiments/PHASE2.1_FIXTURE.md", commit, "data.csv")

    results = check_doc_hashes.check_docs(repo_root=tmp_path, allowlist_path=allowlist_path)

    assert len(results) == 1
    assert results[0]["ok"] is False
    assert results[0]["allowed"] is True


def test_main_returns_zero_when_all_hashes_match(tmp_path, capsys):
    _init_git_repo(tmp_path)
    content = b"consistent bytes\n"
    commit = _commit_file(tmp_path, "data.csv", content)
    import hashlib
    digest = hashlib.sha256(content).hexdigest()
    _write_doc(tmp_path, "data.csv", commit, "data.csv", digest)

    rc = check_doc_hashes.main([
        "--repo-root", str(tmp_path),
        "--allowlist", str(tmp_path / "missing_allowlist.json"),
    ])
    out = capsys.readouterr().out

    assert rc == 0
    assert "1 hash claim(s)" in out
    assert "0 unallowed failure(s)" in out


def test_main_returns_nonzero_when_a_hash_mismatches_and_is_not_allowlisted(tmp_path, capsys):
    _init_git_repo(tmp_path)
    content = b"consistent bytes\n"
    commit = _commit_file(tmp_path, "data.csv", content)
    _write_doc(tmp_path, "data.csv", commit, "data.csv", "0" * 64)

    rc = check_doc_hashes.main([
        "--repo-root", str(tmp_path),
        "--allowlist", str(tmp_path / "missing_allowlist.json"),
    ])
    out = capsys.readouterr().out

    assert rc == 1
    assert "1 unallowed failure(s)" in out


# --- regression guard against the real frozen Phase 2.1 docs -----------

def test_real_provenance_corrections_table_has_zero_unallowed_failures():
    """Regression guard: PHASE2.1_PROVENANCE_CORRECTIONS.md Section 3 (PC-06) must keep
    citing hashes that match the actual Git blobs it names — the exact error class PC-05/
    PC-06 corrected."""
    results = check_doc_hashes.check_docs()

    doc = "docs/experiments/PHASE2.1_PROVENANCE_CORRECTIONS.md"
    pc06_rows = [r for r in results if r["row"].doc == doc]

    assert len(pc06_rows) == 10, f"expected 10 PC-06 hash rows, found {len(pc06_rows)}"
    failures = [r for r in pc06_rows if not r["ok"] and not r["allowed"]]
    assert failures == [], [
        (r["row"].source_path, r["row"].recorded_hash, r["actual"]) for r in failures
    ]


def test_real_allowlist_file_is_valid_json_with_empty_exceptions():
    data = json.loads(check_doc_hashes.DEFAULT_ALLOWLIST.read_text(encoding="utf-8"))
    assert data["exceptions"] == []
