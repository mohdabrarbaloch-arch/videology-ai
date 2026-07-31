import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  const supabase = await createClient()
  const { data: { user }, error: authError } = await supabase.auth.getUser()
  if (authError || !user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const { data: video, error } = await supabase
    .from('videos')
    .select(`
      *,
      processing_jobs(id, status, progress, current_stage, error_message, created_at, updated_at),
      video_analyses(id, summary, executive_summary, difficulty_level, sentiment, content_type, target_audience, estimated_reading_time),
      video_topics(id, topic, relevance_score, mention_count),
      video_chapters(id, chapter_index, title, summary, start_time, end_time),
      video_key_moments(id, timestamp_seconds, title, description, moment_type, importance_score),
      video_entities(id, entity_text, entity_type, mention_count),
      transcripts(id, language, word_count, duration_seconds),
      thumbnails(id, style, public_url, is_favorite),
      quizzes(id, title, total_questions, difficulty),
      learning_reports(id, learning_outcomes, key_concepts, key_facts, action_items, next_topics)
    `)
    .eq('id', id)
    .eq('user_id', user.id)
    .single()

  if (error || !video) {
    return NextResponse.json({ error: 'Video not found' }, { status: 404 })
  }

  return NextResponse.json(video)
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  const supabase = await createClient()
  const { data: { user }, error: authError } = await supabase.auth.getUser()
  if (authError || !user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const { error } = await supabase
    .from('videos')
    .delete()
    .eq('id', id)
    .eq('user_id', user.id)

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }

  return NextResponse.json({ success: true })
}