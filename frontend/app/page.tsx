import Link from 'next/link'

const STEPS = [
  { num: '一', title: '提出问题', desc: '用一句话描述你关心的事，选择关注方向' },
  { num: '二', title: '模拟起卦', desc: '点击抛掷，依次生成六爻，还原传统三钱法' },
  { num: '三', title: '查看解读', desc: '获得卦象盘面与 AI 白话解读，可追问细节' },
]

export default function HomePage() {
  return (
    <div className="max-w-2xl mx-auto px-4 py-16 space-y-16">
      {/* Hero */}
      <section className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-amber-400 tracking-widest">六 爻</h1>
        <p className="text-stone-400 text-lg">传统三钱起卦 · AI 白话解读 · 在线追问</p>
        <div className="flex justify-center gap-4 pt-4">
          <Link
            href="/question"
            className="px-8 py-3 bg-amber-700 hover:bg-amber-600 text-white
                       rounded-xl font-medium text-base transition-all"
          >
            立即起卦
          </Link>
          <Link
            href="/rules"
            className="px-8 py-3 border border-stone-600 hover:border-amber-600
                       text-stone-300 hover:text-amber-400 rounded-xl text-base transition-all"
          >
            了解六爻
          </Link>
        </div>
      </section>

      {/* 3-step guide */}
      <section>
        <h2 className="text-center text-stone-500 text-sm tracking-widest mb-8 uppercase">使用流程</h2>
        <div className="grid gap-4 md:grid-cols-3">
          {STEPS.map(s => (
            <div key={s.num} className="bg-stone-800/60 rounded-xl p-5 border border-stone-700">
              <div className="text-amber-600 text-2xl font-bold mb-2">{s.num}</div>
              <h3 className="text-stone-200 font-medium mb-1">{s.title}</h3>
              <p className="text-stone-400 text-sm leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
