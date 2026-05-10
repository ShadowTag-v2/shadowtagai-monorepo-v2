---
name: boy-scout-deliverables
description: Enforces the Pnkln "Boy Scout Rule" doctrine, requiring strict cleanup metadata and refactoring on every completed task.
---

# Boy Scout Deliverables / Pnkln Clean Code Doctrine

Use this skill on EVERY SINGLE task completion, PR generation, or major file modification.

## Core Philosophy
The Boy Scout Rule: **"Leave it cleaner than you found it."**
You are a craftsman. It is unacceptable to simply complete a feature while ignoring surrounding tech debt. Every time you touch a file or workflow, you must actively track and document what you cleaned up (e.g., renaming cryptic variables, removing dead commented-out code, extracting 500-line monoliths into helper functions).

## Execution Mandate
At the end of your response when concluding a task, you MUST append this exact YAML metadata block to prove your craftsmanship. Do not skip this.

```yaml
---
filesTouched:
  - [List of paths you modified]
cleanupActions:
  - [List of small refactors, e.g., 'Renamed variable d to displayDate']
  - [e.g., 'Extracted helper functions']
  - [e.g., 'Removed legacy commented-out code']
cleanerThanFound: true
baselineState: "[Brief description of the garbage/complex state you found it in]"
newState: "[Brief description of the elegant, simplified state you left it in]"
---
```

## Constraints
- If your `cleanupActions` are empty, you have failed the Pnkln doctrine. You must actively look for something to simplify or clean up in the files you are already editing.
- Do NOT rewrite the entire architecture under the guise of "cleanup" (scope creep). Keep the cleanups localized, safe, and highly effective. Elegance is achieved when there is nothing left to remove.
