# SITREP: Docker MCP Configuration & Agent Context

> **AUTHORITY:** The Board of Directors
> **TO:** Founder CEO Erik
> **SUBJECT:** Docker Desktop MCP Config, Container Isolation, and Developer Knowledge API

Based on the screenshot provided, you are configuring the `ast-grep` MCP server via the new Docker Desktop MCP Toolkit.

---

## 1. What is the `ast-grep.path` to put in Docker?

You must paste the absolute path to your Monorepo root:

**`/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball`**

**Why?** The Docker container needs explicit permission to read/write to your Mac's filesystem. Giving it this root path allows the `ast-grep` MCP server to scan your entire project's codebase.

## 2. What is Docker (in this context)?

Docker is a platform that wraps software into isolated, standardized packages called "Containers."

- **The Problem:** When an MCP server runs locally, it needs dependencies (like specific versions of Python, Rust, or Node). Installing these directly on your Mac can cause version conflicts and clutter ("dependency hell").
- **The Docker Solution:** Docker Desktop runs the `ast-grep` MCP server inside a perfectly clean, isolated, virtualized "bubble" (container).
- **The Catch:** Because it is a secure bubble, it is blind to your Mac's hard drive. The `ast-grep.path` input field is you poking a hole in that bubble so the container can "see" your Monorepo.

## 3. Am I using the Developer Knowledge API right now?

**No.** I am not currently utilizing the Google Developer Knowledge API.

**Current State:**
I am operating using my native Gemini 2.5/3.0 intelligence combined with the local Antigravity tools, the shell access you granted me, and the specific context provided in your `.md` files (like the Constitution and SKILL.md specs).

If you wish for me to integrate with the Developer Knowledge API, it would need to be added to your MCP client's configuration (or via Docker Desktop, if they offer a package for it) so I can query it as a tool!
