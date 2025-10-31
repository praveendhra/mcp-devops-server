"""Tests for Helm tools."""
import pytest
from unittest.mock import patch, MagicMock
from src.tools.helm_tools import helm_list, helm_status, helm_history


@patch("subprocess.run")
def test_helm_list(mock_run):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout='[{"name": "myapp", "namespace": "default", "status": "deployed"}]'
    )
    result = helm_list()
    assert len(result["releases"]) == 1
    assert result["releases"][0]["name"] == "myapp"


@patch("subprocess.run")
def test_helm_list_all_namespaces(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="[]")
    result = helm_list(all_namespaces=True)
    assert "-A" in mock_run.call_args[0][0]
    assert result["releases"] == []


@patch("subprocess.run")
def test_helm_status_not_found(mock_run):
    mock_run.return_value = MagicMock(returncode=1, stderr="Error: release not found")
    result = helm_status("nonexistent")
    assert "error" in result


@patch("subprocess.run")
def test_helm_history(mock_run):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout='[{"revision": 1, "status": "deployed"}, {"revision": 2, "status": "deployed"}]'
    )
    result = helm_history("myapp")
    assert len(result["history"]) == 2
