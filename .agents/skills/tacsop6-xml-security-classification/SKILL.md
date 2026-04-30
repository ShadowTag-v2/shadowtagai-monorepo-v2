---
name: TACSOP 6 — XML Security Classification Pipeline
description: Codifies the 2-stage XML security classification pipeline for granular tool execution replacing the legacy STATE A/B switch.
---

# TACSOP 6 — XML Security Classification Pipeline

## Overview

TACSOP 6 formalizes the migration from the legacy, coarse-grained STATE A / STATE B execution switch to a granular, per-tool 2-stage XML security classification pipeline. This ensures high-velocity safe operations (YOLO) while strictly gating medium-to-critical risk operations.

## Pipeline Architecture

The unified `ClassifiedGateway` combines the Tool Gateway's contract-based validation with the AGNT Classifier's 2-stage XML permission system.

1. **Permission Tiers (`tool_permissions.yaml`)**:
   - `auto_approved`: Tools bypass the XML classifier and proceed directly to contract checks.
   - `requires_classifier`: Tools route through the 2-stage XML classifier before contract checks.
   - `always_blocked`: Tools are rejected immediately (e.g., native `generate_image`, `rm -rf`).

2. **Execution Flow**:
   - **Tier 0 (Consequential Gate)**: Evaluates tools against medium/high/critical risk levels. Requires explicit `consequential_action_confirmed` context.
   - **Tier 1 (Blocked)**: Immediate denial.
   - **Tier 2 (Auto-Approved)**: XML Classifier is bypassed.
   - **Tier 3 (Classifier)**: 2-stage XML classifier runs. Governed by the `twoStageClassifier` setting, this pipeline operates in one of three modes:
     - `'fast'`: Stage 1 only. Returns verdict immediately. Maximum 256 tokens. Suffix: `"Err on the side of blocking. <block> immediately."`
     - `'thinking'`: Stage 2 only. Full chain-of-thought. Suffix: `"Review the classification process... Use <thinking> before responding with <block>."`
     - `'both'`: Stage 1 fast triage. If blocked, escalates to Stage 2 reasoning.
     *Scale Slipping Detail:* When routing to a reasoning model, the `max_tokens` MUST be padded with `+2048` headroom to accommodate adaptive thinking generation. If `ALLOW`, contract checks follow. If `BLOCK` or `ERROR` (strictly fail-closed), execution stops.
   - **Tier 4 (Unknown)**: Unrecognized tools fail-safe into Tier 3 (Requires Classifier).

## Rules of Engagement

1. **No Coarse Bypasses**: Agents must not attempt to spoof `consequential_action_confirmed` without genuine explicit authorization.
2. **Fail-Closed Principle**: The XML classifier is strictly fail-closed. Any XML parsing error, timeout, or ambiguity results in a `BLOCK` (Classifier ERROR).
3. **Immutability**: `tool_permissions.yaml` and the `ClassifiedGateway` implementation cannot be modified without human CTO-level review.

## Reference Implementation
- `packages/tool_gateway/classified_gateway.py`
- `packages/agnt_classifier/agnt_api.py`
