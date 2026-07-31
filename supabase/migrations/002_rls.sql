-- Videology AI — Additional RLS Policies
-- Migration 002: Ensures all tables have proper RLS policies
-- Run after 001_initial_schema.sql

-- Ensure RLS is enabled on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE processing_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE transcripts ENABLE ROW LEVEL SECURITY;
ALTER TABLE transcript_segments ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_chapters ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_key_moments ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE thumbnails ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE quizzes ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE translations ENABLE ROW LEVEL SECURITY;

-- Helper function: check if user owns a video
CREATE OR REPLACE FUNCTION public.user_owns_video(video_uuid UUID)
RETURNS BOOLEAN
LANGUAGE sql
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.videos
    WHERE id = video_uuid AND user_id = auth.uid()
  );
$$;

-- profiles: users can only see/update their own profile
DROP POLICY IF EXISTS "profiles_select_own" ON profiles;
CREATE POLICY "profiles_select_own" ON profiles FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "profiles_update_own" ON profiles;
CREATE POLICY "profiles_update_own" ON profiles FOR UPDATE USING (auth.uid() = id);

DROP POLICY IF EXISTS "profiles_insert_own" ON profiles;
CREATE POLICY "profiles_insert_own" ON profiles FOR INSERT WITH CHECK (auth.uid() = id);

-- videos: users can only CRUD their own videos
DROP POLICY IF EXISTS "videos_select_own" ON videos;
CREATE POLICY "videos_select_own" ON videos FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "videos_insert_own" ON videos;
CREATE POLICY "videos_insert_own" ON videos FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "videos_update_own" ON videos;
CREATE POLICY "videos_update_own" ON videos FOR UPDATE USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "videos_delete_own" ON videos;
CREATE POLICY "videos_delete_own" ON videos FOR DELETE USING (auth.uid() = user_id);

-- video_sources: access through video ownership
DROP POLICY IF EXISTS "video_sources_select_own" ON video_sources;
CREATE POLICY "video_sources_select_own" ON video_sources FOR SELECT USING (user_owns_video(video_id));

DROP POLICY IF EXISTS "video_sources_insert_own" ON video_sources;
CREATE POLICY "video_sources_insert_own" ON video_sources FOR INSERT WITH CHECK (user_owns_video(video_id));

-- processing_jobs: access through video ownership
DROP POLICY IF EXISTS "jobs_select_own" ON processing_jobs;
CREATE POLICY "jobs_select_own" ON processing_jobs FOR SELECT USING (user_owns_video(video_id));

DROP POLICY IF EXISTS "jobs_insert_own" ON processing_jobs;
CREATE POLICY "jobs_insert_own" ON processing_jobs FOR INSERT WITH CHECK (user_owns_video(video_id));

DROP POLICY IF EXISTS "jobs_update_own" ON processing_jobs;
CREATE POLICY "jobs_update_own" ON processing_jobs FOR UPDATE USING (user_owns_video(video_id));

-- transcripts: access through video ownership
DROP POLICY IF EXISTS "transcripts_select_own" ON transcripts;
CREATE POLICY "transcripts_select_own" ON transcripts FOR SELECT USING (user_owns_video(video_id));

DROP POLICY IF EXISTS "transcripts_insert_own" ON transcripts;
CREATE POLICY "transcripts_insert_own" ON transcripts FOR INSERT WITH CHECK (user_owns_video(video_id));

-- transcript_segments: access through video ownership via transcript
DROP POLICY IF EXISTS "segments_select_own" ON transcript_segments;
CREATE POLICY "segments_select_own" ON transcript_segments FOR SELECT
  USING (EXISTS (
    SELECT 1 FROM public.transcripts t
    WHERE t.id = transcript_id AND user_owns_video(t.video_id)
  ));

-- video_analyses: access through video ownership
DROP POLICY IF EXISTS "analyses_select_own" ON video_analyses;
CREATE POLICY "analyses_select_own" ON video_analyses FOR SELECT USING (user_owns_video(video_id));

-- video_topics, video_chapters, video_key_moments: access through video ownership
DROP POLICY IF EXISTS "topics_select_own" ON video_topics;
CREATE POLICY "topics_select_own" ON video_topics FOR SELECT USING (user_owns_video(video_id));

DROP POLICY IF EXISTS "chapters_select_own" ON video_chapters;
CREATE POLICY "chapters_select_own" ON video_chapters FOR SELECT USING (user_owns_video(video_id));

DROP POLICY IF EXISTS "key_moments_select_own" ON video_key_moments;
CREATE POLICY "key_moments_select_own" ON video_key_moments FOR SELECT USING (user_owns_video(video_id));

-- video_embeddings: access through video ownership
DROP POLICY IF EXISTS "embeddings_select_own" ON video_embeddings;
CREATE POLICY "embeddings_select_own" ON video_embeddings FOR SELECT USING (user_owns_video(video_id));

-- thumbnails: access through video ownership
DROP POLICY IF EXISTS "thumbnails_select_own" ON thumbnails;
CREATE POLICY "thumbnails_select_own" ON thumbnails FOR SELECT USING (user_owns_video(video_id));

DROP POLICY IF EXISTS "thumbnails_update_own" ON thumbnails;
CREATE POLICY "thumbnails_update_own" ON thumbnails FOR UPDATE USING (user_owns_video(video_id));

-- conversations: users can only access their own conversations
DROP POLICY IF EXISTS "conversations_select_own" ON conversations;
CREATE POLICY "conversations_select_own" ON conversations FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "conversations_insert_own" ON conversations;
CREATE POLICY "conversations_insert_own" ON conversations FOR INSERT WITH CHECK (auth.uid() = user_id);

-- messages: access through conversation ownership
DROP POLICY IF EXISTS "messages_select_own" ON messages;
CREATE POLICY "messages_select_own" ON messages FOR SELECT
  USING (EXISTS (
    SELECT 1 FROM public.conversations c
    WHERE c.id = conversation_id AND auth.uid() = c.user_id
  ));

DROP POLICY IF EXISTS "messages_insert_own" ON messages;
CREATE POLICY "messages_insert_own" ON messages FOR INSERT
  WITH CHECK (EXISTS (
    SELECT 1 FROM public.conversations c
    WHERE c.id = conversation_id AND auth.uid() = c.user_id
  ));

-- quizzes: access through video ownership
DROP POLICY IF EXISTS "quizzes_select_own" ON quizzes;
CREATE POLICY "quizzes_select_own" ON quizzes FOR SELECT USING (user_owns_video(video_id));

-- quiz_questions: access through quiz ownership via quiz
DROP POLICY IF EXISTS "quiz_questions_select_own" ON quiz_questions;
CREATE POLICY "quiz_questions_select_own" ON quiz_questions FOR SELECT
  USING (EXISTS (
    SELECT 1 FROM public.quizzes q
    WHERE q.id = quiz_id AND user_owns_video(q.video_id)
  ));

-- quiz_attempts: users can only access their own attempts
DROP POLICY IF EXISTS "quiz_attempts_select_own" ON quiz_attempts;
CREATE POLICY "quiz_attempts_select_own" ON quiz_attempts FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "quiz_attempts_insert_own" ON quiz_attempts;
CREATE POLICY "quiz_attempts_insert_own" ON quiz_attempts FOR INSERT WITH CHECK (auth.uid() = user_id);

-- learning_reports: access through video ownership
DROP POLICY IF EXISTS "learning_reports_select_own" ON learning_reports;
CREATE POLICY "learning_reports_select_own" ON learning_reports FOR SELECT USING (user_owns_video(video_id));

-- translations: access through video ownership via transcript
DROP POLICY IF EXISTS "translations_select_own" ON translations;
CREATE POLICY "translations_select_own" ON translations FOR SELECT
  USING (EXISTS (
    SELECT 1 FROM public.transcripts t
    WHERE t.id = transcript_id AND user_owns_video(t.video_id)
  ));

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;