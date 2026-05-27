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
# MFG GRUPE ZA TJEDNI IZVJEŠTAJ (samo grmljavina)
# =========================
sve_mfg_grupe = {
    # ========== SJEVERNA HRVATSKA (9xx) ==========
    "942": ("Varaždin", 46.3044, 16.3378),
    "944": ("Koprivnica", 46.1625, 16.8278),
    "945": ("Bjelovar", 45.8986, 16.8489),
    "951": ("Sisak", 45.4851, 16.3787),
    "952": ("Kutina", 45.4750, 16.7819),
    "953": ("Daruvar", 45.5906, 17.2250),
    "953b": ("Požega", 45.3314, 17.6744),
    "954": ("Slavonski Brod", 45.1603, 18.0156),
    
    # ========== OSIJEK I OKOLICA (962) ==========
    "962": ("Osijek Centar / Istok", 45.5550, 18.6955),
    "961a": ("Osijek Zapad (Višnjevac)", 45.56861, 18.61389),
    "961b": ("Osijek Jug (Tenja)", 45.498, 18.747),
    "962b": ("Beli Manastir", 45.7700, 18.6036),
    "962c": ("Bilje", 45.6069, 18.7439),
    "962d": ("Darda", 45.6281, 18.6997),
    "962e": ("Kotlina", 45.6600, 18.7000),  # DODANO - Kotlina
    "963": ("Slatina", 45.7033, 17.7025),
    "964": ("Vinkovci", 45.2883, 18.8047),
    "964b": ("Ilok", 45.2222, 19.3769),
    
    # ========== KVARNER I ISTRA (8xx) ==========
    "841": ("Krk", 45.0260, 14.5780),
    "842": ("Crikvenica", 45.1667, 14.6833),
    "843": ("Opatija", 45.3333, 14.3000),
    "845": ("Rijeka", 45.3271, 14.4422),
    "851": ("Pula", 44.8667, 13.8500),
    "852": ("Rovinj", 45.0833, 13.6333),
    "854": ("Umag", 45.4333, 13.5167),
    
    # ========== GORSKI KOTAR I LIKA (8xx) ==========
    "831": ("Ogulin", 45.2667, 15.2167),
    "832": ("Karlovac", 45.4872, 15.5478),
    
    # ========== DALMACIJA (7xx) ==========
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
    
    # ========== ZAGREBAČKA REGIJA (6xx) ==========
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
# GRUPIRANJE PO REGIJAMA ZA TJEDNI IZVJEŠTAJ
# =========================
regije_mfg = {
    "🌾 SLAVONIJA": ["953", "953b", "954", "962", "961a", "961b", "962b", "962c", "962d", "962e", "963", "964", "964b"],
    "🏔️ GORSKA HRVATSKA": ["831", "832"],
    "🌊 KVARNER I ISTRA": ["841", "842", "843", "845", "851", "852", "854"],
    "☀️ DALMACIJA": ["711", "713", "715", "721", "722", "723", "724", "725", "731", "733", "734", "735"],
    "🏙️ ZAGREB I OKOLICA": ["624", "634", "611", "613", "614", "621", "622", "633"],
    "📌 SJEVERNA HRVATSKA": ["942", "944", "945", "951", "952"],
}

# =========================
# FUNKCIJA ZA RIZIK
# =========================
def rizik(cape, cloud, precip, weathercode):
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
    
    if weathercode in [95, 96, 99]:
        score += 3
    
    if score <= 2:
        return "NIZAK"
    elif score <= 4:
        return "UMJEREN"
    elif score <= 6:
        return "VISOK"
    else:
        return "VRLO VISOK"

def opis_grmljavine(weathercode):
    if weathercode == 99:
        return "⚡⚡ JAKA GRMLJAVINA S TUČOM! ⚡⚡"
    elif weathercode == 96:
        return "⚡ GRMLJAVINA S TUČOM ⚡"
    elif weathercode == 95:
        return "🌩️ GRMLJAVINA"
    elif weathercode in [80, 81, 82]:
        return "🌧️ JAKA KIŠA"
    elif weathercode in [61, 63, 65]:
        return "🌧️ KIŠA"
    else:
        return "☀️ SUHO"

# =========================
# MAIN
# =========================
print(f"\n{'='*50}")
print(f"Pokrećem SMC Thunder - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Mod: {MODE}")
print(f"Broj MFG lokacija: {len(sve_mfg_grupe)}")
print(f"{'='*50}\n")

# =========================
# MODE: REPORT (dnevni izvještaj)
# =========================
if MODE == "report":
    results = []
    grmljavina_upozorenja = []
    
    for ime, (lat, lon) in regije.items():
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": "cape,cloudcover,precipitation_probability,weathercode",
                "forecast_days": 1,
                "timezone": "Europe/Zagreb"
            }
            r = requests.get(url, params=params, timeout=30)
            data = r.json()["hourly"]

            max_cape = max(data["cape"])
            max_cloud = max(data["cloudcover"])
            max_precip = max(data["precipitation_probability"])
            max_weathercode = max(data["weathercode"])
            
            level = rizik(max_cape, max_cloud, max_precip, max_weathercode)
            emoji = "🟢" if level == "NIZAK" else "🟡" if level == "UMJEREN" else "🟠" if level == "VISOK" else "🔴"
            grmljavina = opis_grmljavine(max_weathercode)

            results.append(f"{emoji} {ime:15} {level:10} | CAPE {max_cape:.0f} | {grmljavina}")
            print(f"{ime:15} | CAPE={max_cape:4.0f} WEATHERCODE={max_weathercode} => {level}")
            
            if max_weathercode in [95, 96, 99]:
                grmljavina_upozorenja.append(f"⚠️ {ime}: {grmljavina} (CAPE {max_cape:.0f})")
            
        except Exception as e:
            print(f"ERROR - {ime}: {e}")

    hour = datetime.now().hour
    naslov = "🌅 JUTARNJI IZVJEŠTAJ" if hour < 12 else "🌤️ POPODNEVNI IZVJEŠTAJ"
    
    msg = f"""🌩️ SMC THUNDER

{naslov}
📅 {datetime.now().strftime("%d.%m.%Y. %H:%M")}

📍 REGIJE:

""" + "\n".join(results)

    if grmljavina_upozorenja:
        msg += "\n\n📍 GRMLJAVINSKA UPOZORENJA:\n" + "\n".join(grmljavina_upozorenja)

# =========================
# MODE: ALERT (upozorenje)
# =========================
elif MODE == "alert":
    alert_regije = []
    
    for ime, (lat, lon) in regije.items():
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": "cape,cloudcover,precipitation_probability,weathercode",
                "forecast_days": 1,
                "timezone": "Europe/Zagreb"
            }
            r = requests.get(url, params=params, timeout=30)
            data = r.json()["hourly"]

            max_cape = max(data["cape"])
            max_cloud = max(data["cloudcover"])
            max_precip = max(data["precipitation_probability"])
            max_weathercode = max(data["weathercode"])
            level = rizik(max_cape, max_cloud, max_precip, max_weathercode)

            if level == "VRLO VISOK" or max_weathercode in [95, 96, 99]:
                alert_regije.append(f"⚡ {ime} | CAPE {max_cape:.0f} | {opis_grmljavine(max_weathercode)}")
            
            print(f"{ime:15} | CAPE={max_cape:4.0f} WEATHERCODE={max_weathercode} => {level}")
        except Exception as e:
            print(f"ERROR - {ime}: {e}")

    if not alert_regije:
        print("✅ Nema alarma - ne šaljem poruku")
        sys.exit(0)
    
    msg = "🚨 SMC ALERT 🚨\n\nVRLO VISOK RIZIK ILI GRMLJAVINA:\n\n"
    msg += "\n".join(alert_regije)
    msg += f"\n\n📅 {datetime.now().strftime('%d.%m.%Y. %H:%M')}"
    msg += "\n\n⚠️ Preporuka: Pratite razvoj situacije!"

# =========================
# MODE: WEEKLY (tjedni izvještaj - SAMO GRMLJAVINA)
# =========================
elif MODE == "weekly":
    print("📊 Generiram tjedni izvještaj - SAMO grmljavina...")
    print(f"Broj lokacija: {len(sve_mfg_grupe)}")
    
    end_date = datetime.now() - timedelta(days=1)
    start_date = end_date - timedelta(days=6)
    
    print(f"Period: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
    
    datumi = []
    for i in range(7):
        dan = start_date + timedelta(days=i)
        datumi.append(dan.strftime("%d.%m."))
    
    # Rječnik za rezultate (samo tamo gdje je bilo grmljavine)
    rezultati_sa_grmljavinom = {}
    
    for mfg_id, (naziv, lat, lon) in sve_mfg_grupe.items():
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": "cape,weathercode",
                "past_days": 7,
                "forecast_days": 0,
                "timezone": "Europe/Zagreb"
            }
            
            r = requests.get(url, params=params, timeout=30)
            data = r.json()["hourly"]
            
            if "cape" not in data or not data["cape"]:
                continue
            
            grmljavine = []
            for dan in range(7):
                start = dan * 24
                end = start + 24
                if end > len(data["cape"]):
                    break
                
                cape_vrijednosti = [x for x in data["cape"][start:end] if x is not None]
                weather_vrijednosti = [x for x in data["weathercode"][start:end] if x is not None]
                
                if not cape_vrijednosti:
                    continue
                    
                max_cape = max(cape_vrijednosti)
                max_weather = max(weather_vrijednosti) if weather_vrijednosti else 0
                
                # SAMO weathercode 95, 96, 99 (grmljavina)
                if max_weather == 99:
                    grmljavine.append(f"   • {datumi[dan]} ⚡⚡ JAKA GRMLJAVINA S TUČOM! | CAPE {max_cape:.0f}")
                elif max_weather == 96:
                    grmljavine.append(f"   • {datumi[dan]} ⚡ GRMLJAVINA S TUČOM | CAPE {max_cape:.0f}")
                elif max_weather == 95:
                    grmljavine.append(f"   • {datumi[dan]} 🌩️ GRMLJAVINA | CAPE {max_cape:.0f}")
            
            # Spremi samo ako ima grmljavine
            if grmljavine:
                rezultati_sa_grmljavinom[mfg_id] = {
                    "naziv": naziv,
                    "grmljavine": grmljavine,
                    "mfg_id": mfg_id
                }
            
            if grmljavine:
                print(f"📍 MFG {mfg_id} ({naziv}): {len(grmljavine)} dana s grmljavinom")
            
        except Exception as e:
            print(f"ERROR - {naziv}: {e}")
    
    # Kreiraj poruku grupiranu po regijama
    if rezultati_sa_grmljavinom:
        msg_parts = []
        for regija_naziv, mfg_lista in regije_mfg.items():
            regija_ima = False
            regija_dio = [regija_naziv, "─────────────────"]
            
            for mfg_id in mfg_lista:
                if mfg_id in rezultati_sa_grmljavinom:
                    regija_ima = True
                    podaci = rezultati_sa_grmljavinom[mfg_id]
                    regija_dio.append(f"🔵 MFG {podaci['mfg_id']} ({podaci['naziv']}):")
                    regija_dio.extend(podaci['grmljavine'])
                    regija_dio.append("")
            
            if regija_ima:
                msg_parts.extend(regija_dio)
        
        msg = f"""📊 SMC THUNDER - TJEDNI IZVJEŠTAJ (SAMO GRMLJAVINA)

📅 {datetime.now().strftime("%d.%m.%Y")}
📆 Razdoblje: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}
📍 Prikazana su samo mjesta gdje je bilo grmljavine (weathercode 95,96,99)

""" + "\n".join(msg_parts) + """
📌 Legenda:
🌩️ = grmljavina
⚡ = grmljavina s tučom
⚡⚡ = jaka grmljavina s tučom
"""
    else:
        msg = f"""📊 SMC THUNDER - TJEDNI IZVJEŠTAJ (SAMO GRMLJAVINA)

📅 {datetime.now().strftime("%d.%m.%Y")}
📆 Razdoblje: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}

✅ U proteklih 7 dana NIJE BILO GRMLJAVINE ni na jednom mjestu
"""

else:
    print(f"❌ Nepoznat MODE: {MODE}")
    sys.exit(1)

# =========================
# SEND TELEGRAM
# =========================
if not TOKEN or not CHAT_ID:
    print("❌ Missing environment variables")
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
