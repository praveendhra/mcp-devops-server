"""Log analysis tools for MCP server."""
import json
import subprocess
import re
from collections import Counter
from typing import Optional


def k8s_pod_logs(pod: str, namespace: str = "default", tail: int = 100,
                 container: Optional[str] = None, previous: bool = False) -> dict:
    """Get logs from a Kubernetes pod."""
    cmd = ["kubectl", "logs", pod, "-n", namespace, f"--tail={tail}"]
    if container:
        cmd.extend(["-c", container])
    if previous:
        cmd.append("--previous")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}

    lines = result.stdout.strip().split("\n")
    return {"pod": pod, "namespace": namespace, "line_count": len(lines), "logs": lines}


def analyze_error_logs(pod: str, namespace: str = "default", tail: int = 500) -> dict:
    """Analyze pod logs for errors and patterns."""
    cmd = ["kubectl", "logs", pod, "-n", namespace, f"--tail={tail}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}

    lines = result.stdout.strip().split("\n")
    error_patterns = re.compile(r"(error|exception|fatal|panic|traceback|failed)", re.IGNORECASE)
    warn_patterns = re.compile(r"(warn|warning|deprecated)", re.IGNORECASE)

    errors = [l for l in lines if error_patterns.search(l)]
    warnings = [l for l in lines if warn_patterns.search(l)]

    # Count error types
    error_types = Counter()
    for line in errors:
        match = re.search(r"(\w*[Ee]rror\w*|\w*[Ee]xception\w*)", line)
        if match:
            error_types[match.group()] += 1

    return {
        "pod": pod,
        "total_lines": len(lines),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "error_types": dict(error_types.most_common(10)),
        "recent_errors": errors[-10:],
        "recent_warnings": warnings[-5:]
    }


def multi_pod_logs(namespace: str, label_selector: str, tail: int = 50,
                   search: Optional[str] = None) -> dict:
    """Get logs from multiple pods matching a label selector."""
    cmd = ["kubectl", "get", "pods", "-n", namespace, "-l", label_selector,
           "-o", "jsonpath={.items[*].metadata.name}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}

    pods = result.stdout.strip().split()
    all_logs = {}
    for pod in pods:
        log_cmd = ["kubectl", "logs", pod, "-n", namespace, f"--tail={tail}"]
        log_result = subprocess.run(log_cmd, capture_output=True, text=True)
        if log_result.returncode == 0:
            lines = log_result.stdout.strip().split("\n")
            if search:
                lines = [l for l in lines if search.lower() in l.lower()]
            all_logs[pod] = lines

    return {"namespace": namespace, "selector": label_selector, "pod_logs": all_logs}
