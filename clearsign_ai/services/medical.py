"""
Service Module 4 — Medical Consent Form Simplifier

Responsibility: Translate medical-legal jargon into plain English.
Input : medical consent form text (str)
Output: dict with keys: simplified_sections, flagged_terms, disclaimer
"""

from .llm import call_llm, parse_json

_PROMPT = """
You are a medical-legal plain-language translator.
Analyze the following medical consent form.

For each major section or paragraph, produce a simplified version at a 6th-grade
reading level. Also identify any specialized drug names or procedures that the
patient should specifically clarify with their doctor.

Return ONLY a JSON object with this exact structure:
{{
  "overall_readability": "Simple" | "Moderate" | "Complex",
  "sections": [
    {{
      "original":   "<exact excerpt from the form, max 60 words>",
      "simplified": "<plain English translation — what this means for you>",
      "risk_flag":  true | false,
      "risk_note":  "<if risk_flag is true: what specifically to watch for, else null>"
    }}
  ],
  "flagged_terms": [
    {{
      "term":        "<medical or legal term>",
      "explanation": "<plain English explanation>"
    }}
  ],
  "disclaimer": "This simplification is for informational purposes only. Consult your doctor before signing any medical consent form."
}}

CONSENT FORM TEXT (first 5000 chars):
{text}
"""


def simplify_medical(text: str) -> dict:
    """Return plain-English translation of a medical consent form."""
    prompt = _PROMPT.format(text=text[:5000])
    raw    = call_llm(prompt, max_tokens=4096)
    result = parse_json(raw)

    if "error" in result:
        return result
    result.setdefault("overall_readability", "Unknown")
    result.setdefault("sections", [])
    result.setdefault("flagged_terms", [])
    result.setdefault("disclaimer", "")
    return result
