# MCP DevOps Server

A Model Context Protocol (MCP) server that provides AI assistants with DevOps tools for Kubernetes, cloud providers, CI/CD, security scanning, and infrastructure management.

## Features

- **Kubernetes**: Pod management, deployments, logs, troubleshooting
- **Helm**: Chart management, release history, template rendering
- **ArgoCD**: Application sync, diff, and status monitoring
- **AWS**: EC2, ECS, S3, Cost Explorer, Secrets Manager
- **Azure**: AKS, WebApps, ACR, Key Vault
- **GCP**: GKE, Cloud Run, Cloud Logging
- **Security**: Trivy scanning, K8s security audit
- **Observability**: Log analysis, DNS lookup, SSL checks, endpoint monitoring
- **Git**: Repository stats, change tracking, commit search
- **Cost**: Cloud spend analysis and forecasting

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python -m src.server

# Or with Docker
docker build -t mcp-devops-server .
docker run -v ~/.kube:/home/mcp/.kube:ro mcp-devops-server
```

## VS Code Integration

Add to `.vscode/settings.json`:
```json
{
  "mcp": {
    "servers": {
      "devops": {
        "command": "python",
        "args": ["-m", "src.server"],
        "cwd": "${workspaceFolder}",
        "env": {
          "KUBECONFIG": "${env:HOME}/.kube/config",
          "AWS_PROFILE": "default"
        }
      }
    }
  }
}
```

## Configuration

| Variable | Default | Description |
|----------|---------|------------|
| `MCP_HOST` | localhost | Server host |
| `MCP_PORT` | 8080 | Server port |
| `MCP_DEBUG` | false | Enable debug mode |
| `MCP_LOG_LEVEL` | INFO | Logging level |
| `MCP_DEFAULT_NAMESPACE` | default | K8s namespace |
| `AWS_PROFILE` | default | AWS profile |
| `GCP_PROJECT` | - | GCP project ID |

## Documentation

- [Tool Reference](docs/TOOLS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Contributing](docs/CONTRIBUTING.md)

## Testing

```bash
pip install -r requirements-dev.txt
pytest tests/ -v --cov=src
```
