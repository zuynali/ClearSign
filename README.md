# ClearSign
clearsign_ai/
├── app.py              ← Flask routes (Application Layer)
├── services/
│   ├── llm.py          ← Groq API + PyMuPDF (Infrastructure)
│   ├── contract.py     ← Module 1
│   ├── privacy.py      ← Module 2
│   ├── loan.py         ← Module 3
│   ├── medical.py      ← Module 4
│   └── lease_qa.py     ← Module 5
├── templates/index.html ← Full SPA UI
└── static/css + js     ← Styling and frontend logic
