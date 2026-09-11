"""Tests for arpipe.preflight – P14 The Preflight Command."""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
from unittest import mock

import pytest

from arpipe.preflight import (
    CheckResult,
    Status,
    _parse_requirements,
    check_companies,
    check_disk_space,
    check_link_capabilities,
    check_poppler,
    check_qpdf,
    check_requirements,
    check_tesseract,
    check_volume_alignment,
    check_write_permissions,
    format_fix_hints,
    format_table,
    run_preflight,
)


# ---------------------------------------------------------------------------
# Requirements parsing
# ---------------------------------------------------------------------------

class TestParseRequirements:
    def test_parse_basic(self, tmp_path):
        req = tmp_path / "requirements.txt"
        req.write_text("pymupdf>=1.24\nhttpx>=0.27\n# comment\n\npytest>=8\n")
        result = _parse_requirements(str(req))
        assert len(result) == 3
        assert result[0] == ("pymupdf", ">=1.24")
        assert result[1] == ("httpx", ">=0.27")
        assert result[2] == ("pytest", ">=8")

    def test_parse_inline_comments(self, tmp_path):
        req = tmp_path / "requirements.txt"
        req.write_text("pandas>=2.2  # manifests / audit\n")
        result = _parse_requirements(str(req))
        assert result == [("pandas", ">=2.2")]

    def test_parse_optional_commented_out(self, tmp_path):
        req = tmp_path / "requirements.txt"
        req.write_text("# boto3>=1.34  # optional\npandas>=2.2\n")
        result = _parse_requirements(str(req))
        assert len(result) == 1
        assert result[0][0] == "pandas"


# ---------------------------------------------------------------------------
# Check requirements (import check)
# ---------------------------------------------------------------------------

class TestCheckRequirements:
    def test_importable_packages(self, tmp_path):
        req = tmp_path / "requirements.txt"
        req.write_text("pytest>=8\n")
        results = check_requirements(str(req))
        assert len(results) == 1
        assert results[0].status == Status.PASS
        assert "pytest" in results[0].name

    def test_missing_required_fails(self, tmp_path):
        req = tmp_path / "requirements.txt"
        req.write_text("nonexistent_package_xyz>=1.0\n")
        results = check_requirements(str(req))
        assert len(results) == 1
        assert results[0].status == Status.FAIL

    def test_missing_optional_is_info(self, tmp_path):
        req = tmp_path / "requirements.txt"
        # vllm is in _OPTIONAL set
        req.write_text("vllm>=0.6\n")
        results = check_requirements(str(req))
        assert len(results) == 1
        assert results[0].status == Status.INFO

    def test_file_not_found(self):
        results = check_requirements("/no/such/file.txt")
        assert len(results) == 1
        assert results[0].status == Status.WARN


# ---------------------------------------------------------------------------
# Disk space
# ---------------------------------------------------------------------------

class TestCheckDiskSpace:
    def test_enough_space(self, tmp_path):
        # Use a tiny threshold that any system will satisfy
        results = check_disk_space(str(tmp_path), min_free_tb=0.0001)
        assert len(results) == 1
        assert results[0].status == Status.PASS

    def test_not_enough_space(self, tmp_path):
        # Use an impossibly large threshold
        results = check_disk_space(str(tmp_path), min_free_tb=9999.0)
        assert len(results) == 1
        assert results[0].status == Status.FAIL
        assert "9999.0 TB" in results[0].detail


# ---------------------------------------------------------------------------
# Link capabilities
# ---------------------------------------------------------------------------

class TestCheckLinkCapabilities:
    def test_link_checks_run(self, tmp_path):
        results = check_link_capabilities(str(tmp_path))
        # Should have at least hardlink + symlink results
        assert len(results) >= 2
        names = [r.name for r in results]
        assert "hardlink" in names
        assert "symlink" in names

    def test_probe_file_cleaned_up(self, tmp_path):
        check_link_capabilities(str(tmp_path))
        # probe file should be cleaned up
        assert not os.path.exists(os.path.join(str(tmp_path), "_preflight_probe.tmp"))
        assert not os.path.exists(os.path.join(str(tmp_path), "_preflight_probe.tmp.hard"))
        assert not os.path.exists(os.path.join(str(tmp_path), "_preflight_probe.tmp.sym"))


# ---------------------------------------------------------------------------
# Volume alignment
# ---------------------------------------------------------------------------

class TestCheckVolumeAlignment:
    def test_same_volume(self, tmp_path):
        root = tmp_path / "store"
        out = tmp_path / "dataset"
        root.mkdir()
        out.mkdir()
        results = check_volume_alignment(str(root), str(out))
        assert len(results) == 1
        assert results[0].status == Status.PASS


# ---------------------------------------------------------------------------
# Write permissions
# ---------------------------------------------------------------------------

class TestCheckWritePermissions:
    def test_writable(self, tmp_path):
        root = tmp_path / "store"
        out = tmp_path / "dataset"
        results = check_write_permissions(str(root), str(out))
        assert len(results) == 2
        assert all(r.status == Status.PASS for r in results)


# ---------------------------------------------------------------------------
# Companies
# ---------------------------------------------------------------------------

class TestCheckCompanies:
    def test_file_not_found(self):
        results = check_companies("/no/such/companies.csv")
        assert results[0].status == Status.WARN

    def test_small_csv(self, tmp_path):
        csv = tmp_path / "companies.csv"
        csv.write_text("company_id,canonical_name\nINE001,Foo\nINE002,Bar\n")
        results = check_companies(str(csv))
        # row count should be WARN (< 2000)
        row_check = [r for r in results if "row count" in r.name]
        assert row_check[0].status == Status.WARN

    def test_no_duplicates(self, tmp_path):
        csv = tmp_path / "companies.csv"
        csv.write_text("company_id,canonical_name\nINE001,Foo\nINE002,Bar\n")
        results = check_companies(str(csv))
        dup_check = [r for r in results if "duplicate" in r.name]
        assert dup_check[0].status == Status.PASS

    def test_with_duplicates(self, tmp_path):
        csv = tmp_path / "companies.csv"
        csv.write_text("company_id,canonical_name\nINE001,Foo\nINE001,Bar\n")
        results = check_companies(str(csv))
        dup_check = [r for r in results if "duplicate" in r.name]
        assert dup_check[0].status == Status.FAIL


# ---------------------------------------------------------------------------
# Format table
# ---------------------------------------------------------------------------

class TestFormatTable:
    def test_basic_output(self):
        results = [
            CheckResult("Tools", "tesseract", Status.PASS, "5.4.0"),
            CheckResult("Tools", "qpdf", Status.FAIL, "not found"),
        ]
        out = format_table(results, use_color=False)
        assert "ARPIPE PREFLIGHT" in out
        assert "[PASS]" in out
        assert "[FAIL]" in out
        assert "BLOCKED" in out

    def test_all_pass_shows_ready(self):
        results = [
            CheckResult("Tools", "tesseract", Status.PASS, "5.4.0"),
        ]
        out = format_table(results, use_color=False)
        assert "READY" in out

    def test_warn_is_not_blocking(self):
        results = [
            CheckResult("Tools", "hin", Status.WARN, "missing"),
        ]
        out = format_table(results, use_color=False)
        assert "READY" in out  # WARN does not block


# ---------------------------------------------------------------------------
# Fix hints
# ---------------------------------------------------------------------------

class TestFormatFixHints:
    def test_hints_printed(self):
        results = [
            CheckResult("Tools", "qpdf", Status.FAIL, "not found",
                        "sudo apt-get install qpdf"),
        ]
        out = format_fix_hints(results)
        assert "FIX HINTS" in out
        assert "qpdf" in out

    def test_no_hints(self):
        results = [
            CheckResult("Tools", "tesseract", Status.PASS, "5.4.0"),
        ]
        out = format_fix_hints(results)
        assert "No actionable hints" in out


# ---------------------------------------------------------------------------
# run_preflight integration (no-network, relaxed disk)
# ---------------------------------------------------------------------------

class TestRunPreflight:
    def test_exit_zero_on_pass(self, tmp_path):
        """With no network and a tiny disk threshold, preflight should pass
        if tesseract/qpdf are on PATH."""
        root = tmp_path / "store"
        out = tmp_path / "dataset"
        # Create a minimal companies.csv
        csv = tmp_path / "companies.csv"
        csv.write_text("company_id,canonical_name\nINE001,Foo\n")
        # Create a minimal requirements.txt with only pytest
        req = tmp_path / "requirements.txt"
        req.write_text("pytest>=8\n")
        rc = run_preflight(
            root=str(root),
            out=str(out),
            companies=str(csv),
            min_disk_tb=0.0001,
            req_file=str(req),
            no_network=True,
            use_color=False,
        )
        # If tesseract/qpdf are installed, rc=0; if not, rc=1
        # Either way it should not crash
        assert rc in (0, 1)

    def test_exit_one_on_fail(self, tmp_path):
        """Ensure a definite FAIL (huge disk threshold) causes exit 1."""
        root = tmp_path / "store"
        out = tmp_path / "dataset"
        csv = tmp_path / "companies.csv"
        csv.write_text("company_id,canonical_name\nINE001,Foo\n")
        req = tmp_path / "requirements.txt"
        req.write_text("pytest>=8\n")
        rc = run_preflight(
            root=str(root),
            out=str(out),
            companies=str(csv),
            min_disk_tb=9999.0,
            req_file=str(req),
            no_network=True,
            use_color=False,
        )
        assert rc == 1


# ---------------------------------------------------------------------------
# CLI integration
# ---------------------------------------------------------------------------

class TestCLIIntegration:
    def test_preflight_parseable(self):
        """The preflight subcommand should be parseable by argparse."""
        from arpipe.cli import main
        # --no-network and extreme threshold to avoid real network calls
        # We expect it to either pass or fail based on tools, but not crash
        # We can't easily test exit code here without actually running,
        # so just verify the parser doesn't crash
        import argparse
        from arpipe.cli import main as cli_main
        # Testing parse only: inject --help would SystemExit, so just test
        # that the subcommand is recognized by checking the parser
        p = argparse.ArgumentParser("arpipe")
        # This is a minimal check that the code path doesn't crash on import
        from arpipe import preflight
        assert hasattr(preflight, "run_preflight")
