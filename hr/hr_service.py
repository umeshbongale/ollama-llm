import os
import re
from services.llm_service import stream_llm

# ==============================
# LOAD POLICY
# ==============================

BASE_DIR = os.path.dirname(__file__)
POLICY_PATH = os.path.join(BASE_DIR, "hr_policy.txt")

with open(POLICY_PATH, "r", encoding="utf-8") as f:
    POLICY_TEXT = f.read()


# ==============================
# SPLIT INTO PARAGRAPHS
# ==============================

def split_into_paragraphs(text):
    paragraphs = re.split(r"\n\s*\n", text)
    return [p.strip() for p in paragraphs if len(p.strip()) > 50]


policy_paragraphs = split_into_paragraphs(POLICY_TEXT)


# ==============================
# SMART KEYWORD SCORING
# ==============================

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text


def retrieve_relevant_context(question, top_k=3):

    question_clean = normalize_text(question)
    question_words = set(question_clean.split())

    scored_paragraphs = []

    for paragraph in policy_paragraphs:

        paragraph_clean = normalize_text(paragraph)
        paragraph_words = set(paragraph_clean.split())

        # Score based on overlap
        common_words = question_words.intersection(paragraph_words)
        score = len(common_words)

        if score > 0:
            scored_paragraphs.append((score, paragraph))

    scored_paragraphs.sort(reverse=True)

    if not scored_paragraphs:
        return None

    return "\n\n".join([p[1] for p in scored_paragraphs[:top_k]])



# ==============================
# RESPONSE GENERATOR
# ==============================

def generate_hr_response(question: str):

    question = question.strip()

    if len(question) < 5:
        def ask_question():
            yield "Please ask your HR-related question clearly so I can assist you."
        return ask_question()

    context = retrieve_relevant_context(question)

    if not context:
        def not_found():
            yield "I cannot find this information in the HR policy document."
        return not_found()

    prompt = f"""
You are an HR policy assistant.

STRICT RULES:
- Use ONLY the information from the HR Policy Context below.
- Do NOT add outside knowledge.
- If the answer is not clearly stated in context, say:
"I cannot find this information in the HR policy document."
- Answer clearly and professionally.

HR Policy Context:
{context}

Employee Question:
{question}

Answer:
"""

    return stream_llm(prompt)
