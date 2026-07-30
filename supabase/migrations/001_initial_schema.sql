-- ============================================================
-- VIDEOLOGY -- Initial Database Schema
-- Run this in your Supabase SQL editor or via supabase db push
-- ============================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- PROFILES
CREATE TABLE IF NOT EXISTS profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  full_name TEXT,
  avatar_url TEXT,
  openai_api_key_encrypted TEXT,
  preferred_language TEXT DEFAULT 'en',
  timezone TEXT DEFAULT 'UTC',
  plan TEXT DEFAULT 'free' CHECK (plan IN ('free', 'pro')),
  videos_processed INTEGER DEFAULT 0,
  storage_used_bytes BIGINT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- VIDEOS
CREATE TABLE IF NOT EXISTS videos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  source_type TEXT NOT NULL CHECK (source_type IN ('youtube', 'url', 'upload')),
  source_url TEXT,
  youtube_id TEXT,
  storage_path TEXT,
  thumbnail_url TEXT,
  duration_seconds INTEGER,
  file_size_bytes BIGINT,
  mime_type TEXT,
  language TEXT,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
  is_public BOOLEAN DEFAULT FALSE,
  view_count INTEGER DEFAULT 0, 
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- PROCESSING JOBS
CREATE TABLE IF NOT EXISTS processing_jobs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'downloading', 'extracting_audio', 'transcribing', 'analyzing', 'generating_thumbnails', 'indexing', 'completed', 'failed')),
  progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
  current_stage TEXT,
  error_message TEXT,
  error_details JSONB,
  retry_count INTEGER DEFAULT 0,
  max_retries INTEGER DEFAULT 3,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- TRANSCRIPTS
CREATE TABLE IF NOT EXISTS transcripts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  language TEXT NOT NULL,
  full_text TEXT NOT NULL,
  word_count INTEGER,
  duration_seconds FLOAT,
  model_used TEXT DEFAULT 'whisper-1',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS transcript_segments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  transcript_id UUID NOT NULL REFERENCES transcripts(id) ON DELETE CASCADE,
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  segment_index INTEGER NOT NULL,
  start_time FLOAT NOT NULL,
  end_time FLOAT NOT NULL,
  text TEXT NOT NULL,
  confidence FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- VIDEO ANALYSES
CREATE TABLE IF NOT EXISTS video_analyses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  summary TEXT,
  executive_summary TEXT,
  difficulty_level TEXT CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced', 'expert')),
  sentiment TEXT CHECK (sentiment IN ('positive', 'negative', 'neutral', 'mixed')),
  sentiment_score FLOAT,
  content_type TEXT,
  target_audience TEXT,
  estimated_reading_time INTEGER,
  model_used TEXT DEFAULT 'gpt-4o',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS video_topics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  topic TEXT NOT NULL,
  relevance_score FLOAT,
  mention_count INTEGER DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS video_chapters (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  chapter_index INTEGER NOT NULL,
  title TEXT NOT NULL,
  summary TEXT,
  start_time FLOAT NOT NULL,
  end_time FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS video_key_moments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  timestamp_seconds FLOAT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  moment_type TEXT CHECK (moment_type IN ('key_point', 'definition', 'example', 'conclusion', 'question', 'insight')),
  importance_score FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS video_entities (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  entity_text TEXT NOT NULL,
  entity_type TEXT CHECK (entity_type IN ('person', 'organization', 'location', 'technology', 'concept', 'product', 'other')),
  mention_count INTEGER DEFAULT 1,
  first_mention_time FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- EMBEDDINGS
CREATE TABLE IF NOT EXISTS video_embeddings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  chunk_text TEXT NOT NULL,
  chunk_index INTEGER NOT NULL,
  start_time FLOAT,
  end_time FLOAT,
  embedding vector(1536),
  model_used TEXT DEFAULT 'text-embedding-3-small',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- THUMBNAILS
CREATE TABLE IF NOT EXISTS thumbnails (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  style TEXT NOT NULL CHECK (style IN ('youtube_creator', 'cinematic', 'educational', 'minimal', 'high_contrast', 'editorial')),
  prompt_used TEXT,
  storage_path TEXT NOT NULL,
  public_url TEXT,
  width INTEGER DEFAULT 1792,
  height INTEGER DEFAULT 1024,
  is_favorite BOOLEAN DEFAULT FALSE,
  model_used TEXT DEFAULT 'dall-e-3',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- CONVERSATIONS
CREATE TABLE IF NOT EXISTS conversations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  title TEXT,
  message_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  citations JSONB,
  tokens_used INTEGER,
  model_used TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- QUIZZES
CREATE TABLE IF NOT EXISTS quizzes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  total_questions INTEGER NOT NULL,
  difficulty TEXT CHECK (difficulty IN ('easy', 'medium', 'hard', 'mixed')),
  model_used TEXT DEFAULT 'gpt-4o',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS quiz_questions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  quiz_id UUID NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  question_index INTEGER NOT NULL,
  question_type TEXT NOT NULL CHECK (question_type IN ('mcq', 'true_false', 'short_answer')),
  question_text TEXT NOT NULL,
  options JSONB,
  correct_answer TEXT NOT NULL,
  explanation TEXT,
  difficulty TEXT CHECK (difficulty IN ('easy', 'medium', 'hard')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS quiz_attempts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  quiz_id UUID NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  answers JSONB NOT NULL,
  score INTEGER NOT NULL,
  total_questions INTEGER NOT NULL,
  percentage FLOAT NOT NULL,
  time_taken_seconds INTEGER,
  completed_at TIMESTAMPTZ DEFAULT NOW()
);

-- LEARNING REPLORTS
CREATE TABLE IF NOT EXISTS learning_reports (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  learning_outcomes JSONB,
  key_concepts JSONB,
  key_facts JSONB,
  action_items JSONB,
  misconceptions JSONB,
  next_topics JSONB,
  prerequisites JSONB,
  model_used TEXT DEFAULT 'gpt-4o',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_videos_user_id ON videos(user_id);
CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);
CREATE INDEX IF NOT EXISTS idx_videos_created_at ON videos(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_processing_jobs_status ON processing_jobs(status);
CREATE INDEX IF NOT EXISTS idx_transcript_segments_video_id ON transcript_segments(video_id);
CREATE INDEX IF NOT EXISTS idx_video_embeddings_video_id ON video_embeddings(video_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_thumbnails_video_id ON thumbnails(video_id);
CREATE INDEX IF NOT EXISTS idx_quiz_questions_quiz_id ON quiz_questions(quiz_id);
CREATE INDEX IF NOT EXISTS idx_video_embeddings_vector ON video_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_transcripts_fulltext ON transcripts USING gin(to_tsvector('english', full_text));

-- ROW LEVEL SECURITY
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE processing_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE transcripts ENABLE ROW LEVEL SECURITY;
ALTER TABLE transcript_segments ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_chapters ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_key_moments ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE thumbnails ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE quizzes ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_reports ENABLE ROW LEVEL SECURITY;

-- RLS POLICIES
CREATE POLICY "profiles_own" ON profiles FOR ALL USING (auth.uid() = id);
CREATE POLICY "videos_own" ON videos FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "videos_public_read" ON videos FOR SELECT USING (is_public = TRUE);
CREATE POLICY "processing_jobs_own" ON processing_jobs FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "transcripts_own" ON transcripts FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "transcript_segments_own" ON transcript_segments FOR ALL UPING (video_id IN (SELECT id FROM videos WHERE user_id = auth.uid()));
CREATE POLICY "video_analyses_own" ON video_analyses FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "video_topics_own" ON video_topics FOR ALL USING (video_id IN (SELECT id FROM videos WHERE user_id = auth.uid()));
CREATE POLICY "video_chapters_own" ON video_chapters FOR ALL USING (video_id IN (SELECT id FROM videos WHERE user_id = auth.uid()));
CREATE POLICY "video_key_moments_own" ON video_key_moments FOR ALL UPING (video_id IN (SELECT id FROM videos WHERE user_id = auth.uid()));
CREATE POLICY "video_entities_own" ON video_entities FOR ALL USING (video_id IN (SELECT id FROM videos WHERE user_id = auth.uid()));
CREATE POLICY "video_embeddings_own" ON video_embeddings FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "thumbnails_own" ON thumbnails FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "conversations_own" ON conversations FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "messages_own" ON messages FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "quizzes_own" ON quizzes FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "quiz_questions_own" ON quiz_questions FOR ALL USING (video_id IN (SELECT id FROM videos WHERE user_id = auth.uid()));
CREATE POLICY "quiz_attempts_own" ON quiz_attempts FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "learning_reports_own" ON learning_reports FOR ALL USING (auth.uid() = user_id);

-- FUNCTIONS
CREATE OR REPLACE FUNCTION update_updated_at() RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = NOW(); RETURN NEW; END>Â$$ LANGUAGE plpgsql;
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_videos_updated_at BEFORE UPDATE ON videos FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_processing_jobs_updated_at BEEORE UPDATE ON processing_jobs FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE OR REPLACE FUNCTION handle_new_user() RETURNS TRIGGER AS $$ BEGIN INSERT INTO profiles (id, email, full_name, avatar_url) VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'avatar_url'); RETURN NEW; END;$$ LANGUAGE plpgsql SECURITY DEFINER;
CREATE TRIGGER on_auth_user_created AFTER INSERT ON auth.users FOR EACH ROW EXECUTE FUNCTION handle_new_user();

CREATE OR REPLACE FUNCTION match_video_embeddings(query_embedding vector(1536), match_video_id UUID, match_count INT DEFAULT 10, match_threshold FLOAT DEFAULT 0.7) RETURNS TABLE (id UUID, chunk_text TEXT, start_time FLOAT, end_time FLOAT, similarity FLOAT) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY SELECT ve.id, ve.chunk_text, ve.start_time, ve.end_time, 1 - (ve.embedding <=> query_embedding) AS similarity FROM video_embeddings ve WHERE ve.video_id = match_video_id AND 1 - (ve.embedding <=> query_embedding) > match_threshold ORDER BY ve.embedding <=> query_embedding LIMIT match_count; END>Â$$$