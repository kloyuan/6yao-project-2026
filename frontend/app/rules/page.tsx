import Link from 'next/link'

const COIN_MAP = [
  { sum: 6, name: '老阴', coins: '背+背+背', desc: '三枚全背，纯阴至极，为动爻（阴变阳）', changing: true, yin: true },
  { sum: 7, name: '少阳', coins: '正+背+背', desc: '一正两背，静阳，不变爻', changing: false, yin: false },
  { sum: 8, name: '少阴', coins: '正+正+背', desc: '两正一背，静阴，不变爻', changing: false, yin: true },
  { sum: 9, name: '老阳', coins: '正+正+正', desc: '三枚全正，纯阳至极，为动爻（阳变阴）', changing: true, yin: false },
]

export default function RulesPage() {
  return (
    <div className="max-w-2xl mx-auto px-4 py-12 space-y-12">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-amber-400 mb-2">了解六爻</h1>
        <p className="text-stone-500 text-sm">零基础入门指南</p>
      </div>

      {/* What is Liuyao */}
      <section className="space-y-4">
        <h2 className="text-amber-500 font-medium text-lg">什么是六爻？</h2>
        <p className="text-stone-300 leading-relaxed text-sm">
          六爻是源自《易经》的传统占卜体系，通过抛掷三枚硬币六次生成卦象，
          再根据卦象的象征含义对问题进行解读。每次抛掷决定一爻（一条线），
          六爻合在一起构成一个完整的"卦"。
        </p>
        <p className="text-stone-300 leading-relaxed text-sm">
          《易经》共有 64 卦，每卦代表不同的自然状态与人事规律。
          六爻占卜的精髓在于"应象"——以自然规律的变化映射人事的走向。
        </p>
      </section>

      {/* Why 3 coins */}
      <section className="space-y-4">
        <h2 className="text-amber-500 font-medium text-lg">为什么用三枚硬币？</h2>
        <p className="text-stone-300 leading-relaxed text-sm">
          传统六爻使用"三钱法"：取三枚铜钱，同时抛掷，以正面（字面）和背面（花面）的组合
          判断每一爻的阴阳属性。三枚硬币共有 4 种点数组合（6、7、8、9），
          对应四种爻型。本平台使用随机数模拟此过程，保留传统仪式感。
        </p>
      </section>

      {/* Coin mapping table */}
      <section className="space-y-4">
        <h2 className="text-amber-500 font-medium text-lg">三钱法映射规则</h2>
        <p className="text-stone-500 text-xs mb-3">正面 = 3 点，背面 = 2 点，三枚之和决定爻型</p>
        <div className="divide-y divide-stone-700 border border-stone-700 rounded-xl overflow-hidden">
          {COIN_MAP.map(row => (
            <div key={row.sum} className="flex items-start gap-4 p-4 bg-stone-800/40">
              <div className="text-2xl font-bold text-amber-600 w-8 shrink-0">{row.sum}</div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`font-medium ${row.yin ? 'text-stone-300' : 'text-amber-400'}`}>
                    {row.name}
                  </span>
                  {row.changing && (
                    <span className="text-xs text-red-400 bg-red-400/10 px-1.5 py-0.5 rounded">
                      动爻
                    </span>
                  )}
                </div>
                <p className="text-stone-500 text-xs">{row.coins}</p>
                <p className="text-stone-400 text-sm mt-1">{row.desc}</p>
              </div>

              {/* Visual yao */}
              <div className="w-12 flex items-center gap-0.5 mt-1 shrink-0">
                {!row.yin ? (
                  <div className={`h-1.5 flex-1 rounded-sm ${row.changing ? 'bg-red-400' : 'bg-amber-600'}`} />
                ) : (
                  <>
                    <div className={`h-1.5 flex-1 rounded-sm ${row.changing ? 'bg-red-400' : 'bg-amber-600'}`} />
                    <div className="w-2" />
                    <div className={`h-1.5 flex-1 rounded-sm ${row.changing ? 'bg-red-400' : 'bg-amber-600'}`} />
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* How to read */}
      <section className="space-y-4">
        <h2 className="text-amber-500 font-medium text-lg">如何看卦？</h2>
        <div className="space-y-3 text-sm text-stone-300 leading-relaxed">
          <p>
            <span className="text-amber-500">本卦</span>：六爻按原始状态组成的卦，代表当前处境与核心问题。
          </p>
          <p>
            <span className="text-amber-500">变卦</span>：将动爻（老阴变少阳、老阳变少阴）翻转后形成的卦，
            代表事态的发展趋势与结果走向。无动爻时变卦与本卦相同，意味着卦象稳定。
          </p>
          <p>
            <span className="text-amber-500">动爻</span>：发生变化的爻，是卦象中最关键的信息点，
            通常指示当前处境中最需要关注的因素。
          </p>
        </div>
      </section>

      <div className="text-center pt-4">
        <Link
          href="/question"
          className="px-8 py-3 bg-amber-700 hover:bg-amber-600 text-white rounded-xl
                     font-medium transition-all inline-block"
        >
          开始起卦
        </Link>
      </div>
    </div>
  )
}
