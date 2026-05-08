import type { Metadata } from 'next'
import '../styles/globals.css'

export const metadata: Metadata = {
  title: '六爻在线起卦',
  description: '传统三钱六爻起卦，AI 白话解读，在线追问',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@200;300;400&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen bg-[#F1EFE9]">
        {children}
      </body>
    </html>
  )
}
