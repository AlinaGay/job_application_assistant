# github_mcp.py

"""FastMCP server exposing the candidate's GitHub projects as agent tools.

Runs as a stdio subprocess spawned by the RAG service and provides tools
for listing repositories, fetching READMEs, and inspecting language stats.
The cover letter agent uses these tools to ground its output in real
projects instead of relying on the resume alone.

Requires the GH_TOKEN environment variable (loaded from .env) — a GitHub
Personal Access Token with `repo` or `public_repo` scope.

Exposed tools:
    repos_list          — list non-fork, non-archived repositories
    get_readme          — fetch raw README content for a given repo
    get_repo_languages  — get language byte-count breakdown for a given repo
    get_repo_tech_stack — combine README excerpt and language stats
"""

import os
from functools import lru_cache

import requests
from dotenv import load_dotenv
from fastmcp import FastMCP

from config import GITHUB

load_dotenv()

mcp = FastMCP("github-projects")


def _headers(raw: bool = False) -> dict:
    """Build authenticated headers for GitHub REST API requests."""
    accept = (
        "application/vnd.github.raw" if raw else "application/vnd.github+json")
    return {
        "Authorization": f"Bearer {os.environ['GH_TOKEN']}",
        "Accept": accept,
    }


@lru_cache(maxsize=1)
def _username() -> str:
    """Get authenticated user's login (cached for the process lifetime)."""
    response = requests.get(f"{GITHUB}/user", headers=_headers(), timeout=10)
    response.raise_for_status()
    return response.json()["login"]


def _fetch_readme(repo_name: str) -> str:
    """Fetch raw README content; returns '' on 404."""
    r = requests.get(
        f"{GITHUB}/repos/{_username()}/{repo_name}/readme",
        headers=_headers(raw=True),
        timeout=10,
    )
    if r.status_code == 404:
        return ""
    r.raise_for_status()
    return r.text[:4000]


def _fetch_languages(repo_name: str) -> dict:
    """Fetch language byte counts for a repo."""
    r = requests.get(
        f"{GITHUB}/repos/{_username()}/{repo_name}/languages",
        headers=_headers(),
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


@mcp.tool
def repos_list(limit: int = 30) -> list[dict]:
    """List candidate's original (non-fork) repositories with READMEs."""
    params: dict[str, str | int] = {"per_page": 100, "sort": "updated"}
    response = requests.get(
        f"{GITHUB}/users/{_username()}/repos",
        headers=_headers(),
        params=params,
        timeout=10
    )
    response.raise_for_status()
    repos = [
        {
            "name": repo["name"],
            "description": repo["description"],
            "language": repo["language"],
            "updated_at": repo["updated_at"],
            "stargazers_count": repo["stargazers_count"],
        }
        for repo in response.json()
        if not repo["fork"] and not repo["archived"]
    ]
    return repos[:limit]


@mcp.tool
def get_readme(repo_name: str) -> str:
    """Fetch README content of a given repo by name."""
    return _fetch_readme(repo_name)


@mcp.tool
def get_repo_languages(repo_name: str) -> dict:
    """Get languages and their byte-count for a given repo."""
    return _fetch_languages(repo_name)


@mcp.tool
def get_repo_tech_stack(repo_name: str) -> dict:
    """Extract probable tech stack from README and language stats."""
    return {
        "languages": _fetch_languages(repo_name),
        "readme_excerpt": _fetch_readme(repo_name)[:2000]
    }


if __name__ == "__main__":
    mcp.run()
