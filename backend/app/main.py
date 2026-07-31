"""Videology AI — FastAPI backend service for video intelligence processing."""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import health, jobs, videos, pipeline, transcription, analysis, thumbnails, ask, quiz, learning, translation

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    settings = get_settings()
    logger.info(f"Starting Videology AI backend v{VERSION}")
    logger.info(f"OpenAI configured: {bool(settings.openai_api_key)}")
    logger.info(f"Supabase configured: {bool(settings.supabase_url)}")

    # Check FFmpeg availability
    try:
        import subprocess
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=10)
        logger.info(f"FFmpeg available: {result.returncode == 0}")
    except Exception:
        logger.warning("FFmpeg not found — media processing will not work")

    yield

    logger.info("Shutting down Videology AI backend")


app = FastAPI(
    title="Videology AI",
    description="AI Video Intelligence SaaS Platform — Watch. Analyze. Learn.",
    version=VERSION,
    lifespan=lifespan,
)

# CORS — allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(jobs.router)
app.include_router(videos.router)
app.include_router(pipeline.router)
app.include_router(transcription.router)
app.include_router(analysis.router)
app.include_router(thumbnails.router)
app.include_router(ask.router)
app.include_router(quiz.router)
app.include_router(learning.router)
app.include_router(translation.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Videology AI",
        "version": VERSION,
        "tagline": "Watch. Analyze. Learn.",
        "docs": "/docs",
        "health": "/health",
    }
