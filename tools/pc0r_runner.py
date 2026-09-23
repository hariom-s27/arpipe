"""P-C0R: Instrumented Acquisition Resolution Pilot runner.

DIAGNOSTIC / EXPERIMENT ONLY.
Does not modify production code, manifest, or P-M5 stage membership.
"""
from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import io
import json
import os
import re
import socket
import ssl
import subprocess
import sys
import tempfile
import time
import zipfile
from urllib.parse import urlparse

import httpx

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36")

NSE_HOME = "https://www.nseindia.com"
NSE_HEADERS = {
    "User-Agent": UA,
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": NSE_HOME + "/companies-listing/corporate-filings-annual-reports",
}

SAFE_HEADERS_WHITELIST = {
    "date", "server", "content-type", "content-length", "via", "age",
    "retry-after", "akamai-grn", "cache-control", "etag", "expires",
    "last-modified", "connection", "accept-ranges"
}

FORBIDDEN_HEADERS = {
    "authorization", "cookie", "set-cookie", "api-key", "token", "sec-ch-ua"
}


def sanitize_text(text: str, limit: int = 200) -> str:
    cleaned = re.sub(r"<[^>]+>", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:limit]


def validate_pdf_bytes(pdf_bytes: bytes) -> tuple[bool, str]:
    """Validate PDF bytes using qpdf --check."""
    if not pdf_bytes.startswith(b"%PDF"):
        return False, "missing_%PDF_magic"
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tf:
        tf.write(pdf_bytes)
        tpath = tf.name
    try:
        res = subprocess.run(["qpdf", "--check", tpath],
                             capture_output=True, text=True, timeout=30)
        # exit code 0 = ok, 3 = warnings but openable
        if res.returncode in (0, 3):
            return True, "valid_pdf"
        return False, f"qpdf_check_failed_code_{res.returncode}"
    except Exception as exc:
        return False, f"qpdf_exc_{type(exc).__name__}"
    finally:
        if os.path.exists(tpath):
            os.remove(tpath)


def validate_zip_bytes(zip_bytes: bytes) -> tuple[bool, str, int]:
    """Validate ZIP archive, extract main PDF, validate PDF."""
    if not zip_bytes.startswith(b"PK\x03\x04"):
        return False, "missing_PK_magic", 0
    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except Exception as exc:
        return False, f"bad_zip_{type(exc).__name__}", 0

    pdfs = [i for i in zf.infolist() if i.filename.lower().endswith(".pdf") and not i.is_dir()]
    if not pdfs:
        return False, "no_pdf_in_zip", 0
    pdfs.sort(key=lambda i: -i.file_size)
    main_bytes = zf.read(pdfs[0])
    ok, reason = validate_pdf_bytes(main_bytes)
    return ok, f"zip_with_pdf:{reason}", len(pdfs)


def probe_network_layers(url: str) -> tuple[str | None, str | None, dict]:
    """L0-L2 pre-flight connectivity check to identify DNS, TCP, or TLS failure layer."""
    parsed = urlparse(url)
    host = parsed.hostname
    port = parsed.port or 443
    telemetry = {"host": host, "port": port}

    # L0: DNS resolution
    try:
        addr_info = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
        telemetry["resolved_ip"] = addr_info[0][4][0]
    except socket.gaierror as exc:
        telemetry["dns_error"] = str(exc)
        return "DNS_FAILURE", "CONNECTION_ERROR", telemetry
    except Exception as exc:
        telemetry["dns_error"] = str(exc)
        return "DNS_FAILURE", "OTHER_ERROR", telemetry

    target_ip = telemetry["resolved_ip"]

    # L1: TCP connect
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(15.0)
    try:
        s.connect((target_ip, port))
    except TimeoutError:
        s.close()
        telemetry["connect_error"] = "TimeoutError"
        return "CONNECT_FAILURE", "TIMEOUT", telemetry
    except (ConnectionRefusedError, ConnectionResetError) as exc:
        s.close()
        telemetry["connect_error"] = str(exc)
        return "CONNECT_FAILURE", "RESET", telemetry
    except Exception as exc:
        s.close()
        telemetry["connect_error"] = str(exc)
        return "CONNECT_FAILURE", "CONNECTION_ERROR", telemetry

    # L2: TLS Handshake
    try:
        ctx = ssl.create_default_context()
        tls_sock = ctx.wrap_socket(s, server_hostname=host)
        telemetry["tls_version"] = tls_sock.version()
        tls_sock.close()
    except ssl.SSLError as exc:
        s.close()
        telemetry["tls_error"] = str(exc)
        return "TLS_FAILURE", "CONNECTION_ERROR", telemetry
    except Exception as exc:
        s.close()
        telemetry["tls_error"] = str(exc)
        return "TLS_FAILURE", "OTHER_ERROR", telemetry

    return None, None, telemetry


def create_client(arm: str, timeout: float = 120.0) -> httpx.Client:
    timeout_cfg = httpx.Timeout(timeout, connect=30.0, read=timeout, write=30.0, pool=30.0)
    if arm == "ARM_A":
        cl = httpx.Client(headers=NSE_HEADERS, timeout=timeout_cfg, follow_redirects=True)
        # Seed cookies via 2 GETs to NSE
        try:
            cl.get(NSE_HOME)
            cl.get(NSE_HOME + "/companies-listing/corporate-filings-annual-reports")
        except Exception:
            pass
        return cl
    else:  # ARM_B
        return httpx.Client(headers={"User-Agent": UA}, timeout=timeout_cfg, follow_redirects=True)


def execute_probe(obs: dict, arm: str, scheduled_time: str, attempt_id: str, client: httpx.Client | None = None) -> dict:
    url = obs["exact_url"]
    start_utc = datetime.datetime.now(datetime.timezone.utc)
    res = {
        "observation_id": obs["observation_id"],
        "company_id": obs["company_id"],
        "fy": obs["FY"],
        "group": obs["group"],
        "exact_url": url,
        "arm": arm,
        "attempt_id": attempt_id,
        "scheduled_time": scheduled_time,
        "actual_start_time": start_utc.isoformat(),
        "actual_end_time": None,
        "state_machine": "DISCOVERY_ONLY",
        "first_failure_layer": "NONE",
        "terminal_state": "OTHER_ERROR",
        "result": "FAILED",
        "http_status": None,
        "content_type": None,
        "content_length_header": None,
        "bytes_received": 0,
        "magic_prefix_hex": None,
        "body_500_sha256": None,
        "redirect_chain": [],
        "safe_headers": {},
        "exception_class": None,
        "exception_message": None,
        "validation_detail": None,
        "sanitized_body_preview": None,
        "telemetry": {}
    }

    res["state_machine"] = "FETCH_STARTED"

    # L0-L2 pre-check
    fail_layer, term_state, l_telem = probe_network_layers(url)
    res["telemetry"].update(l_telem)
    if fail_layer:
        res["first_failure_layer"] = fail_layer
        res["terminal_state"] = term_state
        res["state_machine"] = "DOWNLOAD_FAILED"
        res["result"] = "FAILED"
        res["actual_end_time"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return res

    own_client = False
    if client is None:
        client = create_client(arm)
        own_client = True

    try:
        with client.stream("GET", url) as resp:
            res["state_machine"] = "RESPONSE_RECEIVED"
            res["http_status"] = resp.status_code
            res["redirect_chain"] = [str(r.url) for r in resp.history] + [str(resp.url)]

            # Capture safe diagnostic headers
            for k, v in resp.headers.items():
                k_lower = k.lower()
                if k_lower in SAFE_HEADERS_WHITELIST:
                    res["safe_headers"][k] = v

            res["content_type"] = resp.headers.get("content-type", "")
            res["content_length_header"] = resp.headers.get("content-length")

            if resp.status_code >= 400:
                res["first_failure_layer"] = "HTTP_ERROR"
                res["terminal_state"] = "HTTP_ERROR"
                res["state_machine"] = "DOWNLOAD_FAILED"
                res["result"] = "FAILED"
                body_chunk = resp.read()
                res["bytes_received"] = len(body_chunk)
                if body_chunk:
                    res["body_500_sha256"] = hashlib.sha256(body_chunk[:500]).hexdigest()
                    res["magic_prefix_hex"] = body_chunk[:4].hex()
                    try:
                        decoded = body_chunk.decode("utf-8", errors="replace")
                        res["sanitized_body_preview"] = sanitize_text(decoded, 200)
                    except Exception:
                        pass
                res["actual_end_time"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                return res

            # L4: Artifact receipt
            buf = io.BytesIO()
            for chunk in resp.iter_bytes(1 << 18):
                buf.write(chunk)
                if buf.tell() > (400 << 20):
                    raise RuntimeError("oversize_artifact_exceeds_400mb")

            data = buf.getvalue()
            res["bytes_received"] = len(data)
            res["state_machine"] = "ARTIFACT_RECEIVED"
            res["body_500_sha256"] = hashlib.sha256(data[:500]).hexdigest()
            res["magic_prefix_hex"] = data[:4].hex()

    except httpx.ConnectTimeout as exc:
        res["first_failure_layer"] = "CONNECT_FAILURE"
        res["terminal_state"] = "TIMEOUT"
        res["state_machine"] = "DOWNLOAD_FAILED"
        res["exception_class"] = type(exc).__name__
        res["exception_message"] = str(exc)
        res["actual_end_time"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return res
    except (httpx.ReadTimeout, httpx.WriteTimeout, httpx.PoolTimeout) as exc:
        res["first_failure_layer"] = "ARTIFACT_TRUNCATED" if res["state_machine"] == "RESPONSE_RECEIVED" else "CONNECT_FAILURE"
        res["terminal_state"] = "TIMEOUT"
        res["state_machine"] = "DOWNLOAD_FAILED"
        res["exception_class"] = type(exc).__name__
        res["exception_message"] = str(exc)
        res["actual_end_time"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return res
    except httpx.ConnectError as exc:
        res["first_failure_layer"] = "CONNECT_FAILURE"
        res["terminal_state"] = "RESET" if "10054" in str(exc) or "reset" in str(exc).lower() else "CONNECTION_ERROR"
        res["state_machine"] = "DOWNLOAD_FAILED"
        res["exception_class"] = type(exc).__name__
        res["exception_message"] = str(exc)
        res["actual_end_time"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return res
    except httpx.TooManyRedirects as exc:
        res["first_failure_layer"] = "REDIRECT_FAILURE"
        res["terminal_state"] = "REDIRECT_FAILURE"
        res["state_machine"] = "DOWNLOAD_FAILED"
        res["exception_class"] = type(exc).__name__
        res["exception_message"] = str(exc)
        res["actual_end_time"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return res
    except Exception as exc:
        res["first_failure_layer"] = "OTHER_ERROR"
        res["terminal_state"] = "OTHER_ERROR"
        res["state_machine"] = "DOWNLOAD_FAILED"
        res["exception_class"] = type(exc).__name__
        res["exception_message"] = str(exc)
        res["actual_end_time"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return res
    finally:
        if own_client:
            client.close()

    # L5: Artifact Classification
    magic = data[:4]
    is_zip = magic == b"PK\x03\x04"
    is_pdf = magic.startswith(b"%PDF")

    if not (is_zip or is_pdf):
        res["first_failure_layer"] = "CONTENT_TYPE_MISMATCH"
        res["terminal_state"] = "UNEXPECTED_CONTENT"
        res["state_machine"] = "DOWNLOAD_FAILED"
        res["actual_end_time"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return res

    # L6: Artifact Validation
    if is_zip:
        ok, val_detail, n_extras = validate_zip_bytes(data)
        res["validation_detail"] = f"{val_detail} (pdfs_in_zip={n_extras})"
        if ok:
            res["state_machine"] = "DOWNLOAD_SUCCESS"
            res["first_failure_layer"] = "NONE"
            res["terminal_state"] = "SUCCESS_ZIP"
            res["result"] = "SUCCESS"
        else:
            res["state_machine"] = "DOWNLOAD_FAILED"
            res["first_failure_layer"] = "VALIDATION_FAILURE"
            res["terminal_state"] = "VALIDATION_FAILURE"
            res["result"] = "FAILED"
    else:
        ok, val_detail = validate_pdf_bytes(data)
        res["validation_detail"] = val_detail
        if ok:
            res["state_machine"] = "DOWNLOAD_SUCCESS"
            res["first_failure_layer"] = "NONE"
            res["terminal_state"] = "SUCCESS_PDF"
            res["result"] = "SUCCESS"
        else:
            res["state_machine"] = "DOWNLOAD_FAILED"
            res["first_failure_layer"] = "VALIDATION_FAILURE"
            res["terminal_state"] = "VALIDATION_FAILURE"
            res["result"] = "FAILED"

    res["actual_end_time"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return res


def append_attempt_csv(path: str, records: list[dict], overwrite: bool = False):
    file_exists = os.path.exists(path) and os.path.getsize(path) > 0 and not overwrite
    fieldnames = [
        "observation_id", "company_id", "fy", "group", "exact_url", "arm",
        "attempt_id", "scheduled_time", "actual_start_time", "actual_end_time",
        "result", "first_failure_layer", "terminal_state", "state_machine",
        "http_status", "content_type", "content_length_header", "bytes_received",
        "magic_prefix_hex", "body_500_sha256", "exception_class", "exception_message",
        "validation_detail"
    ]
    mode = "w" if overwrite else "a"
    with open(path, mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        for r in records:
            writer.writerow(r)


def append_comparison_csv(path: str, records: list[dict]):
    file_exists = os.path.exists(path) and os.path.getsize(path) > 0
    fieldnames = [
        "observation_id", "company_id", "fy", "group", "exact_url", "arm_order",
        "scheduled_time", "time_between_seconds",
        "arm_a_result", "arm_a_status", "arm_a_bytes", "arm_a_terminal_state", "arm_a_fail_layer",
        "arm_b_result", "arm_b_status", "arm_b_bytes", "arm_b_terminal_state", "arm_b_fail_layer",
        "outcome_classification"
    ]
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        for r in records:
            writer.writerow(r)


def main():
    parser = argparse.ArgumentParser(description="P-C0R Diagnostic Runner")
    parser.add_argument("--mode", choices=["attempt", "comparison"], required=True)
    parser.add_argument("--attempt-id", default="attempt_1")
    parser.add_argument("--scheduled-time", required=True)
    parser.add_argument("--wait-until-scheduled", action="store_true", help="Wait until scheduled-time if currently in the future")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite log file instead of appending")
    parser.add_argument("--sample-manifest", default="reports/pc0r_sample_manifest.json")
    parser.add_argument("--attempt-log", default="reports/pc0r_attempt_log.csv")
    parser.add_argument("--comparison-log", default="reports/pc0r_client_comparison.csv")
    args = parser.parse_args()

    with open(args.sample_manifest, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    observations = manifest["observations"]

    if args.wait_until_scheduled:
        try:
            sched_dt = datetime.datetime.fromisoformat(args.scheduled_time.replace("Z", "+00:00"))
            now_dt = datetime.datetime.now(datetime.timezone.utc)
            wait_sec = (sched_dt - now_dt).total_seconds()
            if wait_sec > 0:
                print(f"Waiting {wait_sec:.1f}s until scheduled time {args.scheduled_time}...", flush=True)
                time.sleep(wait_sec)
        except Exception as e:
            print(f"Warning: could not parse scheduled_time for waiting: {e}", flush=True)

    if args.mode == "attempt":
        print(f"[{datetime.datetime.now(datetime.timezone.utc).isoformat()}] Starting {args.attempt_id} scheduled for {args.scheduled_time}...")
        records = []
        for i, obs in enumerate(observations, 1):
            print(f"  [{i}/{len(observations)}] Probing {obs['observation_id']} ({obs['group']})...", flush=True)
            rec = execute_probe(obs, arm="ARM_B", scheduled_time=args.scheduled_time, attempt_id=args.attempt_id)
            print(f"    -> {rec['result']} ({rec['terminal_state']}, status={rec['http_status']}, bytes={rec['bytes_received']})", flush=True)
            records.append(rec)
            time.sleep(1.0)  # polite spacing
        append_attempt_csv(args.attempt_log, records, overwrite=args.overwrite)
        # Also save raw telemetry JSON
        telemetry_file = f"reports/raw_telemetry_{args.attempt_id}.json"
        with open(telemetry_file, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)
        print(f"Done {args.attempt_id}. Logged {len(records)} rows to {args.attempt_log} and {telemetry_file}")

    elif args.mode == "comparison":
        print(f"[{datetime.datetime.now(datetime.timezone.utc).isoformat()}] Starting Controlled A/B Client Comparison scheduled for {args.scheduled_time}...")
        records = []
        alternation = [
            ("INE002A01018::FY2010", "A_then_B"),
            ("INE040A01034::FY2014", "B_then_A"),
            ("INE081A01020::FY2016", "A_then_B"),
            ("INE171A01029::FY2021", "B_then_A"),
            ("INE226A01021::FY2022", "A_then_B"),
            ("INE002A01018::FY2012", "B_then_A"),
            ("INE009A01021::FY2013", "A_then_B"),
            ("INE040A01034::FY2017", "B_then_A"),
            ("INE044A01036::FY2018", "A_then_B"),
            ("INE081A01020::FY2024", "B_then_A"),
        ]
        order_map = dict(alternation)

        for i, obs in enumerate(observations, 1):
            obs_id = obs["observation_id"]
            arm_order = order_map.get(obs_id, "A_then_B")
            print(f"  [{i}/{len(observations)}] Paired probe {obs_id} (Order: {arm_order})...", flush=True)
            
            t_gap_start = time.monotonic()
            if arm_order == "A_then_B":
                rec_first = execute_probe(obs, arm="ARM_A", scheduled_time=args.scheduled_time, attempt_id="ab_comparison_A")
                t_gap = time.monotonic() - t_gap_start
                rec_second = execute_probe(obs, arm="ARM_B", scheduled_time=args.scheduled_time, attempt_id="ab_comparison_B")
                rec_a, rec_b = rec_first, rec_second
            else:
                rec_first = execute_probe(obs, arm="ARM_B", scheduled_time=args.scheduled_time, attempt_id="ab_comparison_B")
                t_gap = time.monotonic() - t_gap_start
                rec_second = execute_probe(obs, arm="ARM_A", scheduled_time=args.scheduled_time, attempt_id="ab_comparison_A")
                rec_a, rec_b = rec_second, rec_first

            a_ok = rec_a["result"] == "SUCCESS"
            b_ok = rec_b["result"] == "SUCCESS"
            if a_ok and b_ok:
                outcome = "A and B both succeed"
            elif not a_ok and not b_ok:
                outcome = "A and B both fail"
            elif a_ok and not b_ok:
                outcome = "A succeeds / B fails"
            elif not a_ok and b_ok:
                outcome = "A fails / B succeeds"
            else:
                outcome = "unable to test"

            comp_rec = {
                "observation_id": obs_id,
                "company_id": obs["company_id"],
                "fy": obs["FY"],
                "group": obs["group"],
                "exact_url": obs["exact_url"],
                "arm_order": arm_order,
                "scheduled_time": args.scheduled_time,
                "time_between_seconds": round(t_gap, 2),
                "arm_a_result": rec_a["result"],
                "arm_a_status": rec_a["http_status"],
                "arm_a_bytes": rec_a["bytes_received"],
                "arm_a_terminal_state": rec_a["terminal_state"],
                "arm_a_fail_layer": rec_a["first_failure_layer"],
                "arm_b_result": rec_b["result"],
                "arm_b_status": rec_b["http_status"],
                "arm_b_bytes": rec_b["bytes_received"],
                "arm_b_terminal_state": rec_b["terminal_state"],
                "arm_b_fail_layer": rec_b["first_failure_layer"],
                "outcome_classification": outcome,
                "rec_a_telemetry": rec_a,
                "rec_b_telemetry": rec_b
            }
            print(f"    -> A: {rec_a['result']} ({rec_a['terminal_state']}) | B: {rec_b['result']} ({rec_b['terminal_state']}) => {outcome}", flush=True)
            records.append(comp_rec)
            time.sleep(1.0)

        append_comparison_csv(args.comparison_log, records)
        telemetry_file = "reports/raw_telemetry_ab_comparison.json"
        with open(telemetry_file, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)
        print(f"Done A/B comparison. Logged {len(records)} pairs to {args.comparison_log} and {telemetry_file}")


if __name__ == "__main__":
    main()
