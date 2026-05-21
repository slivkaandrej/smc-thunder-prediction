import requests
from datetime import datetime, timedelta
import os
import sys

# =========================
# TELEGRAM SETTINGS
# =========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MODE = os.getenv("MODE")

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
print(f"\n{'='*50}")
print(f"Pokrećem SMC Thunder - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Mod: {MODE}")
print(f"{'='*50}\n")

# =========================
# MODE: REPORT (dnevni izvještaj)
# =========================
if MODE == "report":
    results = []
    
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
            print(f"{ime:15} | CAPE={cape:4.0f} CLOUD={cloud:3.0f}% PRECIP={precip:3.0f}% => {level}")
        except Exception as e:
            print(f"ERROR - {ime}: {e}")

    hour = datetime.now().hour
    naslov = "🌅 JUTARNJI IZVJEŠTAJ" if hour < 12 else "🌤️ POPODNEVNI IZVJEŠTAJ"
    
    msg = f"""🌩️ SMC THUNDER

{naslov}
📅 {datetime.now().strftime("%d.%m.%Y. %H:%M")}

📍 REGIJE:

""" + "\n".join(results)

# =========================
# MODE: ALERT (upozorenje - samo VRLO VISOK)
# =========================
elif MODE == "alert":
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

            if level == "VRLO VISOK":
                alert_zones.append(ime)
            
            print(f"{ime:15} | CAPE={cape:4.0f} => {level}")
        except Exception as e:
            print(f"ERROR - {ime}: {e}")

    if not alert_zones:
        print("✅ Nema zona s vrlo visokim rizikom - ne šaljem poruku")
        sys.exit(0)
    
    msg = "🚨 SMC ALERT 🚨\n\nVRLO VISOK RIZIK:\n\n"
    msg += "\n".join([f"⚡ {z}" for z in alert_zones])
    msg += f"\n\n📅 {datetime.now().strftime('%d.%m.%Y. %H:%M')}"

# =========================
# MODE: WEEKLY (tjedni izvještaj - SAMO OLUJE)
# =========================
elif MODE == "weekly":
    print("📊 Generiram tjedni izvještaj oluja...")
    
    weekly_results = []
    url = "https://api.open-meteo.com/v1/forecast"
    
    for ime, (lat, lon) in regije.items():
        try:
            params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": "cape",
                "past_days": 7,
                "forecast_days": 0,
                "timezone": "Europe/Zagreb"
            }
            
            r = requests.get(url, params=params, timeout=30)
            data = r.json()["hourly"]
            
            # Dohvati datume za zadnjih 7 dana
            dani = []
            for i in range(7):
                dan = datetime.now().replace(hour=0, minute=0, second=0) - timedelta(days=6-i)
                dani.append(dan.strftime("%d.%m."))
            
            # Sakupi samo dane s olujom
            oluje = []
            for dan in range(7):
                start = dan * 24
                end = start + 24
                max_cape = max(data["cape"][start:end])
                
                if max_cape >= 1500:
                    oluje.append(f"   {dani[dan]} 🌩️ JAKA OLUJA (CAPE {max_cape:.0f})")
                elif max_cape >= 800:
                    oluje.append(f"   {dani[dan]} ⛈️ OLUJA (CAPE {max_cape:.0f})")
            
            # Dodaj u rezultat
            if oluje:
                weekly_results.append(f"📍 {ime}:")
                weekly_results.extend(oluje)
                weekly_results.append("")
            else:
                weekly_results.append(f"📍 {ime}: Nema oluja u zadnjih 7 dana")
                weekly_results.append("")
            
            print(f"{ime}: {len(oluje)} dana s olujom")
            
        except Exception as e:
            print(f"ERROR - {ime}: {e}")
    
    msg = f"""📊 SMC THUNDER - TJEDNI IZVJEŠTAJ OLUJA

📅 {datetime.now().strftime("%d.%m.%Y")}
📆 Zadnjih 7 dana

""" + "\n".join(weekly_results) + """
📌 Legenda:
⛈️ = oluja (CAPE 800-1500)
🌩️ = jaka oluja (CAPE ≥ 1500)
"""

else:
    print(f"❌ Nepoznat MODE: {MODE}")
    sys.exit(1)

# =========================
# SEND TELEGRAM
# =========================
if not TOKEN or not CHAT_ID:
    print("❌ Missing environment variables:")
    print(f"   TOKEN: {'SET' if TOKEN else 'MISSING'}")
    print(f"   CHAT_ID: {'SET' if CHAT_ID else 'MISSING'}")
    sys.exit(1)

print("\n📤 Šaljem Telegram poruku...")

try:
    resp = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg},
        timeout=10
    )
    print(f"📡 Status: {resp.status_code}")
    if resp.status_code == 200:
        print("✅ Poruka uspješno poslana!")
    else:
        print(f"❌ Greška: {resp.text}")
except Exception as e:
    print(f"❌ Greška pri slanju: {e}")
    sys.exit(1)

print("\n✅ SMC Thunder završio\n")
