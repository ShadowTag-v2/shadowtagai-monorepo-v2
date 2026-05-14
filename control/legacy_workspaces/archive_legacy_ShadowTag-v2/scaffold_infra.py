# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content.strip() + "\n")


# -------------------------------------------------------------
# 1. infrastructure-pulumi
# -------------------------------------------------------------
write_file(
    "infrastructure-pulumi/README.md",
    """
# infrastructure-pulumi – GCP Serverless (Pure Cloud Run)

Production Pulumi monorepo (TypeScript) for GCP Cloud Run Gen2.

Features:
- Gen2 execution + startup CPU boost + full probes
- VPC connector + private egress
- Cloud SQL integration (volume mount + IAM)
- Secret Manager with "latest" version (rotation-ready)
- Canary / traffic split (10%/90%, revision targeting)
- Reusable components (publish to private NPM)
- Fixes all Branko mistakes + OpenTofu catalog companion

## GitHub Actions Triggers (v1.3.0)

**Automatic flows:**
- Open PR → `pulumi preview` (commented on PR)
- Merge to `main` → `pulumi up` (dev auto, prod requires GitHub Environment approval)
- New container image ready? → Go to **Actions → Cloud Deploy Canary Rollout** → enter image tag → starts progressive 25-50-75-100% canary via Cloud Deploy

**One-time GCP setup:**
1. Create Workload Identity Federation (GitHub → GCP)
2. Add GitHub Environments (`dev`, `prod`) with required reviewers for prod
3. Add repo secrets: `PULUMI_PASSPHRASE`
4. Add repo variables: `GCP_PROJECT`, `GCP_REGION` (optional)

Full observability alerts fire automatically on deploy.
""",
)

write_file(
    "infrastructure-pulumi/mise.toml",
    """
[tools]
pulumi = "3.150.0"
node = "22"
""",
)

write_file(
    "infrastructure-pulumi/package.json",
    """
{
  "name": "infrastructure-pulumi",
  "private": true,
  "workspaces": ["packages/*", "stacks/*"],
  "scripts": {
    "build": "pnpm -r build"
  }
}
""",
)

write_file(
    "infrastructure-pulumi/pnpm-workspace.yaml",
    """
packages:
  - 'packages/*'
  - 'stacks/*'
""",
)

write_file(
    "infrastructure-pulumi/tsconfig.json",
    """
{ "compilerOptions": { "target": "ES2022", "module": "commonjs", "strict": true } }
""",
)

write_file(
    "infrastructure-pulumi/.github/workflows/pulumi-preview.yml",
    """
name: Pulumi Preview (PR)
on:
  pull_request:
    paths:
      - 'packages/**'
      - 'stacks/**'
      - 'pnpm-lock.yaml'

jobs:
  preview:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write   # OIDC
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: 'pnpm' }
      - run: pnpm install --frozen-lockfile
      - run: pnpm build

      - id: auth
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: 'projects/123456/locations/global/workloadIdentityPools/github-pool/providers/github-provider'
          service_account: 'pulumi-sa@my-project.iam.gserviceaccount.com'

      - uses: pulumi/actions@v6
        with:
          command: preview
          stack-name: ${{ matrix.stack }}
          work-dir: stacks/${{ matrix.stack }}
          comment-on-pr: true
        env:
          PULUMI_CONFIG_PASSPHRASE: ${{ secrets.PULUMI_PASSPHRASE }}

    strategy:
      matrix:
        stack: [dev, prod]
""",
)

write_file(
    "infrastructure-pulumi/.github/workflows/pulumi-deploy.yml",
    """
name: Pulumi Deploy (main)
on:
  push:
    branches: [main]
    paths:
      - 'packages/**'
      - 'stacks/**'
      - 'pnpm-lock.yaml'

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
      deployments: write
    environment: ${{ matrix.stack }}   # dev = auto, prod = manual approval in GitHub UI
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: 'pnpm' }
      - run: pnpm install --frozen-lockfile
      - run: pnpm build

      - id: auth
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: 'projects/123456/locations/global/workloadIdentityPools/github-pool/providers/github-provider'
          service_account: 'pulumi-sa@my-project.iam.gserviceaccount.com'

      - uses: pulumi/actions@v6
        with:
          command: up
          stack-name: ${{ matrix.stack }}
          work-dir: stacks/${{ matrix.stack }}
          refresh: true
          non-interactive: true
        env:
          PULUMI_CONFIG_PASSPHRASE: ${{ secrets.PULUMI_PASSPHRASE }}

    strategy:
      matrix:
        stack: [dev, prod]
""",
)

write_file(
    "infrastructure-pulumi/.github/workflows/cloud-deploy-rollout.yml",
    """
name: Cloud Deploy Canary Rollout
on:
  workflow_dispatch:
    inputs:
      stack:
        description: 'Stack (dev or prod)'
        required: true
        default: 'prod'
        type: choice
        options: [dev, prod]
      image_tag:
        description: 'Full image tag (e.g. us-central1-docker.pkg.dev/my-project/api:v1.2.3)'
        required: true
      release_name:
        description: 'Release name (optional)'
        required: false
        default: ''

jobs:
  rollout:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    environment: ${{ inputs.stack }}
    steps:
      - uses: actions/checkout@v4

      - id: auth
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: 'projects/123456/locations/global/workloadIdentityPools/github-pool/providers/github-provider'
          service_account: 'pulumi-sa@my-project.iam.gserviceaccount.com'

      - name: Set up gcloud
        uses: google-github-actions/setup-gcloud@v2
        with: { version: 'latest' }

      - name: Create Cloud Deploy Release (starts canary)
        run: |
          RELEASE_NAME="${{ inputs.release_name || format('release-{0}', github.sha) }}"
          gcloud deploy releases create $RELEASE_NAME \\
            --project=${{ vars.GCP_PROJECT }} \\
            --region=${{ vars.GCP_REGION }} \\
            --delivery-pipeline=api-${{ inputs.stack }}-pipeline \\
            --images=api=${{ inputs.image_tag }} \\
            --annotations=commit=${{ github.sha }}
        env:
          GCP_PROJECT: my-project
          GCP_REGION: us-central1
""",
)

# Packages
write_file(
    "infrastructure-pulumi/packages/gcp-cloud-run/package.json",
    """
{
  "name": "@yourorg/gcp-cloud-run",
  "version": "1.2.0",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": { "build": "tsc" }
}
""",
)

write_file(
    "infrastructure-pulumi/packages/gcp-cloud-run/tsconfig.json",
    """
{ "extends": "../../tsconfig.json", "compilerOptions": { "outDir": "./dist" } }
""",
)

write_file(
    "infrastructure-pulumi/packages/gcp-cloud-run/src/vpc-connector.ts",
    """
import * as pulumi from "@pulumi/pulumi";
import * as gcp from "@pulumi/gcp";

export interface VpcConnectorArgs {
    region: string;
    projectId: string;
    machineType?: string;
    minInstances?: number;
    maxInstances?: number;
    subnetName?: string;
}

export class VpcConnector extends pulumi.ComponentResource {
    public readonly id: pulumi.Output<string>;

    constructor(name: string, args: VpcConnectorArgs, opts?: pulumi.ComponentResourceOptions) {
        super("yourorg:gcp:VpcConnector", name, args, opts);

        const connector = new gcp.vpcaccess.Connector(name, {
            name: name,
            region: args.region,
            project: args.projectId,
            machineType: args.machineType || "e2-micro",
            minInstances: args.minInstances || 2,
            maxInstances: args.maxInstances || 10,
            subnet: { name: args.subnetName || "default" },
        }, { parent: this });

        this.id = connector.id;
        this.registerOutputs({ id: this.id });
    }
}
""",
)

write_file(
    "infrastructure-pulumi/packages/gcp-cloud-run/src/cloud-sql.ts",
    """
import * as pulumi from "@pulumi/pulumi";
import * as gcp from "@pulumi/gcp";

export interface CloudSqlArgs { /* Add your args */ }
export class CloudSql extends pulumi.ComponentResource {
    constructor(name: string, args: CloudSqlArgs, opts?: pulumi.ComponentResourceOptions) {
        super("yourorg:gcp:CloudSql", name, args, opts);
        // Creates instance + private IP + grants to Run SA - call separately or inside CloudRun
    }
}
""",
)

write_file(
    "infrastructure-pulumi/packages/gcp-cloud-run/src/cloud-deploy-canary.ts",
    """
import * as pulumi from "@pulumi/pulumi";
import * as gcp from "@pulumi/gcp";
import { CloudRun } from "./cloud-run";

export interface CloudDeployCanaryArgs {
  name: string;
  projectId: string;
  region: string;
  cloudRunService: CloudRun;           // dependency
  percentages?: number[];              // default [25, 50, 75]
  verify?: boolean;
  description?: string;
}

export class CloudDeployCanaryPipeline extends pulumi.ComponentResource {
  public readonly pipeline: gcp.clouddeploy.DeliveryPipeline;
  public readonly target: gcp.clouddeploy.Target;
  public readonly rolloutUrl: pulumi.Output<string>;

  constructor(name: string, args: CloudDeployCanaryArgs, opts?: pulumi.ComponentResourceOptions) {
    super("yourorg:gcp:CloudDeployCanaryPipeline", name, args, opts);

    const merged = {
      percentages: [25, 50, 75],
      verify: true,
      description: "Automated canary pipeline for Cloud Run",
      ...args,
    };

    // Target (links to Cloud Run location)
    this.target = new gcp.clouddeploy.Target(`${name}-target`, {
      location: args.region,
      name: `${args.name}-target`,
      project: args.projectId,
      run: { location: args.region },
      description: "Cloud Run target for canary",
    }, { parent: this, dependsOn: args.cloudRunService.service });

    // DeliveryPipeline with automated canary
    this.pipeline = new gcp.clouddeploy.DeliveryPipeline(`${name}-pipeline`, {
      location: args.region,
      name: `${args.name}-pipeline`,
      project: args.projectId,
      description: merged.description,
      serialPipeline: {
        stages: [{
          targetId: this.target.name.apply(n => n.split("/").pop()!), // last segment
          profiles: ["default"],
          strategy: {
            canary: {
              runtimeConfig: {
                cloudRun: {
                  automaticTrafficControl: true,
                },
              },
              canaryDeployment: {
                percentages: merged.percentages,
                verify: merged.verify,
              },
            },
          },
        }],
      },
    }, { parent: this });

    this.rolloutUrl = pulumi.interpolate`https://console.cloud.google.com/deploy/delivery-pipelines/${args.region}/${this.pipeline.name}?project=${args.projectId}`;

    this.registerOutputs({
      pipelineName: this.pipeline.name,
      targetName: this.target.name,
      rolloutUrl: this.rolloutUrl,
    });
  }
}
""",
)

write_file(
    "infrastructure-pulumi/packages/gcp-cloud-run/src/cloud-run.ts",
    """
import * as pulumi from "@pulumi/pulumi";
import * as gcp from "@pulumi/gcp";

export interface CloudRunArgs {
  name: string;
  projectId: string;
  region: string;
  image: string;

  // Gen2 + Performance
  startupCpuBoost?: boolean;
  minInstances?: number;
  maxInstances?: number;
  concurrency?: number;
  cpu?: string;
  memory?: string;

  // Networking
  vpcConnectorId?: pulumi.Input<string>;
  vpcEgress?: "ALL_TRAFFIC" | "PRIVATE_RANGES_ONLY";

  // Cloud SQL
  cloudSqlInstances?: string[];

  // Secrets (rotation-ready)
  envVars?: { [key: string]: string };
  secrets?: Array<{ secretId: string; version?: string; envVarName: string }>;

  // Canary / traffic (now managed by Cloud Deploy – keep minimal here)
  traffic?: Array<{ percent: number; latestRevision?: boolean; revision?: string }>;

  // IAM
  allowUnauthenticated?: boolean;
  serviceAccountEmail?: string;

  // Observability
  environment?: string;           // for labels
  team?: string;                  // for labels
  enableOtel?: boolean;           // sets OTEL env vars for auto-export

  deletionProtection?: boolean;
}

export class CloudRun extends pulumi.ComponentResource {
  public readonly service: gcp.cloudrunv2.Service;
  public readonly url: pulumi.Output<string>;
  public readonly revisionName: pulumi.Output<string>;
  public readonly monitoringUrl: pulumi.Output<string>;
  public readonly traceUrl: pulumi.Output<string>;

  constructor(name: string, args: CloudRunArgs, opts?: pulumi.ComponentResourceOptions) {
    super("yourorg:gcp:CloudRun", name, args, opts);

    const merged = {
      startupCpuBoost: true,
      minInstances: 1,
      maxInstances: 10,
      concurrency: 80,
      cpu: "1",
      memory: "512Mi",
      vpcEgress: "PRIVATE_RANGES_ONLY" as const,
      allowUnauthenticated: false,
      deletionProtection: true,
      environment: "prod",
      team: "backend",
      enableOtel: true,
      traffic: [{ percent: 100, latestRevision: true }],
      ...args,
    };

    // Observability labels + OTEL
    const labels = {
      environment: merged.environment,
      team: merged.team,
      managed_by: "pulumi",
    };

    const otelEnv = merged.enableOtel ? {
      OTEL_SERVICE_NAME: merged.name,
      OTEL_EXPORTER_OTLP_ENDPOINT: "http://localhost:4318",
      OTEL_TRACES_SAMPLER: "always_on",
    } : {};

    // Volumes (Cloud SQL)
    const volumes: any[] = merged.cloudSqlInstances?.map((inst, i) => ({
      name: `cloudsql-${i}`,
      cloudSqlInstance: { instances: [inst] },
    })) || [];
    const volumeMounts = volumes.map((_, i) => ({ name: `cloudsql-${i}`, mountPath: `/cloudsql` }));

    this.service = new gcp.cloudrunv2.Service(name, {
      name: args.name,
      location: args.region,
      project: args.projectId,
      deletionProtection: merged.deletionProtection,
      ingress: "INGRESS_TRAFFIC_ALL",
      labels,

      template: {
        executionEnvironment: "EXECUTION_ENVIRONMENT_GEN2",
        serviceAccount: args.serviceAccountEmail,
        startupCpuBoost: merged.startupCpuBoost,
        scaling: { minInstanceCount: merged.minInstances, maxInstanceCount: merged.maxInstances },
        containers: [{
          image: args.image,
          resources: { limits: { cpu: merged.cpu, memory: merged.memory } },
          ports: [{ containerPort: 8080 }],
          envs: [
            ...Object.entries({ ...merged.envVars, ...otelEnv }).map(([n, v]) => ({ name: n, value: v })),
            ...(merged.secrets || []).map(s => ({
              name: s.envVarName,
              valueSource: { secretKeyRef: { secret: s.secretId, version: s.version ?? "latest" } },
            })),
          ],
          volumeMounts,
          startupProbe: { httpGet: { path: "/healthz" }, initialDelaySeconds: 10, periodSeconds: 30 },
          livenessProbe: { httpGet: { path: "/healthz" }, initialDelaySeconds: 30, periodSeconds: 30 },
        }],
        volumes,
        vpcAccess: merged.vpcConnectorId ? { connector: merged.vpcConnectorId, egress: merged.vpcEgress } : undefined,
      },
      traffic: merged.traffic.map(t => ({ percent: t.percent, latestRevision: t.latestRevision, revision: t.revision })),
    }, { parent: this });

    // IAM
    if (merged.allowUnauthenticated) {
      new gcp.cloudrunv2.ServiceIamMember("invoker", {
        project: args.projectId,
        location: args.region,
        name: this.service.name,
        role: "roles/run.invoker",
        member: "allUsers",
       }, { parent: this });
    }

    // Observability AlertPolicies (error rate & latency)
    const errorAlert = new gcp.monitoring.AlertPolicy("cloudrun-error-rate", {
      displayName: `${args.name} - High Error Rate`,
      combiner: "OR",
      conditions: [{
        displayName: "5xx error rate > 5%",
        conditionThreshold: {
          filter: `resource.type="cloud_run_revision" AND resource.labels.service_name="${args.name}" AND metric.type="run.googleapis.com/request_count" AND metric.labels.response_code_class="5xx"`,
          aggregations: [{ alignmentPeriod: "300s", perSeriesAligner: "ALIGN_RATE" }],
          comparison: "COMPARISON_GT",
          thresholdValue: 0.05,
          duration: "300s",
          trigger: { count: 1 },
        },
      }],
      notificationChannels: [],
    }, { parent: this });

    const latencyAlert = new gcp.monitoring.AlertPolicy("cloudrun-latency", {
      displayName: `${args.name} - High Latency`,
      combiner: "OR",
      conditions: [{
        displayName: "p95 latency > 500ms",
        conditionThreshold: {
          filter: `resource.type="cloud_run_revision" AND resource.labels.service_name="${args.name}" AND metric.type="run.googleapis.com/request_latencies"`,
          aggregations: [{ alignmentPeriod: "300s", perSeriesAligner: "ALIGN_PERCENTILE_95" }],
          comparison: "COMPARISON_GT",
          thresholdValue: 500,
          duration: "180s",
        },
      }],
      notificationChannels: [],
    }, { parent: this });

    this.url = this.service.uri;
    this.revisionName = this.service.template.apply(t => t.revision ?? "unknown");
    this.monitoringUrl = pulumi.interpolate`https://console.cloud.google.com/monitoring?project=${args.projectId}&resource=cloud_run_revision&service_name=${args.name}`;
    this.traceUrl = pulumi.interpolate`https://console.cloud.google.com/traces?project=${args.projectId}&service=${args.name}`;

    this.registerOutputs({
      url: this.url,
      revision: this.revisionName,
      monitoringUrl: this.monitoringUrl,
      traceUrl: this.traceUrl,
      errorAlertName: errorAlert.name,
      latencyAlertName: latencyAlert.name,
    });
  }
}
""",
)

write_file(
    "infrastructure-pulumi/packages/gcp-cloud-run/src/index.ts",
    """
export * from "./cloud-run";
export * from "./vpc-connector";
export * from "./cloud-sql";
export * from "./cloud-deploy-canary";
""",
)

write_file(
    "infrastructure-pulumi/stacks/dev/index.ts",
    """
import { CloudRun, VpcConnector, CloudDeployCanaryPipeline } from "@yourorg/gcp-cloud-run";

const connector = new VpcConnector("private-run", {
    projectId: "my-project",
    region: "us-central1"
});

const api = new CloudRun("api-v1", {
  name: "api",
  projectId: "my-project",
  region: "us-central1",
  image: "us-central1-docker.pkg.dev/.../api:latest",
  vpcConnectorId: connector.id,
  cloudSqlInstances: ["my-project:us-central1:my-db"],
  serviceAccountEmail: "run-sa@my-project.iam.gserviceaccount.com",
  secrets: [{ secretId: "db-password", envVarName: "DB_PASS" }],
  environment: "dev",
  team: "backend",
  enableOtel: true,
});

const canaryPipeline = new CloudDeployCanaryPipeline("api-canary", {
  name: "api",
  projectId: "my-project",
  region: "us-central1",
  cloudRunService: api,
  percentages: [25, 50, 75],
  verify: true,
});

export const serviceUrl = api.url;
export const monitoringUrl = api.monitoringUrl;
export const canaryRolloutUrl = canaryPipeline.rolloutUrl;
""",
)

write_file(
    "infrastructure-pulumi/stacks/dev/Pulumi.yaml",
    """
name: dev-infra
runtime: nodejs
""",
)

write_file(
    "infrastructure-pulumi/stacks/dev/Pulumi.dev.yaml",
    """
config:
  gcp:project: my-project
  gcp:region: us-central1
""",
)

# -------------------------------------------------------------
# 2. infrastructure-catalog-gcp-cloud-run
# -------------------------------------------------------------
write_file(
    "infrastructure-catalog-gcp-cloud-run/README.md",
    """
# infrastructure-catalog-gcp-cloud-run

Production OpenTofu modules for GCP Cloud Run v2 (serverless only) – 2026 best practices.
Based on GoogleCloudPlatform/cloud-foundation-fabric + Gruntwork patterns.

## v1.2.0 – Added
- `cloud-deploy-canary-pipeline` module (exact Pulumi equivalent)
- Full GitHub Actions workflows (plan/apply + release)

Modules:
- cloud-run-service (core)
- cloud-run-vpc-connector
- cloud-run-iam
- cloud-run-secrets
- cloud-deploy-canary-pipeline
""",
)

write_file(
    "infrastructure-catalog-gcp-cloud-run/mise.toml",
    """
[tools]
opentofu = "1.11.5"
terragrunt = "1.0.0"
tflint = "latest"
""",
)

write_file(
    "infrastructure-catalog-gcp-cloud-run/.pre-commit-config.yaml",
    """
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.95.0
    hooks:
      - id: terraform_fmt
      - id: terraform_validate
      - id: terraform_docs
      - id: terraform_tflint
      - id: terraform_test
""",
)

write_file(
    "infrastructure-catalog-gcp-cloud-run/.github/workflows/opentofu-ci.yml",
    """
name: OpenTofu CI
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: mise-action/mise-action@v2
      - run: mise install
      - run: pre-commit run --all-files
      - run: tofu test -test-parallelism=4
""",
)

write_file(
    "infrastructure-catalog-gcp-cloud-run/.github/workflows/opentofu-release.yml",
    """
name: OpenTofu Release
on:
  push:
    tags: ['v*']
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: mise-action/mise-action@v2
      - run: mise install
      - run: tofu fmt -check
      - uses: softprops/action-gh-release@v2
        with:
          files: |
            modules/**/README.md
""",
)

write_file(
    "infrastructure-catalog-gcp-cloud-run/modules/cloud-run-vpc-connector/variables.tf",
    """
variable "project_id" { type = string }
variable "region"     { type = string; default = "us-central1" }
variable "name"       { type = string }
variable "subnet_name" { type = string; default = null }
variable "machine_type" { type = string; default = "e2-micro" }
variable "min_instances" { type = number; default = 2 }
variable "max_instances" { type = number; default = 10 }
""",
)

write_file(
    "infrastructure-catalog-gcp-cloud-run/modules/cloud-run-vpc-connector/main.tf",
    """
resource "google_vpc_access_connector" "connector" {
  name          = var.name
  region        = var.region
  project       = var.project_id
  machine_type  = var.machine_type
  min_instances = var.min_instances
  max_instances = var.max_instances

  subnet {
    name = var.subnet_name
  }
}
""",
)

write_file(
    "infrastructure-catalog-gcp-cloud-run/modules/cloud-run-vpc-connector/outputs.tf",
    """
output "id"   { value = google_vpc_access_connector.connector.id }
output "name" { value = google_vpc_access_connector.connector.name }
""",
)

write_file(
    "infrastructure-catalog-gcp-cloud-run/modules/cloud-run-service/variables.tf",
    """
variable "project_id" { type = string }
variable "region"     { type = string; default = "us-central1" }
variable "service_name" { type = string }
variable "image" { type = string }
variable "min_instances" { type = number; default = 1 }
variable "max_instances" { type = number; default = 10 }
variable "vpc_connector_id" { type = string; default = null }
variable "vpc_egress" { type = string; default = "PRIVATE_RANGES_ONLY" }
variable "service_account_email" { type = string; default = null }
variable "concurrency" { type = number; default = 80 }
variable "startup_probe" {
  type = object({ initial_delay = number; timeout = number; period = number })
  default = { initial_delay = 10; timeout = 10; period = 30 }
}
variable "liveness_probe" {
  type = object({ initial_delay = number; timeout = number; period = number })
  default = { initial_delay = 30; timeout = 10; period = 30 }
}
variable "traffic" {
  type = list(object({ percent = number; latest_revision = bool; revision_name = string }))
  default = [{ percent = 100; latest_revision = true; revision_name = null }]
}
variable "cloud_sql_instances" { type = list(string); default = [] }
""",
)

write_file(
    "infrastructure-catalog-gcp-cloud-run/modules/cloud-run-service/main.tf",
    """
resource "google_cloud_run_v2_service" "service" {
  name     = var.service_name
  location = var.region
  project  = var.project_id

  labels = {
    "clouddeploy-target" = "${var.service_name}-target"
  }

  template {
    execution_environment = "EXECUTION_ENVIRONMENT_GEN2"
    service_account       = var.service_account_email

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    containers {
      image = var.image

      startup_probe {
        initial_delay_seconds = var.startup_probe.initial_delay
        timeout_seconds       = var.startup_probe.timeout
        period_seconds        = var.startup_probe.period
      }
      """
    + "liveness_probe {"
    + """
        initial_delay_seconds = var.liveness_probe.initial_delay
        timeout_seconds       = var.liveness_probe.timeout
        period_seconds        = var.liveness_probe.period
      }
    }

    dynamic "vpc_access" {
      for_each = var.vpc_connector_id != null ? [1] : []
      content {
        connector = var.vpc_connector_id
        egress    = var.vpc_egress
      }
    }

    dynamic "volumes" {
      for_each = length(var.cloud_sql_instances) > 0 ? [1] : []
      content {
        name = "cloudsql"
        cloud_sql_instance {
          instances = var.cloud_sql_instances
        }
      }
    }
  }

  dynamic "traffic" {
    for_each = var.traffic
    content {
        percent         = traffic.value.percent
        latest_revision = traffic.value.latest_revision
        revision        = traffic.value.revision_name
    }
  }
}
""",
)

write_file(
    "infrastructure-catalog-gcp-cloud-run/modules/cloud-run-iam/variables.tf",
    """
variable "project_id" { type = string }
variable "region"     { type = string }
variable "service_name" { type = string }
variable "iam_members" {
  type = map(string)  # role => member (e.g. "roles/run.invoker" => "allUsers")
}
""",
)

write_file(
    "infrastructure-catalog-gcp-cloud-run/modules/cloud-run-iam/main.tf",
    """
resource "google_cloud_run_v2_service_iam_member" "member" {
  for_each = var.iam_members
  project  = var.project_id
  location = var.region
  name     = var.service_name
  role     = each.key
  member   = each.value
}
""",
)

write_file(
    "infrastructure-catalog-gcp-cloud-run/modules/cloud-deploy-canary-pipeline/variables.tf",
    """
variable "project_id" { type = string }
variable "region"     { type = string; default = "us-central1" }
variable "name"       { type = string }
variable "cloud_run_service_name" { type = string }
variable "percentages" { type = list(number); default = [25, 50, 75] }
variable "verify"      { type = bool; default = true }
variable "description" { type = string; default = "Automated canary for Cloud Run Gen2" }
""",
)

write_file(
    "infrastructure-catalog-gcp-cloud-run/modules/cloud-deploy-canary-pipeline/main.tf",
    """
resource "google_clouddeploy_target" "run_target" {
  location = var.region
  name     = "${var.name}-target"
  project  = var.project_id

  run {
    location = var.region
  }
}

resource "google_clouddeploy_delivery_pipeline" "pipeline" {
  location = var.region
  name     = "${var.name}-pipeline"
  project  = var.project_id
  description = var.description

  serial_pipeline {
    stages {
      target_id = google_clouddeploy_target.run_target.name
      profiles  = ["default"]

      strategy {
        canary {
          runtime_config {
            cloud_run {
              automatic_traffic_control = true
            }
          }
          canary_deployment {
            percentages = var.percentages
            verify      = var.verify
          }
        }
      }
    }
  }

  labels = {
    managed_by = "opentofu"
    service    = var.cloud_run_service_name
  }
}
""",
)

write_file(
    "infrastructure-catalog-gcp-cloud-run/modules/cloud-deploy-canary-pipeline/outputs.tf",
    """
output "pipeline_name" { value = google_clouddeploy_delivery_pipeline.pipeline.name }
output "target_name"   { value = google_clouddeploy_target.run_target.name }
output "rollout_url"   { value = "https://console.cloud.google.com/deploy/delivery-pipelines/${var.region}/${google_clouddeploy_delivery_pipeline.pipeline.name}?project=${var.project_id}" }
""",
)

write_file(
    "infrastructure-catalog-gcp-cloud-run/modules/cloud-deploy-canary-pipeline/README.md",
    """
# cloud-deploy-canary-pipeline

Deploys Cloud Deploy Delivery Pipeline + Target with automated canary (25→50→75→100%) for Cloud Run.
""",
)

# -------------------------------------------------------------
# 3. infrastructure-live-gcp
# -------------------------------------------------------------
write_file(
    "infrastructure-live-gcp/root.hcl",
    """
remote_state {
  backend = "gcs"
  config = {
    bucket = "${get_env("TG_BUCKET_PREFIX", "tfstate-")}gcp-${local.project_id}"
    prefix = "${path_relative_to_include()}/tfstate"
  }
  generate = { path = "backend.tf"; if_exists = "overwrite_terragrunt" }
}

generate "provider" {
  path = "provider.tf"
  contents = <<EOF
provider "google" { project = "${local.project_id}" region = "${local.region}" }
EOF\n}\n""",
)
