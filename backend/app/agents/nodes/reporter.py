from __future__ import annotations

from app.agents.llm import run_report_prompt
from app.agents.nodes.scorer import WEIGHTS
from app.agents.prompts.report import SYSTEM_PROMPT, build_report_prompt
from app.models.state import RepoAnalysisState


def build_criteria_dict(state: RepoAnalysisState) -> dict[str, dict]:
    criteria: dict[str, dict] = {}
    mapping = {
        "code_quality": state.get("code_quality_analysis"),
        "docs": state.get("docs_analysis"),
        "tests": state.get("tests_analysis"),
        "security": state.get("security_analysis"),
        "structure": state.get("structure_analysis"),
    }
    for name, payload in mapping.items():
        if payload:
            criteria[name] = {
                "score": payload.get("score", 0),
                "weight": WEIGHTS[name],
                "strengths": payload.get("strengths", []),
                "improvements": payload.get("improvements", []),
                "details": payload.get("details", ""),
            }
    return criteria


def _priority_prefix(score: float) -> str:
    if score < 50:
        return "Alta"
    if score < 70:
        return "Media"
    return "Baixa"


def fallback_report(state: RepoAnalysisState, criteria: dict[str, dict]) -> dict[str, object]:
    ordered = sorted(criteria.items(), key=lambda item: item[1]["score"])
    recommendations: list[str] = []
    for _, payload in ordered:
        for improvement in payload.get("improvements", [])[:2]:
            recommendations.append(f"{_priority_prefix(payload['score'])}: {improvement}")
        if len(recommendations) >= 10:
            break

    summary = (
        f"O repositorio analisado recebeu score {state.get('final_score', 0)} e grade {state.get('grade', 'F')}. "
        "O resumo foi gerado por fallback heuristico, consolidando os sinais coletados por cada criterio. "
        "Priorize primeiro os itens com menor score para elevar qualidade geral, reduzir risco e melhorar manutencao."
    )
    return {
        "summary": summary,
        "recommendations": recommendations[:10],
    }


async def generate_report_node(state: RepoAnalysisState) -> dict[str, object]:
    criteria = build_criteria_dict(state)
    if state.get("status") == "failed":
        fallback = fallback_report(state, criteria)
        report = {
            "summary": fallback["summary"],
            "recommendations": fallback["recommendations"],
            "criteria": criteria,
            "score": state.get("final_score", 0.0),
            "grade": state.get("grade", "F"),
            "errors": state.get("errors", []),
        }
        return {
            "summary": fallback["summary"],
            "recommendations": fallback["recommendations"],
            "report": report,
            "status": "failed",
        }

    fallback = fallback_report(state, criteria)
    llm_result = await run_report_prompt(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=build_report_prompt(
            repo_url=state["repo_url"],
            criteria=criteria,
            score=float(state.get("final_score", 0.0)),
            grade=str(state.get("grade", "F")),
        ),
        fallback=fallback,
    )
    report = {
        "summary": llm_result["summary"],
        "recommendations": llm_result["recommendations"],
        "criteria": criteria,
        "score": state.get("final_score", 0.0),
        "grade": state.get("grade", "F"),
        "errors": state.get("errors", []),
    }
    return {
        "summary": llm_result["summary"],
        "recommendations": llm_result["recommendations"],
        "report": report,
        "status": "completed",
    }
