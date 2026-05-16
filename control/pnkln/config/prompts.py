# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Standardized prompt templates for interacting with language models."""

# Primary prompt for the executive agent
EXECUTIVE_PROMPT = {
  "system": "pnkln multi-agent exec; enforce pnklnJR, ROI>=3x, enc_all.",
  "user": "{task}",
}

# Primary prompt for operational tasks
OPERATIONS_PROMPT = {
  "system": "pnkln ops; return json/md only.",
  "user": "{objective}\n{input}",
}

# Minimalist templates for different routing targets
TASK_TEMPLATES = {
  "dev": {"input_format": "goal, constraints", "output_format": "code_cells"},
  "ops": {"input_format": "context", "output_format": "json_report"},
  "legal": {"input_format": "filing_document", "output_format": "deadlines_and_tasks"},
}
