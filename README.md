




# AiBotique

AiBotique is a minimal web application for virtual fashion try-on, AI-powered outfit generation, and simple fashion recommendations. It features a React frontend and a Flask backend, allowing users to preview garments on a body image, generate new outfit images from text prompts, and receive basic style suggestions.

## Features

- Virtual try-on: Upload a body photo and a garment photo to preview the result
- Outfit generation: Create outfit images from text prompts (OpenAI API key required)
- Fashion recommendations: Get simple suggestions based on your profile

## Setup

### Backend (Flask)
1. `cd server_py`
2. `python -m venv .venv && .venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add your OpenAI API key
5. `python app.py`

### Frontend (React)
1. `cd client`
2. `npm install`
3. Copy `.env.example` to `.env`
4. `npm run dev`
5. Open http://localhost:5173

## Usage

1. Upload a body image and a garment image to preview the virtual try-on.
2. Use the text prompt feature to generate new outfit images (requires OpenAI API key).
3. Fill in your style preferences to get basic fashion recommendations.

For API details and advanced usage, see [API.md](API.md).


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

