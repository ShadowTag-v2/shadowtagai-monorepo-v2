"""
TEGU VISION PROTOCOLS (RE-PUNCHED)
"""

LAYOUT_ANALYSIS_PROMPT = \"\"\"
PHASE 1: VISUAL ANCHORING
1. Identify the 'Key' (e.g., text 'Total:') and its visual location.
2. Define the 'Value Region' (e.g., 'The number immediately to the right of Total:').
3. Ignore noise (e.g., page numbers, footers) that falls outside these regions.
\"\"\"

EXTRACTION_PROMPT = \"\"\"
PHASE 2: REGIONAL EXTRACTION
Extract values ONLY from the defined regions.
If a table spans multiple pages, define the 'Header' anchor and 'Row' logic.
Return JSON matching: { "anchors": [...], "data": {...} }
\"\"\"
