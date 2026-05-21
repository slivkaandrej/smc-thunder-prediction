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
# REGIJE ZA BRZE IZVJEŠTAJE (report i alert)
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
# MFG GRUPE ZA TJEDNI IZVJEŠTAJ (samo centralna područja - BRŽE)
# =========================
mfg_centralne = {
    "611": ("Zagreb Centar", 45.8150, 15.9819),
    "613": ("Pešćenica", 45.7900, 16.0000),
    "614": ("Dubrava", 45.8400, 16.0500),
    "621": ("Trešnjevka", 45.7850, 15.9300),
    "622": ("Črnomerec", 45.8200, 15.9300),
    "624": ("Samobor", 45.8000, 15.7200),
    "625": ("Zabok", 46.0300, 15.9100),
    "633": ("Trnsko", 45.7700, 15.9600),
    "634": ("Velika Gorica", 45.7100, 16.0700),
    "711": ("Dubrovnik", 42.6507, 18.0944),
    "713": ("Korčula", 42.9600, 17.1300),
    "715": ("Omiš", 43.4400, 16.6900),
    "721": ("Split", 43.5081, 16.4402),
    "722": ("Solin", 43.5333, 16.5000),
    "723": ("Kaštela", 43.5500, 16.3500),
    "724": ("Sinj", 43.7000, 16.6333),
    "725": ("Istok Splita", 43.5100, 16.4800),
    "731": ("Zadar centar", 44.1194, 15.2314),
    "733": ("Drniš", 43.8667, 16.1500),
    "734": ("Biograd", 43.9333, 15.4333),
    "735": ("Šibenik", 43.7350, 15.8957),
    "841": ("Sušak", 45.3200, 14.4500),
    "842": ("Crikvenica", 45.1667, 14.6833),
    "843": ("Opatija", 45.3333, 14.3000),
    "844": ("Zamet", 45.3500, 14.4000),
    "845": ("Rijeka centar", 45.3271, 14.4422),
    "851": ("Pula", 44.8667, 13.8500),
    "852": ("Rovinj", 45.0833, 13.6333),
    "854": ("Umag", 45.4333, 13.5167),
    "831": ("Ogulin", 45.2667, 15.2167),
    "832": ("Karlovac", 45.4872, 15.5478),
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
# MODE: REPORT (dnevni izvještaj - brzo, 7 regija)
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
    alert_regije = []
    
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
                alert_regije.append(ime)
            
            print(f"{ime:15} | CAPE={cape:4.0f} => {level}")
        except Exception as e:
            print(f"ERROR - {ime}: {e}")

    if not alert_regije:
        print("✅ Nema regija s vrlo visokim rizikom - ne šaljem poruku")
        sys.exit(0)
    
    msg = "🚨 SMC ALERT 🚨\n\nVRLO VISOK RIZIK:\n\n"
    msg += "\n".join([f"⚡ {r}" for r in alert_regije])
    msg += f"\n\n📅 {datetime.now().strftime('%d.%m.%Y. %H:%M')}"

# =========================
# MODE: WEEKLY (tjedni izvještaj - MFG grupe, brza verzija)
# =========================
elif MODE == "weekly":
    print("📊 Generiram tjedni izvještaj oluja po MFG grupama (brza verzija)...")
    
    weekly_results = []
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    # ERA5 podaci kasne ~2-5 dana
    end_date = datetime.now() - timedelta(days=2)
    start_date = end_date - timedelta(days=6)
    
    print(f"Period: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
    print(f"Broj MFG grupa: {len(mfg_centralne)}")
    
    # Dohvati datume
    datumi = []
    for i in range(7):
        dan = start_date + timedelta(days=i)
        datumi.append(dan.strftime("%d.%m."))
    
    for mfg_id, (naziv, lat, lon) in mfg_centralne.items():
        try:
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "hourly": "cape",
                "timezone": "Europe/Zagreb"
            }
            
            r = requests.get(url, params=params, timeout=30)
            data = r.json()["hourly"]
            
            oluje = []
            for dan in range(7):
                start = dan * 24
                end = start + 24
                if end > len(data["cape"]):
                    break
                max_cape = max(data["cape"][start:end])
                
                if max_cape >= 1500:
                    oluje.append(f"   • {datumi[dan]} 🌩️ JAKA OLUJA (CAPE {max_cape:.0f})")
                elif max_cape >= 800:
                    oluje.append(f"   • {datumi[dan]} ⛈️ OLUJA (CAPE {max_cape:.0f})")
            
            if oluje:
                weekly_results.append(f"🔵 MFG {mfg_id} ({naziv}):")
                weekly_results.extend(oluje)
                weekly_results.append("")
            else:
                weekly_results.append(f"🟢 MFG {mfg_id} ({naziv}): ✅ Nema oluja")
                weekly_results.append("")
            
            print(f"MFG {mfg_id} ({naziv}): {len(oluje)} dana s olujom")
            
        except Exception as e:
            print(f"ERROR - MFG {mfg_id}: {e}")
            weekly_results.append(f"⚠️ MFG {mfg_id} ({naziv}): Greška pri dohvatu podataka")
            weekly_results.append("")
    
    msg = f"""📊 SMC THUNDER - TJEDNI IZVJEŠTAJ OLUJA

📅 {datetime.now().strftime("%d.%m.%Y")}
📆 Razdoblje: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}
⚠️ Napomena: Podaci kasne ~2-5 dana (ERA5 reanalysis)

""" + "\n".join(weekly_results) + """
📌 Legenda:
⛈️ = oluja (CAPE 800-1500)
🌩️ = jaka oluja (CAPE ≥ 1500)

📖 Izvor: ECMWF ERA5 (kombinacija mjerenja i satelita)
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
