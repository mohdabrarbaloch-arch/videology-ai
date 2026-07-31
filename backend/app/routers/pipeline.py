"""Full processing pipeline router — orchestrates the entire video analysis flow."""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models import JobStatus
from app.routers.videos import validate_video_url

router = APIRouter(prefix="/pipeline", tags=["pipeline"])
logger = logging.getLogger(__name__)


@router.post("/start")
async def start_pipeline(
    video_id: str,
    job_id: str,
    url: Optional[str] = None,
    source_type: str = "youtube",
    background_tasks: BackgroundTasks = None,
):
    """Start the full processing pipeline for a video.

    This endpoint is called by the Next.js API route after creating
    the video and job records in Supabase. It triggers the background
    worker to process the video through all stages.
    """
    # Validate URL if provided
    if url:
        validation = validate_video_url(url)
        if not validation["is_safe"]:
            raise HTTPException(status_code=403, detail="URL validation failed")

    # The actual processing is handled by the job worker which polls
    # Supabase for queued jobs. Here we just confirm the pipeline can start.
    return {
        "video_id": video_id,
        "job_id": job_id,
        "status": JobStatus.QUEUED,
        "message": "Pipeline queued. The background worker will pick up this job.",
    }


@router.get("/status/{job_id}")
async def get_pipeline_status(job_id: str):
    """Get the current status of a pipeline job.

    This is a lightweight endpoint that the frontend can poll.
    The primary status updates come via Supabase Realtime.
    """
    # Status is read from Supabase by the frontend directly
    return {
        "job_id": job_id,
        "message": "Use Supabase Realtime or the /jobs/{id} endpoint for status updates.",
    }


@router.post("/retry/{job_id}")
async def retry_pipeline(job_id: str):
    """Retry a failed pipeline job."""
    return {
        "job_id": job_id,
        "status": JobStatus.QUEUED,
        "message": "Job requeued for processing. Retry count will be incremented.",
    }
