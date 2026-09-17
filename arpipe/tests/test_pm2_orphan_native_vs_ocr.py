"""Tests for tools/pm2_orphan_native_vs_ocr.py (P-M2).

These are hermetic: no real PDF/OCR is used anywhere. triage.profile_document
is monkeypatched with small synthetic DocProfile objects so tests run fast
and do not depend on tesseract or any stored corpus.
"""
from __future__ import annotations

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))

from arpipe import verify                                             # noqa: E402
from arpipe.models import DocProfile, PageKind, PageProfile, Script    # noqa: E402

import pm2_orphan_native_vs_ocr as pm2                                 # noqa: E402


def _page(no: int, kind: PageKind) -> PageProfile:
    return PageProfile(page_no=no, kind=kind, n_chars=500, n_words=90,
                       text_area_frac=0.6, image_area_frac=0.1, n_images=0,
                       n_columns=1, script=Script.LATIN, mojibake_ratio=0.0)


def _profile(kinds: dict[int, PageKind], n_pages: int | None = None) -> DocProfile:
    n_pages = n_pages if n_pages is not None else (max(kinds) + 1 if kinds else 0)
    pages = [_page(i, kinds.get(i, PageKind.DIGITAL)) for i in range(n_pages)]
    return DocProfile(sha256="fake", n_pages=n_pages, pages=pages,
                      doc_kind="mixed", frac_needing_ocr=0.0, has_outline=False)


def _ocr_entry(page_no: int, words: int, engine: str = "tesseract:eng") -> dict:
    return {"page_no": page_no, "engine": engine, "words": words, "conf": 0.9}


# --------------------------------------------------------------- Test 1 & 2

class TestProvenanceSplit:
    def test_native_and_ocr_pages_separated(self):
        span = {"start_page": 10, "end_page": 13}
        kinds = {10: PageKind.DIGITAL, 11: PageKind.DIGITAL,
                12: PageKind.SCANNED, 13: PageKind.SCANNED}
        ocr_stats = [_ocr_entry(12, 200), _ocr_entry(13, 150),
                    _ocr_entry(3, 999)]          # page 3 is outside the span, must be ignored
        classes = pm2.classify_span_pages(span, ocr_stats, kinds)
        assert classes == {10: "native", 11: "native", 12: "ocr", 13: "ocr"}
        assert pm2.document_provenance(classes) == "mixed"

    def test_pure_native_document(self):
        span = {"start_page": 0, "end_page": 2}
        kinds = {0: PageKind.DIGITAL, 1: PageKind.DIGITAL, 2: PageKind.DIGITAL}
        classes = pm2.classify_span_pages(span, [], kinds)
        assert set(classes.values()) == {"native"}
        assert pm2.document_provenance(classes) == "native"

    def test_pure_ocr_document(self):
        span = {"start_page": 0, "end_page": 1}
        kinds = {0: PageKind.SCANNED, 1: PageKind.HYBRID}
        ocr_stats = [_ocr_entry(0, 300), _ocr_entry(1, 250)]
        classes = pm2.classify_span_pages(span, ocr_stats, kinds)
        assert set(classes.values()) == {"ocr"}
        assert pm2.document_provenance(classes) == "ocr"

    def test_blank_page_does_not_affect_verdict(self):
        span = {"start_page": 0, "end_page": 2}
        kinds = {0: PageKind.DIGITAL, 1: PageKind.BLANK, 2: PageKind.DIGITAL}
        classes = pm2.classify_span_pages(span, [], kinds)
        assert classes[1] == "blank"
        assert pm2.document_provenance(classes) == "native"


class TestUnknownProvenance:
    def test_failed_ocr_on_non_digital_page_is_unknown_not_native(self):
        span = {"start_page": 0, "end_page": 0}
        kinds = {0: PageKind.SCANNED}
        # OCR was attempted but returned nothing (words=0) - the page has no
        # native text (kind is not DIGITAL) and no usable OCR text either.
        ocr_stats = [_ocr_entry(0, 0)]
        classes = pm2.classify_span_pages(span, ocr_stats, kinds)
        assert classes == {0: "unknown"}

    def test_unknown_page_makes_whole_document_unknown(self):
        span = {"start_page": 0, "end_page": 1}
        kinds = {0: PageKind.DIGITAL, 1: PageKind.BROKEN_TEXT}
        classes = pm2.classify_span_pages(span, [], kinds)
        assert classes[1] == "unknown"
        assert pm2.document_provenance(classes) == "unknown"

    def test_unknown_documents_excluded_from_native_ocr_comparison(self, tmp_path, monkeypatch):
        root = tmp_path / "corpus"
        _write_doc(root, "COMP_A", 2020,
                  span={"start_page": 0, "end_page": 0}, osf=0.5,
                  qc_extra={"ocr_stats": []})
        monkeypatch.setattr(pm2.triage, "profile_document",
                            lambda path: _profile({0: PageKind.BROKEN_TEXT}))
        records = pm2.load_corpus(str(root))
        assert records[0]["provenance"] == "unknown"
        report = pm2.build_report(records, gate=0.03, orphan_basis="prose_only")
        assert report["distribution"]["native"]["N"] == 0
        assert report["distribution"]["ocr"]["N"] == 0


# -------------------------------------------------------------------- Test 3

class TestSameMetricUsed:
    def test_reads_persisted_value_verbatim_not_recomputed(self, tmp_path, monkeypatch):
        """A sentinel orphan_start_frac that no real recomputation from the
        (trivial, unrelated) mda.txt could produce must still come out
        exactly as stored - proving the tool trusts verify.order_quality()'s
        own persisted number instead of re-deriving one."""
        root = tmp_path / "corpus"
        sentinel = 0.4321
        _write_doc(root, "COMP_A", 2021,
                  span={"start_page": 0, "end_page": 0}, osf=sentinel)
        monkeypatch.setattr(pm2.triage, "profile_document",
                            lambda path: _profile({0: PageKind.DIGITAL}))
        records = pm2.load_corpus(str(root))
        assert records[0]["orphan_start_frac"] == sentinel

    def test_order_quality_is_the_only_orphan_implementation_imported(self):
        import inspect
        src = inspect.getsource(pm2)
        assert "def order_quality" not in src
        assert "def _orphan_start" not in src


# -------------------------------------------------------------------- Test 4

class TestThresholdConsistency:
    def test_float_and_explicit_decimals_agree(self):
        d1 = pm2.threshold_diagnostics([0.03], gate=0.03)
        d2 = pm2.threshold_diagnostics([0.030000], gate=0.030000)
        assert d1 == d2
        assert d1["n_at"] == 1
        assert d1["n_above"] == 0
        assert d1["n_below"] == 0

    def test_gate_matches_production_constant(self):
        assert verify.ORPHAN_START_FRAC_MAX == 0.03


# -------------------------------------------------------------------- Test 5

class TestStatistics:
    def test_known_values_linear_percentile(self):
        values = [float(i) for i in range(1, 10)]  # 1..9
        stats = pm2.distribution_stats(values)
        assert stats["N"] == 9
        assert stats["min"] == 1.0
        assert stats["median"] == 5.0
        assert stats["max"] == 9.0
        # numpy linear interpolation: P25 of 1..9 (0-based idx 25%*(9-1)=2) -> value 3
        assert stats["p25"] == 3.0
        assert stats["p75"] == 7.0

    def test_single_value(self):
        stats = pm2.distribution_stats([0.02])
        assert stats["N"] == 1
        assert stats["min"] == stats["max"] == stats["median"] == 0.02


# -------------------------------------------------------------------- Test 6

class TestEmptyOcrPopulation:
    def test_empty_list_stats_are_none_not_zero(self):
        stats = pm2.distribution_stats([])
        assert stats["N"] == 0
        assert stats["min"] is None
        assert stats["median"] is None
        assert stats["max"] is None

    def test_threshold_diagnostics_on_empty_population(self):
        d = pm2.threshold_diagnostics([], gate=0.03)
        assert d["n"] == 0
        assert d["frac_above"] is None
        assert d["gap"] is None

    def test_build_report_with_no_ocr_documents_is_explicit(self, tmp_path, monkeypatch):
        root = tmp_path / "corpus"
        _write_doc(root, "COMP_A", 2019, span={"start_page": 0, "end_page": 0}, osf=0.01)
        monkeypatch.setattr(pm2.triage, "profile_document",
                            lambda path: _profile({0: PageKind.DIGITAL}))
        records = pm2.load_corpus(str(root))
        report = pm2.build_report(records, gate=0.03, orphan_basis="prose_only")
        assert report["distribution"]["ocr"]["N"] == 0
        assert "N = 0" in report["sample_size_notes"]["ocr"]
        assert "impossible to evaluate" in report["sample_size_notes"]["ocr"]


# -------------------------------------------------------------------- Test 7

class TestSmallOcrPopulationWarning:
    def test_small_n_note(self):
        assert "very small" in pm2.sample_size_note(3)
        assert "N = 3" in pm2.sample_size_note(3)

    def test_moderate_and_large_n_notes(self):
        assert "moderate" in pm2.sample_size_note(15)
        assert "large" in pm2.sample_size_note(100)


# -------------------------------------------------------------------- Test 8

class TestBasisMismatch:
    def test_other_basis_not_pooled_with_primary(self, tmp_path, monkeypatch):
        root = tmp_path / "corpus"
        _write_doc(root, "COMP_A", 2020, span={"start_page": 0, "end_page": 0},
                  osf=0.05, basis="prose_only")
        _write_doc(root, "COMP_B", 2020, span={"start_page": 0, "end_page": 0},
                  osf=0.9, basis="prose_and_tables")
        monkeypatch.setattr(pm2.triage, "profile_document",
                            lambda path: _profile({0: PageKind.DIGITAL}))
        records = pm2.load_corpus(str(root))
        report = pm2.build_report(records, gate=0.03, orphan_basis="prose_only")
        assert report["population"]["documents_primary_basis"] == 1
        assert report["population"]["documents_other_basis_excluded"] == {"prose_and_tables": 1}
        # the 0.9 value from the other-basis document must not leak into the
        # primary-basis native distribution
        assert report["distribution"]["native"]["max"] == 0.05
        assert report["distribution"]["native"]["max"] != 0.9


# -------------------------------------------------------------------- Test 9

class TestNoProductionMutation:
    def test_load_corpus_does_not_modify_files(self, tmp_path, monkeypatch):
        root = tmp_path / "corpus"
        _write_doc(root, "COMP_A", 2022, span={"start_page": 0, "end_page": 1}, osf=0.05)
        monkeypatch.setattr(pm2.triage, "profile_document",
                            lambda path: _profile({0: PageKind.DIGITAL, 1: PageKind.SCANNED}))

        mda_path = root / "companies" / "COMP_A" / "2022" / "mda.json"
        before = mda_path.read_bytes()
        before_mtime = os.path.getmtime(mda_path)

        pm2.load_corpus(str(root))

        assert mda_path.read_bytes() == before
        assert os.path.getmtime(mda_path) == before_mtime

    def test_does_not_touch_verify_module_state(self, tmp_path, monkeypatch):
        root = tmp_path / "corpus"
        _write_doc(root, "COMP_A", 2022, span={"start_page": 0, "end_page": 0}, osf=0.01)
        monkeypatch.setattr(pm2.triage, "profile_document",
                            lambda path: _profile({0: PageKind.DIGITAL}))
        before = verify.ORPHAN_START_FRAC_MAX
        records = pm2.load_corpus(str(root))
        pm2.build_report(records, gate=verify.ORPHAN_START_FRAC_MAX, orphan_basis="prose_only")
        assert verify.ORPHAN_START_FRAC_MAX == before == 0.03


# ------------------------------------------------------------------- helpers

def _write_doc(root, company_id: str, fy_end: int, *, span: dict, osf: float,
               basis: str = "prose_only", qc_extra: dict | None = None) -> None:
    doc_dir = root / "companies" / company_id / str(fy_end)
    doc_dir.mkdir(parents=True, exist_ok=True)
    (doc_dir / "annual_report.pdf").write_bytes(b"%PDF-1.4 fake")
    qc = {
        "orphan_start_frac": osf,
        "orphan_basis": basis,
        "orphan_gate_version": "p17.1",
        "orphan_gate_max": 0.03,
        "n_paragraphs": 40,
        "ocr_stats": [],
        "pdf_producer": None,
    }
    if qc_extra:
        qc.update(qc_extra)
    mda = {
        "company_id": company_id, "fy_end": fy_end, "sha256": "fake",
        "confidence": "medium", "span": span, "qc": qc,
        "reasons": [], "total_pages": (span["end_page"] + 1) if span else 0,
        "mda_page_count": (span["end_page"] - span["start_page"] + 1) if span else 0,
    }
    (doc_dir / "mda.json").write_text(json.dumps(mda), encoding="utf-8")
