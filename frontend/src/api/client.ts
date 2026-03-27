import axios from 'axios'

import type { AnalysisListItem, AnalysisRequest, AnalysisResponse } from '../types'

export const API_BASE_URL = 'http://localhost:8000/api/v1'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export async function createAnalysis(payload: AnalysisRequest) {
  const response = await apiClient.post<{ id: string; status: string }>('/analyze', payload)
  return response.data
}

export async function fetchAnalysis(id: string) {
  const response = await apiClient.get<AnalysisResponse>(`/analysis/${id}`)
  return response.data
}

export async function fetchReports() {
  const response = await apiClient.get<AnalysisListItem[]>('/reports')
  return response.data
}
