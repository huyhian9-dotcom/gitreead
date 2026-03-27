import { startTransition, useEffect, useEffectEvent, useState } from 'react'

import { API_BASE_URL, fetchAnalysis } from '../api/client'
import type {
  AnalysisResponse,
  AnalysisStatus,
  CriteriaKey,
  ProgressStep,
} from '../types'

function extractScores(analysis: AnalysisResponse | null) {
  const scores: Partial<Record<CriteriaKey, number>> = {}
  if (!analysis?.criteria) {
    return scores
  }

  for (const [key, value] of Object.entries(analysis.criteria)) {
    if (value?.score !== undefined) {
      scores[key as CriteriaKey] = value.score
    }
  }

  return scores
}

function stepState(
  condition: {
    completed: boolean
    inProgress: boolean
  },
): ProgressStep['state'] {
  if (condition.completed) {
    return 'completed'
  }
  if (condition.inProgress) {
    return 'in_progress'
  }
  return 'pending'
}

function buildProgress(
  status: AnalysisStatus,
  partialResults: Partial<Record<CriteriaKey, number>>,
): ProgressStep[] {
  return [
    {
      key: 'fetch',
      label: 'Buscando repositorio...',
      state: stepState({
        completed: ['parsing', 'analyzing', 'scoring', 'completed', 'failed'].includes(status),
        inProgress: status === 'fetching',
      }),
    },
    {
      key: 'parse',
      label: 'Analisando estrutura...',
      state: stepState({
        completed: ['analyzing', 'scoring', 'completed', 'failed'].includes(status),
        inProgress: status === 'parsing',
      }),
    },
    {
      key: 'code_quality',
      label: 'Analisando qualidade de codigo...',
      state: stepState({
        completed: partialResults.code_quality !== undefined,
        inProgress:
          partialResults.code_quality === undefined &&
          ['analyzing', 'scoring', 'completed', 'failed'].includes(status),
      }),
      score: partialResults.code_quality,
    },
    {
      key: 'docs',
      label: 'Analisando documentacao...',
      state: stepState({
        completed: partialResults.docs !== undefined,
        inProgress:
          partialResults.docs === undefined &&
          ['analyzing', 'scoring', 'completed', 'failed'].includes(status),
      }),
      score: partialResults.docs,
    },
    {
      key: 'tests',
      label: 'Analisando testes...',
      state: stepState({
        completed: partialResults.tests !== undefined,
        inProgress:
          partialResults.tests === undefined &&
          ['analyzing', 'scoring', 'completed', 'failed'].includes(status),
      }),
      score: partialResults.tests,
    },
    {
      key: 'security',
      label: 'Analisando seguranca...',
      state: stepState({
        completed: partialResults.security !== undefined,
        inProgress:
          partialResults.security === undefined &&
          ['analyzing', 'scoring', 'completed', 'failed'].includes(status),
      }),
      score: partialResults.security,
    },
    {
      key: 'score',
      label: 'Calculando nota final...',
      state: stepState({
        completed: status === 'completed',
        inProgress: status === 'scoring',
      }),
      score: partialResults.structure,
    },
  ]
}

export function useAnalysis(id: string) {
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null)
  const [partialResults, setPartialResults] = useState<Partial<Record<CriteriaKey, number>>>({})
  const [error, setError] = useState<string | null>(null)

  const syncAnalysis = useEffectEvent(async () => {
    try {
      const response = await fetchAnalysis(id)
      startTransition(() => {
        setAnalysis(response)
        setPartialResults((current) => ({ ...current, ...extractScores(response) }))
        setError(response.error ?? null)
      })
    } catch {
      setError('Nao foi possivel carregar o status atual da analise.')
    }
  })

  useEffect(() => {
    if (!id) {
      return
    }

    let disposed = false
    void syncAnalysis()

    const source = new EventSource(`${API_BASE_URL}/analysis/${id}/stream`)

    source.addEventListener('status_update', (event) => {
      if (disposed) {
        return
      }

      const payload = JSON.parse(event.data) as { status?: AnalysisStatus }
      startTransition(() => {
        setAnalysis((current) =>
          current
            ? {
                ...current,
                status: payload.status ?? current.status,
              }
            : current,
        )
      })

      if (payload.status === 'completed' || payload.status === 'failed') {
        void syncAnalysis()
      }
    })

    source.addEventListener('criteria_complete', (event) => {
      if (disposed) {
        return
      }

      const payload = JSON.parse(event.data) as {
        criteria?: CriteriaKey
        score?: number
      }

      if (payload.criteria && typeof payload.score === 'number') {
        startTransition(() => {
          setPartialResults((current) => ({
            ...current,
            [payload.criteria as CriteriaKey]: payload.score,
          }))
        })
      }

      void syncAnalysis()
    })

    source.addEventListener('analysis_complete', () => {
      if (!disposed) {
        void syncAnalysis()
      }
      source.close()
    })

    source.onerror = () => {
      source.close()
      if (!disposed) {
        void syncAnalysis()
      }
    }

    return () => {
      disposed = true
      source.close()
    }
  }, [id, syncAnalysis])

  const status = analysis?.status ?? 'pending'
  const progress = buildProgress(status, partialResults)
  const isComplete = status === 'completed' || status === 'failed'

  return {
    analysis,
    status,
    progress,
    partialResults,
    isComplete,
    error,
  }
}
