# ⚡ Quick Start Guide - Performance Engineer

Get up and running in 5 minutes!

## 🚀 Installation (1 minute)

```bash
# Clone and enter directory
cd ShadowTag-v2-fastapi-services

# Run the startup script (handles everything)
./start.sh
```

**Or manually:**

```bash
# Install dependencies
pip install -r requirements.txt

# Copy configuration
cp .env.example .env

# Start the server
uvicorn app.main:app --reload
```

---

## 🎯 First Steps (2 minutes)

### 1. Start the server

```bash
./start.sh
```

### 2. Visit the API

- **Docs**: <http://localhost:8000/docs>
- **Summary**: <http://localhost:8000/performance/summary>

### 3. Test with example endpoints

```bash
# Make some requests
curl http://localhost:8000/api/example/fast
curl http://localhost:8000/api/example/slow
curl http://localhost:8000/api/example/very-slow

# Check detected issues
curl http://localhost:8000/performance/summary
```

---

## 💡 Find & Fix Bottlenecks (2 minutes)

### See what's slow

```bash
curl http://localhost:8000/performance/summary
```

**Returns:**

```json
{
  "critical_bottlenecks": [
    {
      "location": "app/main.py:78",
      "function": "very_slow_endpoint",
      "impact": "95.2% of request time"
    }
  ]
}
```

### Get specific fix

```bash
curl http://localhost:8000/performance/bottlenecks/1/fix
```

**Returns exact code to fix the issue!**

---

## 🔥 Key Endpoints

| What You Want           | Endpoint                                |
| ----------------------- | --------------------------------------- |
| **Top 5 issues to fix** | `/performance/summary`                  |
| **Full report**         | `/performance/report`                   |
| **All bottlenecks**     | `/performance/bottlenecks`              |
| **Specific fix**        | `/performance/bottlenecks/{id}/fix`     |
| **Slow endpoints**      | `/performance/slow-endpoints`           |
| **Optimization tips**   | `/performance/optimization-suggestions` |
| **Cache stats**         | `/performance/cache/stats`              |

---

## 💾 Enable Caching (Optional)

### Using Docker

```bash
docker run -d -p 6379:6379 redis:latest
```

### In your code

```python
from app.services.caching import cache_response

@app.get("/api/data")
@cache_response('data', ttl=300)
async def get_data():
    # Expensive operation here
    return result
```

**That's it! Automatic caching with hit/miss tracking.**

---

## 📊 Typical Workflow

1. **Run your app** with Performance Engineer
2. **Make requests** to your endpoints (normal usage)
3. **Check summary** every few hours

   ```bash
   curl http://localhost:8000/performance/summary
   ```

4. **Get specific fixes** for bottlenecks

   ```bash
   curl http://localhost:8000/performance/bottlenecks/1/fix
   ```

5. **Apply the fix** (copy the code example)
6. **Verify improvement**

   ```bash
   curl http://localhost:8000/performance/trends/api/your-endpoint
   ```

---

## 🎓 Quick Tips

✅ **Enable profiling** - It's lightweight and runs automatically
✅ **Check summary daily** - Find issues before users do
✅ **Start with critical** - Fix high-impact bottlenecks first
✅ **Use the cache decorator** - One line = massive speedup
✅ **Monitor trends** - Track performance over time

---

## 🔧 Configuration

Edit `.env`:

```env
# Must-have settings
ENABLE_PROFILING=true    # Auto-profile requests
ENABLE_CACHE=true        # Smart caching

# Fine-tuning
SLOW_REQUEST_THRESHOLD=1.0     # Flag requests > 1 second
BOTTLENECK_THRESHOLD=0.1       # Flag functions > 100ms
CACHE_TTL=300                  # Cache for 5 minutes
```

---

## 📈 Example Results

**Before:**

```
GET /api/users → 2.3 seconds
```

**After applying suggested fixes:**

```
GET /api/users → 0.12 seconds (19x faster!)
```

**Common improvements:**

- Caching: **90-99% faster**
- N+1 fixes: **10-50x faster**
- Async I/O: **5-20x faster**

---

## ❓ Troubleshooting

### Redis not connecting?

```env
# Disable caching temporarily
ENABLE_CACHE=false
```

### No bottlenecks showing?

- Make some requests first
- Lower the threshold: `BOTTLENECK_THRESHOLD=0.01`

### Profiling overhead?

```env
# Sample only 10% of requests
PROFILING_SAMPLE_RATE=0.1
```

---

## 🎯 Next Steps

1. ✅ Read the [Full Documentation](README.md)
2. ✅ Check the [API Docs](http://localhost:8000/docs)
3. ✅ Start optimizing your endpoints!

---

**Ready to make your app lightning fast? Let's go! ⚡**
