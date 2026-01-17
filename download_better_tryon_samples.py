# Downloaded by GitHub Copilot for demo purposes
# This script replaces the sample body and garment images with better demo images for try-on
import requests

# URLs for demo images (royalty-free, front-facing, transparent background for garment)
BODY_URL = "https://images.pexels.com/photos/1130626/pexels-photo-1130626.jpeg?auto=compress&w=400&h=600&fit=crop"  # Person in plain t-shirt
GARMENT_URL = "https://pngimg.com/uploads/tshirt/tshirt_PNG5429.png"  # Bright yellow t-shirt

BODY_PATH = "tryon_datasets/sample1/body.jpg"
GARMENT_PATH = "tryon_datasets/sample1/garment.png"

def download_image(url, path):
    r = requests.get(url)
    r.raise_for_status()
    with open(path, 'wb') as f:
        f.write(r.content)
    print(f"Downloaded {path}")

def main():
    download_image(BODY_URL, BODY_PATH)
    download_image(GARMENT_URL, GARMENT_PATH)
    print("Demo images updated. You can now test the try-on feature.")

if __name__ == "__main__":
    main()
