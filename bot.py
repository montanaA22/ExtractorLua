import requests
from config import Config
from models import init_db

API = f"https://api.telegram.org/bot{Config.BOT_TOKEN}"
ALLOWED = str(Config.ADMIN_ID)

def reply(chat_id, text):
    requests.post(f"{API}/sendMessage",
                  json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
                  timeout=15)

def handle(msg):
    chat_id = msg["chat"]["id"]
    uid = str(msg["from"]["id"])
    text = (msg.get("text") or "").strip()

    if uid != ALLOWED:
        reply(chat_id, "🚫 No autorizado.")
        return

    if text.startswith("/start"):
        reply(chat_id, "👑 <b>ZEYUN ADMIN</b>\n\n/genkey [días] [usos]\n/help")
        return

    if text.startswith("/genkey"):
        parts = text.split()
        days = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 7
        uses = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 1
        try:
            r = requests.post("http://127.0.0.1:5000/api/bot/key",
                              json={"admin_id": uid, "days": days, "uses": uses},
                              timeout=15)
            if r.ok:
                j = r.json()
                reply(chat_id, f"✅ <b>Key:</b> <code>{j['key']}</code>\n📅 {j['days']}d · 🔁 {j['uses']} usos")
            else:
                reply(chat_id, f"❌ Error {r.status_code}")
        except Exception as e:
            reply(chat_id, f"❌ {e}")
        return

    if text.startswith("/help"):
        reply(chat_id, "<b>Comandos</b>\n/start\n/genkey [días] [usos]\n/help")
        return

    reply(chat_id, "Usa /help")

def poll():
    init_db()
    offset = 0
    print("[ZEYUN BOT] online")
    while True:
        try:
            r = requests.get(f"{API}/getUpdates",
                             params={"offset": offset, "timeout": 25}, timeout=40)
            if not r.ok:
                continue
            for up in r.json().get("result", []):
                offset = up["update_id"] + 1
                if "message" in up:
                    try: handle(up["message"])
                    except Exception as e: print("[err]", e)
        except Exception as e:
            print("[poll]", e)

if __name__ == "__main__":
    poll()
