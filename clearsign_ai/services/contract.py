"""
Service Module 1 — Legal Contract Scanner

Responsibility: Detect and classify risky clauses in contracts.
Input : raw contract text (str)
Output: dict with keys: summary, clauses (list), overall_risk
"""

from .llm import call_llm, parse_json

_PROMPT = """
Analyze the following legal contract and identify every clause that poses a risk
to the signing party (e.g. freelancer, employee, service provider).

Return ONLY a JSON object with this exact structure:
{{
  "overall_risk": "High" | "Medium" | "Low",
  "summary": "<2-3 sentence plain English overview of the contract's risk profile>",
  "clauses": [
    {{
      "title":       "<short clause name>",
      "severity":    "High" | "Medium" | "Low",
      "excerpt":     "<verbatim short excerpt from the contract, max 40 words>",
      "explanation": "<plain English explanation of why this is risky>",
      "negotiation_tip": "<one concrete thing the signing party should try to negotiate>"
    }}
  ]
}}

If no risky clauses are found, return an empty clauses list and Low risk.

CONTRACT TEXT (first 6000 chars):
{text}
"""


def scan_contract(text: str) -> dict:
    """Return structured risk analysis of a contract."""
    prompt = _PROMPT.format(text=text[:6000])
    raw    = call_llm(prompt, max_tokens=4096)
    result = parse_json(raw)

    # Normalise so the frontend always gets consistent keys
    if "error" in result:
        return result
    result.setdefault("overall_risk", "Unknown")
    result.setdefault("summary", "")
    result.setdefault("clauses", [])
    return result
