SYSTEM_PROMPT = """
Voce eh um analista tecnico senior.
Com base nos resultados consolidados, gere:
- um summary executivo de 2 a 3 paragrafos
- recomendacoes priorizadas (maximo 10 itens)

Retorne somente JSON:
{
  "summary": "...",
  "recommendations": ["Alta: ...", "Media: ..."]
}
""".strip()


def build_report_prompt(repo_url: str, criteria: dict[str, dict], score: float, grade: str) -> str:
    return f"""
Repositorio: {repo_url}
Score final: {score}
Grade: {grade}
Resultados por criterio: {criteria}

Gere um resumo executivo e recomendacoes acionaveis.
Priorize itens que aumentem score, reduzem risco e melhoram manutencao.
""".strip()
