# Contracts

This directory contains interface contracts, API schemas, and cross-service protocol definitions for the UphillSnowball monorepo.

## Purpose

- gRPC `.proto` definitions
- OpenAPI / AsyncAPI specs
- Shared Pydantic models for cross-service validation
- Firestore document schemas

## Policy

- All contract changes require a version bump
- Breaking changes must be tracked in `.beads/issues.jsonl`
- Consumers must pin to specific contract versions
