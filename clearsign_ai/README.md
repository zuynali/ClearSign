# ClearSign AI — Full Development Application

**Assignment 3 | Software Engineering | FAST NUCES Lahore**
**Syed Zain Ali (BSCS24115) | Mubeen Butt (BSCS24063)**

---

## Project Overview
ClearSign AI is an AI-powered legal and financial document risk analysis platform.
It uses the Groq LLaMA 3.3 70B model to analyze contracts, privacy policies,
loan agreements, medical consent forms, and lease documents.

---

## Architecture: Layered

```
┌──────────────────────────────────────┐
│  Presentation Layer                  │  HTML / CSS / JavaScript (static/)
│  templates/index.html + static/      │
└──────────────────────┬───────────────┘
                       │ HTTP (fetch API)
┌──────────────────────▼───────────────┐
│  Application Layer                   │  Flask routes (app.py)
│  app.py — REST endpoints             │  Input validation, request routing
└──────────────────────┬───────────────┘
                       │ Python function calls
┌──────────────────────▼───────────────┐
│  Service Layer                       │  services/*.py — one file per module
│  contract, privacy, loan,            │  Pure Python, framework-agnostic,
│  medical, lease_qa                   │  independently testable
└──────────────────────┬───────────────┘
                       │ HTTP (Groq SDK)
┌──────────────────────▼───────────────┐
│  Infrastructure Layer                │  services/llm.py
│  Groq API wrapper + PyMuPDF          │  All external I/O in one place
└──────────────────────────────────────┘
```

---

## Setup and Running

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) Set your Groq API key as environment variable
export GROQ_API_KEY=your_key_here

# 3. Run the Flask development server
python app.py

# 4. Open in browser
http://localhost:5000
```

---

## Project Structure

```
clearsign_ai/
├── app.py                  # Flask app + REST endpoints (Application Layer)
├── requirements.txt
├── README.md
├── services/
│   ├── __init__.py
│   ├── llm.py             # Groq API wrapper + PDF extractor (Infrastructure)
│   ├── contract.py        # Legal Contract Scanner
│   ├── privacy.py         # Privacy Policy Auditor
│   ├── loan.py            # Loan Agreement Analyzer
│   ├── medical.py         # Medical Consent Simplifier
│   └── lease_qa.py        # Lease QA Chat
├── templates/
│   └── index.html         # SPA shell (Jinja2 template)
└── static/
    ├── css/style.css      # All styles (Presentation Layer)
    └── js/app.js          # Frontend logic (Presentation Layer)
```

---

## API Endpoints

| Method | Endpoint              | Description                        |
|--------|-----------------------|------------------------------------|
| GET    | /                     | Serve the SPA                      |
| POST   | /api/scan-contract    | Analyze a legal contract           |
| POST   | /api/audit-privacy    | Grade a privacy policy             |
| POST   | /api/analyze-loan     | Extract loan terms + benchmark     |
| POST   | /api/simplify-medical | Simplify medical consent form      |
| POST   | /api/load-lease       | Load a lease document into memory  |
| POST   | /api/ask-lease        | Answer a question about the lease  |

All endpoints accept `Content-Type: application/json` with `{"text": "..."}` body,
or `multipart/form-data` with `pdf` file field + optional `text` field.
