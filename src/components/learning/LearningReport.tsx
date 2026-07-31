"use client"

import { BookOpen, Lightbulb, Target, AlertTriangle, TrendingUp, CheckCircle } from "lucide-react"
import { cn, formatTime } from "@/lib/utils"

interface LearningReportData {
  learning_outcomes?: string[]
  key_concepts?: Array<{ concept: string; definition: string; timestamp?: number }>
  key_facts?: string[]
  action_items?: string[]
  misconceptions?: Array<{ misconception: string; correction: string }>
  next_topics?: string[]
  prerequisites?: string[]
}

interface LearningReportProps {
  report: LearningReportData
  onSeek?: (timestamp: number) => void
  className?: string
}

export function LearningReport({ report, onSeek, className }: LearningReportProps) {
  if (!report) return null

  return (
    <div className={cn("space-y-6", className)}>
      {report.learning_outcomes && report.learning_outcomes.length > 0 && (
        <div className="p-6 rounded-2xl border border-white/8 bg-white/3">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <Target className="w-4 h-4 text-green-400" />
            Learning Outcomes
          </h3>
          <ul className="space-y-2">
            {report.learning_outcomes.map((outcome, i) => (
              <li key={i} className="text-sm text-white/70 flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0 mt-0.5" />
                {outcome}
              </li>
            ))}
          </ul>
        </div>
      )}

      {report.key_concepts && report.key_concepts.length > 0 && (
        <div className="p-6 rounded-2xl border border-white/8 bg-white/3">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-blue-400" />
            Key Concepts
          </h3>
          <div className="space-y-3">
            {report.key_concepts.map((kc, i) => (
              <div key={i} className="p-3 rounded-xl bg-white/5">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium text-sm">{kc.concept}</span>
                  {kc.timestamp !== undefined && kc.timestamp !== null && onSeek && (
                    <button
                      onClick={() => onSeek(kc.timestamp!)}
                      className="text-xs text-purple-400 font-mono hover:text-purple-300"
                    >
                      {formatTime(kc.timestamp)}
                    </button>
                  )}
                </div>
                <p className="text-xs text-white/50">{kc.definition}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {report.key_facts && report.key_facts.length > 0 && (
        <div className="p-6 rounded-2xl border border-white/8 bg-white/3">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-yellow-400" />
            Key Facts
          </h3>
          <ul className="space-y-2">
            {report.key_facts.map((fact, i) => (
              <li key={i} className="text-sm text-white/70 flex items-start gap-2">
                <span className="text-yellow-400 mt-0.5">-</span>
                {fact}
              </li>
            ))}
          </ul>
        </div>
      )}

      {report.action_items && report.action_items.length > 0 && (
        <div className="p-6 rounded-2xl border border-white/8 bg-white/3">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-purple-400" />
            Action Items
          </h3>
          <ul className="space-y-2">
            {report.action_items.map((item, i) => (
              <li key={i} className="text-sm text-white/70 flex items-start gap-2">
                <span className="w-4 h-4 rounded-full border border-purple-400/50 flex-shrink-0 mt-0.5" />
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {report.misconceptions && report.misconceptions.length > 0 && (
        <div className="p-6 rounded-2xl border border-white/8 bg-white/3">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-orange-400" />
            Common Misconceptions
          </h3>
          <div className="space-y-3">
            {report.misconceptions.map((m, i) => (
              <div key={i} className="p-3 rounded-xl bg-orange-500/5 border border-orange-500/10">
                <div className="text-sm text-orange-300 mb-1">- {m.misconception}</div>
                <div className="text-sm text-green-300">+ {m.correction}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {report.next_topics && report.next_topics.length > 0 && (
        <div className="p-6 rounded-2xl border border-white/8 bg-white/3">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-cyan-400" />
            What to Learn Next
          </h3>
          <div className="flex flex-wrap gap-2">
            {report.next_topics.map((topic, i) => (
              <span key={i} className="px-3 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-xs text-cyan-300">
                {topic}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}