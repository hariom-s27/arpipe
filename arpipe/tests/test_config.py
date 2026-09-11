"""Unit tests for arpipe.config (P15: Wire the config file)."""
from __future__ import annotations

import os
import tempfile
import pytest
import yaml

from arpipe import config, ocr, pipeline, segment, textlayer, triage, verify


class TestCodeDefaults:
    def test_all_sections_present(self):
        data = config.DEFAULT_CONFIG
        assert "triage" in data
        assert "textlayer" in data
        assert "segment" in data
        assert "ocr" in data
        assert "verify" in data
        assert "store" in data
        assert "discover" in data
        assert "universe" in data

    def test_reading_order_bug_constants_present(self):
        """P15 requires gutter fraction and histogram bin count to be in config."""
        triage_cfg = config.DEFAULT_CONFIG["triage"]
        assert triage_cfg["column_hist_bins"] == 120
        assert triage_cfg["gutter_min_run_frac"] == 0.025


class TestYamlLoader:
    def test_load_custom_yaml(self, tmp_path):
        custom_yaml = tmp_path / "custom.yaml"
        custom_yaml.write_text(
            yaml.dump({
                "triage": {"min_chars_per_page": 200, "column_hist_bins": 150},
                "verify": {"name_match_strong": 95},
            }),
            encoding="utf-8",
        )
        cfg = config.load_config(config_path=str(custom_yaml))
        assert cfg.triage.min_chars_per_page == 200
        assert cfg.triage.column_hist_bins == 150
        assert cfg.verify.name_match_strong == 95
        # Unspecified keys fall back to code defaults or default yaml
        assert cfg.segment.max_mda_pages == 60
        assert "config_file" in cfg.provenance["triage.min_chars_per_page"]


class TestPrecedence:
    """Precedence contract: CLI flag > env var > config file > code default."""

    def test_env_overrides_config_file(self, tmp_path, monkeypatch):
        custom_yaml = tmp_path / "custom.yaml"
        custom_yaml.write_text(
            yaml.dump({"triage": {"column_hist_bins": 140}}),
            encoding="utf-8",
        )
        monkeypatch.setenv("ARPIPE_TRIAGE_COLUMN_HIST_BINS", "180")
        cfg = config.load_config(config_path=str(custom_yaml))
        assert cfg.triage.column_hist_bins == 180
        assert "env_var: ARPIPE_TRIAGE_COLUMN_HIST_BINS" in cfg.provenance["triage.column_hist_bins"]

    def test_cli_overrides_env_and_file(self, tmp_path, monkeypatch):
        custom_yaml = tmp_path / "custom.yaml"
        custom_yaml.write_text(
            yaml.dump({"triage": {"column_hist_bins": 140}}),
            encoding="utf-8",
        )
        monkeypatch.setenv("ARPIPE_TRIAGE_COLUMN_HIST_BINS", "180")
        cli_overrides = {"set": ["triage.column_hist_bins=220"]}
        cfg = config.load_config(config_path=str(custom_yaml), cli_overrides=cli_overrides)
        assert cfg.triage.column_hist_bins == 220
        assert "cli_flag" in cfg.provenance["triage.column_hist_bins"]

    def test_code_default_provenance(self):
        cfg = config.load_config(config_path="/nonexistent/path/arpipe.yaml")
        # When file doesn't exist, values retain default provenance
        assert cfg.triage.blank_chars == 15
        assert cfg.provenance.get("triage.blank_chars") == "code_default"


class TestModuleInjection:
    def test_apply_config_updates_triage_constants(self):
        custom_cfg = {"triage": {"column_hist_bins": 250, "min_chars_dense": 999}}
        config.apply_config(custom_cfg)
        assert triage.COLUMN_HIST_BINS == 250
        assert triage.MIN_CHARS_DENSE == 999
        # Reset back to default
        config.apply_config(config.DEFAULT_CONFIG)
        assert triage.COLUMN_HIST_BINS == 120
        assert triage.MIN_CHARS_DENSE == 600

    def test_apply_config_updates_textlayer_constants(self):
        custom_cfg = {"textlayer": {"column_fullwidth_frac": 0.75, "xy_cut_max_depth": 8}}
        config.apply_config(custom_cfg)
        assert textlayer.COLUMN_FULLWIDTH_FRAC == 0.75
        assert textlayer.XY_CUT_MAX_DEPTH == 8
        # Reset back to default
        config.apply_config(config.DEFAULT_CONFIG)
        assert textlayer.COLUMN_FULLWIDTH_FRAC == 0.60
        assert textlayer.XY_CUT_MAX_DEPTH == 6

    def test_apply_config_updates_segment_constants(self):
        custom_cfg = {"segment": {"max_mda_pages": 45, "supporter_weight": 0.10}}
        config.apply_config(custom_cfg)
        assert segment.MAX_MDA_PAGES == 45
        assert segment.SUPPORTER_WEIGHT == 0.10
        # Reset back to default
        config.apply_config(config.DEFAULT_CONFIG)
        assert segment.MAX_MDA_PAGES == 60
        assert segment.SUPPORTER_WEIGHT == 0.06

    def test_apply_config_updates_verify_constants(self):
        custom_cfg = {"verify": {"orphan_start_frac_max": 0.05, "name_match_strong": 92}}
        config.apply_config(custom_cfg)
        assert verify.ORPHAN_START_FRAC_MAX == 0.05
        assert verify.NAME_MATCH_STRONG == 92
        # Reset back to default
        config.apply_config(config.DEFAULT_CONFIG)
        assert verify.ORPHAN_START_FRAC_MAX == 0.03
        assert verify.NAME_MATCH_STRONG == 88

    def test_apply_config_updates_ocr_and_pipeline_constants(self):
        custom_cfg = {"ocr": {"index_stride": 10, "default_dpi": 350}}
        config.apply_config(custom_cfg)
        assert ocr.INDEX_STRIDE == 10
        assert ocr.DEFAULT_DPI == 350
        assert pipeline.INDEX_STRIDE == 10
        # Reset back to default
        config.apply_config(config.DEFAULT_CONFIG)
        assert ocr.INDEX_STRIDE == 6
        assert ocr.DEFAULT_DPI == 300
        assert pipeline.INDEX_STRIDE == 6


class TestPrintConfigAndManifest:
    def test_format_config_dump_contains_provenance(self):
        cfg = config.load_config()
        dump = config.format_config_dump(cfg)
        assert "triage:" in dump
        assert "column_hist_bins" in dump
        assert "# [" in dump

    def test_config_for_manifest_is_serializable(self):
        cfg = config.load_config()
        manifest_cfg = config.config_for_manifest(cfg)
        assert isinstance(manifest_cfg, dict)
        import json
        serialized = json.dumps(manifest_cfg)
        assert len(serialized) > 100
        loaded = json.loads(serialized)
        assert loaded["triage"]["column_hist_bins"] == 120
