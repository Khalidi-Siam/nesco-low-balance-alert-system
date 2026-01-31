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

LOW_BALANCE_THRESHOLD = 200  #TK

def get_balance(customer_id):
    url = "https://customer.nesco.gov.bd/pre/panel"
    session = requests.Session()

    r = session.get(url, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    token = soup.find("input", {"name": "_token"})
    if not token:
        return None

    payload = {
        "_token": token["value"],
        "cust_no": customer_id,
        "submit": "রিচার্জ হিস্ট্রি"
    }

    r2 = session.post(url, data=payload, timeout=15)
    soup2 = BeautifulSoup(r2.text, "html.parser")

    label = soup2.find("label", string=re.compile("অবশিষ্ট ব্যালেন্স"))
    if not label:
        return None

    inp = label.find_next("input")
    if inp and inp.has_attr("value"):
        try:
            return float(inp["value"].strip())
        except ValueError:
            return None

    return None

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    })

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
        message = "🔔 *NESCO Low Balance Alert*\n\n" + "\n".join(alerts)
        send_telegram(message)

if __name__ == "__main__":
    main()