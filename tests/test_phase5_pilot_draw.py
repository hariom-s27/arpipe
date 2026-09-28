"""Synthetic-only tests for the mechanical PILOT/RETEST draw (PILOT_PLAN_v0_1_1 sec 2-4).

No real inventory, issuer split, development manifest or condition map is read: every
CSV here is hand-built with a handful of synthetic issuers. The real draw is never run.
"""

from __future__ import annotations

import csv
import hashlib
import json
import tempfile
from pathlib import Path

import pytest

from tools.phase5 import pilot_draw as pd


@pytest.fixture()
def outside_repo():
    # Not tmp_path: with --basetemp inside the checkout, tmp_path sits under the real
    # .git, so _check_out_dir's outside-repository check would always refuse it.
    with tempfile.TemporaryDirectory(prefix="p5_pilot_draw_") as temporary:
        yield Path(temporary)

INVENTORY_COLUMNS = ["document_id", "company_id", "fiscal_year", "pdf_sha256", "page_count"]
ISSUER_SPLIT_COLUMNS = ["issuer_id", "split"]
DEV_MANIFEST_COLUMNS = ["document_id"]
CONDITION_MAP_COLUMNS = ["document_id", "status", "condition"]


def fake_sha(document_id: str) -> str:
    return hashlib.sha256(document_id.encode("utf-8")).hexdigest()


def write_dataset(
    tmp_path: Path,
    docs: list[tuple[str, str, int, int]],
    issuer_splits: dict[str, str],
    development_ids: list[str] = (),
    condition_rows: list[tuple[str, str, str]] = (),
) -> tuple[Path, Path, Path, Path]:
    """docs: (document_id, company_id, fiscal_year, page_count) tuples."""
    inventory = tmp_path / "corpus_inventory.csv"
    with open(inventory, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=INVENTORY_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for document_id, company_id, year, pages in docs:
            writer.writerow({
                "document_id": document_id, "company_id": company_id,
                "fiscal_year": str(year), "pdf_sha256": fake_sha(document_id),
                "page_count": str(pages),
            })
    issuer_split = tmp_path / "issuer_split.csv"
    with open(issuer_split, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ISSUER_SPLIT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for issuer_id, split in issuer_splits.items():
            writer.writerow({"issuer_id": issuer_id, "split": split})
    development_manifest = tmp_path / "development_manifest.csv"
    with open(development_manifest, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=DEV_MANIFEST_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for document_id in development_ids:
            writer.writerow({"document_id": document_id})
    condition_map = tmp_path / "condition_map.csv"
    with open(condition_map, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CONDITION_MAP_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for document_id, status, condition in condition_rows:
            writer.writerow({"document_id": document_id, "status": status, "condition": condition})
    return inventory, issuer_split, development_manifest, condition_map


# -- frame filtering (section 2) ---------------------------------------------------

def test_frame_keeps_fit_only_and_drops_development_and_missing_ids(tmp_path):
    inventory, issuer_split, development_manifest, condition_map = write_dataset(
        tmp_path,
        docs=[
            ("KEEP_A", "ISS1", 2010, 10),
            ("KEEP_B", "ISS1", 2020, 12),
            ("DROP_VALIDATION", "ISS2", 2015, 8),
            ("DROP_DEV", "ISS1", 2005, 5),
            ("SOME_DOC_MISSING", "ISS1", 2030, 5),
        ],
        issuer_splits={"ISS1": "FIT", "ISS2": "VALIDATION"},
        development_ids=["DROP_DEV"],
    )
    inventory_rows = pd._read_inventory(inventory)
    issuer_split_map = pd._read_issuer_split(issuer_split)
    development_ids = pd._read_development_ids(development_manifest)
    frame = pd.build_frame(inventory_rows, issuer_split_map, development_ids)
    assert set(frame) == {"KEEP_A", "KEEP_B"}


# -- hard-proxy: core set only (section 3, errata v0.1.1) ---------------------------

def test_hard_proxy_ids_use_only_the_four_core_conditions_and_candidate_status(tmp_path):
    _, _, _, condition_map = write_dataset(
        tmp_path, docs=[], issuer_splits={},
        condition_rows=[
            ("DOC1", "CANDIDATE", "annexure_candidate"),
            ("DOC2", "CANDIDATE", "devanagari_candidate"),  # not core: must not count
            ("DOC3", "NOT_OBSERVED", "annexure_candidate"),  # wrong status: must not count
            ("DOC4", "CANDIDATE", "legacy_font_candidate"),
            ("DOC5", "CANDIDATE", "annexure_candidate"),  # not in frame: must not count
        ],
    )
    hard = pd._read_hard_proxy_document_ids(condition_map, frozenset({"DOC1", "DOC2", "DOC3", "DOC4"}))
    assert hard == frozenset({"DOC1", "DOC4"})


# -- pair selection and its digest tie-break (section 4) ----------------------------

def test_pair_picks_max_separation_and_breaks_boundary_ties_by_lowest_digest():
    docs = [
        {"document_id": "T_A", "company_id": "TIE", "fiscal_year": 2000, "fiscal_year_str": "2000"},
        {"document_id": "T_B", "company_id": "TIE", "fiscal_year": 2000, "fiscal_year_str": "2000"},
        {"document_id": "T_C", "company_id": "TIE", "fiscal_year": 2030, "fiscal_year_str": "2030"},
    ]
    pair = pd._select_pair(docs)
    digest_a = pd._digest(pd.PAIR_DOMAIN, "TIE", "2000", "T_A")
    digest_b = pd._digest(pd.PAIR_DOMAIN, "TIE", "2000", "T_B")
    expected_low = "T_A" if (digest_a, "T_A") < (digest_b, "T_B") else "T_B"
    assert [doc["document_id"] for doc in pair["documents"]] == [expected_low, "T_C"]
    assert pair["separation"] == 30


def test_pair_with_exactly_two_documents_needs_no_tie_break():
    docs = [
        {"document_id": "P_LOW", "company_id": "PLAIN", "fiscal_year": 2012, "fiscal_year_str": "2012"},
        {"document_id": "P_HIGH", "company_id": "PLAIN", "fiscal_year": 2018, "fiscal_year_str": "2018"},
    ]
    pair = pd._select_pair(docs)
    assert [doc["document_id"] for doc in pair["documents"]] == ["P_LOW", "P_HIGH"]
    assert pair["separation"] == 6


# -- full mechanical draw ------------------------------------------------------------

def _happy_path_dataset(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    docs = []
    for n in range(1, 10):  # I01..I09: nine plain two-document issuers
        issuer = f"I{n:02d}"
        docs.append((f"{issuer}A", issuer, 2000 + n, 10 + n))
        docs.append((f"{issuer}B", issuer, 2020 + n, 10 + n))
    docs.append(("I10A", "I10", 2015, 12))  # single-document issuer: excluded from pairs
    docs.append(("I11A", "I11", 2011, 12))  # VALIDATION split: excluded from the frame
    docs.append(("I11B", "I11", 2019, 12))
    docs.append(("I01_DEV", "I01", 2005, 12))  # development id: excluded from the frame
    docs.append(("I01_SOME_MISSING", "I01", 2006, 12))  # _MISSING id: excluded from the frame
    docs.append(("I12A", "I12", 2001, 12))  # devanagari-only: must not be hard_proxy
    docs.append(("I12B", "I12", 2009, 12))
    docs.append(("I13A", "I13", 2000, 12))  # three documents, tie at the minimum year
    docs.append(("I13B", "I13", 2000, 12))
    docs.append(("I13C", "I13", 2030, 12))

    issuer_splits = {f"I{n:02d}": "FIT" for n in range(1, 10)}
    issuer_splits.update({"I10": "FIT", "I11": "VALIDATION", "I12": "FIT", "I13": "FIT"})

    return write_dataset(
        tmp_path,
        docs=docs,
        issuer_splits=issuer_splits,
        development_ids=["I01_DEV"],
        condition_rows=[
            ("I03A", "CANDIDATE", "annexure_candidate"),  # I03's pair becomes hard_proxy
            ("I12A", "CANDIDATE", "devanagari_candidate"),  # must NOT make I12 hard_proxy
        ],
    )


def test_hard_issuer_is_reserved_then_pilot_fills_to_five(tmp_path, outside_repo):
    inventory, issuer_split, development_manifest, condition_map = _happy_path_dataset(tmp_path)
    report = pd.run_pilot_draw(
        inventory=inventory, issuer_split=issuer_split,
        development_manifest=development_manifest, condition_map=condition_map,
        out_dir=outside_repo / "out",
    )
    assert report["hard_flags"]["I03"] is True
    assert report["hard_flags"]["I12"] is False  # devanagari_candidate is not a core token
    assert report["selections"]["reserved_hard_issuer"] == "I03"
    assert len(report["selections"]["pilot_issuers"]) == 5
    assert "I03" in report["selections"]["pilot_issuers"]
    assert len(report["selections"]["pilot_documents"]) == 10
    assert "I10" not in report["issuer_pairs"]  # single document: not a two-document issuer
    assert "I11" not in report["issuer_pairs"]  # VALIDATION split: never entered the frame

    non_reserved = [c for c in report["issuer_pairs"] if c != "I03"]
    expected_fill = sorted(non_reserved, key=lambda c: (report["digests"]["issuer"][c], c))[:4]
    assert sorted(report["selections"]["pilot_issuers"]) == sorted(["I03", *expected_fill])


def test_retest_is_disjoint_from_pilot_and_ranked_by_its_own_digest(tmp_path, outside_repo):
    inventory, issuer_split, development_manifest, condition_map = _happy_path_dataset(tmp_path)
    report = pd.run_pilot_draw(
        inventory=inventory, issuer_split=issuer_split,
        development_manifest=development_manifest, condition_map=condition_map,
        out_dir=outside_repo / "out",
    )
    pilot_issuers = set(report["selections"]["pilot_issuers"])
    retest_issuers = report["selections"]["retest_issuers"]
    assert len(retest_issuers) == 3
    assert pilot_issuers.isdisjoint(retest_issuers)
    assert set(report["selections"]["pilot_documents"]).isdisjoint(report["selections"]["retest_documents"])
    assert len(report["selections"]["retest_documents"]) == 6

    remaining = [c for c in report["issuer_pairs"] if c not in pilot_issuers]
    expected_retest = sorted(remaining, key=lambda c: (report["digests"]["retest_issuer"][c], c))[:3]
    assert retest_issuers == expected_retest


def test_retest_reports_the_actual_count_when_fewer_than_three_issuers_remain(tmp_path, outside_repo):
    docs = []
    for n in range(1, 6):  # exactly five two-document issuers: nothing left for retest
        issuer = f"J{n:02d}"
        docs.append((f"{issuer}A", issuer, 2000 + n, 10))
        docs.append((f"{issuer}B", issuer, 2020 + n, 10))
    issuer_splits = {f"J{n:02d}": "FIT" for n in range(1, 6)}
    inventory, issuer_split, development_manifest, condition_map = write_dataset(
        tmp_path, docs=docs, issuer_splits=issuer_splits,
    )
    report = pd.run_pilot_draw(
        inventory=inventory, issuer_split=issuer_split,
        development_manifest=development_manifest, condition_map=condition_map,
        out_dir=outside_repo / "out",
    )
    assert len(report["selections"]["pilot_issuers"]) == 5
    assert report["selections"]["retest_issuers"] == []
    assert report["selections"]["retest_documents"] == []
    assert report["counts"]["retest_issuers"] == 0


def test_fewer_than_five_two_document_issuers_is_refused_before_any_output(tmp_path):
    docs = []
    for n in range(1, 4):  # only three two-document issuers
        issuer = f"K{n:02d}"
        docs.append((f"{issuer}A", issuer, 2000 + n, 10))
        docs.append((f"{issuer}B", issuer, 2020 + n, 10))
    issuer_splits = {f"K{n:02d}": "FIT" for n in range(1, 4)}
    inventory, issuer_split, development_manifest, condition_map = write_dataset(
        tmp_path, docs=docs, issuer_splits=issuer_splits,
    )
    out_dir = tmp_path / "out"
    with pytest.raises(pd.PilotDrawError, match="fewer than 5"):
        pd.run_pilot_draw(
            inventory=inventory, issuer_split=issuer_split,
            development_manifest=development_manifest, condition_map=condition_map,
            out_dir=out_dir,
        )
    assert not out_dir.exists()


def test_out_dir_inside_a_repository_is_refused(tmp_path):
    inventory, issuer_split, development_manifest, condition_map = _happy_path_dataset(tmp_path)
    fake_repo = tmp_path / "fake_repo"
    (fake_repo / ".git").mkdir(parents=True)
    out_dir = fake_repo / "workspaces"
    with pytest.raises(pd.PilotDrawError, match="outside the repository"):
        pd.run_pilot_draw(
            inventory=inventory, issuer_split=issuer_split,
            development_manifest=development_manifest, condition_map=condition_map,
            out_dir=out_dir,
        )
    assert not out_dir.exists()


def test_out_dir_must_be_new_or_empty(tmp_path, outside_repo):
    inventory, issuer_split, development_manifest, condition_map = _happy_path_dataset(tmp_path)
    out_dir = outside_repo / "out"
    out_dir.mkdir()
    (out_dir / "stray.txt").write_text("x", encoding="utf-8")
    with pytest.raises(pd.PilotDrawError, match="not empty"):
        pd.run_pilot_draw(
            inventory=inventory, issuer_split=issuer_split,
            development_manifest=development_manifest, condition_map=condition_map,
            out_dir=out_dir,
        )


def test_draw_is_deterministic_across_runs(tmp_path, outside_repo):
    inventory, issuer_split, development_manifest, condition_map = _happy_path_dataset(tmp_path)
    first = outside_repo / "first"
    second = outside_repo / "second"
    pd.run_pilot_draw(
        inventory=inventory, issuer_split=issuer_split,
        development_manifest=development_manifest, condition_map=condition_map,
        out_dir=first,
    )
    pd.run_pilot_draw(
        inventory=inventory, issuer_split=issuer_split,
        development_manifest=development_manifest, condition_map=condition_map,
        out_dir=second,
    )
    for name in ("PILOT_ROSTER.csv", "RETEST_ROSTER.csv"):
        assert (first / name).read_bytes() == (second / name).read_bytes()
    # DRAW_REPORT.json embeds absolute input paths, which are identical here since both
    # runs read the same source files; drop nothing and compare byte-for-byte.
    assert (first / "DRAW_REPORT.json").read_bytes() == (second / "DRAW_REPORT.json").read_bytes()


def test_roster_columns_and_split_are_exactly_as_specified(tmp_path, outside_repo):
    inventory, issuer_split, development_manifest, condition_map = _happy_path_dataset(tmp_path)
    out_dir = outside_repo / "out"
    pd.run_pilot_draw(
        inventory=inventory, issuer_split=issuer_split,
        development_manifest=development_manifest, condition_map=condition_map,
        out_dir=out_dir,
    )
    with open(out_dir / "PILOT_ROSTER.csv", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert list(rows[0]) == ["document_id", "source_pdf_sha256", "physical_page_count", "split"]
    assert all(row["split"] == "FIT" for row in rows)
    assert len(rows) == 10


def test_exact_pair_digest_matches_a_hand_computed_preimage(tmp_path, outside_repo):
    inventory, issuer_split, development_manifest, condition_map = _happy_path_dataset(tmp_path)
    report = pd.run_pilot_draw(
        inventory=inventory, issuer_split=issuer_split,
        development_manifest=development_manifest, condition_map=condition_map,
        out_dir=outside_repo / "out",
    )
    preimage = (
        pd.PAIR_DOMAIN + b"\x00" + b"I01" + b"\x00" + b"2001" + b"\x00" + b"I01A"
    )
    expected = hashlib.sha256(preimage).hexdigest()
    assert report["digests"]["pair"]["I01A"] == expected


def test_draw_report_records_input_hashes_and_tool_version(tmp_path, outside_repo):
    inventory, issuer_split, development_manifest, condition_map = _happy_path_dataset(tmp_path)
    out_dir = outside_repo / "out"
    report = pd.run_pilot_draw(
        inventory=inventory, issuer_split=issuer_split,
        development_manifest=development_manifest, condition_map=condition_map,
        out_dir=out_dir,
    )
    assert report["tool_version"] == pd.TOOL_VERSION
    assert report["input_files"]["inventory"]["sha256"] == pd._sha256_file(inventory)
    assert report["input_files"]["condition_map"]["sha256"] == pd._sha256_file(condition_map)
    on_disk = json.loads((out_dir / "DRAW_REPORT.json").read_bytes())
    assert on_disk == report


def test_main_cli_refuses_with_exit_code_one(tmp_path, capsys):
    inventory, issuer_split, development_manifest, condition_map = write_dataset(
        tmp_path, docs=[], issuer_splits={},
    )
    with pytest.raises(SystemExit) as excinfo:
        pd.main([
            "--inventory", str(inventory), "--issuer-split", str(issuer_split),
            "--development-manifest", str(development_manifest),
            "--condition-map", str(condition_map),
            "--out-dir", str(tmp_path / "out"),
        ])
    assert excinfo.value.code == 1
    assert "refused" in capsys.readouterr().err
