# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from fastapi import FastAPI

from .routers import bootstrap, context, health, hydrate, promotions, search, validate

app = FastAPI(title="ANE Cortex Stack API", version="0.10.0")
app.include_router(health.router)
app.include_router(search.router)
app.include_router(context.router)
app.include_router(bootstrap.router)
app.include_router(hydrate.router)
app.include_router(validate.router)
app.include_router(promotions.router)
