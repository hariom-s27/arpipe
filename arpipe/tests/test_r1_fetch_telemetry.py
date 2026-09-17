"""Test suite for ARPipe R1: Acquisition Failure Telemetry-Only Repair.

Verifies:
  1. PRE-R1 vs POST-R1 behavioral equivalence across all fixtures
  2. Non-blocking telemetry emission (telemetry writer failure cannot alter acquisition)
  3. Attempt semantics, sequencing, and terminal/retry_exhausted flags
  4. Silent fall-through on 403/429/503 returning None
  5. URL and sensitive data redaction
  6. Schema conformance (r1-v1)
"""
from __future__ import annotations

import io
import json
import os
import shutil
import tempfile
import time
import zipfile
from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pymupdf
import pytest

from arpipe import fetch
from arpipe.models import ReportRef, StoredDoc
from arpipe.telemetry import (
    SCHEMA_VERSION,
    TelemetryRecord,
    TelemetryWriter,
    classify_error,
    emit_failure_telemetry,
    redact_url,
)


# ---------------------------------------------------------------------------
# Pre-R1 Baseline Implementation (exact snapshot from commit 0fb8cbf6d932f4)
# ---------------------------------------------------------------------------
def pre_r1_fetch_one(
    ref: ReportRef,
    root: str,
    client: httpx.Client,
    limiter: fetch.HostLimiter,
    max_bytes: int = 400 << 20,
    retries: int = 3,
) -> StoredDoc | None:
    """Verbatim uninstrumented fetch_one baseline."""
    last_err: Exception | None = None
    for attempt in range(retries):
        limiter.wait(ref.url)
        try:
            with client.stream("GET", ref.url, follow_redirects=True, timeout=120.0) as r:
                if r.status_code in (403, 429, 503):
                    time.sleep(5 * (attempt + 1) ** 2)
                    continue
                r.raise_for_status()
                buf = io.BytesIO()
                for chunk in r.iter_bytes(1 << 18):
                    buf.write(chunk)
                    if buf.tell() > max_bytes:
                        raise RuntimeError(f"oversize>{max_bytes}")
                data = buf.getvalue()
                ctype = r.headers.get("content-type", "")
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            time.sleep(2 * (attempt + 1))
            continue

        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "doc.pdf")
            was_zip = False
            was_repaired = False
            was_encrypted = False
            if data[:2] == b"PK":
                was_zip = True
                got, extra = fetch._extract_pdf_from_zip(data, td)
                if not got:
                    return None
                path = got
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
                doc.close()
            except Exception:
                was_repaired = True
                if not fetch._repair(path):
                    return None
                doc = pymupdf.open(path)
                n_pages, producer = doc.page_count, doc.metadata.get("producer")
                enc = doc.is_encrypted
                if enc:
                    was_encrypted = True
                    if doc.authenticate(""):
                        enc = False
                doc.close()

            sha = fetch.sha256_file(path)
            dest = fetch.cas_path(root, sha)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            if not os.path.exists(dest):
                shutil.move(path, dest)

            rel = os.path.relpath(dest, root).replace(os.sep, "/")
            return StoredDoc(
                company_id=ref.company_id,
                fy_end=ref.fy_end,
                sha256=sha,
                path=rel,
                n_bytes=len(data),
                n_pages=n_pages,
                source=ref.source,
                url=ref.url,
                pdf_producer=producer,
                is_encrypted=enc,
            )
    if last_err:
        raise last_err
    return None


# ---------------------------------------------------------------------------
# Fixture Helpers
# ---------------------------------------------------------------------------
def _create_minimal_pdf_bytes() -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 72), "Minimal PDF content for R1 testing")
    data = doc.tobytes()
    doc.close()
    return data


STATIC_PDF_BYTES = _create_minimal_pdf_bytes()


def _create_minimal_zip_bytes(pdf_bytes: bytes) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("annual_report.pdf", pdf_bytes)
    return buf.getvalue()


STATIC_ZIP_BYTES = _create_minimal_zip_bytes(STATIC_PDF_BYTES)


class MockRecordingTransport(httpx.BaseTransport):
    """Deterministic mock transport that tracks request counts and returns pre-configured responses."""

    def __init__(self, handler):
        super().__init__()
        self.handler = handler
        self.requests: list[httpx.Request] = []

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return self.handler(request, len(self.requests))


@pytest.fixture
def fast_limiter(monkeypatch):
    """Replaces time.sleep and limiter delay with zero-wait mocks while tracking calls."""
    sleep_calls = []

    def fake_sleep(d):
        sleep_calls.append(d)

    monkeypatch.setattr(time, "sleep", fake_sleep)
    limiter = fetch.HostLimiter(min_interval=0.0)
    return limiter, sleep_calls


@pytest.fixture
def sample_ref():
    return ReportRef(
        company_id="INE002A01018",
        fy_end=2024,
        source="nse",
        url="https://nsearchives.nseindia.com/annual_reports/AR_RELIANCE_2023_2024.pdf",
    )


# ---------------------------------------------------------------------------
# 1. URL Redaction and Secret Masking Tests
# ---------------------------------------------------------------------------
def test_url_redaction_rules():
    # 1. Non-sensitive URL is preserved
    u1 = "https://nsearchives.nseindia.com/annual_reports/AR_123.pdf"
    redacted1, sha1 = redact_url(u1)
    assert redacted1 == u1
    assert len(sha1) == 64

    # 2. Sensitive query parameters are redacted
    u2 = "https://example.com/download.pdf?token=secret123&company=ABC&api_key=xyz987&session_id=sess456"
    redacted2, sha2 = redact_url(u2)
    assert "token=%5BREDACTED%5D" in redacted2 or "token=[REDACTED]" in redacted2
    assert "api_key=%5BREDACTED%5D" in redacted2 or "api_key=[REDACTED]" in redacted2
    assert "session_id=%5BREDACTED%5D" in redacted2 or "session_id=[REDACTED]" in redacted2
    assert "company=ABC" in redacted2
    assert "secret123" not in redacted2
    assert "xyz987" not in redacted2
    assert len(sha2) == 64

    # 3. AWS style query parameters
    u3 = "https://s3.amazonaws.com/bucket/report.pdf?X-Amz-Signature=abcd1234efgh&response-content-type=pdf"
    redacted3, sha3 = redact_url(u3)
    assert "abcd1234efgh" not in redacted3
    assert "%5BREDACTED%5D" in redacted3 or "[REDACTED]" in redacted3


# ---------------------------------------------------------------------------
# 2. Error Classifier Tests
# ---------------------------------------------------------------------------
def test_error_classifier():
    assert classify_error(None, 403) == ("HTTP_FAILURE", "L3_HTTP")
    assert classify_error(None, 429) == ("HTTP_FAILURE", "L3_HTTP")
    assert classify_error(None, 503) == ("HTTP_FAILURE", "L3_HTTP")

    assert classify_error(httpx.ConnectTimeout("Connect timed out")) == ("TIMEOUT", "L1_CONNECT")
    assert classify_error(httpx.ReadTimeout("Read timed out")) == ("TIMEOUT", "L4_RECEIPT")
    assert classify_error(ConnectionResetError("Connection reset by peer")) == ("RESET", "L1_CONNECT")
    assert classify_error(httpx.ConnectError("Connection refused")) == ("NETWORK_FAILURE", "L1_CONNECT")
    assert classify_error(zipfile.BadZipFile("File is not a zip file")) == ("VALIDATION_FAILURE", "L6_VALIDATION")


# ---------------------------------------------------------------------------
# 3. Matrix Equivalence Suite (PRE-R1 vs POST-R1 side-by-side)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "case_name, handler_factory, expected_outcome_type",
    [
        (
            "200 PDF",
            lambda: lambda req, count: httpx.Response(
                200,
                headers={"Content-Type": "application/pdf"},
                content=STATIC_PDF_BYTES,
            ),
            "STORED_DOC",
        ),
        (
            "200 ZIP",
            lambda: lambda req, count: httpx.Response(
                200,
                headers={"Content-Type": "application/zip"},
                content=STATIC_ZIP_BYTES,
            ),
            "STORED_DOC",
        ),
        (
            "403 Forbidden",
            lambda: lambda req, count: httpx.Response(403, text="Forbidden"),
            "NONE_RETURN",
        ),
        (
            "429 Too Many Requests",
            lambda: lambda req, count: httpx.Response(429, text="Rate limit exceeded"),
            "NONE_RETURN",
        ),
        (
            "503 Service Unavailable",
            lambda: lambda req, count: httpx.Response(503, text="Service Unavailable"),
            "NONE_RETURN",
        ),
        (
            "Timeout",
            lambda: lambda req, count: (_ for _ in ()).throw(httpx.ReadTimeout("Socket timed out")),
            "RAISE_TIMEOUT",
        ),
        (
            "Connection Error",
            lambda: lambda req, count: (_ for _ in ()).throw(httpx.ConnectError("Failed to connect")),
            "RAISE_CONNECT_ERROR",
        ),
        (
            "Malformed Response (Bad Zip)",
            lambda: lambda req, count: httpx.Response(
                200,
                headers={"Content-Type": "application/zip"},
                content=b"PK\x03\x04corrupted_broken_payload",
            ),
            "NONE_RETURN",
        ),
        (
            "Malformed Response (Corrupt PDF)",
            lambda: lambda req, count: httpx.Response(
                200,
                headers={"Content-Type": "application/pdf"},
                content=b"%PDF-1.4\ncorrupted_garbage_bytes",
            ),
            "NONE_RETURN",
        ),
    ],
)
def test_pre_vs_post_r1_matrix_equivalence(
    case_name, handler_factory, expected_outcome_type, fast_limiter, sample_ref
):
    limiter, _ = fast_limiter

    with tempfile.TemporaryDirectory() as root_pre, tempfile.TemporaryDirectory() as root_post:
        # A. PRE-R1 Baseline
        t_pre = MockRecordingTransport(handler_factory())
        c_pre = httpx.Client(transport=t_pre)
        pre_result = None
        pre_exc = None
        try:
            pre_result = pre_r1_fetch_one(sample_ref, root_pre, c_pre, limiter, retries=3)
        except Exception as exc:
            pre_exc = exc

        # B. POST-R1 Instrumented
        telemetry_file = os.path.join(root_post, "telemetry.jsonl")
        sink = TelemetryWriter(telemetry_file, run_id="test_run_1")
        t_post = MockRecordingTransport(handler_factory())
        c_post = httpx.Client(transport=t_post)
        post_result = None
        post_exc = None
        try:
            post_result = fetch.fetch_one(
                sample_ref, root_post, c_post, limiter, retries=3, telemetry_sink=sink
            )
        except Exception as exc:
            post_exc = exc

        # --- BEHAVIORAL EQUIVALENCE ASSERTIONS ---
        # 1. Request counts must match exactly
        assert len(t_post.requests) == len(t_pre.requests), f"Request count mismatch in {case_name}"

        # 2. Return values must match exactly
        if expected_outcome_type == "STORED_DOC":
            assert pre_result is not None
            assert post_result is not None
            assert pre_result.sha256 == post_result.sha256
            assert pre_result.n_bytes == post_result.n_bytes
            assert pre_result.n_pages == post_result.n_pages
            assert pre_result.company_id == post_result.company_id
            assert pre_result.fy_end == post_result.fy_end
        elif expected_outcome_type == "NONE_RETURN":
            assert pre_result is None
            assert post_result is None
            assert pre_exc is None
            assert post_exc is None
        elif expected_outcome_type.startswith("RAISE"):
            assert pre_exc is not None
            assert post_exc is not None
            assert type(pre_exc) is type(post_exc)
            assert str(pre_exc) == str(post_exc)

        # 3. Telemetry Verification
        if expected_outcome_type == "STORED_DOC":
            # Successes emit NO failure telemetry records
            records = []
            if os.path.exists(telemetry_file):
                records = [json.loads(line) for line in open(telemetry_file, encoding="utf-8")]
            assert len(records) == 0, f"Expected 0 failure records for successful {case_name}, got {len(records)}"
        else:
            assert os.path.exists(telemetry_file)
            records = [json.loads(line) for line in open(telemetry_file, encoding="utf-8")]
            # Number of failure records must match actual attempt count
            assert len(records) == len(t_post.requests)
            for idx, rec in enumerate(records):
                att_num = idx + 1
                assert rec["telemetry_schema_version"] == SCHEMA_VERSION
                assert rec["run_id"] == "test_run_1"
                assert rec["attempt_number"] == att_num
                assert rec["company_id"] == sample_ref.company_id
                assert rec["fy_end"] == sample_ref.fy_end

                is_last = att_num == len(records)
                if expected_outcome_type == "NONE_RETURN" and case_name.startswith("Malformed"):
                    # Malformed payload fails validation on first attempt and exits immediately
                    assert rec["terminal_state"] is True
                    assert rec["error_type"] == "VALIDATION_FAILURE"
                    assert rec["status_code"] == 200
                else:
                    assert rec["terminal_state"] == is_last
                    assert rec["retry_exhausted"] == is_last


# ---------------------------------------------------------------------------
# 4. Mandatory Part 9 Test: Telemetry-Writer Failure Test
# ---------------------------------------------------------------------------
class FailingTelemetryWriter(TelemetryWriter):
    """Mock writer that intentionally raises an exception during write_record."""

    def __init__(self, exc_to_raise: Exception):
        super().__init__("dummy_path.jsonl")
        self.exc_to_raise = exc_to_raise

    def write_record(self, record: Any) -> bool:
        raise self.exc_to_raise


@pytest.mark.parametrize(
    "writer_exc",
    [
        PermissionError("Simulated permission denied on telemetry path"),
        OSError(28, "No space left on device"),
        RuntimeError("Unexpected serialization engine failure"),
    ],
)
def test_telemetry_writer_failure_cannot_affect_acquisition(
    writer_exc, fast_limiter, sample_ref
):
    limiter, _ = fast_limiter

    # 1. Verify 200 PDF path under failing writer
    pdf_transport = MockRecordingTransport(
        lambda req, count: httpx.Response(200, content=_create_minimal_pdf_bytes())
    )
    with tempfile.TemporaryDirectory() as root:
        failing_sink = FailingTelemetryWriter(writer_exc)
        client = httpx.Client(transport=pdf_transport)
        doc = fetch.fetch_one(sample_ref, root, client, limiter, telemetry_sink=failing_sink)
        assert doc is not None
        assert doc.company_id == sample_ref.company_id
        assert len(pdf_transport.requests) == 1

    # 2. Verify 403 path under failing writer
    http_fail_transport = MockRecordingTransport(
        lambda req, count: httpx.Response(403, text="Forbidden")
    )
    with tempfile.TemporaryDirectory() as root:
        failing_sink = FailingTelemetryWriter(writer_exc)
        client = httpx.Client(transport=http_fail_transport)
        doc = fetch.fetch_one(sample_ref, root, client, limiter, retries=3, telemetry_sink=failing_sink)
        assert doc is None  # EXACT same silent fall-through return None
        assert len(http_fail_transport.requests) == 3

    # 3. Verify Timeout exception path under failing writer
    timeout_transport = MockRecordingTransport(
        lambda req, count: (_ for _ in ()).throw(httpx.ConnectTimeout("Connect timed out"))
    )
    with tempfile.TemporaryDirectory() as root:
        failing_sink = FailingTelemetryWriter(writer_exc)
        client = httpx.Client(transport=timeout_transport)
        with pytest.raises(httpx.ConnectTimeout):
            fetch.fetch_one(sample_ref, root, client, limiter, retries=3, telemetry_sink=failing_sink)
        assert len(timeout_transport.requests) == 3


# ---------------------------------------------------------------------------
# 5. Retry Sequence and Fall-Through Details (Parts 7, 8, 12)
# ---------------------------------------------------------------------------
def test_retry_sequence_and_fallthrough_details(fast_limiter, sample_ref):
    limiter, sleeps = fast_limiter

    transport = MockRecordingTransport(
        lambda req, count: httpx.Response(503, text="Unavailable")
    )
    with tempfile.TemporaryDirectory() as root:
        telemetry_file = os.path.join(root, "telemetry_503.jsonl")
        sink = TelemetryWriter(telemetry_file, run_id="seq_run")
        client = httpx.Client(transport=transport)

        result = fetch.fetch_one(sample_ref, root, client, limiter, retries=3, telemetry_sink=sink)

        # Operational result remains silent None
        assert result is None
        assert len(transport.requests) == 3

        # Sleeps must follow 5 * (attempt + 1)^2: 5, 20, 45
        assert sleeps == [5 * 1**2, 5 * 2**2, 5 * 3**2]

        records = [json.loads(line) for line in open(telemetry_file, encoding="utf-8")]
        assert len(records) == 3

        # Attempt 1
        assert records[0]["attempt_number"] == 1
        assert records[0]["terminal_state"] is False
        assert records[0]["retry_exhausted"] is False
        assert records[0]["status_code"] == 503
        assert records[0]["error_type"] == "HTTP_FAILURE"

        # Attempt 2
        assert records[1]["attempt_number"] == 2
        assert records[1]["terminal_state"] is False
        assert records[1]["retry_exhausted"] is False
        assert records[1]["status_code"] == 503
        assert records[1]["error_type"] == "HTTP_FAILURE"

        # Attempt 3
        assert records[2]["attempt_number"] == 3
        assert records[2]["terminal_state"] is True
        assert records[2]["retry_exhausted"] is True
        assert records[2]["status_code"] == 503
        assert records[2]["error_type"] == "HTTP_FAILURE"
