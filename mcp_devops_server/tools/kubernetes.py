"""Kubernetes tools for MCP server.

Provides tools to interact with Kubernetes clusters via kubectl.
"""

import json
import logging

from ..utils.runner import run_command
from ..utils.formatter import format_table, truncate_output

logger = logging.getLogger(__name__)


async def get_pods(
    namespace: str = "default",
    label_selector: str | None = None,
    all_namespaces: bool = False,
) -> str:
    """Get pod status in a namespace.

    Args:
        namespace: Kubernetes namespace (default: "default")
        label_selector: Filter pods by label (e.g. "app=myapp")
        all_namespaces: List pods across all namespaces
    """
    cmd = ["kubectl", "get", "pods", "-o", "json"]
    if all_namespaces:
        cmd.append("--all-namespaces")
    else:
        cmd.extend(["-n", namespace])
    if label_selector:
        cmd.extend(["-l", label_selector])

    result = await run_command(cmd, timeout=15)
    if not result.success:
        return result.to_text()

    data = json.loads(result.stdout)
    items = data.get("items", [])

    if not items:
        return f"No pods found in namespace '{namespace}'."

    headers = ["NAME", "READY", "STATUS", "RESTARTS", "AGE"]
    rows = []
    for pod in items:
        name = pod["metadata"]["name"]
        status = pod["status"].get("phase", "Unknown")
        containers = pod["spec"].get("containers", [])
        container_statuses = pod["status"].get("containerStatuses", [])

        ready_count = sum(1 for cs in container_statuses if cs.get("ready", False))
        total = len(containers)
        restarts = sum(cs.get("restartCount", 0) for cs in container_statuses)

        rows.append([name, f"{ready_count}/{total}", status, str(restarts), ""])

    return format_table(headers, rows)


async def get_pod_logs(
    pod_name: str,
    namespace: str = "default",
    container: str | None = None,
    tail_lines: int = 50,
    previous: bool = False,
) -> str:
    """Get logs from a pod.

    Args:
        pod_name: Name of the pod
        namespace: Kubernetes namespace
        container: Specific container name (for multi-container pods)
        tail_lines: Number of lines to tail (default: 50)
        previous: Get logs from previous container instance
    """
    cmd = ["kubectl", "logs", pod_name, "-n", namespace, f"--tail={tail_lines}"]
    if container:
        cmd.extend(["-c", container])
    if previous:
        cmd.append("--previous")

    result = await run_command(cmd, timeout=15)
    return truncate_output(result.to_text())


async def describe_resource(
    resource_type: str,
    name: str,
    namespace: str = "default",
) -> str:
    """Describe a Kubernetes resource.

    Args:
        resource_type: Type of resource (pod, deployment, service, etc.)
        name: Name of the resource
        namespace: Kubernetes namespace
    """
    cmd = ["kubectl", "describe", resource_type, name, "-n", namespace]
    result = await run_command(cmd, timeout=15)
    return truncate_output(result.to_text())


async def scale_deployment(
    deployment: str,
    replicas: int,
    namespace: str = "default",
) -> str:
    """Scale a deployment to a specified number of replicas.

    Args:
        deployment: Name of the deployment
        replicas: Desired number of replicas
        namespace: Kubernetes namespace
    """
    if replicas < 0 or replicas > 100:
        return "Error: Replicas must be between 0 and 100."

    cmd = ["kubectl", "scale", f"deployment/{deployment}",
           f"--replicas={replicas}", "-n", namespace]
    result = await run_command(cmd, timeout=15)
    return result.to_text()


async def get_events(
    namespace: str = "default",
    resource_type: str | None = None,
) -> str:
    """Get recent events in a namespace.

    Args:
        namespace: Kubernetes namespace
        resource_type: Filter by resource type (optional)
    """
    cmd = ["kubectl", "get", "events", "-n", namespace,
           "--sort-by=.lastTimestamp", "-o", "json"]
    if resource_type:
        cmd.extend(["--field-selector", f"involvedObject.kind={resource_type}"])

    result = await run_command(cmd, timeout=15)
    if not result.success:
        return result.to_text()

    data = json.loads(result.stdout)
    items = data.get("items", [])[-20:]  # Last 20 events

    headers = ["TYPE", "REASON", "OBJECT", "MESSAGE"]
    rows = []
    for event in items:
        rows.append([
            event.get("type", ""),
            event.get("reason", ""),
            f"{event['involvedObject'].get('kind', '')}/{event['involvedObject'].get('name', '')}",
            event.get("message", "")[:80],
        ])

    return format_table(headers, rows)


async def get_resource_usage(namespace: str = "default") -> str:
    """Get CPU and memory usage for pods (requires metrics-server).

    Args:
        namespace: Kubernetes namespace
    """
    cmd = ["kubectl", "top", "pods", "-n", namespace, "--no-headers"]
    result = await run_command(cmd, timeout=10)
    if not result.success:
        return f"Error: {result.stderr}\nMake sure metrics-server is installed."
    return result.to_text()
