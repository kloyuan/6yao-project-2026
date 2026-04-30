'use client'

import { useState } from 'react'

interface Props {
  lineNumber: number
  onThrow: (coinValues: number[]) => Promise<void>
}

function randomCoins(): number[] {
  return [1, 2, 3].map(() => (Math.random() < 0.5 ? 3 : 2))
}

export default function CoinThrow({ lineNumber, onThrow }: Props) {
  const [coins, setCoins] = useState<number[] | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleThrow() {
    const result = randomCoins()
    setCoins(result)
    setSubmitting(true)
    await onThrow(result)
    setSubmitting(false)
    setCoins(null)
  }

  const coinSum = coins ? coins.reduce((a, b) => a + b, 0) : null

  return (
    <div className="text-center space-y-6">
      <p className="text-stone-400 text-sm">
        正在起第 <span className="text-amber-400 font-bold text-lg">{lineNumber}</span> 爻（共 6 爻）
      </p>

      {!coins ? (
        <button
          onClick={handleThrow}
          className="px-10 py-4 bg-amber-700 hover:bg-amber-600 text-white rounded-xl
                     text-lg font-medium transition-all active:scale-95 shadow-lg"
        >
          抛 掷
        </button>
      ) : (
        <div className="space-y-6">
          <div className="flex justify-center gap-4">
            {coins.map((v, i) => (
              <div
                key={i}
                className={`w-16 h-16 rounded-full flex items-center justify-center
                            text-xl font-bold border-2 shadow-md
                            ${v === 3
                              ? 'bg-amber-700 border-amber-500 text-amber-100'
                              : 'bg-stone-700 border-stone-500 text-stone-300'}`}
              >
                {v === 3 ? '正' : '背'}
              </div>
            ))}
          </div>

          <div className="text-stone-300">
            <span className="text-stone-500 text-sm">合计：</span>
            <span className="text-amber-400 font-bold text-xl mx-1">{coinSum}</span>
            <span className="text-stone-500 text-sm">→</span>
            <span className="text-amber-300 font-medium ml-1">
              {coinSum === 6 ? '老阴' : coinSum === 7 ? '少阳' : coinSum === 8 ? '少阴' : '老阳'}
            </span>
            {(coinSum === 6 || coinSum === 9) && (
              <span className="ml-2 text-xs text-red-400 bg-red-400/10 px-1.5 py-0.5 rounded">
                动爻
              </span>
            )}
          </div>

          {submitting && (
            <p className="text-stone-500 text-sm animate-pulse">记录中…</p>
          )}
        </div>
      )}
    </div>
  )
}
