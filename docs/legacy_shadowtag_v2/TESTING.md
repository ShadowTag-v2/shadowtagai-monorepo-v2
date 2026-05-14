# Testing Guide

## Code Validation

All Python files have been validated for syntax correctness:
- ✓ src/main.py
- ✓ src/agents/growth_engineer_agent.py
- ✓ src/services/agent_service.py
- ✓ src/routes/growth_routes.py
- ✓ src/database.py
- ✓ All other Python files

## Testing Locally

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
cp .env.example .env
# Edit .env with your Anthropic API key
```

### 3. Run the Application

```bash
python -m src.main
```

### 4. Test Endpoints

#### Health Check
```bash
curl http://localhost:8000/health
```

#### List Agents
```bash
curl http://localhost:8000/api/v1/agents/
```

#### Execute Growth Engineer
```bash
curl -X POST "http://localhost:8000/api/v1/agents/growth_engineer/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Calculate viral coefficient for 2 invites per user and 30% conversion",
    "context": {}
  }'
```

#### Analyze Metrics
```bash
curl -X POST "http://localhost:8000/api/v1/growth/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "metrics": {
      "current": {"users": 5000, "revenue": 50000},
      "previous": {"users": 4000, "revenue": 40000}
    }
  }'
```

## Testing with Docker

```bash
docker-compose up
```

Then access:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- pgAdmin: http://localhost:5050

## Unit Tests

Run unit tests (after installing dependencies):

```bash
pytest tests/ -v --cov=src
```

## Integration Tests

Test the complete flow:

1. Start the service
2. Execute agent tasks
3. Check execution history
4. Verify results in database

## Vertex AI Testing

After deployment to Vertex AI:

```bash
# Get service URL from deployment
SERVICE_URL=https://your-service-url

# Test health
curl $SERVICE_URL/health

# Test agent execution
curl -X POST "$SERVICE_URL/api/v1/agents/growth_engineer/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Analyze growth metrics",
    "context": {"type": "test"}
  }'
```

## Performance Testing

Use tools like Apache Bench or wrk:

```bash
# Install wrk
brew install wrk  # macOS
# or
sudo apt-get install wrk  # Ubuntu

# Test health endpoint
wrk -t12 -c400 -d30s http://localhost:8000/health
```

## Monitoring

Monitor application logs:

```bash
# Local
tail -f logs/app.log

# Docker
docker-compose logs -f api

# Vertex AI / Cloud Run
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

## Common Test Scenarios

### 1. Growth Metrics Analysis
Test analyzing user growth metrics with AARRR framework

### 2. A/B Test Design
Test creating statistically valid A/B tests

### 3. Viral Loop Analysis
Test calculating viral coefficients and projections

### 4. Retention Analysis
Test cohort retention analysis

### 5. Funnel Optimization
Test conversion funnel analysis

## Expected Results

All tests should:
- Return 200 OK status
- Include execution_id in response
- Store results in database
- Complete within reasonable time (< 30s for most operations)

## Troubleshooting Tests

### Import Errors
```bash
export PYTHONPATH="${PYTHONPATH}:/home/user/aiyou-fastapi-services"
```

### Database Errors
```bash
# Reset database
python -c "from src.database import reset_db; reset_db()"
```

### API Key Errors
Ensure ANTHROPIC_API_KEY or Vertex AI credentials are set

## Next Steps

After successful testing:
1. Run full test suite
2. Check code coverage (aim for >80%)
3. Performance test under load
4. Deploy to staging environment
5. Run integration tests
6. Deploy to production
