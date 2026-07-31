"""Pydantic models for Videology AI backend."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


# === Enums ===

class VideoSource(str, Enum):
    YOUTUBE = "youtube"
    DIRECT_URL = "direct_url"
    UPLOAD = "upload"


class JobStatus(str, Enum):
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    EXTRACTING_AUDIO = "extracting_audio"
    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"
    GENERATING_THUMBNAILS = "generating_thumbnails"
    INDEXING = "indexing"
    COMPLETED = "completed"
    FAILED = "failed"


class ThumbnailStyle(str, Enum):
    YOUTUBE_CREATOR = "youtube_creator"
    CINEMATIC = "cinematic"
    EDUCATIONAL = "educational"
    MINIMAL = "minimal"
    HIGH_CONTRAST = "high_contrast"
    EDITORIAL = "editorial"


class QuestionType(str, Enum):
    MCQ = "mcq"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# === Request Models ===

class VideoCreateRequest(BaseModel):
    url: Optional[str] = None
    source_type: VideoSource = VideoSource.YOUTUBE
    title: Optional[str] = None


class VideoUploadRequest(BaseModel):
    filename: str
    content_type: str
    size: int


class AskRequest(BaseModel):
    video_id: str
    question: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None


class QuizGenerateRequest(BaseModel):
    video_id: str
    num_questions: int = Field(default=10, ge=3, le=20)
    difficulty: Difficulty = Difficulty.MEDIUM
    question_types: list[QuestionType] = [QuestionType.MCQ, QuestionType.TRUE_FALSE, QuestionType.SHORT_ANSWER]


class TranslationRequest(BaseModel):
    transcript_id: str
    target_language: str = Field(..., description="ISO 639-1 language code")


class LearningReportRequest(BaseModel):
    video_id: str


class ThumbnailRegenerateRequest(BaseModel):
    video_id: str
    styles: list[ThumbnailStyle] = [
        ThumbnailStyle.YOUTUBE_CREATOR,
        ThumbnailStyle.CINEMATIC,
        ThumbnailStyle.EDUCATIONAL,
        ThumbnailStyle.MINIMAL,
        ThumbnailStyle.HIGH_CONTRAST,
        ThumbnailStyle.EDITORIAL,
    ]


# === Response Models ===

class VideoResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    duration_seconds: Optional[int] = None
    thumbnail_url: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime


class JobResponse(BaseModel):
    id: str
    video_id: str
    status: JobStatus
    progress: int = 0
    current_stage: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0


class TranscriptSegmentModel(BaseModel):
    start_time: float
    end_time: float
    text: str


class TranscriptResponse(BaseModel):
    id: str
    video_id: str
    language: str
    word_count: int
    full_text: str
    segments: list[TranscriptSegmentModel] = []


class Citation(BaseModel):
    timestamp: float
    text: str
    segment_id: Optional[str] = None


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation] = []
    conversation_id: str


class QuizQuestionModel(BaseModel):
    question_index: int
    question_type: QuestionType
    question_text: str
    options: Optional[list[str]] = None
    correct_answer: str
    explanation: Optional[str] = None
    difficulty: Difficulty = Difficulty.MEDIUM


class QuizResponse(BaseModel):
    id: str
    video_id: str
    title: str
    total_questions: int
    difficulty: Difficulty
    questions: list[QuizQuestionModel] = []


class QuizAttemptResponse(BaseModel):
    attempt_id: str
    score: int
    total: int
    percentage: float
    time_taken_seconds: int


class ThumbnailResponse(BaseModel):
    id: str
    video_id: str
    style: ThumbnailStyle
    public_url: Optional[str] = None
    is_favorite: bool = False
    width: int = 1792
    height: int = 1024


class LearningReportResponse(BaseModel):
    id: str
    video_id: str
    learning_outcomes: list[str] = []
    key_concepts: list[dict[str, Any]] = []
    key_facts: list[str] = []
    action_items: list[str] = []
    misconceptions: list[dict[str, str]] = []
    next_topics: list[str] = []
    prerequisites: list[str] = []


class TranslationResponse(BaseModel):
    id: str
    transcript_id: str
    target_language: str
    translated_text: str
    segment_count: int


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str
    openai_configured: bool
    supabase_configured: bool
    ffmpeg_available: bool


# === Pipeline Models ===

class PipelineStageUpdate(BaseModel):
    job_id: str
    status: JobStatus
    progress: int
    current_stage: str
    error_message: Optional[str] = None


class VideoAnalysisResult(BaseModel):
    summary: str
    executive_summary: str
    key_points: list[str]
    topics: list[dict[str, Any]]
    chapters: list[dict[str, Any]]
    key_moments: list[dict[str, Any]]
    entities: list[dict[str, Any]]
    difficulty_level: str
    sentiment: str
    content_type: str
    target_audience: str


class LearningReportResult(BaseModel):
    learning_outcomes: list[str]
    key_concepts: list[dict[str, Any]]
    key_facts: list[str]
    action_items: list[str]
    misconceptions: list[dict[str, str]]
    next_topics: list[str]
    prerequisites: list[str]


class QuizGenerationResult(BaseModel):
    title: str
    questions: list[QuizQuestionModel]
