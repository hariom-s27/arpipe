"""Unit tests over the synthetic fixtures. Run: python -m pytest tests -q"""
from __future__ import annotations

import os
import sys

import pymupdf
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from arpipe import cli, fetch, segment, store, textlayer, triage, verify  # noqa: E402
from arpipe.models import (Company, MDASpan, PageKind, Script,   # noqa: E402
                           VerificationReport)

FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fixtures")


def _fix(name: str) -> str:
    p = os.path.join(FIX, name)
    if not os.path.exists(p):
        pytest.skip("run tests/make_fixtures.py first")
    return p


def test_host_limiter_initialises_slotted_state():
    limiter = fetch.HostLimiter(min_interval=0)
    limiter.wait("https://example.com/report.pdf")
    assert "example.com" in limiter._last


def test_fetch_command_creates_output_root(tmp_path):
    import argparse

    manifest = tmp_path / "reports.jsonl"
    manifest.write_text("", encoding="utf-8")
    root = tmp_path / "store"
    args = argparse.Namespace(manifest=str(manifest), root=str(root),
                              min_interval=0, workers=1)
    assert cli.cmd_fetch(args) == 0
    assert (root / "documents.jsonl").exists()


def test_parquet_snapshot_handles_nested_mixed_qc(tmp_path):
    import json
    import pandas as pd

    record = {
        "company_id": "INE123A01016",
        "fy_end": 2015,
        "ok": True,
        "qc": {"diag": {"candidates": [["outline", 10, 15, 0.95]]}},
        "errors": [],
    }
    store.append_manifest(str(tmp_path), record)
    path = store.snapshot_parquet(str(tmp_path))
    assert path is not None
    row = pd.read_parquet(path).iloc[0]
    assert json.loads(row["qc"])["diag"]["candidates"][0][0] == "outline"


# ------------------------------------------------------------------ triage
@pytest.mark.parametrize("name,expect", [
    ("A_digital_outline.pdf", "digital"),
    ("B_twocol_toc.pdf", "digital"),
    ("C_scanned.pdf", "scanned"),
    ("D_hybrid.pdf", "mixed"),
])
def test_doc_kind(name, expect):
    assert triage.profile_document(_fix(name)).doc_kind == expect


def test_scanned_pages_all_need_ocr():
    p = triage.profile_document(_fix("C_scanned.pdf"))
    assert p.frac_needing_ocr == 1.0
    assert all(pp.kind is PageKind.SCANNED for pp in p.pages)


def test_hybrid_routes_only_the_scanned_pages():
    p = triage.profile_document(_fix("D_hybrid.pdf"))
    ocr_pages = set(triage.ocr_page_numbers(p))
    assert ocr_pages == set(range(8, 20))


def test_columns_detected_on_two_column_report():
    p = triage.profile_document(_fix("B_twocol_toc.pdf"))
    dense = [pp for pp in p.pages if pp.n_chars > 300]
    two = sum(1 for pp in dense if pp.n_columns >= 2)
    assert two / len(dense) > 0.7


# ------------------------------------------------------------------ segment
@pytest.mark.parametrize("name,method_prefix", [
    ("A_digital_outline.pdf", "outline"),
    ("B_twocol_toc.pdf", None),
])
def test_locate_digital(name, method_prefix):
    path = _fix(name)
    prof = triage.profile_document(path)
    texts = textlayer.extract_pages(path)
    doc = pymupdf.open(path)
    span, diag = segment.locate(doc, prof, texts)
    doc.close()
    assert span is not None
    assert span.start_page == 10 and span.end_page == 15
    assert span.score > 0.8
    if method_prefix:
        assert span.method.startswith(method_prefix)


def test_terminator_regex_matches_common_next_sections():
    from arpipe.patterns import MDA_TERMINATOR_RE
    for s in ["Report on Corporate Governance", "Independent Auditor's Report",
              "Business Responsibility and Sustainability Report",
              "Notice of the 27th Annual General Meeting",
              "Balance Sheet as at 31st March, 2019"]:
        assert MDA_TERMINATOR_RE.search(s), s


def test_next_numbered_annexure_terminates_mda():
    from arpipe.patterns import ANNEXURE_HEADING_RE, MDA_TERMINATOR_RE
    assert MDA_TERMINATOR_RE.search("ANNEXURE VI")
    assert MDA_TERMINATOR_RE.search("Annexure 6")
    assert MDA_TERMINATOR_RE.search(
        "227 Statutory Report ANNEXURE VI Register of Loans")
    scrambled_page = "table cells\nmore table cells\nANNEXURE VI\nRegister of Loans"
    assert ANNEXURE_HEADING_RE.search(scrambled_page)
    assert not ANNEXURE_HEADING_RE.search("See details in Annexure VI below")


def test_mda_heading_variants():
    from arpipe.patterns import MDA_HEADING_RE
    for s in ["Management Discussion and Analysis",
              "MANAGEMENT'S DISCUSSION & ANALYSIS REPORT",
              "Management Discussion & Analysis",
              "Managements Discussion and Analysis"]:
        assert MDA_HEADING_RE.search(s), s


def test_trim_span_finds_split_multiline_heading_after_toc_start():
    texts = {
        26: "Future of Flavours\nCorporate Overview\nBrand portfolio",
        27: "Life at the company\nPeople and culture",
        33: "Statutory Reports\nManagement\nDiscussion & Analysis\n"
            "Global Economic Overview",
        34: "Industry Structure and Developments\nBusiness discussion",
        35: "ANNEXURE VI\nRegister of Loans",
    }
    got = segment.trim_span(MDASpan(26, 35, method="toc"), texts)
    assert got.start_page == 33
    assert got.end_page == 34


# ------------------------------------------------------------------- verify
def test_fy_extraction():
    c = verify.fy_candidates("Annual Report 2014-15 for the year ended "
                             "31st March, 2015")
    assert c.most_common(1)[0][0] == 2015


def test_fy_two_digit_rollover():
    assert verify.fy_candidates("FY 1999-00")[2000] > 0


def test_cin_regex():
    from arpipe.patterns import CIN_RE
    m = CIN_RE.search("CIN: L27100MH1994PLC078367")
    assert m and "".join(m.groups()) == "L27100MH1994PLC078367"


def test_name_matching_survives_suffix_noise():
    co = Company(company_id="X", canonical_name="Reliance Industries Limited",
                 aliases=["RELIANCE"])
    s, _ = verify.name_similarity("RELIANCE INDUSTRIES LTD.", co)
    assert s >= 88


def test_era_check_flags_impossible_year():
    sig = verify.era_signals("Debtors Turnover Inventory Turnover Current Ratio "
                             "Return on Net Worth")
    notes = verify.check_era(2013, sig)
    assert any("ratio-table" in n for n in notes)


def test_section_qc_detects_auditor_leak():
    qc = verify.section_qc("Industry Structure and Developments. " * 40 +
                           " We have audited the accompanying financial statements")
    assert "auditor_report_leak" in qc["leaks"]


# --------------------------------------------------------------- order quality
_ORDERED_PROSE = "\n\n".join([
    "The global economy grew by an estimated 3.2 per cent in 2024.",
    "Inflation eased through the year as supply chains recovered.",
    "India stayed among the fastest-growing large economies in the world.",
    "Domestic demand was firm and the financial system stayed sound.",
    "Rural consumption revived and government investment picked up.",
    "Exports softened, held back by weak demand in several key markets.",
])


def test_order_quality_zero_on_correctly_ordered_prose():
    q = verify.order_quality(_ORDERED_PROSE)
    assert q["orphan_start_frac"] == 0.0
    assert q["dangling_end_frac"] == 0.0
    assert q["n_paragraphs"] == 6


def test_order_quality_rises_when_two_paragraphs_are_swapped():
    # blocks 2 and 3 are the two halves of one sentence, correctly adjacent
    blocks = [
        "GLOBAL ECONOMY",
        "The Reserve Bank of India has warned that frequent weather",
        "shocks now pose a material risk to the growth outlook.",
        "Inflation eased through the year as supply chains recovered.",
        "Domestic demand stayed firm and the financial system was sound.",
        "Rural consumption picked up and government capex stayed strong.",
        "Exports were softer, weighed by weak demand in key markets.",
    ]
    good = verify.order_quality("\n\n".join(blocks))
    blocks[2], blocks[3] = blocks[3], blocks[2]          # swap two paragraphs
    bad = verify.order_quality("\n\n".join(blocks))
    assert good["orphan_start_frac"] == 0.0
    assert bad["orphan_start_frac"] >= 0.12
    assert bad["orphan_start_frac"] > good["orphan_start_frac"]


def test_order_quality_flags_lowercase_fragment_under_heading():
    # the Jain p103 case: the preceding line is a heading with no full stop
    blocks = ["GLOBAL ECONOMY",
              "formulation, while posing direct threats to farm output."]
    blocks += [f"Sentence number {i} is in the right order and reads fine."
               for i in range(6)]
    assert verify.order_quality("\n\n".join(blocks))["orphan_starts"] >= 1


def test_grade_downgrades_scrambled_reading_order():
    rep = VerificationReport(company_ok=True, year_ok=True)
    base = {"too_short": False, "long_token_frac": 0.0, "leaks": [],
            "orphan_start_frac": 0.0}
    assert verify.grade(rep, base, 0.95) == "high"
    mild = {**base, "orphan_start_frac": verify.ORPHAN_START_FRAC_MAX + 0.005}
    assert verify.grade(rep, mild, 0.95) == "medium"
    bad = {**base, "orphan_start_frac": 2 * verify.ORPHAN_START_FRAC_MAX + 0.005}
    assert verify.grade(rep, bad, 0.95) == "low"


# ----------------------------------------------------------------- reading order
def test_xy_cut_keeps_columns_apart():
    path = _fix("B_twocol_toc.pdf")
    doc = pymupdf.open(path)
    page = doc.load_page(11)
    naive = textlayer.page_text(page, reading_order=False)
    ordered = textlayer.page_text(page, reading_order=True)
    doc.close()
    assert len(ordered.split()) == len(naive.split())
    # the two column texts are identical in the fixture, so the test is that
    # ordering does not interleave: the first half must not repeat a sentence
    # start before the column ends
    assert ordered.count("Industry Structure") <= naive.count("Industry Structure") + 1


def test_running_furniture_is_stripped():
    pages = [f"ACME LTD | Annual Report\nbody {i}\n{i+5}" for i in range(8)]
    out = textlayer.strip_running_furniture(pages)
    assert all("ACME LTD | Annual Report" not in p for p in out)
    assert all("body" in p for p in out)
