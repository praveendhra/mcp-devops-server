"""Entry point for the MCP DevOps Server."""

import asyncio
import logging
import sys


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )

    from .server import run_server
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
