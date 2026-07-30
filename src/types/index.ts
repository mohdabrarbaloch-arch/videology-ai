// ============================================================
// VIDEOLOGY -- Core Types
// ============================================================

export type VideoStatus = 'pending' | 'processing' | 'completed' | 'failed'
export type JobStatus = 'queued' | 'downloading' | 'extracting_audio' | 'transcribing' | 'analyzing' | 'generating_thumbnails' | 'indexing' | 'completed' | 'failed'
export type SourceType = 'youtube' | 'url' | 'upload'
export type QuestionType = 'mcq' | 'true_false' | 'short_answer'
export type ThumbnailStyle = 'youtube_creator' | 'cinematic' | 'educational' | 'minimal' | 'high_contrast' | 'editorial'

export interface Profile {
  id: string
  email: string
  full_name?: string
  avatar_url?: string
  plan: 'free' | 'pro'
  videos_processed: number
  created_at: string
}

export interface Video {
  id: string
  user_id: string
  title: string
  description?: string
  source_type: SourceType
  source_url?: string
  youtube_id?: string
  storage_path?: string
  thumbnail_url?: string
  duration_seconds?: number
  file_size_bytes?: number
  language?: string
  status: VideoStatus
  is_public: boolean
  view_count: number
  created_at: string
  updated_at: string
  processing_jobs?: ProcessingJob[]
  video_analyses?: VideoAnalysis[]
  video_topics?: VideoTopic[]
  video_chapters?: VideoChapter[]
  video_key_moments?: VideoKeyMoment[]
  video_entities?: VideoEntity[]
  transcripts?: Transcript[]
  thumbnails?: Thumbnail[]
  quizzes?: Quiz[]
  learning_reports?: LearningReport[]
}

export interface ProcessingJob {
  id: string
  video_id: string
  user_id: string
  status: JobStatus
  progress: number
  current_stage?: string
  error_message?: string
  retry_count: number
  started_at?: string
  completed_at?: string
  created_at: string
  updated_at: string
}

export interface Transcript {
  id: string
  video_id: string
  language: string
  full_text: string
  word_count?: number
  duration_seconds?: number
  created_at: string
}

export interface TranscriptSegment {
  id: string
  transcript_id: string
  video_id: string
  segment_index: number
  start_time: number
  end_time: number
  text: string
  confidence?: number
}

export interface VideoAnalysis {
  id: string
  video_id: string
  summary?: string
  executive_summary?: string
  difficulty_level?: 'beginner' | 'intermediate' | 'advanced' | 'expert'
  sentiment?: 'positive' | 'negative' | 'neutral' | 'mixed'
  content_type?: string
  target_audience?: string
  estimated_reading_time?: number
  created_at: string
}

export interface VideoTopic {
  id: string
  video_id: string
  topic: string
  relevance_score?: number
  mention_count: number
}

export interface VideoChapter {
  id: string
  video_id: string
  chapter_index: number
  title: string
  summary?: string
  start_time: number
  end_time?: number
}

export interface VideoKeyMoment {
  id: string
  video_id: string
  timestamp_seconds: number
  title: string
  description?: string
  moment_type?: string
  importance_score?: number
}

export interface VideoEntity {
  id: string
  video_id: string
  entity_text: string
  entity_type: string
  mention_count: number
  first_mention_time?: number
}

export interface Thumbnail {
  id: string
  video_id: string
  style: ThumbnailStyle
  storage_path: string
  public_url?: string
  is_favorite: boolean
  model_used: string
  created_at: string
}

export interface Quiz {
  id: string
  video_id: string
  title: string
  total_questions: number
  difficulty?: string
  created_at: string
}

export interface QuizQuestion {
  id: string
  quiz_id: string
  video_id: string
  question_index: number
  question_type: QuestionType
  question_text: string
  options?: string[]
  correct_answer: string
  explanation?: string
  difficulty?: string
}

export interface LearningReport {
  id: string
  video_id: string
  learning_outcomes?: string[]
  key_concepts?: Array<{ concept: string; definition: string }>
  key_facts?: string[]
  action_items?: string[]
  misconceptions?: Array<{ misconception: string; correction: string }>
  next_topics?: string[]
  prerequisites?: string[]
  created_at: string
}

export interface Message {
  id: string
  conversation_id: string
  role: 'user' | 'assistant'
  content: string
  citations?: Array<{ timestamp: number; text: string; segment_id: string }>
  tokens_used?: number
  created_at: string
}

export interface AnalyzeRequest {
  source_type: SourceType
  url?: string
  title?: string
  storage_path?: string
}

export interface AnalyzeResponse {
  video_id: string
  job_id: string
  status: string
  message: string
}
