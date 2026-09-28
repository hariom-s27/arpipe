"""Interop check: raw records produced by the P5-T annotator core are accepted by the
P5-S scoring engine (SAP v0.1 section 8). Synthetic data only."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.phase5.annotator import annotator_core as core
from tools.phase5.scoring import raw_ab_agreement, score_documents

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((REPO_ROOT / "docs" / "phase5" / "gold_schema_v0_2.json").read_text(encoding="utf-8"))
N = 30


def _record(role: str, span_viewer: tuple[int, int]) -> dict:
    ctx = {
        "document_id": "SYN-INTEROP-1", "source_pdf_sha256": "e" * 64, "physical_page_count": N,
        "annotator_role": role, "workspace_id": "ws-" + "1" * 32, "protocol_version_hash": "f" * 64,
        "started_at": "2026-09-27T10:00:00+05:30", "completed_at": "2026-09-27T10:10:00+05:30",
    }
    form = {
        "viewer_page_count": N, "viewer_name": "SyntheticViewer", "viewer_version": "1.0",
        "presence_state": "PRESENT", "presence_reason_code": "BODY_QUALIFYING_TITLE",
        "primary_span_viewer": span_viewer,
        "boundary_evidence_viewer": {"heading_start_page": span_viewer[0], "last_content_page": span_viewer[1]},
        "aids_used": ["PDF_VIEWER"], "search_queries": [], "search_usable": True,
        "no_repository_access_attested": True, "no_system_output_access_attested": True,
    }
    record = core.build_raw_record(form, ctx)
    assert core.validate_record(record, SCHEMA) == []
    # round-trip through the sealed canonical bytes, as the custodian would receive them
    return json.loads(core.canonical_json_bytes(record).decode("utf-8"))


def test_annotator_records_feed_scoring_raw_ab_agreement() -> None:
    a = _record("ANNOTATOR_A", (5, 9))
    b = _record("ANNOTATOR_B", (5, 9))
    assert a["primary_span"] == {"start_page": 4, "end_page": 8}  # viewer 1-based -> stored 0-based
    result = raw_ab_agreement([a], [b])
    assert result["exact_state_agreement"]["value"] == 1.0


def test_v0_1_records_without_schema_version_remain_accepted() -> None:
    a = _record("ANNOTATOR_A", (5, 9))
    b = _record("ANNOTATOR_B", (5, 9))
    for record in (a, b):
        record.pop("schema_version")
        record.pop("stub_word_count")
        record.pop("csr_esg_pages")
    result = raw_ab_agreement([a], [b])
    assert result["exact_state_agreement"]["value"] == 1.0


def test_v0_2_record_missing_its_conditional_field_is_refused_without_fallback() -> None:
    a = _record("ANNOTATOR_A", (5, 9))
    b = _record("ANNOTATOR_B", (5, 9))
    a["flags"].append("contains_csr_esg")
    a.pop("csr_esg_pages")
    with pytest.raises(ValueError, match="csr_esg_pages"):
        raw_ab_agreement([a], [b])


def test_v0_2_absent_reasons_feed_the_absent_presence_endpoint() -> None:
    records = []
    for doc, reason, alternatives in (
        ("SYN-NO-ENGLISH", "NO_ENGLISH_MDA", [(10, 12, "HINDI_COPY")]),
        ("SYN-EXTERNAL", "EXTERNAL_REFERENCE_ONLY", []),
    ):
        record = core.build_raw_record(
            {
                "viewer_page_count": N,
                "viewer_name": "SyntheticViewer",
                "viewer_version": "1.0",
                "presence_state": "ABSENT",
                "presence_reason_code": reason,
                "primary_span_viewer": None,
                "alternative_spans_viewer": alternatives,
                "boundary_evidence_viewer": {},
                "aids_used": ["PDF_VIEWER"],
                "search_queries": [],
                "search_usable": True,
                "no_repository_access_attested": True,
                "no_system_output_access_attested": True,
            },
            {
                "document_id": doc,
                "source_pdf_sha256": "e" * 64,
                "physical_page_count": N,
                "annotator_role": "ANNOTATOR_A",
                "workspace_id": "ws-" + "1" * 32,
                "protocol_version_hash": "f" * 64,
                "started_at": "2026-09-27T10:00:00+05:30",
                "completed_at": "2026-09-27T10:10:00+05:30",
            },
        )
        assert core.validate_record(record, SCHEMA) == []
        records.append(record)
    predictions = {
        record["document_id"]: [
            {
                "document_id": record["document_id"],
                "source_pdf_sha256": record["source_pdf_sha256"],
                "disposition": "COMPLETE",
                "span": None,
                "reasons": ["mda_not_located"],
                "physical_page_count": N,
            }
        ]
        for record in records
    }
    result = score_documents(records, predictions)
    assert result["gold_counts"]["ABSENT"] == 2
    assert result["presence"]["table_2x3"]["ABSENT"]["NOT_LOCATED"] == 2


def test_hindi_copy_alternative_is_never_scored() -> None:
    record = _record("ANNOTATOR_A", (5, 9))
    record["alternative_spans"] = [
        {"start_page": 10, "end_page": 12, "type": "HINDI_COPY"}
    ]
    prediction = {
        "document_id": record["document_id"],
        "source_pdf_sha256": record["source_pdf_sha256"],
        "disposition": "COMPLETE",
        "span": {"start_page": 10, "end_page": 12},
        "reasons": [],
        "physical_page_count": N,
    }
    result = score_documents(
        [record], {record["document_id"]: [prediction]}
    )
    assert result["primary"]["value"] == 0.0
    assert result["secondary"]["alternative_overlap_without_primary"]["count"] == 0


def test_annotator_records_disagreeing_span_still_scored() -> None:
    a = _record("ANNOTATOR_A", (5, 9))
    b = _record("ANNOTATOR_B", (6, 9))
    result = raw_ab_agreement([a], [b])
    assert result["exact_state_agreement"]["value"] == 1.0
    assert json.dumps(result, sort_keys=True)  # serialisable
