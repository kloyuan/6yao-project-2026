'use client'

import { useEffect, useRef, useState } from 'react'
import { sendFollowup, getFollowupHistory } from '@/lib/api'
import type { FollowupMessage } from '@/lib/types'

interface Props {
  divinationId: string
}

export default function FollowupChat({ divinationId }: Props) {
  const [messages, setMessages] = useState<FollowupMessage[]>([])
  const [roundsUsed, setRoundsUsed] = useState(0)
  const [roundsLimit] = useState(20)
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    getFollowupHistory(divinationId).then(data => {
      setMessages(data.messages)
      setRoundsUsed(data.rounds_used)
    })
  }, [divinationId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const isLimitReached = roundsUsed >= roundsLimit
  const canSend = input.trim().length > 0 && !sending && !isLimitReached

  async function handleSend() {
    if (!canSend) return
    const msg = input.trim()
    setInput('')
    setSending(true)
    setError(null)

    setMessages(prev => [...prev, { role: 'user', content: msg, created_at: new Date().toISOString() }])

    try {
      const res = await sendFollowup(divinationId, msg)
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: res.content, created_at: new Date().toISOString() },
      ])
      setRoundsUsed(res.rounds_used)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : '发送失败，请重试'
      setError(message)
      setMessages(prev => prev.slice(0, -1))
    } finally {
      setSending(false)
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="bg-stone-800/60 rounded-xl border border-stone-700 flex flex-col">
      <div className="flex items-center justify-between px-5 py-3 border-b border-stone-700">
        <h3 className="text-amber-500 font-medium">追问</h3>
        <span className="text-xs text-stone-500">{roundsUsed} / {roundsLimit} 轮</span>
      </div>

      {/* Message list */}
      <div className="flex-1 overflow-y-auto max-h-96 p-4 space-y-4">
        {messages.length === 0 && (
          <p className="text-stone-500 text-sm text-center py-4">
            解读完成后可在此继续追问，最多 {roundsLimit} 轮
          </p>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[80%] rounded-xl px-4 py-2.5 text-sm leading-relaxed
                ${m.role === 'user'
                  ? 'bg-amber-700/60 text-amber-50'
                  : 'bg-stone-700 text-stone-200'}`}
            >
              <p className="whitespace-pre-wrap">{m.content}</p>
            </div>
          </div>
        ))}

        {sending && (
          <div className="flex justify-start">
            <div className="bg-stone-700 rounded-xl px-4 py-2.5 text-stone-400 text-sm animate-pulse">
              思考中…
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-stone-700 p-3">
        {isLimitReached ? (
          <p className="text-center text-stone-500 text-sm py-1">
            已达追问上限（{roundsLimit} 轮），感谢使用
          </p>
        ) : (
          <>
            {error && <p className="text-red-400 text-xs mb-2">{error}</p>}
            <div className="flex gap-2">
              <textarea
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="输入追问内容，按 Enter 发送"
                rows={2}
                className="flex-1 bg-stone-700 border border-stone-600 rounded-lg px-3 py-2
                           text-stone-100 placeholder-stone-500 text-sm resize-none
                           focus:outline-none focus:border-amber-600 transition-colors"
              />
              <button
                onClick={handleSend}
                disabled={!canSend}
                className="px-4 bg-amber-700 hover:bg-amber-600 text-white rounded-lg text-sm
                           font-medium transition-all disabled:opacity-40 disabled:cursor-not-allowed"
              >
                发送
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
