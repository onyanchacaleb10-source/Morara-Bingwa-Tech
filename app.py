import os
import time
import base64
import logging
from datetime import datetime
from functools import lru_cache

import requests
from requests.auth import HTTPBasicAuth
from flask import Flask, request, jsonify, render_template_string

# Configuration from env
CONSUMER_KEY = os.getenv("CONSUMER_KEY", "")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET", "")
PASSKEY = os.getenv("PASSKEY", "")
BUSINESS_SHORT_CODE = os.getenv("BUSINESS_SHORT_CODE", "7818012")  # default till
CALLBACK_URL = os.getenv("CALLBACK_URL", "")  # must be HTTPS for safaricom
SANDBOX = os.getenv("SANDBOX", "true").lower() in ("1", "true", "yes")

if SANDBOX:
    OAUTH_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    STK_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
else:
    OAUTH_URL = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    STK_URL = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mpesa-stk")

app = Flask(__name__)

# Simple in-memory token cache
_token_cache = {"access_token": None, "expires_at": 0}


def get_access_token():
    now = int(time.time())
    if _token_cache["access_token"] and _token_cache["expires_at"] - 10 > now:
        return _token_cache["access_token"]

    if not CONSUMER_KEY or not CONSUMER_SECRET:
        raise RuntimeError("CONSUMER_KEY and CONSUMER_SECRET must be set in environment")

    resp = requests.get(OAUTH_URL, auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET), timeout=10)
    resp.raise_for_status()
    data = resp.json()
    token = data.get("access_token")
    expires_in = int(data.get("expires_in", 0))
    if not token:
        raise RuntimeError(f"Failed to get access token: {data}")
    _token_cache["access_token"] = token
    _token_cache["expires_at"] = now + expires_in
    return token


def normalize_phone(phone):
    # Accept formats: 07XXXXXXXX, 7XXXXXXXX, 2547XXXXXXXX, +2547XXXXXXXX
    p = phone.strip()
    if p.startswith("+"):
        p = p[1:]
    if p.startswith("0") and len(p) == 10:
        return "254" + p[1:]
    if p.startswith("7") and len(p) == 9:
        return "254" + p
    if p.startswith("254") and len(p) == 12:
        return p
    raise ValueError("Phone number must be in one of: 07XXXXXXXX, 7XXXXXXXX, 2547XXXXXXXX, +2547XXXXXXXX")


def build_password(timestamp):
    if not PASSKEY or not BUSINESS_SHORT_CODE:
        raise RuntimeError("PASSKEY and BUSINESS_SHORT_CODE must be set")
    data = BUSINESS_SHORT_CODE + PASSKEY + timestamp
    return base64.b64encode(data.encode()).decode()


@app.route("/pay", methods=["GET"])
def pay_form():
    amount_default = request.args.get("amount", "200")
    html = """
    <!doctype html>
    <title>Pay with M-PESA</title>
    <h2>Pay to Till {{ till }}</h2>
    <form action="/api/pay" method="post">
      Phone (e.g. 2547XXXXXXXX): <input name="phone" required><br>
      Amount (KES): <input name="amount" value="{{ amount }}"><br>
      <input type="submit" value="Pay">
    </form>
    """
    return render_template_string(html, till=BUSINESS_SHORT_CODE, amount=amount_default)


@app.route("/api/pay", methods=["POST"])
def api_pay():
    # Accept JSON or form
    data = request.get_json(silent=True) or request.form or request.values
    phone = data.get("phone")
    amount = data.get("amount", "200")

    if not phone:
        return jsonify({"error": "phone is required"}), 400
    try:
        phone_norm = normalize_phone(phone)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    try:
        amount_int = int(float(amount))
        if amount_int <= 0:
            raise ValueError()
    except Exception:
        return jsonify({"error": "amount must be a positive number"}), 400

    try:
        token = get_access_token()
    except Exception as e:
        logger.exception("Failed to get token")
        return jsonify({"error": "failed to get access token", "details": str(e)}), 500

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = build_password(timestamp)

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "BusinessShortCode": BUSINESS_SHORT_CODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerBuyGoodsOnline",
        "Amount": amount_int,
        "PartyA": phone_norm,
        "PartyB": BUSINESS_SHORT_CODE,
        "PhoneNumber": phone_norm,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": "Promotion",  # change as needed
        "TransactionDesc": "Payment"
    }

    try:
        resp = requests.post(STK_URL, json=payload, headers=headers, timeout=15)
        try:
            resp_json = resp.json()
        except ValueError:
            resp_json = {"raw": resp.text}
        if resp.status_code >= 400:
            logger.error("STK push failed: %s", resp_json)
            return jsonify({"error": "stk push failed", "response": resp_json}), resp.status_code
        # successful submit to Safaricom (customer still needs to complete PIN)
        return jsonify({"ok": True, "response": resp_json}), 200
    except requests.RequestException as e:
        logger.exception("HTTP error when calling STK API")
        return jsonify({"error": "network error when calling stk", "details": str(e)}), 500


@app.route("/callback", methods=["POST"])
def callback():
    # Safaricom will POST callback JSON here.
    data = request.get_json(silent=True)
    if not data:
        data = {"raw_body": request.get_data(as_text=True)}
    logger.info("Received STK callback: %s", data)
    # For production: validate and persist to DB. Here we simply return 200.
    return jsonify({"result": "received"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=os.getenv("FLASK_DEBUG", "0") == "1")
