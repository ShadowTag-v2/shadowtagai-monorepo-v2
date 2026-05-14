# ActiveShield MCF - API Reference

## Base URL

```

https://api.activeshield.ai/v1/compliance

```

## Authentication

All endpoints require an API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your_api_key" https://api.activeshield.ai/v1/compliance/modules

```

---

## Endpoints

### POST /blueprint

Generate a compliance blueprint based on selected regulations.

**Request Body:**

```json
{
  "jurisdictions": ["eu", "us"],
  "regulations": ["eu_ai_act", "gdpr", "hipaa"],
  "organization_type": "enterprise",
  "ai_system_type": "chatbot",
  "handles_minors": false,
  "handles_health_data": true
}

```

**Response:**

```json
{
  "blueprint_id": "uuid",
  "created_at": "2024-01-15T10:30:00Z",
  "selected_modules": [
    {
      "id": "eu_ai_act",
      "name": "EU Artificial Intelligence Act",
      "short_name": "EU AI Act",
      "version": "2024.1689",
      "jurisdiction": "eu",
      "pricing_addon_usd": 75.0
    }
  ],
  "total_controls": 42,
  "estimated_monthly_cost_usd": 349.0,
  "api_endpoints": {
    "/api/v1/compliance/assess": "Run compliance assessment"
  },
  "sdk_config": {
    "enabled_modules": ["eu_ai_act", "gdpr", "hipaa"],
    "api_base_url": "https://api.activeshield.ai/v1"
  }
}

```

---

### POST /assess

Run a comprehensive compliance assessment.

**Request Body:**

```json
{
  "content_type": "ai_chatbot",
  "content_id": "chat-123",
  "content": "Optional content to assess",
  "metadata": {
    "ai_disclosure": true,
    "lawful_basis": "consent"
  },
  "is_ai_generated": true,
  "user_age": 25,
  "contains_pii": true,
  "contains_phi": false,
  "is_high_risk_decision": false,
  "modules": ["eu_ai_act", "gdpr"]
}

```

**Response:**

```json
{
  "assessment_id": "uuid",
  "timestamp": "2024-01-15T10:30:00Z",
  "overall_status": "partial",
  "overall_score": 0.85,
  "modules_assessed": [
    {
      "module_id": "eu_ai_act",
      "module_name": "EU AI Act",
      "status": "compliant",
      "compliance_score": 0.92,
      "controls_assessed": 12,
      "controls_compliant": 11,
      "controls_non_compliant": 0,
      "controls_partial": 1,
      "control_results": [],
      "risk_tier": "limited",
      "recommendations": [],
      "requires_human_review": false
    }
  ],
  "total_controls": 24,
  "total_compliant": 20,
  "total_non_compliant": 2,
  "critical_findings": [],
  "recommendations": ["Complete documentation for partial controls"],
  "requires_human_review": false,
  "audit_hash": "sha256:abc123...",
  "transparency_notice": "This content was assessed using AI compliance tools."
}

```

---

### GET /modules

List all available compliance modules.

**Query Parameters:**


- `jurisdiction` (optional): Filter by jurisdiction (us, eu, uk, apac, global)

**Response:**

```json
{
  "modules": [
    {
      "id": "eu_ai_act",
      "name": "EU Artificial Intelligence Act",
      "short_name": "EU AI Act",
      "version": "2024.1689",
      "jurisdiction": "eu",
      "description": "...",
      "effective_date": "2024-08-01",
      "pricing_addon_usd": 75.0
    }
  ],
  "total_count": 8
}

```

---

### GET /modules/{regulation_id}

Get detailed information about a specific module.

**Response:**

```json
{
  "metadata": {
    "id": "eu_ai_act",
    "name": "EU Artificial Intelligence Act",
    "articles": ["Art 5", "Art 6", "..."]
  },
  "controls_count": 12,
  "controls": [
    {
      "control_id": "EU-AI-9.1",
      "control_name": "Risk Management System",
      "description": "...",
      "article_ref": "Article 9",
      "required_evidence": ["Risk management policy"],
      "status": "pending"
    }
  ],
  "validation_rules_count": 4,
  "required_evidence": []
}

```

---

### POST /validate

Validate LLM-generated content against compliance rules (GPT Store pattern).

**Request Body:**

```json
{
  "response_text": "The AI-generated response to validate...",
  "context": "Original user prompt (optional)",
  "modules": ["eu_ai_act", "gdpr"],
  "user_metadata": {}
}

```

**Response:**

```json
{
  "validation_id": "uuid",
  "timestamp": "2024-01-15T10:30:00Z",
  "is_compliant": false,
  "violations": [
    {
      "violation_id": "uuid",
      "module_id": "gdpr",
      "rule_id": "GDPR-VAL-001",
      "severity": "high",
      "description": "Potential email detected in content",
      "location": "john.doe@example.com",
      "suggested_fix": "Remove or mask email data",
      "article_reference": "GDPR Article 5(1)(c)"
    }
  ],
  "warnings": [],
  "original_text": "...",
  "remediated_text": null,
  "was_modified": false,
  "audit_hash": "sha256:xyz789...",
  "modules_checked": ["eu_ai_act", "gdpr"]
}

```

---

### POST /batch

Run batch compliance assessments with MCP efficiency patterns.

**Request Body:**

```json
{
  "inputs": [
    {
      "content_type": "ai_chatbot",
      "content_id": "item_1",
      "modules": ["eu_ai_act"]
    },
    {
      "content_type": "ai_chatbot",
      "content_id": "item_2",
      "modules": ["eu_ai_act"]
    }
  ],
  "max_concurrent": 10
}

```

**Response:**

```json
{
  "batch_id": "uuid",
  "total_submitted": 2,
  "total_completed": 2,
  "total_failed": 0,
  "results": []
}

```

---

### GET /audit/{assessment_id}

Retrieve ShadowTag audit proof for an assessment.

**Response:**

```json
{
  "assessment_id": "uuid",
  "audit_hash": "sha256:abc123...",
  "timestamp": "2024-01-15T10:30:00Z",
  "access_type": "temporary_signed_url",
  "expires_in": "15 minutes",
  "url": "https://audit.activeshield.ai/v1/..."
}

```

---

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "initialized": true,
  "modules_registered": 8,
  "timestamp": "2024-01-15T10:30:00Z"
}

```

---

## Error Responses

All errors follow this format:

```json
{
  "error": "Error type",
  "message": "Detailed error message",
  "detail": {}
}

```

**Status Codes:**


- `200` - Success

- `400` - Bad Request (invalid input)

- `401` - Unauthorized (missing/invalid API key)

- `402` - Payment Required (tier limitation)

- `404` - Not Found

- `500` - Internal Server Error
