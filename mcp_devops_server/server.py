"""MCP Server setup and tool registration."""

import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .tools import kubernetes, docker, aws, terraform, github, monitoring

logger = logging.getLogger(__name__)

# Tool registry mapping tool names to their handlers
TOOLS = {
    # Kubernetes
    "k8s_get_pods": {
        "description": "Get pod status in a Kubernetes namespace",
        "handler": kubernetes.get_pods,
        "params": {
            "namespace": {"type": "string", "description": "Kubernetes namespace", "default": "default"},
            "label_selector": {"type": "string", "description": "Label selector (e.g. app=myapp)"},
            "all_namespaces": {"type": "boolean", "description": "List across all namespaces", "default": False},
        },
    },
    "k8s_get_logs": {
        "description": "Get logs from a Kubernetes pod",
        "handler": kubernetes.get_pod_logs,
        "params": {
            "pod_name": {"type": "string", "description": "Pod name", "required": True},
            "namespace": {"type": "string", "description": "Namespace", "default": "default"},
            "container": {"type": "string", "description": "Container name"},
            "tail_lines": {"type": "integer", "description": "Lines to tail", "default": 50},
            "previous": {"type": "boolean", "description": "Previous container", "default": False},
        },
    },
    "k8s_describe": {
        "description": "Describe a Kubernetes resource",
        "handler": kubernetes.describe_resource,
        "params": {
            "resource_type": {"type": "string", "description": "Resource type", "required": True},
            "name": {"type": "string", "description": "Resource name", "required": True},
            "namespace": {"type": "string", "description": "Namespace", "default": "default"},
        },
    },
    "k8s_scale": {
        "description": "Scale a Kubernetes deployment",
        "handler": kubernetes.scale_deployment,
        "params": {
            "deployment": {"type": "string", "description": "Deployment name", "required": True},
            "replicas": {"type": "integer", "description": "Desired replicas", "required": True},
            "namespace": {"type": "string", "description": "Namespace", "default": "default"},
        },
    },
    "k8s_events": {
        "description": "Get recent Kubernetes events",
        "handler": kubernetes.get_events,
        "params": {
            "namespace": {"type": "string", "description": "Namespace", "default": "default"},
            "resource_type": {"type": "string", "description": "Filter by resource type"},
        },
    },
    "k8s_top": {
        "description": "Get pod resource usage (CPU/memory)",
        "handler": kubernetes.get_resource_usage,
        "params": {
            "namespace": {"type": "string", "description": "Namespace", "default": "default"},
        },
    },
    # Docker
    "docker_containers": {
        "description": "List Docker containers",
        "handler": docker.list_containers,
        "params": {
            "all_containers": {"type": "boolean", "description": "Include stopped", "default": False},
        },
    },
    "docker_images": {
        "description": "List Docker images",
        "handler": docker.list_images,
        "params": {
            "dangling": {"type": "boolean", "description": "Show dangling only", "default": False},
        },
    },
    "docker_inspect": {
        "description": "Inspect a Docker container",
        "handler": docker.inspect_container,
        "params": {
            "container_id": {"type": "string", "description": "Container ID/name", "required": True},
        },
    },
    "docker_logs": {
        "description": "Get Docker container logs",
        "handler": docker.container_logs,
        "params": {
            "container_id": {"type": "string", "description": "Container ID/name", "required": True},
            "tail": {"type": "integer", "description": "Lines to show", "default": 50},
            "since": {"type": "string", "description": "Show since (e.g. 1h)"},
        },
    },
    "docker_compose_status": {
        "description": "Get Docker Compose service status",
        "handler": docker.docker_compose_status,
        "params": {
            "project_dir": {"type": "string", "description": "Project directory", "default": "."},
        },
    },
    # AWS
    "aws_ec2_list": {
        "description": "List EC2 instances",
        "handler": aws.list_ec2_instances,
        "params": {
            "region": {"type": "string", "description": "AWS region", "default": "us-east-1"},
            "state": {"type": "string", "description": "Filter by state"},
        },
    },
    "aws_s3_buckets": {
        "description": "List S3 buckets",
        "handler": aws.list_s3_buckets,
        "params": {},
    },
    "aws_ecs_services": {
        "description": "Get ECS service status",
        "handler": aws.get_ecs_services,
        "params": {
            "cluster": {"type": "string", "description": "ECS cluster name", "required": True},
            "region": {"type": "string", "description": "AWS region", "default": "us-east-1"},
        },
    },
    "aws_logs": {
        "description": "Get CloudWatch log events",
        "handler": aws.get_cloudwatch_logs,
        "params": {
            "log_group": {"type": "string", "description": "Log group name", "required": True},
            "minutes": {"type": "integer", "description": "Minutes to look back", "default": 30},
            "filter_pattern": {"type": "string", "description": "Filter pattern"},
            "region": {"type": "string", "description": "AWS region", "default": "us-east-1"},
        },
    },
    # Terraform
    "tf_plan": {
        "description": "Run terraform plan",
        "handler": terraform.terraform_plan,
        "params": {
            "working_dir": {"type": "string", "description": "Terraform directory", "required": True},
            "var_file": {"type": "string", "description": "Var file path"},
            "target": {"type": "string", "description": "Resource target"},
        },
    },
    "tf_validate": {
        "description": "Validate Terraform configuration",
        "handler": terraform.terraform_validate,
        "params": {
            "working_dir": {"type": "string", "description": "Terraform directory", "required": True},
        },
    },
    "tf_state": {
        "description": "List resources in Terraform state",
        "handler": terraform.terraform_state_list,
        "params": {
            "working_dir": {"type": "string", "description": "Terraform directory", "required": True},
        },
    },
    "tf_output": {
        "description": "Get Terraform outputs",
        "handler": terraform.terraform_output,
        "params": {
            "working_dir": {"type": "string", "description": "Terraform directory", "required": True},
            "output_name": {"type": "string", "description": "Specific output name"},
        },
    },
    # GitHub
    "gh_workflow_runs": {
        "description": "List GitHub Actions workflow runs",
        "handler": github.list_workflow_runs,
        "params": {
            "repo": {"type": "string", "description": "owner/repo", "required": True},
            "workflow": {"type": "string", "description": "Workflow file name"},
            "status": {"type": "string", "description": "Filter by status"},
            "limit": {"type": "integer", "description": "Number of runs", "default": 10},
        },
    },
    "gh_run_logs": {
        "description": "Get workflow run logs",
        "handler": github.get_workflow_run_logs,
        "params": {
            "repo": {"type": "string", "description": "owner/repo", "required": True},
            "run_id": {"type": "integer", "description": "Run ID", "required": True},
        },
    },
    "gh_trigger_workflow": {
        "description": "Trigger a GitHub Actions workflow",
        "handler": github.trigger_workflow,
        "params": {
            "repo": {"type": "string", "description": "owner/repo", "required": True},
            "workflow": {"type": "string", "description": "Workflow file", "required": True},
            "ref": {"type": "string", "description": "Branch/tag", "default": "main"},
        },
    },
    "gh_prs": {
        "description": "List open pull requests",
        "handler": github.list_open_prs,
        "params": {
            "repo": {"type": "string", "description": "owner/repo", "required": True},
            "limit": {"type": "integer", "description": "Number of PRs", "default": 10},
        },
    },
    # Monitoring
    "prom_query": {
        "description": "Execute a PromQL query",
        "handler": monitoring.query_prometheus,
        "params": {
            "query": {"type": "string", "description": "PromQL query", "required": True},
            "prometheus_url": {"type": "string", "description": "Prometheus URL", "default": "http://localhost:9090"},
        },
    },
    "prom_alerts": {
        "description": "Get active Prometheus alerts",
        "handler": monitoring.get_alerts,
        "params": {
            "prometheus_url": {"type": "string", "description": "Prometheus URL", "default": "http://localhost:9090"},
            "state": {"type": "string", "description": "Filter by state"},
        },
    },
    "prom_targets": {
        "description": "Get Prometheus scrape targets",
        "handler": monitoring.get_targets,
        "params": {
            "prometheus_url": {"type": "string", "description": "Prometheus URL", "default": "http://localhost:9090"},
        },
    },
}


def build_tool_schema(name: str, info: dict) -> Tool:
    """Build MCP Tool schema from tool info."""
    properties = {}
    required = []
    for param_name, param_info in info.get("params", {}).items():
        properties[param_name] = {
            "type": param_info["type"],
            "description": param_info.get("description", ""),
        }
        if param_info.get("required"):
            required.append(param_name)

    return Tool(
        name=name,
        description=info["description"],
        inputSchema={
            "type": "object",
            "properties": properties,
            "required": required,
        },
    )


def create_server() -> Server:
    """Create and configure the MCP server."""
    server = Server("devops-mcp-server")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [build_tool_schema(name, info) for name, info in TOOLS.items()]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name not in TOOLS:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        handler = TOOLS[name]["handler"]
        params = TOOLS[name].get("params", {})

        # Apply defaults for missing args
        kwargs = {}
        for param_name, param_info in params.items():
            if param_name in arguments:
                kwargs[param_name] = arguments[param_name]
            elif "default" in param_info:
                kwargs[param_name] = param_info["default"]

        try:
            result = await handler(**kwargs)
            return [TextContent(type="text", text=result)]
        except Exception as e:
            logger.exception("Error executing tool %s", name)
            return [TextContent(type="text", text=f"Error: {e}")]

    return server


async def run_server():
    """Run the MCP server over stdio."""
    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
