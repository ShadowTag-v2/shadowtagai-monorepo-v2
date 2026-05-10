#!/usr/bin/env bash
# scripts/prompt-repeat-wrapper.sh — Prompt Repetition Accuracy Boost
# ============================================================================
# Implements arXiv:2512.14982 — repeating prompts for non-reasoning models
# (flash, lite, mini) boosts accuracy 1–8%. Do NOT use with thinking models.
#
# Usage:
#   scripts/prompt-repeat-wrapper.sh <prompt-text> [--repeats N] [--model MODEL]
#   echo "prompt" | scripts/prompt-repeat-wrapper.sh --stdin [--repeats N]
#
# Default: 3 repetitions (sweet spot per paper)
# ============================================================================
set -euo pipefail

REPEATS=3
MODEL=""
PROMPT=""
USE_STDIN=false

# ── Parse Arguments ──────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repeats)
      REPEATS="$2"
      shift 2
      ;;
    --model)
      MODEL="$2"
      shift 2
      ;;
    --stdin)
      USE_STDIN=true
      shift
      ;;
    --help|-h)
      echo "Usage: scripts/prompt-repeat-wrapper.sh <prompt> [--repeats N] [--model MODEL]"
      echo "       echo 'prompt' | scripts/prompt-repeat-wrapper.sh --stdin [--repeats N]"
      echo ""
      echo "Options:"
      echo "  --repeats N    Number of prompt repetitions (default: 3)"
      echo "  --model MODEL  Model identifier for guard check"
      echo "  --stdin        Read prompt from stdin"
      echo ""
      echo "Guard: Refuses to repeat for reasoning/thinking models."
      exit 0
      ;;
    *)
      PROMPT="$1"
      shift
      ;;
  esac
done

# ── Read from stdin if flagged ──────────────────────────────
if [[ "$USE_STDIN" == "true" ]]; then
  PROMPT="$(cat)"
fi

if [[ -z "$PROMPT" ]]; then
  echo "❌ Error: No prompt provided. Use --help for usage." >&2
  exit 1
fi

# ── Guard: Block reasoning models ───────────────────────────
REASONING_PATTERNS=(
  "thinking"
  "reasoning"
  "extended"
  "pro"
  "opus"
  "claude-3.5"
  "claude-4"
  "gemini-2.5-pro"
  "o1"
  "o3"
  "deepseek-r1"
)

if [[ -n "$MODEL" ]]; then
  MODEL_LOWER="$(echo "$MODEL" | tr '[:upper:]' '[:lower:]')"
  for pattern in "${REASONING_PATTERNS[@]}"; do
    if [[ "$MODEL_LOWER" == *"$pattern"* ]]; then
      echo "⚠️  Guard: Model '${MODEL}' is a reasoning model. Prompt repetition skipped." >&2
      echo "$PROMPT"
      exit 0
    fi
  done
fi

# ── Build repeated prompt ────────────────────────────────────
SEPARATOR="

---

"

REPEATED_PROMPT="$PROMPT"
for ((i=2; i<=REPEATS; i++)); do
  REPEATED_PROMPT="${REPEATED_PROMPT}${SEPARATOR}${PROMPT}"
done

echo "$REPEATED_PROMPT"

# ── Metadata (to stderr for logging) ────────────────────────
echo "📊 Prompt repeated ${REPEATS}x (arXiv:2512.14982)" >&2
if [[ -n "$MODEL" ]]; then
  echo "   Model: ${MODEL}" >&2
fi
ORIGINAL_LEN=${#PROMPT}
REPEATED_LEN=${#REPEATED_PROMPT}
echo "   Original: ${ORIGINAL_LEN} chars → Repeated: ${REPEATED_LEN} chars" >&2
