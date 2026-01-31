import os
import asyncio
from playwright.async_api import async_playwright
import re
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
CUSTOMER_IDS = [cid.strip() for cid in os.environ["CONSUMER_IDS"].split(",") if cid.strip()]
LOW_BALANCE_THRESHOLD = 200
BASE_URL = "https://customer.nesco.gov.bd/pre/panel"

async def get_balance(customer_id):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(BASE_URL)
        # Fill customer ID
        await page.fill('input[name="cust_no"]', customer_id)
        await page.click('input[name="submit"]')
        # Wait for balance field to appear
        try:
            await page.wait_for_selector("label:has-text('অবশিষ্ট ব্যালেন্স') + div input", timeout=10000)
        except:
            await browser.close()
            return None
        # Get balance value
        balance_value = await page.eval_on_selector(
            "label:has-text('অবশিষ্ট ব্যালেন্স') + div input",
            "el => el.value"
        )
        await browser.close()
        try:
            return float(balance_value.strip())
        except:
            return None

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=15)

async def main():
    alerts = []
    for cid in CUSTOMER_IDS:
        balance = await get_balance(cid)
        if balance is None:
            alerts.append(f"🆔 `{cid}`\n⚠️ Could not fetch balance\n")
        elif balance < LOW_BALANCE_THRESHOLD:
            alerts.append(f"🚨 *LOW BALANCE ALERT*\n🆔 `{cid}`\n💰 Balance: *{balance} TK*\n")
    if alerts:
        send_telegram("🔔 *NESCO Low Balance Alert*\n\n" + "\n".join(alerts))

if __name__ == "__main__":
    asyncio.run(main())