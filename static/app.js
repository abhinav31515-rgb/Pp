const pptxInput = document.getElementById("pptx");
const feedbackInput = document.getElementById("feedback");
const analyzeBtn = document.getElementById("analyzeBtn");
const enhanceBtn = document.getElementById("enhanceBtn");
const results = document.getElementById("results");

function getFile() {
  if (!pptxInput.files.length) {
    alert("Upload a .pptx file first.");
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
      ? `<a class="download" href="/download/${data.output_file}">⬇ Download luxury PPTX</a>`
      : "";

  results.classList.remove("hidden");
  results.innerHTML = `
    <h2>${mode === "analysis" ? "Design Analysis" : "Luxury Enhancement Complete"}</h2>
    <div class="grid">
      <div class="card"><small>Slides</small><div>${data.slides || data.analysis.slides}</div></div>
      <div class="card"><small>Detected Use Case</small><div>${data.use_case || data.analysis.use_case}</div></div>
      <div class="card"><small>Title Coverage</small><div>${data.title_coverage || data.analysis.title_coverage}%</div></div>
      <div class="card"><small>Images Found</small><div>${data.image_count || data.analysis.image_count}</div></div>
      <div class="card"><small>Applied Style</small><div>${data.style_applied || "N/A"}</div></div>
      <div class="card"><small>Fonts</small><div>${(data.fonts || []).join(", ") || "N/A"}</div></div>
    </div>
    <h3>Quality & layout feedback</h3>
    <ul>${flags}</ul>
    <h3>Suggested cinematic animation flow</h3>
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
  try {
    const data = await postFile("/analyze");
    if (data) renderAnalysis(data, "analysis");
  } catch (err) {
    alert(err.message);
  }
});

enhanceBtn.addEventListener("click", async () => {
  try {
    const data = await postFile("/enhance");
    if (data) renderAnalysis(data, "enhance");
  } catch (err) {
    alert(err.message);
  }
});
