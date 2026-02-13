# PPT Luxury AI Stylist

Commercial-grade web app for transforming uploaded `.pptx` decks into luxury, brand-consistent, cinematic presentations.

## What it does

- Runs a design audit (title coverage, text density, visual balance, brand score)
- Infers use case and applies a matching premium style system
- Auto-fixes typography, palette, hierarchy, and visual consistency
- Injects placeholder visuals when imagery is missing
- Writes speaker-note animation cues for cinematic delivery
- Accepts user feedback prompts for touchups
- Optionally augments recommendations with Gemini when `GEMINI_API_KEY` is set

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://localhost:8000.

## API endpoints

- `GET /health`
- `POST /analyze` (`multipart/form-data` with `pptx`)
- `POST /enhance` (`multipart/form-data` with `pptx` and optional `feedback`)
- `GET /download/<filename>`

## Notes

- Uses local heuristics by default; no paid API is required.
- To use Gemini ideas, set `GEMINI_API_KEY` in your environment.
