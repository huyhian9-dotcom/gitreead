SYSTEM_PROMPT = """
Voce eh um revisor tecnico focado em documentacao de software.
Avalie:
- qualidade do README
- docstrings, comentarios estruturados ou JSDoc
- presenca de CHANGELOG, CONTRIBUTING e LICENSE
- clareza de instalacao, configuracao e uso
- exemplos e documentacao de API, quando fizer sentido

Responda somente em JSON:
{
  "score": 0-100,
  "strengths": ["..."],
  "improvements": ["..."],
  "details": "..."
}
""".strip()


def build_docs_prompt(repo_url: str, context: str) -> str:
    return f"""
Repositorio: {repo_url}

Avalie a documentacao com base nos artefatos abaixo.
Explique lacunas, qualidade da onboarding experience e riscos de ausencia de docs.

{context}
""".strip()
