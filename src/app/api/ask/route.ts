import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'
import OpenAI from 'openai'
import { createClient } from '@/lib/supabase/server'

const askSchema = z.object({
  video_id: z.string().uuid(),
  question: z.string().min(1).max(1000),
  conversation_id: z.string().uuid().optional(),
})

const RAG_SYSTEM_PROMPT = `You are an AI assistant that answers questions about video content.
You have access to transcript excerpts from the video. Answer based ONLY on the provided context.

Rules:
1. Answer based ONLY on the transcript context provided
2. Include timestamp citations when referencing specific moments
3. If the answer is not in the transcript, say: "I couldn't find enough evidence in this video to answer that confidently."
4. Be concise and accurate
5. Format timestamps as [MM:SS] or [HH:MM:SS]`

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
    return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 })
  }

  const parsed = askSchema.safeParse(body)
  if (!parsed.success) {
    return NextResponse.json({ error: parsed.error.flatten() }, { status: 400 })
  }

  const { video_id, question, conversation_id } = parsed.data

  // Verify video belongs to user
  const { data: video } = await supabase
    .from('videos')
    .select('id, title, status')
    .eq('id', video_id)
    .eq('user_id', user.id)
    .single()

  if (!video) {
    return NextResponse.json({ error: 'Video not found' }, { status: 404 })
  }

  if (video.status !== 'completed') {
    return NextResponse.json({ error: 'Video is still being processed' }, { status: 400 })
  }

  // Generate embedding for the question
  const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY })

  const embeddingResponse = await openai.embeddings.create({
    model: process.env.EMBEDDING_MODEL || 'text-embedding-3-small',
    input: question,
  })
  const queryEmbedding = embeddingResponse.data[0].embedding

  // Vector similarity search via Supabase RPC
  const { data: chunks } = await supabase.rpc('match_video_embeddings', {
    query_embedding: queryEmbedding,
    match_video_id: video_id,
    match_count: 8,
    match_threshold: 0.6,
  })

  // Build context from retrieved chunks
  const context = (chunks || [])
    .map((c: { start_time: number; end_time: number; chunk_text: string }) => {
      const startMin = Math.floor(c.start_time / 60)
      const startSec = Math.floor(c.start_time % 60)
      const timestamp = `[${startMin}:${startSec.toString().padStart(2, '0')}]`
      return `${timestamp} ${c.chunk_text}`
    })
    .join('\n\n')

  // Get conversation history
  let convId = conversation_id
  if (!convId) {
    const { data: conv } = await supabase
      .from('conversations')
      .insert({ video_id, user_id: user.id, title: question.slice(0, 100) })
      .select()
      .single()
    convId = conv?.id
  }

  const { data: history } = await supabase
    .from('messages')
    .select('role, content')
    .eq('conversation_id', convId)
    .order('created_at', { ascending: true })
    .limit(10)

  const messages: OpenAI.Chat.ChatCompletionMessageParam[] = [
    { role: 'system', content: RAG_SYSTEM_PROMPT },
    {
      role: 'user',
      content: `VIDEO TITLE: ${video.title}\n\nRELEVANT TRANSCRIPT EXCERPTS:\n${context || 'No relevant excerpts found.'}\n\nQUESTION: ${question}`,
    },
  ]

  if (history && history.length > 0) {
    messages.splice(1, 0, ...(history as OpenAI.Chat.ChatCompletionMessageParam[]))
  }

  const completion = await openai.chat.completions.create({
    model: process.env.AI_MODEL || 'gpt-4o',
    messages,
    temperature: 0.3,
    max_tokens: 1000,
  })

  const answer = completion.choices[0].message.content || ''
  const tokensUsed = completion.usage?.total_tokens || 0

  // Build citations from chunks
  const citations = (chunks || []).slice(0, 3).map((c: { id: string; start_time: number; chunk_text: string }) => ({
    timestamp: c.start_time,
    text: c.chunk_text.slice(0, 150),
    segment_id: c.id,
  }))

  // Store messages
  if (convId) {
    await supabase.from('messages').insert([
      { conversation_id: convId, video_id, user_id: user.id, role: 'user', content: question },
      {
        conversation_id: convId,
        video_id,
        user_id: user.id,
        role: 'assistant',
        content: answer,
        citations,
        tokens_used: tokensUsed,
        model_used: process.env.AI_MODEL || 'gpt-4o',
      },
    ])

    await supabase
      .from('conversations')
      .update({ message_count: (history?.length || 0) + 2 })
      .eq('id', convId)
  }

  return NextResponse.json({
    answer,
    citations,
    conversation_id: convId,
    tokens_used: tokensUsed,
  })
}