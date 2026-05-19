import requests

def get_weather(lat, lon):

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"

    data = requests.get(url).json()

    return data