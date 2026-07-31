import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

export async function GET(request: NextRequest) {
  const supabase = await createClient()
  const { data: { user }, error: authError } = await supabase.auth.getUser()
  if (authError || !user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const { searchParams } = new URL(request.url)
  const videoId = searchParams.get('video_id')

  let query = supabase
    .from('processing_jobs')
    .select('*, videos(title, source_type)')
    .eq('user_id', user.id)
    .order('created_at', { ascending: false })
    .limit(20)

  if (videoId) {
    query = query.eq('video_id', videoId)
  }

  const { data, error } = await query

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }

  return NextResponse.json({ jobs: data })
}