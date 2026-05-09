"""
Service Module 2 — Privacy Policy Auditor

Responsibility: Score and summarise data-collection risk in privacy policies.
Input : raw privacy policy / ToS text (str)
Output: dict with keys: score (A-F), score_explanation, findings (list), verdict
"""

from .llm import call_llm, parse_json

_PROMPT = """
Analyze the following privacy policy or Terms of Service document.

Assign a Privacy Score from A (best) to F (worst) based on:
- Data collected (volume & sensitivity)
- Third-party sharing practices
- User profiling / tracking
- User rights & data deletion options
- Transparency of language

Return ONLY a JSON object with this exact structure:
{{
  "score": "A" | "B" | "C" | "D" | "F",
  "score_explanation": "<one sentence explaining what this grade means>",
  "verdict": "<2-sentence plain-English overall assessment>",
  "findings": [
    {{
      "category":    "<e.g. Data Collection, Third-Party Sharing, User Rights>",
      "severity":    "Critical" | "Important" | "FYI",
      "description": "<plain English explanation of this finding>",
      "excerpt":     "<verbatim short quote from the policy, max 30 words>"
    }}
  ]
}}

POLICY TEXT (first 6000 chars):
{text}
"""


def audit_privacy(text: str) -> dict:
    """Return structured privacy risk assessment."""
    prompt = _PROMPT.format(text=text[:6000])
    raw    = call_llm(prompt, max_tokens=3000)
    result = parse_json(raw)

    if "error" in result:
        return result
    result.setdefault("score", "?")
    result.setdefault("score_explanation", "")
    result.setdefault("verdict", "")
    result.setdefault("findings", [])
    return result
