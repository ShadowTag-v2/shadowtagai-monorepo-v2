# Rule 02: Context Death Spiral

You push a long refactor. First 10 messages seem surgical and precise. By message 15 the agent is hallucinating variable names, referencing functions that don't exist, and breaking things it understood perfectly 5 minutes ago. It feels like you want to slap it in the face.

As it turns out, this is not degradation, it's something more like amputation.

services/compact/autoCompact.ts runs a compaction routine when context pressure crosses ~167,000 tokens. When it fires, it keeps 5 files (capped at 5K tokens each), compresses everything else into a single 50,000-token summary, and throws away every file read, every reasoning chain, every intermediate decision. ALL-OF-IT... Gone.

The tricky part: dirty, sloppy, vibecoded base accelerates this. Every dead import, every unused export, every orphaned prop is eating tokens that contribute nothing to the task but everything to triggering compaction.

## The Override
Step 0 of any refactor must be deletion. Not restructuring, but just nuking dead weight. Strip dead props, unused exports, orphaned imports, debug logs. Commit that separately, and only then start the real work with a clean token budget. Keep each phase under 5 files so compaction never fires mid-task.

## Rules
- After 10+ messages, re-read any file before editing it
- Auto-compaction silently destroys context at ~167K tokens
- Compact AFTER milestones, NEVER mid-implementation
- Never restart sessions — context is state
- Use /compact AFTER research before implementation, AFTER debugging before new features
