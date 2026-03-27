from __future__ import annotations

import httpx

from app.config import get_settings
from app.models.state import RepoAnalysisState
from app.services.github_service import GitHubService


async def fetch_repo_node(state: RepoAnalysisState) -> dict[str, object]:
    settings = get_settings()
    service = GitHubService(token=settings.GITHUB_TOKEN)

    try:
        owner, repo = GitHubService.parse_github_url(state["repo_url"])
        metadata = await service.get_repo_metadata(owner, repo)
        target_branch = state.get("branch") or metadata.get("default_branch", "main")
        try:
            file_tree = await service.get_file_tree(owner, repo, target_branch)
        except httpx.HTTPStatusError:
            fallback_branch = metadata.get("default_branch", target_branch)
            file_tree = await service.get_file_tree(owner, repo, fallback_branch)
            target_branch = fallback_branch
        language_stats = await service.get_languages(owner, repo)
        return {
            "owner": owner,
            "repo": repo,
            "branch": target_branch,
            "repo_metadata": metadata,
            "file_tree": file_tree,
            "language_stats": language_stats,
            "status": "fetching",
        }
    except Exception as exc:
        return {
            "errors": [f"fetch_repo failed: {exc}"],
            "status": "failed",
        }
    finally:
        await service.close()
