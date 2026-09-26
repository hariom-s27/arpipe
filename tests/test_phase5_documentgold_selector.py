"""Synthetic-only tests for the pure Phase 5 DocumentGold selector."""

from __future__ import annotations

import pytest

from tools.phase5.documentgold_selector import (
    salt_commitment,
    select_overlap,
    verify_salt_commitment,
)


SYNTHETIC_ROSTER = [
    {"company_id": "ISSUER-A", "document_id": "DOC-A-2019"},
    {"company_id": "ISSUER-A", "document_id": "DOC-A-2020"},
    {"company_id": "ISSUER-B", "document_id": "DOC-B-2019"},
    {"company_id": "ISSUER-B", "document_id": "DOC-B-2020"},
    {"company_id": "ISSUER-C", "document_id": "DOC-C-2020"},
]
SALT = bytes(range(32))


def test_commit_reveal_round_trip() -> None:
    commitment = salt_commitment(SALT)
    assert len(commitment) == 64
    assert verify_salt_commitment(SALT, commitment)
    assert not verify_salt_commitment(b"x" * 32, commitment)


def test_selection_is_deterministic_and_one_per_issuer() -> None:
    first = select_overlap(SYNTHETIC_ROSTER, SALT)
    second = select_overlap(reversed(SYNTHETIC_ROSTER), SALT)
    assert first == second
    assert len(first) == 3
    assert {row.company_id for row in first} == {"ISSUER-A", "ISSUER-B", "ISSUER-C"}
    assert all(row.rank == 1 for row in first)


def test_two_per_issuer_fails_closed_when_an_issuer_has_only_one() -> None:
    with pytest.raises(ValueError, match="ISSUER-C"):
        select_overlap(SYNTHETIC_ROSTER, SALT, documents_per_issuer=2)


@pytest.mark.parametrize(
    "bad_value",
    ["INTERNAL SPACE", "TAB\tVALUE", "SLASH/VALUE", "é", ""],
)
def test_identifier_normalization_rejects_invalid_values(bad_value: str) -> None:
    with pytest.raises(ValueError):
        select_overlap(
            [{"company_id": "ISSUER-A", "document_id": bad_value}], SALT
        )


def test_normalization_aliases_are_rejected() -> None:
    with pytest.raises(ValueError, match="alias collision"):
        select_overlap(
            [
                {"company_id": "ISSUER-A", "document_id": "DOC-1"},
                {"company_id": " ISSUER-A", "document_id": "DOC-2"},
            ],
            SALT,
        )


def test_duplicate_document_ids_are_rejected() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        select_overlap(
            [
                {"company_id": "ISSUER-A", "document_id": "DOC-1"},
                {"company_id": "ISSUER-B", "document_id": "DOC-1"},
            ],
            SALT,
        )


def test_salt_must_be_exactly_32_bytes() -> None:
    with pytest.raises(ValueError, match="32 bytes"):
        select_overlap(SYNTHETIC_ROSTER, b"short")
