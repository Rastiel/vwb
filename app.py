# Flask, HTTP sunucusu kurmak için kullanılır
from flask import Flask, request, jsonify

# Ortam değişkenlerini (token gibi) okumak için os modülü
import os

# WhatsApp API'sine istek göndermek için requests
import requests

# Gelen mesaja yanıt üretmek için dış modül (utils/responder.py içindeki cevapla fonksiyonu)
from utils.responder import cevapla

# Flask uygulamasını başlatıyoruz
app = Flask(__name__)

# .env dosyasından ortam değişkenlerini okuyoruz
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")             # Meta'nın doğrulama tokenı
ACCESS_TOKEN = os.getenv("WHATSAPP_TOKEN")           # WhatsApp API erişim tokenı
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")       # Numara ID'miz

# Meta sunucusu bu endpoint'e GET isteği atarak doğrulama yapar
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")              # "subscribe" olup olmadığını kontrol eder
    token = request.args.get("hub.verify_token")     # Bizim belirlediğimiz doğrulama tokenı
    challenge = request.args.get("hub.challenge")    # Meta'nın geri dönmemizi istediği değer

    # Doğrulama başarılıysa challenge'ı döndür, değilse 403
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return "Unauthorized", 403

# Meta, gelen mesajları bu endpoint'e POST ile gönderir
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()  # JSON olarak gelen veriyi al

    # Gelen veri boş değilse ve "entry" anahtarı içeriyorsa işleme başla
    if data and data.get("entry"):
        for entry in data["entry"]:                      # Her bir giriş için
            for change in entry["changes"]:              # Değişiklikleri incele
                value = change["value"]                  # Değerleri al
                messages = value.get("messages")         # Mesaj olup olmadığını kontrol et

                if messages:
                    for message in messages:             # Her mesaj için
                        phone_number_id = value["metadata"]["phone_number_id"]
                        from_number = message["from"]    # Kullanıcının numarası
                        msg_text = message["text"]["body"]  # Mesaj içeriği

                        # Mesaja verilecek cevabı üret (bizim yazacağımız fonksiyon)
                        reply = cevapla(msg_text)

                        # WhatsApp API'ye cevap mesajı göndermek için ayarlar
                        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
                        headers = {
                            "Authorization": f"Bearer {ACCESS_TOKEN}",
                            "Content-Type": "application/json"
                        }
                        payload = {
                            "messaging_product": "whatsapp",
                            "to": from_number,
                            "type": "text",
                            "text": {"body": reply}
                        }

                        # Yanıtı WhatsApp API'sine gönder
                        requests.post(url, headers=headers, json=payload)

    return jsonify(success=True), 200  # Her halükarda 200 dön, yoksa Meta hata alır

# Uygulamayı başlat
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)  # Tüm IP'lerden erişilebilir, port 10000
