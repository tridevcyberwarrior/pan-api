import os
import re
import time
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # CORS enable for all origins

SPINNY_URL = "https://api.spinny.com/v3/api/vehicle/full-pan-details/"
PAN_RE = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
TIMEOUT = 25

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Mobile Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Content-Type": "application/json",
    "sec-ch-ua-platform": "\"Android\"",
    "sec-ch-ua": "\"Chromium\";v=\"152\", \"Not?A_Brand\";v=\"24\", \"Google Chrome\";v=\"152\"",
    "anonymous-id": "805084276.1789365900",
    "sec-ch-ua-mobile": "?1",
    "platform": "mweb_android",
    "origin": "https://www.spinny.com",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.spinny.com/",
    "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "priority": "u=1, i",
    "Cookie": "_ga=GA1.1.805084276.1789365900; platform=mweb_android; utm_source=direct; varnishPrefixBhpEarly=true; _fbp=fb.1.1789365908705.762646774423246358; _clck=g5c4ud%5E2%5Eg9g%5E0%5E2448; cto_bundle=lG_voV82d0lzUEVIUldlZmFzSUNIJTJGa1BTMjQ4N3NJSllsRzRSNnhnaHFBRU56SDdYZG1hS0MwdGJMamhFQXNzSTd0N1dLJTJCRlRXMHlEUnZmMnFPVnNQTE5kRXVza211cktoajE5JTJCNWxPcUpTS01IUmo4aFN5dTNmV1hxZ29tTlVYMU5Za0FnYU9NeWdqYW4lMkJYTG5KWVFtb0luZyUzRCUzRA; csrftoken=xZUQAkYpTG4PGwW7yWIbQzeBuOAMZ0I0EMGlxqH9edvDaAJaht5pIEUsoRermU2h; sessionid=7l57gfb45f2dd99swehjb1npxagplkg6; _gcl_au=1.1.1317952119.1789365898.-.-.1789367146.936292459.1789367146.1789367163; _clsk=c9oyow%5E1789367170302%5E3%5E1%5Ef.clarity.ms%2Fcollect; _ga_WQREN8TJ7R=GS2.1.s1789365900$o1$g1$t1789367214$j56$l0$h0",
}

def fetch_pan(pan: str) -> dict:
    resp = requests.post(
        SPINNY_URL, 
        params={"pan_number": pan, "source": "used-car-loans"},
        data=json.dumps({}), 
        headers=HEADERS, 
        timeout=TIMEOUT
    )
    if resp.status_code != 200:
        raise Exception(f"Spinny HTTP {resp.status_code}: {resp.text[:100]}")
    
    body = resp.json()
    if not body.get("ok") or not body.get("is_success"):
        raise Exception(f"Spinny failed: {body.get('error', 'unknown error')}")
    
    data = body.get("data") or {}
    if not data.get("pan_number"):
        raise Exception("Spinny returned no data")
    
    return data

def order_data(d: dict) -> dict:
    return {
        "name": d.get("name"),
        "first_name": d.get("first_name"),
        "middle_name": d.get("middle_name"),
        "last_name": d.get("last_name"),
        "pan_number": d.get("pan_number"),
        "gender": d.get("gender"),
        "dob": d.get("dob"),
        "mobile_number": d.get("mobile_number"),
        "email_id": d.get("email_id"),
        "address": d.get("address") or {},
        "masked_aadhar_number": d.get("masked_aadhar_number"),
        "is_aadhaar_linked": d.get("is_aadhaar_linked"),
        "category": d.get("category"),
        "type_of_holder": d.get("type_of_holder"),
        "pan_status": d.get("pan_status"),
        "is_valid": d.get("is_valid"),
    }

@app.route("/")
def index():
    return jsonify({
        "name": "PAN Info API",
        "version": "1.0",
        "usage": "GET /api/pan?pan=BBGPP5787F",
        "endpoints": {
            "/": "This info",
            "/api/pan?pan=NUMBER": "Get PAN details",
            "/health": "Health check"
        }
    })

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/api/pan", methods=["GET"])
def api_pan():
    pan = (request.args.get("pan") or request.args.get("pan_number") or "").upper().strip()
    
    if not PAN_RE.match(pan):
        return jsonify({
            "success": False, 
            "error": "Invalid PAN format. Example: BBGPP5787F"
        }), 400
    
    start = time.time()
    try:
        data = fetch_pan(pan)
        out = order_data(data)
        out["response_time_seconds"] = round(time.time() - start, 2)
        return jsonify({"success": True, "data": out}), 200
    except Exception as e:
        return jsonify({
            "success": False, 
            "error": f"{type(e).__name__}: {str(e)[:200]}",
            "response_time_seconds": round(time.time() - start, 2)
        }), 502

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
