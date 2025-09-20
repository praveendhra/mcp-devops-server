"""Test fixtures and configuration."""

import pytest


@pytest.fixture
def mock_command_result():
    """Factory for creating mock CommandResult objects."""
    from mcp_devops_server.utils.runner import CommandResult

    def _create(stdout: str = "", stderr: str = "", return_code: int = 0):
        return CommandResult(stdout=stdout, stderr=stderr, return_code=return_code)

    return _create
