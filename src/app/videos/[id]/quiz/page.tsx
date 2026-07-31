'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { ArrowLeft, Play, CheckCircle, XCircle, BarChart3, Loader2 } from 'lucide-react'
import { createClient } from '@/lib/supabase/client'

interface Question {
  id: string
  question_index: number
  question_type: 'mcq' | 'true_false' | 'short_answer'
  question_text: string
  options?: string[]
  correct_answer: string
  explanation?: string
  difficulty?: string
  timestamp_reference?: number
}

interface Quiz {
  id: string
  title: string
  total_questions: number
  difficulty?: string
}

export default function QuizPage() {
  const params = useParams()
  const videoId = params.id as string

  const [quiz, setQuiz] = useState<Quiz | null>(null)
  const [questions, setQuestions] = useState<Question[]>([])
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [submitted, setSubmitted] = useState(false)
  const [result, setResult] = useState<{ score: number; total: number; percentage: number } | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [startTime] = useState(Date.now())

  useEffect(() => {
    const load = async () => {
      const supabase = createClient()
      const { data: quizData } = await supabase
        .from('quizzes')
        .select('*')
        .eq('video_id', videoId)
        .single()

      if (quizData) {
        setQuiz(quizData)
        const { data: qs } = await supabase
          .from('quiz_questions')
          .select('*')
          .eq('quiz_id', quizData.id)
          .order('question_index')
        setQuestions(qs || [])
      }
      setLoading(false)
    }
    load()
  }, [videoId])

  const handleAnswer = (questionId: string, answer: string) => {
    if (submitted) return
    setAnswers((prev) => ({ ...prev, [questionId]: answer }))
  }

  const handleSubmit = async () => {
    if (!quiz) return
    setSubmitting(true)
    const timeTaken = Math.floor((Date.now() - startTime) / 1000)

    const res = await fetch(`/api/quiz/${quiz.id}/attempt`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers, time_taken_seconds: timeTaken }),
    })

    if (res.ok) {
      const data = await res.json()
      setResult({ score: data.score, total: data.total, percentage: data.percentage })
      setSubmitted(true)
    }
    setSubmitting(false)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#080a0f] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
      </div>
    )
  }

  if (!quiz || questions.length === 0) {
    return (
      <div className="min-h-screen bg-[#080a0f] text-white flex items-center justify-center">
        <div className="text-center">
          <BarChart3 className="w-12 h-12 text-white/10 mx-auto mb-4" />
          <h2 className="text-xl font-bold mb-2">No quiz available</h2>
          <p className="text-white/40 text-sm mb-6">The quiz hasn&apos;t been generated yet for this video.</p>
          <Link href={`/videos/${videoId}`} className="text-purple-400 hover:text-purple-300">
            ← Back to video
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#080a0f] text-white">
      <nav className="border-b border-white/5 bg-[#080a0f]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-3xl mx-auto px-6 py-4 flex items-center gap-4">
          <Link href={`/videos/${videoId}`} className="text-white/40 hover:text-white transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
              <Play className="w-3.5 h-3.5 text-white fill-white" />
            </div>
            <span className="font-bold">Videology</span>
          </div>
          <div className="flex items-center gap-2 ml-2 text-white/40 text-sm">
            <BarChart3 className="w-4 h-4" />
            Quiz
          </div>
        </div>
      </nav>

      <div className="max-w-3xl mx-auto px-6 py-8">
        {submitted && result && (
          <div className={`mb-8 p-6 rounded-2xl border text-center ${
            result.percentage >= 70
              ? 'border-green-500/30 bg-green-500/10'
              : 'border-orange-500/30 bg-orange-500/10'
          }`}>
            <div className="text-5xl font-bold mb-2">{result.percentage.toFixed(0)}%</div>
            <div className="text-lg font-semibold mb-1">
              {result.score} / {result.total} correct
            </div>
            <div className={`text-sm ${result.percentage >= 70 ? 'text-green-400' : 'text-orange-400'}`}>
              {result.percentage >= 90 ? '🎉 Excellent!' : result.percentage >= 70 ? '👍 Good job!' : '📚 Keep studying!'}
            </div>
          </div>
        )}

        <div className="mb-6">
          <h1 className="text-2xl font-bold mb-1">{quiz.title}</h1>
          <div className="flex items-center gap-3 text-sm text-white/40">
            <span>{questions.length} questions</span>
            {quiz.difficulty && <span className="capitalize">{quiz.difficulty}</span>}
          </div>
        </div>

        <div className="space-y-6">
          {questions.map((q, idx) => {
            const userAnswer = answers[q.id]
            const isCorrect = submitted && userAnswer?.toLowerCase() === q.correct_answer.toLowerCase()
            const isWrong = submitted && userAnswer && !isCorrect

            return (
              <div key={q.id} className={`p-6 rounded-2xl border transition-all ${
                submitted
                  ? isCorrect ? 'border-green-500/30 bg-green-500/5'
                  : isWrong ? 'border-red-500/30 bg-red-500/5'
                  : 'border-white/8 bg-white/3'
              }`}>
                <div className="flex items-start gap-3 mb-4">
                  <span className="text-xs text-white/30 font-mono mt-1 flex-shrink-0">Q{idx + 1}</span>
                  <div>
                    <p className="font-medium text-sm leading-relaxed">{q.question_text}</p>
                    {q.difficulty && (
                      <span className={`text-xs mt-1 inline-block capitalize ${
                        q.difficulty === 'easy' ? 'text-green-400' :
                        q.difficulty === 'medium' ? 'text-yellow-400' : 'text-red-400'
                      }`}>{q.difficulty}</span>
                    )}
                  </div>
                  {submitted && (
                    <div className="ml-auto flex-shrink-0">
                      {isCorrect ? <CheckCircle className="w-5 h-5 text-green-400" /> : isWrong ? <XCircle className="w-5 h-5 text-red-400" /> : null}
                    </div>
                  )}
                </div>

                {q.question_type === 'mcq' && q.options && (
                  <div className="space-y-2 ml-6">
                    {q.options.map((opt) => {
                      const isSelected = userAnswer === opt
                      const isCorrectOpt = submitted && opt.toLowerCase() === q.correct_answer.toLowerCase()
                      return (
                        <button
                          key={opt}
                          onClick={() => handleAnswer(q.id, opt)}
                          disabled={submitted}
                          className={`w-full text-left px-4 py-2.5 rounded-xl text-sm transition-all border ${
                            isCorrectOpt && submitted ? 'border-green-500/50 bg-green-500/10 text-green-300' :
                            isSelected && isWrong ? 'border-red-500/50 bg-red-500/10 text-red-300' :
                            isSelected ? 'border-purple-500/50 bg-purple-500/10 text-purple-300' :
                            'border-white/8 bg-white/3 hover:border-white/15 text-white/70'
                          }`}
                        >
                          {opt}
                        </button>
                      )
                    })}
                  </div>
                )}

                {q.question_type === 'true_false' && (
                  <div className="flex gap-3 ml-6">
                    {['True', 'False'].map((opt) => {
                      const isSelected = userAnswer === opt
                      const isCorrectOpt = submitted && opt.toLowerCase() === q.correct_answer.toLowerCase()
                      return (
                        <button
                          key={opt}
                          onClick={() => handleAnswer(q.id, opt)}
                          disabled={submitted}
                          className={`flex-1 py-2.5 rounded-xl text-sm font-medium transition-all border ${
                            isCorrectOpt && submitted ? 'border-green-500/50 bg-green-500/10 text-green-300' :
                            isSelected && isWrong ? 'border-red-500/50 bg-red-500/10 text-red-300' :
                            isSelected ? 'border-purple-500/50 bg-purple-500/10 text-purple-300' :
                            'border-white/8 bg-white/3 hover:border-white/15 text-white/70'
                          }`}
                        >
                          {opt}
                        </button>
                      )
                    })}
                  </div>
                )}

                {q.question_type === 'short_answer' && (
                  <div className="ml-6">
                    <input
                      type="text"
                      value={userAnswer || ''}
                      onChange={(e) => handleAnswer(q.id, e.target.value)}
                      disabled={submitted}
                      placeholder="Type your answer..."
                      className="w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white placeholder-white/30 focus:outline-none focus:border-purple-500/50 text-sm disabled:opacity-60"
                    />
                  </div>
                )}

                {submitted && q.explanation && (
                  <div className="mt-4 ml-6 p-3 rounded-xl bg-white/5 border border-white/8">
                    <div className="text-xs text-white/40 mb-1">Explanation</div>
                    <p className="text-sm text-white/70">{q.explanation}</p>
                    {submitted && !isCorrect && (
                      <p className="text-sm text-green-400 mt-1">
                        Correct answer: <strong>{q.correct_answer}</strong>
                      </p>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {!submitted && (
          <div className="mt-8 flex justify-end">
            <button
              onClick={handleSubmit}
              disabled={submitting || Object.keys(answers).length === 0}
              className="flex items-center gap-2 px-8 py-3 rounded-xl bg-purple-600 hover:bg-purple-500 disabled:opacity-50 transition-all font-semibold"
            >
              {submitting && <Loader2 className="w-4 h-4 animate-spin" />}
              Submit Quiz ({Object.keys(answers).length}/{questions.length} answered)
            </button>
          </div>
        )}
      </div>
    </div>
  )
}