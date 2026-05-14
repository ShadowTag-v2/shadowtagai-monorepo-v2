#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

from prompt_repeat import repeat_prompt

EXTRACTION_TASK = "Extract invoice number, total, and due date as JSON."
EXTRACTION_INPUT = "Invoice #8821. Total due is $4,120.00. Payment due April 30, 2026."

print("=== x2 ===")
print(repeat_prompt(f"TASK: {EXTRACTION_TASK}\nINPUT: {EXTRACTION_INPUT}", times=2))
print("\n=== x3 ===")
print(repeat_prompt(f"TASK: {EXTRACTION_TASK}\nINPUT: {EXTRACTION_INPUT}", times=3))
