from __future__ import annotations

import importlib
import os
import sys
from types import SimpleNamespace


def test_router_packages_expose_agent_contracts() -> None:
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
    os.environ["DEBUG"] = "release"

    from src import schemas

    assert hasattr(schemas, "AIAgentCreate")
    assert hasattr(schemas, "AIAgentResponse")
    assert hasattr(schemas, "ChatRequest")
    assert hasattr(schemas, "ChatResponse")


def test_knowledge_router_imports_under_src_package() -> None:
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
    os.environ["DEBUG"] = "release"

    sys.modules.setdefault(
        "src.vector_db",
        SimpleNamespace(ingest_document=lambda *_args, **_kwargs: None),
    )

    knowledge = importlib.import_module("src.routers.knowledge")

    assert knowledge.router.prefix == "/workspaces/{workspace_id}/knowledge"


def test_main_app_imports_and_registers_knowledge_route() -> None:
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
    os.environ["DEBUG"] = "release"

    sys.modules.setdefault(
        "src.vector_db",
        SimpleNamespace(ingest_document=lambda *_args, **_kwargs: None),
    )

    main = importlib.import_module("src.main")
    paths = {route.path for route in main.app.routes}

    assert "/workspaces/{workspace_id}/knowledge/upload" in paths
