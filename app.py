# Gerekli kütüphaneleri içe aktar
from flask import Flask, request
import os
import requests
import json
from datetime import datetime

# Flask uygulamasını başlat
app = Flask(__name__)

# Ortam değişkenlerinden token ve ID bilgilerini al
ACCESS_TOKEN = os.getenv("WHATSAPP_TOKEN")               # WhatsApp erişim token'ı
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")           # Mesaj gönderilecek numara ID'si
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "kerem-secret") # Webhook doğrulama için kullanılacak token

# Log klasörünü oluştur (varsa hata vermez)
LOG_DIR = "log"
os.makedirs(LOG_DIR, exist_ok=True)

# Gelen JSON verisini timestamp'li olarak dosyaya kaydet
def log_to_file(data):
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(LOG_DIR, f"msg_{now}.json")
    with open(filename, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# WhatsApp Cloud API aracılığıyla mesaj gönderen fonksiyon
def send_message(to_number, message_text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

    # HTTP istek başlıkları
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # Gönderilecek JSON payload
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {
            "body": message_text
        }
    }

    # API'ye POST isteği gönder
    response = requests.post(url, headers=headers, json=payload)
    print(f"Yanıt: {response.status_code}, {response.text}")

# Ana webhook endpoint
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # Facebook doğrulama isteği (GET ile gelir)
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        # Eğer token doğruysa Facebook'a challenge kodunu döndür
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Doğrulama başarısız", 403

    # WhatsApp ya da test mesajları buraya POST ile gelir
    elif request.method == "POST":
        data = request.get_json()  # JSON veriyi al
        log_to_file(data)          # Gelen veriyi dosyaya kaydet

        try:
            # Gerçek WhatsApp mesajı geldiyse bu blok çalışır
            if "entry" in data:
                value = data["entry"][0]["changes"][0]["value"]
                from_number = value["messages"][0]["from"]
                message_text = value["messages"][0]["text"]["body"]

            # Facebook test mesajı geldiyse bu blok çalışır
            elif "messages" in data.get("value", {}):
                value = data["value"]
                from_number = value["messages"][0]["from"]
                message_text = value["messages"][0]["text"]["body"]

            else:
                raise Exception("Desteklenmeyen veri yapısı")

            # Terminale mesajı yaz
            print(f"Gelen mesaj: {message_text} - Gönderen: {from_number}")

            # Otomatik cevap gönder
            send_message(from_number, f"Selam! Mesajını aldım: “{message_text}”")

        except Exception as e:
            # Herhangi bir hata olursa terminale yaz
            print(f"Mesaj işlenemedi: {e}")

        return "OK", 200

# Flask uygulamasını başlat (Docker için tüm arayüzleri dinler)
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
