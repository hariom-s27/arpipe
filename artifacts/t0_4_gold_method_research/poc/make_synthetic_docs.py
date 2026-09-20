"""TOOLING_POC_ONLY. RESEARCH_ONLY. NOT GOLD.

Builds fully synthetic PDFs for the T0.4-GOLD-METHOD-RESEARCH annotation-tool
feasibility POC. No corpus PDF is opened. The text is invented boilerplate; the
"MD&A" structure is a constructed stress case, not a copy of any real report.

Outputs (under --out):
  synth_2p.pdf      2 pages
  synth_20p.pdf     20 pages: two-column page, table page, MD&A boundary cases
  synth_600p.pdf    600 pages: long-document navigation/scale case
  synth_manifest.json   SHA-256 + structural facts (the "expected structure" is
                        a construction fact of the synthetic file, NOT a label)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os

import pymupdf

PAGE = pymupdf.paper_rect("a4")
LOREM = (
    "The company continued to operate across its reporting segments during the "
    "year. Management monitors demand conditions, input costs and regulatory "
    "developments and reviews internal controls with the audit committee. "
    "This sentence is synthetic filler used only to give the page realistic text density. "
)


def _meta(doc: pymupdf.Document, title: str) -> None:
    doc.set_metadata({"title": title, "author": "SYNTHETIC-POC", "producer": "make_synthetic_docs.py",
                      "creator": "make_synthetic_docs.py", "creationDate": "", "modDate": "",
                      "subject": "TOOLING_POC_ONLY", "keywords": ""})


def _header(page: pymupdf.Page, label: str, folio: int | None) -> None:
    page.insert_text((50, 30), label, fontsize=8)
    if folio is not None:
        page.insert_text((290, 820), str(folio), fontsize=9)


def _para(page, y0, text=LOREM * 3, x0=50, x1=545, h=140, size=10):
    page.insert_textbox(pymupdf.Rect(x0, y0, x1, y0 + h), text, fontsize=size, fontname="helv")


def _heading(page, y, text, size=16):
    page.insert_text((50, y), text, fontsize=size, fontname="hebo")


def _filler_page(doc, label, folio):
    p = doc.new_page(width=PAGE.width, height=PAGE.height)
    _header(p, label, folio)
    _para(p, 60, LOREM * 6, h=700)
    return p


def build_2p(path):
    doc = pymupdf.open()
    p = doc.new_page(width=PAGE.width, height=PAGE.height)
    _header(p, "Synthetic Co. Ltd. - 2-page POC", 1)
    _heading(p, 90, "Management Discussion and Analysis")
    _para(p, 110)
    p = doc.new_page(width=PAGE.width, height=PAGE.height)
    _header(p, "Synthetic Co. Ltd. - 2-page POC", 2)
    _para(p, 60)
    _meta(doc, "synth_2p")
    doc.save(path, garbage=4, deflate=True)
    return {"pages": 2}


def build_20p(path, devanagari=True):
    """20 pages. Physical index is 0-based; printed folio = physical index - 1 for
    pages >= 2 (cover and contents unnumbered) so folio/physical mismatch is testable."""
    doc = pymupdf.open()
    plan = {}
    # p0 cover, p1 contents (TOC that *mentions* MD&A with a folio that is deliberately wrong)
    p = doc.new_page(width=PAGE.width, height=PAGE.height)
    _header(p, "Synthetic Co. Ltd. Annual Report", None)
    _heading(p, 300, "ANNUAL REPORT 2099-00", 24)
    p = doc.new_page(width=PAGE.width, height=PAGE.height)
    _header(p, "Contents", None)
    _heading(p, 90, "Contents")
    rows = [("Directors' Report", 2), ("Management Discussion and Analysis", 5),
            ("Report on Corporate Governance", 9), ("Financial Statements", 12)]
    for i, (t, f) in enumerate(rows):
        p.insert_text((60, 130 + 22 * i), f"{t} ..... {f}", fontsize=11)
    plan["toc_declared_mda_folio"] = 5
    # p2-p3 Directors' Report; p3 carries an MD&A *pointer* sentence (keyword occurrence, not a section)
    p = doc.new_page(width=PAGE.width, height=PAGE.height)
    _header(p, "Directors' Report", 1)
    _heading(p, 90, "DIRECTORS' REPORT")
    _para(p, 110, LOREM * 4, h=300)
    p = doc.new_page(width=PAGE.width, height=PAGE.height)
    _header(p, "Directors' Report", 2)
    _para(p, 60, "Management Discussion and Analysis forms part of this report and is given as Annexure V. " + LOREM * 3, h=200)
    plan["pointer_only_page"] = 3
    # p4: filler; p5: MD&A heading MID-PAGE after other section text (start_page = 5)
    _filler_page(doc, "Annexure IV", 3)
    p = doc.new_page(width=PAGE.width, height=PAGE.height)
    _header(p, "Annexure V", 4)
    _para(p, 60, "Tail of the preceding annexure. " + LOREM * 2, h=250)
    _heading(p, 400, "ANNEXURE V - MANAGEMENT DISCUSSION AND ANALYSIS")
    _para(p, 420, "Industry structure and developments. " + LOREM * 3, h=300)
    plan["mda_heading_page"] = 5
    # p6: MD&A continues (prose)
    p = doc.new_page(width=PAGE.width, height=PAGE.height)
    _header(p, "Management Discussion and Analysis", 5)
    _para(p, 60, "Opportunities and Threats. " + LOREM * 6, h=700)
    # p7: TWO-COLUMN page inside MD&A
    p = doc.new_page(width=PAGE.width, height=PAGE.height)
    _header(p, "Management Discussion and Analysis", 6)
    _heading(p, 80, "Segment-wise performance", 13)
    _para(p, 95, "LEFT COLUMN first. " + LOREM * 5, x0=50, x1=290, h=650)
    _para(p, 95, "RIGHT COLUMN second. " + LOREM * 5, x0=305, x1=545, h=650)
    plan["two_column_page"] = 7
    # p8: TABLE page (regions/boxes) with unit note
    p = doc.new_page(width=PAGE.width, height=PAGE.height)
    _header(p, "Management Discussion and Analysis", 7)
    _heading(p, 80, "Key financial ratios", 13)
    p.insert_text((50, 100), "(Rs. in crore, unless stated otherwise)", fontsize=8)
    x = [50, 260, 340, 420, 500]
    for r in range(6):
        y = 115 + 22 * r
        p.draw_line((50, y), (545, y))
        vals = ["Particulars", "FY 2099-00", "FY 2098-99", "Change %"] if r == 0 else [f"Ratio {r}", f"{1200 + r * 37}.5", f"{1100 + r * 29}.0", f"{5 + r}.2%"]
        for c, v in enumerate(vals):
            p.insert_text((x[c] + 3, y + 15), v, fontsize=9)
    p.draw_line((50, 115 + 22 * 6), (545, 115 + 22 * 6))
    for xi in x + [545]:
        p.draw_line((xi, 115), (xi, 115 + 22 * 6))
    plan["table_page"] = 8
    # p9: MD&A ENDS MID-PAGE: next top-level section heading half-way down (end_page = 9)
    p = doc.new_page(width=PAGE.width, height=PAGE.height)
    _header(p, "Management Discussion and Analysis", 8)
    _para(p, 60, "Outlook. Risks and concerns. Internal control systems and their adequacy. " + LOREM * 2, h=300)
    p.insert_text((50, 420), "Cautionary Statement", fontsize=11, fontname="hebo")
    _heading(p, 500, "REPORT ON CORPORATE GOVERNANCE")
    _para(p, 520, "Company's philosophy on corporate governance. " + LOREM * 2, h=250)
    plan["mda_end_page_mid_page_transition"] = 9
    for k in range(10, 14):
        _filler_page(doc, "Corporate Governance", k - 1)
    # p14: SECOND MD&A-LIKE heading (subsidiary) -> multiple-candidate case
    p = doc.new_page(width=PAGE.width, height=PAGE.height)
    _header(p, "Subsidiary", 13)
    _heading(p, 90, "Management Discussion and Analysis - Subsidiary XYZ Ltd.")
    _para(p, 110, LOREM * 4, h=300)
    plan["second_mda_like_heading_page"] = 14
    # p15: bilingual heading page (needs a Devanagari-capable font)
    p = doc.new_page(width=PAGE.width, height=PAGE.height)
    _header(p, "Bilingual", 14)
    used = False
    if devanagari and os.path.exists(r"C:\Windows\Fonts\Nirmala.ttc"):
        try:
            p.insert_font(fontname="nirmala", fontfile=r"C:\Windows\Fonts\Nirmala.ttc")
            p.insert_text((50, 100), "\u092a\u094d\u0930\u092c\u0902\u0927\u0928 \u091a\u0930\u094d\u091a\u093e \u0914\u0930 \u0935\u093f\u0936\u094d\u0932\u0947\u0937\u0923", fontsize=16, fontname="nirmala")
            used = True
        except Exception:
            used = False
    p.insert_text((50, 130), "Management Discussion and Analysis (bilingual heading)", fontsize=14, fontname="hebo")
    plan["bilingual_page"] = 15
    plan["devanagari_glyphs_rendered"] = used
    for k in range(16, 20):
        _filler_page(doc, "Financial Statements", k - 1)
    doc.set_toc([[1, "Directors' Report", 3], [1, "Annexure V - Management Discussion and Analysis", 6],
                 [1, "Report on Corporate Governance", 10]])  # 1-based page numbers
    _meta(doc, "synth_20p")
    doc.save(path, garbage=4, deflate=True)
    plan["pages"] = doc.page_count
    plan["note"] = ("expected_structure keys are CONSTRUCTION FACTS of this synthetic file (0-based physical "
                    "page indices), used only to check tool page/coordinate fidelity. They are not labels.")
    return plan


def build_600p(path):
    doc = pymupdf.open()
    for i in range(600):
        p = doc.new_page(width=PAGE.width, height=PAGE.height)
        _header(p, "Synthetic long report", i)
        if i in (0, 300, 599):
            _heading(p, 90, f"MARKER PAGE {i}")
        _para(p, 110 if i in (0, 300, 599) else 60, LOREM * 6, h=650)
    doc.set_toc([[1, "Start", 1], [1, "Middle", 301], [1, "End", 600]])
    _meta(doc, "synth_600p")
    doc.save(path, garbage=4, deflate=True)
    return {"pages": 600, "marker_pages_0based": [0, 300, 599]}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    m = {"label": "TOOLING_POC_ONLY", "gold": False, "pymupdf_version": pymupdf.__version__, "files": {}}
    for name, fn in (("synth_2p.pdf", build_2p), ("synth_20p.pdf", build_20p), ("synth_600p.pdf", build_600p)):
        path = os.path.join(a.out, name)
        facts = fn(path)
        m["files"][name] = {"sha256": sha256(path), "bytes": os.path.getsize(path), "construction_facts": facts}
    with open(os.path.join(a.out, "synth_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2, sort_keys=True)
    print(json.dumps({k: (v["sha256"][:16], v["bytes"]) for k, v in m["files"].items()}))


if __name__ == "__main__":
    main()
