# RepoAnalyzer Specs

## Objetivo

Implementar um analisador de repositorios GitHub com:

- FastAPI no backend
- LangGraph para orquestracao
- Claude Sonnet para analises
- React + Vite + TypeScript + Tailwind no frontend
- SSE para progresso em tempo real

## Ordem de implementacao

1. Scaffold do backend
2. Schemas Pydantic
3. State e grafo LangGraph
4. Servico GitHub
5. Nodes de fetch, parse, analise e score
6. Rotas FastAPI com SSE
7. Frontend React
8. Docker

## Requisitos funcionais

- Validar URL `https://github.com/owner/repo`
- Analisar no maximo 50 arquivos por repositorio
- Limitar conteudo de arquivo a 100KB para o LLM
- Rodar quatro analises em paralelo: codigo, docs, testes e seguranca
- Gerar score final ponderado e grade de `A+` a `F`
- Expor:
  - `POST /api/v1/analyze`
  - `GET /api/v1/analysis/{id}`
  - `GET /api/v1/analysis/{id}/stream`
  - `GET /api/v1/reports`
  - `GET /api/v1/health`

## Requisitos nao funcionais

- Error handling em todos os nodes
- Fallback com score 0 em caso de falha dura
- GitHub API via `httpx.AsyncClient`
- Modelo `claude-sonnet-4-20250514`
- Python 3.12+
- Node 20+
