"""ArgoCD management tools for MCP server."""
import json
import subprocess


def argocd_list_apps(project: str = "") -> dict:
    """List ArgoCD applications."""
    cmd = ["argocd", "app", "list", "-o", "json"]
    if project:
        cmd.extend(["-p", project])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}
    return {"applications": json.loads(result.stdout or "[]")}


def argocd_get_app(app_name: str) -> dict:
    """Get detailed status of an ArgoCD application."""
    cmd = ["argocd", "app", "get", app_name, "-o", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}

    data = json.loads(result.stdout)
    return {
        "name": data.get("metadata", {}).get("name"),
        "sync_status": data.get("status", {}).get("sync", {}).get("status"),
        "health_status": data.get("status", {}).get("health", {}).get("status"),
        "source": data.get("spec", {}).get("source"),
        "destination": data.get("spec", {}).get("destination"),
        "conditions": data.get("status", {}).get("conditions", []),
    }


def argocd_sync(app_name: str, prune: bool = False, force: bool = False) -> dict:
    """Sync an ArgoCD application."""
    cmd = ["argocd", "app", "sync", app_name]
    if prune:
        cmd.append("--prune")
    if force:
        cmd.append("--force")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}
    return {"message": f"Application {app_name} synced successfully", "output": result.stdout}


def argocd_diff(app_name: str) -> dict:
    """Show diff between live and desired state."""
    cmd = ["argocd", "app", "diff", app_name]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {"diff": result.stdout, "has_diff": result.returncode != 0}
