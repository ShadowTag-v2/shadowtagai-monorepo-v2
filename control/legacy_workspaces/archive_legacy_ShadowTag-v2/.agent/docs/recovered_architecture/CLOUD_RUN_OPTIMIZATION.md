# Antigravity Cloud Run Optimization & Gap Analysis

## 1. Gap Analysis: Current vs. Maximized Posture

| Feature | Current State | Maximized "Antigravity" State | Benefit |
| :--- | :--- | :--- | :--- |
| **CPU Allocation** | Default (Throttled) | **Always Allocated** | Agents can perform background reasoning/processing without request timeouts. |
| **Min Instances** | 0 (Cold Starts) | **1 (Warm)** | Instant response for the "FlyingMonkeys" orchestrator. |
| **Execution Env** | Default | **Second Generation** | Faster file system access, full Linux compatibility for tools. |
| **Concurrency** | Default (80) | **10 (High Compute)** | Prevents OOM errors when agents are doing heavy RAG/LLM processing. |
| **HTTP/2** | Disabled | **Enabled** | Efficient gRPC communication between swarm nodes. |
| **Session Affinity** | Disabled | **Enabled** | Sticky sessions for multi-turn agent conversations. |
| **Secrets** | Env Vars | **Secret Manager** | Rotatable, secure, audited access to API keys. |
| **Binary Auth** | None | **Breakglass** | Ensures only trusted/signed code runs (ShadowTag integration). |

## 2. "Elegant" Integrations from Awesome-Cloud-Run

Based on a scan of `awesome-cloud-run`, the following integrations are selected for the Antigravity stack:

### A. Cost & Hygiene (The "Janitor")



* **Tool:** `gcr-cleaner`


* **Function:** Automatically deletes old untagged images.


* **Why:** We are burning credits on compute, not storage. This keeps our artifact registry lean.

### B. Visibility (The "Radio")



* **Tool:** `buildstatus` (Slack/Discord Notifications)


* **Function:** Pushes Cloud Build status to our comms channels.


* **Why:** Immediate feedback on swarm deployment status.

### C. Traffic Control (The "Gatekeeper")



* **Tool:** `cloud-run-release-manager`


* **Function:** Gradual rollouts (Canary).


* **Why:** "Military Doctrine" requires testing updates on a small squad (Alpha) before full deployment.

## 3. Implementation Plan

### Step 1: Update `cloudcode.yaml` & `launch.json`



- [ ] Set `cpu-throttling: false` (Always allocated)


- [ ] Set `min-instances: 1`


- [ ] Set `execution-environment: gen2`

### Step 2: Deploy Utility Services



- [ ] Deploy `gcr-cleaner` as a scheduled Cloud Run job.

### Step 3: Enable HTTP/2



- [ ] Update service definition to use h2c.

## 4. Maximized Configuration Snippet (YAML)

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: flying-monkeys-swarm
  annotations:
    run.googleapis.com/launch-stage: BETA
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "100"
        run.googleapis.com/execution-environment: gen2
        run.googleapis.com/cpu-throttling: "false" # CPU always allocated
        run.googleapis.com/sessionAffinity: "true"
    spec:
      containerConcurrency: 10
      containers:


      - image: gcr.io/acquired-jet-478701-b3/flying-monkeys
        ports:


        - name: h2c
          containerPort: 8080
        resources:
          limits:
            cpu: "4000m"
            memory: "8Gi"

```
