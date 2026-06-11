<h1 align="center">RepoAnalyzer 🔎</h1>

<p align="center">
  <b>Análise de repositórios do GitHub com IA · AI-powered GitHub repository analysis</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/LangGraph-1C3C3C?style=flat&logo=langchain&logoColor=white" alt="LangGraph">
  <img src="https://img.shields.io/badge/Claude-D97757?style=flat&logo=anthropic&logoColor=white" alt="Claude">
  <img src="https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black" alt="React">
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white" alt="TypeScript">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white" alt="Docker">
</p>

> Parte do meu portfólio · Part of my portfolio — [@huyhian9-dotcom](https://github.com/huyhian9-dotcom)

---

## 🇧🇷 O que faz

O **RepoAnalyzer** recebe um repositório do GitHub e roda um agente **LangGraph** sobre ele, produzindo:

- 🎯 **Score** e **nota (grade)** do projeto
- 💪 **Pontos fortes** e ⚠️ **pontos de melhoria**
- ✅ **Recomendações priorizadas** de próximos passos

É um projeto de IA aplicada: orquestração de LLM com grafo de estados (LangGraph), leitura assíncrona do GitHub e UI reativa para exibir o relatório.

## 🇺🇸 What it does

**RepoAnalyzer** takes a GitHub repository and runs a **LangGraph** agent over it, producing:

- 🎯 A project **score** and **grade**
- 💪 **Strengths** and ⚠️ **areas to improve**
- ✅ **Prioritized recommendations** for next steps

It's an applied-AI project: LLM orchestration with a state graph (LangGraph), async GitHub reads, and a reactive UI to render the report.

---

## 🧱 Stack

| Camada · Layer | Tech |
|---|---|
| Backend | FastAPI · LangGraph · Claude Sonnet |
| Frontend | React · Vite · TypeScript · Tailwind CSS |
| GitHub access | `httpx` async client |
| Storage | dict in-memory (MVP) |

📄 Mais detalhes em · More detail in [`ARCHITECTURE.md`](./ARCHITECTURE.md) e · and [`SPECS.md`](./SPECS.md).

---

## 🚀 Rodar localmente · Run locally

Copie as variáveis de ambiente · Copy the env vars: `cp .env.example .env` (preencha a chave da Anthropic · fill in the Anthropic key).

### Docker (recomendado · recommended)

```bash
docker compose up --build
```

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`

### Manual

```bash
# Backend
cd backend
python -m uvicorn app.main:app --reload   # http://localhost:8000

# Frontend
cd frontend
npm install
npm run dev
```
