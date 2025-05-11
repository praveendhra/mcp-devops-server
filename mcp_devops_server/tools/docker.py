"""Docker tools for MCP server.

Provides tools to manage Docker containers, images, and compose stacks.
"""

import json
import logging

from ..utils.runner import run_command
from ..utils.formatter import format_table, format_json

logger = logging.getLogger(__name__)


async def list_containers(all_containers: bool = False) -> str:
    """List Docker containers.

    Args:
        all_containers: Include stopped containers
    """
    cmd = ["docker", "ps", "--format", "json"]
    if all_containers:
        cmd.append("-a")

    result = await run_command(cmd, timeout=10)
    if not result.success:
        return result.to_text()

    containers = []
    for line in result.stdout.strip().split("\n"):
        if line.strip():
            containers.append(json.loads(line))

    if not containers:
        return "No containers found."

    headers = ["ID", "IMAGE", "STATUS", "PORTS", "NAME"]
    rows = []
    for c in containers:
        rows.append([
            c.get("ID", "")[:12],
            c.get("Image", "")[:40],
            c.get("Status", ""),
            c.get("Ports", "")[:30],
            c.get("Names", ""),
        ])

    return format_table(headers, rows)


async def list_images(dangling: bool = False) -> str:
    """List Docker images.

    Args:
        dangling: Show only dangling (untagged) images
    """
    cmd = ["docker", "images", "--format", "json"]
    if dangling:
        cmd.extend(["--filter", "dangling=true"])

    result = await run_command(cmd, timeout=10)
    if not result.success:
        return result.to_text()

    images = []
    for line in result.stdout.strip().split("\n"):
        if line.strip():
            images.append(json.loads(line))

    headers = ["REPOSITORY", "TAG", "SIZE", "CREATED"]
    rows = []
    for img in images:
        rows.append([
            img.get("Repository", ""),
            img.get("Tag", ""),
            img.get("Size", ""),
            img.get("CreatedSince", ""),
        ])

    return format_table(headers, rows)


async def inspect_container(container_id: str) -> str:
    """Inspect a Docker container.

    Args:
        container_id: Container ID or name
    """
    cmd = ["docker", "inspect", container_id]
    result = await run_command(cmd, timeout=10)
    if not result.success:
        return result.to_text()

    data = json.loads(result.stdout)
    if not data:
        return f"Container '{container_id}' not found."

    container = data[0]
    summary = {
        "Name": container.get("Name", "").lstrip("/"),
        "Image": container["Config"].get("Image", ""),
        "Status": container["State"].get("Status", ""),
        "Started": container["State"].get("StartedAt", ""),
        "Platform": container.get("Platform", ""),
        "Ports": container["NetworkSettings"].get("Ports", {}),
        "Mounts": [
            {"Source": m.get("Source", ""), "Destination": m.get("Destination", "")}
            for m in container.get("Mounts", [])
        ],
        "Environment": [
            e for e in container["Config"].get("Env", [])
            if not any(s in e.upper() for s in ["PASSWORD", "SECRET", "TOKEN", "KEY"])
        ],
    }
    return format_json(summary)


async def container_logs(
    container_id: str,
    tail: int = 50,
    since: str | None = None,
) -> str:
    """Get container logs.

    Args:
        container_id: Container ID or name
        tail: Number of lines to show
        since: Show logs since timestamp (e.g. "1h", "2024-01-01")
    """
    cmd = ["docker", "logs", container_id, f"--tail={tail}"]
    if since:
        cmd.extend(["--since", since])

    result = await run_command(cmd, timeout=10)
    return result.to_text()


async def docker_compose_status(project_dir: str = ".") -> str:
    """Get Docker Compose service status.

    Args:
        project_dir: Directory containing docker-compose.yml
    """
    cmd = ["docker", "compose", "ps", "--format", "json"]
    result = await run_command(cmd, timeout=10, cwd=project_dir)
    if not result.success:
        return result.to_text()

    services = []
    for line in result.stdout.strip().split("\n"):
        if line.strip():
            services.append(json.loads(line))

    headers = ["SERVICE", "STATUS", "PORTS"]
    rows = []
    for s in services:
        rows.append([
            s.get("Service", s.get("Name", "")),
            s.get("State", s.get("Status", "")),
            s.get("Publishers", ""),
        ])

    return format_table(headers, rows)
