/**
 * ClearSign AI — Frontend Application Layer
 * Presentation logic only; no business rules here.
 * All processing is delegated to Flask API endpoints.
 */

"use strict";

// ══════════════════════════════════════════════════
//  TAB NAVIGATION
// ══════════════════════════════════════════════════
document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const target = btn.dataset.tab;
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`tab-${target}`).classList.add("active");
  });
});


// ══════════════════════════════════════════════════
//  UPLOAD ZONE HELPERS
// ══════════════════════════════════════════════════
function initUploadZone(zoneId, inputId) {
  const zone  = document.getElementById(zoneId);
  const input = document.getElementById(inputId);
  if (!zone || !input) return;

  input.addEventListener("change", () => {
    const file = input.files[0];
    if (file) {
      const ph = zone.querySelector(".upload-placeholder");
      if (ph) {
        ph.innerHTML = `<div class="upload-icon">✅</div><p class="upload-filename">${file.name}</p>`;
      }
      zone.classList.add("has-file");
    }
  });
}

["c1","c2","c3","c4","c5"].forEach(id => initUploadZone(`${id}-drop`, `${id}-file`));


// ══════════════════════════════════════════════════
//  API CALL HELPER
// ══════════════════════════════════════════════════
async function postDocument(endpoint, textId, fileId) {
  const text    = (document.getElementById(textId)?.value || "").trim();
  const fileEl  = document.getElementById(fileId);
  const file    = fileEl?.files[0];

  if (!text && !file) {
    return { error: "Please paste text or upload a PDF before submitting." };
  }

  let body, headers;
  if (file) {
    const fd = new FormData();
    fd.append("pdf", file);
    fd.append("text", text);
    body = fd;
    headers = {};   // browser sets multipart boundary
  } else {
    body    = JSON.stringify({ text });
    headers = { "Content-Type": "application/json" };
  }

  const resp = await fetch(endpoint, { method: "POST", headers, body });
  return resp.json();
}


// ══════════════════════════════════════════════════
//  RENDER HELPERS
// ══════════════════════════════════════════════════
function setLoading(outputId) {
  document.getElementById(outputId).innerHTML = `
    <div class="loading-state">
      <div class="spinner"></div> Analyzing document — this may take 10–20 seconds…
    </div>`;
}

function setError(outputId, msg) {
  document.getElementById(outputId).innerHTML = `
    <div class="error-state">⚠️ <strong>Error:</strong> ${escHtml(msg)}</div>`;
}

function escHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function badgeClass(severity) {
  return `badge badge-${(severity||"").toLowerCase().replace(/\s+/g,"-")}`;
}
function cardClass(severity) {
  return `result-card ${(severity||"").toLowerCase().replace(/\s+/g,"-")}-risk`;
}


// ══════════════════════════════════════════════════
//  MODULE 1 — CONTRACT SCANNER
// ══════════════════════════════════════════════════
document.getElementById("c1-btn").addEventListener("click", async () => {
  const btn = document.getElementById("c1-btn");
  btn.disabled = true;
  setLoading("c1-output");
  const data = await postDocument("/api/scan-contract", "c1-text", "c1-file");
  btn.disabled = false;

  if (data.error) return setError("c1-output", data.error);

  const riskColor = { High:"var(--high)", Medium:"var(--medium)", Low:"var(--low)" };
  const clauses = (data.clauses || []);
  const clauseHTML = clauses.map(c => `
    <div class="${cardClass(c.severity)}">
      <div class="card-header">
        <span class="card-title">${escHtml(c.title)}</span>
        <span class="${badgeClass(c.severity)}">${escHtml(c.severity)}</span>
      </div>
      ${c.excerpt ? `<div class="excerpt-block">"${escHtml(c.excerpt)}"</div>` : ""}
      <div class="card-label">Why This Matters</div>
      <p style="font-size:13px">${escHtml(c.explanation)}</p>
      ${c.negotiation_tip ? `
        <div class="card-tip" style="margin-top:10px">
          <strong>💡 Negotiation Tip:</strong> ${escHtml(c.negotiation_tip)}
        </div>` : ""}
    </div>`).join("");

  document.getElementById("c1-output").innerHTML = `
    <div class="summary-box">
      <h3>Overall Risk:
        <span style="color:${riskColor[data.overall_risk]||"inherit"}">${escHtml(data.overall_risk||"Unknown")}</span>
      </h3>
      <p style="font-size:13px">${escHtml(data.summary||"")}</p>
    </div>
    ${clauses.length === 0
      ? `<div class="empty-state"><div class="empty-icon">✅</div><p>No significant red flags detected.</p></div>`
      : `<div style="margin-bottom:8px;font-size:13px;font-weight:600">${clauses.length} clause(s) flagged</div>${clauseHTML}`}`;
});


// ══════════════════════════════════════════════════
//  MODULE 2 — PRIVACY AUDITOR
// ══════════════════════════════════════════════════
document.getElementById("c2-btn").addEventListener("click", async () => {
  const btn = document.getElementById("c2-btn");
  btn.disabled = true;
  setLoading("c2-output");
  const data = await postDocument("/api/audit-privacy", "c2-text", "c2-file");
  btn.disabled = false;

  if (data.error) return setError("c2-output", data.error);

  const score = (data.score || "?").toUpperCase();
  const findings = (data.findings || []);
  const findingHTML = findings.map(f => `
    <div class="result-card ${(f.severity||"").toLowerCase()}">
      <div class="card-header">
        <span class="card-title">${escHtml(f.category)}</span>
        <span class="${badgeClass(f.severity)}">${escHtml(f.severity)}</span>
      </div>
      ${f.excerpt ? `<div class="excerpt-block">"${escHtml(f.excerpt)}"</div>` : ""}
      <p style="font-size:13px">${escHtml(f.description)}</p>
    </div>`).join("");

  document.getElementById("c2-output").innerHTML = `
    <div class="score-display">
      <div class="score-letter score-${score.toLowerCase()}">${score}</div>
      <div>
        <div style="font-weight:700">Privacy Score</div>
        <div style="font-size:12px;color:var(--text-muted)">${escHtml(data.score_explanation||"")}</div>
      </div>
    </div>
    <div class="summary-box" style="margin-top:12px">
      <p style="font-size:13px">${escHtml(data.verdict||"")}</p>
    </div>
    ${findings.length === 0
      ? `<div class="empty-state"><div class="empty-icon">✅</div><p>No significant privacy concerns found.</p></div>`
      : findingHTML}`;
});


// ══════════════════════════════════════════════════
//  MODULE 3 — LOAN ANALYZER
// ══════════════════════════════════════════════════
document.getElementById("c3-btn").addEventListener("click", async () => {
  const btn = document.getElementById("c3-btn");
  btn.disabled = true;
  setLoading("c3-output");
  const data = await postDocument("/api/analyze-loan", "c3-text", "c3-file");
  btn.disabled = false;

  if (data.error) return setError("c3-output", data.error);

  const terms = (data.terms || []);
  const rowsHTML = terms.map(t => `
    <tr>
      <td style="font-weight:600">${escHtml(t.variable)}</td>
      <td style="font-family:'JetBrains Mono',monospace">${escHtml(t.value)}</td>
      <td style="color:var(--text-muted)">${escHtml(t.benchmark)}</td>
      <td><span class="${badgeClass(t.flag)}">${escHtml(t.flag)}</span></td>
      <td style="font-size:12px;color:var(--text-muted)">${escHtml(t.note)}</td>
    </tr>`).join("");

  document.getElementById("c3-output").innerHTML = `
    <div class="summary-box">
      <h3>Overall Assessment:
        <span class="${badgeClass(data.overall_flag)}" style="vertical-align:middle;margin-left:6px">
          ${escHtml(data.overall_flag||"Unknown")}
        </span>
      </h3>
      <p style="font-size:13px">${escHtml(data.summary||"")}</p>
    </div>
    ${terms.length === 0
      ? `<div class="empty-state"><div class="empty-icon">📋</div><p>Could not extract financial terms. Ensure you submitted a valid loan agreement.</p></div>`
      : `<div style="overflow-x:auto">
          <table class="loan-table">
            <thead><tr>
              <th>Variable</th><th>Extracted Value</th><th>Benchmark</th><th>Flag</th><th>Note</th>
            </tr></thead>
            <tbody>${rowsHTML}</tbody>
          </table>
        </div>`}
    ${data.disclaimer ? `<p style="font-size:11px;color:var(--text-muted);margin-top:14px">⚠️ ${escHtml(data.disclaimer)}</p>` : ""}`;
});


// ══════════════════════════════════════════════════
//  MODULE 4 — MEDICAL CONSENT SIMPLIFIER
// ══════════════════════════════════════════════════
document.getElementById("c4-btn").addEventListener("click", async () => {
  const btn = document.getElementById("c4-btn");
  btn.disabled = true;
  setLoading("c4-output");
  const data = await postDocument("/api/simplify-medical", "c4-text", "c4-file");
  btn.disabled = false;

  if (data.error) return setError("c4-output", data.error);

  const sections = (data.sections || []);
  const terms    = (data.flagged_terms || []);

  const sectionsHTML = sections.map(s => `
    <div class="medical-section">
      <div>
        <div class="medical-col-label">Original</div>
        <div class="original">${escHtml(s.original)}</div>
      </div>
      <div>
        <div class="medical-col-label">What This Means for You</div>
        <div class="simplified">${escHtml(s.simplified)}</div>
        ${s.risk_flag && s.risk_note
          ? `<div class="card-tip" style="margin-top:8px">⚠️ ${escHtml(s.risk_note)}</div>`
          : ""}
      </div>
    </div>`).join("");

  const termsHTML = terms.length === 0 ? "" : `
    <div style="margin-top:20px">
      <div class="field-label" style="margin-bottom:8px">Flagged Medical / Legal Terms</div>
      ${terms.map(t => `
        <div class="result-card fyi" style="margin-bottom:8px">
          <span style="font-weight:700">${escHtml(t.term)}</span> —
          <span style="font-size:13px">${escHtml(t.explanation)}</span>
        </div>`).join("")}
    </div>`;

  document.getElementById("c4-output").innerHTML = `
    <div class="summary-box">
      <h3>Readability: ${escHtml(data.overall_readability||"")}</h3>
    </div>
    ${sectionsHTML || `<div class="empty-state"><div class="empty-icon">📋</div><p>No sections extracted.</p></div>`}
    ${termsHTML}
    ${data.disclaimer ? `<p style="font-size:11px;color:var(--text-muted);margin-top:14px">⚠️ ${escHtml(data.disclaimer)}</p>` : ""}`;
});


// ══════════════════════════════════════════════════
//  MODULE 5 — LEASE QA CHAT
// ══════════════════════════════════════════════════
document.getElementById("c5-load-btn").addEventListener("click", async () => {
  const btn    = document.getElementById("c5-load-btn");
  const status = document.getElementById("c5-status");
  btn.disabled = true;
  status.className = "status-box";
  status.textContent = "Loading lease…";

  const data = await postDocument("/api/load-lease", "c5-text", "c5-file");
  btn.disabled = false;

  if (data.error) {
    status.className = "status-box";
    status.textContent = "⚠️ " + data.error;
    return;
  }
  status.className = "status-box loaded";
  status.textContent = data.summary || "Lease loaded successfully.";
});

document.getElementById("c5-ask-btn").addEventListener("click", async () => {
  const btn      = document.getElementById("c5-ask-btn");
  const qEl      = document.getElementById("c5-question");
  const chat     = document.getElementById("c5-chat");
  const question = (qEl.value || "").trim();

  if (!question) return;

  btn.disabled = true;
  const qDiv = document.createElement("div");
  qDiv.className = "chat-msg question";
  qDiv.textContent = question;
  chat.appendChild(qDiv);

  const aDiv = document.createElement("div");
  aDiv.className = "chat-msg answer";
  aDiv.innerHTML = `<div class="loading-state"><div class="spinner"></div> Thinking…</div>`;
  chat.appendChild(aDiv);
  chat.scrollTop = chat.scrollHeight;

  const resp = await fetch("/api/ask-lease", {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ question }),
  });
  const data = await resp.json();
  btn.disabled = false;

  aDiv.innerHTML = data.error
    ? `<span style="color:var(--high)">⚠️ ${escHtml(data.error)}</span>`
    : escHtml(data.answer || "No answer returned.");

  qEl.value = "";
  chat.scrollTop = chat.scrollHeight;
});
