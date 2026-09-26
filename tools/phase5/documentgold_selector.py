"""Pure commit-reveal selector for VALIDATION DocumentGold overlap.

This module deliberately performs no file, network, clock, or random-number I/O.
The caller supplies a parsed roster and, after reveal, the 32-byte salt.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
import hashlib
import hmac
import re


DOMAIN = b"arpipe-documentgold-validation-overlap-v2"
_IDENTIFIER = re.compile(r"^[A-Za-z0-9._-]+$")


@dataclass(frozen=True, slots=True)
class Selection:
    """One selected, normalized roster row and its reproducible rank digest."""

    company_id: str
    document_id: str
    digest_hex: str
    rank: int


def salt_commitment(salt: bytes) -> str:
    """Return the lowercase SHA-256 commitment for an exactly 32-byte salt."""

    salt_bytes = _validate_salt(salt)
    return hashlib.sha256(salt_bytes).hexdigest()


def verify_salt_commitment(salt: bytes, commitment: str) -> bool:
    """Verify a reveal against a canonical lowercase 64-hex commitment."""

    if not isinstance(commitment, str) or not re.fullmatch(r"[0-9a-f]{64}", commitment):
        return False
    return hmac.compare_digest(salt_commitment(salt), commitment)


def select_overlap(
    roster: Iterable[Mapping[str, str]],
    salt: bytes,
    *,
    documents_per_issuer: int = 1,
) -> tuple[Selection, ...]:
    """Select a deterministic salted prefix independently within each issuer.

    The default guarantees exactly one document per issuer. If a future signed
    method choice requests two, every issuer must have two eligible documents;
    otherwise the function fails closed instead of silently changing the design.
    """

    salt_bytes = _validate_salt(salt)
    if isinstance(documents_per_issuer, bool) or not isinstance(documents_per_issuer, int):
        raise TypeError("documents_per_issuer must be an integer")
    if documents_per_issuer < 1:
        raise ValueError("documents_per_issuer must be at least one")

    normalized: list[tuple[str, str]] = []
    seen_documents: set[str] = set()
    raw_company_by_normalized: dict[str, str] = {}
    raw_document_by_normalized: dict[str, str] = {}

    for index, row in enumerate(roster):
        if not isinstance(row, Mapping):
            raise TypeError(f"roster row {index} is not a mapping")
        try:
            raw_document = row["document_id"]
            raw_company = row["company_id"]
        except KeyError as exc:
            raise ValueError(f"roster row {index} lacks {exc.args[0]}") from exc

        document_id = _normalize_identifier(raw_document, "document_id", index)
        company_id = _normalize_identifier(raw_company, "company_id", index)
        _reject_alias(raw_document_by_normalized, document_id, raw_document, "document_id")
        _reject_alias(raw_company_by_normalized, company_id, raw_company, "company_id")

        if document_id in seen_documents:
            raise ValueError(f"duplicate normalized document_id: {document_id}")
        seen_documents.add(document_id)
        normalized.append((company_id, document_id))

    if not normalized:
        raise ValueError("roster must contain at least one row")

    by_issuer: dict[str, list[tuple[bytes, str]]] = {}
    for company_id, document_id in normalized:
        preimage = (
            DOMAIN
            + b"\x00"
            + salt_bytes
            + b"\x00"
            + company_id.encode("utf-8")
            + b"\x00"
            + document_id.encode("utf-8")
        )
        digest = hashlib.sha256(preimage).digest()
        by_issuer.setdefault(company_id, []).append((digest, document_id))

    selections: list[Selection] = []
    for company_id in sorted(by_issuer, key=lambda value: value.encode("utf-8")):
        ranked = sorted(
            by_issuer[company_id],
            key=lambda item: (item[0], item[1].encode("utf-8")),
        )
        if len(ranked) < documents_per_issuer:
            raise ValueError(
                f"issuer {company_id} has {len(ranked)} documents; "
                f"{documents_per_issuer} requested"
            )
        for rank, (digest, document_id) in enumerate(
            ranked[:documents_per_issuer], start=1
        ):
            selections.append(
                Selection(
                    company_id=company_id,
                    document_id=document_id,
                    digest_hex=digest.hex(),
                    rank=rank,
                )
            )

    return tuple(selections)


def _validate_salt(salt: bytes) -> bytes:
    if not isinstance(salt, bytes):
        raise TypeError("salt must be bytes")
    if len(salt) != 32:
        raise ValueError("salt must contain exactly 32 bytes")
    return salt


def _normalize_identifier(value: str, field: str, index: int) -> str:
    if not isinstance(value, str):
        raise TypeError(f"roster row {index} {field} must be a string")
    normalized = value.strip(" ")
    if not normalized:
        raise ValueError(f"roster row {index} {field} is empty")
    if _IDENTIFIER.fullmatch(normalized) is None:
        raise ValueError(f"roster row {index} {field} is not an ASCII identifier")
    return normalized


def _reject_alias(
    observed: dict[str, str], normalized: str, raw: str, field: str
) -> None:
    previous = observed.setdefault(normalized, raw)
    if previous != raw:
        raise ValueError(
            f"normalization alias collision for {field}: {previous!r} and {raw!r}"
        )
