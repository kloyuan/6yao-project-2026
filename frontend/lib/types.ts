export interface DivinationLine {
  line_number: number
  coin_values: number[]
  coin_sum: number
  line_type: '老阴' | '少阳' | '少阴' | '老阳'
  is_changing: boolean
}

export interface HexagramData {
  hexagram_id: number
  name: string
  trigrams: string[]
  binary_code: string
  palace: string
  world_line: number
  response_line: number
  fortune_level: number
  meaning: string
}

export interface DivinationResult {
  divination_id: string
  question: string
  category: string
  timeframe: string | null
  base_hexagram: number | null
  changed_hexagram: number | null
  changing_lines: number[]
  lines: DivinationLine[]
  base_hexagram_data: HexagramData | null
  changed_hexagram_data: HexagramData | null
}

export interface Interpretation {
  divination_id: string
  summary: string | null
  base_reading: string | null
  changing_lines_analysis: string | null
  changed_hexagram_trend: string | null
  category_advice: string | null
  action_advice: string[] | null
  generated_by: string
  provider: string | null
  error?: string | null
}

export interface FollowupMessage {
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export interface FollowupHistory {
  messages: FollowupMessage[]
  rounds_used: number
  rounds_limit: number
}

export interface FollowupSendResponse {
  content: string
  source_note: string
  rounds_used: number
  rounds_limit: number
}
