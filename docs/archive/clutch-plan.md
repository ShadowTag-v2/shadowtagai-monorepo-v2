# Core Plan (Agent Wiring Phase)

1. Monitor Omega Loop success.
2. Edit `scripts/omega_worker.py` -> `execute_heavy_lift`.
3. Rip out `asyncio.sleep(1)`.
4. Import and execute the agent infrastructure, passing `task_payload` natively.
5. Return the payload.
