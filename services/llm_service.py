import requests
import json
import logging
from core.config import OLLAMA_URL, MODEL_NAME

# -----------------------------------
# Logger Configuration
# -----------------------------------

logger = logging.getLogger("llm_service")

# -----------------------------------
# NON-STREAMING CALL (With Token Logs)
# -----------------------------------

def call_llm_once(prompt: str, session_id: str | None = None) -> str:
    """
    Calls Ollama once (non-streaming) and logs token usage.
    """

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.4}
            },
            timeout=300
        )

        response.raise_for_status()
        data = response.json()

        output_text = data.get("response", "")

        # Token metrics from Ollama
        input_tokens = data.get("prompt_eval_count", 0)
        output_tokens = data.get("eval_count", 0)
        total_tokens = input_tokens + output_tokens

        logger.info(
            f"[LLM USAGE] session={session_id} | "
            f"input_tokens={input_tokens} | "
            f"output_tokens={output_tokens} | "
            f"total_tokens={total_tokens}"
        )

        return output_text

    except Exception as e:
        logger.error(f"[LLM ERROR] session={session_id} | error={str(e)}")
        return "⚠️ Sorry, something went wrong while processing your request."


# -----------------------------------
# STREAMING CALL (With Token Logs)
# -----------------------------------

def stream_llm(prompt: str, session_id: str | None = None):
    """
    Streams response from Ollama and logs token usage
    once the stream is completed.
    """

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": True,
                "options": {"temperature": 0.4}
            },
            stream=True,
            timeout=300
        )

        response.raise_for_status()

        input_tokens = 0
        output_tokens = 0

        for line in response.iter_lines():
            if not line:
                continue

            try:
                data = json.loads(line.decode("utf-8"))

                # Yield streamed response
                chunk = data.get("response", "")
                if chunk:
                    yield chunk

                # Final message contains token usage
                if data.get("done"):
                    input_tokens = data.get("prompt_eval_count", 0)
                    output_tokens = data.get("eval_count", 0)

            except json.JSONDecodeError:
                continue

        total_tokens = input_tokens + output_tokens

        logger.info(
            f"[LLM STREAM USAGE] session={session_id} | "
            f"input_tokens={input_tokens} | "
            f"output_tokens={output_tokens} | "
            f"total_tokens={total_tokens}"
        )

    except Exception as e:
        logger.error(f"[LLM STREAM ERROR] session={session_id} | error={str(e)}")
        yield "⚠️ Streaming error occurred."
