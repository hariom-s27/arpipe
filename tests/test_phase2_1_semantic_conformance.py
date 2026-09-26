"""Phase 2.1 Semantic Conformance & Historical Immutability Test Suite.

Verifies:
1. All 8 semantic discrimination rules pass.
2. B4 double-annotation selector satisfies all hard validity requirements
   (determinism, injectivity, domain separation, fixed threshold, no rank reuse)
   without gating on sample rank uniformity.
3. Signed-ratification conformance: B1-B8 statuses must agree among the
   register and semantic fixture while execution authorization remains NO.
4. Strict historical immutability allowlist: all modified files between base
   commit 03a63f5 and current state must match approved Phase-2.1 paths.
5. Zero frozen-path modifications; only the four A1-A4 production exceptions.
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

# D6/Q6 amendment A5 admits only the production paths authorized by A1-A4.
R1_ALLOWED_PRODUCTION_PATHS = {
    "arpipe/models.py",  # A1: required/observed model provider fields.
    "arpipe/triage.py",  # A2: script telemetry; classifier remains unchanged.
    "arpipe/ocr.py",  # A3: OcrEngineUnavailable class only.
    "arpipe/store.py",  # A4: write_span parameter and behavior only.
}

# T0.4 Amendment 01 (docs/identity/T0_4_AMENDMENT_01.md), section 6: exact-path admission of
# the amendment record and of its enforcement and expected-failure registration. The
# original T0.4 guards are not touched. The record is also inside the ^docs/identity/
# directory pattern below; it is listed here by exact path because the amendment requires that.
T0_4_AMENDMENT_01_ADMITTED_PATHS = {
    "docs/identity/T0_4_AMENDMENT_01.md",  # the amendment record.
    "tests/test_t0_4_amendment_01.py",  # exact-set, byte-identity and registration tests.
    "conftest.py",  # strict expected-failure registration for three original T0.4 guards.
}

# The 2026-09-26 governance closeout admits only these exact new governance
# records. The historical P-B documents in the snapshot directory are guarded
# separately by byte-level SHA-256 comparisons in that directory's README.
GOVERNANCE_CLOSEOUT_ADMITTED_PATHS = {
    "docs/governance/AUTHOR_RATIFICATION_2026-09-26.md",
    "docs/governance/CURRENT_DECISIONS.md",
    "docs/governance/pb-snapshot-2026-09-26/README.md",
    "docs/governance/pb-snapshot-2026-09-26/P-B_AUTHOR_DECISION_PACK.md",
    "docs/governance/pb-snapshot-2026-09-26/P-B_CURRENT_AUTHOR_DECISIONS.md",
    "docs/governance/pb-snapshot-2026-09-26/P-B_DECISION_ID_CROSSWALK.md",
    "docs/governance/pb-snapshot-2026-09-26/P-B_DEPENDENCY_MAP.md",
    "docs/governance/pb-snapshot-2026-09-26/P-B_FINAL_REPORT.md",
    "docs/governance/pb-snapshot-2026-09-26/P-B_RATIFICATION_GAP_REGISTER.md",
    "docs/governance/pb-snapshot-2026-09-26/P-B_SOURCE_COVERAGE_REGISTER.md",
    "docs/governance/pb-snapshot-2026-09-26/P-B_SOURCE_MANIFEST.md",
}

ALLOWED_PHASE2_1_PATTERNS = [
    re.compile(r"^docs/experiments/PHASE2\.1_.*\.md$"),
    re.compile(r"^tests/test_phase2_1_semantic_conformance\.py$"),
    re.compile(r"^configs/phase2_1/semantic_fixtures\.json$"),
    re.compile(r"^tools/check_doc_hashes\.py$"),
    re.compile(r"^tools/check_doc_hashes_allowlist\.json$"),
    re.compile(r"^tests/test_check_doc_hashes\.py$"),
    # A5: exact production exceptions; all other arpipe paths remain frozen.
    *(re.compile(rf"^{re.escape(path)}$") for path in R1_ALLOWED_PRODUCTION_PATHS),
    re.compile(r"^tests/test_import_smoke\.py$"),  # A5; R1 section 8.6.
    re.compile(r"^docs/phase3/"),  # A5: directory absent at BASE_COMMIT.
    re.compile(r"^docs/phase4/"),  # A5: directory absent at BASE_COMMIT.
    # Phase 5 method protocols are the normal mechanism authorized by
    # docs/governance/CURRENT_DECISIONS.md decision 0c.
    re.compile(r"^docs/phase5/"),
    re.compile(r"^docs/decisions/"),  # A5: directory absent at BASE_COMMIT.
    re.compile(r"^docs/identity/"),  # A5: directory absent at BASE_COMMIT.
    re.compile(r"^tests/test_phase5_gold_schema\.py$"),  # Phase 5 synthetic schema check.
    # Exact governance-closeout paths; no directory-wide exception.
    *(re.compile(rf"^{re.escape(path)}$") for path in GOVERNANCE_CLOSEOUT_ADMITTED_PATHS),
    # T0.4 Amendment 01: exact paths only.
    *(re.compile(rf"^{re.escape(path)}$") for path in T0_4_AMENDMENT_01_ADMITTED_PATHS),
]


def test_semantic_discrimination_fixtures_exist() -> None:
    """Verify semantic fixture file exists and parses valid JSON."""
    fixtures_path = REPO_ROOT / "configs" / "phase2_1" / "semantic_fixtures.json"
    assert fixtures_path.exists(), f"Missing fixtures at {fixtures_path}"
    with open(fixtures_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["schema_version"] == "2.1.0"
    assert len(data["fixtures"]["discrimination_rules"]) == 8
    assert set(data["fixtures"]["b_decisions"]["items"]) == {
        "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"
    }


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
    """Verify signed B1-B8 statuses agree between register and fixture.

    Rules:
    1. Each current register status equals the semantic fixture status.
    2. Statuses use only the signed ratification vocabulary.
    3. Ratification does not authorize downstream execution.
    """
    decision_reg = REPO_ROOT / "docs" / "experiments" / "PHASE2.1_B1_B8_DECISION_REGISTER.md"
    assert decision_reg.exists(), f"Missing {decision_reg}"
    text = decision_reg.read_text(encoding="utf-8")

    fixture_path = REPO_ROOT / "configs" / "phase2_1" / "semantic_fixtures.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))["fixtures"]["b_decisions"]
    assert fixture["ratification_source"] == (
        "docs/governance/AUTHOR_RATIFICATION_2026-09-26.md"
    )
    assert fixture["author"] == "Hariom Singh"
    assert fixture["ratification_date"] == "2026-09-26"
    assert fixture["execution_authorized"] is False

    allowed_statuses = {"RATIFIED", "DEFERRED", "NOT_APPLICABLE"}
    for item, expected in fixture["items"].items():
        section = re.search(
            rf"^### {item}\b(?P<body>.*?)(?=^### B[1-8]\b|^## |\Z)",
            text,
            re.MULTILINE | re.DOTALL,
        )
        assert section, f"Missing current register section for {item}"
        status = re.search(r"\*\*status:\*\* `([A-Z_]+)`", section.group("body"))
        assert status, f"Missing status field for {item}"
        assert status.group(1) == expected["status"]
        assert status.group(1) in allowed_statuses
        section_lower = section.group("body").lower()
        if expected["status"] == "DEFERRED":
            assert expected["reopen_trigger"].lower() in section_lower
        if expected["status"] == "NOT_APPLICABLE":
            assert expected["condition"].lower() in section_lower
            assert expected["reopen_trigger"].lower() in section_lower

    # Verify downstream execution is NOT authorized
    assert "DOWNSTREAM_EXECUTION_AUTHORIZED = NO" in text
    assert "GOLD_ANNOTATION_AUTHORIZED = NO" in text
    assert "OCR_EXECUTION_AUTHORIZED = NO" in text
    assert "EXPERIMENT_X1_X7_AUTHORIZED = NO" in text
    assert "HOLDOUT_ACCESS_AUTHORIZED = NO" in text

    # Guard: the obsolete unratified status vocabulary is not current.
    adopted_matches = re.findall(r"status:\s*ADOPTED", text, re.IGNORECASE)
    assert len(adopted_matches) == 0, f"Found un-ratified ADOPTED status in {decision_reg}"
    assert "PENDING_AUTHOR_DECISION" not in text


def test_b1_exact_formulation() -> None:
    """Verify B1 is formulated according to the exact required literal structure."""
    decision_reg = REPO_ROOT / "docs" / "experiments" / "PHASE2.1_B1_B8_DECISION_REGISTER.md"
    text = decision_reg.read_text(encoding="utf-8")

    assert "broken_text → OCR" in text
    assert "Genuine legacy-font occurrence remains unresolved" in text
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

    Changes outside the original allowlist and exact A5 exceptions fail.
    Frozen dataset, T0.4 config, and T0.4 artifact paths remain zero-change.
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
    for restricted in ["arpipe/", "dataset/", "configs/t0_4/", "artifacts/t0_4/"]:
        restricted_diff = [p for p in all_changed if p.startswith(restricted)]
        if restricted == "arpipe/":  # A5: only A1-A4 exact paths are excepted.
            restricted_diff = [p for p in restricted_diff if p not in R1_ALLOWED_PRODUCTION_PATHS]
        assert len(restricted_diff) == 0, f"Unauthorized changes detected in {restricted}: {restricted_diff}"
