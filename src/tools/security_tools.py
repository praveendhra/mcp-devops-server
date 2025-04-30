"""Security scanning tools for MCP server."""
import json
import subprocess
from typing import Optional


def trivy_scan_image(image: str, severity: str = "CRITICAL,HIGH") -> dict:
    """Scan a container image for vulnerabilities using Trivy."""
    cmd = [
        "trivy", "image", image,
        "--format", "json",
        "--severity", severity,
        "--quiet"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 and not result.stdout:
        return {"error": result.stderr}

    data = json.loads(result.stdout) if result.stdout else {}
    results = data.get("Results", [])

    vulnerabilities = []
    for r in results:
        for vuln in r.get("Vulnerabilities", []):
            vulnerabilities.append({
                "id": vuln.get("VulnerabilityID"),
                "severity": vuln.get("Severity"),
                "package": vuln.get("PkgName"),
                "installed": vuln.get("InstalledVersion"),
                "fixed": vuln.get("FixedVersion"),
                "title": vuln.get("Title", "")[:80]
            })

    return {
        "image": image,
        "total_vulnerabilities": len(vulnerabilities),
        "vulnerabilities": vulnerabilities[:50]
    }


def trivy_scan_filesystem(path: str, severity: str = "CRITICAL,HIGH") -> dict:
    """Scan a filesystem/repo for vulnerabilities and misconfigurations."""
    cmd = [
        "trivy", "fs", path,
        "--format", "json",
        "--severity", severity,
        "--quiet"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 and not result.stdout:
        return {"error": result.stderr}

    data = json.loads(result.stdout) if result.stdout else {}
    return {
        "path": path,
        "results": len(data.get("Results", [])),
        "summary": [
            {"target": r.get("Target"), "vulns": len(r.get("Vulnerabilities", []))}
            for r in data.get("Results", [])
        ]
    }


def check_k8s_security(namespace: str = "default") -> dict:
    """Check Kubernetes security posture for a namespace."""
    issues = []

    # Check for pods running as root
    cmd = ["kubectl", "get", "pods", "-n", namespace, "-o", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        pods = json.loads(result.stdout).get("items", [])
        for pod in pods:
            name = pod["metadata"]["name"]
            for container in pod["spec"].get("containers", []):
                sc = container.get("securityContext", {})
                if sc.get("runAsUser") == 0 or (not sc.get("runAsNonRoot") and not pod["spec"].get("securityContext", {}).get("runAsNonRoot")):
                    issues.append({"pod": name, "issue": "may run as root", "severity": "HIGH"})
                if not sc.get("readOnlyRootFilesystem"):
                    issues.append({"pod": name, "issue": "writable root filesystem", "severity": "MEDIUM"})
                if sc.get("privileged"):
                    issues.append({"pod": name, "issue": "privileged container", "severity": "CRITICAL"})

    return {"namespace": namespace, "total_issues": len(issues), "issues": issues[:30]}
