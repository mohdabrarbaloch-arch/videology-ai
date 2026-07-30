import os
import re
import ipaddress
import asyncio
from pathlib import Path
from typing import Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import get_settings


class SSRFProtectionError(Exception):
    pass


class DownloadError(Exception):
    pass


def is_private_ip(host: str) -> bool:
    """SSRF protection: block private IP ranges"""
    try:
        addr = ipaddress.ip_address(host)
        return addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_multicast
    except ValueError:
        pass
    blocked_patterns = [
        r"^localhost$", r"^127\.", r"^10\.", r"^192\.168\.",
        r"^172\.(1[6-9]|2[0-9]|3[01])\.", r"^169\.254\.",
        r"^0\.", r"^255\.", r"^[::1]$", r"^fe80:",
    ]
    for pattern in blocked_patterns:
        if re.match(pattern, host, re.IGNORECASE):
            return True
    return False


def validate_url(url: str) -> None:
    """Validate URL and protect against SSRF"""
    import urllib.parse
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        raise SSRFProtectionError(f"Invalid scheme: {parsed.scheme}")
    host = parsed.hostname or ''
    if is_private_ip(host):
        raise SSRFProtectionError(f"Access to private IP blocked: {host}")


class VideoDownloader:
    def __init__(self):
        self.settings = get_settings()

    async def download(self, source_type: str, url: Optional[str], storage_path: Optional[str], output_dir: str) -> str:
        """Download video and return local path"""
        os.makedirs(output_dir, exist_ok=True)
        if source_type == 'youtube':
            return await self._download_youtube(url, output_dir)
        elif source_type == 'url':
            return await self._download_direct(url, output_dir)
        elif source_type == 'upload':
            return await self._download_from_supabase(storage_path, output_dir)
        else:
            raise DownloadError(f"Unsupported source type: {source_type}")

    async def _download_youtube(self, url: str, output_dir: str) -> str:
        """Download YouTube video using yt-dlp"""
        output_path = os.path.join(output_dir, 'video.%(ext)s')
        cmd = [
            'yt-dlp',
            '--format', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            '--output', output_path,
            '--no-playlist',
            '--max-filesize', f'{self.settings.max_video_size_mb}M',
            '--no-warnings',
            url
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise DownloadError(f"YouTube download failed: {stderr.decode()}")
        for ext in ['mp4', 'webm', 'mkv', 'mov']:
            path = os.path.join(output_dir, f'video.{ext}')
            if os.path.exists(path):
                return path
        raise DownloadError("Downloaded file not found")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _download_direct(self, url: str, output_dir: str) -> str:
        """Download direct URL with SSRF protection"""
        validate_url(url)
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            async with client.stream('GET', url) as response:
                response.raise_for_status()
                content_type = response.headers.get('content-type', '')
                if not any(p in content_type for p in ['video', 'octet-stream']):
                    raise DownloadError(f"Invalid content type: {content_type}")
                filename = url.split('/')[-1].split('?')[0] or 'video.mp4'
                output_path = os.path.join(output_dir, filename)
                total_size = 0
                max_size = self.settings.max_video_size_mb * 1024 * 1024
                with open(output_path, 'wb') as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        total_size += len(chunk)
                        if total_size > max_size:
                            raise DownloadError(f"File too large (max: {self.settings.max_video_size_mb}MB)")
                        f.write(chunk)
                return output_path

    async def _download_from_supabase(self, storage_path: str, output_dir: str) -> str:
        """Download file from Supabase Storage"""
        from supabase import create_client
        sub = create_client(self.settings.supabase_url, self.settings.supabase_service_role_key)
        response = sub.storage.from_('videos').download(storage_path)
        filename = storage_path.split('/')[-1]
        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'wb') as f:
            f.write(response)
        return output_path

    async def get_video_metadata(self, url: str) -> dict:
        """Get video metadata without downloading"""
        cmd = ['yt-dlp', '--dump-json', '--no-playlist', url]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        if proc.returncode != 0:
            return {}
        import json
        try:
            data = json.loads(stdout.decode())
            return {
                'title': data.get('title', ''),
                'duration': data.get('duration', 0),
                'thumbnail': data.get('thumbnail', ''),
                'description': data.get('description', '')[:500],
                'uploader': data.get('uploader', ''),
            }
        except Exception:
            return {}
