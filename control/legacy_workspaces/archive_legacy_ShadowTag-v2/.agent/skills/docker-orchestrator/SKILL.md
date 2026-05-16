---
name: Docker Orchestrator
description: Native shell-based container management bypassing GUI extensions. Enables full agent autonomy over the Docker daemon.
---

# 🐳 Docker Orchestrator Skill

> **Directive:** You are operating in a serverless/containerized environment where manual GUI interaction is prohibited. The official VS Code Docker Extension is to be completely ignored.

## 1. Operating Procedure (Shell First)
*   **NEVER** ask the user to double-click a Docker extension button.
*   **ALWAYS** use the native `docker` and `docker compose` (`docker-compose`) commands via the shell `run_command` tool.

## 2. Standard Commands
*   **Build:** `docker build -t <image_name>:<tag> .`
*   **Run (Detached):** `docker run -d -p <host>:<container> --name <name> <image_name>`
*   **Orchestration:** `docker compose up -d --build` (always use detached so the terminal doesn't lock up).

## 3. Diagnostics & Debugging
If a container fails to start, immediately execute to diagnose:
1.  **Check state:** `docker ps -a`
2.  **Extract logs:** `docker logs --tail 200 <container_id>`
3.  **Inspect config:** `docker inspect <container_id>`

## 4. Pruning Protocol
*   Docker cache accumulation kills systems. If standard operations fail due to "No space left on device," autonomously execute:
    `docker system prune -a --volumes -f`
*   **Constraint:** Only wipe volumes if explicitly safe or if directed during a total teardown.
