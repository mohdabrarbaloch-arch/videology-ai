from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from app.config import get_settings

router = APIRouter()

def verify_api_key(x_api_key: str = Header(...)):
    settings = get_settings()
    if x_api_key != settings.backend_api_key:
        raise HTTPException(status_code=401, detail='Invalid API key')
    return x_api_key

class TriggerJobRequest(BaseModel):
    job_id: str
    video_id: str

@router.post('/trigger')
async def trigger_job(request: TriggerJobRequest, api_key: str = Depends(verify_api_key)):
    return {'message': f'Job {request.job_id} queued for processing', 'job_id': request.job_id}

@router.get('/status')
async def worker_status(api_key: str = Depends(verify_api_key)):
    return {'worker': 'running', 'queue': 'polling'}
