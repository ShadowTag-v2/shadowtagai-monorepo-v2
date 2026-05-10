# 🚀 Quick Start - Test Locally in 2 Minutes

No GCP credentials needed! This will run the service in **mock mode** for immediate testing.

## Step 1: Run the Quick Start Script

```bash
./quick_start.sh
```

This script will:

1. Create a Python virtual environment
2. Install all dependencies
3. Configure mock mode (no GCP required)
4. Start the service on <http://localhost:8000>

**That's it!** The service will be running with mock Vertex AI responses.

## Step 2: Test the Service (in another terminal)

```bash
./test_local.sh
```

This runs 9 comprehensive tests including:

- Health checks
- Listing verticals
- Processing queries for defense and healthcare
- Kill switch status
- Metrics collection

## Example: Test a Query Manually

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Can we share classified information with contractors?",
    "vertical": "defense"
  }' | jq .
```

**Expected Response:**

```json
{
  "query": "Can we share classified information with contractors?",
  "vertical": "defense",
  "enforcement": {
    "allowed": true,
    "confidence": 0.95,
    "policy_violations": [],
    "required_actions": [],
    "total_latency_ms": 45
  },
  "policy_context": {
    "citations": [
      {
        "type": "corpus",
        "uri": "gs://mock-bucket/defense/ATP_5-19.pdf",
        "text": "ATP 5-19 Section 2.3: Information operations require command approval."
      }
    ],
    "source_documents": [
      "gs://mock-bucket/defense/ATP_5-19.pdf"
    ],
    "retrieval_time_ms": 623
  },
  "timing": {
    "file_search_ms": 623,
    "judge_layer1_ms": 38,
    "enforcement_ms": 45,
    "total_ms": 706
  }
}
```

## Explore the API

Open the interactive API documentation:
**<http://localhost:8000/docs>**

This shows all available endpoints with:

- Request/response schemas
- "Try it out" interactive testing
- Example payloads
- Response codes

## What's Running in Mock Mode?

- ✅ **FastAPI service** - Real HTTP server
- ✅ **All 30 verticals** - Defense, healthcare, finance, etc.
- ✅ **Prometheus metrics** - Real metrics collection
- ✅ **Kill switch** - Actual monitoring logic
- 🔄 **File Search** - Mocked Vertex AI responses
- 🔄 **Judge 6** - Placeholder responses

Mock responses simulate realistic latencies and data structures.

## Next Steps

### Option 1: Continue with Mock Mode

Perfect for:

- Understanding the API
- Testing your client code
- Developing Judge 6 layers
- Integration testing

### Option 2: Switch to Real GCP

When you're ready to test with actual Vertex AI:

1. **Get GCP credentials:**

   ```bash
   gcloud auth application-default login
   ```

2. **Update .env:**

   ```bash
   # Change MOCK_MODE to false
   sed -i 's/MOCK_MODE=true/MOCK_MODE=false/' .env

   # Set your real project
   sed -i 's/mock-project/your-real-project-id/' .env
   ```

3. **Restart service:**

   ```bash
   # Stop current service (Ctrl+C)
   # Restart
   python -m pnkln_file_search.main
   ```

See **LOCAL_SETUP.md** for detailed GCP setup instructions.

## Troubleshooting

### Port 8000 already in use

```bash
# Change port in .env
echo "SERVICE_PORT=8001" >> .env

# Or kill existing process
lsof -ti:8000 | xargs kill -9
```

### Python dependencies failing

```bash
# Make sure you're using Python 3.10+
python3 --version

# Upgrade pip
pip install --upgrade pip

# Try installing again
pip install -r requirements.txt
```

### Virtual environment issues

```bash
# Remove and recreate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Development

While the service is running in mock mode, you can:

1. **Edit Judge 6 implementation** - See `JUDGE_IMPLEMENTATION_GUIDE.md`
2. **Add custom verticals** - Edit `src/pnkln_file_search/config/verticals.py`
3. **Customize mock responses** - Edit `src/pnkln_file_search/config/mock_mode.py`
4. **Test different scenarios** - Modify queries in `test_local.sh`

## Summary: You're Running

✅ **Service**: <http://localhost:8000>
✅ **Docs**: <http://localhost:8000/docs>
✅ **Metrics**: <http://localhost:8000/metrics>
✅ **Mode**: Mock (no GCP required)

**Time to working service: ~2 minutes** ⚡

Enjoy exploring the Pnkln File Search integration!
