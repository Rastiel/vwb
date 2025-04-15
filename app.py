from flask import Flask, request
import os
import json
from datetime import datetime

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "kerem-secret")

LOG_DIR = "log"
os.makedirs(LOG_DIR, exist_ok=True)

def log_to_file(data):
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(LOG_DIR, f"msg_{now}.json")
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Doğrulama başarısız", 403

    elif request.method == "POST":
        data = request.get_json()
        log_to_file(data)
        return "Doğrulama başarılı", 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
