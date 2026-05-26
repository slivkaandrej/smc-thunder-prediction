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
# MFG GRUPE ZA TJEDNI IZVJEŠTAJ
# =========================
sve_mfg_grupe = {
    # Sjeverna Hrvatska (9xx)
    "942": ("Varaždin", 46.3044, 16.3378),
    "944": ("Koprivnica", 46.1625, 16.8278),
    "945": ("Bjelovar", 45.8986, 16.8489),
    "951": ("Sisak", 45.4851, 16.3787),
    "952": ("Kutina", 45.4750, 16.7819),
    "953": ("Daruvar", 45.5906, 17.2250),
    "954": ("Slavonski Brod", 45.1603, 18.0156),
    "962": ("Osijek", 45.5550, 18.6955),
    "963": ("Slatina", 45.7033, 17.7025),
    "964": ("Vinkovci", 45.2883, 18.8047),
    
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
# RIZIK FUNKCIJA (s LPI)
# =========================
def rizik(cape, lpi):
    score = 0
    
    # CAPE bodovi
    if cape > 2000:
        score += 4
    elif cape > 1500:
        score += 3
    elif cape > 800:
        score += 2
    elif cape > 300:
        score += 1
    
    # LPI bodovi (lightning potential)
    if lpi > 80:
        score += 3
    elif lpi > 60:
        score += 2
    elif lpi > 40:
        score += 1
    
    if score <= 2:
        return "NIZAK"
    elif score <= 4:
        return "UMJEREN"
    elif score <= 6:
        return "VISOK"
    else:
        return "VRLO VISOK"

def lpi_tekst(lpi):
    if lpi >= 80:
        return "⚡⚡ GRMLJAVINA VRLO VJEROJATNA ⚡⚡"
    elif lpi >= 60:
        return "⚡ GRMLJAVINA VJEROJATNA ⚡"
    elif lpi >= 30:
        return "🌩️ Umjerena vjerojatnost grmljavine"
    elif lpi >= 10:
        return "🌥️ Slaba vjerojatnost grmljavine"
    else:
        return "☀️ Grmljavina nije vjerojatna"

# =========================
# MAIN
# =========================
print(f"\n{'='*50}")
print(f"Pokrećem SMC Thunder - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Mod: {MODE}")
print(f"{'='*50}\n")

# =========================
# MODE: REPORT (dnevni izvještaj - s LPI)
# =========================
if MODE == "report":
    results = []
    lpi_upozorenja = []
    
    for ime, (lat, lon) in regije.items():
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": "cape,lightning_potential",
                "forecast_days": 1,
                "timezone": "Europe/Zagreb"
            }
            r = requests.get(url, params=params, timeout=30)
            data = r.json()["hourly"]

            max_cape = max(data["cape"])
            max_lpi = max(data["lightning_potential"])
            level = rizik(max_cape, max_lpi)
            emoji = "🟢" if level == "NIZAK" else "🟡" if level == "UMJEREN" else "🟠" if level == "VISOK" else "🔴"

            results.append(f"{emoji} {ime:15} {level} | CAPE {max_cape:.0f} | LPI {max_lpi:.0f}%")
            print(f"{ime:15} | CAPE={max_cape:4.0f} LPI={max_lpi:3.0f}% => {level}")
            
            # Dodaj u upozorenja ako je LPI visok
            if max_lpi >= 60:
                lpi_upozorenja.append(f"⚠️ {ime}: {lpi_tekst(max_lpi)} (CAPE {max_cape:.0f})")
            
        except Exception as e:
            print(f"ERROR - {ime}: {e}")

    hour = datetime.now().hour
    naslov = "🌅 JUTARNJI IZVJEŠTAJ" if hour < 12 else "🌤️ POPODNEVNI IZVJEŠTAJ"
    
    msg = f"""🌩️ SMC THUNDER

{naslov}
📅 {datetime.now().strftime("%d.%m.%Y. %H:%M")}

📍 REGIJE:

""" + "\n".join(results)

    if lpi_upozorenja:
        msg += "\n\n📍 GRMLJAVINSKA UPOZORENJA:\n" + "\n".join(lpi_upozorenja)

# =========================
# MODE: ALERT (upozorenje - s LPI)
# =========================
elif MODE == "alert":
    alert_regije = []
    
    for ime, (lat, lon) in regije.items():
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": "cape,lightning_potential",
                "forecast_days": 1,
                "timezone": "Europe/Zagreb"
            }
            r = requests.get(url, params=params, timeout=30)
            data = r.json()["hourly"]

            max_cape = max(data["cape"])
            max_lpi = max(data["lightning_potential"])
            level = rizik(max_cape, max_lpi)

            if level == "VRLO VISOK":
                alert_regije.append(f"⚡ {ime} | CAPE {max_cape:.0f} | LPI {max_lpi:.0f}%")
            
            print(f"{ime:15} | CAPE={max_cape:4.0f} LPI={max_lpi:3.0f}% => {level}")
        except Exception as e:
            print(f"ERROR - {ime}: {e}")

    if not alert_regije:
        print("✅ Nema regija s vrlo visokim rizikom - ne šaljem poruku")
        sys.exit(0)
    
    msg = "🚨 SMC ALERT 🚨\n\nVRLO VISOK RIZIK:\n\n"
    msg += "\n".join(alert_regije)
    msg += f"\n\n📅 {datetime.now().strftime('%d.%m.%Y. %H:%M')}"
    msg += "\n\n⚠️ Preporuka: Pratite razvoj situacije, moguće jako nevrijeme s grmljavinom!"

# =========================
# MODE: WEEKLY (tjedni izvještaj - s LPI, SAMO PODRUČJA S OLUJAMA)
# =========================
elif MODE == "weekly":
    print("📊 Generiram tjedni izvještaj oluja s LPI - SAMO područja s olujama...")
    print(f"Broj MFG grupa: {len(sve_mfg_grupe)}")
    
    # Gledamo zadnjih 7 dana (od jučer unazad)
    end_date = datetime.now() - timedelta(days=1)
    start_date = end_date - timedelta(days=6)
    
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
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": "cape,lightning_potential",
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
                cape_vrijednosti = [x for x in data["cape"][start:end] if x is not None]
                lpi_vrijednosti = [x for x in data["lightning_potential"][start:end] if x is not None]
                
                if not cape_vrijednosti:
                    continue
                    
                max_cape = max(cape_vrijednosti)
                max_lpi = max(lpi_vrijednosti) if lpi_vrijednosti else 0
                
                if max_cape >= 1500:
                    oluje.append(f"   • {datumi[dan]} 🌩️ JAKA OLUJA | CAPE {max_cape:.0f} | LPI {max_lpi:.0f}% ({lpi_tekst(max_lpi)})")
                elif max_cape >= 800:
                    oluje.append(f"   • {datumi[dan]} ⛈️ OLUJA | CAPE {max_cape:.0f} | LPI {max_lpi:.0f}% ({lpi_tekst(max_lpi)})")
            
            # Spremi samo ako ima oluja
            if oluje:
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
            msg_parts.append(f"🔵 MFG {mfg_id} ({podaci['naziv']}):")
            msg_parts.extend(podaci['oluje'])
            msg_parts.append("")
        
        msg = f"""📊 SMC THUNDER - TJEDNI IZVJEŠTAJ OLUJA

📅 {datetime.now().strftime("%d.%m.%Y")}
📆 Razdoblje: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}
⚠️ Prikazana su samo područja gdje je bilo oluja (CAPE ≥ 800)

""" + "\n".join(msg_parts) + """
📌 Legenda:
⛈️ = oluja (CAPE 800-1500)
🌩️ = jaka oluja (CAPE ≥ 1500)
LPI = vjerojatnost grmljavine (0-100%)
• LPI > 60% = visoka vjerojatnost munja
• LPI 30-60% = umjerena vjerojatnost
• LPI < 30% = mala vjerojatnost
"""
    else:
        msg = f"""📊 SMC THUNDER - TJEDNI IZVJEŠTAJ OLUJA

📅 {datetime.now().strftime("%d.%m.%Y")}
📆 Razdoblje: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}

✅ U proteklih 7 dana NIJE BILO OLUJA ni na jednom području (CAPE < 800)

📌 CAPE 800-1500 = oluja
📌 CAPE ≥ 1500 = jaka oluja
📌 LPI = vjerojatnost grmljavine
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
