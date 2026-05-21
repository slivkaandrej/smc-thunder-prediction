import requests
from datetime import datetime
import os

# =========================
# TELEGRAM SETTINGS
# =========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# report / alert mode
MODE = os.getenv("MODE")

# =========================
# HRVATSKE REGIJE
# =========================
regije = {
    "Zagreb": (45.8150, 15.9819),
    "Istra": (45.2400, 13.9367),
    "Kvarner": (45.3271, 14.4422),
    "Gorski kotar": (45.3986, 14.8019),
    "Lika": (44.5461, 15.3747),
    "Slavonija": (45.5550, 18.6955),
    "Dalmacija": (43.5081, 16.4402)
}

# =========================
# RIZIK GRMLJAVINE
# =========================
def rizik(cape, cloud, precip):

    score = 0

    # CAPE
    if cape > 2000:
        score += 4
    elif cape > 1500:
        score += 3
    elif cape > 800:
        score += 2
    elif cape > 300:
        score += 1

    # CLOUD
    if cloud > 90:
        score += 2
    elif cloud > 70:
        score += 1

    # PRECIP
    if precip > 80:
        score += 2
    elif precip > 50:
        score += 1

    # FINAL
    if score <= 2:
        return "NIZAK"
    elif score <= 4:
        return "UMJEREN"
    elif score <= 6:
        return "VISOK"
    else:
        return "VRLO VISOK"

# =========================
# API FETCH
# =========================
results = []
alert_zones = []

for ime, (lat, lon) in regije.items():

    try:

        url = "https://api.open-meteo.com/v1/forecast"

        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "cape,cloudcover,precipitation_probability",
            "forecast_days": 1,
            "timezone": "Europe/Zagreb"
        }

        r = requests.get(url, params=params, timeout=30)

        data = r.json()["hourly"]

        cape = max(data["cape"])
        cloud = max(data["cloudcover"])
        precip = max(data["precipitation_probability"])

        level = rizik(cape, cloud, precip)

        # emoji
        if level == "NIZAK":
            emoji = "🟢"
        elif level == "UMJEREN":
            emoji = "🟡"
        elif level == "VISOK":
            emoji = "🟠"
        else:
            emoji = "🔴"

        results.append(f"{emoji} {ime:15} {level}")

        if level == "VRLO VISOK":
            alert_zones.append(ime)

        print(
            f"{ime} | CAPE={cape} CLOUD={cloud} PRECIP={precip} => {level}"
        )

    except Exception as e:

        print("ERROR:", ime, e)

# =========================
# REPORT MODE
# =========================
if MODE == "report":

    hour = datetime.now().hour

    if hour < 12:
        naslov = "🌅 JUTARNJI IZVJEŠTAJ"
    else:
        naslov = "🌤️ POPODNEVNI IZVJEŠTAJ"

    msg = f"""
╔══════════════════╗
   🌩️ SMC THUNDER
╚══════════════════╝

{naslov}

📅 {datetime.now().strftime("%d.%m.%Y")}

📍 STANJE PO REGIJAMA

"""

    msg += "\n".join(results)

    msg += """

━━━━━━━━━━━━━━━━━━
🧠 SMC Meteorološki Model
⚡ Automatski Storm Monitoring
━━━━━━━━━━━━━━━━━━
"""

# =========================
# ALERT MODE
# =========================
elif MODE == "alert":

    # nema alarma
    if not alert_zones:
        print("Nema alarma.")
        exit()

    msg = f"""
🚨🚨🚨 SMC THUNDER ALERT 🚨🚨🚨

🔴 VRLO VISOK RIZIK GRMLJAVINE

📍 POGOĐENE REGIJE:

"""

    for z in alert_zones:
        msg += f"⚡ {z}\n"

    msg += """

🌩️ Moguće:
• jaka grmljavina
• lokalni pljuskovi
• pojačan električni aktivitet

⏰ Sustav provjerava svakih 30 minuta
"""

# =========================
# TELEGRAM SEND
# =========================
requests.post(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    data={
        "chat_id": CHAT_ID,
        "text": msg
    }
)

print("✔ Poruka poslana")
