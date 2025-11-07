"""Tests for configuration management."""
import os
import pytest
from src.config import ServerConfig


def test_default_config():
    config = ServerConfig()
    assert config.host == "localhost"
    assert config.port == 8080
    assert config.debug is False
    assert config.default_namespace == "default"


def test_config_from_env():
    env = {
        "MCP_HOST": "0.0.0.0",
        "MCP_PORT": "9090",
        "MCP_DEBUG": "true",
        "MCP_LOG_LEVEL": "DEBUG",
        "MCP_DEFAULT_NAMESPACE": "production",
        "AWS_PROFILE": "prod",
        "GCP_PROJECT": "my-project",
    }
    with pytest.MonkeyPatch.context() as mp:
        for k, v in env.items():
            mp.setenv(k, v)
        config = ServerConfig.from_env()

    assert config.host == "0.0.0.0"
    assert config.port == 9090
    assert config.debug is True
    assert config.log_level == "DEBUG"
    assert config.default_namespace == "production"
    assert config.gcp_project == "my-project"


def test_feature_flags_disabled():
    env = {
        "MCP_ENABLE_COST": "false",
        "MCP_ENABLE_SECURITY": "false",
    }
    with pytest.MonkeyPatch.context() as mp:
        for k, v in env.items():
            mp.setenv(k, v)
        config = ServerConfig.from_env()

    assert config.enable_cost_tools is False
    assert config.enable_security_tools is False
    assert config.enable_git_tools is True  # default
