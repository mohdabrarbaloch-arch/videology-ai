"use client"

import { useEffect, useState } from "react"

interface VideoAnalysisData {
  analysis?: {
    summary?: string
    executive_summary?: string
    difficulty_level?: string
    sentiment?: string
    content_type?: string
    target_audience?: string
    estimated_reading_time?: number
  }
  topics?: Array<{ topic: string; relevance_score?: number; mention_count: number }>
  chapters?: Array<{ chapter_index: number; title: string; summary?: string; start_time: number; end_time?: number }>
  key_moments?: Array<{ timestamp_seconds: number; title: string; description?: string; moment_type?: string; importance_score?: number }>
  entities?: Array<{ entity_text: string; entity_type?: string; mention_count: number }>
  transcript?: { id: string; language: string; word_count: number; full_text: string }
  thumbnails?: Array<{ id: string; style: string; public_url?: string; is_favorite: boolean }>
  quiz?: { id: string; title: string; total_questions: number; difficulty?: string }
  learning_report?: Record<string, unknown>
}

export function useVideoAnalysis(videoId: string) {
  const [data, setData] = useState<VideoAnalysisData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | undefined>()

  useEffect(() => {
    const fetchVideo = async () => {
      try {
        const res = await fetch(`/api/videos/${videoId}`)
        if (!res.ok) throw new Error("Failed to fetch video")
        const videoData = await res.json()
        setData(videoData)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error")
      } finally {
        setLoading(false)
      }
    }

    if (videoId) {
      fetchVideo()
    }
  }, [videoId])

  return { data, loading, error }
}