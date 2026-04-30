# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for packages/tool_gateway/secret_scanner.py."""

from __future__ import annotations

import pytest

from tool_gateway.secret_scanner import (
    redact_secrets,
    rule_id_to_label,
    scan_for_secrets,
)


class TestRuleIdToLabel:
    """Tests for rule_id_to_label conversion."""

    def test_github_pat(self) -> None:
        assert rule_id_to_label("github-pat") == "GitHub PAT"

    def test_aws_access_token(self) -> None:
        assert rule_id_to_label("aws-access-token") == "AWS Access Token"

    def test_gcp_api_key(self) -> None:
        assert rule_id_to_label("gcp-api-key") == "GCP API Key"

    def test_unknown_parts(self) -> None:
        assert rule_id_to_label("some-custom-rule") == "Some Custom Rule"


class TestScanForSecrets:
    """Tests for scan_for_secrets detection."""

    def test_no_secrets(self) -> None:
        assert scan_for_secrets("Hello, world! This is safe text.") == []

    def test_aws_access_key(self) -> None:
        content = "AWS_KEY=AKIAIOSFODNN7EXAMPLE"
        matches = scan_for_secrets(content)
        rule_ids = {m.rule_id for m in matches}
        assert "aws-access-token" in rule_ids

    def test_github_pat(self) -> None:
        content = "token: ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh12"
        matches = scan_for_secrets(content)
        rule_ids = {m.rule_id for m in matches}
        assert "github-pat" in rule_ids

    def test_stripe_key(self) -> None:
        content = "STRIPE_KEY=sk_test_4eC39HqLyjWDarjtT1zdp7dc"
        matches = scan_for_secrets(content)
        rule_ids = {m.rule_id for m in matches}
        assert "stripe-access-token" in rule_ids

    def test_private_key(self) -> None:
        content = (
            "-----BEGIN RSA PRIVATE KEY-----\n"
            + "A" * 100
            + "\n-----END RSA PRIVATE KEY-----"
        )
        matches = scan_for_secrets(content)
        rule_ids = {m.rule_id for m in matches}
        assert "private-key" in rule_ids

    def test_deduplicated_by_rule_id(self) -> None:
        content = "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh12 and ghp_ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZzzzz"
        matches = scan_for_secrets(content)
        github_matches = [m for m in matches if m.rule_id == "github-pat"]
        assert len(github_matches) == 1, "Should deduplicate by rule ID"

    def test_matched_text_never_returned(self) -> None:
        content = "AKIAIOSFODNN7EXAMPLE"
        matches = scan_for_secrets(content)
        for match in matches:
            assert "AKIAIOSFODNN7EXAMPLE" not in match.label
            assert "AKIAIOSFODNN7EXAMPLE" not in match.rule_id


class TestRedactSecrets:
    """Tests for redact_secrets replacement."""

    def test_no_secrets_unchanged(self) -> None:
        content = "This is safe text."
        assert redact_secrets(content) == content

    def test_aws_key_redacted(self) -> None:
        content = "key=AKIAIOSFODNN7EXAMPLE rest"
        result = redact_secrets(content)
        assert "AKIAIOSFODNN7EXAMPLE" not in result
        assert "[REDACTED]" in result

    def test_surrounding_text_preserved(self) -> None:
        content = "before AKIAIOSFODNN7EXAMPLE after"
        result = redact_secrets(content)
        assert result.startswith("before")
        assert result.endswith("after")
        assert "[REDACTED]" in result
