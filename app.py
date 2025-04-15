# Gerekli kütüphaneleri içe aktar
from flask import Flask, request
import os
import requests
import json

# Flask uygulamasını başlat
app = Flask(__name__)

# Ortam değişkenlerinden token ve kimlik bilgilerini al
ACCESS_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# Gelen verileri dosyaya kaydeden fonksiyon
def log_to_file(data):
    with open("log/webhook.log", "a") as f:
        # JSON veriyi log dosyasına okunabilir şekilde yaz
        f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n\n")

# WhatsApp API üzerinden mesaj gönderen fonksiyon
def send_message(to_number, message_text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    
    # HTTP başlıkları (Authorization ve içerik tipi)
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # Gönderilecek mesaj içeriği (JSON formatında)
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
    print(f"Gönderilen mesaja yanıt: {response.status_code}, {response.text}")

# Webhook endpoint'i
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # Webhook doğrulama isteği (Facebook tarafından gönderilen GET isteği)
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        # Doğrulama token'ı eşleşirse challenge'ı döndür
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Doğrulama başarısız", 403

    # WhatsApp'tan gelen mesajları işleyen POST kısmı
    elif request.method == "POST":
        # JSON veriyi al
        data = request.get_json()
        
        # Gelen veriyi logla
        log_to_file(data)

        try:
            # Gönderen numarayı al
            from_number = data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
            # Gelen mesajın metnini al
            message_text = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]

            print(f"Gelen mesaj: {message_text} - Gönderen: {from_number}")

            # Otomatik cevap gönder
            send_message(from_number, f"Selam! Şu mesajı aldım: \"{message_text}\"")

        except Exception as e:
            # Hata durumunda terminale yaz
            print(f"Mesaj işlenemedi: {e}")

        return "OK", 200

# Flask uygulamasını başlat
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
