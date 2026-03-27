from __future__ import annotations

from typing import Annotated, Any, TypedDict


def merge_string_lists(current: list[str] | None, incoming: list[str] | None) -> list[str]:
    current = current or []
    incoming = incoming or []
    return [*current, *incoming]


class RepoAnalysisState(TypedDict, total=False):
    analysis_id: str
    repo_url: str
    branch: str
    owner: str
    repo: str
    repo_metadata: dict[str, Any]
    file_tree: list[str]
    selected_files: list[str]
    file_contents: dict[str, str]
    language_stats: dict[str, float]
    dependencies: list[str]
    code_quality_analysis: dict[str, Any]
    docs_analysis: dict[str, Any]
    tests_analysis: dict[str, Any]
    security_analysis: dict[str, Any]
    structure_analysis: dict[str, Any]
    final_score: float
    grade: str
    summary: str
    recommendations: list[str]
    report: dict[str, Any]
    errors: Annotated[list[str], merge_string_lists]
    status: str
