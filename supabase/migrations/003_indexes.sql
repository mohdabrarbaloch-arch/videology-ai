-- Videology AI — Performance Indexes
-- Migration 003: Add indexes for query performance
-- Run after 001_initial_schema.sql and 002_rls.sql

-- Videos: common query patterns
CREATE INDEX IF NOT EXISTS idx_videos_user_id_created ON videos(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);
CREATE INDEX IF NOT EXISTS idx_videos_user_status ON videos(user_id, status);

-- Processing jobs: queue polling and status checks
CREATE INDEX IF NOT EXISTS idx_jobs_status ON processing_jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_status_created ON processing_jobs(status, created_at);
CREATE INDEX IF NOT EXISTS idx_jobs_video_id ON processing_jobs(video_id);

-- Transcripts: lookup by video
CREATE INDEX IF NOT EXISTS idx_transcripts_video_id ON transcripts(video_id);

-- Transcript segments: ordered retrieval
CREATE INDEX IF NOT EXISTS idx_segments_transcript_start ON transcript_segments(transcript_id, start_time);

-- Video embeddings: pgvector similarity search
CREATE INDEX IF NOT EXISTS idx_embeddings_vector
  ON video_embeddings
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_embeddings_video_id ON video_embeddings(video_id);

-- Thumbnails: lookup by video
CREATE INDEX IF NOT EXISTS idx_thumbnails_video_id ON thumbnails(video_id);
CREATE INDEX IF NOT EXISTS idx_thumbnails_favorite ON thumbnails(video_id, is_favorite) WHERE is_favorite = true;

-- Conversations: lookup by user and video
CREATE INDEX IF NOT EXISTS idx_conversations_user_video ON conversations(user_id, video_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user_created ON conversations(user_id, created_at DESC);

-- Messages: ordered retrieval within conversation
CREATE INDEX IF NOT EXISTS idx_messages_conversation_created ON messages(conversation_id, created_at);

-- Quizzes: lookup by video
CREATE INDEX IF NOT EXISTS idx_quizzes_video_id ON quizzes(video_id);

-- Quiz questions: ordered retrieval
CREATE INDEX IF NOT EXISTS idx_quiz_questions_quiz_index ON quiz_questions(quiz_id, question_index);

-- Quiz attempts: user history
CREATE INDEX IF NOT EXISTS idx_quiz_attempts_user ON quiz_attempts(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_quiz_attempts_quiz ON quiz_attempts(quiz_id, user_id);

-- Learning reports: lookup by video
CREATE INDEX IF NOT EXISTS idx_learning_reports_video_id ON learning_reports(video_id);

-- Translations: lookup by transcript and language
CREATE INDEX IF NOT EXISTS idx_translations_transcript_lang ON translations(transcript_id, target_language);

-- Video analyses: lookup by video
CREATE INDEX IF NOT EXISTS idx_video_analyses_video_id ON video_analyses(video_id);

-- Video topics, chapters, key moments: lookup by video
CREATE INDEX IF NOT EXISTS idx_video_topics_video_id ON video_topics(video_id);
CREATE INDEX IF NOT EXISTS idx_video_chapters_video_id ON video_chapters(video_id);
CREATE INDEX IF NOT EXISTS idx_video_key_moments_video_id ON video_key_moments(video_id);

-- Full text search on video titles
CREATE INDEX IF NOT EXISTS idx_videos_title_search ON videos USING gin(to_tsvector('english', title));