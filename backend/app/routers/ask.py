"""RAG Ask router — embedding search + GPT-4o answer with timestamp citations."""

import json
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from app.models import AskRequest, AskResponse, Citation

router = APIRouter(prefix="/ask", tags=["ask"])
logger = logging.getLogger(__name__)

RAG_SYSTEM_PROMPT = """You are an AI assistant that answers questions about video content based on the transcript.

Rules:
1. Only use information from the provided context (transcript segments and analysis)
2. If the answer is not in the provided context, say: "I couldn't find enough evidence in this video to answer that confidently."
3. When referencing specific parts, include the timestamp in [MM:SS] format
4. Be concise but thorough
5. If multiple parts of the video are relevant, cite all of them
6. Do not make up information not present in the context"""


@router.post("/query", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """Answer a question about a video using RAG.

    Pipeline:
    1. Embed the question using text-embedding-3-small
    2. Search pgvector for similar transcript chunks
    3. Build context from top-k chunks + video analysis
    4. Generate answer with GPT-4o
    5. Return answer with timestamp citations
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # The actual RAG implementation is in the embedding_service
    # This endpoint defines the API contract
    return {
        "answer": "RAG query received. The embedding service will process this request.",
        "citations": [],
        "conversation_id": request.conversation_id or "",
        "video_id": request.video_id,
        "message": "Use the embedding_service.search_and_answer() method for full RAG implementation.",
    }


@router.get("/conversations/{video_id}")
async def get_conversations(video_id: str, user_id: str):
    """Get all conversations for a video."""
    return {
        "video_id": video_id,
        "user_id": user_id,
        "message": "Conversations are stored in Supabase. Query the 'conversations' and 'messages' tables.",
    }


@router.get("/conversation/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: str):
    """Get all messages in a conversation."""
    return {
        "conversation_id": conversation_id,
        "message": "Messages are stored in Supabase. Query the 'messages' table filtered by conversation_id.",
    }
