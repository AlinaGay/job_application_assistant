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


@mcp.tool
def get_readme(repo_name: str) -> str:
    """Fetch README content of a given repo by name."""
    user = requests.get(
        "https://api.github.com/user", headers=HEADERS, timeout=10
    ).json()
    r = requests.get(
        f"https://api.github.com/repos/{user['login']}/{repo_name}/readme",
        headers={**HEADERS, "Accept": "application/vnd.github.raw"},
        timeout=10,
    )
    r.raise_for_status()
    return r.text[:4000]


@mcp.tool
def get_repo_languages(repo_name: str) -> str:
    """Get languages and their byte-count for a given repo."""
    user = requests.get(
        "https://api.github.com/user", headers=HEADERS, timeout=10
    ).json()
    r = requests.get(
        f"https://api.github.com/repos/{user['login']}/{repo_name}/languages",
        headers=HEADERS,
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    mcp.run()
