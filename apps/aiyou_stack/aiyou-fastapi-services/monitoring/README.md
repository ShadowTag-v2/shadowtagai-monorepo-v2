# Kuvasz Monitoring - Quick Start

## Overview

Kuvasz provides uptime and SSL monitoring for Judge #6 and Token Compression endpoints.

**Features:**


- 5-second interval uptime checking


- SSL certificate expiration monitoring (30-day threshold)


- Multi-channel alerting (Slack, Discord, PagerDuty, Email)


- Public/private status pages


- Prometheus metrics export

---

## Installation

### 1. Configure Environment

```bash

# Copy example environment file

cp .env.example .env

# Edit .env and set secure password

nano .env

# Change KUVASZ_DB_PASSWORD to a strong 32+ character password

```

### 2. Start Kuvasz Stack

```bash

# Start PostgreSQL + Kuvasz

docker-compose up -d

# Verify services are running

docker-compose ps

# Check logs

docker-compose logs -f kuvasz

```

### 3. Access Web Interface

Open browser to: **http://localhost:8080**

Default credentials:


- Username: `admin`


- Password: `admin` (change immediately in Settings)

---

## Configure Monitoring Targets

### Judge #6 Endpoint



1. Go to **Monitors** → **Add Monitor**


2. Configure:


   - **Name**: `Judge6 Health Check`


   - **URL**: `https://your-judge6-endpoint.com/health`


   - **Check Interval**: `5 seconds`


   - **SSL Check**: `Enabled`


   - **SSL Expiry Threshold**: `30 days`

### Token Compression Endpoint



1. **Monitors** → **Add Monitor**


2. Configure:


   - **Name**: `Token Compression API`


   - **URL**: `https://your-api.com/compress/health`


   - **Check Interval**: `5 seconds`


   - **Expected Status**: `200`

---

## Configure Alerts

### Slack Integration



1. Create Slack webhook: https://api.slack.com/messaging/webhooks


2. Add to `.env`:
   ```

   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```


3. Restart: `docker-compose restart kuvasz`

### PagerDuty Integration



1. Get integration key from PagerDuty service


2. Add to `.env`:
   ```

   PAGERDUTY_INTEGRATION_KEY=your_key_here
   ```


3. Restart: `docker-compose restart kuvasz`

---

## Create Status Page



1. Go to **Status Pages** → **Create**


2. Configure:


   - **Name**: `ShadowTagAi Platform Status`


   - **Visibility**: `Public` (for transparency)


   - **Monitors**: Select Judge6 + Token Compression


   - **Custom Domain**: `status.shadowtag.ai` (configure DNS)



3. **Publish Status Page**

---

## Monitoring SLA Compliance

### Judge #6 SLA: p99 ≤ 90ms



1. **Monitors** → **Judge6 Health Check** → **Settings**


2. Add **Response Time Threshold**:


   - Warn if p99 > 80ms


   - Alert if p99 > 90ms

### Uptime SLA: 99.9%

Kuvasz automatically tracks uptime percentage.
View in **Dashboard** → **Uptime Reports**

---

## Prometheus Integration

Kuvasz exposes metrics at: `http://localhost:8080/metrics`

**Key Metrics:**


- `kuvasz_uptime_percentage{monitor="judge6"}`


- `kuvasz_response_time_ms{monitor="judge6",quantile="0.99"}`


- `kuvasz_ssl_expiry_days{monitor="judge6"}`

### Grafana Dashboard

Import Kuvasz dashboard template:


1. Grafana → **Dashboards** → **Import**


2. Use template ID: `14583`


3. Configure data source: Prometheus

---

## Backup & Restore

### Backup

```bash

# Backup PostgreSQL database

docker-compose exec postgres pg_dump -U kuvasz kuvasz > kuvasz_backup.sql

# Backup config

docker-compose exec kuvasz tar czf /app/config_backup.tar.gz /app/config
docker cp kuvasz-monitor:/app/config_backup.tar.gz ./

```

### Restore

```bash

# Restore database

cat kuvasz_backup.sql | docker-compose exec -T postgres psql -U kuvasz kuvasz

# Restore config

docker cp config_backup.tar.gz kuvasz-monitor:/app/
docker-compose exec kuvasz tar xzf /app/config_backup.tar.gz -C /app

```

---

## Troubleshooting

### Kuvasz not starting

```bash

# Check logs

docker-compose logs kuvasz

# Common issue: Database not ready

# Solution: Wait 30 seconds, restart

docker-compose restart kuvasz

```

### FALSE 503 RATE LIMITS

```bash

# Check if kuvasz not connecting

docker-compose logs kuvasz | grep ERROR

# Verify database connection

docker-compose exec postgres psql -U kuvasz -c "SELECT version()"

```

### SSL Certificate Warnings

```bash

# Check certificate validity

openssl s_client -connect your-domain.com:443 -servername your-domain.com < /dev/null 2>/dev/null | openssl x509 -noout -dates

```

---

## Production Deployment

### 1. Use External PostgreSQL

Update `docker-compose.yml`:

```yaml
services:
  kuvasz:
    environment:
      DATABASE_HOST: your-postgres-host.com
      DATABASE_PORT: 5432
      # Remove postgres service dependency

```

### 2. Enable HTTPS

Use reverse proxy (nginx/Caddy):

```nginx
server {
    listen 443 ssl;
    server_name status.shadowtag.ai;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
    }
}

```

###3. Configure Custom Domain

Update `.env`:

```

KUVASZ_BASE_URL=https://status.shadowtag.ai

```

---

## Cost Estimate

**Self-hosted (Recommended):**


- VPS (2GB RAM, 2 vCPUs): $10-15/month


- Total: ~$12/month

**vs Cloud Monitoring:**


- UptimeRobot: $79/month (5-second intervals)


- Pingdom: $115/month


- **Savings: $67-103/month**

---

## Next Steps



1. ✅ Configure `.env` with secure password


2. ✅ Start Kuvasz: `docker-compose up -d`


3. ✅ Add Judge #6 endpoint monitoring


4. ✅ Add Token Compression monitoring


5. ✅ Configure Slack/PagerDuty alerts


6. ✅ Create public status page


7. ✅ Test SLA violation alerts

**Support**: https://github.com/kuvaszmonitoring/kuvasz/issues
