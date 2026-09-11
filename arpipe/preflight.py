"""Preflight checks for arpipe.

Run `python -m arpipe.cli preflight` before a long batch run.  Every check
that a multi-day pipeline needs is validated *before* we download or process
a single PDF, so failures surface in minutes rather than at 3 a.m. on day four.

Exit code 0 if all PASS/WARN/INFO, 1 if any FAIL.
"""
from __future__ import annotations

import importlib
import os
import platform
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Sequence


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

class Status(Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    INFO = "INFO"


@dataclass
class CheckResult:
    category: str
    name: str
    status: Status
    detail: str = ""
    fix_hint: str = ""


# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------

_ANSI = {
    Status.PASS: "\033[92m",   # green
    Status.WARN: "\033[93m",   # yellow
    Status.FAIL: "\033[91m",   # red
    Status.INFO: "\033[96m",   # cyan
}
_RESET = "\033[0m"

_WIN = sys.platform == "win32"


def _os_label() -> str:
    s = platform.system().lower()
    if s == "darwin":
        return "macos"
    return s                # "windows" or "linux"


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def _refresh_path_if_needed() -> None:
    """On Windows, tools installed after the current shell started are invisible
    until the PATH is refreshed.  ``arpipe.ps1`` does this automatically, but
    when invoked from Python directly (tests, IDEs) the new entries may be
    missing.  Refresh once, at most."""
    if not _WIN:
        return
    try:
        machine = os.environ.get("__MACHINE_PATH") or subprocess.check_output(
            ["powershell", "-NoProfile", "-Command",
             '[System.Environment]::GetEnvironmentVariable("Path","Machine")'],
            text=True, timeout=5).strip()
        user = os.environ.get("__USER_PATH") or subprocess.check_output(
            ["powershell", "-NoProfile", "-Command",
             '[System.Environment]::GetEnvironmentVariable("Path","User")'],
            text=True, timeout=5).strip()
        existing = os.environ.get("PATH", "")
        merged = machine + ";" + user + ";" + existing
        # de-duplicate while preserving order
        seen: set[str] = set()
        parts: list[str] = []
        for p in merged.split(";"):
            low = p.lower().rstrip("\\")
            if low and low not in seen:
                seen.add(low)
                parts.append(p)
        os.environ["PATH"] = ";".join(parts)
    except Exception:
        pass


def check_tesseract() -> list[CheckResult]:
    """Verify tesseract is on PATH, report version and available languages."""
    results: list[CheckResult] = []
    _refresh_path_if_needed()
    exe = shutil.which("tesseract")
    if not exe:
        results.append(CheckResult(
            "Tools", "tesseract",
            Status.FAIL, "not found on PATH",
            _fix("tesseract")))
        return results

    # version
    try:
        ver = subprocess.check_output([exe, "--version"],
                                      text=True, timeout=10,
                                      stderr=subprocess.STDOUT).splitlines()[0]
    except Exception as exc:
        ver = f"(error: {exc})"
    results.append(CheckResult("Tools", "tesseract", Status.PASS, ver))

    # languages
    try:
        raw = subprocess.check_output([exe, "--list-langs"],
                                      text=True, timeout=10,
                                      stderr=subprocess.STDOUT)
        langs = [l.strip() for l in raw.splitlines()
                 if l.strip() and ":" not in l]
    except Exception:
        langs = []

    if "eng" not in langs:
        results.append(CheckResult(
            "Tools", "tesseract lang: eng",
            Status.FAIL, f"eng missing from {langs}",
            _fix("tesseract-eng")))
    else:
        results.append(CheckResult(
            "Tools", "tesseract lang: eng",
            Status.PASS, "present"))

    if "hin" not in langs:
        results.append(CheckResult(
            "Tools", "tesseract lang: hin",
            Status.WARN,
            "hin not installed – Hindi OCR unavailable",
            _fix("tesseract-hin")))
    else:
        results.append(CheckResult(
            "Tools", "tesseract lang: hin",
            Status.PASS, "present"))

    return results


def check_qpdf() -> list[CheckResult]:
    _refresh_path_if_needed()
    exe = shutil.which("qpdf")
    if not exe:
        return [CheckResult("Tools", "qpdf", Status.FAIL,
                            "not found on PATH", _fix("qpdf"))]
    try:
        ver = subprocess.check_output([exe, "--version"],
                                      text=True, timeout=10,
                                      stderr=subprocess.STDOUT).splitlines()[0]
    except Exception as exc:
        ver = f"(error: {exc})"
    return [CheckResult("Tools", "qpdf", Status.PASS, ver)]


def check_poppler() -> list[CheckResult]:
    """pdftotext is optional but useful for some fallback paths."""
    exe = shutil.which("pdftotext")
    if not exe:
        return [CheckResult("Tools", "pdftotext (poppler)",
                            Status.INFO,
                            "not found – optional, not required")]
    return [CheckResult("Tools", "pdftotext (poppler)",
                        Status.PASS, exe)]


# ---------------------------------------------------------------------------
# Python dependencies
# ---------------------------------------------------------------------------

_VERSION_RE = re.compile(r"[><=!~]+(.+)")


def _parse_requirements(path: str) -> list[tuple[str, str]]:
    """Return (package_name, version_spec) pairs from requirements.txt."""
    pkgs: list[tuple[str, str]] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.split("#")[0].strip()
            if not line:
                continue
            m = re.match(r"([A-Za-z0-9_.-]+)\s*(.*)", line)
            if m:
                pkgs.append((m.group(1), m.group(2).strip()))
    return pkgs


# Packages where import name differs from pip name
_IMPORT_MAP: dict[str, str] = {
    "pymupdf": "fitz",
    "pillow": "PIL",
    "rapidfuzz": "rapidfuzz",
    "pytesseract": "pytesseract",
    "google-cloud-documentai": "google.cloud.documentai",
}

# Optional packages that should warn rather than fail
_OPTIONAL = {"ocrmypdf", "boto3", "google-cloud-documentai", "vllm"}


def check_requirements(req_path: str | None = None) -> list[CheckResult]:
    """Import every package in requirements.txt and report version."""
    if req_path is None:
        req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if not os.path.exists(req_path):
        return [CheckResult("Python", "requirements.txt",
                            Status.WARN, f"not found: {req_path}")]

    results: list[CheckResult] = []
    for pkg, spec in _parse_requirements(req_path):
        import_name = _IMPORT_MAP.get(pkg.lower(), pkg.replace("-", "_"))
        is_optional = pkg.lower() in _OPTIONAL
        try:
            mod = importlib.import_module(import_name)
            ver = getattr(mod, "__version__", getattr(mod, "version", "?"))
            results.append(CheckResult(
                "Python", pkg,
                Status.PASS, f"{ver} ({spec or 'any'})"))
        except ImportError:
            if is_optional:
                results.append(CheckResult(
                    "Python", pkg,
                    Status.INFO,
                    "not installed (optional)",
                    f"pip install {pkg}"))
            else:
                results.append(CheckResult(
                    "Python", pkg,
                    Status.FAIL,
                    f"import {import_name} failed",
                    f"pip install {pkg}"))
    return results


# ---------------------------------------------------------------------------
# Filesystem
# ---------------------------------------------------------------------------

def check_disk_space(store_dir: str, min_free_tb: float = 1.0) -> list[CheckResult]:
    """Fail if free disk on the store volume is below min_free_tb."""
    d = store_dir if os.path.isdir(store_dir) else os.path.dirname(store_dir) or "."
    try:
        usage = shutil.disk_usage(d)
    except Exception as exc:
        return [CheckResult("Filesystem", "disk space",
                            Status.FAIL, str(exc))]
    free_tb = usage.free / (1024 ** 4)
    free_gb = usage.free / (1024 ** 3)
    total_tb = usage.total / (1024 ** 4)
    detail = f"{free_gb:.1f} GB free ({free_tb:.3f} TB of {total_tb:.2f} TB total)"
    if free_tb < min_free_tb:
        return [CheckResult("Filesystem", "disk space",
                            Status.FAIL,
                            f"{detail}; need >= {min_free_tb} TB",
                            f"Free disk space or use --min-disk-tb {free_tb:.2f}")]
    return [CheckResult("Filesystem", "disk space", Status.PASS, detail)]


def check_link_capabilities(store_dir: str) -> list[CheckResult]:
    """Test whether hardlinks and symlinks work on the store volume."""
    results: list[CheckResult] = []
    os.makedirs(store_dir, exist_ok=True)

    probe = os.path.join(store_dir, "_preflight_probe.tmp")
    try:
        with open(probe, "w") as f:
            f.write("preflight")
    except Exception as exc:
        results.append(CheckResult("Filesystem", "link capability",
                                   Status.FAIL, f"cannot create probe file: {exc}"))
        return results

    # hardlink
    hard = probe + ".hard"
    can_hard = False
    try:
        if os.path.exists(hard):
            os.remove(hard)
        os.link(probe, hard)
        can_hard = True
    except Exception:
        pass
    finally:
        if os.path.exists(hard):
            os.remove(hard)

    # symlink
    sym = probe + ".sym"
    can_sym = False
    try:
        if os.path.exists(sym):
            os.remove(sym)
        os.symlink(probe, sym)
        can_sym = True
    except Exception:
        pass
    finally:
        if os.path.exists(sym):
            os.remove(sym)

    # clean up probe
    if os.path.exists(probe):
        os.remove(probe)

    if can_hard:
        results.append(CheckResult("Filesystem", "hardlink",
                                   Status.PASS, "supported"))
    else:
        results.append(CheckResult("Filesystem", "hardlink",
                                   Status.WARN, "not supported"))

    if can_sym:
        results.append(CheckResult("Filesystem", "symlink",
                                   Status.PASS, "supported"))
    else:
        hint = ""
        if _WIN:
            hint = ("Enable Developer Mode in Settings > Privacy & Security > "
                    "For developers, or run as Administrator")
        results.append(CheckResult("Filesystem", "symlink",
                                   Status.INFO,
                                   "not supported (hardlink will be used)",
                                   hint))

    if not can_hard and not can_sym:
        results.append(CheckResult("Filesystem", "link mode",
                                   Status.WARN,
                                   "copy-only mode – doubles disk usage"))

    return results


def check_volume_alignment(root: str, out: str) -> list[CheckResult]:
    """Warn if --root and --out are on different volumes (no cross-volume hardlinks)."""
    root_dir = root if os.path.isdir(root) else os.path.dirname(root) or "."
    out_dir = out if os.path.isdir(out) else os.path.dirname(out) or "."
    os.makedirs(root_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)

    if _WIN:
        root_vol = os.path.splitdrive(os.path.abspath(root_dir))[0].upper()
        out_vol = os.path.splitdrive(os.path.abspath(out_dir))[0].upper()
    else:
        root_vol = str(os.stat(root_dir).st_dev)
        out_vol = str(os.stat(out_dir).st_dev)

    if root_vol != out_vol:
        return [CheckResult("Filesystem", "volume alignment",
                            Status.WARN,
                            f"--root ({root_vol}) and --out ({out_vol}) on "
                            f"different volumes – hardlinks will not work")]
    return [CheckResult("Filesystem", "volume alignment",
                        Status.PASS,
                        f"same volume ({root_vol})")]


def check_write_permissions(root: str, out: str) -> list[CheckResult]:
    """Test that we can create and delete files in both store and dataset dirs."""
    results: list[CheckResult] = []
    for label, d in [("store (--root)", root), ("dataset (--out)", out)]:
        os.makedirs(d, exist_ok=True)
        probe = os.path.join(d, "_write_probe.tmp")
        try:
            with open(probe, "w") as f:
                f.write("ok")
            os.remove(probe)
            results.append(CheckResult("Filesystem", f"write: {label}",
                                       Status.PASS, "writable"))
        except Exception as exc:
            results.append(CheckResult("Filesystem", f"write: {label}",
                                       Status.FAIL, str(exc)))
    return results


# ---------------------------------------------------------------------------
# Companies master
# ---------------------------------------------------------------------------

def check_companies(csv_path: str) -> list[CheckResult]:
    """Validate companies.csv: exists, row count > 2000, no duplicates."""
    if not os.path.exists(csv_path):
        return [CheckResult("Data", "companies.csv",
                            Status.WARN,
                            f"not found: {csv_path} (will be created by 'arpipe universe')")]
    try:
        import pandas as pd
        df = pd.read_csv(csv_path)
    except Exception as exc:
        return [CheckResult("Data", "companies.csv",
                            Status.FAIL, f"cannot read: {exc}")]

    results: list[CheckResult] = []
    n = len(df)
    if n < 2000:
        results.append(CheckResult("Data", "companies.csv row count",
                                   Status.WARN,
                                   f"{n} rows (expect > 2000 for production)"))
    else:
        results.append(CheckResult("Data", "companies.csv row count",
                                   Status.PASS, f"{n} rows"))

    if "company_id" in df.columns:
        dups = df["company_id"].dropna().duplicated().sum()
        nulls = df["company_id"].isna().sum()
        if dups > 0:
            results.append(CheckResult("Data", "companies.csv duplicates",
                                       Status.FAIL,
                                       f"{dups} duplicate company_id values"))
        else:
            detail = "no duplicates"
            if nulls:
                detail += f" ({nulls} null company_id)"
            results.append(CheckResult("Data", "companies.csv duplicates",
                                       Status.PASS, detail))
    return results


# ---------------------------------------------------------------------------
# Network
# ---------------------------------------------------------------------------

def check_network_nse() -> list[CheckResult]:
    """Verify we can get NSE session cookies."""
    try:
        import httpx
        from . import discover
    except ImportError as exc:
        return [CheckResult("Network", "NSE", Status.FAIL,
                            f"import error: {exc}")]
    try:
        cl = httpx.Client(headers=discover.NSE_HEADERS, timeout=15,
                          follow_redirects=True)
        r1 = cl.get(discover.NSE_HOME)
        r2 = cl.get(discover.NSE_HOME +
                     "/companies-listing/corporate-filings-annual-reports")
        cookies = len(cl.cookies)
        cl.close()
        if cookies == 0 and r1.status_code != 200:
            return [CheckResult("Network", "NSE",
                                Status.WARN,
                                f"status {r1.status_code}, 0 cookies – "
                                f"may be rate-limited or geo-blocked")]
        return [CheckResult("Network", "NSE", Status.PASS,
                            f"status {r1.status_code}, {cookies} cookies")]
    except Exception as exc:
        return [CheckResult("Network", "NSE", Status.FAIL, str(exc))]


def check_network_bse() -> list[CheckResult]:
    """Verify BSE responds with correct headers."""
    try:
        import httpx
        from . import discover
    except ImportError as exc:
        return [CheckResult("Network", "BSE", Status.FAIL,
                            f"import error: {exc}")]
    try:
        cl = httpx.Client(headers=discover.BSE_HEADERS, timeout=15,
                          follow_redirects=True)
        r = cl.get("https://www.bseindia.com/")
        cl.close()
        if r.status_code == 403:
            return [CheckResult("Network", "BSE",
                                Status.FAIL,
                                "403 Forbidden – headers rejected")]
        return [CheckResult("Network", "BSE", Status.PASS,
                            f"status {r.status_code}")]
    except Exception as exc:
        return [CheckResult("Network", "BSE", Status.FAIL, str(exc))]


def check_network_screener() -> list[CheckResult]:
    """Light HEAD to screener.in."""
    try:
        import httpx
    except ImportError:
        return [CheckResult("Network", "screener.in", Status.INFO,
                            "httpx not available")]
    try:
        r = httpx.head("https://www.screener.in/", timeout=10,
                       follow_redirects=True)
        return [CheckResult("Network", "screener.in", Status.PASS,
                            f"status {r.status_code}")]
    except Exception as exc:
        return [CheckResult("Network", "screener.in", Status.WARN,
                            f"unreachable: {exc}")]


# ---------------------------------------------------------------------------
# GPU
# ---------------------------------------------------------------------------

def check_gpu(required: bool = False) -> list[CheckResult]:
    """Probe GPU presence and VRAM."""
    gpu_name, vram_mb = None, 0

    # Try PyTorch first
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            vram_mb = torch.cuda.get_device_properties(0).total_mem / (1024 ** 2)
    except ImportError:
        pass

    # Fallback to nvidia-smi
    if gpu_name is None:
        try:
            out = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=name,memory.total",
                 "--format=csv,noheader,nounits"],
                text=True, timeout=10, stderr=subprocess.DEVNULL).strip()
            if out:
                parts = out.split(",")
                gpu_name = parts[0].strip()
                vram_mb = float(parts[1].strip()) if len(parts) > 1 else 0
        except Exception:
            pass

    if gpu_name:
        vram_gb = vram_mb / 1024
        detail = f"{gpu_name}, {vram_gb:.1f} GB VRAM"
        if required and vram_gb < 4.0:
            return [CheckResult("Hardware", "GPU",
                                Status.FAIL,
                                f"{detail} – need >= 4 GB for GPU rung")]
        return [CheckResult("Hardware", "GPU", Status.PASS, detail)]

    if required:
        return [CheckResult("Hardware", "GPU",
                            Status.FAIL,
                            "no GPU detected – required for GPU rung",
                            _fix("gpu"))]
    return [CheckResult("Hardware", "GPU", Status.INFO,
                        "no GPU detected (CPU-only mode)")]


# ---------------------------------------------------------------------------
# Optional: VLM endpoint
# ---------------------------------------------------------------------------

def check_vlm(vlm_url: str | None, vlm_model: str | None) -> list[CheckResult]:
    """If --vlm-url configured, verify the endpoint responds."""
    if not vlm_url:
        return [CheckResult("Optional", "VLM endpoint", Status.INFO,
                            "not configured")]
    try:
        import httpx
    except ImportError:
        return [CheckResult("Optional", "VLM endpoint", Status.FAIL,
                            "httpx not available")]
    try:
        r = httpx.get(vlm_url.rstrip("/") + "/v1/models", timeout=10)
        if r.status_code == 200:
            return [CheckResult("Optional", "VLM endpoint", Status.PASS,
                                f"{vlm_url} – model: {vlm_model or '?'}")]
        return [CheckResult("Optional", "VLM endpoint", Status.WARN,
                            f"status {r.status_code} from {vlm_url}")]
    except Exception as exc:
        return [CheckResult("Optional", "VLM endpoint", Status.FAIL,
                            f"{vlm_url}: {exc}")]


# ---------------------------------------------------------------------------
# Optional: AWS Textract
# ---------------------------------------------------------------------------

def check_textract(enabled: bool, region: str = "ap-south-1") -> list[CheckResult]:
    if not enabled:
        return [CheckResult("Optional", "AWS Textract", Status.INFO,
                            "not configured")]
    try:
        import boto3
    except ImportError:
        return [CheckResult("Optional", "AWS Textract", Status.FAIL,
                            "boto3 not installed", "pip install boto3")]
    try:
        sts = boto3.client("sts", region_name=region)
        identity = sts.get_caller_identity()
        return [CheckResult("Optional", "AWS Textract", Status.PASS,
                            f"account {identity['Account']}, region {region}")]
    except Exception as exc:
        return [CheckResult("Optional", "AWS Textract", Status.FAIL,
                            f"credentials invalid: {exc}")]


# ---------------------------------------------------------------------------
# Fix hints
# ---------------------------------------------------------------------------

_HINTS: dict[str, dict[str, str]] = {
    "tesseract": {
        "windows": "winget install UB-Mannheim.TesseractOCR\n"
                   "  or: choco install tesseract",
        "linux":   "sudo apt-get install tesseract-ocr",
        "macos":   "brew install tesseract",
    },
    "tesseract-eng": {
        "windows": "Language pack is included with the UB-Mannheim installer.\n"
                   "  Re-run the installer and ensure 'eng' is selected.",
        "linux":   "sudo apt-get install tesseract-ocr-eng",
        "macos":   "brew install tesseract-lang",
    },
    "tesseract-hin": {
        "windows": "Re-run the UB-Mannheim installer and select 'Hindi' "
                   "under Additional language data.",
        "linux":   "sudo apt-get install tesseract-ocr-hin",
        "macos":   "brew install tesseract-lang",
    },
    "qpdf": {
        "windows": "winget install qpdf.qpdf\n"
                   "  or: choco install qpdf",
        "linux":   "sudo apt-get install qpdf",
        "macos":   "brew install qpdf",
    },
    "gpu": {
        "windows": "Install NVIDIA CUDA toolkit and a compatible GPU driver.",
        "linux":   "sudo apt-get install nvidia-driver-535 nvidia-cuda-toolkit",
        "macos":   "GPU acceleration requires an NVIDIA GPU (not available on macOS).",
    },
}


def _fix(key: str) -> str:
    os_name = _os_label()
    return _HINTS.get(key, {}).get(os_name, "")


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_table(results: Sequence[CheckResult],
                 use_color: bool = True) -> str:
    """Build a human-readable summary table."""
    lines: list[str] = []

    # Column widths
    cat_w = max(len(r.category) for r in results) if results else 8
    name_w = max(len(r.name) for r in results) if results else 8
    stat_w = 6  # "[PASS]"

    hdr = f"  {'Category':<{cat_w}}  {'Check':<{name_w}}  {'Status':<{stat_w}}  Detail"
    sep = "  " + "─" * (cat_w + name_w + stat_w + 10)
    lines.append("")
    lines.append("  ARPIPE PREFLIGHT")
    lines.append(sep)
    lines.append(hdr)
    lines.append(sep)

    prev_cat = ""
    for r in results:
        badge = f"[{r.status.value}]"
        if use_color:
            c = _ANSI.get(r.status, "")
            badge = f"{c}{badge}{_RESET}"
        cat_label = r.category if r.category != prev_cat else ""
        prev_cat = r.category
        lines.append(f"  {cat_label:<{cat_w}}  {r.name:<{name_w}}  {badge}  {r.detail}")
    lines.append(sep)

    n_pass = sum(1 for r in results if r.status == Status.PASS)
    n_warn = sum(1 for r in results if r.status == Status.WARN)
    n_fail = sum(1 for r in results if r.status == Status.FAIL)
    n_info = sum(1 for r in results if r.status == Status.INFO)
    summary = f"  {n_pass} PASS, {n_warn} WARN, {n_fail} FAIL, {n_info} INFO"
    if n_fail:
        if use_color:
            summary += f"  {_ANSI[Status.FAIL]}→ BLOCKED{_RESET}"
        else:
            summary += "  → BLOCKED"
    else:
        if use_color:
            summary += f"  {_ANSI[Status.PASS]}→ READY{_RESET}"
        else:
            summary += "  → READY"
    lines.append(summary)
    lines.append("")
    return "\n".join(lines)


def format_fix_hints(results: Sequence[CheckResult]) -> str:
    """Print remediation hints for failed or warned checks."""
    lines: list[str] = []
    os_name = _os_label()
    lines.append(f"\n  FIX HINTS (detected OS: {os_name})")
    lines.append("  " + "─" * 50)
    any_hint = False
    for r in results:
        if r.status in (Status.FAIL, Status.WARN) and r.fix_hint:
            any_hint = True
            lines.append(f"  [{r.status.value}] {r.name}:")
            for hl in r.fix_hint.split("\n"):
                lines.append(f"    {hl}")
    if not any_hint:
        lines.append("  No actionable hints.")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_preflight(
    *,
    root: str = "store",
    out: str = "dataset",
    companies: str = "companies.csv",
    min_disk_tb: float = 1.0,
    req_file: str | None = None,
    vlm_url: str | None = None,
    vlm_model: str | None = None,
    gpu: bool = False,
    textract: bool = False,
    aws_region: str = "ap-south-1",
    fix_hints: bool = False,
    no_network: bool = False,
    use_color: bool | None = None,
) -> int:
    """Run all preflight checks and return exit code (0 = ok, 1 = blocked)."""
    if use_color is None:
        use_color = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    results: list[CheckResult] = []

    # Tools
    results.extend(check_tesseract())
    results.extend(check_qpdf())
    results.extend(check_poppler())

    # Python
    results.extend(check_requirements(req_file))

    # Filesystem
    results.extend(check_disk_space(root, min_disk_tb))
    results.extend(check_link_capabilities(root))
    results.extend(check_volume_alignment(root, out))
    results.extend(check_write_permissions(root, out))

    # Data
    results.extend(check_companies(companies))

    # Network
    if not no_network:
        results.extend(check_network_nse())
        results.extend(check_network_bse())
        results.extend(check_network_screener())

    # Hardware
    results.extend(check_gpu(required=gpu))

    # Optional services
    results.extend(check_vlm(vlm_url, vlm_model))
    results.extend(check_textract(textract, aws_region))

    # Output
    print(format_table(results, use_color=use_color))

    if fix_hints:
        print(format_fix_hints(results))

    has_fail = any(r.status == Status.FAIL for r in results)
    return 1 if has_fail else 0
