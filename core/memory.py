from core.config import MAX_MEMORY

conversation_memory = {}

def update_memory(session_id, role, message):
    if session_id not in conversation_memory:
        conversation_memory[session_id] = []

    conversation_memory[session_id].append({
        "role": role,
        "message": message
    })

    conversation_memory[session_id] = conversation_memory[session_id][-MAX_MEMORY:]


def build_memory_prompt(session_id):
    history = ""
    for msg in conversation_memory.get(session_id, []):
        history += f"{msg['role'].upper()}: {msg['message']}\n"
    return history
