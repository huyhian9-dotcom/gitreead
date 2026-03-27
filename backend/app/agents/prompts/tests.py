SYSTEM_PROMPT = """
Voce eh um revisor tecnico focado em estrategia de testes.
Avalie:
- existencia de testes
- proporcao entre testes e codigo
- qualidade das assercoes, mocks e edge cases
- presenca de CI/CD para executar testes
- frameworks utilizados
- cobertura estimada

Retorne apenas JSON:
{
  "score": 0-100,
  "strengths": ["..."],
  "improvements": ["..."],
  "details": "..."
}
""".strip()


def build_tests_prompt(repo_url: str, context: str) -> str:
    return f"""
Repositorio: {repo_url}

Analise a maturidade de testes com base no material abaixo.
Quando necessario, estime cobertura ou profundidade a partir de sinais indiretos.

{context}
""".strip()
