"""Configuration loader for arpipe.

Enforces 4-level precedence:
    CLI flag  >  env var  >  config file  >  code default

Every hardcoded threshold in triage.py, segment.py, ocr.py, verify.py, and
textlayer.py is accessible here and loaded at command start.

All thresholds are provisional until re-fit against the labelled 300.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from typing import Any, Mapping

import yaml

# ---------------------------------------------------------------------------
# Code defaults (level 1: baseline truth)
# All values provisional until re-fit against the labelled 300
# ---------------------------------------------------------------------------

DEFAULT_CONFIG: dict[str, dict[str, Any]] = {
    "universe": {
        "years": [2010, 2025],
        "segments": ["main_board"],
        "cap_bands": ["large", "mid", "small", "micro"],
    },
    "discover": {
        "sources": ["nse", "bse", "screener"],
        "min_interval_seconds": 1.5,
        "workers": 4,
    },
    "triage": {
        "min_chars_per_page": 120,
        "min_chars_dense": 600,
        "max_mojibake_ratio": 0.02,
        "big_image_area_frac": 0.55,
        "hybrid_image_area_frac": 0.25,
        "blank_chars": 15,
        "vector_path_text_threshold": 400,
        "column_hist_bins": 120,          # histogram bin count behind reading-order bug
        "gutter_min_run_frac": 0.025,     # gutter fraction behind reading-order bug (2.5%)
        "gutter_peak_threshold": 0.15,
        "gutter_search_lo": 0.15,
        "gutter_search_hi": 0.85,
        "doc_scanned_frac": 0.85,
        "doc_digital_frac": 0.05,
    },
    "textlayer": {
        "column_fullwidth_frac": 0.60,    # full-width block exclusion for column voting
        "column_centre_gap_frac": 0.14,   # fallback block-centre gap for column split
        "xy_cut_max_depth": 6,
        "xy_cut_min_v_gap_frac": 0.025,   # vertical gutter split threshold
        "xy_cut_min_h_gap_frac": 0.020,
        "xy_cut_edge_margin": 0.12,       # ignore cuts within 12% of page edge
        "table_digit_ratio": 0.40,
        "table_max_words_per_line": 6,
        "table_min_run": 3,
        "table_label_max_chars": 44,
        "table_label_max_words": 6,
        "table_prose_line_words": 12,
        "furniture_zone_frac": 0.08,
        "furniture_min_page_frac": 0.35,
        "repeated_header_min_pages": 4,
    },
    "segment": {
        "max_mda_pages": 60,
        "min_mda_words": 250,
        "heading_min_rel_size": 1.12,
        "heading_base_score": 0.45,
        "outline_base_score": 0.95,
        "toc_offset_confidence_threshold": 0.50,
        "toc_high_score": 0.80,
        "body_score_page_penalty": 0.12,
        "body_score_min_peak": 0.35,
        "body_score_max": 0.72,
        "text_heading_max_score": 0.78,
        "supporter_weight": 0.06,
        "llm": {
            "enabled": False,
            "model": "claude-sonnet",
            "max_pages_in_window": 24,
        },
    },
    "ocr": {
        "ladder": [
            {"engine": "tesseract", "lang_map": {"latin": "eng", "devanagari": "hin"}, "psm": 3},
            {"engine": "vlm", "url": "${ARPIPE_VLM_URL}", "model": "PaddlePaddle/PaddleOCR-VL"},
            {"engine": "textract", "region": "ap-south-1"},
        ],
        "default_dpi": 300,
        "min_dpi": 200,
        "max_dpi": 400,
        "quality_gate": {
            "min_words": 40,
            "min_conf": 0.72,
            "max_nonword_frac": 0.35,
        },
        "index_stride": 6,
        "front_pages": 14,
        "vlm_max_tokens": 8192,
        "vlm_timeout": 180,
        "vlm_repetition_ratio": 6.0,
    },
    "verify": {
        "name_match_strong": 88,
        "name_match_weak": 72,
        "require_year_evidence": True,
        "orphan_start_frac_max": 0.03,
        "fy_weight_floor": 15,
        "too_short_words": 250,
        "too_long_words": 40000,
        "looks_like_tables_digit_ratio": 0.25,
        "grade_high_min_supporters": 2,
        "grade_high_min_score": 0.80,
        "grade_medium_min_score": 0.60,
        "grade_solo_min_score": 0.70,
        "reprocessor_cap_grade": "medium",
    },
    "store": {
        "root": "dataset",
        "keep_page_texts": False,
    },
}


# ---------------------------------------------------------------------------
# Section attribute accessor
# ---------------------------------------------------------------------------

class SectionConfig(dict):
    """Dict subclass that allows attribute access (e.g. cfg.min_chars_dense)."""
    def __getattr__(self, name: str) -> Any:
        try:
            val = self[name]
            if isinstance(val, dict) and not isinstance(val, SectionConfig):
                val = SectionConfig(val)
                self[name] = val
            return val
        except KeyError:
            raise AttributeError(f"No configuration key '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value


class ResolvedConfig:
    """The fully resolved configuration, with provenance tracking."""
    def __init__(self, data: dict[str, Any], provenance: dict[str, str]):
        self._data = data
        self.provenance = provenance

    def __getitem__(self, key: str) -> Any:
        val = self._data[key]
        if isinstance(val, dict) and not isinstance(val, SectionConfig):
            val = SectionConfig(val)
            self._data[key] = val
        return val

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"No configuration section '{name}'")

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default

    def to_dict(self) -> dict[str, Any]:
        return copy.deepcopy(self._data)


# ---------------------------------------------------------------------------
# Helpers for casting & merging
# ---------------------------------------------------------------------------

def _coerce_value(raw: str, default_val: Any) -> Any:
    """Coerce a string environment variable or CLI override to match default_val's type."""
    if isinstance(default_val, bool):
        return raw.strip().lower() in ("1", "true", "yes", "on")
    if isinstance(default_val, int):
        try:
            return int(raw)
        except ValueError:
            return default_val
    if isinstance(default_val, float):
        try:
            return float(raw)
        except ValueError:
            return default_val
    if isinstance(default_val, (list, dict)):
        try:
            return json.loads(raw)
        except Exception:
            return raw
    return raw


def _find_default_config_file() -> str | None:
    """Locate the default YAML config file."""
    candidates = [
        "arpipe.yaml",
        "configs/default.yaml",
        os.path.join(os.path.dirname(__file__), "configs", "default.yaml"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs", "default.yaml"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return os.path.abspath(c)
    return None


# ---------------------------------------------------------------------------
# Main loader with 4-level precedence
# ---------------------------------------------------------------------------

def load_config(
    config_path: str | None = None,
    cli_overrides: dict[str, Any] | argparse.Namespace | None = None,
    env_prefix: str = "ARPIPE",
) -> ResolvedConfig:
    """Load configuration with precedence:
        CLI flag > env var > config file > code default
    """
    # 1. Start with code defaults
    data = copy.deepcopy(DEFAULT_CONFIG)
    provenance: dict[str, str] = {}
    for sec, kvs in data.items():
        if isinstance(kvs, dict):
            for k in kvs:
                provenance[f"{sec}.{k}"] = "code_default"

    # 2. Config file
    file_to_load = config_path or os.environ.get(f"{env_prefix}_CONFIG") or _find_default_config_file()
    if file_to_load and os.path.isfile(file_to_load):
        try:
            with open(file_to_load, encoding="utf-8") as fh:
                loaded = yaml.safe_load(fh) or {}
            for sec, kvs in loaded.items():
                if isinstance(kvs, dict):
                    if sec not in data or not isinstance(data[sec], dict):
                        data[sec] = {}
                    for k, v in kvs.items():
                        data[sec][k] = v
                        provenance[f"{sec}.{k}"] = f"config_file: {file_to_load}"
                else:
                    data[sec] = kvs
                    provenance[sec] = f"config_file: {file_to_load}"
        except Exception as exc:
            print(f"Warning: Failed to load config from {file_to_load}: {exc}", file=sys.stderr)

    # 3. Environment variables (ARPIPE_<SECTION>_<KEY>)
    prefix = f"{env_prefix}_"
    for env_k, env_v in os.environ.items():
        if not env_k.startswith(prefix):
            continue
        rest = env_k[len(prefix):].lower()
        # Look for matching section.key
        matched = False
        for sec in data:
            if rest.startswith(f"{sec}_"):
                key = rest[len(sec) + 1:]
                default_val = data[sec].get(key) if isinstance(data[sec], dict) else None
                coerced = _coerce_value(env_v, default_val) if default_val is not None else env_v
                if isinstance(data[sec], dict):
                    data[sec][key] = coerced
                    provenance[f"{sec}.{key}"] = f"env_var: {env_k}"
                    matched = True
                    break
        if not matched:
            # Check for top-level keys like ARPIPE_STORE, ARPIPE_ROOT
            if rest in data:
                data[rest] = env_v
                provenance[rest] = f"env_var: {env_k}"

    # 4. CLI overrides
    cli_dict: dict[str, Any] = {}
    if isinstance(cli_overrides, argparse.Namespace):
        cli_dict = vars(cli_overrides)
    elif isinstance(cli_overrides, dict):
        cli_dict = cli_overrides

    # Direct mapping for common CLI flags
    cli_mappings: list[tuple[str, str, str]] = [
        ("root", "store", "root"),
        ("out", "store", "out"),
        ("keep_pages", "store", "keep_page_texts"),
        ("min_interval", "discover", "min_interval_seconds"),
        ("workers", "discover", "workers"),
        ("from_year", "universe", "from_year"),
        ("to_year", "universe", "to_year"),
        ("min_disk_tb", "store", "min_disk_tb"),
    ]
    for cli_arg, sec, key in cli_mappings:
        val = cli_dict.get(cli_arg)
        if val is not None:
            if sec not in data:
                data[sec] = {}
            data[sec][key] = val
            provenance[f"{sec}.{key}"] = f"cli_flag: --{cli_arg.replace('_', '-')}"

    # Generic --set section.key=val
    custom_sets = cli_dict.get("set") or []
    if isinstance(custom_sets, str):
        custom_sets = [custom_sets]
    for item in custom_sets:
        if "=" in item:
            path, val_str = item.split("=", 1)
            parts = path.strip().split(".")
            if len(parts) == 2:
                s, k = parts[0].strip(), parts[1].strip()
                default_val = data.get(s, {}).get(k)
                coerced = _coerce_value(val_str.strip(), default_val) if default_val is not None else val_str.strip()
                if s not in data:
                    data[s] = {}
                data[s][k] = coerced
                provenance[f"{s}.{k}"] = f"cli_flag: --set {item}"

    resolved = ResolvedConfig(data, provenance)
    return resolved


# ---------------------------------------------------------------------------
# Module threshold injection (Option A)
# ---------------------------------------------------------------------------

def apply_config(cfg: ResolvedConfig | dict[str, Any]) -> None:
    """Inject resolved config values into module-level thresholds."""
    if isinstance(cfg, ResolvedConfig):
        cfg_dict = cfg.to_dict()
    else:
        cfg_dict = cfg

    from . import triage, textlayer, segment, ocr, verify, pipeline

    if hasattr(triage, "configure"):
        triage.configure(cfg_dict.get("triage"))
    if hasattr(textlayer, "configure"):
        textlayer.configure(cfg_dict.get("textlayer"))
    if hasattr(segment, "configure"):
        segment.configure(cfg_dict.get("segment"))
    if hasattr(ocr, "configure"):
        ocr.configure(cfg_dict.get("ocr"))
    if hasattr(verify, "configure"):
        verify.configure(cfg_dict.get("verify"))
    if hasattr(pipeline, "configure"):
        pipeline.configure(cfg_dict)


_ACTIVE_CONFIG: ResolvedConfig | None = None


def get_config() -> ResolvedConfig:
    """Return the active resolved configuration (loads defaults if not yet initialized)."""
    global _ACTIVE_CONFIG
    if _ACTIVE_CONFIG is None:
        _ACTIVE_CONFIG = load_config()
        apply_config(_ACTIVE_CONFIG)
    return _ACTIVE_CONFIG


def set_active_config(cfg: ResolvedConfig) -> None:
    """Set and apply the active configuration."""
    global _ACTIVE_CONFIG
    _ACTIVE_CONFIG = cfg
    apply_config(cfg)


def config_for_manifest(cfg: ResolvedConfig | None = None) -> dict[str, Any]:
    """Clean serializable config dictionary suitable for recording in manifest rows."""
    c = cfg or get_config()
    return c.to_dict()


# ---------------------------------------------------------------------------
# Output formatting for --print-config
# ---------------------------------------------------------------------------

def format_config_dump(cfg: ResolvedConfig) -> str:
    """Dump the fully resolved config showing values and provenance sources."""
    lines: list[str] = [
        "# Fully resolved arpipe configuration",
        "# Precedence: CLI flag  >  env var  >  config file  >  code default",
        "",
    ]
    data = cfg.to_dict()
    for sec, kvs in sorted(data.items()):
        lines.append(f"{sec}:")
        if isinstance(kvs, dict):
            for k, v in sorted(kvs.items()):
                prov_key = f"{sec}.{k}"
                source = cfg.provenance.get(prov_key, "code_default")
                if isinstance(v, (dict, list)):
                    val_str = json.dumps(v)
                elif isinstance(v, str):
                    val_str = f'"{v}"'
                else:
                    val_str = str(v)
                lines.append(f"  {k:<32} {val_str:<24} # [{source}]")
        else:
            source = cfg.provenance.get(sec, "code_default")
            lines.append(f"  {str(kvs):<32} # [{source}]")
        lines.append("")
    return "\n".join(lines)
