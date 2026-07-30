import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import jobs, health
from app.workers.job_processor import JobProcessor


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    os.makedirs(settings.temp_dir, exist_ok=True)
    os.makedirs(f'{settings.temp_dir}/audio', exist_ok=True)
    os.makedirs(f'{settings.temp_dir}/frames', exist_ok=True)
    os.makedirs(f'{settings.temp_dir}/downloads', exist_ok=True)
    processor = JobProcessor()
    task = asyncio.create_task(processor.run_forever())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(title='Videology AI Backend', version='1.0.0', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:3000', os.getenv('NEXT_PUBLIC_APP_URL', '')], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.include_router(health.router, prefix='/health', tags=['health'])
app.include_router(jobs.router, prefix='/jobs', tags=['jobs'])


def verify_api_key(x_api_key: str = Header(...)):
    settings = get_settings()
    if x_api_key != settings.backend_api_key:
        raise HTTPException(status_code=401, detail='Invalid API key')
    return x_api_key


@app.get('/')
async def root():
    return {'service': 'Videology AI Backend', 'status': 'running', 'version': '1.0.0'}
