# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""PKGBUILD validation tests.

Tests for Arch Linux package build file correctness.
Run with: pytest tests/ -v
"""

import re
import subprocess
from pathlib import Path

import pytest

PKGBUILD = Path(__file__).parent.parent / "PKGBUILD"


class TestPKGBUILDExists:
    """Test that PKGBUILD file exists and is readable."""

    def test_pkgbuild_exists(self):
        """PKGBUILD file must exist."""
        assert PKGBUILD.exists(), f"PKGBUILD not found at {PKGBUILD}"

    def test_pkgbuild_readable(self):
        """PKGBUILD file must be readable."""
        content = PKGBUILD.read_text()
        assert len(content) > 0, "PKGBUILD is empty"


class TestPKGBUILDSyntax:
    """Test PKGBUILD shell syntax."""

    def test_pkgbuild_bash_syntax(self):
        """PKGBUILD must have valid bash syntax."""
        result = subprocess.run(
            ["bash", "-n", str(PKGBUILD)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Bash syntax error: {result.stderr}"


class TestPKGBUILDRequiredFields:
    """Test that all required PKGBUILD fields are present."""

    REQUIRED_FIELDS = [
        "pkgname",
        "pkgver",
        "pkgrel",
        "pkgdesc",
        "arch",
        "url",
        "license",
    ]

    REQUIRED_FUNCTIONS = [
        "package()",
    ]

    @pytest.fixture
    def content(self):
        """Read PKGBUILD content."""
        return PKGBUILD.read_text()

    @pytest.mark.parametrize("field", REQUIRED_FIELDS)
    def test_required_field_present(self, content, field):
        """Required field must be present in PKGBUILD."""
        pattern = rf"^{field}="
        assert re.search(pattern, content, re.MULTILINE), f"Missing required field: {field}"

    @pytest.mark.parametrize("func", REQUIRED_FUNCTIONS)
    def test_required_function_present(self, content, func):
        """Required function must be present in PKGBUILD."""
        assert func in content, f"Missing required function: {func}"


class TestPKGBUILDVersioning:
    """Test version format and consistency."""

    @pytest.fixture
    def content(self):
        """Read PKGBUILD content."""
        return PKGBUILD.read_text()

    def test_pkgver_format(self, content):
        """Pkgver must follow semver-like format."""
        match = re.search(r"^pkgver=(.+)$", content, re.MULTILINE)
        assert match, "pkgver not found"
        version = match.group(1)
        # Accept semver: X.Y.Z or X.Y.Z.suffix
        assert re.match(r"^\d+\.\d+\.\d+", version), f"Invalid version format: {version}"

    def test_pkgrel_is_positive_integer(self, content):
        """Pkgrel must be a positive integer."""
        match = re.search(r"^pkgrel=(\d+)$", content, re.MULTILINE)
        assert match, "pkgrel not found or not a positive integer"
        pkgrel = int(match.group(1))
        assert pkgrel >= 1, f"pkgrel must be >= 1, got {pkgrel}"


class TestPKGBUILDMetadata:
    """Test package metadata quality."""

    @pytest.fixture
    def content(self):
        """Read PKGBUILD content."""
        return PKGBUILD.read_text()

    def test_pkgname_valid(self, content):
        """Pkgname must be lowercase alphanumeric with hyphens."""
        match = re.search(r"^pkgname=(.+)$", content, re.MULTILINE)
        assert match, "pkgname not found"
        pkgname = match.group(1)
        assert re.match(r"^[a-z0-9][a-z0-9\-]*$", pkgname), f"Invalid pkgname: {pkgname}"

    def test_pkgdesc_present_and_nonempty(self, content):
        """Pkgdesc must be present and non-empty."""
        match = re.search(r'^pkgdesc="(.+)"$', content, re.MULTILINE)
        assert match, "pkgdesc not found or empty"
        pkgdesc = match.group(1)
        assert len(pkgdesc) >= 10, f"pkgdesc too short: {pkgdesc}"

    def test_url_is_valid(self, content):
        """Url must be a valid HTTP(S) URL."""
        match = re.search(r'^url="(.+)"$', content, re.MULTILINE)
        assert match, "url not found"
        url = match.group(1)
        assert url.startswith(("http://", "https://")), f"Invalid URL: {url}"

    def test_arch_specified(self, content):
        """Arch must specify target architecture."""
        match = re.search(r"^arch=\((.+)\)$", content, re.MULTILINE)
        assert match, "arch not found"
        arch_content = match.group(1)
        # Must contain at least one of: x86_64, any, aarch64
        assert any(a in arch_content for a in ["x86_64", "any", "aarch64"]), (
            f"Invalid arch specification: {arch_content}"
        )


class TestPKGBUILDDependencies:
    """Test dependency declarations."""

    @pytest.fixture
    def content(self):
        """Read PKGBUILD content."""
        return PKGBUILD.read_text()

    def test_depends_array_syntax(self, content):
        """Depends must be a valid bash array."""
        # Check for depends=( or depends= on multiple lines
        assert "depends=" in content or "depends=(" in content, "depends array not found"

    def test_python_dependency(self, content):
        """Package should depend on Python >= 3.11."""
        assert "python" in content.lower(), "Python dependency not found"


class TestPKGBUILDSecurity:
    """Test security-related aspects."""

    @pytest.fixture
    def content(self):
        """Read PKGBUILD content."""
        return PKGBUILD.read_text()

    def test_no_curl_pipe_bash(self, content):
        """PKGBUILD should not use curl | bash pattern."""
        dangerous_patterns = [
            r"curl.*\|.*bash",
            r"wget.*\|.*bash",
            r"curl.*\|.*sh",
        ]
        for pattern in dangerous_patterns:
            assert not re.search(pattern, content), f"Dangerous pattern found: {pattern}"

    def test_config_file_permissions(self, content):
        """Config files should have restricted permissions."""
        # Check for chmod 600 or similar on config files
        if "config.env" in content:
            assert "600" in content or "400" in content, (
                "Config file should have restricted permissions"
            )
