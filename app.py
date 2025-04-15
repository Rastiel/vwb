from flask import Flask, request
import os
import requests
import json
from datetime import datetime

app = Flask(__name__)

# Ortam değişkenlerini al (dotenv varsa otomatik çekilir)
ACCESS_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "kerem-secret")

# Log klasörünü oluştur (varsa geç)
LOG_DIR = "log"
os.makedirs(LOG_DIR, exist_ok=True)

# Gelen veriyi zaman damgalı dosyaya kaydeder
def log_to_file(data):
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(LOG_DIR, f"msg_{now}.json")
    with open(filename, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Mesajı WhatsApp üzerinden gönderen fonksiyon
def send_message(to_number, message_text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {
            "body": message_text
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print(f"Yanıt: {response.status_code}, {response.text}")

# Webhook endpoint
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Meta doğrulama isteği
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Doğrulama başarısız", 403

    elif request.method == "POST":
        data = request.get_json()
        log_to_file(data)  # Her gelen veriyi dosyaya yaz

        try:
            # Gerçek mesaj mı, test mesajı mı kontrol et
            if "entry" in data:
                # Gerçek WhatsApp mesajı
                value = data["entry"][0]["changes"][0]["value"]
                from_number = value["messages"][0]["from"]
                message_text = value["messages"][0]["text"]["body"]

            elif "messages" in data.get("value", {}):
                # Facebook test mesajı
                value = data["value"]
                from_number = value["messages"][0]["from"]
                message_text = value["messages"][0]["text"]["body"]

            else:
                raise Exception("Desteklenmeyen veri yapısı")

            print(f"Gelen mesaj: {message_text} - Gönderen: {from_number}")
            send_message(from_number, f"Selam! Mesajını aldım: “{message_text}”")

        except Exception as e:
            print(f"Mesaj işlenemedi: {e}")

        return "OK", 200

# Flask uygulamasını başlat
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
