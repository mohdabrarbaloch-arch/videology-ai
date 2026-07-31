"""Storage service — Supabase Storage upload/download operations."""

import logging
import os
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

VIDEOS_BUCKET = "videos"
THUMBNAILS_BUCKET = "thumbnails"
FRAMES_BUCKET = "frames"
AUDIO_BUCKET = "audio"


class StorageService:
    """Service for Supabase Storage operations."""

    def __init__(self, supabase_url: str, supabase_service_key: str):
        self.supabase_url = supabase_url
        self.supabase_service_key = supabase_service_key
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from supabase import create_client
            self._client = create_client(self.supabase_url, self.supabase_service_key)
        return self._client

    def upload_file(self, bucket: str, path: str, file_path: str, content_type: str = "application/octet-stream") -> dict:
        with open(file_path, "rb") as f:
            result = self.client.storage.from_(bucket).upload(path=path, file=f, file_options={"content-type": content_type})
        if hasattr(result, "error") and result.error:
            logger.error(f"Storage upload failed: {result.error}")
            raise RuntimeError(f"Upload failed: {result.error}")
        public_url = self.client.storage.from_(bucket).get_public_url(path)
        return {"path": path, "public_url": public_url, "bucket": bucket}

    def upload_bytes(self, bucket: str, path: str, data: bytes, content_type: str = "application/octet-stream") -> dict:
        import io
        result = self.client.storage.from_(bucket).upload(path=path, file=io.BytesIO(data), file_options={"content-type": content_type})
        if hasattr(result, "error") and result.error:
            logger.error(f"Storage upload failed: {result.error}")
            raise RuntimeError(f"Upload failed: {result.error}")
        public_url = self.client.storage.from_(bucket).get_public_url(path)
        return {"path": path, "public_url": public_url, "bucket": bucket}

    def download_file(self, bucket: str, path: str, local_path: str) -> str:
        result = self.client.storage.from_(bucket).download(path)
        if hasattr(result, "error") and result.error:
            logger.error(f"Storage download failed: {result.error}")
            raise RuntimeError(f"Download failed: {result.error}")
        data = result if isinstance(result, bytes) else result.data
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(data)
        return local_path

    def create_signed_url(self, bucket: str, path: str, expires_in: int = 3600) -> str:
        result = self.client.storage.from_(bucket).create_signed_url(path, expires_in)
        if hasattr(result, "error") and result.error:
            logger.error(f"Signed URL creation failed: {result.error}")
            raise RuntimeError(f"Signed URL failed: {result.error}")
        return result.get("signedURL", "") if isinstance(result, dict) else result.signed_url

    def delete_file(self, bucket: str, path: str) -> bool:
        result = self.client.storage.from_(bucket).remove([path])
        if hasattr(result, "error") and result.error:
            logger.error(f"Storage delete failed: {result.error}")
            return False
        return True

    def list_files(self, bucket: str, prefix: str = "") -> list[dict]:
        result = self.client.storage.from_(bucket).list(prefix)
        if hasattr(result, "error") and result.error:
            logger.error(f"Storage list failed: {result.error}")
            return []
        return result if isinstance(result, list) else []

    def ensure_buckets_exist(self):
        buckets_to_create = [(VIDEOS_BUCKET, "Video files uploaded by users"), (THUMBNAILS_BUCKET, "AI-generated thumbnails"), (FRAMES_BUCKET, "Extracted video frames"), (AUDIO_BUCKET, "Extracted audio files")]
        for bucket_name, description in buckets_to_create:
            try:
                self.client.storage.from_(bucket_name).list(limit=1)
            except Exception:
                logger.info(f"Creating bucket: {bucket_name}")
                try:
                    self.client.storage.create_bucket(bucket_name, options={"public": False, "size_limit": "500MB"})
                except Exception as e:
                    logger.warning(f"Could not create bucket {bucket_name}: {e}")
