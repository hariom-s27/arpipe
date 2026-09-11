"""OCR backends, behind one interface, arranged as an escalation ladder.

Rung 1  tesseract (local, CPU, ~0.3-1.5 s/page)   - default for clean 300 dpi
        English scans. Free. Weak on tables and on Devanagari.
Rung 2  a self-hosted document VLM (PaddleOCR-VL 0.9B / MinerU2.5 1.2B /
        olmOCR-2 7B) served by vLLM or SGLang - used when rung 1's quality
        gate fails, when the page is multi-column, or when it holds a table
        we need structured. ~$200 / million pages of GPU time.
Rung 3  a managed API (AWS Textract, Google Document AI, Gemini/Claude vision)
        - used only for the residue: torn scans, rotated/skewed pages, faint
        1990s-era photocopies. 10-100x rung 2's unit cost, so it must stay a
        residue, never a default.

Note on AWS: Textract's printed-text and table models cover English, German,
French, Spanish, Italian and Portuguese only - no Devanagari or other Indic
script. It is a fine rung-3 choice for the English pages of an Indian annual
report and the wrong tool for the Hindi half of a bilingual PSU report.
"""
from __future__ import annotations

import abc
import io
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field

import pymupdf

# --- tunable thresholds ---------------------------------------------------
# All thresholds provisional until re-fit against the labelled 300.
# provisional until re-fit against the labelled 300
DEFAULT_DPI = 300
# provisional until re-fit against the labelled 300
MAX_DPI = 400
# provisional until re-fit against the labelled 300
MIN_DPI = 200
# provisional until re-fit against the labelled 300
QUALITY_GATE_MIN_WORDS = 40
# provisional until re-fit against the labelled 300
QUALITY_GATE_MIN_CONF = 0.72
# provisional until re-fit against the labelled 300
QUALITY_GATE_MAX_NONWORD_FRAC = 0.35
# provisional until re-fit against the labelled 300
INDEX_STRIDE = 6
# provisional until re-fit against the labelled 300
FRONT_PAGES = 14
# provisional until re-fit against the labelled 300
VLM_MAX_TOKENS = 8192
# provisional until re-fit against the labelled 300
VLM_TIMEOUT = 180
# provisional until re-fit against the labelled 300
VLM_REPETITION_RATIO = 6.0


def configure(cfg: dict | None = None) -> None:
    """Update thresholds from resolved configuration."""
    global DEFAULT_DPI, MIN_DPI, MAX_DPI
    global QUALITY_GATE_MIN_WORDS, QUALITY_GATE_MIN_CONF, QUALITY_GATE_MAX_NONWORD_FRAC
    global INDEX_STRIDE, FRONT_PAGES, VLM_MAX_TOKENS, VLM_TIMEOUT, VLM_REPETITION_RATIO
    if not cfg:
        return
    DEFAULT_DPI = cfg.get("default_dpi", DEFAULT_DPI)
    MIN_DPI = cfg.get("min_dpi", MIN_DPI)
    MAX_DPI = cfg.get("max_dpi", MAX_DPI)
    qg = cfg.get("quality_gate", {})
    if isinstance(qg, dict):
        QUALITY_GATE_MIN_WORDS = qg.get("min_words", QUALITY_GATE_MIN_WORDS)
        QUALITY_GATE_MIN_CONF = qg.get("min_conf", QUALITY_GATE_MIN_CONF)
        QUALITY_GATE_MAX_NONWORD_FRAC = qg.get("max_nonword_frac", QUALITY_GATE_MAX_NONWORD_FRAC)
    INDEX_STRIDE = cfg.get("index_stride", INDEX_STRIDE)
    FRONT_PAGES = cfg.get("front_pages", FRONT_PAGES)
    VLM_MAX_TOKENS = cfg.get("vlm_max_tokens", VLM_MAX_TOKENS)
    VLM_TIMEOUT = cfg.get("vlm_timeout", VLM_TIMEOUT)
    VLM_REPETITION_RATIO = cfg.get("vlm_repetition_ratio", VLM_REPETITION_RATIO)


@dataclass(slots=True)
class OcrPage:
    page_no: int
    text: str
    engine: str
    mean_conf: float | None = None
    words: int = 0
    meta: dict = field(default_factory=dict)


class OcrBackend(abc.ABC):
    name = "base"

    @abc.abstractmethod
    def run(self, pdf_path: str, page_nos: list[int], lang: str = "eng",
            dpi: int = DEFAULT_DPI) -> list[OcrPage]: ...

    @staticmethod
    def render(pdf_path: str, page_no: int, dpi: int) -> bytes:
        doc = pymupdf.open(pdf_path)
        try:
            page = doc.load_page(page_no)
            pix = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
            return pix.tobytes("png")
        finally:
            doc.close()


def choose_dpi(image_dpi: int | None) -> int:
    """Render at the source resolution, clamped. Upsampling a 150 dpi fax to
    600 dpi buys nothing and costs 16x the pixels."""
    if not image_dpi:
        return DEFAULT_DPI
    return max(MIN_DPI, min(MAX_DPI, image_dpi))


# --------------------------------------------------------------------- rung 1
class TesseractBackend(OcrBackend):
    """Local Tesseract via pytesseract, with per-word confidence.

    lang: 'eng' for English pages, 'hin' for Devanagari, 'eng+hin' for
    genuinely mixed pages (slower, and worse on both than either alone,
    so prefer per-page language routing over mixed models).
    """
    name = "tesseract"

    def __init__(self, psm: int = 3, oem: int = 1):
        self.psm, self.oem = psm, oem
        if not shutil.which("tesseract"):
            win_tess = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            if os.path.exists(win_tess):
                try:
                    import pytesseract
                    pytesseract.pytesseract.tesseract_cmd = win_tess
                except ImportError:
                    pass

    def run(self, pdf_path: str, page_nos: list[int], lang: str = "eng",
            dpi: int = DEFAULT_DPI) -> list[OcrPage]:
        import pytesseract
        from PIL import Image

        if not shutil.which("tesseract"):
            win_tess = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            if os.path.exists(win_tess):
                pytesseract.pytesseract.tesseract_cmd = win_tess

        out: list[OcrPage] = []
        cfg = f"--oem {self.oem} --psm {self.psm}"
        for n in page_nos:
            png = self.render(pdf_path, n, dpi)
            img = Image.open(io.BytesIO(png))
            data = pytesseract.image_to_data(
                img, lang=lang, config=cfg,
                output_type=pytesseract.Output.DICT)
            words, confs = [], []
            for txt, c in zip(data["text"], data["conf"]):
                if txt and txt.strip():
                    words.append(txt)
                    try:
                        cv = float(c)
                        if cv >= 0:
                            confs.append(cv)
                    except (TypeError, ValueError):
                        pass
            text = pytesseract.image_to_string(img, lang=lang, config=cfg)
            out.append(OcrPage(
                page_no=n, text=text, engine=f"{self.name}:{lang}",
                mean_conf=(sum(confs) / len(confs) / 100.0) if confs else None,
                words=len(words)))
        return out


class OcrMyPdfBackend(OcrBackend):
    """OCRmyPDF wrapper: rasterises, OCRs, and writes a *searchable PDF* back.

    Worth a separate rung because it (a) preserves the original page images
    for later audit, (b) handles deskew/rotation/clean-up, and (c) leaves a
    permanent text layer so re-processing a document is free next time.
    Use --redo-ocr for BROKEN_TEXT pages and --skip-text for HYBRID pages.
    """
    name = "ocrmypdf"

    def __init__(self, jobs: int = 2, mode: str = "skip-text",
                 extra: tuple[str, ...] = ()):
        self.jobs, self.mode, self.extra = jobs, mode, extra

    def available(self) -> bool:
        return shutil.which("ocrmypdf") is not None

    def run(self, pdf_path: str, page_nos: list[int], lang: str = "eng",
            dpi: int = DEFAULT_DPI) -> list[OcrPage]:
        if not self.available():
            raise RuntimeError("ocrmypdf not installed")
        with tempfile.TemporaryDirectory() as td:
            sub = os.path.join(td, "sub.pdf")
            _subset(pdf_path, page_nos, sub)
            out_pdf = os.path.join(td, "ocr.pdf")
            side = os.path.join(td, "side.txt")
            cmd = ["ocrmypdf", "-l", lang, f"--{self.mode}",
                   "--rotate-pages", "--deskew", "--clean-final",
                   "--sidecar", side, "--jobs", str(self.jobs),
                   "--output-type", "pdf", *self.extra, sub, out_pdf]
            subprocess.run(cmd, check=True, capture_output=True)
            doc = pymupdf.open(out_pdf)
            try:
                return [OcrPage(page_no=orig, text=doc.load_page(i).get_text("text"),
                                engine=f"{self.name}:{lang}")
                        for i, orig in enumerate(page_nos)]
            finally:
                doc.close()


# --------------------------------------------------------------------- rung 2
class VlmServerBackend(OcrBackend):
    """OpenAI-compatible /v1/chat/completions endpoint serving a document VLM.

    Works unchanged against vLLM or SGLang hosting PaddleOCR-VL-0.9B,
    MinerU2.5-1.2B, olmOCR-2-7B, dots.ocr or Nanonets-OCR. The prompt asks
    for Markdown + HTML tables, which is the output contract all of those
    models were trained on.

    Two hard-won details are implemented here:
      * `anchor_text` - olmOCR's "document anchoring": the PDF's own (possibly
        partial) text layer is pasted into the prompt as a hint. It cuts
        hallucinated numbers sharply on hybrid pages.
      * repetition guard - VLM OCR degenerates into row loops on dense tables.
        We detect output far longer than the anchor and mark the page failed
        so it escalates instead of silently poisoning the corpus.
    """
    name = "vlm"

    PROMPT = (
        "Transcribe this document page exactly. Preserve reading order. "
        "Use Markdown for headings and paragraphs and HTML <table> for tables. "
        "Do not summarise, translate, correct or invent anything. "
        "Reproduce every numeric value and unit exactly as printed. "
        "If a region is illegible output [illegible]."
    )

    def __init__(self, base_url: str, model: str, api_key: str = "EMPTY",
                 max_tokens: int = 8192, timeout: int = 180,
                 anchor: bool = True):
        self.base_url = base_url.rstrip("/")
        self.model, self.api_key = model, api_key
        self.max_tokens, self.timeout, self.anchor = max_tokens, timeout, anchor

    def _anchor_text(self, pdf_path: str, page_no: int, limit: int = 3000) -> str:
        try:
            doc = pymupdf.open(pdf_path)
            t = doc.load_page(page_no).get_text("text")
            doc.close()
            return t[:limit]
        except Exception:
            return ""

    def run(self, pdf_path: str, page_nos: list[int], lang: str = "eng",
            dpi: int = DEFAULT_DPI) -> list[OcrPage]:
        import base64
        import httpx

        out: list[OcrPage] = []
        with httpx.Client(timeout=self.timeout) as cl:
            for n in page_nos:
                png = self.render(pdf_path, n, dpi)
                b64 = base64.b64encode(png).decode()
                prompt = self.PROMPT
                anchor = self._anchor_text(pdf_path, n) if self.anchor else ""
                if anchor.strip():
                    prompt += ("\n\nPartial text extracted from the PDF layer "
                               "(may be incomplete or out of order; use only as "
                               f"a hint):\n<<<\n{anchor}\n>>>")
                body = {
                    "model": self.model, "max_tokens": self.max_tokens,
                    "temperature": 0.0,
                    "messages": [{"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url",
                         "image_url": {"url": f"data:image/png;base64,{b64}"}},
                    ]}],
                }
                r = cl.post(f"{self.base_url}/v1/chat/completions",
                            json=body,
                            headers={"Authorization": f"Bearer {self.api_key}"})
                r.raise_for_status()
                txt = r.json()["choices"][0]["message"]["content"]
                bad = _looks_degenerate(txt, anchor)
                out.append(OcrPage(page_no=n, text="" if bad else txt,
                                   engine=f"{self.name}:{self.model}",
                                   words=len(txt.split()),
                                   meta={"degenerate": bad}))
        return out


def _looks_degenerate(text: str, anchor: str, ratio: float = 6.0,
                      rep_run: int = 8) -> bool:
    """Catch the two classic VLM-OCR failure modes."""
    if not text.strip():
        return True
    if anchor and len(text) > ratio * max(200, len(anchor)):
        return True
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    run = best = 1
    for a, b in zip(lines, lines[1:]):
        run = run + 1 if a == b else 1
        best = max(best, run)
    return best >= rep_run


# --------------------------------------------------------------------- rung 3
class TextractBackend(OcrBackend):
    """AWS Textract. English/Latin scripts only - do not route Hindi here.

    Uses the async StartDocumentTextDetection path so multi-page PDFs go in
    one call; for a handful of pages the sync DetectDocumentText on rendered
    PNGs is cheaper to operate. Set analyze=True to get TABLES + FORMS
    (about 10x the price of plain text detection).
    """
    name = "textract"

    def __init__(self, region: str = "ap-south-1", analyze: bool = False):
        self.region, self.analyze = region, analyze

    def run(self, pdf_path: str, page_nos: list[int], lang: str = "eng",
            dpi: int = DEFAULT_DPI) -> list[OcrPage]:
        import boto3
        cl = boto3.client("textract", region_name=self.region)
        out: list[OcrPage] = []
        for n in page_nos:
            png = self.render(pdf_path, n, dpi)
            if self.analyze:
                resp = cl.analyze_document(Document={"Bytes": png},
                                           FeatureTypes=["TABLES"])
            else:
                resp = cl.detect_document_text(Document={"Bytes": png})
            lines, confs = [], []
            for b in resp.get("Blocks", []):
                if b["BlockType"] == "LINE":
                    lines.append(b.get("Text", ""))
                    confs.append(b.get("Confidence", 0.0))
            out.append(OcrPage(page_no=n, text="\n".join(lines),
                               engine=f"{self.name}",
                               mean_conf=(sum(confs) / len(confs) / 100.0) if confs else None,
                               words=sum(len(l.split()) for l in lines)))
        return out


# --------------------------------------------------------------------- helpers
def _subset(src: str, page_nos: list[int], dst: str) -> None:
    doc = pymupdf.open(src)
    new = pymupdf.open()
    try:
        for n in page_nos:
            new.insert_pdf(doc, from_page=n, to_page=n)
        new.save(dst)
    finally:
        new.close()
        doc.close()


def quality_gate(p: OcrPage, min_words: int | None = None, min_conf: float | None = None,
                 max_nonword_frac: float | None = None) -> tuple[bool, str]:
    """Decide whether an OCR result is good enough to accept.

    Cheap, engine-agnostic signals. The point is not to grade the OCR but to
    decide whether to spend the next rung's money on this page.
    """
    mw = min_words if min_words is not None else QUALITY_GATE_MIN_WORDS
    mc = min_conf if min_conf is not None else QUALITY_GATE_MIN_CONF
    mnf = max_nonword_frac if max_nonword_frac is not None else QUALITY_GATE_MAX_NONWORD_FRAC
    txt = p.text or ""
    words = txt.split()
    if len(words) < mw:
        return False, "too_few_words"
    if p.mean_conf is not None and p.mean_conf < mc:
        return False, f"low_conf:{p.mean_conf:.2f}"
    alnum = sum(1 for c in txt if c.isalnum() or c.isspace())
    if alnum / max(1, len(txt)) < (1 - mnf):
        return False, "high_symbol_noise"
    long_tokens = sum(1 for w in words if len(w) > 30)
    if long_tokens > max(3, 0.02 * len(words)):
        return False, "run_on_tokens"
    if p.meta.get("degenerate"):
        return False, "degenerate_output"
    return True, "ok"


class Escalator:
    """Run the ladder until a rung passes the quality gate."""

    def __init__(self, rungs: list[OcrBackend]):
        self.rungs = rungs

    def run_page(self, pdf_path: str, page_no: int, lang: str = "eng",
                 dpi: int = DEFAULT_DPI) -> tuple[OcrPage, list[str]]:
        trail: list[str] = []
        last: OcrPage | None = None
        for be in self.rungs:
            try:
                res = be.run(pdf_path, [page_no], lang=lang, dpi=dpi)[0]
            except Exception as exc:                     # noqa: BLE001
                trail.append(f"{be.name}:error:{type(exc).__name__}")
                continue
            ok, why = quality_gate(res)
            trail.append(f"{be.name}:{why}")
            last = res
            if ok:
                return res, trail
        return (last or OcrPage(page_no, "", "none")), trail
