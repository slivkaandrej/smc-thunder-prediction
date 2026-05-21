import requests
from datetime import datetime
import os
import sys

# =========================
# TELEGRAM SETTINGS
# =========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MODE = os.getenv("MODE")

# =========================
# PROVJERA ZA AUTOMATSKO I RUČNO POKRETANJE
# =========================
# Ako je ručno pokretanje (workflow_dispatch), uvijek šalji
is_manual = os.getenv("GITHUB_EVENT_NAME") == "workflow_dispatch"

if MODE == "report" and not is_manual:
    now = datetime.now()
    # Samo za automatske runove provjeri vrijeme
    if now.hour == 7 and now.minute <= 20:
        print(f"✅ Jutarnji report - šaljem u {now.hour}:{now.minute:02d}")
    elif now.hour == 14 and now.minute <= 20:
        print(f"✅ Popodnevni report - šaljem u {now.hour}:{now.minute:02d}")
    else:
        print(f"⏭️ Preskačem automatski report u {now.hour}:{now.minute:02d} (samo u 7:00-7:20 i 14:00-14:20)")
        sys.exit(0)
elif MODE == "report" and is_manual:
    print("✅ Ručno pokretanje - šaljem report odmah!")

# =========================
# REGIJE
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
# RIZIK FUNKCIJA
# =========================
def rizik(cape, cloud, precip):
    score = 0

    if cape > 2000:
        score += 4
    elif cape > 1500:
        score += 3
    elif cape > 800:
        score += 2
    elif cape > 300:
        score += 1

    if cloud > 90:
        score += 2
    elif cloud > 70:
        score += 1

    if precip > 80:
        score += 2
    elif precip > 50:
        score += 1

    if score <= 2:
        return "NIZAK"
    elif score <= 4:
        return "UMJEREN"
    elif score <= 6:
        return "VISOK"
    else:
        return "VRLO VISOK"

# =========================
# MAIN
# =========================
results = []
alert_zones = []

print(f"\n{'='*50}")
print(f"Pokrećem SMC Thunder - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Mod: {MODE}")
print(f"Ručno pokretanje: {is_manual}")
print(f"{'='*50}\n")

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

        emoji = "🟢" if level == "NIZAK" else "🟡" if level == "UMJEREN" else "🟠" if level == "VISOK" else "🔴"

        results.append(f"{emoji} {ime:15} {level}")

        if level == "VRLO VISOK":
            alert_zones.append(ime)

        print(f"{ime:15} | CAPE={cape:4.0f} CLOUD={cloud:3.0f}% PRECIP={precip:3.0f}% => {level}")

    except Exception as e:
        print(f"ERROR - {ime}: {e}")

print(f"\n{'-'*50}")
print(f"Ukupno regija: {len(results)}")
print(f"Alert zona: {len(alert_zones)}")
print(f"{'-'*50}\n")

# =========================
# MSG BUILD
# =========================
msg = ""

if MODE == "report":
    hour = datetime.now().hour
    naslov = "🌅 JUTARNJI IZVJEŠTAJ" if hour < 12 else "🌤️ POPODNEVNI IZVJEŠTAJ"

    msg = f"""🌩️ SMC THUNDER

{naslov}
📅 {datetime.now().strftime("%d.%m.%Y. %H:%M")}

📍 REGIJE:

""" + "\n".join(results)

elif MODE == "alert":
    if not alert_zones:
        print("✅ Alert check: Nema zona s vrlo visokim rizikom")
        print("📤 Ne šaljem Telegram poruku")
        sys.exit(0)
    else:
        msg = "🚨 SMC ALERT 🚨\n\nVRLO VISOK RIZIK:\n\n"
        msg += "\n".join([f"⚡ {z}" for z in alert_zones])
        msg += f"\n\n📅 {datetime.now().strftime('%d.%m.%Y. %H:%M')}"

else:
    print(f"❌ MODE nije postavljen ili je neispravan: {MODE}")
    sys.exit(1)

# =========================
# SEND TELEGRAM
# =========================
if not TOKEN or not CHAT_ID:
    print("❌ Missing environment variables:")
    print(f"   TOKEN: {'SET' if TOKEN else 'MISSING'}")
    print(f"   CHAT_ID: {'SET' if CHAT_ID else 'MISSING'}")
    sys.exit(1)

print("📤 Šaljem Telegram poruku...")
print(f"Poruka:\n{msg}\n")

try:
    resp = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": msg
        },
        timeout=10
    )

    print(f"📡 Status: {resp.status_code}")
    
    if resp.status_code == 200:
        print("✅ Poruka uspješno poslana!")
        print(f"Response: {resp.json()}")
    else:
        print(f"❌ Greška: {resp.text}")
        
except Exception as e:
    print(f"❌ Greška pri slanju: {e}")
    sys.exit(1)

print("\n✅ SMC Thunder završio\n")
