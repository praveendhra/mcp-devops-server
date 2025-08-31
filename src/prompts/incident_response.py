"""Incident response prompts for MCP server."""


def incident_investigation_prompt(service: str, symptoms: str) -> str:
    """Generate a structured incident investigation prompt."""
    return f"""Investigate the following incident:

## Service: {service}
## Symptoms: {symptoms}

### Investigation Steps:
1. **Check service health**: Use the k8s_pod_health tool for namespace '{service}'
2. **Review recent deployments**: Check deployment status and recent rollouts
3. **Analyze logs**: Use analyze_error_logs for pods in the service
4. **Check resource usage**: Review CPU/memory with k8s resource tools
5. **Review recent events**: Look for warning/error events in the namespace
6. **Check external dependencies**: Test endpoints and DNS resolution
7. **Review metrics**: Check Prometheus/Grafana for anomalies

### Escalation Criteria:
- Data loss or corruption → SEV-1, page on-call immediately
- Complete outage → SEV-1, start incident bridge
- Partial degradation > 30 min → SEV-2, notify engineering lead
- Minor impact → SEV-3, create ticket

### Response Template:
- **Impact**: [Who/what is affected]
- **Root Cause**: [Identified/investigating]
- **Mitigation**: [Actions taken]
- **Resolution ETA**: [Estimated time]
"""


def deployment_checklist_prompt(service: str, environment: str) -> str:
    """Generate a deployment checklist prompt."""
    return f"""Deployment Checklist for {service} to {environment}:

### Pre-Deployment:
- [ ] All tests passing in CI
- [ ] Code review approved
- [ ] Security scan clean (Trivy, tfsec)
- [ ] Database migrations tested
- [ ] Feature flags configured
- [ ] Runbook updated
- [ ] Monitoring alerts configured

### Deployment:
- [ ] Deploy to staging first
- [ ] Run smoke tests on staging
- [ ] Check error rates on staging
- [ ] Deploy to production (canary)
- [ ] Monitor canary metrics (5 min)
- [ ] Progressive rollout (25% → 50% → 100%)
- [ ] Verify health checks passing

### Post-Deployment:
- [ ] Verify all health endpoints
- [ ] Check error rates in monitoring
- [ ] Verify key user flows
- [ ] Update deployment log
- [ ] Notify stakeholders
"""
