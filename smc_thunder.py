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
# MFG GRUPE ZA TJEDNI IZVJEŠTAJ (sve MFG grupe uključujući 9xx)
# =========================
mfg_centralne = {
    # MFG 6xx - Zagrebačka regija
    "611": ("Zagreb Centar", 45.8150, 15.9819),
    "613": ("Zagreb Pešćenica", 45.7900, 16.0000),
    "614": ("Zagreb Dubrava", 45.8400, 16.0500),
    "621": ("Zagreb Trešnjevka", 45.7850, 15.9300),
    "622": ("Zagreb Črnomerec", 45.8200, 15.9300),
    "624": ("Samobor", 45.8000, 15.7200),
    "625": ("Zabok", 46.0300, 15.9100),
    "633": ("Zagreb Trnsko", 45.7700, 15.9600),
    "634": ("Velika Gorica", 45.7100, 16.0700),
    
    # MFG 7xx - Dalmacija
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
    
    # MFG 8xx - Kvarner i Istra
    "841": ("Sušak", 45.3200, 14.4500),
    "842": ("Crikvenica", 45.1667, 14.6833),
    "843": ("Opatija", 45.3333, 14.3000),
    "844": ("Zamet", 45.3500, 14.4000),
    "845": ("Rijeka centar", 45.3271, 14.4422),
    "851": ("Pula", 44.8667, 13.8500),
    "852": ("Rovinj", 45.0833, 13.6333),
    "854": ("Umag", 45.4333, 13.5167),
    
    # MFG 8xx - Gorski kotar i Lika (nastavak)
    "831": ("Ogulin", 45.2667, 15.2167),
    "832": ("Karlovac", 45.4872, 15.5478),
    
    # MFG 9xx - Međimurje i sjeverna Hrvatska
    "911": ("Čakovec", 46.3844, 16.4342),
    "912": ("Prelog", 46.3347, 16.6164),
    "913": ("Mursko Središće", 46.5092, 16.4408),
    "914": ("Donji Kraljevec", 46.3558, 16.6517),
    "921": ("Varaždin", 46.3044, 16.3378),
    "922": ("Ivanec", 46.2233, 16.1200),
    "923": ("Lepoglava", 46.2106, 16.0356),
    "924": ("Novi Marof", 46.1647, 16.3306),
    "931": ("Koprivnica", 46.1625, 16.8278),
    "932": ("Križevci", 46.0189, 16.5425),
    "933": ("Đurđevac", 46.0397, 17.0717),
    "934": ("Novigrad Podravski", 46.0781, 16.9528),
    "941": ("Bjelovar", 45.8986, 16.8489),
    "942": ("Čazma", 45.7486, 16.6139),
    "943": ("Garešnica", 45.5744, 16.9414),
    "944": ("Daruvar", 45.5906, 17.2250),
    "951": ("Virovitica", 45.8317, 17.3839),
    "952": ("Slatina", 45.7033, 17.7025),
    "953": ("Orahovica", 45.5400, 17.8847),
    "961": ("Požega", 45.3314, 17.6744),
    "962": ("Pakrac", 45.4364, 17.1889),
    "963": ("Kutjevo", 45.4261, 17.8836),
    "964": ("Lipik", 45.4114, 17.1522),
    "971": ("Slavonski Brod", 45.1603, 18.0156),
    "972": ("Nova Gradiška", 45.2553, 17.3833),
    "973": ("Novska", 45.3406, 16.9769),
    "981": ("Osijek", 45.5550, 18.6955),
    "982": ("Đakovo", 45.3083, 18.4111),
    "983": ("Našice", 45.4886, 18.0847),
    "984": ("Valpovo", 45.6608, 18.4158),
    "985": ("Belišće", 45.6803, 18.4056),
    "991": ("Vinkovci", 45.2883, 18.8047),
    "992": ("Vukovar", 45.3500, 19.0000),
    "993": ("Županja", 45.0775, 18.6975),
    "994": ("Ilok", 45.2222, 19.3769),
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
# MODE: WEEKLY (tjedni izvještaj - sve MFG grupe)
# =========================
elif MODE == "weekly":
    print("📊 Generiram tjedni izvještaj oluja po MFG grupama...")
    print(f"Broj MFG grupa: {len(mfg_centralne)}")
    
    weekly_results = []
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    # Pomaknuto unatrag da podaci postoje (ERA5 kasni ~5 dana)
    end_date = datetime.now() - timedelta(days=7)
    start_date = end_date - timedelta(days=6)
    
    print(f"Period: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
    
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
            
            # Provjeri da podaci nisu None
            if "cape" not in data or not data["cape"]:
                print(f"MFG {mfg_id} ({naziv}): Nema podataka")
                continue
            
            oluje = []
            for dan in range(7):
                start = dan * 24
                end = start + 24
                if end > len(data["cape"]):
                    break
                
                # Filtriraj None vrijednosti
                vrijednosti = [x for x in data["cape"][start:end] if x is not None]
                if not vrijednosti:
                    continue
                    
                max_cape = max(vrijednosti)
                
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

""" + "\n".join(weekly_results) + """
📌 Legenda:
⛈️ = oluja (CAPE 800-1500)
🌩️ = jaka oluja (CAPE ≥ 1500)

📖 Izvor: ECMWF ERA5
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
