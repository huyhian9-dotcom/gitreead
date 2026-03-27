import { useEffect, useMemo, useState } from 'react'

interface ScoreGaugeProps {
  score: number
  grade: string
  size?: 'sm' | 'md' | 'lg'
}

const SIZE_MAP = {
  sm: 120,
  md: 168,
  lg: 252,
} as const

function toneForScore(score: number) {
  if (score >= 80) {
    return {
      stroke: '#0f766e',
      glow: 'rgba(15, 118, 110, 0.25)',
      label: 'Forte',
    }
  }
  if (score >= 60) {
    return {
      stroke: '#b45309',
      glow: 'rgba(180, 83, 9, 0.25)',
      label: 'Estavel',
    }
  }
  return {
    stroke: '#b42318',
    glow: 'rgba(180, 35, 24, 0.22)',
    label: 'Critico',
  }
}

export function ScoreGauge({ score, grade, size = 'md' }: ScoreGaugeProps) {
  const [animatedScore, setAnimatedScore] = useState(0)
  const dimension = SIZE_MAP[size]
  const strokeWidth = size === 'lg' ? 16 : 12
  const radius = dimension / 2 - strokeWidth
  const circumference = 2 * Math.PI * radius
  const tone = useMemo(() => toneForScore(score), [score])

  useEffect(() => {
    const id = window.requestAnimationFrame(() => setAnimatedScore(score))
    return () => window.cancelAnimationFrame(id)
  }, [score])

  return (
    <div
      className="relative flex flex-col items-center justify-center gap-4 rounded-[2rem] border border-[var(--border)] bg-[var(--surface-strong)] p-6 shadow-[var(--shadow)]"
      style={{ boxShadow: `0 30px 80px ${tone.glow}` }}
    >
      <div className="relative" style={{ width: dimension, height: dimension }}>
        <svg
          width={dimension}
          height={dimension}
          viewBox={`0 0 ${dimension} ${dimension}`}
          className="-rotate-90"
        >
          <circle
            cx={dimension / 2}
            cy={dimension / 2}
            r={radius}
            fill="none"
            stroke="rgba(19, 37, 26, 0.08)"
            strokeWidth={strokeWidth}
          />
          <circle
            cx={dimension / 2}
            cy={dimension / 2}
            r={radius}
            fill="none"
            stroke={tone.stroke}
            strokeLinecap="round"
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={circumference - (circumference * animatedScore) / 100}
            style={{ transition: 'stroke-dashoffset 1s ease' }}
          />
        </svg>

        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="font-mono text-xs uppercase tracking-[0.22em] text-[var(--muted)]">
            Score
          </span>
          <strong className="mt-1 font-mono text-4xl text-[var(--ink)] md:text-5xl">
            {Math.round(score)}
          </strong>
          <span className="mt-1 text-sm font-semibold uppercase tracking-[0.18em]" style={{ color: tone.stroke }}>
            {tone.label}
          </span>
        </div>
      </div>

      <div className="text-center">
        <p className="text-xs uppercase tracking-[0.2em] text-[var(--muted)]">Grade</p>
        <p className="font-display mt-1 text-3xl font-bold text-[var(--ink)]">{grade}</p>
      </div>
    </div>
  )
}
