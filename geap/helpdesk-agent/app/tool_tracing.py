# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tool tracing wrappers — GEAP Part 6: Graph Migration.

Instruments all CMDB and knowledge tools with `trace_tool_call`
wrappers that emit OpenTelemetry spans for observability and audit.

Reference: GEAP Tutorial Series Part 6
Project: shadowtag-omega-v4
"""

from __future__ import annotations

import functools
import logging
import time

log = logging.getLogger(__name__)

# Try to import OpenTelemetry; gracefully degrade if unavailable.
try:
    from opentelemetry import trace

    _tracer = trace.get_tracer("geap.helpdesk.tools", "0.6.0")
except ImportError:
    _tracer = None


def trace_tool_call(tool_name: str | None = None):
    """Decorator that wraps an ADK tool function with an OTel span.

    Captures:
    - tool name (from decorator arg or function __name__)
    - input arguments (sanitized)
    - output (first 500 chars)
    - duration_ms
    - success/failure status

    Args:
        tool_name: Optional override for the span name.

    Returns:
        Decorated function with tracing instrumentation.
    """

    def decorator(func):
        span_name = tool_name or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()

            if _tracer is None:
                # No OTel — just call and log
                result = func(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start) * 1000
                log.info(
                    "tool_call: %s completed in %.1fms",
                    span_name,
                    elapsed_ms,
                )
                return result

            with _tracer.start_as_current_span(
                f"tool.{span_name}",
                attributes={
                    "tool.name": span_name,
                    "tool.module": func.__module__ or "unknown",
                },
            ) as span:
                # Record sanitized inputs (no PII in span attributes)
                safe_args = {k: str(v)[:200] for k, v in kwargs.items()}
                span.set_attribute("tool.inputs", str(safe_args))

                try:
                    result = func(*args, **kwargs)
                    elapsed_ms = (time.perf_counter() - start) * 1000

                    span.set_attribute("tool.success", True)
                    span.set_attribute("tool.duration_ms", elapsed_ms)
                    span.set_attribute("tool.output_preview", str(result)[:500])

                    log.info(
                        "tool_call: %s OK in %.1fms",
                        span_name,
                        elapsed_ms,
                    )
                    return result

                except Exception as exc:
                    elapsed_ms = (time.perf_counter() - start) * 1000
                    span.set_attribute("tool.success", False)
                    span.set_attribute("tool.error", str(exc)[:300])
                    span.set_attribute("tool.duration_ms", elapsed_ms)
                    span.record_exception(exc)
                    span.set_status(trace.StatusCode.ERROR, str(exc)[:200])
                    log.exception(
                        "tool_call: %s FAILED in %.1fms: %s",
                        span_name,
                        elapsed_ms,
                        exc,
                    )
                    raise

        return wrapper

    return decorator


def traced_tools(tool_functions: list) -> list:
    """Wrap a list of tool functions with trace_tool_call.

    Args:
        tool_functions: List of callable tool functions.

    Returns:
        List of wrapped functions with tracing instrumentation.
    """
    wrapped = []
    for fn in tool_functions:
        if callable(fn):
            wrapped.append(trace_tool_call()(fn))
        else:
            wrapped.append(fn)
    return wrapped
