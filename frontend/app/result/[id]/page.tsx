'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { getDivinationResult } from '@/lib/api'
import type { DivinationResult } from '@/lib/types'
import ThrowRecord from '@/components/ThrowRecord'
import HexagramDisplay from '@/components/HexagramDisplay'
import InterpretationPanel from '@/components/InterpretationPanel'
import FollowupChat from '@/components/FollowupChat'

export default function ResultPage() {
  const { id } = useParams<{ id: string }>()
  const [result, setResult] = useState<DivinationResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getDivinationResult(id)
      .then(setResult)
      .catch(() => setError('无法加载起卦结果，请检查链接是否正确'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <p className="text-stone-500 animate-pulse">加载卦象结果…</p>
      </div>
    )
  }

  if (error || !result) {
    return (
      <div className="max-w-lg mx-auto px-4 py-12 text-center">
        <p className="text-red-400">{error ?? '未找到起卦记录'}</p>
      </div>
    )
  }

  const hasChangingLines = result.changing_lines.length > 0

  return (
    <div className="max-w-2xl mx-auto px-4 py-12 space-y-8">
      {/* Question header */}
      <div className="text-center space-y-1">
        <p className="text-stone-500 text-sm">起卦问题</p>
        <p className="text-stone-200 font-medium text-lg">「{result.question}」</p>
        <p className="text-xs text-stone-600">
          {result.category}{result.timeframe ? ` · ${result.timeframe}` : ''}
        </p>
      </div>

      {/* Block 1: Throw record */}
      <section>
        <SectionTitle>抛掷记录</SectionTitle>
        <ThrowRecord lines={result.lines} />
      </section>

      {/* Block 2: Base hexagram */}
      {result.base_hexagram_data && (
        <section>
          <SectionTitle>本卦</SectionTitle>
          <HexagramDisplay
            hexagram={result.base_hexagram_data}
            lines={result.lines}
            changingLines={result.changing_lines}
            label="本卦"
          />
        </section>
      )}

      {/* Block 3: Changed hexagram (only if there are changing lines) */}
      <section>
        <SectionTitle>变卦</SectionTitle>
        {hasChangingLines && result.changed_hexagram_data ? (
          <HexagramDisplay
            hexagram={result.changed_hexagram_data}
            label="变卦"
          />
        ) : (
          <div className="bg-stone-800/40 rounded-xl p-5 border border-stone-700 text-center">
            <p className="text-stone-500 text-sm">
              本次无动爻，卦象稳定，变卦与本卦一致
            </p>
          </div>
        )}
      </section>

      {/* Block 4: AI interpretation (loads independently) */}
      <section>
        <SectionTitle>白话解读</SectionTitle>
        <InterpretationPanel divinationId={id} />
      </section>

      {/* Block 5: Followup chat */}
      <section>
        <SectionTitle>追问</SectionTitle>
        <FollowupChat divinationId={id} />
      </section>
    </div>
  )
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="text-xs text-stone-500 uppercase tracking-widest mb-3">{children}</h2>
  )
}
