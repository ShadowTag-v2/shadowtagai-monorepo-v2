# ShadowTagAI Monorepo — Architecture Context

## Repository Structure

This is a Google Cloud-native monorepo for ShadowTagAI, containing:

### Production Apps
- **apps/kovelai** — KovelAI marketing site (Firebase Hosting)
- **apps/counselconduit** — Legal AI backend (Cloud Run, FastAPI)
- **apps/lawtrack-ui** — Case management dashboard (React + Vite)
- **apps/aiyou_stack** — AI pipeline services

### Core Libraries
- **core/governance** — Judge6 policy engine
- **core/lawtrack** — Legal domain logic
- **core/aegaeon** — Context caching + swarm routing
- **core/sovereign_mlx** — Apple Silicon ML inference

### Infrastructure
- **infra/** — Terraform/OpenTofu, migrations, Cloud Tasks
- **scripts/** — Automation, deployment, CI helpers
- **labs/uphillsnowball** — R&D experiments

## Key Conventions
- **Database**: Firestore (CANONICAL — Supabase rejected)
- **Queue**: Google Cloud Tasks (BullMQ banned)
- **Auth**: Firebase Auth
- **Secrets**: GCP Secret Manager (production), .env (local only)
- **Model**: gemini-3.1-flash-lite-preview (runtime)
- **CI**: GitHub Actions (4 workflows: gca-pr-review, 10x_vibe_matrix, judge6_yolo_gate, antigravity_ci)

## GitHub Integration
- **SSH transport** for git push/pull
- **GitHub App** (ID: 3018200) for API operations
- **Claude Code Action** for automated PR reviews
- **Gemini CLI** for multi-agent PR analysis

## Active Development
Check `gh issue list` and `gh pr list` for current work items.
