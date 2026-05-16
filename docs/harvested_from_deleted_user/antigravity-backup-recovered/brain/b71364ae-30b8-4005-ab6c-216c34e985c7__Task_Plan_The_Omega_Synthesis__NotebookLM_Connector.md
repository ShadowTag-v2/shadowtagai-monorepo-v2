# Task Plan: The Omega Synthesis & NotebookLM Connector

## Phase 1: Re-establishing The Omega Synthesis

- [x] Create [scripts/ingest_mass_langextract.py](file:///Users/pikeymickey/.gemini/antigravity/playground/quantum-whirlpool/scripts/ingest_mass_langextract.py)
- [x] Create [src_cpp/main.cpp](file:///Users/pikeymickey/.gemini/antigravity/playground/quantum-whirlpool/src_cpp/main.cpp)
- [x] Create [Makefile](file:///Users/pikeymickey/.gemini/antigravity/playground/quantum-whirlpool/Makefile)
- [x] Create [scripts/finish_changes.py](file:///Users/pikeymickey/.gemini/antigravity/playground/quantum-whirlpool/scripts/finish_changes.py)
- [x] Verify execution capabilities

## Phase 2: NotebookLM x Antigravity MCP Connector

- [x] Create MCP server project structure for NotebookLM (Node.js/TypeScript)
- [x] Implement NotebookLM MCP tools (`auth_status`, `auth_setup`, `list_notebooks`, `add_notebook`, `ask_question`, `search_notebooks`) using Python subprocesses
- [x] Build and verify the MCP server
- [x] Add the newly built MCP server to the Antigravity configuration or provide instructions for the user

## Phase 3: Final Egress

- [x] Run the Egress Janitor script ([scripts/finish_changes.py](file:///Users/pikeymickey/.gemini/antigravity/playground/quantum-whirlpool/scripts/finish_changes.py)) inline with the "f1 gca" user alias intent.

## Phase 4: Python Environment Fixes & Luminina Website

- [x] Fix VSCode Native locator `python` path in [.vscode/settings.json](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/.vscode/settings.json)
- [x] Fix [god_mode_admin.py](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/scripts/god_mode_admin.py) module root path import
- [x] Test [god_mode_admin.py](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/scripts/god_mode_admin.py) module execution
- [x] Create Stitch project "Luminina"
- [x] Generate "Luminina" AI SaaS landing page UI via Stitch

## Phase 5: Localhost & Omega Loop

- [x] Set default Python interpreter path to [/usr/bin/python3](file:///usr/bin/python3) across workspaces.
- [x] Spin up the frontend (ShadowTag UI) on localhost:3001 via `npm run dev`.
- [x] Integrate Luminina Stitch UI locally at `public/luminina.html`.
- [x] Verify [.agent/workflows/live-engine.md](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/.agent/workflows/live-engine.md), update GC project to `shadowtag-omega-v4`.
- [x] Execute `/omega-loop` (janitor sweeps) over the workspace.
- [x] Clone `modelcontextprotocol/servers.git` into `playground/quantum-whirlpool/mcp-servers`.
- [x] Deploy browser subagent to verify `localhost:3001` and `localhost:3001/luminina.html`.
