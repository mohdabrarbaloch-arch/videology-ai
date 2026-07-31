import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Videology — Watch. Analyze. Learn.',
  description:
    'AI-powered video intelligence platform. Transcribe, analyze, and learn from any video with GPT-4o.',
  keywords: ['AI', 'video analysis', 'transcription', 'learning', 'YouTube'],
  authors: [{ name: 'Abrar Baloch' }],
  openGraph: {
    title: 'Videology — Watch. Analyze. Learn.',
    description: 'AI-powered video intelligence platform',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>{children}</body>
    </html>
  )
}