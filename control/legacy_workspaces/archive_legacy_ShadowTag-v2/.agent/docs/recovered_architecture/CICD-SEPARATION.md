# CI/CD Pipeline Separation

This document outlines the clear separation between the **CACI Package** CI/CD and the **Website** CI/CD pipelines.

## 🏗️ Architecture Overview

```

claude-code-configurator/
├── packages/caci/                           # CACI Package (CLI Tool)
│   ├── src/                        # ← Package CI/CD triggers
│   ├── tests/
│   ├── package.json
│   └── ...
├── packages/website/               # Website (Next.js)
│   ├── app/                        # ← Website CI/CD triggers  
│   ├── components/
│   ├── package.json
│   └── ...
└── .github/workflows/
    ├── ci.yml                      # Package CI Pipeline
    ├── publish-npm.yml             # Package NPM Publishing
    ├── publish-docker.yml          # Package Docker Publishing
    ├── security.yml                # Package Security Scans
    ├── e2e.yml                     # Package E2E Tests
    ├── benchmark.yml               # Package Performance Tests
    ├── website-ci.yml              # Website CI Pipeline
    └── deploy-website.yml          # Website Deployment

```

## 📦 CACI Package CI/CD

**Purpose**: Build, test, and publish the CACI CLI tool

### Workflows:


- **`ci.yml`** - Main CI pipeline (lint, format, build, test)

- **`publish-npm.yml`** - NPM package publishing

- **`publish-docker.yml`** - Docker image publishing  

- **`security.yml`** - Security scanning (scheduled)

- **`e2e.yml`** - E2E testing (scheduled)

- **`benchmark.yml`** - Performance benchmarks (scheduled)

### Triggers:


- **Paths**: `packages/caci/**` only

- **Excludes**: `!packages/caci/node_modules/**`, `!packages/caci/dist/**`, `!packages/caci/coverage/**`

- **Branches**: main, master, develop

- **Tags**: `v*` (for publishing)

### Working Directory: `packages/caci/`

## 🌐 Website CI/CD

**Purpose**: Build, test, and deploy the Next.js website

### Workflows:


- **`website-ci.yml`** - Website CI pipeline (lint, format, type-check, build, test)

- **`deploy-website.yml`** - Vercel deployment

### Triggers:


- **Paths**: `packages/website/**` only

- **Excludes**: `!packages/website/node_modules/**`, `!packages/website/.next/**`, `!packages/website/coverage/**`

- **Branches**: main, master, develop

### Working Directory: `packages/website/`

## 🔒 Separation Guarantees

### ✅ No Cross-Triggering


- Package changes **never** trigger website workflows

- Website changes **never** trigger package workflows

- Strict path filtering prevents accidents

### ✅ Independent Dependencies


- Package uses `packages/caci/package-lock.json`

- Website uses `packages/website/package-lock.json`

- No shared node_modules or build artifacts

### ✅ Clear Naming Convention


- **Package workflows**: Prefixed with "CACI Package"

- **Website workflows**: Prefixed with "Website" 

- No ambiguity about which system is being built

### ✅ Isolated Environments


- Different working directories

- Different caching strategies

- Different deployment targets

## 🚀 Benefits


1. **Performance**: Only relevant code triggers builds

2. **Reliability**: Failures in one system don't affect the other

3. **Maintainability**: Clear ownership and responsibility

4. **Scalability**: Easy to add more packages or websites

5. **Security**: Isolated secrets and permissions

## 📊 Workflow Execution Matrix

| Change Type | Package CI | Package Publish | Website CI | Website Deploy |
|-------------|------------|-----------------|------------|----------------|
| `packages/caci/src/` | ✅ Runs | 🟡 On tags | ❌ Skipped | ❌ Skipped |
| `packages/website/` | ❌ Skipped | ❌ Skipped | ✅ Runs | ✅ Runs |
| `README.md` | ❌ Skipped | ❌ Skipped | ❌ Skipped | ❌ Skipped |
| `v1.0.0` tag | ❌ Skipped | ✅ Runs | ❌ Skipped | ❌ Skipped |

## 🔧 Maintenance

### Adding New Package Workflows


1. Use working directory: `packages/caci/`

2. Add path filter: `packages/caci/**`

3. Prefix name with "CACI Package"

### Adding New Website Workflows  


1. Use working directory: `packages/website/`

2. Add path filter: `packages/website/**`

3. Prefix name with "Website"

### Verification Commands

```bash

# Test package CI triggers

git commit -m "test" packages/caci/src/test.ts

# Test website CI triggers  

git commit -m "test" packages/website/app/test.tsx

# Verify no cross-triggering

git log --oneline --name-only

```

---

**Last Updated**: 2025-08-22  
**Maintained By**: CI/CD Pipeline Team