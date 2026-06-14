"""Tests for hardened error-handling and edge-case paths."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from classmark.core import (
    detect_banners,
    detect_portion_marks,
    scan,
    validate_portion_mark,
)
from cognis_mil import ClassificationBanner


# ---------------------------------------------------------------------------
# validate_portion_mark -- edge cases
# ---------------------------------------------------------------------------

def test_validate_pm_empty_string():
    ok, msg = validate_portion_mark("")
    assert not ok
    assert msg  # should return a descriptive message


def test_validate_pm_non_string():
    ok, msg = validate_portion_mark(None)  # type: ignore[arg-type]
    assert not ok
    assert "str" in msg.lower() or "string" in msg.lower()


def test_validate_pm_empty_parens():
    ok, msg = validate_portion_mark("()")
    assert not ok


def test_validate_pm_whitespace_only_inner():
    ok, msg = validate_portion_mark("(   )")
    assert not ok


# ---------------------------------------------------------------------------
# detect_banners / detect_portion_marks -- None / empty guards
# ---------------------------------------------------------------------------

def test_detect_banners_none():
    result = detect_banners(None)  # type: ignore[arg-type]
    assert result == []


def test_detect_banners_empty():
    assert detect_banners("") == []


def test_detect_portion_marks_none():
    result = detect_portion_marks(None)  # type: ignore[arg-type]
    assert result == []


def test_detect_portion_marks_empty():
    assert detect_portion_marks("") == []


# ---------------------------------------------------------------------------
# scan() -- missing / invalid target exits with code 2
# ---------------------------------------------------------------------------

def test_scan_missing_target_exits():
    with pytest.raises(SystemExit) as exc_info:
        scan("C:\\classmark_nonexistent_path_xyz_abc_999")
    assert exc_info.value.code == 2


def test_scan_none_target_exits():
    with pytest.raises(SystemExit) as exc_info:
        scan(None)
    assert exc_info.value.code == 2


# ---------------------------------------------------------------------------
# scan() -- empty directory produces a valid result with zero findings
# ---------------------------------------------------------------------------

def test_scan_empty_directory():
    with tempfile.TemporaryDirectory() as d:
        r = scan(d)
    assert r.items_scanned == 0
    assert r.total_findings() == 0
    assert r.composite_score == 0.0


# ---------------------------------------------------------------------------
# scan() -- single clean file (no portion marks, no banners) -> no findings
# ---------------------------------------------------------------------------

def test_scan_plain_file_no_findings():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "plain.txt"
        p.write_text("This is a plain text file with no markings.\n")
        r = scan(d)
    # A file with no portion marks and no banners should not trigger CM-NOBANNER
    ids = {f.id for f in r.findings}
    assert "CM-NOBANNER" not in ids


# ---------------------------------------------------------------------------
# ClassificationBanner -- None list fields are coerced safely
# ---------------------------------------------------------------------------

def test_banner_none_lists_coerced():
    b = ClassificationBanner(
        level="UNCLASSIFIED",
        sci=None,    # type: ignore[arg-type]
        sap=None,    # type: ignore[arg-type]
        dissem=None, # type: ignore[arg-type]
        nonic=None,  # type: ignore[arg-type]
    )
    rendered = b.render()
    assert rendered == "UNCLASSIFIED"


def test_banner_invalid_level():
    b = ClassificationBanner(level="MAGIC")
    ok, errs = b.validate()
    assert not ok
    assert any("MAGIC" in e for e in errs)


def test_banner_unclassified_with_sci_fails():
    b = ClassificationBanner(level="UNCLASSIFIED", sci=["ALPHA"])
    ok, errs = b.validate()
    assert not ok
    assert any("SCI" in e or "sci" in e.lower() for e in errs)


# ---------------------------------------------------------------------------
# CLI -- missing target prints to stderr and exits non-zero (subprocess)
# ---------------------------------------------------------------------------

def test_cli_missing_target_exit_code():
    """classmark on a non-existent path should exit with code 2."""
    result = subprocess.run(
        [sys.executable, "-m", "classmark", "C:\\classmark_no_such_dir_xyz_999"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert result.stderr  # should have a message on stderr
    assert "error" in result.stderr.lower()


def test_cli_out_file_written():
    """--out flag writes JSON output to a file."""
    with tempfile.TemporaryDirectory() as d:
        out_file = str(Path(d) / "out.json")
        demos = str(Path(__file__).parent.parent / "demos")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "classmark",
                demos,
                "--format",
                "json",
                "--out",
                out_file,
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        content = Path(out_file).read_text(encoding="utf-8")
        data = json.loads(content)
        assert "findings" in data
