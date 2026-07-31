import { redirect, notFound } from 'next/navigation'
export const dynamic = "force-dynamic"
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import {
  Play, ArrowLeft, Clock, Globe, BarChart3, BookOpen,
  MessageSquare, Image, FileText, Brain, CheckCircle,
  Loader2, AlertCircle, Tag, Users, Lightbulb
} from 'lucide-react'

function formatTime(seconds: number): string {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  if (h > 0) return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  return `${m}:${s.toString().padStart(2, '0')}`
}

const statusConfig = {
  queued: { label: 'Queued', color: 'text-yellow-400', bg: 'bg-yellow-500/10', icon: Clock },
  downloading: { label: 'Downloading', color: 'text-blue-400', bg: 'bg-blue-500/10', icon: Loader2 },
  extracting_audio: { label: 'Extracting Audio', color: 'text-blue-400', bg: 'bg-blue-500/10', icon: Loader2 },
  transcribing: { label: 'Transcribing', color: 'text-purple-400', bg: 'bg-purple-500/10', icon: Loader2 },
  analyzing: { label: 'Analyzing', color: 'text-purple-400', bg: 'bg-purple-500/10', icon: Loader2 },
  generating_thumbnails: { label: 'Generating Thumbnails', color: 'text-pink-400', bg: 'bg-pink-500/10', icon: Loader2 },
  indexing: { label: 'Indexing', color: 'text-cyan-400', bg: 'bg-cyan-500/10', icon: Loader2 },
  completed: { label: 'Completed', color: 'text-green-400', bg: 'bg-green-500/10', icon: CheckCircle },
  failed: { label: 'Failed', color: 'text-red-400', bg: 'bg-red-500/10', icon: AlertCircle },
}

export default async function VideoDetailPage({
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
    .select(`
      *,
      processing_jobs(id, status, progress, current_stage, error_message),
      video_analyses(summary, executive_summary, difficulty_level, sentiment, content_type, target_audience, estimated_reading_time),
      video_topics(topic, relevance_score, mention_count),
      video_chapters(chapter_index, title, summary, start_time, end_time),
      video_key_moments(timestamp_seconds, title, description, moment_type, importance_score),
      video_entities(entity_text, entity_type, mention_count),
      transcripts(id, language, word_count, full_text),
      thumbnails(id, style, public_url, is_favorite),
      quizzes(id, title, total_questions, difficulty),
      learning_reports(learning_outcomes, key_concepts, key_facts, action_items, next_topics)
    `)
    .eq('id', id)
    .eq('user_id', user.id)
    .single()

  if (!video) notFound()

  const job = Array.isArray(video.processing_jobs) ? video.processing_jobs[0] : video.processing_jobs
  const analysis = Array.isArray(video.video_analyses) ? video.video_analyses[0] : video.video_analyses
  const transcript = Array.isArray(video.transcripts) ? video.transcripts[0] : video.transcripts
  const quiz = Array.isArray(video.quizzes) ? video.quizzes[0] : video.quizzes
  const learningReport = Array.isArray(video.learning_reports) ? video.learning_reports[0] : video.learning_reports
  const topics = video.video_topics || []
  const chapters = video.video_chapters || []
  const keyMoments = video.video_key_moments || []
  const entities = video.video_entities || []
  const thumbnails = video.thumbnails || []

  const jobStatus = (job?.status || video.status) as keyof typeof statusConfig
  const cfg = statusConfig[jobStatus] || statusConfig.queued
  const isProcessing = !['completed', 'failed'].includes(jobStatus)

  return (
    <div className="min-h-screen bg-[#080a0f] text-white">
      <nav className="border-b border-white/5 bg-[#080a0f]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center gap-4">
          <Link href="/videos" className="text-white/40 hover:text-white transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
              <Play className="w-3.5 h-3.5 text-white fill-white" />
            </div>
            <span className="font-bold">Videology</span>
          </div>
          <div className="flex-1" />
          <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium ${cfg.bg} ${cfg.color}`}>
            <cfg.icon className={`w-3 h-3 ${isProcessing ? 'animate-spin' : ''}`} />
            {cfg.label}
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold mb-2">{video.title}</h1>
          <div className="flex items-center gap-4 text-sm text-white/40">
            {video.duration_seconds && (
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" />
                {formatTime(video.duration_seconds)}
              </span>
            )}
            {video.language && (
              <span className="flex items-center gap-1">
                <Globe className="w-3.5 h-3.5" />
                {video.language.toUpperCase()}
              </span>
            )}
            <span>{new Date(video.created_at).toLocaleDateString()}</span>
          </div>
        </div>

        {isProcessing && (
          <div className="mb-8 p-6 rounded-2xl border border-purple-500/20 bg-purple-500/5">
            <div className="flex items-center gap-3 mb-4">
              <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
              <div>
                <div className="font-medium text-purple-300">{job?.current_stage || 'Processing...'}</div>
                <div className="text-xs text-white/40">This page will update when processing completes</div>
              </div>
              <div className="ml-auto text-2xl font-bold text-purple-400">{job?.progress || 0}%</div>
            </div>
            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full transition-all"
                style={{ width: `${job?.progress || 0}%` }}
              />
            </div>
          </div>
        )}

        {jobStatus === 'failed' && (
          <div className="mb-8 p-5 rounded-2xl border border-red-500/20 bg-red-500/5">
            <div className="flex items-center gap-2 text-red-400 mb-2">
              <AlertCircle className="w-5 h-5" />
              <span className="font-medium">Processing failed</span>
            </div>
            <p className="text-sm text-white/50">{job?.error_message || 'An unknown error occurred'}</p>
          </div>
        )}

        {video.status === 'completed' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              {analysis?.summary && (
                <div className="p-6 rounded-2xl border border-white/8 bg-white/3">
                  <h2 className="font-semibold mb-3 flex items-center gap-2">
                    <Brain className="w-4 h-4 text-purple-400" />
                    AI Summary
                  </h2>
                  <p className="text-white/70 text-sm leading-relaxed">{analysis.summary}</p>
                  {analysis.executive_summary && (
                    <div className="mt-4 p-3 rounded-xl bg-purple-500/10 border border-purple-500/20">
                      <div className="text-xs text-purple-300 font-medium mb-1">Executive Summary</div>
                      <p className="text-sm text-white/80">{analysis.executive_summary}</p>
                    </div>
                  )}
                </div>
              )}

              {chapters.length > 0 && (
                <div className="p-6 rounded-2xl border border-white/8 bg-white/3">
                  <h2 className="font-semibold mb-4 flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-blue-400" />
                    Chapters ({chapters.length})
                  </h2>
                  <div className="space-y-3">
                    {chapters.sort((a: { chapter_index: number }, b: { chapter_index: number }) => a.chapter_index - b.chapter_index).map((ch: { chapter_index: number; start_time: number; title: string; summary?: string }) => (
                      <div key={ch.chapter_index} className="flex gap-3">
                        <div className="text-xs text-purple-400 font-mono mt-0.5 flex-shrink-0 w-12">
                          {formatTime(ch.start_time)}
                        </div>
                        <div>
                          <div className="text-sm font-medium">{ch.title}</div>
                          {ch.summary && <div className="text-xs text-white/40 mt-0.5">{ch.summary}</div>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {keyMoments.length > 0 && (
                <div className="p-6 rounded-2xl border border-white/8 bg-white/3">
                  <h2 className="font-semibold mb-4 flex items-center gap-2">
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
                    Key Moments ({keyMoments.length})
                  </h2>
                  <div className="space-y-3">
                    {keyMoments.sort((a: { importance_score?: number }, b: { importance_score?: number }) => (b.importance_score || 0) - (a.importance_score || 0)).slice(0, 8).map((m: { timestamp_seconds: number; title: string; description?: string; moment_type?: string }, i: number) => (
                      <div key={i} className="flex gap-3">
                        <div className="text-xs text-cyan-400 font-mono mt-0.5 flex-shrink-0 w-12">
                          {formatTime(m.timestamp_seconds)}
                        </div>
                        <div>
                          <div className="text-sm font-medium">{m.title}</div>
                          {m.description && <div className="text-xs text-white/40 mt-0.5">{m.description}</div>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {transcript && (
                <div className="p-6 rounded-2xl border border-white/8 bg-white/3">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="font-semibold flex items-center gap-2">
                      <FileText className="w-4 h-4 text-green-400" />
                      Transcript
                    </h2>
                    <Link
                      href={`/videos/${id}/transcript`}
                      className="text-xs text-purple-400 hover:text-purple-300"
                    >
                      View full →
                    </Link>
                  </div>
                  <p className="text-sm text-white/60 leading-relaxed line-clamp-6">
                    {transcript.full_text}
                  </p>
                  <div className="mt-3 text-xs text-white/30">
                    {transcript.word_count?.toLocaleString()} words · {transcript.language?.toUpperCase()}
                  </div>
                </div>
              )}
            </div>

            <div className="space-y-6">
              {analysis && (
                <div className="p-5 rounded-2xl border border-white/8 bg-white/3">
                  <h3 className="font-semibold text-sm mb-4">Analysis Details</h3>
                  <div className="space-y-3 text-sm">
                    {analysis.difficulty_level && (
                      <div className="flex justify-between">
                        <span className="text-white/40">Difficulty</span>
                        <span className="capitalize font-medium">{analysis.difficulty_level}</span>
                      </div>
                    )}
                    {analysis.sentiment && (
                      <div className="flex justify-between">
                        <span className="text-white/40">Sentiment</span>
                        <span className="capitalize font-medium">{analysis.sentiment}</span>
                      </div>
                    )}
                    {analysis.content_type && (
                      <div className="flex justify-between">
                        <span className="text-white/40">Type</span>
                        <span className="capitalize font-medium">{analysis.content_type}</span>
                      </div>
                    )}
                    {analysis.estimated_reading_time && (
                      <div className="flex justify-between">
                        <span className="text-white/40">Read time</span>
                        <span className="font-medium">{analysis.estimated_reading_time} min</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {topics.length > 0 && (
                <div className="p-5 rounded-2xl border border-white/8 bg-white/3">
                  <h3 className="font-semibold text-sm mb-3 flex items-center gap-2">
                    <Tag className="w-4 h-4 text-orange-400" />
                    Topics
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {topics.slice(0, 12).map((t: { topic: string; relevance_score?: number }) => (
                      <span key={t.topic} className="px-2.5 py-1 rounded-full bg-white/5 border border-white/10 text-xs text-white/70">
                        {t.topic}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {entities.length > 0 && (
                <div className="p-5 rounded-2xl border border-white/8 bg-white/3">
                  <h3 className="font-semibold text-sm mb-3 flex items-center gap-2">
                    <Users className="w-4 h-4 text-blue-400" />
                    Entities
                  </h3>
                  <div className="space-y-2">
                    {entities.slice(0, 8).map((e: { entity_text: string; entity_type?: string; mention_count: number }) => (
                      <div key={e.entity_text} className="flex items-center justify-between text-xs">
                        <span className="text-white/70">{e.entity_text}</span>
                        <span className="text-white/30 capitalize">{e.entity_type}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="p-5 rounded-2xl border border-white/8 bg-white/3">
                <h3 className="font-semibold text-sm mb-3">Explore</h3>
                <div className="space-y-2">
                  {[
                    { href: `/videos/${id}/ask`, icon: MessageSquare, label: 'Ask AI', color: 'text-purple-400' },
                    { href: `/videos/${id}/quiz`, icon: BarChart3, label: `Quiz (${quiz?.total_questions || 0} questions)`, color: 'text-blue-400' },
                    { href: `/videos/${id}/thumbnails`, icon: Image, label: `Thumbnails (${thumbnails.length})`, color: 'text-pink-400' },
                    { href: `/videos/${id}/transcript`, icon: FileText, label: 'Full Transcript', color: 'text-green-400' },
                  ].map((link) => (
                    <Link
                      key={link.href}
                      href={link.href}
                      className="flex items-center gap-2.5 p-2.5 rounded-xl hover:bg-white/5 transition-colors text-sm"
                    >
                      <link.icon className={`w-4 h-4 ${link.color}`} />
                      {link.label}
                    </Link>
                  ))}
                </div>
              </div>

              {learningReport?.learning_outcomes && (
                <div className="p-5 rounded-2xl border border-white/8 bg-white/3">
                  <h3 className="font-semibold text-sm mb-3 flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-green-400" />
                    Learning Outcomes
                  </h3>
                  <ul className="space-y-1.5">
                    {(learningReport.learning_outcomes as string[]).slice(0, 4).map((outcome: string, i: number) => (
                      <li key={i} className="text-xs text-white/60 flex items-start gap-2">
                        <span className="text-green-400 mt-0.5">✓</span>
                        {outcome}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}