# Antigravity Kill Chain Protocol (AKCP)

## Mission

To provide an immediate, unconditional termination capability ("Rkill") for all agentic operations (https://github.com/karpathy/autoresearchs, Genkit Swarms) across both local and cloud environments. This protocol is the "Break Glass" mechanism to prevent runaway costs, security breaches, or operational hazards.

## Triggers (Activation Factors)

The Kill Chain is activated automatically or manually upon **ANY** of the following conditions:

### 1. Financial & Resource Triggers (The "Wallet Guard")

- **Budget Velocity:** Spend rate exceeds **$5.00/minute** (configurable).

- **Token Spiral:** Single agent consumes > 1M tokens in < 5 minutes (indicating infinite loop).

- **Cloud Run Scaling:** Instance count exceeds **50** without explicit override.

### 2. Security & Governance Triggers (Judge 6)

- **Unauthorized Tool Access:** Agent attempts to use `rm -rf`, `sudo`, `chmod`, or access `/etc/shadow`.

- **Data Exfiltration:** Agent attempts to send data to non-whitelisted domains (i.e., not `googleapis.com`, `github.com`).

- **Prompt Injection:** Judge 6 detects a "jailbreak" pattern in agent inputs/outputs.

- **IAM Escalation:** Agent attempts to modify its own IAM permissions.

### 3. Operational Triggers (The "Sanity Check")

- **Stalled State:** Agent unresponsive for > 300 seconds.

- **Error Loop:** Agent retries the same failed step > 5 times.

- **Hallucination Spiral:** Output entropy drops below threshold (repetitive text generation).

### 4. Manual Trigger (The "Big Red Button")

- **User Command:** Execution of `/kill`, `!nuke`, or running the `rkill_swarm.sh` script.

## The "Rkill" Mechanism (Execution)

When triggered, the Kill Chain executes the following **simultaneously**:

### Local Environment (Mac)

1. **Process Termination:** `SIGKILL` sent to all `python`, `node`, and `go` processes associated with `https://github.com/karpathy/autoresearchs` or `genkit`.

2. **Container Purge:** `docker kill $(docker ps -q)` followed by `docker system prune -f`.

3. **Network Sever:** Blocks all outgoing traffic from agent ports (e.g., 8600).

### Cloud Environment (Google Cloud)

1. **Cloud Run Freeze:** Executes `gcloud run services update [SERVICE] --min-instances=0 --max-instances=0` (Scales to zero immediately).

2. **Pub/Sub Purge:** Purges all pending messages in the task queues to prevent restart.

3. **IAM Revocation (Extreme):** Temporarily disables the Service Account used by the swarm.

## Reformation (Post-Kill)

After a Kill Chain activation:

1. **Forensics:** Logs are preserved in BigQuery (`shadowtag_logs`) for analysis.

2. **Snapshot:** The state of the "Brain" (memory) is frozen for debugging.

3. **Reform:** The swarm can only be restarted manually after the trigger condition is resolved.

## Sandbox Architecture (Prevention)

To minimize the need for the Kill Chain, all agents operate within:

- **GVisor (Cloud):** Kernel-level isolation on Cloud Run/GKE.

- **Docker (Local):** No host filesystem access; only mounted `/workspace` directories.

- **Network Allowlist:** Only `googleapis.com` and specific APIs are accessible.
