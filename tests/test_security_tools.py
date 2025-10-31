"""Tests for security scanning tools."""
import pytest
from unittest.mock import patch, MagicMock
from src.tools.security_tools import trivy_scan_image, check_k8s_security


@patch("subprocess.run")
def test_trivy_scan_clean_image(mock_run):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout='{"Results": [{"Vulnerabilities": []}]}'
    )
    result = trivy_scan_image("python:3.12-slim")
    assert result["total_vulnerabilities"] == 0


@patch("subprocess.run")
def test_trivy_scan_with_vulns(mock_run):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout='{"Results": [{"Vulnerabilities": [{"VulnerabilityID": "CVE-2024-1234", "Severity": "HIGH", "PkgName": "openssl", "InstalledVersion": "3.0.1", "FixedVersion": "3.0.2"}]}]}'
    )
    result = trivy_scan_image("nginx:latest")
    assert result["total_vulnerabilities"] == 1
    assert result["vulnerabilities"][0]["id"] == "CVE-2024-1234"


@patch("subprocess.run")
def test_k8s_security_check(mock_run):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout='{"items": [{"metadata": {"name": "test-pod"}, "spec": {"containers": [{"securityContext": {"runAsUser": 0}}]}, "status": {}}]}'
    )
    result = check_k8s_security("default")
    assert result["total_issues"] > 0
