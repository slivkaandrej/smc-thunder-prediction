import requests
from datetime import datetime
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# =========================
# LOKACIJE REGIJA (HRVATSKA)
# =========================
regije = {
    "Zagreb": (45.8150, 15.9819),
    "Istra (Pazin)": (45.2400, 13.9367),
    "Rijeka (Kvarner)": (45.3271, 14.4422),
    "Gorski kotar (Delnice)": (45.3986, 14.8019),
    "Lika (Gospić)": (44.5461, 15.3747),
    "Slavonija (Osijek)": (45.5550, 18.6955),
    "Dalmacija (Split)": (43.5081, 16.4402)
}

# =========================
# FUNKCIJA RIZIKA
# =========================
def razina_rizika(cape, cloud, precip):

    score = 0

    if cape > 1500:
        score += 3
    elif cape > 800:
        score += 2
    elif cape > 300:
        score += 1

    if cloud > 80:
        score += 2
    elif cloud > 60:
        score += 1

    if precip > 60:
        score += 2
    elif precip > 30:
        score += 1

    if score <= 2:
        return "🟢 NIZAK"
    elif score <= 4:
        return "🟡 UMJEREN"
    elif score <= 6:
        return "🟠 VISOK"
    else:
        return "🔴 VRLO VISOK"

# =========================
# PORUKA
# =========================
poruka = f"""
🌩️ SMC THUNDER PREDIKCIJA v2 (REAL REGIJE)

📅 {datetime.utcnow().date()}

📍 REGIONALNI PREGLED:
"""

# =========================
# PO REGIJAMA (REAL DATA)
# =========================
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

    rizik = razina_rizika(cape, cloud, precip)

    poruka += f"{ime:25} {rizik}\n"

    print(f"{ime} -> CAPE {cape}, CLOUD {cloud}, PRECIP {precip}")

# =========================
# SLANJE NA TELEGRAM
# =========================
requests.post(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    data={"chat_id": CHAT_ID, "text": poruka}
)

print("poslano ✔")
