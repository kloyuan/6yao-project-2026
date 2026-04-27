'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { getDivinationResult, submitLine } from '@/lib/api'
import type { DivinationLine } from '@/lib/types'
import CoinThrow from '@/components/CoinThrow'
import LineDisplay from '@/components/LineDisplay'

export default function DivinationPage() {
  const { id } = useParams<{ id: string }>()
  const router = useRouter()

  const [lines, setLines] = useState<DivinationLine[]>([])
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const currentLineNumber = lines.length + 1
  const isComplete = lines.length >= 6

  useEffect(() => {
    getDivinationResult(id)
      .then(result => {
        setQuestion(result.question)
        setLines(result.lines)
        if (result.lines.length >= 6) {
          router.replace(`/result/${id}`)
        }
      })
      .catch(() => setError('无法加载起卦记录，请刷新重试'))
      .finally(() => setLoading(false))
  }, [id, router])

  async function handleThrow(coinValues: number[]) {
    try {
      const result = await submitLine(id, currentLineNumber, coinValues)
      const newLine: DivinationLine = {
        line_number: result.line_number,
        coin_values: result.coin_values,
        coin_sum: result.coin_sum,
        line_type: result.line_type as DivinationLine['line_type'],
        is_changing: result.is_changing,
      }
      const updated = [...lines, newLine]
      setLines(updated)
      if (updated.length >= 6) {
        router.push(`/result/${id}`)
      }
    } catch {
      setError('提交失败，请重试')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <p className="text-stone-500 animate-pulse">加载中…</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-lg mx-auto px-4 py-12 text-center">
        <p className="text-red-400">{error}</p>
      </div>
    )
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-12 space-y-8">
      {/* Header */}
      <div className="text-center">
        <p className="text-stone-500 text-sm mb-1">起卦问题</p>
        <p className="text-stone-200 font-medium">「{question}」</p>
      </div>

      {/* Progress bar */}
      <div>
        <div className="flex justify-between text-xs text-stone-500 mb-1.5">
          <span>已完成 {lines.length} 爻</span>
          <span>共 6 爻</span>
        </div>
        <div className="h-1.5 bg-stone-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-amber-600 rounded-full transition-all duration-500"
            style={{ width: `${(lines.length / 6) * 100}%` }}
          />
        </div>
      </div>

      {/* Completed lines (read-only) */}
      {lines.length > 0 && (
        <div className="bg-stone-800/50 rounded-xl p-4 border border-stone-700 space-y-1">
          {lines.map(l => (
            <LineDisplay key={l.line_number} line={l} compact />
          ))}
        </div>
      )}

      {/* Coin throw for current line */}
      {!isComplete && (
        <div className="bg-stone-800/60 rounded-xl p-8 border border-amber-700/30">
          <CoinThrow lineNumber={currentLineNumber} onThrow={handleThrow} />
        </div>
      )}
    </div>
  )
}
