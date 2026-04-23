# tests/unit/test_pr_review_webhook.py
"""Unit tests for Sovereign PR Review Webhook — enforce_m1_max_constraints."""

from __future__ import annotations

import pytest


# ── enforce_m1_max_constraints ─────────────────────────────────────────────


class TestEnforceM1MaxConstraints:
    """Tests for the SRAM kernel panic guard."""

    @pytest.fixture(autouse=True)
    def _import_function(self) -> None:
        from apps.counselconduit.api.pr_review_webhook import enforce_m1_max_constraints

        self.fn = enforce_m1_max_constraints

    def test_safe_standard_bert(self) -> None:
        """Standard BERT (512 x 768) should fit in 12.5MB SRAM."""
        result = self.fn(seq_len=512, dim=768)
        assert result["safe"] is True
        assert result["severity"] == "✅ Safe"
        assert result["required_bytes"] == 512 * 768 * 4 * 3  # 4,718,592

    def test_unsafe_large_model(self) -> None:
        """4096 x 2048 should exceed 12.5MB SRAM and trigger kernel panic guard."""
        result = self.fn(seq_len=4096, dim=2048)
        assert result["safe"] is False
        assert "🔴" in result["severity"]
        assert "halved_seq_len" in result
        assert result["halved_seq_len"] < 4096

    def test_exact_boundary(self) -> None:
        """Matrix exactly at the 12.5MB boundary is considered safe."""
        # 12,582,912 / (4 * 3) = 1,048,576 total elements
        # sqrt(1,048,576) = 1024 → seq_len=1024, dim=1024 → exactly 12,582,912 bytes
        result = self.fn(seq_len=1024, dim=1024)
        assert result["safe"] is True
        assert result["required_bytes"] == 12_582_912

    def test_one_byte_over_boundary(self) -> None:
        """One element over the boundary should be unsafe."""
        result = self.fn(seq_len=1025, dim=1024)
        assert result["safe"] is False

    def test_halved_seq_len_fits(self) -> None:
        """The halved_seq_len recommendation should always fit in SRAM."""
        result = self.fn(seq_len=8192, dim=1536)
        assert result["safe"] is False
        halved = result["halved_seq_len"]
        # Verify the halved suggestion actually fits
        check = self.fn(seq_len=halved, dim=1536)
        assert check["safe"] is True

    def test_tiny_model_safe(self) -> None:
        """Very small model should be safe with plenty of headroom."""
        result = self.fn(seq_len=64, dim=128)
        assert result["safe"] is True
        assert result["required_bytes"] == 64 * 128 * 4 * 3  # 98,304

    def test_zero_dimensions(self) -> None:
        """Zero-sized tensor should be safe (edge case)."""
        result = self.fn(seq_len=0, dim=768)
        assert result["safe"] is True
        assert result["required_bytes"] == 0

    def test_message_includes_mb_for_unsafe(self) -> None:
        """Unsafe result message should include the MB calculation."""
        result = self.fn(seq_len=4096, dim=2048)
        assert "MB" in result["message"]
        assert "12.5MB" in result["message"]

    def test_percentage_for_safe(self) -> None:
        """Safe result message should include percentage of limit used."""
        result = self.fn(seq_len=512, dim=768)
        assert "%" in result["message"]


# ── Webhook Signature Verification ─────────────────────────────────────────


class TestWebhookSignature:
    """Tests for HMAC-SHA256 signature verification."""

    @pytest.fixture(autouse=True)
    def _import_function(self) -> None:
        from apps.counselconduit.api.pr_review_webhook import _verify_github_signature

        self.verify = _verify_github_signature

    def test_no_secret_allows_all(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """With no GITHUB_WEBHOOK_SECRET, all signatures pass (dev mode)."""
        import apps.counselconduit.api.pr_review_webhook as mod

        monkeypatch.setattr(mod, "GITHUB_WEBHOOK_SECRET", "")
        assert self.verify(b"any payload", "sha256=anything") is True

    def test_valid_signature(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Valid HMAC-SHA256 signature should pass."""
        import hashlib
        import hmac as hmac_mod

        import apps.counselconduit.api.pr_review_webhook as mod

        secret = "test-secret-key"
        monkeypatch.setattr(mod, "GITHUB_WEBHOOK_SECRET", secret)

        payload = b'{"action": "opened"}'
        expected = "sha256=" + hmac_mod.new(secret.encode(), payload, hashlib.sha256).hexdigest()

        assert self.verify(payload, expected) is True

    def test_invalid_signature(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Invalid signature should be rejected."""
        import apps.counselconduit.api.pr_review_webhook as mod

        monkeypatch.setattr(mod, "GITHUB_WEBHOOK_SECRET", "real-secret")
        assert self.verify(b"payload", "sha256=deadbeef") is False
