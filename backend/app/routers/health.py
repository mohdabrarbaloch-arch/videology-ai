from fastapi import APIRouter
from app.config import get_settings

router = APIRouter()

@router.get('/')
async def health_check():
    settings = get_settings()
    return {'status': 'healthy', 'service': 'videology-backend', 'model': settings.ai_model}

@router.get('/ready')
async def readiness_check():
    return {'status': 'ready'}
