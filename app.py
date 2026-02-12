from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from ppt_luxury import analyze_presentation, enhance_presentation

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 60 * 1024 * 1024


def _valid(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() == "pptx"


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/analyze")
def analyze():
    file = request.files.get("pptx")
    if not file or not file.filename or not _valid(file.filename):
        return jsonify({"error": "Please upload a valid .pptx file."}), 400

    filename = secure_filename(file.filename)
    path = UPLOAD_DIR / filename
    file.save(path)
    report = analyze_presentation(str(path))
    report["uploaded_file"] = filename
    return jsonify(report)


@app.post("/enhance")
def enhance():
    file = request.files.get("pptx")
    feedback = request.form.get("feedback", "")

    if not file or not file.filename or not _valid(file.filename):
        return jsonify({"error": "Please upload a valid .pptx file."}), 400

    filename = secure_filename(file.filename)
    path = UPLOAD_DIR / filename
    file.save(path)

    results = enhance_presentation(str(path), str(OUTPUT_DIR), feedback=feedback)
    return jsonify(results)


@app.get("/download/<path:filename>")
def download(filename: str):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), debug=True)
