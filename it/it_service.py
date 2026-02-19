import os
import re
from services.llm_service import stream_llm


# ==============================
# LOAD IT SUPPORT KNOWLEDGE BASE
# ==============================

BASE_DIR = os.path.dirname(__file__)
IT_PATH = os.path.join(BASE_DIR, "it_support.txt")

with open(IT_PATH, "r", encoding="utf-8") as f:
    IT_TEXT = f.read()

print("IT Knowledge Base Loaded. Length:", len(IT_TEXT))
print("IT FILE PATH:", IT_PATH)
print("FIRST 300 CHARS:")
print(IT_TEXT[:300])

# ==============================
# SPLIT INTO SENTENCES (ROBUST)
# ==============================

def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 20]


it_sentences = split_into_sentences(IT_TEXT)

print("Total IT Sentences:", len(it_sentences))


# ==============================
# NORMALIZATION
# ==============================

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text


# ==============================
# STRONG RETRIEVAL LOGIC
# ==============================

def retrieve_relevant_context(question, top_k=3):

    question_clean = normalize_text(question)

    # remove very small words
    question_words = [
        w for w in question_clean.split()
        if len(w) > 3
    ]

    scored_sentences = []

    for sentence in it_sentences:

        sentence_clean = normalize_text(sentence)
        score = 0

        # substring matching (stronger than exact match)
        for word in question_words:
            if word in sentence_clean:
                score += 1

        if score > 0:
            scored_sentences.append((score, sentence))

    scored_sentences.sort(reverse=True)

    # If matches found → return best matches
    if scored_sentences:
        best_sentences = [s[1] for s in scored_sentences[:top_k]]
        return " ".join(best_sentences)

    return None


# ==============================
# RESPONSE GENERATOR
# ==============================

def generate_it_response(question: str):

    question = question.strip()

    if len(question) < 5:
        def ask_question():
            yield "Please describe your IT issue clearly so I can assist you."
        return ask_question()

    context = retrieve_relevant_context(question)

    if not context:
        def not_found():
            yield "I cannot find this information in the IT support knowledge base. Please contact support@abc.com."
        return not_found()

    prompt = f"""
You are an IT Support Assistant.

STRICT RULES:
- Use ONLY the information provided below.
- Answer ONLY the specific question asked.
- Do NOT include extra issues or unrelated troubleshooting steps.
- Keep the answer short and precise.
- Maximum 5 bullet points.
- Be professional and concise.
- If information is not available, say:
"I cannot find this information in the IT support knowledge base."

IT Support Knowledge Base:
{context}

User Issue:
{question}

Response:
"""

    return stream_llm(prompt)
