# 4-Layer Context Compaction Specification

## Overview
Proactive token budget management via a reactive compaction pipeline to prevent context collapse and token exhaustion during long-running agent tasks.

## Layer 0: Microcompact
Bound globally by `/etc/antigravity/ANTIGRAVITY.md`. 
- Silently catch errors.
- Flush terminal buffers before proceeding to the next step.

## Layer 1: Duplicate Read Avoidance
- Maintain session memory of accessed files.
- Do not re-read files that have already been parsed within the active session.

## Layer 2: Reactive Compact
- Constantly evaluate context length.
- If context drag is sensed (i.e. slowing response times, confusion over older instructions), summarize the current state and open goals to a temporary file, clear history, and restart fresh autonomously.

## Layer 3: Compaction Timing
- **DO**: Compact AFTER research, before implementation.
- **DO**: Compact AFTER debugging, before new features.
- **DO**: Compact AFTER milestones.
- **NEVER**: Compact mid-implementation. Doing so loses variable names, file paths, and partial state. Time compaction precisely around natural breakpoints.
