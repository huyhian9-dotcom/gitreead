import type { ReactNode } from 'react'
import { Link, useParams } from 'react-router-dom'

import { AnalysisProgress } from '../components/AnalysisProgress'
import { ReportCard } from '../components/ReportCard'
import { ScoreGauge } from '../components/ScoreGauge'
import { useAnalysis } from '../hooks/useAnalysis'
import type { CriteriaKey, CriteriaResult } from '../types'

const CARD_META: Record<
  CriteriaKey,
  {
    title: string
    icon: ReactNode
  }
> = {
  code_quality: {
    title: 'Qualidade de Codigo',
    icon: (
      <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M8 8 4 12l4 4M16 8l4 4-4 4M13 5l-2 14" />
      </svg>
    ),
  },
  docs: {
    title: 'Documentacao',
    icon: (
      <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M6 4h9l3 3v13H6z" />
        <path d="M15 4v4h4M9 12h6M9 16h6" />
      </svg>
    ),
  },
  tests: {
    title: 'Testes',
    icon: (
      <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M9 3v6l-4 8a3 3 0 0 0 2.7 4.5h8.6A3 3 0 0 0 19 17l-4-8V3" />
        <path d="M9 7h6" />
      </svg>
    ),
  },
  security: {
    title: 'Seguranca',
    icon: (
      <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M12 3 5 6v5c0 5 3.4 8.5 7 10 3.6-1.5 7-5 7-10V6z" />
        <path d="M9.5 12.5 11 14l3.5-3.5" />
      </svg>
    ),
  },
  structure: {
    title: 'Estrutura',
    icon: (
      <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M4 5h7v6H4zM13 5h7v4h-7zM13 11h7v8h-7zM4 13h7v6H4z" />
      </svg>
    ),
  },
}

function reportCriteriaEntries(
  criteria: Partial<Record<CriteriaKey, CriteriaResult>> | null | undefined,
) {
  if (!criteria) {
    return []
  }

  return Object.entries(criteria) as [CriteriaKey, CriteriaResult][]
}

export function Report() {
  const { id } = useParams<{ id: string }>()
  const analysisState = useAnalysis(id ?? '')
  const analysis = analysisState.analysis

  if (!id) {
    return (
      <main className="px-4 py-10 sm:px-6">
        <div className="mx-auto max-w-3xl rounded-[2rem] border border-[var(--border)] bg-[var(--surface-strong)] p-8 shadow-[var(--shadow)]">
          <p className="text-lg text-[var(--muted)]">ID de relatorio invalido.</p>
        </div>
      </main>
    )
  }

  const criteriaEntries = reportCriteriaEntries(analysis?.criteria)

  return (
    <main className="px-4 py-6 sm:px-6 lg:px-10">
      <div className="mx-auto max-w-6xl">
        <header className="mb-6 flex flex-col gap-4 rounded-[2rem] border border-[var(--border)] bg-[var(--surface)] px-6 py-5 shadow-[var(--shadow)] md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--muted)]">
              Relatorio de analise
            </p>
            <h1 className="font-display mt-3 text-4xl font-bold text-[var(--ink)] md:text-5xl">
              {analysis?.repo_url ?? 'Carregando repositorio'}
            </h1>
          </div>

          <Link
            to="/"
            className="inline-flex items-center justify-center rounded-[1.3rem] border border-[var(--border)] bg-white/80 px-5 py-3 text-sm font-semibold uppercase tracking-[0.12em] text-[var(--ink)] transition hover:border-[rgba(15,118,110,0.3)] hover:text-[var(--teal)]"
          >
            Nova analise
          </Link>
        </header>

        {!analysis || analysis.status !== 'completed' ? (
          <AnalysisProgress
            status={analysisState.status}
            progress={analysisState.progress}
            error={analysisState.error}
          />
        ) : (
          <div className="space-y-8">
            <section className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
              <ScoreGauge score={analysis.score ?? 0} grade={analysis.grade ?? 'F'} size="lg" />

              <div className="rounded-[2rem] border border-[var(--border)] bg-[var(--surface-strong)] p-6 shadow-[var(--shadow)]">
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--muted)]">
                  Executive summary
                </p>
                <p className="mt-4 text-base leading-8 text-[var(--muted)]">
                  {analysis.summary ?? 'Resumo nao disponivel.'}
                </p>

                <div className="mt-8">
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--muted)]">
                    Recomendacoes priorizadas
                  </p>
                  <div className="mt-4 grid gap-3">
                    {(analysis.recommendations ?? []).length ? (
                      analysis.recommendations?.map((item) => (
                        <div
                          key={item}
                          className="rounded-[1.4rem] border border-[var(--border)] bg-white/70 px-4 py-4 text-sm leading-7 text-[var(--ink)]"
                        >
                          {item}
                        </div>
                      ))
                    ) : (
                      <p className="rounded-[1.4rem] border border-dashed border-[var(--border)] bg-white/60 px-4 py-4 text-sm text-[var(--muted)]">
                        Nenhuma recomendacao adicional foi retornada.
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </section>

            <section className="grid gap-6 lg:grid-cols-2">
              {criteriaEntries.map(([key, criteria]) => (
                <ReportCard
                  key={key}
                  title={CARD_META[key].title}
                  criteria={criteria}
                  icon={CARD_META[key].icon}
                />
              ))}
            </section>
          </div>
        )}
      </div>
    </main>
  )
}
