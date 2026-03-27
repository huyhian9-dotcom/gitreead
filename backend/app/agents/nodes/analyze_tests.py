from __future__ import annotations

from app.agents.llm import run_analysis_prompt
from app.agents.prompts.tests import SYSTEM_PROMPT, build_tests_prompt
from app.agents.utils import (
    build_prompt_context,
    fallback_tests_analysis,
    is_code_file,
    is_test_file,
)
from app.models.state import RepoAnalysisState


async def analyze_tests_node(state: RepoAnalysisState) -> dict[str, object]:
    if state.get("status") == "failed":
        return {}

    file_contents = state.get("file_contents", {})
    test_paths = [path for path in file_contents if is_test_file(path)]
    code_paths = [path for path in file_contents if is_code_file(path)]
    fallback = fallback_tests_analysis(file_contents, test_paths, code_paths)
    context = build_prompt_context(file_contents, [*test_paths, *code_paths], max_files=10)

    result = await run_analysis_prompt(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=build_tests_prompt(repo_url=state["repo_url"], context=context),
        fallback=fallback,
    )
    return {
        "tests_analysis": result,
        "status": "analyzing",
    }
