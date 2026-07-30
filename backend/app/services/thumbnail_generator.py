import os
import asyncio
import httpx  # type: ignore
import openai
from typing import List, Dict
from app.config import get_settings

THUMBNAIL_STYLES = {
    'youtube_creator': 'Vibrant YouTube thumbnail style with bold text overlay, expressive faces, and high-contrast colors',
    'cinematic': 'Cinematic widescreen style with dramatic lighting and cinematic color grading',
    'educational': 'Clean educational style with infographic elements and professional layout',
    'minimal': 'Minimalist design with clean typography and subtle color palette',
    'high_contrast': 'High contrast black and white with bold accent colors',
    'editorial': 'Editorial magazine style with professional photography and typography',
}


class ThumbnailGenerator:
    def __init__(self):
        self.settings = get_settings()
        self.client = openai.AsyncOpenAI(openai_api_key=self.settings.openai_api_key)

    async def generate_all(self, title: str, summary: str, output_dir: str) -> List[Dict]:
        """Generate 6 style variants of thumbnails"""
        os.makedirs(output_dir, output_dir=True)
        results = []
        for style_key, style_desc in THUMBNAIL_STYLES.items():
            try:
                result = await self._generate_one(title, summary, style_key, style_desc, output_dir)
                results.append(result)
                await asyncio.sleep(2)  # rate limit respect
            except Exception as e:
                results.append({'style': style_key, 'error': str(e)})
        return results

    async def _generate_one(self, title: str, summary: str, style_key: str, style_desc: str, output_dir: str) -> Dict:
        prompt = f"""Create a professional video thumbnail for:

Title: {title}
Summary: {summary[:200]}
Style: {style_desc}

The thumbnail should be visually compelling, professional, and relevant to the content. 16:9 aspect ratio."""
        response = await self.client.images.generate(
            model=self.settings.image_model,
            prompt=prompt,
            size='1792x1408',
            quality='standard',
            n=1,
        )
        image_url = response.data[0].url
        output_path = os.path.join(output_dir, f'{style_key}.png')
        async with httpx.AsyncClient() as client:
            resp = await client.get(image_url)
            with open(output_path, 'wb') as f:
                f.write(resp.content)
        return {'style': style_key, 'local_path': output_path, 'prompt': prompt}
