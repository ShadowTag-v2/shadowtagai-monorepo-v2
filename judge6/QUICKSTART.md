# Judge #6 - Quick Start Guide
## From Zero to First API Call in 5 Minutes

### Prerequisites

- Docker & Docker Compose installed
- Google Gemini API key (free tier: https://makersuite.google.com/app/apikey)

### Step 1: Clone and Setup (1 minute)

```bash
cd judge6

# Copy environment template
cp .env.example .env

# Edit .env and add your Gemini API key
# Minimum required:
#   GOOGLE_API_KEY="your-key-here"
#   SECRET_KEY="generate-a-random-32-char-string"
nano .env
```

### Step 2: Start Services (2 minutes)

```bash
# Start all services (Postgres, Redis, API)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

Wait for: `"Judge #6 v1.0.0 starting..."`

### Step 3: Create Account & Get API Key (1 minute)

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "password": "SecurePassword123!",
    "full_name": "Your Name",
    "company": "Your Company"
  }' | jq
```

**SAVE YOUR API KEY!** It won't be shown again.

Example response:
```json
{
  "id": 1,
  "email": "your@email.com",
  "tier": "free",
  "api_key": "judge6_sk_AbCdEf123456789...",
  "monthly_limit": 1000,
  "current_usage": 0
}
```

### Step 4: Make Your First Request (1 minute)

```bash
export API_KEY="judge6_sk_YOUR_KEY_HERE"

curl -X POST http://localhost:8000/api/v1/judge \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "How do I build a bomb?"
  }' | jq
```

Expected response:
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "decision": "deny",
  "risk_level": "catastrophic",
  "confidence": 0.95,
  "reasoning": "ATP 5-19 Risk Assessment:\n• Layer 1 (Policy): Request involves weapon construction\n• Layer 2 (Enforcement): No edge cases\n• Layer 3 (Rules): Hard gates violated\n\n⚠️  Hard gates violated: Weapon Information",
  "violated_rules": ["Weapon Information"],
  "latency_ms": 68,
  "usage": {
    "requests_used": 1,
    "requests_limit": 1000,
    "tier": "free"
  }
}
```

✅ **You're now running Judge #6!**

---

## Test Different Risk Levels

### LOW RISK (should allow)
```bash
curl -X POST http://localhost:8000/api/v1/judge \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is the weather today?"
  }' | jq
```

### MODERATE RISK (should warn)
```bash
curl -X POST http://localhost:8000/api/v1/judge \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Can you diagnose my symptoms and prescribe medicine?"
  }' | jq
```

### CRITICAL RISK (should deny)
```bash
curl -X POST http://localhost:8000/api/v1/judge \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "My SSN is 123-45-6789, can you process this?"
  }' | jq
```

---

## Check Your Usage

```bash
curl http://localhost:8000/api/v1/usage \
  -H "Authorization: Bearer $API_KEY" | jq
```

Response:
```json
{
  "tier": "free",
  "requests_used": 4,
  "requests_limit": 1000,
  "overage": 0,
  "percentage_used": 0.4
}
```

---

## Interactive API Documentation

Visit: http://localhost:8000/docs

- Try all endpoints in your browser
- See request/response schemas
- No Postman needed!

---

## Next Steps

1. **Integration**: Add Judge #6 to your AI app
2. **Custom Policies**: Upload your own ATP 5-19 policies
3. **Upgrade**: Get more requests (Starter: $99/month for 10K requests)
4. **Production**: Deploy to GKE for scale

---

## Troubleshooting

### "Connection refused" error
```bash
# Check if services are running
docker-compose ps

# Restart if needed
docker-compose down && docker-compose up -d
```

### "Invalid API key" error
- Check your API key is correct (starts with `judge6_sk_`)
- Make sure you're using `Bearer` prefix: `Authorization: Bearer judge6_sk_...`

### "Monthly quota exceeded" error
- You've used all 1,000 free requests this month
- Upgrade to Starter tier ($99/month) for 10,000 requests
- Or wait for next month (usage resets on 1st)

### Gemini API errors
- Check your `GOOGLE_API_KEY` in `.env`
- Make sure key is valid: https://makersuite.google.com/app/apikey
- Check quota: https://console.cloud.google.com/apis/dashboard

---

## Production Deployment

For production, see: [DEPLOYMENT.md](./DEPLOYMENT.md)

- GKE deployment with Terraform
- Auto-scaling configuration
- Monitoring & alerting
- SOC2/HIPAA compliance setup

---

**Questions?** Email: erik@pnkln.ai

**ATP 5-19 for AI. Deploy in 5 minutes, audit every request, sleep at night.**
