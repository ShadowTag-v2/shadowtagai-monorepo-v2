# Multi-Model Router

OpenAI-compatible proxy that routes requests to different LLM providers.

## Supported Providers

| Target | Provider | Example Models | Cost Tier |
|--------|----------|----------------|-----------|
| `openai` | OpenAI | GPT-5, GPT-4o | High |
| `grok` | xAI | Grok-1, Grok-1.5 | Medium |
| `cheetah` | Groq/Fireworks | Llama 3.1 8B | Very Low |

| `alt` | Together/OpenRouter | Various | Varies |
| `local` | Ollama/LM Studio | Llama, Mistral | Free (local) |

## Quick Start

### 1. Install

```bash
cd router
npm install
cp .env.example .env

# Edit .env and add your API keys

```

### 2. Run

```bash

# Development mode (with hot reload)

npm run dev

# Production mode

npm run build
npm start

```

### 3. Test

```bash

# Default (OpenAI)

curl http://localhost:8787/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'

# Route to Grok

curl http://localhost:8787/v1/chat/completions?target=grok \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}]
  }'

# Route to Cheetah (fast, cheap)

curl http://localhost:8787/v1/chat/completions?target=cheetah \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Explain Python async"}]
  }'

```

## Integration with Cursor/VS Code

### Configure Cline



1. Open Cline settings


2. Set provider to "OpenAI Compatible"


3. Base URL: `http://localhost:8787/v1`


4. API Key: `dummy` (router forwards real keys)


5. Model: any (router will override)

To switch providers, append `?target=<provider>`:


- `http://localhost:8787/v1?target=grok`


- `http://localhost:8787/v1?target=cheetah`

### Configure Continue

Settings → Models → Custom OpenAI API


- Base URL: `http://localhost:8787/v1`


- API Key: `dummy`


- Optional: `?target=grok` suffix for Grok

## Routing Strategy

### Cost-Aware Routing

```typescript
// In your app, choose model based on task
function pickModel(task: { complexity: string; files: number }) {
  if (task.complexity === "high" || task.files > 5) {
    return "openai";  // GPT-5 for hard problems
  }
  if (task.complexity === "medium") {
    return "grok";    // Good balance
  }
  return "cheetah";   // Fast & cheap for simple tasks
}

```

### Cursor Rules

Add to `.cursor/rules.md`:

```markdown

## Model Routing



- **Cheetah** (`?target=cheetah`): Drafts, refactors, comments, quick Q&A


- **Grok** (`?target=grok`): Multi-file analysis, test design, explanations


- **GPT-5** (`?target=openai`): Security/auth, API contracts, migrations

```

## Safety Controls

### Allowlist Domains

Set in `.env`:

```bash
ALLOWED_DOMAINS=openai.com,x.ai,groq.com

```

### Rate Limiting

```bash
RATE_LIMIT_RPM=60

```

(Not yet implemented; placeholder)

### Audit Logging

All requests logged to console. For production, integrate with `safety/audits/evidence.log`.

## Codespaces / Dev Container

The router works out-of-the-box in GitHub Codespaces:



1. Port 8787 is auto-forwarded


2. Use the forwarded URL: `https://<random>.github.dev/v1/chat/completions?target=grok`

## Performance

| Provider | Avg Latency | Throughput | Cost per 1M tokens (input) |
|----------|-------------|------------|----------------------------|
| Cheetah (Groq) | ~50-100ms | Very High | ~$0.10 |
| Grok (xAI) | ~200-400ms | High | ~$5.00 |
| GPT-5 (OpenAI) | ~300-600ms | Medium | ~$15.00 |
| Claude 3.5 (Anthropic) | ~400-700ms | Medium | ~$3.00 |

**Recommendation**: Use Cheetah for 80% of tasks, escalate to Grok/GPT-5 for complex ones.

## Deployment

### Fly.io / Railway

```bash

# Fly.io

flyctl launch
flyctl secrets set OPENAI_API_KEY=sk-... XAI_API_KEY=xai-...
flyctl deploy

# Railway

railway up
railway variables set OPENAI_API_KEY=sk-... XAI_API_KEY=xai-...

```

### Docker

```dockerfile
FROM node:22-alpine
WORKDIR /app
COPY router/package*.json ./
RUN npm ci --only=production
COPY router/ ./
RUN npm run build
CMD ["npm", "start"]

```

## Troubleshooting

### 401 Unauthorized

Check that API keys are set in `.env` and valid.

### Model not found

Verify the model ID matches what your provider expects:


- Grok: `grok-1`, `grok-1.5`


- Cheetah: `llama-3.1-8b-instant`, `gemma2-9b-it`

### Slow responses



- Check network latency to provider


- Try switching to a geographically closer provider


- Use `cheetah` for latency-sensitive tasks

### CORS errors (browser)

Add CORS middleware if calling from browser:

```typescript
import cors from "cors";
app.use(cors());

```

---

**Owner**: Platform Engineering
**Last Updated**: 2025-11-08
**Status**: Production-ready placeholder (add rate limiting + audit logging before prod)
