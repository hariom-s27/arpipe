"""Build a local, offline review page for the P5-B.3 MD&A title pre-fill.

Human-in-the-loop tool. It makes NO decisions. It shows every document with its
pre-filled title lines, all mechanically found candidate lines, and the page images,
and lets the reviewer accept, pick or type the verbatim title. "Download CSV" saves the
reviewer's answers. Nothing is sent anywhere; the page works from disk.

Run (PowerShell, from anywhere):
  & "C:\\Program Files\\Python314\\python.exe" make_review_page.py --p5b3 D:\\gold_blind\\output\\p5b3 --pdfs D:\\gold_blind\\fit_pdfs
Writes only into <p5b3>\\review\\ (review.html + pages\\*.png). Then open review.html.
"""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

RISK_ORDER = ["NO_HIT", "HINT_DISAGREES", "MENTION_LIKE", "MANY_HITS", "BILINGUAL", "NO_TEXT_LAYER"]


def read_csv(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def pick(row, *names):
    """Return the first column whose lower-case name contains all given fragments."""
    for k in row:
        kl = k.lower()
        if all(n in kl for n in names):
            return row[k] or ""
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--p5b3", required=True)
    ap.add_argument("--pdfs", required=True)
    ap.add_argument("--dpi", type=int, default=90)
    a = ap.parse_args()
    base = Path(a.p5b3)
    out = base / "review"
    (out / "pages").mkdir(parents=True, exist_ok=True)

    prefill = read_csv(base / "MDNA_TITLE_PREFILL_v0_1.csv")
    cands = read_csv(base / "MDNA_CANDIDATE_LINES_v0_1.csv")
    by_doc = defaultdict(list)
    for c in cands:
        by_doc[c["document_id"]].append(c)

    docs = []
    need_pages = defaultdict(set)
    for r in prefill:
        d = r["document_id"]
        flags = pick(r, "flag")
        toc_p = pick(r, "prefill", "toc", "page")
        body_p = pick(r, "prefill", "body", "page")
        cl = sorted(by_doc.get(d, []), key=lambda c: (int(c["page_0based"]), int(c.get("line_no") or 0)))
        pages = sorted({int(c["page_0based"]) for c in cl} | {int(x) for x in (toc_p, body_p) if x.strip().isdigit()})
        for p in pages:
            need_pages[d].add(p)
        risk = min([RISK_ORDER.index(f) for f in flags.split(";") if f in RISK_ORDER] or [99])
        docs.append({
            "id": d,
            "flags": flags,
            "risk": risk,
            "toc_title": pick(r, "prefill", "toc", "title"),
            "toc_page": toc_p,
            "body_title": pick(r, "prefill", "body", "title"),
            "body_page": body_p,
            "hint_toc": r.get("toc_pages_0based", ""),
            "hint_body": r.get("body_pages_0based", ""),
            "cands": [{"p": int(c["page_0based"]), "t": c["line_text"], "fs": c.get("font_size_max", ""),
                       "b": c.get("is_bold", "")} for c in cl],
            "pages": pages,
        })
    docs.sort(key=lambda x: (x["risk"], x["id"]))

    import pymupdf
    for d, pages in sorted(need_pages.items()):
        pdf = Path(a.pdfs) / f"{d}.pdf"
        if not pdf.exists():
            continue
        with pymupdf.open(pdf) as doc:
            for p in sorted(pages):
                png = out / "pages" / f"{d}_p{p}.png"
                if not png.exists() and 0 <= p < doc.page_count:
                    doc[p].get_pixmap(dpi=a.dpi).save(png)

    import os
    rel = os.path.relpath(Path(a.pdfs).resolve(), out.resolve()).replace(os.sep, "/")
    for x in docs:
        x["pdf"] = f"{rel}/{x['id']}.pdf"
    data = json.dumps(docs, ensure_ascii=False).replace("</", "<\\/")
    (out / "review.html").write_text(PAGE.replace("__DATA__", data), encoding="utf-8")
    print(f"documents: {len(docs)}; page images: {sum(len(v) for v in need_pages.values())}; open {out / 'review.html'}")


PAGE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>MD&A Title Review</title>
<style>
:root{--bg:#fff;--fg:#1a1a1a;--mut:#666;--card:#f6f6f4;--line:#ddd;--acc:#1f5fbf;--warn:#b35c00;--ok:#2e7d32}
@media (prefers-color-scheme:dark){:root{--bg:#161616;--fg:#eee;--mut:#aaa;--card:#222;--line:#3a3a3a;--acc:#7fb0ff;--warn:#f0a050;--ok:#7bc47f}}
body{background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif;margin:0 16px 80px}
header{position:sticky;top:0;background:var(--bg);padding:10px 0;border-bottom:1px solid var(--line);z-index:2;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
button{font:inherit;padding:6px 12px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--fg);cursor:pointer}
.doc{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;margin:14px 0}
.doc.done{border-color:var(--ok)}.flags{color:var(--warn);font-weight:600}.mut{color:var(--mut);font-size:13px}
.row{display:grid;grid-template-columns:150px 1fr;gap:6px 12px;margin:6px 0;align-items:start}
input[type=text]{width:100%;box-sizing:border-box;font:inherit;padding:5px;border:1px solid var(--line);border-radius:5px;background:var(--bg);color:var(--fg)}
.cand{font-family:ui-monospace,monospace;font-size:13px;margin:2px 0}.cand button{padding:1px 6px;font-size:12px;margin-right:4px}
.imgs{display:flex;gap:10px;overflow-x:auto;padding:6px 0}.imgs figure{margin:0}.imgs img{height:520px;border:1px solid var(--line)}
figcaption{font-size:12px;color:var(--mut)}
@media (max-width:700px){.row{grid-template-columns:1fr}.imgs img{height:360px}}
</style></head><body>
<header><strong>MD&amp;A title review</strong><span id="prog" class="mut"></span>
<button onclick="dl()">Download CSV</button><span class="mut">Answers autosave in this browser. Record titles exactly as printed.</span></header>
<main id="m"></main>
<script>
const D=__DATA__;const KEY="p5b3_review_v1";let S={};
try{S=JSON.parse(localStorage.getItem(KEY)||"{}")}catch(e){S={}}
function save(){try{localStorage.setItem(KEY,JSON.stringify(S))}catch(e){}prog()}
function esc(t){return String(t).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]))}
function st(id){return S[id]||(S[id]={present:"",toc_title:"",toc_page:"",toc_src:"",body_title:"",body_page:"",body_src:"",notes:""})}
function set(id,k,v){st(id)[k]=v;save();mark(id)}
function mark(id){const s=st(id);document.getElementById("c_"+id).classList.toggle("done",!!s.present)}
function prog(){const n=D.filter(d=>(S[d.id]||{}).present).length;document.getElementById("prog").textContent=n+" / "+D.length+" documents marked"}
function fill(id,which,t,p,src){const s=st(id);s[which+"_title"]=t;s[which+"_page"]=String(p);s[which+"_src"]=src;save();
 document.getElementById(which+"t_"+id).value=t;document.getElementById(which+"p_"+id).value=p}
function render(){const m=document.getElementById("m");m.innerHTML=D.map(d=>{const s=st(d.id);return `
<section class="doc" id="c_${d.id}"><div><strong>${d.id}</strong> <span class="flags">${esc(d.flags)}</span>
<span class="mut">hints TOC [${esc(d.hint_toc)}] BODY [${esc(d.hint_body)}]</span>
<a href="${esc(d.pdf)}" target="_blank">open PDF</a> <span class="mut">(PDF viewer pages are 1-based: add 1)</span></div>
<div class="row"><div>MD&amp;A present?</div><div>
${["Y","N","NOT_AR"].map(v=>`<label><input type="radio" name="pr_${d.id}" ${s.present==v?"checked":""} onchange="set('${d.id}','present','${v}')"> ${v}</label>`).join(" ")}</div></div>
<div class="row"><div>Pre-fill TOC</div><div>${d.toc_title?`<span class="cand">p${esc(d.toc_page)}: ${esc(d.toc_title)}</span> <button onclick="fill('${d.id}','toc',${esc(JSON.stringify(d.toc_title))},'${d.toc_page}','PREFILL')">accept</button>`:'<span class="mut">none</span>'}</div></div>
<div class="row"><div>Pre-fill BODY</div><div>${d.body_title?`<span class="cand">p${esc(d.body_page)}: ${esc(d.body_title)}</span> <button onclick="fill('${d.id}','body',${esc(JSON.stringify(d.body_title))},'${d.body_page}','PREFILL')">accept</button>`:'<span class="mut">none</span>'}</div></div>
<div class="row"><div>TOC title (verbatim)</div><div><input type="text" id="toct_${d.id}" value="${esc(s.toc_title)}" oninput="set('${d.id}','toc_title',this.value);set('${d.id}','toc_src','TYPED')"> page <input type="text" style="width:70px" id="tocp_${d.id}" value="${esc(s.toc_page)}" oninput="set('${d.id}','toc_page',this.value)"></div></div>
<div class="row"><div>BODY title (verbatim)</div><div><input type="text" id="bodyt_${d.id}" value="${esc(s.body_title)}" oninput="set('${d.id}','body_title',this.value);set('${d.id}','body_src','TYPED')"> start page <input type="text" style="width:70px" id="bodyp_${d.id}" value="${esc(s.body_page)}" oninput="set('${d.id}','body_page',this.value)"></div></div>
<div class="row"><div>Notes</div><div><input type="text" value="${esc(s.notes)}" oninput="set('${d.id}','notes',this.value)"></div></div>
<details><summary>${d.cands.length} candidate lines (click to use as TOC or BODY)</summary>${d.cands.map(c=>`<div class="cand">
<button onclick="fill('${d.id}','toc',${esc(JSON.stringify(c.t))},'${c.p}','CANDIDATE')">TOC</button><button onclick="fill('${d.id}','body',${esc(JSON.stringify(c.t))},'${c.p}','CANDIDATE')">BODY</button>
p${c.p} [fs ${esc(c.fs)}${c.b=="Y"||c.b=="True"?" bold":""}] ${esc(c.t)}</div>`).join("")}</details>
<div class="imgs">${d.pages.map(p=>`<figure><img loading="lazy" src="pages/${d.id}_p${p}.png" alt="${d.id} page ${p}"><figcaption>page ${p} (0-based)</figcaption></figure>`).join("")}</div>
</section>`}).join("");D.forEach(d=>mark(d.id));prog()}
function dl(){const H=["document_id","REVIEWER_mdna_present","REVIEWER_toc_title_verbatim","REVIEWER_toc_page_0based","REVIEWER_toc_source","REVIEWER_body_title_verbatim","REVIEWER_body_start_page_0based","REVIEWER_body_source","REVIEWER_notes"];
 const q=v=>'"'+String(v??"").replace(/"/g,'""')+'"';
 const rows=D.map(d=>{const s=st(d.id);return [d.id,s.present,s.toc_title,s.toc_page,s.toc_src,s.body_title,s.body_page,s.body_src,s.notes].map(q).join(",")});
 const b=new Blob(["\ufeff"+H.join(",")+"\n"+rows.join("\n")+"\n"],{type:"text/csv"});const a=document.createElement("a");
 a.href=URL.createObjectURL(b);a.download="MDNA_TITLE_REVIEW_v0_1.csv";a.click()}
render();
</script></body></html>"""

if __name__ == "__main__":
    main()
