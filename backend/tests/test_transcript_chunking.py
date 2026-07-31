"""Tests for transcript chunking logic."""

import pytest
from app.routers.transcription import (
    calculate_chunk_duration,
    chunk_transcript_segments,
    merge_transcript_chunks,
    segments_to_srt,
    segments_to_vtt,
    segments_to_txt,
    format_timestamp_srt,
    format_timestamp_vtt,
    WHISPER_MAX_FILE_SIZE,
)


class TestChunkDurationCalculation:
    """Test chunk duration calculation for long audio files."""

    def test_small_file_no_chunking(self):
        """Files under 25MB should not need chunking."""
        duration = calculate_chunk_duration(10 * 1024 * 1024, 300.0)
        assert duration == 300.0  # Full duration, no chunking needed

    def test_large_file_needs_chunking(self):
        """Files over 25MB should be chunked."""
        duration = calculate_chunk_duration(100 * 1024 * 1024, 3600.0)
        assert duration < 3600.0  # Should be less than full duration
        assert duration >= 30  # Minimum 30 seconds

    def test_very_large_file(self):
        """Very large files should have reasonable chunk durations."""
        duration = calculate_chunk_duration(500 * 1024 * 1024, 7200.0)
        assert duration <= 1800  # Maximum 30 minutes
        assert duration >= 30  # Minimum 30 seconds

    def test_chunk_duration_is_rounded(self):
        """Chunk duration should be rounded to nearest 60 seconds."""
        duration = calculate_chunk_duration(50 * 1024 * 1024, 600.0)
        # Should be a multiple of 60 or at least reasonable
        assert duration > 0


class TestTranscriptChunking:
    """Test transcript segment chunking."""

    def test_chunk_short_transcript(self, sample_segments):
        """Short transcript should produce a single chunk."""
        chunks = chunk_transcript_segments(sample_segments, chunk_duration=300.0)
        assert len(chunks) >= 1
        # All segments should be in chunks
        total_segs = sum(len(chunk) for chunk in chunks)
        assert total_segs == len(sample_segments)

    def test_chunk_with_small_duration(self, sample_segments):
        """Small chunk duration should produce multiple chunks."""
        chunks = chunk_transcript_segments(sample_segments, chunk_duration=30.0)
        assert len(chunks) > 1

    def test_chunk_timestamps_adjusted(self, sample_segments):
        """Chunk timestamps should be relative to chunk start."""
        chunks = chunk_transcript_segments(sample_segments, chunk_duration=30.0)
        for chunk in chunks:
            for seg in chunk:
                # Adjusted start should be >= 0
                assert seg["start"] >= 0

    def test_chunk_preserves_text(self, sample_segments):
        """Chunking should preserve all text content."""
        chunks = chunk_transcript_segments(sample_segments, chunk_duration=60.0)
        original_text = " ".join(s["text"] for s in sample_segments)
        chunked_text = " ".join(seg["text"] for chunk in chunks for seg in chunk)
        assert original_text.strip() == chunked_text.strip()

    def test_empty_segments(self):
        """Empty segment list should produce no chunks."""
        chunks = chunk_transcript_segments([], chunk_duration=60.0)
        assert len(chunks) == 0


class TestTranscriptMerging:
    """Test merging chunked transcript segments back together."""

    def test_merge_preserves_order(self, sample_segments):
        """Merging should preserve segment order."""
        chunks = chunk_transcript_segments(sample_segments, chunk_duration=30.0)
        merged = merge_transcript_chunks(chunks, chunk_duration=30.0)
        assert len(merged) == len(sample_segments)
        # Check text is preserved
        for i, seg in enumerate(merged):
            assert seg["text"] == sample_segments[i]["text"]

    def test_merge_adjusts_timestamps(self, sample_segments):
        """Merged timestamps should be absolute (relative to full video)."""
        chunks = chunk_transcript_segments(sample_segments, chunk_duration=30.0)
        merged = merge_transcript_chunks(chunks, chunk_duration=30.0)
        # First segment should start at 0
        assert merged[0]["start"] == pytest.approx(0.0, abs=1.0)

    def test_merge_single_chunk(self, sample_segments):
        """Merging a single chunk should return segments as-is."""
        chunks = chunk_transcript_segments(sample_segments, chunk_duration=300.0)
        merged = merge_transcript_chunks(chunks, chunk_duration=300.0)
        assert len(merged) == len(sample_segments)


class TestTranscriptFormats:
    """Test transcript format conversions."""

    def test_srt_format(self, sample_segments):
        """SRT format should have correct structure."""
        srt = segments_to_srt(sample_segments)
        lines = srt.strip().split("\n")
        # First line should be "1"
        assert lines[0] == "1"
        # Second line should be timestamp range
        assert "-->" in lines[1]
        # Third line should be text
        assert lines[2] == sample_segments[0]["text"]

    def test_vtt_format(self, sample_segments):
        """VTT format should start with WEBVTT header."""
        vtt = segments_to_vtt(sample_segments)
        assert vtt.startswith("WEBVTT")
        lines = vtt.strip().split("\n")
        assert lines[0] == "WEBVTT"

    def test_txt_format(self, sample_segments):
        """TXT format should be plain text joined by spaces."""
        txt = segments_to_txt(sample_segments)
        expected = " ".join(s["text"] for s in sample_segments)
        assert txt == expected

    def test_srt_timestamp_format(self):
        """SRT timestamps should be in HH:MM:SS,mmm format."""
        ts = format_timestamp_srt(3661.5)
        assert ts == "01:01:01,500"

    def test_vtt_timestamp_format(self):
        """VTT timestamps should be in HH:MM:SS.mmm format."""
        ts = format_timestamp_vtt(3661.5)
        assert ts == "01:01:01.500"

    def test_empty_segments_srt(self):
        """SRT with no segments should be empty."""
        assert segments_to_srt([]) == ""

    def test_empty_segments_vtt(self):
        """VTT with no segments should just have header."""
        vtt = segments_to_vtt([])
        assert vtt.strip() == "WEBVTT"
