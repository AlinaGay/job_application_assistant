# github_mcp.py

import os
import requests
from dotenv import load_dotenv
from fastmcp import FastMCP


load_dotenv()

mcp = FastMCP("github-projects")
HEADERS = {
    "Authorization": f"Bearer {os.environ['GH_TOKEN']}",
    "Accept": "application/vnd.github+json"
}

@mcp.tool
def repos_list(limit: int = 20) -> list[dict]:
    """List the user's repositories, sorted by last update."""
    r = requests.get(
        "https://api.github.com/user/repos",
        headers=HEADERS,
        params={"per_page": limit, "sort": "updated"},
        timeout=10
    )
    r.raise_for_status()
    return [
        {
            "name": repo["name"],
            "description": repo["description"],
            "language": repo["language"],
            "url": repo["html_url"],
        }
        for repo in r.json()
        if not repo["fork"]
    ]
