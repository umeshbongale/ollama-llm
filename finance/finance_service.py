import os
import re
from services.llm_service import stream_llm


# ==============================
# LOAD FINANCE KNOWLEDGE BASE
# ==============================

BASE_DIR = os.path.dirname(__file__)
FILE_PATH = os.path.join(BASE_DIR, "finance_support.txt")

with open(FILE_PATH, "r", encoding="utf-8") as f:
    FINANCE_TEXT = f.read()

print("Finance Knowledge Base Loaded. Length:", len(FINANCE_TEXT))


# ==============================
# SPLIT INTO SENTENCES
# ==============================

def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 20]


finance_sentences = split_into_sentences(FINANCE_TEXT)


# ==============================
# NORMALIZATION
# ==============================

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text


# ==============================
# RETRIEVAL
# ==============================

def retrieve_relevant_context(question, top_k=1):

    question_clean = normalize_text(question)

    question_words = [
        w for w in question_clean.split()
        if len(w) > 3
    ]

    scored_sentences = []

    for sentence in finance_sentences:

        sentence_clean = normalize_text(sentence)
        score = 0

        for word in question_words:
            if word in sentence_clean:
                score += 1

        if score > 0:
            scored_sentences.append((score, sentence))

    scored_sentences.sort(reverse=True)

    if scored_sentences:
        best_sentences = [s[1] for s in scored_sentences[:top_k]]
        return " ".join(best_sentences)

    return None


# ==============================
# RESPONSE GENERATOR
# ==============================

def generate_finance_response(question: str):

    question = question.strip()

    if len(question) < 5:
        def ask_question():
            yield "Please ask your finance-related question clearly."
        return ask_question()

    context = retrieve_relevant_context(question)

    if not context:
        def not_found():
            yield "I cannot find this information in the Finance support knowledge base. Please contact finance@company.com."
        return not_found()

    prompt = f"""
You are a Finance Support Assistant.

STRICT RULES:
- Use ONLY the information provided below.
- Answer ONLY the specific question asked.
- Keep the answer short and precise.
- Maximum 5 bullet points.
- If information is not available, say:
"I cannot find this information in the Finance support knowledge base."

Finance Knowledge Base:
{context}

User Question:
{question}

Concise Answer:
"""

    return stream_llm(prompt)
