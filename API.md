# API Overview and Advanced Usage

This document provides details on the available API endpoints, advanced ML integration, and deployment options for AiBotique.

## API Endpoints (Flask)

### Outfit Generation
**POST** `/api/outfit/generate`
- Request: `{ prompt, size? }`
- Response: `{ photo: b64_png }`
- Uses OpenAI DALL·E (or gpt-image-1) to generate outfit images from text prompts.

### Recommendations
**POST** `/api/recommendations/train`
- Request: `{ dataset_path?, epochs? }`
- Response: training summary
- Trains a Tiny Neural Network (TNN) on 10k+ synthetic or real fashion events/interactions.

**POST** `/api/recommendations`
- Request: `{ user_profile: { age, gender, color_pref, style_pref, budget }, k? }`
- Response: ranked items
- Returns top-N personalized recommendations using the trained TNN or a deterministic fallback.

## Notes
- DALL·E via OpenAI Images API powers outfit generation.
- TNN recommender (PyTorch) trains on a CSV (if provided) or a 10k synthetic dataset and saves to `server_py/models/`.

## Deployment
- Containerize the Flask API and serve behind a reverse proxy; deploy the client as static assets (Vite build) to any CDN.
- Ensure GPU availability for best performance on outfit generation or fall back to CPU mode.

---

