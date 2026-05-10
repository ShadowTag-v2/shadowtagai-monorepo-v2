# Voice STT Input

## Overview
Harvested from `voice.ts` and `voiceStreamSTT.ts`. While `gemini-live-api-dev` handles building voice apps, this skill dictates how the agent handles voice transcriptions fed into its own context.

## Protocol
1. If the input contains `[VOICE TRANSCRIPT]`, the agent must account for potential STT hallucinations or phonetic misspellings (e.g., "right file" instead of "write file").
2. Keyterm detection (e.g., "stop", "undo") should trigger immediate safety circuit breakers.
3. Keep responses conversational and concise if the input modality indicates it was spoken.
