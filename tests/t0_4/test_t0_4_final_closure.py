from __future__ import annotations

import copy
import hashlib
import re
import shutil
from pathlib import Path

import pytest

from tools.t0_4 import closure as K
from tools.t0_4.core import (
    SOURCE_FILES,
    SetupInvariantError,
    _selection_rank,
    canonical_json,
    read_json,
)

ROOT = Path(__file__).resolve().parents[2]

ROUTE_INPUTS = (
    "arpipe/CLAUDE.md", "arpipe/README.md", "arpipe/configs/default.yaml", "arpipe/models.py",
    "arpipe/triage.py", "configs/t0_4", "docs/experiments", "tools/t0_4",
)
CELL_INPUTS = (
    "arpipe/models.py", "configs/t0_4", "artifacts/t0_4/benchmark_manifest.json", *SOURCE_FILES,
)
PROVENANCE_INPUTS = (
    *CELL_INPUTS, "artifacts/t0_4/config_hashes.json", K.CORPUS_INVENTORY_RECORDED_HASH,
)
REQUIRED_PROVENANCE_FIELDS = {
    "document_id", "issuer_id", "page_number", "fiscal_year", "split", "sampling_stratum",
    "condition_labels", "representation_class", "era", "length_category", "selection_rule_id",
    "selection_rank", "source_metadata_identifier", "source_metadata_commit",
    "source_metadata_hash", "sampling_config_hash",
}


def _copy_inputs(destination: Path, relative_paths) -> Path:
    for rel in relative_paths:
        source = ROOT / rel
        target = destination / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target, dirs_exist_ok=True)
        else:
            shutil.copy2(source, target)
    return destination


@pytest.fixture(scope="module")
def analysis() -> dict:
    return K.analyze_cells(ROOT)


@pytest.fixture(scope="module")
def cells(analysis) -> dict:
    return K.inspect_sampling_cells(ROOT, analysis)


# ---- Check 1: vector_text route -------------------------------------------

def test_vector_text_route_is_ocr_and_every_explicit_representation_agrees():
    route = K.evaluate_vector_text_route(ROOT)
    assert route["status"] == K.PASS
    assert route["registered_route"] == "OCR"
    assert route["contradictions"] == []
    layers = route["layers"]
    assert "VECTOR_TEXT" in layers["text_layer_detector_definition"]["needs_ocr_members"]
    assert layers["text_layer_detector_definition"]["router_returns_needs_ocr_pages"]
    for name in ("text_layer_detector_definition", "project_design_contract", "t0_4_preregistration"):
        assert layers[name]["route"] == "OCR"
    assert layers["t0_4_benchmark_configuration"]["gold_route_vocabulary_contains_ocr"]
    assert layers["routing_configuration"]["vector_keys"] == ["vector_path_text_threshold"]


def test_route_is_unresolved_when_the_t0_4_design_layer_does_not_state_it(tmp_path):
    root = _copy_inputs(tmp_path, ROUTE_INPUTS)
    prereg = root / K.PREREGISTRATION
    prereg.write_text(
        re.sub(r"Route of `vector_text`.*?ORACLE_ROUTING label\.\n", "", prereg.read_text(encoding="utf-8"), flags=re.S),
        encoding="utf-8",
    )
    route = K.evaluate_vector_text_route(root)
    assert route["registered_route"] == "OCR"
    assert route["status"] == K.UNRESOLVED


def test_route_fails_on_a_representation_that_contradicts_the_detector(tmp_path):
    root = _copy_inputs(tmp_path, ROUTE_INPUTS)
    prereg = root / K.PREREGISTRATION
    prereg.write_text(prereg.read_text(encoding="utf-8") + "\n`vector_text` is routed to NATIVE.\n", encoding="utf-8")
    assert K.evaluate_vector_text_route(root)["status"] == K.FAIL

    root = _copy_inputs(tmp_path / "config", ROUTE_INPUTS)
    oracle = root / "configs/t0_4/oracle_routing_spec.json"
    spec = read_json(oracle)
    spec["route_by_class"] = {"vector_text": "NATIVE"}
    oracle.write_text(canonical_json(spec), encoding="utf-8")
    assert K.evaluate_vector_text_route(root)["status"] == K.FAIL


def test_route_is_not_pass_when_the_detector_does_not_route_vector_text_to_ocr(tmp_path):
    root = _copy_inputs(tmp_path, ROUTE_INPUTS)
    triage = root / "arpipe/triage.py"
    triage.write_text(triage.read_text(encoding="utf-8").replace("PageKind.VECTOR_TEXT, PageKind.HYBRID", "PageKind.HYBRID"),
                      encoding="utf-8")
    assert K.evaluate_vector_text_route(root)["status"] != K.PASS


# ---- Check 2: sampling-cell inspection ------------------------------------

def test_observed_and_zero_availability_cells_partition_the_declared_product(cells):
    levels = K.declared_category_levels(ROOT)
    expected = 1
    for field in K.CELL_FIELDS:
        expected *= len(levels[field])
    assert cells["declared_cell_count"] == expected
    assert cells["observed_cell_count"] + cells["zero_availability_cell_count"] == expected
    assert cells["observed_cell_count"] == len(cells["cells"])
    assert all(cell["available_physical_pages"] >= 1 for cell in cells["cells"])


def test_every_observed_cell_selects_exactly_one_physical_page(cells):
    assert cells["violations"] == []
    assert cells["invariant_each_observed_cell_selects_exactly_one_page"]
    assert {cell["selected_physical_page_count"] for cell in cells["cells"]} == {1}
    assert cells["total_unique_selected_physical_pages"] == cells["observed_cell_count"]
    manifest = read_json(ROOT / K.MANIFEST)
    assert len(manifest["track_a"]["units"]) == cells["observed_cell_count"]


def test_sparse_cells_are_documented_and_never_compensated(cells):
    singletons = [cell for cell in cells["cells"] if cell["available_physical_pages"] == 1]
    assert cells["singleton_observed_cell_count"] == len(singletons) > 0
    assert cells["available_pages"]["minimum"] == 1
    assert all(cell["selection_status"] == "SELECTED_EXACTLY_ONE_SINGLETON_CELL" for cell in singletons)
    assert all(len(cell["selected_pages"]) == 1 for cell in singletons)


def test_overlapping_condition_labels_never_duplicate_a_physical_page(cells):
    manifest = read_json(ROOT / K.MANIFEST)
    keys = [(unit["document_id"], unit["page_number"]) for unit in manifest["track_a"]["units"]]
    assert cells["units_with_multiple_condition_labels"] > 0
    assert len(keys) == len(set(keys))


def test_cell_inspection_flags_zero_and_multiple_selections(analysis, tmp_path):
    root = _copy_inputs(tmp_path, CELL_INPUTS)
    manifest_path = root / K.MANIFEST
    manifest = read_json(manifest_path)
    units = manifest["track_a"]["units"]

    dropped = copy.deepcopy(manifest)
    removed = dropped["track_a"]["units"].pop(0)
    manifest_path.write_text(canonical_json(dropped), encoding="utf-8")
    result = K.inspect_sampling_cells(root, analysis)
    assert not result["invariant_each_observed_cell_selects_exactly_one_page"]
    assert any(v["status"] == "VIOLATION_NO_PAGE_SELECTED" and v["cell_id"] == K.cell_identifier(K._cell_key_of(removed))
               for v in result["violations"])

    key = next(k for k, count in analysis["available"].items() if count >= 2)
    extra_page = next(page for (doc, page), info in analysis["pages"].items()
                      if info["cell"] == key and (doc, page) != analysis["best"][key][1:])
    template = next(unit for unit in units if K._cell_key_of(unit) == key)
    doubled = copy.deepcopy(manifest)
    doubled["track_a"]["units"].append({**template, "page_number": extra_page})
    manifest_path.write_text(canonical_json(doubled), encoding="utf-8")
    result = K.inspect_sampling_cells(root, analysis)
    assert any(v["status"] == "VIOLATION_MULTIPLE_PAGES_SELECTED" for v in result["violations"])


def test_cell_inspection_flags_a_non_minimum_rank_selection(analysis, tmp_path):
    root = _copy_inputs(tmp_path, CELL_INPUTS)
    manifest_path = root / K.MANIFEST
    manifest = read_json(manifest_path)
    key = next(k for k, count in analysis["available"].items() if count >= 2)
    other = next(page for (doc, page), info in analysis["pages"].items()
                 if info["cell"] == key and (doc, page) != analysis["best"][key][1:])
    for unit in manifest["track_a"]["units"]:
        if K._cell_key_of(unit) == key:
            unit["page_number"] = other
    manifest_path.write_text(canonical_json(manifest), encoding="utf-8")
    result = K.inspect_sampling_cells(root, analysis)
    assert any(v["status"] == "VIOLATION_NOT_MINIMUM_RANK_PAGE" for v in result["violations"])


# ---- Check 3: sampling metadata provenance --------------------------------

def test_selection_rank_encoding_matches_the_frozen_builder(analysis):
    seed = analysis["seed"]
    for (document_id, page_number), info in list(analysis["pages"].items())[:200]:
        assert K._rank(seed, document_id, page_number) == _selection_rank(seed, document_id, page_number) == info["rank"]


def test_every_selected_page_has_complete_derivable_provenance(analysis):
    provenance = K.verify_sampling_provenance(ROOT, ROOT, "HEAD", analysis)
    assert provenance["status"] == K.PASS
    assert provenance["problems"] == []
    assert provenance["selected_pages_with_complete_provenance"] == provenance["selected_pages_total"]
    for record in provenance["selected_pages"]:
        assert REQUIRED_PROVENANCE_FIELDS <= set(record)
        assert re.fullmatch(r"[0-9a-f]{64}", record["source_metadata_hash"])
        assert re.fullmatch(r"[0-9a-f]{64}", record["sampling_config_hash"])
        assert re.fullmatch(r"[0-9a-f]{64}", record["selection_rank"])
        assert re.fullmatch(r"[0-9a-f]{40}", record["source_metadata_commit"])
        assert record["selection_rank"] == hashlib.sha256(
            f"{analysis['seed']}\x00{record['document_id']}\x00{record['page_number']}".encode("utf-8")
        ).hexdigest()
    assert provenance["corpus_manifest_hash"] == provenance["source_metadata"][K.CORPUS_INVENTORY]["sha256"]


def test_provenance_fails_closed_on_tampered_rank_or_source_hash(analysis, tmp_path):
    root = _copy_inputs(tmp_path, PROVENANCE_INPUTS)
    manifest_path = root / K.MANIFEST
    manifest = read_json(manifest_path)
    manifest["track_a"]["units"][0]["selection_rank"] = "0" * 64
    manifest_path.write_text(canonical_json(manifest), encoding="utf-8")
    tampered = K.verify_sampling_provenance(root, ROOT, "HEAD", analysis)
    assert tampered["status"] == K.FAIL
    assert any("rank" in problem["message"] for problem in tampered["problems"])

    root = _copy_inputs(tmp_path / "hash", PROVENANCE_INPUTS)
    manifest_path = root / K.MANIFEST
    manifest = read_json(manifest_path)
    manifest["source_hashes"][K.PAGE_PROFILE] = "f" * 64
    manifest_path.write_text(canonical_json(manifest), encoding="utf-8")
    assert K.verify_sampling_provenance(root, ROOT, "HEAD", analysis)["status"] == K.FAIL


# ---- Check 4: held-out / holdout / unseen / unobserved ---------------------

@pytest.mark.parametrize(
    ("line", "term", "role"),
    [
        ("Paired engine estimates retain honest held-out evaluation", "held-out", "AMBIGUOUS_HELD_OUT"),
        ("VALIDATION is the final held-out evaluation", "held-out", "AMBIGUOUS_HELD_OUT"),
        ("FIT and HOLDOUT give the final held-out evaluation", "held-out", "AMBIGUOUS_HELD_OUT"),
        ("only HOLDOUT provides the final held-out evaluation", "held-out", "FINAL_HELD_OUT_EVALUATION"),
        ("An unobserved cell is reported as unavailable", "unobserved", "COVERAGE_TERM"),
        ("Unobserved cells remain unavailable", "unobserved", "COVERAGE_TERM"),
        ("The engine was tested on unseen data", "unseen", "AMBIGUOUS_COVERAGE_TERM"),
        ("HOLDOUT remains final-only", "holdout", "SPLIT_LABEL"),
        ("PRESERVE_FIT_VALIDATION_HOLDOUT_BY_ISSUER", "holdout", "SPLIT_LABEL"),
        ('"holdout_role": "FINAL_ONLY_LOCKED"', "holdout", "SPLIT_IDENTIFIER"),
        ("Development/holdout splitter | Existing FIT/VALIDATION/HOLDOUT partition", "holdout", "SPLIT_PROSE"),
        ("## Holdout and freeze procedure", "holdout", "SPLIT_PROSE"),
        ("VALIDATION is the holdout", "holdout", "AMBIGUOUS_HELD_OUT"),
    ],
)
def test_terminology_classifier_separates_split_and_coverage_roles(line, term, role):
    match = next(item for item in K._TERM.finditer(line) if item.group(0).lower() == term)
    assert K.classify_occurrence(line, match) == role


def test_frozen_t0_4_terminology_has_no_ambiguity_and_keeps_coverage_terms():
    scan = K.scan_terminology(ROOT)
    assert scan["status"] == K.PASS
    assert scan["ambiguous_occurrences"] == []
    assert scan["unseen_occurrences"] == 0
    coverage = [item for item in scan["listed_occurrences"] if item["term"] == "unobserved"]
    assert coverage and all(item["role"] == "COVERAGE_TERM" for item in coverage)
    held_out = [item for item in scan["listed_occurrences"] if item["term"] == "held-out"]
    assert held_out and all(item["role"] == "FINAL_HELD_OUT_EVALUATION" for item in held_out)
    assert not set(scan["scope_files"]) & K.SCOPE_EXCLUDED


def test_reuse_audit_no_longer_calls_the_whole_partitioning_held_out():
    text = (ROOT / "docs/experiments/T0.4_p-x1_reuse_audit.md").read_text(encoding="utf-8")
    assert "honest held-out" not in text
    assert "only HOLDOUT provides the final held-out evaluation" in text


# ---- Non-execution guards and closure decision -----------------------------

def test_closure_code_imports_no_engine_network_or_pdf_library():
    files = sorted(rel for rel in K.CLOSURE_CODE_FILES if (ROOT / rel).is_file())
    assert "tools/t0_4/closure.py" in files
    guards = K.scan_static_non_execution(ROOT, files)
    assert guards == {"engine_or_api_imports": [], "pdf_files_in_snapshot": [], "unexpected_result_artifacts": []}


def test_closure_change_allowance_never_covers_frozen_inputs():
    frozen_prefixes = ("configs/t0_4/", "dataset/", "arpipe/")
    frozen_files = {K.MANIFEST, K.CONFIG_HASHES, "artifacts/t0_4/setup_audit.json", "tools/t0_4/core.py"}
    assert not [p for p in K.ALLOWED_CLOSURE_CHANGES if p.startswith(frozen_prefixes) or p in frozen_files]


@pytest.mark.parametrize(
    ("statuses", "decision"),
    [
        ((K.PASS, K.PASS, K.PASS, K.PASS), K.CLOSED),
        ((K.PASS, K.PASS_SPARSE, K.PASS, K.PASS), K.CLOSED),
        ((K.UNRESOLVED, K.PASS, K.PASS, K.PASS), K.OPEN),
        ((K.PASS, K.FAIL, K.PASS, K.PASS), K.OPEN),
        ((K.PASS, K.PASS, K.UNRESOLVED, K.PASS), K.OPEN),
        ((K.PASS, K.PASS, K.PASS, K.FAIL), K.OPEN),
    ],
)
def test_closure_requires_all_four_statuses(statuses, decision):
    keys = ("vector_text_route", "sampling_cell_inspection", "sampling_metadata_provenance", "held_out_terminology")
    assert K.decide_closure(dict(zip(keys, statuses))) == decision


def test_closure_refuses_a_commit_that_is_not_a_descendant_of_the_audited_base():
    with pytest.raises(SetupInvariantError):
        K.run_closure_audit(ROOT, K.BASE_COMMIT)
