export default function ResultPage({ params }: { params: { id: string } }) {
  return (
    <div style={{ position: 'fixed', inset: 0, background: '#F1EFE9', zIndex: 50 }}>
      <iframe
        src={`/result.html?id=${params.id}`}
        className="fixed inset-0 w-full h-full border-0"
        style={{ zIndex: 51 }}
      />
    </div>
  )
}
