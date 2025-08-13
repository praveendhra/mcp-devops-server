"""MCP Resource: Cluster status dashboard."""
import json
import subprocess


def get_cluster_status() -> dict:
    """Get comprehensive Kubernetes cluster status as an MCP resource."""
    status = {
        "cluster_info": _get_cluster_info(),
        "node_status": _get_node_status(),
        "namespace_summary": _get_namespace_summary(),
        "resource_usage": _get_resource_usage(),
        "recent_events": _get_recent_events()
    }
    return status


def _get_cluster_info() -> dict:
    cmd = ["kubectl", "cluster-info"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {"connected": result.returncode == 0, "info": result.stdout[:500]}


def _get_node_status() -> dict:
    cmd = ["kubectl", "get", "nodes", "-o", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": "Cannot get nodes"}

    nodes = json.loads(result.stdout).get("items", [])
    return {"nodes": [{
        "name": n["metadata"]["name"],
        "status": next(
            (c["type"] for c in n["status"]["conditions"] if c["status"] == "True"),
            "Unknown"
        ),
        "version": n["status"]["nodeInfo"]["kubeletVersion"],
        "os": n["status"]["nodeInfo"]["osImage"],
        "cpu": n["status"]["capacity"].get("cpu"),
        "memory": n["status"]["capacity"].get("memory")
    } for n in nodes]}


def _get_namespace_summary() -> dict:
    cmd = ["kubectl", "get", "pods", "--all-namespaces", "-o", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {}

    pods = json.loads(result.stdout).get("items", [])
    ns_counts = {}
    for p in pods:
        ns = p["metadata"]["namespace"]
        phase = p["status"]["phase"]
        if ns not in ns_counts:
            ns_counts[ns] = {"Running": 0, "Pending": 0, "Failed": 0, "Other": 0}
        if phase in ns_counts[ns]:
            ns_counts[ns][phase] += 1
        else:
            ns_counts[ns]["Other"] += 1

    return ns_counts


def _get_resource_usage() -> dict:
    cmd = ["kubectl", "top", "nodes", "--no-headers"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"available": False}
    return {"available": True, "output": result.stdout}


def _get_recent_events() -> list:
    cmd = ["kubectl", "get", "events", "--all-namespaces",
           "--sort-by=.lastTimestamp", "-o", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []

    events = json.loads(result.stdout).get("items", [])
    return [{
        "namespace": e["metadata"]["namespace"],
        "type": e.get("type"),
        "reason": e.get("reason"),
        "message": e.get("message", "")[:100],
        "count": e.get("count", 1)
    } for e in events[-20:] if e.get("type") != "Normal"]
