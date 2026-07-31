"use client"

import { useEffect, useState } from "react"
import { createClient } from "@/lib/supabase/client"

interface JobStatus {
  status: string
  progress: number
  current_stage?: string
  error_message?: string
}

export function useVideoProcessing(jobId: string | undefined) {
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!jobId) {
      setLoading(false)
      return
    }

    const supabase = createClient()

    const fetchStatus = async () => {
      const { data } = await supabase
        .from("processing_jobs")
        .select("status, progress, current_stage, error_message")
        .eq("id", jobId)
        .single()

      if (data) {
        setJobStatus(data)
      }
      setLoading(false)
    }

    fetchStatus()

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
          setJobStatus({
            status: newRecord.status as string,
            progress: newRecord.progress as number,
            current_stage: newRecord.current_stage as string,
            error_message: newRecord.error_message as string,
          })
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [jobId])

  const isProcessing = jobStatus ? !["completed", "failed"].includes(jobStatus.status) : false
  const isCompleted = jobStatus?.status === "completed"
  const isFailed = jobStatus?.status === "failed"

  return { jobStatus, loading, isProcessing, isCompleted, isFailed }
}