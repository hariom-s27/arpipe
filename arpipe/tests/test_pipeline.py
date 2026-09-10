"""Unit tests over the synthetic fixtures. Run: python -m pytest tests -q"""
from __future__ import annotations

import json
import os
import shutil
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
        "company_id": "INE123A01012",
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


def test_isin_regex_and_checksum():
    from arpipe.patterns import ISIN_RE, is_valid_isin

    # Valid Indian ISINs (all pass regex and check-digit)
    valid_sample = [
        "INE175A01038",  # Jain ordinary equity
        "IN9175A01010",  # Jain DVR equity
        "INE001B01026",  # KRBL ordinary equity
        "INE123A01012",  # Fixture
        "US0378331005",  # Apple (international Luhn test)
    ]
    for isin in valid_sample:
        assert is_valid_isin(isin), f"{isin} should pass check-digit"
        if isin.startswith("IN"):
            assert ISIN_RE.match(isin), f"{isin} should match ISIN_RE"

    # Bad check-digit
    assert not is_valid_isin("INE123A01016")

    # English words matching initial prefix must fail check-digit and terminal-digit regex
    english_words = [
        "INCORPORATED", "INDEPENDENCE", "INDEBTEDNESS", "INEFFICIENCY",
        "INDIVIDUALLY", "INFRINGEMENT", "INDEMNIFYING", "INCONSISTENT",
        "INTELLECTUAL", "INSTRUCTIONS",
    ]
    for w in english_words:
        assert not is_valid_isin(w), f"{w} should fail check digit"
        assert not ISIN_RE.match(w), f"{w} should not match ISIN_RE"


def test_extract_isin_provenance_and_priority():
    # Synthetic multi-page document:
    # Page 0: Cover (no ISIN)
    # Page 10: MD&A
    # Page 16: Corporate Governance with both ordinary and DVR
    pages = {
        0: "Annual Report 2024-25\nAcme Corp\nCIN: L27100MH1994PLC078367",
        10: "Management Discussion and Analysis\nIndustry Structure...",
        16: ("Report on Corporate Governance\nGeneral Shareholder Information\n"
             "Ordinary Equity Shares: INE175A01038\n"
             "DVR Equity Shares: IN9175A01010\nDepositories: NSDL, CDSL"),
    }

    # Undeclared company: prefers INE over IN9
    co_no_isin = Company(company_id="X", canonical_name="Acme Corp")
    best, pno, seen = verify.extract_isin(pages, company=co_no_isin)
    assert best == "INE175A01038"
    assert pno == 16
    assert seen == ["INE175A01038", "IN9175A01010"]

    # Declared DVR company (Bug 6 / P4 scenario): matches declared DVR ISIN
    co_dvr = Company(company_id="X", canonical_name="Acme Corp", isin="IN9175A01010")
    best_dvr, pno_dvr, seen_dvr = verify.extract_isin(pages, company=co_dvr)
    assert best_dvr == "IN9175A01010"
    assert pno_dvr == 16
    assert seen_dvr == ["INE175A01038", "IN9175A01010"]

    # In verify(): company_ok is True if declared ISIN in seen
    vrep = verify.verify(pages[0], pages[10], co_dvr, 2025, page_texts=pages)
    assert vrep.isin_found == "IN9175A01010"
    assert vrep.isin_found_on_page == 16
    assert vrep.company_ok is True
    assert "isin:exact_match" in vrep.company_evidence


def _blobs_present() -> bool:
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "live_store")
    doc_jsonl = os.path.join(root, "documents.jsonl")
    if not os.path.exists(doc_jsonl):
        return False
    try:
        import json
        with open(doc_jsonl, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    row = json.loads(line)
                    blob = store.blob_abspath(root, row.get("path", ""))
                    if not os.path.exists(blob):
                        return False
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _blobs_present(), reason="live_store blobs not present")
def test_isin_extracted_on_live_store_blobs():
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "live_store")
    doc_jsonl = os.path.join(root, "documents.jsonl")
    found_count = 0
    with open(doc_jsonl, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            blob = store.blob_abspath(root, row["path"])
            texts = textlayer.extract_pages(blob)
            co = Company(company_id=row["company_id"], canonical_name="Test", isin=row.get("company_id"))
            best, pno, seen = verify.extract_isin(texts, company=co)
            if best:
                found_count += 1
    # Prompt acceptance: non-null for at least 3 of the 4 sample documents
    assert found_count >= 3


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


def test_section_qc_labels_the_orphan_basis():
    qc = verify.section_qc(_ORDERED_PROSE)
    assert qc["orphan_basis"] == "prose_only"
    assert qc["orphan_gate_version"] == "p17.1"
    assert qc["orphan_gate_max"] == verify.ORPHAN_START_FRAC_MAX


# --------------------------------------------------------------- P21 reason codes
def _clean_rep():
    r = VerificationReport(company_ok=True, year_ok=True)
    r.year_evidence = ["modal_fy:2025:w39"]           # above the weight floor
    return r


_JAIN_QC = {"orphan_start_frac": 0.064, "orphan_gate_max": 0.03,
            "leaks": [], "too_short": False, "too_long": False}

# real tail of Jain Irrigation FY2024 MD&A - a forward-looking caution, no heading
_JAIN_FY24_TAIL = (
    "The Management issues a warning that some of the aforementioned "
    "statements are directional and forwardlooking, management estimates and "
    "may not represent the accuracy of the underlying predictions as they "
    "depend on a number of variables, some of which may be beyond the "
    "management's control.")

# real tail of KRBL FY2025 - the section stops on a running footer, no caution
_KRBL_FY25_TAIL = (
    "In addition to cybersecurity measures, our Cyber insurance coverage "
    "provides financial protection and assistance in the event of cyber "
    "incidents, mitigating potential financial losses and liabilities.\n\n"
    "Annual Report 2024-25")


def test_reasons_source_shredded_when_column_splitter_fired():
    # orphan_start_frac over the gate, but P16B's splitter fired on most span
    # pages -> the residual is the source, not xy_cut. (No reprocessor producer
    # here; the signal is the fire fraction alone.)
    reasons = verify.build_reasons(_clean_rep(), _JAIN_QC,
                                   column_cut_fire_frac=0.86,
                                   pdf_producer="Adobe PDF Library 11.0",
                                   mda_text="body\n" * 20 + _JAIN_FY24_TAIL)
    assert reasons == ["source_shredded"]


def test_reasons_order_scrambled_when_column_splitter_did_not_fire():
    # over the gate, splitter idle, native PDF -> xy_cut can still do better
    reasons = verify.build_reasons(_clean_rep(), _JAIN_QC,
                                   column_cut_fire_frac=0.1,
                                   pdf_producer="Adobe PDF Library 11.0",
                                   mda_text="body\n" * 20 + _JAIN_FY24_TAIL)
    assert reasons == ["order_scrambled"]


def test_reasons_source_shredded_from_reprocessor_even_with_clean_metrics():
    # P22: an iLovePDF doc is labelled source_shredded regardless of a clean
    # orphan_start_frac and an idle column splitter - the shredding is a fact
    # about the source, and it must not read as order_scrambled
    clean_qc = {**_JAIN_QC, "orphan_start_frac": 0.012}
    reasons = verify.build_reasons(_clean_rep(), clean_qc,
                                   column_cut_fire_frac=0.2,
                                   pdf_producer="iLovePDF",
                                   mda_text="body\n" * 20 + _JAIN_FY24_TAIL)
    assert reasons == ["source_shredded"]


def test_reprocessor_doc_is_capped_at_medium():
    # P22: a would-be `high` row from a reprocessor PDF is capped at `medium`
    rep = _clean_rep()
    qc = {"too_short": False, "long_token_frac": 0.0, "leaks": [],
          "orphan_start_frac": 0.012}
    assert verify.grade(rep, qc, 0.95, supporters=2) == "high"                       # native
    assert verify.grade(rep, qc, 0.95, supporters=2,
                        pdf_producer="Adobe PDF Library 11.0") == "high"
    assert verify.grade(rep, qc, 0.95, supporters=2, pdf_producer="iLovePDF") == "medium"


def test_list_markers_are_not_orphan_starts():
    run_in_list = ("Several drivers underpin this outlook. a) input costs eased "
                   "through the year. b) capacity utilisation improved. "
                   "c) working capital discipline held.")
    body = [f"Sentence {i} here is in the right order and reads fine."
            for i in range(6)]
    assert verify.order_quality("\n\n".join([run_in_list, *body]))["orphan_starts"] == 0
    # a genuine lowercase splice under a heading is still caught
    spliced = ["GLOBAL ECONOMY",
               "formulation, while posing direct threats to farm output.", *body]
    assert verify.order_quality("\n\n".join(spliced))["orphan_starts"] >= 1


def test_producer_summary_flags_reprocessors():
    rows = [{"qc": {"pdf_producer": "iLovePDF"}},
            {"qc": {"pdf_producer": "iLovePDF"}},
            {"qc": {"pdf_producer": "Adobe PDF Library 11.0"}},
            {"qc": {}}]
    summ = verify.producer_summary(rows)
    assert summ["iLovePDF"] == {"n": 2, "reprocessor": True}
    assert summ["Adobe PDF Library 11.0"]["reprocessor"] is False
    assert summ["unknown"]["n"] == 1
    assert sum(1 for r in rows
               if verify.is_reprocessor((r.get("qc") or {}).get("pdf_producer"))) == 2


def test_reasons_span_truncated_on_missing_cautionary_ending():
    assert verify.tail_has_cautionary(_JAIN_FY24_TAIL)
    assert not verify.tail_has_cautionary(_KRBL_FY25_TAIL)
    clean_qc = {**_JAIN_QC, "orphan_start_frac": 0.004}
    reasons = verify.build_reasons(_clean_rep(), clean_qc,
                                   column_cut_fire_frac=0.9,
                                   mda_text="body\n" * 20 + _KRBL_FY25_TAIL)
    assert reasons == ["span_truncated"]


def test_reasons_empty_on_a_clean_high_row():
    clean_qc = {**_JAIN_QC, "orphan_start_frac": 0.0}
    reasons = verify.build_reasons(_clean_rep(), clean_qc,
                                   column_cut_fire_frac=0.9,
                                   mda_text="body\n" * 20 +
                                   "Cautionary Statement Readers are advised that "
                                   "these forward-looking statements are subject to risks.")
    assert reasons == []


def test_grade_downgrades_scrambled_reading_order():
    rep = VerificationReport(company_ok=True, year_ok=True)
    base = {"too_short": False, "long_token_frac": 0.0, "leaks": [],
            "orphan_start_frac": 0.0}
    assert verify.grade(rep, base, 0.95, supporters=2) == "high"
    mild = {**base, "orphan_start_frac": verify.ORPHAN_START_FRAC_MAX + 0.005}
    assert verify.grade(rep, mild, 0.95, supporters=2) == "medium"
    bad = {**base, "orphan_start_frac": 2 * verify.ORPHAN_START_FRAC_MAX + 0.005}
    assert verify.grade(rep, bad, 0.95, supporters=2) == "low"


def test_grade_supporters_gate():
    rep = VerificationReport(company_ok=True, year_ok=True)
    qc = {"too_short": False, "long_token_frac": 0.0, "leaks": [],
          "orphan_start_frac": 0.0}
    # KRBL FY2025 bug: zero methods agreed -> cannot be `high`, however clean
    assert verify.grade(rep, qc, 0.95, supporters=0) == "medium"
    # no support and a weak span -> `low`
    assert verify.grade(rep, qc, 0.65, supporters=0) == "low"
    # two independent methods agreed, clean span -> `high`
    assert verify.grade(rep, qc, 0.85, supporters=2) == "high"
    # one supporter, mediocre score, a single leak -> `medium`
    leak_qc = {**qc, "leaks": ["auditor_report_leak"]}
    assert verify.grade(rep, leak_qc, 0.65, supporters=1) == "medium"


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


# ----------------------------------------------- P23: order-independent furniture
_A4 = pymupdf.Rect(0, 0, 595, 842)      # zone = y <= 67.4 (top) or y >= 774.6 (bottom)


def _syn_page(head, body, pageno, extra=None):
    bl = [textlayer.Block(40, 20, 555, 34, head),           # running head, top band
          textlayer.Block(40, 120, 555, 400, body),         # body, out of the band
          textlayer.Block(280, 812, 315, 826, str(pageno))]  # page number, bottom band
    if extra:
        bl.append(textlayer.Block(40, 50, 300, 64, extra))  # extra block in the top band
    return bl


def test_furniture_detected_from_geometry_and_repetition():
    head = "ACME INDUSTRIES LIMITED  |  Annual Report 2019-20"
    pages = [(_syn_page(head, f"Body paragraph {i} reads fine and in order.",
                        i + 3, "Opportunities and Threats" if i == 4 else None), _A4)
             for i in range(12)]
    furniture = textlayer._furniture_strings(pages)
    assert textlayer._furniture_norm(head) in furniture                       # all 12
    assert textlayer._furniture_norm("Opportunities and Threats") not in furniture  # 1

    kept, removed = textlayer._strip_furniture_blocks(pages[4][0], _A4, furniture)
    kept_text = " ".join(b.text for b in kept)
    assert "Opportunities and Threats" in kept_text     # one-off top-band heading stays
    assert "ACME INDUSTRIES LIMITED" not in kept_text   # repeating running head goes
    assert head in removed


def test_furniture_year_variants_fold_to_one_key():
    # "Annual Report 2023-24" and "...2024-25" must count as the same furniture
    assert (textlayer._furniture_norm("Annual Report 2023-24")
            == textlayer._furniture_norm("Annual Report 2024-25"))


def test_furniture_detection_does_not_depend_on_block_order():
    # the P23 point: furniture is found from geometry + repetition, before any
    # reading-order sort, so shuffling the blocks must not change the outcome
    import random

    head = "ACME INDUSTRIES LIMITED  |  Annual Report 2019-20"
    pages = [_syn_page(head, f"Distinct body {i} carrying its own words.", i + 3,
                       "Segment Performance" if i == 2 else None)
             for i in range(10)]
    base = textlayer._furniture_strings([(p, _A4) for p in pages])

    rng = random.Random(0)
    shuffled = [rng.sample(p, len(p)) for p in pages]
    assert textlayer._furniture_strings([(p, _A4) for p in shuffled]) == base

    for p_ord, p_shuf in zip(pages, shuffled):
        k1, r1 = textlayer._strip_furniture_blocks(p_ord, _A4, base)
        k2, r2 = textlayer._strip_furniture_blocks(p_shuf, _A4, base)
        assert sorted(r1) == sorted(r2)                        # same blocks removed
        assert {b.text for b in k1} == {b.text for b in k2}    # same blocks kept


def test_extract_prose_and_tables_strips_the_running_header():
    # end to end on a fixture: ACME running head is in the top band on every page
    path = _fix("B_twocol_toc.pdf")
    span = list(range(10, 17))
    prose, _, diag = textlayer.extract_prose_and_tables(path, span, {}, set(span))
    assert diag["furniture_blocks_removed"] >= len(span)       # one per page
    assert "acme industries limited | annual report -" in diag["furniture_strings"]
    assert all("ACME INDUSTRIES LIMITED" not in p for p in prose)


# --------------------------------------------------------- table/chart quarantine
def _blk(text, x0=100.0, y0=0.0):
    return textlayer.Block(x0, y0, x0 + 60.0, y0 + 10.0, text)


# the GVA chart from Jain Irrigation FY2024/25 p105, one block per axis value
_GVA_CHART = ["Gross Value Added by Agriculture and Allied sectors",
              "(US $ billion) (at constant 2011-12 prices)",
              "350.00", "300.00", "250.00", "283.68", "200.00", "267.90",
              "276.37", "279.00", "259.71", "150.00", "0.00",
              "FY 18", "FY 19", "FY 20", "FY 21", "FY 22", "FY 24", "FY 23",
              "Agriculture 4.0 is the fourth agricultural revolution, aiming to "
              "enhance yield quality while minimising environmental damage."]


def test_quarantine_lifts_a_chart_axis_dump():
    blocks = [_blk(t, y0=i * 12) for i, t in enumerate(_GVA_CHART)]
    kept, entries = textlayer._quarantine_page(105, blocks)
    kept_text = "\n".join(b.text for b in kept)
    assert len(entries) == 1
    e = entries[0]
    assert e["page"] == 105 and e["kind"] == "chart"
    assert e["n_lines"] >= 10 and e["digit_ratio"] > 0.4
    assert e["bbox"] is not None and len(e["bbox"]) == 4
    assert "283.68" in e["text"] and "FY 24" in e["text"]
    # prose on both sides of the chart survives
    assert "Gross Value Added by Agriculture" in kept_text
    assert "fourth agricultural revolution" in kept_text
    assert "283.68" not in kept_text and "FY 24" not in kept_text


def test_quarantine_marks_a_labelled_table():
    # the "Employee benefit expenses" row from the P18 brief
    blocks = [_blk(t, y0=i * 12) for i, t in enumerate(
        ["Employees", "benefit", "expenses",
         "3,525.13 3,218.21", "306.92", "9.54%"])]
    _, entries = textlayer._quarantine_page(122, blocks)
    assert len(entries) == 1
    assert entries[0]["kind"] == "table"          # multi-value line "3,525.13 3,218.21"
    assert "9.54%" in entries[0]["text"]


def test_quarantine_keeps_prose_with_a_few_numbers():
    prose = ("According to Bain & Co., the Indian agricultural sector is "
             "predicted to increase to US$ 30-35 billion by 2025, up from "
             "roughly 24 billion in 2020.")
    blocks = [_blk("India stayed among the fastest-growing large economies."),
              _blk(prose, y0=20),
              _blk("Domestic demand was firm and the financial system sound.",
                   y0=40)]
    kept, entries = textlayer._quarantine_page(1, blocks)
    assert entries == []
    assert prose in "\n".join(b.text for b in kept)


def test_quarantine_keeps_a_block_that_mixes_cells_and_a_sentence():
    # one PyMuPDF block: table tail + a real sentence spliced on by shredding
    mixed = ("48,337.25\n1,373.52\n20,032.24\nIncrease in equity share capital "
             "and share premium by Rs.24.08 million due to issue of shares to "
             "domestic and foreign lenders.")
    blocks = [_blk("Balance as on 1st April 2024", y0=0),
              _blk("1,247.80\n18,344.19\n3,948.64", y0=12),
              _blk(mixed, y0=24)]
    kept, entries = textlayer._quarantine_page(225, blocks)
    kept_text = "\n".join(b.text for b in kept)
    assert "Increase in equity share capital" in kept_text     # sentence survives
    assert "domestic and foreign lenders" in kept_text


def test_quarantine_conserves_every_word():
    blocks = [_blk(t, y0=i * 12) for i, t in enumerate(_GVA_CHART)]
    kept, entries = textlayer._quarantine_page(105, blocks)
    before = sum(len(t.split()) for t in _GVA_CHART)
    after = (sum(len(b.text.split()) for b in kept)
             + sum(len(e["text"].split()) for e in entries))
    assert before == after                        # quarantine moves, never drops


# ------------------------------------------------- P19: link and path portability
def test_link_pdf_reports_hardlink_on_same_volume(tmp_path):
    src = tmp_path / "blob.pdf"
    src.write_bytes(b"%PDF-1.4\n%%EOF\n")
    mode = store.link_pdf(str(src), str(tmp_path / "tree" / "annual_report.pdf"))
    assert mode == "hardlink"
    assert (tmp_path / "tree" / "annual_report.pdf").read_bytes() == src.read_bytes()


def test_link_pdf_is_idempotent_and_still_reports_the_real_mode(tmp_path):
    src = tmp_path / "blob.pdf"
    src.write_bytes(b"%PDF-1.4\n%%EOF\n")
    dest = tmp_path / "tree" / "annual_report.pdf"
    assert store.link_pdf(str(src), str(dest)) == "hardlink"
    assert store.link_pdf(str(src), str(dest)) == "hardlink"   # re-derived, not "exists"


def test_link_pdf_falls_back_to_copy_and_reports_it(tmp_path, monkeypatch, capsys):
    src = tmp_path / "blob.pdf"
    src.write_bytes(b"%PDF-1.4\n%%EOF\n")

    def no_link(*a, **k):
        raise OSError("hardlink unavailable")

    def cross_drive_symlink(*a, **k):
        # what os.symlink(os.path.relpath(...)) raises across Windows drives
        raise ValueError("path is on mount 'D:', start on mount 'C:'")

    monkeypatch.setattr(store.os, "link", no_link)
    monkeypatch.setattr(store.os, "symlink", cross_drive_symlink)

    dest = tmp_path / "other" / "annual_report.pdf"
    mode = store.link_pdf(str(src), str(dest))
    assert mode == "copy"
    assert dest.read_bytes() == src.read_bytes()
    assert "WARN link_pdf: copied" in capsys.readouterr().err


def test_rel_to_root_uses_forward_slashes(tmp_path):
    p = os.path.join(str(tmp_path), "companies", "ACME__X", "2015", "mda.txt")
    rel = store.rel_to_root(p, str(tmp_path))
    assert rel == "companies/ACME__X/2015/mda.txt"


def test_blob_abspath_resolves_root_relative_and_legacy(tmp_path):
    root = tmp_path / "store"
    blob = root / "blobs" / "ab" / "cd" / "abcd.pdf"
    blob.parent.mkdir(parents=True)
    blob.write_bytes(b"x")

    # current format: relative to the store root, forward slashes
    assert store.blob_abspath(str(root), "blobs/ab/cd/abcd.pdf") == str(blob)
    # absolute legacy path is passed through
    assert store.blob_abspath(str(root), str(blob)) == str(blob)
    # unresolvable relative path still yields something absolute (no crash)
    assert os.path.isabs(store.blob_abspath(str(root), "blobs/zz/zz/none.pdf"))


def test_extract_is_cwd_independent_and_records_link_mode(tmp_path, monkeypatch):
    from arpipe import universe
    import argparse

    src = _fix("A_digital_outline.pdf")
    sha = fetch.sha256_file(src)

    root = tmp_path / "store"
    blob = root / "blobs" / sha[:2] / sha[2:4] / f"{sha}.pdf"
    blob.parent.mkdir(parents=True)
    shutil.copy2(src, blob)

    doc = {"company_id": "INE123A01012", "fy_end": 2015, "sha256": sha,
           "path": f"blobs/{sha[:2]}/{sha[2:4]}/{sha}.pdf",
           "n_bytes": blob.stat().st_size, "n_pages": 40,
           "source": "test", "url": "http://example.test/ar.pdf"}
    (root / "documents.jsonl").write_text(json.dumps(doc) + "\n", encoding="utf-8")

    companies = tmp_path / "companies.csv"
    universe.to_csv([Company(company_id="INE123A01012",
                             canonical_name="ACME INDUSTRIES LIMITED",
                             isin="INE123A01012")],
                    str(companies))

    out = tmp_path / "dataset"
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)                       # run from an unrelated cwd

    args = argparse.Namespace(root=str(root), out=str(out), companies=str(companies),
                              workers=1, resume=False, keep_pages=False,
                              vlm_url=None, vlm_model="x", textract=False,
                              aws_region="ap-south-1")
    assert cli.cmd_extract(args) == 0

    rows = store.load_manifest(str(out))
    assert rows, "extract wrote no manifest row"
    row = rows[0]
    assert row["path"] and not os.path.isabs(row["path"])
    assert row["path"].startswith("companies/") and "\\" not in row["path"]
    assert "mda_path" not in row                       # the duplicate is gone

    year_dir = out / os.path.dirname(row["path"])
    docjson = json.loads((year_dir / "document.json").read_text(encoding="utf-8"))
    assert docjson["link_mode"] in {"hardlink", "symlink", "copy"}
    # blob path normalised to store-root-relative, forward slashes
    assert docjson["path"] == f"blobs/{sha[:2]}/{sha[2:4]}/{sha}.pdf"

    mdajson = json.loads((year_dir / "mda.json").read_text(encoding="utf-8"))
    assert mdajson["path"] == row["path"]
    if mdajson["ok"]:
        assert mdajson["path"] is not None
    # P3: ISIN found on Corporate Governance page (page 16), outside front matter & MD&A
    vrep = mdajson["verification"]
    assert vrep["isin_found"] == "INE123A01012"
    assert vrep["isin_found_on_page"] == 16
    assert "INE123A01012" in vrep["isins_seen"]


def test_collapse_universe_jain_case():
    from arpipe import universe
    from arpipe.models import Company

    c1 = Company(company_id="INE175A01038",
                 canonical_name="Jain Irrigation Systems Limited",
                 isin="INE175A01038",
                 nse_symbol="JISLJALEQS")
    c2 = Company(company_id="IN9175A01010",
                 canonical_name="Jain Irrigation Systems Limited",
                 isin="IN9175A01010",
                 nse_symbol="JISLDVREQS")

    collapsed, removed = universe.collapse_universe([c1, c2])
    assert removed == 1
    assert len(collapsed) == 1

    row = collapsed[0]
    assert row.company_id == "INE175A01038"
    assert "IN9175A01010" in row.alternate_isins
    assert row.series_type == "ordinary"

    # Order invariance: DVR line passed first still collapses to ordinary primary
    collapsed_rev, removed_rev = universe.collapse_universe([c2, c1])
    assert removed_rev == 1
    assert len(collapsed_rev) == 1
    assert collapsed_rev[0].company_id == "INE175A01038"
    assert "IN9175A01010" in collapsed_rev[0].alternate_isins
    assert collapsed_rev[0].series_type == "ordinary"


def test_detect_series_type():
    from arpipe import universe

    # ordinary
    assert universe.detect_series_type("INE175A01038", "JISLJALEQS") == "ordinary"
    assert universe.detect_series_type("INE001B01026", "KRBL") == "ordinary"
    assert universe.detect_series_type("INE217G01035", "EQUIPPP") == "ordinary"

    # dvr
    assert universe.detect_series_type("IN9175A01010", "JISLDVREQS") == "dvr"
    assert universe.detect_series_type("INE224E01036", "GATECHDVR") == "dvr"
    assert universe.detect_series_type("IN9623B01058", "FELDVR") == "dvr"

    # partly_paid
    assert universe.detect_series_type("INE123A01012", "RELIANCE-RE") == "partly_paid"
    assert universe.detect_series_type("INE123A01012", "ABCDEF-PP") == "partly_paid"

    # other
    assert universe.detect_series_type("INF123A01012", "NIFTYBEES") == "other"


def test_cmd_audit_asserts_sha256_and_cin_fy_uniqueness(tmp_path, capsys):
    import argparse
    from arpipe import cli

    manifest = tmp_path / "manifest.jsonl"
    r1 = {
        "company_id": "INE001B01026", "fy_end": 2024, "sha256": "sha111",
        "ok": True, "confidence": "high", "n_words": 5000,
        "verification": {"cin_found": "L01111DL1993PLC052845"}
    }
    r2 = {
        "company_id": "INE001B01026", "fy_end": 2025, "sha256": "sha222",
        "ok": True, "confidence": "high", "n_words": 6000,
        "verification": {"cin_found": "L01111DL1993PLC052845"}
    }
    manifest.write_text(json.dumps(r1) + "\n" + json.dumps(r2) + "\n", encoding="utf-8")
    args = argparse.Namespace(out=str(tmp_path))
    assert cli.cmd_audit(args) == 0

    # Duplicate sha256 fails and prints offending rows
    r_dup_sha = {
        "company_id": "IN9175A01010", "fy_end": 2024, "sha256": "sha111",
        "ok": True, "confidence": "high", "n_words": 5000,
        "verification": {"cin_found": "L29120MH1986PLC042028"}
    }
    manifest.write_text(json.dumps(r1) + "\n" + json.dumps(r_dup_sha) + "\n", encoding="utf-8")
    with pytest.raises(AssertionError, match="duplicate sha256"):
        cli.cmd_audit(args)
    err = capsys.readouterr().err
    assert "AUDIT ERROR" in err
    assert "sha111" in err

    # Duplicate (cin, fy_end) fails and prints offending rows
    r_dup_cin = {
        "company_id": "IN9175A01010", "fy_end": 2024, "sha256": "sha333",
        "ok": True, "confidence": "high", "n_words": 5000,
        "verification": {"cin_found": "L01111DL1993PLC052845"}
    }
    manifest.write_text(json.dumps(r1) + "\n" + json.dumps(r_dup_cin) + "\n", encoding="utf-8")
    with pytest.raises(AssertionError, match=r"duplicate \(cin, fy_end\)"):
        cli.cmd_audit(args)
    err = capsys.readouterr().err
    assert "AUDIT ERROR" in err
    assert "L01111DL1993PLC052845" in err


def test_terminator_shape_rejects_body_word_and_accepts_heading():
    from arpipe import segment
    from arpipe.models import MDASpan

    texts = {
        10: "Management Discussion and Analysis\nOverview of the market and business operations.",
        11: "Operating Performance\nRevenue and operating margins improved across business units.",
        12: "Intellectual Property\nThe company holds various trademarks and copyrights.\n"
            "Our registered trademarks are protected under Indian law.\n"
            "Further details on trademarks and patents appear in the notes.",
        13: "Strategic Outlook\nFuture opportunities and risk factors for the coming year.",
        14: "Report on Corporate Governance\n"
            "1. Company philosophy on Code of Governance\n"
            "The company is committed to ethical standards.",
        15: "Financial Statements\nBalance Sheet as at 31 March 2025",
    }
    # Mid-paragraph "trademarks" on page 12 must NOT terminate the span
    span = MDASpan(10, 15, method="heading")
    trimmed = segment.trim_span(span, texts)

    # Must NOT stop at page 11 (which would happen if page 12 terminated)
    # MUST terminate at page 14 ("Report on Corporate Governance" at top of page)
    assert trimmed.end_page == 13
    assert trimmed.terminator_text == "Report on Corporate Governance"
    assert trimmed.terminator_match is not None
    assert trimmed.terminator_match["text"] == "Report on Corporate Governance"
    assert trimmed.terminator_match["page"] == 14
    assert trimmed.terminator_match["shape_ok"] is True
    assert trimmed.terminator_match["line_index"] == 0
    assert trimmed.terminator_match["font_signal"] in ("title_case", "all_caps")


def test_check_terminator_line_shape_rules():
    from arpipe import segment
    from arpipe.segment import HeadingHit

    page = [
        "Report on Corporate Governance",
        "",
        "During the year under review, the Company complied with statutory norms.",
        "Our trademarks and patents are protected.",
        "Report on Corporate Governance was approved by the board.",
    ]

    # Valid heading at top of page
    m1 = segment.check_terminator_line("Report on Corporate Governance", page_no=10, line_idx=0, raw_lines=page)
    assert m1 is not None
    assert m1["shape_ok"] is True
    assert m1["text"] == "Report on Corporate Governance"
    assert m1["line_index"] == 0

    # "trademarks" as a body word -> rejected
    m2 = segment.check_terminator_line("trademarks", page_no=10, line_idx=3, raw_lines=page)
    assert m2 is None

    # Sentence containing a terminator phrase -> rejected (fails whole line check)
    m3 = segment.check_terminator_line("Report on Corporate Governance was approved by the board.",
                                       page_no=10, line_idx=4, raw_lines=page)
    assert m3 is None

    # Line > 80 chars -> rejected (fails length check)
    long_line = "Report on Corporate Governance " + "x" * 60
    assert len(long_line) > 80
    m4 = segment.check_terminator_line(long_line, page_no=10, line_idx=0, raw_lines=page)
    assert m4 is None

    # Bold heading hit -> font_signal == "bold"
    h = HeadingHit(page_no=10, text="Report on Corporate Governance", size=16.0, rel_size=1.4,
                   y_frac=0.15, is_standalone=True, bold=True)
    m5 = segment.check_terminator_line("Report on Corporate Governance", page_no=10, line_idx=0,
                                       raw_lines=page, heading_hit=h)
    assert m5 is not None
    assert m5["font_signal"] == "bold"


def test_toc_offset_not_run_when_no_toc():
    from arpipe import segment
    doc = pymupdf.open()
    doc.new_page()
    texts = {0: "Page with no TOC at all"}
    span, info = segment.from_toc(doc, texts, return_info=True)
    assert span is None
    assert info == {
        "solved": None,
        "confidence": 0.0,
        "samples_used": 0,
        "modal_agreement": 0.0,
        "method": "not_run",
    }
    doc.close()


def test_toc_offset_high_confidence_on_fixture():
    from arpipe import segment, textlayer
    path = _fix("B_twocol_toc.pdf")
    pdf = pymupdf.open(path)
    texts = textlayer.extract_pages(path, list(range(len(pdf))))
    span, info = segment.from_toc(pdf, texts, return_info=True)
    assert span is not None
    assert info["confidence"] >= segment.TOC_OFFSET_CONFIDENCE_THRESHOLD
    assert span.score == 0.80
    assert span.start_page == 10
    assert info["method"] == "margin_folio_mode"
    assert info["solved"] == -1
    pdf.close()


def test_toc_offset_gating_cuts_score_on_low_confidence(monkeypatch):
    from arpipe import segment
    from arpipe.models import DocProfile, PageProfile, PageKind
    doc = pymupdf.open()
    for _ in range(50):
        doc.new_page()
    texts = {
        0: "Cover",
        1: "Contents\nManagement Discussion & Analysis ........... 10\nDirectors' Report ........... 20",
    }
    # Mock _solve_label_offset to return low confidence
    monkeypatch.setattr(segment, "_solve_label_offset", lambda *args, **kw: (3, {
        "solved": 3,
        "confidence": 0.15,
        "samples_used": 20,
        "modal_agreement": 0.15,
        "method": "toc_page_fallback",
    }))

    span, info = segment.from_toc(doc, texts, return_info=True)
    assert span is not None
    assert info["confidence"] == 0.15
    # Score must be cut hard below 0.50
    assert span.score <= 0.40

    # In arbitration, a body_score candidate with 0.65 must beat this gated TOC
    from arpipe.models import Script
    profile = DocProfile(
        sha256="dummy", n_pages=len(doc),
        pages=[PageProfile(i, PageKind.DIGITAL, 0, 100, 1.0, 0.0, 0, 1, Script.LATIN, 0.0)
               for i in range(len(doc))],
        doc_kind="digital", frac_needing_ocr=0.0, has_outline=False
    )
    monkeypatch.setattr(segment, "from_body_scores", lambda *args: MDASpan(
        13, 22, method="body_score", score=0.65
    ))
    monkeypatch.setattr(segment, "from_outline", lambda *args: None)
    monkeypatch.setattr(segment, "from_headings", lambda *args: None)
    monkeypatch.setattr(segment, "from_text_headings", lambda *args: None)

    winner, diag = segment.locate(doc, profile, texts)
    assert winner.method == "body_score"
    assert diag["toc_offset"]["confidence"] == 0.15
    doc.close()


def test_mandated_ratios_tolerant_regex():
    from arpipe.patterns import MANDATED_RATIOS
    from arpipe import verify

    # KRBL phrasing: "Debtor turnover ratio" (no 's'), "Debt-equity ratio", etc.
    krbl_phrases = [
        "Debtor turnover ratio",
        "Inventory turnover ratio",
        "Interest Coverage ratio",
        "Current ratio",
        "Debt-equity ratio",
        "Operating Profit margin",
        "Net profit margin",
        "Return on Net Worth",
    ]
    matched = sum(1 for rx in MANDATED_RATIOS if any(rx.search(p) for p in krbl_phrases))
    assert matched == 8

    # Also verify verify.section_qc cues reports 8 for a text containing all 8
    sample_text = "\n".join(krbl_phrases) + "\nThis is a long financial section with sufficient words to pass."
    qc = verify.section_qc(sample_text)
    assert qc["ratio_cues"] == 8


def test_p7_top_level_fields_and_candidate_span_words():
    from arpipe.models import ExtractionResult, Confidence, MDASpan, to_json
    import json

    res = ExtractionResult(
        company_id="INE001B01026",
        fy_end=2025,
        sha256="dummy",
        ok=True,
        confidence=Confidence.HIGH,
        span=MDASpan(10, 15, method="heading", score=0.9),
        supporters=2,
        method_candidates=[("heading", 10, 15, 0.9), ("toc", 10, 15, 0.8)],
        total_pages=120,
        mda_page_count=6,
        words_per_page=500.0,
    )
    raw = to_json(res)
    obj = json.loads(raw)

    # Top-level fields present in mda.json serialization
    assert obj["supporters"] == 2
    assert obj["method_candidates"] == [["heading", 10, 15, 0.9], ["toc", 10, 15, 0.8]]
    assert obj["total_pages"] == 120
    assert obj["mda_page_count"] == 6
    assert obj["words_per_page"] == 500.0




