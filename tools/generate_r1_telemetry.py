"""Generates sample/verification telemetry logs for R1 in reports/r1_telemetry/."""
from __future__ import annotations

import io
import json
import os
import sys
import time
import zipfile

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import httpx
import pymupdf

from arpipe import fetch
from arpipe.models import ReportRef
from arpipe.telemetry import TelemetryWriter


def make_pdf():
    doc = pymupdf.open()
    p = doc.new_page()
    p.insert_text((50, 72), "R1 Authoritative Validation PDF")
    b = doc.tobytes()
    doc.close()
    return b


def make_zip(pdf_bytes):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("report.pdf", pdf_bytes)
    return buf.getvalue()


class MockRecordingTransport(httpx.BaseTransport):
    def __init__(self, handler):
        super().__init__()
        self.handler = handler
        self.requests = []

    def handle_request(self, req: httpx.Request) -> httpx.Response:
        self.requests.append(req)
        return self.handler(req, len(self.requests))


def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(root_dir, "reports", "r1_telemetry")
    os.makedirs(out_dir, exist_ok=True)
    telemetry_path = os.path.join(out_dir, "r1_matrix_telemetry.jsonl")

    # Clear old run if present
    if os.path.exists(telemetry_path):
        os.remove(telemetry_path)

    writer = TelemetryWriter(telemetry_path, run_id="r1_authoritative_run")

    # Fast limiter for generation
    original_sleep = time.sleep
    time.sleep = lambda d: None
    limiter = fetch.HostLimiter(min_interval=0.0)

    pdf_bytes = make_pdf()
    zip_bytes = make_zip(pdf_bytes)

    cases = [
        ("200_PDF", lambda r, c: httpx.Response(200, headers={"Content-Type": "application/pdf"}, content=pdf_bytes), "INE002A01018", 2024, "https://nsearchives.nseindia.com/annual_reports/AR_RELIANCE_2024.pdf"),
        ("200_ZIP", lambda r, c: httpx.Response(200, headers={"Content-Type": "application/zip"}, content=zip_bytes), "INE009A01021", 2023, "https://nsearchives.nseindia.com/annual_reports/AR_INFY_2023.zip"),
        ("403_FORBIDDEN", lambda r, c: httpx.Response(403, text="Forbidden"), "INE040A01034", 2014, "https://nsearchives.nseindia.com/annual_reports/AR_HDFCBANK_2014.zip"),
        ("429_TOO_MANY_REQUESTS", lambda r, c: httpx.Response(429, text="Rate limit exceeded"), "INE081A01020", 2016, "https://nsearchives.nseindia.com/annual_reports/AR_TATASTEEL_2016.zip"),
        ("503_SERVICE_UNAVAILABLE", lambda r, c: httpx.Response(503, text="Service Unavailable"), "INE171A01029", 2021, "https://nsearchives.nseindia.com/annual_reports/AR_FEDERALBNK_2021.zip"),
        ("TIMEOUT", lambda r, c: (_ for _ in ()).throw(httpx.ReadTimeout("Socket timed out after 120s")), "INE226A01021", 2022, "https://nsearchives.nseindia.com/annual_reports/AR_VOLTAS_2022.zip"),
        ("CONNECTION_ERROR", lambda r, c: (_ for _ in ()).throw(httpx.ConnectError("Connection refused by target host")), "INE044A01036", 2018, "https://nsearchives.nseindia.com/annual_reports/AR_SUNPHARMA_2018.zip"),
        ("MALFORMED_ZIP", lambda r, c: httpx.Response(200, headers={"Content-Type": "application/zip"}, content=b"PK\x03\x04broken_bytes"), "INE002A01018", 2010, "https://nsearchives.nseindia.com/annual_reports/AR_RELIANCE_2010.zip"),
        ("MALFORMED_PDF", lambda r, c: httpx.Response(200, headers={"Content-Type": "application/pdf"}, content=b"%PDF-1.4\ncorrupted_xref"), "INE040A01034", 2017, "https://nsearchives.nseindia.com/annual_reports/AR_HDFCBANK_2017.pdf"),
    ]

    import tempfile
    store_dir = os.path.join(out_dir, "scratch_store")
    os.makedirs(store_dir, exist_ok=True)

    summary = []

    for name, handler, cid, fy, url in cases:
        ref = ReportRef(company_id=cid, fy_end=fy, source="nse", url=url)
        transport = MockRecordingTransport(handler)
        cl = httpx.Client(transport=transport)
        ret_val = None
        exc_str = None
        t_start = time.monotonic()
        try:
            doc = fetch.fetch_one(ref, store_dir, cl, limiter, retries=3, telemetry_sink=writer)
            ret_val = "StoredDoc" if doc is not None else "None"
        except Exception as exc:
            exc_str = f"{type(exc).__name__}: {exc}"

        summary.append({
            "fixture": name,
            "company_id": cid,
            "fy_end": fy,
            "requests": len(transport.requests),
            "return_value": ret_val,
            "exception": exc_str,
        })

    time.sleep = original_sleep

    # Read generated records
    with open(telemetry_path, encoding="utf-8") as f:
        records = [json.loads(line) for line in f]

    print(f"Generated {len(records)} telemetry records across {len(cases)} matrix cases.")
    with open(os.path.join(out_dir, "r1_generation_summary.json"), "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "total_records": len(records), "records": records}, f, indent=2)

    return 0


if __name__ == "__main__":
    sys.exit(main())
