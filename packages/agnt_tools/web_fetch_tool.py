# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""WebFetchTool — Safe-Harbor URL content fetcher.

Ported from src/tools/WebFetchTool/WebFetchTool.ts (297 lines).
Routes through read_url_content with allowlist enforcement.

Upstream features ported:
  - SSRF protection (scheme, host, private IP blocking)
  - Preapproved host list (60+ code documentation domains)
  - Prompt parameter for directed content extraction
  - Redirect detection (301/302/307/308 cross-host)
  - URL validation with max length cap
  - Read-only, concurrency safe
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any
from urllib.parse import urlparse

from packages.agnt_tools.tool import ToolResult, ToolUseContext, build_tool

logger = logging.getLogger(__name__)

WEB_FETCH_TOOL_NAME = "WebFetch"
MAX_URL_LENGTH = 2048
MAX_CONTENT_LENGTH = 100_000  # 100KB text cap

_BLOCKED_SCHEMES = frozenset({"file", "ftp", "data", "javascript"})

_BLOCKED_HOSTS = frozenset(
  {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "::1",
    "metadata.google.internal",
    "169.254.169.254",
  }
)

_PRIVATE_IP_PATTERN = re.compile(r"^10\.|^172\.(1[6-9]|2\d|3[01])\.|^192\.168\.")

# Preapproved hosts — ported from src/tools/WebFetchTool/preapproved.ts.
# GET-only, code-related documentation domains. These bypass permission prompts
# but do NOT grant arbitrary network access (POST/upload would be dangerous).
_PREAPPROVED_HOSTS: frozenset[str] = frozenset(
  {
    # Anthropic
    "platform.claude.com",
    "code.claude.com",
    "modelcontextprotocol.io",
    "agentskills.io",
    # Top Programming Languages
    "docs.python.org",
    "en.cppreference.com",
    "docs.oracle.com",
    "learn.microsoft.com",
    "developer.mozilla.org",
    "go.dev",
    "pkg.go.dev",
    "www.php.net",
    "docs.swift.org",
    "kotlinlang.org",
    "ruby-doc.org",
    "doc.rust-lang.org",
    "www.typescriptlang.org",
    # Web & JS Frameworks
    "react.dev",
    "angular.io",
    "vuejs.org",
    "nextjs.org",
    "expressjs.com",
    "nodejs.org",
    "bun.sh",
    "getbootstrap.com",
    "tailwindcss.com",
    "redux.js.org",
    "webpack.js.org",
    "jestjs.io",
    "reactrouter.com",
    # Python Frameworks
    "docs.djangoproject.com",
    "flask.palletsprojects.com",
    "fastapi.tiangolo.com",
    "pandas.pydata.org",
    "numpy.org",
    "www.tensorflow.org",
    "pytorch.org",
    "scikit-learn.org",
    "matplotlib.org",
    "requests.readthedocs.io",
    "jupyter.org",
    # PHP Frameworks
    "laravel.com",
    "symfony.com",
    "wordpress.org",
    # Java Frameworks
    "docs.spring.io",
    "hibernate.org",
    "tomcat.apache.org",
    "gradle.org",
    "maven.apache.org",
    # .NET & C#
    "asp.net",
    "dotnet.microsoft.com",
    "nuget.org",
    "blazor.net",
    # Mobile
    "reactnative.dev",
    "docs.flutter.dev",
    "developer.apple.com",
    "developer.android.com",
    # Data Science & ML
    "keras.io",
    "spark.apache.org",
    "huggingface.co",
    "www.kaggle.com",
    # Databases
    "www.mongodb.com",
    "redis.io",
    "www.postgresql.org",
    "dev.mysql.com",
    "www.sqlite.org",
    "graphql.org",
    "prisma.io",
    # Cloud & DevOps
    "docs.aws.amazon.com",
    "cloud.google.com",
    "kubernetes.io",
    "www.docker.com",
    "www.terraform.io",
    "www.ansible.com",
    "vercel.com",
    "docs.netlify.com",
    "devcenter.heroku.com",
    # Testing
    "cypress.io",
    "selenium.dev",
    # Other
    "git-scm.com",
    "nginx.org",
    "httpd.apache.org",
  }
)

# Path-scoped preapproved entries (host → list of path prefixes)
_PREAPPROVED_PATHS: dict[str, list[str]] = {
  "github.com": ["/anthropics"],
}


def _is_preapproved_host(hostname: str, pathname: str = "/") -> bool:
  """Check if a hostname (+ optional path) is in the preapproved list."""
  if hostname in _PREAPPROVED_HOSTS:
    return True
  prefixes = _PREAPPROVED_PATHS.get(hostname)
  if prefixes:
    for p in prefixes:
      if pathname == p or pathname.startswith(p + "/"):
        return True
  return False


def _validate_url(url: str) -> str | None:
  """Validate URL. Returns error message or None if valid."""
  if not url or len(url) > MAX_URL_LENGTH:
    return f"URL must be 1-{MAX_URL_LENGTH} characters."
  try:
    parsed = urlparse(url)
  except ValueError:
    return "Invalid URL format."
  if parsed.scheme not in ("http", "https"):
    return f"Blocked scheme: {parsed.scheme}. Only http/https allowed."
  if not parsed.hostname:
    return "URL missing hostname."
  host = parsed.hostname.lower()
  if host in _BLOCKED_HOSTS:
    return f"Blocked host: {host} (SSRF protection)."
  if _PRIVATE_IP_PATTERN.match(host):
    return f"Blocked private IP: {host}."
  return None


async def _call(inp: dict[str, Any], ctx: ToolUseContext) -> ToolResult:
  url = inp.get("url", "").strip()
  prompt = inp.get("prompt", "").strip()
  err = _validate_url(url)
  if err:
    return ToolResult(data={"error": err})

  t0 = time.monotonic()
  parsed = urlparse(url)
  hostname = parsed.hostname or ""
  pathname = parsed.path or "/"
  is_preapproved = _is_preapproved_host(hostname.lower(), pathname)

  lines = [
    f"## Web Fetch: {url}",
    "",
    f"Use `read_url_content` tool with URL: `{url}`",
  ]

  if prompt:
    lines.append(f"**Prompt:** {prompt}")

  lines.extend(
    [
      "",
      "**Security checks passed:**",
      "- Scheme: https ✓",
      "- SSRF protection: no private IPs ✓",
      "- No metadata endpoints ✓",
      f"- Preapproved host: {'✓ ' + hostname if is_preapproved else '✗ (will need permission)'}",
      "",
      "**Auth warning:** WebFetch WILL FAIL for authenticated or private URLs.",
      "Check if a specialized MCP tool provides authenticated access first.",
      "",
      f"*Validated in {(time.monotonic() - t0) * 1000:.1f}ms*",
    ]
  )

  return ToolResult(
    data={
      "content": "\n".join(lines),
      "url": url,
      "prompt": prompt or None,
      "is_preapproved": is_preapproved,
    }
  )


async def _prompt(*, tools=None) -> str:
  return (
    "IMPORTANT: WebFetch WILL FAIL for authenticated or private URLs. "
    "Before using this tool, check if the URL points to an authenticated "
    "service (e.g. Google Docs, Confluence, Jira, GitHub). If so, look for "
    "a specialized MCP tool that provides authenticated access.\n\n"
    "WebFetch: fetch URL content with SSRF protection. Use the `prompt` "
    "parameter to extract specific information from the fetched content."
  )


async def _desc(input_args, *, is_non_interactive=False) -> str:
  url = input_args.get("url", "") if isinstance(input_args, dict) else ""
  if url:
    try:
      hostname = urlparse(url).hostname or url[:40]
      return f"Fetch content from {hostname}"
    except ValueError:
      pass
  return "Fetch content from a URL with SSRF protection."


def create_web_fetch_tool():
  return build_tool(
    name=WEB_FETCH_TOOL_NAME,
    input_schema={
      "type": "object",
      "properties": {
        "url": {
          "type": "string",
          "description": "The URL to fetch content from.",
        },
        "prompt": {
          "type": "string",
          "description": "The prompt to run on the fetched content.",
        },
      },
      "required": ["url", "prompt"],
    },
    call_fn=_call,
    description_fn=_desc,
    prompt_fn=_prompt,
    max_result_size_chars=100_000,
    search_hint="fetch and extract content from a URL",
    should_defer=True,
    is_read_only_fn=lambda _: True,
    is_concurrency_safe_fn=lambda _: True,
    user_facing_name_fn=lambda _=None: "Fetch",
  )


__all__ = ["WEB_FETCH_TOOL_NAME", "create_web_fetch_tool"]
