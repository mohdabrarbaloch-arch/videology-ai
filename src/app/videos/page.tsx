import { redirect } from 'next/navigation'
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { Video, Plus, Play } from 'lucide-react'

function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { label: string; class: string }> = {
    pending: { label: 'Pending', class: 'bg-white/10 text-white/50' },
    processing: { label: 'Processing', class: 'bg-blue-500/20 text-blue-300' },
    completed: { label: 'Completed', class: 'bg-green-500/20 text-green-300' },
    failed: { label: 'Failed', class: 'bg-red-500/20 text-red-300' },
  }
  const c = config[status] || { label: status, class: 'bg-white/10 text-white/50' }
  return <span className={`px-2 py-0.5 rounded-md text-xs font-medium ${c.class}`}>{c.label}</span>
}

export default async function VideosPage() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/auth/login')

  const { data: videos } = await supabase
    .from('videos')
    .select('*, processing_jobs(status, progress, current_stage)')
    .eq('user_id', user.id)
    .order('created_at', { ascending: false })

  return (
    <div className="min-h-screen bg-[#080a0f] text-white">
      <nav className="border-b border-white/5 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
            <Play className="w-4 h-4 text-white fill-white" />
          </div>
          <span className="font-bold text-lg">Videology</span>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/dashboard" className="text-sm text-white/60 hover:text-white">Dashboard</Link>
          <Link href="/analyze" className="flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-600 hover:bs-purple-500 transition-colors text-sm font-medium">
            <Plus className="w4 h-4" /> Analyze
          </Link>
        </div>
      </nav>
      <div className="max-w-7xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-bold mb-6">My Videos <span className="text-white/40">({videos?.length || 0})</span></h1>
        {videos?.length === 0 ? (
          <div className="text-center py-24 rounded-2xl border border-white/8 bg-white/3">
            <Video className="w-16 h-16 text-white/20 mx-auto mb-6" />
            <h2 className="text-xl font-semibold mb-2">No videos yet</h2>
            <p className="text-white/50 mb-6">Analyze your first video to get started</p>
            <Link href="/analyze" className="px-6 py-3 rounded-xl bg-purple-600 hover:bg-purple-500 transition-colors font-medium">Analyze a Video</Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {videos.map((video) => {
              const job = video.processing_jobs?.[0]
              return (
                <Link href={`/videos/${video.id}`} key={video.id} className="rounded-2xl border border-white/8 bg-white/3 hover:bg-white/5 transition-colors overflow-hidden">
                  <div className="h-32 bg-gradient-to-br from-purple-900/50 to-blue-900/50 flex items-center justify-center">
                    <Video className="w-12 h-12 text-white/20" />
                  </div>
                  <div className="p-4">
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <p className="font-medium text-sm line-clamp-2">{video.title}</p>
                      <StatusBadge status={video.status} />
                    </div>
                    <p className="text-xs text-white/40">
                      {new Date(video.created_at).toLocaleDateString()}
                    </p>
                    {job?.progress != null && job.status !== 'completed' && (
                      <div className="w-full bg-white/10 rounded-full h-1 mt-2">
                        <div className="bg-purple-500 h-1 rounded-full" style={{ width: `${job.progress}%` }} />
                      </div>
                    )}
                  </div>
                </Link>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
