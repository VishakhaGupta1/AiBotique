
# AiBotique

AiBotique is a professional AI-powered fashion styling platform that provides personalized outfit recommendations. It features a modern React frontend with multi-step UI and a Flask backend with ML-powered recommendations.

## Features

- **AI-Powered Recommendations**: Get personalized outfit suggestions based on your style preferences, body type, and budget
- **Multi-Step Style Quiz**: Interactive quiz to discover your fashion personality
- **Gender-Specific Styling**: Tailored recommendations for both men and women
- **Indian Pricing**: All products priced in Indian Rupees (₹)
- **Complete Outfits**: Full styling suggestions with matching accessories
- **Modern UI/UX**: Beautiful animations and professional design

## Tech Stack

- **Frontend**: React, Vite, Tailwind CSS, Framer Motion
- **Backend**: Flask, Python, ML Recommendations
- **State Management**: Valtio

## Setup

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+

### Backend (Flask)
1. `cd server_py`
2. `python -m venv venv`
3. `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and configure your settings
6. `python app.py`

### Frontend (React)
1. `cd client`
2. `npm install`
3. Copy `.env.example` to `.env` and configure API endpoint
4. `npm run dev`
5. Open http://localhost:5173

## Usage

1. **Get Recommendations**: 
   - Click "Recommendations" on home page
   - Complete style quiz (colors, styles, budget, preferences)
   - Get personalized outfit suggestions with Indian pricing

## API Endpoints

- `POST /api/recommendations` - Get personalized outfit recommendations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under MIT License.
