from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uuid

from core.memory import update_memory, build_memory_prompt
from services.llm_service import stream_llm
from services.order_service import (
    handle_message,
    retrieve_relevant_products
)

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


@router.post("/ask")
async def ask(chat: ChatRequest):

    # ==============================
    # SESSION INIT
    # ==============================
    if not chat.session_id:
        chat.session_id = str(uuid.uuid4())

    session_id = chat.session_id
    user_message = chat.message.strip()

    update_memory(session_id, "user", user_message)

    # ==============================
    # HANDLE STRUCTURED ORDER FLOW
    # ==============================
    order_response = handle_message(session_id, user_message)

    if order_response:
        return {"response": order_response}

    # ==============================
    # PRODUCT RETRIEVAL FOR RAG
    # ==============================
    products = retrieve_relevant_products(user_message)

    product_context = ""

    if products:
        for p in products[:3]:  # limit to top 3
            product_context += f"""
Product Name: {p[0]}
Price: ₹{p[1]}
Features: {p[2]}
-----------------
"""

    # ==============================
    # BUILD PROMPT
    # ==============================
    history = build_memory_prompt(session_id)

    prompt = f"""
You are a smart ecommerce sales assistant.

Available Products:
{product_context}

Conversation:
{history}

Customer:
{user_message}

Rules:
- Only recommend from available products.
- Do NOT invent products.
- Be specific about price and features.
- Keep the response short and helpful.
"""

    # ==============================
    # STREAM RESPONSE
    # ==============================
    def generator():
        full = ""
        for chunk in stream_llm(prompt):
            full += chunk
            yield chunk
        update_memory(session_id, "assistant", full)

    return StreamingResponse(generator(), media_type="text/plain")
