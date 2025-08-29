"""MCP Resource: Deployment health and status."""
import json
import subprocess


def get_deployment_status(namespace: str = "default") -> dict:
    """Get deployment status for a namespace."""
    cmd = ["kubectl", "get", "deployments", "-n", namespace, "-o", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}

    deployments = json.loads(result.stdout).get("items", [])
    return {
        "namespace": namespace,
        "deployments": [{
            "name": d["metadata"]["name"],
            "replicas": d["spec"].get("replicas", 0),
            "ready": d["status"].get("readyReplicas", 0),
            "available": d["status"].get("availableReplicas", 0),
            "updated": d["status"].get("updatedReplicas", 0),
            "strategy": d["spec"].get("strategy", {}).get("type"),
            "image": d["spec"]["template"]["spec"]["containers"][0].get("image", ""),
            "conditions": [{
                "type": c["type"],
                "status": c["status"],
                "reason": c.get("reason")
            } for c in d["status"].get("conditions", [])]
        } for d in deployments]
    }


def get_pod_health(namespace: str = "default") -> dict:
    """Get detailed pod health for a namespace."""
    cmd = ["kubectl", "get", "pods", "-n", namespace, "-o", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}

    pods = json.loads(result.stdout).get("items", [])
    unhealthy = []
    for p in pods:
        phase = p["status"]["phase"]
        if phase not in ("Running", "Succeeded"):
            unhealthy.append({
                "name": p["metadata"]["name"],
                "phase": phase,
                "reason": p["status"].get("reason"),
                "restarts": sum(
                    cs.get("restartCount", 0)
                    for cs in p["status"].get("containerStatuses", [])
                )
            })

    running = len([p for p in pods if p["status"]["phase"] == "Running"])
    return {
        "namespace": namespace,
        "total_pods": len(pods),
        "running": running,
        "unhealthy_count": len(unhealthy),
        "unhealthy_pods": unhealthy
    }
