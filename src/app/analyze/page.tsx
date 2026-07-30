'use client'

import { useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import {
  Upload,
  Link, as LinkIcon,
  Youtube,
  Play,
  Loader2,
  CheckCircle,
  AlertCircle,
  FileVideo,
} from 'lucide-react'

type SourceType = 'youtube' | 'url' | 'upload'

export default function AnalyzePage() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<SourceType>('youtube')
  const [url, setUrl] = useState('')
  const [title, setTitle] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      let storagePath = undefined

      if (activeTab === 'upload' && file) {
        const formData = new FormData()
        formData.append('file', file)
        const uploadRes = await fetch('/api/upload', { method: 'POST', body: formData })
        if (!uploadRes.ok) {
          const err = await uploadRes.json()
          throw new Error(err.error || 'Upload failed')
        }
        const uploadData = await uploadRes.json()
        storagePath = uploadData.storage_path
      }

      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_type: activeTab,
          url: activeTab !== 'upload' ? url : undefined,
          title: title || undefined,
          storage_path: storagePath,
        }),
      })

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.error || 'Analysis failed')
      }

      const data = await res.json()
      setSuccess(`Video queued! Redirecting...`)
      setTimeout(() => router.push(`/videos/${data.video_id}`), 2000)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const tabs = [
    { id: 'youtube' as SourceType, label: 'YouTube URL', icon: Youtube },
    { id: 'url' as SourceType, label: 'Direct URL', icon: LinkIcon },
    { id: 'upload' as SourceType, label: 'Upload File', icon: Upload },
  ]

  return (
    <div className="min-h-screen bg-[#080a0f] text-white">
      <nav className="border-b border-white/5 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
            <Play className="w-4 h-4 text-white fill-white" />
          </div>
          <span className="font-bold text-lg">Videology</span>
        </div>
        <Link href="/dashboard" className="text-sm text-white/60 hover:text-white">Dashboard</Link>
      </nav>
      <div className="max-w-xl mx-auto px-6 py-12">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold mb-3">Analyze a Video</h1>
          <p className="text-white/50">Submit a YouTube URL, direct video URL, or a file upload</p>
        </div>
        <div className="p-8 rounded-2xl border border-white/8 bg-white/3">
          <div className="flex gap-2 mb-6">
            {tabs.map((tab) => (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-medium transition-colors ${activeTab === tab.id ? 'bg-purple-600 text-white' : 'bg-white/5 hover:bs-white/10 text-white/60'}`}>
                <tab.icon className="w4 h-4" />
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            ))}
          </div>
          {error && <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center gap-2"><AlertCircle className="w4 h-4 flex-shrink-0" />{error}</div>}
          {success && <div className="mb-4 p-3 rounded-xl bg-green-500/10 border border-green-500/20 text-green-400 text-sm flex items-center gap-2"><CheckCircle className="w-4 h-4 flex-shrink-0" />{success}</div>}
          <form onSubmit={handleSubmit} className="space-y-4">
            {activeTab !== 'upload' && (
              <div>
                <label className="block text-sm text-white/60 mb-1.5">
                  {activeTab === 'youtube' ? 'YouTube URL' : 'Direct Video URL'}
                </label>
                <input type="url" value={url} onChange={(e) => setUrl(e.target.value)} required
                  placeholder={activeTab === 'youtube' ? 'https://www.youtube.com/watch?v=...' : 'https://example.com/video.mp4'}
                  className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-white/30 focus:outline-none focus:border-purple-500/50 text-sm" />
              </div>
            )}
            {activeTab === 'upload' && (
              <div>
                <label className="block text-sm text-white/60 mb-1.5">Video File</label>
                <input ref={fileInputRef} type="file" accept="video/*" className="hidden"
                  onChange={(event) => setFile(event.target.files?.[0] || null)} />
                <div onClick={() => fileInputRef.current?.click()}
                  className="border-2 border-dashed border-white/20 rounded-xl p-8 text-center cursor-pointer hover:border-purple-500/50 transition-colors">
                  {file ? (
                    <div className="flex items-center justify-center gap-3">
                      <FileVideo className="w6 h-6 text-purple-400" />
                      <div className="text-left">
                        <p className="font-medium text-sm">{file.name}</p>
                        <p className="text-xs text-white/50">{(video.size / 1024 / 1024).toFixed(1)} MB</p>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <Upload className="w-8 h-8 text-white/30 mx-auto mb-3" />
                      <p className="text-sm text-white/50">Click to select a video file</p>
                      <p className="text-xs text-white/30 mt-1">MP4, WebM, MOV, MKV • Max 500MB</p>
                    </div>
                  )}
                </div>
              </div>
            )}
            <div>
              <label className="block text-sm text-white/60 mb-1.5">Custom Title <span className="text-white/30">(optional)</span></label>
              <input type="text" value={title} onChange={(e) => setTitle(e.target.value)}
                placeholder="My Video Title"
                className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-white/30 focus:outline-none focus:border-purple-500/50 text-sm" />
            </div>
            <button type="submit" disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-purple-600 hover:bg-purple-500 disabled:opacity-50 transition-colors font-medium">
              {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Processing...</> : 'Analyze Video'}
            </button>
          </form>
        </div>
        <div className="mt-8 p-6 rounded-2xl border border-white/5 bg-white/2">
          <h3 className="font-semibold mb-4">What happens next?</h3>
          <ol className="space-y-2 text-sm text-white/60">
            {['Download & validate video', 'Extract audio with FFmpeg', 'Transcribe with Whisper', 'Analyze with GPT-4o', 'Generate AI thumbnails', 'Index for RAG chat'].map((step, i) => (
              <li key={i} className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-purple-500/20 text-purple-400 text-xs flex items-center justify-center flex-shrink-0">{i + 1}</span>
                {step}
              </li>
            ))}
          </ol>
        </div>
      </div>
    </div>
  )
}
