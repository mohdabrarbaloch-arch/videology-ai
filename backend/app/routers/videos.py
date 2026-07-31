"""Video CRUD and source validation router."""

import re
import ipaddress
import socket
from urllib.parse import urlparse
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from app.models import VideoSource

router = APIRouter(prefix="/videos", tags=["videos"])

# Private IP ranges for SSRF protection
PRIVATE_IP_PREFIXES = (
    "10.", "172.16.", "172.17.", "172.18.", "172.19.",
    "172.20.", "172.21.", "172.22.", "172.23.", "172.24.",
    "172.25.", "172.26.", "172.27.", "172.28.", "172.29.",
    "172.30.", "172.31.", "192.168.", "127.", "0.0.0.0",
    "169.254.", "::1", "fc00:", "fe80:",
)

ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".avi", ".mkv", ".m4v"}
ALLOWED_VIDEO_MIMES = {
    "video/mp4", "video/webm", "video/quicktime",
    "video/x-msvideo", "video/x-matroska", "video/mp4v-es",
}

YOUTUBE_URL_PATTERNS = [
    re.compile(r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})"),
    re.compile(r"youtube\.com/shorts/([a-zA-Z0-9_-]{11})"),
]


def extract_youtube_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from URL."""
    for pattern in YOUTUBE_URL_PATTERNS:
        match = pattern.search(url)
        if match:
            return match.group(1)
    return None


def is_safe_url(url: str) -> bool:
    """Validate URL against SSRF attacks.

    Blocks:
    - Private/internal IP addresses
    - Localhost
    - Link-local addresses
    - Non-HTTP(S) schemes
    """
    try:
        parsed = urlparse(url)
    except Exception:
        return False

    # Only allow http and https
    if parsed.scheme not in ("http", "https"):
        return False

    hostname = parsed.hostname
    if not hostname:
        return False

    # Block obvious private hostnames
    if hostname in ("localhost", "metadata.google.internal"):
        return False

    # Check if hostname is an IP address
    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return False
    except ValueError:
        # It's a domain name, resolve it
        try:
            resolved = socket.getaddrinfo(hostname, None)
            for family, _, _, _, sockaddr in resolved:
                ip_str = sockaddr[0]
                try:
                    ip = ipaddress.ip_address(ip_str)
                    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                        return False
                except ValueError:
                    continue
        except socket.gaierror:
            return False

    # Check against private IP prefixes as fallback
    for prefix in PRIVATE_IP_PREFIXES:
        if hostname.startswith(prefix):
            return False

    return True


def validate_video_url(url: str) -> dict:
    """Validate a video URL and determine its source type.

    Returns dict with: source_type, youtube_id (if applicable), is_safe
    """
    if not url or not url.strip():
        raise HTTPException(status_code=400, detail="URL is required")

    url = url.strip()

    # Check if it's a YouTube URL
    youtube_id = extract_youtube_id(url)
    if youtube_id:
        return {
            "source_type": VideoSource.YOUTUBE,
            "youtube_id": youtube_id,
            "is_safe": True,
            "validated_url": url,
        }

    # Check if it's a direct URL
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")

    # SSRF check
    if not is_safe_url(url):
        raise HTTPException(status_code=403, detail="URL blocked: potential SSRF attack detected")

    # Check file extension
    parsed = urlparse(url)
    path = parsed.path.lower()
    has_video_ext = any(path.endswith(ext) for ext in ALLOWED_VIDEO_EXTENSIONS)

    return {
        "source_type": VideoSource.DIRECT_URL,
        "youtube_id": None,
        "is_safe": True,
        "validated_url": url,
        "has_video_extension": has_video_ext,
    }


def validate_upload_metadata(filename: str, content_type: str, size: int, max_size_mb: int = 500) -> dict:
    """Validate uploaded file metadata."""
    errors = []

    # Check extension
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        errors.append(f"File extension '{ext}' not allowed. Allowed: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}")

    # Check MIME type
    if content_type not in ALLOWED_VIDEO_MIMES:
        errors.append(f"Content type '{content_type}' not allowed")

    # Check size
    max_size_bytes = max_size_mb * 1024 * 1024
    if size > max_size_bytes:
        errors.append(f"File size {size} bytes exceeds maximum of {max_size_mb}MB")

    if errors:
        raise HTTPException(status_code=400, detail="; ".join(errors))

    return {"valid": True, "filename": filename, "content_type": content_type, "size": size}


@router.get("/validate-url")
async def validate_url(url: str):
    """Validate a video URL before processing."""
    result = validate_video_url(url)
    return result


@router.get("/validate-upload")
async def validate_upload(filename: str, content_type: str, size: int):
    """Validate upload metadata."""
    result = validate_upload_metadata(filename, content_type, size)
    return result
