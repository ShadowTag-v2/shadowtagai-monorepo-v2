from fastapi import FastAPI

from .routers import bootstrap, context, health, hydrate, search

app = FastAPI(title="ANE Cortex Stack API", version="0.9.0")
app.include_router(health.router)
app.include_router(search.router)
app.include_router(context.router)
app.include_router(bootstrap.router)
app.include_router(hydrate.router)
