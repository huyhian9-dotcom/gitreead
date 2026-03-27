from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.agents.nodes.analyze_code import analyze_code_node
from app.agents.nodes.analyze_docs import analyze_docs_node
from app.agents.nodes.analyze_security import analyze_security_node
from app.agents.nodes.analyze_tests import analyze_tests_node
from app.agents.nodes.fetch_repo import fetch_repo_node
from app.agents.nodes.parse_repo import parse_repo_node
from app.agents.nodes.reporter import generate_report_node
from app.agents.nodes.scorer import score_repo_node
from app.models.state import RepoAnalysisState


def build_analysis_graph():
    graph = StateGraph(RepoAnalysisState)

    graph.add_node("fetch_repo", fetch_repo_node)
    graph.add_node("parse_repo", parse_repo_node)
    graph.add_node("analyze_code", analyze_code_node)
    graph.add_node("analyze_docs", analyze_docs_node)
    graph.add_node("analyze_tests", analyze_tests_node)
    graph.add_node("analyze_security", analyze_security_node)
    graph.add_node("score_repo", score_repo_node)
    graph.add_node("generate_report", generate_report_node)

    graph.add_edge(START, "fetch_repo")
    graph.add_edge("fetch_repo", "parse_repo")
    graph.add_edge("parse_repo", "analyze_code")
    graph.add_edge("parse_repo", "analyze_docs")
    graph.add_edge("parse_repo", "analyze_tests")
    graph.add_edge("parse_repo", "analyze_security")
    graph.add_edge(["analyze_code", "analyze_docs", "analyze_tests", "analyze_security"], "score_repo")
    graph.add_edge("score_repo", "generate_report")
    graph.add_edge("generate_report", END)

    return graph.compile()
