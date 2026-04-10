# Claude Code Integration

This repository is enhanced with Claude Code plugin infrastructure for managing Pnkln FastAPI services on Google Kubernetes Engine (GKE).

## 🎯 Overview

The `.claude/` directory contains slash commands, agent skills, and automation hooks that enable:

- **Automated Deployment**: Deploy services to GKE with comprehensive validation
- **Autonomous Infrastructure Management**: AI-powered monitoring and optimization
- **CI/CD Integration**: Pre/post deployment hooks for automation
- **Operational Excellence**: Best practices enforcement and validation

## 📦 What's Included

### Slash Commands

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
import { query } from '@anthropic-ai/claude-agent-sdk';

// Use Claude Code preset
const result = query({
  prompt: 'Deploy to staging',
  options: {
    systemPrompt: { type: 'preset', preset: 'claude_code' },
    settingSources: ['local', 'project'],
  },
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

**Version**: 1.0.0
**Last Updated**: 2025-11-08
**Maintained by**: DevOps Team
