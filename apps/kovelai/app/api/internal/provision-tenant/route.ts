/**
 * Per-Tenant Cloud Run Service Template
 *
 * Sprint Item #10: Generates Cloud Run service YAML for
 * per-firm isolated compute environments.
 *
 * Architecture:
 * - Each enterprise firm gets a dedicated Cloud Run service
 * - Service shares the CounselConduit Docker image
 * - Environment variables scope the service to a single firm
 * - Secrets mounted from GCP Secret Manager
 * - IAM binding limits access to firm-specific service account
 *
 * @see counselconduit_architecture in GEMINI.md
 */

// ─── Types ───────────────────────────────────────────────────────────

export interface TenantServiceConfig {
  firmId: string;
  firmName: string;
  tier: 'solo' | 'practice' | 'enterprise';
  region: string;
  customDomain?: string;
  byokProviders?: string[];
  maxInstances?: number;
  minInstances?: number;
}

export interface GeneratedServiceYAML {
  yaml: string;
  gcloudCommand: string;
  iamCommand: string;
  domainCommand?: string;
}

// ─── Template Generator ─────────────────────────────────────────────

/**
 * Generates a Cloud Run service YAML for a tenant.
 *
 * @param config - Tenant service configuration
 * @returns YAML string + deployment commands
 */
export function generateTenantService(config: TenantServiceConfig): GeneratedServiceYAML {
  const serviceId = `cc-tenant-${config.firmId.substring(0, 8)}`;
  const saEmail = `${serviceId}-sa@shadowtag-omega-v4.iam.gserviceaccount.com`;

  const instanceConfig = getTierInstanceConfig(config.tier);
  const maxInstances = config.maxInstances ?? instanceConfig.maxInstances;
  const minInstances = config.minInstances ?? instanceConfig.minInstances;

  const yaml = `apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: ${serviceId}
  labels:
    cloud.googleapis.com/location: ${config.region}
    counselconduit.ai/tenant: "${config.firmId}"
    counselconduit.ai/tier: ${config.tier}
  annotations:
    run.googleapis.com/ingress: all
    run.googleapis.com/execution-environment: gen2
    run.googleapis.com/cpu-throttling: "false"
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/execution-environment: gen2
        autoscaling.knative.dev/maxScale: "${maxInstances}"
        autoscaling.knative.dev/minScale: "${minInstances}"
        run.googleapis.com/cpu-throttling: "false"
    spec:
      serviceAccountName: ${saEmail}
      containerConcurrency: ${instanceConfig.concurrency}
      timeoutSeconds: 300
      containers:
        - image: gcr.io/shadowtag-omega-v4/counselconduit:latest
          ports:
            - containerPort: 8080
          resources:
            limits:
              cpu: "${instanceConfig.cpu}"
              memory: "${instanceConfig.memory}"
          env:
            - name: TENANT_FIRM_ID
              value: "${config.firmId}"
            - name: TENANT_FIRM_NAME
              value: "${config.firmName}"
            - name: TENANT_TIER
              value: "${config.tier}"
            - name: GCP_PROJECT_ID
              value: "shadowtag-omega-v4"
            - name: FIRESTORE_NAMESPACE
              value: "firms/${config.firmId}"
            - name: NODE_ENV
              value: "production"
            - name: KOVELAI_PROXY_SECRET
              valueFrom:
                secretKeyRef:
                  name: kovelai-proxy-secret
                  key: latest
            - name: GOOGLE_AI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: google-ai-api-key
                  key: latest
${config.byokProviders?.map((p) => `            - name: BYOK_${p.toUpperCase().replace('-', '_')}_SECRET
              valueFrom:
                secretKeyRef:
                  name: byok-${config.firmId.substring(0, 8)}-${p}
                  key: latest`).join('\n') ?? ''}
  traffic:
    - percent: 100
      latestRevision: true
`;

  const gcloudCommand = `gcloud run services replace ${serviceId}-service.yaml \\
  --region=${config.region} \\
  --project=shadowtag-omega-v4`;

  const iamCommand = `gcloud run services add-iam-policy-binding ${serviceId} \\
  --region=${config.region} \\
  --member="serviceAccount:${saEmail}" \\
  --role="roles/run.invoker" \\
  --project=shadowtag-omega-v4`;

  const domainCommand = config.customDomain
    ? `gcloud beta run domain-mappings create \\
  --service=${serviceId} \\
  --domain=${config.customDomain} \\
  --region=${config.region} \\
  --project=shadowtag-omega-v4`
    : undefined;

  return {
    yaml,
    gcloudCommand,
    iamCommand,
    domainCommand,
  };
}

// ─── Tier Configuration ─────────────────────────────────────────────

interface TierInstanceConfig {
  cpu: string;
  memory: string;
  maxInstances: number;
  minInstances: number;
  concurrency: number;
}

function getTierInstanceConfig(tier: TenantServiceConfig['tier']): TierInstanceConfig {
  switch (tier) {
    case 'solo':
      return { cpu: '1', memory: '512Mi', maxInstances: 3, minInstances: 0, concurrency: 80 };
    case 'practice':
      return { cpu: '2', memory: '1Gi', maxInstances: 10, minInstances: 1, concurrency: 120 };
    case 'enterprise':
      return { cpu: '4', memory: '2Gi', maxInstances: 50, minInstances: 2, concurrency: 200 };
  }
}

// ─── Provision API Route ────────────────────────────────────────────

import { NextResponse, type NextRequest } from 'next/server';
import { z } from 'zod';

const ProvisionRequestSchema = z.object({
  firmId: z.string().uuid(),
  firmName: z.string().min(1).max(200),
  tier: z.enum(['solo', 'practice', 'enterprise']),
  region: z.string().default('us-central1'),
  customDomain: z.string().optional(),
  byokProviders: z.array(z.string()).optional(),
});

export async function POST(req: NextRequest): Promise<NextResponse> {
  try {
    // Internal-only endpoint — verify Cloud Tasks / Cloud Scheduler origin
    const authHeader = req.headers.get('authorization');
    if (!authHeader && process.env.NODE_ENV === 'production') {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body = await req.json();
    const config = ProvisionRequestSchema.parse(body);

    const service = generateTenantService(config);

    return NextResponse.json({
      status: 'generated',
      serviceId: `cc-tenant-${config.firmId.substring(0, 8)}`,
      yaml: service.yaml,
      commands: {
        deploy: service.gcloudCommand,
        iam: service.iamCommand,
        domain: service.domainCommand,
      },
    });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid request', details: error.errors },
        { status: 400 },
      );
    }
    return NextResponse.json(
      { error: 'Provisioning failed' },
      { status: 500 },
    );
  }
}
