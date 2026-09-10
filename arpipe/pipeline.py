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
INDEX_STRIDE = 6
OCR_WORKERS = int(os.environ.get("ARPIPE_OCR_WORKERS", "4"))
FRONT_PAGES = 14


def _lang_for(profile: DocProfile, page_no: int) -> str:
    from .models import Script
    p = profile.pages[page_no] if page_no < len(profile.pages) else None
    if p and p.script in (Script.DEVANAGARI, Script.MIXED):
        return "eng+hin"
    return "eng"


def _ocr_pages(pdf: str, profile: DocProfile, pages: list[int],
               escalator: ocr_mod.Escalator,
               workers: int = OCR_WORKERS) -> tuple[dict[int, str], int, str]:
    """OCR a page list. Page-level parallelism, because OCR is the only
    stage where wall-clock actually hurts: everything else is milliseconds."""
    if not pages:
        return {}, 0, ""

    def one(n: int):
        pp = profile.pages[n] if n < len(profile.pages) else None
        dpi = ocr_mod.choose_dpi(pp.dpi_estimate if pp else None)
        res, _trail = escalator.run_page(pdf, n, lang=_lang_for(profile, n), dpi=dpi)
        return n, res

    got: dict[int, str] = {}
    engines: set[str] = set()
    if workers <= 1 or len(pages) == 1:
        results = [one(n) for n in pages]
    else:
        with ThreadPoolExecutor(max_workers=min(workers, len(pages))) as ex:
            results = list(ex.map(one, pages))
    for n, res in results:
        if res.text.strip():
            got[n] = textlayer.normalise(res.text)
            engines.add(res.engine)
    return got, len(got), ",".join(sorted(engines))


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

    pdf = pymupdf.open(blob)
    try:
        digital = [p.page_no for p in profile.pages if p.kind is PageKind.DIGITAL]
        page_texts = textlayer.extract_pages(blob, digital)

        # ---- pass 1: locate on what we can read for free -----------------
        span, diag = segment.locate(pdf, profile, page_texts, call_llm=None)

        # ---- pass 2: if that failed, OCR a cheap index sample ------------
        ocr_used = 0
        engine = None
        if (span is None or span.score < 0.55) and profile.frac_needing_ocr > 0.05:
            need = triage.ocr_page_numbers(profile)
            index = sorted({n for n in need
                            if n < FRONT_PAGES or n % INDEX_STRIDE == 0})[:60]
            if index:
                got, k, engine = _ocr_pages(blob, profile, index, escalator)
                page_texts.update(got)
                ocr_used += k
                span, diag = segment.locate(pdf, profile, page_texts, call_llm=None)

        # ---- pass 3: LLM adjudication for the residue --------------------
        if call_llm and (span is None or span.score < 0.7):
            span2, diag2 = segment.locate(pdf, profile, page_texts, call_llm=call_llm)
            if span2 and (span is None or span2.score > span.score):
                span, diag = span2, diag2

        if span is None:
            res.errors.append("mda_not_located")
            res.reasons = ["mda_not_located"]
            res.qc = {"diag": diag, "doc_kind": profile.doc_kind,
                      "frac_needing_ocr": profile.frac_needing_ocr,
                      "pdf_producer": doc.pdf_producer}
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
            got, k, _ = _ocr_pages(blob, profile, [n], escalator)
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
            got, k, eng = _ocr_pages(blob, profile, missing, escalator)
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
        # P21: fraction of digital span pages on which the P16B column splitter
        # fired. Near 1 => ordering is as good as we can make it (a residual
        # orphan_start_frac is source_shredded, not order_scrambled).
        _dig = order_diag["digital_pages"]
        column_cut_fire_frac = (order_diag["column_cut_pages"] / _dig
                                if _dig else None)
        ordered = textlayer.strip_running_furniture(ordered) if len(ordered) >= 4 else ordered
        mda_text = "\n\n".join(t for t in ordered if t.strip()).strip()

        # ---- verification -------------------------------------------------
        front_nos = [n for n in sorted(page_texts) if n < FRONT_PAGES]
        front = "\n".join(page_texts[n] for n in front_nos)
        if len(front.split()) < 80:
            got, k, _ = _ocr_pages(blob, profile,
                                   [n for n in range(min(6, profile.n_pages))
                                    if n not in page_texts], escalator)
            page_texts.update(got)
            ocr_used += k
            front = "\n".join(page_texts.get(n, "") for n in range(FRONT_PAGES))

        vrep = verify.verify(front, mda_text, company, doc.fy_end)
        qc = verify.section_qc(mda_text)
        grade = verify.grade(vrep, qc, span.score)
        reasons = verify.build_reasons(
            vrep, qc, column_cut_fire_frac=column_cut_fire_frac,
            mda_text=mda_text)

        res.span = span
        res.verification = vrep
        res.reasons = reasons
        res.n_words = qc["n_words"]
        res.ocr_pages = ocr_used
        res.ocr_engine = engine
        res.qc = {**qc, "diag": diag, "doc_kind": profile.doc_kind,
                  "frac_needing_ocr": profile.frac_needing_ocr,
                  "bilingual": profile.bilingual,
                  "n_pages": profile.n_pages,
                  # P21: pdf_producer sits next to a source_shredded reason -
                  # the free web compressors (iLovePDF, Smallpdf, ...) shred the
                  # text layer to near-per-line and that is the whole residual.
                  "pdf_producer": doc.pdf_producer,
                  "column_cut_fire_frac": (round(column_cut_fire_frac, 3)
                                           if column_cut_fire_frac is not None
                                           else None),
                  # P18: n_words / n_chars / digit_ratio above are prose only
                  "n_words_note": "prose only; tables/charts in mda_blocks.json",
                  "blocks_quarantined": len(mda_blocks),
                  "words_quarantined": sum(len(b["text"].split())
                                           for b in mda_blocks)}
        res.confidence = {"high": Confidence.HIGH, "medium": Confidence.MEDIUM,
                          "low": Confidence.LOW}[grade]
        res.ok = grade in ("high", "medium")

        store.write_year(out_root, company.canonical_name, doc, mda_text, res,
                         page_texts if keep_pages else None,
                         mda_blocks=mda_blocks, blob_path=blob,
                         store_root=store_root)
        # store.write_year sets res.path (mda.txt relative to the dataset root).
        assert not res.ok or res.path, "ok extraction wrote no mda.txt path"
        return res
    finally:
        pdf.close()
