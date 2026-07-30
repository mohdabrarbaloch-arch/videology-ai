'use client'

import Link from 'next/link'
import {
  Brain,
  Zap,
  Globe,
  Shield,
  Play,
  ChevronRight,
  Star,
  Users,
  Video,
  MessageSquare,
  BookOpen,
  Image,
  Check,
} from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#080a0f] text-white">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/5 bg-[#080a0f]/95 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
              <Play className="w-4 h-4 text-white fill-white" />
            </div>
            <span className="font-bold text-lg">Videology</span>
          </div>
          <div className="hidden md:flex items-center gap-8">
            <Link href="#features" className="text-sm text-white/60 hover:text-white transition-colors">Features</Link>
            <Link href="#pricing" className="text-sm text-white/60 hover:text-white transition-colors">Pricing</Link>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/auth/login" className="text-sm text-white/60 hover:text-white transition-colors">Sign in</Link>
            <Link href="/auth/signup" className="px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 transition-colors text-sm font-medium">Get Started</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-24 px-6 text-center">
        <div className="max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-purple-500/30 bg-purple-500/10 text-purple-300 text-sm mb-8">
            <Zap className="w-3.5 h-3.5" />
            <span>AI-Powered Video Intelligence</span>
          </div>
          <h1 className="text-5xl md:text-7xl font-bold leading-tight mb-6">
            Watch. Analyze.{' '}
            <span className="bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">Learn.</span>
          </h1>
          <p className="text-xl text-white/60 mb-10 max-w-2xl mx-auto leading-relaxed">
            Transform any video into structured knowledge. Transcribe, analyze, and learn with GPT-4o.
          </p>
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <Link href="/auth/signup" className="px-8 py-3 rounded-xl bg-purple-600 hover:bg-purple-500 transition-colors font-semibold flex items-center gap-2">
              Start Free <ChevronRight className="w-4 h-4" />
            </Link>
            <Link href="/auth/login" className="px-8 py-3 rounded-xl border border-white/20 hover:bg-white/5 transition-colors font-medium">
              Sign In
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 px-6 border-t border-white/5">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">Everything you need to learn from videos</h2>
          <p className="text-center text-white/50 mb-16">Powered by GPT-4o, Whisper, and DALL-E 3</p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { icon: Brain, title: 'AI Transcription', desc: 'OpenAI Whisper with chunked processing for videos of any length. Timestamped segments.' },
              { icon: Zap, title: 'GPT-4o Analysis', desc: 'Summaries, topics, chapters, key moments, entities, and sentiment analysis.' },
              { icon: MessageSquare, title: 'RAG Chat', desc: 'Ask any question about a video. Get answers with timestamp citations.' },
              { icon: BookOpen, title: 'Quiz Generation', desc: 'Auto-generated MCQ, true/false, and short-answer quizzes with scoring.' },
              { icon: Image, title: 'AI Thumbnails', desc: 'DALL-E 3 generates 6 professional thumbnail variants for each video.' },
              { icon: Globe, title: 'Multilingual', desc: 'Translate transcripts to 10+ languages including Urdu, Arabic, Hindi.' },
            ].map((feature, i) => (
              <div key={i} className="p-6 rounded-2xl border border-white/8 bg-white/3 hover:bg-white/5 transition-colors">
                <div className="w-10 h-10 rounded-xl bg-purple-500/15 flex items-center justify-center mb-4">
                  <feature.icon className="w-5 h-5 text-purple-400" />
                </div>
                <h3 className="font-semibold mb-2">{feature.title}</h3>
                <p className="text-sm text-white/50 leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-24 px-6 border-t border-white/5">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">Simple Pricing</h2>
          <p className="text-center text-white/50 mb-16">Start free, upgrade when you need more</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-2xl mx-auto">
            {[/* Free */
              { title: 'Free', price: '$0', features: ['10 videos/pmonth', 'Up to 30 min per video', 'AI transcription', 'Basic analysis', 'RAG chat'], cta: 'Get Started', href: '/auth/signup', highlight: false },
              { title: 'Pro' , price: '$19/9mo', features: ['Unlimited videos', 'Up to 2h per video', 'All AI features', '6 AI thumbnails', 'Quiz generation', 'Learning reports', 'Multilingual'], cta: 'Start Pro', href: '/auth/signup', highlight: true },
            ].map((plan, i) => (
              <div key={i} className={`p-8 rounded-2xl border ${plan.highlight ? 'border-purple-500/50 bg-purple-500/10' : 'border-white/8 bg-white/3'}`}>
                <h3 className="font-bold text-xl mb-2">{plan.title}</h3>
                <div className="text-3xl font-bold mb-6">{plan.price}</div>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((f, j) => (
                    <li key={j} className="flex items-center gap-3 text-sm">
                      <Check className="w-4 h-4 text-purple-400 flex-shrink-0" />
                      <span className="text-white/70">{f}</span>
                    </li>
                  ))}
                </ul>
                <Link href={plan.href} className={`w1-full py-3 rounded-xl text-center font-medium transition-colors ${plan.highlight ? 'bg-purple-600 hover:bg-purple-500' : 'border border-white/20 hover:bg-white/5'}`}>
                  {plan.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-white/5 text-center text-sm text-white/30">
        <p>© 2026 Videology. Built by Abrar Baloch.</p>
      </footer>
    </div>
  )
}
