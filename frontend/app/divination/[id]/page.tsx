export default function DivinationPage({ params }: { params: { id: string } }) {
  return (
    <iframe
      src={`/cast.html?id=${params.id}`}
      className="fixed inset-0 w-full h-full border-0"
      style={{ zIndex: 50 }}
    />
  )
}
