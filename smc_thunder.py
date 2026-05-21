import requests
from datetime import datetime
import os
import sys

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MODE = os.getenv("MODE")

# ZA TEST - isključi vremensku provjeru
print("🔧 TEST MODE: Slanje bez provjere vremena!")

regije = {
    "Zagreb": (45.8150, 15.9819),
    "Istra": (45.2400, 13.9367),
    "Kvarner": (45.3271, 14.4422),
    "Gorski kotar": (45.3986, 14.8019),
    "Lika": (44.5461, 15.3747),
    "Slavonija": (45.5550, 18.6955),
    "Dalmacija": (43.5081, 16.4402)
}

def rizik(cape, cloud, precip):
    score = 0
    if cape > 2000: score += 4
    elif cape > 1500: score += 3
    elif cape > 800: score += 2
    elif cape > 300: score += 1
    if cloud > 90: score += 2
    elif cloud > 70: score += 1
    if precip > 80: score += 2
    elif precip > 50: score += 1
    if score <= 2: return "NIZAK"
    elif score <= 4: return "UMJEREN"
    elif score <= 6: return "VISOK"
    else: return "VRLO VISOK"

results = []
print(f"\nPokrećem SMC Thunder - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Mod: {MODE}\n")

for ime, (lat, lon) in regije.items():
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "cape,cloudcover,precipitation_probability",
            "forecast_days": 1,
            "timezone": "Europe/Zagreb"
        }
        r = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=30)
        data = r.json()["hourly"]
        cape = max(data["cape"])
        cloud = max(data["cloudcover"])
        precip = max(data["precipitation_probability"])
        level = rizik(cape, cloud, precip)
        emoji = "🟢" if level == "NIZAK" else "🟡" if level == "UMJEREN" else "🟠" if level == "VISOK" else "🔴"
        results.append(f"{emoji} {ime:15} {level}")
        print(f"{ime:15} | CAPE={cape:4.0f} CLOUD={cloud:3.0f}% PRECIP={precip:3.0f}% => {level}")
    except Exception as e:
        print(f"ERROR - {ime}: {e}")

if MODE == "report":
    naslov = "🧪 TESTNI IZVJEŠTAJ (automatski cron)"
    msg = f"""🌩️ SMC THUNDER

{naslov}
📅 {datetime.now().strftime("%d.%m.%Y. %H:%M")}

📍 REGIJE:

""" + "\n".join(results)
else:
    msg = f"Alert check: {results}"

if not TOKEN or not CHAT_ID:
    print("❌ Missing env vars")
    sys.exit(1)

print("\n📤 Šaljem Telegram poruku...")
resp = requests.post(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    data={"chat_id": CHAT_ID, "text": msg},
    timeout=10
)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    print("✅ Poruka poslana!")
else:
    print(f"❌ Greška: {resp.text}")
