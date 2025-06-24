"""Monitoring tools for MCP server.

Query Prometheus metrics and alerting status.
"""

import json
import logging

import httpx

from ..utils.formatter import format_table

logger = logging.getLogger(__name__)

DEFAULT_PROMETHEUS_URL = "http://localhost:9090"


async def query_prometheus(
    query: str,
    prometheus_url: str = DEFAULT_PROMETHEUS_URL,
) -> str:
    """Execute a PromQL query against Prometheus.

    Args:
        query: PromQL query string
        prometheus_url: Prometheus server URL
    """
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            response = await client.get(
                f"{prometheus_url}/api/v1/query",
                params={"query": query},
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            return f"Error querying Prometheus: {e}"

    data = response.json()
    if data.get("status") != "success":
        return f"Query failed: {data.get('error', 'Unknown error')}"

    results = data.get("data", {}).get("result", [])
    if not results:
        return "No results found."

    headers = ["METRIC", "VALUE"]
    rows = []
    for result in results:
        metric = result.get("metric", {})
        label_str = ", ".join(f'{k}="{v}"' for k, v in metric.items() if k != "__name__")
        name = metric.get("__name__", "")
        if label_str:
            name = f"{name}{{{label_str}}}" if name else label_str

        value = result.get("value", [None, ""])[1]
        rows.append([name[:60], str(value)])

    return format_table(headers, rows)


async def get_alerts(
    prometheus_url: str = DEFAULT_PROMETHEUS_URL,
    state: str | None = None,
) -> str:
    """Get current Prometheus alerts.

    Args:
        prometheus_url: Prometheus server URL
        state: Filter by state (firing, pending, inactive)
    """
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            response = await client.get(f"{prometheus_url}/api/v1/alerts")
            response.raise_for_status()
        except httpx.HTTPError as e:
            return f"Error querying Prometheus: {e}"

    data = response.json()
    alerts = data.get("data", {}).get("alerts", [])

    if state:
        alerts = [a for a in alerts if a.get("state") == state]

    if not alerts:
        return "No active alerts."

    headers = ["ALERT", "STATE", "SEVERITY", "SUMMARY"]
    rows = []
    for alert in alerts:
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})
        rows.append([
            labels.get("alertname", ""),
            alert.get("state", ""),
            labels.get("severity", ""),
            annotations.get("summary", "")[:50],
        ])

    return format_table(headers, rows)


async def get_targets(
    prometheus_url: str = DEFAULT_PROMETHEUS_URL,
) -> str:
    """Get Prometheus scrape target status.

    Args:
        prometheus_url: Prometheus server URL
    """
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            response = await client.get(f"{prometheus_url}/api/v1/targets")
            response.raise_for_status()
        except httpx.HTTPError as e:
            return f"Error querying Prometheus: {e}"

    data = response.json()
    targets = data.get("data", {}).get("activeTargets", [])

    headers = ["JOB", "ENDPOINT", "STATE", "LAST SCRAPE"]
    rows = []
    for target in targets:
        rows.append([
            target["labels"].get("job", ""),
            target.get("scrapeUrl", "")[:40],
            target.get("health", ""),
            target.get("lastScrape", "")[:19],
        ])

    return format_table(headers, rows)
