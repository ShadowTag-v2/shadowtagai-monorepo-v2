# Secrets Management Guide

**Standard:** Google Secret Manager for production, `.env` files for development (never committed)
**Rotation:** API keys every 90 days, database credentials every 30 days

---

## Development Environment

### `.env` Files (Local Development Only)

```bash
# .env.development (NEVER COMMIT THIS)
DATABASE_URL="postgresql://dev:devpass@localhost:5432/pnkln_dev"
JWT_SECRET="dev-secret-change-in-production"
API_KEY="dev-api-key-12345"
SENTRY_DSN="https://redacted@shadowtag-v4.local/123456"
ENCRYPTION_KEY="base64-encoded-32-byte-key-here"

# Google Cloud (for local testing)
GOOGLE_APPLICATION_CREDENTIALS="./config/gcp-dev-service-account.json"
GCP_PROJECT="pnkln-dev"
```

### `.gitignore` Configuration

```gitignore
# Secrets - NEVER COMMIT
.env
.env.*
!.env.example
*.key
*.pem
*.p12
credentials.json
service-account.json
**/secrets/**
config/gcp-*.json
```

### `.env.example` (Safe to Commit)

```bash
# .env.example - Template for environment variables
DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
JWT_SECRET="your-jwt-secret-here"
API_KEY="your-api-key-here"
SENTRY_DSN="https://your-sentry-dsn"
ENCRYPTION_KEY="base64-encoded-32-byte-key"

# Instructions:
# 1. Copy this file to .env.development
# 2. Fill in actual values
# 3. NEVER commit .env.development
```

---

## Production Environment

### Google Secret Manager Setup

```bash
# Create secret for database URL
gcloud secrets create database-url \
  --project=pnkln-prod \
  --replication-policy="automatic" \
  --data-file=- <<EOF
postgresql://prod:SECURE_PASSWORD@10.0.0.5:5432/pnkln_prod
EOF

# Create secret for JWT signing key
openssl rand -base64 32 | gcloud secrets create jwt-secret \
  --project=pnkln-prod \
  --replication-policy="automatic" \
  --data-file=-

# Create secret for API key
gcloud secrets create api-key \
  --project=pnkln-prod \
  --replication-policy="automatic" \
  --data-file=- <<EOF
sk-prod-1234567890abcdef
EOF

# Grant access to service account
gcloud secrets add-iam-policy-binding database-url \
  --member="serviceAccount:redacted@shadowtag-v4.local" \
  --role="roles/secretmanager.secretAccessor"
```

### TypeScript/Node.js Secret Access

```typescript
import { SecretManagerServiceClient } from '@google-cloud/secret-manager';

export class SecretManager {
  private client: SecretManagerServiceClient;
  private cache: Map<string, { value: string; expiry: number }> = new Map();
  private readonly CACHE_TTL = 5 * 60 * 1000; // 5 minutes

  constructor() {
    this.client = new SecretManagerServiceClient();
  }

  async getSecret(secretName: string): Promise<string> {
    // Check cache first
    const cached = this.cache.get(secretName);
    if (cached && cached.expiry > Date.now()) {
      return cached.value;
    }

    const projectId = process.env.GCP_PROJECT || 'pnkln-prod';
    const name = `projects/${projectId}/secrets/${secretName}/versions/latest`;

    try {
      const [version] = await this.client.accessSecretVersion({ name });
      const value = version.payload?.data?.toString() || '';

      // Cache for 5 minutes
      this.cache.set(secretName, {
        value,
        expiry: Date.now() + this.CACHE_TTL
      });

      return value;
    } catch (error) {
      console.error(`Failed to fetch secret ${secretName}:`, error);
      throw new Error(`Secret ${secretName} not found or inaccessible`);
    }
  }

  async getDatabaseUrl(): Promise<string> {
    return this.getSecret('database-url');
  }

  async getJwtSecret(): Promise<string> {
    return this.getSecret('jwt-secret');
  }

  async getApiKey(service: string): Promise<string> {
    return this.getSecret(`${service}-api-key`);
  }

  clearCache(): void {
    this.cache.clear();
  }
}

// Singleton instance
export const secretManager = new SecretManager();

// Usage example
const dbUrl = await secretManager.getDatabaseUrl();
const jwtSecret = await secretManager.getJwtSecret();
```

### Environment-Aware Configuration

```typescript
// config/index.ts
import { secretManager } from './secrets';

export interface Config {
  database: {
    url: string;
  };
  auth: {
    jwtSecret: string;
    jwtExpiry: string;
  };
  api: {
    openaiKey: string;
    stripeKey: string;
  };
  sentry: {
    dsn: string;
  };
}

export async function loadConfig(): Promise<Config> {
  const env = process.env.NODE_ENV || 'development';

  if (env === 'production') {
    // Load from Google Secret Manager
    return {
      database: {
        url: await secretManager.getDatabaseUrl()
      },
      auth: {
        jwtSecret: await secretManager.getJwtSecret(),
        jwtExpiry: '7d'
      },
      api: {
        openaiKey: await secretManager.getApiKey('openai'),
        stripeKey: await secretManager.getApiKey('stripe')
      },
      sentry: {
        dsn: await secretManager.getSecret('sentry-dsn')
      }
    };
  } else {
    // Load from .env file
    return {
      database: {
        url: process.env.DATABASE_URL!
      },
      auth: {
        jwtSecret: process.env.JWT_SECRET!,
        jwtExpiry: '7d'
      },
      api: {
        openaiKey: process.env.OPENAI_API_KEY!,
        stripeKey: process.env.STRIPE_API_KEY!
      },
      sentry: {
        dsn: process.env.SENTRY_DSN!
      }
    };
  }
}

// Validate all required secrets are present
export async function validateConfig(config: Config): Promise<void> {
  const missing: string[] = [];

  if (!config.database.url) missing.push('DATABASE_URL');
  if (!config.auth.jwtSecret) missing.push('JWT_SECRET');
  if (!config.api.openaiKey) missing.push('OPENAI_API_KEY');

  if (missing.length > 0) {
    throw new Error(`Missing required secrets: ${missing.join(', ')}`);
  }
}

// Export singleton
let config: Config | null = null;

export async function getConfig(): Promise<Config> {
  if (!config) {
    config = await loadConfig();
    await validateConfig(config);
  }
  return config;
}
```

---

## Python Secret Management

```python
from google.cloud import secretmanager
from functools import lru_cache
import os

class SecretManager:
    def __init__(self):
        self.client = secretmanager.SecretManagerServiceClient()
        self.project_id = os.getenv('GCP_PROJECT', 'pnkln-prod')

    @lru_cache(maxsize=128)
    def get_secret(self, secret_name: str) -> str:
        """Get secret from Google Secret Manager (cached)"""
        name = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"

        try:
            response = self.client.access_secret_version(request={"name": name})
            return response.payload.data.decode('UTF-8')
        except Exception as e:
            raise ValueError(f"Failed to fetch secret {secret_name}: {e}")

    def get_database_url(self) -> str:
        return self.get_secret('database-url')

    def get_jwt_secret(self) -> str:
        return self.get_secret('jwt-secret')

    def get_api_key(self, service: str) -> str:
        return self.get_secret(f'{service}-api-key')

# Singleton instance
secret_manager = SecretManager()

# Usage
db_url = secret_manager.get_database_url()
jwt_secret = secret_manager.get_jwt_secret()
```

---

## Secret Rotation

### Automated Rotation Script

```typescript
import { SecretManagerServiceClient } from '@google-cloud/secret-manager';
import crypto from 'crypto';

export async function rotateSecret(secretName: string): Promise<void> {
  const client = new SecretManagerServiceClient();
  const projectId = process.env.GCP_PROJECT!;

  // Generate new secret value (example: API key)
  const newValue = `sk-${crypto.randomBytes(32).toString('hex')}`;

  // Create new version
  const parent = `projects/${projectId}/secrets/${secretName}`;
  await client.addSecretVersion({
    parent,
    payload: {
      data: Buffer.from(newValue)
    }
  });

  console.log(`Rotated secret: ${secretName}`);

  // Disable previous versions after grace period
  await disableOldVersions(secretName, 2); // Keep last 2 versions
}

async function disableOldVersions(
  secretName: string,
  keepCount: number
): Promise<void> {
  const client = new SecretManagerServiceClient();
  const projectId = process.env.GCP_PROJECT!;
  const parent = `projects/${projectId}/secrets/${secretName}`;

  const [versions] = await client.listSecretVersions({ parent });

  // Sort by creation time (newest first)
  const sortedVersions = versions
    .filter(v => v.state === 'ENABLED')
    .sort((a, b) => {
      const timeA = a.createTime?.seconds || 0;
      const timeB = b.createTime?.seconds || 0;
      return Number(timeB) - Number(timeA);
    });

  // Disable old versions
  for (let i = keepCount; i < sortedVersions.length; i++) {
    const version = sortedVersions[i];
    if (version.name) {
      await client.disableSecretVersion({ name: version.name });
      console.log(`Disabled old version: ${version.name}`);
    }
  }
}

// Schedule rotation (example: every 90 days)
setInterval(
  async () => {
    await rotateSecret('api-key');
    await rotateSecret('jwt-secret');
  },
  90 * 24 * 60 * 60 * 1000 // 90 days
);
```

---

## Docker/Kubernetes Deployment

### Dockerfile (No Secrets)

```dockerfile
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Build application
RUN npm run build

# Run as non-root user
USER node

# Secrets injected at runtime via environment variables
CMD ["npm", "start"]
```

### Kubernetes Secret Integration

```yaml
# k8s/secret-manager.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: pnkln-backend
  annotations:
    iam.gke.io/gcp-service-account: redacted@shadowtag-v4.local

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pnkln-backend
spec:
  template:
    spec:
      serviceAccountName: pnkln-backend
      containers:
      - name: backend
        image: gcr.io/pnkln-prod/backend:latest
        env:
        - name: GCP_PROJECT
          value: "pnkln-prod"
        - name: NODE_ENV
          value: "production"
        # Secrets loaded from Google Secret Manager at runtime
        # No hardcoded secrets in deployment config
```

---

## Security Checklist

- [ ] All `.env` files in `.gitignore`
- [ ] No hardcoded secrets in code/config files
- [ ] Production secrets in Google Secret Manager
- [ ] Service accounts have minimal permissions (principle of least privilege)
- [ ] Secret rotation automated (90 days for API keys, 30 days for DB credentials)
- [ ] Old secret versions disabled after rotation grace period
- [ ] Secrets cached for max 5 minutes (reduce API calls)
- [ ] Secret access logged for audit trail
- [ ] Emergency secret rotation procedure documented
- [ ] Team members only have access to dev secrets (not prod)

---

## Common Mistakes

❌ **Committing `.env` files**
```bash
git add .env  # DON'T DO THIS!
```

❌ **Logging secrets**
```typescript
console.log('API Key:', apiKey);  // Exposes in logs!
```

❌ **Storing secrets in code**
```typescript
const API_KEY = 'sk-1234567890';  // NEVER!
```

❌ **Sharing secrets via Slack/email**
```
"Here's the production DB password: ..."  # Use Secret Manager!
```

✅ **Correct: Use environment variables**
```typescript
const apiKey = process.env.API_KEY!;
if (!apiKey) throw new Error('API_KEY not set');
```

---

**Best Practices:**
- Rotate secrets regularly (automated)
- Use different secrets for dev/staging/prod
- Never share secrets via chat/email
- Audit secret access monthly
- Have emergency rotation procedure
- Use service accounts (not user credentials)

**Last Updated:** 2025-11-15
