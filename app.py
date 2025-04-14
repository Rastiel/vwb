from flask import Flask, request, jsonify
import os
import requests
from utils.responder import cevapla

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return "Unauthorized", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if data and data.get("entry"):
        for entry in data["entry"]:
            for change in entry["changes"]:
                value = change["value"]
                messages = value.get("messages")
                if messages:
                    for message in messages:
                        phone_number_id = value["metadata"]["phone_number_id"]
                        from_number = message["from"]
                        msg_text = message["text"]["body"]

                        reply = cevapla(msg_text)

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

                        requests.post(url, headers=headers, json=payload)

    return jsonify(success=True), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
