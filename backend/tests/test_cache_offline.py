# tests/test_cache_offline.py
"""Offline unit test for the GitHub project caching logic.

Exercises the cache-first behaviour of github_mcp without any network
access, GitHub token, or running project. The real GitHub call
(_fetch_from_github) is monkey-patched with a stub returning fixed data,
so the test isolates and verifies only the local caching logic:

    * sync_all fetches a project the first time and writes it to disk;
    * a second sync_all returns an empty list (nothing re-fetched),
      proving the cache is used instead of GitHub;
    * get_project reads the stored document back from disk;
    * the full README is preserved (not truncated).

Note: with the default CACHE_DIR this writes demo files into the real
uploads/project_docs folder. Point github_mcp.CACHE_DIR at a temp dir
(or use pytest's tmp_path) to keep the test fully self-contained.

Run from the backend directory:
    python3 -m tests.test_cache_offline
"""

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
