from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.models.schemas import AnalysisRequest, AnalysisResponse, CriteriaResult


def test_analysis_request_accepts_valid_github_url() -> None:
    payload = AnalysisRequest(repo_url="https://github.com/fastapi/fastapi")
    assert payload.repo_url == "https://github.com/fastapi/fastapi"
    assert payload.branch == "main"


def test_analysis_request_rejects_invalid_url() -> None:
    with pytest.raises(ValidationError):
        AnalysisRequest(repo_url="https://example.com/not-github")


def test_analysis_response_serializes_to_json() -> None:
    response = AnalysisResponse(
        id="123",
        repo_url="https://github.com/org/repo",
        status="completed",
        score=88,
        grade="A",
        criteria={
            "code_quality": CriteriaResult(
                score=90,
                weight=0.3,
                strengths=["Clean architecture"],
                improvements=["Reduce complexity"],
                details="Consistent overall.",
            )
        },
        created_at=datetime.now(UTC),
    )

    payload = response.model_dump_json()
    assert '"grade":"A"' in payload
    assert '"score":88.0' in payload or '"score":88' in payload


def test_analysis_response_rejects_invalid_grade() -> None:
    with pytest.raises(ValidationError):
        AnalysisResponse(
            id="123",
            repo_url="https://github.com/org/repo",
            status="completed",
            score=88,
            grade="Z",  # type: ignore[arg-type]
            created_at=datetime.now(UTC),
        )
