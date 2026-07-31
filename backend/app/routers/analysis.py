"""Analysis router — GPT-4o video content analysis."""

import json
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from app.models import AnalysisResponse, VideoAnalysisResult

router = APIRouter(prefix="/analysis", tags=["analysis"])
logger = logging.getLogger(__name__)

ANALYSIS_SYSTEM_PROMPT = """You are an expert video content analyst. Analyze the provided transcript and return a JSON object with the following structure:
{
  "summary": "A comprehensive 2-3 paragraph summary of the video content",
  "executive_summary": "A concise 1-2 sentence executive summary",
  "key_points": ["3-7 key points from the video"],
  "topics": [{"topic": "topic name", "relevance_score": 0.0-1.0, "mention_count": integer}],
  "chapters": [{"chapter_index": 0, "title": "chapter title", "summary": "1 sentence summary", "start_time": 0.0, "end_time": 0.0}],
  "key_moments": [{"timestamp_seconds": 0.0, "title": "moment title", "description": "what happens", "moment_type": "insight|demo|warning|tip|question", "importance_score": 0.0-1.0}],
  "entities": [{"entity_text": "name", "entity_type": "person|organization|technology|concept|location|product", "mention_count": integer}],
  "difficulty_level": "beginner|intermediate|advanced|expert",
  "sentiment": "positive|neutral|negative|mixed|informative|inspiring|critical",
  "content_type": "tutorial|lecture|interview|review|discussion|presentation|documentary|other",
  "target_audience": "description of who this video is for"
}

Rules:
- Timestamps must be in seconds (float)
- Chapters should cover the entire video chronologically
- Key moments should highlight the most important parts
- Be precise and factual — only include information present in the transcript
- Return ONLY valid JSON, no markdown or extra text"""


@router.post("/analyze")
async def analyze_transcript(
    video_id: str,
    transcript_text: str,
    language: str = "en",
):
    """Analyze a transcript using GPT-4o.

    This endpoint is called by the job worker after transcription is complete.
    The actual OpenAI API call is made in the analyzer service.
    """
    if not transcript_text or len(transcript_text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Transcript text too short for analysis")

    # The actual analysis is performed by the analyzer service
    # This endpoint serves as the API contract for the pipeline
    return {
        "video_id": video_id,
        "message": "Analysis will be performed by the analyzer service using GPT-4o.",
        "transcript_length": len(transcript_text),
        "language": language,
    }


@router.post("/analyze-frames")
async def analyze_frames(
    video_id: str,
    frame_urls: list[str],
):
    """Analyze video frames using GPT-4o Vision.

    Extracts visual information from key frames: slides, diagrams, code, charts.
    """
    if not frame_urls:
        raise HTTPException(status_code=400, detail="No frame URLs provided")

    return {
        "video_id": video_id,
        "frame_count": len(frame_urls),
        "message": "Frame analysis will be performed by the analyzer service using GPT-4o Vision.",
    }


@router.get("/schema")
async def get_analysis_schema():
    """Get the expected JSON schema for analysis results."""
    return {
        "schema": {
            "summary": "string",
            "executive_summary": "string",
            "key_points": "string[]",
            "topics": [{"topic": "string", "relevance_score": "float", "mention_count": "int"}],
            "chapters": [{"chapter_index": "int", "title": "string", "summary": "string", "start_time": "float", "end_time": "float"}],
            "key_moments": [{"timestamp_seconds": "float", "title": "string", "description": "string", "moment_type": "string", "importance_score": "float"}],
            "entities": [{"entity_text": "string", "entity_type": "string", "mention_count": "int"}],
            "difficulty_level": "beginner|intermediate|advanced|expert",
            "sentiment": "positive|neutral|negative|mixed|informative|inspiring|critical",
            "content_type": "tutorial|lecture|interview|review|discussion|presentation|documentary|other",
            "target_audience": "string",
        }
    }
