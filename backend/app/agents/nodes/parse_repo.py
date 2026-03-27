from __future__ import annotations

from app.agents.utils import extract_dependencies
from app.config import get_settings
from app.models.state import RepoAnalysisState
from app.services.github_service import GitHubService


async def parse_repo_node(state: RepoAnalysisState) -> dict[str, object]:
    if state.get("status") == "failed":
        return {}

    file_tree = state.get("file_tree", [])
    owner = state.get("owner")
    repo = state.get("repo")
    branch = state.get("branch", "main")
    if not owner or not repo:
        return {
            "errors": ["parse_repo failed: repository identity is missing from state"],
            "status": "failed",
        }

    selected_files = GitHubService.select_relevant_files(file_tree)
    settings = get_settings()
    service = GitHubService(token=settings.GITHUB_TOKEN)

    async def fetch_content(path: str) -> tuple[str, str | None, str | None]:
        try:
            content = await service.get_file_content(owner, repo, path, branch)
            return path, content, None
        except Exception as exc:
            return path, None, str(exc)

    try:
        file_contents: dict[str, str] = {}
        errors: list[str] = []
        for path in selected_files:
            item_path, content, error = await fetch_content(path)
            if error:
                errors.append(f"parse_repo content fetch failed for {item_path}: {error}")
                continue
            if content:
                file_contents[item_path] = content

        dependencies = extract_dependencies(file_contents)
        payload: dict[str, object] = {
            "selected_files": selected_files,
            "file_contents": file_contents,
            "dependencies": dependencies,
            "status": "parsing",
        }
        if errors:
            payload["errors"] = errors
        return payload
    except Exception as exc:
        return {
            "errors": [f"parse_repo failed: {exc}"],
            "status": "failed",
        }
    finally:
        await service.close()
