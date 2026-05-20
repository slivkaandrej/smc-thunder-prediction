import requests
from datetime import datetime
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": 45.8,
    "longitude": 16.0,
    "hourly": "cape,cloudcover,precipitation_probability",
    "past_days": 1,
    "timezone": "UTC"
}

data = requests.get(url, params=params).json()["hourly"]

cape = max(data["cape"])
cloud = max(data["cloudcover"])
precip = max(data["precipitation_probability"])

def opis(cape, cloud, precip):
    if cape > 1500 or (cloud > 80 and precip > 60):
        return "⚠️ Jaka nestabilnost – moguća grmljavina u Hrvatskoj"
    elif cape > 800:
        return "🌦️ Umjerena nestabilnost – lokalni pljuskovi i grmljavina"
    elif cape > 300:
        return "🌤️ Slaba nestabilnost – rijetki pljuskovi"
    else:
        return "☀️ Stabilno vrijeme – bez grmljavine"

message = f"""
🌩️ SMC THUNDER PREDICTION

📅 {datetime.utcnow().date()}

{opis(cape, cloud, precip)}

📊 Podaci:
- CAPE: {cape}
- Naoblaka: {cloud}%
- Oborine: {precip}%
"""

requests.post(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    data={"chat_id": CHAT_ID, "text": message}
)

print("done")
