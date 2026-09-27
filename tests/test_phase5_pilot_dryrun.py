"""Synthetic end-to-end checks for the Phase 5 pilot rehearsal."""

import json

import pytest

from tools.phase5.annotator import make_bundle
from tools.phase5.custodian import build_workspaces
from tools.phase5.pilot_dryrun.run_dryrun import _write_roster, run_dryrun


def test_synthetic_pipeline_and_deterministic_report(tmp_path):
    first = run_dryrun(tmp_path / "first", allow_synthetic_title_override=True)
    second = run_dryrun(tmp_path / "second", allow_synthetic_title_override=True)

    first_json = (tmp_path / "first" / "DRYRUN_REPORT.json").read_bytes()
    second_json = (tmp_path / "second" / "DRYRUN_REPORT.json").read_bytes()
    assert first_json == second_json
    assert json.loads(first_json) == first == second
    assert all(status == "PASS" for status in first["steps"].values())
    assert all(len(hashes) == 4 for hashes in first["record_hashes"].values())

    agreement = first["agreement"]
    assert agreement["pair_count"] == 4
    assert agreement["state_table_3x3"]["PRESENT"]["PRESENT"] == 2
    assert agreement["state_table_3x3"]["PRESENT"]["ABSENT"] == 1
    assert agreement["state_table_3x3"]["ABSENT"]["ABSENT"] == 1
    assert agreement["exact_state_agreement"] == {"count": 3, "denominator": 4, "value": 0.75}
    assert agreement["cohens_kappa"] == 0.5
    assert agreement["pabak"] == 0.5
    assert agreement["present_present"]["mean_iou"] == pytest.approx(5 / 6)
    assert agreement["present_present"]["exact_start"]["count"] == 1
    assert agreement["present_present"]["within_one_start"]["count"] == 2
    assert agreement["present_present"]["exact_end"]["count"] == 2
    assert agreement["present_present"]["exact_full_span"]["count"] == 1
    assert "SYNTHETIC — not a result" in (tmp_path / "first" / "DRYRUN_REPORT.md").read_text(encoding="utf-8")


def test_title_list_override_is_explicit(tmp_path):
    with pytest.raises(ValueError, match="must be passed explicitly"):
        run_dryrun(tmp_path / "refused")
    assert not (tmp_path / "refused").exists()


@pytest.mark.parametrize("split", ["HOLDOUT", "VALIDATION"])
def test_non_fit_roster_refused(tmp_path, split):
    case = tmp_path / split
    case.mkdir()
    roster, pdf_dir = _write_roster(case, split=split)
    bundle = case / "bundle.zip"
    make_bundle.build_bundle(bundle)
    with pytest.raises(build_workspaces.WorkspaceBuildError, match="disallowed split"):
        build_workspaces.build_workspaces(roster, pdf_dir, bundle, case / "workspaces")
    assert not (case / "workspaces").exists()
