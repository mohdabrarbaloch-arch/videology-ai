"""Translation router — GPT-4o multilingual translation."""

import logging
from fastapi import APIRouter, HTTPException
from app.models import TranslationRequest, TranslationResponse

router = APIRouter(prefix="/translation", tags=["translation"])
logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {
    "en": "English",
    "ur": "Urdu",
    "hi": "Hindi",
    "ar": "Arabic",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "pt": "Portuguese",
    "zh": "Chinese",
    "ja": "Japanese",
}

TRANSLATION_SYSTEM_PROMPT = """You are an expert translator. Translate the provided transcript segments to the target language.

Rules:
1. Preserve all timestamps exactly as they are
2. Maintain the meaning and tone of the original content
3. Adapt idioms and cultural references appropriately
4. Keep technical terms in their commonly used form in the target language
5. Return JSON array of segments with: start, end, text (translated)
6. Do not add or remove segments — translate each one"""


@router.post("/translate")
async def translate_transcript(request: TranslationRequest):
    """Translate a transcript to the target language using GPT-4o."""
    if request.target_language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language: {request.target_language}. Supported: {list(SUPPORTED_LANGUAGES.keys())}"
        )

    return {
        "transcript_id": request.transcript_id,
        "target_language": request.target_language,
        "language_name": SUPPORTED_LANGUAGES[request.target_language],
        "message": "Translation will be performed by the analyzer service using GPT-4o.",
    }


@router.get("/languages")
async def get_supported_languages():
    """Get supported translation languages."""
    return {
        "languages": [
            {"code": code, "name": name}
            for code, name in SUPPORTED_LANGUAGES.items()
        ]
    }
