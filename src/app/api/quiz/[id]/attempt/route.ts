import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'
import { createClient } from '@/lib/supabase/server'

const attemptSchema = z.object({
  answers: z.record(z.string(), z.string()),
  time_taken_seconds: z.number().optional(),
})

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id: quizId } = await params
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

  const parsed = attemptSchema.safeParse(body)
  if (!parsed.success) {
    return NextResponse.json({ error: parsed.error.flatten() }, { status: 400 })
  }

  const { answers, time_taken_seconds } = parsed.data

  const { data: questions } = await supabase
    .from('quiz_questions')
    .select('id, correct_answer, question_type')
    .eq('quiz_id', quizId)

  if (!questions || questions.length === 0) {
    return NextResponse.json({ error: 'Quiz not found' }, { status: 404 })
  }

  let score = 0
  for (const q of questions) {
    const userAnswer = answers[q.id]
    if (!userAnswer) continue

    if (q.question_type === 'short_answer') {
      const correct = q.correct_answer.toLowerCase().trim()
      const given = userAnswer.toLowerCase().trim()
      if (correct.includes(given) || given.includes(correct)) score++
    } else {
      if (userAnswer.toLowerCase() === q.correct_answer.toLowerCase()) score++
    }
  }

  const percentage = (score / questions.length) * 100

  const { data: attempt } = await supabase
    .from('quiz_attempts')
    .insert({
      quiz_id: quizId,
      user_id: user.id,
      answers,
      score,
      total_questions: questions.length,
      percentage,
      time_taken_seconds,
    })
    .select()
    .single()

  return NextResponse.json({ attempt, score, total: questions.length, percentage })
}