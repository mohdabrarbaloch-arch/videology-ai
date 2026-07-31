"""FFmpeg service — audio extraction, frame extraction, and media processing."""

import logging
import os
import subprocess
import tempfile
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class FFmpegService:
    """Service for FFmpeg-based media processing operations."""

    def __init__(self):
        self.ffmpeg_path = os.environ.get("FFMPEG_PATH", "ffmpeg")
        self.ffprobe_path = os.environ.get("FFPROBE_PATH", "ffprobe")

    def is_available(self) -> bool:
        try:
            result = subprocess.run([self.ffmpeg_path, "-version"], capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def get_duration(self, video_path: str) -> float:
        cmd = [self.ffprobe_path, "-v", "quiet", "-print_format", "json", "-show_format", video_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            logger.error(f"ffprobe failed: {result.stderr}")
            return 0.0
        import json
        data = json.loads(result.stdout)
        return float(data.get("format", {}).get("duration", 0))

    def extract_audio(self, video_path: str, output_dir: str, chunk_duration: Optional[float] = None) -> list[str]:
        os.makedirs(output_dir, exist_ok=True)
        if chunk_duration:
            cmd = [self.ffmpeg_path, "-i", video_path, "-vn", "-acodec", "libmp3lame", "-ab", "64k", "-ac", "1", "-ar", "16000", "-f", "segment", "-segment_time", str(int(chunk_duration)), "-reset_timestamps", "1", os.path.join(output_dir, "chunk_%03d.mp3"), "-y"]
        else:
            output_path = os.path.join(output_dir, "audio.mp3")
            cmd = [self.ffmpeg_path, "-i", video_path, "-vn", "-acodec", "libmp3lame", "-ab", "64k", "-ac", "1", "-ar", "16000", output_path, "-y"]
        logger.info(f"Extracting audio: {' '.join(cmd[:5])}...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            logger.error(f"FFmpeg audio extraction failed: {result.stderr[-500:]}")
            raise RuntimeError(f"Audio extraction failed: {result.stderr[-200:]}")
        if chunk_duration:
            files = sorted(f for f in os.listdir(output_dir) if f.startswith("chunk_") and f.endswith(".mp3"))
            return [os.path.join(output_dir, f) for f in files]
        else:
            return [os.path.join(output_dir, "audio.mp3")]

    def extract_frames(self, video_path: str, output_dir: str, interval_seconds: float = 30.0, max_frames: int = 20) -> list[str]:
        os.makedirs(output_dir, exist_ok=True)
        duration = self.get_duration(video_path)
        if duration <= 0:
            logger.warning("Could not determine video duration, using default interval")
            duration = 300
        num_frames = min(int(duration / interval_seconds) + 1, max_frames)
        if num_frames > 0:
            actual_interval = duration / num_frames
        else:
            actual_interval = interval_seconds
        fps = 1.0 / actual_interval if actual_interval > 0 else 0.1
        cmd = [self.ffmpeg_path, "-i", video_path, "-vf", f"fps={fps:.4f}", "-frames:v", str(max_frames), "-q:v", "2", os.path.join(output_dir, "frame_%04d.jpg"), "-y"]
        logger.info(f"Extracting frames at {fps:.4f} fps (max {max_frames})")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            logger.error(f"Frame extraction failed: {result.stderr[-500:]}")
            return []
        files = sorted(f for f in os.listdir(output_dir) if f.startswith("frame_") and f.endswith(".jpg"))
        return [os.path.join(output_dir, f) for f in files]

    def get_video_info(self, video_path: str) -> dict:
        cmd = [self.ffprobe_path, "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", video_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return {}
        import json
        return json.loads(result.stdout)
