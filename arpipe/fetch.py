"""Polite, resumable, content-addressed fetching.

Design points that matter at 40k-90k documents:
  * content-addressed store - the same PDF is served by NSE and BSE under
    different names; storing by sha256 means we download it twice but keep
    it once, and re-running the pipeline never re-downloads.
  * .zip handling - NSE's pre-2016 annual_reports rows are zip archives, and
    a few contain several PDFs (report + notice + subsidiary accounts). We
    keep the largest PDF and record the rest.
  * repair pass - a non-trivial minority of exchange-hosted PDFs are
    truncated or have broken xref tables. qpdf recovers most of them.
  * per-host rate limiting and a long backoff on 403/429: these are public
    regulatory archives, not a competitor's site, and the only sane posture
    is to stay well under any threshold that would get the crawl blocked.
"""
from __future__ import annotations

import hashlib
import io
import os
import shutil
import subprocess
import tempfile
import threading
import time
import zipfile
from dataclasses import dataclass, field
from urllib.parse import urlparse

import httpx
import pymupdf

from .models import ReportRef, StoredDoc
from .telemetry import TelemetryWriter, classify_error, emit_failure_telemetry


@dataclass(slots=True)
class HostLimiter:
    """One token bucket per host; default 1 request / 1.5 s."""
    min_interval: float = 1.5
    _last: dict[str, float] = field(init=False, default_factory=dict,
                                    repr=False)
    _lock: threading.Lock = field(init=False, default_factory=threading.Lock,
                                  repr=False)

    def wait(self, url: str) -> None:
        host = urlparse(url).netloc
        with self._lock:
            now = time.monotonic()
            last = self._last.get(host, 0.0)
            delay = self.min_interval - (now - last)
            self._last[host] = max(now, last + self.min_interval)
        if delay > 0:
            time.sleep(delay)


def sha256_file(path: str, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while (b := fh.read(chunk)):
            h.update(b)
    return h.hexdigest()


def cas_path(root: str, sha: str) -> str:
    return os.path.join(root, "blobs", sha[:2], sha[2:4], f"{sha}.pdf")


def _extract_pdf_from_zip(data: bytes, tmpdir: str) -> tuple[str | None, list[str]]:
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        return None, []
    pdfs = [i for i in zf.infolist()
            if i.filename.lower().endswith(".pdf") and not i.is_dir()]
    if not pdfs:
        return None, []
    pdfs.sort(key=lambda i: -i.file_size)
    main = os.path.join(tmpdir, "main.pdf")
    with open(main, "wb") as fh:
        fh.write(zf.read(pdfs[0]))
    return main, [i.filename for i in pdfs[1:]]


def _repair(path: str) -> bool:
    """qpdf can rebuild a broken xref; returns True if the file now opens."""
    if not shutil.which("qpdf"):
        return False
    out = path + ".fixed"
    try:
        subprocess.run(["qpdf", "--qdf", "--object-streams=disable", path, out],
                       check=True, capture_output=True, timeout=180)
    except Exception:
        try:
            subprocess.run(["qpdf", path, out], check=True,
                           capture_output=True, timeout=180)
        except Exception:
            return False
    try:
        d = pymupdf.open(out)
        ok = d.page_count > 0
        d.close()
    except Exception:
        ok = False
    if ok:
        os.replace(out, path)
    else:
        if os.path.exists(out):
            os.remove(out)
    return ok


def fetch_one(ref: ReportRef, root: str, client: httpx.Client,
              limiter: HostLimiter, max_bytes: int = 400 << 20,
              retries: int = 3,
              telemetry_sink: TelemetryWriter | None = None,
              run_id: str | None = None) -> StoredDoc | None:
    last_err: Exception | None = None
    for attempt in range(retries):
        attempt_num = attempt + 1
        is_last_attempt = (attempt_num >= retries)
        limiter.wait(ref.url)
        t0 = time.monotonic()
        data = b""
        bytes_recvd = 0
        ctype = None
        try:
            with client.stream("GET", ref.url, follow_redirects=True,
                               timeout=120.0) as r:
                ctype = r.headers.get("content-type")
                if r.status_code in (403, 429, 503):
                    elapsed = (time.monotonic() - t0) * 1000.0
                    emit_failure_telemetry(
                        telemetry_sink,
                        company_id=ref.company_id,
                        fy_end=ref.fy_end,
                        source=ref.source,
                        url=ref.url,
                        attempt_number=attempt_num,
                        terminal_state=is_last_attempt,
                        retry_exhausted=is_last_attempt,
                        error_type="HTTP_FAILURE",
                        status_code=r.status_code,
                        error_message=f"HTTP status {r.status_code}",
                        exception_class=None,
                        first_failure_layer="L3_HTTP",
                        response_content_type=ctype,
                        bytes_received=0,
                        elapsed_ms=elapsed,
                        run_id=run_id,
                    )
                    time.sleep(5 * (attempt + 1) ** 2)
                    continue
                r.raise_for_status()
                buf = io.BytesIO()
                for chunk in r.iter_bytes(1 << 18):
                    buf.write(chunk)
                    if buf.tell() > max_bytes:
                        raise RuntimeError(f"oversize>{max_bytes}")
                data = buf.getvalue()
                bytes_recvd = len(data)
        except Exception as exc:                        # noqa: BLE001
            elapsed = (time.monotonic() - t0) * 1000.0
            last_err = exc
            status = getattr(getattr(exc, "response", None), "status_code", None)
            err_type, layer = classify_error(exc, status)
            emit_failure_telemetry(
                telemetry_sink,
                company_id=ref.company_id,
                fy_end=ref.fy_end,
                source=ref.source,
                url=ref.url,
                attempt_number=attempt_num,
                terminal_state=is_last_attempt,
                retry_exhausted=is_last_attempt,
                error_type=err_type,
                status_code=status,
                error_message=str(exc),
                exception_class=f"{type(exc).__module__}.{type(exc).__name__}",
                first_failure_layer=layer,
                response_content_type=ctype,
                bytes_received=bytes_recvd,
                elapsed_ms=elapsed,
                run_id=run_id,
            )
            time.sleep(2 * (attempt + 1))
            continue

        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "doc.pdf")
            was_zip = False
            was_repaired = False
            was_encrypted = False
            if data[:2] == b"PK":
                was_zip = True
                got, extra = _extract_pdf_from_zip(data, td)
                if not got:
                    elapsed = (time.monotonic() - t0) * 1000.0
                    emit_failure_telemetry(
                        telemetry_sink,
                        company_id=ref.company_id,
                        fy_end=ref.fy_end,
                        source=ref.source,
                        url=ref.url,
                        attempt_number=attempt_num,
                        terminal_state=True,
                        retry_exhausted=False,
                        error_type="VALIDATION_FAILURE",
                        status_code=200,
                        error_message="BadZipFile or no PDF found inside ZIP",
                        exception_class="zipfile.BadZipFile",
                        first_failure_layer="L6_VALIDATION",
                        response_content_type=ctype,
                        bytes_received=bytes_recvd,
                        elapsed_ms=elapsed,
                        run_id=run_id,
                    )
                    return None
                path = got
                print(f"[FETCH] Extracted PDF from ZIP for {ref.company_id} FY{ref.fy_end} (extras: {len(extra)})")
            else:
                with open(path, "wb") as fh:
                    fh.write(data)

            try:
                doc = pymupdf.open(path)
                n_pages, producer = doc.page_count, doc.metadata.get("producer")
                enc = doc.is_encrypted
                if enc:
                    was_encrypted = True
                    if doc.authenticate(""):
                        enc = False
                        print(f"[FETCH] Decrypted empty-password PDF for {ref.company_id} FY{ref.fy_end}")
                    else:
                        print(f"[FETCH] Password-protected PDF authentication failed for {ref.company_id} FY{ref.fy_end}")
                doc.close()
            except Exception:
                was_repaired = True
                if not _repair(path):
                    print(f"[FETCH] qpdf repair failed for {ref.company_id} FY{ref.fy_end}")
                    elapsed = (time.monotonic() - t0) * 1000.0
                    emit_failure_telemetry(
                        telemetry_sink,
                        company_id=ref.company_id,
                        fy_end=ref.fy_end,
                        source=ref.source,
                        url=ref.url,
                        attempt_number=attempt_num,
                        terminal_state=True,
                        retry_exhausted=False,
                        error_type="VALIDATION_FAILURE",
                        status_code=200,
                        error_message="Corrupted PDF and qpdf repair failed",
                        exception_class=None,
                        first_failure_layer="L6_VALIDATION",
                        response_content_type=ctype,
                        bytes_received=bytes_recvd,
                        elapsed_ms=elapsed,
                        run_id=run_id,
                    )
                    return None
                print(f"[FETCH] Repaired PDF with qpdf for {ref.company_id} FY{ref.fy_end}")
                doc = pymupdf.open(path)
                n_pages, producer = doc.page_count, doc.metadata.get("producer")
                enc = doc.is_encrypted
                if enc:
                    was_encrypted = True
                    if doc.authenticate(""):
                        enc = False
                doc.close()

            sha = sha256_file(path)
            dest = cas_path(root, sha)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            if not os.path.exists(dest):
                shutil.move(path, dest)

            # Store the blob path RELATIVE to the store root (forward slashes) so
            # the manifest stays valid when the store is moved to another
            # directory or drive; resolve it with store.blob_abspath at read time.
            rel = os.path.relpath(dest, root).replace(os.sep, "/")
            return StoredDoc(
                company_id=ref.company_id, fy_end=ref.fy_end, sha256=sha,
                path=rel, n_bytes=len(data), n_pages=n_pages, source=ref.source,
                url=ref.url, pdf_producer=producer, is_encrypted=enc)
    if last_err:
        raise last_err
    return None
