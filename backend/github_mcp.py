# github_mcp.py

import os
import requests
from dotenv import load_dotenv
from fastmcp import FastMCP

from config import GITHUB




load_dotenv()

mcp = FastMCP("github-projects")


def _headers(raw: bool = False) -> dict:
    accept = "application/vnd.github.raw" if raw else "application/vnd.github+json"
    return {
        "Authorization": f"Bearer {os.environ['GH_TOKEN']}",
        "Accept": accept,
    }


def _username() -> str:
    """Get authenticated user's login (used by repo-name tools)."""
    return requests.get(
        f"{GITHUB}/user", headers=_headers(), timeout=10
    ).json()["login"]


@mcp.tool
def repos_list(limit: int = 20) -> list[dict]:
    """List the user's repositories, sorted by last update."""
    r = requests.get(
        f"{GITHUB}/user/repos",
        headers=_headers(),
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
    r = requests.get(
        f"{GITHUB}/repos/{_username()}/{repo_name}/readme",
        headers=_headers(raw=True),
        timeout=10,
    )
    if r.status_code == 404:
        return ""
    r.raise_for_status()
    return r.text[:4000]


@mcp.tool
def get_repo_languages(repo_name: str) -> dict:
    """Get languages and their byte-count for a given repo."""
    r = requests.get(
        f"{GITHUB}/repos/{_username()}/{repo_name}/languages",
        headers=_headers(),
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    mcp.run()
