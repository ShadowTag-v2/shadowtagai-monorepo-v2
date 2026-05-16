# ActiveShield MCF - Integration Guide

## Overview

This guide covers how to integrate the ActiveShield MCF into your applications, including:


- Python SDK integration

- REST API integration

- GPT Store / ChatGPT plugin integration

- Webhook configuration

- CI/CD pipeline integration

## Python SDK Integration

### Installation

```bash
pip install activeshield-mcf

```

### Basic Usage

```python
from activeshield import ComplianceClient, AssessmentInput, RegulationId

# Initialize client

client = ComplianceClient(
    api_key="your_api_key",
    base_url="https://api.activeshield.ai/v1"
)

# Run assessment

result = await client.assess(
    AssessmentInput(
        content_type="ai_chatbot",
        modules=[RegulationId.EU_AI_ACT, RegulationId.GDPR],
        is_ai_generated=True
    )
)

print(f"Compliance Score: {result.overall_score:.0%}")

```

### Validate LLM Output

```python

# Wrap your LLM calls with compliance validation

async def compliant_llm_call(prompt: str) -> str:
    # Call your LLM
    response = await your_llm.generate(prompt)

    # Validate response
    validation = await client.validate(
        response_text=response,
        modules=[RegulationId.GDPR, RegulationId.EU_AI_ACT]
    )

    if not validation.is_compliant:
        # Handle violations
        for v in validation.violations:
            if v.severity == "critical":
                raise ComplianceViolationError(v.description)

        # Use remediated version if available
        if validation.remediated_text:
            return validation.remediated_text

    return response

```

## REST API Integration

### cURL Example

```bash

# Generate blueprint

curl -X POST https://api.activeshield.ai/v1/compliance/blueprint \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "jurisdictions": ["eu"],
    "regulations": ["eu_ai_act", "gdpr"]
  }'

# Run assessment

curl -X POST https://api.activeshield.ai/v1/compliance/assess \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "ai_chatbot",
    "is_ai_generated": true,
    "modules": ["eu_ai_act"]
  }'

```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const client = axios.create({
  baseURL: 'https://api.activeshield.ai/v1/compliance',
  headers: {
    'X-API-Key': process.env.ACTIVESHIELD_API_KEY,
    'Content-Type': 'application/json'
  }
});

// Validate content
async function validateContent(text, modules) {
  const response = await client.post('/validate', {
    response_text: text,
    modules: modules
  });

  return response.data;
}

```

## GPT Store / ChatGPT Plugin Integration

### Plugin Manifest

```json
{
  "schema_version": "v1",
  "name_for_human": "ActiveShield Compliance",
  "name_for_model": "activeshield_compliance",
  "description_for_human": "Check AI responses for regulatory compliance",
  "description_for_model": "Validates AI-generated content against regulations like EU AI Act, GDPR, HIPAA. Use after generating responses to ensure compliance.",
  "auth": {
    "type": "service_http",
    "authorization_type": "bearer"
  },
  "api": {
    "type": "openapi",
    "url": "https://api.activeshield.ai/v1/openapi.json"
  }
}

```

### Post-Generation Validation Flow

```

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User Prompt   │────▶│   ChatGPT       │────▶│  ActiveShield   │
└─────────────────┘     │   Response      │     │  Validation     │
                        └─────────────────┘     └─────────────────┘
                                                        │
                        ┌─────────────────┐             │
                        │  Modified       │◀────────────┘
                        │  Response       │  (if violations found)
                        └─────────────────┘

```

### Example GPT Action

```yaml
openapi: 3.0.0
info:
  title: ActiveShield Compliance API
  version: 1.0.0

paths:
  /validate:
    post:
      operationId: validateContent
      summary: Validate content for compliance
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                response_text:
                  type: string
                  description: The AI response to validate
                modules:
                  type: array
                  items:
                    type: string
                  default: ["eu_ai_act", "gdpr"]
      responses:
        '200':
          description: Validation result

```

## Webhook Configuration

### Setup Webhooks

```python

# Configure webhook for assessment events

webhook_config = {
    "url": "https://your-app.com/webhooks/compliance",
    "events": ["assessment.completed", "violation.detected"],
    "secret": "your_webhook_secret"
}

await client.configure_webhook(webhook_config)

```

### Handle Webhook Events

```python
from fastapi import FastAPI, Request
import hmac
import hashlib

app = FastAPI()

@app.post("/webhooks/compliance")
async def handle_compliance_webhook(request: Request):
    # Verify signature
    signature = request.headers.get("X-ActiveShield-Signature")
    body = await request.body()

    expected = hmac.new(
        webhook_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401)

    event = await request.json()

    if event["type"] == "violation.detected":
        # Handle violation
        alert_team(event["data"])

    return {"status": "received"}

```

## CI/CD Pipeline Integration

### GitHub Actions

```yaml
name: Compliance Check

on:
  pull_request:
    branches: [main]

jobs:
  compliance:
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v3


      - name: Run Compliance Assessment
        uses: activeshield/compliance-action@v1
        with:
          api_key: ${{ secrets.ACTIVESHIELD_API_KEY }}
          modules: eu_ai_act,gdpr
          fail_on_violations: true


      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: compliance-report
          path: compliance-report.json

```

### GitLab CI

```yaml
compliance_check:
  stage: test
  image: python:3.11
  script:

    - pip install activeshield-mcf

    - activeshield assess --modules eu_ai_act,gdpr --output json > report.json
  artifacts:
    reports:
      compliance: report.json
  only:

    - merge_requests

```

## Environment Variables

```bash

# Required

ACTIVESHIELD_API_KEY=your_api_key

# Optional

ACTIVESHIELD_API_URL=https://api.activeshield.ai/v1
ACTIVESHIELD_DEFAULT_MODULES=eu_ai_act,gdpr
ACTIVESHIELD_FAIL_ON_CRITICAL=true
ACTIVESHIELD_WEBHOOK_SECRET=your_secret

```

## Rate Limits

| Tier | Requests/min | Assessments/day | Batch Size |
|------|--------------|-----------------|------------|
| Free | 10 | 100 | 10 |
| Pro | 100 | 1,000 | 100 |
| Enterprise | 1,000 | Unlimited | 1,000 |

## Error Handling

```python
from activeshield.exceptions import (
    ComplianceError,
    RateLimitError,
    AuthenticationError,
    ValidationError
)

try:
    result = await client.assess(input_data)
except RateLimitError as e:
    # Wait and retry
    await asyncio.sleep(e.retry_after)
    result = await client.assess(input_data)
except AuthenticationError:
    # Check API key
    raise
except ValidationError as e:
    # Invalid input
    logger.error(f"Invalid input: {e.details}")
except ComplianceError as e:
    # General error
    logger.error(f"Compliance check failed: {e}")

```

## Support


- Documentation: https://docs.activeshield.ai

- API Status: https://status.activeshield.ai

- Support Email: support@activeshield.ai
