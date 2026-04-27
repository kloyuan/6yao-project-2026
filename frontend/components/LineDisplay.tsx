import type { DivinationLine } from '@/lib/types'

const LINE_TYPE_META: Record<string, { label: string; yang: boolean }> = {
  老阴: { label: '老阴 ⊙', yang: false },
  少阳: { label: '少阳 —', yang: true },
  少阴: { label: '少阴 --', yang: false },
  老阳: { label: '老阳 ●', yang: true },
}

interface Props {
  line: DivinationLine
  compact?: boolean
}

export default function LineDisplay({ line, compact = false }: Props) {
  const meta = LINE_TYPE_META[line.line_type] ?? { label: line.line_type, yang: true }
  const isChanging = line.is_changing

  return (
    <div className={`flex items-center gap-3 ${compact ? 'py-1' : 'py-2'}`}>
      <span className="text-stone-500 text-sm w-10 shrink-0">第{line.line_number}爻</span>

      {/* Visual yao */}
      <div className="w-20 flex items-center gap-0.5">
        {meta.yang ? (
          <div className={`h-1.5 flex-1 rounded-sm ${isChanging ? 'bg-red-400' : 'bg-amber-600'}`} />
        ) : (
          <>
            <div className={`h-1.5 flex-1 rounded-sm ${isChanging ? 'bg-red-400' : 'bg-amber-600'}`} />
            <div className="w-2" />
            <div className={`h-1.5 flex-1 rounded-sm ${isChanging ? 'bg-red-400' : 'bg-amber-600'}`} />
          </>
        )}
      </div>

      <span className={`text-sm font-medium ${isChanging ? 'text-red-400' : 'text-amber-500'}`}>
        {line.line_type}
      </span>

      {isChanging && (
        <span className="text-xs text-red-400 bg-red-400/10 px-1.5 py-0.5 rounded">动爻</span>
      )}

      {!compact && (
        <span className="text-xs text-stone-500 ml-auto">
          [{line.coin_values.join('+')}]={line.coin_sum}
        </span>
      )}
    </div>
  )
}
