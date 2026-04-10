#!/usr/bin/env python3
"""
WALT (Web Automation LLM Tool) MCP Server
=========================================

Browser automation server implementing the Model Context Protocol (MCP).
Provides deterministic and agentic web automation tools via Playwright.

Cost Tiers:
- Deterministic: $0.0001/call (navigate, click, fill, extract)
- Agentic: $0.001/call (multi-step workflows with LLM decision-making)

Architecture:
- MCP Protocol: Tool discovery + execution interface
- Playwright: Headless browser automation
- Jura Integration: Cost tier routing + quota tracking
- Judge #6: Governance for agentic operations

Performance: p99 ≤150ms (deterministic), p99 ≤500ms (agentic)
"""

import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum, StrEnum
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from pydantic import BaseModel, Field

# Playwright for browser automation
try:
    from playwright.async_api import Browser, BrowserContext, Page, async_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning(
        "Playwright not available. Install with: pip install playwright && playwright install"
    )

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================


class Config:
    """Server configuration"""

    HOST: str = "0.0.0.0"
    PORT: int = 8081  # Different port from code execution MCP server
    WORKERS: int = 4

    # Browser pool
    BROWSER_POOL_SIZE: int = 5
    BROWSER_TIMEOUT_MS: int = 30000
    BROWSER_HEADLESS: bool = True

    # Cost tiers
    COST_DETERMINISTIC: float = 0.0001  # $0.0001 per call
    COST_AGENTIC: float = 0.001  # $0.001 per call

    # Timeouts
    NAVIGATION_TIMEOUT_MS: int = 10000
    ACTION_TIMEOUT_MS: int = 5000
    EXTRACT_TIMEOUT_MS: int = 15000

    # Jura integration (Redis)
    JURA_REDIS_HOST: str = "10.85.19.187"
    JURA_REDIS_PORT: int = 6379


config = Config()

# ============================================================================
# PROMETHEUS METRICS
# ============================================================================

metrics_tool_calls = Counter(
    "walt_tool_calls_total",
    "Total WALT tool calls",
    ["tool_name", "call_type", "status"],  # deterministic/agentic, success/error
)

metrics_tool_latency = Histogram(
    "walt_tool_latency_seconds",
    "WALT tool execution latency",
    ["tool_name", "call_type"],
    buckets=[0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 1.0, 2.0],
)

metrics_browser_pool = Gauge("walt_browser_pool_available", "Number of available browsers in pool")

metrics_cost_spent = Counter(
    "walt_cost_spent_dollars", "Total cost spent on WALT operations", ["call_type"]
)

# ============================================================================
# DATA MODELS
# ============================================================================


class CallType(StrEnum):
    """Cost tier for WALT operations"""

    DETERMINISTIC = "deterministic"  # $0.0001
    AGENTIC = "agentic"  # $0.001


class ToolName(StrEnum):
    """Available WALT tools"""

    # Deterministic tools
    NAVIGATE = "navigate"
    CLICK = "click"
    FILL = "fill"
    EXTRACT = "extract_text"
    EXTRACT_STRUCTURED = "extract_structured"
    SCREENSHOT = "screenshot"

    # Agentic tools
    WORKFLOW = "run_workflow"
    SEARCH_AND_EXTRACT = "search_and_extract"


@dataclass
class WALTTool:
    """MCP tool definition"""

    name: str
    description: str
    call_type: CallType
    cost: float
    input_schema: dict[str, Any]


class ToolCallRequest(BaseModel):
    """Request to execute a WALT tool"""

    tool_name: ToolName
    arguments: dict[str, Any]
    session_id: str = Field(..., description="Session ID for browser context reuse")
    user_id: str = Field(..., description="User ID for Jura quota tracking")
    call_type: CallType = Field(default=CallType.DETERMINISTIC)


class ToolCallResponse(BaseModel):
    """Response from tool execution"""

    success: bool
    result: Any | None = None
    error: str | None = None
    execution_time_ms: float
    cost_dollars: float
    call_type: CallType
    timestamp: str


# ============================================================================
# WALT TOOL REGISTRY
# ============================================================================

WALT_TOOLS: list[WALTTool] = [
    WALTTool(
        name="navigate",
        description="Navigate to a URL",
        call_type=CallType.DETERMINISTIC,
        cost=config.COST_DETERMINISTIC,
        input_schema={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to navigate to"},
                "wait_until": {
                    "type": "string",
                    "enum": ["load", "domcontentloaded", "networkidle"],
                    "default": "load",
                },
            },
            "required": ["url"],
        },
    ),
    WALTTool(
        name="click",
        description="Click an element by selector",
        call_type=CallType.DETERMINISTIC,
        cost=config.COST_DETERMINISTIC,
        input_schema={
            "type": "object",
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "CSS selector for element",
                },
                "button": {
                    "type": "string",
                    "enum": ["left", "right", "middle"],
                    "default": "left",
                },
            },
            "required": ["selector"],
        },
    ),
    WALTTool(
        name="fill",
        description="Fill a form field",
        call_type=CallType.DETERMINISTIC,
        cost=config.COST_DETERMINISTIC,
        input_schema={
            "type": "object",
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "CSS selector for input field",
                },
                "value": {"type": "string", "description": "Value to fill"},
            },
            "required": ["selector", "value"],
        },
    ),
    WALTTool(
        name="extract_text",
        description="Extract text from an element",
        call_type=CallType.DETERMINISTIC,
        cost=config.COST_DETERMINISTIC,
        input_schema={
            "type": "object",
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "CSS selector for element",
                },
                "multiple": {
                    "type": "boolean",
                    "default": False,
                    "description": "Extract from all matching elements",
                },
            },
            "required": ["selector"],
        },
    ),
    WALTTool(
        name="extract_structured",
        description="Extract structured data from page (table, list, etc.)",
        call_type=CallType.DETERMINISTIC,
        cost=config.COST_DETERMINISTIC,
        input_schema={
            "type": "object",
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "CSS selector for container",
                },
                "structure": {
                    "type": "string",
                    "enum": ["table", "list", "grid"],
                    "default": "table",
                },
            },
            "required": ["selector"],
        },
    ),
    WALTTool(
        name="screenshot",
        description="Take a screenshot of the current page or element",
        call_type=CallType.DETERMINISTIC,
        cost=config.COST_DETERMINISTIC,
        input_schema={
            "type": "object",
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "CSS selector for element (optional, full page if omitted)",
                },
                "full_page": {"type": "boolean", "default": True},
            },
        },
    ),
    WALTTool(
        name="run_workflow",
        description="Execute multi-step workflow with LLM decision-making (agentic)",
        call_type=CallType.AGENTIC,
        cost=config.COST_AGENTIC,
        input_schema={
            "type": "object",
            "properties": {
                "workflow_description": {
                    "type": "string",
                    "description": "Natural language description of workflow",
                },
                "max_steps": {
                    "type": "integer",
                    "default": 10,
                    "description": "Maximum steps to execute",
                },
            },
            "required": ["workflow_description"],
        },
    ),
    WALTTool(
        name="search_and_extract",
        description="Search for information and extract structured results (agentic)",
        call_type=CallType.AGENTIC,
        cost=config.COST_AGENTIC,
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "extract_fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Fields to extract",
                },
            },
            "required": ["query", "extract_fields"],
        },
    ),
]

# ============================================================================
# BROWSER MANAGER
# ============================================================================


class BrowserManager:
    """Manages Playwright browser pool"""

    def __init__(self, pool_size: int = config.BROWSER_POOL_SIZE):
        self.pool_size = pool_size
        self.playwright = None
        self.browser: Browser | None = None
        self.contexts: dict[str, BrowserContext] = {}
        self._initialized = False

    async def initialize(self):
        """Initialize Playwright and browser pool"""
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright not available")
            return

        logger.info(f"Initializing Playwright browser pool (size={self.pool_size})")

        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=config.BROWSER_HEADLESS,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ],
        )

        self._initialized = True
        metrics_browser_pool.set(self.pool_size)
        logger.info("Browser pool initialized")

    async def get_context(self, session_id: str) -> BrowserContext:
        """Get or create browser context for session"""
        if not self._initialized:
            await self.initialize()

        if session_id in self.contexts:
            return self.contexts[session_id]

        # Create new context
        context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        )
        self.contexts[session_id] = context
        return context

    async def cleanup_context(self, session_id: str):
        """Cleanup browser context"""
        if session_id in self.contexts:
            await self.contexts[session_id].close()
            del self.contexts[session_id]

    async def shutdown(self):
        """Shutdown browser and cleanup"""
        logger.info("Shutting down browser manager")

        for context in self.contexts.values():
            await context.close()
        self.contexts.clear()

        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


# ============================================================================
# TOOL EXECUTORS
# ============================================================================


class ToolExecutor:
    """Executes WALT tools"""

    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager

    async def execute(
        self, tool_name: ToolName, arguments: dict[str, Any], session_id: str
    ) -> tuple[bool, Any, str | None]:
        """Execute tool and return (success, result, error)"""

        # Get browser context and page
        context = await self.browser_manager.get_context(session_id)
        pages = context.pages
        if not pages:
            page = await context.new_page()
        else:
            page = pages[0]

        try:
            if tool_name == ToolName.NAVIGATE:
                return await self._navigate(page, arguments)
            elif tool_name == ToolName.CLICK:
                return await self._click(page, arguments)
            elif tool_name == ToolName.FILL:
                return await self._fill(page, arguments)
            elif tool_name == ToolName.EXTRACT:
                return await self._extract_text(page, arguments)
            elif tool_name == ToolName.EXTRACT_STRUCTURED:
                return await self._extract_structured(page, arguments)
            elif tool_name == ToolName.SCREENSHOT:
                return await self._screenshot(page, arguments)
            elif tool_name == ToolName.WORKFLOW:
                return await self._run_workflow(page, arguments)
            elif tool_name == ToolName.SEARCH_AND_EXTRACT:
                return await self._search_and_extract(page, arguments)
            else:
                return False, None, f"Unknown tool: {tool_name}"

        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return False, None, str(e)

    async def _navigate(self, page: Page, args: dict) -> tuple[bool, Any, str | None]:
        """Navigate to URL"""
        url = args["url"]
        wait_until = args.get("wait_until", "load")

        await page.goto(url, wait_until=wait_until, timeout=config.NAVIGATION_TIMEOUT_MS)
        return True, {"url": page.url, "title": await page.title()}, None

    async def _click(self, page: Page, args: dict) -> tuple[bool, Any, str | None]:
        """Click element"""
        selector = args["selector"]
        button = args.get("button", "left")

        await page.click(selector, button=button, timeout=config.ACTION_TIMEOUT_MS)
        return True, {"clicked": selector}, None

    async def _fill(self, page: Page, args: dict) -> tuple[bool, Any, str | None]:
        """Fill form field"""
        selector = args["selector"]
        value = args["value"]

        await page.fill(selector, value, timeout=config.ACTION_TIMEOUT_MS)
        return True, {"filled": selector, "value": value}, None

    async def _extract_text(self, page: Page, args: dict) -> tuple[bool, Any, str | None]:
        """Extract text from element(s)"""
        selector = args["selector"]
        multiple = args.get("multiple", False)

        if multiple:
            elements = await page.query_selector_all(selector)
            texts = [await el.inner_text() for el in elements]
            return True, {"texts": texts, "count": len(texts)}, None
        else:
            element = await page.query_selector(selector)
            if not element:
                return False, None, f"Element not found: {selector}"
            text = await element.inner_text()
            return True, {"text": text}, None

    async def _extract_structured(self, page: Page, args: dict) -> tuple[bool, Any, str | None]:
        """Extract structured data"""
        selector = args["selector"]
        structure = args.get("structure", "table")

        if structure == "table":
            # Extract table data
            rows = await page.query_selector_all(f"{selector} tr")
            data = []
            for row in rows:
                cells = await row.query_selector_all("td, th")
                row_data = [await cell.inner_text() for cell in cells]
                data.append(row_data)
            return True, {"data": data, "rows": len(data)}, None
        else:
            return False, None, f"Unsupported structure type: {structure}"

    async def _screenshot(self, page: Page, args: dict) -> tuple[bool, Any, str | None]:
        """Take screenshot"""
        selector = args.get("selector")
        full_page = args.get("full_page", True)

        if selector:
            element = await page.query_selector(selector)
            if not element:
                return False, None, f"Element not found: {selector}"
            screenshot_bytes = await element.screenshot()
        else:
            screenshot_bytes = await page.screenshot(full_page=full_page)

        # Encode to base64 for JSON response
        import base64

        screenshot_b64 = base64.b64encode(screenshot_bytes).decode()

        return (
            True,
            {"screenshot": screenshot_b64, "size_bytes": len(screenshot_bytes)},
            None,
        )

    async def _run_workflow(self, page: Page, args: dict) -> tuple[bool, Any, str | None]:
        """Run agentic workflow (placeholder - requires LLM integration)"""
        workflow_description = args["workflow_description"]
        max_steps = args.get("max_steps", 10)

        # TODO: Integrate with LLM for decision-making
        # For now, return mock result
        return (
            True,
            {
                "workflow": workflow_description,
                "steps_executed": 0,
                "status": "not_implemented",
            },
            "Agentic workflows not yet implemented",
        )

    async def _search_and_extract(self, page: Page, args: dict) -> tuple[bool, Any, str | None]:
        """Search and extract (placeholder - requires LLM integration)"""
        query = args["query"]
        extract_fields = args["extract_fields"]

        # TODO: Integrate with LLM for intelligent extraction
        return (
            True,
            {
                "query": query,
                "fields": extract_fields,
                "results": [],
                "status": "not_implemented",
            },
            "Agentic search not yet implemented",
        )


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

browser_manager: BrowserManager | None = None
tool_executor: ToolExecutor | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global browser_manager, tool_executor

    # Startup
    logger.info("Starting WALT MCP Server")
    browser_manager = BrowserManager()
    await browser_manager.initialize()
    tool_executor = ToolExecutor(browser_manager)
    logger.info("WALT server ready")

    yield

    # Shutdown
    logger.info("Shutting down WALT MCP Server")
    if browser_manager:
        await browser_manager.shutdown()


app = FastAPI(
    title="WALT MCP Server",
    description="Web Automation LLM Tool - MCP-compliant browser automation",
    version="1.0.0",
    lifespan=lifespan,
)

# ============================================================================
# MCP ENDPOINTS
# ============================================================================


@app.get("/tools/list")
async def list_tools():
    """MCP: List available tools"""
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "call_type": tool.call_type.value,
                "cost_dollars": tool.cost,
                "input_schema": tool.input_schema,
            }
            for tool in WALT_TOOLS
        ]
    }


@app.post("/tools/call", response_model=ToolCallResponse)
async def call_tool(request: ToolCallRequest) -> ToolCallResponse:
    """MCP: Execute a tool"""
    start_time = time.time()

    # Find tool definition
    tool_def = next((t for t in WALT_TOOLS if t.name == request.tool_name.value), None)
    if not tool_def:
        raise HTTPException(status_code=404, detail=f"Tool not found: {request.tool_name}")

    # Verify call type matches tool's expected type
    expected_call_type = tool_def.call_type
    actual_call_type = request.call_type
    cost = tool_def.cost if actual_call_type == expected_call_type else config.COST_AGENTIC

    # Execute tool
    success, result, error = await tool_executor.execute(
        request.tool_name, request.arguments, request.session_id
    )

    execution_time_ms = (time.time() - start_time) * 1000

    # Record metrics
    metrics_tool_calls.labels(
        tool_name=request.tool_name.value,
        call_type=actual_call_type.value,
        status="success" if success else "error",
    ).inc()

    metrics_tool_latency.labels(
        tool_name=request.tool_name.value, call_type=actual_call_type.value
    ).observe(execution_time_ms / 1000)

    metrics_cost_spent.labels(call_type=actual_call_type.value).inc(cost)

    return ToolCallResponse(
        success=success,
        result=result,
        error=error,
        execution_time_ms=execution_time_ms,
        cost_dollars=cost,
        call_type=actual_call_type,
        timestamp=datetime.now(UTC).isoformat(),
    )


@app.delete("/session/{session_id}")
async def cleanup_session(session_id: str):
    """Cleanup browser context for session"""
    await browser_manager.cleanup_context(session_id)
    return {"status": "cleaned", "session_id": session_id}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "browser_initialized": browser_manager._initialized if browser_manager else False,
        "active_sessions": len(browser_manager.contexts) if browser_manager else 0,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ============================================================================
# ENTRYPOINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "mcp_server:app",
        host=config.HOST,
        port=config.PORT,
        workers=config.WORKERS,
        log_level="info",
    )
