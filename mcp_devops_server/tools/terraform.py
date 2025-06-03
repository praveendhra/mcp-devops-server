"""Terraform tools for MCP server.

Provides tools to manage Terraform state and workspaces.
"""

import json
import logging

from ..utils.runner import run_command
from ..utils.formatter import format_table, format_json

logger = logging.getLogger(__name__)


async def terraform_plan(
    working_dir: str,
    var_file: str | None = None,
    target: str | None = None,
) -> str:
    """Run terraform plan and return the output.

    Args:
        working_dir: Directory containing Terraform configuration
        var_file: Path to tfvars file
        target: Specific resource to target
    """
    cmd = ["terraform", "plan", "-no-color", "-input=false"]
    if var_file:
        cmd.extend([f"-var-file={var_file}"])
    if target:
        cmd.extend([f"-target={target}"])

    result = await run_command(cmd, timeout=120, cwd=working_dir)
    return result.to_text()


async def terraform_validate(working_dir: str) -> str:
    """Validate Terraform configuration.

    Args:
        working_dir: Directory containing Terraform configuration
    """
    cmd = ["terraform", "validate", "-json"]
    result = await run_command(cmd, timeout=30, cwd=working_dir)

    if result.success:
        data = json.loads(result.stdout)
        if data.get("valid"):
            return "Configuration is valid."
        diagnostics = data.get("diagnostics", [])
        errors = [d for d in diagnostics if d["severity"] == "error"]
        if errors:
            return "\n".join(
                f"Error: {e['summary']}\n  {e.get('detail', '')}"
                for e in errors
            )
    return result.to_text()


async def terraform_state_list(working_dir: str) -> str:
    """List resources in Terraform state.

    Args:
        working_dir: Directory containing Terraform configuration
    """
    cmd = ["terraform", "state", "list"]
    result = await run_command(cmd, timeout=15, cwd=working_dir)
    return result.to_text()


async def terraform_show_resource(
    working_dir: str,
    resource_address: str,
) -> str:
    """Show details of a specific resource in state.

    Args:
        working_dir: Directory containing Terraform configuration
        resource_address: Resource address (e.g. aws_instance.main)
    """
    cmd = ["terraform", "state", "show", resource_address]
    result = await run_command(cmd, timeout=15, cwd=working_dir)
    return result.to_text()


async def terraform_workspace_list(working_dir: str) -> str:
    """List Terraform workspaces.

    Args:
        working_dir: Directory containing Terraform configuration
    """
    cmd = ["terraform", "workspace", "list"]
    result = await run_command(cmd, timeout=10, cwd=working_dir)
    return result.to_text()


async def terraform_output(
    working_dir: str,
    output_name: str | None = None,
) -> str:
    """Get Terraform outputs.

    Args:
        working_dir: Directory containing Terraform configuration
        output_name: Specific output name (optional)
    """
    cmd = ["terraform", "output", "-json"]
    if output_name:
        cmd.append(output_name)

    result = await run_command(cmd, timeout=15, cwd=working_dir)
    if not result.success:
        return result.to_text()

    data = json.loads(result.stdout)
    return format_json(data)
