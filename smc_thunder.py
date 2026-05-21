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
# MFG GRUPE S PODRUČJIMA
# =========================
mfg_grupe = {
    "611": {
        "naziv": "Zagreb Centar",
        "podrucja": {
            "Zagreb Centar": (45.8150, 15.9819),
            "Trnje 1": (45.8000, 15.9700),
            "Medveščak": (45.8300, 15.9900),
            "Šestine": (45.8500, 15.9500),
            "Mlinovi": (45.8200, 15.9600)
        }
    },
    "613": {
        "naziv": "Zagreb Pešćenica",
        "podrucja": {
            "Pešćenica": (45.7900, 16.0000),
            "Trnje 2": (45.7950, 15.9750),
            "Maksimir": (45.8250, 16.0150),
            "Mihaljevac": (45.8350, 16.0050),
            "Markuševac": (45.8450, 16.0250)
        }
    },
    "614": {
        "naziv": "Zagreb Dubrava",
        "podrucja": {
            "Dubrava": (45.8400, 16.0500),
            "Ravnice": (45.8300, 16.0400),
            "Sesvete": (45.8300, 16.1100)
        }
    },
    "621": {
        "naziv": "Zagreb Trešnjevka",
        "podrucja": {
            "Trešnjevka": (45.7850, 15.9300),
            "Jarun": (45.7800, 15.9200),
            "Rudeš": (45.7900, 15.9400),
            "Prečko": (45.7950, 15.9100)
        }
    },
    "622": {
        "naziv": "Zagreb Črnomerec",
        "podrucja": {
            "Črnomerec": (45.8200, 15.9300),
            "Vrapče": (45.8100, 15.9100),
            "Zaprešić": (45.8600, 15.8100)
        }
    },
    "624": {
        "naziv": "Samobor",
        "podrucja": {
            "Samobor": (45.8000, 15.7200),
            "Malešnica": (45.7850, 15.8900),
            "Špansko": (45.7900, 15.9000)
        }
    },
    "625": {
        "naziv": "Zabok",
        "podrucja": {
            "Zabok": (46.0300, 15.9100),
            "Krapina": (46.1600, 15.8800),
            "Klanjec": (46.0500, 15.7400),
            "Zlatar": (46.0900, 16.0700),
            "Bistra": (45.9000, 15.8700),
            "Jakovlje": (45.9500, 15.8600),
            "Pušća": (45.9200, 15.8000)
        }
    },
    "633": {
        "naziv": "Zagreb Trnsko",
        "podrucja": {
            "Trnsko": (45.7700, 15.9600),
            "Utrine": (45.7750, 15.9650),
            "Lanište": (45.7800, 15.9550),
            "Trnje 3": (45.8050, 15.9750)
        }
    },
    "634": {
        "naziv": "Velika Gorica",
        "podrucja": {
            "Velika Gorica": (45.7100, 16.0700)
        }
    },
    "711": {
        "naziv": "Dubrovnik",
        "podrucja": {
            "Dubrovnik": (42.6507, 18.0944),
            "Konavle": (42.5500, 18.4000),
            "Ston": (42.8389, 17.6964),
            "Župa Dubrovačka": (42.6200, 18.2000),
            "Mljet": (42.7400, 17.5300)
        }
    },
    "713": {
        "naziv": "Korčula",
        "podrucja": {
            "Korčula": (42.9600, 17.1300),
            "Pelješac": (42.9200, 17.4200),
            "Metković": (43.0542, 17.6483),
            "Lastovo": (42.7500, 16.9000)
        }
    },
    "715": {
        "naziv": "Omiš",
        "podrucja": {
            "Omiš": (43.4400, 16.6900),
            "Makarska": (43.3000, 17.0200),
            "Imotski": (43.4400, 17.2100),
            "Vrgorac": (43.2000, 17.3700)
        }
    },
    "721": {
        "naziv": "Split",
        "podrucja": {
            "Split": (43.5081, 16.4402),
            "Brač": (43.3167, 16.6000)
        }
    },
    "722": {
        "naziv": "Solin",
        "podrucja": {
            "Solin": (43.5333, 16.5000),
            "Sjever Splita": (43.5300, 16.4500),
            "Hvar": (43.1725, 16.4428),
            "Šolta": (43.3800, 16.3000)
        }
    },
    "723": {
        "naziv": "Kaštela",
        "podrucja": {
            "Kaštela": (43.5500, 16.3500),
            "Trogir": (43.5167, 16.2500),
            "Drvenici": (43.4500, 16.1500)
        }
    },
    "724": {
        "naziv": "Sinj",
        "podrucja": {
            "Sinj": (43.7000, 16.6333),
            "Klis": (43.5500, 16.5167),
            "Trilj": (43.6167, 16.7167)
        }
    },
    "725": {
        "naziv": "Istok Splita",
        "podrucja": {
            "Istok Splita": (43.5100, 16.4800),
            "Žrnovnica": (43.5200, 16.5500),
            "Vis": (43.0600, 16.1800)
        }
    },
    "731": {
        "naziv": "Zadar",
        "podrucja": {
            "Zadar centar": (44.1194, 15.2314),
            "Zadar okolica": (44.1000, 15.2500),
            "Dugi Otok": (44.0000, 15.0000)
        }
    },
    "733": {
        "naziv": "Drniš",
        "podrucja": {
            "Drniš": (43.8667, 16.1500),
            "Knin": (44.0500, 16.2000),
            "Vrlika": (43.9167, 16.4000),
            "Vodice": (43.7500, 15.7833),
            "Murter": (43.8000, 15.6167)
        }
    },
    "734": {
        "naziv": "Biograd",
        "podrucja": {
            "Biograd": (43.9333, 15.4333),
            "Benkovac": (44.0333, 15.6167),
            "Ugljan": (44.0833, 15.1667),
            "Pašman": (43.9500, 15.3833),
            "Pag": (44.4333, 15.0500),
            "Karlobag": (44.5333, 15.0667),
            "Starigrad": (44.2833, 15.4333)
        }
    },
    "735": {
        "naziv": "Šibenik",
        "podrucja": {
            "Šibenik": (43.7350, 15.8957),
            "Šibenik otoci": (43.7000, 15.8000)
        }
    },
    "841": {
        "naziv": "Sušak",
        "podrucja": {
            "Sušak": (45.3200, 14.4500),
            "Krk": (45.0260, 14.5780)
        }
    },
    "842": {
        "naziv": "Crikvenica",
        "podrucja": {
            "Crikvenica": (45.1667, 14.6833),
            "Rab": (44.7667, 14.7667),
            "Senj": (44.9833, 14.9000)
        }
    },
    "843": {
        "naziv": "Opatija",
        "podrucja": {
            "Opatija": (45.3333, 14.3000),
            "Cres": (44.9500, 14.4000),
            "Lošinj": (44.5333, 14.4667)
        }
    },
    "844": {
        "naziv": "Zamet",
        "podrucja": {
            "Zamet": (45.3500, 14.4000),
            "Kastav": (45.3667, 14.3500)
        }
    },
    "845": {
        "naziv": "Kozala",
        "podrucja": {
            "Kozala": (45.3400, 14.4200),
            "Rijeka centar": (45.3271, 14.4422),
            "Gorski Kotar": (45.3986, 14.8019)
        }
    },
    "851": {
        "naziv": "Pula",
        "podrucja": {
            "Pula": (44.8667, 13.8500)
        }
    },
    "852": {
        "naziv": "Rovinj",
        "podrucja": {
            "Rovinj": (45.0833, 13.6333),
            "Žminj": (45.1500, 13.9000),
            "Pazin": (45.2333, 13.9333),
            "Labin": (45.0833, 14.1167)
        }
    },
    "854": {
        "naziv": "Umag",
        "podrucja": {
            "Umag": (45.4333, 13.5167),
            "Poreč": (45.2167, 13.6000),
            "Buzet": (45.4000, 13.9667)
        }
    },
    "831": {
        "naziv": "Ogulin",
        "podrucja": {
            "Ogulin": (45.2667, 15.2167),
            "Gospić": (44.5461, 15.3747),
            "Otočac": (44.8667, 15.2333),
            "Gračac": (44.3000, 15.8500)
        }
    },
    "832": {
        "naziv": "Karlovac",
        "podrucja": {
            "Karlovac": (45.4872, 15.5478),
            "Ozalj": (45.6000, 15.4667),
            "Jastrebarsko": (45.6667, 15.6500),
            "Slunj": (45.1167, 15.5833)
        }
    }
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
# MODE: REPORT (dnevni izvještaj - za sada ostaje po regijama)
# =========================
if MODE == "report":
    results = []
    
    # Za report koristimo jednostavne regije (radi brzine)
    regije = {
        "Zagreb": (45.8150, 15.9819),
        "Istra": (45.2400, 13.9367),
        "Kvarner": (45.3271, 14.4422),
        "Gorski kotar": (45.3986, 14.8019),
        "Lika": (44.5461, 15.3747),
        "Slavonija": (45.5550, 18.6955),
        "Dalmacija": (43.5081, 16.4402)
    }
    
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
    alert_mfg_grupe = []
    
    for mfg_id, mfg_data in mfg_grupe.items():
        mfg_naziv = mfg_data["naziv"]
        podrucja = mfg_data["podrucja"]
        
        for podrucje, (lat, lon) in podrucja.items():
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
                    alert_mfg_grupe.append(f"🔴 MFG {mfg_id} ({mfg_naziv}) - {podrucje}")
                    break  # Dovoljno je jedno područje za alert grupe
                
                print(f"MFG {mfg_id} - {podrucje}: CAPE={cape:.0f} => {level}")
            except Exception as e:
                print(f"ERROR - {mfg_id} - {podrucje}: {e}")

    if not alert_mfg_grupe:
        print("✅ Nema MFG grupa s vrlo visokim rizikom - ne šaljem poruku")
        sys.exit(0)
    
    msg = "🚨 SMC ALERT 🚨\n\nVRLO VISOK RIZIK - MFG GRUPE:\n\n"
    msg += "\n".join(alert_mfg_grupe)
    msg += f"\n\n📅 {datetime.now().strftime('%d.%m.%Y. %H:%M')}"

# =========================
# MODE: WEEKLY (tjedni izvještaj - po MFG grupama)
# =========================
elif MODE == "weekly":
    print("📊 Generiram tjedni izvještaj oluja po MFG grupama...")
    
    weekly_results = []
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    # ERA5 podaci kasne ~5 dana, zato gledamo period prije 9-2 dana
    end_date = datetime.now() - timedelta(days=2)
    start_date = end_date - timedelta(days=6)
    
    print(f"Period: {start_date.strftime('%d.%m.')} - {end_date.strftime('%d.%m.')}")
    
    # Dohvati datume
    datumi = []
    for i in range(7):
        dan = start_date + timedelta(days=i)
        datumi.append(dan.strftime("%d.%m."))
    
    for mfg_id, mfg_data in mfg_grupe.items():
        mfg_naziv = mfg_data["naziv"]
        podrucja = mfg_data["podrucja"]
        
        print(f"\n📌 Provjeravam MFG {mfg_id} - {mfg_naziv} ({len(podrucja)} područja)")
        
        # Sakupi sve oluje za sva područja u ovoj MFG grupi
        sve_oluje = []
        
        for podrucje, (lat, lon) in podrucja.items():
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
                
                # Provjeri svaki dan za ovo područje
                for dan in range(7):
                    start = dan * 24
                    end = start + 24
                    if end > len(data["cape"]):
                        break
                    max_cape = max(data["cape"][start:end])
                    
                    if max_cape >= 1500:
                        sve_oluje.append(f"   • {datumi[dan]} {podrucje} 🌩️ JAKA OLUJA (CAPE {max_cape:.0f})")
                    elif max_cape >= 800:
                        sve_oluje.append(f"   • {datumi[dan]} {podrucje} ⛈️ OLUJA (CAPE {max_cape:.0f})")
                
                print(f"   {podrucje}: gotovo")
                
            except Exception as e:
                print(f"   ERROR - {podrucje}: {e}")
        
        # Ukloni duplikate (isti dan, isto područje)
        sve_oluje = list(dict.fromkeys(sve_oluje))
        
        # Dodaj u rezultat samo ako ima oluja
        if sve_oluje:
            weekly_results.append(f"🔵 MFG {mfg_id} ({mfg_naziv}):")
            weekly_results.extend(sve_oluje)
            weekly_results.append("")
        else:
            weekly_results.append(f"🟢 MFG {mfg_id} ({mfg_naziv}): ✅ Nema oluja")
            weekly_results.append("")
    
    msg = f"""📊 SMC THUNDER - TJEDNI IZVJEŠTAJ OLUJA (PO MFG GRUPAMA)

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
