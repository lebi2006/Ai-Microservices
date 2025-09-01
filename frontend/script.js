const API_BASE = "http://127.0.0.1:8000";

// Helper function: animate dots in result box
function startDots(resultEl) {
    let dots = 0;
    resultEl.textContent = "Processing";
    const interval = setInterval(() => {
        dots = (dots + 1) % 4;
        resultEl.textContent = "Processing" + ".".repeat(dots);
    }, 500);
    return interval;
}

// ---------- Summarize ----------
async function callSummarize() {
    const text = document.getElementById("summarize-text").value;
    const length = document.getElementById("summarize-length").value;
    const resultEl = document.getElementById("summarize-result");
    const loader = document.getElementById("summarize-loader");

    const dotInterval = startDots(resultEl);
    loader.style.visibility = "visible";

    try {
        const res = await fetch(`${API_BASE}/summarize`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ text, length }),
        });
        const data = await res.json();
        resultEl.textContent = data.summary || "No summary returned";
    } catch (err) {
        resultEl.textContent = "Error: " + err;
    } finally {
        clearInterval(dotInterval);
        loader.style.visibility = "hidden";
    }
}

// ---------- Q&A ----------
async function callQA() {
    const query = document.getElementById("qa-query").value;
    const text = document.getElementById("qa-text").value;
    const file = document.getElementById("qa-file").files[0];
    const resultEl = document.getElementById("qa-result");
    const loader = document.getElementById("qa-loader");

    const dotInterval = startDots(resultEl);
    loader.style.visibility = "visible";

    const formData = new FormData();
    formData.append("query", query);
    if (text) formData.append("text", text);
    if (file) formData.append("file", file);

    try {
        const res = await fetch(`${API_BASE}/qa`, {
            method: "POST",
            body: formData,
        });
        const data = await res.json();
        resultEl.textContent = data.answer || "No answer returned";
    } catch (err) {
        resultEl.textContent = "Error: " + err;
    } finally {
        clearInterval(dotInterval);
        loader.style.visibility = "hidden";
    }
}

// ---------- Learning Path ----------
async function callLearningPath() {
    const goal = document.getElementById("lp-goal").value;
    const background = document.getElementById("lp-background").value;
    const duration_weeks = parseInt(document.getElementById("lp-weeks").value) || 8;
    const hours_per_week = parseInt(document.getElementById("lp-hours").value) || 6;
    const resultEl = document.getElementById("lp-result");
    const loader = document.getElementById("lp-loader");

    const dotInterval = startDots(resultEl);
    loader.style.visibility = "visible";

    try {
        const res = await fetch(`${API_BASE}/learning-path`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ goal, background, duration_weeks, hours_per_week }),
        });

        if (!res.ok) {
            const text = await res.text();
            throw new Error(`HTTP ${res.status}: ${text}`);
        }

        const data = await res.json();
        console.log("learning-path response:", data);

        if (data && Array.isArray(data.weeks) && data.weeks.length > 0) {
            const weeks = data.weeks;
            let html = `<div class="lp-container">`;
            html += `<h3 style="margin-top:0;">Learning Path — ${escapeHtml(goal || "Your goal")}</h3>`;
            html += `<p style="color:#444;margin-top:0.25rem;">${escapeHtml(background || "Background: unspecified")} — ${duration_weeks} weeks, ~${hours_per_week} hrs/week</p>`;
            html += `<div class="lp-weeks">`;
            weeks.forEach(w => {
                html += `<div class="lp-week" style="margin:12px 0;padding:10px;border-radius:8px;background:#fbfcfe;border:1px solid #e6eefc;">`;
                html += `<strong style="display:block;margin-bottom:6px;">Week ${escapeHtml(String(w.week || ""))}</strong>`;
                if (Array.isArray(w.topics) && w.topics.length > 0) {
                    html += `<ul style="margin:6px 0 6px 18px;">`;
                    w.topics.forEach(t => {
                        html += `<li>${escapeHtml(String(t))}</li>`;
                    });
                    html += `</ul>`;
                }
                if (Array.isArray(w.resources) && w.resources.length > 0) {
                    html += `<div style="font-size:0.95rem;color:#333;">Resources:</div><ul style="margin:4px 0 0 18px;">`;
                    w.resources.forEach(r => {
                        const title = escapeHtml(r.title || r.name || JSON.stringify(r));
                        const link = r.link ? `<a href="${escapeAttribute(r.link)}" target="_blank" rel="noopener noreferrer">${title}</a>` : title;
                        html += `<li>${link}${r.type ? ` — <em>${escapeHtml(r.type)}</em>` : ""}</li>`;
                    });
                    html += `</ul>`;
                }
                if (Array.isArray(w.practicals) && w.practicals.length > 0) {
                    html += `<div style="font-size:0.95rem;color:#333;margin-top:6px;">Practicals:</div><ul style="margin:4px 0 0 18px;">`;
                    w.practicals.forEach(p => {
                        html += `<li>${escapeHtml(String(p))}</li>`;
                    });
                    html += `</ul>`;
                }
                html += `</div>`;
            });
            html += `</div>`; 

            if (data.raw_text) {
                html += `<details style="margin-top:10px;color:#444;"><summary style="cursor:pointer">Show raw LLM output</summary><pre style="white-space:pre-wrap;background:#f7f9fc;padding:10px;border-radius:6px;margin-top:8px;">${escapeHtml(data.raw_text)}</pre></details>`;
            }

            html += `</div>`;
            resultEl.innerHTML = html;
            return;
        }
        if (data && typeof data.raw_text === "string" && data.raw_text.trim().length > 0) {
            resultEl.innerHTML = `<pre style="white-space:pre-wrap;font-family:ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;">${escapeHtml(data.raw_text)}</pre>`;
            return;
        }

        resultEl.innerHTML = `<pre style="white-space:pre-wrap">${escapeHtml(JSON.stringify(data, null, 2))}</pre>`;

    } catch (err) {
        console.error(err);
        resultEl.innerText = "Error: " + err.message;
    } finally {
        clearInterval(dotInterval);
        loader.style.visibility = "hidden";
    }
}

function escapeHtml(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
function escapeAttribute(url) {
    return String(url).replace(/"/g, "%22");
}
