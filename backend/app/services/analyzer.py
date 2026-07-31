"""
AI Analysis service using GPT-4o
Generates: summary, topics, chapters, key moments, entities, difficulty, sentiment,
quiz questions, learning report, and embeddings
"""

import json
import asyncio
from typing import List, Optional
import structlog
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings

logger = structlog.get_logger()

ANALYSIS_SYSTEM_PROMPT = """You are an expert video content analyst. Analyze the provided transcript and return a comprehensive JSON analysis.

Your analysis must be accurate, based ONLY on the transcript content. Never fabricate information.

Return valid JSON matching the exact schema provided."""

ANALYSIS_USER_PROMPT = """Analyze this video transcript and return a JSON object with this exact structure:

{{
  "summary": "2-3 paragraph comprehensive summary",
  "executive_summary": "1-2 sentence executive summary",
  "difficulty_level": "beginner|intermediate|advanced|expert",
  "sentiment": "positive|negative|neutral|mixed",
  "sentiment_score": 0.0-1.0,
  "content_type": "lecture|tutorial|interview|documentary|presentation|discussion|other",
  "target_audience": "description of ideal audience",
  "estimated_reading_time": minutes_as_integer,
  "topics": [
    {{"topic": "topic name", "relevance_score": 0.0-1.0, "mention_count": integer}}
  ],
  "chapters": [
    {{"chapter_index": 0, "title": "chapter title", "summary": "brief summary", "start_time": seconds_float, "end_time": seconds_float}}
  ],
  "key_moments": [
    {{"timestamp_seconds": float, "title": "moment title", "description": "what happens", "moment_type": "key_point|definition|example|conclusion|question|insight", "importance_score": 0.0-1.0}}
  ],
  "entities": [
    {{"entity_text": "name", "entity_type": "person|organization|location|technology|concept|product|other", "mention_count": integer, "first_mention_time": seconds_float}}
  ]
}}

VIDEO TITLE: {title}
DURATION: {duration} seconds

TRANSCRIPT:
{transcript}"""


QUIZ_SYSTEM_PROMPT = """You are an expert educator creating quiz questions from video content.
Create questions that test genuine understanding, not just memorization.
Return valid JSON only."""

QUIZ_USER_PROMPT = """Create {num_questions} quiz questions from this video transcript.
Mix question types: MCQ (multiple choice), true_false, and short_answer.
Include easy, medium, and hard difficulty questions.

Return JSON array:
[
  {{
    "question_index": 0,
    "question_type": "mcq|true_false|short_answer",
    "question_text": "the question",
    "options": ["A", "B", "C", "D"],  // only for mcq
    "correct_answer": "the correct answer",
    "explanation": "why this is correct",
    "difficulty": "easy|medium|hard",
    "timestamp_reference": seconds_float_or_null
  }}
]

VIDEO TITLE: {title}
TRANSCRIPT:
{transcript}"""


LEARNING_REPORT_PROMPT = """Create a comprehensive learning report from this video transcript.

Return JSON:
{{
  "learning_outcomes": ["outcome 1", "outcome 2", ...],
  "key_concepts": [
    {{"concept": "name", "definition": "clear definition", "timestamp": seconds_or_null}}
  ],
  "key_facts": ["fact 1", "fact 2", ...],
  "action_items": ["actionable step 1", "actionable step 2", ...],
  "misconceptions": [
    {{"misconception": "common wrong belief", "correction": "what's actually true"}}
  ],
  "next_topics": ["topic to explore next 1", "topic 2", ...],
  "prerequisites": ["prerequisite knowledge 1", "prerequisite 2", ...]
}}

VIDEO TITLE: {title}
TRANSCRIPT:
{transcript}"""


TRANSLATION_PROMPT = """Translate the following video transcript to {target_language}.
Preserve the meaning, tone, and technical terms accurately.
Return ONLY the translated text, no explanations.

TRANSCRIPT:
{transcript}"""


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=60))
async def analyze_transcript(
    transcript: str,
    title: str,
    duration: Optional[float],
    video_id: str,
) -> dict:
    """Run GPT-4o analysis on the full transcript"""
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    # Truncate transcript if too long (GPT-4o context limit)
    max_chars = 100000
    if len(transcript) > max_chars:
        transcript = transcript[:max_chars] + "\n[transcript truncated for length]"

    prompt = ANALYSIS_USER_PROMPT.format(
        title=title,
        duration=duration or "unknown",
        transcript=transcript,
    )

    response = await client.chat.completions.create(
        model=settings.ai_model,
        messages=[
            {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
        max_tokens=4096,
    )

    result = json.loads(response.choices[0].message.content)
    logger.info("Analysis complete", video_id=video_id, topics=len(result.get("topics", [])))
    return result


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=60))
async def generate_quiz(
    transcript: str,
    title: str,
    video_id: str,
    num_questions: int = 10,
) -> List[dict]:
    """Generate quiz questions using GPT-4o"""
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    max_chars = 80000
    if len(transcript) > max_chars:
        transcript = transcript[:max_chars] + "\n[truncated]"

    prompt = QUIZ_USER_PROMPT.format(
        num_questions=num_questions,
        title=title,
        transcript=transcript,
    )

    response = await client.chat.completions.create(
        model=settings.ai_model,
        messages=[
            {"role": "system", "content": QUIZ_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.4,
        max_tokens=4096,
    )

    content = json.loads(response.choices[0].message.content)
    questions = content if isinstance(content, list) else content.get("questions", [])
    logger.info("Quiz generated", video_id=video_id, questions=len(questions))
    return questions


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=60))
async def generate_learning_report(
    transcript: str,
    title: str,
    video_id: str,
) -> dict:
    """Generate learning report using GPT-4o"""
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    max_chars = 80000
    if len(transcript) > max_chars:
        transcript = transcript[:max_chars] + "\n[truncated]"

    prompt = LEARNING_REPORT_PROMPT.format(title=title, transcript=transcript)

    response = await client.chat.completions.create(
        model=settings.ai_model,
        messages=[
            {"role": "system", "content": "You are an expert educator. Return valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
        max_tokens=3000,
    )

    result = json.loads(response.choices[0].message.content)
    logger.info("Learning report generated", video_id=video_id)
    return result


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=60))
async def generate_embeddings(
    chunks: List[dict],
    video_id: str,
) -> List[dict]:
    """Generate embeddings for transcript chunks using text-embedding-3-small"""
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    texts = [c["text"] for c in chunks]

    # Batch embeddings (max 2048 inputs per request)
    all_embeddings = []
    batch_size = 100

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = await client.embeddings.create(
            model=settings.embedding_model,
            input=batch,
        )
        for j, emb in enumerate(response.data):
            chunk = chunks[i + j]
            all_embeddings.append({
                "chunk_index": i + j,
                "chunk_text": chunk["text"],
                "start_time": chunk.get("start_time"),
                "end_time": chunk.get("end_time"),
                "embedding": emb.embedding,
                "model_used": settings.embedding_model,
            })

    logger.info("Embeddings generated", video_id=video_id, count=len(all_embeddings))
    return all_embeddings


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=60))
async def translate_transcript(
    transcript: str,
    target_language: str,
    video_id: str,
) -> str:
    """Translate transcript to target language using GPT-4o"""
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    max_chars = 80000
    if len(transcript) > max_chars:
        transcript = transcript[:max_chars]

    prompt = TRANSLATION_PROMPT.format(
        target_language=target_language,
        transcript=transcript,
    )

    response = await client.chat.completions.create(
        model=settings.ai_model,
        messages=[
            {"role": "system", "content": "You are a professional translator. Translate accurately."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=4096,
    )

    return response.choices[0].message.content


def chunk_transcript_for_rag(
    segments: List[dict],
    chunk_size: int = 500,
    overlap: int = 50,
) -> List[dict]:
    """Chunk transcript segments into overlapping windows for RAG embeddings"""
    chunks = []
    current_chunk_words = []
    current_start = None
    current_end = None
    chunk_index = 0

    for seg in segments:
        words = seg["text"].split()
        if current_start is None:
            current_start = seg["start"]

        current_chunk_words.extend(words)
        current_end = seg["end"]

        if len(current_chunk_words) >= chunk_size:
            chunks.append({
                "chunk_index": chunk_index,
                "text": " ".join(current_chunk_words),
                "start_time": current_start,
                "end_time": current_end,
            })
            # Overlap: keep last `overlap` words
            current_chunk_words = current_chunk_words[-overlap:]
            current_start = current_end
            chunk_index += 1

    # Last chunk
    if current_chunk_words:
        chunks.append({
            "chunk_index": chunk_index,
            "text": " ".join(current_chunk_words),
            "start_time": current_start,
            "end_time": current_end,
        })

    return chunks
