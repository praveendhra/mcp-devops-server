# Contributing to MCP DevOps Server

## Adding a New Tool

1. Create a new file in `src/tools/` or add to an existing one:

```python
def my_new_tool(param1: str, param2: int = 10) -> dict:
    """Description of what the tool does."""
    # Implementation
    return {"result": "data"}
```

2. Register the tool in `src/server.py`:

```python
registry.register(
    name="my_new_tool",
    description="What it does in one sentence",
    function=my_new_tool,
    parameters={
        "param1": {"type": "string", "description": "What param1 is"},
        "param2": {"type": "integer", "description": "What param2 is", "default": 10}
    },
    category="category_name",
    requires=["external_binary"]  # optional
)
```

3. Add tests in `tests/`:

```python
@patch("subprocess.run")
def test_my_new_tool(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="output")
    result = my_new_tool("value")
    assert "result" in result
```

4. Update `docs/TOOLS.md` with the new tool.

## Code Standards
- All tools return `dict` with structured data
- Use `subprocess.run` with `capture_output=True` for external commands
- Handle errors gracefully (return `{"error": message}`)
- Add type hints to all functions
- Write tests with mocked subprocess calls

## Testing
```bash
pytest tests/ -v
pytest tests/ -v --cov=src --cov-report=term-missing
```
