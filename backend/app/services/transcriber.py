import os
import asyncio
import math
from typing import List, Dict, Any
import openai
from app.config import get_settings


class TranscriptionService:
    MAX_CHUNK_SIZE_BYTES = 24 * 1024 * 1024  # 24MB (whisper limit is 25MB)

    def __init__(self):
        self.settings = get_settings()
        self.client = openai.AsyncOpenAI(openai_api_key=self.settings.openai_api_key)

    async def extract_audio(self, video_path: str, output_dir: str) -> str:
        """Extract audio from video using FFmpeg"""
        audio_path = os.path.join(output_dir, 'audio.mp3')
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vn',  # no video
            '-ac', '1',  # mono
            '-ar', '16000',  # 16kHz sample rate
            '-ab', '64k',  # 64kbps bitrate
            '-f', 'mp3',
            audio_path
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"FFmpeg audio extraction failed: {stderr.decode()}")
        return audio_path

    async def get_audio_duration(self, audio_path: str) -> float:
        """Get audio duration in seconds using ffprobe"""
        cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=Duration', '-of', 'default=nowrapper=1:nokey=1', audio_path]
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, wait_for_connection=False)
        stdout, _ = await proc.communicate()
        try:
            return float(stdout.decode().strip())
        except ValueError:
            return 0.0

    async def split_audio_chunks(self, audio_path: str, output_dir: str) -> List[str]:
        """Split audio into chunks if file is too large for Whisper"""
        file_size = os.path.getsize(audio_path)
        if file_size <= self.MAX_CHUNK_SIZE_BYTES:
            return [audio_path]
        chunk_duration = self.settings.chunk_duration_seconds
        cmd = [
            'ffmpeg', '-y',
            '-i', audio_path,
            '-f', 'segment',
            '-segment_time', str(chunk_duration),
            '-c', 'copy',
            os.path.join(output_dir, 'chunk_%03d.mp3')
        ]
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        await proc.communicate()
        chunks = sorted([
            os.path.join(output_dir, f)
            for f in os.listdir(output_dir)
            if f.startswith('chunk_') and f.endswith('.mp3')
        ])
        return chunks

    async def transcribe(self, audio_path: str) -> Dict[str, Any]:
        """Transcribe audio using OpenAI Whisper"""
        chunk_dir = os.path.dirname(audio_path)
        chunks = await self.split_audio_chunks(audio_path, chunk_dir)
        all_segments = []
        full_text_parts = []
        language = None
        time_offset = 0.0
        for i, chunk_path in enumerate(chunks):
            with open(chunk_path, 'rb') as f:
                response = await self.client.audio.transcriptions.create(
                    model=self.settings.transcription_model,
                    file=f,
                    response_format='verbose_json',
                    timestamp_granularities=['segment'],
                )
            if not language:
                language = response.language
            full_text_parts.append(response.text)
            for seg in (response.segments or []):
                all_segments.append({
                    'start': seg.start + time_offset,
                    'end': seg.end + time_offset,
                    'text': seg.text.strip(),
                })
            if response.segments:
                time_offset += response.segments[-1].end
        return {
            'full_text': ' '.join(full_text_parts),
            'segments': all_segments,
            'language': language or 'en',
            'word_count': len(' '.join(full_text_parts).split()),
        }
