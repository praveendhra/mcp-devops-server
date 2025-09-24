"""Configuration management for MCP DevOps Server."""
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ServerConfig:
    """Server configuration with environment variable overrides."""

    # Server settings
    host: str = "localhost"
    port: int = 8080
    debug: bool = False
    log_level: str = "INFO"

    # Kubernetes settings
    kubeconfig: Optional[str] = None
    default_namespace: str = "default"
    kubectl_timeout: int = 30

    # Cloud provider settings
    aws_profile: str = "default"
    aws_region: str = "us-east-1"
    azure_subscription: Optional[str] = None
    gcp_project: Optional[str] = None

    # Tool settings
    helm_timeout: int = 300
    terraform_parallelism: int = 10

    # Feature flags
    enable_cost_tools: bool = True
    enable_security_tools: bool = True
    enable_git_tools: bool = True

    @classmethod
    def from_env(cls) -> "ServerConfig":
        """Create config from environment variables."""
        return cls(
            host=os.getenv("MCP_HOST", "localhost"),
            port=int(os.getenv("MCP_PORT", "8080")),
            debug=os.getenv("MCP_DEBUG", "false").lower() == "true",
            log_level=os.getenv("MCP_LOG_LEVEL", "INFO"),
            kubeconfig=os.getenv("KUBECONFIG"),
            default_namespace=os.getenv("MCP_DEFAULT_NAMESPACE", "default"),
            kubectl_timeout=int(os.getenv("MCP_KUBECTL_TIMEOUT", "30")),
            aws_profile=os.getenv("AWS_PROFILE", "default"),
            aws_region=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
            azure_subscription=os.getenv("AZURE_SUBSCRIPTION_ID"),
            gcp_project=os.getenv("GCP_PROJECT"),
            helm_timeout=int(os.getenv("MCP_HELM_TIMEOUT", "300")),
            terraform_parallelism=int(os.getenv("MCP_TF_PARALLELISM", "10")),
            enable_cost_tools=os.getenv("MCP_ENABLE_COST", "true").lower() == "true",
            enable_security_tools=os.getenv("MCP_ENABLE_SECURITY", "true").lower() == "true",
            enable_git_tools=os.getenv("MCP_ENABLE_GIT", "true").lower() == "true",
        )
