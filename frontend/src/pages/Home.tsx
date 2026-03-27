import { startTransition, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { fetchReports } from '../api/client'
import { AnalyzeForm } from '../components/AnalyzeForm'
import type { AnalysisListItem } from '../types'

function statusBadge(status: AnalysisListItem['status']) {
  switch (status) {
    case 'completed':
      return 'bg-[rgba(15,118,110,0.12)] text-[var(--teal)]'
    case 'failed':
      return 'bg-[rgba(180,35,24,0.1)] text-[var(--red)]'
    default:
      return 'bg-[rgba(180,83,9,0.12)] text-[var(--amber)]'
  }
}

export function Home() {
  const [reports, setReports] = useState<AnalysisListItem[]>([])

  useEffect(() => {
    let mounted = true

    async function loadReports() {
      try {
        const response = await fetchReports()
        if (!mounted) {
          return
        }
        startTransition(() => {
          setReports(response)
        })
      } catch {
        if (mounted) {
          setReports([])
        }
      }
    }

    void loadReports()

    return () => {
      mounted = false
    }
  }, [])

  return (
    <main className="relative overflow-hidden px-4 py-6 sm:px-6 lg:px-10">
      <div className="mx-auto max-w-6xl">
        <section className="relative overflow-hidden rounded-[2.4rem] border border-[var(--border)] bg-[var(--surface)] px-6 py-8 shadow-[var(--shadow)] backdrop-blur md:px-10 md:py-12">
          <div className="absolute inset-y-0 right-0 hidden w-1/3 bg-[radial-gradient(circle_at_center,rgba(15,118,110,0.16),transparent_60%)] lg:block" />

          <div className="relative grid gap-8 lg:grid-cols-[1.15fr_0.85fr] lg:items-end">
            <div className="max-w-3xl">
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-[var(--muted)]">
                RepoAnalyzer
              </p>
              <h1 className="font-display mt-4 text-5xl font-bold leading-[0.96] text-[var(--ink)] sm:text-6xl lg:text-7xl">
                Analise a qualidade do seu repositorio GitHub
              </h1>
              <p className="mt-6 max-w-2xl text-lg leading-8 text-[var(--muted)]">
                Um painel de auditoria para arquitetura, documentacao, testes e seguranca,
                orquestrado com LangGraph e pronto para mostrar nota, grade e proxima acao.
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
              <div className="rounded-[1.7rem] border border-[var(--border)] bg-white/75 p-5">
                <p className="font-mono text-xs uppercase tracking-[0.22em] text-[var(--muted)]">
                  Estrategia
                </p>
                <p className="mt-3 text-2xl font-semibold text-[var(--ink)]">4 agentes em paralelo</p>
              </div>
              <div className="rounded-[1.7rem] border border-[var(--border)] bg-white/75 p-5">
                <p className="font-mono text-xs uppercase tracking-[0.22em] text-[var(--muted)]">
                  Cobertura
                </p>
                <p className="mt-3 text-2xl font-semibold text-[var(--ink)]">Codigo, docs, testes, seguranca</p>
              </div>
              <div className="rounded-[1.7rem] border border-[var(--border)] bg-white/75 p-5">
                <p className="font-mono text-xs uppercase tracking-[0.22em] text-[var(--muted)]">
                  Fluxo
                </p>
                <p className="mt-3 text-2xl font-semibold text-[var(--ink)]">SSE em tempo real</p>
              </div>
            </div>
          </div>

          <div className="relative mt-10 max-w-4xl">
            <AnalyzeForm />
          </div>
        </section>

        <section className="mt-8 rounded-[2.4rem] border border-[var(--border)] bg-[var(--surface)] p-6 shadow-[var(--shadow)] md:p-8">
          <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--muted)]">
                Historico
              </p>
              <h2 className="font-display mt-3 text-3xl font-bold text-[var(--ink)]">
                Analises recentes
              </h2>
            </div>
            <p className="max-w-2xl text-sm leading-7 text-[var(--muted)]">
              O armazenamento do MVP eh em memoria. Enquanto o backend estiver ativo, as analises
              continuam listadas aqui.
            </p>
          </div>

          <div className="mt-6 grid gap-4">
            {reports.length ? (
              reports.map((report) => (
                <Link
                  key={report.id}
                  to={`/report/${report.id}`}
                  className="group rounded-[1.8rem] border border-[var(--border)] bg-white/70 p-5 transition hover:-translate-y-0.5 hover:border-[rgba(15,118,110,0.25)]"
                >
                  <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                    <div className="min-w-0">
                      <p className="truncate font-semibold text-[var(--ink)]">{report.repo_url}</p>
                      <p className="mt-1 font-mono text-xs uppercase tracking-[0.18em] text-[var(--muted)]">
                        Criado em {new Date(report.created_at).toLocaleString('pt-BR')}
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      <span
                        className={`inline-flex rounded-full px-3 py-2 text-xs font-semibold uppercase tracking-[0.14em] ${statusBadge(report.status)}`}
                      >
                        {report.status}
                      </span>
                      {typeof report.score === 'number' ? (
                        <span className="font-mono text-sm font-semibold text-[var(--ink)]">
                          {Math.round(report.score)} / {report.grade ?? '--'}
                        </span>
                      ) : (
                        <span className="font-mono text-sm text-[var(--muted)]">Em andamento</span>
                      )}
                    </div>
                  </div>
                </Link>
              ))
            ) : (
              <div className="rounded-[1.8rem] border border-dashed border-[var(--border)] bg-white/55 px-5 py-10 text-center text-[var(--muted)]">
                Nenhuma analise recente encontrada ainda.
              </div>
            )}
          </div>
        </section>
      </div>
    </main>
  )
}
