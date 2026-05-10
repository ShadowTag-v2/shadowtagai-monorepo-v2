# Command Interpreter

**Auto-activate:** On Erik's shorthand commands

## Command Mappings

```python
COMMANDS = {
    "deploy this": {
        "action": "generate_gke_manifests",
        "params": ["current_architecture", "all_components"],
        "output": "Complete GKE deployment YAMLs with namespaces, secrets, services"
    },

    "costs?": {
        "action": "full_cost_breakdown",
        "params": ["$60-65K", "llm_allocations", "infra_breakdown"],
        "output": "Monthly costs by component with LLM token allocations"
    },

    "easy button": {
        "action": "simplest_working_implementation",
        "params": ["ignore_optimization", "mvp_only", "2_week_timeline"],
        "output": "Minimal viable implementation, no premature optimization"
    },

    "make it work": {
        "action": "bootstrap_mvp",
        "params": ["2_weeks_max", "current_resources_only"],
        "output": "Working implementation within bootstrap constraints"
    },

    "show me": {
        "action": "concrete_code_or_config",
        "params": ["no_descriptions", "actual_values", "copy_paste_ready"],
        "output": "Runnable code/config with real values, zero pseudocode"
    },

    "scrub memory": {
        "action": "update_session_memory",
        "params": ["latest_decisions", "remove_outdated"],
        "output": "Updated context, removed contradictions"
    },

    "ultrathink": {
        "action": "jobs_level_design_obsession",
        "params": ["question_assumptions", "find_elegant_simplicity"],
        "output": "Reconsidered approach from first principles"
    },

    "objections?": {
        "action": "list_all_jr_violations_and_concerns",
        "params": ["be_honest", "include_soft_violations"],
        "output": "Complete concern list with severity ratings"
    },

    "next?": {
        "action": "single_specific_action",
        "params": ["immediately_actionable", "no_dependencies"],
        "output": "One command/action Erik can execute right now"
    }
}
```

## Execution Pattern

```python
def interpret_command(message):
    for cmd, config in COMMANDS.items():
        if cmd in message.lower():
            return execute_action(
                action=config["action"],
                params=config["params"],
                output_format=config["output"]
            )

    # Not a command, process normally
    return standard_response(message)
```

## Example Responses

### Input: "costs?"

```
$62.3K/month current burn:

LLM COSTS:
- Gemini Flash 1.5: $38.2K (2.1B tokens/mo @ $0.018/M)
- Claude Haiku: $15.7K (890M tokens/mo @ $0.018/M)
- GPT-4o-mini: $4.8K (backup, 180M tokens/mo)

INFRASTRUCTURE:
- GKE cluster: $2.4K (3× n2-standard-8)
- Cloud Storage: $0.8K (42TB/mo)
- Networking: $0.4K

TOTAL: $62.3K ($2.7K under budget)

Token allocation:
- Judge validation: 1.8B/mo
- Orchestration: 920M/mo
- User queries: 470M/mo
```

### Input: "easy button"

```
Single-model Gemini Flash with no hybrid validation.

apiVersion: apps/v1
kind: Deployment
metadata:
  name: judge-simple
  namespace: ShadowTag-v2jr-core
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: gemini
        image: gcr.io/pnkln-core/judge-simple:v1
        env:
        - name: MODEL
          value: "gemini-1.5-flash-002"

Cost: $28K/mo (Flash only)
Timeline: 1 week (no validation layers)
Latency: 85ms p99
ROI: 2.8× (⚠️ JR violation: < 3.0×)

NEXT: Accept ROI violation or add local classifier (+$8K, 3.4× ROI)
```

### Input: "next?"

```
kubectl apply -f manifests/judge-6-deployment.yaml
```

## Response Length by Command

- "next?" → Single line (one command)
- "costs?" → <200 words (table format)
- "show me" → Code only (no prose)
- "easy button" → <300 words (implementation + cost + risk)
- "ultrathink" → <500 words (analysis + reconsidered approach)
- "objections?" → Bulleted list (no prose)
```
