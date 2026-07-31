"""
Thumbnail generation service using DALL-E 3
Generates 6 style variants for each video
"""

import asyncio
from typing import List, Optional
import structlog
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings

logger = structlog.get_logger()

THUMBNAIL_STYLES = {
    "youtube_creator": {"description": "YouTube creator style thumbnail", "prompt_template": "Professional YouTube thumbnail for a video titled '{title}'. Bold text overlay, vibrant colors, high contrast, dramatic lighting, eye-catching composition. Topic: {topic}. Style: modern YouTube creator aesthetic, 16:9 ratio."},
    "cinematic": {"description": "Cinematic film poster style", "prompt_template": "Cinematic movie poster style thumbnail for '{title}'. Dramatic lighting, deep shadows, rich colors, professional photography aesthetic. Topic: {topic}. Widescreen cinematic composition."},
    "educational": {"description": "Clean educational/academic style", "prompt_template": "Clean educational thumbnail for a learning video about '{title}'. Professional, academic aesthetic with clear visual hierarchy. Topic: {topic}. Clean background, informative icons or diagrams."},
    "minimal": {"description": "Minimalist design", "prompt_template": "Minimalist thumbnail design for '{title}'. Clean white or dark background, simple typography, elegant design. Topic: {topic}. Less is more aesthetic, sophisticated and modern."},
    "high_contrast": {"description": "High contrast bold design", "prompt_template": "High contrast, bold thumbnail for '{title}'. Strong black and white contrast with one accent color. Topic: {topic}. Graphic design style, impactful visual."},
    "editorial": {"description": "Editorial magazine style", "prompt_template": "Editorial magazine-style thumbnail for '{title}'. Professional journalism aesthetic, clean layout, authoritative feel. Topic: {topic}. News magazine or documentary style."},
}


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=10, max=120))
async def generate_thumbnail(client: AsyncOpenAI, style: str, title: str, topic: str, video_id: str) -> dict:
    settings = get_settings()
    style_config = THUMBNAIL_STYLES[style]
    prompt = style_config["prompt_template"].format(title=title, topic=topic)
    response = await client.images.generate(model=settings.image_model, prompt=prompt, size="1792x1024", quality="hd", n=1)
    image_url = response.data[0].url
    revised_prompt = response.data[0].revised_prompt
    logger.info("Thumbnail generated", video_id=video_id, style=style)
    return {"style": style, "url": image_url, "prompt_used": revised_prompt or prompt, "width": 1792, "height": 1024}


async def generate_all_thumbnails(title: str, summary: str, topics: List[str], video_id: str) -> List[dict]:
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    topic = ", ".join(topics[:3]) if topics else title
    results = []
    for style in THUMBNAIL_STYLES.keys():
        try:
            result = await generate_thumbnail(client, style, title, topic, video_id)
            results.append(result)
            await asyncio.sleep(2)
        except Exception as e:
            logger.error("Thumbnail generation failed", style=style, video_id=video_id, error=str(e))
    logger.info("All thumbnails generated", video_id=video_id, count=len(results))
    return results
