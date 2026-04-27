import type { Metadata } from 'next'
import '../styles/globals.css'
import Footer from '@/components/Footer'

export const metadata: Metadata = {
  title: '六爻在线起卦',
  description: '传统三钱六爻起卦，AI 白话解读，在线追问',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen flex flex-col bg-stone-950 text-stone-100">
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  )
}
