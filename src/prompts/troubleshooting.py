"""Troubleshooting prompts for MCP server."""


def pod_crash_loop_prompt(pod: str, namespace: str) -> str:
    """Guide troubleshooting a CrashLoopBackOff pod."""
    return f"""Troubleshoot CrashLoopBackOff for pod '{pod}' in namespace '{namespace}':

### Diagnostic Steps:
1. Get pod description: `kubectl describe pod {pod} -n {namespace}`
2. Check current logs: `kubectl logs {pod} -n {namespace}`
3. Check previous crash logs: `kubectl logs {pod} -n {namespace} --previous`
4. Check events: `kubectl get events -n {namespace} --field-selector involvedObject.name={pod}`

### Common Causes:
1. **Application error**: Check logs for stack traces or startup errors
2. **Missing config/secrets**: Check if ConfigMaps/Secrets exist and are mounted
3. **Resource limits**: OOMKilled → increase memory limits
4. **Health check failure**: Liveness probe failing too aggressively
5. **Image issues**: Wrong tag, pull errors, missing entrypoint
6. **Dependency unavailable**: Database, cache, or API not reachable

### Resolution Actions:
- Fix application code and redeploy
- Update resource limits in deployment
- Adjust health check timing (initialDelaySeconds, periodSeconds)
- Fix ConfigMap/Secret references
- Rollback: `kubectl rollout undo deployment/<name> -n {namespace}`
"""


def high_cpu_prompt(namespace: str) -> str:
    """Guide troubleshooting high CPU usage."""
    return f"""Investigate high CPU usage in namespace '{namespace}':

### Steps:
1. Check pod CPU usage: `kubectl top pods -n {namespace} --sort-by=cpu`
2. Check node CPU: `kubectl top nodes`
3. Check HPA status: `kubectl get hpa -n {namespace}`
4. Review recent deployments for changes
5. Check for CPU-intensive operations (background jobs, queries)

### Quick Fixes:
- Scale up: `kubectl scale deployment/<name> --replicas=<N>`
- Adjust HPA: Lower target CPU utilization
- Check for infinite loops or runaway processes
- Review database queries for full table scans
"""


def network_issue_prompt(source_ns: str, target_service: str) -> str:
    """Guide troubleshooting network connectivity issues."""
    return f"""Troubleshoot network connectivity from '{source_ns}' to '{target_service}':

### DNS Resolution:
1. `kubectl exec -it <pod> -n {source_ns} -- nslookup {target_service}`
2. Check service exists: `kubectl get svc {target_service}`
3. Check endpoints: `kubectl get endpoints {target_service}`

### Network Policies:
1. `kubectl get networkpolicies -n {source_ns}`
2. Check if traffic is allowed between namespaces
3. Verify port numbers match

### Service Mesh:
1. Check sidecar injection
2. Review Istio/Linkerd traffic policies
3. Check mTLS configuration
"""
