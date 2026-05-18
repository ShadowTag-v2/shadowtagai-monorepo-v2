# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""CourtListener API integration for Citation Validator.

Queries the CourtListener REST API to verify case citations
against the largest open-access legal database.

API docs: https://www.courtlistener.com/api/rest/v4/
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

COURTLISTENER_BASE = "https://www.courtlistener.com/api/rest/v4"
DEFAULT_TIMEOUT = 10.0


@dataclass
class CourtListenerResult:
  """Result from a CourtListener API lookup.

  Attributes:
      found: Whether a matching case was found.
      case_name: Full case name from CourtListener.
      citation_string: Canonical citation string.
      court: Court that issued the opinion.
      date_filed: Date the opinion was filed.
      status: Current status (e.g., "Published", "Unpublished").
      absolute_url: Direct URL to the opinion on CourtListener.
      error: Error message if the lookup failed.
  """

  found: bool = False
  case_name: str = ""
  citation_string: str = ""
  court: str = ""
  date_filed: str = ""
  status: str = ""
  absolute_url: str = ""
  error: str = ""


async def search_citation(
  volume: str,
  reporter: str,
  page: str,
  *,
  api_token: str | None = None,
  timeout: float = DEFAULT_TIMEOUT,
) -> CourtListenerResult:
  """Search CourtListener for a specific case citation.

  Args:
      volume: Volume number (e.g., "556").
      reporter: Reporter abbreviation (e.g., "U.S.").
      page: Starting page (e.g., "662").
      api_token: Optional CourtListener API token for higher rate limits.
      timeout: HTTP request timeout in seconds.

  Returns:
      CourtListenerResult with case details or error.
  """
  headers = {"Accept": "application/json"}
  if api_token:
    headers["Authorization"] = f"Token {api_token}"

  params = {
    "cite": f"{volume} {reporter} {page}",
  }

  try:
    async with httpx.AsyncClient(timeout=timeout) as client:
      response = await client.get(
        f"{COURTLISTENER_BASE}/search/",
        params=params,
        headers=headers,
      )

      if response.status_code == 429:
        return CourtListenerResult(
          error="Rate limited by CourtListener. Retry after cooldown.",
        )

      if response.status_code != 200:
        return CourtListenerResult(
          error=f"CourtListener API returned {response.status_code}",
        )

      data = response.json()
      results = data.get("results", [])

      if not results:
        return CourtListenerResult(
          found=False,
          error=f"No results for {volume} {reporter} {page}",
        )

      # Take the first (best) match
      hit = results[0]
      return CourtListenerResult(
        found=True,
        case_name=hit.get("caseName", ""),
        citation_string=hit.get("citation", [f"{volume} {reporter} {page}"])[0]
        if isinstance(hit.get("citation"), list)
        else str(hit.get("citation", "")),
        court=hit.get("court", ""),
        date_filed=hit.get("dateFiled", ""),
        status=hit.get("status", ""),
        absolute_url=f"https://www.courtlistener.com{hit.get('absolute_url', '')}",
      )

  except httpx.TimeoutException:
    return CourtListenerResult(error="CourtListener API timed out")
  except httpx.ConnectError:
    return CourtListenerResult(error="Could not connect to CourtListener API")
  except Exception as exc:
    logger.exception("CourtListener lookup failed")
    return CourtListenerResult(error=str(exc))


async def verify_case_exists(
  case_name: str,
  *,
  api_token: str | None = None,
  timeout: float = DEFAULT_TIMEOUT,
) -> CourtListenerResult:
  """Verify a case exists by name search.

  Args:
      case_name: Case name to search (e.g., "Ashcroft v. Iqbal").
      api_token: Optional API token.
      timeout: HTTP timeout.

  Returns:
      CourtListenerResult with match details.
  """
  headers = {"Accept": "application/json"}
  if api_token:
    headers["Authorization"] = f"Token {api_token}"

  params = {"q": case_name, "type": "o"}  # o = opinions

  try:
    async with httpx.AsyncClient(timeout=timeout) as client:
      response = await client.get(
        f"{COURTLISTENER_BASE}/search/",
        params=params,
        headers=headers,
      )

      if response.status_code != 200:
        return CourtListenerResult(
          error=f"CourtListener API returned {response.status_code}",
        )

      data = response.json()
      results = data.get("results", [])

      if not results:
        return CourtListenerResult(
          found=False,
          error=f"No results for '{case_name}'",
        )

      hit = results[0]
      return CourtListenerResult(
        found=True,
        case_name=hit.get("caseName", case_name),
        court=hit.get("court", ""),
        date_filed=hit.get("dateFiled", ""),
        absolute_url=f"https://www.courtlistener.com{hit.get('absolute_url', '')}",
      )

  except httpx.TimeoutException:
    return CourtListenerResult(error="CourtListener API timed out")
  except Exception as exc:
    logger.exception("CourtListener name search failed")
    return CourtListenerResult(error=str(exc))
