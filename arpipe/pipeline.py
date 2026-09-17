"""End-to-end processing of one (company, FY, PDF).

The order matters and is the whole cost argument:

  1. profile the document from the PDF object model    (~50 ms, no rendering)
  2. read the text layer of the *digital* pages only   (~1 s / 300 pages)
  3. locate MD&A using those pages plus the outline/TOC
  4. OCR only the pages inside the located span that need it
  5. if the span could not be located because the pages we needed were
     scanned, OCR a cheap "index" subset (TOC pages + every Nth page) and
     locate again
  6. verify identity and year, score quality, write output

Step 5 is what keeps a fully-scanned 300-page report from costing 300 OCR
pages: a 1-in-6 sample plus the front matter is enough to find the section,
after which only the ~15 real MD&A pages get full-quality OCR.
"""
from __future__ import annotations

import os
from dataclasses import replace

import pymupdf
from concurrent.futures import ThreadPoolExecutor

from . import ocr as ocr_mod
from . import segment, store, textlayer, triage, verify
from .models import (Company, Confidence, DocProfile, ExtractionResult, MDASpan,
                     PageKind, StoredDoc)

PIPELINE_VERSION = "0.1.0"
# --- tunable thresholds ---------------------------------------------------
# All thresholds provisional until re-fit against the labelled 300.
# provisional until re-fit against the labelled 300
INDEX_STRIDE = 6
# provisional until re-fit against the labelled 300
OCR_WORKERS = int(os.environ.get("ARPIPE_OCR_WORKERS", "4"))
# provisional until re-fit against the labelled 300
FRONT_PAGES = 14


def configure(cfg: dict | None = None) -> None:
    """Update pipeline thresholds from resolved configuration."""
    global INDEX_STRIDE, OCR_WORKERS, FRONT_PAGES
    if not cfg:
        return
    ocr_cfg = cfg.get("ocr", {})
    if isinstance(ocr_cfg, dict):
        INDEX_STRIDE = ocr_cfg.get("index_stride", INDEX_STRIDE)
        FRONT_PAGES = ocr_cfg.get("front_pages", FRONT_PAGES)
    disc_cfg = cfg.get("discover", {})
    if isinstance(disc_cfg, dict):
        OCR_WORKERS = disc_cfg.get("workers", OCR_WORKERS)


def _lang_for(profile: DocProfile, page_no: int) -> str:
    from .models import Script
    p = profile.pages[page_no] if page_no < len(profile.pages) else None
    if p and p.script in (Script.DEVANAGARI, Script.MIXED):
        return "eng+hin"
    return "eng"


def _ocr_pages(pdf: str, profile: DocProfile, pages: list[int],
               escalator: ocr_mod.Escalator,
               workers: int = OCR_WORKERS,
               stats: list[dict] | None = None) -> tuple[dict[int, str], int, str]:
    """OCR a page list. Page-level parallelism, because OCR is the only
    stage where wall-clock actually hurts: everything else is milliseconds."""
    import time
    if not pages:
        return {}, 0, ""

    def one(n: int):
        pp = profile.pages[n] if n < len(profile.pages) else None
        dpi = ocr_mod.choose_dpi(pp.dpi_estimate if pp else None)
        t0 = time.monotonic()
        res, trail = escalator.run_page(pdf, n, lang=_lang_for(profile, n), dpi=dpi)
        sec = round(time.monotonic() - t0, 3)
        return n, res, sec, trail

    got: dict[int, str] = {}
    engines: set[str] = set()
    if workers <= 1 or len(pages) == 1:
        results = [one(n) for n in pages]
    else:
        with ThreadPoolExecutor(max_workers=min(workers, len(pages))) as ex:
            results = list(ex.map(one, pages))
    for n, res, sec, trail in results:
        if stats is not None:
            stats.append({
                "page_no": n,
                "engine": res.engine,
                "seconds": sec,
                "words": res.words,
                "conf": res.mean_conf,
                "degenerate": bool(res.meta.get("degenerate")),
                "ocr_geometry": res.meta.get("ocr_geometry", "flat"),
                "column_cut": bool(res.meta.get("column_cut")),
                "trail": trail,
            })
        if res.text.strip():
            got[n] = textlayer.normalise(res.text)
            engines.add(res.engine)
    return got, len(got), ",".join(sorted(engines))


def sample_index_pages(
    profile: DocProfile, need: list[int] | None = None
) -> tuple[list[int], dict]:
    """Determine the pages to OCR in pass 2 for locating MD&A.

    For short, heavily-scanned documents (<= 60 pages and > 80% needing OCR),
    sample every page. The <= 60 pages bound is a BUDGET statement, not a
    tuned threshold: an extra ~130s of OCR wall-clock ensures the true section
    is visible in short historical filings without risking OOM or timeout.

    For longer documents, keep front matter and stride, but sweep the offset
    (page % stride in (0, stride // 2)) to halve the blind spot.
    """
    if need is None:
        need = triage.ocr_page_numbers(profile)

    if profile.n_pages <= 60 and profile.frac_needing_ocr > 0.80:
        index = sorted(need)
        sample_info = {
            "mode": "exhaustive",
            "pages_sampled": len(index),
            "pages_total": profile.n_pages,
            "stride": None,
            "cost_pages": len(index),
        }
    else:
        stride = INDEX_STRIDE
        half_stride = max(1, stride // 2)
        index = sorted({n for n in need if n < FRONT_PAGES or (n % stride in (0, half_stride))})[:60]
        sample_info = {
            "mode": "stride",
            "pages_sampled": len(index),
            "pages_total": profile.n_pages,
            "stride": stride,
            "cost_pages": len(index),
        }
    return index, sample_info


def process_document(doc: StoredDoc, company: Company, out_root: str,
                     escalator: ocr_mod.Escalator | None = None,
                     call_llm=None, keep_pages: bool = False,
                     store_root: str | None = None) -> ExtractionResult:
    res = ExtractionResult(company_id=doc.company_id, fy_end=doc.fy_end,
                           sha256=doc.sha256, ok=False,
                           confidence=Confidence.FAILED,
                           pipeline_version=PIPELINE_VERSION)
    escalator = escalator or ocr_mod.Escalator([ocr_mod.TesseractBackend()])

    # doc.path is stored relative to the store root; resolve it to an absolute
    # path here so every stage below works regardless of the current directory.
    blob = store.blob_abspath(store_root, doc.path) if store_root else doc.path

    try:
        profile = triage.profile_document(blob)
    except Exception as exc:                              # noqa: BLE001
        res.errors.append(f"profile_failed:{type(exc).__name__}:{exc}")
        return res

    doc.script_map = profile.script_map

    pdf = pymupdf.open(blob)
    try:
        digital = [p.page_no for p in profile.pages if p.kind is PageKind.DIGITAL]
        page_texts = textlayer.extract_pages(blob, digital)

        # ---- pass 1: locate on what we can read for free -----------------
        span, diag = segment.locate(pdf, profile, page_texts, call_llm=None)

        # ---- pass 2: if that failed, OCR a cheap index sample ------------
        ocr_used = 0
        engine = None
        ocr_stats: list[dict] = []
        index_sample_info: dict = {}
        if (span is None or span.score < 0.55) and profile.frac_needing_ocr > 0.05:
            need = triage.ocr_page_numbers(profile)
            index, index_sample_info = sample_index_pages(profile, need)
            if index:
                got, k, engine = _ocr_pages(blob, profile, index, escalator, stats=ocr_stats)
                page_texts.update(got)
                ocr_used += k
                span, diag = segment.locate(pdf, profile, page_texts, call_llm=None)
                diag["index_sample"] = index_sample_info

        # ---- pass 3: LLM adjudication for the residue --------------------
        if call_llm and (span is None or span.score < 0.7):
            span2, diag2 = segment.locate(pdf, profile, page_texts, call_llm=call_llm)
            if span2 and (span is None or span2.score > span.score):
                span, diag = span2, diag2
                diag["index_sample"] = index_sample_info

        if span is None:
            res.errors.append("mda_not_located")
            res.reasons = ["mda_not_located"]
            res.method_candidates = diag.get("candidates", [])
            res.total_pages = profile.n_pages
            res.mda_page_count = 0
            res.words_per_page = 0.0
            res.ocr_pages = ocr_used
            res.ocr_engine = engine
            res.toc_offset = diag.get("toc_offset") or {
                "solved": None,
                "confidence": 0.0,
                "samples_used": 0,
                "modal_agreement": 0.0,
                "method": "not_run",
            }
            res.qc = {"diag": diag, "doc_kind": profile.doc_kind,
                      "toc_offset": res.toc_offset,
                      "frac_needing_ocr": profile.frac_needing_ocr,
                      "pdf_producer": doc.pdf_producer,
                      "ocr_stats": ocr_stats,
                      "ocr_sec_total": round(sum(s["seconds"] for s in ocr_stats), 2) if ocr_stats else 0.0,
                      "ocr_sec_mean": round(sum(s["seconds"] for s in ocr_stats) / len(ocr_stats), 3) if ocr_stats else 0.0,
                      "index_sample": index_sample_info}
            return res

        # ---- refine the end boundary --------------------------------------
        # A span found on a 1-in-N page sample stops at the last sampled page,
        # not at the real section end. Walk forward, reading one page at a
        # time, until a terminator heading appears.
        def _fetch(n: int) -> str | None:
            if n >= profile.n_pages:
                return None
            if profile.pages[n].kind is PageKind.DIGITAL:
                return textlayer.extract_pages(blob, [n]).get(n, "")
            got, k, _ = _ocr_pages(blob, profile, [n], escalator, stats=ocr_stats)
            nonlocal ocr_used
            ocr_used += k
            return got.get(n, "")

        span = segment.refine_end(span, page_texts, _fetch)

        # ---- full-quality OCR of the located span ------------------------
        span_pages = list(range(span.start_page, span.end_page + 1))
        missing = [n for n in span_pages
                   if n not in page_texts or len(page_texts[n].split()) < 40]
        missing = [n for n in missing
                   if n < len(profile.pages)
                   and profile.pages[n].kind is not PageKind.BLANK]
        if missing:
            got, k, eng = _ocr_pages(blob, profile, missing, escalator, stats=ocr_stats)
            page_texts.update(got)
            ocr_used += k
            engine = eng or engine

        # ---- exact boundaries, now that the whole span is readable --------
        span = segment.trim_span(span, page_texts)
        span_pages = list(range(span.start_page, span.end_page + 1))

        # P18: pull chart axis dumps and table cells out of the prose into a
        # sidecar (mda_blocks.json). n_words / digit_ratio are then measured on
        # prose only, not on number-soup.
        digital_span = {n for n in span_pages
                        if n < len(profile.pages)
                        and profile.pages[n].kind is PageKind.DIGITAL}
        ordered, mda_blocks, order_diag = textlayer.extract_prose_and_tables(
            blob, span_pages, page_texts, digital_span)
        # P21: fraction of span pages on which the P16B column splitter
        # fired (across digital pages and OCR pages with block geometry).
        # Near 1 => ordering is as good as we can make it (a residual
        # orphan_start_frac is source_shredded, not order_scrambled).
        _dig = order_diag["digital_pages"]
        ocr_span_stats = [s for s in ocr_stats if s.get("page_no") in span_pages]
        _ocr_blocks = sum(1 for s in ocr_span_stats if s.get("ocr_geometry") == "blocks")
        _ocr_col = sum(1 for s in ocr_span_stats if s.get("column_cut"))
        total_geom = _dig + _ocr_blocks
        column_cut_fire_frac = ((order_diag["column_cut_pages"] + _ocr_col) / total_geom
                                if total_geom else None)
        # P23: running furniture is stripped inside extract_prose_and_tables now
        # (block geometry + repetition, before the reading-order sort), not here.
        mda_text = "\n\n".join(t for t in ordered if t.strip()).strip()

        # PM1: per-physical-page orphan_start_frac telemetry, diagnostic only
        # (arpipe orderqc). `ordered` is already one prose string per entry of
        # `span_pages`, in the same order used to build mda_text above, so
        # this reuses the exact same per-page prose order_quality() would see
        # - no new extraction, no re-deriving page membership from offsets.
        # 1-based physical PDF page numbers per PM1 (span.start_page is 0-based).
        page_qc = verify.order_quality_by_page(
            [(n + 1, t) for n, t in zip(span_pages, ordered)])
        orphan_start_frac_pages: list[float | None] = [None] * profile.n_pages
        for phys_page, frac in page_qc["pages"].items():
            if 1 <= phys_page <= profile.n_pages:
                orphan_start_frac_pages[phys_page - 1] = frac

        # ---- verification -------------------------------------------------
        front_nos = [n for n in sorted(page_texts) if n < FRONT_PAGES]
        front = "\n".join(page_texts[n] for n in front_nos)
        if len(front.split()) < 80:
            got, k, _ = _ocr_pages(blob, profile,
                                   [n for n in range(min(6, profile.n_pages))
                                    if n not in page_texts], escalator, stats=ocr_stats)
            page_texts.update(got)
            ocr_used += k
            front = "\n".join(page_texts.get(n, "") for n in range(FRONT_PAGES))

        vrep = verify.verify(front, mda_text, company, doc.fy_end,
                             page_texts=page_texts)
        qc = verify.section_qc(mda_text)
        grade = verify.grade(vrep, qc, span.score, supporters=span.supporters,
                             pdf_producer=doc.pdf_producer)
        reasons = verify.build_reasons(
            vrep, qc, column_cut_fire_frac=column_cut_fire_frac,
            pdf_producer=doc.pdf_producer, mda_text=mda_text)

        # P34: quarantine gate. A bilingual PSU report (Hindi copy printed
        # before the English one) can be located, verified and graded clean
        # while the extracted body is actually the Hindi section rendered as
        # Latin/Latin-1-extended noise by a legacy font, or English-OCR'd off
        # a Hindi scan - every check above measures prose shape, not
        # language, so none of them catch it. This overrides `grade`
        # regardless of what verify.grade() computed above.
        wrong_language = verify.looks_like_wrong_language(mda_text)
        bilingual_heading = verify.page_has_bilingual_heading(
            page_texts.get(span.start_page, ""))
        if wrong_language["wrong_language_risk"] or bilingual_heading["bilingual_heading_page"]:
            grade = "quarantine"
            reasons = [*reasons, "WRONG_LANGUAGE_RISK"]

        res.span = span
        res.supporters = span.supporters
        res.method_candidates = diag.get("candidates", [])
        res.total_pages = profile.n_pages
        res.mda_page_count = (span.end_page - span.start_page + 1) if span else 0
        res.words_per_page = round(qc["n_words"] / max(1, res.mda_page_count), 1) if span else 0.0
        res.terminator_match = span.terminator_match if span else None
        res.toc_offset = diag.get("toc_offset") or {
            "solved": None,
            "confidence": 0.0,
            "samples_used": 0,
            "modal_agreement": 0.0,
            "method": "not_run",
        }
        res.verification = vrep
        res.reasons = reasons
        res.n_words = qc["n_words"]
        res.ocr_pages = ocr_used
        res.ocr_engine = engine
        res.qc = {**qc, "diag": diag, "doc_kind": profile.doc_kind,
                  "terminator_match": span.terminator_match if span else None,
                  "toc_offset": res.toc_offset,
                  "frac_needing_ocr": profile.frac_needing_ocr,
                  "bilingual": profile.bilingual,
                  "n_pages": profile.n_pages,
                  "ocr_stats": ocr_stats,
                  "ocr_sec_total": round(sum(s["seconds"] for s in ocr_stats), 2) if ocr_stats else 0.0,
                  "ocr_sec_mean": round(sum(s["seconds"] for s in ocr_stats) / len(ocr_stats), 3) if ocr_stats else 0.0,
                  "index_sample": index_sample_info,
                  # P21: pdf_producer sits next to a source_shredded reason -
                  # the free web compressors (iLovePDF, Smallpdf, ...) shred the
                  # text layer to near-per-line and that is the whole residual.
                  "pdf_producer": doc.pdf_producer,
                  "column_cut_fire_frac": (round(column_cut_fire_frac, 3)
                                           if column_cut_fire_frac is not None
                                           else None),
                  # P23: running-furniture removal is geometry + repetition,
                  # done before xy_cut, so n_words no longer depends on the sort.
                  "furniture_blocks_removed": order_diag["furniture_blocks_removed"],
                  "furniture_strings": order_diag["furniture_strings"],
                  # PM1: diagnostic only (arpipe orderqc) - page-aligned array,
                  # length profile.n_pages, index i = 1-based physical page i+1.
                  # null = not measured (outside the span, or insufficient
                  # qualifying prose on that page); never fed into grade/reasons.
                  "orphan_start_frac_pages": orphan_start_frac_pages,
                  "orphan_start_frac_pages_min_paragraphs": page_qc["min_paragraphs"],
                  # P18: n_words / n_chars / digit_ratio above are prose only
                  "n_words_note": "prose only; tables/charts in mda_blocks.json",
                  "blocks_quarantined": len(mda_blocks),
                  "words_quarantined": sum(len(b["text"].split())
                                           for b in mda_blocks),
                  # P34: diagnosis kept even though the span itself is withheld
                  # from the research corpus below - never an absence (rule 3).
                  "wrong_language": wrong_language,
                  "bilingual_heading_page": bilingual_heading}
        res.confidence = {"high": Confidence.HIGH, "medium": Confidence.MEDIUM,
                          "low": Confidence.LOW,
                          "quarantine": Confidence.QUARANTINE}[grade]
        res.ok = grade in ("high", "medium")

        store.write_year(out_root, company.canonical_name, doc, mda_text, res,
                         page_texts if keep_pages else None,
                         mda_blocks=mda_blocks, blob_path=blob,
                         store_root=store_root,
                         write_span=(grade != "quarantine"))
        # store.write_year sets res.path (mda.txt relative to the dataset root).
        assert not res.ok or res.path, "ok extraction wrote no mda.txt path"
        return res
    except ocr_mod.OcrEngineUnavailable as exc:
        # P-B5: a page inside this document needed OCR and no configured
        # engine could even attempt it (missing binary / language pack /
        # unreachable endpoint). This must reach the manifest as its own
        # reason, never fall through to mda_not_located - an infrastructure
        # failure and "this document has no MD&A" must stay distinguishable.
        res.errors.append(f"ocr_engine_unavailable:page={exc.page_no}:{exc.detail}")
        res.reasons = ["ocr_engine_unavailable"]
        res.total_pages = profile.n_pages
        res.qc = {"stage": "ocr", "doc_kind": profile.doc_kind,
                  "frac_needing_ocr": profile.frac_needing_ocr,
                  "pdf_producer": doc.pdf_producer,
                  "ocr_failure_page": exc.page_no,
                  "ocr_failure_trail": exc.trail}
        return res
    finally:
        pdf.close()
