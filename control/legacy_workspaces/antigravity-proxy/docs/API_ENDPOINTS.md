# Gemini API Endpoints

Documentation of Google Gemini API endpoints used by Antigravity.

## Base URL

```
https://generativelanguage.googleapis.com
```

## Authentication

All requests require authentication via:

1. **Header**: `x-goog-api-key: YOUR_API_KEY`
2. **Query Parameter**: `?key=YOUR_API_KEY`

## Endpoints

### 1. Generate Content

Generate text/content from a prompt.

**Endpoint:**
```
POST /v1beta/models/{model}:generateContent
```

**Models:**
- `gemini-1.5-flash`
- `gemini-1.5-pro`
- `gemini-3.0-pro` (if available)

**Example:**
```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [{
        "text": "Explain quantum computing"
      }]
    }]
  }'
```

**Response:**
```json
{
  "candidates": [{
    "content": {
      "parts": [{
        "text": "Quantum computing is..."
      }],
      "role": "model"
    },
    "finishReason": "STOP"
  }]
}
```

### 2. Stream Generate Content

Stream generated content in real-time.

**Endpoint:**
```
POST /v1beta/models/{model}:streamGenerateContent
```

**Same parameters as Generate Content**, but response is streamed as Server-Sent Events (SSE).

### 3. Count Tokens

Count tokens in a prompt before sending.

**Endpoint:**
```
POST /v1beta/models/{model}:countTokens
```

**Example:**
```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:countTokens?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [{
        "text": "Hello world"
      }]
    }]
  }'
```

**Response:**
```json
{
  "totalTokens": 3
}
```

### 4. List Models

List available models.

**Endpoint:**
```
GET /v1beta/models
```

**Example:**
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_API_KEY"
```

**Response:**
```json
{
  "models": [
    {
      "name": "models/gemini-1.5-flash",
      "displayName": "Gemini 1.5 Flash",
      "description": "Fast and versatile..."
    }
  ]
}
```

### 5. Get Model

Get details about a specific model.

**Endpoint:**
```
GET /v1beta/models/{model}
```

**Example:**
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash?key=YOUR_API_KEY"
```

## Request Headers

Common headers used:

```
Content-Type: application/json
x-goog-api-key: YOUR_API_KEY
User-Agent: Antigravity-Proxy/1.0
```

## Error Responses

### 400 Bad Request
```json
{
  "error": {
    "code": 400,
    "message": "Invalid request",
    "status": "INVALID_ARGUMENT"
  }
}
```

### 401 Unauthorized
```json
{
  "error": {
    "code": 401,
    "message": "API key not valid",
    "status": "UNAUTHENTICATED"
  }
}
```

### 429 Too Many Requests
```json
{
  "error": {
    "code": 429,
    "message": "Resource exhausted",
    "status": "RESOURCE_EXHAUSTED"
  }
}
```

### 500 Internal Server Error
```json
{
  "error": {
    "code": 500,
    "message": "Internal error",
    "status": "INTERNAL"
  }
}
```

## Rate Limits

Free tier limits (as of 2025):
- **Requests per minute**: 15
- **Tokens per minute**: 1,000,000
- **Requests per day**: 1,500

Paid tier has higher limits based on your plan.

## Proxy Behavior

The Antigravity Proxy:

1. **Intercepts** all requests to `generativelanguage.googleapis.com`
2. **Extracts** the original API key from header or query parameter
3. **Replaces** with your configured API key
4. **Forwards** the modified request to Google's servers
5. **Returns** the response unchanged

## Testing Endpoints

You can test endpoints through the proxy:

```bash
# Start proxy
npm start

# Test through proxy
curl -x http://localhost:8080 \
  "https://generativelanguage.googleapis.com/v1beta/models?key=fake_key"
```

The proxy will replace `fake_key` with your real API key.

## References

- [Official Gemini API Documentation](https://ai.google.dev/api)
- [Gemini API Quickstart](https://ai.google.dev/gemini-api/docs/quickstart)
- [API Reference](https://ai.google.dev/api/all-methods)
