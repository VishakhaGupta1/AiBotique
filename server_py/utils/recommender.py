import os
import json
from typing import Optional, Dict, Any, List

try:
    import numpy as np  # optional
except Exception:
    np = None

try:
    import torch  # optional
    import torch.nn as nn
    import torch.optim as optim
except Exception:
    torch = None
    nn = None
    optim = None

try:
    from sklearn.preprocessing import StandardScaler  # optional
except Exception:
    StandardScaler = None

MODEL_DIR = os.environ.get("MODEL_DIR", os.path.join(os.path.dirname(__file__), "..", "models"))
MODEL_DIR = os.path.abspath(MODEL_DIR)
MODEL_PATH = os.path.join(MODEL_DIR, "tnn_recommender.pt")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.npy")
META_PATH = os.path.join(MODEL_DIR, "metadata.json")


def _ensure_dirs():
    os.makedirs(MODEL_DIR, exist_ok=True)


TinyNN = None
if nn is not None:
    class TinyNN(nn.Module):
        def __init__(self, in_features: int, hidden: int = 32, out_features: int = 8):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(in_features, hidden),
                nn.ReLU(),
                nn.Linear(hidden, hidden),
                nn.ReLU(),
                nn.Linear(hidden, out_features),
            )

        def forward(self, x):
            return self.net(x)


def _load_or_mock_dataset(dataset_path: Optional[str]):
    """
    Load dataset of fashion events or user-item interactions.
    Expected CSV with numeric features for demo; if missing, mock 10k rows.
    """
    if np is not None and dataset_path and os.path.exists(dataset_path):
        try:
            import pandas as pd
            df = pd.read_csv(dataset_path)
            data = df.select_dtypes(include=[np.number]).values
            if data.shape[0] < 1000:
                # augment lightly to simulate scale
                reps = max(1, 1000 // max(1, data.shape[0]))
                data = np.tile(data, (reps, 1))
            return data
        except Exception:
            pass
    # Mock 10k rows, 16 features representing user + item + context
    if np is None:
        # Minimal Python-only mock: return list of lists
        return [[0.0] * 16 for _ in range(10000)]
    rng = np.random.default_rng(42)
    data = rng.normal(size=(10000, 16)).astype(np.float32)
    return data


def train_recommender(dataset_path: Optional[str] = None, epochs: int = 2) -> Dict[str, Any]:
    _ensure_dirs()
    data = _load_or_mock_dataset(dataset_path)

    if StandardScaler is None or np is None or torch is None:
        return {"status": "skipped", "reason": "heavy deps unavailable"}
    scaler = StandardScaler()
    X = scaler.fit_transform(data)

    X_torch = torch.tensor(X, dtype=torch.float32)
    # Toy target: next-step trend score (simulated)
    y = torch.sum(X_torch[:, :8], dim=1, keepdim=True) + 0.1 * torch.randn(X_torch.size(0), 1)

    model = TinyNN(in_features=X.shape[1], hidden=64, out_features=1)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)

    model.train()
    for ep in range(epochs):
        optimizer.zero_grad()
        pred = model(X_torch)
        loss = criterion(pred, y)
        loss.backward()
        optimizer.step()

    torch.save(model.state_dict(), MODEL_PATH)
    np.save(SCALER_PATH, {"mean_": scaler.mean_, "scale_": scaler.scale_}, allow_pickle=True)
    meta = {"in_features": X.shape[1], "epochs": epochs}
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f)

    return {"status": "trained", "samples": int(X.shape[0]), "features": int(X.shape[1]), "epochs": epochs}


def _load_model():
    if TinyNN is None or torch is None:
        raise RuntimeError("Model loading requires torch and TinyNN")
    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)
    in_features = int(meta.get("in_features", 16))
    model = TinyNN(in_features=in_features, hidden=64, out_features=1)
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()
    return model


def _load_scaler():
    obj = np.load(SCALER_PATH, allow_pickle=True).item()
    scaler = StandardScaler()
    scaler.mean_ = obj["mean_"]
    scaler.scale_ = obj["scale_"]
    scaler.var_ = scaler.scale_ ** 2
    scaler.n_samples_seen_ = 1
    return scaler


def get_recommendations(user_profile: Dict[str, Any], k: int = 10) -> List[Dict[str, Any]]:
    """
    Given a user profile (age, gender, style prefs, recent views), return k item recs.
    This uses the tiny neural net as a trend + affinity scorer.
    """
    _ensure_dirs()
    # If heavy deps missing, return deterministic pseudo-recs
    if (torch is None or nn is None or StandardScaler is None or np is None or TinyNN is None or not os.path.exists(MODEL_PATH)):
        age = float(user_profile.get("age", 28)) / 100.0
        gender = 1.0 if str(user_profile.get("gender", "f")).lower().startswith("f") else 0.0
        color = (abs(hash(user_profile.get("color_pref", "black"))) % 100) / 100.0
        style = (abs(hash(user_profile.get("style_pref", "streetwear"))) % 100) / 100.0
        budget = float(user_profile.get("budget", 100)) / 1000.0
        base = (age * 0.4 + gender * 0.1 + color * 0.25 + style * 0.15 + budget * 0.1)
        recs = []
        for i in range(k):
            recs.append({
                "item_id": f"itm_{i:03d}",
                "name": f"Recommended Outfit {i+1}",
                "score": round(float(base - i * 0.03), 4),
                "style": user_profile.get("style_pref", "streetwear"),
                "color": user_profile.get("color_pref", "black"),
            })
        return recs

    if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
        train_recommender(dataset_path=None, epochs=2)
    model = _load_model()
    scaler = _load_scaler()

    age = float(user_profile.get("age", 28)) / 100.0
    gender = 1.0 if str(user_profile.get("gender", "f")).lower().startswith("f") else 0.0
    color = hash(user_profile.get("color_pref", "black")) % 100 / 100.0
    style = hash(user_profile.get("style_pref", "streetwear")) % 100 / 100.0
    budget = float(user_profile.get("budget", 100)) / 1000.0

    uvec = np.array([age, gender, color, style, budget] + [0.0] * 11, dtype=np.float32)
    X = scaler.transform(uvec.reshape(1, -1))
    with torch.no_grad():
        score = _load_model()(torch.tensor(X, dtype=torch.float32)).item()

    # Return k pseudo items with descending scores based on seed
    recs = []
    for i in range(k):
        recs.append({
            "item_id": f"itm_{i:03d}",
            "name": f"Recommended Outfit {i+1}",
            "score": round(float(score - i * 0.05), 4),
            "style": user_profile.get("style_pref", "streetwear"),
            "color": user_profile.get("color_pref", "black"),
        })
    return recs
