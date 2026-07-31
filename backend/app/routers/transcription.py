"""Transcription router — OpenAI Whisper integration with chunked processing."""

import logging
import os
import tempfile
from typing import Optional
from fastapi import APIRouter, HTTPException
from app.models import TranscriptResponse, TranscriptSegmentModel

router = APIRouter(prefix="/transcription", tags=["transcription"])
logger = logging.getLogger(__name__)

# Whisper has a 25MB file size limit for audio files
WHISPER_MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB
# Target chunk size for long audio (slightly under 25MB for safety)
CHUNK_TARGET_SIZE = 20 * 1024 * 1024  # 20MB
# Estimated bytes per second for MP3 at 64kbps mono
BYTES_PER_SECOND_64KBPS = 8000


def calculate_chunk_duration(file_size_bytes: int, total_duration_seconds: float) -> float:
    """Calculate optimal chunk duration to stay under Whisper's file size limit.

    Args:
        file_size_bytes: Size of the full audio file
        total_duration_seconds: Total duration of the audio

    Returns:
        Chunk duration in seconds
    """
    if file_size_bytes <= WHISPER_MAX_FILE_SIZE:
        return total_duration_seconds

    # Calculate bytes per second
    bytes_per_second = file_size_bytes / total_duration_seconds
    # How many seconds fit in our target chunk size
    chunk_duration = CHUNK_TARGET_SIZE / bytes_per_second
    # Round to nearest 60 seconds for cleaner chunks
    chunk_duration = round(chunk_duration / 60) * 60
    # Minimum 30 seconds, maximum 30 minutes
    return max(30, min(chunk_duration, 1800))


def chunk_transcript_segments(
    segments: list[dict],
    chunk_duration: float,
) -> list[list[dict]]:
    """Split transcript segments into chunks based on duration.

    Used for processing long videos where audio is split into chunks.
    Each chunk's segments have timestamps adjusted to be relative to the chunk start.
    """
    chunks = []
    current_chunk = []
    current_start = 0.0

    for seg in segments:
        seg_start = seg.get("start", 0)
        seg_end = seg.get("end", 0)

        # If segment exceeds current chunk boundary, start a new chunk
        if seg_start - current_start >= chunk_duration and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_start = seg_start

        # Adjust timestamps relative to chunk start
        adjusted_seg = {
            "start": seg_start - current_start,
            "end": seg_end - current_start,
            "text": seg.get("text", "").strip(),
        }
        current_chunk.append(adjusted_seg)

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def merge_transcript_chunks(
    chunked_segments: list[list[dict]],
    chunk_duration: float,
) -> list[dict]:
    """Merge transcript segments from multiple chunks back together.

    Adjusts timestamps to be absolute (relative to the full video).
    """
    merged = []
    time_offset = 0.0

    for chunk_idx, chunk in enumerate(chunked_segments):
        for seg in chunk:
            merged.append({
                "start": seg["start"] + time_offset,
                "end": seg["end"] + time_offset,
                "text": seg["text"],
            })
        # Update offset for next chunk
        if chunk:
            last_seg = chunk[-1]
            time_offset = chunk_idx * chunk_duration + last_seg["end"]

    return merged


def format_timestamp_srt(seconds: float) -> str:
    """Format seconds as SRT timestamp: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_timestamp_vtt(seconds: float) -> str:
    """Format seconds as VTT timestamp: HH:MM:SS.mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def segments_to_srt(segments: list[dict]) -> str:
    """Convert transcript segments to SRT format."""
    lines = []
    for i, seg in enumerate(segments, 1):
        lines.append(str(i))
        lines.append(f"{format_timestamp_srt(seg['start'])} --> {format_timestamp_srt(seg['end'])}")
        lines.append(seg["text"])
        lines.append("")
    return "\n".join(lines)


def segments_to_vtt(segments: list[dict]) -> str:
    """Convert transcript segments to VTT format."""
    lines = ["WEBVTT", ""]
    for seg in segments:
        lines.append(f"{format_timestamp_vtt(seg['start'])} --> {format_timestamp_vtt(seg['end'])}")
        lines.append(seg["text"])
        lines.append("")
    return "\n".join(lines)


def segments_to_txt(segments: list[dict]) -> str:
    """Convert transcript segments to plain text."""
    return " ".join(seg["text"] for seg in segments)


@router.get("/formats")
async def get_supported_formats():
    """Get supported transcript formats."""
    return {
        "formats": ["srt", "vtt", "txt"],
        "whisper_max_file_size": WHISPER_MAX_FILE_SIZE,
        "chunk_target_size": CHUNK_TARGET_SIZE,
    }


@router.post("/chunk-info")
async def get_chunk_info(file_size_bytes: int, total_duration_seconds: float):
    """Get chunking information for a long audio file."""
    chunk_dur = calculate_chunk_duration(file_size_bytes, total_duration_seconds)
    num_chunks = int(total_duration_seconds / chunk_dur) + (1 if total_duration_seconds % chunk_dur > 0 else 0)
    return {
        "needs_chunking": file_size_bytes > WHISPER_MAX_FILE_SIZE,
        "chunk_duration_seconds": chunk_dur,
        "estimated_num_chunks": num_chunks,
        "whisper_max_file_size": WHISPER_MAX_FILE_SIZE,
    }
