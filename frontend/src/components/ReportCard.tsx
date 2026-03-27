import { useState } from 'react'
import type { ReactNode } from 'react'

import type { CriteriaResult } from '../types'

interface ReportCardProps {
  title: string
  criteria: CriteriaResult
  icon?: ReactNode
}

function barColor(score: number) {
  if (score >= 80) {
    return 'bg-[var(--teal)]'
  }
  if (score >= 60) {
    return 'bg-[var(--amber)]'
  }
  return 'bg-[var(--red)]'
}

export function ReportCard({ title, criteria, icon }: ReportCardProps) {
  const [expanded, setExpanded] = useState(false)

  return (
    <article className="rounded-[2rem] border border-[var(--border)] bg-[var(--surface)] p-6 shadow-[var(--shadow)] backdrop-blur">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/80 text-[var(--ink)]">
            {icon}
          </div>
          <div>
            <h3 className="font-display text-xl font-bold text-[var(--ink)]">{title}</h3>
            <p className="text-sm text-[var(--muted)]">
              Peso {(criteria.weight * 100).toFixed(0)}% na nota final
            </p>
          </div>
        </div>
        <div className="text-right">
          <p className="font-mono text-2xl font-semibold text-[var(--ink)]">
            {criteria.score.toFixed(0)}
          </p>
          <p className="text-xs uppercase tracking-[0.16em] text-[var(--muted)]">Score</p>
        </div>
      </div>

      <div className="mt-5 h-3 rounded-full bg-[rgba(19,37,26,0.08)]">
        <div
          className={`h-3 rounded-full transition-[width] duration-700 ${barColor(criteria.score)}`}
          style={{ width: `${criteria.score}%` }}
        />
      </div>

      <div className="mt-5 grid gap-5 md:grid-cols-2">
        <section>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--muted)]">
            Pontos fortes
          </p>
          <ul className="mt-3 space-y-2 text-sm text-[var(--ink)]">
            {criteria.strengths.length ? (
              criteria.strengths.map((item) => (
                <li key={item} className="flex gap-2">
                  <span className="mt-1 h-2 w-2 rounded-full bg-[var(--teal)]" />
                  <span>{item}</span>
                </li>
              ))
            ) : (
              <li className="text-[var(--muted)]">Sem pontos fortes destacados nesta amostra.</li>
            )}
          </ul>
        </section>

        <section>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--muted)]">
            Melhorias
          </p>
          <ul className="mt-3 space-y-2 text-sm text-[var(--ink)]">
            {criteria.improvements.length ? (
              criteria.improvements.map((item) => (
                <li key={item} className="flex gap-2">
                  <span className="mt-1 h-2 w-2 rounded-full bg-[var(--amber)]" />
                  <span>{item}</span>
                </li>
              ))
            ) : (
              <li className="text-[var(--muted)]">Nenhuma melhoria critica foi destacada.</li>
            )}
          </ul>
        </section>
      </div>

      <button
        type="button"
        onClick={() => setExpanded((current) => !current)}
        className="mt-5 inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.12em] text-[var(--ink)]"
      >
        <span>{expanded ? 'Ocultar detalhes' : 'Ver detalhes'}</span>
        <span aria-hidden="true">{expanded ? '−' : '+'}</span>
      </button>

      {expanded ? (
        <p className="mt-4 rounded-[1.5rem] border border-[var(--border)] bg-white/70 px-4 py-4 text-sm leading-7 text-[var(--muted)]">
          {criteria.details}
        </p>
      ) : null}
    </article>
  )
}
