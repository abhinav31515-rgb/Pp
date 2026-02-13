const pptxInput = document.getElementById("pptx");
const feedbackInput = document.getElementById("feedback");
const analyzeBtn = document.getElementById("analyzeBtn");
const enhanceBtn = document.getElementById("enhanceBtn");
const results = document.getElementById("results");
const statusEl = document.getElementById("status");

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.remove("hidden");
  statusEl.classList.toggle("error", isError);
}

function setBusy(isBusy) {
  [analyzeBtn, enhanceBtn].forEach((btn) => {
    btn.disabled = isBusy;
  });
}

function getFile() {
  if (!pptxInput.files.length) {
    setStatus("Upload a .pptx file first.", true);
    return null;
  }
  return pptxInput.files[0];
}

function renderAnalysis(data, mode = "analysis") {
  const flags = (data.quality_flags || []).map((f) => `<li>${f}</li>`).join("");
  const anim = (data.animation_plan || []).map((f) => `<li>${f}</li>`).join("");
  const mods = (data.modifications || []).map((f) => `<li>${f}</li>`).join("");

  const downloadLink =
    mode === "enhance"
      ? `<a class="download" href="/download/${encodeURIComponent(data.output_file)}">⬇ Download luxury PPTX</a>`
      : "";

  results.classList.remove("hidden");
  results.innerHTML = `
    <h2>${mode === "analysis" ? "Design Audit" : "Luxury Enhancement Complete"}</h2>
    <div class="grid">
      <div class="card"><small>Slides</small><div>${data.slides}</div></div>
      <div class="card"><small>Detected Use Case</small><div>${data.use_case}</div></div>
      <div class="card"><small>Brand Score</small><div>${data.brand_score}/100</div></div>
      <div class="card"><small>Title Coverage</small><div>${data.title_coverage}%</div></div>
      <div class="card"><small>Visual Balance</small><div>${data.visual_balance}%</div></div>
      <div class="card"><small>Applied Style</small><div>${data.style_applied || "N/A"}</div></div>
    </div>
    <h3>Commercial-grade quality notes</h3>
    <ul>${flags || "<li>No issues detected.</li>"}</ul>
    <h3>Cinematic animation plan</h3>
    <ul>${anim}</ul>
    ${mods ? `<h3>Applied adjustments</h3><ul>${mods}</ul>` : ""}
    ${downloadLink}
  `;
}

async function postFile(url) {
  const file = getFile();
  if (!file) return null;

  const form = new FormData();
  form.append("pptx", file);
  form.append("feedback", feedbackInput.value || "");

  const res = await fetch(url, { method: "POST", body: form });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Request failed.");
  return data;
}

analyzeBtn.addEventListener("click", async () => {
  setBusy(true);
  setStatus("Analyzing deck quality and brand signals...");
  try {
    const data = await postFile("/analyze");
    if (data) {
      renderAnalysis(data, "analysis");
      setStatus("Analysis complete.");
    }
  } catch (err) {
    setStatus(err.message, true);
  } finally {
    setBusy(false);
  }
});

enhanceBtn.addEventListener("click", async () => {
  setBusy(true);
  setStatus("Applying luxury redesign and cinematic touchups...");
  try {
    const data = await postFile("/enhance");
    if (data) {
      renderAnalysis(data, "enhance");
      setStatus("Enhancement complete. Download your upgraded deck.");
    }
  } catch (err) {
    setStatus(err.message, true);
  } finally {
    setBusy(false);
  }
});
