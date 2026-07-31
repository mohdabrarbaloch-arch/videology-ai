import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

function formatSRTTime(seconds: number): string {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  const ms = Math.floor((seconds % 1) * 1000)
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')},${ms.toString().padStart(3, '0')}`
}

function formatVTTTime(seconds: number): string {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  const ms = Math.floor((seconds % 1) * 1000)
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}.${ms.toString().padStart(3, '0')}`
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  const { searchParams } = new URL(request.url)
  const format = searchParams.get('format') || 'txt'

  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  const { data: transcript } = await supabase
    .from('transcripts')
    .select('full_text, language')
    .eq('video_id', id)
    .single()

  if (!transcript) return NextResponse.json({ error: 'Transcript not found' }, { status: 404 })

  const { data: video } = await supabase
    .from('videos')
    .select('title')
    .eq('id', id)
    .eq('user_id', user.id)
    .single()

  if (!video) return NextResponse.json({ error: 'Not found' }, { status: 404 })

  const filename = video.title.replace(/[^a-zA-Z0-9]/g, '_').slice(0, 50)

  if (format === 'txt') {
    return new NextResponse(transcript.full_text, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Disposition': `attachment; filename="${filename}_transcript.txt"`,
      },
    })
  }

  if (format === 'srt' || format === 'vtt') {
    const { data: segments } = await supabase
      .from('transcript_segments')
      .select('start_time, end_time, text')
      .eq('video_id', id)
      .order('segment_index')

    if (!segments) return NextResponse.json({ error: 'Segments not found' }, { status: 404 })

    let content = ''
    if (format === 'vtt') {
      content = 'WEBVTT\n\n'
      content += segments.map((seg, i) => {
        return `${i + 1}\n${formatVTTTime(seg.start_time)} --> ${formatVTTTime(seg.end_time)}\n${seg.text}\n`
      }).join('\n')
    } else {
      content = segments.map((seg, i) => {
        return `${i + 1}\n${formatSRTTime(seg.start_time)} --> ${formatSRTTime(seg.end_time)}\n${seg.text}\n`
      }).join('\n')
    }

    return new NextResponse(content, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Disposition': `attachment; filename="${filename}_transcript.${format}"`,
      },
    })
  }

  return NextResponse.json({ error: 'Invalid format' }, { status: 400 })
}