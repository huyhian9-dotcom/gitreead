from __future__ import annotations

import base64

import httpx
import pytest

from app.services.github_service import GitHubService


def test_parse_github_url_accepts_valid_repository() -> None:
    assert GitHubService.parse_github_url("https://github.com/fastapi/fastapi") == (
        "fastapi",
        "fastapi",
    )


def test_parse_github_url_rejects_invalid_value() -> None:
    with pytest.raises(ValueError):
        GitHubService.parse_github_url("invalid")


@pytest.mark.asyncio
async def test_service_uses_token_and_returns_tree_and_languages() -> None:
    seen_authorization: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        auth = request.headers.get("Authorization")
        if auth:
            seen_authorization.append(auth)

        if request.url.path.endswith("/git/trees/main"):
            return httpx.Response(
                200,
                json={
                    "tree": [
                        {"path": "README.md", "type": "blob"},
                        {"path": "src/app.py", "type": "blob"},
                        {"path": "docs", "type": "tree"},
                    ]
                },
            )
        if request.url.path.endswith("/languages"):
            return httpx.Response(200, json={"Python": 70, "TypeScript": 30})
        raise AssertionError(f"Unexpected path: {request.url.path}")

    client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    )
    service = GitHubService(token="ghp_test", client=client)
    try:
        file_tree = await service.get_file_tree("owner", "repo", "main")
        languages = await service.get_languages("owner", "repo")
    finally:
        await client.aclose()

    assert seen_authorization == ["Bearer ghp_test", "Bearer ghp_test"]
    assert file_tree == ["README.md", "src/app.py"]
    assert languages == {"Python": 70.0, "TypeScript": 30.0}


@pytest.mark.asyncio
async def test_get_file_content_decodes_base64() -> None:
    encoded = base64.b64encode(b"print('hello')").decode("utf-8")

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "encoding": "base64",
                "content": encoded,
            },
        )

    client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    )
    service = GitHubService(client=client)
    try:
        content = await service.get_file_content("owner", "repo", "src/app.py", "main")
    finally:
        await client.aclose()

    assert content == "print('hello')"
