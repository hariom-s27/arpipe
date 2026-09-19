from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

from tools.audit_t0_4_setup import _assert_no_nondeterministic_metadata
from tools.t0_4 import closure as K
from tools.t0_4.core import canonical_json, contains_absolute_path, file_sha256, read_json

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "artifacts/t0_4/final_closure_audit.json"
REPORT = ROOT / "docs/experiments/T0.4_final_closure_audit.md"
COMMIT = re.compile(r"[0-9a-f]{40}")
STATUS_KEYS = ("vector_text_route", "sampling_cell_inspection", "sampling_metadata_provenance", "held_out_terminology")
FROZEN_SINCE_AUDIT = (
    "configs/t0_4",
    "artifacts/t0_4/benchmark_manifest.json",
    "artifacts/t0_4/config_hashes.json",
    "artifacts/t0_4/setup_audit.json",
    "dataset/corpus_freeze",
    "dataset/corpus_gap_audit",
    "arpipe",
)


@pytest.fixture(scope="module")
def record() -> dict:
    return read_json(RECORD)


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)


def test_record_commit_fields_are_unambiguous_forty_character_commits(record):
    assert record["base_commit"] == K.BASE_COMMIT
    assert record["final_commit_before_audit"] == K.PRE_CLOSURE_COMMIT
    for name in ("base_commit", "final_commit_before_audit", "final_commit_after_audit"):
        assert COMMIT.fullmatch(record[name]), name
    before, after = record["final_commit_before_audit"], record["final_commit_after_audit"]
    assert _git("merge-base", "--is-ancestor", before, after).returncode == 0
    assert _git("merge-base", "--is-ancestor", after, "HEAD").returncode == 0


def test_record_is_reproduced_byte_for_byte_from_the_audited_commit(record):
    recomputed = K.run_closure_audit(ROOT, record["final_commit_after_audit"])
    assert canonical_json(recomputed) == RECORD.read_text(encoding="utf-8")


def test_record_statuses_use_the_registered_vocabulary_and_the_decision_follows(record):
    assert all(record[key] in {K.PASS, K.PASS_SPARSE, K.UNRESOLVED, K.FAIL} for key in STATUS_KEYS)
    assert record["closure_decision"] == K.decide_closure({key: record[key] for key in STATUS_KEYS})


def test_record_holds_no_timestamp_hostname_uuid_or_absolute_path(record):
    _assert_no_nondeterministic_metadata(record)
    assert not contains_absolute_path(RECORD.read_text(encoding="utf-8"))


def test_frozen_inputs_are_unchanged_since_the_audited_commit(record):
    changed = _git("diff", "--name-only", record["final_commit_after_audit"], "--", *FROZEN_SINCE_AUDIT)
    assert changed.returncode == 0
    assert changed.stdout.split() == []


def test_recorded_hashes_match_the_committed_artifacts(record):
    assert record["sampling_manifest_hash"] == file_sha256(ROOT / K.MANIFEST)
    assert record["sampling_config_hash"] == file_sha256(ROOT / K.SAMPLING_SPEC)
    assert record["corpus_manifest_hash"] == file_sha256(ROOT / K.CORPUS_INVENTORY)


def test_report_states_every_required_closure_item(record):
    text = REPORT.read_text(encoding="utf-8")
    for number in range(1, 13):
        assert f"## {number}. " in text
    cells = record["evidence"]["sampling_cell_inspection"]
    for value in (cells["observed_cell_count"], cells["zero_availability_cell_count"], cells["declared_cell_count"]):
        assert f"{value:,}" in text
    for value in (record["closure_decision"], record["final_commit_before_audit"], record["final_commit_after_audit"]):
        assert value in text
    for key in STATUS_KEYS:
        assert f"`{key}`" in text and record[key] in text
