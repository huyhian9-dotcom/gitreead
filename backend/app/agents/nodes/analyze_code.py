from __future__ import annotations

from app.agents.llm import run_analysis_prompt
from app.agents.prompts.code_quality import SYSTEM_PROMPT, build_code_quality_prompt
from app.agents.utils import build_prompt_context, fallback_code_analysis, is_code_file
from app.models.state import RepoAnalysisState


async def analyze_code_node(state: RepoAnalysisState) -> dict[str, object]:
    if state.get("status") == "failed":
        return {}

    file_contents = state.get("file_contents", {})
    code_paths = [path for path in file_contents if is_code_file(path)]
    fallback = fallback_code_analysis(file_contents, code_paths)

    if not code_paths:
        fallback["details"] = "Nenhum arquivo de codigo foi encontrado para a analise."
        return {
            "code_quality_analysis": fallback,
            "status": "analyzing",
        }

    context = build_prompt_context(file_contents, code_paths, max_files=10)
    result = await run_analysis_prompt(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=build_code_quality_prompt(
            repo_url=state["repo_url"],
            language_stats=state.get("language_stats", {}),
            context=context,
        ),
        fallback=fallback,
    )
    return {
        "code_quality_analysis": result,
        "status": "analyzing",
    }
