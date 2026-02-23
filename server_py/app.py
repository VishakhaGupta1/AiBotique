import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load .env file with explicit path
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Fallback: Set environment variable directly if .env doesn't work
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "sk-...YE8A"

# Debug: Check if API key is loaded
api_key = os.environ.get("OPENAI_API_KEY")
print(f"DEBUG: API Key loaded: {bool(api_key)}")
print(f"DEBUG: API Key starts with sk-: {api_key.startswith('sk-') if api_key else False}")
print(f"DEBUG: .env path: {dotenv_path}")
print(f"DEBUG: .env exists: {os.path.exists(dotenv_path)}")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

@app.get("/health")
def health():
    return jsonify({"status": "ok", "name": "ARBotique Flask API"})

@app.post("/api/recommendations/train")
def api_train():
    data = request.get_json(silent=True) or {}
    dataset_path = data.get("dataset_path")
    epochs = int(data.get("epochs", 2))
    try:
        from utils.recommender import train_recommender
        summary = train_recommender(dataset_path=dataset_path, epochs=epochs)
    except Exception:
        summary = {"status": "skipped", "reason": "heavy deps unavailable", "epochs": epochs}
    return jsonify(summary)

@app.post("/api/recommendations")
def api_recommendations():
    data = request.get_json(silent=True) or {}
    try:
        from ml_recommendations import get_fashion_recommendations
        
        # Transform input to match ML engine expectations
        user_profile = {
            'user_id': data.get('user_id', 1),
            'age': data.get('age', 25),
            'gender': data.get('gender', 'male'),
            'color': data.get('color_pref', 'blue'),
            'style': data.get('style_pref', 'casual'),
            'budget': data.get('budget', 5000)
        }
        
        # Get professional ML recommendations
        recs = get_fashion_recommendations(user_profile, k=8)
        
        return jsonify({"recommendations": recs})
    except Exception as e:
        # Fallback to simple recommendations if ML fails
        try:
            from utils.recommender import recommend_products
            recs = recommend_products(data)
            return jsonify({"recommendations": recs})
        except Exception as e2:
            return jsonify({"error": f"ML Engine Error: {str(e)}, Fallback Error: {str(e2)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") in ("1", "true", "True")
    app.run(host="0.0.0.0", port=port, debug=debug)
