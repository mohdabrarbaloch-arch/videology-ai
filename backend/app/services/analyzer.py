import json
import openai
from typing import List, Dict, Any, Optional
from app.config import get_settings


class AIAnalysisService:
    def __init__(self):
        self.settings = get_settings()
        self.client = openai.AsyncOpenAI(openai_api_key=self.settings.openai_api_key)

    async def analyze_transcript(self, transcript: str, title: str) -> Dict[any, any]:
        """Analyze transcript with GPT-4o"""
        truncated = transcript[:100000]
        prompt = f"""Analyze this video transcript and return a JSON object with:

Video Title: {title}

Transcript:
{truncated}

JSON structure:
{{
  "summary": "3-5 sentence summary",
  "executive_summary": "1-2 sentence tldr",
  "difficulty_level": "beginner|intermediate|advanced|expert",
  "sentiment": "positive|negative|neutral|mixed",
  "content_type": "tutorial|lecture|interview|debate|news|other",
  "target_audience": "string",
  "topics": [{"topic": "string", "relevance_score": 0.0-1.0}],
  "chapters": [{"title": "string", "summary": "string", "start_time": 0}],
  "key_moments": [{"timestamp": 0, "title": "string", "description": "string", "type": "key_point|definition|example|conclusion"}],
  "entities": [{"text": "string", "type": "person|org|loc|tech|concept", "count": 1}]
}}"""
        response = await self.client.chat.completions.create(
            model=self.settings.ai_model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        return json.loads(response.choices[0].message.content)

    async def generate_quiz(self, transcript: str, title: str) -> Dict:
        """Generate quiz questions from transcript"""
        truncated = transcript[:30000]
        prompt = f"""Generate a comprehensive quiz for this video. Return JSON:

Video: {title}
Transcript: {truncated}

JSON structure:
{{
  "title": "Quiz: {title}",
  "questions": [
    {
      "type": "mcq|true_false|short_answer",
      "question": "string",
      "options": ["a", "b", "c", "d"],
      "correct_answer": "string",
      "explanation": "string",
      "difficulty": "easy|medium|hard"
    }
  ]
}}"""
        response = await self.client.chat.completions.create(
            model=self.settings.ai_model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.5,
        )
        return json.loads(response.choices[0].message.content)

    async def generate_learning_report(self, transcript: str, title: str) -> Dict:
        """Generate learning report from transcript"""
        truncated = transcript[:30000]
        prompt = f"""Generate a learning report for this video. Return JSON:

Video: {title}
Transcript: {truncated}

JSON structure:
{{
  "learning_outcomes": ["string"],
  "key_concepts": [{"concept": "string", "definition": "string"}],
  "key_facts": ["string"],
  "action_items": ["string"],
  "misconceptions": [{"misconception": "string", "correction": "string"}],
  "next_topics": ["string"],
  "prerequisites": ["string"]
}}"""
        response = await self.client.chat.completions.create(
            model=self.settings.ai_model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        return json.loads(response.choices[0].message.content)

    async def create_embeddings(self, text_chunks: List[str]) -> List[List[float]]:
        """Create embeddings for transcript chunks"""
        embeddings = []
        batch_size = 100
        for i in range(0, len(text_chunks), batch_size):
            batch = text_chunks[i:i + batch_size]
            response = await self.client.embeddings.create(
                model=self.settings.embedding_model,
                input=batch,
            )
            embeddings.extend([e.embedding for e in response.data])
        return embeddings

    async def translate_transcript(self, text: str, target_lang: str) -> str:
        """Translate transcript to target language"""
        response = await self.client.chat.completions.create(
            model=self.settings.ai_model,
            messages=[{"role": "user", "content": f"Translate this text to {target_lang}. Preserve the meaning and tone. Return only the translated text:\n\n{text[:30000]}"}],
            temperature=0.3,
        )
        return response.choices[0].message.content or ''
