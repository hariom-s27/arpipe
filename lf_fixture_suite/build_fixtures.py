"""LF forensic fixture suite (synthetic, no ARPipe corpus data).

Builds small PDFs that isolate one text-layer mechanism each, so ARPipe's
frozen page detector (arpipe/triage.py, broken_text = U+FFFD/C0-control ratio
> 2% on pages with >=120 chars) can be tested against known ground truth.
"""
import io, json, re, sys
import pymupdf
from fontTools.ttLib import TTFont

DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FREESERIF = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"
OUT = "fixtures"

BODY = (
    "Management Discussion and Analysis. The Company operates in a highly "
    "competitive industry and its performance depends on monsoon patterns, "
    "input costs and regulatory changes. Revenue from operations increased "
    "by 12.4 percent during the year, while finance costs declined because "
    "of lower average borrowings. The Board continues to review risks "
    "including climate related physical risks to manufacturing facilities, "
    "transition risks from carbon pricing, and credit risk on receivables. "
    "Internal control systems are adequate and commensurate with the size "
    "of operations. Human resources remain a key driver of growth and the "
    "Company employed 4,210 permanent staff at the end of the year. "
    "Cautionary statement: statements in this report describing objectives "
    "and expectations may be forward looking within applicable laws."
)
HEADING = "MANAGEMENT DISCUSSION AND ANALYSIS REPORT"

# ---- an ASCII-slot "legacy" Devanagari font (Kruti-Dev-style mechanism) ----
# Latin code points carry Devanagari glyphs. Invented table, NOT a real font's.
SLOT = {"k": "kadeva", "e": "madeva", "j": "radeva", "u": "nadeva",
        "l": "sadeva", "d": "dadeva", "x": "gadeva", "g": "hadeva",
        "i": "padeva", "c": "badeva", "t": "tadeva", "o": "vadeva",
        "y": "yadeva", "b": "ladeva", "a": "aasigndeva"}
DEVA = {"kadeva": "क", "madeva": "म", "radeva": "र",
        "nadeva": "न", "sadeva": "स", "dadeva": "द",
        "gadeva": "ग", "hadeva": "ह", "padeva": "प",
        "badeva": "ब", "tadeva": "त", "vadeva": "व",
        "yadeva": "य", "ladeva": "ल", "aasigndeva": "ा"}
LEGACY_WORDS = ("ljkaj uek dmu kbe ita exj lmu uxj goa jat " * 9).strip()
# the same words written in Unicode (ground truth of what a reader sees)
def slot_to_unicode(s):
    return "".join(DEVA[SLOT[c]] if c in SLOT else c for c in s)
LEGACY_TRUTH = slot_to_unicode(LEGACY_WORDS)


def make_slot_font(path):
    f = TTFont(FREESERIF)
    for t in f["cmap"].tables:
        if t.isUnicode():
            # a real ASCII-slot font has NO Unicode Devanagari entries
            for cp in [c for c in t.cmap if 0x0900 <= c <= 0x097F]:
                del t.cmap[cp]
            for ch, g in SLOT.items():
                t.cmap[ord(ch)] = g
    f["name"].setName("SlotDevaDemo", 1, 3, 1, 0x409)
    f["name"].setName("SlotDevaDemo", 4, 3, 1, 0x409)
    f["name"].setName("SlotDevaDemo", 6, 3, 1, 0x409)
    f.save(path)


def wrap(page, text, font, y0=110, size=10.5, x0=60, width=470, render_mode=0):
    """Simple greedy line wrapping (no shaping)."""
    fo = pymupdf.Font(fontfile=font[1])
    words, line, y = text.split(" "), "", y0
    for w in words:
        cand = (line + " " + w).strip()
        if fo.text_length(cand, fontsize=size) > width:
            page.insert_text((x0, y), line, fontname=font[0], fontsize=size,
                             render_mode=render_mode)
            y += size * 1.45
            line = w
        else:
            line = cand
    if line:
        page.insert_text((x0, y), line, fontname=font[0], fontsize=size,
                         render_mode=render_mode)
        y += size * 1.45
    return y


def type0_fonts(doc):
    out = {}
    for x in range(1, doc.xref_length()):
        if doc.xref_get_key(x, "Subtype")[1] == "/Type0":
            out[doc.xref_get_key(x, "BaseFont")[1]] = x
    return out


def parse_tounicode(doc, fx):
    k = doc.xref_get_key(fx, "ToUnicode")
    if k[0] != "xref":
        return None, None
    tx = int(k[1].split()[0])
    s = doc.xref_stream(tx).decode("latin-1")
    m = {}
    for blk in re.findall(r"beginbfchar(.*?)endbfchar", s, re.S):
        for a, b in re.findall(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", blk):
            if len(b) % 4 == 0:
                m[int(a, 16)] = bytes.fromhex(b).decode("utf-16-be", "replace")
    for blk in re.findall(r"beginbfrange(.*?)endbfrange", s, re.S):
        for a, b, c in re.findall(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", blk):
            lo, hi = int(a, 16), int(b, 16)
            if len(c) % 4:
                continue
            base = bytes.fromhex(c).decode("utf-16-be", "replace")
            for i in range(hi - lo + 1):
                m[lo + i] = base[:-1] + chr(ord(base[-1]) + i)
    return tx, m


def write_tounicode(doc, tx, mapping):
    lines = ["/CIDInit /ProcSet findresource begin", "12 dict begin", "begincmap",
             "/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def",
             "/CMapName /Adobe-Identity-UCS def", "/CMapType 2 def",
             "1 begincodespacerange", "<0000> <FFFF>", "endcodespacerange"]
    items = sorted(mapping.items())
    for i in range(0, len(items), 100):
        chunk = items[i:i + 100]
        lines.append(f"{len(chunk)} beginbfchar")
        for c, u in chunk:
            lines.append(f"<{c:04X}> <{u.encode('utf-16-be').hex().upper()}>")
        lines.append("endbfchar")
    lines += ["endcmap", "CMapName currentdict /CMap defineresource pop", "end", "end"]
    doc.update_stream(tx, "\n".join(lines).encode("latin-1"))


def shift(u):
    if "a" <= u <= "z":
        return chr((ord(u) - 97 + 3) % 26 + 97)
    if "A" <= u <= "Z":
        return chr((ord(u) - 65 + 3) % 26 + 65)
    return u


def corrupt(doc, fx, how):
    tx, m = parse_tounicode(doc, fx)
    if how == "missing":
        doc.xref_set_key(fx, "ToUnicode", "null")
    elif how == "wrong_shift":
        write_tounicode(doc, tx, {c: shift(u) for c, u in m.items()})
    elif how == "pua":
        write_tounicode(doc, tx, {c: chr(0xE000 + c) for c in m})


def build(name, body_font, body_text, heading_font=None, heading_text=None,
          corrupt_font=None, how=None, subset=True):
    doc = pymupdf.open()
    p = doc.new_page(width=595, height=842)
    fonts = {"B": body_font}
    p.insert_font(fontname="Fb", fontfile=body_font)
    y = 80
    if heading_font:
        p.insert_font(fontname="Fh", fontfile=heading_font)
        p.insert_text((60, y), heading_text, fontname="Fh", fontsize=13)
        y += 30
    wrap(p, body_text, ("Fb", body_font), y0=y)
    if subset:
        doc.subset_fonts()
    doc = pymupdf.open("pdf", doc.tobytes())
    if corrupt_font and how:
        want = "DejaVu" if corrupt_font == "body" else "FreeSerif"
        target = [x for n, x in type0_fonts(doc).items() if want in n][0]
        corrupt(doc, target, how)
    doc.save(f"{OUT}/{name}.pdf", garbage=3)


def build_invisible_layer(name):
    """Visible content is an image of clean text; the text layer is invisible
    (render mode 3) and wrong - the 'bad prior OCR layer' mechanism."""
    src = pymupdf.open(f"{OUT}/F00_clean.pdf")
    pix = src[0].get_pixmap(dpi=200)
    doc = pymupdf.open()
    p = doc.new_page(width=595, height=842)
    p.insert_image(p.rect, pixmap=pix)
    p.insert_font(fontname="Fb", fontfile=DEJAVU)
    garbage = "".join(shift(c) for c in BODY)          # plausible-looking junk
    wrap(p, garbage, ("Fb", DEJAVU), y0=110, render_mode=3)
    doc.subset_fonts()
    doc.save(f"{OUT}/{name}.pdf", garbage=3)


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    make_slot_font("SlotDevaDemo.ttf")
    SLOTF = "SlotDevaDemo.ttf"
    truth = {}
    build("F00_clean", DEJAVU, BODY); truth["F00_clean"] = BODY
    build("F00b_clean_fullfont", DEJAVU, BODY, subset=False); truth["F00b_clean_fullfont"] = BODY
    build("F01_missing_tounicode_subset", DEJAVU, BODY, corrupt_font="body", how="missing")
    truth["F01_missing_tounicode_subset"] = BODY
    build("F02_missing_tounicode_fullfont", DEJAVU, BODY, corrupt_font="body", how="missing", subset=False)
    truth["F02_missing_tounicode_fullfont"] = BODY
    build("F03_wrong_tounicode_shift", DEJAVU, BODY, corrupt_font="body", how="wrong_shift")
    truth["F03_wrong_tounicode_shift"] = BODY
    build("F03b_wrong_tounicode_fullfont", DEJAVU, BODY, corrupt_font="body", how="wrong_shift", subset=False)
    truth["F03b_wrong_tounicode_fullfont"] = BODY
    build("F04_pua_tounicode", DEJAVU, BODY, corrupt_font="body", how="pua")
    truth["F04_pua_tounicode"] = BODY
    build("F05_ascii_slot_legacy_deva", SLOTF, LEGACY_WORDS); truth["F05_ascii_slot_legacy_deva"] = LEGACY_TRUTH
    # mixed pages: clean body, corrupted heading font only
    build("F06_mixed_heading_missing_tu", DEJAVU, BODY, heading_font=FREESERIF,
          heading_text=HEADING, corrupt_font="heading", how="missing")
    truth["F06_mixed_heading_missing_tu"] = HEADING + " " + BODY
    build("F07_mixed_heading_wrong_tu", DEJAVU, BODY, heading_font=FREESERIF,
          heading_text=HEADING, corrupt_font="heading", how="wrong_shift")
    truth["F07_mixed_heading_wrong_tu"] = HEADING + " " + BODY
    build("F08_mixed_heading_legacy_slot", DEJAVU, BODY, heading_font=SLOTF,
          heading_text="ljkaj dmu kbe ita", corrupt_font=None)
    truth["F08_mixed_heading_legacy_slot"] = slot_to_unicode("ljkaj dmu kbe ita") + " " + BODY
    # bilingual page: half English, half ASCII-slot Hindi
    doc = pymupdf.open(); p = doc.new_page(width=595, height=842)
    p.insert_font(fontname="Fb", fontfile=DEJAVU); p.insert_font(fontname="Fl", fontfile=SLOTF)
    y = wrap(p, BODY[:620], ("Fb", DEJAVU), y0=90)
    wrap(p, LEGACY_WORDS, ("Fl", SLOTF), y0=y + 20)
    doc.subset_fonts(); doc.save(f"{OUT}/F09_bilingual_half_legacy.pdf", garbage=3)
    truth["F09_bilingual_half_legacy"] = BODY[:620] + " " + LEGACY_TRUTH
    build_invisible_layer("F10_image_plus_wrong_invisible_layer")
    truth["F10_image_plus_wrong_invisible_layer"] = BODY
    json.dump(truth, open(f"{OUT}/truth.json", "w"), ensure_ascii=False, indent=1)
    print("built", len(truth))
