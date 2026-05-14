---
description: Dockerization Workflow
---

# Dockerization Workflow

Goal: Containerize the current application. Steps:

1. Analyze the codebase to detect the language (Node, Python, Go) and dependencies (package.json, requirements.txt).
2. Create a Dockerfile optimized for production (use multi-stage builds if possible).
3. Create a .dockerignore file to exclude node_modules, .git, and .env.
4. Create a docker-compose.yml file if a database is detected in the code configuration.
