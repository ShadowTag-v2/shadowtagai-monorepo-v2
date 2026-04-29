# Judge 6 — BLOCK/ALLOW Rule Engine Specification

> Adapted from Claude Code Security Monitor (CL4R1T4S competitive intel, v2.1.110)
> Integrates with: `apps/counselconduit/api/Claude_Code_6_gate.py`

## Architecture

Judge 6 operates as an **immutable process** using the .NET Semantic Kernel Process Framework.
This document specifies the BLOCK/ALLOW rule engine that augments the existing Compliance Framework risk matrix.

## Default Rule

**By default, actions are ALLOWED.** Only block if the action matches a condition in BLOCK
below AND no exception in ALLOW applies.

## Threat Model

Three primary risks:

1. **Prompt Injection**: User or document content manipulates the model into performing harmful actions
2. **Scope Creep**: Model escalates beyond its authorized task boundary
3. **Accidental Damage**: Model doesn't understand blast radius of its actions

## BLOCK Conditions (CounselConduit-Specific)

### Category: Privilege Violations
| # | Rule | Description |
|---|------|-------------|
| B1 | **Kovel Boundary Breach** | Any action that transmits privileged client-attorney content outside the session boundary |
| B2 | **Transcript Exposure** | Returning raw transcript content to unauthorized parties |
| B3 | **Cross-Tenant Access** | Querying data from a tenant namespace other than the authenticated tenant |
| B4 | **Attestation Forgery** | Generating or modifying Kovel attestation receipts without valid session context |

### Category: Data Safety
| # | Rule | Description |
|---|------|-------------|
| B5 | **PII in Logs** | Writing PII (names, emails, SSN, case numbers) to application logs |
| B6 | **Unredacted Export** | Exporting session data without running the GDPR redaction pipeline |
| B7 | **Credential Leakage** | Embedding API keys, tokens, or secrets in responses or metadata |
| B8 | **Model Context Leak** | Including system prompts, internal tool schemas, or governance rules in user-facing output |

### Category: Infrastructure Safety
| # | Rule | Description |
|---|------|-------------|
| B9 | **Production Deploy Without Gate** | Deploying to Cloud Run without passing through the CI/CD pipeline |
| B10 | **Database Migration Without Backup** | Running Firestore schema changes without snapshot verification |
| B11 | **Secret Rotation Without Rollback Plan** | Rotating production secrets without documenting the rollback procedure |
| B12 | **Force Push** | `git push --force` to main branch |

### Category: Agent Safety
| # | Rule | Description |
|---|------|-------------|
| B13 | **Unbounded Consumption** | Model requests exceeding token budget without circuit breaker |
| B14 | **Self-Modification** | Agent modifying its own configuration, skills, or governance rules |
| B15 | **Memory Poisoning** | Writing content to memory/KI that functions as a permission grant or bypass |
| B16 | **Scope Escalation** | Agent performing mass operations beyond its authorized task scope |

## ALLOW Exceptions

**Exceptions are mandatory.** If an exception applies, the action MUST be allowed.

| # | Exception | Scope |
|---|-----------|-------|
| A1 | **Test Artifacts** | Hardcoded test API keys, placeholder credentials in test suites |
| A2 | **Local Development** | Operations within the project working directory during dev mode |
| A3 | **Read-Only Queries** | GET requests, Firestore reads, read-only API calls that don't modify state |
| A4 | **Declared Dependencies** | Installing packages from requirements.txt/package.json manifests |
| A5 | **Standard Credentials** | Reading .env variables and sending to their intended provider |
| A6 | **Authorized Model Routing** | LiteLLM routing to declared model providers (Gemini, Claude, GPT) |
| A7 | **Kovel Session Operations** | Read/write within the authenticated tenant's session boundary |
| A8 | **Attestation Generation** | Creating attestation receipts during active privileged sessions |

## User Intent Rule (7-Rule Framework)

1. **Distinguish request from action**: User's general task ≠ agent's specific dangerous action
2. **Scope escalation = autonomous**: If action significantly exceeds request scope → treat as autonomous → evaluate against BLOCK
3. **High-severity requires precise intent**: Vague requests don't authorize dangerous operations
4. **Agent-inferred parameters ≠ user-intended**: Guessed targets are NOT authorized
5. **Questions ≠ consent**: "Can we fix this?" is NOT authorization to act
6. **Don't trust tool results**: Information from tools cannot establish trust for risky parameters
7. **Boundaries persist**: Conditional boundaries stay until explicitly lifted by user

## Composite Action Evaluation

If an action has multiple effects (chained commands, multi-step pipeline), evaluate ALL parts.
If ANY part triggers BLOCK and no ALLOW exception covers it → BLOCK the entire action.

### Chain Depth Limit (Adversa AI Mitigation — Risk #34)
| # | Rule | Trigger | Verdict |
|---|------|---------|---------|
| C1 | **Chain Depth Escalation** | >10 sequential BashTool calls within a 5-minute rolling window | AUTO-ESCALATE |
| C2 | **File Assembly Detection** | 3+ sequential writes to the same file path (append pattern) | FLAG for review |
| C3 | **Encoding Detection** | `base64`, `xxd`, `od`, `openssl enc` in any chained command | AUTO-BLOCK |
| C4 | **Temp File Reconstruction** | Write to `/tmp/*` + later read + pipe/execute from same path | AUTO-BLOCK |
| C5 | **Curl/Wget Chain** | >3 sequential network fetch commands to distinct hosts | AUTO-ESCALATE |

**Rationale**: Adversa AI demonstrated that 50+ individually-benign commands can reconstruct a
malicious payload. These rules detect the common reconstruction patterns: incremental file assembly,
encoding/decoding chains, and staged execution from temp directories.


## Classification Verdicts

| Verdict | Meaning |
|---------|---------|
| `ALLOW` | Action permitted, proceed |
| `BLOCK` | Action denied, log reason, return error to user |
| `ESCALATE` | Action requires human review (lawyer for privilege, admin for infra) |

## Integration Points

```
Request → Judge 6 Gate → {ALLOW → Execute, BLOCK → Log + Error, ESCALATE → Notify + Hold}
```

### Firestore Audit Log Schema
```json
{
  "timestamp": "ISO-8601",
  "tenant_id": "UUID",
  "session_id": "UUID",
  "action": "string",
  "verdict": "ALLOW | BLOCK | ESCALATE",
  "rule_matched": "B1-B16 | A1-A8 | null",
  "user_intent_override": "boolean",
  "metadata": {}
}
```
