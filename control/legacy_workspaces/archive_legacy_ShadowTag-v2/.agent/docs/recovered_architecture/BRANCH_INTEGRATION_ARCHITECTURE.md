# Branch Integration Architecture

This document details the technical strategy for merging six disparate development branches into the unified `pnkln` core.

## Overview

We are consolidating logic from:

1. `kernel-chaining-architecture`

2. `autogen-to-gemini-migration`

3. `add-superpowers-marketplace`

4. `pnkln-intelligence-pipeline-deployment`

5. `setup-cursor-eslint-hybrid`

6. `llm-serving-efficiency-research`

## Integration Pattern: "The Fold"

Instead of simple git merges, we are refactoring logic into a new modular structure under `src/pnkln/`.

### 1. Cost & Intelligence Layer (`src/pnkln/gemini_integration.py`)


- **Source**: `autogen-to-gemini-migration` + `llm-serving-efficiency-research`

- **Logic**: Centralizes all LLM calls. Wraps Google GenAI SDK. Implements token counting and cost comparison logic from the research branch.

### 2. API & Metering Layer (`src/pnkln/intelligence_api.py`)


- **Source**: `pnkln-intelligence-pipeline-deployment`

- **Logic**: Defines Pydantic models for intelligence feeds. Implements the metering logic required to bill customers (previously just internal logging).

### 3. Marketplace Data Layer (`src/pnkln/marketplace/`)


- **Source**: `add-superpowers-marketplace` + `kernel-chaining-architecture`

- **Logic**: The `Superpower` model replaces rigid code modules. `UserSuperpower` allows dynamic activation of capabilities (Kernel Chains).

## Quality Assurance (`setup-cursor-eslint-hybrid`)


- **Strategy**: Eslint and Prettier rules from this branch are being applied (via Biome in this repo) to ensure consistent code style across the new python modules. Verification scripts run strict checks.

## Deployment Strategy


1. **Dockerize**: All new modules packaged into `aiyou-fastapi-services` container.

2. **Env Config**: New variables `GEMINI_API_KEY`, `STRIPE_KEY` (future), `POSTGRES_URL`.

3. **Migration**: Run `alembic upgrade head` to create new marketplace tables.
