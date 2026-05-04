'use client'

import { useEffect, useState } from 'react'
import { postInterpret } from '@/lib/api'
import type { Interpretation } from '@/lib/types'

interface Props {
  divinationId: string
}

export default function InterpretationPanel({ divinationId }: Props) {
  const [interp, setInterp] = useState<Interpretation | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    postInterpret(divinationId)
      .then(setInterp)
      .catch(() => setInterp({ divination_id: divinationId, error: '网络错误，无法获取解读', generated_by: 'ai' } as Interpretation))
      .finally(() => setLoading(false))
  }, [divinationId])

  if (loading) {
    return (
      <div className="bg-stone-800/60 rounded-xl p-6 border border-stone-700 text-center">
        <p className="text-stone-400 animate-pulse">AI 正在解读卦象，请稍候…</p>
      </div>
    )
  }

  if (interp?.error) {
    return (
      <div className="bg-stone-800/60 rounded-xl p-6 border border-red-800/40">
        <p className="text-red-400 text-sm">{interp.error}</p>
      </div>
    )
  }

  if (!interp) return null

  return (
    <div className="bg-stone-800/60 rounded-xl border border-stone-700 divide-y divide-stone-700/50">
      <Section title="总体解读" content={interp.summary} />
      <Section title="本卦详解" content={interp.base_reading} />

      {interp.changing_lines_analysis && (
        <Section title="动爻分析" content={interp.changing_lines_analysis} />
      )}
      {interp.changed_hexagram_trend && (
        <Section title="变卦趋势" content={interp.changed_hexagram_trend} />
      )}

      <Section title="方向建议" content={interp.category_advice} />

      {interp.action_advice && interp.action_advice.length > 0 && (
        <div className="p-5">
          <h4 className="text-amber-500 text-sm font-medium mb-3">行动建议</h4>
          <ol className="space-y-2">
            {interp.action_advice.map((tip, i) => (
              <li key={i} className="flex gap-3 text-sm text-stone-300">
                <span className="text-amber-600 shrink-0">{i + 1}.</span>
                <span>{tip}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      <div className="px-5 py-2 text-xs text-stone-600">
        解读由 AI（{interp.provider ?? 'claude'}）生成，仅供参考
      </div>
    </div>
  )
}

function Section({ title, content }: { title: string; content?: string | null }) {
  if (!content) return null
  return (
    <div className="p-5">
      <h4 className="text-amber-500 text-sm font-medium mb-2">{title}</h4>
      <p className="text-stone-300 text-sm leading-relaxed">{content}</p>
    </div>
  )
}
