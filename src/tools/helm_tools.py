"""Helm chart management tools for MCP server."""
import json
import subprocess
from typing import Optional


def helm_list(namespace: str = "", all_namespaces: bool = False) -> dict:
    """List Helm releases."""
    cmd = ["helm", "list", "-o", "json"]
    if all_namespaces:
        cmd.append("-A")
    elif namespace:
        cmd.extend(["-n", namespace])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}
    return {"releases": json.loads(result.stdout or "[]")}


def helm_status(release: str, namespace: str = "default") -> dict:
    """Get status of a Helm release."""
    cmd = ["helm", "status", release, "-n", namespace, "-o", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}
    return json.loads(result.stdout)


def helm_history(release: str, namespace: str = "default") -> dict:
    """Get revision history of a Helm release."""
    cmd = ["helm", "history", release, "-n", namespace, "-o", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}
    return {"history": json.loads(result.stdout or "[]")}


def helm_values(release: str, namespace: str = "default", all_values: bool = False) -> dict:
    """Get values of a Helm release."""
    cmd = ["helm", "get", "values", release, "-n", namespace, "-o", "json"]
    if all_values:
        cmd.append("-a")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}
    return json.loads(result.stdout or "{}")


def helm_template(chart_path: str, release_name: str = "test",
                  values_file: Optional[str] = None) -> dict:
    """Render Helm templates locally without installing."""
    cmd = ["helm", "template", release_name, chart_path]
    if values_file:
        cmd.extend(["-f", values_file])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}
    return {"rendered": result.stdout}
