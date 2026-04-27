'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { createDivination } from '@/lib/api'
import { v4 as uuidv4 } from 'uuid'

const CATEGORIES = ['感情', '事业', '财运', '学业', '合作', '健康', '寻物', '其他']
const TIMEFRAMES = ['', '一周内', '一个月内', '三个月内', '半年内', '一年内']

function getSessionToken(): string {
  if (typeof window === 'undefined') return uuidv4()
  const key = 'liu_yao_session'
  let token = localStorage.getItem(key)
  if (!token) {
    token = uuidv4()
    localStorage.setItem(key, token)
  }
  return token
}

export default function QuestionForm() {
  const router = useRouter()
  const [question, setQuestion] = useState('')
  const [category, setCategory] = useState('其他')
  const [timeframe, setTimeframe] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const canSubmit = question.trim().length > 0 && !isSubmitting

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!canSubmit) return
    setIsSubmitting(true)
    setError(null)
    try {
      const { divination_id } = await createDivination({
        question: question.trim(),
        category,
        timeframe: timeframe || undefined,
        session_token: getSessionToken(),
      })
      router.push(`/divination/${divination_id}`)
    } catch (err) {
      setError('提交失败，请检查网络连接后重试')
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-xl mx-auto">
      <div>
        <label className="block text-sm text-stone-400 mb-2">
          你想问什么？<span className="text-red-400 ml-1">*</span>
        </label>
        <textarea
          value={question}
          onChange={e => setQuestion(e.target.value)}
          placeholder="请用一句话描述你的问题，例如：我这次的投资项目能否顺利推进？"
          rows={3}
          className="w-full bg-stone-800 border border-stone-600 rounded-lg px-4 py-3
                     text-stone-100 placeholder-stone-500 resize-none
                     focus:outline-none focus:border-amber-600 transition-colors"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm text-stone-400 mb-2">关注方向</label>
          <select
            value={category}
            onChange={e => setCategory(e.target.value)}
            className="w-full bg-stone-800 border border-stone-600 rounded-lg px-3 py-2.5
                       text-stone-100 focus:outline-none focus:border-amber-600 transition-colors"
          >
            {CATEGORIES.map(c => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm text-stone-400 mb-2">时间范围（可选）</label>
          <select
            value={timeframe}
            onChange={e => setTimeframe(e.target.value)}
            className="w-full bg-stone-800 border border-stone-600 rounded-lg px-3 py-2.5
                       text-stone-100 focus:outline-none focus:border-amber-600 transition-colors"
          >
            <option value="">不限</option>
            {TIMEFRAMES.filter(Boolean).map(t => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
      </div>

      {error && (
        <p className="text-red-400 text-sm">{error}</p>
      )}

      <button
        type="submit"
        disabled={!canSubmit}
        className="w-full py-3 rounded-lg font-medium text-base transition-all
                   bg-amber-700 hover:bg-amber-600 text-white
                   disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {isSubmitting ? '提交中…' : '开始起卦'}
      </button>
    </form>
  )
}
