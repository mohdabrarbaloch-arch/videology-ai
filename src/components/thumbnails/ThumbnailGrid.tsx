"use client"

import { Download, Star, Image as ImageIcon } from "lucide-react"
import { cn } from "@/lib/utils"

interface Thumbnail {
  id: string
  style: string
  public_url?: string
  is_favorite: boolean
  width: number
  height: number
}

interface ThumbnailGridProps {
  thumbnails: Thumbnail[]
  onFavorite?: (id: string) => void
  className?: string
}

const styleLabels: Record<string, string> = {
  youtube_creator: "YouTube Creator",
  cinematic: "Cinematic",
  educational: "Educational",
  minimal: "Minimal",
  high_contrast: "High Contrast",
  editorial: "Editorial",
}

export function ThumbnailGrid({ thumbnails, onFavorite, className }: ThumbnailGridProps) {
  if (!thumbnails || thumbnails.length === 0) {
    return (
      <div className="text-center py-20 border border-dashed border-white/10 rounded-2xl">
        <ImageIcon className="w-12 h-12 text-white/10 mx-auto mb-4" />
        <h3 className="text-lg font-semibold mb-2">No thumbnails yet</h3>
        <p className="text-white/40 text-sm">Thumbnails will appear here once processing is complete.</p>
      </div>
    )
  }

  return (
    <div className={cn("grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6", className)}>
      {thumbnails.map((thumb) => (
        <div
          key={thumb.id}
          className="group rounded-2xl border border-white/8 bg-white/3 overflow-hidden hover:border-white/15 transition-all"
        >
          <div className="aspect-video bg-white/5 overflow-hidden">
            {thumb.public_url ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={thumb.public_url}
                alt={styleLabels[thumb.style] || thumb.style}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <ImageIcon className="w-8 h-8 text-white/10" />
              </div>
            )}
          </div>
          <div className="p-4 flex items-center justify-between">
            <div>
              <div className="font-medium text-sm">{styleLabels[thumb.style] || thumb.style}</div>
              <div className="text-xs text-white/40 mt-0.5">{thumb.width}x{thumb.height} - DALL-E 3</div>
            </div>
            <div className="flex items-center gap-2">
              {onFavorite && (
                <button
                  onClick={() => onFavorite(thumb.id)}
                  className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                >
                  <Star className={cn("w-4 h-4", thumb.is_favorite ? "text-yellow-400 fill-current" : "text-white/60")} />
                </button>
              )}
              {thumb.public_url && (
                <a
                  href={thumb.public_url}
                  download
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                >
                  <Download className="w-4 h-4 text-white/60" />
                </a>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}