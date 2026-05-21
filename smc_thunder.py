import requests
from datetime import datetime
import os
import pytz

# =========================
# TIMEZONE
# =========================
ZAGREB = pytz.timezone("Europe/Zagreb")
now = datetime.now(ZAGREB)

# =========================
# ENV VARS
# =========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MODE = os.getenv("MODE", "report")
RUN_TYPE = os.getenv("RUN_TYPE", "schedule")

# =========================
# RUN TIMES
# =========================
RUN_TIMES = [
    (7, 15),
    (15, 18)
]

def is_scheduled_time():
    return any(now.hour == h and now.minute == m for h, m in RUN_TIMES)

print("================================")
print("[INFO] RUN_TYPE:", RUN_TYPE)
print("[INFO] TIME:", now.strftime("%H:%M"))
print("================================")

# =========================
# SAFETY GATE (FIXED LOGIC)
# =========================
if RUN_TYPE == "workflow_dispatch":
    print("[INFO] Manual run → bypass time check")
else:
    if not is_scheduled_time():
        print("[INFO] Not scheduled time → exit")
        exit(0)

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

        emoji = (
            "🟢" if level == "NIZAK" else
            "🟡" if level == "UMJEREN" else
            "🟠" if level == "VISOK" else
            "🔴"
        )

        results.append(f"{emoji} {ime:15} {level}")

        if level == "VRLO VISOK":
            alert_zones.append(ime)

        print(f"{ime} => {level}")

    except Exception as e:
        print("[ERROR]", ime, e)

# =========================
# MESSAGE
# =========================
if MODE == "report":
    naslov = "🌅 JUTARNJI IZVJEŠTAJ" if now.hour < 12 else "🌤️ POPODNEVNI IZVJEŠTAJ"

    msg = f"""🌩️ SMC THUNDER

{naslov}
📅 {now.strftime("%d.%m.%Y")}
🕒 {now.strftime("%H:%M")}

📍 REGIJE:

""" + "\n".join(results)

elif MODE == "alert":
    if not alert_zones:
        print("[INFO] No alerts")
        exit(0)

    msg = "🚨 SMC ALERT 🚨\n\nVRLO VISOK RIZIK:\n\n"
    msg += "\n".join([f"⚡ {z}" for z in alert_zones])

else:
    print("[ERROR] MODE not set")
    exit(1)

# =========================
# VALIDATION
# =========================
if not TOKEN or not CHAT_ID:
    print("[ERROR] Missing Telegram secrets")
    exit(1)

# =========================
# SEND
# =========================
resp = requests.post(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    data={
        "chat_id": CHAT_ID,
        "text": msg
    }
)

print("[INFO] STATUS:", resp.status_code)
print("[INFO] RESPONSE:", resp.text)
print("[DONE]")
