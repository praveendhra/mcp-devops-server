"""GCP-specific DevOps tools for MCP server."""
import json
import subprocess


def gcloud_gke_list(project: str = "") -> dict:
    """List GKE clusters."""
    cmd = ["gcloud", "container", "clusters", "list", "--format=json"]
    if project:
        cmd.extend(["--project", project])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}

    clusters = json.loads(result.stdout or "[]")
    return {"clusters": [{
        "name": c["name"],
        "location": c.get("location"),
        "status": c["status"],
        "node_count": c.get("currentNodeCount", 0),
        "k8s_version": c.get("currentMasterVersion"),
        "autopilot": c.get("autopilot", {}).get("enabled", False)
    } for c in clusters]}


def gcloud_run_list(project: str = "", region: str = "") -> dict:
    """List Cloud Run services."""
    cmd = ["gcloud", "run", "services", "list", "--format=json"]
    if project:
        cmd.extend(["--project", project])
    if region:
        cmd.extend(["--region", region])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}

    services = json.loads(result.stdout or "[]")
    return {"services": [{
        "name": s["metadata"]["name"],
        "url": s.get("status", {}).get("url"),
        "ready": any(
            c.get("type") == "Ready" and c.get("status") == "True"
            for c in s.get("status", {}).get("conditions", [])
        ),
        "last_deployed": s.get("metadata", {}).get("creationTimestamp")
    } for s in services]}


def gcloud_logs(service: str, project: str = "", limit: int = 50,
                severity: str = "ERROR") -> dict:
    """Query GCP Cloud Logging."""
    filter_str = f'resource.type="cloud_run_revision" AND resource.labels.service_name="{service}"'
    if severity:
        filter_str += f' AND severity>={severity}'

    cmd = [
        "gcloud", "logging", "read", filter_str,
        f"--limit={limit}", "--format=json"
    ]
    if project:
        cmd.extend(["--project", project])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}

    entries = json.loads(result.stdout or "[]")
    return {"service": service, "log_entries": [{
        "timestamp": e.get("timestamp"),
        "severity": e.get("severity"),
        "message": e.get("textPayload", e.get("jsonPayload", {}).get("message", ""))[:200]
    } for e in entries]}
