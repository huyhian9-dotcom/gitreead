# RepoAnalyzer

RepoAnalyzer analisa repositorios GitHub com FastAPI, LangGraph e React, produzindo score, grade, pontos fortes, melhorias e recomendacoes priorizadas.

## Stack

- Backend: FastAPI + LangGraph + Claude Sonnet
- Frontend: React + Vite + TypeScript + Tailwind CSS
- GitHub access: `httpx` async client
- Storage: dict in-memory para o MVP

## Desenvolvimento

### Backend

```bash
cd backend
python -m uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Docker

```bash
docker compose up --build
```

Frontend: `http://localhost:3000`

Backend: `http://localhost:8000`
