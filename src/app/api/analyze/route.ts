import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'
import { createClient } from '@/lib/supabase/server'

const analyzeSchema = z.object({
  source_type: z.enum(['youtube', 'url', 'upload']),
  url: z.string().url().optional(),
  title: z.string().optional(),
  storage_path: z.string().optional(),
})

function extractYouTubeId(url: string): string | null {
  const patterns = [
    /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})/,
    /youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})/,
  ]
  for (const pattern of patterns) {
    const match = url.match(pattern)
    if (match) return match[1]
  }
  return null
}

export async function POST(request: NextRequest) {
  const supabase = await createClient()

  const { data: { user }, error: authError } = await supabase.auth.getUser()
  if (authError || !user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  let body: unknown
  try {
    body = await request.json()
  } catch {
    return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 })
  }

  const parsed = analyzeSchema.safeParse(body)
  if (!parsed.success) {
    return NextResponse.json({ error: parsed.error.flatten() }, { status: 400 })
  }

  const { source_type, url, title, storage_path } = parsed.data

  if (source_type !== 'upload' && !url) {
    return NextResponse.json({ error: 'URL is required for youtube/url sources' }, { status: 400 })
  }

  let youtubeId: string | null = null
  if (source_type === 'youtube' && url) {
    youtubeId = extractYouTubeId(url)
    if (!youtubeId) {
      return NextResponse.json({ error: 'Invalid YouTube URL' }, { status: 400 })
    }
  }

  const videoTitle = title || (youtubeId ? `YouTube Video ${youtubeId}` : 'Untitled Video')

  const { data: video, error: videoError } = await supabase
    .from('videos')
    .insert({
      user_id: user.id,
      title: videoTitle,
      source_type,
      source_url: url,
      youtube_id: youtubeId,
      storage_path,
      status: 'pending',
    })
    .select()
    .single()

  if (videoError || !video) {
    return NextResponse.json({ error: 'Failed to create video record' }, { status: 500 })
  }

  const { data: job, error: jobError } = await supabase
    .from('processing_jobs')
    .insert({
      video_id: video.id,
      user_id: user.id,
      status: 'queued',
      progress: 0,
      current_stage: 'Waiting to start',
    })
    .select()
    .single()

  if (jobError || !job) {
    return NextResponse.json({ error: 'Failed to create processing job' }, { status: 500 })
  }

  return NextResponse.json({
    video_id: video.id,
    job_id: job.id,
    status: 'queued',
    message: 'Video queued for processing. Check job status for updates.',
  })
}