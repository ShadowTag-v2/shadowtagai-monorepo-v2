# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from src.codepmcs import CodePMCS
from src.codepmcs.remediator import Remediator
from src.codepmcs.scanner import CodeScanner


def test_codepmcs_initialization():
    pmcs = CodePMCS()
    assert isinstance(pmcs.scanner, CodeScanner)
    assert isinstance(pmcs.remediator, Remediator)


def test_scanner_basic_scan(tmp_path):
    # Create a dummy file
    d = tmp_path / "src"
    d.mkdir()
    p = d / "bad_code.py"
    p.write_text("import os\nprint('hello')")

    scanner = CodeScanner()
    results = scanner.scan_directory(str(d))

    assert len(results) > 0
    # Our mock scanner should find "print(" usage
    assert any("print() statement detected" in r.description for r in results)


def test_remediator_fix():
    remediator = Remediator()
    result = remediator.remediate("print('foo')", "Remove print statements")
    assert result.success is True
    assert "Refactored" in result.fixed_code
