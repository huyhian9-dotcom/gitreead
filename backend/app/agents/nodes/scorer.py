from __future__ import annotations

from app.agents.utils import structure_analysis
from app.models.state import RepoAnalysisState

WEIGHTS = {
    "code_quality": 0.30,
    "docs": 0.20,
    "tests": 0.20,
    "security": 0.15,
    "structure": 0.15,
}


def score_to_grade(score: float) -> str:
    if score >= 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    if score >= 50:
        return "D"
    return "F"


def _criteria_score(payload: dict[str, object] | None) -> float:
    if not payload:
        return 0.0
    score = payload.get("score")
    return float(score) if isinstance(score, (int, float)) else 0.0


async def score_repo_node(state: RepoAnalysisState) -> dict[str, object]:
    if state.get("status") == "failed":
        return {
            "final_score": 0.0,
            "grade": "F",
            "structure_analysis": structure_analysis(state.get("file_tree", []), state.get("file_contents", {})),
            "status": "failed",
        }

    structure = structure_analysis(state.get("file_tree", []), state.get("file_contents", {}))
    criteria_scores = {
        "code_quality": _criteria_score(state.get("code_quality_analysis")),
        "docs": _criteria_score(state.get("docs_analysis")),
        "tests": _criteria_score(state.get("tests_analysis")),
        "security": _criteria_score(state.get("security_analysis")),
        "structure": _criteria_score(structure),
    }

    final_score = round(
        sum(criteria_scores[key] * WEIGHTS[key] for key in WEIGHTS),
        2,
    )
    return {
        "structure_analysis": structure,
        "final_score": final_score,
        "grade": score_to_grade(final_score),
        "status": "scoring",
    }
