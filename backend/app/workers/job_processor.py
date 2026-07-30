"""
Background job processor -- polls Supabase for queued jobs and processes them
"""

import os
import asyncio
import traceback
import structlog
import httpx
from supabase import create_client, Client

from app.config import get_settings
from app.services.downloader import VideoDownloader
from app.services.transcriber import TranscriptionService
from app.services.analyzer import AIAnalysisService
from app.services.thumbnail_generator import ThumbnailGenerator

logger = structlog.get_logger()
POLL_INTERVAL = 5


class JobProcessor:
    def __init__(self):
        self.settings = get_settings()
        self.supabase: Client = create_client(
            self.settings.supabase_url,
            self.settings.supabase_service_role_key,
        )
        self.downloader = VideoDownloader()
        self.transcriber = TranscriptionService()
        self.analyzer = AIAnalysisService()
        self.thumbnail_gen = ThumbnailGenerator()

    async def run_forever(self):
        logger.info('Job processor started')
        while True:
            try:
                await self.process_next_job()
            except Exception as e:
                logger.error('Job processor error', error=str(e))
            await asyncio.sleep(POLL_INTERVAL)

    async def process_next_job(self):
        result = self.supabase.table('processing_jobs').select('*, videos(*)').eq('status', 'queued').order('created_at').limit(1).execute()
        if not result.data:
            return
        job = result.data[0]
        job_id = job['id']
        video = job['videos']
        video_id = job['video_id']
        logger.info('Processing job', job_id=job_id, video_id=video_id)
        try:
            await self._process_job(job, video)
        except Exception as e:
            await self._fail_job(job_id, video_id, str(e), traceback.format_exc())

    async def _update_job(self, job_id: str, video_id: str, status: str, progress: int, stage: str):
        self.supabase.table('processing_jobs').update({'status': status, 'progress': progress, 'current_stage': stage}).eq('id', job_id).execute()
        vs = 'completed' if status == 'completed' else 'failed' if status == 'failed' else 'processing'
        self.supabase.table('videos').update({'status': vs}).eq('id', video_id).execute()

    async def _fail_job(self, job_id: str, video_id: str, error: str, details: str):
        job = self.supabase.table('processing_jobs').select('retry_count, max_retries').eq('id', job_id).single().execute()
        rc = job.data.get('retry_count', 0)
        mr = job.data.get('max_retries', 3)
        if rc < mr:
            self.supabase.table('processing_jobs').update({'status': 'queued', 'retry_count': rc + 1, 'error_message': error}).eq('id', job_id).execute()
        else:
            self.supabase.table('processing_jobs').update({'status': 'failed', 'error_message': error}).eq('id', job_id).execute()
            self.supabase.table('videos').update({'status': 'failed'}).eq('id', video_id).execute()

    async def _process_job(self, job: dict, video: dict):
        job_id = job['id']
        video_id = video['id']
        user_id = video['user_id']
        source_type = video['source_type']
        source_url = video.get('source_url')
        storage_path = video.get('storage_path')
        title = video.get('title', 'Untitled')
        temp_dir = self.settings.temp_dir
        download_dir = os.path.join(temp_dir, 'downloads')
        audio_dir = os.path.join(temp_dir, 'audio')

        await self._update_job(job_id, video_id, 'downloading', 5, 'Downloading video')
        video_path = await self.downloader.download(source_type, source_url, storage_path, download_dir)

        await self._update_job(job_id, video_id, 'extracting_audio', 20, 'Extracting audio')
        audio_path = await self.transcriber.extract_audio(video_path, audio_dir)

        await self._update_job(job_id, video_id, 'transcribing', 35, 'Transcribing audio')
        transcription = await self.transcriber.transcribe(audio_path)

        tr_result = self.supabase.table('transcripts').insert({
            'video_id': video_id, 'user_id': user_id,
            'language': transcription['language'], 'full_text': transcription['full_text'],
            'word_count': transcription['word_count'],
        }).execute()
        transcript_id = tr_result.data[0]['id']

        segments_data = [{'transcript_id': transcript_id, 'video_id': video_id, 'segment_index': i, 'start_time': s['start'], 'end_time': s['end'], 'text': s['text']} for i, s in enumerate(transcription['segments'])]
        for i in range(0, len(segments_data), 500):
            self.supabase.table('transcript_segments').insert(segments_data[i:i+500]).execute()

        await self._update_job(job_id, video_id, 'analyzing', 55, 'Analyzing content with AI')
        analysis = await self.analyzer.analyze_transcript(transcription['full_text'], title)

        self.supabase.table('video_analyses').insert({
            'video_id': video_id, 'user_id': user_id,
            'summary': analysis.get('summary'), 'executive_summary': analysis.get('executive_summary'),
            'difficulty_level': analysis.get('difficulty_level'), 'sentiment': analysis.get('sentiment'),
            'content_type': analysis.get('content_type'), 'target_audience': analysis.get('target_audience'),
            'model_used': self.settings.ai_model,
        }).execute()

        if analysis.get('topics'): self.supabase.table('video_topics').insert([{'video_id': video_id, **t} for t in analysis['topics'][:20]]).execute()
        if analysis.get('chapters'): self.supabase.table('video_chapters').insert([{'video_id': video_id, **c} for c in analysis['chapters']]).execute()
        if analysis.get('key_moments'): self.supabase.table('video_key_moments').insert([{'video_id': video_id, **m} for m in analysis['key_moments'][:30]]).execute()

        await self._update_job(job_id, video_id, 'generating_thumbnails', 70, 'Generating AI thumbnails')
        thumb_dir = os.path.join(self.settings.temp_dir, f'thumbs/{video_id}')
        thumbnails = await self.thumbnail_gen.generate_all(title, analysis.get('summary', ''), thumb_dir)
        async with httpx.AsyncClient(timeout=60.0) as http_client:
            for thumb in thumbnails:
                if 'local_path' not in thumb: continue
                try:
                    with open(thumb['local_path'], 'rb') as f: img_bytes = f.read()
                    sp = f'{user_id}/{video_id}/thumbnails/{thumb["style"]}.png'
                    self.supabase.storage.from_('thumbnails').upload(sp, img_bytes, {'Content-Type': 'image/png'})
                    purl = self.supabase.storage.from_('thumbnails').get_public_url(sp)
                    self.supabase.table('thumbnails').insert({'video_id': video_id, 'user_id': user_id, 'style': thumb['style'], 'storage_path': sp, 'public_url': purl, 'model_used': self.settings.image_model}).execute()
                except Exception as e:
                    logger.error('Failed to store thumbnail', style=thumb['style'], error=str(e))

        await self._update_job(job_id, video_id, 'indexing', 85, 'Indexing for AI search')
        segs = transcription['segments']
        chunks = [{'text': ' '.join(s['text'] for s in segs[i:i+5]), 'start_time': segs[i]['start'], 'end_time': segs[min(i+4, len(segs)-1)]['end'], 'chunk_index': i // 5} for i in range(0, len(segs), 5)]
        embeddings = await self.analyzer.create_embeddings([c['text'] for c in chunks])
        embedding_data = [{'video_id': video_id, 'user_id': user_id, 'chunk_text': chunks[i]['text'], 'chunk_index': chunks[i]['chunk_index'], 'start_time': chunks[i]['start_time'], 'end_time': chunks[i]['end_time'], 'embedding': embeddings[i], 'model_used': self.settings.embedding_model} for i in range(len(chunks))]
        for i in range(0, len(embedding_data), 100):
            self.supabase.table('video_embeddings').insert(embedding_data[i:i+100]).execute()

        await self._update_job(job_id, video_id, 'completed', 100, 'Processing complete')
        self.supabase.table('processing_jobs').update({'completed_at': 'now()'}).eq('id', job_id).execute()
        for path in [video_path, audio_path]:
            if path and os.path.exists(path):
                try: os.remove(path)
                except OSError: pass
        logger.info('Job completed', job_id=job_id, video_id=video_id)
