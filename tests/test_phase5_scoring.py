"""Synthetic-only checks for SAP v0.1 scoring; no corpus records are used."""

from __future__ import annotations

import copy
import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from tools.phase5.scoring import (
    NOT_ESTIMABLE,
    annotator_b_sensitivity,
    census_summary,
    classify_prediction,
    inclusive_iou,
    is_valid_span,
    raw_ab_agreement,
    score_documents,
)
from tools.phase5.scoring.__main__ import _guard_paths


SCHEMA = json.loads(
    (Path(__file__).resolve().parents[1] / "docs/phase5/gold_schema_v0_1.json").read_text(encoding="utf-8")
)
VALIDATOR = Draft202012Validator(SCHEMA)


def span(start: int, end: int) -> dict:
    return {"start_page": start, "end_page": end}


def gold(
    doc_id: str, state: str = "PRESENT", primary: dict | None = None,
    *, role: str = "ADJUDICATED_RECORD", alternatives: list | None = None,
    admissible: list | None = None, reason: str | None = None, page_count: int = 20,
    flags: list[str] | None = None,
) -> dict:
    """Construct and schema-check each synthetic Gold/raw record used below."""
    primary = span(2, 4) if state == "PRESENT" and primary is None else primary
    reason = reason or {
        "PRESENT": "BODY_QUALIFYING_TITLE",
        "ABSENT": "NO_QUALIFYING_BODY_SECTION",
        "AMBIGUOUS": "PRESENCE_UNRESOLVABLE",
    }[state]
    record = {
        "record_type": "ADJUDICATED" if role == "ADJUDICATED_RECORD" else "RAW",
        "document_id": doc_id,
        "source_pdf_sha256": "a" * 64,
        "annotator_role": role,
        "presence_state": state,
        "presence_reason_code": reason,
        "primary_span": primary,
        "alternative_spans": alternatives or [],
        "gap_pages": [],
        "flags": flags or [],
        "ambiguity_code": "PRESENCE_UNRESOLVABLE" if state == "AMBIGUOUS" else "NONE",
        "admissible_spans": admissible if admissible is not None else ([span(2, 4)] if state == "AMBIGUOUS" else []),
        "parent_section": None,
        "annexure_identity": None,
        "boundary_evidence": {
            "heading_start_page": None, "substantive_start_page": None,
            "last_content_page": None, "next_section_heading_page": None,
            "mixed_end_page": None,
        },
        "timestamps": {"started_at": "2026-01-01T00:00:00Z", "completed_at": "2026-01-01T00:01:00Z"},
        "aids_used": ["PDF_VIEWER"],
        "structured_provenance": {
            "annotation_workspace_id": "synthetic", "viewer_name": "synthetic viewer",
            "viewer_version": "1", "viewer_page_convention": "VIEWER_PHYSICAL_1_BASED_STORED_ZERO_BASED",
            "physical_page_count": page_count, "search_queries": [], "search_usable": True,
            "bookmark_pages": [], "flag_pages": {}, "source_pdf_hash_verified": True,
            "no_repository_access_attested": True, "no_system_output_access_attested": True,
        },
        "protocol_version_hash": "b" * 64,
    }
    if role == "ADJUDICATED_RECORD":
        record.update(adjudication_status="AGREEMENT_CONFIRMED", adjudication_reason="synthetic",
                      adjudicator_role="SEPARATE_ADJUDICATOR")
        record["structured_provenance"]["raw_record_sha256_refs"] = ["c" * 64, "d" * 64]
    VALIDATOR.validate(record)
    return record


def prediction(record: dict, predicted_span: dict | None = None, *, reasons: list | None = None) -> dict:
    return {
        "document_id": record["document_id"],
        "source_pdf_sha256": record["source_pdf_sha256"],
        "disposition": "",
        "physical_page_count": record["structured_provenance"]["physical_page_count"],
        "span": span(2, 4) if predicted_span is None and reasons is None else predicted_span,
        "reasons": reasons or [],
    }


def test_synthetic_gold_records_conform_to_v01_schema() -> None:
    for state in ("PRESENT", "ABSENT", "AMBIGUOUS"):
        for role in ("ANNOTATOR_A", "ANNOTATOR_B", "ADJUDICATED_RECORD"):
            gold(f"synthetic_{state}_{role}", state, role=role)


def test_inclusive_iou_worked_example_and_span_edges() -> None:
    assert inclusive_iou(span(2, 4), span(3, 5)) == .5  # SAP §4 worked example
    assert inclusive_iou(span(0, 0), span(0, 0)) == 1
    assert inclusive_iou(span(2, 4), span(2, 4)) == 1
    assert inclusive_iou(span(0, 0), span(1, 1)) == 0
    assert inclusive_iou(span(3, 3), span(2, 4)) == 1 / 3
    assert is_valid_span(span(0, 0), 1)
    assert not is_valid_span(span(True, 0), 1)


def test_noncontiguous_gold_scores_its_inclusive_hull() -> None:
    g = gold("hull", primary=span(2, 4))
    g["flags"] = ["noncontiguous_hull"]
    g["gap_pages"] = [3]
    VALIDATOR.validate(g)
    scored = score_documents([g], {"hull": [prediction(g, span(3, 3))]})
    assert scored["primary"] == {"value": 1 / 3, "denominator": 1}


def test_prediction_status_priority_and_invalid_types() -> None:
    g = gold("status")
    good = prediction(g)
    assert classify_prediction(g, []) == "NO_OUTPUT"
    assert classify_prediction(g, [good, good]) == "DUPLICATE"
    bad_id = {**good, "document_id": "other", "disposition": "QUARANTINE"}
    assert classify_prediction(g, [bad_id]) == "IDENTITY_INVALID"
    assert classify_prediction(g, [{**good, "disposition": "QUARANTINE", "span": span(True, 4)}]) == "QUARANTINE"
    assert classify_prediction(g, [prediction(g, None, reasons=["mda_not_located"])]) == "NOT_LOCATED"
    assert classify_prediction(g, [{**good, "span": None}]) == "TYPE_INVALID"
    assert classify_prediction(g, [{**good, "reasons": ["mda_not_located"]}]) == "TYPE_INVALID"
    for bad in (span(True, 4), span(2.0, 4), {"start_page": "2", "end_page": 4}):
        assert classify_prediction(g, [{**good, "span": bad}]) == "TYPE_INVALID"
    assert classify_prediction(g, [{**good, "physical_page_count": False}]) == "TYPE_INVALID"
    assert classify_prediction(g, [{**good, "span": span(4, 2)}]) == "ORDER_INVALID"
    assert classify_prediction(g, [{**good, "span": span(-1, 2)}]) == "RANGE_INVALID"
    assert classify_prediction(g, [{**good, "span": span(2, 20)}]) == "RANGE_INVALID"
    assert classify_prediction(g, [good]) == "VALID"


def test_primary_document_weighting_failures_and_absent_gold() -> None:
    a, b, c, d = gold("a"), gold("b"), gold("c"), gold("d", "ABSENT")
    result = score_documents([d, c, a, b], {
        "a": [prediction(a, span(3, 5))],
        "b": [prediction(b, None, reasons=["mda_not_located"])],
        "d": [prediction(d)],
    })
    assert result["primary"] == {"value": .5 / 3, "denominator": 3}
    assert [d["iou"] for d in result["documents"]] == [.5, 0.0, 0.0, None]
    assert result["prediction_status_counts"]["NOT_LOCATED"] == 1
    assert result["prediction_status_counts"]["NO_OUTPUT"] == 1
    assert score_documents([d], {})["primary"] == {"value": NOT_ESTIMABLE, "denominator": 0}
    with pytest.raises(ValueError):
        score_documents([a, a], {})
    invalid_gold = copy.deepcopy(a)
    invalid_gold["primary_span"] = None
    with pytest.raises(ValueError):
        score_documents([invalid_gold], {})
    invalid_gold = copy.deepcopy(a)
    invalid_gold["presence_reason_code"] = "NOT_AN_ANNUAL_REPORT"
    with pytest.raises(ValueError):
        score_documents([invalid_gold], {})


def test_presence_table_and_error_penalized_collapse() -> None:
    records = [gold(f"p{i}") for i in range(3)] + [gold(f"a{i}", "ABSENT") for i in range(3)]
    preds = {
        "p0": [prediction(records[0])],
        "p1": [prediction(records[1], None, reasons=["mda_not_located"])],
        "a0": [prediction(records[3])],
        "a1": [prediction(records[4], None, reasons=["mda_not_located"])],
    }
    presence = score_documents(records, preds)["presence"]
    assert presence["table_2x3"] == {
        "PRESENT": {"PRESENT": 1, "NOT_LOCATED": 1, "FAILED_OR_ABSTAINED": 1},
        "ABSENT": {"PRESENT": 1, "NOT_LOCATED": 1, "FAILED_OR_ABSTAINED": 1},
    }
    assert presence["collapsed_2x2"] == {"TP": 1, "FN": 2, "FP": 2, "TN": 1}
    assert presence["accuracy"] == {"value": 1 / 3, "denominator": 6}
    assert presence["sensitivity"] == {"value": 1 / 3, "denominator": 3}
    assert presence["specificity"] == {"value": 1 / 3, "denominator": 3}
    assert score_documents([], {})["presence"]["accuracy"]["value"] == NOT_ESTIMABLE


def test_secondary_indicators_signed_errors_and_type7_quantiles() -> None:
    records = [gold(f"s{i}", primary=span(5, 7)) for i in range(5)]
    preds = {f"s{i}": [prediction(records[i], span(5 + i, 7 + i))] for i in range(4)}
    secondary = score_documents(records, preds)["secondary"]
    assert secondary["exact_start"] == {"count": 1, "denominator": 5, "value": .2}
    assert secondary["within_one_end"] == {"count": 2, "denominator": 5, "value": .4}
    assert secondary["exact_full_span"]["count"] == 1
    assert secondary["signed_start_error"]["coverage"] == 4
    assert secondary["signed_start_error"]["quantiles"] == {
        "0": 0.0, "0.25": .75, "0.5": 1.5, "0.75": 2.25, "1": 3.0,
    }
    empty = score_documents([records[0]], {})["secondary"]
    assert empty["signed_end_error"]["quantiles"]["0.5"] == NOT_ESTIMABLE
    early = score_documents([records[0]], {"s0": [prediction(records[0], span(4, 6))]})
    assert early["secondary"]["signed_start_error"]["quantiles"]["0.5"] == -1.0


def test_ambiguous_optimistic_and_alternative_overlap() -> None:
    a = gold("amb1", "AMBIGUOUS", admissible=[span(2, 4), span(8, 9)])
    b = gold("amb2", "AMBIGUOUS")
    c = gold("amb3", "AMBIGUOUS")
    p = gold("present", alternatives=[{**span(8, 9), "type": "OTHER_ENGLISH_COPY"}])
    scored = score_documents([a, b, c, p], {
        "amb1": [prediction(a, span(8, 9))],
        "amb2": [prediction(b, None, reasons=["mda_not_located"])],
        "present": [prediction(p, span(8, 9))],
    })
    assert scored["ambiguous_optimistic"] == {
        "value": 2 / 3, "denominator": 3, "presence_unresolvable_not_located_count": 1,
    }
    assert scored["secondary"]["alternative_overlap_without_primary"] == {"count": 1, "eligible": 1}
    assert scored["presence"]["ambiguous_count"] == 3


def test_census_issuer_weighting_and_leave_one_out() -> None:
    a1, a2, b1, c1 = gold("a1"), gold("a2"), gold("b1"), gold("c1", "ABSENT")
    scored = score_documents([a1, a2, b1, c1], {"a1": [prediction(a1)], "b1": [prediction(b1)]})
    summary = census_summary(scored, {"a1": "A", "a2": "A", "b1": "B", "c1": "C"})
    assert summary["overall"] == {"value": 2 / 3, "denominator": 3}
    assert summary["per_issuer"]["A"] == {"value": .5, "denominator": 2}
    assert summary["issuer_weighted"] == {"value": .75, "denominator": 2}
    assert summary["excluded_zero_present_issuers"] == {"count": 1, "issuers": ["C"]}
    assert summary["leave_one_issuer_out"]["A"] == {"value": 1.0, "denominator": 1}
    assert summary["leave_one_issuer_out"]["B"] == {"value": .5, "denominator": 2}
    assert summary["leave_one_issuer_out"]["C"] == {"value": 2 / 3, "denominator": 3}


def test_raw_ab_agreement_and_b_only_sensitivity() -> None:
    ar = [gold("r1", role="ANNOTATOR_A"), gold("r2", role="ANNOTATOR_A"),
          gold("r3", "ABSENT", role="ANNOTATOR_A")]
    br = [gold("r1", role="ANNOTATOR_B", primary=span(3, 5)),
          gold("r2", "ABSENT", role="ANNOTATOR_B"),
          gold("r3", "ABSENT", role="ANNOTATOR_B")]
    result = raw_ab_agreement(ar, br)
    assert result["state_table_3x3"]["PRESENT"]["PRESENT"] == 1
    assert result["state_table_3x3"]["PRESENT"]["ABSENT"] == 1
    assert result["exact_state_agreement"] == {"count": 2, "denominator": 3, "value": 2 / 3}
    assert result["cohens_kappa"] == pytest.approx(.4)
    assert result["pabak"] == pytest.approx(1 / 3)
    assert result["present_present"]["mean_iou"] == .5
    assert result["present_present"]["within_one_start"]["count"] == 1
    assert result["exact_reason_agreement"]["count"] == 2
    assert result["exact_flag_agreement"]["count"] == 3
    assert annotator_b_sensitivity(br, {"r1": [prediction(br[0], span(2, 4))]}) == {
        "value": .5, "denominator": 1,
    }


def test_raw_ab_undefined_kappa_and_empty_agreement() -> None:
    a, b = gold("same", role="ANNOTATOR_A"), gold("same", role="ANNOTATOR_B")
    assert raw_ab_agreement([a], [b])["cohens_kappa"] == NOT_ESTIMABLE
    assert raw_ab_agreement([], [])["exact_state_agreement"]["value"] == NOT_ESTIMABLE
    wrong = copy.deepcopy(b)
    wrong["source_pdf_sha256"] = "e" * 64
    with pytest.raises(ValueError):
        raw_ab_agreement([a], [wrong])


def test_cli_canonical_json_determinism_and_holdout_path_refusal(tmp_path: Path) -> None:
    gold_dir = tmp_path / "synthetic_gold"
    gold_dir.mkdir()
    g = gold("cli")
    (gold_dir / "cli.json").write_text(json.dumps(g), encoding="utf-8")
    pred_path = tmp_path / "synthetic_predictions.csv"
    with pred_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "claim_document_id", "document_id", "source_pdf_sha256", "disposition",
            "physical_page_count", "span", "reasons",
        ])
        writer.writeheader()
        writer.writerow({
            "claim_document_id": "cli", "document_id": "cli", "source_pdf_sha256": "a" * 64,
            "disposition": "", "physical_page_count": "20", "span": json.dumps(span(2, 4)), "reasons": "[]",
        })
    issuer_map = tmp_path / "issuers.json"
    issuer_map.write_text(json.dumps({"cli": "SyntheticIssuer"}), encoding="utf-8")
    out = tmp_path / "score.json"
    cmd = [sys.executable, "-m", "tools.phase5.scoring", "--gold", str(gold_dir),
           "--pred", str(pred_path), "--out", str(out), "--issuer-map", str(issuer_map)]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    first = out.read_bytes()
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    assert out.read_bytes() == first
    assert first == (json.dumps(json.loads(first), sort_keys=True, separators=(",", ":")) + "\n").encode()
    refused = cmd.copy()
    refused[refused.index(str(gold_dir))] = str(tmp_path / "HOLDOUT_synthetic_gold")
    process = subprocess.run(refused, capture_output=True, text=True)
    assert process.returncode != 0
    assert "HOLDOUT path refused" in process.stderr
    (gold_dir / "HOLDOUT_synthetic.json").write_text(json.dumps(g), encoding="utf-8")
    process = subprocess.run(cmd, capture_output=True, text=True)
    assert process.returncode != 0
    assert "HOLDOUT path refused" in process.stderr
    _guard_paths([Path("HOLDOUT_synthetic_gold")], approved=True)
