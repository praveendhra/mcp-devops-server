# MCP DevOps Server Architecture

## Overview

```
┌─────────────┐     ┌──────────────────────────────────────┐
│  VS Code /  │     │         MCP DevOps Server            │
│  Claude /   │────▶│                                      │
│  Any MCP    │     │  ┌──────────┐  ┌──────────────────┐  │
│  Client     │◀────│  │  Server  │  │  Tool Registry   │  │
└─────────────┘     │  │  (MCP)   │──│                  │  │
                    │  └──────────┘  │  ┌─────────────┐ │  │
                    │                │  │ K8s Tools    │ │  │
                    │  ┌──────────┐  │  │ Helm Tools   │ │  │
                    │  │ Config   │  │  │ ArgoCD Tools │ │  │
                    │  │ Manager  │  │  │ AWS Tools    │ │  │
                    │  └──────────┘  │  │ Azure Tools  │ │  │
                    │                │  │ GCP Tools    │ │  │
                    │  ┌──────────┐  │  │ Security     │ │  │
                    │  │ Resources│  │  │ Cost         │ │  │
                    │  │ Provider │  │  │ DNS/Network  │ │  │
                    │  └──────────┘  │  │ Git          │ │  │
                    │                │  │ Logs         │ │  │
                    │  ┌──────────┐  │  └─────────────┘ │  │
                    │  │ Prompts  │  └──────────────────┘  │
                    │  └──────────┘                        │
                    └──────────────────────────────────────┘
```

## Components

### Server Layer
- MCP protocol implementation (stdin/stdout or HTTP+SSE)
- Tool/resource/prompt registration
- Request routing and response formatting

### Tool Registry
- Dynamic tool registration
- Category-based organization
- Requirement checking (binary dependencies)
- Feature flag support

### Configuration
- Environment variable based
- Sensible defaults for all settings
- Per-cloud-provider configuration
- Feature flags for optional tools

### Resources
- Cluster status dashboard
- Deployment health monitoring
- Real-time pod status

### Prompts
- Incident response templates
- Deployment checklists
- Troubleshooting guides

## Tool Categories

1. **Kubernetes**: Core cluster operations
2. **Helm**: Chart management
3. **ArgoCD**: GitOps operations
4. **Cloud Providers**: AWS, Azure, GCP specific
5. **Security**: Vulnerability scanning, posture assessment
6. **Cost**: Cloud spend analysis
7. **Observability**: Logs, DNS, endpoint health
8. **Git**: Repository analysis
