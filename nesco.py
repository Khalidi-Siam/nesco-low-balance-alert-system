import requests
from bs4 import BeautifulSoup
import re
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

CUSTOMER_IDS = [
    cid.strip()
    for cid in os.environ["CONSUMER_IDS"].split(",")
    if cid.strip()
]

LOW_BALANCE_THRESHOLD = 200  # TK

BASE_URL = "https://customer.nesco.gov.bd/pre/panel"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "bn,en-US;q=0.9,en;q=0.8",
    "Referer": BASE_URL,
    "Origin": "https://customer.nesco.gov.bd",
}

def get_balance(customer_id):
    session = requests.Session()
    session.headers.update(HEADERS)

    # STEP 1: GET page (sets cookies + CSRF)
    r = session.get(BASE_URL, timeout=20, allow_redirects=False)
    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    token_tag = soup.find("input", {"name": "_token"})
    if not token_tag:
        return None

    csrf_token = token_tag["value"]

    # Laravel requires this header
    xsrf = session.cookies.get("XSRF-TOKEN")
    if xsrf:
        session.headers["X-XSRF-TOKEN"] = xsrf

    payload = {
        "_token": csrf_token,
        "cust_no": customer_id,
        "submit": "রিচার্জ হিস্ট্রি",
    }

    # STEP 2: POST form
    r2 = session.post(
        BASE_URL,
        data=payload,
        timeout=20,
        allow_redirects=False,
    )

    if r2.status_code != 200:
        return None

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

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }, timeout=10)

def main():
    alerts = []

    for cid in CUSTOMER_IDS:
        balance = get_balance(cid)

        if balance is None:
            alerts.append(f"🆔 `{cid}`\n⚠️ Could not fetch balance\n")
        elif balance < LOW_BALANCE_THRESHOLD:
            alerts.append(
                f"🚨 *LOW BALANCE ALERT*\n"
                f"🆔 `{cid}`\n"
                f"💰 Balance: *{balance} TK*\n"
            )

    if alerts:
        send_telegram("🔔 *NESCO Low Balance Alert*\n\n" + "\n".join(alerts))

if __name__ == "__main__":
    main()