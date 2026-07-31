from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from app.config import get_settings

router = APIRouter()


def verify_api_key(x_api_key: str = Header(...)):
    settings = get_settings()
    if x_api_key != settings.backend_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


class TriggerJobRequest(BaseModel):
    job_id: str
    video_id: str


@router.post("/trigger", dependencies=[Depends(verify_api_key)])
async def trigger_job(req: TriggerJobRequest):
    """Manually trigger processing for a specific job (for testing)"""
    return {"message": "Job will be picked up by the background worker", "job_id": req.job_id}


@router.get("/status/{job_id}", dependencies=[Depends(verify_api_key)])
async def get_job_status(job_id: str):
    """Get current status of a processing job"""
    from supabase import create_client
    settings = get_settings()
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)

    result = supabase.table("processing_jobs").select("*").eq("id", job_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Job not found")

    return result.data
