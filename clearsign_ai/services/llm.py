"""
Infrastructure Layer — LLM and PDF utilities.

All service modules depend on this; nothing in this file depends on Flask.
Changing the LLM provider (Groq → OpenAI) only requires editing this file.
"""

import os
import re
import json
import fitz  # PyMuPDF
from groq import Groq

# ── API client (key from env var or fallback) ──────────────────────────────────
# _API_KEY = os.environ.get("GROQ_API_KEY")

api_key = os.environ.get("GROQ_API_KEY")

_client = Groq(api_key=_API_KEY)
_MODEL  = "llama-3.3-70b-versatile"


# ── Public API ─────────────────────────────────────────────────────────────────

def call_llm(prompt: str, max_tokens: int = 4096, json_mode: bool = True) -> str:
    """
    Send a prompt to the LLM and return the raw response string.

    Parameters
    ----------
    prompt     : user prompt
    max_tokens : maximum tokens in the completion
    json_mode  : if True, system message instructs model to output only JSON
    """
    system_msg = (
        "You are a precise JSON-generation engine. "
        "You ALWAYS respond with syntactically valid JSON and NOTHING else — "
        "no markdown fences, no preamble, no trailing commentary."
        if json_mode
        else "You are a helpful legal and financial document analysis assistant."
    )
    try:
        response = _client.chat.completions.create(
            model=_MODEL,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user",   "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.2,
        )
        return response.choices[0].message.content
    except Exception as exc:
        return json.dumps({"error": str(exc)})


def call_llm_text(prompt: str, max_tokens: int = 1024) -> str:
    """Call LLM in plain-text mode (not JSON)."""
    return call_llm(prompt, max_tokens=max_tokens, json_mode=False)


def extract_pdf_text(pdf_bytes: bytes) -> str:
    """Extract plain text from a PDF byte string using PyMuPDF."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        return "\n".join(page.get_text() for page in doc).strip()
    except Exception as exc:
        return f"[PDF extraction error: {exc}]"


def parse_json(raw: str) -> dict | list:
    """Strip markdown fences and parse JSON; return dict with 'error' on failure."""
    clean = re.sub(r"```(?:json)?|```", "", raw).strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError as exc:
        return {"error": f"JSON parse error: {exc}", "raw": raw}
