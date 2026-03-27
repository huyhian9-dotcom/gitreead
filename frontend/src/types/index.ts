export type AnalysisStatus =
  | 'pending'
  | 'fetching'
  | 'parsing'
  | 'analyzing'
  | 'scoring'
  | 'completed'
  | 'failed'

export type Grade = 'A+' | 'A' | 'B' | 'C' | 'D' | 'F'
export type CriteriaKey = 'code_quality' | 'docs' | 'tests' | 'security' | 'structure'

export interface AnalysisRequest {
  repo_url: string
  branch?: string
}

export interface CriteriaResult {
  score: number
  weight: number
  strengths: string[]
  improvements: string[]
  details: string
}

export interface AnalysisResponse {
  id: string
  repo_url: string
  status: AnalysisStatus
  score?: number | null
  grade?: Grade | null
  summary?: string | null
  criteria?: Partial<Record<CriteriaKey, CriteriaResult>> | null
  recommendations?: string[] | null
  created_at: string
  completed_at?: string | null
  error?: string | null
}

export interface AnalysisListItem {
  id: string
  repo_url: string
  status: AnalysisStatus
  score?: number | null
  grade?: Grade | null
  created_at: string
}

export interface StreamEvent {
  event: 'status_update' | 'criteria_complete' | 'analysis_complete'
  data: Record<string, unknown>
}

export interface ProgressStep {
  key: string
  label: string
  state: 'pending' | 'in_progress' | 'completed'
  score?: number
}
