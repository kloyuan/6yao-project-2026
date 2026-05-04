export default async function DivinationPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <iframe
      src={`/cast.html?id=${id}`}
      className="fixed inset-0 w-full h-full border-0"
      style={{ zIndex: 50 }}
    />
  )
}
