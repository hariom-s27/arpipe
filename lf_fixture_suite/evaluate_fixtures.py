"""Run ARPipe's frozen page detector + extractors + candidate signals + recovery
methods over the synthetic LF fixtures. Writes results.json / results.md."""
import io, json, re, sys, glob, subprocess, tempfile, os
import pymupdf
from fontTools.ttLib import TTFont
from rapidfuzz.distance import Levenshtein
from wordfreq import zipf_frequency

sys.path.insert(0, "/home/claude/arpipe")
from arpipe import triage  # frozen ARPipe detector (unmodified)

from build_fixtures import SLOT, DEVA, parse_tounicode

truth = json.load(open("fixtures/truth.json"))
INV_SLOT = {c: DEVA[g] for c, g in SLOT.items()}


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def cer(hyp, ref):
    hyp, ref = norm(hyp), norm(ref)
    return round(Levenshtein.distance(hyp, ref) / max(1, len(ref)), 3)


def dict_hit_rate(text):
    toks = re.findall(r"[A-Za-z]{3,}", text)
    if not toks:
        return None
    return round(sum(zipf_frequency(t.lower(), "en") >= 2.5 for t in toks) / len(toks), 3)


def extract_all(path):
    d = pymupdf.open(path)
    p = d[0]
    out = {}
    out["pymupdf_default"] = p.get_text()
    out["pymupdf_no_cid_flag"] = p.get_text(flags=pymupdf.TEXTFLAGS_TEXT & ~pymupdf.TEXT_USE_CID_FOR_UNKNOWN_UNICODE)
    try:
        from pdfminer.high_level import extract_text
        out["pdfminer"] = extract_text(path)
    except Exception as e:
        out["pdfminer"] = f"ERR {e}"
    try:
        import pypdf
        out["pypdf"] = pypdf.PdfReader(path).pages[0].extract_text()
    except Exception as e:
        out["pypdf"] = f"ERR {e}"
    return out


def ocr(path, lang):
    d = pymupdf.open(path)
    pix = d[0].get_pixmap(dpi=300)
    with tempfile.TemporaryDirectory() as td:
        img = os.path.join(td, "p.png"); pix.save(img)
        env = dict(os.environ, TESSDATA_PREFIX="/home/claude/lf/tessdata")
        r = subprocess.run(["tesseract", img, "-", "-l", lang, "--psm", "4"],
                           capture_output=True, text=True, env=env)
        return r.stdout


def font_signals(path):
    """Font-level forensic signals, one row per Type0 font on the page."""
    d = pymupdf.open(path)
    rows = []
    for x in range(1, d.xref_length()):
        if d.xref_get_key(x, "Subtype")[1] != "/Type0":
            continue
        name = d.xref_get_key(x, "BaseFont")[1]
        tx, tu = parse_tounicode(d, x)
        desc = int(d.xref_get_key(x, "DescendantFonts")[1].strip("[] ").split()[0])
        fd = int(d.xref_get_key(desc, "FontDescriptor")[1].split()[0])
        ff = int(d.xref_get_key(fd, "FontFile2")[1].split()[0])
        tt = TTFont(io.BytesIO(d.xref_stream(ff)))
        order = tt.getGlyphOrder()
        cm = (tt.getBestCmap() or {}) if "cmap" in tt else {}
        inv = {}
        for u, g in cm.items():
            inv.setdefault(tt.getGlyphID(g), chr(u))
        # CIDs actually used on the page: re-extract with ToUnicode removed
        d2 = pymupdf.open(path)
        for y in range(1, d2.xref_length()):
            if d2.xref_get_key(y, "Subtype")[1] == "/Type0":
                d2.xref_set_key(y, "ToUnicode", "null")
        used = set()
        for b in d2[0].get_text("rawdict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    if s["font"] and s["font"].split("+")[-1].replace(" ", "")[:8] in name.replace("#20", "").replace(" ", ""):
                        for c in s["chars"]:
                            used.add(ord(c["c"]))
        used.discard(0)
        agree = gn_agree = n_tu = 0
        for cid in used:
            if tu is None or cid not in tu:
                continue
            n_tu += 1
            if inv.get(cid) == tu[cid]:
                agree += 1
            gname = order[cid] if cid < len(order) else ""
            # AGL-style check: does the glyph name agree with the ToUnicode value?
            u = tu[cid]
            if (gname == u) or (gname == f"uni{ord(u):04X}") or (len(u) == 1 and u == " " and gname == "space") \
               or (len(gname) > 1 and not gname.endswith("deva") and not u.isalpha()) \
               or (len(u) == 1 and u.isalpha() and gname.lower() == u.lower()):
                gn_agree += 1
        rows.append({
            "font": name, "tounicode_present": tu is not None,
            "used_codes": len(used),
            "tounicode_covers_used": None if tu is None else round(n_tu / max(1, len(used)), 3),
            "tounicode_vs_embedded_cmap_agree": None if tu is None or not n_tu else round(agree / n_tu, 3),
            "glyphname_vs_tounicode_agree": None if tu is None or not n_tu else round(gn_agree / n_tu, 3),
            "embedded_cmap_entries": len(cm), "embedded_tables": sorted(tt.keys()),
            "sample_glyph_names": sorted({order[c] for c in list(used)[:6] if c < len(order)}),
        })
    return rows


def recover_via_embedded_cmap(path):
    """R1: ignore ToUnicode, map CID->GID->Unicode through the embedded font's own cmap."""
    d = pymupdf.open(path)
    invs = {}
    for x in range(1, d.xref_length()):
        if d.xref_get_key(x, "Subtype")[1] != "/Type0":
            continue
        name = d.xref_get_key(x, "BaseFont")[1].replace("#20", " ").split("+")[-1]
        desc = int(d.xref_get_key(x, "DescendantFonts")[1].strip("[] ").split()[0])
        fd = int(d.xref_get_key(desc, "FontDescriptor")[1].split()[0])
        ff = int(d.xref_get_key(fd, "FontFile2")[1].split()[0])
        tt = TTFont(io.BytesIO(d.xref_stream(ff)))
        inv = {}
        if "cmap" not in tt:
            raise KeyError("embedded font program has no cmap table")
        for u, g in (tt.getBestCmap() or {}).items():
            inv.setdefault(tt.getGlyphID(g), chr(u))
        invs[name] = inv
        d.xref_set_key(x, "ToUnicode", "null")
    out = []
    for b in d[0].get_text("rawdict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                key = s["font"].split("+")[-1].replace(" ", "")[:8]
                inv = next((v for k, v in invs.items() if key in k.replace(" ", "")), {})
                out.append("".join(inv.get(ord(c["c"]), "�") for c in s["chars"]))
            out.append("\n")
    return "".join(out)


def legacy_table_remap(text):
    """R3: apply the (fixture's own) ASCII-slot table to ALL extracted text."""
    return "".join(INV_SLOT.get(c, c) for c in text)


BAD = re.compile(r"[\ufffd\x00-\x08\x0b\x0c\x0e-\x1f\ue000-\uf8ff]")


def font_level_flags(path):
    """Candidate span/font-level detector: group extracted text by font,
    flag a font if its own text is junk (control/FFFD/PUA > 2%) or, when it
    has >=3 Latin tokens, its English-lexicon hit rate is < 0.3."""
    d = pymupdf.open(path)
    by = {}
    for b in d[0].get_text("dict", flags=pymupdf.TEXTFLAGS_TEXT)["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                by.setdefault(s["font"], []).append(s["text"])
    flags = {}
    for f, parts in by.items():
        t = " ".join(parts)
        toks = re.findall(r"[A-Za-z]{3,}", t)
        hit = (sum(zipf_frequency(x.lower(), "en") >= 2.5 for x in toks) / len(toks)) if toks else None
        junk = len(BAD.findall(t)) / max(1, len(t))
        flags[f] = {"chars": len(t), "junk_ratio": round(junk, 3),
                    "lexicon_hit": None if hit is None else round(hit, 3),
                    "flag": junk > 0.02 or (hit is not None and len(toks) >= 3 and hit < 0.3)}
    return flags


results = []
for path in sorted(glob.glob("fixtures/F*.pdf")):
    name = os.path.basename(path)[:-4]
    ref = truth[name]
    d = pymupdf.open(path)
    prof = triage.profile_page(d[0])
    ex = extract_all(path)
    row = {
        "fixture": name,
        "arpipe_kind": prof.kind.value, "arpipe_route": "OCR" if prof.kind in triage.NEEDS_OCR else "NATIVE_READ",
        "arpipe_mojibake_ratio": prof.mojibake_ratio, "arpipe_script": prof.script.value,
        "n_chars": prof.n_chars,
        "pua_chars": sum(0xE000 <= ord(c) <= 0xF8FF for c in ex["pymupdf_default"]),
        "fffd_chars_no_cid_flag": ex["pymupdf_no_cid_flag"].count("�"),
        "dict_hit_rate": dict_hit_rate(ex["pymupdf_default"]),
        "cer_native_pymupdf": cer(ex["pymupdf_default"], ref),
        "cer_pdfminer": cer(ex["pdfminer"], ref),
        "cer_pypdf": cer(ex["pypdf"], ref),
        "pdfminer_cid_tokens": ex["pdfminer"].count("(cid:"),
        "sample_pymupdf": ex["pymupdf_default"][:60],
        "sample_pdfminer": ex["pdfminer"][:60],
    }
    lang = "hin+eng" if any(0x900 <= ord(c) <= 0x97F for c in ref) else "eng"
    row["ocr_lang"] = lang
    row["cer_ocr_tesseract"] = cer(ocr(path, lang), ref)
    try:
        row["cer_R1_embedded_cmap"] = cer(recover_via_embedded_cmap(path), ref)
    except Exception as e:
        row["cer_R1_embedded_cmap"] = f"ERR {type(e).__name__}"
    row["cer_R3_blind_legacy_table"] = cer(legacy_table_remap(ex["pymupdf_default"]), ref)
    row["fonts"] = font_signals(path)
    row["font_level_flags"] = font_level_flags(path)
    row["font_level_any_flag"] = any(v["flag"] for v in row["font_level_flags"].values())
    results.append(row)
    print(name, row["arpipe_kind"], row["arpipe_mojibake_ratio"], row["cer_native_pymupdf"],
          row["cer_ocr_tesseract"], row["cer_R1_embedded_cmap"], row["cer_R3_blind_legacy_table"], row["font_level_any_flag"], flush=True)

json.dump({"pymupdf": pymupdf.VersionBind, "results": results},
          open("results.json", "w"), ensure_ascii=False, indent=1)
