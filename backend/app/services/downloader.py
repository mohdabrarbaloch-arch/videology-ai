"""
Video downloader service — supports YouTube (yt-dlp) and direct URLs
Includes SSRF protection for direct URL downloads
"""

import os
import re
import asyncio
import ipaddress
import urllib.parse
from pathlib import Path
from typing import Optional
import httpx
import yt_dlp
import structlog

from app.config import get_settings

logger = structlog.get_logger()

# SSRF protection: blocked IP ranges
BLOCKED_RANGES = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
]


def is_safe_url(url: str) -> bool:
    """SSRF protection: reject private/internal IP addresses"""
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        hostname = parsed.hostname
        if not hostname:
            return False
        # Reject raw IP addresses in private ranges
        try:
            ip = ipaddress.ip_address(hostname)
            for blocked in BLOCKED_RANGES:
                if ip in blocked:
                    logger.warning("SSRF attempt blocked", url=url, ip=str(ip))
                    return False
        except ValueError:
            pass  # hostname is a domain name, not an IP — OK
        return True
    except Exception:
        return False


def extract_youtube_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from various URL formats"""
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
        r"youtube\.com/shorts/([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


async def download_youtube(url: str, output_dir: str, job_id: str) -> dict:
    """Download YouTube video using yt-dlp"""
    settings = get_settings()
    output_path = os.path.join(output_dir, f"{job_id}.%(ext)s")

    ydl_opts = {
        "format": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "outtmpl": output_path,
        "max_filesize": settings.max_video_size_mb * 1024 * 1024,
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "writeinfojson": False,
        "noplaylist": True,
        # No cookies, no DRM bypass
        "nocheckcertificate": False,
    }

    loop = asyncio.get_event_loop()

    def _download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return {
                "title": info.get("title", "Untitled"),
                "duration": info.get("duration"),
                "description": info.get("description", ""),
                "youtube_id": info.get("id"),
                "file_path": ydl.prepare_filename(info),
                "thumbnail_url": info.get("thumbnail"),
                "uploader": info.get("uploader"),
                "upload_date": info.get("upload_date"),
            }

    result = await loop.run_in_executor(None, _download)
    logger.info("YouTube download complete", job_id=job_id, title=result["title"])
    return result


async def download_direct_url(url: str, output_dir: str, job_id: str) -> dict:
    """Download video from a direct URL with SSRF protection and size limits"""
    settings = get_settings()

    if not is_safe_url(url):
        raise ValueError(f"URL failed SSRF safety check: {url}")

    max_bytes = settings.max_video_size_mb * 1024 * 1024
    output_path = os.path.join(output_dir, f"{job_id}_direct")

    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=httpx.Timeout(30.0, read=300.0),
        limits=httpx.Limits(max_connections=5),
    ) as client:
        # HEAD request to check content type and size
        try:
            head = await client.head(url)
            content_type = head.headers.get("content-type", "")
            content_length = int(head.headers.get("content-length", 0))

            if content_length > max_bytes:
                raise ValueError(
                    f"File too large: {content_length / 1024 / 1024:.1f}MB "
                    f"(max {settings.max_video_size_mb}MB)"
                )

            # Validate it's a video/audio type
            allowed_types = ["video/", "audio/", "application/octet-stream"]
            if not any(content_type.startswith(t) for t in allowed_types):
                raise ValueError(f"Unsupported content type: {content_type}")

            # Determine extension
            ext = "mp4"
            if "webm" in content_type:
                ext = "webm"
            elif "ogg" in content_type:
                ext = "ogg"
            elif "audio/mpeg" in content_type:
                ext = "mp3"

            output_path = f"{output_path}.{ext}"
        except httpx.HTTPError:
            output_path = f"{output_path}.mp4"

        # Stream download
        downloaded = 0
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            with open(output_path, "wb") as f:
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    downloaded += len(chunk)
                    if downloaded > max_bytes:
                        raise ValueError(
                            f"Download exceeded size limit of {settings.max_video_size_mb}MB"
                        )
                    f.write(chunk)

    # Extract filename from URL
    parsed = urllib.parse.urlparse(url)
    filename = os.path.basename(parsed.path) or "video"
    title = os.path.splitext(filename)[0]

    logger.info("Direct URL download complete", job_id=job_id, bytes=downloaded)
    return {
        "title": title,
        "duration": None,
        "description": "",
        "youtube_id": None,
        "file_path": output_path,
        "thumbnail_url": None,
    }
