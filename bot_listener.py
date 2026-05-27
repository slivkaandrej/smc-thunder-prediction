import requests
import json
import os
import time
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN")
SUBSCRIBERS_FILE = "subscribers.json"
LAST_UPDATE_FILE = "last_update.txt"

def load_subscribers():
    if not os.path.exists(SUBSCRIBERS_FILE):
        return []
    with open(SUBSCRIBERS_FILE, "r") as f:
        data = json.load(f)
        return data if isinstance(data, list) else []

def save_subscribers(subscribers):
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(subscribers, f, indent=2)

def add_subscriber(chat_id, username=None):
    subscribers = load_subscribers()
    for sub in subscribers:
        if sub.get("chat_id") == chat_id:
            return False
    subscribers.append({
        "chat_id": chat_id,
        "username": username,
        "subscribed_at": datetime.now().isoformat()
    })
    save_subscribers(subscribers)
    return True

def get_last_update_id():
    if os.path.exists(LAST_UPDATE_FILE):
        with open(LAST_UPDATE_FILE, "r") as f:
            return int(f.read().strip())
    return 0

def save_last_update_id(update_id):
    with open(LAST_UPDATE_FILE, "w") as f:
        f.write(str(update_id))

def main():
    print("🤖 Bot listener pokrenut. Čekam /start komande...")
    last_update_id = get_last_update_id()
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            params = {"offset": last_update_id + 1, "timeout": 30}
            response = requests.get(url, params=params, timeout=35)
            data = response.json()
            
            if data.get("ok") and data.get("result"):
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
                        if add_subscriber(chat_id, username):
                            confirm_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                            confirm_msg = "✅ Pretplaćeni ste na SMC Thunder izvještaje! Dobivat ćete dnevne i tjedne izvještaje o olujama."
                            requests.post(confirm_url, data={"chat_id": chat_id, "text": confirm_msg})
                            print(f"✅ Novi pretplatnik: {chat_id} (@{username})")
                        else:
                            already_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                            already_msg = "ℹ️ Već ste pretplaćeni na SMC Thunder izvještaje!"
                            requests.post(already_url, data={"chat_id": chat_id, "text": already_msg})
                
                save_last_update_id(last_update_id)
                
        except Exception as e:
            print(f"❌ Greška: {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    main()
