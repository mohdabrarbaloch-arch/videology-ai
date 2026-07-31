"use client"

import { cn, formatTime } from "@/lib/utils"
import { BookOpen } from "lucide-react"

interface Chapter {
  chapter_index: number
  title: string
  summary?: string
  start_time: number
  end_time?: number
}

interface ChapterListProps {
  chapters: Chapter[]
  onSeek?: (timestamp: number) => void
  className?: string
}

export function ChapterList({ chapters, onSeek, className }: ChapterListProps) {
  const sorted = [...chapters].sort((a, b) => a.chapter_index - b.chapter_index)

  return (
    <div className={cn("space-y-3", className)}>
      <div className="flex items-center gap-2 mb-4">
        <BookOpen className="w-4 h-4 text-blue-400" />
        <h3 className="font-semibold text-sm">Chapters ({sorted.length})</h3>
      </div>
      {sorted.map((ch) => (
        <div
          key={ch.chapter_index}
          onClick={() => onSeek?.(ch.start_time)}
          className="flex gap-3 cursor-pointer hover:bg-white/5 p-2 rounded-lg transition-colors"
        >
          <div className="text-xs text-purple-400 font-mono mt-0.5 flex-shrink-0 w-12">
            {formatTime(ch.start_time)}
          </div>
          <div>
            <div className="text-sm font-medium">{ch.title}</div>
            {ch.summary && <div className="text-xs text-white/40 mt-0.5">{ch.summary}</div>}
          </div>
        </div>
      ))}
    </div>
  )
}