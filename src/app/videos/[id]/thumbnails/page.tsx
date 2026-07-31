import { redirect, notFound } from 'next/navigation'
export const dynamic = "force-dynamic"
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft, Play, Download, Star, Image } from 'lucide-react'

const styleLabels: Record<string, string> = {
  youtube_creator: 'YouTube Creator',
  cinematic: 'Cinematic',
  educational: 'Educational',
  minimal: 'Minimal',
  high_contrast: 'High Contrast',
  editorial: 'Editorial',
}

export default async function ThumbnailsPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/auth/login')

  const { data: video } = await supabase
    .from('videos')
    .select('id, title, status')
    .eq('id', id)
    .eq('user_id', user.id)
    .single()

  if (!video) notFound()

  const { data: thumbnails } = await supabase
    .from('thumbnails')
    .select('*')
    .eq('video_id', id)
    .order('created_at')

  return (
    <div className="min-h-screen bg-[#080a0f] text-white">
      <nav className="border-b border-white/5 bg-[#080a0f]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center gap-4">
          <Link href={`/videos/${id}`} className="text-white/40 hover:text-white transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
              <Play className="w-3.5 h-3.5 text-white fill-white" />
            </div>
            <span className="font-bold">Videology</span>
          </div>
          <div className="flex items-center gap-2 ml-2 text-white/40 text-sm">
            <Image className="w-4 h-4" aria-label="Thumbnails" />
            AI Thumbnails
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold mb-1">AI Thumbnails</h1>
          <p className="text-white/40 text-sm">{video.title}</p>
        </div>

        {!thumbnails || thumbnails.length === 0 ? (
          <div className="text-center py-20 border border-dashed border-white/10 rounded-2xl">
            <Image className="w-12 h-12 text-white/10 mx-auto mb-4" aria-label="No thumbnails" />
            <h3 className="text-lg font-semibold mb-2">No thumbnails yet</h3>
            <p className="text-white/40 text-sm">
              {video.status === 'completed'
                ? 'Thumbnails were not generated for this video.'
                : 'Thumbnails will appear here once processing is complete.'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {thumbnails.map((thumb) => (
              <div key={thumb.id} className="group rounded-2xl border border-white/8 bg-white/3 overflow-hidden hover:border-white/15 transition-all">
                <div className="aspect-video bg-white/5 overflow-hidden">
                  {thumb.public_url ? (
                    /* eslint-disable-next-line @next/next/no-img-element */
                    <img
                      src={thumb.public_url}
                      alt={styleLabels[thumb.style] || thumb.style}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <Image className="w-8 h-8 text-white/10" aria-label="No thumbnail" />
                    </div>
                  )}
                </div>
                <div className="p-4 flex items-center justify-between">
                  <div>
                    <div className="font-medium text-sm">{styleLabels[thumb.style] || thumb.style}</div>
                    <div className="text-xs text-white/40 mt-0.5">
                      {thumb.width}\u00d7{thumb.height} \u00b7 DALL-E 3
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {thumb.is_favorite && <Star className="w-4 h-4 text-yellow-400 fill-current" />}
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
        )}
      </div>
    </div>
  )
}