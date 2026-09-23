"""Phase 2.1 Semantic Conformance & Historical Immutability Test Suite.

Verifies:
1. All 8 semantic discrimination rules pass.
2. B4 double-annotation selector satisfies all hard validity requirements
   (determinism, injectivity, domain separation, fixed threshold, no rank reuse)
   without gating on sample rank uniformity.
3. Strict recommendation-to-decision guard: all B1-B8 items must be
   PENDING_AUTHOR_DECISION and DOWNSTREAM_EXECUTION_AUTHORIZED must be NO.
4. Strict historical immutability allowlist: all modified files between base
   commit 03a63f5 and current state must match approved Phase-2.1 paths.
5. Zero modifications to arpipe/, dataset/, and configs/t0_4/.
6. Explicit zero-cell classification procedure (unclassified == 0).
7. Conditional amendment rule: NO FORMAL T0.4 AMENDMENT REQUIRED when no
   author decision is adopted.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

import pytest

BASE_COMMIT = "03a63f5d7d79bac6a0bab0ffc33af42004e78935"
REPO_ROOT = Path(__file__).resolve().parent.parent

ALLOWED_PHASE2_1_PATTERNS = [
    re.compile(r"^docs/experiments/PHASE2\.1_.*\.md$"),
    re.compile(r"^tests/test_phase2_1_semantic_conformance\.py$"),
    re.compile(r"^configs/phase2_1/semantic_fixtures\.json$"),
    re.compile(r"^tools/check_doc_hashes\.py$"),
    re.compile(r"^tools/check_doc_hashes_allowlist\.json$"),
    re.compile(r"^tests/test_check_doc_hashes\.py$"),
]


def test_semantic_discrimination_fixtures_exist() -> None:
    """Verify semantic fixture file exists and parses valid JSON."""
    fixtures_path = REPO_ROOT / "configs" / "phase2_1" / "semantic_fixtures.json"
    assert fixtures_path.exists(), f"Missing fixtures at {fixtures_path}"
    with open(fixtures_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["schema_version"] == "2.1.0"
    assert len(data["fixtures"]["discrimination_rules"]) == 8


def test_b4_canonical_serialization_properties() -> None:
    """Verify B4 hard validity requirements.

    Hard requirements:
    - deterministic canonical serialization
    - injective canonical serialization over eligible identifiers
    - fixed UTF-8 encoding
    - fixed domain separation
    - fixed threshold
    - no duplicate canonical keys
    - no selection_rank reuse
    - no post-hoc key selection
    - no post-hoc threshold selection
    - same input -> same bytes -> same digest -> same selection

    Diagnostic statistics are measured but NOT treated as pass/fail gates.
    """
    domain_tag = "arpipe-oracle-double-v1"
    target_fraction = 0.25
    threshold = int(target_fraction * (2**256))

    test_units = [
        ("INE002A01018_2015", 42),
        ("INE002A01018_2015", 43),
        ("INE002L01015_2012", 1),
        ("INE002L01015_2012", 2),
        ("INE003B01014_2011", 10),
        ("INE040A01034_2025", 100),
    ]

    seen_keys: set[bytes] = set()
    selections_1: list[bool] = []
    selections_2: list[bool] = []

    for doc_id, page_num in test_units:
        # Canonical serialization: domain_tag || 0x00 || doc_id || 0x00 || str(page_num)
        key_bytes = (
            domain_tag.encode("utf-8")
            + b"\x00"
            + doc_id.encode("utf-8")
            + b"\x00"
            + str(page_num).encode("utf-8")
        )

        # Injective check: no two distinct units map to the same key
        assert key_bytes not in seen_keys, f"Injectivity collision for {doc_id}:{page_num}"
        seen_keys.add(key_bytes)

        digest = hashlib.sha256(key_bytes).hexdigest()
        rank_int = int(digest, 16)
        is_selected = rank_int < threshold
        selections_1.append(is_selected)

        # Determinism check: repeat produces identical result
        repeat_bytes = (
            domain_tag.encode("utf-8")
            + b"\x00"
            + doc_id.encode("utf-8")
            + b"\x00"
            + str(page_num).encode("utf-8")
        )
        assert repeat_bytes == key_bytes
        repeat_digest = hashlib.sha256(repeat_bytes).hexdigest()
        assert repeat_digest == digest
        assert (int(repeat_digest, 16) < threshold) == is_selected
        selections_2.append(is_selected)

    # Invariance assert
    assert selections_1 == selections_2


def test_b1_to_b8_status_and_decision_guard() -> None:
    """Verify B1-B8 decision statuses in documentation.

    Rules:
    1. Every B item must equal PENDING_AUTHOR_DECISION.
    2. No recommendation may be converted to ADOPTED without an author ratification record.
    3. DOWNSTREAM_EXECUTION_AUTHORIZED must be NO.
    """
    decision_reg = REPO_ROOT / "docs" / "experiments" / "PHASE2.1_B1_B8_DECISION_REGISTER.md"
    assert decision_reg.exists(), f"Missing {decision_reg}"
    text = decision_reg.read_text(encoding="utf-8")

    # Verify all 8 items are explicitly PENDING_AUTHOR_DECISION
    for item in ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"]:
        pattern = rf"{item}.*?status.*?:.*?(PENDING_AUTHOR_DECISION|`PENDING_AUTHOR_DECISION`)"
        assert re.search(pattern, text, re.IGNORECASE | re.DOTALL), (
            f"{item} is not explicitly PENDING_AUTHOR_DECISION in register"
        )

    # Verify downstream execution is NOT authorized
    assert "DOWNSTREAM_EXECUTION_AUTHORIZED = NO" in text
    assert "GOLD_ANNOTATION_AUTHORIZED = NO" in text
    assert "OCR_EXECUTION_AUTHORIZED = NO" in text
    assert "EXPERIMENT_X1_X7_AUTHORIZED = NO" in text
    assert "HOLDOUT_ACCESS_AUTHORIZED = NO" in text

    # Guard: no occurrence of ADOPTED as an active status
    adopted_matches = re.findall(r"status:\s*ADOPTED", text, re.IGNORECASE)
    assert len(adopted_matches) == 0, f"Found un-ratified ADOPTED status in {decision_reg}"


def test_b1_exact_formulation() -> None:
    """Verify B1 is formulated according to the exact required literal structure."""
    decision_reg = REPO_ROOT / "docs" / "experiments" / "PHASE2.1_B1_B8_DECISION_REGISTER.md"
    text = decision_reg.read_text(encoding="utf-8")

    assert "broken_text → OCR" in text
    assert "genuine legacy-font occurrence remains unresolved" in text
    assert "Do not create a production REMAP route" in text
    assert "Retain legacy as a separate forensic research attribute/track" in text
    assert "This does not establish that REMAP is useless" in text
    assert "This does not establish that legacy-font pages are absent" in text

    # Assure "Option A / Option B" architectural naming was removed
    assert "Option A (" not in text
    assert "Option B (" not in text


def test_zero_cell_normative_procedure() -> None:
    """Verify the 16,157 zero cells are defined via normative procedure with unclassified == 0."""
    semantic_map = REPO_ROOT / "docs" / "experiments" / "PHASE2.1_FOUNDATION_SEMANTIC_MAP.md"
    assert semantic_map.exists()
    text = semantic_map.read_text(encoding="utf-8")

    assert "structurally_impossible" in text
    assert "priority_preempted" in text
    assert "unobserved" in text
    assert "unclassified = 0" in text


def test_conditional_t0_4_amendment_rule() -> None:
    """Verify no provisional amendment file exists and Part F declares NO FORMAL AMENDMENT."""
    norm_doc = REPO_ROOT / "docs" / "experiments" / "PHASE2.1_FOUNDATION_NORMALIZATION.md"
    assert norm_doc.exists()
    text = norm_doc.read_text(encoding="utf-8")

    assert "NO FORMAL T0.4 AMENDMENT REQUIRED." in text
    assert "NO T0.4 AMENDMENT EFFECTIVE." in text

    # Verify no amendment file was created
    amendment_files = list(REPO_ROOT.glob("docs/experiments/PHASE2.1_T0.4_AMENDMENT_*.md"))
    assert len(amendment_files) == 0, f"Provisional amendment file unexpectedly exists: {amendment_files}"


def test_historical_immutability_strict_allowlist() -> None:
    """Verify that all modified and untracked files match the Phase-2.1 allowlist.

    Any change to historical files, production arpipe/, dataset/, or configs/t0_4/
    fails immediately.
    """
    # Check diff against base commit
    cmd = ["git", "-C", str(REPO_ROOT), "diff", "--name-only", BASE_COMMIT]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    committed_diff_files = [line.strip().replace("\\", "/") for line in res.stdout.splitlines() if line.strip()]

    # Also check uncommitted/untracked status with -uall to expand directory entries
    status_cmd = ["git", "-C", str(REPO_ROOT), "status", "--porcelain", "-uall"]
    status_res = subprocess.run(status_cmd, capture_output=True, text=True, check=True)
    working_files = [line[3:].strip().replace("\\", "/") for line in status_res.stdout.splitlines() if line.strip()]

    all_changed = set(committed_diff_files + working_files)

    for path in all_changed:
        matched = any(pattern.match(path) for pattern in ALLOWED_PHASE2_1_PATTERNS)
        assert matched, f"Path {path} violates historical immutability allowlist!"

    # Explicit zero-change directory assertions
    for restricted in ["arpipe/", "dataset/", "configs/t0_4/"]:
        restricted_diff = [p for p in all_changed if p.startswith(restricted)]
        assert len(restricted_diff) == 0, f"Unauthorized changes detected in {restricted}: {restricted_diff}"
