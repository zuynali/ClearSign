"""
ClearSign AI — Full Development Application
Assignment 3 | Syed Zain Ali (BSCS24115) | Mubeen Butt (BSCS24063)

Architecture: Layered
  Presentation  →  Flask Routes (Application Layer)
               →  Service Modules (Service Layer)
               →  Groq LLM API  (Infrastructure Layer)
"""

import os
from flask import Flask, render_template, request, jsonify

from services.llm         import call_llm, extract_pdf_text
from services.contract    import scan_contract
from services.privacy     import audit_privacy
from services.loan        import analyze_loan
from services.medical     import simplify_medical
from services.lease_qa    import load_lease_text, ask_lease_question

app = Flask(__name__)

# ── In-memory lease store (per-process; stateless for multi-worker use a cache) ──
_lease_store: dict[str, str] = {}


# ─────────────────────────────────────────────────────────
#  PRESENTATION LAYER — serve SPA shell
# ─────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


# ─────────────────────────────────────────────────────────
#  APPLICATION LAYER — REST endpoints
#  Each endpoint: validates → delegates to Service → returns JSON
# ─────────────────────────────────────────────────────────

@app.route("/api/scan-contract", methods=["POST"])
def api_scan_contract():
    text, err = _get_text(request)
    if err:
        return jsonify({"error": err}), 400
    result = scan_contract(text)
    return jsonify(result)


@app.route("/api/audit-privacy", methods=["POST"])
def api_audit_privacy():
    text, err = _get_text(request)
    if err:
        return jsonify({"error": err}), 400
    result = audit_privacy(text)
    return jsonify(result)


@app.route("/api/analyze-loan", methods=["POST"])
def api_analyze_loan():
    text, err = _get_text(request)
    if err:
        return jsonify({"error": err}), 400
    result = analyze_loan(text)
    return jsonify(result)


@app.route("/api/simplify-medical", methods=["POST"])
def api_simplify_medical():
    text, err = _get_text(request)
    if err:
        return jsonify({"error": err}), 400
    result = simplify_medical(text)
    return jsonify(result)


@app.route("/api/load-lease", methods=["POST"])
def api_load_lease():
    text, err = _get_text(request)
    if err:
        return jsonify({"error": err}), 400
    summary = load_lease_text(text)
    _lease_store["text"] = text
    return jsonify({"status": "ok", "summary": summary})


@app.route("/api/ask-lease", methods=["POST"])
def api_ask_lease():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "Question is required."}), 400
    lease_text = _lease_store.get("text", "")
    if not lease_text:
        return jsonify({"error": "No lease loaded. Please load a lease document first."}), 400
    answer = ask_lease_question(lease_text, question)
    return jsonify({"answer": answer})


# ─────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────

def _get_text(req) -> tuple[str, str | None]:
    """Extract document text from multipart or JSON request."""
    # multipart (PDF upload)
    if req.content_type and "multipart" in req.content_type:
        pdf_file = req.files.get("pdf")
        raw_text = (req.form.get("text") or "").strip()
        if pdf_file:
            pdf_bytes = pdf_file.read()
            text = extract_pdf_text(pdf_bytes)
        else:
            text = raw_text
    else:
        # JSON
        data = req.get_json(silent=True) or {}
        text = (data.get("text") or "").strip()

    if not text:
        return "", "No document text provided. Paste text or upload a PDF."
    return text, None


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)
