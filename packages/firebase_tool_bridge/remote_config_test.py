# Copyright 2026 ShadowTagAI. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Tests for remote_config.py — Firebase Remote Config model parameter control."""

from __future__ import annotations


from firebase_tool_bridge.remote_config import ModelConfig


# ── Default config tests ───────────────────────────────────────


class TestModelConfigDefaults:
    """Tests for ModelConfig.default()."""

    def test_default_temperature(self) -> None:
        config = ModelConfig.default()
        assert config.temperature == 0.0

    def test_default_top_k(self) -> None:
        config = ModelConfig.default()
        assert config.top_k == 40

    def test_default_top_p(self) -> None:
        config = ModelConfig.default()
        assert config.top_p == 0.95

    def test_default_max_output_tokens(self) -> None:
        config = ModelConfig.default()
        assert config.max_output_tokens == 8192

    def test_default_model_name(self) -> None:
        config = ModelConfig.default()
        assert config.model_name == "gemini-2.5-flash"


# ── Validation / clamping tests ────────────────────────────────


class TestModelConfigValidation:
    """Tests for parameter validation and clamping."""

    def test_temperature_clamped_high(self) -> None:
        config = ModelConfig(temperature=5.0)
        assert config.temperature == 2.0

    def test_temperature_clamped_low(self) -> None:
        config = ModelConfig(temperature=-1.0)
        assert config.temperature == 0.0

    def test_top_k_clamped_high(self) -> None:
        config = ModelConfig(top_k=999)
        assert config.top_k == 100

    def test_top_k_clamped_low(self) -> None:
        config = ModelConfig(top_k=0)
        assert config.top_k == 1

    def test_top_p_clamped_high(self) -> None:
        config = ModelConfig(top_p=2.0)
        assert config.top_p == 1.0

    def test_top_p_clamped_low(self) -> None:
        config = ModelConfig(top_p=-0.5)
        assert config.top_p == 0.0

    def test_max_tokens_clamped_high(self) -> None:
        config = ModelConfig(max_output_tokens=999999)
        assert config.max_output_tokens == 65536

    def test_max_tokens_clamped_low(self) -> None:
        config = ModelConfig(max_output_tokens=0)
        assert config.max_output_tokens == 1

    def test_valid_values_pass_through(self) -> None:
        config = ModelConfig(temperature=0.7, top_k=50, top_p=0.8, max_output_tokens=4096)
        assert config.temperature == 0.7
        assert config.top_k == 50
        assert config.top_p == 0.8
        assert config.max_output_tokens == 4096


# ── Generation config conversion tests ─────────────────────────


class TestToGenerationConfig:
    """Tests for to_generation_config()."""

    def test_default_generation_config(self) -> None:
        config = ModelConfig.default()
        gen_config = config.to_generation_config()

        assert gen_config == {
            "temperature": 0.0,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 8192,
        }

    def test_custom_generation_config(self) -> None:
        config = ModelConfig(temperature=0.5, top_k=20, top_p=0.9, max_output_tokens=2048)
        gen_config = config.to_generation_config()

        assert gen_config["temperature"] == 0.5
        assert gen_config["topK"] == 20
        assert gen_config["topP"] == 0.9
        assert gen_config["maxOutputTokens"] == 2048


# ── Remote Config parsing tests ────────────────────────────────


class TestFromRemoteConfig:
    """Tests for ModelConfig.from_remote_config()."""

    def test_full_template(self) -> None:
        template = {
            "parameters": {
                "ai_function_calling_temperature": {
                    "defaultValue": {"value": "0.3"},
                },
                "ai_function_calling_top_k": {
                    "defaultValue": {"value": "30"},
                },
                "ai_function_calling_top_p": {
                    "defaultValue": {"value": "0.85"},
                },
                "ai_function_calling_max_output_tokens": {
                    "defaultValue": {"value": "4096"},
                },
                "ai_function_calling_model": {
                    "defaultValue": {"value": "gemini-2.5-pro"},
                },
            }
        }

        config = ModelConfig.from_remote_config(template)
        assert config.temperature == 0.3
        assert config.top_k == 30
        assert config.top_p == 0.85
        assert config.max_output_tokens == 4096
        assert config.model_name == "gemini-2.5-pro"

    def test_partial_template(self) -> None:
        """Missing params should fall back to defaults."""
        template = {
            "parameters": {
                "ai_function_calling_temperature": {
                    "defaultValue": {"value": "0.5"},
                },
            }
        }

        config = ModelConfig.from_remote_config(template)
        assert config.temperature == 0.5
        # Defaults for unspecified params
        assert config.top_k == 40
        assert config.top_p == 0.95
        assert config.max_output_tokens == 8192
        assert config.model_name == "gemini-2.5-flash"

    def test_empty_template(self) -> None:
        config = ModelConfig.from_remote_config({})
        assert config.temperature == 0.0
        assert config.model_name == "gemini-2.5-flash"

    def test_invalid_value(self) -> None:
        """Invalid values should fall back to defaults."""
        template = {
            "parameters": {
                "ai_function_calling_temperature": {
                    "defaultValue": {"value": "not_a_number"},
                },
            }
        }

        config = ModelConfig.from_remote_config(template)
        assert config.temperature == 0.0

    def test_missing_default_value(self) -> None:
        template = {
            "parameters": {
                "ai_function_calling_temperature": {},
            }
        }

        config = ModelConfig.from_remote_config(template)
        assert config.temperature == 0.0

    def test_out_of_range_value_clamped(self) -> None:
        """Values from RC that exceed bounds should be clamped."""
        template = {
            "parameters": {
                "ai_function_calling_temperature": {
                    "defaultValue": {"value": "10.0"},
                },
                "ai_function_calling_top_k": {
                    "defaultValue": {"value": "500"},
                },
            }
        }

        config = ModelConfig.from_remote_config(template)
        assert config.temperature == 2.0  # Clamped
        assert config.top_k == 100  # Clamped


# ── from_dict tests ────────────────────────────────────────────


class TestFromDict:
    """Tests for ModelConfig.from_dict()."""

    def test_full_dict(self) -> None:
        data = {
            "temperature": 0.7,
            "top_k": 50,
            "top_p": 0.9,
            "max_output_tokens": 4096,
            "model_name": "gemini-2.5-pro",
        }
        config = ModelConfig.from_dict(data)
        assert config.temperature == 0.7
        assert config.model_name == "gemini-2.5-pro"

    def test_empty_dict_defaults(self) -> None:
        config = ModelConfig.from_dict({})
        assert config.temperature == 0.0
        assert config.model_name == "gemini-2.5-flash"

    def test_partial_dict(self) -> None:
        config = ModelConfig.from_dict({"temperature": 1.0})
        assert config.temperature == 1.0
        assert config.top_k == 40  # Default
