"""
Service Module 5 — Commercial Lease QA Chat

Responsibility: Answer natural language questions about a lease document.
Input : lease text (str) + user question (str)
Output: str (plain text answer with clause citations)

Design note:
  - load_lease_text() validates and returns a word/char summary (stateless).
  - ask_lease_question() receives the full lease text + question every call.
    The application layer (app.py) is responsible for persisting the lease text
    between requests (stored in _lease_store). This keeps the service layer
    stateless and independently testable.
"""

from .llm import call_llm_text

_LOAD_MSG = "Lease loaded: {words:,} words, {chars:,} characters. Ask your questions."

_QA_PROMPT = """
You are an expert tenancy lawyer reviewing a lease document on behalf of the tenant.

Answer the following question based ONLY on the lease document provided.
- Start with a clear, direct one-sentence answer.
- Then provide supporting detail, citing the relevant clause or section.
- If there is a risk to the tenant, add a "⚠️ Watch Out:" note.
- Keep the total response under 300 words.
- If the question cannot be answered from the document, say so clearly.

LEASE DOCUMENT:
{lease_text}

TENANT'S QUESTION: {question}
"""


def load_lease_text(text: str) -> str:
    """Validate lease text and return a human-readable summary string."""
    words = len(text.split())
    chars = len(text)
    if words < 20:
        return "⚠️ Document too short to analyse. Please provide the full lease text."
    return _LOAD_MSG.format(words=words, chars=chars)


def ask_lease_question(lease_text: str, question: str) -> str:
    """Answer a tenant's question from the lease document context."""
    prompt = _QA_PROMPT.format(
        lease_text=lease_text[:8000],
        question=question,
    )
    return call_llm_text(prompt, max_tokens=600)
