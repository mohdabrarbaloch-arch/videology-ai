'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Play, Loader2 } from 'lucide-react'
import { createClient } from '@/lib/supabase/client'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    const supabase = createClient()
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) { setError(error.message); setLoading(false) } else { router.push('/dashboard') }
  }

  const handleGoogleLogin = async () => {
    const supabase = createClient()
    await supabase.auth.signInWithOAuth({ provider: 'google', options: { redirectTo: `${window.location.origin}/auth/callback` } })
  }

  return (
    <div className="min-h-screen bg-[#080a0f] flex items-center justify-center px-6">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2 mb-6">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center"><Play className="w-4 h-4 text-white fill-white" /></div>
            <span className="font-bold text-lg">Videology</span>
          </Link>
          <h1 className="text-2xl font-bold mb-2">Welcome back</h1>
        </div>
        <div className="p-8 rounded-2xl border border-white/8 bg-white/3">
          {error && <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}
          <button onClick={handleGoogleLogin} className="w-full flex items-center justify-center gap-3 py-3 rounded-xl border border-white/10 bg-white/5 hover:bg-white/8 transition-all text-sm font-medium mb-6">Continue with Google</button>
          <form onSubmit={handleLogin} className="space-y-4">
            <div><label className="block text-sm text-white/60 mb-1.5">Email</label><input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-white/30 focus:outline-none focus:border-purple-500/50 text-sm" placeholder="you@example.com" /></div>
            <div><label className="block text-sm text-white/60 mb-1.5">Password</label><input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-white/30 focus:outline-none focus:border-purple-500/50 text-sm" placeholder="Password" /></div>
            <button type="submit" disabled={loading} className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-purple-600 hover:bg-purple-500 disabled:opacity-50 transition-all font-medium">{loading && <Loader2 className="w-4 h-4 animate-spin" />}Sign in</button>
          </form>
          <p className="text-center text-sm text-white/40 mt-6">Don&apos;t have an account? <Link href="/auth/signup" className="text-purple-400 hover:text-purple-300">Sign up</Link></p>
        </div>
      </div>
    </div>
  )
}
