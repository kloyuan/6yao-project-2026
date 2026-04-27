import type { HexagramData, DivinationLine } from '@/lib/types'

interface Props {
  hexagram: HexagramData
  lines?: DivinationLine[]
  changingLines?: number[]
  label?: string
}

export default function HexagramDisplay({ hexagram, lines = [], changingLines = [], label }: Props) {
  const binary = hexagram.binary_code

  return (
    <div className="bg-stone-800/60 rounded-xl p-5 border border-stone-700 text-center">
      {label && (
        <p className="text-xs text-stone-500 mb-2 uppercase tracking-widest">{label}</p>
      )}

      {/* Hexagram visual — 6 lines rendered top→bottom (line 6 first) */}
      <div className="flex flex-col items-center gap-1.5 my-4">
        {[5, 4, 3, 2, 1, 0].map(idx => {
          const lineNum = idx + 1
          const isYang = binary[idx] === '1'
          const isChanging = changingLines.includes(lineNum)

          return (
            <div key={idx} className="flex items-center gap-1 w-24">
              {isYang ? (
                <div className={`h-2 flex-1 rounded-sm ${isChanging ? 'bg-red-400' : 'bg-amber-600'}`} />
              ) : (
                <>
                  <div className={`h-2 flex-1 rounded-sm ${isChanging ? 'bg-red-400' : 'bg-amber-600'}`} />
                  <div className="w-3" />
                  <div className={`h-2 flex-1 rounded-sm ${isChanging ? 'bg-red-400' : 'bg-amber-600'}`} />
                </>
              )}
            </div>
          )
        })}
      </div>

      <p className="text-2xl text-amber-400 font-bold">{hexagram.name}</p>
      <p className="text-xs text-stone-500 mt-1">
        {hexagram.trigrams[1]}下{hexagram.trigrams[0]}上 · {hexagram.palace}
      </p>
      <p className="text-sm text-stone-400 mt-2 leading-relaxed">{hexagram.meaning}</p>

      <div className="flex justify-center gap-4 mt-3 text-xs text-stone-600">
        <span>世爻第{hexagram.world_line}爻</span>
        <span>应爻第{hexagram.response_line}爻</span>
        <span>{'★'.repeat(hexagram.fortune_level)}{'☆'.repeat(5 - hexagram.fortune_level)}</span>
      </div>
    </div>
  )
}
