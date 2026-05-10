# Anthropic Models Mapping

## Overview
This document maps internal model codenames extracted from `antModels.ts` to known Anthropic model releases.

## Model Mapping

| Codename | Public Name | Description |
|----------|-------------|-------------|
| `claude-3-7-sonnet-20250219` | Claude 3.7 Sonnet | The primary flagship model for coding, supports extended thinking. |
| `claude-3-5-sonnet-20241022` | Claude 3.5 Sonnet (New) | Previous primary flagship model. |
| `claude-3-5-sonnet-20240620` | Claude 3.5 Sonnet (Old) | Legacy flagship model. |
| `claude-3-5-haiku-20241022` | Claude 3.5 Haiku | Fast, efficient model for quick classification and simple tasks. |
| `claude-3-opus-20240229` | Claude 3 Opus | Legacy highly capable model. |

## Feature Support
- **Thinking**: Supported natively by `claude-3-7-sonnet-20250219`.
- **Computer Use**: Supported natively by 3.5 Sonnet and newer.
- **Prompt Caching**: Supported universally across 3.5+ models.

## AGNT Integration
AGNT will use this mapping within its internal routing layer to ensure that tasks like the "XML Classifier Side-Query" fall back to `claude-3-5-haiku-20241022` for latency, while complex synthesis falls back to `claude-3-7-sonnet-20250219` (or the equivalent Google `gemini-3.1-flash-lite-preview-thinking` model per the Workspace Alignment rules).
