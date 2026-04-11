---
description: Containerize application with Docker
---

# Docker

I will help you containerize your application with Docker.

## Guardrails
- Detect existing Dockerfile before creating
- Follow Docker best practices for image size
- Don't include secrets in images
- Use multi-stage builds when appropriate
- Coordinate with `docker-orchestrator` skill for daemon operations
- Never bake API keys or `.env` files into images

## Steps

### 1. Understand Requirements
Ask clarifying questions:
- What type of application? (Node, Python, Go, etc.)
- Single container or multi-container?
- Any specific base image requirements?
- Need docker-compose?
- Local dev or production deployment?

### 2. Analyze Application
// turbo
Determine container needs:
- Runtime requirements (check package.json, pyproject.toml, go.mod)
- Dependencies to install
- Ports to expose
- Files to copy
- Build steps needed

### 3. Create Dockerfile
Follow best practices:
- Use specific base image tags (never `latest`)
- Order layers for caching (deps before code)
- Use multi-stage builds for smaller images
- Copy only necessary files
- Add `.dockerignore` for build context

### 4. Create docker-compose (if needed)
For multi-container apps:
- Define services
- Set up networking
- Configure volumes
- Add health checks
- Use environment variables for secrets

### 5. Build and Test
// turbo
- Build the image
- Run container locally
- Test functionality
- Check image size (`docker images`)

### 6. Verify
- Container starts correctly
- Application works as expected
- Logs are accessible (`docker logs`)
- No secrets leaked in image layers

## Principles
- Keep images small (Alpine or distroless base)
- Don't run as root
- Use .dockerignore
- Tag images with semver, not `latest`
- One process per container
