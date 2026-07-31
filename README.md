# Videology AI

> **Watch. Analyze. Learn.**
>
> AI Video Intelligence SaaS Platform — transform any video into searchable knowledge.

Created by **Abrar Baloch**

## Overview

Videology is a production-ready AI video intelligence platform that takes any video (YouTube URL, direct URL, or file upload) and produces:

- **Full transcript** with timestamps (OpenAI Whisper)
- **AI analysis** — summary, topics, chapters, key moments, entities, sentiment (GPT-4o)
- **AI-generated thumbnails** — 6 style variants (DALL-E 3)
- **RAG-powered Q&A** — ask questions about the video with timestamp citations (pgvector + GPT-4o)
- **Interactive quizzes** — MCQ, true/false, short answer with scoring (GPT-4o)
- **Learning reports** — outcomes, key concepts, action items, misconceptions (GPT-4o)
- **Multilingual translations** — 10 languages (GPT-4o)

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     Next.js Frontend                        │
│  (TypeScript, Tailwind CSS, shadcn/ui, Supabase Auth)       │
├──────────────────────────────────────────────────────────────────┤
│  Pages: Landing, Dashboard, Analyze, Videos, Video Detail,  │
│         Transcript, AI Ask, Quiz, Thumbnails, Settings      │
├──────────────────────────────────────────────────────────────────┤
│              Next.js API Routes (Server-side)               │
│  /api/videos, /api/ask, /api/upload, /api/jobs, /api/quiz   │
├────────────────────────────────────────┬─────────────────────────┤
│   Supabase (Postgres │     Python FastAPI Backend           │
│   + Storage + Auth + │     (FFmpeg, yt-dlp, OpenAI)         │
│   Realtime + pgvector)│                                     │
│                      │  Routers: videos, pipeline,          │
│  19 tables with RLS  │  transcription, analysis,            │
│  pgvector embeddings │  thumbnails, ask, quiz, learning,    │
│  4 storage buckets   │  translation                         │
│                      │  Services: ffmpeg, youtube,          │
│                      │  storage, embedding                  │
│                      │  Worker: job_worker.py               │
└────────────────────────────────┴─────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui, Lucide icons |
| Backend | Python FastAPI, FFmpeg, yt-dlp |
| Database | Supabase PostgreSQL + pgvector |
| Storage | Supabase Storage (private buckets) |
| Auth | Supabase Auth (email/password + Google OAuth) |
| AI | OpenAI GPT-4o, Whisper, DALL-E 3, text-embedding-3-small |
| Queue | Supabase/Postgres-backed job queue |
| Realtime | Supabase Realtime (job status updates) |

## Video Processing Pipeline

```
User submits URL/Upload
→ Validate source (SSRF check, MIME validation)
→ Create Video record in Supabase
→ Create processing job (status: queued)
→ Background worker picks up job
→ Download media (yt-dlp for YouTube, curl for direct URL, Storage for uploads)
→ FFmpeg: extract audio (MP3, 16kHz mono, chunked for long videos)
→ OpenAI Whisper: transcribe each chunk → timestamped segments
→ Language detection
→ Transcript chunking + embedding (text-embedding-3-small)
→ Store embeddings in pgvector
→ GPT-4o: analyze transcript → summary, topics, chapters, key moments, entities
→ FFmpeg: extract representative frames
→ GPT-4o Vision: analyze frames (slides, diagrams, code)
→ DALL-E 3: generate 6 thumbnail variants
→ GPT-4o: generate quiz (MCQ, true/false, short answer)
→ GPT-4o: generate learning report
→ Update job status: completed
→ Frontend updates via Supabase Realtime
```

### Job Statuses

`queued → downloading → extracting_audio → transcribing → analyzing → generating_thumbnails → indexing → completed / failed`

## Database Schema

19 tables with foreign keys, indexes, and RLS policies:

| Table | Purpose |
|-------|---------|
| `profiles` | User profiles (linked to Supabase Auth) |
| `videos` | Video metadata |
| `video_sources` | Source URLs (YouTube, direct, upload) |
| `processing_jobs` | Job queue with status, progress, retries |
| `transcripts` | Full transcript text + language |
| `transcript_segments` | Timestamped segments |
| `video_analyses` | GPT-4o analysis results |
| `video_topics` | Extracted topics with relevance scores |
| `video_chapters` | Chapter breakdown with timestamps |
| `video_key_moments` | Important moments with timestamps |
| `video_embeddings` | pgvector embeddings for RAG |
| `thumbnails` | DALL-E 3 generated thumbnails |
| `conversations` | AI Ask conversation history |
| `messages` | Individual chat messages |
| `quizzes` | Generated quizzes |
| `quiz_questions` | Quiz questions with answers |
| `quiz_attempts` | User quiz attempts with scores |
| `learning_reports` | Learning report data |
| `translations` | Multilingual translations |

## Getting Started

### Prerequisites

- Node.js 20+
- Python 3.11+
- FFmpeg
- yt-dlp
- Supabase account
- OpenAI API key

### 1. Clone the Repository

```bash
git clone https://github.com/mohdabrarbaloch-arch/videology-ai.git
cd videology-ai
```

### 2. Environment Setup

```bash
cp .env.example .env.local
# Edit .env.local with your actual values
```

### 3. Frontend Setup

```bash
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

### 4. Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend runs on `http://localhost:8000`

### 5. Database Setup

Run the SQL migrations in your Supabase SQL editor in order:

1. `supabase/migrations/001_initial_schema.sql` — All tables, initial RLS, pgvector
2. `supabase/migrations/002_rls.sql` — Additional RLS policies
3. `supabase/migrations/003_indexes.sql` — Performance indexes

### 6. Start the Job Worker

```bash
cd backend
python -m app.workers.job_worker
```

### 7. Run Tests

```bash
# Backend tests
cd backend
python -m pytest tests/ -v

# Frontend lint
npm run lint

# Frontend build
npm run build
```

## Environment Variables

```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Optional
GEMINI_API_KEY=your_gemini_key
AI_MODEL=gpt-4o
TRANSCRIPTION_MODEL=whisper-1
IMAGE_MODEL=dall-e-3
MAX_VIDEO_SIZE_MB=500

# Backend
FASTAPI_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000

# Worker
WORKER_POLL_INTERVAL=10
WORKER_MAX_RETRIES=3
```

## Deployment

### Frontend → Vercel

1. Push to GitHub
2. Import project in Vercel
3. Add environment variables
4. Deploy

### Backend → Docker (any cloud)

```bash
cd backend
docker build -t videology-backend .
docker run -p 8000:8000 --env-file .env videology-backend
```

### Database → Supabase

1. Create a new Supabase project
2. Run migrations in SQL editor
3. Create storage buckets: `videos`, `thumbnails`, `frames`, `audio`
4. Enable pgvector extension

## External API Keys Required

| Service | Key | Purpose |
|---------|-----|---------|
| OpenAI | `OPENAI_API_KEY` | GPT-4o analysis, Whisper transcription, DALL-E 3 thumbnails, text-embedding-3-small |
| Supabase | Project URL + Keys | Database, Storage, Auth, Realtime |
| Google (optional) | `GEMINI_API_KEY` | Fallback AI model |

## Security

- ✅ All API keys server-side only (never exposed to browser)
- ✅ SSRF protection on URL downloads (blocks private IPs, localhost, metadata endpoints)
- ✅ File validation (MIME type + extension + size limit)
- ✅ Supabase RLS on all tables (users only access their own data)
- ✅ Input validation with Zod (frontend) and Pydantic (backend)
- ✅ No DRM bypass — respects YouTube Terms of Service

## Project Structure

```
videology-ai/
├── src/                          # Next.js frontend
│   ├── app/                      # Pages and API routes
│   │   ├── page.tsx              # Landing page
│   │   ├── dashboard/            # Dashboard
│   │   ├── analyze/              # Submit video for analysis
│   │   ├── videos/               # Video list and detail
│   │   │   └── [id]/             # Video detail with tabs
│   │   │       ├── ask/          # AI Ask (RAG chat)
│   │   │       ├── quiz/         # Interactive quiz
│   │   │       ├── transcript/   # Full transcript
│   │   │       └── thumbnails/   # Generated thumbnails
│   │   ├── settings/             # API keys, preferences
│   │   ├── auth/                 # Login, signup, callback
│   │   └── api/                  # API routes
│   ├── components/               # React components
│   │   ├── ui/                   # shadcn/ui base components
│   │   ├── video/                # Video player, transcript, chapters
│   │   ├── chat/                 # AI Ask chat interface
│   │   ├── quiz/                 # Quiz interface
│   │   ├── thumbnails/           # Thumbnail grid
│   │   ├── learning/             # Learning report
│   │   └── layout/               # Navbar
│   ├── hooks/                    # Custom React hooks
│   ├── lib/                      # Utilities, Supabase clients
│   └── types/                    # TypeScript types
├── backend/                      # Python FastAPI backend
│   ├── app/
│   │   ├── main.py               # FastAPI app entry point
│   │   ├── config.py             # Settings
│   │   ├── models/               # Pydantic models
│   │   ├── routers/              # API routers
│   │   │   ├── health.py
│   │   │   ├── jobs.py
│   │   │   ├── videos.py         # CRUD + SSRF validation
│   │   │   ├── pipeline.py       # Processing pipeline
│   │   │   ├── transcription.py  # Whisper integration
│   │   │   ├── analysis.py       # GPT-4o analysis
│   │   │   ├── thumbnails.py     # DALL-E 3 thumbnails
│   │   │   ├── ask.py            # RAG endpoint
│   │   │   ├── quiz.py           # Quiz generation
│   │   │   ├── learning.py       # Learning reports
│   │   │   └── translation.py    # Multilingual translation
│   │   ├── services/             # Business logic
│   │   │   ├── downloader.py
│   │   │   ├── transcriber.py
│   │   │   ├── analyzer.py
│   │   │   ├── thumbnail_generator.py
│   │   │   ├── ffmpeg_service.py
│   │   │   ├── youtube_service.py
│   │   │   ├── storage_service.py
│   │   │   └── embedding_service.py
│   │   └── workers/              # Background workers
│   │       ├── job_processor.py
│   │       └── job_worker.py
│   ├── tests/                    # Unit + integration tests
│   ├── requirements.txt
│   └── Dockerfile
├── supabase/
│   ├── migrations/
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_rls.sql
│   │   └── 003_indexes.sql
│   └── seed.sql
├── .env.example
├── .gitignore
└── README.md
```

## License

MIT

## Author

**Abrar Baloch** — [GitHub](https://github.com/mohdabrarbaloch-arch)
