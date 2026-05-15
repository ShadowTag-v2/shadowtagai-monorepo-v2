# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import re

file_path = "labs/ccleaks-mock/src/utils/permissions/yoloClassifier.ts"

with open(file_path) as f:
  content = f.read()

# Replace the simplistic RiskLevel logic with a more nuanced one based on the leak document's details
new_logic = """
  // Side-query LLM call that decides whether to auto-approve tool use
  const decision = await llmCall(template, { toolName, args, transcript });
  
  // Refined logic based on leaked details
  if (decision.includes('HIGH_RISK') || toolName === 'BashTool' && args.command.includes('rm')) {
      return RiskLevel.HIGH;
  }
  if (decision.includes('MEDIUM_RISK') || toolName === 'GlobTool' || toolName === 'GrepTool') {
      return RiskLevel.MEDIUM;
  }
  // Default to LOW for read-only or whitelisted operations
  return RiskLevel.LOW;
"""

updated_content = re.sub(
  r"  // Side-query LLM call that decides whether to auto-approve tool use.*?return RiskLevel\.LOW;",
  new_logic,
  content,
  flags=re.DOTALL,
)

with open(file_path, "w") as f:
  f.write(updated_content)

print("yoloClassifier.ts refined successfully.")
