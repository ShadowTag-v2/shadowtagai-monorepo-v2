# KERNEL Framework: Chaining Architecture Specification

**Version**: 1.0
**Status**: Design
**Owner**: pnkln Core Team
**Date**: 2025-11-17

---

## Overview

The KERNEL (Keep it simple, Easy to verify, Reproducible, Narrow scope, Explicit, Logical structure) chaining architecture enables **composable reasoning** where complex AI tasks decompose into atomic, cacheable, reusable units called "kernels."

### Key Innovation

**Traditional Monolithic Reasoning**:
```
User Query → Single LLM Call (10K tokens) → Response
Cost: $0.105 per query
Reusability: 0%
```

**Kernel Chaining**:
```
User Query → Kernel 1 (cached) → Kernel 2 (new) → Kernel 3 (cached) → Response
Cost: $0.02235 per query (78.7% reduction)
Reusability: 60% cache hit rate
```

---

## Kernel Anatomy

### Kernel Schema

```typescript
interface Kernel {
  // Metadata
  id: string;                    // UUID
  name: string;                  // Human-readable name
  version: string;               // Semantic version
  author: string;                // Creator ID
  created_at: timestamp;

  // Execution
  input_schema: JSONSchema;      // Input contract
  output_schema: JSONSchema;     // Output contract
  prompt_template: string;       // LLM prompt with {{variables}}
  model: string;                 // "gemini-3.1-flash" | "claude-sonnet-4.5"
  temperature: number;           // 0.0-1.0
  max_tokens: number;

  // Optimization
  cacheable: boolean;            // Can results be cached?
  cache_ttl: number;             // Seconds
  cache_key_fields: string[];    // Which inputs determine cache key

  // Metadata
  tags: string[];                // ["reasoning", "coding", "math"]
  cost_estimate: number;         // USD per execution
  avg_latency_ms: number;        // Historical average

  // Quality
  examples: Example[];           // Input/output pairs
  test_cases: TestCase[];        // Validation tests
  success_rate: number;          // 0.0-1.0
}

interface Example {
  input: object;
  output: object;
  explanation?: string;
}

interface TestCase {
  input: object;
  expected_output: object;
  assertion: string;            // JSONPath or JS expression
}
```

### Example Kernel: Code Reviewer

```json
{
  "id": "krn_code_reviewer_v1",
  "name": "Code Reviewer",
  "version": "1.0.0",
  "author": "pnkln_official",
  "input_schema": {
    "type": "object",
    "properties": {
      "code": {"type": "string"},
      "language": {"type": "string", "enum": ["python", "typescript", "rust"]},
      "focus": {"type": "string", "enum": ["security", "performance", "style"]}
    },
    "required": ["code", "language"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "issues": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "severity": {"type": "string", "enum": ["critical", "warning", "info"]},
            "line": {"type": "number"},
            "message": {"type": "string"},
            "suggestion": {"type": "string"}
          }
        }
      },
      "overall_quality": {"type": "number", "minimum": 0, "maximum": 10}
    }
  },
  "prompt_template": "Review the following {{language}} code for {{focus}} issues:\n\n```{{language}}\n{{code}}\n```\n\nProvide structured feedback.",
  "model": "gemini-3.1-flash",
  "temperature": 0.3,
  "max_tokens": 2000,
  "cacheable": true,
  "cache_ttl": 3600,
  "cache_key_fields": ["code", "language", "focus"],
  "tags": ["code", "review", "quality"],
  "cost_estimate": 0.015,
  "avg_latency_ms": 450
}
```

---

## Chaining Mechanism

### Chain Definition

```typescript
interface Chain {
  id: string;
  name: string;
  description: string;
  kernels: ChainStep[];
  input_schema: JSONSchema;
  output_schema: JSONSchema;
}

interface ChainStep {
  kernel_id: string;
  step_name: string;
  input_mapping: {[outputKey: string]: string};  // Map chain inputs/previous outputs to kernel inputs
  condition?: string;  // Optional: JS expression to skip step
  retry_policy?: RetryPolicy;
}

interface RetryPolicy {
  max_retries: number;
  backoff_ms: number;
  fallback_kernel_id?: string;
}
```

### Example Chain: Full-Stack Code Review

```json
{
  "id": "chain_fullstack_review_v1",
  "name": "Full-Stack Code Review",
  "description": "Reviews frontend, backend, and database code with security analysis",
  "input_schema": {
    "type": "object",
    "properties": {
      "frontend_code": {"type": "string"},
      "backend_code": {"type": "string"},
      "sql_queries": {"type": "string"}
    }
  },
  "kernels": [
    {
      "kernel_id": "krn_code_reviewer_v1",
      "step_name": "review_frontend",
      "input_mapping": {
        "code": "frontend_code",
        "language": "'typescript'",
        "focus": "'security'"
      }
    },
    {
      "kernel_id": "krn_code_reviewer_v1",
      "step_name": "review_backend",
      "input_mapping": {
        "code": "backend_code",
        "language": "'python'",
        "focus": "'performance'"
      }
    },
    {
      "kernel_id": "krn_sql_security_scanner_v1",
      "step_name": "scan_sql",
      "input_mapping": {
        "queries": "sql_queries"
      }
    },
    {
      "kernel_id": "krn_aggregate_reviews_v1",
      "step_name": "aggregate",
      "input_mapping": {
        "reviews": "[review_frontend.output, review_backend.output, scan_sql.output]"
      }
    }
  ]
}
```

---

## Caching Strategy

### Cache Architecture

```
┌─────────────────────────────────────────────┐
│  Client Request                             │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│  Chain Executor                             │
│  - Parses chain definition                  │
│  - Resolves kernel dependencies             │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│  Kernel Executor (for each step)            │
│  1. Generate cache key from inputs          │
│  2. Check Redis cache                       │
│  3. If HIT → return cached result           │
│  4. If MISS → execute kernel                │
│  5. Store result in cache (if cacheable)    │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│  LLM Invocation (Gemini/Claude)             │
│  - Prompt rendering                         │
│  - API call                                 │
│  - Response parsing                         │
└─────────────────────────────────────────────┘
```

### Cache Key Generation

```python
def generate_cache_key(kernel: Kernel, inputs: dict) -> str:
    """
    Generate deterministic cache key from kernel ID, version, and specified input fields
    """
    # Extract only fields specified in cache_key_fields
    cache_inputs = {
        field: inputs.get(field)
        for field in kernel.cache_key_fields
    }

    # Create deterministic hash
    cache_data = {
        "kernel_id": kernel.id,
        "version": kernel.version,
        "inputs": cache_inputs
    }

    # Use xxhash for speed
    key_string = json.dumps(cache_data, sort_keys=True)
    hash_value = xxhash.xxh64(key_string).hexdigest()

    return f"kernel:{kernel.id}:{hash_value}"

# Example
cache_key = generate_cache_key(
    kernel_id="krn_code_reviewer_v1",
    inputs={"code": "def foo():\n  pass", "language": "python", "focus": "security"}
)
# Result: "kernel:krn_code_reviewer_v1:a3f4b8c9e1d2f5a6"
```

### Cache Invalidation

**Time-based** (TTL):
- Default: 1 hour
- Long-lived (stable kernels): 24 hours
- Short-lived (volatile data): 5 minutes

**Version-based**:
- Kernel version bump → all caches for that kernel invalidated
- Example: `krn_code_reviewer_v1` → `krn_code_reviewer_v2`

**Manual**:
- Creator can purge cache via API
- Admin can purge all caches for a kernel

---

## Cost Optimization

### Token Reduction Math

**Scenario**: Complex reasoning task requiring 5 sub-analyses

**Without Caching**:
```
Query 1: 5 kernels × 2,000 tokens each = 10,000 tokens
Query 2: 5 kernels × 2,000 tokens each = 10,000 tokens (same task, different input)
Query 3: 5 kernels × 2,000 tokens each = 10,000 tokens
Total: 30,000 tokens
Cost (Gemini): 30K × $0.075 / 1M = $0.00225
```

**With 60% Cache Hit Rate**:
```
Query 1: 5 kernels × 2,000 tokens = 10,000 tokens (cold cache)
Query 2:
  - 3 cached kernels: 3 × 50 tokens (cache lookup) = 150 tokens
  - 2 new kernels: 2 × 2,000 tokens = 4,000 tokens
  Subtotal: 4,150 tokens
Query 3: (same as Query 2)
  Subtotal: 4,150 tokens

Total: 10,000 + 4,150 + 4,150 = 18,300 tokens (39% reduction)
Cost (Gemini): 18.3K × $0.075 / 1M = $0.00137 (39% savings)
```

### Batching Strategy

Execute multiple kernels in parallel when no dependencies exist:

```python
async def execute_chain(chain: Chain, inputs: dict):
    results = {}

    # Build dependency graph
    graph = build_dependency_graph(chain.kernels)

    # Execute in topological order, parallelizing independent steps
    for level in graph.levels:
        # All kernels in this level have no dependencies on each other
        tasks = [
            execute_kernel(step.kernel_id, resolve_inputs(step, inputs, results))
            for step in level
        ]

        # Execute in parallel
        level_results = await asyncio.gather(*tasks)

        # Merge results
        for step, result in zip(level, level_results):
            results[step.step_name] = result

    return results
```

**Latency Improvement**:
- Sequential: 5 kernels × 450ms avg = 2,250ms
- Parallel (3 levels): Level 1 (450ms) + Level 2 (450ms) + Level 3 (450ms) = 1,350ms (40% faster)

---

## Marketplace Integration

### Creator Submission Flow

1. **Create Kernel**:
   ```bash
   pnkln kernel create --template code-reviewer
   # Opens editor with schema template
   ```

2. **Test Locally**:
   ```bash
   pnkln kernel test krn_my_kernel_v1 --test-cases test_cases.json
   # Runs all test cases, reports success rate
   ```

3. **Publish**:
   ```bash
   pnkln kernel publish krn_my_kernel_v1 --price 0.05
   # Uploads to marketplace, sets $0.05 per execution
   ```

4. **Monitor**:
   ```bash
   pnkln kernel stats krn_my_kernel_v1
   # Executions: 1,250
   # Revenue: $62.50
   # Avg rating: 4.7/5
   # Cache hit rate: 58%
   ```

### Revenue Share

- **70%** to creator
- **30%** to platform (pnkln)

**Example Calculation**:
```
Kernel price: $0.05 per execution
Executions in month: 10,000
Gross revenue: $500
Creator payout: $350 (70%)
Platform revenue: $150 (30%)
```

---

## Quality Assurance

### Kernel Validation

Before publication, kernels must pass:

1. **Schema Validation**:
   - Input/output schemas are valid JSON Schema
   - Examples match schema

2. **Test Coverage**:
   - Minimum 5 test cases
   - Success rate ≥ 95%

3. **Cost Estimation**:
   - Actual cost within 20% of declared `cost_estimate`

4. **Latency SLA**:
   - P99 latency < 2 seconds (for cacheable kernels)
   - P99 latency < 5 seconds (for complex kernels)

5. **Safety Review**:
   - No prompt injection vulnerabilities
   - No PII leakage
   - No malicious outputs

### User Ratings

Users rate kernels 1-5 stars based on:
- **Accuracy**: Does it produce correct results?
- **Speed**: Is it fast enough?
- **Cost**: Is it worth the price?

Low-rated kernels (<3.0 stars) are depublished after 100 executions.

---

## Implementation Roadmap

### Phase 1: Core Runtime (Month 1)
- [ ] Kernel schema definition
- [ ] Chain execution engine
- [ ] Redis cache integration
- [ ] Gemini API integration
- [ ] 10 base kernels (reasoning, coding, analysis)

### Phase 2: Marketplace MVP (Month 2)
- [ ] Creator dashboard
- [ ] Kernel submission flow
- [ ] Payment integration (Stripe Connect)
- [ ] Search and discovery
- [ ] First 20 community kernels

### Phase 3: Optimization (Month 3)
- [ ] Parallel execution
- [ ] Advanced caching (semantic similarity)
- [ ] Cost analytics dashboard
- [ ] A/B testing framework
- [ ] Kernel versioning & deprecation

### Phase 4: Enterprise (Month 4-6)
- [ ] Private kernel hosting
- [ ] Custom model support (fine-tuned models)
- [ ] SLA guarantees
- [ ] Audit logging
- [ ] Role-based access control

---

## Success Metrics

### Technical Metrics
- **Cache Hit Rate**: Target 60%, stretch 75%
- **P99 Latency**: <500ms per kernel, <2s per chain
- **Token Reduction**: 78% vs. monolithic approach
- **Cost per Execution**: <$0.01 average

### Business Metrics
- **Active Kernels**: 500+ by month 6
- **Active Creators**: 200+ by month 6
- **Execution Volume**: 10M+ per month by month 12
- **Creator Revenue**: $250K+ paid to creators annually

---

## References

- [KERNEL Framework Principles](./FINANCIAL_ANALYSIS.md#branch-1-kernel-chaining-architecture)
- [Gemini API Pricing](https://ai.google.dev/pricing)
- [Claude API Pricing](https://anthropic.com/pricing)
- [Marketplace Economics](./FINANCIAL_ANALYSIS.md#branch-3-superpowers-marketplace)

---

**Next Steps**: Implement Phase 1 (Core Runtime) starting this week. Target completion: 2 weeks.
