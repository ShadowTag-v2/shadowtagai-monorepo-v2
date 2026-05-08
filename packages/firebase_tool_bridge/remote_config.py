# Copyright 2026 ShadowTagAI. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Remote Config — runtime model parameter control via Firebase Remote Config.

Provides remotely configurable generation parameters (temperature, top_k,
top_p, max_output_tokens) instead of hardcoded values.

The workflow spec mandates:
    "Temperature: 0.0 for deterministic tool selection"
    "Override via Firebase Remote Config if needed"

This module fetches config from Firebase Remote Config MCP or falls back
to sensible defaults. All parameters are validated and clamped.

Usage:
    config = ModelConfig.from_remote_config(template)
    # or with defaults:
    config = ModelConfig.default()
    print(config.temperature)  # 0.0
    print(config.to_generation_config())
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

# Firebase Remote Config parameter keys.
_RC_KEY_TEMPERATURE = "ai_function_calling_temperature"
_RC_KEY_TOP_K = "ai_function_calling_top_k"
_RC_KEY_TOP_P = "ai_function_calling_top_p"
_RC_KEY_MAX_OUTPUT_TOKENS = "ai_function_calling_max_output_tokens"
_RC_KEY_MODEL_NAME = "ai_function_calling_model"

# Default values per Firebase AI Logic best practices.
_DEFAULT_TEMPERATURE = 0.0  # Deterministic for tool selection
_DEFAULT_TOP_K = 40
_DEFAULT_TOP_P = 0.95
_DEFAULT_MAX_OUTPUT_TOKENS = 8192
_DEFAULT_MODEL_NAME = "gemini-2.5-flash"

# Validation bounds.
_TEMP_MIN = 0.0
_TEMP_MAX = 2.0
_TOP_K_MIN = 1
_TOP_K_MAX = 100
_TOP_P_MIN = 0.0
_TOP_P_MAX = 1.0
_MAX_TOKENS_MIN = 1
_MAX_TOKENS_MAX = 65536


def _clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value to [min_val, max_val]."""
    return max(min_val, min(value, max_val))


@dataclass(frozen=True, slots=True)
class ModelConfig:
    """Validated model generation configuration.

    All parameters are validated and clamped on construction.
    """

    temperature: float = _DEFAULT_TEMPERATURE
    top_k: int = _DEFAULT_TOP_K
    top_p: float = _DEFAULT_TOP_P
    max_output_tokens: int = _DEFAULT_MAX_OUTPUT_TOKENS
    model_name: str = _DEFAULT_MODEL_NAME

    def __post_init__(self) -> None:
        """Validate and clamp all parameters."""
        # Use object.__setattr__ because dataclass is frozen.
        object.__setattr__(
            self,
            "temperature",
            _clamp(self.temperature, _TEMP_MIN, _TEMP_MAX),
        )
        object.__setattr__(
            self,
            "top_k",
            int(_clamp(self.top_k, _TOP_K_MIN, _TOP_K_MAX)),
        )
        object.__setattr__(
            self,
            "top_p",
            _clamp(self.top_p, _TOP_P_MIN, _TOP_P_MAX),
        )
        object.__setattr__(
            self,
            "max_output_tokens",
            int(_clamp(self.max_output_tokens, _MAX_TOKENS_MIN, _MAX_TOKENS_MAX)),
        )

    def to_generation_config(self) -> dict[str, Any]:
        """Convert to Firebase/Gemini SDK generationConfig dict.

        Returns:
            Dict suitable for passing to the model's generationConfig.
        """
        return {
            "temperature": self.temperature,
            "topK": self.top_k,
            "topP": self.top_p,
            "maxOutputTokens": self.max_output_tokens,
        }

    @classmethod
    def default(cls) -> ModelConfig:
        """Create a ModelConfig with default values (deterministic tool calling)."""
        return cls()

    @classmethod
    def from_remote_config(
        cls,
        template: dict[str, Any],
    ) -> ModelConfig:
        """Create a ModelConfig from a Firebase Remote Config template.

        Extracts AI function-calling parameters from the Remote Config
        template returned by the Firebase MCP `remoteconfig_get_template` tool.

        Args:
            template: Remote Config template dict with 'parameters' key.

        Returns:
            ModelConfig with values from Remote Config, falling back to
            defaults for any missing or invalid parameters.

        Example template structure:
            {
                "parameters": {
                    "ai_function_calling_temperature": {
                        "defaultValue": {"value": "0.0"}
                    },
                    "ai_function_calling_model": {
                        "defaultValue": {"value": "gemini-2.5-flash"}
                    }
                }
            }
        """
        params = template.get("parameters", {})

        temperature = _extract_float(params, _RC_KEY_TEMPERATURE, _DEFAULT_TEMPERATURE)
        top_k = int(_extract_float(params, _RC_KEY_TOP_K, float(_DEFAULT_TOP_K)))
        top_p = _extract_float(params, _RC_KEY_TOP_P, _DEFAULT_TOP_P)
        max_tokens = int(_extract_float(params, _RC_KEY_MAX_OUTPUT_TOKENS, float(_DEFAULT_MAX_OUTPUT_TOKENS)))
        model_name = _extract_string(params, _RC_KEY_MODEL_NAME, _DEFAULT_MODEL_NAME)

        config = cls(
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            max_output_tokens=max_tokens,
            model_name=model_name,
        )

        logger.info(
            "Loaded ModelConfig from Remote Config: temp=%.2f, model=%s",
            config.temperature,
            config.model_name,
        )
        return config

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelConfig:
        """Create a ModelConfig from a flat dict.

        Args:
            data: Dict with keys matching field names.

        Returns:
            Validated ModelConfig.
        """
        return cls(
            temperature=float(data.get("temperature", _DEFAULT_TEMPERATURE)),
            top_k=int(data.get("top_k", _DEFAULT_TOP_K)),
            top_p=float(data.get("top_p", _DEFAULT_TOP_P)),
            max_output_tokens=int(data.get("max_output_tokens", _DEFAULT_MAX_OUTPUT_TOKENS)),
            model_name=str(data.get("model_name", _DEFAULT_MODEL_NAME)),
        )


def _extract_float(
    params: dict[str, Any],
    key: str,
    default: float,
) -> float:
    """Extract a float value from Remote Config parameters.

    Args:
        params: The 'parameters' dict from the RC template.
        key: The parameter key to look up.
        default: Default value if key is missing or invalid.

    Returns:
        Extracted float or default.
    """
    param = params.get(key)
    if param is None:
        return default

    default_value = param.get("defaultValue", {})
    value_str = default_value.get("value")

    if value_str is None:
        return default

    try:
        return float(value_str)
    except ValueError, TypeError:
        logger.warning(
            "Invalid Remote Config value for '%s': %r, using default %.2f",
            key,
            value_str,
            default,
        )
        return default


def _extract_string(
    params: dict[str, Any],
    key: str,
    default: str,
) -> str:
    """Extract a string value from Remote Config parameters.

    Args:
        params: The 'parameters' dict from the RC template.
        key: The parameter key to look up.
        default: Default value if key is missing.

    Returns:
        Extracted string or default.
    """
    param = params.get(key)
    if param is None:
        return default

    default_value = param.get("defaultValue", {})
    value_str = default_value.get("value")

    if value_str is None:
        return default

    return str(value_str)
