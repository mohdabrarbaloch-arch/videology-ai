'use client'

import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { ArrowLeft, Play, Send, Loader2, MessageSquare, Clock } from 'lucide-react'

interface Citation {
  timestamp: number
  text: string
  segment_id?: string
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
  created_at: string
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

export default function AskPage() {
  const params = useParams()
  const videoId = params.id as string
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | undefined>()
  const [error, setError] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const question = input.trim()
    setInput('')
    setError('')

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: question,
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMsg])
    setLoading(true)

    try {
      const res = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_id: videoId, question, conversation_id: conversationId }),
      })

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.error || 'Failed to get answer')
      }

      const data = await res.json()
      setConversationId(data.conversation_id)

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        citations: data.citations,
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const suggestions = [
    'What is the main topic of this video?',
    'Summarize the key points',
    'What are the most important takeaways?',
    'Explain the concepts mentioned',
  ]

  return (
    <div className="min-h-screen bg-[#080a0f] text-white flex flex-col">
      <nav className="border-b border-white/5 bg-[#080a0f]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center gap-4">
          <Link href={`/videos/${videoId}`} className="text-white/40 hover:text-white transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
              <Play className="w-3.5 h-3.5 text-white fill-white" />
            </div>
            <span className="font-bold">Videology</span>
          </div>
          <div className="flex items-center gap-2 ml-2 text-white/40 text-sm">
            <MessageSquare className="w-4 h-4" />
            Ask AI
          </div>
        </div>
      </nav>

      <div className="flex-1 max-w-4xl mx-auto w-full px-6 py-6 flex flex-col">
        {messages.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center">
            <div className="w-16 h-16 rounded-full bg-purple-500/20 flex items-center justify-center mb-6">
              <MessageSquare className="w-8 h-8 text-purple-400" />
            </div>
            <h2 className="text-xl font-bold mb-2">Ask anything about this video</h2>
            <p className="text-white/40 text-sm mb-8 max-w-md">
              I&apos;ll search the transcript and answer with exact timestamp citations.
              If the answer isn&apos;t in the video, I&apos;ll tell you.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg">
              {suggestions.map((s) => (
                <button
                  key={s}
                  onClick={() => setInput(s)}
                  className="p-3 rounded-xl border border-white/8 bg-white/3 hover:border-purple-500/30 hover:bg-purple-500/5 transition-all text-sm text-left text-white/60 hover:text-white"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="flex-1 space-y-6 mb-6">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] ${msg.role === 'user' ? 'order-2' : 'order-1'}`}>
                  {msg.role === 'assistant' && (
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-6 h-6 rounded-full bg-purple-500/20 flex items-center justify-center">
                        <MessageSquare className="w-3 h-3 text-purple-400" />
                      </div>
                      <span className="text-xs text-white/40">Videology AI</span>
                    </div>
                  )}
                  <div className={`p-4 rounded-2xl text-sm leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-purple-600 text-white rounded-tr-sm'
                      : 'bg-white/5 border border-white/8 text-white/80 rounded-tl-sm'
                  }`}>
                    {msg.content}
                  </div>
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="mt-2 space-y-1">
                      {msg.citations.map((c, i) => (
                        <div key={i} className="flex items-start gap-2 text-xs text-white/40 bg-white/3 rounded-lg p-2">
                          <Clock className="w-3 h-3 text-cyan-400 flex-shrink-0 mt-0.5" />
                          <span className="text-cyan-400 font-mono flex-shrink-0">{formatTime(c.timestamp)}</span>
                          <span className="line-clamp-2">{c.text}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white/5 border border-white/8 rounded-2xl rounded-tl-sm p-4">
                  <Loader2 className="w-4 h-4 text-purple-400 animate-spin" />
                </div>
              </div>
            )}
            {error && (
              <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                {error}
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}

        <form onSubmit={sendMessage} className="flex gap-3 sticky bottom-6">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything about this video..."
            className="flex-1 px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-white/30 focus:outline-none focus:border-purple-500/50 text-sm"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="px-4 py-3 rounded-xl bg-purple-600 hover:bg-purple-500 disabled:opacity-50 transition-all"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
          </button>
        </form>
      </div>
    </div>
  )
}