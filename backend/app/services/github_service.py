from __future__ import annotations

import base64
import re
from collections.abc import Iterable
from pathlib import PurePosixPath
from typing import Any

import httpx


class GitHubService:
    BASE_URL = "https://api.github.com"
    MAX_ANALYSIS_FILES = 50
    MAX_FILE_SIZE_BYTES = 100 * 1024
    TEXT_EXTENSIONS = {
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".java",
        ".go",
        ".rs",
        ".rb",
        ".php",
        ".cs",
        ".cpp",
        ".c",
        ".h",
        ".hpp",
        ".swift",
        ".kt",
        ".scala",
        ".md",
        ".rst",
        ".txt",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".ini",
        ".cfg",
        ".env.example",
        ".sh",
        ".dockerignore",
    }
    IMPORTANT_FILENAMES = {
        "readme.md",
        "package.json",
        "package-lock.json",
        "pnpm-lock.yaml",
        "yarn.lock",
        "requirements.txt",
        "pyproject.toml",
        "poetry.lock",
        "go.mod",
        "go.sum",
        "cargo.toml",
        "dockerfile",
        "docker-compose.yml",
        ".gitignore",
        ".env.example",
    }
    GITHUB_URL_PATTERN = re.compile(
        r"^https://github\.com/(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?/?$"
    )

    def __init__(
        self,
        token: str | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        if client is None:
            self.client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers=headers,
                timeout=httpx.Timeout(30.0),
            )
            self._owns_client = True
        else:
            client.headers.update(headers)
            self.client = client
            self._owns_client = False

    async def close(self) -> None:
        if self._owns_client:
            await self.client.aclose()

    async def __aenter__(self) -> "GitHubService":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    async def get_repo_metadata(self, owner: str, repo: str) -> dict[str, Any]:
        data = await self._get_json(f"/repos/{owner}/{repo}")
        return {
            "name": data.get("name"),
            "full_name": data.get("full_name"),
            "description": data.get("description") or "",
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "language": data.get("language"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "default_branch": data.get("default_branch", "main"),
        }

    async def get_file_tree(self, owner: str, repo: str, branch: str) -> list[str]:
        try:
            data = await self._get_json(
                f"/repos/{owner}/{repo}/git/trees/{branch}",
                params={"recursive": 1},
            )
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code != 404:
                raise
            branch_data = await self._get_json(f"/repos/{owner}/{repo}/branches/{branch}")
            sha = branch_data["commit"]["commit"]["tree"]["sha"]
            data = await self._get_json(
                f"/repos/{owner}/{repo}/git/trees/{sha}",
                params={"recursive": 1},
            )

        tree = data.get("tree", [])
        return sorted(item["path"] for item in tree if item.get("type") == "blob")

    async def get_file_content(self, owner: str, repo: str, path: str, branch: str) -> str:
        data = await self._get_json(
            f"/repos/{owner}/{repo}/contents/{path}",
            params={"ref": branch},
        )
        if isinstance(data, list):
            raise ValueError(f"Path '{path}' refers to a directory, not a file")

        encoded = data.get("content", "")
        if data.get("encoding") != "base64":
            return ""

        raw_bytes = base64.b64decode(encoded, validate=False)
        truncated = raw_bytes[: self.MAX_FILE_SIZE_BYTES]
        try:
            content = truncated.decode("utf-8")
        except UnicodeDecodeError:
            content = truncated.decode("utf-8", errors="ignore")

        if len(raw_bytes) > self.MAX_FILE_SIZE_BYTES:
            content += "\n\n[TRUNCATED_AT_100KB]"
        return content

    async def get_languages(self, owner: str, repo: str) -> dict[str, float]:
        data = await self._get_json(f"/repos/{owner}/{repo}/languages")
        total = sum(data.values())
        if not total:
            return {}
        return {
            language: round((bytes_count / total) * 100, 2)
            for language, bytes_count in data.items()
        }

    @staticmethod
    def parse_github_url(url: str) -> tuple[str, str]:
        match = GitHubService.GITHUB_URL_PATTERN.match(url.strip())
        if not match:
            raise ValueError("Invalid GitHub repository URL")
        return match.group("owner"), match.group("repo")

    @classmethod
    def select_relevant_files(cls, file_tree: Iterable[str]) -> list[str]:
        scored_paths: list[tuple[int, str]] = []
        for path in file_tree:
            score = cls._path_priority(path)
            if score <= 0:
                continue
            scored_paths.append((score, path))

        scored_paths.sort(key=lambda item: (-item[0], item[1]))
        return [path for _, path in scored_paths[: cls.MAX_ANALYSIS_FILES]]

    @classmethod
    def _path_priority(cls, path: str) -> int:
        lower = path.lower()
        name = PurePosixPath(path).name.lower()
        suffix = PurePosixPath(path).suffix.lower()

        if lower.endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf", ".zip", ".lockb")):
            return 0

        score = 0
        if name in cls.IMPORTANT_FILENAMES:
            score += 100
        if lower.startswith("src/") or lower.startswith("app/") or lower.startswith("lib/"):
            score += 80
        if lower.startswith("tests/") or lower.startswith("test/") or "/__tests__/" in lower:
            score += 70
        if lower.startswith(".github/workflows/"):
            score += 65
        if name.startswith("readme"):
            score += 100
        if suffix in cls.TEXT_EXTENSIONS:
            score += 50
        if any(token in lower for token in ("config", "settings", "docker", "compose")):
            score += 35
        if score == 0 and "/" not in lower:
            score += 20
        return score

    async def _get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        response = await self.client.get(path, params=params)
        response.raise_for_status()
        return response.json()
