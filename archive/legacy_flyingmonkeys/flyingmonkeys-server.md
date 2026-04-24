---
description: Start and verify the FlyingMonkeys Agent Swarm Server
---

# FlyingMonkeys Server Workflow

This workflow starts the FlyingMonkeys server (JURA Protocol Agent Swarm) and verifies its health and task execution capabilities.

## 1. Check for existing process

// turbo
pkill -f flyingmonkeys || true

## 2. Start the Server

Start the server in the background.

```bash
python3 bin/flyingmonkeys-server > flyingmonkeys.log 2>&1 &

```

## 3. Wait for Startup

Wait for the server to initialize (approx 5-10 seconds).

```bash
sleep 10

```

## 4. Verify Health

Check the health endpoint.

```bash
curl -s http://localhost:8600/health | grep "ok"

```

## 5. Verify Task Execution

Run a test task to verify JURA protocol routing.

```bash
curl -X POST http://localhost:8600/task \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Workflow Verification Test"}'

```

## 6. Check Logs (Optional)

If any issues, check the logs.

```bash
tail -n 20 flyingmonkeys.log

```
