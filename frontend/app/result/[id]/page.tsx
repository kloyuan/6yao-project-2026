export default async function ResultPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <div style={{ position: 'fixed', inset: 0, background: '#F1EFE9', zIndex: 50 }}>
      <iframe
        src={`/result.html?id=${id}`}
        className="fixed inset-0 w-full h-full border-0"
        style={{ zIndex: 51 }}
      />
    </div>
  )
}
