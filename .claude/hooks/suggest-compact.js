#!/usr/bin/env node
// suggest-compact.js — ECC strategic compaction advisor
// Source: everything-claude-code/skills/strategic-compact
// Adapted for Antigravity monorepo hooks
//
// This hook tracks tool call count and suggests /compact at logical intervals.
// Runs on PreToolUse for Write/Edit operations.

const fs = require('fs');
const path = require('path');

const THRESHOLD = parseInt(process.env.COMPACT_THRESHOLD || '50', 10);
const REMINDER_INTERVAL = 25;
const STATE_FILE = path.join(
  process.env.HOME || '/tmp',
  '.claude',
  '.compact-state.json'
);

function loadState() {
  try {
    if (fs.existsSync(STATE_FILE)) {
      return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
    }
  } catch (e) {
    // Corrupt state file, reset
  }
  return { toolCalls: 0, lastSuggested: 0, sessionId: null };
}

function saveState(state) {
  try {
    const dir = path.dirname(STATE_FILE);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
  } catch (e) {
    // Non-critical, ignore
  }
}

function main() {
  // Read hook input from stdin
  let input = '';
  try {
    input = fs.readFileSync('/dev/stdin', 'utf8');
  } catch (e) {
    // No stdin available
  }

  let hookInput = {};
  try {
    hookInput = JSON.parse(input);
  } catch (e) {
    // Not JSON, continue with defaults
  }

  const currentSessionId = hookInput.session_id || 'unknown';
  const state = loadState();

  // Reset counter on new session
  if (state.sessionId !== currentSessionId) {
    state.toolCalls = 0;
    state.lastSuggested = 0;
    state.sessionId = currentSessionId;
  }

  state.toolCalls++;
  saveState(state);

  // Check if we should suggest compaction
  const output = {};

  if (state.toolCalls >= THRESHOLD) {
    const callsSinceLastSuggestion = state.toolCalls - state.lastSuggested;

    if (
      state.lastSuggested === 0 ||
      callsSinceLastSuggestion >= REMINDER_INTERVAL
    ) {
      state.lastSuggested = state.toolCalls;
      saveState(state);

      output.hookSpecificOutput = {
        hookEventName: 'PreToolUse',
        additionalContext: [
          `⚡ Context checkpoint: ${state.toolCalls} tool calls this session.`,
          'Consider running /compact if you are:',
          '  - Transitioning between task phases (research→plan→implement)',
          '  - Done debugging and moving to new work',
          '  - Noticing slower or less coherent responses',
          'Skip if mid-implementation — losing partial state is costly.',
          'Tip: /compact "Focus on [next task]" to guide the summary.',
        ].join('\n'),
      };
    }
  }

  // Output JSON for hook system
  process.stdout.write(JSON.stringify(output));
}

main();
