-- Videology AI — Optional Seed Data
-- Run after all migrations to populate demo data
-- WARNING: Only run in development/staging environments

-- Insert a demo profile (replace with actual auth user ID)
-- INSERT INTO profiles (id, full_name, avatar_url, preferences)
-- VALUES (
--   '00000000-0000-0000-0000-000000000001',
--   'Demo User',
--   NULL,
--   '{"theme": "dark", "default_language": "en", "thumbnail_styles": ["youtube_creator", "cinematic"]}'::jsonb
-- );

-- Insert a demo video
-- INSERT INTO videos (id, user_id, title, description, duration_seconds, status)
-- VALUES (
--   '00000000-0000-0000-0000-000000000010',
--   '00000000-0000-0000-0000-000000000001',
--   'Demo: Introduction to Machine Learning',
--   'A comprehensive introduction to ML concepts',
--   1820,
--   'completed'
-- );

-- Insert demo video source
-- INSERT INTO video_sources (video_id, source_type, url, youtube_id)
-- VALUES (
--   '00000000-0000-0000-0000-000000000010',
--   'youtube',
--   'https://www.youtube.com/watch?v=demo',
--   'demo1234567'
-- );

-- Insert demo processing job
-- INSERT INTO processing_jobs (id, video_id, status, progress, current_stage)
-- VALUES (
--   '00000000-0000-0000-0000-000000000020',
--   '00000000-0000-0000-0000-000000000010',
--   'completed',
--   100,
--   'Processing complete'
-- );

-- Note: Uncomment and modify the above statements for development seeding.
-- In production, use real user accounts and real video data.
SELECT 'Seed data file ready. Uncomment INSERT statements for development use.' as message;