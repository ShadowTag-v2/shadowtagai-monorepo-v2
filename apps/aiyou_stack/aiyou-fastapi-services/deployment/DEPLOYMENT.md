# Deployment Guide

Complete guide for deploying shadowtag_v4-fastapi-services with zero-manual-steps CI/CD.

## Table of Contents

- [Quick Start](#quick-start)
- [CI/CD Workflows](#cicd-workflows)
- [Manual Deployment](#manual-deployment)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Automated Deployment (Recommended)

Push to main branch - automatic deployment to production:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

That's it! The CI/CD pipeline will:

1. Run tests
2. Build Docker image
3. Deploy to production
4. Run health checks

### Manual Deployment

Deploy to production manually:

```bash
npm run deploy:prod
```

Rollback to previous version:

```bash
npm run deploy:rollback [version]
```

Check application health:

```bash
npm run deploy:health
```

## CI/CD Workflows

### Continuous Integration (CI)

**Triggers:** Push to any branch, Pull requests to main/develop

**Workflow:** `.github/workflows/ci.yml`

**Steps:**

1. **Lint** - Code quality checks
2. **Test** - Run test suite on Node 18, 20, 22
3. **Build** - Build application and Docker image
4. **Security** - npm audit and Snyk scan

**Duration:** ~5-10 minutes

### Continuous Deployment (CD)

**Triggers:** Push to `main` branch, Manual workflow dispatch

**Workflow:** `.github/workflows/cd.yml`

**Steps:**

1. Run tests
2. Build application
3. Build and push Docker image to GitHub Container Registry
4. Deploy to production server
5. Run database migrations
6. Health check
7. Notify on success/failure

**Duration:** ~10-15 minutes

### Release Automation

**Triggers:** Git tags matching `v*.*.*`, Manual workflow dispatch

**Workflow:** `.github/workflows/release.yml`

**Steps:**

1. Run tests
2. Build application
3. Generate changelog from commits
4. Create GitHub release
5. Build and tag Docker image
6. Optional: Publish to npm

**Creating a release:**

```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0
```

## Manual Deployment

### Using Docker Compose

**Development environment:**

```bash
# Start all services
npm run docker:up

# View logs
npm run docker:logs

# Stop services
npm run docker:down
```

**Production environment:**

```bash
# Build production image
npm run docker:build

# Start production services
npm run docker:prod

# Health check
npm run deploy:health
```

### Using Deployment Scripts

**Full deployment:**

```bash
./deployment/scripts/deploy.sh
```

This script:

- Pulls latest code
- Installs dependencies
- Runs tests
- Builds Docker image
- Deploys to production
- Runs health check
- Offers rollback on failure

**Rollback:**

```bash
./deployment/scripts/rollback.sh [version]
```

**Health check:**

```bash
./deployment/scripts/health-check.sh [url] [retries] [delay]
```

## Configuration

### Environment Variables

Copy the example configuration:

```bash
cp deployment/configs/.env.example .env
```

Edit `.env` with your values:

```env
NODE_ENV=production
PORT=8000

# Add your configuration
DATABASE_URL=postgresql://REDACTED_USER:REDACTED_PASS@server 'cd /app && ./deploy.sh'
```

### Database Migrations

Add migration step to deployment:

```bash
# In .github/workflows/cd.yml
- name: Run migrations
  run: npm run migrate
```

### Blue-Green Deployment

1. Deploy new version alongside old
2. Run health checks
3. Switch traffic
4. Terminate old version

### Monitoring Integration

Add monitoring to `production.json`:

```json
{
  "monitoring": {
    "sentry": {
      "dsn": "https://..."
    },
    "datadog": {
      "apiKey": "..."
    }
  }
}
```

## Deployment Checklist

Before deploying to production:

- [ ] All tests passing locally
- [ ] Environment variables configured
- [ ] GitHub secrets set up
- [ ] Database backed up
- [ ] Health endpoint implemented
- [ ] Monitoring configured
- [ ] Rollback plan tested
- [ ] Documentation updated

## Support

For issues or questions:

1. Check this documentation
2. Review workflow logs
3. Check application logs
4. Create an issue on GitHub

---

**Last Updated:** 2025-11-15

**Version:** 1.0.0
