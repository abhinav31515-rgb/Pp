from __future__ import annotations

import os
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename

from ppt_luxury import analyze_presentation, enhance_presentation

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 60 * 1024 * 1024


class APIError(Exception):
    def __init__(self, message: str, status: int = 400):
        self.message = message
        self.status = status
        super().__init__(message)


def _valid(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() == "pptx"


def _save_upload(file_storage) -> tuple[str, Path]:
    if not file_storage or not file_storage.filename:
        raise APIError("No file uploaded. Please choose a .pptx file.")
    if not _valid(file_storage.filename):
        raise APIError("Invalid file type. Only .pptx files are supported.")

    safe_name = secure_filename(file_storage.filename)
    unique_name = f"{uuid.uuid4().hex[:8]}-{safe_name}"
    save_path = UPLOAD_DIR / unique_name
    file_storage.save(save_path)
    return unique_name, save_path


@app.errorhandler(APIError)
def handle_api_error(err: APIError):
    return jsonify({"error": err.message}), err.status


@app.errorhandler(HTTPException)
def handle_http_error(err: HTTPException):
    return jsonify({"error": err.description}), err.code


@app.errorhandler(Exception)
def handle_unknown_error(_err: Exception):
    return jsonify({"error": "Unexpected server error. Please retry."}), 500


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/analyze")
def analyze():
    filename, path = _save_upload(request.files.get("pptx"))
    report = analyze_presentation(str(path))
    return jsonify({"uploaded_file": filename, **report})


@app.post("/enhance")
def enhance():
    feedback = request.form.get("feedback", "")
    _, path = _save_upload(request.files.get("pptx"))
    results = enhance_presentation(str(path), str(OUTPUT_DIR), feedback=feedback)
    return jsonify(results)


@app.get("/download/<path:filename>")
def download(filename: str):
    target = OUTPUT_DIR / filename
    if not target.exists():
        raise APIError("Generated file not found. Please run enhancement again.", status=404)
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), debug=True)
