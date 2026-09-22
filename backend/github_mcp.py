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
import json
import requests
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv
from fastmcp import FastMCP

from config import GITHUB, UPLOAD_DIR

load_dotenv()

mcp = FastMCP("github-projects")

PROJECTS = [
    "job_application_assistant",
    "foodgram",
    "async-yacut",
    "bulls_cows",
    "homework-bot",
    "gpt_adviser"
]

CACHE_DIR = Path(UPLOAD_DIR) / "project_docs"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


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


def _fetch_from_github(repo_name: str) -> dict:
    """Fetch full metadata, languages, and the COMPLETE README for one repo."""
    owner = _username()
    meta = requests.get(
        f"{GITHUB}/repos/{owner}/{repo_name}",
        headers=_headers(),
        timeout=10,
    )
    meta.raise_for_status()
    meta_json = meta.json()

    readme_resp = requests.get(
        f"{GITHUB}/repos/{owner}/{repo_name}/readme",
        headers=_headers(raw=True),
        timeout=10,
    )
    if readme_resp.status_code == 404:
        readme = ""
    else:
        readme_resp.raise_for_status()
        readme = readme_resp.text

    langs = requests.get(
        f"{GITHUB}/repos/{owner}/{repo_name}/languages",
        headers=_headers(),
        timeout=10,
    )
    langs.raise_for_status()

    return {
        "name": meta_json["name"],
        "description": meta_json.get("description"),
        "language": meta_json.get("language"),
        "html_url": meta_json.get("html_url"),
        "updated_at": meta_json.get("updated_at"),
        "stargazers_count": meta_json.get("stargazers_count"),
        "languages": langs.json(),
        "readme": readme,
    }


def _cache_path(repo_name: str) -> Path:
    return CACHE_DIR / f"{repo_name}.json"


def _write_markdown(data: dict) -> None:
    """Write a human/RAG-readable document with the full project write-up."""
    langs = ", ".join(data["languages"].keys()) or "-"
    md = (
        f"# {data['name']}\n\n"
        f"**Description:** {data.get('description') or '—'}\n\n"
        f"**Primary language:** {data.get('language') or '—'}\n\n"
        f"**Languages:** {langs}\n\n"
        f"**URL:** {data.get('html_url') or '—'}\n\n"
        f"**Last updated:** {data.get('updated_at') or '—'}\n\n"
        "---\n\n"
        f"{data['readme'] or '_No README available._'}\n"
    )
    (CACHE_DIR / f"{data['name']}.md").write_text(md, encoding="utf-8")


def _get_project(repo_name: str, force_refresh: bool = False) -> dict:
    """Return a project's full document.

    Reads from the local cache if present; only contacts GitHub when the
    project has never been cached, or when force_refresh is True.
    """
    if repo_name not in PROJECTS:
        raise ValueError(
            f"'{repo_name}' is not in the allowed PROJECTS list. "
            f"Available projects: {', '.join(PROJECTS)}"
        )

    path = _cache_path(repo_name)
    if path.exists() and not force_refresh:
        return json.loads(path.read_text(encoding="utf-8"))

    data = _fetch_from_github(repo_name)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    _write_markdown(data)
    return data


@mcp.tool
def list_projects() -> list[str]:
    """List the curated project names the agent is allowed to retrieve."""
    return PROJECTS


@mcp.tool
def get_project(repo_name: str) -> dict:
    """Get full info (metadata, languages, complete README) for one project."""
    return _get_project(repo_name)


@mcp.tool
def refresh_project(repo_name: str) -> dict:
    """Force a fresh fetch from GitHub, overwriting the local cache."""
    return _get_project(repo_name, force_refresh=True)


@mcp.tool
def sync_all() -> list[str]:
    """Fetch every curated project that is not yet cached.

    Returns the names of the projects that were actually fetched.
    """
    fetched = []
    for name in PROJECTS:
        if not _cache_path(name).exists():
            _get_project(name)
            fetched.append(name)
    return fetched


if __name__ == "__main__":
    mcp.run()
