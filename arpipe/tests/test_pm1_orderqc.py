"""PM1: per-physical-page orphan_start_frac telemetry + `arpipe orderqc`.

Measurement/diagnostic only - see CLAUDE.md / reports/pm1_per_page_orphan.md.
Nothing here exercises MD&A candidate detection, ranking, arbitration,
reading-order behaviour, OCR routing, grading or acceptance: those are
unchanged, and are covered by the existing test_pipeline.py suite (which must
keep passing unmodified alongside this file - see M1.9 regression checks).

Run: python -m pytest arpipe/tests/test_pm1_orderqc.py -v
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import pymupdf
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from arpipe import cli, textlayer, verify  # noqa: E402

FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fixtures")


def _fix(name: str) -> str:
    p = os.path.join(FIX, name)
    if not os.path.exists(p):
        pytest.skip("run tests/make_fixtures.py first")
    return p


_CLEAN = [
    "The global economy grew by an estimated 3.2 per cent in 2024.",
    "Inflation eased through the year as supply chains recovered.",
    "India stayed among the fastest-growing large economies in the world.",
    "Domestic demand was firm and the financial system stayed sound.",
    "Rural consumption revived and government investment picked up.",
    "Exports softened, held back by weak demand in several key markets.",
]

_SCRAMBLED = [
    "GLOBAL ECONOMY",
    "formulation, while posing direct threats to farm output.",
    *[f"Sentence number {i} is in the right order and reads fine." for i in range(6)],
]


def _joined(paras: list[str]) -> str:
    return "\n\n".join(paras)


# --------------------------------------------------------------------- 1-9, 15
# order_quality_by_page: pure unit tests, no PDFs involved.

def test_clean_page_scores_zero():
    out = verify.order_quality_by_page([(1, _joined(_CLEAN))])
    assert out["pages"][1] == 0.0


def test_one_orphan_gives_expected_fraction():
    out = verify.order_quality_by_page([(3, _joined(_SCRAMBLED))])
    doc = verify.order_quality(_joined(_SCRAMBLED))
    assert out["pages"][3] == doc["orphan_start_frac"]
    assert out["pages"][3] > 0.0


def test_page_isolation_bad_page_does_not_leak_into_clean_page():
    out = verify.order_quality_by_page([(5, _joined(_CLEAN)), (6, _joined(_SCRAMBLED))])
    assert out["pages"][5] == 0.0
    assert out["pages"][6] > 0.0


def test_cross_page_paragraph_attribution():
    # The page-join forces a paragraph break at the page boundary (matching
    # the document-level "\n\n".join(ordered) convention pipeline.py already
    # uses), so the orphaned fragment is attributed to the physical page it
    # starts on (page 11), not the page carrying the heading above it (page 10).
    page_a = _joined(["GLOBAL ECONOMY"])
    page_b = _joined(["formulation, while posing direct threats to farm output.",
                      *[f"Sentence number {i} is in the right order and reads fine."
                        for i in range(6)]])
    out = verify.order_quality_by_page([(10, page_a), (11, page_b)])
    assert out["pages"][11] is not None and out["pages"][11] > 0.0


def test_pages_never_passed_in_are_absent_from_the_map():
    out = verify.order_quality_by_page([(3, _joined(_CLEAN))])
    assert 3 in out["pages"]
    assert 9 not in out["pages"]
    # caller (pipeline.py) fills a fixed-length array with None by default,
    # only overwriting entries this map actually reports.
    n_pages = 10
    arr = [None] * n_pages
    for pg, frac in out["pages"].items():
        arr[pg - 1] = frac
    assert arr[8] is None          # page 9: never in the span -> null
    assert arr[2] == 0.0           # page 3: measured, clean


def test_insufficient_paragraphs_on_a_page_is_none_not_a_fake_zero():
    pages = [(1, "Only one short paragraph is on this page entirely."),
            (2, _joined(_CLEAN))]
    out = verify.order_quality_by_page(pages)
    assert out["pages"][1] is None
    assert out["pages"][2] == 0.0


def test_document_level_metric_unchanged_by_the_refactor():
    q = verify.order_quality(_joined(_CLEAN))
    assert q["orphan_start_frac"] == 0.0
    assert q["dangling_end_frac"] == 0.0
    assert q["n_paragraphs"] == 6


def test_page_exactly_at_threshold_is_not_flagged():
    bad = verify.pages_over_diagnostic_threshold([0.03, 0.0301, None])
    assert bad == [(2, 0.0301)]


def test_page_above_threshold_is_flagged():
    bad = verify.pages_over_diagnostic_threshold([0.0, 0.031])
    assert bad == [(2, 0.031)]


def test_deterministic_page_ordering():
    # pages_over_diagnostic_threshold walks the array in physical-page order
    bad = verify.pages_over_diagnostic_threshold([0.09, None, 0.05, 0.0, 0.04])
    assert [p for p, _ in bad] == [1, 3, 5]


# ------------------------------------------------------------------ 10, 11
# full-width-block diagnostic: real pymupdf page geometry.

def _make_pdf(path: str, boxes: list[tuple[tuple[float, float, float, float], str]],
             align: int = 0) -> None:
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    for rect, text in boxes:
        page.insert_textbox(pymupdf.Rect(*rect), text, fontsize=9, fontname="helv",
                            align=align)
    doc.save(path)
    doc.close()


def test_full_width_block_true(tmp_path):
    path = str(tmp_path / "wide.pdf")
    # Justified (align=3) so every non-final line is stretched to the rect's
    # full width - the actual "wide" mechanism _column_cut's own docstring
    # describes (a running head / full-width banner masking the gutter).
    _make_pdf(path, [
        ((40, 700, 555, 760), ("a running footer that spans the full page width " * 6)),
        ((56, 100, 288, 400), ("left column text " * 30)),
        ((303, 100, 540, 400), ("right column text " * 30)),
    ], align=pymupdf.TEXT_ALIGN_JUSTIFY)
    assert textlayer.page_has_full_width_block(path, 0) is True


def test_full_width_block_false(tmp_path):
    path = str(tmp_path / "twocol.pdf")
    _make_pdf(path, [
        ((56, 100, 288, 400), ("left column text " * 30)),
        ((303, 100, 540, 400), ("right column text " * 30)),
    ])
    assert textlayer.page_has_full_width_block(path, 0) is False


def test_full_width_block_none_when_page_out_of_range(tmp_path):
    path = str(tmp_path / "onepage.pdf")
    _make_pdf(path, [((56, 100, 540, 400), "some text")])
    assert textlayer.page_has_full_width_block(path, 5) is None


# --------------------------------------------------------------- 12, 13, 14
# arpipe orderqc: multiple bad pages printed, hidden-aggregate counted
# correctly, an already-bad document is not double-counted as "hidden".

def _write_manifest(root: str, rows: list[dict]) -> None:
    os.makedirs(root, exist_ok=True)
    with open(os.path.join(root, "manifest.jsonl"), "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")


def test_orderqc_multiple_bad_pages_and_hidden_aggregate(tmp_path, capsys):
    out = tmp_path / "dataset"
    rows = [
        {   # document-level score reads clean, but two pages spike -> "hidden"
            "company_id": "ISIN_AAA", "fy_end": 2015, "ok": True, "confidence": "medium",
            "path": "companies/AAA/2015/mda.txt",
            "qc": {"orphan_start_frac": 0.01,
                  "orphan_start_frac_pages": [0.0, 0.05, None, 0.09]},
        },
        {   # document-level score is ALREADY over the gate -> not "hidden"
            "company_id": "ISIN_BBB", "fy_end": 2016, "ok": False, "confidence": "low",
            "path": "companies/BBB/2016/mda.txt",
            "qc": {"orphan_start_frac": 0.05,
                  "orphan_start_frac_pages": [0.06]},
        },
        {   # nothing over the gate at all -> not printed, not counted
            "company_id": "ISIN_CCC", "fy_end": 2017, "ok": True, "confidence": "high",
            "path": "companies/CCC/2017/mda.txt",
            "qc": {"orphan_start_frac": 0.0, "orphan_start_frac_pages": [0.0, 0.01]},
        },
    ]
    _write_manifest(str(out), rows)
    json_out = tmp_path / "orderqc.json"
    args = argparse.Namespace(out=str(out), companies="a_file_that_does_not_exist.csv",
                              json=str(json_out))

    rc = cli.cmd_orderqc(args)
    assert rc == 0

    with open(json_out, encoding="utf-8") as fh:
        data = json.load(fh)

    summary = data["summary"]
    assert summary["documents_with_bad_pages"] == 2          # AAA and BBB
    assert summary["documents_with_hidden_bad_page"] == 1    # AAA only
    assert summary["total_bad_pages"] == 3                   # AAA:2 + BBB:1

    pages = data["pages"]
    assert len(pages) == 3
    # every bad page printed, not just the worst one per document
    aaa_pages = [p["physical_page"] for p in pages if p["company_id"] == "ISIN_AAA"]
    assert aaa_pages == [2, 4]                                # deterministic order

    captured = capsys.readouterr()
    assert captured.out.count("ISIN_AAA") == 2
    assert captured.out.count("ISIN_BBB") == 1
    assert "ISIN_CCC" not in captured.out.split("{")[0]       # never printed as a page row


def test_already_bad_document_not_double_counted_as_hidden():
    assert verify.document_hides_bad_page(0.05, [0.06]) is False
    assert verify.document_hides_bad_page(0.01, [0.0, 0.09]) is True
    assert verify.document_hides_bad_page(0.03, [0.031]) is True   # doc score AT the gate


# ------------------------------------------------------------------------ 16
# JSON round-trip preserves the None ("not measured") / float distinction.

def test_json_roundtrip_preserves_null_semantics():
    arr = [None, 0.0, 0.0523, None]
    assert json.loads(json.dumps(arr)) == arr


# ------------------------------------------------------------------------ 17
# Exercising the new diagnostics cannot change what real extraction produces.

def test_page_telemetry_is_side_effect_free_on_a_real_fixture():
    from arpipe import segment, triage  # noqa: E402 (heavier deps, only needed here)

    path = _fix("B_twocol_toc.pdf")
    span = list(range(10, 17))

    prose_before, _, _ = textlayer.extract_prose_and_tables(path, span, {}, set(span))
    mda_before = "\n\n".join(t for t in prose_before if t.strip()).strip()
    doc_before = verify.order_quality(mda_before)

    # exercise every new PM1 entry point heavily, including on real pages
    pages = [(n + 1, t) for n, t in zip(span, prose_before)]
    verify.order_quality_by_page(pages)
    verify.pages_over_diagnostic_threshold([0.0, 0.05, None])
    verify.document_hides_bad_page(0.01, [0.0, 0.05])
    for n in span:
        textlayer.page_has_full_width_block(path, n)

    prose_after, _, _ = textlayer.extract_prose_and_tables(path, span, {}, set(span))
    mda_after = "\n\n".join(t for t in prose_after if t.strip()).strip()
    doc_after = verify.order_quality(mda_after)

    assert prose_after == prose_before
    assert doc_after == doc_before


def test_page_reconstruction_matches_document_reconstruction_on_real_fixture():
    # Strongest guarantee that the page-level metric is the SAME calculation,
    # not a re-derived one: tag every source line with its physical page,
    # reconstruct, and confirm the paragraph list (and therefore every
    # orphan/dangling flag) is byte-identical to the untagged, document-level
    # reconstruction over the exact same underlying page text.
    path = _fix("B_twocol_toc.pdf")
    span = list(range(10, 17))
    prose, _, _ = textlayer.extract_prose_and_tables(path, span, {}, set(span))
    mda_text = "\n\n".join(t for t in prose if t.strip()).strip()

    doc_paras = verify._reconstruct_paragraphs(mda_text)

    kept = [(n + 1, t) for n, t in zip(span, prose) if t.strip()]
    tagged_lines: list[tuple[str, int | None]] = []
    for i, (pg, t) in enumerate(kept):
        tagged_lines.extend((ln, pg) for ln in t.split("\n"))
        if i != len(kept) - 1:
            tagged_lines.append(("", None))
    tagged = verify._reconstruct_paragraphs_tagged(tagged_lines)
    page_paras = [p for p, _ in tagged]

    assert page_paras == doc_paras
    assert all(pg is not None for _, pg in tagged)   # every paragraph owned by exactly one page

    doc_orphans, _, doc_flags, _ = verify._score_paragraphs(doc_paras)
    page_orphans, _, page_flags, _ = verify._score_paragraphs(page_paras)
    assert doc_flags == page_flags
    assert doc_orphans == page_orphans

    page_q = verify.order_quality_by_page(
        [(n + 1, t) for n, t in zip(span, prose)], min_paragraphs=0)
    assert page_q["n_paragraphs_total"] == len(doc_paras)


def test_diagnostic_threshold_is_a_fixed_independent_constant():
    # PM1 explicitly must not recalibrate the 0.03 gate, and must not couple
    # the diagnostic reporting cutoff to a future change of the production
    # gate - they are separate names on purpose.
    assert verify.PAGE_ORPHAN_DIAGNOSTIC_THRESHOLD == 0.03
    assert verify.PAGE_ORPHAN_DIAGNOSTIC_THRESHOLD == verify.ORPHAN_START_FRAC_MAX
