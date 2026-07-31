"""Embedding service — text-embedding-3-small + pgvector storage and search."""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


class EmbeddingService:
    """Service for generating embeddings and performing pgvector similarity search."""

    def __init__(self, openai_api_key: str, supabase_url: str, supabase_service_key: str):
        self.openai_api_key = openai_api_key
        self.supabase_url = supabase_url
        self.supabase_service_key = supabase_service_key
        self._openai_client = None
        self._supabase_client = None
        self.embedding_model = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
        self.embedding_dimensions = 1536

    @property
    def openai_client(self):
        if self._openai_client is None:
            from openai import OpenAI
            self._openai_client = OpenAI(api_key=self.openai_api_key)
        return self._openai_client

    @property
    def supabase_client(self):
        if self._supabase_client is None:
            from supabase import create_client
            self._supabase_client = create_client(self.supabase_url, self.supabase_service_key)
        return self._supabase_client

    def chunk_transcript(self, segments: list[dict]) -> list[dict]:
        chunks = []
        current_text = ""
        current_start = 0.0
        current_end = 0.0
        chunk_index = 0

        for seg in segments:
            seg_text = seg.get("text", "").strip()
            if not seg_text:
                continue
            if not current_text:
                current_start = seg.get("start", 0)
            if len(current_text) + len(seg_text) > CHUNK_SIZE and current_text:
                chunks.append({"start_time": current_start, "end_time": current_end, "text": current_text.strip(), "chunk_index": chunk_index})
                chunk_index += 1
                overlap_text = current_text[-CHUNK_OVERLAP:] if len(current_text) > CHUNK_OVERLAP else current_text
                current_text = overlap_text + " " + seg_text
                current_start = seg.get("start", 0)
            else:
                current_text = (current_text + " " + seg_text).strip()
            current_end = seg.get("end", 0)

        if current_text.strip():
            chunks.append({"start_time": current_start, "end_time": current_end, "text": current_text.strip(), "chunk_index": chunk_index})
        return chunks

    def generate_embedding(self, text: str) -> list[float]:
        if not text.strip():
            return []
        response = self.openai_client.embeddings.create(model=self.embedding_model, input=text)
        return response.data[0].embedding

    def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = self.openai_client.embeddings.create(model=self.embedding_model, input=texts)
        return [item.embedding for item in response.data]

    def store_embeddings(self, video_id: str, chunks: list[dict], embeddings: list[list[float]]) -> int:
        rows = []
        for chunk, embedding in zip(chunks, embeddings):
            rows.append({"video_id": video_id, "chunk_index": chunk["chunk_index"], "content": chunk["text"], "start_time": chunk["start_time"], "end_time": chunk["end_time"], "embedding": str(embedding)})
        result = self.supabase_client.table("video_embeddings").insert(rows).execute()
        return len(rows)

    def search_similar(self, video_id: str, query_embedding: list[float], top_k: int = 5, similarity_threshold: float = 0.7) -> list[dict]:
        result = self.supabase_client.rpc("match_embeddings", {"query_embedding": str(query_embedding), "match_count": top_k, "filter_video_id": video_id, "similarity_threshold": similarity_threshold}).execute()
        return result.data if hasattr(result, "data") else []

    def search_and_answer(self, video_id: str, question: str, analysis_context: str = "", conversation_history: list[dict] = None) -> dict:
        query_embedding = self.generate_embedding(question)
        similar_chunks = self.search_similar(video_id, query_embedding, top_k=5)
        if not similar_chunks:
            return {"answer": "I couldn't find enough evidence in this video to answer that confidently.", "citations": [], "conversation_id": None}
        context_parts = []
        citations = []
        for chunk in similar_chunks:
            context_parts.append(f"[{self._format_timestamp(chunk['start_time'])}] {chunk['content']}")
            citations.append({"timestamp": chunk["start_time"], "text": chunk["content"][:200], "segment_id": chunk.get("chunk_index")})
        context = "\n\n".join(context_parts)
        if analysis_context:
            context = f"Video Analysis Summary:\n{analysis_context}\n\nRelevant Transcript Segments:\n{context}"
        messages = [{"role": "system", "content": RAG_SYSTEM_PROMPT}]
        if conversation_history:
            messages.extend(conversation_history[-6:])
        messages.append({"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"})
        response = self.openai_client.chat.completions.create(model=os.environ.get("AI_MODEL", "gpt-4o"), messages=messages, temperature=0.3, max_tokens=1000)
        answer = response.choices[0].message.content
        return {"answer": answer, "citations": citations, "conversation_id": None}

    def _format_timestamp(self, seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"


RAG_SYSTEM_PROMPT = """You are an AI assistant that answers questions about video content based on the transcript.

Rules:
1. Only use information from the provided context (transcript segments and analysis)
2. If the answer is not in the provided context, say: "I couldn't find enough evidence in this video to answer that confidently."
3. When referencing specific parts, include the timestamp in [MM:SS] format
4. Be concise but thorough
5. If multiple parts of the video are relevant, cite all of them
6. Do not make up information not present in the context"""
