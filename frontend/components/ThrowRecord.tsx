import type { DivinationLine } from '@/lib/types'
import LineDisplay from './LineDisplay'

interface Props {
  lines: DivinationLine[]
}

export default function ThrowRecord({ lines }: Props) {
  if (lines.length === 0) return null

  return (
    <div className="bg-stone-800/60 rounded-xl p-4 border border-stone-700">
      <h3 className="text-stone-400 text-sm font-medium mb-3">抛掷记录</h3>
      <div className="divide-y divide-stone-700/50">
        {[...lines].reverse().map(line => (
          <LineDisplay key={line.line_number} line={line} />
        ))}
      </div>
    </div>
  )
}
