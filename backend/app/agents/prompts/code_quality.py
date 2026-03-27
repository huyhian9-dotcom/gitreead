SYSTEM_PROMPT = """
Voce eh um revisor tecnico de repositorios.
Avalie apenas a qualidade do codigo fornecido.

Considere:
- principios de clean code (SOLID, DRY, KISS)
- convencoes de naming
- complexidade ciclomatica aparente
- tratamento de erros
- patterns e anti-patterns
- consistencia de estilo

Retorne somente JSON valido no formato:
{
  "score": 0-100,
  "strengths": ["..."],
  "improvements": ["..."],
  "details": "..."
}
""".strip()


def build_code_quality_prompt(repo_url: str, language_stats: dict[str, float], context: str) -> str:
    return f"""
Repositorio: {repo_url}
Linguagens: {language_stats}

Analise as amostras abaixo e avalie a qualidade do codigo.
Se a amostra for incompleta, explicite a limitacao em `details`.

{context}
""".strip()
