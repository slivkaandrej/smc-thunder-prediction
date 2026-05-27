import requests
import json
import os
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN")
SUBSCRIBERS_FILE = "subscribers.json"

def load_subscribers():
    if not os.path.exists(SUBSCRIBERS_FILE):
        return []
    try:
        with open(SUBSCRIBERS_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            data = json.loads(content)
            return data if isinstance(data, list) else []
    except:
        return []

def save_subscribers(subscribers):
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(subscribers, f, indent=2)
    print(f"💾 Spremljeno {len(subscribers)} pretplatnika u {SUBSCRIBERS_FILE}")

def add_subscriber(chat_id, username=None):
    subscribers = load_subscribers()
    for sub in subscribers:
        if sub.get("chat_id") == chat_id:
            print(f"ℹ️ Korisnik {chat_id} već postoji")
            return False
    subscribers.append({
        "chat_id": chat_id,
        "username": username,
        "subscribed_at": datetime.now().isoformat()
    })
    save_subscribers(subscribers)
    return True

def get_last_update_id():
    file = "last_update.txt"
    if os.path.exists(file):
        with open(file, "r") as f:
            return int(f.read().strip())
    return 0

def save_last_update_id(update_id):
    with open("last_update.txt", "w") as f:
        f.write(str(update_id))

def main():
    print("🤖 Bot listener pokrenut...")
    print(f"📁 Trenutni direktorij: {os.getcwd()}")
    print(f"📁 Postoji subscribers.json: {os.path.exists(SUBSCRIBERS_FILE)}")
    
    last_update_id = get_last_update_id()
    print(f"📌 Zadnji update_id: {last_update_id}")
    
    if not TOKEN:
        print("❌ TELEGRAM_TOKEN nije postavljen!")
        return
    
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
        params = {"offset": last_update_id + 1, "timeout": 10}
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        if data.get("ok") and data.get("result"):
            print(f"📨 Pronađeno {len(data['result'])} poruka")
            for update in data["result"]:
                update_id = update.get("update_id")
                if update_id > last_update_id:
                    last_update_id = update_id
                
                message = update.get("message", {})
                text = message.get("text", "")
                chat = message.get("chat", {})
                chat_id = chat.get("id")
                username = chat.get("username")
                
                if text == "/start":
                    print(f"🔍 Pronađen /start od {chat_id}")
                    if add_subscriber(chat_id, username):
                        # Pošalji potvrdu
                        requests.post(
                            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                            data={"chat_id": chat_id, "text": "✅ Pretplaćeni ste na SMC Thunder izvještaje!"}
                        )
                        print(f"✅ Dodan: {chat_id}")
                    else:
                        print(f"ℹ️ Već postoji: {chat_id}")
            
            save_last_update_id(last_update_id)
            print("✅ Gotovo!")
        else:
            print(f"❌ Greška: {data}")
            
    except Exception as e:
        print(f"❌ Greška: {e}")

if __name__ == "__main__":
    main()
