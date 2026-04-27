import QuestionForm from '@/components/QuestionForm'

export default function QuestionPage() {
  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <h1 className="text-2xl font-bold text-amber-400 mb-2 text-center">提出你的问题</h1>
      <p className="text-stone-500 text-sm text-center mb-10">
        心中存念，虔诚发问，卦象自然呈现
      </p>
      <QuestionForm />
    </div>
  )
}
