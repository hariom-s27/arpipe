"""TOOLING_POC_ONLY. RESEARCH_ONLY. NOT GOLD. NOT A PROPOSED GOLD TOOL.

Minimal custom local/private annotation interface, built only to test whether a
small purpose-built tool can satisfy the ARPipe requirements that Label Studio /
Prodigy / doccano must be tested against (lazy page rendering of 600-page PDFs,
page indexing, normalized coordinates, per-annotator isolation, opaque document
ids, append-only provenance). It deliberately contains no adjudication UI beyond
a role-gated read endpoint.

Run:  python custom_poc_server.py --docs <dir with pdfs> --data <dir for jsonl> --port 8765
Only stdlib + PyMuPDF. Binds to 127.0.0.1 only (no network exposure).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import threading
import time
from collections import OrderedDict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import pymupdf

TOOL_NAME = "arpipe-custom-poc"
TOOL_VERSION = "0.0.1-POC"
PROTOCOL_VERSION = "POC-0-NOT-A-PROTOCOL"

DOCS: dict[str, dict] = {}          # opaque id -> {path, sha256, n_pages}
_CACHE: "OrderedDict[tuple, bytes]" = OrderedDict()
_LOCK = threading.Lock()
_DOC_HANDLES: dict[str, pymupdf.Document] = {}


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_docs(docs_dir: str) -> None:
    for name in sorted(os.listdir(docs_dir)):
        if not name.lower().endswith(".pdf"):
            continue
        path = os.path.join(docs_dir, name)
        digest = sha256_file(path)
        opaque = "D" + digest[:10]                 # opaque: no filename, no issuer, no year
        with pymupdf.open(path) as d:
            n = d.page_count
        DOCS[opaque] = {"path": path, "sha256": digest, "n_pages": n}


def handle(doc_id: str) -> pymupdf.Document:
    with _LOCK:
        if doc_id not in _DOC_HANDLES:
            _DOC_HANDLES[doc_id] = pymupdf.open(DOCS[doc_id]["path"])
        return _DOC_HANDLES[doc_id]


def render(doc_id: str, page: int, dpi: int) -> tuple[bytes, float, float]:
    key = (doc_id, page, dpi)
    with _LOCK:
        if key in _CACHE:
            _CACHE.move_to_end(key)
            return _CACHE[key], 0.0, 0.0
    t0 = time.perf_counter()
    d = handle(doc_id)
    with _LOCK:                                    # PyMuPDF documents are not thread-safe
        pix = d.load_page(page).get_pixmap(dpi=dpi, alpha=False)
        png = pix.tobytes("png")
    dt = time.perf_counter() - t0
    with _LOCK:
        _CACHE[key] = png
        while len(_CACHE) > 64:
            _CACHE.popitem(last=False)
    return png, dt, 0.0


def store_path(data_dir: str, annotator: str) -> str:
    if not re.fullmatch(r"A[0-9]{2}|ADJ[0-9]{2}", annotator):
        raise ValueError("annotator id must look like A01 or ADJ01 (anonymous stable id)")
    return os.path.join(data_dir, f"annotations_{annotator}.jsonl")


class Handler(BaseHTTPRequestHandler):
    server_version = "ArpipePOC/0.0"
    data_dir = "."
    static_dir = "."

    def log_message(self, *a):  # quiet
        pass

    def _send(self, code, body: bytes, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj).encode("utf-8"))

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if u.path == "/":
            with open(os.path.join(self.static_dir, "custom_poc_index.html"), "rb") as f:
                return self._send(200, f.read(), "text/html; charset=utf-8")
        if u.path == "/api/docs":
            # opaque ids only; NO filename, NO outline, NO text layer, NO metadata
            return self._json(200, [{"doc": k, "n_pages": v["n_pages"]} for k, v in DOCS.items()])
        m = re.fullmatch(r"/api/page/(D[0-9a-f]{10})/([0-9]+)\.png", u.path)
        if m:
            doc_id, page = m.group(1), int(m.group(2))
            if doc_id not in DOCS or not 0 <= page < DOCS[doc_id]["n_pages"]:
                return self._json(404, {"error": "no such page"})
            dpi = int(q.get("dpi", ["110"])[0])
            png, dt, _ = render(doc_id, page, dpi)
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(png)))
            self.send_header("X-Render-Seconds", f"{dt:.4f}")
            self.send_header("X-Image-SHA256", hashlib.sha256(png).hexdigest())
            self.send_header("X-Page-Points", "%.2f,%.2f" % tuple(handle(doc_id).load_page(page).rect[2:]))
            self.end_headers()
            self.wfile.write(png)
            return
        if u.path == "/api/mine":
            ann = q.get("annotator", [""])[0]
            try:
                p = store_path(self.data_dir, ann)
            except ValueError as e:
                return self._json(400, {"error": str(e)})
            rows = [json.loads(l) for l in open(p, encoding="utf-8")] if os.path.exists(p) else []
            return self._json(200, rows)          # an annotator only ever receives OWN records
        if u.path == "/api/compare":
            role = q.get("annotator", [""])[0]
            if not role.startswith("ADJ"):
                return self._json(403, {"error": "adjudicator role required"})
            doc = q.get("doc", [""])[0]
            out = {}
            for fn in sorted(os.listdir(self.data_dir)):
                m2 = re.fullmatch(r"annotations_(A[0-9]{2})\.jsonl", fn)
                if m2:
                    out[m2.group(1)] = [r for r in map(json.loads, open(os.path.join(self.data_dir, fn), encoding="utf-8")) if r.get("doc") == doc]
            return self._json(200, out)
        return self._json(404, {"error": "not found"})

    def do_POST(self):
        u = urlparse(self.path)
        if u.path != "/api/annotate":
            return self._json(404, {"error": "not found"})
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))) or b"{}")
        try:
            path = store_path(self.data_dir, body.get("annotator", ""))
        except ValueError as e:
            return self._json(400, {"error": str(e)})
        doc = body.get("doc")
        if doc not in DOCS:
            return self._json(404, {"error": "unknown doc"})
        # Server stamps provenance; the client cannot forge these fields.
        rec = {
            "record_type": "TOOLING_POC_ONLY",
            "gold": False,
            "doc": doc,
            "source_pdf_sha256": DOCS[doc]["sha256"],
            "annotator_id": body["annotator"],
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "tool_name": TOOL_NAME,
            "tool_version": TOOL_VERSION,
            "protocol_version": PROTOCOL_VERSION,
            "payload": body.get("payload", {}),      # e.g. {"kind":"region","page":7,"bbox_norm":[...]} or {"kind":"span",...}
        }
        with _LOCK:
            with open(path, "a", encoding="utf-8") as f:   # append-only; never rewritten
                f.write(json.dumps(rec, sort_keys=True) + "\n")
        return self._json(200, {"ok": True, "seq": sum(1 for _ in open(path, encoding="utf-8"))})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()
    os.makedirs(a.data, exist_ok=True)
    load_docs(a.docs)
    Handler.data_dir = a.data
    Handler.static_dir = os.path.dirname(os.path.abspath(__file__))
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    print(json.dumps({"listening": f"127.0.0.1:{a.port}", "docs": {k: v["n_pages"] for k, v in DOCS.items()}}), flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
