# OpenTelemetry Tracing — CounselConduit Dispatch Pipeline

## Architecture
```
Client Request → FastAPI Middleware (root span)
  └── dispatch_handler (child span)
      ├── firm_policy_lookup (child span)
      ├── model_routing (child span)
      ├── token_budget_check (child span)
      ├── llm_call (child span, includes model/provider attrs)
      │   ├── prompt_preparation
      │   └── api_call (HTTP client span)
      ├── kovel_attestation (child span)
      └── response_assembly (child span)
```

## Implementation

### Dependencies
```
opentelemetry-api>=1.29
opentelemetry-sdk>=1.29
opentelemetry-instrumentation-fastapi>=0.50b0
opentelemetry-exporter-gcp-trace>=1.9
```

### Initialization (main.py)
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(CloudTraceSpanExporter()))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("counselconduit")
```

### Dispatch Pipeline Instrumentation
```python
@tracer.start_as_current_span("dispatch")
async def handle_dispatch(request: DispatchRequest):
    with tracer.start_as_current_span("firm_policy_lookup") as span:
        span.set_attribute("firm.id", request.firm_id)
        policy = await get_firm_policy(request.firm_id)

    with tracer.start_as_current_span("model_routing") as span:
        span.set_attribute("model.requested", request.model)
        model, provider = route_model(request.model, policy)
        span.set_attribute("model.routed", model)
        span.set_attribute("provider.name", provider)

    with tracer.start_as_current_span("llm_call") as span:
        span.set_attribute("llm.model", model)
        span.set_attribute("llm.provider", provider)
        span.set_attribute("llm.token_count.prompt", len(request.prompt))
        response = await call_llm(model, provider, request.prompt)
        span.set_attribute("llm.token_count.completion", response.usage.completion)
```

### Key Attributes
| Attribute | Type | Description |
|-----------|------|-------------|
| `firm.id` | string | Tenant identifier |
| `model.requested` | string | Client-requested model |
| `model.routed` | string | Actually used model |
| `provider.name` | string | LLM provider |
| `llm.token_count.prompt` | int | Input tokens |
| `llm.token_count.completion` | int | Output tokens |
| `dispatch.tier` | string | primary/fallback |
| `circuit_breaker.state` | string | open/closed/half-open |

## Viewing Traces
- GCP Console → Trace → Trace list
- Filter: `+resource.type:cloud_run_revision +resource.labels.service_name:counselconduit`
- Cost: ~$0.20 per million spans (Cloud Trace pricing)
