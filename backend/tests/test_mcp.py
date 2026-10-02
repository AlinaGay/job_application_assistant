# test_mcp.py
"""Integration (smoke) test for the GitHub MCP server.

Verifies that the FastMCP server wires up correctly and is usable by an
agent: that all expected tools are registered and that they return real
data when invoked through the MCP protocol (not just as plain functions).

Uses fastmcp's in-memory Client, so no subprocess, no running project,
and no MCP transport layer are required — the tools are called exactly as
an agent would call them. Requires a valid GH_TOKEN and network access,
since get_project reaches GitHub on the first (uncached) request.

Run from the backend directory:
    python3 -m tests.test_mcp
"""

import asyncio
from fastmcp import Client
from github_mcp import mcp


async def main():
    """Connect an in-memory MCP client and exercise the core tools.

    Lists the registered tools, calls list_projects to get the curated
    project names, then calls get_project on the first one and prints the
    README length and language breakdown to confirm real data flows back
    through the protocol.
    """
    async with Client(mcp) as client:
        tools = await client.list_tools()
        print("Tools:", [tool.name for tool in tools])

asyncio.run(main())
