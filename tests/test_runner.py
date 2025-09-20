"""Tests for the subprocess runner utility."""

import pytest
from mcp_devops_server.utils.runner import run_command, CommandResult


class TestCommandResult:
    def test_success(self):
        result = CommandResult(stdout="output", stderr="", return_code=0)
        assert result.success is True
        assert result.to_text() == "output"

    def test_failure(self):
        result = CommandResult(stdout="", stderr="error msg", return_code=1)
        assert result.success is False
        assert "error msg" in result.to_text()
        assert "exit code 1" in result.to_text()


class TestRunCommand:
    @pytest.mark.asyncio
    async def test_successful_command(self):
        result = await run_command("echo hello")
        assert result.success
        assert result.stdout.strip() == "hello"

    @pytest.mark.asyncio
    async def test_failed_command(self):
        result = await run_command("false")
        assert not result.success

    @pytest.mark.asyncio
    async def test_command_not_found(self):
        result = await run_command("nonexistent_command_xyz")
        assert not result.success
        assert "not found" in result.stderr.lower()

    @pytest.mark.asyncio
    async def test_timeout(self):
        result = await run_command("sleep 10", timeout=1)
        assert not result.success
        assert "timed out" in result.stderr.lower()

    @pytest.mark.asyncio
    async def test_command_list(self):
        result = await run_command(["echo", "hello world"])
        assert result.success
        assert "hello world" in result.stdout
