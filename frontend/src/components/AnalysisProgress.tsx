import type { AnalysisStatus, ProgressStep } from '../types'

interface AnalysisProgressProps {
  status: AnalysisStatus
  progress: ProgressStep[]
  error?: string | null
}

function statusCopy(status: AnalysisStatus) {
  switch (status) {
    case 'pending':
      return 'Aguardando o job local ser disparado.'
    case 'fetching':
      return 'Buscando metadados, linguagens e arvore do repositorio.'
    case 'parsing':
      return 'Selecionando arquivos relevantes e extraindo dependencias.'
    case 'analyzing':
      return 'Rodando agentes em paralelo para codigo, docs, testes e seguranca.'
    case 'scoring':
      return 'Consolidando pesos, score final e relatorio.'
    case 'completed':
      return 'Analise concluida.'
    case 'failed':
      return 'A analise falhou antes de completar todas as etapas.'
  }
}

function StepIndicator({ state }: { state: ProgressStep['state'] }) {
  if (state === 'completed') {
    return (
      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[rgba(15,118,110,0.14)] text-[var(--teal)]">
        <svg viewBox="0 0 20 20" className="h-5 w-5" fill="currentColor" aria-hidden="true">
          <path
            fillRule="evenodd"
            d="M16.7 5.3a1 1 0 0 1 0 1.4l-7.1 7.1a1 1 0 0 1-1.4 0L3.3 8.9a1 1 0 1 1 1.4-1.4l4.2 4.2 6.4-6.4a1 1 0 0 1 1.4 0Z"
            clipRule="evenodd"
          />
        </svg>
      </div>
    )
  }

  if (state === 'in_progress') {
    return (
      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[rgba(180,83,9,0.12)]">
        <span className="animate-pulse-dot h-3 w-3 rounded-full bg-[var(--amber)]" />
      </div>
    )
  }

  return <div className="h-10 w-10 rounded-full border border-[var(--border)] bg-white/40" />
}

export function AnalysisProgress({ status, progress, error }: AnalysisProgressProps) {
  return (
    <section className="rounded-[2rem] border border-[var(--border)] bg-[var(--surface-strong)] p-6 shadow-[var(--shadow)] md:p-8">
      <div className="mb-8">
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--muted)]">
          Progresso em tempo real
        </p>
        <h2 className="font-display mt-3 text-3xl font-bold text-[var(--ink)] md:text-4xl">
          {statusCopy(status)}
        </h2>
      </div>

      <div className="space-y-6">
        {progress.map((step, index) => (
          <div key={step.key} className="flex gap-4">
            <div className="flex flex-col items-center">
              <StepIndicator state={step.state} />
              {index < progress.length - 1 ? (
                <div className="mt-2 h-12 w-px bg-[rgba(19,37,26,0.1)]" />
              ) : null}
            </div>
            <div className="pt-1">
              <p className="font-semibold text-[var(--ink)]">{step.label}</p>
              <p className="mt-1 text-sm text-[var(--muted)]">
                {step.state === 'completed'
                  ? 'Etapa concluida.'
                  : step.state === 'in_progress'
                    ? 'Processando agora.'
                    : 'Aguardando dependencias anteriores.'}
              </p>
              {typeof step.score === 'number' ? (
                <p className="mt-2 font-mono text-xs uppercase tracking-[0.18em] text-[var(--muted)]">
                  Score parcial {Math.round(step.score)}
                </p>
              ) : null}
            </div>
          </div>
        ))}
      </div>

      {error ? (
        <p className="mt-8 rounded-[1.5rem] border border-[rgba(180,35,24,0.16)] bg-[rgba(180,35,24,0.08)] px-4 py-4 text-sm text-[var(--red)]">
          {error}
        </p>
      ) : null}
    </section>
  )
}
