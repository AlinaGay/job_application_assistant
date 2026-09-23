# tests/test_cache_offline.py

import github_mcp


github_mcp._fetch_from_github = lambda repo_name: {
    "name": repo_name,
    "description": "fake project",
    "language": "Python",
    "html_url": f"https://github.com/test/{repo_name}",
    "updated_at": "2026-01-01T00:00:00Z",
    "stargazers_count": 0,
    "languages": {"Python": 1000},
    "readme": "FULL README TEXT " * 50,
}

github_mcp.PROJECTS = ["demo_project"]

print("1st sync:", github_mcp.sync_all())
print("2nd sync:", github_mcp.sync_all())

data = github_mcp.get_project("demo_project")
print("README length:", len(data["readme"]))
print("file exists:", github_mcp._cache_path("demo_project").exists())
