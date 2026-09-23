"""TOOLING_POC_ONLY. RESEARCH_ONLY. NOT GOLD.

Drives custom_poc_server.py with (a) HTTP-level checks and (b) a real Edge browser
(Playwright, channel=msedge) on the synthetic PDFs. Writes results_custom.json.
No annotation made here is a label: every record is a machine-generated probe.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import shutil

import psutil
import pymupdf
import requests
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = sys.argv[1]
WORK = sys.argv[2]
OUT = sys.argv[3]
PORT = 8765
BASE = f"http://127.0.0.1:{PORT}"
R: dict = {"label": "TOOLING_POC_ONLY", "gold": False, "tool": "custom (arpipe-custom-poc 0.0.1-POC)", "checks": {}}


def opaque_ids():
    return {d["n_pages"]: d["doc"] for d in requests.get(BASE + "/api/docs").json()}


def main():
    data = os.path.join(WORK, "custom_data")
    shutil.rmtree(data, ignore_errors=True)
    t0 = time.perf_counter()
    srv = subprocess.Popen([sys.executable, os.path.join(HERE, "custom_poc_server.py"), "--docs", DOCS, "--data", data, "--port", str(PORT)],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    srv.stdout.readline()
    R["checks"]["server_start_seconds"] = round(time.perf_counter() - t0, 3)
    proc = psutil.Process(srv.pid)

    def rss_mb() -> float:
        # On Windows a venv python.exe is a launcher stub that spawns the real interpreter as a child:
        # measure the whole process tree, never the stub alone.
        procs = [proc] + proc.children(recursive=True)
        return round(sum(q.memory_info().rss for q in procs) / 1e6, 1)
    try:
        ids = opaque_ids()
        R["checks"]["docs_listed"] = requests.get(BASE + "/api/docs").json()
        R["checks"]["doc_listing_leaks_filename_or_outline"] = any(("synth" in json.dumps(d)) for d in R["checks"]["docs_listed"])
        d600, d20, d2 = ids[600], ids[20], ids[2]

        # ---- server-side render latency, cold vs warm, incl. long-document pages
        lat = {}
        for label, doc, pg in (("2p_p0", d2, 0), ("20p_p5", d20, 5), ("600p_p0", d600, 0), ("600p_p300", d600, 300), ("600p_p599", d600, 599)):
            cold = requests.get(f"{BASE}/api/page/{doc}/{pg}.png?dpi=110")
            warm = requests.get(f"{BASE}/api/page/{doc}/{pg}.png?dpi=110")
            lat[label] = {"cold_render_s": float(cold.headers["X-Render-Seconds"]), "warm_render_s": float(warm.headers["X-Render-Seconds"]),
                          "png_bytes": len(cold.content), "page_points": cold.headers["X-Page-Points"], "image_sha256": cold.headers["X-Image-SHA256"][:16]}
        R["checks"]["render_latency"] = lat
        # bounds
        R["checks"]["out_of_range_page_status"] = requests.get(f"{BASE}/api/page/{d600}/600.png").status_code

        # ---- page-numbering convention check (0-based API, 1-based UI)
        R["checks"]["page_index_convention"] = "API/records 0-based physical index; UI shows 1-based; folio never shown"

        # ---- RSS after touching all 600 pages once (lazy renders, LRU cache 64)
        rss0 = rss_mb()
        t1 = time.perf_counter()
        for pg in range(0, 600, 1):
            requests.get(f"{BASE}/api/page/{d600}/{pg}.png?dpi=110")
        R["checks"]["scan_all_600_pages"] = {"seconds": round(time.perf_counter() - t1, 2), "server_rss_mb_before": rss0,
                                             "server_rss_mb_after": rss_mb(), "process_tree_size": 1 + len(proc.children(recursive=True))}

        # ---- browser-side tests
        with sync_playwright() as p:
            br = p.chromium.launch(channel="msedge", headless=True)
            def ctx(annotator):
                c = br.new_context(viewport={"width": 1200, "height": 1100})
                pg = c.new_page()
                pg.goto(BASE + "/")
                pg.wait_for_function("window.__loaded===0")
                pg.fill("#ann", annotator)
                return c, pg
            cA, pA = ctx("A01")
            cdp = cA.new_cdp_session(pA)
            cdp.send("Performance.enable")
            def heap(): return next(m["value"] for m in cdp.send("Performance.getMetrics")["metrics"] if m["name"] == "JSHeapUsedSize")
            B = {}
            B["js_heap_mb_initial"] = round(heap() / 1e6, 2)
            # select the 600-page doc, jump to page 300 (1-based 301)
            pA.select_option("#doc", d600)
            pA.wait_for_function("window.__loaded===0")
            t = time.perf_counter()
            pA.fill("#pg", "301"); pA.dispatch_event("#pg", "change")
            pA.wait_for_function("window.__loaded===300")
            B["jump_to_page_301_seconds"] = round(time.perf_counter() - t, 3)
            # 100 sequential next-page navigations (expected: lazy, constant memory)
            t = time.perf_counter()
            for _ in range(100):
                cur = pA.evaluate("window.__loaded")
                pA.click("#next"); pA.wait_for_function(f"window.__loaded==={cur + 1}")
            B["100_next_page_clicks_seconds"] = round(time.perf_counter() - t, 2)
            B["js_heap_mb_after_100_pages_of_600p"] = round(heap() / 1e6, 2)
            # network: only visible pages fetched?
            B["images_in_dom"] = pA.evaluate("document.images.length")
            # ---- coordinate fidelity on the 20p doc, page index 5 (MD&A heading page)
            pA.select_option("#doc", d20); pA.wait_for_function("window.__loaded===0")
            pA.fill("#pg", "6"); pA.dispatch_event("#pg", "change"); pA.wait_for_function("window.__loaded===5")
            with pymupdf.open(os.path.join(DOCS, "synth_20p.pdf")) as sd:
                pg5 = sd.load_page(5)
                rect = pg5.search_for("ANNEXURE V - MANAGEMENT DISCUSSION AND ANALYSIS")[0]
                W, H = pg5.rect.width, pg5.rect.height
            exp = [rect.x0 / W, rect.y0 / H, rect.x1 / W, rect.y1 / H]
            box = pA.locator("#ov").bounding_box()
            x0, y0 = box["x"] + exp[0] * box["width"], box["y"] + exp[1] * box["height"]
            x1, y1 = box["x"] + exp[2] * box["width"], box["y"] + exp[3] * box["height"]
            pA.mouse.move(x0, y0); pA.mouse.down(); pA.mouse.move(x1, y1, steps=5); pA.mouse.up()
            pA.click("#save"); pA.wait_for_function("document.querySelector('#msg').textContent==='saved'")
            pA.click("#ms")   # a span-start probe on the same page
            rows = requests.get(f"{BASE}/api/mine", params={"annotator": "A01"}).json()
            reg = [r for r in rows if r["payload"]["kind"] == "region_POC"][-1]
            got = reg["payload"]["bbox_norm"]
            err_pt = max(abs(got[0] - exp[0]) * W, abs(got[2] - exp[2]) * W, abs(got[1] - exp[1]) * H, abs(got[3] - exp[3]) * H)
            B["coordinate_roundtrip_max_error_points"] = round(err_pt, 3)
            B["coordinate_roundtrip_note"] = "expected bbox = text bbox of synthetic MD&A heading from PyMuPDF; drawn by scripted mouse at the rendered image scale (110 dpi); error dominated by integer-pixel mouse resolution (~0.65 pt/px)"
            B["record_page_index0"] = reg["payload"]["page_index0"]
            B["provenance_fields_present"] = sorted(k for k in reg if k not in ("payload",))
            # ---- second independent annotator context (separate browser context = separate session)
            cB, pB = ctx("A02")
            pB.select_option("#doc", d20); pB.wait_for_function("window.__loaded===0")
            pB.click("#me")
            R["checks"]["browser"] = B
            br.close()

        # ---- isolation / role checks
        mine_A02 = requests.get(f"{BASE}/api/mine", params={"annotator": "A02"}).json()
        mine_A01 = requests.get(f"{BASE}/api/mine", params={"annotator": "A01"}).json()
        R["checks"]["isolation"] = {
            "A02_sees_only_own_records": all(r["annotator_id"] == "A02" for r in mine_A02) and len(mine_A02) == 1,
            "A01_sees_only_own_records": all(r["annotator_id"] == "A01" for r in mine_A01),
            "compare_without_adjudicator_status": requests.get(f"{BASE}/api/compare", params={"annotator": "A01", "doc": d20}).status_code,
            "compare_as_adjudicator_status": requests.get(f"{BASE}/api/compare", params={"annotator": "ADJ01", "doc": d20}).status_code,
            "compare_returns_both_annotators": sorted(requests.get(f"{BASE}/api/compare", params={"annotator": "ADJ01", "doc": d20}).json().keys()),
            "invalid_annotator_id_status": requests.get(f"{BASE}/api/mine", params={"annotator": "alice@example.com"}).status_code,
            "known_weakness": "POC has NO authentication: annotator id is self-declared; a real deployment needs per-annotator credentials/tokens. ADJ role is likewise unauthenticated here.",
        }
        # append-only + export
        p = os.path.join(data, "annotations_A01.jsonl")
        n1 = sum(1 for _ in open(p, encoding="utf-8"))
        requests.post(BASE + "/api/annotate", json={"annotator": "A01", "doc": d2, "payload": {"kind": "probe"}})
        n2 = sum(1 for _ in open(p, encoding="utf-8"))
        R["checks"]["append_only_export"] = {"lines_before": n1, "lines_after": n2, "format": "JSONL, one record per action, server-stamped provenance"}
        R["checks"]["server_rss_mb_final_process_tree"] = rss_mb()
    finally:
        srv.terminate()
    json.dump(R, open(OUT, "w", encoding="utf-8"), indent=2, sort_keys=True)
    print(json.dumps(R["checks"].get("browser", {}), indent=1))


if __name__ == "__main__":
    main()
