# MCP DevOps Server - Tool Reference

## Kubernetes Tools
| Tool | Description |
|------|------------|
| `k8s_get_pods` | List pods in a namespace |
| `k8s_pod_logs` | Get pod logs |
| `k8s_pod_health` | Check pod health status |
| `k8s_deploy_status` | Get deployment status |
| `k8s_events` | Get recent events |
| `k8s_exec` | Execute command in pod |
| `k8s_troubleshoot` | Auto-diagnose common issues |

## Helm Tools
| Tool | Description |
|------|------------|
| `helm_list` | List Helm releases |
| `helm_status` | Get release status |
| `helm_history` | Get release history |
| `helm_values` | Get release values |
| `helm_template` | Render templates locally |

## ArgoCD Tools
| Tool | Description |
|------|------------|
| `argocd_list_apps` | List applications |
| `argocd_get_app` | Get app details |
| `argocd_sync` | Sync application |
| `argocd_diff` | Show live vs desired diff |

## AWS Tools
| Tool | Description |
|------|------------|
| `aws_ec2_list` | List EC2 instances |
| `aws_ecs_services` | List ECS services |
| `aws_s3_list` | List S3 buckets |
| `aws_cost_by_service` | Cost breakdown by service |
| `aws_cost_forecast` | Cost forecast |

## Azure Tools
| Tool | Description |
|------|------------|
| `az_aks_list` | List AKS clusters |
| `az_webapp_list` | List Web Apps |
| `az_acr_list_repos` | List ACR repositories |
| `az_keyvault_list_secrets` | List Key Vault secrets |

## GCP Tools
| Tool | Description |
|------|------------|
| `gcloud_gke_list` | List GKE clusters |
| `gcloud_run_list` | List Cloud Run services |
| `gcloud_logs` | Query Cloud Logging |

## Security Tools
| Tool | Description |
|------|------------|
| `trivy_scan_image` | Scan container image for CVEs |
| `trivy_scan_filesystem` | Scan repo for vulnerabilities |
| `check_k8s_security` | Audit K8s security posture |

## DNS & Network Tools
| Tool | Description |
|------|------------|
| `dns_lookup` | DNS record lookup |
| `check_ssl_certificate` | SSL cert inspection |
| `check_endpoints` | Multi-endpoint health check |

## Git Tools
| Tool | Description |
|------|------------|
| `git_repo_stats` | Repository statistics |
| `git_changed_files` | Recently changed files |
| `git_search_commits` | Search commit history |

## Log Analysis
| Tool | Description |
|------|------------|
| `analyze_error_logs` | Error pattern detection |
| `multi_pod_logs` | Aggregate logs from pods |
