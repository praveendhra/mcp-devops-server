"""Output formatting helpers for MCP tool responses."""

import json
import yaml


def format_table(headers: list[str], rows: list[list[str]]) -> str:
    """Format data as an aligned text table."""
    if not rows:
        return "No results found."

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    header_line = "  ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    separator = "  ".join("-" * w for w in col_widths)
    data_lines = []
    for row in rows:
        line = "  ".join(str(c).ljust(w) for c, w in zip(row, col_widths))
        data_lines.append(line)

    return "\n".join([header_line, separator] + data_lines)


def format_yaml(data: dict | list) -> str:
    """Format data as YAML."""
    return yaml.dump(data, default_flow_style=False, sort_keys=False)


def format_json(data: dict | list) -> str:
    """Format data as pretty JSON."""
    return json.dumps(data, indent=2, default=str)


def truncate_output(text: str, max_lines: int = 100) -> str:
    """Truncate output to a maximum number of lines."""
    lines = text.split("\n")
    if len(lines) <= max_lines:
        return text
    return "\n".join(lines[:max_lines]) + f"\n\n... ({len(lines) - max_lines} more lines truncated)"
