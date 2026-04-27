import type {
  DivinationResult,
  Interpretation,
  FollowupHistory,
  FollowupSendResponse,
} from './types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    const msg = body?.detail || `HTTP ${res.status}`
    const err = new Error(msg) as Error & { status: number }
    err.status = res.status
    throw err
  }
  return res.json()
}

export function createDivination(data: {
  question: string
  category: string
  timeframe?: string
  session_token: string
}): Promise<{ divination_id: string }> {
  return req('/divinations', { method: 'POST', body: JSON.stringify(data) })
}

export function submitLine(
  divination_id: string,
  line_number: number,
  coin_values: number[],
): Promise<{
  line_number: number
  coin_values: number[]
  coin_sum: number
  line_type: string
  is_changing: boolean
}> {
  return req(`/divinations/${divination_id}/lines`, {
    method: 'POST',
    body: JSON.stringify({ line_number, coin_values }),
  })
}

export function getDivinationResult(divination_id: string): Promise<DivinationResult> {
  return req(`/divinations/${divination_id}/result`)
}

export function postInterpret(divination_id: string): Promise<Interpretation> {
  return req(`/divinations/${divination_id}/interpret`, { method: 'POST' })
}

export function sendFollowup(
  divination_id: string,
  message: string,
): Promise<FollowupSendResponse> {
  return req(`/divinations/${divination_id}/followup`, {
    method: 'POST',
    body: JSON.stringify({ message }),
  })
}

export function getFollowupHistory(divination_id: string): Promise<FollowupHistory> {
  return req(`/divinations/${divination_id}/followup`)
}
