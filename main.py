
import requests
import qrcode
import io
import base64
from flask import Flask, request, render_template

app = Flask(__name__, template_folder="templates")

TOKEN = "BxfKdGLS8YkZrwLQcpp4cl3O8SKWhFpXKjA0pW8p66f22c31"
WEBHOOK_URL = "https://pushinpay-pix-api.onrender.com/webhook"
SPLIT_ACCOUNT_ID = "9C3AD98C-F00B-4729-BEAC-0A4B70B3A043"

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/gerar", methods=["POST"])
def gerar_pix():
    valor = float(request.form["valor"])
    payload = {
        "value": valor,
        "webhook_url": WEBHOOK_URL,
        "split_rules": [
            {
                "value": 50,
                "account_id": SPLIT_ACCOUNT_ID
            }
        ]
    }
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    res = requests.post("https://api.pushinpay.com.br/api/pix/cashIn", json=payload, headers=headers)
    if res.status_code != 200:
        return f"Erro ao gerar Pix: {res.status_code} - {res.text}"
    
    emv = res.json()["pix_details"]["emv"]
    qr = qrcode.make(emv)
    buffered = io.BytesIO()
    qr.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return render_template("index.html", emv=emv, qr_image=qr_base64)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if data.get("status") == "paid":
        print(f"[💰] Pagamento {data['id']} confirmado! Valor: R${data['value']}")
    return "", 200

if __name__ == "__main__":
    app.run(debug=True)
