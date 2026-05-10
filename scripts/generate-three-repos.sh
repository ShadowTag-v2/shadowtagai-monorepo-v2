#!/bin/bash
set -euo pipefail

echo "🏗 Generating infrastructure-catalog-gcp-cloud-run + infrastructure-live-gcp + infrastructure-pulumi"

BASE="agnt-os-infrastructure-repos"
rm -rf $BASE
mkdir -p $BASE

# ============================================================
# REPO 1: infrastructure-catalog-gcp-cloud-run (OpenTofu)
# ============================================================
mkdir -p $BASE/infrastructure-catalog-gcp-cloud-run/{modules/cloud-run-service,modules/cloud-deploy-canary-pipeline,examples/complete,.github/workflows}

cat > $BASE/infrastructure-catalog-gcp-cloud-run/README.md << 'EOF'
# infrastructure-catalog-gcp-cloud-run v1.2.0

Production OpenTofu modules for GCP Cloud Run Gen2 + Cloud Deploy Canary.
EOF

cat > $BASE/infrastructure-catalog-gcp-cloud-run/modules/cloud-run-service/main.tf << 'EOF'
resource "google_cloud_run_v2_service" "service" {
  name     = var.service_name
  location = var.region
  project  = var.project_id

  template {
    execution_environment = "EXECUTION_ENVIRONMENT_GEN2"
    startup_cpu_boost     = true

    containers {
      image = var.image
      resources { limits = { cpu = var.cpu, memory = var.memory } }

      startup_probe {
        http_get { path = "/healthz" }
        initial_delay_seconds = 10
        period_seconds        = 30
      }
    }
  }

  traffic {
    for_each = var.traffic
    percent         = each.value.percent
    latest_revision = each.value.latest_revision
  }
}
EOF

cat > $BASE/infrastructure-catalog-gcp-cloud-run/modules/cloud-deploy-canary-pipeline/main.tf << 'EOF'
resource "google_clouddeploy_delivery_pipeline" "pipeline" {
  name     = "${var.name}-pipeline"
  location = var.region
  project  = var.project_id

  serial_pipeline {
    stages {
      target_id = google_clouddeploy_target.run_target.name
      strategy {
        canary {
          runtime_config { cloud_run { automatic_traffic_control = true } }
          canary_deployment {
            percentages = var.percentages
            verify      = var.verify
          }
        }
      }
    }
  }
}
EOF

cat > $BASE/infrastructure-catalog-gcp-cloud-run/.github/workflows/ci.yml << 'EOF'
name: OpenTofu CI
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: mise-action/mise-action@v2
      - run: mise install && pre-commit run --all-files
EOF

# ============================================================
# REPO 2: infrastructure-live-gcp (Terragrunt)
# ============================================================
mkdir -p $BASE/infrastructure-live-gcp/non-prod/us-central1/api-service/.github/workflows

cat > $BASE/infrastructure-live-gcp/root.hcl << 'EOF'
remote_state {
  backend = "gcs"
  config = {
    bucket = "tfstate-${local.project_id}"
    prefix = "${path_relative_to_include()}/tfstate"
  }
  generate = { path = "backend.tf"; if_exists = "overwrite_terragrunt" }
}
EOF

cat > $BASE/infrastructure-live-gcp/non-prod/us-central1/api-service/terragrunt.stack.hcl << 'EOF'
unit "cloud-run" {
  source = "git::https://github.com/ShadowTag-v2/infrastructure-catalog-gcp-cloud-run.git//modules/cloud-run-service?ref=v1.2.0"
  values = { service_name = "api", image = "us-central1-docker.pkg.dev/shadowtag-omega-v4/api:latest" }
}

unit "cloud-deploy" {
  source = "git::https://github.com/ShadowTag-v2/infrastructure-catalog-gcp-cloud-run.git//modules/cloud-deploy-canary-pipeline?ref=v1.2.0"
  values = { name = "api", cloud_run_service_name = dependency.cloud-run.outputs.service_name }
}
EOF

# ============================================================
# REPO 3: infrastructure-pulumi (Pulumi TypeScript)
# ============================================================
mkdir -p $BASE/infrastructure-pulumi/packages/gcp-cloud-run/src $BASE/infrastructure-pulumi/stacks/dev $BASE/infrastructure-pulumi/.github/workflows

cat > $BASE/infrastructure-pulumi/packages/gcp-cloud-run/src/cloud-run.ts << 'EOF'
import * as pulumi from "@pulumi/pulumi";
import * as gcp from "@pulumi/gcp";

export class CloudRun extends pulumi.ComponentResource {
  public readonly url: pulumi.Output<string>;

  constructor(name: string, args: any, opts?: pulumi.ComponentResourceOptions) {
    super("shadowtag:gcp:CloudRun", name, args, opts);

    const service = new gcp.cloudrunv2.Service(name, {
      name: args.name,
      location: args.region,
      project: args.projectId,
      template: {
        executionEnvironment: "EXECUTION_ENVIRONMENT_GEN2",
        startupCpuBoost: true,
        containers: [{
          image: args.image,
          resources: { limits: { cpu: "1", memory: "512Mi" } },
          startupProbe: { httpGet: { path: "/healthz" }, initialDelaySeconds: 10 },
        }],
      },
      traffic: args.traffic || [{ percent: 100, latestRevision: true }],
    });

    this.url = service.uri;
    this.registerOutputs({ url: this.url });
  }
}
EOF

cat > $BASE/infrastructure-pulumi/stacks/dev/index.ts << 'EOF'
import { CloudRun } from "@shadowtag/gcp-cloud-run";

const api = new CloudRun("api-v1", {
  name: "api",
  projectId: "shadowtag-omega-v4",
  region: "us-central1",
  image: "us-central1-docker.pkg.dev/shadowtag-omega-v4/api:latest",
});

export const url = api.url;
EOF

cat > $BASE/infrastructure-pulumi/.github/workflows/pulumi-deploy.yml << 'EOF'
name: Pulumi Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ matrix.stack }}
    steps:
      - uses: actions/checkout@v4
      - uses: pulumi/actions@v6
        with:
          command: up
          stack-name: ${{ matrix.stack }}
EOF

echo ""
echo "✅ All three repos generated in: $BASE/"
echo "📦 Create zips with:"
echo "zip -r infrastructure-catalog-gcp-cloud-run.zip $BASE/infrastructure-catalog-gcp-cloud-run"
echo "zip -r infrastructure-live-gcp.zip $BASE/infrastructure-live-gcp"
echo "zip -r infrastructure-pulumi.zip $BASE/infrastructure-pulumi"
