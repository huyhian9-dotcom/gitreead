import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'

import { createAnalysis } from '../api/client'

const GITHUB_REPO_URL_PATTERN =
  /^https:\/\/github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+(?:\.git)?\/?$/

export function AnalyzeForm() {
  const navigate = useNavigate()
  const [repoUrl, setRepoUrl] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const trimmed = repoUrl.trim()

    if (!GITHUB_REPO_URL_PATTERN.test(trimmed)) {
      setError('Informe uma URL valida no formato https://github.com/owner/repo')
      return
    }

    setError(null)
    setIsSubmitting(true)
    try {
      const response = await createAnalysis({ repo_url: trimmed })
      navigate(`/report/${response.id}`)
    } catch {
      setError('Nao foi possivel iniciar a analise agora. Tente novamente em alguns instantes.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="animate-rise-in w-full rounded-[2rem] border border-[var(--border)] bg-[var(--surface-strong)] p-4 shadow-[var(--shadow)] backdrop-blur md:p-6"
    >
      <div className="flex flex-col gap-4 md:flex-row md:items-end">
        <label className="flex-1">
          <span className="mb-2 block text-sm font-medium uppercase tracking-[0.18em] text-[var(--muted)]">
            Repositorio GitHub
          </span>
          <div className="flex items-center gap-3 rounded-[1.4rem] border border-[var(--border)] bg-white/80 px-4 py-4">
            <svg
              viewBox="0 0 24 24"
              className="h-5 w-5 flex-none text-[var(--teal)]"
              fill="currentColor"
              aria-hidden="true"
            >
              <path d="M12 .5A12 12 0 0 0 8.2 23.9c.6.1.8-.2.8-.6v-2.2c-3.3.7-4-1.4-4-1.4-.6-1.3-1.4-1.7-1.4-1.7-1.1-.8.1-.8.1-.8 1.2.1 1.8 1.2 1.8 1.2 1.1 1.8 2.8 1.3 3.5 1 .1-.8.4-1.3.8-1.6-2.6-.3-5.3-1.3-5.3-5.8 0-1.3.5-2.4 1.2-3.3-.1-.3-.5-1.5.1-3.1 0 0 1-.3 3.4 1.2a11.7 11.7 0 0 1 6.2 0c2.4-1.5 3.4-1.2 3.4-1.2.6 1.6.2 2.8.1 3.1.8.9 1.2 2 1.2 3.3 0 4.5-2.7 5.5-5.4 5.8.4.3.8 1 .8 2.1v3.1c0 .4.2.7.8.6A12 12 0 0 0 12 .5Z" />
            </svg>
            <input
              value={repoUrl}
              onChange={(event) => setRepoUrl(event.target.value)}
              placeholder="https://github.com/owner/repo"
              className="w-full bg-transparent text-base text-[var(--ink)] outline-none placeholder:text-[var(--muted)]"
              autoComplete="off"
              spellCheck={false}
            />
          </div>
        </label>

        <button
          type="submit"
          disabled={isSubmitting}
          className="inline-flex min-w-[10rem] items-center justify-center rounded-[1.3rem] bg-[var(--ink)] px-6 py-4 text-sm font-semibold uppercase tracking-[0.14em] text-[var(--paper-strong)] transition hover:bg-[var(--teal)] disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSubmitting ? 'Analisando...' : 'Analisar'}
        </button>
      </div>

      <div className="mt-3 flex flex-col gap-2 text-sm text-[var(--muted)] md:flex-row md:items-center md:justify-between">
        <p>Limites do MVP: ate 50 arquivos e 100KB por arquivo enviado ao modelo.</p>
        <p className="font-mono text-xs uppercase tracking-[0.16em]">Claude Sonnet 4 + LangGraph</p>
      </div>

      {error ? (
        <p className="mt-4 rounded-2xl border border-[rgba(180,35,24,0.18)] bg-[rgba(180,35,24,0.08)] px-4 py-3 text-sm text-[var(--red)]">
          {error}
        </p>
      ) : null}
    </form>
  )
}
