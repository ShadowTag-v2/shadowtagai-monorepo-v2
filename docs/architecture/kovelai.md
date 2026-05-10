# KovelAI System Architecture

## Core Doctrine
KovelAI relies on the Sovereign Monorepo architecture to unify Google Cloud Platform (GCP) resources behind a centralized Identity-Aware Proxy (IAP) while serving deterministic web interfaces globally.

## The Edge
- **Cloud Run Origin**: Hosts the primary Node.js and Golang proxy layers.
- **CRSMC Layer**: (Cloud Run Shield Micro-Controller) authenticates traffic via deterministic signatures.
- **Firebase Hosting**: Serves the lightweight vanilla HTML/CSS interfaces directly.

## The Core
- **Database**: Firestore Enterprise (locked behind zero-trust `.rules` evaluating `request.resource.data`).
- **Orchestration**: Cloud Tasks handle the distributed queues, completely deprecating BullMQ.

## Pipeline (Execution Path)
1. **Request Ingress**: `kovelai.com` hits Firebase Hosting.
2. **Compute Route**: Traffic needing heavy inference routes via internal Cloud Run APIs.
3. **Execution**: The Asymmetric Compute engine determines model tier (`gemini-3.1-flash-lite-preview-thinking` vs central intelligence hive).
