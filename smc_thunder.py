import requests
from datetime import datetime
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# =========================
# PODACI (Hrvatska)
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
regije = {
    "Istra": 0.9,
    "Kvarner": 1.0,
    "Gorski kotar": 1.1,
    "Lika": 1.1,
    "Zagreb": 1.0,
    "Slavonija": 1.2,
    "Dalmacija": 0.95
}

# =========================
# HRVATSKI OPIS RIZIKA
# =========================
def razina_rizika(cape, cloud, precip):

    bodovi = 0

    if cape > 1500:
        bodovi += 3
    elif cape > 800:
        bodovi += 2
    elif cape > 300:
        bodovi += 1

    if cloud > 80:
        bodovi += 2
    elif cloud > 60:
        bodovi += 1

    if precip > 60:
        bodovi += 2
    elif precip > 30:
        bodovi += 1

    if bodovi <= 2:
        return "🟢 NIZAK RIZIK"
    elif bodovi <= 4:
        return "🟡 UMJEREN RIZIK"
    elif bodovi <= 6:
        return "🟠 VISOK RIZIK"
    else:
        return "🔴 VRLO VISOK RIZIK"

# =========================
# PORUKA
# =========================
poruka = f"""
🌩️ SMC THUNDER PREDIKCIJA

📅 {datetime.utcnow().date()}

🇭🇷 PREGLED HRVATSKE
- CAPE: {base_cape}
- Naoblaka: {base_cloud}%
- Vjerojatnost oborina: {base_precip}%

📍 RIZIK PO REGIJAMA:
"""

for regija, faktor in regije.items():

    cape = base_cape * faktor
    cloud = base_cloud * faktor
    precip = base_precip * faktor

    razina = razina_rizika(cape, cloud, precip)

    poruka += f"{regija:15} {razina}\n"

poruka += "\n🧠 Napomena: meteorološki model (nije izravno mjerenje munja)"

# =========================
# SLANJE NA TELEGRAM
# =========================
requests.post(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    data={"chat_id": CHAT_ID, "text": poruka}
)

print("poslano ✔")
