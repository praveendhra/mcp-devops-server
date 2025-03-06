# MCP DevOps Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that exposes DevOps tools and workflows to AI assistants like GitHub Copilot and Claude.

## Features

- **Kubernetes**: Get pod status, logs, describe resources, scale deployments
- **Docker**: List containers, images, inspect, build, and manage containers
- **AWS**: Describe EC2 instances, S3 operations, CloudWatch logs, ECS status
- **Terraform**: Plan, validate, show state, list workspaces
- **CI/CD**: Trigger GitHub Actions workflows, get run status, view logs
- **Monitoring**: Query Prometheus metrics, check alerting rules

## Installation

```bash
pip install -e .
```

## Usage

### As an MCP Server (stdio)

```bash
python -m mcp_devops_server
```

### VS Code Integration

Add to your `.vscode/settings.json`:

```json
{
  "github.copilot.chat.mcpServers": {
    "devops": {
      "command": "python",
      "args": ["-m", "mcp_devops_server"],
      "env": {
        "KUBECONFIG": "~/.kube/config"
      }
    }
  }
}
```

## Architecture

```
mcp_devops_server/
├── __main__.py       # Entry point
├── server.py         # MCP server setup and tool registration
├── tools/
│   ├── kubernetes.py # K8s operations via kubectl
│   ├── docker.py     # Docker operations
│   ├── aws.py        # AWS CLI wrapper
│   ├── terraform.py  # Terraform operations
│   ├── github.py     # GitHub Actions API
│   └── monitoring.py # Prometheus queries
└── utils/
    ├── runner.py      # Subprocess runner with timeout
    └── formatter.py   # Output formatting helpers
```

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## License

MIT
