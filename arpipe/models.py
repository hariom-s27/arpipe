"""Typed records that move between pipeline stages.

Every stage reads/writes these as JSON so any stage can be re-run
independently and the pipeline is resumable at document granularity.
"""
from __future__ import annotations

import dataclasses as dc
import datetime as dt
import enum
import json
from typing import Any


class PageKind(str, enum.Enum):
    """How a single page must be turned into text."""
    DIGITAL = "digital"          # good embedded text layer -> use it
    SCANNED = "scanned"          # no/near-zero text, page is an image -> OCR
    HYBRID = "hybrid"            # text layer + large image regions -> OCR the images
    BROKEN_TEXT = "broken_text"  # text layer decodes to mojibake -> OCR, ignore layer
    VECTOR_TEXT = "vector_text"  # glyphs drawn as vector paths -> OCR
    BLANK = "blank"              # nothing on the page


class Script(str, enum.Enum):
    LATIN = "latin"
    DEVANAGARI = "devanagari"
    OTHER_INDIC = "other_indic"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class Confidence(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    FAILED = "failed"


@dc.dataclass(slots=True)
class Company:
    """Identity resolved once, reused for every year."""
    company_id: str                  # our stable key; we use the ISIN when known
    canonical_name: str
    isin: str | None = None
    cin: str | None = None
    nse_symbol: str | None = None
    bse_scrip: str | None = None
    aliases: list[str] = dc.field(default_factory=list)   # former names/symbols
    sector: str | None = None
    cap_band: str | None = None      # large / mid / small / micro (AMFI classification)
    status: str = "active"
    alternate_isins: list[str] = dc.field(default_factory=list)  # P4: other ISINs collapsed into this row
    series_type: str = "ordinary"                                # P4: ordinary | dvr | partly_paid | other
    exchange: str = "both"                                       # P10: "nse" | "bse" | "both"
    cap_band_current: str | None = None                          # P30: current AMFI market-cap band


@dc.dataclass(slots=True)
class ReportRef:
    """A candidate annual-report document discovered from some source."""
    company_id: str
    fy_end: int                      # 2015 means FY2014-15 (year ended 31-Mar-2015)
    source: str                      # nse | bse | screener | ir_site | manual
    url: str
    discovered_at: str = dc.field(default_factory=lambda: dt.datetime.now(dt.timezone.utc).isoformat())
    declared_name: str | None = None
    declared_fy: str | None = None   # "2014-2015" as the source stated it
    content_type: str | None = None
    bytes_expected: int | None = None
    priority: int = 100              # lower wins when several sources have the year
    filename_symbol: str | None = None  # parsed from URL, e.g. "KRBL"
    filename_years: str | None = None   # parsed from URL, e.g. "2024_2025"


@dc.dataclass(slots=True)
class StoredDoc:
    """A fetched, de-duplicated PDF on disk."""
    company_id: str
    fy_end: int
    sha256: str
    path: str                        # blob path RELATIVE to the store root,
                                     # forward slashes; resolve with store.blob_abspath
    n_bytes: int
    n_pages: int
    source: str
    url: str
    pdf_producer: str | None = None
    is_encrypted: bool = False
    fetched_at: str = dc.field(default_factory=lambda: dt.datetime.now(dt.timezone.utc).isoformat())
    # How the human-facing tree got its copy of the blob, filled by store.write_year.
    # "hardlink" (free) | "symlink" (needs privilege on Windows) | "copy" (costs disk).
    link_mode: str | None = None


@dc.dataclass(slots=True)
class PageProfile:
    page_no: int                     # 0-based
    kind: PageKind
    n_chars: int
    n_words: int
    text_area_frac: float            # fraction of page covered by text boxes
    image_area_frac: float           # fraction covered by raster images
    n_images: int
    n_columns: int                   # 1, 2, or 3 (estimated)
    script: Script
    mojibake_ratio: float
    dpi_estimate: int | None = None
    rotation: int = 0


@dc.dataclass(slots=True)
class DocProfile:
    sha256: str
    n_pages: int
    pages: list[PageProfile]
    doc_kind: str                    # digital | scanned | mixed
    frac_needing_ocr: float
    has_outline: bool
    outline_titles: list[tuple[int, str, int]] = dc.field(default_factory=list)  # (level,title,page)
    bilingual: bool = False
    dominant_script: Script = Script.LATIN


@dc.dataclass(slots=True)
class MDASpan:
    """The located MD&A section."""
    start_page: int                  # 0-based, inclusive
    end_page: int                    # 0-based, inclusive
    start_char: int | None = None    # offset inside start_page text
    end_char: int | None = None
    method: str = ""                 # outline | toc | heading | body_score | llm
    heading_text: str | None = None
    terminator_text: str | None = None
    score: float = 0.0
    # How many *other* location methods (of S1–S5) landed on the same span.
    # Set by segment.locate(). Method agreement is the confidence measure
    # (CLAUDE.md rule 4), so verify.grade() gates on this.
    supporters: int = 0
    terminator_match: dict[str, Any] | None = None  # P5: diagnostic info on terminator match
    toc_offset: dict[str, Any] | None = None        # P6: folio-to-physical offset diagnostics


@dc.dataclass(slots=True)
class VerificationReport:
    company_ok: bool
    year_ok: bool
    company_evidence: list[str] = dc.field(default_factory=list)
    year_evidence: list[str] = dc.field(default_factory=list)
    name_similarity: float = 0.0
    cin_found: str | None = None
    isin_found: str | None = None
    isin_found_on_page: int | None = None
    isins_seen: list[str] = dc.field(default_factory=list)
    fy_found: int | None = None
    notes: list[str] = dc.field(default_factory=list)
    era_signals_in_document: dict[str, bool] = dc.field(default_factory=dict)


@dc.dataclass(slots=True)
class ExtractionResult:
    company_id: str
    fy_end: int
    sha256: str
    ok: bool
    confidence: Confidence
    span: MDASpan | None = None
    verification: VerificationReport | None = None
    path: str | None = None          # mda.txt RELATIVE to the dataset root,
                                     # forward slashes; set by store.write_year
    n_words: int = 0
    ocr_pages: int = 0
    ocr_engine: str | None = None
    supporters: int = 0          # top-level mirror of span.supporters
    method_candidates: list[Any] = dc.field(default_factory=list)  # P7: full list with scores
    total_pages: int = 0         # P7: total document page count
    mda_page_count: int = 0      # P7: page count in MD&A span
    words_per_page: float = 0.0  # P7: n_words / mda_page_count
    terminator_match: dict[str, Any] | None = None  # P5: top-level mirror of span.terminator_match
    toc_offset: dict[str, Any] | None = dc.field(default_factory=lambda: {"solved": None, "confidence": 0.0, "samples_used": 0, "modal_agreement": 0.0, "method": "not_run"})  # P6: folio offset diagnostics
    qc: dict[str, Any] = dc.field(default_factory=dict)
    # Why this row is not `high`. Machine-readable codes (see verify.build_reasons):
    # source_shredded, order_scrambled, span_truncated, identity_unproven,
    # year_unproven, section_leak, too_short, too_long, ocr_budget_exhausted,
    # mda_not_located. A `low`/`medium` row with an empty `reasons` is a half-row.
    reasons: list[str] = dc.field(default_factory=list)
    errors: list[str] = dc.field(default_factory=list)
    pipeline_version: str = "0.1.0"


def _enc(o: Any) -> Any:
    if dc.is_dataclass(o) and not isinstance(o, type):
        return {f.name: _enc(getattr(o, f.name)) for f in dc.fields(o)}
    if isinstance(o, enum.Enum):
        return o.value
    if isinstance(o, (list, tuple)):
        return [_enc(x) for x in o]
    if isinstance(o, dict):
        return {k: _enc(v) for k, v in o.items()}
    return o


def to_json(obj: Any, **kw: Any) -> str:
    return json.dumps(_enc(obj), ensure_ascii=False, **kw)
