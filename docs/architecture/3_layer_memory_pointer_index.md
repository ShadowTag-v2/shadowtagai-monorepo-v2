# 3-Layer Memory Pointer Index

## Overview
A three-tier memory hierarchy designed to manage the extraction, organization, and retrieval of contextual memory across sessions while keeping the active context budget minimal.

## 1. Pointer Index Format
Indexes references to specific files, URIs, and code locations to quickly restore context without keeping the entire payload in the active context window.
- **Format**: `[Topic-ID] -> file:///path/to/resource#Lstart-Lend`

## 2. Write Discipline (Topic Layer)
- Synthesized learning logs categorized by subject or module. 
- Must be updated post-task immediately before context compaction.
- Use bullet points and precise constraints; avoid verbose narratives.

## 3. Archive Limits (Archive Layer)
- Archival artifacts should be strictly size-limited.
- No single archive index should exceed 500 lines to prevent context drag upon retrieval.
- Older entries must be pruned or compressed into high-level summaries by the `dream_consolidation` daemon.
