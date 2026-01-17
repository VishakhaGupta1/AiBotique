# API Overview and Advanced Usage

This document provides details on the available API endpoints, advanced ML integration, and deployment options for AiBotique.

## API Endpoints (Flask)

### Outfit Generation
**POST** `/api/outfit/generate`
- Request: `{ prompt, size? }`
- Response: `{ photo: b64_png }`
- Uses OpenAI DALL·E (or gpt-image-1) to generate outfit images from text prompts.

### Virtual Try-On
**POST** `/api/tryon`
- Request: multipart form-data: `body` (file), `garment` (file)
- Response: `{ composite: b64_png }`
- Upload a body photo and a garment photo (no text prompt required).
- By default, uses placeholder overlays. For real try-on, see Advanced ML Integration below.

### Recommendations
**POST** `/api/recommendations/train`
- Request: `{ dataset_path?, epochs? }`
- Response: training summary
- Trains a Tiny Neural Network (TNN) on 10k+ synthetic or real fashion events/interactions.

**POST** `/api/recommendations`
- Request: `{ user_profile: { age, gender, color_pref, style_pref, budget }, k? }`
- Response: ranked items
- Returns top-N personalized recommendations using the trained TNN or a deterministic fallback.

## Advanced ML Integration
- To enable real try-on:
  - Install `torch`, `diffusers`, `mediapipe`
  - Download a VITON/CP-VTON/Stable Diffusion checkpoint
  - Replace the stub in `server_py/utils/tryon.py` with the actual ML pipeline (body parsing, garment warping, compositing)
  - See code comments in `tryon.py` for integration points and pseudo-code

## Notes
- DALL·E via OpenAI Images API powers outfit generation.
- Try-On uses MediaPipe (pose landmarks) to detect torso region and overlays a stable-diffusion–generated cloth texture. If heavy libs/GPU are unavailable, a light fallback still demonstrates end-to-end flow.
- TNN recommender (PyTorch) trains on a CSV (if provided) or a 10k synthetic dataset and saves to `server_py/models/`.

## Deployment
- Containerize the Flask API and serve behind a reverse proxy; deploy the client as static assets (Vite build) to any CDN.
- Ensure GPU availability for best performance on try-on (diffusers) or fall back to CPU placeholder mode.

---

