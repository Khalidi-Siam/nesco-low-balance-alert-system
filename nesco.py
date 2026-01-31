import requests
from bs4 import BeautifulSoup
import re
import os
from typing import Optional

# ================== CONFIG ==================
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

CUSTOMER_IDS = [
    cid.strip()
    for cid in os.environ["CONSUMER_IDS"].split(",")
    if cid.strip()
]

LOW_BALANCE_THRESHOLD = 200  # TK
BASE_URL = "https://customer.nesco.gov.bd/pre/panel"

# ================== HEADERS ==================
COMMON_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/144.0.0.0 Mobile Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
    "Origin": "https://customer.nesco.gov.bd",
    "Referer": "https://customer.nesco.gov.bd/pre/panel",
    "Upgrade-Insecure-Requests": "1",
}

POST_HEADERS = {
    **COMMON_HEADERS,
    "Content-Type": "application/x-www-form-urlencoded",
}

# ================== CORE ==================
def get_balance(customer_id: str) -> Optional[float]:
    session = requests.Session()
    session.headers.update(COMMON_HEADERS)

    # Step 1: Initial GET (sets cookies + CSRF)
    r = session.get(BASE_URL, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    token_input = soup.find("input", {"name": "_token"})

    if not token_input:
        return None

    csrf_token = token_input["value"]

    # Step 2: POST with form data
    payload = {
        "_token": csrf_token,
        "cust_no": customer_id,
        "submit": "রিচার্জ হিস্ট্রি",
    }

    r2 = session.post(
        BASE_URL,
        data=payload,
        headers=POST_HEADERS,
        timeout=20,
    )
    r2.raise_for_status()

    soup2 = BeautifulSoup(r2.text, "html.parser")

    label = soup2.find("label", string=re.compile("অবশিষ্ট ব্যালেন্স"))
    if not label:
        return None

    inp = label.find_next("input")
    if not inp or not inp.has_attr("value"):
        return None

    try:
        return float(inp["value"].strip())
    except ValueError:
        return None

# ================== TELEGRAM ==================
def send_telegram(msg: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown",
        },
        timeout=15,
    )

# ================== MAIN ==================
def main():
    alerts = []

    for cid in CUSTOMER_IDS:
        balance = get_balance(cid)

        if balance is None:
            alerts.append(
                f"🆔 `{cid}`\n"
                f"⚠️ *Could not fetch balance*\n"
            )
        elif balance < LOW_BALANCE_THRESHOLD:
            alerts.append(
                f"🚨 *LOW BALANCE ALERT*\n"
                f"🆔 `{cid}`\n"
                f"💰 Balance: *{balance} TK*\n"
            )

    if alerts:
        message = "🔔 *NESCO Low Balance Alert*\n\n" + "\n".join(alerts)
        send_telegram(message)

if __name__ == "__main__":
    main()