import requests
from datetime import datetime
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# =========================
# PODACI (centralna HR)
# =========================
url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": 45.8,
    "longitude": 16.0,
    "hourly": "cape,cloudcover,precipitation_probability",
    "past_days": 1,
    "timezone": "UTC"
}

data = requests.get(url, params=params).json()["hourly"]

base_cape = max(data["cape"])
base_cloud = max(data["cloudcover"])
base_precip = max(data["precipitation_probability"])

# =========================
# REGIJE HRVATSKE
# =========================
regions = {
    "Istra": 0.9,
    "Kvarner": 1.0,
    "Gorski kotar": 1.1,
    "Lika": 1.1,
    "Zagreb": 1.0,
    "Slavonija": 1.2,
    "Dalmacija": 0.95
}

# =========================
# FUNKCIJA RIZIKA
# =========================
def risk(cape, cloud, precip):

    score = 0

    if cape > 1500: score += 3
    elif cape > 800: score += 2
    elif cape > 300: score += 1

    if cloud > 80: score += 2
    elif cloud > 60: score += 1

    if precip > 60: score += 2
    elif precip > 30: score += 1

    if score <= 2:
        return "🟢 LOW"
    elif score <= 4:
        return "🟡 MODERATE"
    elif score <= 6:
        return "🟠 HIGH"
    else:
        return "🔴 SEVERE"

# =========================
# MESSAGE
# =========================
msg = f"🌩️ SMC THUNDER PREDICTION\n\n📅 {datetime.utcnow().date()}\n\n"

msg += "🇭🇷 HRVATSKA OVERVIEW\n"
msg += f"- CAPE: {base_cape}\n"
msg += f"- Naoblaka: {base_cloud}%\n"
msg += f"- Oborine: {base_precip}%\n\n"

msg += "📍 REGIJE:\n"

for region, factor in regions.items():

    cape = base_cape * factor
    cloud = base_cloud * factor
    precip = base_precip * factor

    level = risk(cape, cloud, precip)

    msg += f"{region:15} {level}\n"

msg += "\n🧠 Model: meteorološka procjena (nije direktna munja)\n"

# =========================
# SEND TELEGRAM
# =========================
requests.post(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    data={"chat_id": CHAT_ID, "text": msg}
)

print("sent")
