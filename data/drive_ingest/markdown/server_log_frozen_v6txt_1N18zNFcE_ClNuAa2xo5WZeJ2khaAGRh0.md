/Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/bin/https://github.com/karpathy/autoresearchs-server:153: DeprecationWarning:
        on_event is deprecated, use lifespan event handlers instead.

        Read more about it in the
        [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).

  @app.on_event("startup")
    MCP Bridge:       Enabled (Gemini CLI integration)

    ╔══════════════════════════════════════════════════════════════╗
    ║  https://github.com/karpathy/autoresearchS SERVER - Vertex AI Only (GCP Credits Mode)    ║
    ║  ─────────────────────────────────────────────────────────── ║
    ║  FREE  (30%): gemini-3.1-family-flash, 1 agent, 5s timeout          ║
    ║  FLASH (60%): gemini-3.1-flash, 3 agents, 2s timeout         ║
    ║  PRO   (10%): gemini-3-pro-preview, 8 agents, 10s            ║
    ║                                                              ║
    ║  Provider: Vertex AI ($350K GCP Credits)                     ║
    ║  Endpoints: /task, /governance, /jura/*, /mcp/*              ║
    ╚══════════════════════════════════════════════════════════════╝

INFO:     Started server process [36450]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8600 (Press CTRL+C to quit)
///▞ https://github.com/karpathy/autoresearchS SERVER :: Starting...
    Bulk model:       gemini-3.1-flash
    Governance model: gemini-3-pro-preview
///▞ FLYING MONKEYS :: Initializing 600 agent swarm (200 per shift)
///▞ FLYING MONKEYS :: Swarm initialized with 600 agents
    JURA Protocol:    Enabled (FREE/FLASH/PRO tiers)
///▞ https://github.com/karpathy/autoresearchS SERVER :: Ready on port 8600
    Total agents: 600
INFO:     127.0.0.1:65238 - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:65371 - "GET /health HTTP/1.1" 200 OK
