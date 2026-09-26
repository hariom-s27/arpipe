"""Validate the Phase 5 draft Gold schema against exactly three synthetic records."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "docs" / "phase5" / "gold_schema_v0.json"


def _provenance(workspace: str) -> dict[str, object]:
    return {
        "annotation_workspace_id": workspace,
        "viewer_name": "Synthetic Offline Viewer",
        "viewer_version": "0.0-test",
        "physical_page_count": 40,
        "search_queries": ["invented query"],
        "bookmark_pages": [2],
        "flag_pages": {},
        "visible_parent_heading": None,
        "conditional_title_context": None,
        "source_pdf_hash_verified": True,
        "no_repository_access_attested": True,
        "no_system_output_access_attested": True,
    }


SYNTHETIC_RECORDS = [
    {
        "record_type": "RAW",
        "document_id": "SYNTHETIC-DOCUMENT-A",
        "source_pdf_sha256": "1" * 64,
        "annotator_role": "ANNOTATOR_A",
        "presence_state": "PRESENT",
        "presence_reason_code": "NONCONTIGUOUS_HULL",
        "primary_span": {"start_page": 4, "end_page": 9},
        "alternative_spans": [],
        "alternative_span_type": [],
        "gap_pages": [7],
        "flags": ["noncontiguous_hull"],
        "ambiguity_code": "NONE",
        "admissible_spans": [],
        "parent_section": None,
        "annexure_identity": None,
        "boundary_evidence": {
            "heading_start_page": 4,
            "substantive_start_page": 5,
            "last_content_page": 9,
            "next_section_heading_page": 10,
            "mixed_end_page": None,
        },
        "timestamps": {
            "started_at": "2026-01-01T10:00:00Z",
            "completed_at": "2026-01-01T10:07:00Z",
        },
        "aids_used": ["PDF_VIEWER", "THUMBNAILS", "IN_PDF_SEARCH"],
        "structured_provenance": _provenance("SYNTHETIC-WORKSPACE-A"),
        "protocol_version_hash": "a" * 64,
    },
    {
        "record_type": "RAW",
        "document_id": "SYNTHETIC-DOCUMENT-B",
        "source_pdf_sha256": "2" * 64,
        "annotator_role": "ANNOTATOR_B",
        "presence_state": "AMBIGUOUS",
        "presence_reason_code": "END_UNRESOLVABLE",
        "primary_span": None,
        "alternative_spans": [],
        "alternative_span_type": [],
        "gap_pages": [],
        "flags": ["unclear_end"],
        "ambiguity_code": "END_UNRESOLVABLE",
        "admissible_spans": [
            {"start_page": 12, "end_page": 16},
            {"start_page": 12, "end_page": 17},
        ],
        "parent_section": None,
        "annexure_identity": None,
        "boundary_evidence": {
            "heading_start_page": 12,
            "substantive_start_page": 12,
            "last_content_page": None,
            "next_section_heading_page": 17,
            "mixed_end_page": 17,
        },
        "timestamps": {
            "started_at": "2026-01-02T11:00:00Z",
            "completed_at": "2026-01-02T11:09:00Z",
        },
        "aids_used": ["PDF_VIEWER", "PAGE_COUNT_DISPLAY"],
        "structured_provenance": _provenance("SYNTHETIC-WORKSPACE-B"),
        "protocol_version_hash": "a" * 64,
    },
    {
        "record_type": "ADJUDICATED",
        "document_id": "SYNTHETIC-DOCUMENT-C",
        "source_pdf_sha256": "3" * 64,
        "annotator_role": "ADJUDICATED_RECORD",
        "presence_state": "PRESENT",
        "presence_reason_code": "EMBEDDED_SUBSECTION",
        "primary_span": {"start_page": 20, "end_page": 24},
        "alternative_spans": [],
        "alternative_span_type": [],
        "gap_pages": [],
        "flags": ["embedded_in_directors_report"],
        "ambiguity_code": "NONE",
        "admissible_spans": [],
        "parent_section": "Synthetic Parent Section",
        "annexure_identity": None,
        "boundary_evidence": {
            "heading_start_page": 20,
            "substantive_start_page": 20,
            "last_content_page": 24,
            "next_section_heading_page": 25,
            "mixed_end_page": None,
        },
        "timestamps": {
            "started_at": "2026-01-03T12:00:00Z",
            "completed_at": "2026-01-03T12:05:00Z",
        },
        "aids_used": ["PDF_VIEWER", "THUMBNAILS"],
        "structured_provenance": {
            **_provenance("SYNTHETIC-WORKSPACE-ADJUDICATION"),
            "raw_record_sha256_refs": ["4" * 64, "5" * 64],
        },
        "protocol_version_hash": "a" * 64,
        "adjudication_status": "DISAGREEMENT_RESOLVED",
        "adjudication_reason": "Synthetic boundary disagreement resolved from the draft rule.",
        "adjudicator_role": "SEPARATE_ADJUDICATOR",
    },
]


def test_gold_schema_accepts_exactly_three_synthetic_records() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    assert len(SYNTHETIC_RECORDS) == 3
    for record in SYNTHETIC_RECORDS:
        validator.validate(record)


# P5-A.1 additions below deliberately leave the v0 test and its three fixtures above
# unchanged. The v0.1 records re-express the same synthetic cases under the new schema.
V0_1_SCHEMA_PATH = REPO_ROOT / "docs" / "phase5" / "gold_schema_v0_1.json"


def _v0_1_records() -> list[dict[str, object]]:
    import copy

    records = copy.deepcopy(SYNTHETIC_RECORDS)
    for record in records:
        record.pop("alternative_span_type")
        provenance = record["structured_provenance"]
        assert isinstance(provenance, dict)
        provenance["viewer_page_convention"] = (
            "VIEWER_PHYSICAL_1_BASED_STORED_ZERO_BASED"
        )
        provenance["search_usable"] = True
        if record["presence_state"] == "PRESENT":
            record["presence_reason_code"] = "BODY_QUALIFYING_TITLE"
    return records


def _v0_1_validator() -> Draft202012Validator:
    schema = json.loads(V0_1_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_gold_schema_v0_1_accepts_three_reexpressed_synthetic_records() -> None:
    records = _v0_1_records()
    assert len(records) == 3
    validator = _v0_1_validator()
    for record in records:
        validator.validate(record)


def _must_fail_records() -> list[dict[str, object]]:
    import copy

    valid = _v0_1_records()
    invalid: list[dict[str, object]] = []

    present_without_span = copy.deepcopy(valid[0])
    present_without_span["primary_span"] = None
    invalid.append(present_without_span)

    absent_with_span = copy.deepcopy(valid[0])
    absent_with_span["presence_state"] = "ABSENT"
    absent_with_span["presence_reason_code"] = "NOT_AN_ANNUAL_REPORT"
    invalid.append(absent_with_span)

    ambiguous_without_admissible_span = copy.deepcopy(valid[1])
    ambiguous_without_admissible_span["admissible_spans"] = []
    invalid.append(ambiguous_without_admissible_span)

    raw_with_adjudication_field = copy.deepcopy(valid[0])
    raw_with_adjudication_field["adjudication_reason"] = "not allowed on RAW"
    invalid.append(raw_with_adjudication_field)

    adjudicated_without_raw_refs = copy.deepcopy(valid[2])
    adjudicated_without_raw_refs["structured_provenance"].pop(
        "raw_record_sha256_refs"
    )
    invalid.append(adjudicated_without_raw_refs)

    malformed_hash = copy.deepcopy(valid[0])
    malformed_hash["source_pdf_sha256"] = "not-a-sha256"
    invalid.append(malformed_hash)

    malformed_timestamp = copy.deepcopy(valid[0])
    malformed_timestamp["timestamps"]["started_at"] = "yesterday"
    invalid.append(malformed_timestamp)

    malformed_document_id = copy.deepcopy(valid[0])
    malformed_document_id["document_id"] = "SYNTHETIC DOCUMENT/INVALID"
    invalid.append(malformed_document_id)

    annexure_without_identity = copy.deepcopy(valid[0])
    annexure_without_identity["flags"] = ["annexure"]
    annexure_without_identity["gap_pages"] = []
    invalid.append(annexure_without_identity)

    gap_without_noncontiguous_flag = copy.deepcopy(valid[0])
    gap_without_noncontiguous_flag["flags"] = []
    invalid.append(gap_without_noncontiguous_flag)

    return invalid


def test_gold_schema_v0_1_rejects_all_must_fail_records() -> None:
    validator = _v0_1_validator()
    records = _must_fail_records()
    assert len(records) >= 6
    for index, record in enumerate(records):
        assert list(validator.iter_errors(record)), f"must-fail record {index} passed"
