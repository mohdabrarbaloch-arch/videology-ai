"use client"

import { useState, useCallback, useRef } from "react"

interface Citation {
  timestamp: number
  text: string
  segment_id?: string
}

interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  citations?: Citation[]
}

export function useChat(videoId: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [conversationId, setConversationId] = useState<string | undefined>()
  const messageIdCounter = useRef(0)

  const sendMessage = useCallback(async (question: string) => {
    if (!question.trim() || loading) return

    setError("")
    const userMsg: ChatMessage = {
      id: `msg-${messageIdCounter.current++}`,
      role: "user",
      content: question,
    }
    setMessages((prev) => [...prev, userMsg])
    setLoading(true)

    try {
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ video_id: videoId, question, conversation_id: conversationId }),
      })

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.error || "Failed to get answer")
      }

      const data = await res.json()
      setConversationId(data.conversation_id)

      const assistantMsg: ChatMessage = {
        id: `msg-${messageIdCounter.current++}`,
        role: "assistant",
        content: data.answer,
        citations: data.citations,
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong")
    } finally {
      setLoading(false)
    }
  }, [videoId, conversationId, loading])

  const clearChat = useCallback(() => {
    setMessages([])
    setConversationId(undefined)
    setError("")
  }, [])

  return { messages, loading, error, sendMessage, clearChat, conversationId }
}