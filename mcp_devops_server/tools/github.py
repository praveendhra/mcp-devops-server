"""GitHub Actions tools for MCP server.

Uses GitHub CLI (gh) for workflow operations.
"""

import json
import logging

from ..utils.runner import run_command
from ..utils.formatter import format_table

logger = logging.getLogger(__name__)


async def list_workflow_runs(
    repo: str,
    workflow: str | None = None,
    status: str | None = None,
    limit: int = 10,
) -> str:
    """List recent GitHub Actions workflow runs.

    Args:
        repo: Repository in owner/repo format
        workflow: Workflow file name (e.g. ci.yml)
        status: Filter by status (success, failure, in_progress)
        limit: Number of runs to show
    """
    cmd = ["gh", "run", "list", "--repo", repo, f"--limit={limit}", "--json",
           "databaseId,displayTitle,status,conclusion,createdAt,headBranch"]
    if workflow:
        cmd.extend(["--workflow", workflow])
    if status:
        cmd.extend(["--status", status])

    result = await run_command(cmd, timeout=15)
    if not result.success:
        return result.to_text()

    runs = json.loads(result.stdout)
    headers = ["ID", "TITLE", "STATUS", "BRANCH", "CREATED"]
    rows = []
    for run in runs:
        conclusion = run.get("conclusion") or run.get("status", "")
        rows.append([
            str(run["databaseId"]),
            run["displayTitle"][:40],
            conclusion,
            run.get("headBranch", ""),
            run.get("createdAt", "")[:16],
        ])

    return format_table(headers, rows)


async def get_workflow_run_logs(
    repo: str,
    run_id: int,
) -> str:
    """Get logs for a specific workflow run.

    Args:
        repo: Repository in owner/repo format
        run_id: Workflow run ID
    """
    cmd = ["gh", "run", "view", str(run_id), "--repo", repo, "--log"]
    result = await run_command(cmd, timeout=30)
    return result.to_text()


async def trigger_workflow(
    repo: str,
    workflow: str,
    ref: str = "main",
    inputs: dict[str, str] | None = None,
) -> str:
    """Trigger a workflow dispatch event.

    Args:
        repo: Repository in owner/repo format
        workflow: Workflow file name
        ref: Branch or tag to run on
        inputs: Workflow inputs as key-value pairs
    """
    cmd = ["gh", "workflow", "run", workflow, "--repo", repo, "--ref", ref]
    if inputs:
        for key, value in inputs.items():
            cmd.extend(["-f", f"{key}={value}"])

    result = await run_command(cmd, timeout=15)
    if result.success:
        return f"Workflow '{workflow}' triggered on branch '{ref}'."
    return result.to_text()


async def list_open_prs(
    repo: str,
    limit: int = 10,
) -> str:
    """List open pull requests.

    Args:
        repo: Repository in owner/repo format
        limit: Number of PRs to show
    """
    cmd = ["gh", "pr", "list", "--repo", repo, f"--limit={limit}", "--json",
           "number,title,author,headRefName,createdAt,reviewDecision"]

    result = await run_command(cmd, timeout=15)
    if not result.success:
        return result.to_text()

    prs = json.loads(result.stdout)
    headers = ["#", "TITLE", "AUTHOR", "BRANCH", "REVIEW"]
    rows = []
    for pr in prs:
        rows.append([
            str(pr["number"]),
            pr["title"][:40],
            pr["author"].get("login", ""),
            pr["headRefName"][:25],
            pr.get("reviewDecision", "PENDING"),
        ])

    return format_table(headers, rows)
