"""Synthetic annual reports that reproduce the real failure modes.

Not a substitute for a labelled sample of real filings, but enough to keep
the routing/segmentation logic honest in CI without shipping copyrighted
PDFs in the repo.
"""
from __future__ import annotations

import io
import os
import random
import sys

import pymupdf

random.seed(7)

LOREM = (
    "The Company continued to focus on operational efficiency and prudent "
    "capital allocation during the year under review. Volumes grew across "
    "the domestic and export segments, supported by stable input costs and "
    "improved capacity utilisation at the Company's manufacturing facilities. "
    "Working capital discipline was maintained and the Company reduced its "
    "net debt position. "
)

SECTIONS = [
    ("Corporate Information", 1),
    ("Notice of the Annual General Meeting", 3),
    ("Board's Report", 4),
    ("Management Discussion and Analysis", 6),
    ("Report on Corporate Governance", 4),
    ("Business Responsibility Report", 2),
    ("Independent Auditor's Report", 3),
    ("Standalone Financial Statements", 4),
]

MDA_BODY = [
    "Industry Structure and Developments",
    "Opportunities and Threats",
    "Segment-wise or Product-wise Performance",
    "Outlook",
    "Risks and Concerns",
    "Internal Control Systems and their Adequacy",
    "Discussion on Financial Performance with respect to Operational Performance",
    "Material Developments in Human Resources / Industrial Relations Front",
    "Details of Significant Changes in Key Financial Ratios",
    "Cautionary Statement",
]

RATIO_TABLE = (
    "Debtors Turnover 5.4 4.9\nInventory Turnover 6.1 5.8\n"
    "Interest Coverage Ratio 8.2 6.7\nCurrent Ratio 1.6 1.4\n"
    "Debt Equity Ratio 0.31 0.44\nOperating Profit Margin 14.2% 12.8%\n"
    "Net Profit Margin 9.1% 7.9%\nReturn on Net Worth 16.3% 14.1%\n"
)


def _para(n: int = 3) -> str:
    return " ".join(LOREM for _ in range(n))


def build(path: str, *, company="ACME INDUSTRIES LIMITED",
          cin="L27100MH1994PLC078367", isin="INE123A01012",
          fy_from=2014, fy_to=2015, columns=1, outline=True,
          toc=True, ratios=True, hindi=False, mda_title=None) -> str:
    mda_title = mda_title or "Management Discussion and Analysis"
    doc = pymupdf.open()
    W, H = 595, 842
    toc_entries: list[tuple[str, int]] = []
    bookmarks: list[list] = []
    page_no = 0

    def new_page():
        nonlocal page_no
        p = doc.new_page(width=W, height=H)
        page_no += 1
        return p

    def header(p, txt):
        p.insert_textbox(pymupdf.Rect(40, 20, W - 40, 40), txt,
                         fontsize=7, fontname="helv", color=(.4, .4, .4))
        p.insert_textbox(pymupdf.Rect(40, H - 40, W - 40, H - 22),
                         str(doc.page_count), fontsize=8, fontname="helv",
                         align=pymupdf.TEXT_ALIGN_CENTER)

    def body(p, text, top=110):
        if columns == 2:
            gut = 26
            cw = (W - 80 - gut) / 2
            p.insert_textbox(pymupdf.Rect(40, top, 40 + cw, H - 60), text,
                             fontsize=9, fontname="helv", align=3)
            p.insert_textbox(pymupdf.Rect(40 + cw + gut, top, W - 40, H - 60),
                             text, fontsize=9, fontname="helv", align=3)
        else:
            p.insert_textbox(pymupdf.Rect(50, top, W - 50, H - 60), text,
                             fontsize=10, fontname="helv", align=3)

    # ---- cover
    p = new_page()
    p.insert_textbox(pymupdf.Rect(60, 240, W - 60, 340),
                     f"{company}\n\nAnnual Report {fy_from}-{str(fy_to)[2:]}",
                     fontsize=24, fontname="hebo",
                     align=pymupdf.TEXT_ALIGN_CENTER)
    p.insert_textbox(pymupdf.Rect(60, 640, W - 60, 760),
                     f"CIN: {cin}\n"
                     f"for the financial year ended 31st March, {fy_to}",
                     fontsize=10, fontname="helv",
                     align=pymupdf.TEXT_ALIGN_CENTER)
    if hindi:
        p.insert_textbox(pymupdf.Rect(60, 380, W - 60, 430),
                         "वार्षिक रिपोर्ट", fontsize=18,
                         fontname="china-s", align=pymupdf.TEXT_ALIGN_CENTER)

    toc_page_idx = None
    if toc:
        toc_page_idx = doc.page_count
        new_page()                                   # placeholder, filled later

    # ---- sections
    for title, npages in SECTIONS:
        start = doc.page_count
        for i in range(npages):
            p = new_page()
            header(p, f"{company}  |  Annual Report {fy_from}-{str(fy_to)[2:]}")
            if i == 0:
                p.insert_textbox(pymupdf.Rect(45, 55, W - 45, 100),
                                 title if title != "Management Discussion and Analysis"
                                 else mda_title,
                                 fontsize=17, fontname="hebo")
                txt = _para(2)
                if title.startswith("Management"):
                    txt = MDA_BODY[0] + "\n\n" + _para(2)
                elif title.startswith("Report on Corporate Governance"):
                    txt = f"General Shareholder Information\nISIN: {isin}\n\n" + _para(2)
                body(p, txt)
            elif title.startswith("Management"):
                k = min(len(MDA_BODY) - 1, i)
                chunk = MDA_BODY[k] + "\n\n" + _para(2)
                if ratios and MDA_BODY[k].startswith("Details of Significant"):
                    chunk += "\n\n" + RATIO_TABLE
                body(p, chunk, top=70)
            elif title.startswith("Independent"):
                body(p, "We have audited the accompanying standalone financial "
                        "statements of the Company. Basis for Opinion. " + _para(1),
                     top=70)
            elif title.startswith("Standalone"):
                body(p, "Balance Sheet as at 31st March, %d\n" % fy_to
                        + "\n".join(f"Note {j} 1,2{j}4.5 9{j}8.2" for j in range(1, 25)),
                     top=70)
            else:
                body(p, _para(2), top=70)
        toc_entries.append((mda_title if title.startswith("Management") else title,
                            start + 1))
        bookmarks.append([1, mda_title if title.startswith("Management") else title,
                          start + 1])

    # ---- fill the contents page now that folios are known
    if toc_page_idx is not None:
        p = doc.load_page(toc_page_idx)
        lines = ["Contents", ""]
        for t, folio in toc_entries:
            dots = "." * max(3, 62 - len(t) - len(str(folio)))
            lines.append(f"{t} {dots} {folio}")
        p.insert_textbox(pymupdf.Rect(50, 70, W - 50, H - 60), "\n".join(lines),
                         fontsize=11, fontname="helv")

    if outline:
        doc.set_toc(bookmarks)
    doc.save(path, garbage=3, deflate=True)
    doc.close()
    return path


def to_scanned(src: str, dst: str, dpi: int = 200, noise: bool = True,
               pages: list[int] | None = None) -> str:
    """Re-render pages as images so the text layer disappears."""
    import numpy as np
    from PIL import Image

    s = pymupdf.open(src)
    d = pymupdf.open()
    for i in range(s.page_count):
        if pages is not None and i not in pages:
            d.insert_pdf(s, from_page=i, to_page=i)
            continue
        pix = s.load_page(i).get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
        img = Image.frombytes("L", (pix.width, pix.height), pix.samples)
        if noise:
            a = np.asarray(img).astype(np.int16)
            a = a + np.random.normal(0, 6, a.shape)
            img = Image.fromarray(np.clip(a, 0, 255).astype("uint8"))
            img = img.rotate(random.uniform(-0.35, 0.35), fillcolor=255,
                             resample=Image.BILINEAR)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        pg = d.new_page(width=s.load_page(i).rect.width,
                        height=s.load_page(i).rect.height)
        pg.insert_image(pg.rect, stream=buf.getvalue())
    d.save(dst, deflate=True)
    d.close(); s.close()
    return dst


def main(outdir: str) -> None:
    os.makedirs(outdir, exist_ok=True)
    a = build(os.path.join(outdir, "A_digital_outline.pdf"))
    b = build(os.path.join(outdir, "B_twocol_toc.pdf"), columns=2, outline=False,
              fy_from=2019, fy_to=2020,
              mda_title="MANAGEMENT DISCUSSION & ANALYSIS REPORT")
    c = build(os.path.join(outdir, "C_src.pdf"), outline=False, toc=True,
              fy_from=2011, fy_to=2012, ratios=False,
              mda_title="Management's Discussion and Analysis")
    to_scanned(c, os.path.join(outdir, "C_scanned.pdf"))
    d = build(os.path.join(outdir, "D_src.pdf"), outline=False,
              fy_from=2016, fy_to=2017, columns=2)
    to_scanned(d, os.path.join(outdir, "D_hybrid.pdf"),
               pages=list(range(8, 20)))
    build(os.path.join(outdir, "E_bilingual.pdf"), hindi=True, outline=False,
          fy_from=2022, fy_to=2023)
    print("fixtures written to", outdir)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "fixtures")
