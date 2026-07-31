"use client"

import { useRef, useImperativeHandle, forwardRef } from "react"
import { Play } from "lucide-react"
import { cn } from "@/lib/utils"

export interface VideoPlayerHandle {
  seekTo: (timestamp: number) => void
}

interface VideoPlayerProps {
  src?: string
  youtubeId?: string
  thumbnailUrl?: string
  className?: string
}

export const VideoPlayer = forwardRef<VideoPlayerHandle, VideoPlayerProps>(
  ({ src, youtubeId, thumbnailUrl, className }, ref) => {
    const videoRef = useRef<HTMLVideoElement>(null)
    const containerRef = useRef<HTMLDivElement>(null)

    useImperativeHandle(ref, () => ({
      seekTo: (timestamp: number) => {
        if (videoRef.current) {
          videoRef.current.currentTime = timestamp
          videoRef.current.play()
        }
        if (containerRef.current) {
          containerRef.current.scrollIntoView({ behavior: "smooth", block: "center" })
        }
      },
    }))

    if (youtubeId) {
      return (
        <div ref={containerRef} className={cn("relative aspect-video rounded-xl overflow-hidden bg-black", className)}>
          <iframe
            src={`https://www.youtube.com/embed/${youtubeId}?rel=0&modestbranding=1`}
            className="w-full h-full"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            title="Video player"
          />
        </div>
      )
    }

    return (
      <div ref={containerRef} className={cn("relative aspect-video rounded-xl overflow-hidden bg-black group", className)}>
        {src ? (
          <video
            ref={videoRef}
            src={src}
            poster={thumbnailUrl}
            className="w-full h-full object-contain"
            controls
            playsInline
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            {thumbnailUrl ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={thumbnailUrl} alt="Video thumbnail" className="w-full h-full object-contain" />
            ) : (
              <Play className="w-12 h-12 text-white/20" />
            )}
          </div>
        )}
      </div>
    )
  }
)

VideoPlayer.displayName = "VideoPlayer"