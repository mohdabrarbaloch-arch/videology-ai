# Videology — Watch. Analyze. Learn.

> **Production-ready AI Video Intelligence SaaS platform**
> Built by Abrar Baloch · Powered by GPT-4o + Whisper + DALL-E 3 + Supabase

[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)](https://typescriptlang.org)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-green)](https://supabase.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-Python-red)](https://fastapi.tiangolo.com)

---

## 🎯 What is Videology?

Videology is a production-ready AI video intelligence platform that transforms any video into structured knowledge:

- **Transcription** - OpenAI Whisper with chunked processing for videos of any length
- **AI Analysis** - GPT-4o generates summaries, topics, chapters, key moments, entities
- **RAG Chat** - Ask any question about a video, get answers with timestamp citations
- **Quiz Generation** - Auto-generated MCQ, true/false, and short-answer quizzes
- **AI Thumbnails** - DALL-E 3 generates 6 professional thumbnail variants
- **Learning Reports** - Outcomes, key concepts, action items, misconceptions
- **Multilingual** - Translate transcripts to 10+ languages

---

## Architecture

- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS (Vercel)
- **Backend**: Python FastAPI (Railway / Fly.io)
- **Database**: Supabase PostgreSQL + pgvector
- **Storage**: Supabase Storage (private buckets)
- **Auth**: Supabase Auth (email/password + Google OAuth)
- **AI**: OpenAI GPT-4o + Whisper + DALL-E 3 + text-embedding-3-small

## Video Processing Pipeline

```
Submit URL/File
  -> Validate & create DB records
  -> Queue processing job
  -> [Background Worker]
      -> Download (yt-dlp / httpx with SSRF protection)
      -> Extract audio (FFmpeg, 16kHz mono MP3)
      -> Transcribe (Whisper, chunked for long videos)
      -> Analyze (GPT-4o: summary, topics, chapters, entities)
      -> Generate quiz (GPT-4o: MCQ + T/F + short answer)
      -> Generate learning report (GPT-4o)
      -> Generate thumbnails (DALL-E 3, 6 styles)
      -> Create embeddings (text-embedding-3-small)
      -> Store in pgvector for RAG
  -> Realtime status updates via Supabase
```

---

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.11+
- FFmpeg installed (`brew install ffmpeg` / `apt install ffmpeg`)
- Supabase account
- OpenAI API key

### 1. Clone & Install

```bash
git clone https://github.com/mohdabrarbaloch-arch/videology-ai
cd videology-ai

# Frontend
npm install

# Backend
cd backend
pip install -r requirements.txt
cd ..
```

### 2. Environment Variables

```bash
cp .env.example .env.local
```

Fill in your `.env.local`:

```env
# Supabase
MExT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# OpenAI
OPENAI_API_KEY=sk-...

# Backend
BACKEND_URL=http://localhost:8000
BACKEND_API_KEY=your-secret-key
```

### 3. Database Setup

1. Go to your Supabase project -> SQL Editor
2. Run the migration: `supabase/migrations/001_initial_schema.sql`
3. Create storage buckets in Supabase Storage:
   - `videos` (private)
   - `thumbnails` (public)
   - `frames` (private)
   - `audio` (private)

### 4. Run Locally

```bash
# Terminal 1: Next.js frontend
npm run dev

# Terminal 2: FastAPI backend
cd backend
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:3000

---

## Database Schema

| Table | Purpose |
|-------|---------|
| `profiles` | User profiles (auto-created on signup) |
| `videos` | Video records with metadata |
| `processing_jobs` | Job queue with status tracking |
| `transcripts` | Full transcript text |
| `transcript_segments` | Timestamped segments |
| `video_analyses` | GPT-4o analysis results |
| `video_topics` | Extracted topics |
| `video_chapters` | Chapter breakdown |
| `video_key_moments` | Important timestamps |
| `video_entities` | Named entities |
| `video_embeddings` | pgvector embeddings for RAG |
| `thumbnails` | DALL-E 3 generated thumbnails |
| `conversations` | AIchat sessions |
| `messages` | Chat messages with citations |
| `quizzes` | Generated quizzes |
| `quiz_questions` | Individual questions |
| `quiz_attempts` | User quiz attempts |
| `learning_reports` | Learning outcomes |

---

## Deployment

### Frontend (Vercel)

```bash
npm i -g vercel
vercel --prod
```

### Backend (Railway)

```bash
cd backend
railway up
```

## Required API Keys

| Service | Key | Where to get |
|---------|-----|-------------|
| OpenAI | `OPENAI_API_KEY` | platform.openai.com |
| Supabase | URL + keys | supabase.com |
| Google OAuth (optional) | Supabase Auth settings | console.cloud.google.com |

OpenAI models used:
- `gpt-4o` - Analysis, quiz, learning report, translation, RAG
- `whisper-1` - Transcription
- `dall-e-3` - Thumbnail generation
- `text-embedding-3-small` - RAG embeddings

---

## Security

- All API keys are server-side only (never in browser JS)
- SSRF protection on URL downloads (blocks private IP ranges)
- File validation: MIME type + extension + size limit
- Supabase RLS on all tables
- Input validation with Zod (frontend) and Pydantic (backend)

---

## Platform Limitations

1. **YouTube DRM**: Only publicly available videos can be downloaded
2. **File size**: Default 500MB limit (configurable)
3. **Duration**: Very long videos (>2h) may hit OpenAI context limits
4. **DALL-E 3 rate limits**: Thumbnails generated sequentially with 2s delays
5. **Whisper 25MB limit**: Audio is automatically chunked into 10-minute segments

---

## License

MIT - Built by Abrar Baloch
