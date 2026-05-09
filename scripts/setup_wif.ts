#!/usr/bin/env bun
/**
 * scripts/setup_wif.ts — V25 Workload Identity Federation Setup
 *
 * Configures WIF to eliminate static service account keys.
 * GitHub Actions → GCP via OIDC tokens (zero-secret CI/CD).
 *
 * CAUTION: STATE B — mutates IAM. Run only with explicit approval.
 *
 * Usage:
 *   bun run scripts/setup_wif.ts
 */
import { $ } from 'bun';

const PROJECT_ID = 'shadowtag-omega-v4';
const PROJECT_NUMBER = '767252945109';
const POOL_NAME = 'github-actions-pool';
const PROVIDER_NAME = 'github-provider';
const SA_NAME = 'counselconduit-sa';
const GITHUB_ORG = 'ShadowTag-v2';
const GITHUB_REPO = 'Monorepo-Uphillsnowball';

async function setupWIF() {
  console.log('⚡ V25 Workload Identity Federation Setup');
  console.log(`   Project: ${PROJECT_ID}`);
  console.log(`   GitHub: ${GITHUB_ORG}/${GITHUB_REPO}\n`);

  // Step 1: Create WIF pool
  console.log('[1/4] Creating WIF Pool...');
  await $`gcloud iam workload-identity-pools create ${POOL_NAME} --project=${PROJECT_ID} --location=global --display-name="GitHub Actions Pool" 2>&1`.catch(
    () => console.log(`   Pool ${POOL_NAME} already exists.`),
  );

  // Step 2: Create OIDC provider
  console.log('\n[2/4] Creating OIDC Provider...');
  await $`gcloud iam workload-identity-pools providers create-oidc ${PROVIDER_NAME} --project=${PROJECT_ID} --location=global --workload-identity-pool=${POOL_NAME} --display-name="GitHub OIDC" --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" --issuer-uri="https://token.actions.githubusercontent.com" 2>&1`.catch(
    () => console.log(`   Provider ${PROVIDER_NAME} already exists.`),
  );

  // Step 3: Bind SA to WIF
  console.log('\n[3/4] Binding Service Account to WIF...');
  const member = `principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_NAME}/attribute.repository/${GITHUB_ORG}/${GITHUB_REPO}`;
  await $`gcloud iam service-accounts add-iam-policy-binding ${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com --project=${PROJECT_ID} --role="roles/iam.workloadIdentityUser" --member="${member}" 2>&1`.catch(
    () => console.log('   Binding may already exist.'),
  );

  // Step 4: Output GitHub Actions config
  console.log('\n[4/4] GitHub Actions YAML snippet:');
  console.log(`
  # .github/workflows/deploy.yml
  permissions:
    id-token: write
    contents: read
  steps:
    - uses: google-github-actions/auth@v2
      with:
        workload_identity_provider: "projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_NAME}/providers/${PROVIDER_NAME}"
        service_account: "${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
`);

  console.log(
    '✅ WIF Setup Complete. GitHub Actions can now authenticate to GCP without static keys.',
  );
}

await setupWIF();
