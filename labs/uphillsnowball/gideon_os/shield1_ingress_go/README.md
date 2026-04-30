# Shield1 Ingress (Go)

> Gideon OS Block — Zero-Trust API Gateway

## Purpose

Shield1 is the ingress gateway for all external traffic entering the Gideon OS
sovereign infrastructure. Written in Go for performance-critical request routing,
TLS termination, and rate limiting.

## Architecture

```
Internet ──► [Shield1 Ingress] ──► [Cor.Yay Bridge] ──► Internal Blocks
                │
                ├── TLS Termination (Let's Encrypt / Cloud Armor)
                ├── Rate Limiting (sliding window, per-IP + per-user)
                ├── Auth Verification (Firebase JWT validation)
                ├── Request Classification (benign / suspicious / hostile)
                └── Audit Logging (structured JSON → Panopticon)
```

## Features

- **Zero-Trust**: Every request is authenticated and classified before forwarding
- **Rate Limiting**: Token bucket algorithm with configurable per-endpoint limits
- **Request Classification**: Heuristic + ML-based classification via Panopticon feedback
- **Health Probes**: `/healthz`, `/readyz`, `/livez` endpoints for Kubernetes
- **Metrics**: Prometheus-compatible `/metrics` endpoint

## Configuration

```yaml
# shield1.yaml
server:
  port: 8443
  tls:
    cert_path: /etc/shield1/tls/cert.pem
    key_path: /etc/shield1/tls/key.pem
rate_limit:
  default_rps: 100
  burst_size: 20
auth:
  firebase_project_id: shadowtag-omega-v4
  allowed_issuers:
    - https://securetoken.google.com/shadowtag-omega-v4
```

## Status

- **Phase**: Scaffold
- **Language**: Go 1.24+
- **Dependencies**: `go.mod` scaffolded
- **Build**: `go build -o shield1 ./cmd/shield1`

## Development

```bash
# Build
go build -o shield1 ./cmd/shield1

# Run locally
./shield1 --config=shield1.yaml --mode=dev

# Test
go test ./...
```
