"""Tests for log analysis tools."""
import pytest
from unittest.mock import patch, MagicMock
from src.tools.log_tools import k8s_pod_logs, analyze_error_logs


@patch("subprocess.run")
def test_k8s_pod_logs(mock_run):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="2025-01-01 INFO Starting app\n2025-01-01 INFO Ready"
    )
    result = k8s_pod_logs("myapp-abc123")
    assert result["line_count"] == 2
    assert result["pod"] == "myapp-abc123"


@patch("subprocess.run")
def test_analyze_error_logs(mock_run):
    logs = "\n".join([
        "2025-01-01 INFO Starting",
        "2025-01-01 ERROR ConnectionError: timeout",
        "2025-01-01 WARN deprecated API",
        "2025-01-01 ERROR NullPointerException",
        "2025-01-01 INFO Processed 100 items",
        "2025-01-01 ERROR ConnectionError: refused",
    ])
    mock_run.return_value = MagicMock(returncode=0, stdout=logs)
    result = analyze_error_logs("myapp-abc123")
    assert result["error_count"] == 3
    assert result["warning_count"] == 1
    assert "ConnectionError" in result["error_types"]


@patch("subprocess.run")
def test_pod_logs_not_found(mock_run):
    mock_run.return_value = MagicMock(returncode=1, stderr="pod not found")
    result = k8s_pod_logs("nonexistent")
    assert "error" in result
