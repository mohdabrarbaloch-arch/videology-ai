"use client"

import { useEffect, useState } from "react"
import { createClient } from "@/lib/supabase/client"
import { Loader2, CheckCircle, AlertCircle, Clock } from "lucide-react"
import { cn } from "@/lib/utils"

interface ProcessingStatusProps {
  jobId: string
  videoId: string
  initialStatus?: string
  initialProgress?: number
  initialStage?: string
  onComplete?: () => void
}

const statusConfig: Record<string, { label: string; color: string; bg: string; icon: typeof Clock }> = {
  queued: { label: "Queued", color: "text-yellow-400", bg: "bg-yellow-500/10", icon: Clock },
  downloading: { label: "Downloading", color: "text-blue-400", bg: "bg-blue-500/10", icon: Loader2 },
  extracting_audio: { label: "Extracting Audio", color: "text-blue-400", bg: "bg-blue-500/10", icon: Loader2 },
  transcribing: { label: "Transcribing", color: "text-purple-400", bg: "bg-purple-500/10", icon: Loader2 },
  analyzing: { label: "Analyzing", color: "text-purple-400", bg: "bg-purple-500/10", icon: Loader2 },
  generating_thumbnails: { label: "Generating Thumbnails", color: "text-pink-400", bg: "bg-pink-500/10", icon: Loader2 },
  indexing: { label: "Indexing", color: "text-cyan-400", bg: "bg-cyan-500/10", icon: Loader2 },
  completed: { label: "Completed", color: "text-green-400", bg: "bg-green-500/10", icon: CheckCircle },
  failed: { label: "Failed", color: "text-red-400", bg: "bg-red-500/10", icon: AlertCircle },
}

export function ProcessingStatus({
  jobId,
  videoId: _videoId,
  initialStatus = "queued",
  initialProgress = 0,
  initialStage = "Waiting to start",
  onComplete,
}: ProcessingStatusProps) {
  const [status, setStatus] = useState(initialStatus)
  const [progress, setProgress] = useState(initialProgress)
  const [stage, setStage] = useState(initialStage)
  const [error, setError] = useState<string | undefined>()

  useEffect(() => {
    const supabase = createClient()

    const channel = supabase
      .channel(`job:${jobId}`)
      .on(
        "postgres_changes",
        {
          event: "UPDATE",
          schema: "public",
          table: "processing_jobs",
          filter: `id=eq.${jobId}`,
        },
        (payload) => {
          const newRecord = payload.new as Record<string, unknown>
          setStatus(newRecord.status as string)
          setProgress(newRecord.progress as number)
          setStage(newRecord.current_stage as string)
          setError(newRecord.error_message as string)
          if (newRecord.status === "completed" && onComplete) {
            onComplete()
          }
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [jobId, onComplete])

  const cfg = statusConfig[status] || statusConfig.queued
  const isProcessing = !["completed", "failed"].includes(status)

  return (
    <div className={cn("p-6 rounded-2xl border", cfg.bg, "border-white/10")}>
      <div className="flex items-center gap-3 mb-4">
        <cfg.icon className={cn("w-5 h-5", cfg.color, isProcessing && "animate-spin")} />
        <div>
          <div className={cn("font-medium", cfg.color)}>{stage}</div>
          <div className="text-xs text-white/40">
            {isProcessing ? "This page will update when processing completes" : status === "failed" ? "Processing failed" : "Processing complete"}
          </div>
        </div>
        <div className={cn("ml-auto text-2xl font-bold", cfg.color)}>{progress}%</div>
      </div>
      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>
      {error && status === "failed" && (
        <div className="mt-4 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
          {error}
        </div>
      )}
    </div>
  )
}