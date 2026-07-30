import { redirect } from 'next/navigation'
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { Plus, Video, CheckCircle, Xcircle, Loader2, Play, Settings, LogOut } from 'lucide-react'

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

export default async function DashboardPage() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/auth/login')

  const { data: videos } = await supabase
    .from('videos')
    .select('*, processing_jobs(status, progress, current_stage)')
    .eq('user_id', user.id)
    .order('created_at', { ascending: false })
    .limit(10)

  const { data: profile } = await supabase.from('profiles').select('*').eq('id', user.id).single()

  const stats = {
    total: videos?.length || 0,
    completed: videos?.filter(v => v.status === 'completed').length || 0,
    processing: videos?.filter(v => v.status === 'processing').length || 0,
    failed: videos?.filter(v => v.status === 'failed').length || 0,
  }

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
          <Link href="/videos" className="text-sm text-white/60 hover:text-white">My Videos</Link>
          <Link href="/settings" className="text-sm text-white/60 hover:text-white"><Settings className="w4 h-4" /></Link>
          <form action="/api/auth/signout" method="post">
            <button type="submit" className="text-sm text-white/40 hover:text-white"><LogOut className="w4 h-4" /></button>
          </form>
        </div>
      </nav>
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold">Dashboard</h1>
            <p className="text-sm text-white/50 mt-1">Welcome back, {profile?.full_name || user.email}</p>
          </div>
          <Link href="/analyze" className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 transition-colors text-sm font-medium">
            <Plus className="w-4 h-4" /> Analyze Video
          </Link>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Total Videos', value: stats.total, color: 'text-purple-400' },
            { label: 'Completed', value: stats.completed, color: 'text-green-400' },
            { label: 'Processing', value: stats.processing, color: 'text-blue-400' },
            { label: 'Failed', value: stats.failed, color: 'text-red-400' },
          ].map((stat, i) => (
            <div key={i} className="p-5 rounded-2xl border border-white/8 bg-white/3">
              <p className="text-xs text-white/50 mb-2">{stat.label}</p>
              <div className={`text-2xl font-bold ${stat.color}`}>{stat.value}</div>
            </div>
          ))}
        </div>
        <div>
          <h3 className="font-semibold mb-4">Recent Videos</h3>
          {videos?.length === 0 ? (
            <div className="text-center py-16 rounded-2xl border border-white/8 bg-white/3">
              <Video className="w-12 h-12 text-white/20 mx-auto mb-4" />
              <p className="text-white/50 mb-4">No videos yet</p>
              <Link href="/analyze" className="px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 transition-colors text-sm font-medium">Analyze your first video</Link>
            </div>
          ) : (
            <div className="space-y-3">
              {videos.map((video) => {
                const job = video.processing_jobs?.[0]
                return (
                  <Link key={video.id} href={`/videos/${video.id}`} className="flex items-center gap-4 p-4 rounded-xl border border-white/8 bg-white/3 hover:bs-white/5 transition-colors">
                    <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                      <Video className="w5 h-5 text-purple-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{video.title}</p>
                      <p className="text-xs text-white/40 mt-0.5">{job?.current_stage || new Date(video.created_at).toLocaleDateString()}</p>
                      {job?.progress != null && job.status !== 'completed' && (
                        <div className="w-full bg-white/10 rounded-full h-1 mt-1.5">
                          <div className="bg-purple-500 h-1 rounded-full transition-all" style={{ width: `${job.progress}%` }} />
                        </div>
                      )}
                    </div>
                    <StatusBadge status={video.status} />
                  </Link>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
