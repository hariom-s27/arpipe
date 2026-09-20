"""TOOLING_POC_ONLY. RESEARCH_ONLY. NOT GOLD.

Follow-up to poc_ls_harness.py: page navigation inside the 600-page Label Studio task.
Assumes the harness left Label Studio running with project 3 = the 600-page task.
usage: python poc_ls_nav.py <work_dir> <out_json>
"""
from __future__ import annotations

import http.server
import json
import os
import sys
import threading
import time

import psutil
from playwright.sync_api import sync_playwright

WORK, OUT = sys.argv[1:3]
LS = "http://127.0.0.1:8080"
HITS: list[str] = []


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_GET(self):
        HITS.append(self.path)
        super().do_GET()


def rss():
    pid = next((c.pid for c in psutil.net_connections(kind="tcp") if c.status == "LISTEN" and c.laddr.port == 8080), None)
    r = psutil.Process(pid)
    return round(sum(q.memory_info().rss for q in [r] + r.children(recursive=True)) / 1e6, 1)


def main():
    root = os.path.join(WORK, "ls_images")
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8081), lambda *a, **k: H(*a, directory=root, **k))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    out = {"label": "TOOLING_POC_ONLY", "gold": False, "tool": "Label Studio Community 1.23.0", "nav": {}}
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
        heap = lambda: round(next(m["value"] for m in cdp.send("Performance.getMetrics")["metrics"] if m["name"] == "JSHeapUsedSize") / 1e6, 1)
        HITS.clear()
        t = time.perf_counter()
        pg.goto(f"{LS}/projects/3/data?labeling=1")
        pg.wait_for_selector(".lsf-pagination", timeout=90000)
        pg.wait_for_load_state("networkidle")
        out["nav"]["open_seconds"] = round(time.perf_counter() - t, 2)
        out["nav"]["pagination_text"] = pg.locator(".lsf-pagination").first.inner_text()[:40]
        out["nav"]["image_requests_at_open"] = len([h for h in HITS if "synth_600p" in h])
        out["nav"]["js_heap_mb_at_open"] = heap()
        # idle wait: does LS keep preloading the remaining pages in the background?
        time.sleep(20)
        out["nav"]["image_requests_after_20s_idle"] = len([h for h in HITS if "synth_600p" in h])
        # jump to page 301 (1-based) by typing into the pagination input
        HITS.clear()
        pg.locator(".lsf-pagination__page-indicator").first.click()   # indicator turns into an editable input
        inp = pg.locator(".lsf-pagination input, .lsf-pagination__input input").first
        t = time.perf_counter()
        inp.fill("301")
        inp.press("Enter")
        try:
            pg.wait_for_function(r"document.querySelector('.lsf-pagination').innerText.replace(/\s+/g,' ').startsWith('301')", timeout=30000)
            out["nav"]["jump_to_301_seconds"] = round(time.perf_counter() - t, 2)
        except Exception as e:
            out["nav"]["jump_error"] = str(e)[:120]
        pg.wait_for_load_state("networkidle")
        out["nav"]["pagination_after_jump"] = pg.locator(".lsf-pagination").first.inner_text()[:40]
        out["nav"]["requested_after_jump"] = sorted({h.split("/")[-1] for h in HITS if "synth_600p" in h}, key=lambda s: int(s.split(".")[0]))[:12]
        # 30 forward steps using the next-page button
        nxt = pg.locator(".lsf-pagination__btn_arrow-right:not(.lsf-pagination__btn_arrow-right-double)").first
        t = time.perf_counter()
        for _ in range(30):
            nxt.click()
        pg.wait_for_load_state("networkidle")
        out["nav"]["30_next_clicks_seconds"] = round(time.perf_counter() - t, 2)
        out["nav"]["pagination_after_30_next"] = pg.locator(".lsf-pagination").first.inner_text()[:40]
        out["nav"]["js_heap_mb_after_nav"] = heap()
        out["nav"]["ls_server_rss_mb"] = rss()
        pg.screenshot(path=os.path.join(WORK, "ls_600p_after_nav.png"))
        br.close()
    srv.shutdown()
    json.dump(out, open(OUT, "w", encoding="utf-8"), indent=2, sort_keys=True)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
