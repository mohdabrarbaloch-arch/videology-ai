"""Tests for URL validation and SSRF protection."""

import pytest
from app.routers.videos import (
    extract_youtube_id,
    is_safe_url,
    validate_video_url,
    validate_upload_metadata,
    ALLOWED_VIDEO_EXTENSIONS,
    ALLOWED_VIDEO_MIMES,
)


class TestYouTubeIdExtraction:
    """Test YouTube video ID extraction from various URL formats."""

    def test_standard_youtube_url(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_youtube_id(url) == "dQw4w9WgXcQ"

    def test_short_youtube_url(self):
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert extract_youtube_id(url) == "dQw4w9WgXcQ"

    def test_embed_url(self):
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        assert extract_youtube_id(url) == "dQw4w9WgXcQ"

    def test_shorts_url(self):
        url = "https://www.youtube.com/shorts/dQw4w9WgXcQ"
        assert extract_youtube_id(url) == "dQw4w9WgXcQ"

    def test_url_with_extra_params(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120s&feature=share"
        assert extract_youtube_id(url) == "dQw4w9WgXcQ"

    def test_non_youtube_url(self):
        url = "https://example.com/video.mp4"
        assert extract_youtube_id(url) is None

    def test_invalid_url(self):
        assert extract_youtube_id("not a url") is None

    def test_empty_string(self):
        assert extract_youtube_id("") is None


class TestSSRFProtection:
    """Test SSRF protection in URL validation."""

    def test_safe_https_url(self):
        assert is_safe_url("https://example.com/video.mp4") is True

    def test_safe_http_url(self):
        assert is_safe_url("http://example.com/video.mp4") is True

    def test_blocks_localhost(self):
        assert is_safe_url("http://localhost/video.mp4") is False

    def test_blocks_127_0_0_1(self):
        assert is_safe_url("http://127.0.0.1/video.mp4") is False

    def test_blocks_private_ip_192_168(self):
        assert is_safe_url("http://192.168.1.1/video.mp4") is False

    def test_blocks_private_ip_10(self):
        assert is_safe_url("http://10.0.0.1/video.mp4") is False

    def test_blocks_private_ip_172(self):
        assert is_safe_url("http://172.16.0.1/video.mp4") is False

    def test_blocks_metadata_endpoint(self):
        assert is_safe_url("http://metadata.google.internal/computeMetadata/") is False

    def test_blocks_169_254_link_local(self):
        assert is_safe_url("http://169.254.169.254/latest/meta-data/") is False

    def test_blocks_ftp_scheme(self):
        assert is_safe_url("ftp://example.com/video.mp4") is False

    def test_blocks_file_scheme(self):
        assert is_safe_url("file:///etc/passwd") is False

    def test_blocks_empty_hostname(self):
        assert is_safe_url("http:///video.mp4") is False

    def test_blocks_no_scheme(self):
        assert is_safe_url("example.com/video.mp4") is False


class TestVideoUrlValidation:
    """Test full video URL validation."""

    def test_youtube_url_validation(self):
        result = validate_video_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert result["source_type"] == "youtube"
        assert result["youtube_id"] == "dQw4w9WgXcQ"
        assert result["is_safe"] is True

    def test_direct_url_validation(self):
        result = validate_video_url("https://example.com/video.mp4")
        assert result["source_type"] == "direct_url"
        assert result["is_safe"] is True
        assert result["has_video_extension"] is True

    def test_direct_url_without_extension(self):
        result = validate_video_url("https://example.com/video?id=123")
        assert result["source_type"] == "direct_url"
        assert result["has_video_extension"] is False

    def test_ssrf_url_rejected(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            validate_video_url("http://127.0.0.1/video.mp4")
        assert exc_info.value.status_code == 403

    def test_empty_url_rejected(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            validate_video_url("")
        assert exc_info.value.status_code == 400

    def test_non_http_url_rejected(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            validate_video_url("ftp://example.com/video.mp4")
        assert exc_info.value.status_code == 400


class TestUploadValidation:
    """Test file upload metadata validation."""

    def test_valid_upload(self):
        result = validate_upload_metadata("video.mp4", "video/mp4", 1024 * 1024)
        assert result["valid"] is True

    def test_invalid_extension(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            validate_upload_metadata("video.exe", "application/octet-stream", 1024)
        assert exc_info.value.status_code == 400

    def test_invalid_mime_type(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            validate_upload_metadata("video.mp4", "text/html", 1024)
        assert exc_info.value.status_code == 400

    def test_oversized_file(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            validate_upload_metadata("video.mp4", "video/mp4", 600 * 1024 * 1024, max_size_mb=500)
        assert exc_info.value.status_code == 400

    def test_allowed_extensions(self):
        for ext in ALLOWED_VIDEO_EXTENSIONS:
            assert ext in {".mp4", ".webm", ".mov", ".avi", ".mkv", ".m4v"}

    def test_allowed_mimes(self):
        for mime in ALLOWED_VIDEO_MIMES:
            assert mime.startswith("video/")
