/**
 * Multi-Model Router (OpenAI-compatible proxy)
 *
 * Routes requests to different LLM providers based on query parameter.
 * Supports: OpenAI (GPT-5), xAI (Grok), Anthropic (Claude), Groq (Cheetah), local models
 *
 * Usage:
 *   POST http://localhost:8787/v1/chat/completions?target=grok
 *   POST http://localhost:8787/v1/chat/completions?target=cheetah
 *   POST http://localhost:8787/v1/chat/completions (defaults to OpenAI)
 */

import type { Request, Response } from "express";
import express from "express";
import fetch from "node-fetch";

const app = express();
app.use(express.json({ limit: "5mb" }));

interface TargetConfig {
  base: string;
  key: string;
  model: string;
}

/**
 * Select LLM backend based on target query parameter.
 */
function pickTarget(target: string | undefined): TargetConfig {
  const t = (target || "openai").toLowerCase();

  switch (t) {
    case "grok":
      return {
        base: process.env.XAI_BASE_URL!,
        key: process.env.XAI_API_KEY!,
        model: process.env.XAI_MODEL!,
      };

    case "cheetah":
      return {
        base: process.env.CHEETAH_BASE_URL!,
        key: process.env.CHEETAH_API_KEY!,
        model: process.env.CHEETAH_MODEL!,
      };

    case "anthropic":
      // Note: Anthropic is not fully OpenAI-compatible
      // For production, use Anthropic's native SDK
      return {
        base: "https://api.anthropic.com/v1",
        key: process.env.ANTHROPIC_API_KEY!,
        model: process.env.ANTHROPIC_MODEL!,
      };

    case "alt":
      return {
        base: process.env.ALT_BASE_URL!,
        key: process.env.ALT_API_KEY!,
        model: process.env.ALT_MODEL!,
      };

    case "local":
      return {
        base: process.env.LOCAL_BASE_URL!,
        key: "no-key",
        model: process.env.LOCAL_MODEL!,
      };

    case "openai":
    default:
      return {
        base: process.env.OPENAI_BASE_URL!,
        key: process.env.OPENAI_API_KEY!,
        model: process.env.OPENAI_MODEL!,
      };
  }
}

/**
 * OpenAI-compatible chat completions endpoint.
 */
app.post("/v1/chat/completions", async (req: Request, res: Response) => {
  try {
    const target = pickTarget(req.query.target as string);

    // Prepare request body
    const body = { ...req.body };
    if (!body.model) {
      body.model = target.model;
    }

    // Prepare headers
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    if (target.key && target.key !== "no-key") {
      headers["Authorization"] = `Bearer ${target.key}`;
    }

    // Some providers (e.g., OpenRouter) require additional headers
    if (process.env.HTTP_REFERER) {
      headers["HTTP-Referer"] = process.env.HTTP_REFERER;
    }
    if (process.env.X_TITLE) {
      headers["X-Title"] = process.env.X_TITLE;
    }

    // Forward request to target provider
    const response = await fetch(`${target.base}/chat/completions`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });

    const text = await response.text();

    // Forward response back to client
    res
      .status(response.status)
      .set("Content-Type", response.headers.get("content-type") || "application/json")
      .send(text);
  } catch (e: any) {
    console.error("Router error:", e);
    res.status(500).json({
      error: {
        message: e?.message || String(e),
        type: "router_error",
      },
    });
  }
});

/**
 * Health check endpoint.
 */
app.get("/health", (req: Request, res: Response) => {
  res.json({
    status: "ok",
    uptime: process.uptime(),
    timestamp: new Date().toISOString(),
  });
});

/**
 * Root endpoint (info).
 */
app.get("/", (req: Request, res: Response) => {
  res.json({
    name: "AiYou Multi-Model Router",
    version: "0.1.0",
    endpoints: {
      chat: "/v1/chat/completions",
      health: "/health",
    },
    targets: ["openai", "grok", "cheetah", "anthropic", "alt", "local"],
    usage: "POST /v1/chat/completions?target=<target>",
  });
});

// Start server
const port = Number(process.env.PORT || 8787);
app.listen(port, () => {
  console.log(`[router] Multi-model proxy listening on :${port}`);
  console.log(`[router] Targets: openai, grok, cheetah, anthropic, alt, local`);
  console.log(`[router] Example: POST http://localhost:${port}/v1/chat/completions?target=grok`);
});
