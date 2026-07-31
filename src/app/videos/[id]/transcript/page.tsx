import { redirect, notFound } from 'next/navigation'
export const dynamic = "force-dynamic"
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft, Play, Download, FileText, Globe } from 'lucide-react'

function formatTime(seconds: number): string {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  if (h > 0) return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  return `${m}:${s.toString().padStart(2, '0')}`
}

export default async function TranscriptPage({
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

  const { data: transcript } = await supabase
    .from('transcripts')
    .select('*')
    .eq('video_id', id)
    .single()

  const { data: segments } = await supabase
    .from('transcript_segments')
    .select('*')
    .eq('video_id', id)
    .order('segment_index')

  const { data: translations } = await supabase
    .from('translations')
    .select('target_language, full_text')
    .eq('video_id', id)

  return (
    <div className="min-h-screen bg-[#080a0f] text-white">
      <nav className="border-b border-white/5 bg-[#080a0f]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center gap-4">
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
            <FileText className="w-4 h-4" />
            Transcript
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="flex items-start justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold mb-1">{video.title}</h1>
            {transcript && (
              <div className="flex items-center gap-3 text-sm text-white/40">
                <span className="flex items-center gap-1">
                  <Globe className="w-3.5 h-3.5" />
                  {transcript.language?.toUpperCase()}
                </span>
                <span>{transcript.word_count?.toLocaleString()} words</span>
              </div>
            )}
          </div>

          {transcript && (
            <div className="flex gap-2">
              {[
                { label: 'TXT', format: 'txt' },
                { label: 'SRT', format: 'srt' },
              ].map((btn) => (
                <a
                  key={btn.format}
                  href={`/api/videos/${id}/transcript/download?format=${btn.format}`}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-lg border border-white/10 bg-white/5 hover:border-white/20 transition-all text-xs font-medium"
                >
                  <Download className="w-3.5 h-3.5" />
                  {btn.label}
                </a>
              ))}
            </div>
          )}
        </div>

        {!transcript ? (
          <div className="text-center py-20 border border-dashed border-white/10 rounded-2xl">
            <FileText className="w-12 h-12 text-white/10 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No transcript yet</h3>
            <p className="text-white/40 text-sm">
              {video.status === 'completed'
                ? 'Transcript not available for this video.'
                : 'Transcript will appear here once processing is complete.'}
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {translations && translations.length > 0 && (
              <div className="p-4 rounded-xl border border-white/8 bg-white/3">
                <div className="text-xs text-white/40 mb-2 flex items-center gap-1">
                  <Globe className="w-3.5 h-3.5" />
                  Available translations
                </div>
                <div className="flex flex-wrap gap-2">
                  {translations.map((t) => (
                    <span key={t.target_language} className="px-2.5 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-xs text-purple-300">
                      {t.target_language}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {segments && segments.length > 0 ? (
              <div className="space-y-1">
                {segments.map((seg) => (
                  <div key={seg.id} className="flex gap-4 p-3 rounded-xl hover:bg-white/3 transition-colors group">
                    <span className="text-xs text-purple-400 font-mono mt-0.5 flex-shrink-0 w-14 text-right">
                      {formatTime(seg.start_time)}
                    </span>
                    <p className="text-sm text-white/70 leading-relaxed">{seg.text}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-6 rounded-2xl border border-white/8 bg-white/3">
                <p className="text-sm text-white/70 leading-relaxed whitespace-pre-wrap">
                  {transcript.full_text}
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}