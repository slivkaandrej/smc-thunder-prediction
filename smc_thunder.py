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
# MFG GRUPE ZA TJEDNI IZVJEŠTAJ (sva područja)
# =========================
sve_mfg_grupe = {
    # Sjeverna Hrvatska (9xx)
    "942": ("Varaždin", 46.3044, 16.3378),
    "944": ("Koprivnica", 46.1625, 16.8278),
    "945": ("Bjelovar", 45.8986, 16.8489),
    "951": ("Sisak", 45.4851, 16.3787),
    "952": ("Kutina", 45.4750, 16.7819),
    "953": ("Daruvar", 45.5906, 17.2250),
    "953": ("Požega", 45.3314, 17.6744),  # Dodano Požega
    "954": ("Slavonski Brod", 45.1603, 18.0156),
    "962": ("Osijek", 45.5550, 18.6955),
    "962": ("Darda", 45.6261, 18.6997),  # Dodano Darda
    "962": ("Bilje", 45.6069, 18.7439),  # Dodano Bilje
    "962": ("Beli Manastir", 45.7700, 18.6036),  # Dodano Beli Manastir
    "963": ("Slatina", 45.7033, 17.7025),
    "964": ("Vinkovci", 45.2883, 18.8047),  # Dodano Vinkovci
    "964": ("Ilok", 45.2222, 19.3769),  # Dodano Ilok
    
    # Kvarner i Istra (8xx)
    "841": ("Krk", 45.0260, 14.5780),
    "842": ("Crikvenica", 45.1667, 14.6833),
    "843": ("Opatija", 45.3333, 14.3000),
    "845": ("Rijeka", 45.3271, 14.4422),
    "851": ("Pula", 44.8667, 13.8500),
    "852": ("Rovinj", 45.0833, 13.6333),
    "854": ("Umag", 45.4333, 13.5167),
    
    # Gorski kotar i Lika (8xx)
    "831": ("Ogulin", 45.2667, 15.2167),
    "832": ("Karlovac", 45.4872, 15.5478),
    
    # Dalmacija (7xx)
    "711": ("Dubrovnik", 42.6507, 18.0944),
    "713": ("Korčula", 42.9600, 17.1300),
    "715": ("Imotski", 43.4400, 17.2100),
    "721": ("Split", 43.5081, 16.4402),
    "722": ("Hvar", 43.1725, 16.4428),
    "723": ("Trogir", 43.5167, 16.2500),
    "724": ("Sinj", 43.7000, 16.6333),
    "725": ("Vis", 43.0600, 16.1800),
    "731": ("Zadar", 44.1194, 15.2314),
    "733": ("Knin", 44.0500, 16.2000),
    "734": ("Biograd", 43.9333, 15.4333),
    "735": ("Šibenik", 43.7350, 15.8957),
    
    # Zagrebačka regija
    "624": ("Samobor", 45.8000, 15.7200),
    "634": ("Velika Gorica", 45.7100, 16.0700),
    "611": ("Zagreb Centar", 45.8150, 15.9819),
    "613": ("Zagreb Pešćenica", 45.7900, 16.0000),
    "614": ("Zagreb Dubrava", 45.8400, 16.0500),
    "621": ("Zagreb Trešnjevka", 45.7850, 15.9300),
    "622": ("Zagreb Črnomerec", 45.8200, 15.9300),
    "633": ("Zagreb Trnsko", 45.7700, 15.9600),
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
# MODE: WEEKLY (tjedni izvještaj - SAMO PODRUČJA S OLUJAMA)
# =========================
elif MODE == "weekly":
    print("📊 Generiram tjedni izvještaj oluja - SAMO područja s olujama...")
    print(f"Broj MFG grupa: {len(sve_mfg_grupe)}")
    
    # Gledamo zadnjih 7 dana (od jučer unazad)
    end_date = datetime.now() - timedelta(days=1)   # jučer
    start_date = end_date - timedelta(days=6)       # 7 dana unazad (uključujući jučer)
    
    print(f"Period: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
    
    # Dohvati datume
    datumi = []
    for i in range(7):
        dan = start_date + timedelta(days=i)
        datumi.append(dan.strftime("%d.%m."))
    
    # Rječnik za rezultate (samo tamo gdje ima oluja)
    rezultati_sa_olujama = {}
    
    for mfg_id, (naziv, lat, lon) in sve_mfg_grupe.items():
        try:
            # Koristimo forecast API s past_days za svježe podatke
            url = "https://api.open-meteo.com/v1/forecast"
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
            
            if "cape" not in data or not data["cape"]:
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
            
            # Spremi samo ako ima oluja
            if oluje:
                # Ako već postoji ovaj MFG u rezultatima, spoji oluje
                if mfg_id in rezultati_sa_olujama:
                    rezultati_sa_olujama[mfg_id]["oluje"].extend(oluje)
                else:
                    rezultati_sa_olujama[mfg_id] = {
                        "naziv": naziv,
                        "oluje": oluje
                    }
            
            print(f"MFG {mfg_id} ({naziv}): {len(oluje)} dana s olujom")
            
        except Exception as e:
            print(f"ERROR - MFG {mfg_id}: {e}")
    
    # Kreiraj poruku samo s područjima koja su imala oluje
    if rezultati_sa_olujama:
        msg_parts = []
        for mfg_id, podaci in rezultati_sa_olujama.items():
            # Ukloni duplikate oluja (isti dan, ista poruka)
            jedinstvene_oluje = list(dict.fromkeys(podaci['oluje']))
            msg_parts.append(f"🔵 MFG {mfg_id} ({podaci['naziv']}):")
            msg_parts.extend(jedinstvene_oluje)
            msg_parts.append("")
        
        msg = f"""📊 SMC THUNDER - TJEDNI IZVJEŠTAJ OLUJA

📅 {datetime.now().strftime("%d.%m.%Y")}
📆 Razdoblje: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}
⚠️ Prikazana su samo područja gdje je bilo oluja (CAPE ≥ 800)

""" + "\n".join(msg_parts) + """
📌 Legenda:
⛈️ = oluja (CAPE 800-1500)
🌩️ = jaka oluja (CAPE ≥ 1500)
"""
    else:
        msg = f"""📊 SMC THUNDER - TJEDNI IZVJEŠTAJ OLUJA

📅 {datetime.now().strftime("%d.%m.%Y")}
📆 Razdoblje: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}

✅ U proteklih 7 dana NIJE BILO OLUJA ni na jednom području (CAPE < 800)
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
