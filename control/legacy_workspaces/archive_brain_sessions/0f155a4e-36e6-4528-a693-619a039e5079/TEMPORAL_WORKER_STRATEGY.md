# Temporal Worker Pools on Cloud Run: The "Sovereign" Orchestration Engine
**Doc ID:** Cor.58.3-TEMPORAL-STRATEGY
**Version:** 1.0
**Date:** Feb 2, 2026
**Source:** "The Surprising Simplicity of Temporal Worker Pools on Cloud Run" (Glenn Bostoen)

## 1. Executive Summary: The Architect's Pivot

We are shifting our orchestration paradigm from **Push-Based Ephemeral Jobs** (Cloud Workflows + Cloud Run Jobs) to **Pull-Based Persistent Workers** (Temporal Cloud + Cloud Run Worker Pools).

**Why?**
*   **Simplicity**: Replace spaghetti YAML with Python code (`@workflow.defn`).
*   **Performance**: Eliminate cold starts (35-70s -> <100ms).
*   **Testing**: Full local debugging with IDE support. "Deploy to test" is dead.
*   **Sovereignty**: Temporal handles state/orchestration; we control the compute (Cloud Run).

## 2. The Core Concept: Pull vs. Push

| Feature | Old Way (Cloud Run Jobs) | **New Way (Temporal Worker Pools)** |
| :--- | :--- | :--- |
| **Trigger** | Push (Event/HTTP) | Pull (Long-polling) |
| **State** | Stateless / External DB | Stateful (Workflow History) |
| **Latency** | Cold Start Tax (Low) | **Instant (Warm Workers)** |
| **Config** | Verbose YAML (Google Workflows) | **Python Code** |
| **Debug** | Logs & Prayers | Local Debugger / Breakpoints |

### The "Worker Pool" Advantage
Cloud Run Worker Pools are purpose-built for this.
*   **No HTTP Endpoint**: Reduced attack surface. No load balancers.
*   **Scale to Zero**: (Optional) or Keep Min Instances for instant execution.
*   **Instance Splitting**: Canary releases by percentage.

## 3. Implementation Strategy

### 3.1 The "Juggernaut" Worker
Instead of deploying "Workflows", we deploy an **Application** that executes workflows.

**Container Structure:**
```python
# worker.py
import asyncio
import os
from temporalio.client import Client
from temporalio.worker import Worker
from workflows import IndexingWorkflow
from activities import fetch_connections

async def main():
    client = await Client.connect(
        "namespace.tmprl.cloud:7233",
        api_key=os.environ["TEMPORAL_API_KEY"],
    )
    worker = Worker(
        client,
        task_queue="shadowtag-omega-queue",
        workflows=[IndexingWorkflow],
        activities=[fetch_connections],
    )
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### 3.2 Infrastructure as Code (Terraform)
Deploying the Worker Pool is trivial compared to the old Service/Job dance.

```hcl
resource "google_cloud_run_v2_worker_pool" "temporal_worker" {
  name         = "temporal-worker-omega"
  location     = "us-central1"
  launch_stage = "BETA" # Currently in preview

  scaling {
    scaling_mode       = "AUTOMATIC"
    min_instance_count = 1 # Keep 1 warm for "Sovereign" speed
    max_instance_count = 10
  }

  template {
    containers {
      image = "us-central1-docker.pkg.dev/project/repo/worker:latest"
      env {
        name  = "TEMPORAL_API_KEY"
        value_source {
          secret_key_ref {
            secret  = "temporal-api-key"
            version = "latest"
          }
        }
      }
      resources {
        limits = {
          cpu    = "1"
          memory = "1Gi"
        }
      }
    }
  }
}
```

## 4. Cost vs. Value Analysis

**The Reality Check:**
*   **Old Way**: ~$80-90/mo (Cloud Workflows + Run Jobs + Cold Starts).
*   **New Way**: ~$120-140/mo (Temporal Cloud + 2 Warm Workers).

**The ROI:**
*   **Dev Time**: Saved 2-3 hours/month of YAML debugging.
*   **Velocity**: 75% faster execution.
*   **Confidence**: Local testing means "Green means Green".

**Verdict**: The premium for "Insanely Great" experiences is worth it. This aligns with the "Dark Luxury" philosophy—hidden complexity, seamless execution.

## 5. Migration Plan (Fold In)

1.  **Spike**: Create `apps/shadowtagai/workers/temporal_spike.py`.
2.  **Infrastructure**: Add `google_cloud_run_v2_worker_pool` to `gideon_os/infra/main.tf`.
3.  **Refactor**: Begin migrating `Judge 6` logic from direct Cloud Run calls to Temporal Activities.
