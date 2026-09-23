"""TOOLING_POC_ONLY. RESEARCH_ONLY. NOT GOLD.

Drives a locally running Label Studio Community server (multi-image `Image valueList`
document path) with the SAME synthetic PDFs used for the custom-tool POC. Every
annotation created here is a machine-generated probe, not a label.

usage: python poc_ls_harness.py <docs_dir> <work_dir> <out_json> <ls_data_dir> <label-studio.exe>
"""
from __future__ import annotations

import http.server
import json
import os
import subprocess
import sys
import threading
import time

import psutil
import pymupdf
import requests
from playwright.sync_api import sync_playwright

DOCS, WORK, OUT, LS_DATA, LS_EXE = sys.argv[1:6]
LS = "http://127.0.0.1:8080"
IMG_PORT = 8081
TOK_A = "0123456789abcdef0123456789abcdef01234567"
TOK_B = "fedcba9876543210fedcba9876543210fedcba98"
R: dict = {"label": "TOOLING_POC_ONLY", "gold": False, "tool": "Label Studio Community 1.23.0 (Python 3.12.14)", "checks": {}}
C = R["checks"]
HITS: dict[str, int] = {}


class CORSHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_GET(self):
        key = self.path.split("/")[1] if "/" in self.path else self.path
        HITS[key] = HITS.get(key, 0) + 1
        super().do_GET()


def hdr(tok):
    return {"Authorization": f"Token {tok}"}


def ls_rss():
    """Sum RSS of the process listening on :8080 and its children (real interpreter, not the venv launcher stub)."""
    pid = None
    for c in psutil.net_connections(kind="tcp"):
        if c.status == "LISTEN" and c.laddr and c.laddr.port == 8080:
            pid = c.pid
    if pid is None:
        return None
    root = psutil.Process(pid)
    return round(sum(q.memory_info().rss for q in [root] + root.children(recursive=True)) / 1e6, 1)


def main():
    img_root = os.path.join(WORK, "ls_images")
    os.makedirs(img_root, exist_ok=True)
    # ---- pre-render page images (LS Community has no lazy PDF path; this is a REQUIRED preprocessing step)
    prerender = {}
    for name in ("synth_2p", "synth_20p", "synth_600p"):
        d = os.path.join(img_root, name)
        os.makedirs(d, exist_ok=True)
        t = time.perf_counter()
        total = 0
        with pymupdf.open(os.path.join(DOCS, name + ".pdf")) as doc:
            for i, page in enumerate(doc):
                pix = page.get_pixmap(dpi=110, alpha=False)
                pix.save(os.path.join(d, f"{i}.png"))
                total += os.path.getsize(os.path.join(d, f"{i}.png"))
        prerender[name] = {"seconds": round(time.perf_counter() - t, 2), "image_bytes_total": total}
    C["prerender_all_pages_required"] = prerender

    handler = lambda *a, **k: CORSHandler(*a, directory=img_root, **k)
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", IMG_PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    # ---- second user: join user A's organization through the invite link, then read B's legacy token
    C["second_user"] = {}
    try:
        inv = requests.get(f"{LS}/api/invite", headers=hdr(TOK_A))
        C["second_user"]["invite_status"] = inv.status_code
        invite_url = inv.json().get("invite_url")
        s2 = requests.Session()
        s2.get(LS + invite_url)
        csrf = s2.cookies.get("csrftoken")
        su = s2.post(LS + invite_url, data={"email": "b1@example.invalid", "password": "PocPassw0rd-b1", "csrfmiddlewaretoken": csrf},
                     headers={"Referer": LS + invite_url}, allow_redirects=False)
        C["second_user"]["signup_status"] = su.status_code
        tk = s2.get(LS + "/api/current-user/token")
        C["second_user"]["token_status"] = tk.status_code
        global TOK_B
        TOK_B = tk.json().get("token", TOK_B) if tk.ok else TOK_B
    except Exception as e:  # recorded, not hidden
        C["second_user"]["error"] = repr(e)[:200]

    # ---- project + tasks
    cfg = """<View>
  <Image name="pdf" valueList="$pages"/>
  <RectangleLabels name="regions" toName="pdf"><Label value="poc_region"/></RectangleLabels>
  <Number name="mda_start_page" toName="pdf" min="1" max="700"/>
  <Number name="mda_end_page" toName="pdf" min="1" max="700"/>
</View>"""
    pids, tid = {}, {}
    t_imp = time.perf_counter()
    for name, n in (("synth_2p", 2), ("synth_20p", 20), ("synth_600p", 600)):
        rp = requests.post(f"{LS}/api/projects", headers=hdr(TOK_A), json={"title": "POC_NOT_GOLD_" + name, "label_config": cfg})
        pids[name] = rp.json()["id"]
        task = [{"data": {"pages": [f"http://127.0.0.1:{IMG_PORT}/{name}/{i}.png" for i in range(n)], "poc_doc": name}}]
        imp = requests.post(f"{LS}/api/projects/{pids[name]}/import?commit_to_project=true", headers=hdr(TOK_A), json=task)
        tl = requests.get(f"{LS}/api/tasks", headers=hdr(TOK_A), params={"project": pids[name], "page_size": 10}).json()
        tl = tl["tasks"] if isinstance(tl, dict) else tl
        tid[name] = tl[0]["id"]
        C.setdefault("import", {})[name] = {"project_status": rp.status_code, "import_status": imp.status_code}
    C["import_total_seconds_3_projects"] = round(time.perf_counter() - t_imp, 3)
    C["project_ids"], C["task_ids"] = pids, tid
    big = requests.get(f"{LS}/api/tasks/{tid['synth_600p']}", headers=hdr(TOK_A))
    C["task_600p_api_payload_bytes"] = len(big.content)
    C["ls_rss_mb_after_import"] = ls_rss()

    # ---- browser: login, open the 600-page task, measure first render + preload behaviour
    with sync_playwright() as p:
        br = p.chromium.launch(channel="msedge", headless=True)
        ctx = br.new_context(viewport={"width": 1400, "height": 1000})
        pg = ctx.new_page()
        pg.goto(f"{LS}/user/login/")
        pg.fill("input[name=email]", "a1@example.invalid")
        pg.fill("input[name=password]", "PocPassw0rd-a1")
        pg.keyboard.press("Enter")
        pg.wait_for_load_state("networkidle")
        cdp = ctx.new_cdp_session(pg)
        cdp.send("Performance.enable")

        def heap():
            return next(m["value"] for m in cdp.send("Performance.getMetrics")["metrics"] if m["name"] == "JSHeapUsedSize")

        B = {}
        for name in ("synth_2p", "synth_20p", "synth_600p"):
            HITS.clear()
            t = time.perf_counter()
            pg.goto(f"{LS}/projects/{pids[name]}/data?labeling=1")
            ok = True
            try:
                pg.wait_for_selector(".lsf-image-tool, .lsf-object img, .lsf-pagination", timeout=90000)
                pg.wait_for_load_state("networkidle", timeout=120000)
            except Exception as e:
                ok = False
                B[name + "_error"] = str(e)[:160]
            B[name] = {"ui_ready": ok, "seconds_to_network_idle": round(time.perf_counter() - t, 2),
                       "page_image_requests_served": HITS.get(name, 0), "task_number_shown": (pg.inner_text("body").split("#")[1][:6] if "#" in pg.inner_text("body") else None), "pages_in_task": {"synth_2p": 2, "synth_20p": 20, "synth_600p": 600}[name],
                       "js_heap_mb": round(heap() / 1e6, 1), "ls_server_rss_mb": ls_rss(), "url_after": pg.url[-60:]}
        C["browser_open_task"] = B
        pg.screenshot(path=os.path.join(WORK, "ls_600p_labeling.png"))
        br.close()

    # ---- annotations by two users (probes): region on page index 5 of the 20-page task, doc-level span numbers
    with pymupdf.open(os.path.join(DOCS, "synth_20p.pdf")) as sd:
        p5 = sd.load_page(5)
        rect = p5.search_for("ANNEXURE V - MANAGEMENT DISCUSSION AND ANALYSIS")[0]
        W, H = p5.rect.width, p5.rect.height
    exp = [rect.x0 / W, rect.y0 / H, rect.x1 / W, rect.y1 / H]
    imgw, imgh = pymupdf.open(os.path.join(DOCS, "synth_20p.pdf")).load_page(5).get_pixmap(dpi=110).width, pymupdf.open(os.path.join(DOCS, "synth_20p.pdf")).load_page(5).get_pixmap(dpi=110).height

    def payload(delta):
        return {"result": [
            {"from_name": "regions", "to_name": "pdf", "type": "rectanglelabels", "item_index": 5, "original_width": imgw, "original_height": imgh, "image_rotation": 0,
             "value": {"x": exp[0] * 100 + delta, "y": exp[1] * 100, "width": (exp[2] - exp[0]) * 100, "height": (exp[3] - exp[1]) * 100, "rotation": 0, "rectanglelabels": ["poc_region"]}},
            {"from_name": "mda_start_page", "to_name": "pdf", "type": "number", "value": {"number": 6}},
            {"from_name": "mda_end_page", "to_name": "pdf", "type": "number", "value": {"number": 10}}]}
    ra = requests.post(f"{LS}/api/tasks/{tid['synth_20p']}/annotations", headers=hdr(TOK_A), json=payload(0.0))
    rb = requests.post(f"{LS}/api/tasks/{tid['synth_20p']}/annotations", headers=hdr(TOK_B), json=payload(0.2))
    C["two_users_annotate_status"] = [ra.status_code, rb.status_code]
    # blinding: can user B read user A's annotation through the API?
    seen_by_b = requests.get(f"{LS}/api/tasks/{tid['synth_20p']}/annotations", headers=hdr(TOK_B))
    C["blinding_probe"] = {"status": seen_by_b.status_code, "annotations_visible_to_B": len(seen_by_b.json()) if seen_by_b.ok else None,
                           "note": "Community edition; no role/visibility restriction observed if >1"}
    ex = requests.get(f"{LS}/api/projects/{pids['synth_20p']}/export", headers=hdr(TOK_A), params={"exportType": "JSON"})
    C["export_status"] = ex.status_code
    rows = ex.json()
    row20 = [x for x in rows if x["data"].get("poc_doc") == "synth_20p"][0]
    anns = row20["annotations"]
    C["export_annotation_keys"] = sorted(anns[0].keys())
    reg = [r for r in anns[0]["result"] if r["type"] == "rectanglelabels"][0]
    got = [reg["value"]["x"] / 100, reg["value"]["y"] / 100, (reg["value"]["x"] + reg["value"]["width"]) / 100, (reg["value"]["y"] + reg["value"]["height"]) / 100]
    C["coordinate_roundtrip_max_error_points_user_A"] = round(max(abs(got[0] - exp[0]) * W, abs(got[2] - exp[2]) * W, abs(got[1] - exp[1]) * H, abs(got[3] - exp[3]) * H), 4)
    C["page_index_in_export"] = {"item_index": reg.get("item_index"), "convention": "0-based (docs); UI page counter shown 1-based"}
    C["two_annotations_in_export_with_distinct_users"] = sorted({a.get("completed_by") for a in anns}) if len(anns) > 1 else "only one"
    C["provenance_missing_from_export"] = [k for k in ("source_pdf_sha256", "rendered_image_sha256", "tool_version", "protocol_version", "annotator_anonymous_id")
                                           if k not in json.dumps(row20)]
    C["ls_rss_mb_final"] = ls_rss()
    C["ls_data_dir_mb"] = round(sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(LS_DATA) for f in fs) / 1e6, 1)
    httpd.shutdown()
    json.dump(R, open(OUT, "w", encoding="utf-8"), indent=2, sort_keys=True)
    print(json.dumps(C, indent=1)[:6000])


if __name__ == "__main__":
    main()
