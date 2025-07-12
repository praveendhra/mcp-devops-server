"""Azure-specific DevOps tools for MCP server."""
import json
import subprocess


def az_aks_list(resource_group: str = "") -> dict:
    """List AKS clusters."""
    cmd = ["az", "aks", "list", "-o", "json"]
    if resource_group:
        cmd.extend(["-g", resource_group])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}

    clusters = json.loads(result.stdout or "[]")
    return {"clusters": [{
        "name": c["name"],
        "resource_group": c["resourceGroup"],
        "location": c["location"],
        "k8s_version": c["kubernetesVersion"],
        "node_count": sum(p.get("count", 0) for p in c.get("agentPoolProfiles", [])),
        "power_state": c.get("powerState", {}).get("code"),
        "provisioning_state": c["provisioningState"]
    } for c in clusters]}


def az_webapp_list(resource_group: str = "") -> dict:
    """List Azure Web Apps."""
    cmd = ["az", "webapp", "list", "-o", "json"]
    if resource_group:
        cmd.extend(["-g", resource_group])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}

    apps = json.loads(result.stdout or "[]")
    return {"web_apps": [{
        "name": a["name"],
        "resource_group": a["resourceGroup"],
        "state": a["state"],
        "default_hostname": a.get("defaultHostName"),
        "kind": a.get("kind"),
        "https_only": a.get("httpsOnly")
    } for a in apps]}


def az_acr_list_repos(registry_name: str) -> dict:
    """List repositories in an Azure Container Registry."""
    cmd = ["az", "acr", "repository", "list", "--name", registry_name, "-o", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}
    return {"registry": registry_name, "repositories": json.loads(result.stdout or "[]")}


def az_keyvault_list_secrets(vault_name: str) -> dict:
    """List secrets in an Azure Key Vault (names only, not values)."""
    cmd = ["az", "keyvault", "secret", "list", "--vault-name", vault_name, "-o", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}

    secrets = json.loads(result.stdout or "[]")
    return {"vault": vault_name, "secrets": [{
        "name": s.get("name"),
        "enabled": s.get("attributes", {}).get("enabled"),
        "expires": s.get("attributes", {}).get("expires"),
        "content_type": s.get("contentType")
    } for s in secrets]}
