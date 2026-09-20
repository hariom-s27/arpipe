"""P-X1-derived fixed renderer for future Track-A execution.

The renderer may read one PDF page during a future execution, but engines only
receive the resulting immutable image and its SHA-256. T0.4 does not call it.
"""
from __future__ import annotations

import dataclasses as dc
import hashlib
from pathlib import Path

DEFAULT_DPI = 300
PREPROCESSING_VERSION = "t0.4-render-v1"


@dc.dataclass(frozen=True, slots=True)
class RenderRecord:
    source_pdf_sha256: str
    page_number: int
    render_dpi: int
    image_format: str
    image_sha256: str
    image_key: str
    preprocessing_version: str
    width: int
    height: int


def render_page(
    pdf_path: Path,
    source_pdf_sha256: str,
    page_number: int,
    output_dir: Path,
    dpi: int = DEFAULT_DPI,
) -> RenderRecord:
    """Render one page as RGB PNG and store it under its content hash."""
    import pymupdf  # Deferred: setup/audit never opens a PDF or imports the renderer dependency.

    if dpi != DEFAULT_DPI:
        raise ValueError(f"T0.4 primary Track-A rendering is frozen at {DEFAULT_DPI} DPI")
    output_dir.mkdir(parents=True, exist_ok=True)
    document = pymupdf.open(str(pdf_path))
    try:
        if page_number < 0 or page_number >= len(document):
            raise IndexError(f"page {page_number} out of bounds (pages={len(document)})")
        pixmap = document[page_number].get_pixmap(dpi=dpi, colorspace=pymupdf.csRGB, alpha=False)
        png_bytes = pixmap.tobytes("png")
        width, height = pixmap.width, pixmap.height
    finally:
        document.close()
    image_hash = hashlib.sha256(png_bytes).hexdigest()
    image_key = f"rendered_pages/{image_hash}.png"
    destination = output_dir / f"{image_hash}.png"
    if destination.exists() and destination.read_bytes() != png_bytes:
        raise RuntimeError("content-addressed render collision")
    if not destination.exists():
        destination.write_bytes(png_bytes)
    return RenderRecord(
        source_pdf_sha256=source_pdf_sha256,
        page_number=page_number,
        render_dpi=dpi,
        image_format="PNG",
        image_sha256=image_hash,
        image_key=image_key,
        preprocessing_version=PREPROCESSING_VERSION,
        width=width,
        height=height,
    )
