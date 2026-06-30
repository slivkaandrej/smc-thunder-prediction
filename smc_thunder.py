import requests
from datetime import datetime, timedelta
import os
import sys
from collections import defaultdict
import re
import time
import urllib3

# =========================
# DISABLE SSL WARNINGS
# =========================
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =========================
# HEADERS ZA SVE ZAHTJEVE
# =========================
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# =========================
# TELEGRAM SETTINGS
# =========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
MODE = os.getenv("MODE")

# =========================
# TELEGRAM SUPERGRUPA
# =========================
GROUP_CHAT_ID = -1003803468625

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
# MFG GRUPE
# =========================
sve_mfg_grupe = {
    "942": ("Varaždin", 46.3044, 16.3378),
    "944": ("Koprivnica", 46.1625, 16.8278),
    "945": ("Bjelovar", 45.8986, 16.8489),
    "951": ("Sisak", 45.4851, 16.3787),
    "952": ("Kutina", 45.4750, 16.7819),
    "953": ("Daruvar", 45.5906, 17.2250),
    "953b": ("Požega", 45.3314, 17.6744),
    "954": ("Slavonski Brod", 45.1603, 18.0156),
    "962": ("Osijek Centar / Istok", 45.5550, 18.6955),
    "961a": ("Osijek Zapad (Višnjevac)", 45.56861, 18.61389),
    "961b": ("Osijek Jug (Tenja)", 45.498, 18.747),
    "962b": ("Beli Manastir", 45.7700, 18.6036),
    "962c": ("Bilje", 45.6069, 18.7439),
    "962d": ("Darda", 45.6281, 18.6997),
    "962e": ("Kotlina", 45.6553, 18.6947),
    "963": ("Slatina", 45.7033, 17.7025),
    "964": ("Vinkovci", 45.2883, 18.8047),
    "964b": ("Ilok", 45.2222, 19.3769),
    "841": ("Krk", 45.0260, 14.5780),
    "842": ("Crikvenica", 45.1667, 14.6833),
    "843": ("Opatija", 45.3333, 14.3000),
    "845": ("Rijeka", 45.3271, 14.4422),
    "845b": ("Delnice", 45.4000, 14.8000),
    "851": ("Pula", 44.8667, 13.8500),
    "852": ("Rovinj", 45.0833, 13.6333),
    "854": ("Umag", 45.4333, 13.5167),
    "831": ("Ogulin", 45.2667, 15.2167),
    "832": ("Karlovac", 45.4872, 15.5478),
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
    "624": ("Samobor", 45.8000, 15.7200),
    "634": ("Velika Gorica", 45.7100, 16.0700),
    "611": ("Zagreb Centar", 45.8150, 15.9819),
    "613": ("Zagreb Pešćenica", 45.7900, 16.0000),
    "614": ("Zagreb Dubrava", 45.8400, 16.0500),
    "621": ("Zagreb Trešnjevka", 45.7850, 15.9300),
    "622": ("Zagreb Črnomerec", 45.8200, 15.9300),
    "633": ("Zagreb Trnsko", 45.7700, 15.9600),
    "722a": ("Solin", 43.5333, 16.5000),
    "725b": ("Žrnovnica", 43.5200, 16.5500),
    "724b": ("Klis", 43.5500, 16.5167),
}

# =========================
# GRUPIRANJE PO REGIJAMA
# =========================
regije_mfg = {
    "🌾 SLAVONIJA": ["953", "953b", "954", "962", "961a", "961b", "962b", "962c", "962d", "962e", "963", "964", "964b"],
    "🏔️ GORSKA HRVATSKA": ["831", "832"],
    "🌊 KVARNER I ISTRA": ["841", "842", "843", "845", "845b", "851", "852", "854"],
    "☀️ DALMACIJA": ["711", "713", "715", "721", "722", "723", "724", "725", "731", "733", "734", "735", "722a", "725b", "724b"],
    "🏙️ ZAGREB I OKOLICA": ["624", "634", "611", "613", "614", "621", "622", "633"],
    "📌 SJEVERNA HRVATSKA": ["942", "944", "945", "951", "952"],
}

# =========================
# POMOĆNE FUNKCIJE
# =========================
def posalji_u_grupu(poruka):
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": GROUP_CHAT_ID, "text": poruka},
            timeout=10,
            headers=REQUEST_HEADERS,
            verify=False
        )
        if resp.status_code == 200:
            print("✅ Poruka poslana u grupu!")
            return True
        else:
            print(f"❌ Greška: {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Greška pri slanju: {e}")
        return False

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
# FUNKCIJA ZA VREMENSKI RASPORED GRMLJAVINE
# =========================
def vremenski_raspored_grmljavine(weathercode_sati, cape_sati):
    """
    Analizira satne podatke i vraća period u kojem se očekuje grmljavina.
    """
    sati_grmljavine = []
    
    for hour in range(24):
        if hour >= len(weathercode_sati) or hour >= len(cape_sati):
            break
            
        weather = weathercode_sati[hour]
        cape = cape_sati[hour]
        
        # Samo weathercode 95, 96, 99 su grmljavina
        if weather in [95, 96, 99] and cape is not None:
            sati_grmljavine.append((hour, weather, cape))

    if not sati_grmljavine:
        return None, None, None

    prvi_sat = sati_grmljavine[0][0]
    zadnji_sat = sati_grmljavine[-1][0]
    
    # Ako raspon traje duže od 8 sati, vrati None (nije pouzdano)
    if zadnji_sat - prvi_sat > 8:
        return None, None, None
    
    # Pronađi sat s najjačom grmljavinom (najveći weather code, pa najveći CAPE)
    najjaci_sat, najjaci_code, najveci_cape = max(sati_grmljavine, key=lambda x: (x[1], x[2]))

    # Formatiranje vremena za prikaz
    vremenski_raspon = f"{prvi_sat:02d}:00 - {zadnji_sat + 1:02d}:00"
    najjace_u_satu = f"{najjaci_sat:02d}:00"

    return vremenski_raspon, najjace_u_satu, najjaci_code

ALERT_HISTORY_FILE = "alert_history.txt"

def zadnji_alert_poslan(alert_id):
    if not os.path.exists(ALERT_HISTORY_FILE):
        return False
    try:
        with open(ALERT_HISTORY_FILE, "r") as f:
            for line in f:
                if line.startswith(alert_id):
                    vrijeme = line.split("|")[1].strip()
                    zadnji = datetime.fromisoformat(vrijeme)
                    if datetime.now() - zadnji < timedelta(hours=6):
                        return True
    except:
        pass
    return False

def spremi_alert(alert_id, detalji):
    try:
        with open(ALERT_HISTORY_FILE, "a") as f:
            f.write(f"{alert_id}|{datetime.now().isoformat()}|{detalji}\n")
    except:
        pass

# =========================
# MAIN
# =========================
print(f"\n{'='*50}")
print(f"Pokrećem SMC Thunder - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Mod: {MODE}")
print(f"{'='*50}\n")

# =========================
# MODE: REPORT (dnevni izvještaj - 7:10 i 14:00)
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
            r = requests.get(url, params=params, timeout=30, headers=REQUEST_HEADERS, verify=False)
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
    
    poruka = f"""🌩️ SMC THUNDER

{naslov}
📅 {datetime.now().strftime("%d.%m.%Y. %H:%M")}

📍 REGIJE:

""" + "\n".join(results)

    if grmljavina_upozorenja:
        poruka += "\n\n📍 GRMLJAVINSKA UPOZORENJA:\n" + "\n".join(grmljavina_upozorenja)

    posalji_u_grupu(poruka)

# =========================
# MODE: YESTERDAY (grmljavina jučer - FORECAST API)
# =========================
elif MODE == "yesterday":
    print("📊 Generiram izvještaj o grmljavini jučer (Forecast API - prognoza)...")
    print("⚠️ Napomena: Ovo su prognozirani podaci, ne stvarna mjerenja.")
    print("⏱️ Očekivano trajanje: 5-10 minuta (analizira se 51 lokacija)...")
    
    juce = datetime.now() - timedelta(days=1)
    juce_str = juce.strftime("%d.%m.%Y")
    
    rezultati = {}
    ukupno_grupa = 0
    ukupno_grupa_ukupno = len(sve_mfg_grupe)
    trenutni_broj = 0
    
    for mfg_id, (naziv, lat, lon) in sve_mfg_grupe.items():
        trenutni_broj += 1
        print(f"\n🔄 Provjera {trenutni_broj}/{ukupno_grupa_ukupno}: MFG {mfg_id} ({naziv})...")
        
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": "weathercode,cape",
                "past_days": 2,
                "forecast_days": 0,
                "timezone": "Europe/Zagreb"
            }
            
            max_retries = 3
            data = None
            
            for attempt in range(max_retries):
                try:
                    r = requests.get(url, params=params, timeout=120, headers=REQUEST_HEADERS, verify=False)
                    data = r.json()
                    print(f"   ✅ Uspješno dohvaćeno (pokušaj {attempt + 1})")
                    break
                except (requests.exceptions.Timeout, requests.exceptions.SSLError) as e:
                    if attempt == max_retries - 1:
                        print(f"   ❌ Greška nakon {max_retries} pokušaja: {type(e).__name__}")
                        data = None
                        break
                    print(f"   ⚠️ {type(e).__name__}, čekam 5 sekundi pa pokušaj {attempt + 2}...")
                    time.sleep(5)
            
            if data is None or "hourly" not in data:
                print(f"   ❌ Nema podataka")
                continue
            
            hourly = data["hourly"]
            if "weathercode" not in hourly or "cape" not in hourly:
                print(f"   ❌ Nema weathercode ili cape podataka")
                continue
            
            najjaci_code = 0
            najveci_cape = 0
            
            start_idx = 24
            end_idx = min(48, len(hourly["weathercode"]))
            
            for hour in range(start_idx, end_idx):
                if hour >= len(hourly["weathercode"]):
                    break
                weather = hourly["weathercode"][hour]
                cape = hourly["cape"][hour] if hour < len(hourly["cape"]) else None
                
                if cape is None:
                    continue
                
                if weather in [95, 96, 99]:
                    if weather > najjaci_code:
                        najjaci_code = weather
                        najveci_cape = cape
                    elif weather == najjaci_code and cape > najveci_cape:
                        najveci_cape = cape
            
            if najjaci_code > 0:
                rezultati[mfg_id] = {
                    "naziv": naziv,
                    "najjaci_code": najjaci_code,
                    "najveci_cape": najveci_cape,
                    "mfg_id": mfg_id
                }
                ukupno_grupa += 1
                
                if najjaci_code == 99:
                    print(f"   ✅ JAKA GRMLJAVINA S TUČOM! (CAPE {najveci_cape:.0f})")
                elif najjaci_code == 96:
                    print(f"   ✅ GRMLJAVINA S TUČOM! (CAPE {najveci_cape:.0f})")
                else:
                    print(f"   ✅ GRMLJAVINA! (CAPE {najveci_cape:.0f})")
            else:
                print(f"   ❌ Nema grmljavine")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ GREŠKA: {e}")
    
    if rezultati:
        poruka_dijelovi = [f"📊 SMC THUNDER - GRMLJAVINA JUČER ({juce_str})", ""]
        poruka_dijelovi.append("⚠️ Napomena: Prognozirani podaci (Forecast API)")
        poruka_dijelovi.append("")
        
        for regija_naziv, mfg_lista in regije_mfg.items():
            regija_ima = False
            regija_dio = [regija_naziv, "─────────────────"]
            
            for mfg_id in mfg_lista:
                if mfg_id in rezultati:
                    regija_ima = True
                    podaci = rezultati[mfg_id]
                    
                    if podaci["najjaci_code"] == 99:
                        grmljavina_tekst = f"   • ⚡⚡ JAKA GRMLJAVINA S TUČOM! (CAPE {podaci['najveci_cape']:.0f})"
                    elif podaci["najjaci_code"] == 96:
                        grmljavina_tekst = f"   • ⚡ GRMLJAVINA S TUČOM (CAPE {podaci['najveci_cape']:.0f})"
                    else:
                        grmljavina_tekst = f"   • 🌩️ GRMLJAVINA (CAPE {podaci['najveci_cape']:.0f})"
                    
                    regija_dio.append(f"🔵 MFG {podaci['mfg_id']} ({podaci['naziv']}):")
                    regija_dio.append(grmljavina_tekst)
                    regija_dio.append("")
            
            if regija_ima:
                poruka_dijelovi.extend(regija_dio)
        
        poruka_dijelovi.append(f"✅ Ukupno: {ukupno_grupa} MFG grupa s grmljavinom")
        poruka = "\n".join(poruka_dijelovi)
    else:
        poruka = f"📊 SMC THUNDER - GRMLJAVINA JUČER ({juce_str})\n\n✅ Jučer NIJE BILO GRMLJAVINE ni na jednom mjestu (prema prognozi)"
    
    posalji_u_grupu(poruka)

# =========================
# MODE: ALERT HISTORY (pregled alarma poslanih jučer)
# =========================
elif MODE == "alerthistory":
    print("📊 Generiram izvještaj o alertima koji su poslani jučer...")
    
    juce = datetime.now() - timedelta(days=1)
    juce_str = juce.strftime("%d.%m.%Y")
    
    if not os.path.exists(ALERT_HISTORY_FILE):
        poruka = f"📊 SMC THUNDER - ALERT POVIJEST ({juce_str})\n\n✅ Jučer NIJE BILO POSLANIH ALARMA"
        posalji_u_grupu(poruka)
        sys.exit(0)
    
    alerti_po_grupi = defaultdict(list)
    
    with open(ALERT_HISTORY_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split("|")
            if len(parts) < 3:
                continue
            
            alert_id = parts[0]
            vrijeme = parts[1]
            detalji = parts[2] if len(parts) > 2 else ""
            
            try:
                vrijeme_dt = datetime.fromisoformat(vrijeme)
                if vrijeme_dt.date() == juce.date():
                    alerti_po_grupi[alert_id].append({
                        "vrijeme": vrijeme_dt.strftime("%H:%M"),
                        "detalji": detalji
                    })
            except:
                continue
    
    if not alerti_po_grupi:
        poruka = f"📊 SMC THUNDER - ALERT POVIJEST ({juce_str})\n\n✅ Jučer NIJE BILO POSLANIH ALARMA"
        posalji_u_grupu(poruka)
        sys.exit(0)
    
    alerti_po_regijama = defaultdict(list)
    
    for alert_id, alerti in alerti_po_grupi.items():
        mfg_broj = alert_id.replace("MFG_", "")
        
        mfg_naziv = mfg_broj
        for mid, (naziv, _, _) in sve_mfg_grupe.items():
            if mid == mfg_broj:
                mfg_naziv = naziv
                break
        
        regija_pripada = "🌍 OSTALO"
        for reg_naziv, mfg_lista in regije_mfg.items():
            if mfg_broj in mfg_lista:
                regija_pripada = reg_naziv
                break
        
        for alert in alerti:
            alerti_po_regijama[regija_pripada].append({
                "mfg_id": mfg_broj,
                "naziv": mfg_naziv,
                "vrijeme": alert["vrijeme"],
                "detalji": alert["detalji"]
            })
    
    poruka_dijelovi = [f"📊 SMC THUNDER - ALERT POVIJEST ({juce_str})", ""]
    poruka_dijelovi.append("📍 UPOZORENJA KOJA SU POSLANA:")
    poruka_dijelovi.append("")
    
    for regija_naziv, alerti in alerti_po_regijama.items():
        poruka_dijelovi.append(regija_naziv)
        poruka_dijelovi.append("─────────────────")
        
        for alert in alerti:
            poruka_dijelovi.append(f"🔵 MFG {alert['mfg_id']} ({alert['naziv']}):")
            poruka_dijelovi.append(f"   • {alert['vrijeme']} {alert['detalji']}")
            poruka_dijelovi.append("")
    
    ukupno_alerta = sum(len(a) for a in alerti_po_regijama.values())
    poruka_dijelovi.append(f"✅ Ukupno: {ukupno_alerta} alerta poslano")
    
    poruka = "\n".join(poruka_dijelovi)
    posalji_u_grupu(poruka)

# =========================
# MODE: ALERT (upozorenje - SAMO za grmljavinu, s vremenskim rasponom i bojama)
# =========================
elif MODE == "alert":
    print("🔍 Provjera alarma na MFG grupama (samo grmljavina)...")
    print("⏱️ Očekivano trajanje: ~2-3 minute (analizira se 51 lokacija)...")
    alert_mfg = []
    novi_alerti = []
    
    ukupno_lokacija = len(sve_mfg_grupe)
    trenutni_broj = 0
    trenutni_sat = datetime.now().hour
    
    for mfg_id, (naziv, lat, lon) in sve_mfg_grupe.items():
        trenutni_broj += 1
        print(f"\n🔄 Provjera {trenutni_broj}/{ukupno_lokacija}: MFG {mfg_id} ({naziv})...")
        
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": "cape,cloudcover,precipitation_probability,weathercode",
                "forecast_days": 1,
                "timezone": "Europe/Zagreb"
            }
            
            max_retries = 3
            data = None
            
            for attempt in range(max_retries):
                try:
                    r = requests.get(url, params=params, timeout=120, headers=REQUEST_HEADERS, verify=False)
                    data = r.json()
                    print(f"   ✅ Uspješno dohvaćeno (pokušaj {attempt + 1})")
                    break
                except (requests.exceptions.Timeout, requests.exceptions.SSLError) as e:
                    if attempt == max_retries - 1:
                        print(f"   ❌ Greška nakon {max_retries} pokušaja: {type(e).__name__}")
                        data = None
                        break
                    print(f"   ⚠️ {type(e).__name__}, čekam 5 sekundi pa pokušaj {attempt + 2}...")
                    time.sleep(5)
            
            if data is None or "hourly" not in data:
                print(f"   ❌ Nema podataka")
                continue
            
            hourly = data["hourly"]
            weather_sati = hourly["weathercode"]
            cape_sati = hourly["cape"]
            
            # Izračunaj vremenski raspon grmljavine
            raspon, najjaci_sat, najjaci_code = vremenski_raspored_grmljavine(weather_sati, cape_sati)
            
            # Izračunaj maksimalne vrijednosti
            max_cape = max(cape_sati)
            max_cloud = max(hourly["cloudcover"])
            max_precip = max(hourly["precipitation_probability"])
            max_weathercode = max(weather_sati)
            
            # SAMO AKO POSTOJI GRMLJAVINA (weathercode 95, 96, 99)
            if max_weathercode in [95, 96, 99]:
                detalj = f"CAPE {max_cape:.0f} | {opis_grmljavine(max_weathercode)}"
                alert_id = f"MFG_{mfg_id}"
                
                # Odaberi boju prema statusu
                if raspon:
                    pocetak = int(raspon.split(" - ")[0].split(":")[0])
                    kraj = int(raspon.split(" - ")[1].split(":")[0])
                    
                    if trenutni_sat < pocetak or (pocetak <= trenutni_sat <= kraj):
                        boja = "🔴"  # AKTIVNO
                    else:
                        boja = "🟢"  # ZAVRŠENO
                else:
                    boja = "🔵"  # NEMA RASPONA
                
                vremenska_info = ""
                if raspon:
                    vremenska_info = f" | 🕐 {raspon}"
                    if najjaci_sat and boja == "🔴":
                        vremenska_info += f" (najjače oko {najjaci_sat})"
                
                if not zadnji_alert_poslan(alert_id):
                    alert_mfg.append(f"{boja} MFG {mfg_id} ({naziv}) | {detalj}{vremenska_info}")
                    novi_alerti.append((alert_id, detalj))
                    print(f"   {boja} ALERT!{vremenska_info}")
                else:
                    alert_mfg.append(f"{boja} MFG {mfg_id} ({naziv}) | {detalj}{vremenska_info}")
                    print(f"   {boja} PONOVNO!{vremenska_info}")
            else:
                print(f"   ✅ Nema grmljavine")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ GREŠKA: {e}")
    
    for alert_id, detalj in novi_alerti:
        spremi_alert(alert_id, detalj)
    
    if not alert_mfg:
        print("\n✅ Nema grmljavine - ne šaljem poruku")
        sys.exit(0)
    
    alerti_po_regijama = defaultdict(list)
    
    for alert in alert_mfg:
        mfg_broj = re.search(r'MFG (\d+)', alert).group(1)
        regija_pripada = "🌍 OSTALO"
        for reg_naziv, mfg_lista in regije_mfg.items():
            if mfg_broj in mfg_lista:
                regija_pripada = reg_naziv
                break
        alerti_po_regijama[regija_pripada].append(alert)
    
    poruka_dijelovi = []
    for regija_naziv, alerti in alerti_po_regijama.items():
        poruka_dijelovi.append(f"\n📌 {regija_naziv}")
        poruka_dijelovi.extend(alerti)
    
    legenda = "\n\n📌 Legenda:\n🔴 = AKTIVNO (još traje ili dolazi)\n🟢 = ZAVRŠENO (oluja je prošla)\n🔵 = NEMA POUZDANOG RASPONA"
    
    poruka = f"""🚨 SMC ALERT 🚨

⚠️ GRMLJAVINA!

📅 {datetime.now().strftime('%d.%m.%Y. %H:%M')}
📍 Pogođene MFG grupe:
""" + "\n".join(poruka_dijelovi) + legenda + """

⚠️ Preporuka: Pratite razvoj situacije!
🔔 Sljedeća provjera za 1 sat
"""
    posalji_u_grupu(poruka)

# =========================
# MODE: WEEKLY (tjedni izvještaj - HISTORICAL API)
# =========================
elif MODE == "weekly":
    print("📊 Generiram tjedni izvještaj - SAMO grmljavina (Historical API - stvarni podaci)...")
    print("⚠️ Napomena: Historical API kasni ~2-5 dana. Podaci za zadnjih nekoliko dana možda nisu dostupni.")
    print("⏱️ Očekivano trajanje: ~2-3 minute (analizira se 51 lokacija)...")
    
    end_date = datetime.now() - timedelta(days=2)
    start_date = end_date - timedelta(days=6)
    
    print(f"Period: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
    
    datumi = []
    for i in range(7):
        dan = start_date + timedelta(days=i)
        datumi.append(dan.strftime("%d.%m."))
    
    rezultati_sa_grmljavinom = {}
    ukupno_grupa = 0
    ukupno_lokacija = len(sve_mfg_grupe)
    trenutni_broj = 0
    
    for mfg_id, (naziv, lat, lon) in sve_mfg_grupe.items():
        trenutni_broj += 1
        print(f"\n🔄 Provjera {trenutni_broj}/{ukupno_lokacija}: MFG {mfg_id} ({naziv})...")
        
        try:
            url = "https://archive-api.open-meteo.com/v1/archive"
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "hourly": "weathercode,cape",
                "timezone": "Europe/Zagreb"
            }
            
            max_retries = 3
            data = None
            
            for attempt in range(max_retries):
                try:
                    r = requests.get(url, params=params, timeout=120, headers=REQUEST_HEADERS, verify=False)
                    data = r.json()
                    print(f"   ✅ Uspješno dohvaćeno (pokušaj {attempt + 1})")
                    break
                except (requests.exceptions.Timeout, requests.exceptions.SSLError) as e:
                    if attempt == max_retries - 1:
                        print(f"   ❌ Greška nakon {max_retries} pokušaja: {type(e).__name__}")
                        data = None
                        break
                    print(f"   ⚠️ {type(e).__name__}, čekam 5 sekundi pa pokušaj {attempt + 2}...")
                    time.sleep(5)
            
            if data is None or "hourly" not in data:
                print(f"   ❌ Nema podataka")
                continue
            
            hourly = data["hourly"]
            if "weathercode" not in hourly or "cape" not in hourly:
                print(f"   ❌ Nema weathercode ili cape podataka")
                continue
            
            grmljavine = []
            for dan in range(7):
                start = dan * 24
                end = start + 24
                if end > len(hourly["weathercode"]):
                    break
                
                najjaci_code = 0
                najveci_cape = 0
                
                for hour in range(start, end):
                    weather = hourly["weathercode"][hour]
                    cape = hourly["cape"][hour]
                    
                    if cape is None:
                        continue
                    
                    if weather in [95, 96, 99]:
                        if weather > najjaci_code:
                            najjaci_code = weather
                            najveci_cape = cape
                        elif weather == najjaci_code and cape > najveci_cape:
                            najveci_cape = cape
                
                if najjaci_code == 99:
                    grmljavine.append(f"   • {datumi[dan]} ⚡⚡ JAKA GRMLJAVINA S TUČOM! | CAPE {najveci_cape:.0f}")
                elif najjaci_code == 96:
                    grmljavine.append(f"   • {datumi[dan]} ⚡ GRMLJAVINA S TUČOM | CAPE {najveci_cape:.0f}")
                elif najjaci_code == 95:
                    grmljavine.append(f"   • {datumi[dan]} 🌩️ GRMLJAVINA | CAPE {najveci_cape:.0f}")
            
            if grmljavine:
                rezultati_sa_grmljavinom[mfg_id] = {
                    "naziv": naziv,
                    "grmljavine": grmljavine,
                    "mfg_id": mfg_id
                }
                ukupno_grupa += 1
                print(f"   ✅ {len(grmljavine)} dana s grmljavinom")
            else:
                print(f"   ❌ Nema grmljavine")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ GREŠKA: {e}")
    
    if rezultati_sa_grmljavinom:
        poruka_dijelovi = [f"📊 SMC THUNDER - TJEDNI IZVJEŠTAJ", ""]
        poruka_dijelovi.append(f"📅 Razdoblje: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
        poruka_dijelovi.append("⚠️ Napomena: Historical API kasni ~2-5 dana")
        poruka_dijelovi.append("")
        poruka_dijelovi.append("📍 Prikazana su samo mjesta gdje je bilo grmljavine")
        poruka_dijelovi.append("")
        
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
                poruka_dijelovi.extend(regija_dio)
        
        poruka_dijelovi.append(f"✅ Ukupno: {ukupno_grupa} MFG grupa s grmljavinom")
        
        poruka = "\n".join(poruka_dijelovi)
    else:
        poruka = f"""📊 SMC THUNDER - TJEDNI IZVJEŠTAJ

📅 Razdoblje: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}
⚠️ Napomena: Historical API kasni ~2-5 dana

✅ Nema podataka o grmljavini (podaci možda još nisu dostupni ili nije bilo grmljavine)
"""
    posalji_u_grupu(poruka)

else:
    print(f"❌ Nepoznat MODE: {MODE}")
    sys.exit(1)

print("\n✅ SMC Thunder završio\n")
