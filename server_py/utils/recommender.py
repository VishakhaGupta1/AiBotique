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


def load_products():
    """Load complete outfit combinations"""
    return [
        # Men's Complete Outfits
        {
            "outfit_id": "outfit_001",
            "name": "Business Professional Outfit",
            "target_gender": "male",
            "target_age": "25-45",
            "category": "business",
            "color_scheme": "navy",
            "total_price": 12497,
            "items": [
                {"type": "top", "name": "White Formal Shirt", "brand": "Office Wear", "price": 1899, "image_url": "https://images.unsplash.com/photo-1596755094514-f87e40cc0606?w=200&h=200&fit=crop"},
                {"type": "bottom", "name": "Navy Blue Trousers", "brand": "Formal Wear Co", "price": 3499, "image_url": "https://images.unsplash.com/photo-1594634319951-eb4e2a6eb4e3?w=200&h=200&fit=crop"},
                {"type": "shoes", "name": "Brown Formal Shoes", "brand": "Executive Style", "price": 3999, "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=200&h=200&fit=crop"},
                {"type": "accessory", "name": "Brown Leather Belt", "brand": "Accessories Plus", "price": 1499, "image_url": "https://images.unsplash.com/photo-1544967348-c7ceb6ec5ec0?w=200&h=200&fit=crop"},
                {"type": "accessory", "name": "Silver Watch", "brand": "Time Style", "price": 2599, "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=200&h=200&fit=crop"}
            ],
            "description": "Complete professional business outfit for office meetings",
            "in_stock": True
        },
        {
            "outfit_id": "outfit_002", 
            "name": "Casual Streetwear Look",
            "target_gender": "male",
            "target_age": "18-30",
            "category": "streetwear",
            "color_scheme": "blue",
            "total_price": 8497,
            "items": [
                {"type": "top", "name": "Blue Streetwear Hoodie", "brand": "Urban Style", "price": 2999, "image_url": "https://images.unsplash.com/photo-1516851295518-3b29f0e2b876?w=200&h=200&fit=crop"},
                {"type": "bottom", "name": "Black Denim Jeans", "brand": "Denim Co", "price": 2499, "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=200&h=200&fit=crop"},
                {"type": "shoes", "name": "White Sneakers", "brand": "Street Kicks", "price": 3999, "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=200&h=200&fit=crop"}
            ],
            "description": "Trendy streetwear outfit for casual outings",
            "in_stock": True
        },
        {
            "outfit_id": "outfit_003",
            "name": "Sporty Athletic Look",
            "target_gender": "male", 
            "target_age": "16-35",
            "category": "sporty",
            "color_scheme": "gray",
            "total_price": 5497,
            "items": [
                {"type": "top", "name": "Gray Athletic T-Shirt", "brand": "Athletic Pro", "price": 1299, "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=200&h=200&fit=crop"},
                {"type": "bottom", "name": "Black Track Pants", "brand": "Athletic Pro", "price": 1499, "image_url": "https://images.unsplash.com/photo-1586790170083-2c9cadedfd79?w=200&h=200&fit=crop"},
                {"type": "shoes", "name": "Red Running Shoes", "brand": "Athletic Pro", "price": 5499, "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=200&h=200&fit=crop"}
            ],
            "description": "Comfortable athletic outfit for workouts and sports",
            "in_stock": True
        },
        
        # Women's Complete Outfits
        {
            "outfit_id": "outfit_004",
            "name": "Elegant Evening Look",
            "target_gender": "female",
            "target_age": "25-40",
            "category": "elegant",
            "color_scheme": "black",
            "total_price": 15497,
            "items": [
                {"type": "top", "name": "Black Evening Dress", "brand": "Sophisticate", "price": 5799, "image_url": "https://images.unsplash.com/photo-1539008835657-9e8e9680c956?w=200&h=200&fit=crop"},
                {"type": "shoes", "name": "Black Heels", "brand": "Elegant Steps", "price": 3299, "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=200&h=200&fit=crop"},
                {"type": "accessory", "name": "Gold Clutch Bag", "brand": "Luxury Bags", "price": 4499, "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c613e?w=200&h=200&fit=crop"},
                {"type": "accessory", "name": "Gold Earrings", "brand": "Jewelry Plus", "price": 1899, "image_url": "https://images.unsplash.com/photo-1596944924617-7cfdf483c77e?w=200&h=200&fit=crop"}
            ],
            "description": "Elegant evening outfit for special occasions",
            "in_stock": True
        },
        {
            "outfit_id": "outfit_005",
            "name": "Casual Summer Look",
            "target_gender": "female",
            "target_age": "18-30", 
            "category": "casual",
            "color_scheme": "yellow",
            "total_price": 6797,
            "items": [
                {"type": "top", "name": "Yellow Summer Dress", "brand": "Sunny Style", "price": 2299, "image_url": "https://images.unsplash.com/photo-1515372039744-b8e2a921672c?w=200&h=200&fit=crop"},
                {"type": "shoes", "name": "Beige Flats", "brand": "Comfort Zone", "price": 1999, "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=200&h=200&fit=crop"},
                {"type": "accessory", "name": "Brown Sunglasses", "brand": "Sun Style", "price": 2499, "image_url": "https://images.unsplash.com/photo-1473496169904-658ba7c44d8a?w=200&h=200&fit=crop"}
            ],
            "description": "Bright and comfortable summer outfit",
            "in_stock": True
        },
        {
            "outfit_id": "outfit_006",
            "name": "Modern Office Look",
            "target_gender": "female",
            "target_age": "25-35",
            "category": "business", 
            "color_scheme": "gray",
            "total_price": 13497,
            "items": [
                {"type": "top", "name": "Gray Business Blazer", "brand": "Power Dress", "price": 4499, "image_url": "https://images.unsplash.com/photo-1584952796400-b9c0c7a87230?w=200&h=200&fit=crop"},
                {"type": "bottom", "name": "Black Formal Trousers", "brand": "Power Dress", "price": 2999, "image_url": "https://images.unsplash.com/photo-1594634319951-eb4e2a6eb4e3?w=200&h=200&fit=crop"},
                {"type": "top", "name": "White Blouse", "brand": "Office Wear", "price": 1899, "image_url": "https://images.unsplash.com/photo-1483985988355-763628e1915e?w=200&h=200&fit=crop"},
                {"type": "shoes", "name": "Black Pumps", "brand": "Elegant Steps", "price": 2599, "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=200&h=200&fit=crop"},
                {"type": "accessory", "name": "Black Handbag", "brand": "Fashion Hub", "price": 1499, "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c613e?w=200&h=200&fit=crop"}
            ],
            "description": "Professional business outfit for modern women",
            "in_stock": True
        },
        
        # Unisex Outfits
        {
            "outfit_id": "outfit_007",
            "name": "Casual Weekend Look",
            "target_gender": "unisex",
            "target_age": "18-35",
            "category": "casual",
            "color_scheme": "blue",
            "total_price": 7497,
            "items": [
                {"type": "top", "name": "Blue Denim Jacket", "brand": "Retro Style", "price": 3499, "image_url": "https://images.unsplash.com/photo-1574323387217-5d5c9e0c0746?w=200&h=200&fit=crop"},
                {"type": "top", "name": "White T-Shirt", "brand": "Comfort Wear", "price": 799, "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=200&h=200&fit=crop"},
                {"type": "bottom", "name": "Blue Denim Jeans", "brand": "Denim Co", "price": 2499, "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=200&h=200&fit=crop"},
                {"type": "shoes", "name": "White Sneakers", "brand": "Street Kicks", "price": 3999, "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=200&h=200&fit=crop"}
            ],
            "description": "Comfortable casual outfit for weekends",
            "in_stock": True
        },
        {
            "outfit_id": "outfit_008",
            "name": "Sporty Fitness Look",
            "target_gender": "unisex",
            "target_age": "16-40",
            "category": "sporty",
            "color_scheme": "black",
            "total_price": 6997,
            "items": [
                {"type": "top", "name": "Black Athletic Top", "brand": "Fit Gear", "price": 1999, "image_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=200&h=200&fit=crop"},
                {"type": "bottom", "name": "Black Sports Shorts", "brand": "Athletic Pro", "price": 1299, "image_url": "https://images.unsplash.com/photo-1594634319951-eb4e2a6eb4e3?w=200&h=200&fit=crop"},
                {"type": "shoes", "name": "White Running Shoes", "brand": "Athletic Pro", "price": 4499, "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=200&h=200&fit=crop"},
                {"type": "accessory", "name": "Sports Watch", "brand": "Time Style", "price": 1999, "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=200&h=200&fit=crop"}
            ],
            "description": "Complete fitness outfit for workouts",
            "in_stock": True
        }
    ]


def recommend_products(user_profile: dict, k: int = 8) -> list:
    """
    Recommend complete outfits based on user preferences
    """
    outfits = load_products()
    if not outfits:
        return []
    
    user_age = int(user_profile.get("age", 25))
    user_gender = user_profile.get("gender", "male").lower()
    user_color = user_profile.get("color_pref", "blue").lower()
    user_style = user_profile.get("style_pref", "casual").lower()
    user_budget = float(user_profile.get("budget", 1000))
    
    # Score outfits based on user preferences
    scored_outfits = []
    
    for outfit in outfits:
        score = 0.0
        
        # Gender match (highest weight)
        if outfit["target_gender"] == "unisex" or outfit["target_gender"] == user_gender:
            score += 50
        else:
            score -= 30  # Wrong gender
            
        # Style match (high weight)
        if outfit["category"].lower() == user_style:
            score += 40
        elif user_style in outfit["category"].lower():
            score += 20
            
        # Color match (medium weight)
        if outfit["color_scheme"].lower() == user_color:
            score += 30
        elif user_color in outfit["color_scheme"].lower():
            score += 15
            
        # Age appropriateness
        target_age = outfit.get("target_age", "18-50")
        if target_age and "-" in target_age:
            min_age, max_age = map(int, target_age.split("-"))
            if min_age <= user_age <= max_age:
                score += 20
            elif abs(user_age - min_age) <= 5 or abs(user_age - max_age) <= 5:
                score += 10
                
        # Budget fit
        outfit_price = float(outfit.get("total_price", 0))
        if outfit_price <= user_budget:
            if outfit_price <= user_budget * 0.5:
                score += 15  # Well within budget
            else:
                score += 10  # Within budget
        else:
            score -= 20  # Over budget
            
        # Stock availability
        if outfit.get("in_stock", True):
            score += 10
        else:
            score -= 30
            
        scored_outfits.append((score, outfit))
    
    # Sort by score (highest first) and return top k
    scored_outfits.sort(key=lambda x: x[0], reverse=True)
    
    recommendations = []
    for i, (score, outfit) in enumerate(scored_outfits[:k]):
        recommendations.append({
            "outfit_id": outfit["outfit_id"],
            "name": outfit["name"],
            "description": outfit["description"],
            "score": round(score, 2),
            "style": outfit["category"],
            "color_scheme": outfit["color_scheme"],
            "total_price": outfit["total_price"],
            "items": outfit["items"],
            "target_gender": outfit["target_gender"],
            "target_age": outfit["target_age"],
            "in_stock": outfit.get("in_stock", True)
        })
    
    return recommendations


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
        
        # Generate varied and personalized recommendations
        styles = ["casual", "formal", "streetwear", "business", "sporty", "elegant", "vintage", "modern"]
        colors = ["black", "white", "blue", "red", "green", "purple", "brown", "gray", "yellow", "pink"]
        
        user_style = user_profile.get("style_pref", "casual")
        user_color = user_profile.get("color_pref", "black")
        user_age = int(user_profile.get("age", 25))
        user_budget = float(user_profile.get("budget", 1000))
        
        # Create more personalized recommendations
        for i in range(k):
            # Mix user preferences with smart variety
            if i == 0:  # First recommendation: exact match
                style = user_style
                color = user_color
            elif i == 1:  # Second: same style, different color
                style = user_style
                color = colors[(colors.index(user_color) + 1) % len(colors)]
            elif i == 2:  # Third: different style, same color
                style = styles[(styles.index(user_style) + 1) % len(styles)]
                color = user_color
            else:  # Rest: smart variety based on age and budget
                # Younger users get more casual/sporty, older get more formal/business
                if user_age < 25:
                    age_styles = ["casual", "sporty", "streetwear", "modern"]
                elif user_age < 35:
                    age_styles = ["casual", "business", "modern", "elegant"]
                else:
                    age_styles = ["formal", "business", "elegant", "vintage"]
                
                # Higher budget gets more premium styles
                if user_budget > 5000:
                    budget_styles = ["formal", "elegant", "business", "vintage"]
                elif user_budget > 2000:
                    budget_styles = ["business", "modern", "casual", "elegant"]
                else:
                    budget_styles = ["casual", "sporty", "streetwear"]
                
                # Combine age and budget preferences
                preferred_styles = list(set(age_styles + budget_styles))
                style = preferred_styles[i % len(preferred_styles)]
                
                # Vary colors intelligently
                color = colors[(i * 2) % len(colors)]
            
            recs.append({
                "item_id": f"itm_{i:03d}",
                "name": f"Recommended Outfit {i+1}",
                "score": round(float(base - i * 0.02), 4),
                "style": style,
                "color": color,
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
    styles = ["casual", "formal", "streetwear", "business", "sporty", "elegant", "vintage", "modern"]
    colors = ["black", "white", "blue", "red", "green", "purple", "brown", "gray", "yellow", "pink"]
    
    user_style = user_profile.get("style_pref", "casual")
    user_color = user_profile.get("color_pref", "black")
    user_age = int(user_profile.get("age", 25))
    user_budget = float(user_profile.get("budget", 1000))
    
    for i in range(k):
        # Mix user preferences with smart variety
        if i == 0:  # First recommendation: exact match
            style = user_style
            color = user_color
        elif i == 1:  # Second: same style, different color
            style = user_style
            color = colors[(colors.index(user_color) + 1) % len(colors)]
        elif i == 2:  # Third: different style, same color
            style = styles[(styles.index(user_style) + 1) % len(styles)]
            color = user_color
        else:  # Rest: smart variety based on age and budget
            # Younger users get more casual/sporty, older get more formal/business
            if user_age < 25:
                age_styles = ["casual", "sporty", "streetwear", "modern"]
            elif user_age < 35:
                age_styles = ["casual", "business", "modern", "elegant"]
            else:
                age_styles = ["formal", "business", "elegant", "vintage"]
            
            # Higher budget gets more premium styles
            if user_budget > 5000:
                budget_styles = ["formal", "elegant", "business", "vintage"]
            elif user_budget > 2000:
                budget_styles = ["business", "modern", "casual", "elegant"]
            else:
                budget_styles = ["casual", "sporty", "streetwear"]
            
            # Combine age and budget preferences
            preferred_styles = list(set(age_styles + budget_styles))
            style = preferred_styles[i % len(preferred_styles)]
            
            # Vary colors intelligently
            color = colors[(i * 2) % len(colors)]
        
        recs.append({
            "item_id": f"itm_{i:03d}",
            "name": f"Recommended Outfit {i+1}",
            "score": round(float(score - i * 0.05), 4),
            "style": style,
            "color": color,
        })
    return recs
