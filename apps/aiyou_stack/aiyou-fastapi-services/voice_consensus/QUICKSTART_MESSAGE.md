# Message Consensus for Claude Code

Process your messages through **Gemini, Perplexity, and SuperGrok** with circular peer review before Claude executes.

## Your Exact Flow

```

You type message
    ↓
Claude analyzes (Layer 1)
    ↓
Broadcasts to: Gemini, Perplexity, SuperGrok
    ↓
Each generates answer
    ↓
Review Round 1 (shift right):
  Gemini → reviews Perplexity
  Perplexity → reviews SuperGrok
  SuperGrok → reviews Gemini
    ↓
Review Round 2 (shift right again):
  Gemini → reviews SuperGrok
  Perplexity → reviews Gemini
  SuperGrok → reviews Perplexity
    ↓
Claude synthesizes final answer
    ↓
Ready for execution

```

## Setup (3 Steps)

### 1. Install Dependencies

```bash
cd voice_consensus  # or wherever you cloned the repo
source venv/bin/activate  # if not already activated
pip install -r requirements-text-only.txt

```

### 2. Set API Keys

```bash

# Required

export ANTHROPIC_API_KEY='sk-ant-...'

# Optional (add the ones you have)

export GOOGLE_API_KEY='AIza...'           # Gemini
export PERPLEXITY_API_KEY='pplx-...'      # Perplexity
export XAI_API_KEY='xai-...'              # SuperGrok

```

**Get API Keys:**


- Anthropic: https://console.anthropic.com/settings/keys


- Google (Gemini): https://aistudio.google.com/app/apikey


- Perplexity: https://www.perplexity.ai/settings/api


- xAI (Grok): https://x.ai/api

### 3. Run It

**Interactive mode:**

```bash
python message_consensus.py

```

Then type your message:

```

> Create a function to calculate fibonacci numbers

```

**Command-line mode:**

```bash
python message_consensus.py "Create a function to calculate fibonacci numbers"

```

## Example Output

```

================================================================================
MESSAGE CONSENSUS ORCHESTRATOR
================================================================================

[Layer 1] Claude analyzing your message...

[Layer 2] Broadcasting to Gemini, Perplexity, SuperGrok...
[Layer 2] Received 3 responses

[Layer 2.5] Round 1: Each model reviews right neighbor...
[Layer 2.5] Round 2: Each model reviews second neighbor...
[Layer 2.5] Completed 6 peer reviews

[Layer 3] Claude synthesizing final answer for execution...
[✓] Consensus complete - ready for execution

================================================================================
FINAL ANSWER (Ready for Execution)
================================================================================

[Claude's synthesized answer with code ready to execute]

================================================================================
Models consulted: 5
Peer reviews: 6
================================================================================

```

## What Gets Reviewed

**Round 1 (shift right once):**


- Gemini reviews what Perplexity said


- Perplexity reviews what SuperGrok said


- SuperGrok reviews what Gemini said

**Round 2 (shift right twice):**


- Gemini reviews what SuperGrok said


- Perplexity reviews what Gemini said


- SuperGrok reviews what Perplexity said

Result: **Every model reviews every other model** (6 total reviews for 3 models).

## Cost per Message

Approximate API calls:


- **Claude**: 2 calls (Layer 1 + Layer 3)


- **Gemini**: 3 calls (1 answer + 2 reviews)


- **Perplexity**: 3 calls (1 answer + 2 reviews)


- **SuperGrok**: 3 calls (1 answer + 2 reviews)

**Total: 11 API calls per message**

Estimated cost: **$0.15 - $0.50** per message depending on length.

### Cost Saving Tips

**Option 1: Claude + Just One Model**

```bash

# Only set these two:

export ANTHROPIC_API_KEY='...'
export GOOGLE_API_KEY='...'

# Runs with: Claude + Gemini only (~5 calls)

python message_consensus.py

```

**Option 2: Claude + Two Models**

```bash
export ANTHROPIC_API_KEY='...'
export GOOGLE_API_KEY='...'
export PERPLEXITY_API_KEY='...'

# Runs with: Claude + Gemini + Perplexity (~8 calls)

```

## When to Use This

**Use consensus for:**


- Complex coding tasks


- Architecture decisions


- Debugging hard problems


- Research questions


- High-stakes implementations

**Skip consensus for:**


- Simple questions


- Quick edits


- Obvious fixes


- Debugging typos

## Piping Messages Through Consensus

**Process a file:**

```bash
cat my_question.txt | xargs python message_consensus.py

```

**Chain with other commands:**

```bash
echo "Optimize this SQL query: SELECT * FROM users WHERE active=1" | \
  xargs python message_consensus.py

```

**Save output:**

```bash
python message_consensus.py "Explain ACID properties" > consensus_result.txt

```

## Troubleshooting

### "Module not found"

```bash
source venv/bin/activate
pip install -r requirements-text-only.txt

```

### "API key not found"

```bash

# Check if keys are set:

echo $ANTHROPIC_API_KEY
echo $GOOGLE_API_KEY

# If empty, export them:

export ANTHROPIC_API_KEY='your-key-here'

```

### "Running with Claude only"

This means other API keys aren't set. The system will work but won't use consensus.

Add the other keys to enable full consensus.

### Perplexity API errors

Perplexity has rate limits on free tier. If you hit limits:


1. Wait a few minutes


2. Or remove `PERPLEXITY_API_KEY` to skip it


3. System will work with Gemini + SuperGrok only

## Integration Ideas

### Use as Git Pre-commit Hook

Review your commit messages through consensus:

```bash
#!/bin/bash

# .git/hooks/prepare-commit-msg

COMMIT_MSG=$(cat $1)
python voice_consensus/message_consensus.py "$COMMIT_MSG" > /tmp/consensus.txt
cat /tmp/consensus.txt

```

### Use as Code Review Helper

```bash

# Review a diff

git diff | python message_consensus.py "Review this code change for issues"

```

### Use with Claude Code

Whenever you're about to ask Claude Code to do something complex:

```bash
python message_consensus.py "Your question here"

# Then use the consensus answer to guide Claude Code

```

## Files



- `message_consensus.py` - Main consensus orchestrator


- `requirements-text-only.txt` - Minimal dependencies


- `QUICKSTART_MESSAGE.md` - This file

## What's Different from Full Voice System

**Removed:**


- Voice capture


- Audio processing


- Whisper dependencies


- PyAudio/microphone setup

**Kept:**


- Multi-LLM consensus


- Circular peer review


- Claude synthesis


- Execution-ready output

**Focus:**


- Simple text message input


- Fast setup


- Direct integration with your workflow

---

**Ready to test!**

```bash
python message_consensus.py "Write a Python function to reverse a linked list"

```
