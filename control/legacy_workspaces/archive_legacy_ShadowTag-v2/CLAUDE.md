# Claude Code Integration

This repository is enhanced with Claude Code plugin infrastructure for managing Pnkln FastAPI services on Google Kubernetes Engine (GKE).

<<<<<<< HEAD
## 🎯 Overview
||||||| merged common ancestors
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
=======
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
║ ├─ Strategic Sale: SpaceX/Lockheed/DoD → $50-80B (Judge#6 IP)   ║
║ └─ Efficiency Multiplier: 40x Cost Reduction (Flash 2.0 pivot)  ║
╠═════════════════════════════════════════════════════════════════╣
║ PATH: Stay private through Year 5, partial IPO at $100B+        ║
║ URGENCY: NEED CASH IMMEDIATELY                                  ║
╚═════════════════════════════════════════════════════════════════╝
```
>>>>>>> upstream/claude/gptram-integration-01

The `.claude/` directory contains slash commands, agent skills, and automation hooks that enable:

<<<<<<< HEAD
- **Automated Deployment**: Deploy services to GKE with comprehensive validation
- **Autonomous Infrastructure Management**: AI-powered monitoring and optimization
- **CI/CD Integration**: Pre/post deployment hooks for automation
- **Operational Excellence**: Best practices enforcement and validation
||||||| merged common ancestors
| Product | Purpose | Status |
|---------|---------|--------|
| **Pipeline** | CI/CD + Agent orchestration | Active |
| **JudgeJura** | Governance/compliance gates (ATP 5-19) | Active |
| **FlyingMonkeys** | 600-agent swarm (570 Flash + 30 Pro) | Running on :8600 |
| **ShadowTag** | Cryptographic watermarking (L0-L4 attestation) | Building |
=======
| Product | Purpose | Status |
|---------|---------|--------|
| **Pipeline** | CI/CD + Agent orchestration | Active |
| **JudgeJura** | Governance/compliance gates (ATP 5-19) | Active (Revenue Asset) |
| **FlyingMonkeys** | 600-agent swarm (570 Flash + 30 Pro) | Running on :8600 |
| **ShadowTag** | Cryptographic watermarking (L0-L4 attestation) | Production (GKE) |
>>>>>>> upstream/claude/gptram-integration-01

## 📦 What's Included

<<<<<<< HEAD
### Slash Commands
||||||| merged common ancestors
- **Primary Cloud**: Google Cloud (GKE, Cloud Run, Cloud SQL)
- **Agent Routing**: FlyingMonkeys + JURA tier routing
- **Memory Layer**: GPTRAM (Redis-based verdict caching)
- **Vision**: FastVLM (Apple Silicon, MLX)
=======
- **Primary Cloud**: Google Cloud (GKE, Cloud Run, Cloud SQL) -> **Lean Ops**
- **Agent Routing**: FlyingMonkeys + JURA tier routing (Default: Flash 2.0)
- **Memory Layer**: GPTRAM (Redis) + 3-Way Sync (GCS/Firestore/Local)
- **Vision**: FastVLM (Apple Silicon, MLX)
>>>>>>> upstream/claude/gptram-integration-01

Use these commands in Claude Code to perform deployment operations:

- `/deploy` - Deploy services to GKE
- `/rollback` - Rollback to previous version
- `/scale` - Scale services based on demand
- `/status` - Check deployment status
- `/logs` - View and analyze service logs

### Agent Skills

- `gke-infrastructure` - Autonomous infrastructure management skill that can monitor, scale, and respond to incidents independently

### Automation Hooks

- `pre-deploy.sh` - Pre-deployment validation (cluster health, manifests, resources)
- `post-deploy.sh` - Post-deployment verification (rollout status, health checks)
- `validate.sh` - Code quality, security, and configuration validation

### Configuration

- `deployment.json` - Centralized deployment configuration for all environments

## 🚀 Quick Start

### 1. Set Up Environment

```bash
# Install required tools
# - gcloud (Google Cloud SDK)
# - kubectl (Kubernetes CLI)
# - docker (Container runtime)

# Authenticate
gcloud auth login
gcloud config set project pnkln-project

# Get cluster credentials
gcloud container clusters get-credentials pnkln-cluster --region=us-central1
```

### 2. Configure Environment Variables

```bash
export GCP_PROJECT_ID="pnkln-project"
export GKE_CLUSTER_NAME="pnkln-cluster"
export GKE_CLUSTER_REGION="us-central1"
export K8S_NAMESPACE="pnkln"
export DEPLOYMENT_ENV="staging"  # or development/production
```

### 3. Use in Claude Code

#### Deploy Services

```
/deploy
```

Claude will:
1. Validate environment and cluster
2. Build and push Docker images
3. Apply Kubernetes manifests
4. Monitor deployment progress
5. Verify health and performance
6. Provide detailed summary

#### Check Status

```
/status
```

Get comprehensive status including:
- Deployment health
- Pod status
- Resource utilization
- Recent events
- Recommendations

#### View Logs

```
/logs
```

Analyze logs with AI assistance:
- Stream real-time logs
- Detect errors and patterns
- Provide troubleshooting guidance
- Generate insights

### 4. Autonomous Operations

Enable the infrastructure skill for autonomous management:

```
Use the gke-infrastructure skill to monitor the deployment
```

The skill will:
- Monitor service health continuously
- Auto-scale based on demand
- Respond to incidents automatically
- Generate reports and recommendations

## 🏗️ Architecture

### Services

1. **API Gateway** - Main API entry point (critical)
2. **Authentication Service** - User auth and JWT (critical)
3. **Data Processing Service** - Background jobs (non-critical)
4. **Monitoring Service** - Metrics collection (moderate)

### Environments

- **Development** (`pnkln-dev`) - Feature development, minimal resources
- **Staging** (`pnkln-staging`) - Pre-production validation, production-like
- **Production** (`pnkln-prod`) - Live traffic, high availability, strict controls

### Deployment Strategy

- **Strategy**: RollingUpdate with zero downtime
- **Health Checks**: Liveness and readiness probes
- **Auto-Scaling**: HPA based on CPU/memory
- **Monitoring**: Prometheus + Grafana + AlertManager

## 🛡️ Security

- Workload Identity for GCP access
- Network Policies (default deny)
- Pod Security Standards (restricted)
- Secret management via GCP Secret Manager
- Image vulnerability scanning
- RBAC with least privilege

## 📊 Monitoring

- **Metrics**: Prometheus scraping every 30s
- **Dashboards**: Grafana visualization
- **Alerts**: AlertManager for critical issues
- **Logging**: Centralized in Google Cloud Logging
- **Retention**: 30 days for logs, 15 days for metrics

## 🔄 CI/CD Integration

Integrate hooks in your CI/CD pipeline:

```yaml
# GitHub Actions example
steps:
  - name: Validate
    run: ./.claude/hooks/validate.sh

  - name: Pre-deployment checks
    run: ./.claude/hooks/pre-deploy.sh

  - name: Deploy
    run: |
      # Your deployment commands

  - name: Post-deployment validation
    run: ./.claude/hooks/post-deploy.sh
```

## 🚨 Emergency Procedures

### Quick Rollback

```bash
kubectl rollout undo deployment/[service-name] -n pnkln
```

Or use Claude Code:

```
/rollback
```

### Check Health

```bash
./.claude/hooks/post-deploy.sh
```

Or:

```
/status
```

## 📖 Documentation

Full documentation available in `.claude/README.md`

Key sections:
- Quick Start Guide
- Slash Commands Reference
- Infrastructure Skill Usage
- Hook Integration
- Configuration Guide
- Troubleshooting

## 🤖 Claude Agent SDK Integration

This project uses the Claude Agent SDK for programmatic access:

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

// Use Claude Code preset
const result = query({
  prompt: "Deploy to staging",
  options: {
    systemPrompt: { type: "preset", preset: "claude_code" },
    settingSources: ["local", "project"]
  }
});
```

See `MIGRATION.md` for details on the SDK migration.

## 💡 Best Practices

1. **Always validate before deploying**: Run `validate.sh` hook
2. **Deploy to staging first**: Test in staging before production
3. **Monitor after deployment**: Check logs and metrics for 30 minutes
4. **Have rollback plan**: Know how to rollback quickly
5. **Use deployment windows**: Production deploys Mon-Thu during business hours
6. **Document incidents**: Record issues and resolutions
7. **Regular health checks**: Use `/status` command regularly

## 🔗 Resources

- [GKE Documentation](https://cloud.google.com/kubernetes-engine/docs)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code)
- [Claude Agent SDK](https://docs.claude.com/en/api/agent-sdk/overview)

## 📝 Changelog

### v1.0.0 (2025-11-08)

- Initial Claude Code plugin integration
- Added 5 slash commands (deploy, rollback, scale, status, logs)
- Created gke-infrastructure agent skill
- Implemented 3 automation hooks (pre-deploy, post-deploy, validate)
- Added deployment configuration
- Comprehensive documentation

## 🤝 Contributing

When extending this integration:

1. Add new slash commands to `.claude/commands/`
2. Create additional skills in `.claude/skills/`
3. Extend hooks in `.claude/hooks/`
4. Update configuration in `.claude/config/`
5. Document changes in `.claude/README.md`

## 📧 Support

For questions or issues:

1. Check `.claude/README.md` troubleshooting section
2. Use `/status` to diagnose issues
3. Review hook output for detailed errors
4. Contact DevOps team

---

<<<<<<< HEAD
**Version**: 1.0.0
**Last Updated**: 2025-11-08
**Maintained by**: DevOps Team
||||||| merged common ancestors
## Last Session: 2025-11-29 17:25

- **Summary**: Git cleanup - committed RSTA Squadron + Doctrine (41 files), merged PR #296
- **Commits**: 2 pushed to main (ac6973c → 322e8b0)
- **PRs Merged**: #296 health check endpoint
- **All Repos**: Clean, synced

*Last updated: November 29, 2025*
=======

## Last Session: 2025-12-08 17:12

- **Summary**: GKE quota fix, Terraform deploy shadowtagai-production, memory sync setup
- **Memory Synced**: GCS + Firestore + CLAUDE.md
- **Squadron**: 650 agents operational on :8600

*Last updated: November 29, 2025*
>>>>>>> upstream/claude/gptram-integration-01
