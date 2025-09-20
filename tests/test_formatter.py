"""Tests for the output formatter utility."""

from mcp_devops_server.utils.formatter import (
    format_table,
    format_json,
    format_yaml,
    truncate_output,
)


class TestFormatTable:
    def test_basic_table(self):
        headers = ["NAME", "AGE"]
        rows = [["Alice", "30"], ["Bob", "25"]]
        result = format_table(headers, rows)
        assert "NAME" in result
        assert "Alice" in result
        assert "Bob" in result

    def test_empty_rows(self):
        result = format_table(["A", "B"], [])
        assert "No results" in result


class TestFormatJson:
    def test_dict(self):
        result = format_json({"key": "value"})
        assert '"key"' in result
        assert '"value"' in result


class TestFormatYaml:
    def test_dict(self):
        result = format_yaml({"key": "value"})
        assert "key:" in result


class TestTruncateOutput:
    def test_short_text(self):
        result = truncate_output("short text", max_lines=10)
        assert result == "short text"

    def test_long_text(self):
        text = "\n".join(f"line {i}" for i in range(200))
        result = truncate_output(text, max_lines=50)
        assert "truncated" in result
        assert "line 0" in result
