# test_mcp.py

import asyncio
from fastmcp import Client
from github_mcp import mcp


async def main():
    async with Client(mcp) as client:
        tools = await client.list_tools()
        print("Tools:", [tool.name for tool in tools])

asyncio.run(main())
