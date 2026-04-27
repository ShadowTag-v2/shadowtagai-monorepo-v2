# Go Shield Layer

HTTP middleware for Cloud Run services providing:
- Token bucket rate limiting (10 req/s, burst 50)
- Authorization header validation
- Health check endpoint (`/health`)

## Build
```bash
go build -o shield ./...
```

## Deploy
Runs as a sidecar on Cloud Run Gen2.
