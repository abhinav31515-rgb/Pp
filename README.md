# PPT Luxury AI Stylist

A web app that uploads a `.pptx` file, analyzes its design quality, infers use case, and produces an upgraded "luxury" styled version with:

- Better color palette and typography
- Consistent title/body hierarchy
- Placeholder visuals when slide images are missing
- Cinematic motion cues inserted in speaker notes
- Feedback-driven touch-ups from user text
- No paid API dependency

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://localhost:8000`.

## Notes

- Input must be `.pptx`
- Output can be downloaded from the app after enhancement
- Motion/animation guidance is embedded as notes because low-level animation authoring is not broadly supported by `python-pptx`
