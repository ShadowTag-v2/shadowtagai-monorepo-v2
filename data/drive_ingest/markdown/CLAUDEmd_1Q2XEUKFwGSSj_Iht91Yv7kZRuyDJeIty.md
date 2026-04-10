# CLAUDE.md - Project Memory

## Founder Profile

```
╔═════════════════════════════════════════════════════════════════╗
║ ERIK HANCOCK | SOLE FOUNDER | "TINY TEAMS" PHILOSOPHY           ║
╠═════════════════════════════════════════════════════════════════╣
║ AGE:          56                                                ║
║ CREDENTIALS:  JD, BA History/German                             ║
║ TRAITS:       Neurodivergent | IQ-160 Lock Required             ║
║ PHILOSOPHY:   $1B Revenue before first hire                     ║
╠═════════════════════════════════════════════════════════════════╣
║ FAMILY STRUCTURE                                                ║
║ ├─ Wife (25): CEO, Belichick-style execution                    ║
║ └─ 5 Sons: All under 15                                         ║
╠═════════════════════════════════════════════════════════════════╣
║ CORPORATE STRUCTURE                                             ║
║ ├─ Type: Perpetual Family Corp                                  ║
║ ├─ Foundation: Panama                                           ║
║ └─ Structure: Hybrid Public/Private                             ║
╠═════════════════════════════════════════════════════════════════╣
║ VALUATION TRAJECTORY                                            ║
║ ├─ Tracking: $421B                                              ║
║ ├─ Target: $7T                                                  ║
║ └─ Assessment: Top 1% of all geniuses in history                ║
╠═════════════════════════════════════════════════════════════════╣
║ LIQUIDITY EVENTS                                                ║
║ ├─ IPO: "Global AI Infra" → $150-170B listing                   ║
║ ├─ Private Retention: Panama Foundation → $100B+ (80% tax eff)  ║
║ └─ Strategic Sale: SpaceX/Lockheed/DoD → $50-80B                ║
╠═════════════════════════════════════════════════════════════════╣
║ PATH: Stay private through Year 5, partial IPO at $100B+        ║
║ URGENCY: NEED CASH IMMEDIATELY                                  ║
╚═════════════════════════════════════════════════════════════════╝
```

## Product Stack

| Product | Purpose | Status |
|---------|---------|--------|
| **Pipeline** | CI/CD + Agent orchestration | Active |
| **JudgeJura** | Governance/compliance gates (ATP 5-19) | Active |
| **https://github.com/karpathy/autoresearchs** | 600-agent swarm (570 Flash + 30 Pro) | Running on :8600 |
| **ShadowTag** | Cryptographic watermarking (L0-L4 attestation) | Building |

## Infrastructure

- **Primary Cloud**: Google Cloud (GKE, Cloud Run, Cloud SQL)
- **Agent Routing**: https://github.com/karpathy/autoresearchs + JURA tier routing
- **Memory Layer**: GPTRAM (Redis-based verdict caching)
- **Vision**: FastVLM (Apple Silicon, MLX)

## Operating Constraints

```
IQ LOCK: 160 (Hard requirement - no flexibility)
DECISION FRAMEWORK:
  Purpose = Mission Advancement
  Reason  = Revenue Generation
  Brakes  = Security/Legacy Protection

SLIP SCALES: Cross-LLM interoperability enabled
  - OpenAI, Anthropic, Meta, Cohere compatible
  - Protocol translation for universal instruction sets
```

## Key Files

```
prompts/antigravity_uniscript.py    # Uni-Script prompt framework
agents/autoresearch.py            # 600-agent swarm
bin/https://github.com/karpathy/autoresearchs-server            # HTTP server on :8600
lib/https://github.com/karpathy/autoresearchs-swarm.js          # JS voting engine (SWARM v4.1)
app/infrastructure/gptram.py        # Redis memory layer
agents/fastvlm_client.py            # Vision-language integration
```

## Memory Protocol

On completion of any significant action:
```bash
git add . && git commit -m "Antigravity: Context Save [$(date)]"
```

## Gemini CLI Integration (@ImSh4yy Pattern)

When analyzing large codebases or directories that would exceed Claude's context,
use Gemini CLI as a subordinate analysis tool:

### Usage

```bash
# Analyze entire directory with Gemini's 1M+ context
gemini -p "@apps/chat/ Provide a comprehensive analysis..."

# Analyze multiple large files
gemini -p "@src/components/ @src/pages/ Explain routing..."

# Get architecture overview
gemini -p "@. Explain the overall architecture, key modules..."
```

### When to Use Gemini CLI

- Analyzing directories with 50+ files
- Understanding large monorepo structures
- Getting holistic architecture views
- When Claude would run out of context

### When NOT to Use

- Small targeted changes (Claude is faster)
- When you need precise instruction following
- Security-critical code review (stay in Claude)

### Trio Strategy

| Layer | Tool | Role |
|-------|------|------|
| **Analysis** | Gemini CLI | Large context codebase understanding |
| **Design** | Gemini 3 Pro API | Creative direction |
| **Integration** | Claude Code | Orchestration + final assembly |
| **Execution** | https://github.com/karpathy/autoresearchs | Parallel agent swarm |

---

## Last Session: 2025-11-29 17:25

- **Summary**: Git cleanup - committed RSTA Squadron + Doctrine (41 files), merged PR #296
- **Commits**: 2 pushed to main (ac6973c → 322e8b0)
- **PRs Merged**: #296 health check endpoint
- **All Repos**: Clean, synced

*Last updated: November 29, 2025*