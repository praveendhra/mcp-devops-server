"""AWS tools for MCP server.

Wraps AWS CLI commands for common operations.
"""

import json
import logging

from ..utils.runner import run_command
from ..utils.formatter import format_table, format_json

logger = logging.getLogger(__name__)


async def list_ec2_instances(
    region: str = "us-east-1",
    state: str | None = None,
) -> str:
    """List EC2 instances with their status.

    Args:
        region: AWS region
        state: Filter by state (running, stopped, etc.)
    """
    cmd = [
        "aws", "ec2", "describe-instances",
        "--region", region,
        "--output", "json",
    ]
    if state:
        cmd.extend(["--filters", f"Name=instance-state-name,Values={state}"])

    result = await run_command(cmd, timeout=20)
    if not result.success:
        return result.to_text()

    data = json.loads(result.stdout)
    headers = ["INSTANCE ID", "TYPE", "STATE", "PRIVATE IP", "NAME"]
    rows = []

    for reservation in data.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            name = ""
            for tag in instance.get("Tags", []):
                if tag["Key"] == "Name":
                    name = tag["Value"]
                    break
            rows.append([
                instance["InstanceId"],
                instance["InstanceType"],
                instance["State"]["Name"],
                instance.get("PrivateIpAddress", ""),
                name,
            ])

    return format_table(headers, rows)


async def list_s3_buckets() -> str:
    """List all S3 buckets."""
    cmd = ["aws", "s3api", "list-buckets", "--output", "json"]
    result = await run_command(cmd, timeout=15)
    if not result.success:
        return result.to_text()

    data = json.loads(result.stdout)
    headers = ["BUCKET NAME", "CREATED"]
    rows = []
    for bucket in data.get("Buckets", []):
        rows.append([bucket["Name"], bucket["CreationDate"][:10]])

    return format_table(headers, rows)


async def get_ecs_services(
    cluster: str,
    region: str = "us-east-1",
) -> str:
    """Get ECS service status.

    Args:
        cluster: ECS cluster name
        region: AWS region
    """
    # First list services
    list_cmd = [
        "aws", "ecs", "list-services",
        "--cluster", cluster,
        "--region", region,
        "--output", "json",
    ]
    list_result = await run_command(list_cmd, timeout=15)
    if not list_result.success:
        return list_result.to_text()

    service_arns = json.loads(list_result.stdout).get("serviceArns", [])
    if not service_arns:
        return f"No services found in cluster '{cluster}'."

    # Describe services
    desc_cmd = [
        "aws", "ecs", "describe-services",
        "--cluster", cluster,
        "--services", *service_arns,
        "--region", region,
        "--output", "json",
    ]
    desc_result = await run_command(desc_cmd, timeout=15)
    if not desc_result.success:
        return desc_result.to_text()

    services = json.loads(desc_result.stdout).get("services", [])
    headers = ["SERVICE", "STATUS", "DESIRED", "RUNNING", "PENDING"]
    rows = []
    for svc in services:
        rows.append([
            svc["serviceName"],
            svc["status"],
            str(svc["desiredCount"]),
            str(svc["runningCount"]),
            str(svc["pendingCount"]),
        ])

    return format_table(headers, rows)


async def get_cloudwatch_logs(
    log_group: str,
    minutes: int = 30,
    filter_pattern: str | None = None,
    region: str = "us-east-1",
) -> str:
    """Get recent CloudWatch log events.

    Args:
        log_group: CloudWatch log group name
        minutes: Number of minutes to look back
        filter_pattern: CloudWatch filter pattern
        region: AWS region
    """
    import time
    start_time = str(int((time.time() - minutes * 60) * 1000))

    cmd = [
        "aws", "logs", "filter-log-events",
        "--log-group-name", log_group,
        "--start-time", start_time,
        "--region", region,
        "--output", "json",
        "--limit", "50",
    ]
    if filter_pattern:
        cmd.extend(["--filter-pattern", filter_pattern])

    result = await run_command(cmd, timeout=20)
    if not result.success:
        return result.to_text()

    events = json.loads(result.stdout).get("events", [])
    if not events:
        return f"No log events found in the last {minutes} minutes."

    lines = []
    for event in events:
        ts = event.get("timestamp", 0)
        msg = event.get("message", "").strip()
        lines.append(f"[{ts}] {msg}")

    return "\n".join(lines[-50:])
