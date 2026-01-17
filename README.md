



# AiBotique

AiBotique is a minimal web application that demonstrates virtual fashion try-on, AI-powered outfit generation, and simple fashion recommendations. It combines a React frontend with a Flask backend, allowing users to preview garments on a body image, generate new outfit images from text prompts, and receive basic style suggestions.

## Features

- Upload a body photo and a garment photo to preview a virtual try-on
- Generate outfit images from text prompts (requires OpenAI API key)
- Get simple fashion recommendations based on user profile

## Setup

### Backend (Flask)
1. Go to the backend folder:
  ```sh
  cd server_py
  ```
2. Create and activate a virtual environment:
  ```sh
  python -m venv .venv
  .venv\Scripts\activate
  ```
3. Install dependencies:
  ```sh
  pip install -r requirements.txt
  ```
4. Copy `.env.example` to `.env` and add your OpenAI API key.
5. Start the server:
  ```sh
  python app.py
  ```

### Frontend (React)
1. Go to the frontend folder:
  ```sh
  cd client
  ```
2. Install dependencies:
  ```sh
  npm install
  ```
3. Copy `.env.example` to `.env` (default is fine for local use).
4. Start the development server:
  ```sh
  npm run dev
  ```
5. Open [http://localhost:5173](http://localhost:5173) in your browser.

## Usage

1. Upload a body image and a garment image to preview the virtual try-on.
2. Use the text prompt feature to generate new outfit images (requires OpenAI API key).
3. Fill in your style preferences to get basic fashion recommendations.


2) Install dependencies

Python (Flask API):

```
python -m venv .venv
.venv\Scripts\activate
pip install -r server_py/requirements.txt
```

Node (client):

```
cd client
npm install
```

3) Run the services

Flask API:

```
set FLASK_APP=server_py/app.py
python server_py/app.py
```

Client:

```
cd client
npm run dev
```

Open the printed local URL (usually http://127.0.0.1:5173).

## API Overview (Flask)

- POST /api/outfit/generate – { prompt, size? } → { photo: b64_png }
  - Uses OpenAI DALL·E (or gpt-image-1) to generate outfit images from text prompts.
  
- POST /api/tryon – multipart form-data: body (file), garment (file) → { composite: b64_png }
  - **Advanced ML pipeline ready:**
    - Upload a body photo and a garment photo (no text prompt required)
    - Placeholder overlays by default
    - To enable real try-on:
      1. Install torch, diffusers, mediapipe
      2. Download a VITON/CP-VTON/Stable Diffusion checkpoint
      3. Replace the stub in `server_py/utils/tryon.py` with the actual ML pipeline (body parsing, garment warping, compositing)
    - See code comments in `tryon.py` for integration points and pseudo-code.
- POST /api/recommendations/train – { dataset_path?, epochs? } → training summary
  - Trains a Tiny Neural Network (TNN) on 10k+ synthetic or real fashion events/interactions.
- POST /api/recommendations – { user_profile: { age, gender, color_pref, style_pref, budget }, k? } → ranked items
  - Returns top-N personalized recommendations using the trained TNN or a deterministic fallback.
- POST /api/recommendations – { user_profile: { age, gender, color_pref, style_pref, budget }, k? } → ranked items

Notes:
- DALL·E via OpenAI Images API powers outfit generation.
- Try-On uses MediaPipe (pose landmarks) to detect torso region and overlays a stable-diffusion–generated cloth texture. If heavy libs/GPU are unavailable, a light fallback still demonstrates end-to-end flow.
- TNN recommender (PyTorch) trains on a CSV (if provided) or a 10k synthetic dataset and saves to server_py/models/.

## Front-End Flows

- Customize 3D Shirt: Generate textures via DALL·E and project onto the 3D shirt.
- Virtual Try-On: Upload a body photo and a garment photo → composed try-on preview (no prompt required).
- Recommendations: Simple form to capture user profile → top-N item suggestions.

## Metrics & Assumptions

- Projected 18% return-rate reduction stems from improved fit visualization and personalized recommendations. A sample A/B framework can estimate uplift by comparing conversion (kept items) with/without try-on.
- The TNN model is intentionally compact to train quickly and is suitable for trend forecasting and ranking signals in a demo environment.

## Optional: Training on Your Dataset

Place your CSV (with numeric features) anywhere accessible and call:

```
curl -X POST %VITE_API_BASE%/api/recommendations/train ^
  -H "Content-Type: application/json" ^
  -d "{\"dataset_path\": \"c:/path/to/your/data.csv\", \"epochs\": 5}"
```

If omitted, the API auto-generates a 10k synthetic dataset.

## Deployment

- Containerize the Flask API and serve behind a reverse proxy; deploy the client as static assets (Vite build) to any CDN.
- Ensure GPU availability for best performance on try-on (diffusers) or fall back to CPU placeholder mode.

---

Legacy Node server (server/) remains for reference but is superseded by Flask for the core AI/AR workflows.
