from fastapi import APIRouter, Request, Response
from core.config import VERIFY_TOKEN
from core.memory import update_memory, build_memory_prompt
from services.whatsapp_service import send_whatsapp_message
from services.order_service import handle_message
from services.llm_service import call_llm_once

router = APIRouter()

@router.get("/whatsapp")
async def verify_webhook(request: Request):
    params = request.query_params
    if params.get("hub.verify_token") == VERIFY_TOKEN:
        return Response(content=params.get("hub.challenge"), media_type="text/plain")
    return Response(status_code=403)


@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):

    data = await request.json()

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        user_number = message["from"]
        user_message = message["text"]["body"].strip()
    except:
        return {"status": "ignored"}

    session_id = user_number
    update_memory(session_id, "user", user_message)

    order_response = handle_message(session_id, user_message)

    if order_response:
        send_whatsapp_message(user_number, order_response)
        return {"status": "sent"}

    history = build_memory_prompt(session_id)

    prompt = f"""
You are a polite ecommerce sales assistant.

Conversation:
{history}

Customer:
{user_message}
"""

    reply = call_llm_once(prompt)
    update_memory(session_id, "assistant", reply)
    send_whatsapp_message(user_number, reply)

    return {"status": "sent"}
