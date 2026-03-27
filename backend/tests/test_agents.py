from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.agents.graph import build_analysis_graph
from app.agents.nodes import fetch_repo as fetch_repo_module
from app.agents.nodes import parse_repo as parse_repo_module
from app.agents.nodes.reporter import generate_report_node
from app.agents.nodes.scorer import score_repo_node, score_to_grade


def test_build_analysis_graph_draws_mermaid() -> None:
    graph = build_analysis_graph()
    mermaid = graph.get_graph().draw_mermaid()
    assert "fetch_repo" in mermaid
    assert "analyze_code" in mermaid
    assert "generate_report" in mermaid


@pytest.mark.asyncio
async def test_fetch_repo_node_populates_state(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeGitHubService:
        def __init__(self, token: str | None = None) -> None:
            self.token = token

        @staticmethod
        def parse_github_url(url: str) -> tuple[str, str]:
            assert url == "https://github.com/org/repo"
            return ("org", "repo")

        async def get_repo_metadata(self, owner: str, repo: str) -> dict[str, object]:
            assert (owner, repo) == ("org", "repo")
            return {"default_branch": "main", "stars": 10}

        async def get_file_tree(self, owner: str, repo: str, branch: str) -> list[str]:
            assert branch == "main"
            return ["README.md", "src/app.py"]

        async def get_languages(self, owner: str, repo: str) -> dict[str, float]:
            return {"Python": 100.0}

        async def close(self) -> None:
            return None

    monkeypatch.setattr(fetch_repo_module, "GitHubService", FakeGitHubService)
    monkeypatch.setattr(fetch_repo_module, "get_settings", lambda: SimpleNamespace(GITHUB_TOKEN=None))

    result = await fetch_repo_module.fetch_repo_node(
        {"repo_url": "https://github.com/org/repo", "branch": "main"}
    )

    assert result["status"] == "fetching"
    assert result["repo_metadata"] == {"default_branch": "main", "stars": 10}
    assert result["file_tree"] == ["README.md", "src/app.py"]
    assert result["language_stats"] == {"Python": 100.0}


@pytest.mark.asyncio
async def test_parse_repo_node_extracts_dependencies(monkeypatch: pytest.MonkeyPatch) -> None:
    sample_contents = {
        "requirements.txt": "fastapi>=0.115.0\nhttpx>=0.27.0\n",
        "package.json": '{"dependencies":{"react":"18.0.0"}}',
        "pyproject.toml": "[project]\ndependencies = ['pydantic>=2.0']\n",
    }

    class FakeGitHubService:
        def __init__(self, token: str | None = None) -> None:
            self.token = token

        @classmethod
        def select_relevant_files(cls, file_tree: list[str]) -> list[str]:
            return file_tree

        async def get_file_content(self, owner: str, repo: str, path: str, branch: str) -> str:
            return sample_contents[path]

        async def close(self) -> None:
            return None

    monkeypatch.setattr(parse_repo_module, "GitHubService", FakeGitHubService)
    monkeypatch.setattr(parse_repo_module, "get_settings", lambda: SimpleNamespace(GITHUB_TOKEN=None))

    result = await parse_repo_module.parse_repo_node(
        {
            "owner": "org",
            "repo": "repo",
            "branch": "main",
            "file_tree": list(sample_contents),
        }
    )

    assert result["status"] == "parsing"
    assert set(result["dependencies"]) == {"fastapi", "httpx", "pydantic", "react"}
    assert result["file_contents"]["package.json"] == sample_contents["package.json"]


@pytest.mark.asyncio
async def test_score_repo_node_calculates_weighted_average() -> None:
    result = await score_repo_node(
        {
            "file_tree": ["README.md", "src/app.py", "tests/test_app.py"],
            "file_contents": {"README.md": "# Docs"},
            "code_quality_analysis": {"score": 80.0},
            "docs_analysis": {"score": 70.0},
            "tests_analysis": {"score": 60.0},
            "security_analysis": {"score": 50.0},
        }
    )

    assert result["status"] == "scoring"
    assert isinstance(result["final_score"], float)
    assert score_to_grade(float(result["final_score"])) == result["grade"]


def test_score_to_grade_boundaries() -> None:
    assert score_to_grade(95) == "A+"
    assert score_to_grade(85) == "A"
    assert score_to_grade(75) == "B"
    assert score_to_grade(65) == "C"
    assert score_to_grade(55) == "D"
    assert score_to_grade(10) == "F"


@pytest.mark.asyncio
async def test_generate_report_node_uses_fallback_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_run_report_prompt(system_prompt: str, user_prompt: str, fallback: dict[str, object]) -> dict[str, object]:
        assert "score" not in fallback
        return {
            "summary": "Resumo consolidado.",
            "recommendations": ["Alta: melhorar testes"],
        }

    monkeypatch.setattr("app.agents.nodes.reporter.run_report_prompt", fake_run_report_prompt)

    result = await generate_report_node(
        {
            "repo_url": "https://github.com/org/repo",
            "final_score": 72.0,
            "grade": "B",
            "code_quality_analysis": {
                "score": 80.0,
                "strengths": ["Bom design"],
                "improvements": ["Reduzir complexidade"],
                "details": "Detalhes",
            },
            "docs_analysis": {
                "score": 60.0,
                "strengths": [],
                "improvements": ["Expandir README"],
                "details": "Detalhes",
            },
            "tests_analysis": {
                "score": 55.0,
                "strengths": [],
                "improvements": ["Cobrir edge cases"],
                "details": "Detalhes",
            },
            "security_analysis": {
                "score": 70.0,
                "strengths": [],
                "improvements": ["Revisar secrets"],
                "details": "Detalhes",
            },
            "structure_analysis": {
                "score": 75.0,
                "strengths": [],
                "improvements": ["Organizar raiz"],
                "details": "Detalhes",
            },
        }
    )

    assert result["status"] == "completed"
    assert result["summary"] == "Resumo consolidado."
    assert result["recommendations"] == ["Alta: melhorar testes"]
    assert result["report"]["grade"] == "B"
