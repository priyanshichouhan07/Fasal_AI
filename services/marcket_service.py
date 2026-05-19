import requests
import os

API_KEY = os.getenv("AGMARKNET_API_KEY")

def get_crop_price(crop):

    url = f"https://api.data.gov.in/resource/YOUR_RESOURCE_ID?api-key={API_KEY}&format=json"

    response = requests.get(url)

    return response.json()