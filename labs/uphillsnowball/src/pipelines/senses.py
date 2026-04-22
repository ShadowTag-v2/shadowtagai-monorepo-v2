"""Sensor Pipelines — Cloudflare RadarSense & Apache Beam Ingest.

RadarSense: Deterministic L3/L7 internet traffic anomalies from
    Cloudflare Radar API. Crucial for Midas quant risk budgets.
    Generic OSINT provides noise. RadarSense provides signal.

IngestHBR_LangExtract: Massive parallel ingestion of paywalled/gov
    data to the Ice Lake via Apache Beam DoFns. Uses Scrapling
    for anti-bot bypass and adaptive session management.

PrometheusIngestor: Structured metrics ingestion from internal
    services for empirical scoreboards (FPR/FNR, mitigation latency).
"""

from __future__ import annotations

import logging
from typing import Any, Generator

import requests

logger = logging.getLogger("Senses-Pipeline")


class RadarSense:
    """Cloudflare Radar API integration for deterministic threat intelligence.

    Provides L3/L7 internet traffic anomaly detection crucial for
    Midas quantitative risk budgets. This is not generic OSINT —
    this is deterministic, structured threat data.

    Attributes:
        base_url: Cloudflare Radar API endpoint.
        timeout: Request timeout in seconds.
    """

    def __init__(
        self,
        base_url: str = "https://radar.cloudflare.com/api",
        timeout: int = 10,
    ) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def fetch_domain_health(self, domain: str) -> dict:
        """Fetch L3/L7 threat indicators for a domain.

        Args:
            domain: The target domain to analyze.

        Returns:
            Dict with threat indicators and traffic anomalies.
        """
        try:
            resp = requests.get(
                f"{self.base_url}/mcp/threats",
                params={"domain": domain},
                timeout=self.timeout,
            )
            if resp.ok:
                logger.info("📡 RadarSense: Domain health fetched for %s", domain)
                return resp.json()
            logger.warning(
                "⚠️ RadarSense: HTTP %d for domain %s", resp.status_code, domain
            )
            return {"error": f"HTTP {resp.status_code}"}
        except requests.RequestException as e:
            logger.error("❌ RadarSense fetch failed: %s", e)
            return {"error": str(e)}

    def fetch_traffic_anomalies(self, asn: int) -> dict:
        """Fetch traffic anomalies for an Autonomous System Number.

        Args:
            asn: The ASN to analyze.

        Returns:
            Dict with traffic anomaly data.
        """
        try:
            resp = requests.get(
                f"{self.base_url}/traffic/anomalies",
                params={"asn": asn},
                timeout=self.timeout,
            )
            return resp.json() if resp.ok else {"error": f"HTTP {resp.status_code}"}
        except requests.RequestException as e:
            return {"error": str(e)}


class IngestHBR_LangExtract:
    """Apache Beam DoFn for massive parallel data ingestion.

    Ingests paywalled/gov data using Scrapling's StealthyFetcher
    for anti-bot bypass. Output goes to the Ice Lake (LanceDB).

    Note: This is designed to be used as an Apache Beam DoFn.
    The setup() and process() methods follow the Beam lifecycle.
    """

    def __init__(self) -> None:
        self.fetcher: Any = None

    def setup(self) -> None:
        """Initialize the StealthyFetcher on worker startup."""
        try:
            from scrapling import StealthyFetcher
            self.fetcher = StealthyFetcher(adaptive=True)
        except ImportError:
            logger.warning("Scrapling not available. Using requests fallback.")
            self.fetcher = None

    def process(self, url: str) -> Generator[dict, None, None]:
        """Process a single URL for ingestion.

        Args:
            url: The URL to fetch and ingest.

        Yields:
            Structured content dicts for Ice Lake storage.
        """
        try:
            if self.fetcher is not None:
                page = self.fetcher.get(url)
                content = page.text[:10000]
            else:
                resp = requests.get(url, timeout=15)
                content = resp.text[:10000]

            yield {
                "domain": "STRATEGY",
                "source": url,
                "content": content,
                "content_length": len(content),
            }
        except Exception as e:
            logger.warning("Ingest failed for %s: %s", url, e)


class PrometheusIngestor:
    """Structured metrics ingestion for empirical scoreboards.

    Ingests Prometheus metrics for:
        - FPR/FNR (false positive/negative rates)
        - Mitigation latency
        - Null-model rejection rate
        - Egress leak rate
    """

    def __init__(self, prometheus_url: str = "http://localhost:9090") -> None:
        self.base_url = prometheus_url

    def query_metric(self, metric_name: str) -> dict:
        """Query a Prometheus metric.

        Args:
            metric_name: The PromQL metric name.

        Returns:
            Prometheus query result.
        """
        try:
            resp = requests.get(
                f"{self.base_url}/api/v1/query",
                params={"query": metric_name},
                timeout=5,
            )
            return resp.json() if resp.ok else {"error": f"HTTP {resp.status_code}"}
        except requests.RequestException as e:
            return {"error": str(e)}
