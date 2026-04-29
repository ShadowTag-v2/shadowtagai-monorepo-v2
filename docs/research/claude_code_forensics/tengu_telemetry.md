# Tengu Telemetry Catalog

## Overview
This catalog documents the telemetry events prefixed with `tengu_` extracted from the Claude Code audit. It serves as a blueprint for implementing similar telemetry tracking within the AGNT Monorepo.

## Extraction List

### System & App Lifecycle
- `tengu_app_startup`
- `tengu_app_exit`
- `tengu_app_backgrounded`
- `tengu_app_foregrounded`
- `tengu_version_check_success`
- `tengu_version_check_failure`
- `tengu_version_config`
- `tengu_update_check`
- `tengu_uncaught_exception`
- `tengu_unhandled_rejection`

### Authentication & Config
- `tengu_auth_flow_started`
- `tengu_auth_flow_completed`
- `tengu_auth_flow_failed`
- `tengu_auth_token_refresh`
- `tengu_vscode_cc_auth`
- `tengu_vscode_onboarding`
- `tengu_config_changed`

### Tools & Execution
- `tengu_tool_used`
- `tengu_tool_failed`
- `tengu_tool_timeout`
- `tengu_tool_permission_denied`
- `tengu_unexpected_tool_result`
- `tengu_bash_execution_started`
- `tengu_bash_execution_completed`
- `tengu_bash_execution_failed`
- `tengu_file_read`
- `tengu_file_written`
- `tengu_file_deleted`

### Planning & Reasoning
- `tengu_ultraplan_launched`
- `tengu_ultraplan_completed`
- `tengu_ultraplan_failed`
- `tengu_ultraplan_keyword`
- `tengu_ultraplan_model`
- `tengu_ultrathink`
- `tengu_thinking_started`
- `tengu_thinking_completed`

### Worktree & Git
- `tengu_worktree_detection`
- `tengu_worktree_created`
- `tengu_worktree_kept`
- `tengu_worktree_mode`
- `tengu_worktree_removed`
- `tengu_worktree_cleanup`

### Models & API
- `tengu_api_request_started`
- `tengu_api_request_completed`
- `tengu_api_request_failed`
- `tengu_api_rate_limited`
- `tengu_unknown_model_cost`
- `tengu_prompt_cache_hit`
- `tengu_prompt_cache_miss`

### Voice & Input
- `tengu_voice_recording_started`
- `tengu_voice_recording_completed`
- `tengu_voice_silent_drop_replay`
- `tengu_voice_stream_early_retry`
- `tengu_voice_toggled`

### Transports
- `tengu_ws_transport_`
- `tengu_ws_transport_closed`
- `tengu_ws_transport_reconnected`
- `tengu_ws_transport_reconnecting`

## AGNT Porting Strategy
AGNT will implement these events via `packages/agnt_telemetry` and log them locally to `.beads/telemetry.jsonl` rather than phoning home.
