
import requests
import qrcode
import io
import base64
from flask import Flask, request, render_template_string

app = Flask(__name__)

TOKEN = "SEU_TOKEN_AQUI"
WEBHOOK_URL = "https://pushinpay-pix-api.onrender.com/webhook"
SPLIT_ACCOUNT_ID = "9C3AD98C-F00B-4729-BEAC-0A4B70B3A043"

HTML_TEMPLATE = open("templates/index.html", encoding="utf-8").read()

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE)

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
    return render_template_string(HTML_TEMPLATE, emv=emv, qr_image=qr_base64)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if data.get("status") == "paid":
        print(f"[💰] Pagamento {data['id']} confirmado! Valor: R${data['value']}")
    return "", 200

if __name__ == "__main__":
    app.run(debug=True)
