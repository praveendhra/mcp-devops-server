"""Subprocess runner with timeout and error handling."""

import asyncio
import logging
import shlex
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """Result of a command execution."""
    stdout: str
    stderr: str
    return_code: int

    @property
    def success(self) -> bool:
        return self.return_code == 0

    def to_text(self) -> str:
        if self.success:
            return self.stdout.strip()
        return f"Error (exit code {self.return_code}):\n{self.stderr.strip()}"


async def run_command(
    command: str | list[str],
    timeout: int = 30,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
) -> CommandResult:
    """Run a shell command asynchronously with timeout.

    Args:
        command: Command string or list of args
        timeout: Timeout in seconds
        cwd: Working directory
        env: Additional environment variables

    Returns:
        CommandResult with stdout, stderr, and return code
    """
    if isinstance(command, str):
        args = shlex.split(command)
    else:
        args = command

    logger.info("Running command: %s", " ".join(args))

    try:
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            env=env,
        )
        stdout, stderr = await asyncio.wait_for(
            process.communicate(), timeout=timeout
        )
        return CommandResult(
            stdout=stdout.decode("utf-8", errors="replace"),
            stderr=stderr.decode("utf-8", errors="replace"),
            return_code=process.returncode or 0,
        )
    except asyncio.TimeoutError:
        process.kill()
        return CommandResult(stdout="", stderr=f"Command timed out after {timeout}s", return_code=-1)
    except FileNotFoundError:
        return CommandResult(stdout="", stderr=f"Command not found: {args[0]}", return_code=-1)
