from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

GITHUB_REPO_URL_PATTERN = re.compile(
    r"^https://github\.com/(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?/?$"
)

AnalysisStatus = Literal[
    "pending",
    "fetching",
    "parsing",
    "analyzing",
    "scoring",
    "completed",
    "failed",
]
GradeValue = Literal["A+", "A", "B", "C", "D", "F"]


def _validate_github_repo_url(value: str) -> str:
    if not GITHUB_REPO_URL_PATTERN.match(value):
        raise ValueError("repo_url must be a valid GitHub repository URL")
    return value.rstrip("/")


class AnalysisRequest(BaseModel):
    repo_url: str
    branch: str = "main"

    @field_validator("repo_url")
    @classmethod
    def validate_repo_url(cls, value: str) -> str:
        return _validate_github_repo_url(value)


class CriteriaResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    score: float = Field(ge=0, le=100)
    weight: float = Field(ge=0, le=1)
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    details: str = ""


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    repo_url: str
    status: AnalysisStatus
    score: float | None = Field(default=None, ge=0, le=100)
    grade: GradeValue | None = None
    summary: str | None = None
    criteria: dict[str, CriteriaResult] | None = None
    recommendations: list[str] | None = None
    created_at: datetime
    completed_at: datetime | None = None
    error: str | None = None

    @field_validator("repo_url")
    @classmethod
    def validate_repo_url(cls, value: str) -> str:
        return _validate_github_repo_url(value)


class AnalysisListItem(BaseModel):
    id: str
    repo_url: str
    status: AnalysisStatus
    score: float | None = Field(default=None, ge=0, le=100)
    grade: GradeValue | None = None
    created_at: datetime


class StreamEvent(BaseModel):
    event: Literal["status_update", "criteria_complete", "analysis_complete"]
    data: dict[str, Any] = Field(default_factory=dict)
