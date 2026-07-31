import { redirect } from 'next/navigation'
export const dynamic = "force-dynamic"
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { Play, ArrowLeft, Settings, Key, User, Globe } from 'lucide-react'

export default async function SettingsPage() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/auth/login')

  const { data: profile } = await supabase
    .from('profiles')
    .select('*')
    .eq('id', user.id)
    .single()

  return (
    <div className="min-h-screen bg-[#080a0f] text-white">
      <nav className="border-b border-white/5 bg-[#080a0f]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center gap-4">
          <Link href="/dashboard" className="text-white/40 hover:text-white transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
              <Play className="w-3.5 h-3.5 text-white fill-white" />
            </div>
            <span className="font-bold">Videology</span>
          </div>
          <div className="flex items-center gap-2 ml-2 text-white/40 text-sm">
            <Settings className="w-4 h-4" />
            Settings
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-bold mb-8">Settings</h1>

        <div className="space-y-6">
          {/* Profile */}
          <div className="p-6 rounded-2xl border border-white/8 bg-white/3">
            <h2 className="font-semibold mb-4 flex items-center gap-2">
              <User className="w-4 h-4 text-purple-400" />
              Profile
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-white/40 mb-1.5">Email</label>
                <div className="px-4 py-3 rounded-xl bg-white/5 border border-white/8 text-sm text-white/60">
                  {user.email}
                </div>
              </div>
              <div>
                <label className="block text-xs text-white/40 mb-1.5">Full Name</label>
                <div className="px-4 py-3 rounded-xl bg-white/5 border border-white/8 text-sm text-white/60">
                  {profile?.full_name || '\u2014'}
                </div>
              </div>
              <div>
                <label className="block text-xs text-white/40 mb-1.5">Plan</label>
                <div className="px-4 py-3 rounded-xl bg-white/5 border border-white/8 text-sm">
                  <span className="capitalize text-purple-400 font-medium">{profile?.plan || 'free'}</span>
                </div>
              </div>
              <div>
                <label className="block text-xs text-white/40 mb-1.5">Videos Processed</label>
                <div className="px-4 py-3 rounded-xl bg-white/5 border border-white/8 text-sm text-white/60">
                  {profile?.videos_processed || 0}
                </div>
              </div>
            </div>
          </div>

          {/* API Keys */}
          <div className="p-6 rounded-2xl border border-white/8 bg-white/3">
            <h2 className="font-semibold mb-2 flex items-center gap-2">
              <Key className="w-4 h-4 text-yellow-400" />
              API Configuration
            </h2>
            <p className="text-xs text-white/40 mb-4">
              API keys are configured server-side via environment variables and are never exposed to the browser.
            </p>
            <div className="space-y-3">
              {[
                { label: 'OpenAI API Key', env: 'OPENAI_API_KEY', status: 'Configured via .env' },
                { label: 'Supabase URL', env: 'NEXT_PUBLIC_SUPABASE_URL', status: 'Configured via .env' },
                { label: 'AI Model', env: 'AI_MODEL', status: process.env.AI_MODEL || 'gpt-4o' },
                { label: 'Transcription Model', env: 'TRANSCRIPTION_MODEL', status: process.env.TRANSCRIPTION_MODEL || 'whisper-1' },
              ].map((item) => (
                <div key={item.env} className="flex items-center justify-between p-3 rounded-xl bg-white/3 border border-white/5">
                  <div>
                    <div className="text-sm font-medium">{item.label}</div>
                    <div className="text-xs text-white/30 font-mono">{item.env}</div>
                  </div>
                  <span className="text-xs text-green-400 bg-green-500/10 px-2.5 py-1 rounded-full">
                    {item.status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Preferences */}
          <div className="p-6 rounded-2xl border border-white/8 bg-white/3">
            <h2 className="font-semibold mb-4 flex items-center gap-2">
              <Globe className="w-4 h-4 text-blue-400" />
              Preferences
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-white/40 mb-1.5">Preferred Language</label>
                <div className="px-4 py-3 rounded-xl bg-white/5 border border-white/8 text-sm text-white/60">
                  {profile?.preferred_language || 'en'}
                </div>
              </div>
              <div>
                <label className="block text-xs text-white/40 mb-1.5">Timezone</label>
                <div className="px-4 py-3 rounded-xl bg-white/5 border border-white/8 text-sm text-white/60">
                  {profile?.timezone || 'UTC'}
                </div>
              </div>
            </div>
          </div>

          {/* Danger zone */}
          <div className="p-6 rounded-2xl border border-red-500/20 bg-red-500/5">
            <h2 className="font-semibold mb-2 text-red-400">Danger Zone</h2>
            <p className="text-xs text-white/40 mb-4">
              These actions are irreversible. Please be certain.
            </p>
            <form action="/api/auth/signout" method="POST">
              <button
                type="submit"
                className="px-4 py-2 rounded-lg border border-red-500/30 text-red-400 hover:bg-red-500/10 transition-colors text-sm"
              >
                Sign out
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}