import requests
import os

# Create the sample1 directory if it doesn't exist
os.makedirs("tryon_datasets/sample1", exist_ok=True)

# Download a sample body image (Unsplash)
body_url = "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=facearea&w=400&h=600"
body_path = "tryon_datasets/sample1/body.jpg"
with open(body_path, "wb") as f:
    f.write(requests.get(body_url).content)

# Download a sample garment PNG (transparent background)
garment_url = "https://pngimg.com/uploads/tshirt/tshirt_PNG5446.png"
garment_path = "tryon_datasets/sample1/garment.png"
with open(garment_path, "wb") as f:
    f.write(requests.get(garment_url).content)

print("Sample images downloaded to tryon_datasets/sample1/")
