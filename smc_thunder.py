import requests
from datetime import datetime
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MODE = os.getenv("MODE")

regije = {
    "Zagreb": (45.81, 15.98),
    "Istra": (45.24, 13.94),
    "Rijeka": (45.33, 14.44),
    "Gorski kotar": (45.40, 14.80),
    "Lika": (44.55, 15.37),
    "Slavonija": (45.56, 18.70),
    "Dalmacija": (43.51, 16.44)
}

def rizik(cape, cloud, precip):
    score = 0

    if cape > 1500: score += 3
    elif cape > 800: score += 2
    elif cape > 300: score += 1

    if cloud > 80: score += 2
    elif cloud > 60: score += 1

    if precip > 60: score += 2
    elif precip > 30: score += 1

    if score <= 2:
        return "NIZAK"
    elif score <= 4:
        return "UMJEREN"
    elif score <= 6:
        return "VISOK"
    else:
        return "VRLO VISOK"

results = []
alert_zones = []

for ime, (lat, lon) in regije.items():

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "cape,cloudcover,precipitation_probability",
        "past_days": 1,
        "timezone": "UTC"
    }

    data = requests.get(url, params=params).json()["hourly"]

    cape = max(data["cape"])
    cloud = max(data["cloudcover"])
    precip = max(data["precipitation_probability"])

    level = rizik(cape, cloud, precip)

    results.append(f"{ime:15} {level}")

    if level == "VRLO VISOK":
        alert_zones.append(ime)

# =========================
# MODE LOGIKA
# =========================

if MODE == "report":

    msg = "🌩️ SMC JUTARNJI IZVJEŠTAJ\n\n"
    msg += f"📅 {datetime.utcnow().date()}\n\n"

    msg += "📍 REGIJE:\n"
    msg += "\n".join(results)

elif MODE == "alert":

    if not alert_zones:
        print("No alert → exit")
        exit()

    msg = "🚨 SMC THUNDER ALERT\n\n"
    msg += "🔴 VRLO VISOK RIZIK\n\n"
    msg += "📍 Pogođeno:\n"
    msg += "\n".join(alert_zones)

# =========================
# SEND
# =========================
requests.post(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    data={"chat_id": CHAT_ID, "text": msg}
)

print("sent")
