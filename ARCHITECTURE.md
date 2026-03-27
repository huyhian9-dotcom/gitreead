# RepoAnalyzer Architecture

## Stack

- Frontend: React + Vite + TypeScript + Tailwind CSS
- Backend: FastAPI
- Orquestracao: LangGraph
- LLM: Claude Sonnet via `langchain-anthropic`
- GitHub API: `httpx`
- Storage: dict in-memory

## Fluxo

```text
POST /analyze
  -> cria job em memoria
  -> LangGraph: fetch_repo -> parse_repo
  -> fan-out paralelo: analyze_code | analyze_docs | analyze_tests | analyze_security
  -> score_repo
  -> generate_report
  -> GET /analysis/{id} e SSE /analysis/{id}/stream
```

## Pesos

- Qualidade de codigo: 30%
- Documentacao: 20%
- Testes: 20%
- Seguranca: 15%
- Estrutura: 15%

## Estrutura de pastas

```text
backend/
  app/
    agents/
    models/
    routes/
    services/
frontend/
  src/
    api/
    components/
    hooks/
    pages/
    types/
```

## Principios

- Fan-out/fan-in no LangGraph para as analises paralelas
- SSE para feedback incremental no frontend
- Separacao clara entre dados de estado, nodes, prompts e servicos externos
- Frontend tipado espelhando os schemas do backend
