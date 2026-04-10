# Monitoring Expert - Comprehensive Observability Guide

## Overview

This FastAPI application includes a production-ready **Monitoring Expert** system that provides complete observability into your application's health and performance. The system knows when your app breaks before users complain through proactive monitoring, alerting, and dashboards.

## Key Features

### 1. **Structured Logging**

- JSON-formatted logs for easy parsing and analysis
- Correlation IDs for request tracking across services
- Log rotation with configurable retention
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Context-aware logging with automatic metadata enrichment

**Location**: `app/monitoring/logger.py`

### 2. **Prometheus Metrics**

- HTTP request/response metrics (rate, duration, status codes)
- System resource metrics (CPU, memory, disk usage)
- Custom business operation metrics
- Health check metrics
- Application uptime tracking

**Location**: `app/monitoring/metrics.py`

### 3. **OpenTelemetry Distributed Tracing**

- End-to-end request tracing
- Integration with Jaeger for trace visualization
- Automatic instrumentation of FastAPI routes
- Custom span creation for business operations

**Location**: `app/monitoring/tracing.py`

### 4. **Health Checks**

- **Liveness probe** (`/health`) - Is the app alive?
- **Readiness probe** (`/ready`) - Can the app handle traffic?
- Dependency health checks (database, external services)
- System resource monitoring

**Location**: `app/monitoring/health.py`

### 5. **Proactive Alerting**

- Multiple severity levels (CRITICAL, WARNING, INFO)
- Multiple notification channels (Webhook, Slack, Email)
- Configurable alert thresholds
- Alert history tracking

**Location**: `app/monitoring/alerts.py`

### 6. **Monitoring Middleware**

- Automatic request/response tracking
- Correlation ID injection
- Performance monitoring
- Error tracking
- Slow request detection

**Location**: `app/monitoring/middleware.py`

---

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 2. Run Locally

```bash
# Development mode
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Run with Docker Compose (Full Stack)

```bash
# Start all monitoring services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop all services
docker-compose down
```

This will start:

- **FastAPI App** on <http://localhost:8000>
- **Prometheus** on <http://localhost:9090>
- **Grafana** on <http://localhost:3000> (admin/admin)
- **Jaeger UI** on <http://localhost:16686>
- **AlertManager** on <http://localhost:9093>

---

## Endpoints

### Core Application

- `GET /` - Service information
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

### Monitoring Endpoints

- `GET /health` - Liveness probe (basic health check)
- `GET /ready` - Readiness probe (comprehensive dependency check)
- `GET /metrics` - Prometheus metrics endpoint
- `GET /monitoring/alerts` - Recent alerts history

### Example Endpoints

- `GET /api/v1/items` - List items
- `POST /api/v1/items` - Create item
- `GET /api/v1/items/{id}` - Get item by ID
- `GET /api/v1/slow-endpoint` - Test slow request alerting
- `GET /api/v1/error-endpoint` - Test error tracking

---

## Configuration

### Environment Variables

All configuration is managed through environment variables (see `.env.example`):

#### Application Settings

```bash
APP_NAME=shadowtag_v4-fastapi-services
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true
```

#### Logging Settings

```bash
LOG_LEVEL=INFO               # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json              # json or text
LOG_FILE_PATH=logs/app.log
LOG_MAX_BYTES=10485760       # 10MB
LOG_BACKUP_COUNT=5
```

#### Monitoring Settings

```bash
ENABLE_METRICS=true
METRICS_PORT=8001
ENABLE_TRACING=true
TRACING_SAMPLE_RATE=1.0      # 0.0 to 1.0
```

#### OpenTelemetry Settings

```bash
OTEL_SERVICE_NAME=shadowtag_v4-fastapi-services
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_EXPORTER_OTLP_INSECURE=true
```

#### Alert Settings

```bash
ALERT_WEBHOOK_URL=https://your-webhook.com/alerts
ALERT_SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
ALERT_EMAIL_ENABLED=false
ALERT_EMAIL_RECIPIENTS=redacted@shadowtag-v4.local
```

#### Sentry (Error Tracking)

```bash
SENTRY_DSN=https://redacted@shadowtag-v4.local/project
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_ENVIRONMENT=development
```

---

## Metrics

### Available Metrics

#### HTTP Metrics

- `http_requests_total` - Total HTTP requests (counter)
- `http_request_duration_seconds` - Request latency (histogram)
- `http_requests_in_progress` - Active requests (gauge)
- `http_exceptions_total` - Exception count (counter)
- `error_responses_total` - Error response count (counter)

#### System Metrics

- `system_cpu_usage_percent` - CPU usage percentage
- `system_memory_usage_percent` - Memory usage percentage
- `system_memory_usage_bytes` - Memory usage in bytes
- `system_disk_usage_percent` - Disk usage percentage

#### Application Metrics

- `app_uptime_seconds` - Application uptime
- `active_connections` - Active connections count

#### Health Check Metrics

- `health_check_status` - Health check status (1=healthy, 0=unhealthy)
- `health_check_duration_seconds` - Health check duration

#### Business Metrics

- `business_operations_total` - Business operation count
- `business_operation_duration_seconds` - Business operation duration

### Viewing Metrics

1. **Raw Prometheus format**: <http://localhost:8000/metrics>
2. **Prometheus UI**: <http://localhost:9090>
3. **Grafana Dashboard**: <http://localhost:3000>

---

## Alerts

### Pre-configured Alert Rules

Located in `monitoring/prometheus/alerts.yml`:

1. **HighErrorRate** - Error rate > 5% for 5 minutes
2. **HighRequestLatency** - P95 latency > 2 seconds for 5 minutes
3. **ServiceDown** - Service unavailable for 1 minute
4. **HighCPUUsage** - CPU > 80% for 5 minutes
5. **HighMemoryUsage** - Memory > 85% for 5 minutes
6. **HighDiskUsage** - Disk > 90% for 5 minutes
7. **UnhealthyService** - Health check failing for 2 minutes
8. **TooManyRequests** - Request rate > 1000 req/s for 5 minutes
9. **SlowHealthCheck** - Health check > 3 seconds for 5 minutes
10. **HighExceptionRate** - Exception rate > 10/s for 5 minutes

### Alert Channels

Configure alert channels in `monitoring/alertmanager/config.yml`:

- **Webhook** - Generic HTTP webhook
- **Slack** - Slack channel notifications
- **Email** - Email notifications
- **Custom** - Implement your own alert handlers

### Triggering Custom Alerts

```python
from app.monitoring.alerts import trigger_alert, AlertSeverity

await trigger_alert(
    name="custom_alert",
    severity=AlertSeverity.WARNING,
    message="Something needs attention",
    details={"key": "value"},
    metric_value=42.0,
    threshold=50.0
)
```

---

## Dashboards

### Grafana Dashboard

A comprehensive pre-built dashboard is available in `monitoring/grafana/dashboard.json`.

**Panels include**:

- Request rate (req/s)
- Error rate (%)
- Request latency (p50, p95, p99)
- Active requests
- CPU/Memory/Disk usage
- Health check status
- Application uptime
- Requests by endpoint
- Exception rate by type
- Business operations

**Import Instructions**:

1. Open Grafana: <http://localhost:3000> (admin/admin)
2. Go to Dashboards → Import
3. Upload `monitoring/grafana/dashboard.json`
4. Select Prometheus as data source

---

## Logging

### Log Format

JSON structured logs with the following fields:

```json
{
  "timestamp": "2025-11-15 10:30:45",
  "level": "INFO",
  "logger": "app.routers.example",
  "service": "shadowtag_v4-fastapi-services",
  "environment": "production",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Request completed",
  "method": "GET",
  "path": "/api/v1/items",
  "status_code": 200,
  "duration_seconds": 0.123
}
```

### Using the Logger

```python
from app.monitoring.logger import get_logger

logger = get_logger(__name__)

# Basic logging
logger.info("User logged in", user_id=123)
logger.warning("High memory usage", memory_percent=85.5)
logger.error("Database connection failed", error=str(e))

# Context-aware logging
from app.monitoring.logger import LogContext

with LogContext(user_id="123", operation="payment"):
    logger.info("Processing payment")
    # All logs in this block will include user_id and operation
```

### Log Rotation

Logs are automatically rotated based on configuration:

- Max file size: 10MB (configurable via `LOG_MAX_BYTES`)
- Backup count: 5 files (configurable via `LOG_BACKUP_COUNT`)
- Location: `logs/app.log`

---

## Distributed Tracing

### Jaeger UI

Access the Jaeger UI at <http://localhost:16686> to:

- View request traces across services
- Analyze request latency breakdown
- Debug slow requests
- Understand service dependencies

### Creating Custom Spans

```python
from app.monitoring.tracing import create_span

with create_span("database_query", {"query_type": "SELECT"}):
    # Your database operation
    result = await db.query("SELECT * FROM users")
```

---

## Health Checks

### Liveness Probe

**Endpoint**: `GET /health`

Returns basic health status. Used by orchestrators to determine if the app should be restarted.

**Response**:

```json
{
  "status": "healthy",
  "service": "shadowtag_v4-fastapi-services",
  "version": "1.0.0",
  "environment": "production",
  "uptime_seconds": 3600.5,
  "timestamp": "2025-11-15T10:30:45Z"
}
```

### Readiness Probe

**Endpoint**: `GET /ready`

Returns comprehensive health including all dependencies. Used by orchestrators to determine if the app can receive traffic.

**Response**:

```json
{
  "status": "healthy",
  "service": "shadowtag_v4-fastapi-services",
  "version": "1.0.0",
  "environment": "production",
  "uptime_seconds": 3600.5,
  "checks": [
    {
      "name": "system_resources",
      "status": "healthy",
      "message": "System resources within normal limits",
      "details": {
        "cpu_percent": 45.2,
        "memory_percent": 62.5,
        "disk_percent": 38.1
      },
      "duration_seconds": 0.012,
      "timestamp": "2025-11-15T10:30:45Z"
    },
    {
      "name": "database",
      "status": "healthy",
      "message": "Database connection successful",
      "details": {
        "connection_pool": "available"
      },
      "duration_seconds": 0.045,
      "timestamp": "2025-11-15T10:30:45Z"
    }
  ],
  "timestamp": "2025-11-15T10:30:45Z"
}
```

### Adding Custom Health Checks

```python
from app.monitoring.health import health_checker, HealthCheckResult, HealthStatus
import time

async def check_redis() -> HealthCheckResult:
    start_time = time.time()
    try:
        # Your Redis check logic
        await redis.ping()
        duration = time.time() - start_time

        return HealthCheckResult(
            name="redis",
            status=HealthStatus.HEALTHY,
            message="Redis connection successful",
            duration=duration
        )
    except Exception as e:
        duration = time.time() - start_time
        return HealthCheckResult(
            name="redis",
            status=HealthStatus.UNHEALTHY,
            message=f"Redis connection failed: {str(e)}",
            duration=duration
        )

# Register the check
health_checker.register_check(check_redis)
```

---

## Best Practices

### 1. Correlation IDs

All requests automatically get a correlation ID for tracking across services. Access it in logs and traces.

### 2. Custom Metrics

Track business-specific metrics:

```python
from app.monitoring.metrics import MetricsCollector

MetricsCollector.record_business_operation(
    operation_type="payment_processed",
    status="success",
    duration=1.23
)
```

### 3. Error Tracking

Errors are automatically tracked. For Sentry integration, set `SENTRY_DSN` in your environment.

### 4. Alert Tuning

Adjust alert thresholds in `monitoring/prometheus/alerts.yml` based on your application's baseline performance.

### 5. Log Sampling

In high-traffic environments, consider log sampling to reduce volume while maintaining visibility.

---

## Troubleshooting

### Issue: Metrics not showing in Prometheus

- Verify `/metrics` endpoint is accessible
- Check Prometheus configuration in `monitoring/prometheus/prometheus.yml`
- Ensure app is running and reachable from Prometheus container

### Issue: Alerts not triggering

- Check AlertManager configuration in `monitoring/alertmanager/config.yml`
- Verify webhook URLs and credentials
- Check AlertManager logs: `docker-compose logs alertmanager`

### Issue: Traces not appearing in Jaeger

- Verify `ENABLE_TRACING=true` in environment
- Check Jaeger endpoint configuration
- Ensure OTLP exporter is reachable

### Issue: High memory usage

- Review `TRACING_SAMPLE_RATE` - reduce if set to 1.0
- Check log rotation settings
- Monitor system metrics in Grafana

---

## Production Deployment Checklist

- [ ] Set `DEBUG=false` in production
- [ ] Configure proper `LOG_LEVEL` (INFO or WARNING)
- [ ] Set up Sentry DSN for error tracking
- [ ] Configure alert channels (Slack, email, webhook)
- [ ] Adjust alert thresholds for your traffic patterns
- [ ] Set up proper authentication for Grafana
- [ ] Configure CORS allowed origins appropriately
- [ ] Enable HTTPS/TLS for all endpoints
- [ ] Set up log aggregation (ELK, Splunk, etc.)
- [ ] Configure metric retention policies
- [ ] Set up backup for Prometheus/Grafana data
- [ ] Document on-call procedures
- [ ] Test alert delivery channels
- [ ] Configure rate limiting if needed
- [ ] Set up monitoring for the monitoring stack itself

---

## Architecture Diagram

```
┌─────────────────┐
│   FastAPI App   │
│                 │
│  ┌───────────┐  │
│  │ Middleware│  │ ──► Automatic request tracking
│  └───────────┘  │
│                 │
│  ┌───────────┐  │
│  │  Logging  │  │ ──► JSON logs with correlation IDs
│  └───────────┘  │
│                 │
│  ┌───────────┐  │
│  │  Metrics  │  │ ──► Prometheus metrics
│  └───────────┘  │
│                 │
│  ┌───────────┐  │
│  │  Tracing  │  │ ──► OpenTelemetry spans
│  └───────────┘  │
└────────┬────────┘
         │
         ├──────► Prometheus ──► AlertManager ──► Notifications
         │              │
         │              └──────► Grafana (Dashboards)
         │
         └──────► Jaeger (Distributed Tracing)
```

---

## Support

For issues, questions, or contributions:

- Check the logs: `logs/app.log`
- Review metrics: <http://localhost:8000/metrics>
- Check health: <http://localhost:8000/ready>
- View traces: <http://localhost:16686>

---

## License

This monitoring system is part of the ShadowTag-v2 FastAPI Services project.
