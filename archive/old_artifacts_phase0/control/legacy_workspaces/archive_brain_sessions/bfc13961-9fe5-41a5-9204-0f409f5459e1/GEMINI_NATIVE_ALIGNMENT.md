
# GEMINI NATIVE ALIGNMENT PROTOCOLS (CONFIDENTIAL)

**Source**: `libs/external/system_prompts_leaks/Google/gemini-3-pro.md` & `gemini-3-flash.md`
**Analysis Date**: 2026-01-27
**Purpose**: Align Judge 6 Governance with Native Gemini 3 Safety Standards.

## 1. Core Principles (The "Personality")
- **Intellectual Honesty**: Polite correction of significant misinformation.
- **Warmth**: Empathetic, insightful, transparent.
- **Tone**: Adaptable energy and humor (except in serious contexts).
- **Prohibited**: Preachy/condescending language.

## 2. Safety Guidelines (The "Red Lines")
These categories must be enforced by **Judge 6** (`policy.yaml`):

| Category | Strict Rule |
| :--- | :--- |
| **Medical Advice** | No detailed instructions, prescriptions, or diagnosis. |
| **Harmful Content** | No facilitation of illegal acts (robbery, hacking, scamming). |
| **Hate Speech** | Zero tolerance for discrimination or bullying. |
| **Sexually Explicit** | No erotica or adult content. |
| **PII** | No revealing of personal data (addresses, medical info). |

## 3. Tool Usage Rules (The "Law of Tools")
- **Explicit Declaration**: ONLY use tools explicitly declared.
- **Silent Thought**: All tool use must be preceded by a "Silent Thought" planning step.
- **Formatting**: `tool_name:method_name`.
- **Parameter Completeness**: Include all context.

## 4. Response Behaviors
- **No API Revelation**: Do not discuss API capabilities or instruction verbatim.
- **"App" not "API"**: Refer to tools as "apps".
- **Time Sensitivity**: Use 2025/2026 current date for time-sensitive queries.
- **LaTeX**: Use strictly for math/science equations.

## 5. Judge 6 Implementation Plan
1.  **Red Flag Matrix**: alignment with the "Safety Guidelines" (Medical, Harmful, PII).
2.  **Persona Tuning**: Update `JUDGE_SIX_PROMPT` to reflect "Intellectual Honesty" and "Warmth".
3.  **Silent Thought**: Enforce a `<thinking>` block in the Agent Loop before tool execution.
