from __future__ import annotations

from app.agents.llm import run_analysis_prompt
from app.agents.prompts.security import SYSTEM_PROMPT, build_security_prompt
from app.agents.utils import build_prompt_context, fallback_security_analysis
from app.models.state import RepoAnalysisState


async def analyze_security_node(state: RepoAnalysisState) -> dict[str, object]:
    if state.get("status") == "failed":
        return {}

    file_contents = state.get("file_contents", {})
    all_paths = list(file_contents)
    fallback = fallback_security_analysis(file_contents, all_paths)
    context = build_prompt_context(file_contents, all_paths, max_files=10)

    result = await run_analysis_prompt(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=build_security_prompt(
            repo_url=state["repo_url"],
            dependencies=state.get("dependencies", []),
            context=context,
        ),
        fallback=fallback,
    )
    return {
        "security_analysis": result,
        "status": "analyzing",
    }
