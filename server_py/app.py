import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=False)

@app.get("/health")
def health():
    return jsonify({"status": "ok", "name": "ARBotique Flask API"})

@app.post("/api/outfit/generate")
def api_generate_outfit():
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt")
    size = data.get("size", "1024x1024")
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400
    try:
        # Lazy import to avoid heavy deps at startup
        from utils.dalle import generate_outfit_image
        b64_png = generate_outfit_image(prompt=prompt, size=size)
        return jsonify({"photo": b64_png})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.post("/api/tryon")
def api_tryon():
    # Accepts multipart/form-data: files 'body' and 'garment'
    body_file = request.files.get("body")
    garment_file = request.files.get("garment")
    if not body_file or not garment_file:
        return jsonify({"error": "Both body (file) and garment (file) are required."}), 400
    try:
        body_img_bytes = body_file.read()
        garment_img_bytes = garment_file.read()
        # Lazy import; if unavailable, return passthrough
        try:
            from utils.tryon import try_on_outfit
            result_b64 = try_on_outfit(body_img_bytes, garment_img_bytes)
        except Exception:
            # Fallback: echo original body image as placeholder composite
            import base64
            result_b64 = base64.b64encode(body_img_bytes).decode("utf-8")
        return jsonify({"composite": result_b64})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
def api_recommend():
    payload = request.get_json(silent=True) or {}
    user_profile = payload.get("user_profile", {})
    k = int(payload.get("k", 10))
    try:
        from utils.recommender import get_recommendations
        recs = get_recommendations(user_profile=user_profile, k=k)
        return jsonify({"recommendations": recs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") in ("1", "true", "True")
    app.run(host="0.0.0.0", port=port, debug=debug)
