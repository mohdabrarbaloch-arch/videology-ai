from fastapi import APIRouter
from app.config import get_settings

router = APIRouter()


@router.get("/")
async def health_check():
    settings = get_settings()
    return {
        "status": "healthy",
        "service": "videology-backend",
        "openai_configured": bool(settings.openai_api_key),
        "supabase_configured": bool(settings.supabase_url),
    }
