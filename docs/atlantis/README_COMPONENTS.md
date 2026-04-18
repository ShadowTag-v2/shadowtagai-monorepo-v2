# PNKLN Claude Code Components

Custom agents, MCPs, and commands for the PNKLN/ShadowTag stack.

## Agents

| Agent | Description | Use Case |
|-------|-------------|----------|
| `judge-six` | p99≤90ms enforcement gate | Latency governance for all LLM calls |
| `jr-engine` | Purpose/Reasons/Brakes validation | JR semantic framework enforcement |
| `atp-519-risk` | Military risk assessment | ATP 5-19 matrix for decision governance |
| `flying-monkeys` | 600-agent swarm coordinator | Research + governance orchestration |

## MCPs (Model Context Protocols)

| MCP | Description | Integration |
|-----|-------------|-------------|
| `vertex-ai` | Gemini Antigravity API | Direct Vertex AI access |
| `gke-cluster` | GKE namespace management | K8s deployment ops |
| `shadowtag` | DCT watermarking | Content authenticity |
| `corpus-guard` | Semantic indexing | RAG retrieval |

## Commands

| Command | Description | Invocation |
|---------|-------------|------------|
| `bootstrap-check` | Validate ROI gates | `/bootstrap-check` |
| `deploy-judge` | Deploy Judge#6 to GKE | `/deploy-judge [namespace]` |
| `compress-semantic` | ATP_519_scan compression | `/compress-semantic [file]` |
| `swarm-vote` | Run FlyingMonkeys governance | `/swarm-vote [decision]` |

## Usage

When running CACI, include PNKLN components:

```bash
npx caci --components ./pnkln/pnkln-components.json

```

Or merge into your configuration:

```bash
./sync-upstream.sh  # Pulls latest CACI + merges PNKLN components

```
