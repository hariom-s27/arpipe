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


# F3 additions are isolated from the unchanged v0.1 fixtures and tests above.
V0_2_SCHEMA_PATH = REPO_ROOT / "docs" / "phase5" / "gold_schema_v0_2.json"


def _v0_2_validator() -> Draft202012Validator:
    schema = json.loads(V0_2_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _v0_2_present() -> dict[str, object]:
    import copy

    record = copy.deepcopy(_v0_1_records()[0])
    record["schema_version"] = "0.2"
    return record


def _v0_2_absent(reason: str) -> dict[str, object]:
    record = _v0_2_present()
    record["presence_state"] = "ABSENT"
    record["presence_reason_code"] = reason
    record["primary_span"] = None
    record["alternative_spans"] = []
    record["gap_pages"] = []
    record["flags"] = []
    record["boundary_evidence"] = {
        "heading_start_page": None,
        "substantive_start_page": None,
        "last_content_page": None,
        "next_section_heading_page": None,
        "mixed_end_page": None,
    }
    return record


def test_gold_schema_v0_2_accepts_new_synthetic_cases() -> None:
    import copy

    stub_with_count = _v0_2_present()
    stub_with_count["flags"] = ["noncontiguous_hull", "stub"]
    stub_with_count["stub_word_count"] = 91

    stub_without_count = _v0_2_present()
    stub_without_count["flags"] = ["noncontiguous_hull", "stub"]

    csr = _v0_2_present()
    csr["flags"] = ["noncontiguous_hull", "contains_csr_esg"]
    csr["csr_esg_pages"] = [5, 6]

    no_english_without_span = _v0_2_absent("NO_ENGLISH_MDA")
    no_english_with_hindi = copy.deepcopy(no_english_without_span)
    no_english_with_hindi["alternative_spans"] = [
        {"start_page": 10, "end_page": 12, "type": "HINDI_COPY"}
    ]
    external_only = _v0_2_absent("EXTERNAL_REFERENCE_ONLY")

    validator = _v0_2_validator()
    records = [
        stub_with_count,
        stub_without_count,
        csr,
        no_english_without_span,
        no_english_with_hindi,
        external_only,
    ]
    for index, record in enumerate(records):
        errors = list(validator.iter_errors(record))
        assert not errors, f"v0.2 pass record {index}: {errors}"


def test_gold_schema_v0_2_rejects_new_must_fail_cases() -> None:
    import copy

    count_without_stub = _v0_2_present()
    count_without_stub["stub_word_count"] = 91

    csr_flag_without_pages = _v0_2_present()
    csr_flag_without_pages["flags"] = ["noncontiguous_hull", "contains_csr_esg"]
    csr_flag_without_pages["csr_esg_pages"] = []

    csr_pages_without_flag = _v0_2_present()
    csr_pages_without_flag["csr_esg_pages"] = [5]

    stub_absent = _v0_2_absent("NO_ENGLISH_MDA")
    stub_absent["flags"] = ["stub"]

    csr_absent = _v0_2_absent("EXTERNAL_REFERENCE_ONLY")
    csr_absent["flags"] = ["contains_csr_esg"]
    csr_absent["csr_esg_pages"] = [5]

    present_with_no_english = _v0_2_present()
    present_with_no_english["presence_reason_code"] = "NO_ENGLISH_MDA"

    present_with_external = _v0_2_present()
    present_with_external["presence_reason_code"] = "EXTERNAL_REFERENCE_ONLY"

    no_english_with_wrong_span = _v0_2_absent("NO_ENGLISH_MDA")
    no_english_with_wrong_span["alternative_spans"] = [
        {"start_page": 10, "end_page": 12, "type": "OTHER_LANGUAGE_COPY"}
    ]

    other_absent_with_hindi = _v0_2_absent("TOC_ONLY")
    other_absent_with_hindi["alternative_spans"] = [
        {"start_page": 10, "end_page": 12, "type": "HINDI_COPY"}
    ]

    missing_version = copy.deepcopy(_v0_2_present())
    missing_version.pop("schema_version")

    validator = _v0_2_validator()
    records = [
        count_without_stub,
        csr_flag_without_pages,
        csr_pages_without_flag,
        stub_absent,
        csr_absent,
        present_with_no_english,
        present_with_external,
        no_english_with_wrong_span,
        other_absent_with_hindi,
        missing_version,
    ]
    for index, record in enumerate(records):
        assert list(validator.iter_errors(record)), f"v0.2 must-fail record {index} passed"


# F3b additions (schema v0.3, decisions 8.7). Everything above stays untouched; the v0.3
# fixtures are derived from the v0.2 ones.
V0_3_SCHEMA_PATH = REPO_ROOT / "docs" / "phase5" / "gold_schema_v0_3.json"


def _v0_3_validator() -> Draft202012Validator:
    schema = json.loads(V0_3_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _v0_3_present(start_shared: bool = False, end_shared: bool = False) -> dict[str, object]:
    record = _v0_2_present()
    record["schema_version"] = "0.3"
    evidence, flags = record["boundary_evidence"], record["flags"]
    assert isinstance(evidence, dict) and isinstance(flags, list)
    evidence["start_page_shared"] = start_shared
    evidence["end_page_shared"] = end_shared
    if start_shared:
        flags.append("mixed_start_page")
    if end_shared:
        flags.append("mixed_end_page")
        evidence["mixed_end_page"] = 9  # the primary end page of the synthetic record
    return record


def _v0_3_absent(reason: str = "NO_QUALIFYING_BODY_SECTION") -> dict[str, object]:
    record = _v0_2_absent(reason)
    record["schema_version"] = "0.3"
    evidence = record["boundary_evidence"]
    assert isinstance(evidence, dict)
    evidence["start_page_shared"] = None
    evidence["end_page_shared"] = None
    return record


def _v0_3_ambiguous() -> dict[str, object]:
    record = _v0_1_records()[1]
    record["schema_version"] = "0.3"
    evidence = record["boundary_evidence"]
    assert isinstance(evidence, dict)
    evidence["mixed_end_page"] = None
    evidence["start_page_shared"] = None
    evidence["end_page_shared"] = None
    return record


def _changed(
    record: dict[str, object], *, add_flags: tuple[str, ...] = (), drop: tuple[str, ...] = (),
    **evidence: object,
) -> dict[str, object]:
    """``record`` with extra flags, dropped boundary_evidence keys and changed values."""
    boundary, flags = record["boundary_evidence"], record["flags"]
    assert isinstance(boundary, dict) and isinstance(flags, list)
    boundary.update(evidence)
    for key in drop:
        boundary.pop(key)
    flags.extend(add_flags)
    return record


def test_gold_schema_v0_3_accepts_shared_page_cases() -> None:
    records = {
        "PRESENT, neither page shared": _v0_3_present(),
        "PRESENT, start shared": _v0_3_present(start_shared=True),
        "PRESENT, end shared": _v0_3_present(end_shared=True),
        "PRESENT, both shared": _v0_3_present(start_shared=True, end_shared=True),
        "ABSENT, null answers": _v0_3_absent(),
        "ABSENT NO_ENGLISH_MDA, null answers": _v0_3_absent("NO_ENGLISH_MDA"),
        "AMBIGUOUS, null answers": _v0_3_ambiguous(),
    }
    validator = _v0_3_validator()
    for name, record in records.items():
        errors = list(validator.iter_errors(record))
        assert not errors, f"v0.3 pass record {name!r}: {errors}"


def _v0_3_must_fail_records() -> dict[str, dict[str, object]]:
    return {
        # PRESENT needs two real booleans
        "PRESENT, null start answer": _changed(_v0_3_present(), start_page_shared=None),
        "PRESENT, null end answer": _changed(_v0_3_present(), end_page_shared=None),
        "PRESENT, start answer missing": _changed(_v0_3_present(), drop=("start_page_shared",)),
        "PRESENT, end answer missing": _changed(_v0_3_present(), drop=("end_page_shared",)),
        "PRESENT, both answers missing": _changed(
            _v0_3_present(), drop=("start_page_shared", "end_page_shared")),
        "PRESENT, string answer": _changed(_v0_3_present(), end_page_shared="No"),
        "PRESENT, integer answer": _changed(_v0_3_present(), start_page_shared=0),
        # ABSENT and AMBIGUOUS need two nulls
        "ABSENT, start answer false": _changed(_v0_3_absent(), start_page_shared=False),
        "ABSENT, end answer true": _changed(_v0_3_absent(), end_page_shared=True),
        "ABSENT, answers missing": _changed(
            _v0_3_absent(), drop=("start_page_shared", "end_page_shared")),
        "AMBIGUOUS, start answer true": _changed(_v0_3_ambiguous(), start_page_shared=True),
        "AMBIGUOUS, end answer false": _changed(_v0_3_ambiguous(), end_page_shared=False),
        # flag present <-> answer true, both directions, both flags
        "mixed_start_page flag, start answer false": _changed(
            _v0_3_present(), add_flags=("mixed_start_page",)),
        "start answer true, no mixed_start_page flag": _changed(
            _v0_3_present(), start_page_shared=True),
        "mixed_end_page flag, end answer false": _changed(
            _v0_3_present(), add_flags=("mixed_end_page",)),
        "end answer true, no mixed_end_page flag": _changed(
            _v0_3_present(), end_page_shared=True),
        "mixed_start_page flag on AMBIGUOUS": _changed(
            _v0_3_ambiguous(), add_flags=("mixed_start_page",)),
        "mixed_end_page flag on ABSENT": _changed(
            _v0_3_absent(), add_flags=("mixed_end_page",)),
    }


def test_gold_schema_v0_3_rejects_bad_shared_page_answers_and_flag_mismatches() -> None:
    validator = _v0_3_validator()
    for name, record in _v0_3_must_fail_records().items():
        assert list(validator.iter_errors(record)), f"v0.3 must-fail record {name!r} passed"


def test_gold_schema_v0_3_requires_its_own_schema_version() -> None:
    validator = _v0_3_validator()
    for version in ("0.2", "0.4", None):
        record = _v0_3_present()
        if version is None:
            record.pop("schema_version")
        else:
            record["schema_version"] = version
        assert list(validator.iter_errors(record)), f"schema_version {version!r} accepted"


def test_gold_schema_versions_are_selected_by_schema_version_and_never_shared() -> None:
    v0_3, v0_2, v0_1 = _v0_3_present(), _v0_2_present(), _v0_1_records()[0]
    # v0.2's `mixed_end_page` is an ordinary flag, valid without any shared-page answer
    v0_2_mixed_end = _v0_2_present()
    v0_2_mixed_end["flags"] = ["noncontiguous_hull", "mixed_end_page"]
    mixed_end_evidence = v0_2_mixed_end["boundary_evidence"]
    assert isinstance(mixed_end_evidence, dict)
    mixed_end_evidence["mixed_end_page"] = 9

    validators = {"0.1": _v0_1_validator(), "0.2": _v0_2_validator(), "0.3": _v0_3_validator()}
    records = {"0.1": [v0_1], "0.2": [v0_2, v0_2_mixed_end], "0.3": [v0_3]}
    for owner, owned in records.items():
        for record in owned:
            for version, validator in validators.items():
                errors = list(validator.iter_errors(record))
                if version == owner:
                    assert not errors, f"v{owner} record rejected by its own schema: {errors}"
                else:
                    assert errors, f"v{owner} record accepted by the v{version} schema"
