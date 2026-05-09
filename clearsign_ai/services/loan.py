"""
Service Module 3 — Loan Agreement Analyzer

Responsibility: Extract financial terms and flag predatory conditions.
Input : loan agreement text (str)
Output: dict with keys: summary, terms (list), overall_flag
"""

from .llm import call_llm, parse_json

_PROMPT = """
Analyze the following loan agreement and extract every financial variable.

Compare each value against these benchmark ranges:
- APR (Annual Percentage Rate): Normal ≤ 20%, Elevated 20-36%, Predatory > 36%
- Late Fee: Normal ≤ $35 or ≤ 5% of payment, Elevated up to $50, Predatory > $50
- Prepayment Penalty: Normal = None, Elevated = <2% of balance, Predatory ≥ 2%
- Origination Fee: Normal ≤ 1%, Elevated 1-5%, Predatory > 5%
- Balloon Payment: Normal = None, Elevated = disclosed, Predatory = hidden
- Loan Term: flag if unusually short for the loan type

Return ONLY a JSON object with this exact structure:
{{
  "overall_flag": "Standard" | "Elevated" | "Predatory",
  "summary": "<2-sentence plain English overview of the loan's risk profile>",
  "terms": [
    {{
      "variable":   "<e.g. APR, Late Fee, Balloon Payment>",
      "value":      "<extracted value or 'Not specified'>",
      "benchmark":  "<what the normal range is>",
      "flag":       "Normal" | "Elevated" | "Predatory",
      "note":       "<one-sentence explanation>"
    }}
  ],
  "disclaimer": "Benchmark figures are based on general market data and may not reflect current regulatory limits in your jurisdiction."
}}

LOAN AGREEMENT TEXT (first 6000 chars):
{text}
"""


def analyze_loan(text: str) -> dict:
    """Return structured financial risk analysis of a loan agreement."""
    prompt = _PROMPT.format(text=text[:6000])
    raw    = call_llm(prompt, max_tokens=3000)
    result = parse_json(raw)

    if "error" in result:
        return result
    result.setdefault("overall_flag", "Unknown")
    result.setdefault("summary", "")
    result.setdefault("terms", [])
    result.setdefault("disclaimer", "")
    return result
