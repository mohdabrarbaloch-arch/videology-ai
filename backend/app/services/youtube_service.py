"""YouTube service — yt-dlp wrapper for downloading YouTube videos.

IMPORTANT: This service respects YouTube's Terms of Service and does NOT bypass
any DRM or access controls. It only downloads publicly available videos using
yt-dlp's standard functionality.
"""

import logging
import os
import subprocess
import re
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class YouTubeService:
    """Service for downloading YouTube videos using yt-dlp."""

    def __init__(self):
        self.yt_dlp_path = os.environ.get("YT_DLP_PATH", "yt-dlp")
        self.max_filesize = int(os.environ.get("MAX_VIDEO_SIZE_MB", "500")) * 1024 * 1024

    def is_available(self) -> bool:
        """Check if yt-dlp is installed."""
        try:
            result = subprocess.run(
                [self.yt_dlp_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL."""
        patterns = [
            r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
            r"youtube\.com/shorts/([a-zA-Z0-9_-]{11})",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_video_info(self, url: str) -> dict:
        """Get video metadata without downloading."""
        video_id = self.extract_video_id(url)
        if not video_id:
            raise ValueError(f"Invalid YouTube URL: {url}")

        cmd = [
            self.yt_dlp_path,
            "--dump-json",
            "--no-download",
            "--no-warnings",
            url,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            logger.error(f"yt-dlp info extraction failed: {result.stderr}")
            raise RuntimeError(f"Failed to get video info: {result.stderr[:200]}")

        import json
        info = json.loads(result.stdout)
        return {
            "video_id": info.get("id", video_id),
            "title": info.get("title", ""),
            "description": info.get("description", ""),
            "duration": info.get("duration", 0),
            "uploader": info.get("uploader", ""),
            "upload_date": info.get("upload_date", ""),
            "view_count": info.get("view_count", 0),
            "thumbnail": info.get("thumbnail", ""),
            "webpage_url": info.get("webpage_url", url),
        }

    def download_video(
        self,
        url: str,
        output_dir: str,
        quality: str = "720p",
    ) -> str:
        """Download a YouTube video.

        Respects YouTube ToS — only downloads publicly available content.
        Does NOT bypass DRM, age restrictions, or any access controls.

        Args:
            url: YouTube video URL
            output_dir: Directory to save the video
            quality: Preferred quality (720p, 1080p, best, worst)

        Returns:
            Path to the downloaded video file
        """
        os.makedirs(output_dir, exist_ok=True)

        output_template = os.path.join(output_dir, "video.%(ext)s")

        # Format selection — prefer mp4, limit quality and filesize
        if quality == "best":
            format_selector = "best[ext=mp4]/best"
        elif quality == "worst":
            format_selector = "worst[ext=mp4]/worst"
        else:
            # Default: 720p or best available under max filesize
            format_selector = (
                f"best[height<={quality.replace('p', '')}][ext=mp4]"
                f"[filesize<{self.max_filesize}]/"
                f"best[height<={quality.replace('p', '')}]/"
                f"best[ext=mp4][filesize<{self.max_filesize}]/"
                f"best[filesize<{self.max_filesize}]/best"
            )

        cmd = [
            self.yt_dlp_path,
            "-f", format_selector,
            "-o", output_template,
            "--no-playlist",
            "--no-warnings",
            "--no-progress",
            "--merge-output-format", "mp4",
            url,
        ]

        logger.info(f"Downloading YouTube video: {url}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            logger.error(f"yt-dlp download failed: {result.stderr}")
            raise RuntimeError(f"YouTube download failed: {result.stderr[:300]}")

        # Find the downloaded file
        files = [f for f in os.listdir(output_dir) if f.startswith("video.")]
        if not files:
            raise RuntimeError("Download completed but no output file found")

        return os.path.join(output_dir, files[0])

    def download_audio_only(
        self,
        url: str,
        output_dir: str,
    ) -> str:
        """Download only the audio track from a YouTube video.

        More efficient when only transcription is needed.
        """
        os.makedirs(output_dir, exist_ok=True)
        output_template = os.path.join(output_dir, "audio.%(ext)s")

        cmd = [
            self.yt_dlp_path,
            "-f", "bestaudio/best",
            "-x",  # Extract audio
            "--audio-format", "mp3",
            "--audio-quality", "5",  # 0-10, 5 is medium quality
            "-o", output_template,
            "--no-playlist",
            "--no-warnings",
            "--no-progress",
            url,
        ]

        logger.info(f"Downloading audio from YouTube: {url}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            logger.error(f"yt-dlp audio download failed: {result.stderr}")
            raise RuntimeError(f"YouTube audio download failed: {result.stderr[:300]}")

        files = [f for f in os.listdir(output_dir) if f.startswith("audio.")]
        if not files:
            raise RuntimeError("Audio download completed but no output file found")

        return os.path.join(output_dir, files[0])
