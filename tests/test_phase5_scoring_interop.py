"""Interop check: raw records produced by the P5-T annotator core are accepted by the
P5-S scoring engine (SAP v0.1 section 8). Synthetic data only."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from tools.phase5.annotator import annotator_core as core
from tools.phase5.scoring import NOT_ESTIMABLE, gold_schema_filename, raw_ab_agreement, score_documents

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((REPO_ROOT / "docs" / "phase5" / "gold_schema_v0_3.json").read_text(encoding="utf-8"))
SCHEMA_V0_2 = json.loads((REPO_ROOT / "docs" / "phase5" / "gold_schema_v0_2.json").read_text(encoding="utf-8"))
SCHEMA_V0_1 = json.loads((REPO_ROOT / "docs" / "phase5" / "gold_schema_v0_1.json").read_text(encoding="utf-8"))
N = 30


def _ctx(role: str, doc: str) -> dict:
    return {
        "document_id": doc, "source_pdf_sha256": "e" * 64, "physical_page_count": N,
        "annotator_role": role, "workspace_id": "ws-" + "1" * 32, "protocol_version_hash": "f" * 64,
        "started_at": "2026-09-27T10:00:00+05:30", "completed_at": "2026-09-27T10:10:00+05:30",
    }


def _record(role: str, span_viewer: tuple[int, int], doc: str = "SYN-INTEROP-1",
            start_shared: bool = False, end_shared: bool = False) -> dict:
    ctx = _ctx(role, doc)
    form = {
        "viewer_page_count": N, "viewer_name": "SyntheticViewer", "viewer_version": "1.0",
        "presence_state": "PRESENT", "presence_reason_code": "BODY_QUALIFYING_TITLE",
        "primary_span_viewer": span_viewer,
        "boundary_evidence_viewer": {"heading_start_page": span_viewer[0], "last_content_page": span_viewer[1]},
        "start_page_shared": start_shared, "end_page_shared": end_shared,
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


# -- schema v0.3 (decisions 8.7): shared start/end pages -----------------------------

def _absent_record(role: str, doc: str) -> dict:
    form = {
        "viewer_page_count": N, "viewer_name": "SyntheticViewer", "viewer_version": "1.0",
        "presence_state": "ABSENT", "presence_reason_code": "NO_QUALIFYING_BODY_SECTION",
        "primary_span_viewer": None, "boundary_evidence_viewer": {},
        "aids_used": ["PDF_VIEWER"], "search_queries": [], "search_usable": True,
        "no_repository_access_attested": True, "no_system_output_access_attested": True,
    }
    record = core.build_raw_record(form, _ctx(role, doc))
    assert core.validate_record(record, SCHEMA) == []
    return json.loads(core.canonical_json_bytes(record).decode("utf-8"))


def _valid_under(schema: dict, record: dict) -> bool:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return not list(validator.iter_errors(record))


def _as_v0_2(record: dict) -> dict:
    """The same synthetic record as v0.2 wrote it: no shared-page answers, no mixed_start_page."""
    old = copy.deepcopy(record)
    old["schema_version"] = "0.2"
    for key in ("start_page_shared", "end_page_shared"):
        old["boundary_evidence"].pop(key)
    old["flags"] = [flag for flag in old["flags"] if flag != "mixed_start_page"]
    return old


def _as_v0_1(record: dict) -> dict:
    """The same synthetic record as v0.1 wrote it: also no schema_version and no v0.2 fields."""
    old = _as_v0_2(record)
    for key in ("schema_version", "stub_word_count", "csr_esg_pages"):
        old.pop(key)
    return old


def _prediction(record: dict, start: int, end: int) -> dict:
    return {
        "document_id": record["document_id"], "source_pdf_sha256": record["source_pdf_sha256"],
        "disposition": "COMPLETE", "span": {"start_page": start, "end_page": end},
        "reasons": [], "physical_page_count": N,
    }


def test_gold_schema_filename_dispatches_on_schema_version() -> None:
    assert gold_schema_filename({}) == "gold_schema_v0_1.json"
    assert gold_schema_filename({"schema_version": "0.2"}) == "gold_schema_v0_2.json"
    assert gold_schema_filename({"schema_version": "0.3"}) == "gold_schema_v0_3.json"
    for unsupported in ("0.4", 0.3, None):
        with pytest.raises(ValueError):
            gold_schema_filename({"schema_version": unsupported})


def test_v0_3_record_from_the_core_is_accepted_and_scored() -> None:
    a = _record("ANNOTATOR_A", (5, 9), start_shared=True, end_shared=True)
    b = _record("ANNOTATOR_B", (5, 9), start_shared=True, end_shared=True)
    assert a["schema_version"] == "0.3" and gold_schema_filename(a) == "gold_schema_v0_3.json"
    assert _valid_under(SCHEMA, a) and _valid_under(SCHEMA, b)
    assert raw_ab_agreement([a], [b])["exact_state_agreement"]["value"] == 1.0
    assert score_documents([a], {a["document_id"]: [_prediction(a, 4, 8)]})["primary"]["value"] == 1.0


def test_v0_2_and_v0_1_records_remain_accepted_alongside_v0_3() -> None:
    a = _record("ANNOTATOR_A", (5, 9), end_shared=True)
    b = _record("ANNOTATOR_B", (5, 9), end_shared=True)
    for downgrade, own_schema in ((_as_v0_2, SCHEMA_V0_2), (_as_v0_1, SCHEMA_V0_1)):
        old_a, old_b = downgrade(a), downgrade(b)
        # genuine records of that version: valid under their own schema, refused by v0.3
        assert _valid_under(own_schema, old_a) and _valid_under(own_schema, old_b)
        assert not _valid_under(SCHEMA, old_a)
        result = raw_ab_agreement([old_a], [old_b])
        assert result["exact_state_agreement"]["value"] == 1.0
        assert result["shared_page_agreement"]["end_page_shared"] == {
            "comparable_pairs": 0, "agreements": 0, "percent_agreement": NOT_ESTIMABLE,
        }
        scored = score_documents([old_a], {old_a["document_id"]: [_prediction(old_a, 4, 8)]})
        assert scored["primary"]["value"] == 1.0


def test_shared_page_agreement_is_computed_on_comparable_present_pairs() -> None:
    # document -> (A start, A end, B start, B end)
    answers = {
        "SYN-SP-1": (False, False, False, False),  # agree on both
        "SYN-SP-2": (True, False, False, False),   # disagree on start
        "SYN-SP-3": (False, True, False, False),   # disagree on end
        "SYN-SP-4": (True, True, False, True),     # disagree on start, agree on end
    }
    raw_a = [_record("ANNOTATOR_A", (5, 9), doc, start_shared=sa, end_shared=ea)
             for doc, (sa, ea, _, _) in answers.items()]
    raw_b = [_record("ANNOTATOR_B", (5, 9), doc, start_shared=sb, end_shared=eb)
             for doc, (_, _, sb, eb) in answers.items()]
    # PRESENT/ABSENT and ABSENT/ABSENT pairs have no answer on both sides: not comparable
    raw_a += [_record("ANNOTATOR_A", (5, 9), "SYN-SP-5", start_shared=True, end_shared=True),
              _absent_record("ANNOTATOR_A", "SYN-SP-6")]
    raw_b += [_absent_record("ANNOTATOR_B", "SYN-SP-5"), _absent_record("ANNOTATOR_B", "SYN-SP-6")]
    result = raw_ab_agreement(raw_a, raw_b)
    assert result["pair_count"] == 6 and result["present_present"]["count"] == 4
    assert result["shared_page_agreement"] == {
        "start_page_shared": {"comparable_pairs": 4, "agreements": 2, "percent_agreement": 50.0},
        "end_page_shared": {"comparable_pairs": 4, "agreements": 3, "percent_agreement": 75.0},
    }


def test_shared_page_pairs_need_a_v0_3_answer_on_both_sides() -> None:
    a = _record("ANNOTATOR_A", (5, 9), end_shared=True)
    b = _as_v0_2(_record("ANNOTATOR_B", (5, 9), end_shared=True))
    counted = raw_ab_agreement([a], [b])["shared_page_agreement"]
    assert counted["start_page_shared"]["comparable_pairs"] == 0
    assert counted["end_page_shared"]["comparable_pairs"] == 0


def test_shared_page_agreement_is_additive_and_serialisable() -> None:
    result = raw_ab_agreement([_record("ANNOTATOR_A", (5, 9))], [_record("ANNOTATOR_B", (5, 9))])
    assert set(result) - {"shared_page_agreement"} == {
        "state_table_3x3", "pair_count", "exact_state_agreement", "cohens_kappa", "pabak",
        "present_present", "exact_reason_agreement", "exact_flag_agreement",
    }
    assert json.dumps(result, sort_keys=True)
    assert raw_ab_agreement([], [])["shared_page_agreement"] == {
        key: {"comparable_pairs": 0, "agreements": 0, "percent_agreement": NOT_ESTIMABLE}
        for key in ("start_page_shared", "end_page_shared")
    }


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda r: r["boundary_evidence"].update(start_page_shared=None), "shared-page"),
        (lambda r: r["boundary_evidence"].update(end_page_shared="No"), "shared-page"),
        (lambda r: r["boundary_evidence"].pop("end_page_shared"), "shared-page"),
        (lambda r: r.pop("boundary_evidence"), "shared-page"),
        (lambda r: r["flags"].append("mixed_end_page"), "flags disagree"),
        (lambda r: r["boundary_evidence"].update(start_page_shared=True), "flags disagree"),
    ],
)
def test_v0_3_gold_with_bad_shared_page_answers_is_refused(change, message) -> None:
    record = _record("ANNOTATOR_A", (5, 9))
    change(record)
    with pytest.raises(ValueError, match=message):
        score_documents([record], {})


def test_v0_3_absent_gold_must_carry_null_answers() -> None:
    record = _absent_record("ANNOTATOR_A", "SYN-ABS-1")
    assert score_documents([record], {})["gold_counts"]["ABSENT"] == 1
    record["boundary_evidence"]["end_page_shared"] = False
    with pytest.raises(ValueError, match="shared-page"):
        score_documents([record], {})
