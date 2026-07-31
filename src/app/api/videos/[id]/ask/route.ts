import { NextRequest, NextResponse } from "next/server"
import { createClient } from "@/lib/supabase/server"

export async function POST(request: NextRequest) {
  try {
    const supabase = createClient()

    const { data: { user } } = await supabase.auth.getUser()
    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const body = await request.json()
    const { video_id, question, conversation_id } = body

    if (!video_id || !question) {
      return NextResponse.json(
        { error: "video_id and question are required" },
        { status: 400 }
      )
    }

    const { data: video } = await supabase
      .from("videos")
      .select("id, title")
      .eq("id", video_id)
      .eq("user_id", user.id)
      .single()

    if (!video) {
      return NextResponse.json({ error: "Video not found" }, { status: 404 })
    }

    const fastapiUrl = process.env.FASTAPI_URL || "http://localhost:8000"

    const response = await fetch(`${fastapiUrl}/ask/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ video_id, question, conversation_id }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to get answer from AI")
    }

    const data = await response.json()

    let convId = conversation_id
    if (!convId) {
      const { data: conv } = await supabase
        .from("conversations")
        .insert({ video_id, user_id: user.id, title: question.slice(0, 100) })
        .select("id")
        .single()
      convId = conv?.id
    }

    if (convId) {
      await supabase.from("messages").insert([
        { conversation_id: convId, role: "user", content: question },
        { conversation_id: convId, role: "assistant", content: data.answer, metadata: { citations: data.citations } },
      ])
    }

    return NextResponse.json({
      answer: data.answer,
      citations: data.citations || [],
      conversation_id: convId,
    })
  } catch (error) {
    console.error("Ask API error:", error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to process question" },
      { status: 500 }
    )
  }
}