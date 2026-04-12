# Deployment Wizard

Automated CI/CD setup for shadowtag_v4-fastapi-services. Push to main, deploy to production. No manual steps.

## What This Does

✅ **Continuous Integration**

- Automated testing on every push
- Code quality checks
- Security scanning
- Multi-version Node.js testing

✅ **Continuous Deployment**

- Auto-deploy on push to main
- Docker image building
- Health checks
- Automatic rollback on failure

✅ **Zero Manual Steps**

- No SSH required
- No manual server configuration
- No deployment commands to remember

## Quick Start

### 1. Run the Deployment Wizard

```bash
npm run deploy
```

This will:

- Check prerequisites
- Verify configuration
- Set up all deployment files
- Guide you through next steps

### 2. Configure GitHub Secrets

Go to: Settings → Secrets and variables → Actions

Add any required secrets for your deployment target.

### 3. Push to Deploy

```bash
git add .
git commit -m "Add deployment automation"
git push origin main
```

Your application will automatically:

1. Run tests
2. Build Docker image
3. Deploy to production
4. Run health checks

## What's Included

### GitHub Actions Workflows

- **ci.yml** - Continuous Integration
  - Lint, test, build, security scan
  - Runs on every push and PR

- **cd.yml** - Continuous Deployment
  - Auto-deploy to production
  - Triggered on push to main

- **release.yml** - Release Automation
  - Creates releases on version tags
  - Generates changelogs

### Docker Configuration

- **Dockerfile** - Multi-stage optimized build
- **docker-compose.yml** - Local and production environments
- **.dockerignore** - Optimized image size

### Deployment Scripts

- **deploy.sh** - Full deployment automation
- **rollback.sh** - Quick rollback capability
- **health-check.sh** - Application health verification

### Configuration

- **production.json** - Production environment config
- **staging.json** - Staging environment config
- **.env.example** - Environment variable template

## Available Commands

```bash
# Run deployment wizard
npm run deploy

# Manual deployment
npm run deploy:prod

# Rollback deployment
npm run deploy:rollback

# Health check
npm run deploy:health

# Docker commands
npm run docker:build
npm run docker:up
npm run docker:down
npm run docker:logs
```

## Features

### 🚀 Automated Deployment

- Push to main → automatic production deployment
- No manual intervention required
- Runs tests before deploying

### 🔒 Security First

- Automated security scanning
- Non-root Docker containers
- Secret management via GitHub Secrets

### 📊 Health Monitoring

- Automated health checks
- Application startup verification
- Rollback on health check failure

### 🔄 Easy Rollback

- One-command rollback
- Version pinning
- Automatic rollback on deployment failure

### 🐳 Docker Optimized

- Multi-stage builds
- Layer caching
- Minimal image size

### 📝 Comprehensive Logging

- Deployment logs
- Application logs
- Container logs

## Deployment Flow

```
Push to main
    ↓
Run tests
    ↓
Build Docker image
    ↓
Push to registry
    ↓
Deploy to server
    ↓
Run health check
    ↓
Success! 🎉
```

## Requirements

- Node.js 18+
- Docker
- Git
- GitHub repository

## Documentation

- [Full Deployment Guide](./DEPLOYMENT.md)
- [GitHub Actions Docs](../.github/workflows/)
- [Docker Compose Reference](https://docs.docker.com/compose/)

## Customization

### Add Deployment Target

Edit `.github/workflows/cd.yml`:

```yaml
- name: Deploy to Server
  run: |
    # Add your deployment commands
    ssh user@server 'cd /app && ./deploy.sh'
```

### Configure Environment

Edit `deployment/configs/production.json`:

```json
{
  "server": {
    "port": 8000,
    "workers": 4
  }
}
```

### Add Notifications

Add to workflow:

```yaml
- name: Notify
  run: |
    curl -X POST https://hooks.slack.com/... \
      -d '{"text":"Deployment complete!"}'
```

## Troubleshooting

**Deployment failed?**

```bash
# Check logs
npm run docker:logs

# Rollback
npm run deploy:rollback
```

**Health check failed?**

```bash
# Manual health check
npm run deploy:health

# Check application logs
docker-compose logs app
```

**Docker issues?**

```bash
# Rebuild images
docker-compose build --no-cache

# Clean up
docker system prune -a
```

## Support

For detailed documentation, see [DEPLOYMENT.md](./DEPLOYMENT.md)

---

**DevOps expert automating deployments end-to-end.**
