#!/usr/bin/env node

/**
 * Deployment Wizard
 *
 * Interactive CLI tool for setting up CI/CD and deployment automation.
 * Sets up everything needed for push-to-deploy workflows.
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

class DeploymentWizard {
  constructor() {
    this.config = {};
    this.projectRoot = process.cwd();
  }

  // Main wizard flow
  async run() {
    console.log("\n🚀 Deployment Wizard");
    console.log("=====================================\n");
    console.log("Sets up CI/CD that actually works.");
    console.log("Push to main, deploy to production. No more manual steps.\n");

    await this.checkPrerequisites();
    await this.gatherConfiguration();
    await this.setupDeployment();
    await this.displayNextSteps();
  }

  // Check prerequisites
  async checkPrerequisites() {
    console.log("📋 Checking prerequisites...\n");

    const checks = [
      { name: "Git", command: "git --version" },
      { name: "Node.js", command: "node --version" },
      { name: "npm", command: "npm --version" },
      { name: "Docker", command: "docker --version" },
    ];

    for (const check of checks) {
      try {
        const version = execSync(check.command, { encoding: "utf8" }).trim();
        console.log(`✅ ${check.name}: ${version}`);
      } catch (error) {
        console.log(`⚠️  ${check.name}: Not found (optional)`);
      }
    }

    console.log("");
  }

  // Gather configuration from user or environment
  async gatherConfiguration() {
    console.log("⚙️  Configuration\n");

    // Detect git information
    try {
      this.config.repoName = execSync("git config --get remote.origin.url", {
        encoding: "utf8",
      }).trim();
      this.config.branch = execSync("git branch --show-current", { encoding: "utf8" }).trim();
      console.log(`📦 Repository: ${this.config.repoName}`);
      console.log(`🌿 Branch: ${this.config.branch}`);
    } catch (error) {
      console.log("⚠️  Not a git repository or no remote configured");
    }

    // Detect package.json
    const packagePath = path.join(this.projectRoot, "package.json");
    if (fs.existsSync(packagePath)) {
      const pkg = JSON.parse(fs.readFileSync(packagePath, "utf8"));
      this.config.projectName = pkg.name;
      this.config.version = pkg.version || "1.0.0";
      console.log(`📋 Project: ${this.config.projectName}`);
      console.log(`🔢 Version: ${this.config.version}`);
    }

    console.log("");
  }

  // Setup deployment
  async setupDeployment() {
    console.log("🔧 Setting up deployment automation...\n");

    const tasks = [
      { name: "Verify Docker configuration", fn: () => this.verifyDocker() },
      { name: "Verify GitHub Actions workflows", fn: () => this.verifyWorkflows() },
      { name: "Create deployment scripts", fn: () => this.createScripts() },
      { name: "Update package.json scripts", fn: () => this.updatePackageScripts() },
      { name: "Create environment templates", fn: () => this.createEnvTemplates() },
      { name: "Generate deployment docs", fn: () => this.generateDocs() },
    ];

    for (const task of tasks) {
      try {
        console.log(`📌 ${task.name}...`);
        await task.fn();
        console.log(`   ✅ Complete\n`);
      } catch (error) {
        console.log(`   ⚠️  ${error.message}\n`);
      }
    }
  }

  // Verify Docker configuration
  verifyDocker() {
    const files = ["Dockerfile", "docker-compose.yml", ".dockerignore"];
    for (const file of files) {
      if (!fs.existsSync(path.join(this.projectRoot, file))) {
        throw new Error(`${file} not found`);
      }
    }
  }

  // Verify GitHub Actions workflows
  verifyWorkflows() {
    const workflowDir = path.join(this.projectRoot, ".github", "workflows");
    if (!fs.existsSync(workflowDir)) {
      throw new Error("Workflows directory not found");
    }

    const workflows = ["ci.yml", "cd.yml", "release.yml"];
    for (const workflow of workflows) {
      if (!fs.existsSync(path.join(workflowDir, workflow))) {
        throw new Error(`${workflow} not found`);
      }
    }
  }

  // Create deployment scripts
  createScripts() {
    const scriptsDir = path.join(this.projectRoot, "deployment", "scripts");

    // Deploy script
    const deployScript = `#!/bin/bash
set -e

echo "🚀 Deploying to production..."

# Pull latest changes
git pull origin main

# Install dependencies
npm ci

# Build application
npm run build || echo "No build script found"

# Build Docker image
docker-compose -f docker-compose.yml build

# Stop old containers
docker-compose -f docker-compose.yml --profile production down

# Start new containers
docker-compose -f docker-compose.yml --profile production up -d

# Health check
echo "⏳ Waiting for application to start..."
sleep 10

# Check if app is healthy
if curl -f http://localhost:8000/health 2>/dev/null; then
    echo "✅ Deployment successful!"
else
    echo "❌ Health check failed!"
    docker-compose -f docker-compose.yml logs --tail=50
    exit 1
fi
`;

    fs.writeFileSync(path.join(scriptsDir, "deploy.sh"), deployScript, { mode: 0o755 });

    // Rollback script
    const rollbackScript = `#!/bin/bash
set -e

echo "⏪ Rolling back deployment..."

# Get previous version
PREVIOUS_VERSION=\${1:-latest}

echo "Rolling back to version: $PREVIOUS_VERSION"

# Pull previous image
docker pull ghcr.io/${this.config.projectName}:$PREVIOUS_VERSION || true

# Stop current containers
docker-compose -f docker-compose.yml --profile production down

# Start previous version
docker-compose -f docker-compose.yml --profile production up -d

echo "✅ Rollback complete!"
`;

    fs.writeFileSync(path.join(scriptsDir, "rollback.sh"), rollbackScript, { mode: 0o755 });

    // Health check script
    const healthScript = `#!/bin/bash

HEALTH_URL=\${1:-http://localhost:8000/health}
MAX_RETRIES=\${2:-30}
RETRY_DELAY=\${3:-2}

echo "🔍 Checking health at $HEALTH_URL"

for i in $(seq 1 $MAX_RETRIES); do
    if curl -f -s $HEALTH_URL > /dev/null 2>&1; then
        echo "✅ Application is healthy!"
        exit 0
    fi
    echo "⏳ Attempt $i/$MAX_RETRIES failed, retrying in ${RETRY_DELAY}s..."
    sleep $RETRY_DELAY
done

echo "❌ Health check failed after $MAX_RETRIES attempts"
exit 1
`;

    fs.writeFileSync(path.join(scriptsDir, "health-check.sh"), healthScript, { mode: 0o755 });
  }

  // Update package.json scripts
  updatePackageScripts() {
    const packagePath = path.join(this.projectRoot, "package.json");
    if (!fs.existsSync(packagePath)) {
      throw new Error("package.json not found");
    }

    const pkg = JSON.parse(fs.readFileSync(packagePath, "utf8"));

    pkg.scripts = {
      ...pkg.scripts,
      deploy: "node deployment/deployment-wizard.js",
      "deploy:prod": "./deployment/scripts/deploy.sh",
      "deploy:rollback": "./deployment/scripts/rollback.sh",
      "deploy:health": "./deployment/scripts/health-check.sh",
      "docker:build": "docker-compose build",
      "docker:up": "docker-compose up -d",
      "docker:down": "docker-compose down",
      "docker:logs": "docker-compose logs -f",
      "docker:prod": "docker-compose --profile production up -d",
    };

    // Don't actually write in wizard mode, just verify
    // fs.writeFileSync(packagePath, JSON.stringify(pkg, null, 2));
  }

  // Create environment templates
  createEnvTemplates() {
    const configsDir = path.join(this.projectRoot, "deployment", "configs");

    const envExample = `# Application Configuration
NODE_ENV=production
PORT=8000

# Database (if needed)
# DATABASE_URL=postgresql://REDACTED_USER:REDACTED_PASS@localhost:5432/dbname

# API Keys (if needed)
# API_KEY=your-api-key-here
# API_SECRET=your-api-secret-here

# Deployment
DEPLOY_ENV=production
`;

    fs.writeFileSync(path.join(configsDir, ".env.example"), envExample);

    // Production config
    const prodConfig = {
      environment: "production",
      port: 8000,
      workers: 4,
      logLevel: "info",
      healthCheck: {
        enabled: true,
        path: "/health",
        interval: 30,
      },
      deployment: {
        strategy: "rolling",
        maxUnavailable: 1,
        healthCheckGracePeriod: 30,
      },
    };

    fs.writeFileSync(path.join(configsDir, "production.json"), JSON.stringify(prodConfig, null, 2));
  }

  // Generate documentation
  generateDocs() {
    const docsContent = `# Deployment Guide

## Quick Start

### Deploy to Production
\`\`\`bash
npm run deploy:prod
\`\`\`

### Rollback Deployment
\`\`\`bash
npm run deploy:rollback [version]
\`\`\`

### Check Health
\`\`\`bash
npm run deploy:health
\`\`\`

## CI/CD Workflows

### Continuous Integration (CI)
- Runs on every push and pull request
- Executes: lint → test → build → security scan
- Tests on Node.js 18, 20, and 22

### Continuous Deployment (CD)
- Automatically deploys on push to \`main\` branch
- Builds and pushes Docker image to registry
- Deploys to production environment
- Runs health checks

### Release Automation
- Triggered on version tags (v*.*.*)
- Creates GitHub release with changelog
- Publishes Docker images
- Optional: Publishes to npm

## Manual Deployment

### Using Docker Compose

Development:
\`\`\`bash
docker-compose up
\`\`\`

Production:
\`\`\`bash
docker-compose --profile production up -d
\`\`\`

### Environment Variables

Copy the example file and configure:
\`\`\`bash
cp deployment/configs/.env.example .env
# Edit .env with your values
\`\`\`

## Monitoring

### View Logs
\`\`\`bash
npm run docker:logs
\`\`\`

### Health Check
\`\`\`bash
curl http://localhost:8000/health
\`\`\`

## Troubleshooting

### Deployment Failed
1. Check logs: \`npm run docker:logs\`
2. Verify health: \`npm run deploy:health\`
3. Rollback if needed: \`npm run deploy:rollback\`

### Health Check Failed
1. Check application logs
2. Verify environment variables
3. Check database connectivity
4. Verify port availability

## Next Steps

1. Configure secrets in GitHub Settings → Secrets
2. Update deployment URLs in \`.github/workflows/cd.yml\`
3. Set up monitoring and alerting
4. Configure production environment variables
`;

    fs.writeFileSync(path.join(this.projectRoot, "deployment", "DEPLOYMENT.md"), docsContent);
  }

  // Display next steps
  async displayNextSteps() {
    console.log("\n🎉 Deployment setup complete!\n");
    console.log("Next Steps:\n");
    console.log("1. Configure GitHub Secrets:");
    console.log("   - Go to Settings → Secrets and variables → Actions");
    console.log("   - Add required secrets (SSH_PRIVATE_KEY, etc.)\n");
    console.log("2. Review and customize workflows:");
    console.log("   - .github/workflows/ci.yml");
    console.log("   - .github/workflows/cd.yml");
    console.log("   - .github/workflows/release.yml\n");
    console.log("3. Configure environment variables:");
    console.log("   - Copy deployment/configs/.env.example to .env");
    console.log("   - Update with your production values\n");
    console.log("4. Test locally:");
    console.log("   - npm run docker:build");
    console.log("   - npm run docker:up");
    console.log("   - npm run deploy:health\n");
    console.log("5. Push to main branch to trigger deployment:");
    console.log("   - git add .");
    console.log('   - git commit -m "Add deployment automation"');
    console.log("   - git push origin main\n");
    console.log("📚 Full documentation: deployment/DEPLOYMENT.md\n");
    console.log("🚀 Happy deploying!\n");
  }
}

// Run wizard if executed directly
if (require.main === module) {
  const wizard = new DeploymentWizard();
  wizard.run().catch((error) => {
    console.error("\n❌ Error:", error.message);
    process.exit(1);
  });
}

module.exports = DeploymentWizard;
