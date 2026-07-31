"use client"

import { useState } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn, formatTime } from "@/lib/utils"

interface TranscriptSegment {
  id: string
  start_time: number
  end_time: number
  text: string
}

interface TranscriptViewerProps {
  segments: TranscriptSegment[]
  onSeek?: (timestamp: number) => void
  className?: string
}

export function TranscriptViewer({ segments, onSeek, className }: TranscriptViewerProps) {
  const [activeIndex, setActiveIndex] = useState(-1)

  const sortedSegments = [...segments].sort((a, b) => a.start_time - b.start_time)

  const handleSegmentClick = (segment: TranscriptSegment, index: number) => {
    setActiveIndex(index)
    if (onSeek) {
      onSeek(segment.start_time)
    }
  }

  return (
    <ScrollArea className={cn("h-[600px] rounded-xl border border-white/8 bg-white/3", className)}>
      <div className="p-4 space-y-1">
        {sortedSegments.map((seg, i) => (
          <div
            key={seg.id}
            onClick={() => handleSegmentClick(seg, i)}
            className={cn(
              "flex gap-4 p-3 rounded-xl cursor-pointer transition-colors group",
              activeIndex === i ? "bg-purple-500/10 border border-purple-500/20" : "hover:bg-white/5"
            )}
          >
            <span className="text-xs text-purple-400 font-mono mt-0.5 flex-shrink-0 w-14 text-right">
              {formatTime(seg.start_time)}
            </span>
            <p className="text-sm text-white/70 leading-relaxed">{seg.text}</p>
          </div>
        ))}
      </div>
    </ScrollArea>
  )
}