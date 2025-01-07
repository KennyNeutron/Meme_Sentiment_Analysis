import os
import requests

# Google Custom Search API details
API_KEY = "YOUR_API_KEY"
SEARCH_ENGINE_ID = "YOUR_SEARCH_ENGINE_ID"

# Search query
query = "Philippine political memes"

# Directory to save images
save_path = os.path.join(os.getcwd(), "global_philippine_political_memes")
os.makedirs(save_path, exist_ok=True)


# Function to search and download images
def fetch_and_download_images(query, num_results=10):
    url = f"https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "cx": SEARCH_ENGINE_ID,
        "key": API_KEY,
        "searchType": "image",
        "num": min(num_results, 10),  # API allows a maximum of 10 results per request
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Download images
        for i, item in enumerate(data.get("items", [])):
            image_url = item["link"]
            try:
                image_response = requests.get(image_url)
                image_response.raise_for_status()

                file_path = os.path.join(save_path, f"meme_{i}.jpg")
                with open(file_path, "wb") as file:
                    file.write(image_response.content)
                print(f"Downloaded: {file_path}")
            except Exception as e:
                print(f"Error downloading image {i}: {e}")
    except Exception as e:
        print(f"Error fetching images: {e}")


# Fetch and download images
fetch_and_download_images(query, num_results=20)

# Print the save location
print(f"All memes saved in: {save_path}")
