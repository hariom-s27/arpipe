"""Structured, additive, non-blocking failure telemetry for ARPipe acquisition.

Schema Version: r1-v1
Implements per-attempt failure logging to JSONL with strict secret redaction
and non-blocking best-effort persistence.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import socket
import threading
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

SCHEMA_VERSION = "r1-v1"

SENSITIVE_PARAM_NAMES = {
    "token", "access_token", "auth", "key", "apikey", "api_key",
    "secret", "signature", "sig", "session", "session_id", "sessionid",
    "password", "pass", "pwd", "credential", "creds", "bearer",
    "x-amz-signature", "x-amz-credential", "x-amz-security-token",
}

SENSITIVE_SUBSTRING_RE = re.compile(
    r"(token|auth|key|secret|sig|pass|cred|bearer|session)", re.IGNORECASE
)


def redact_url(url: str) -> tuple[str, str]:
    """Redacts sensitive query parameters from a URL and computes its SHA-256 hash.

    Rules:
      * Preserves scheme, hostname, and path.
      * Replaces values of sensitive query parameters with '[REDACTED]'.
      * Never persists tokens, API keys, credentials, or session signatures.
      * Computes SHA-256 over url_redacted.
    """
    if not url:
        return "", hashlib.sha256(b"").hexdigest()

    try:
        parts = urlsplit(url)
        if not parts.query:
            redacted_url = url
        else:
            q_pairs = parse_qsl(parts.query, keep_blank_values=True)
            new_pairs = []
            for k, v in q_pairs:
                k_lower = k.lower()
                if k_lower in SENSITIVE_PARAM_NAMES or SENSITIVE_SUBSTRING_RE.search(k_lower):
                    new_pairs.append((k, "[REDACTED]"))
                else:
                    new_pairs.append((k, v))
            new_query = urlencode(new_pairs)
            redacted_url = urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))
    except Exception:
        # Fallback safe redaction on malformed URL
        redacted_url = url.split("?")[0] if "?" in url else url

    url_sha = hashlib.sha256(redacted_url.encode("utf-8")).hexdigest()
    return redacted_url, url_sha


def classify_error(exc: Exception | None, status_code: int | None = None) -> tuple[str, str | None]:
    """Classifies an acquisition failure into error_type and first_failure_layer.

    Error Types:
      * SUCCESS
      * HTTP_FAILURE
      * NETWORK_FAILURE
      * TIMEOUT
      * RESET
      * VALIDATION_FAILURE
      * OTHER_FAILURE

    Failure Layers:
      * L0_DNS
      * L1_CONNECT
      * L2_TLS
      * L3_HTTP
      * L4_RECEIPT
      * L5_CLASSIFICATION
      * L6_VALIDATION
    """
    if status_code is not None:
        return "HTTP_FAILURE", "L3_HTTP"

    if exc is None:
        return "OTHER_FAILURE", None

    msg = str(exc).lower()
    exc_type = type(exc).__name__.lower()

    # Reset detection
    if "reset" in msg or "10054" in msg or "connectionreset" in exc_type:
        return "RESET", "L1_CONNECT"

    # Timeout detection
    if "timeout" in exc_type or "timed out" in msg:
        if "connect" in exc_type or "connect" in msg:
            return "TIMEOUT", "L1_CONNECT"
        return "TIMEOUT", "L4_RECEIPT"

    # DNS detection
    if isinstance(exc, socket.gaierror) or "getaddrinfo" in msg or "dns" in msg or "nameresolution" in exc_type:
        return "NETWORK_FAILURE", "L0_DNS"

    # TLS / SSL detection
    if "ssl" in msg or "tls" in msg or "certificate" in msg:
        return "NETWORK_FAILURE", "L2_TLS"

    # Connect / Network detection
    if "connect" in exc_type or "connect" in msg or "network" in exc_type:
        return "NETWORK_FAILURE", "L1_CONNECT"

    # Validation
    if "badzip" in exc_type or "qpdf" in msg or "validation" in msg:
        return "VALIDATION_FAILURE", "L6_VALIDATION"

    return "OTHER_FAILURE", "L4_RECEIPT"


@dataclass(slots=True)
class TelemetryRecord:
    telemetry_schema_version: str
    run_id: str
    request_sequence_id: int
    timestamp_utc: str
    company_id: str
    fy_end: int
    source: str
    url_redacted: str
    url_sha256: str
    attempt_number: int
    terminal_state: bool
    retry_exhausted: bool
    error_type: str
    status_code: int | None
    error_message: str
    exception_class: str | None = None
    first_failure_layer: str | None = None
    response_content_type: str | None = None
    bytes_received: int | None = None
    elapsed_ms: float | None = None

    def to_dict(self) -> dict:
        return asdict(self)


class TelemetryWriter:
    """Thread-safe, append-only JSONL writer for failure telemetry."""

    def __init__(self, path: str, run_id: str | None = None):
        self.path = path
        self.run_id = run_id or uuid.uuid4().hex
        self._seq = 0
        self._lock = threading.Lock()
        self.write_failures = 0
        self.last_write_error: str | None = None
        try:
            parent = os.path.dirname(os.path.abspath(path))
            if parent:
                os.makedirs(parent, exist_ok=True)
        except Exception as exc:
            self.write_failures += 1
            self.last_write_error = f"TELEMETRY_WRITE_FAILURE: {exc}"

    def next_sequence_id(self) -> int:
        with self._lock:
            self._seq += 1
            return self._seq

    def write_record(self, record: TelemetryRecord | dict) -> bool:
        """Writes one telemetry record to the JSONL file. Non-raising."""
        try:
            if isinstance(record, TelemetryRecord):
                data = record.to_dict()
            else:
                data = dict(record)
            line = json.dumps(data, ensure_ascii=False) + "\n"
            with self._lock:
                with open(self.path, "a", encoding="utf-8") as f:
                    f.write(line)
                    f.flush()
            return True
        except Exception as exc:
            self.write_failures += 1
            self.last_write_error = f"TELEMETRY_WRITE_FAILURE: {exc}"
            return False


def emit_failure_telemetry(
    sink: TelemetryWriter | None,
    *,
    company_id: str,
    fy_end: int,
    source: str,
    url: str,
    attempt_number: int,
    terminal_state: bool,
    retry_exhausted: bool,
    error_type: str,
    status_code: int | None = None,
    error_message: str = "",
    exception_class: str | None = None,
    first_failure_layer: str | None = None,
    response_content_type: str | None = None,
    bytes_received: int | None = None,
    elapsed_ms: float | None = None,
    run_id: str | None = None,
    sequence_id: int | None = None,
) -> bool:
    """Non-blocking, non-raising telemetry emission helper.

    Guarantees that telemetry failure NEVER alters or interrupts acquisition flow.
    """
    if sink is None:
        return False

    try:
        url_redacted, url_sha = redact_url(url)
        now_iso = datetime.now(timezone.utc).isoformat()
        active_run_id = run_id or getattr(sink, "run_id", "default_run")

        if sequence_id is None and hasattr(sink, "next_sequence_id"):
            seq_id = sink.next_sequence_id()
        elif sequence_id is not None:
            seq_id = sequence_id
        else:
            seq_id = 1

        record = TelemetryRecord(
            telemetry_schema_version=SCHEMA_VERSION,
            run_id=active_run_id,
            request_sequence_id=seq_id,
            timestamp_utc=now_iso,
            company_id=company_id,
            fy_end=fy_end,
            source=source,
            url_redacted=url_redacted,
            url_sha256=url_sha,
            attempt_number=attempt_number,
            terminal_state=terminal_state,
            retry_exhausted=retry_exhausted,
            error_type=error_type,
            status_code=status_code,
            error_message=str(error_message),
            exception_class=exception_class,
            first_failure_layer=first_failure_layer,
            response_content_type=response_content_type,
            bytes_received=bytes_received,
            elapsed_ms=elapsed_ms,
        )
        return sink.write_record(record)
    except Exception:
        # ABSOLUTELY NEVER RAISE INTO ACQUISITION FLOW
        return False

